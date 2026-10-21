#!/usr/bin/env python3
"""Tests for the Herdr pane ledger helpers."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL_DIR = Path(__file__).resolve().parents[1]
MINE = "w-test:p1"


def load_panes():
    path = SKILL_DIR / "scripts" / "panes.py"
    spec = importlib.util.spec_from_file_location("panes", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Completed:
    def __init__(self, args, stdout="", stderr="", returncode=0):
        self.args = args
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class FakeHerdr:
    def __init__(self, agents: dict[str, dict] | None = None):
        self.commands: list[list[str]] = []
        self.agents = agents or {}

    def run(self, cmd, **kwargs):
        self.commands.append(list(cmd))
        if cmd[:3] == ["herdr", "agent", "get"]:
            name = cmd[3]
            info = self.agents.get(name)
            if info is None:
                return Completed(
                    cmd,
                    json.dumps(
                        {"error": {"code": "agent_not_found"}, "id": "cli:agent:get"}
                    ),
                    returncode=1,
                )
            return Completed(
                cmd,
                json.dumps(
                    {"id": "cli:agent:get", "result": {"agent": {"name": name, **info}}}
                ),
            )
        if cmd[:3] == ["herdr", "tab", "create"]:
            return Completed(
                cmd,
                json.dumps(
                    {
                        "result": {
                            "root_pane": {"pane_id": "pane-new", "tab_id": "tab-new"},
                            "tab": {"tab_id": "tab-new"},
                        }
                    }
                ),
            )
        if cmd[:3] == ["herdr", "agent", "read"]:
            return Completed(cmd, "recent output\n")
        if cmd[:3] in (
            ["herdr", "tab", "close"],
            ["herdr", "pane", "close"],
            ["herdr", "agent", "start"],
            ["herdr", "agent", "prompt"],
        ):
            return Completed(cmd)
        return Completed(cmd, returncode=0)


def row(name: str, **overrides) -> dict:
    base = {
        "name": name,
        "kind": "pi",
        "model": "fireworks/accounts/fireworks/routers/deepseek-flash-latest",
        "mode": "worker",
        "tab_id": "tab-1",
        "pane_id": f"pane-{name}",
        "tab_created": True,
        "cwd": "/tmp/project",
        "summary": f"/tmp/project/.herdr-handoffs/{name}-summary.md",
        "raw": f"/tmp/project/.herdr-handoffs/{name}-raw.md",
        "created": "2026-01-01T00:00:00+00:00",
        "creator_pane": MINE,
        "status": "open",
    }
    base.update(overrides)
    return base


def write_ledger(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(item, sort_keys=True) + "\n" for item in rows))


def read_ledger(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


SESSION_CLAUDE = {
    "agent": "claude",
    "kind": "id",
    "source": "herdr:claude",
    "value": "11111111-2222-3333-4444-555555555555",
}
SESSION_PI = {
    "agent": "pi",
    "kind": "path",
    "source": "herdr:pi",
    "value": "/home/x/.pi/agent/sessions/--tmp-project--/2026-01-01T00-00-00-000Z_abc.jsonl",
}
SESSION_SPAWN_PI = {
    "agent": "pi",
    "kind": "id",
    "source": "spawn",
    "value": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
}
SESSION_SPAWN_CLAUDE = {
    "agent": "claude",
    "kind": "id",
    "source": "spawn",
    "value": "ffffffff-1111-4222-8333-444444444444",
}


class PanesTest(unittest.TestCase):
    def run_panes(
        self, mod, argv: list[str], fake: FakeHerdr, env: dict[str, str]
    ) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with (
            patch.dict(os.environ, env),
            patch.object(mod, "run", fake.run),
            patch.object(sys, "argv", ["panes.py", *argv]),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(err),
        ):
            code = mod.main()
        return code, out.getvalue(), err.getvalue()

    def test_list_shows_only_rows_this_pane_created_with_live_status(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger,
                [
                    row("mine-idle"),
                    row("mine-gone"),
                    row("theirs", creator_pane="w-test:p9"),
                    row("mine-closed", status="closed"),
                ],
            )
            fake = FakeHerdr(
                {
                    "mine-idle": {"agent_status": "idle"},
                    "theirs": {"agent_status": "working"},
                }
            )
            code, out, _ = self.run_panes(
                mod, ["list", "--ledger", str(ledger)], fake, {"HERDR_PANE_ID": MINE}
            )

        self.assertEqual(code, 0)
        self.assertIn("mine-idle", out)
        self.assertIn("mine-gone", out)
        self.assertNotIn("theirs", out)
        self.assertIn("missing", out)
        self.assertIn("closed", out)
        self.assertTrue(out.startswith("NAME"))

    def test_list_all_and_json_include_foreign_rows(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger, [row("mine-idle"), row("theirs", creator_pane="w-test:p9")]
            )
            fake = FakeHerdr(
                {
                    "mine-idle": {"agent_status": "idle"},
                    "theirs": {"agent_status": "working"},
                }
            )
            code, out, _ = self.run_panes(
                mod,
                ["list", "--all", "--json", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )

        self.assertEqual(code, 0)
        records = json.loads(out)
        self.assertEqual(
            [record["name"] for record in records], ["mine-idle", "theirs"]
        )
        self.assertEqual(
            {record["name"]: record["live"] for record in records},
            {"mine-idle": "idle", "theirs": "working"},
        )

    def test_read_uses_recent_unwrapped_lines(self):
        mod = load_panes()
        fake = FakeHerdr({"agent-a": {"agent_status": "idle"}})
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(ledger, [row("agent-a")])
            code, out, _ = self.run_panes(
                mod,
                ["read", "agent-a", "--lines", "25", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )

        self.assertEqual(code, 0)
        self.assertEqual(
            fake.commands,
            [
                [
                    "herdr",
                    "agent",
                    "read",
                    "agent-a",
                    "--source",
                    "recent-unwrapped",
                    "--lines",
                    "25",
                ]
            ],
        )
        self.assertEqual(out, "recent output\n")

    def test_close_captures_session_then_closes_whole_created_tab(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger, [row("agent-a", tab_id="tab-1"), row("agent-b", tab_id="tab-1")]
            )
            fake = FakeHerdr(
                {
                    "agent-a": {"agent_status": "idle", "agent_session": SESSION_PI},
                    "agent-b": {"agent_status": "idle", "agent_session": SESSION_PI},
                }
            )
            code, out, _ = self.run_panes(
                mod,
                ["close", "agent-a", "agent-b", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 0)
        closes = [
            cmd
            for cmd in fake.commands
            if cmd[:2] in (["herdr", "tab"], ["herdr", "pane"]) and cmd[2] == "close"
        ]
        self.assertEqual(closes, [["herdr", "tab", "close", "tab-1"]])
        gets = [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "agent", "get"]]
        self.assertEqual(
            gets,
            [
                ["herdr", "agent", "get", "agent-a"],
                ["herdr", "agent", "get", "agent-b"],
            ],
        )
        self.assertLess(fake.commands.index(gets[0]), fake.commands.index(closes[0]))
        self.assertEqual([item["status"] for item in rows], ["closed", "closed"])
        self.assertEqual(rows[0]["session"], SESSION_PI)
        self.assertIn("closed agent-a", out)

    def test_close_closes_only_the_pane_when_siblings_stay_open(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger, [row("agent-a", tab_id="tab-1"), row("agent-b", tab_id="tab-1")]
            )
            fake = FakeHerdr(
                {"agent-a": {"agent_status": "idle", "agent_session": SESSION_PI}}
            )
            code, _, _ = self.run_panes(
                mod,
                ["close", "agent-a", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 0)
        closes = [
            cmd
            for cmd in fake.commands
            if cmd[:2] in (["herdr", "tab"], ["herdr", "pane"]) and cmd[2] == "close"
        ]
        self.assertEqual(closes, [["herdr", "pane", "close", "pane-agent-a"]])
        self.assertEqual([item["status"] for item in rows], ["closed", "open"])

    def test_close_uses_pane_close_for_tabs_it_did_not_create(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(ledger, [row("agent-a", tab_created=False, tab_id="tab-1")])
            fake = FakeHerdr(
                {"agent-a": {"agent_status": "idle", "agent_session": SESSION_PI}}
            )
            code, _, _ = self.run_panes(
                mod,
                ["close", "agent-a", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )

        self.assertEqual(code, 0)
        closes = [
            cmd
            for cmd in fake.commands
            if cmd[:2] in (["herdr", "tab"], ["herdr", "pane"]) and cmd[2] == "close"
        ]
        self.assertEqual(closes, [["herdr", "pane", "close", "pane-agent-a"]])

    def test_close_mine_closes_every_open_row_of_this_pane(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger,
                [
                    row("agent-a", tab_id="tab-1", tab_created=False),
                    row("agent-b", tab_id="tab-2"),
                    row("agent-c", tab_id="tab-3", status="closed"),
                    row("theirs", tab_id="tab-4", creator_pane="w-test:p9"),
                ],
            )
            fake = FakeHerdr(
                {
                    name: {"agent_status": "idle", "agent_session": SESSION_PI}
                    for name in ("agent-a", "agent-b", "theirs")
                }
            )
            code, _, _ = self.run_panes(
                mod,
                ["close", "--mine", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )
            rows = {item["name"]: item for item in read_ledger(ledger)}

        self.assertEqual(code, 0)
        closes = [
            cmd
            for cmd in fake.commands
            if cmd[:2] in (["herdr", "tab"], ["herdr", "pane"]) and cmd[2] == "close"
        ]
        self.assertEqual(
            closes,
            [
                ["herdr", "pane", "close", "pane-agent-a"],
                ["herdr", "tab", "close", "tab-2"],
            ],
        )
        self.assertEqual(rows["agent-a"]["status"], "closed")
        self.assertEqual(rows["agent-b"]["status"], "closed")
        self.assertEqual(rows["agent-c"]["status"], "closed")
        self.assertEqual(rows["theirs"]["status"], "open")

    def test_close_refuses_foreign_rows(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(ledger, [row("theirs", creator_pane="w-test:p9")])
            fake = FakeHerdr(
                {"theirs": {"agent_status": "idle", "agent_session": SESSION_PI}}
            )
            code, _, err = self.run_panes(
                mod,
                ["close", "theirs", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 1)
        self.assertIn("w-test:p9", err)
        self.assertEqual([cmd for cmd in fake.commands if cmd[2:3] == ["close"]], [])
        self.assertEqual(rows[0]["status"], "open")

    def test_close_refuses_agents_missing_from_the_ledger(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(ledger, [])
            fake = FakeHerdr({})
            code, _, err = self.run_panes(
                mod,
                ["close", "stranger", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 1)
        self.assertIn("not in", err)
        self.assertEqual(rows, [])

    def test_close_force_foreign_closes_a_pane_without_recording_it(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(ledger, [row("theirs", creator_pane="w-test:p9")])
            fake = FakeHerdr(
                {"theirs": {"agent_status": "idle", "agent_session": SESSION_PI}}
            )
            code, _, _ = self.run_panes(
                mod,
                ["close", "theirs", "--force-foreign", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 0)
        self.assertEqual(
            [cmd for cmd in fake.commands if cmd[2:3] == ["close"]],
            [["herdr", "pane", "close", "pane-theirs"]],
        )
        self.assertEqual(rows[0]["status"], "closed")
        self.assertEqual(rows[0]["session"], SESSION_PI)

    def test_close_keeps_the_session_recorded_at_spawn_when_herdr_reports_none(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger,
                [
                    row(
                        "agent-p",
                        cwd="/tmp/project",
                        tab_created=False,
                        session=SESSION_SPAWN_PI,
                    )
                ],
            )
            fake = FakeHerdr({"agent-p": {"agent_status": "idle"}})
            code, _, _ = self.run_panes(
                mod,
                ["close", "agent-p", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 0)
        self.assertEqual(rows[0]["status"], "closed")
        self.assertEqual(rows[0]["session"], SESSION_SPAWN_PI)

    def test_close_prefers_the_session_herdr_reports(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger,
                [
                    row(
                        "agent-p",
                        cwd="/tmp/project",
                        tab_created=False,
                        session=SESSION_SPAWN_PI,
                    )
                ],
            )
            fake = FakeHerdr(
                {"agent-p": {"agent_status": "idle", "agent_session": SESSION_PI}}
            )
            code, _, _ = self.run_panes(
                mod,
                ["close", "agent-p", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 0)
        self.assertEqual(rows[0]["session"], SESSION_PI)

    def test_resume_reopens_a_closed_claude_row(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger,
                [
                    row(
                        "agent-c",
                        kind="claude",
                        status="closed",
                        session=SESSION_SPAWN_CLAUDE,
                        cwd="/tmp/project",
                    )
                ],
            )
            fake = FakeHerdr({"agent-c": {"agent_status": "idle"}})
            code, out, _ = self.run_panes(
                mod,
                [
                    "resume",
                    "agent-c",
                    "--prompt",
                    "Say READY2",
                    "--ledger",
                    str(ledger),
                ],
                fake,
                {"HERDR_PANE_ID": MINE, "HERDR_WORKSPACE_ID": "w-test"},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 0)
        self.assertIn(
            [
                "herdr",
                "tab",
                "create",
                "--workspace",
                "w-test",
                "--cwd",
                "/tmp/project",
                "--label",
                "agent-c",
                "--no-focus",
                "--env",
                "RUARIDH_MODE=worker",
            ],
            fake.commands,
        )
        self.assertIn(
            [
                "herdr",
                "agent",
                "start",
                "agent-c",
                "--kind",
                "claude",
                "--pane",
                "pane-new",
                "--",
                "--resume",
                SESSION_SPAWN_CLAUDE["value"],
            ],
            fake.commands,
        )
        prompts = [
            cmd for cmd in fake.commands if cmd[:3] == ["herdr", "agent", "prompt"]
        ]
        self.assertEqual(
            prompts,
            [
                [
                    "herdr",
                    "agent",
                    "prompt",
                    "agent-c",
                    "(aimsg) ruaridh-mode: worker\n\nSay READY2",
                ]
            ],
        )
        self.assertEqual(rows[0]["status"], "open")
        self.assertEqual(rows[0]["pane_id"], "pane-new")
        self.assertEqual(rows[0]["tab_id"], "tab-new")
        self.assertIs(rows[0]["tab_created"], True)
        self.assertEqual(rows[0]["session"], SESSION_SPAWN_CLAUDE)
        self.assertIn("resumed agent-c", out)

    def test_resume_reopens_a_closed_pi_row_with_its_model(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger,
                [row("agent-p", status="closed", session=SESSION_SPAWN_PI)],
            )
            fake = FakeHerdr({"agent-p": {"agent_status": "idle"}})
            code, _, _ = self.run_panes(
                mod,
                ["resume", "agent-p", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE, "HERDR_WORKSPACE_ID": "w-test"},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 0)
        self.assertIn(
            [
                "herdr",
                "agent",
                "start",
                "agent-p",
                "--kind",
                "pi",
                "--pane",
                "pane-new",
                "--",
                "--session",
                SESSION_SPAWN_PI["value"],
                "--model",
                "fireworks/accounts/fireworks/routers/deepseek-flash-latest",
            ],
            fake.commands,
        )
        self.assertEqual(
            [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "agent", "prompt"]],
            [],
        )
        self.assertEqual(rows[0]["session"], SESSION_SPAWN_PI)

    def test_resume_uses_the_session_a_close_captured_from_herdr(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(ledger, [row("agent-p", status="closed", session=SESSION_PI)])
            fake = FakeHerdr({"agent-p": {"agent_status": "idle"}})
            code, _, _ = self.run_panes(
                mod,
                ["resume", "agent-p", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE, "HERDR_WORKSPACE_ID": "w-test"},
            )

        self.assertEqual(code, 0)
        self.assertIn(
            [
                "herdr",
                "agent",
                "start",
                "agent-p",
                "--kind",
                "pi",
                "--pane",
                "pane-new",
                "--",
                "--session",
                SESSION_PI["value"],
                "--model",
                "fireworks/accounts/fireworks/routers/deepseek-flash-latest",
            ],
            fake.commands,
        )

    def test_resume_interactive_row_skips_worker_env(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(
                ledger,
                [
                    row(
                        "agent-i",
                        mode="interactive",
                        status="closed",
                        session=SESSION_PI,
                    )
                ],
            )
            fake = FakeHerdr({"agent-i": {"agent_status": "idle"}})
            code, _, _ = self.run_panes(
                mod,
                ["resume", "agent-i", "--prompt", "hello", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE, "HERDR_WORKSPACE_ID": "w-test"},
            )

        self.assertEqual(code, 0)
        tab_create = next(
            cmd for cmd in fake.commands if cmd[:3] == ["herdr", "tab", "create"]
        )
        self.assertNotIn("--env", tab_create)
        prompts = [
            cmd for cmd in fake.commands if cmd[:3] == ["herdr", "agent", "prompt"]
        ]
        self.assertEqual(
            prompts, [["herdr", "agent", "prompt", "agent-i", "(aimsg) hello"]]
        )

    def test_resume_errors_without_a_recorded_session(self):
        mod = load_panes()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "panes.jsonl"
            write_ledger(ledger, [row("agent-x", status="closed")])
            fake = FakeHerdr({})
            code, _, err = self.run_panes(
                mod,
                ["resume", "agent-x", "--ledger", str(ledger)],
                fake,
                {"HERDR_PANE_ID": MINE, "HERDR_WORKSPACE_ID": "w-test"},
            )
            rows = read_ledger(ledger)

        self.assertEqual(code, 1)
        self.assertIn("no recorded session", err)
        self.assertEqual(
            [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "tab", "create"]], []
        )
        self.assertEqual(rows[0]["status"], "closed")


if __name__ == "__main__":
    unittest.main()
