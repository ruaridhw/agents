#!/usr/bin/env python3
"""List, read, close and resume the Herdr panes this session spawned."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WORKER = "worker"
DEFAULT_LINES = 80


class HerdrError(Exception):
    pass


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def ok(proc: subprocess.CompletedProcess[str], label: str) -> str:
    if proc.returncode != 0:
        raise HerdrError(
            f"{label} failed\nCOMMAND: {' '.join(proc.args)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout


def parse_json(stdout: str, label: str) -> dict:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise HerdrError(f"{label} did not return JSON: {exc}\n{stdout}")


def find_id(payload: dict, key: str) -> str | None:
    stack = [payload]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            value = node.get(key)
            if isinstance(value, str):
                return value
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return None


def ledger_path(override: Path | None) -> Path:
    return (override or Path.cwd() / ".herdr-handoffs" / "panes.jsonl").resolve()


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=".panes-", suffix=".jsonl"
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as out:
            for row in rows:
                out.write(json.dumps(row, sort_keys=True) + "\n")
        os.replace(temp_name, path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise


def latest_rows(rows: list[dict]) -> dict[str, dict]:
    return {row["name"]: row for row in rows if row.get("name")}


def agent_info(name: str) -> dict | None:
    proc = run(["herdr", "agent", "get", name])
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)["result"]["agent"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def live_status(row: dict) -> str:
    if row.get("status") != "open":
        return str(row.get("status") or "unknown")
    info = agent_info(row["name"])
    if not info:
        return "missing"
    return str(info.get("agent_status") or "unknown")


def mine() -> str | None:
    return os.environ.get("HERDR_PANE_ID")


def cmd_list(args: argparse.Namespace) -> int:
    rows = latest_rows(read_rows(args.ledger)).values()
    selected = [row for row in rows if args.all or row.get("creator_pane") == mine()]
    records = [{**row, "live": live_status(row)} for row in selected]
    if args.json:
        print(json.dumps(records, indent=2, sort_keys=True))
        return 0
    if not records:
        print(
            "no panes recorded for this pane" if not args.all else "no panes recorded"
        )
        return 0
    headers = ("NAME", "KIND", "MODE", "STATUS", "TAB", "PANE")
    widths = [len(header) for header in headers]
    for record in records:
        cells = table_cells(record)
        widths = [max(width, len(cell)) for width, cell in zip(widths, cells)]
    print("  ".join(header.ljust(width) for header, width in zip(headers, widths)))
    for record in records:
        print(
            "  ".join(
                cell.ljust(width) for cell, width in zip(table_cells(record), widths)
            )
        )
    return 0


def table_cells(record: dict) -> list[str]:
    return [
        str(record.get("name") or "-"),
        str(record.get("kind") or "-"),
        str(record.get("mode") or "-"),
        str(record.get("live") or "-"),
        str(record.get("tab_id") or "-"),
        str(record.get("pane_id") or "-"),
    ]


def cmd_read(args: argparse.Namespace) -> int:
    proc = run(
        [
            "herdr",
            "agent",
            "read",
            args.name,
            "--source",
            "recent-unwrapped",
            "--lines",
            str(args.lines),
        ]
    )
    if proc.returncode != 0:
        raise HerdrError(
            f"agent read {args.name} failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    sys.stdout.write(proc.stdout)
    return 0


def target_rows(args: argparse.Namespace, rows: list[dict]) -> list[dict]:
    latest = latest_rows(rows)
    if args.mine:
        names = [
            row["name"]
            for row in latest.values()
            if row.get("creator_pane") == mine() and row.get("status") == "open"
        ]
    else:
        names = list(args.names)
    if not names:
        raise HerdrError("nothing to close")
    targets = []
    for name in names:
        row = latest.get(name)
        if row is None:
            if not args.force_foreign:
                raise HerdrError(
                    f"{name} is not in {args.ledger}; pass --force-foreign to close it anyway"
                )
            targets.append(
                {
                    "name": name,
                    "status": "open",
                    "creator_pane": mine(),
                    "foreign": True,
                }
            )
            continue
        if row.get("creator_pane") != mine() and not args.force_foreign:
            raise HerdrError(
                f"{name} was created by pane {row.get('creator_pane')}, not this one; pass --force-foreign to close it anyway"
            )
        targets.append(row)
    return targets


def capture_session(row: dict) -> None:
    info = agent_info(row["name"])
    if info and info.get("agent_session"):
        row["session"] = info["agent_session"]


def close_plans(rows: list[dict], targets: list[dict]) -> list[tuple[dict, str]]:
    latest = latest_rows(rows)
    closing = {row["name"] for row in targets}
    plans: list[tuple[dict, str]] = []
    closed_tabs: set[str] = set()
    for row in targets:
        tab_id = row.get("tab_id")
        shared = {
            name
            for name, other in latest.items()
            if other.get("tab_id") == tab_id and other.get("status") == "open"
        }
        owns_tab = bool(row.get("tab_created")) and row.get("creator_pane") == mine()
        if tab_id and tab_id in closed_tabs:
            plans.append((row, "skip"))
        elif tab_id and owns_tab and shared <= closing:
            plans.append((row, "tab"))
            closed_tabs.add(tab_id)
        else:
            plans.append((row, "pane"))
    return plans


def close_row(row: dict, target: str) -> None:
    if target == "tab":
        ok(
            run(["herdr", "tab", "close", str(row["tab_id"])]),
            f"tab close {row['tab_id']}",
        )
    elif target == "pane":
        if not row.get("pane_id"):
            raise HerdrError(f"{row['name']} has no pane_id to close")
        ok(
            run(["herdr", "pane", "close", row["pane_id"]]),
            f"pane close {row['pane_id']}",
        )
    row["status"] = "closed"


def cmd_close(args: argparse.Namespace) -> int:
    rows = read_rows(args.ledger)
    targets = target_rows(args, rows)
    for row in targets:
        capture_session(row)
    for row, target in close_plans(rows, targets):
        close_row(row, target)
    write_rows(args.ledger, [row for row in rows if not row.get("foreign")])
    for row in targets:
        print(f"closed {row['name']}")
    return 0


def resume_argv(row: dict, session: dict) -> list[str]:
    value = session["value"]
    kind = row.get("kind") or session.get("agent") or "pi"
    if kind == "claude":
        return ["--resume", value]
    resumed = ["--session", value]
    if kind == "pi" and row.get("model"):
        resumed.extend(["--model", str(row["model"])])
    return resumed


def start_agent(name: str, kind: str, pane_id: str, agent_args: list[str]) -> None:
    cmd = [
        "herdr",
        "agent",
        "start",
        name,
        "--kind",
        kind,
        "--pane",
        pane_id,
        "--",
        *agent_args,
    ]
    for attempt in range(6):
        proc = run(cmd)
        if proc.returncode == 0:
            return
        if (
            "agent_pane_busy" not in proc.stderr
            and "not an available shell" not in proc.stderr
        ):
            ok(proc, f"agent start {name}")
        if attempt == 5:
            ok(proc, f"agent start {name}")
        time.sleep(1)


def cmd_resume(args: argparse.Namespace) -> int:
    rows = read_rows(args.ledger)
    row = latest_rows(rows).get(args.name)
    if row is None:
        raise HerdrError(f"{args.name} is not in {args.ledger}")
    session = row.get("session") or {}
    if not session.get("value"):
        raise HerdrError(f"{args.name} has no recorded session to resume")
    workspace_id = os.environ.get("HERDR_WORKSPACE_ID")
    if not workspace_id:
        raise HerdrError(
            "Not running with Herdr workspace context (HERDR_WORKSPACE_ID missing)."
        )
    mode = row.get("mode") or WORKER
    cwd = row.get("cwd") or str(Path.cwd())
    kind = row.get("kind") or session.get("agent") or "pi"
    env = ["--env", f"RUARIDH_MODE={WORKER}"] if mode == WORKER else []
    created = ok(
        run(
            [
                "herdr",
                "tab",
                "create",
                "--workspace",
                workspace_id,
                "--cwd",
                cwd,
                "--label",
                args.name,
                "--no-focus",
                *env,
            ]
        ),
        "tab create",
    )
    payload = parse_json(created, "tab create")
    pane_id = find_id(payload, "pane_id")
    if pane_id is None:
        raise HerdrError(
            f"Could not find pane_id in Herdr response:\n{json.dumps(payload, indent=2)}"
        )
    tab_id = find_id(payload, "tab_id")
    start_agent(args.name, kind, pane_id, resume_argv(row, session))
    if args.prompt:
        prompt = (
            f"ruaridh-mode: {WORKER}\n\n{args.prompt}"
            if mode == WORKER
            else args.prompt
        )
        ok(
            run(["herdr", "agent", "prompt", args.name, prompt]),
            f"agent prompt {args.name}",
        )
    row.update(
        {
            "pane_id": pane_id,
            "tab_id": tab_id,
            "tab_created": True,
            "status": "open",
            "session": session,
            "mode": mode,
        }
    )
    write_rows(args.ledger, rows)
    print(f"resumed {args.name} pane={pane_id} tab={tab_id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--ledger",
        type=Path,
        help="Ledger path. Defaults to <cwd>/.herdr-handoffs/panes.jsonl.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    listing = subparsers.add_parser(
        "list", parents=[common], help="Pane ledger rows with live agent status."
    )
    listing.add_argument(
        "--all",
        action="store_true",
        help="Show rows from every creating pane, not just this one.",
    )
    listing.add_argument("--json", action="store_true", help="Print the rows as JSON.")
    listing.set_defaults(func=cmd_list)

    reader = subparsers.add_parser(
        "read", parents=[common], help="Read an agent's recent unwrapped output."
    )
    reader.add_argument("name")
    reader.add_argument("--lines", type=int, default=DEFAULT_LINES)
    reader.set_defaults(func=cmd_read)

    closer = subparsers.add_parser(
        "close", parents=[common], help="Close panes this invocation created."
    )
    closer.add_argument("names", nargs="*")
    closer.add_argument(
        "--mine", action="store_true", help="Close every open pane this pane created."
    )
    closer.add_argument(
        "--force-foreign",
        action="store_true",
        help="Allow closing rows created by another pane.",
    )
    closer.set_defaults(func=cmd_close)

    resumer = subparsers.add_parser(
        "resume", parents=[common], help="Reopen a closed pane with its own session."
    )
    resumer.add_argument("name")
    resumer.add_argument("--prompt", help="Text to send once the agent is ready.")
    resumer.set_defaults(func=cmd_resume)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.ledger = ledger_path(args.ledger)
    try:
        return args.func(args)
    except HerdrError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
