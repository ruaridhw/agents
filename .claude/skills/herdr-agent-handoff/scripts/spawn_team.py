#!/usr/bin/env python3
"""Spawn a Herdr coordinator plus worker team with shared roster and two-file handoffs."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

NAME_RE = re.compile(r"[a-z][a-z0-9_-]{0,31}")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def ok(proc: subprocess.CompletedProcess[str], label: str) -> str:
    if proc.returncode != 0:
        sys.stderr.write(f"{label} failed\nCOMMAND: {' '.join(proc.args)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}\n")
        raise SystemExit(proc.returncode)
    return proc.stdout


def pane_id(stdout: str) -> str:
    payload = json.loads(stdout)
    stack = [payload]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            value = node.get("pane_id")
            if isinstance(value, str):
                return value
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    raise SystemExit(f"No pane_id in response: {stdout}")


def validate_agent(agent: dict, default_kind: str) -> dict:
    name = agent["name"]
    if not NAME_RE.fullmatch(name):
        raise SystemExit(f"Invalid agent name {name!r}; must match {NAME_RE.pattern}")
    return {
        "name": name,
        "kind": agent.get("kind", default_kind),
        "role": agent.get("role", name),
        "task": agent["task"],
    }


def write_roster(path: Path, agents: list[dict]) -> None:
    lines = ["# Herdr team roster", "", "Each agent has a concise summary file and detailed raw log. Read summaries first.", ""]
    for a in agents:
        lines.extend([
            f"## {a['name']} — {a['role']}",
            f"- Kind: {a['kind']}",
            f"- Summary: {a['summary']}",
            f"- Raw: {a['raw']}",
            f"- Task: {a['task']}",
            "",
        ])
    path.write_text("\n".join(lines))


def start_agent(name: str, kind: str, pid: str) -> None:
    cmd = ["herdr", "agent", "start", name, "--kind", kind, "--pane", pid]
    for attempt in range(6):
        proc = run(cmd)
        if proc.returncode == 0:
            return
        if "agent_pane_busy" not in proc.stderr and "not an available shell" not in proc.stderr:
            ok(proc, f"agent start {name}")
        if attempt == 5:
            ok(proc, f"agent start {name}")
        time.sleep(1)


def create_tab(cwd: Path, label: str) -> str:
    created = ok(run(["herdr", "tab", "create", "--cwd", str(cwd), "--label", label, "--no-focus"]), "tab create")
    return pane_id(created)


def spawn(agent: dict, cwd: Path, root_pane: str, direction: str) -> None:
    split = ok(
        run(["herdr", "pane", "split", "--pane", root_pane, "--direction", direction, "--cwd", str(cwd), "--no-focus"]),
        "pane split",
    )
    pid = pane_id(split)
    start_agent(agent["name"], agent["kind"], pid)

    prompt = f"""ROLE: {agent['role']}
TASK:
{agent['task']}

Team context:
- Roster: {agent['roster']}
- Know the other agents by reading the roster.
- Stay in your role; avoid editing files outside your assigned scope unless the task explicitly requires it.
- If you are the coordinator, wait for worker summary files named in the roster, then integrate summaries; read raw logs only for blockers or missing evidence.

Output contract:
- Write detailed reasoning, commands, diffs, errors, and evidence to: {agent['raw']}
- Write a concise high-level summary to: {agent['summary']}
- The summary must include: outcome, files changed, verification run, blockers, and whether the raw log is needed.
- Do not paste the raw log in chat.
- Final chat response only: HANDOFF_WRITTEN {agent['summary']} {agent['raw']}
"""
    ok(run(["herdr", "agent", "prompt", agent["name"], prompt]), f"agent prompt {agent['name']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team-file", type=Path, required=True, help="JSON file with optional coordinator and workers[].")
    parser.add_argument("--kind", default="pi", help="Default Herdr agent kind.")
    parser.add_argument("--direction", default="right", choices=["right", "down"])
    parser.add_argument("--timeout", default="1200000", help="per-agent wait timeout in ms.")
    parser.add_argument("--handoff-dir", type=Path, help="Defaults to .herdr-handoffs/team-<timestamp>.")
    parser.add_argument("--tab-label", help="Label for the new Herdr tab. Defaults to team name, coordinator name, or first worker.")
    args = parser.parse_args()

    if os.environ.get("HERDR_ENV") != "1":
        sys.stderr.write("Not running inside a Herdr-managed pane (HERDR_ENV=1 missing).\n")
        return 2

    spec = json.loads(args.team_file.read_text())
    agents = []
    if spec.get("coordinator"):
        coord = dict(spec["coordinator"])
        coord.setdefault("role", "coordinator")
        agents.append(validate_agent(coord, args.kind))
    agents.extend(validate_agent(w, args.kind) for w in spec.get("workers", []))
    if not agents:
        raise SystemExit("Team file must define coordinator and/or workers.")

    root = (args.handoff_dir or Path.cwd() / ".herdr-handoffs" / f"team-{int(time.time())}").resolve()
    root.mkdir(parents=True, exist_ok=True)
    roster = root / "roster.md"
    for a in agents:
        a["summary"] = str(root / f"{a['name']}-summary.md")
        a["raw"] = str(root / f"{a['name']}-raw.md")
        a["roster"] = str(roster)
    write_roster(roster, agents)

    tab_label = args.tab_label or spec.get("name") or f"team-{agents[0]['name']}"
    root_pane = create_tab(Path.cwd(), tab_label)
    for a in agents:
        spawn(a, Path.cwd(), root_pane, args.direction)

    print(f"TAB_LABEL={tab_label}")
    print(f"ROSTER={roster}")
    for a in agents:
        wait = run(["herdr", "agent", "wait", a["name"], "--timeout", args.timeout])
        if wait.returncode != 0:
            sys.stderr.write(f"Wait failed for {a['name']}. Inspect: herdr agent read {a['name']} --source recent-unwrapped --lines 120\n")
            sys.stderr.write(wait.stderr)
        summary = Path(a["summary"])
        print(f"\n--- {a['name']} summary ({summary}) ---")
        print(summary.read_text() if summary.exists() else "MISSING SUMMARY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
