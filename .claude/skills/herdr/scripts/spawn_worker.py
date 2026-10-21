#!/usr/bin/env python3
"""Spawn a Herdr sibling agent with a two-file handoff contract."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

WORKER = "worker"
SESSION_ID_KINDS = {"pi", "claude"}


MODE_EXTENSION = (
    Path(__file__).resolve().parents[4] / ".pi" / "extensions" / "ruaridh-mode.ts"
)


def run(
    cmd: list[str], *, input_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, input=input_text, text=True, capture_output=True, check=False
    )


def require_ok(proc: subprocess.CompletedProcess[str], label: str) -> str:
    if proc.returncode != 0:
        sys.stderr.write(
            f"{label} failed\nCOMMAND: {' '.join(proc.args)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}\n"
        )
        raise SystemExit(proc.returncode)
    return proc.stdout


def parse_json(stdout: str, label: str) -> dict:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        sys.stderr.write(f"{label} did not return JSON:\n{stdout}\n")
        raise SystemExit(1)


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


def find_pane_id(payload: dict) -> str:
    # Current Herdr shapes include .result.pane.pane_id for pane split and
    # .result.root_pane.pane_id for tab create. Keep a small recursive fallback
    # so minor envelope changes do not break the helper.
    value = find_id(payload, "pane_id")
    if value is None:
        sys.stderr.write(
            f"Could not find pane_id in Herdr response:\n{json.dumps(payload, indent=2)}\n"
        )
        raise SystemExit(1)
    return value


def valid_agent_name(name: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", name):
        raise argparse.ArgumentTypeError("agent name must match [a-z][a-z0-9_-]{0,31}")
    return name


def mode_env(mode: str) -> list[str]:
    return ["--env", f"RUARIDH_MODE={mode}"] if mode == WORKER else []


def mode_prefix(mode: str) -> str:
    return f"ruaridh-mode: {mode}\n\n" if mode == WORKER else ""


def session_args(kind: str, session_id: str) -> list[str]:
    return ["--session-id", session_id] if kind in SESSION_ID_KINDS else []


def session_record(kind: str, session_id: str) -> dict:
    return {"agent": kind, "kind": "id", "source": "spawn", "value": session_id}


def ledger_row(
    *,
    name: str,
    kind: str,
    model: str | None,
    mode: str,
    tab_id: str | None,
    pane_id: str,
    tab_created: bool,
    cwd: Path,
    summary: Path,
    raw: Path,
    session: dict,
) -> dict:
    return {
        "name": name,
        "kind": kind,
        "model": model,
        "mode": mode,
        "tab_id": tab_id,
        "pane_id": pane_id,
        "tab_created": tab_created,
        "cwd": str(cwd),
        "summary": str(summary),
        "raw": str(raw),
        "session": session,
        "created": datetime.now(UTC).isoformat(timespec="seconds"),
        "creator_pane": os.environ.get("HERDR_PANE_ID"),
        "status": "open",
    }


def append_ledger(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def start_agent(
    name: str, kind: str, pane_id: str, agent_args: list[str] | None = None
) -> None:
    cmd = ["herdr", "agent", "start", name, "--kind", kind, "--pane", pane_id]
    if agent_args:
        cmd.extend(["--", *agent_args])
    for attempt in range(6):
        proc = run(cmd)
        if proc.returncode == 0:
            return
        if (
            "agent_pane_busy" not in proc.stderr
            and "not an available shell" not in proc.stderr
        ):
            require_ok(proc, "agent start")
        if attempt == 5:
            require_ok(proc, "agent start")
        time.sleep(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--task", help="Task to delegate. Use --task-file for long prompts."
    )
    parser.add_argument(
        "--task-file", type=Path, help="File containing the task to delegate."
    )
    parser.add_argument(
        "--name", type=valid_agent_name, default=f"worker-{int(time.time()) % 100000}"
    )
    parser.add_argument(
        "--kind", default="pi", help="Herdr agent kind, e.g. pi, claude, or codex."
    )
    parser.add_argument(
        "--model",
        help="Pi model to pass as --model after Herdr's -- agent-arg separator.",
    )
    parser.add_argument(
        "--lean",
        action="store_true",
        help="Pi only: start with --no-skills --no-extensions --no-prompt-templates (~14.3k -> ~3.8k first-turn baseline). Keeps the AGENTS.md chain; the task text must cite any needed skill files by exact path.",
    )
    parser.add_argument(
        "--agent-arg",
        action="append",
        default=[],
        help="Extra native agent argument. Repeat once per argument.",
    )
    parser.add_argument(
        "--tab-label", help="Label for the new Herdr tab. Defaults to --name."
    )
    parser.add_argument(
        "--mode",
        choices=["worker", "interactive"],
        default="worker",
        help="Worker marks the pane and prompt for the slim mode body; interactive leaves both alone.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Prompt without --wait, print one JSON line, and exit.",
    )
    parser.add_argument(
        "--timeout", default="1200000", help="agent prompt wait timeout in ms."
    )
    parser.add_argument(
        "--summary",
        type=Path,
        help="Summary file path. Defaults under .herdr-handoffs/.",
    )
    parser.add_argument(
        "--raw", type=Path, help="Raw log file path. Defaults under .herdr-handoffs/."
    )
    parser.add_argument(
        "--ledger", type=Path, help="Ledger path. Defaults under .herdr-handoffs/."
    )
    args = parser.parse_args()

    if os.environ.get("HERDR_ENV") != "1":
        sys.stderr.write(
            "Not running inside a Herdr-managed pane (HERDR_ENV=1 missing).\n"
        )
        return 2
    workspace_id = os.environ.get("HERDR_WORKSPACE_ID")
    if not workspace_id:
        sys.stderr.write(
            "Not running with Herdr workspace context (HERDR_WORKSPACE_ID missing).\n"
        )
        return 2

    if bool(args.task) == bool(args.task_file):
        sys.stderr.write("Provide exactly one of --task or --task-file.\n")
        return 2

    task = args.task_file.read_text() if args.task_file else args.task
    cwd = Path.cwd()
    handoff_dir = cwd / ".herdr-handoffs"
    handoff_dir.mkdir(exist_ok=True)
    summary = (args.summary or handoff_dir / f"{args.name}-summary.md").resolve()
    raw = (args.raw or handoff_dir / f"{args.name}-raw.md").resolve()
    summary.parent.mkdir(parents=True, exist_ok=True)
    raw.parent.mkdir(parents=True, exist_ok=True)
    ledger = (args.ledger or handoff_dir / "panes.jsonl").resolve()

    tab_label = args.tab_label or args.name
    tab = require_ok(
        run(
            [
                "herdr",
                "tab",
                "create",
                "--workspace",
                workspace_id,
                "--cwd",
                str(cwd),
                "--label",
                tab_label,
                "--no-focus",
                *mode_env(args.mode),
            ]
        ),
        "tab create",
    )
    tab_payload = parse_json(tab, "tab create")
    pane_id = find_pane_id(tab_payload)
    tab_id = find_id(tab_payload, "tab_id")

    agent_args = []
    if args.model:
        agent_args.extend(["--model", args.model])
    if args.lean and args.kind == "pi":
        agent_args.extend(["--no-skills", "--no-extensions", "--no-prompt-templates"])
        if args.mode == "worker" and MODE_EXTENSION.exists():
            agent_args.extend(["-e", str(MODE_EXTENSION)])
    session_id = str(uuid.uuid4())
    agent_args.extend(session_args(args.kind, session_id))
    agent_args.extend(args.agent_arg)
    start_agent(args.name, args.kind, pane_id, agent_args)

    append_ledger(
        ledger,
        ledger_row(
            name=args.name,
            kind=args.kind,
            model=args.model,
            mode=args.mode,
            tab_id=tab_id,
            pane_id=pane_id,
            tab_created=True,
            cwd=cwd,
            summary=summary,
            raw=raw,
            session=session_record(args.kind, session_id),
        ),
    )

    prompt = f"""{mode_prefix(args.mode)}TASK:
{task}

Shell discipline:
- Batch independent probes into one bash call (e.g. git status && git log && rg -n ...); one pipeline answers what would otherwise take several tool calls.
- Locate with rg first, then read with offset/limit around the hits.
- Read each file once; note the line ranges in your raw log so later steps work from those notes.

Output contract:
- Write detailed reasoning, commands, diffs, errors, and evidence to: {raw}
- Write a concise high-level summary to: {summary}
- The summary must include: outcome, files changed, verification run, blockers, and whether the raw log is needed.
- After both files are written, echo the full summary text in your final chat response.
- Do not paste the raw log in chat.
- Final chat response: the summary, then HANDOFF_WRITTEN {summary} {raw}
"""

    if args.no_wait:
        require_ok(run(["herdr", "agent", "prompt", args.name, prompt]), "agent prompt")
        print(
            json.dumps(
                {
                    "name": args.name,
                    "pane_id": pane_id,
                    "tab_id": tab_id,
                    "summary": str(summary),
                    "raw": str(raw),
                }
            )
        )
        return 0

    proc = run(
        [
            "herdr",
            "agent",
            "prompt",
            args.name,
            prompt,
            "--wait",
            "--timeout",
            args.timeout,
        ]
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.stderr.write("\nWorker may be blocked. Inspect with:\n")
        sys.stderr.write(
            f"herdr agent get {args.name}\nherdr agent read {args.name} --source recent-unwrapped --lines 120\n"
        )
        return proc.returncode

    print(f"SUMMARY={summary}")
    print(f"RAW={raw}")
    if summary.exists():
        print("\n--- summary ---")
        print(summary.read_text())
    else:
        sys.stderr.write("Summary file was not written. Recent worker output:\n")
        recent = run(
            [
                "herdr",
                "agent",
                "read",
                args.name,
                "--source",
                "recent-unwrapped",
                "--lines",
                "120",
            ]
        )
        sys.stderr.write(recent.stdout or recent.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
