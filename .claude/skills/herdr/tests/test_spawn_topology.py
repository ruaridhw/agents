#!/usr/bin/env python3
"""Tests for Herdr handoff helper topology."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

SKILL_DIR = Path(__file__).resolve().parents[1]
MINE = "w-test:p1"


def load_script(name: str):
    path = SKILL_DIR / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
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
    def __init__(self, busy_starts: dict[str, int] | None = None):
        self.commands: list[list[str]] = []
        self.busy_starts = busy_starts or {}

    def run(self, cmd, text=True, capture_output=True, check=False, **kwargs):
        self.commands.append(list(cmd))
        if cmd[:3] == ["herdr", "tab", "create"]:
            return Completed(
                cmd,
                json.dumps(
                    {
                        "result": {
                            "tab": {"tab_id": "tab-1"},
                            "root_pane": {"pane_id": "root-pane"},
                        }
                    }
                ),
            )
        if cmd[:3] == ["herdr", "pane", "split"]:
            return Completed(
                cmd,
                json.dumps(
                    {"result": {"pane": {"pane_id": f"pane-{len(self.commands)}"}}}
                ),
            )
        if cmd[:3] == ["herdr", "pane", "layout"]:
            return Completed(
                cmd,
                json.dumps(
                    {
                        "result": {
                            "layout": {
                                "area": {"height": 80, "width": 120, "x": 0, "y": 0},
                                "panes": [],
                                "splits": [],
                            }
                        }
                    }
                ),
            )
        if cmd[:3] == ["herdr", "pane", "resize"]:
            return Completed(cmd)
        if cmd[:3] == ["herdr", "agent", "start"]:
            name = cmd[3]
            if self.busy_starts.get(name, 0) > 0:
                self.busy_starts[name] -= 1
                return Completed(
                    cmd,
                    stderr='{"error":{"code":"agent_pane_busy","message":"agent target pane is not an available shell"}}',
                    returncode=1,
                )
            return Completed(cmd)
        if cmd[:3] == ["herdr", "agent", "prompt"]:
            prompt = cmd[4]
            marker = "Write a concise high-level summary to: "
            if marker in prompt:
                summary = Path(prompt.split(marker, 1)[1].split("\n", 1)[0])
                summary.write_text("outcome: ok\n")
            return Completed(cmd)
        if cmd[:3] == ["herdr", "agent", "wait"]:
            return Completed(cmd)
        return Completed(cmd)


def ledger_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def prompt_command(fake: FakeHerdr, name: str) -> list[str]:
    matches = [
        cmd
        for cmd in fake.commands
        if cmd[:3] == ["herdr", "agent", "prompt"] and cmd[3] == name
    ]
    assert matches, f"no prompt sent to {name}"
    return matches[-1]


def start_commands(fake: FakeHerdr, name: str) -> list[list[str]]:
    return [
        cmd for cmd in fake.commands if cmd[:4] == ["herdr", "agent", "start", name]
    ]


class SpawnTopologyTest(unittest.TestCase):
    def test_single_worker_defaults_to_worker_mode_and_records_ledger(self):
        mod = load_script("spawn_worker")
        fake = FakeHerdr(busy_starts={"api": 1})
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(
                os.environ,
                {
                    "HERDR_ENV": "1",
                    "HERDR_WORKSPACE_ID": "w-test",
                    "HERDR_PANE_ID": MINE,
                },
            ),
            patch.object(
                sys,
                "argv",
                [
                    "spawn_worker.py",
                    "--name",
                    "api",
                    "--task",
                    "check api",
                    "--model",
                    "fireworks/accounts/fireworks/routers/kimi-latest",
                ],
            ),
            patch.object(mod.subprocess, "run", fake.run),
            patch.object(mod.time, "sleep"),
            patch("os.getcwd", return_value=tmp),
        ):
            cwd = os.getcwd()
            with patch.object(Path, "cwd", return_value=Path(cwd)):
                self.assertEqual(mod.main(), 0)
                rows = ledger_rows(Path(cwd) / ".herdr-handoffs" / "panes.jsonl")

        self.assertIn(
            [
                "herdr",
                "tab",
                "create",
                "--workspace",
                "w-test",
                "--cwd",
                cwd,
                "--label",
                "api",
                "--no-focus",
                "--env",
                "RUARIDH_MODE=worker",
            ],
            fake.commands,
        )
        self.assertNotIn(
            [
                "herdr",
                "pane",
                "split",
                "--pane",
                "root-pane",
                "--direction",
                "right",
                "--cwd",
                cwd,
                "--no-focus",
            ],
            fake.commands,
        )
        starts = start_commands(fake, "api")
        self.assertEqual(len(starts), 2)
        session_id = starts[0][-1]
        self.assertEqual(
            starts[0][:-2],
            [
                "herdr",
                "agent",
                "start",
                "api",
                "--kind",
                "pi",
                "--pane",
                "root-pane",
                "--",
                "--model",
                "fireworks/accounts/fireworks/routers/kimi-latest",
            ],
        )
        self.assertEqual(starts[0][-2], "--session-id")
        self.assertEqual(str(uuid.UUID(session_id)), session_id)
        prompt = prompt_command(fake, "api")
        self.assertEqual(prompt[4].splitlines()[0], "ruaridh-mode: worker")
        self.assertEqual(prompt[-3:], ["--wait", "--timeout", "1200000"])

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["name"], "api")
        self.assertEqual(row["kind"], "pi")
        self.assertEqual(
            row["model"], "fireworks/accounts/fireworks/routers/kimi-latest"
        )
        self.assertEqual(row["mode"], "worker")
        self.assertEqual(row["tab_id"], "tab-1")
        self.assertEqual(row["pane_id"], "root-pane")
        self.assertIs(row["tab_created"], True)
        self.assertEqual(row["cwd"], cwd)
        self.assertEqual(
            row["summary"], str(Path(cwd) / ".herdr-handoffs" / "api-summary.md")
        )
        self.assertEqual(row["raw"], str(Path(cwd) / ".herdr-handoffs" / "api-raw.md"))
        self.assertEqual(row["creator_pane"], MINE)
        self.assertEqual(row["status"], "open")
        self.assertEqual(
            row["session"],
            {"agent": "pi", "kind": "id", "source": "spawn", "value": session_id},
        )

    def test_worker_interactive_mode_leaves_pane_and_prompt_alone(self):
        mod = load_script("spawn_worker")
        fake = FakeHerdr()
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(
                os.environ,
                {
                    "HERDR_ENV": "1",
                    "HERDR_WORKSPACE_ID": "w-test",
                    "HERDR_PANE_ID": MINE,
                },
            ),
            patch.object(
                sys,
                "argv",
                [
                    "spawn_worker.py",
                    "--name",
                    "api",
                    "--task",
                    "check api",
                    "--mode",
                    "interactive",
                ],
            ),
            patch.object(mod.subprocess, "run", fake.run),
            patch.object(mod.time, "sleep"),
            patch.object(Path, "cwd", return_value=Path(tmp)),
        ):
            self.assertEqual(mod.main(), 0)
            rows = ledger_rows(Path(tmp) / ".herdr-handoffs" / "panes.jsonl")

        tab_create = next(
            cmd for cmd in fake.commands if cmd[:3] == ["herdr", "tab", "create"]
        )
        self.assertNotIn("--env", tab_create)
        prompt = prompt_command(fake, "api")
        self.assertEqual(prompt[4].splitlines()[0], "TASK:")
        self.assertEqual(rows[0]["mode"], "interactive")

    def test_worker_passes_a_session_id_to_claude_too(self):
        mod = load_script("spawn_worker")
        fake = FakeHerdr()
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(
                os.environ,
                {
                    "HERDR_ENV": "1",
                    "HERDR_WORKSPACE_ID": "w-test",
                    "HERDR_PANE_ID": MINE,
                },
            ),
            patch.object(
                sys,
                "argv",
                [
                    "spawn_worker.py",
                    "--name",
                    "rev",
                    "--kind",
                    "claude",
                    "--task",
                    "review",
                ],
            ),
            patch.object(mod.subprocess, "run", fake.run),
            patch.object(mod.time, "sleep"),
            patch.object(Path, "cwd", return_value=Path(tmp)),
        ):
            self.assertEqual(mod.main(), 0)
            rows = ledger_rows(Path(tmp) / ".herdr-handoffs" / "panes.jsonl")

        start = start_commands(fake, "rev")[0]
        self.assertEqual(
            start[:8],
            [
                "herdr",
                "agent",
                "start",
                "rev",
                "--kind",
                "claude",
                "--pane",
                "root-pane",
            ],
        )
        self.assertEqual(start[8:10], ["--", "--session-id"])
        self.assertEqual(rows[0]["kind"], "claude")
        self.assertEqual(
            rows[0]["session"],
            {"agent": "claude", "kind": "id", "source": "spawn", "value": start[10]},
        )

    def test_worker_no_wait_skips_wait_and_prints_json(self):
        mod = load_script("spawn_worker")
        fake = FakeHerdr()
        out = io.StringIO()
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(
                os.environ,
                {
                    "HERDR_ENV": "1",
                    "HERDR_WORKSPACE_ID": "w-test",
                    "HERDR_PANE_ID": MINE,
                },
            ),
            patch.object(
                sys,
                "argv",
                [
                    "spawn_worker.py",
                    "--name",
                    "api",
                    "--task",
                    "check api",
                    "--no-wait",
                ],
            ),
            patch.object(mod.subprocess, "run", fake.run),
            patch.object(mod.time, "sleep"),
            patch.object(Path, "cwd", return_value=Path(tmp)),
            contextlib.redirect_stdout(out),
        ):
            self.assertEqual(mod.main(), 0)

        prompt = prompt_command(fake, "api")
        self.assertNotIn("--wait", prompt)
        payload = json.loads(out.getvalue().strip())
        self.assertEqual(
            payload,
            {
                "name": "api",
                "pane_id": "root-pane",
                "tab_id": "tab-1",
                "summary": str(Path(tmp) / ".herdr-handoffs" / "api-summary.md"),
                "raw": str(Path(tmp) / ".herdr-handoffs" / "api-raw.md"),
            },
        )
        self.assertEqual(prompt[4].splitlines()[0], "ruaridh-mode: worker")

    def test_team_creates_one_named_tab_and_splits_remaining_agents_inside_it(self):
        mod = load_script("spawn_team")
        fake = FakeHerdr()
        team = {
            "coordinator": {"name": "coord", "task": "integrate"},
            "workers": [
                {"name": "api", "task": "api"},
                {"name": "db", "task": "db"},
            ],
        }
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(
                os.environ,
                {
                    "HERDR_ENV": "1",
                    "HERDR_WORKSPACE_ID": "w-test",
                    "HERDR_PANE_ID": MINE,
                },
            ),
            patch.object(mod.subprocess, "run", fake.run),
        ):
            cwd = Path(tmp)
            team_file = cwd / "team.json"
            team_file.write_text(json.dumps(team))
            argv = [
                "spawn_team.py",
                "--team-file",
                str(team_file),
                "--handoff-dir",
                str(cwd / "handoffs"),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(Path, "cwd", return_value=cwd),
            ):
                self.assertEqual(mod.main(), 0)
                rows = ledger_rows(cwd / ".herdr-handoffs" / "panes.jsonl")
        tab_creates = [
            cmd for cmd in fake.commands if cmd[:3] == ["herdr", "tab", "create"]
        ]
        self.assertEqual(
            tab_creates,
            [
                [
                    "herdr",
                    "tab",
                    "create",
                    "--workspace",
                    "w-test",
                    "--cwd",
                    str(cwd),
                    "--label",
                    "team-coord",
                    "--no-focus",
                    "--env",
                    "RUARIDH_MODE=worker",
                ]
            ],
        )
        splits = [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "pane", "split"]]
        self.assertEqual(len(splits), 2)
        for cmd in splits:
            self.assertIn("--pane", cmd)
            self.assertIn("root-pane", cmd)
            self.assertEqual(cmd[-2:], ["--env", "RUARIDH_MODE=worker"])
        coord_start = start_commands(fake, "coord")[0]
        self.assertEqual(
            coord_start[:8],
            ["herdr", "agent", "start", "coord", "--kind", "pi", "--pane", "root-pane"],
        )
        self.assertEqual(coord_start[8:10], ["--", "--session-id"])
        self.assertEqual(coord_start[10], rows[0]["session"]["value"])
        for name in ("coord", "api", "db"):
            self.assertEqual(
                prompt_command(fake, name)[4].splitlines()[0], "ruaridh-mode: worker"
            )

        self.assertEqual([row["name"] for row in rows], ["coord", "api", "db"])
        self.assertEqual(rows[0]["pane_id"], "root-pane")
        self.assertEqual(rows[0]["tab_id"], "tab-1")
        self.assertEqual(len({row["tab_id"] for row in rows}), 1)
        self.assertEqual(len({row["pane_id"] for row in rows}), 3)
        self.assertTrue(all(row["tab_created"] for row in rows))
        self.assertTrue(all(row["creator_pane"] == MINE for row in rows))
        self.assertEqual(rows[2]["summary"], str(cwd / "handoffs" / "db-summary.md"))
        for member in rows:
            self.assertEqual(
                member["session"],
                {
                    "agent": "pi",
                    "kind": "id",
                    "source": "spawn",
                    "value": member["session"]["value"],
                },
            )
            self.assertEqual(
                start_commands(fake, member["name"])[0][-1], member["session"]["value"]
            )
        self.assertEqual(len({member["session"]["value"] for member in rows}), 3)

    def test_team_no_wait_skips_agent_wait_and_prints_one_line_per_agent(self):
        mod = load_script("spawn_team")
        fake = FakeHerdr()
        team = {
            "workers": [{"name": "api", "task": "api"}, {"name": "db", "task": "db"}]
        }
        out = io.StringIO()
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(
                os.environ,
                {
                    "HERDR_ENV": "1",
                    "HERDR_WORKSPACE_ID": "w-test",
                    "HERDR_PANE_ID": MINE,
                },
            ),
            patch.object(mod.subprocess, "run", fake.run),
        ):
            cwd = Path(tmp)
            team_file = cwd / "team.json"
            team_file.write_text(json.dumps(team))
            argv = [
                "spawn_team.py",
                "--team-file",
                str(team_file),
                "--handoff-dir",
                str(cwd / "handoffs"),
                "--no-wait",
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(Path, "cwd", return_value=cwd),
                contextlib.redirect_stdout(out),
            ):
                self.assertEqual(mod.main(), 0)

        self.assertEqual(
            [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "agent", "wait"]], []
        )
        lines = [json.loads(line) for line in out.getvalue().strip().splitlines()]
        self.assertEqual([line["name"] for line in lines], ["api", "db"])
        for line in lines:
            self.assertEqual(
                sorted(line), ["name", "pane_id", "raw", "summary", "tab_id"]
            )

    def test_worker_requires_workspace_context(self):
        mod = load_script("spawn_worker")
        fake = FakeHerdr()
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(os.environ, {"HERDR_ENV": "1"}, clear=True),
            patch.object(
                sys, "argv", ["spawn_worker.py", "--name", "api", "--task", "check api"]
            ),
            patch.object(mod.subprocess, "run", fake.run),
            patch.object(Path, "cwd", return_value=Path(tmp)),
        ):
            self.assertEqual(mod.main(), 2)

        self.assertEqual(fake.commands, [])

    def test_equal_width_resize_steps_balance_repeated_right_splits(self):
        mod = load_script("spawn_team")
        layout = {
            "area": {"height": 79, "width": 453, "x": 0, "y": 0},
            "panes": [
                {"pane_id": "pA", "rect": {"height": 79, "width": 29, "x": 0, "y": 0}},
                {"pane_id": "pE", "rect": {"height": 79, "width": 28, "x": 29, "y": 0}},
                {"pane_id": "pD", "rect": {"height": 79, "width": 57, "x": 57, "y": 0}},
                {
                    "pane_id": "pC",
                    "rect": {"height": 79, "width": 113, "x": 114, "y": 0},
                },
                {
                    "pane_id": "pB",
                    "rect": {"height": 79, "width": 226, "x": 227, "y": 0},
                },
            ],
            "splits": [
                {
                    "direction": "right",
                    "ratio": 0.5,
                    "rect": {"height": 79, "width": 453, "x": 0, "y": 0},
                },
                {
                    "direction": "right",
                    "ratio": 0.5,
                    "rect": {"height": 79, "width": 227, "x": 0, "y": 0},
                },
                {
                    "direction": "right",
                    "ratio": 0.5,
                    "rect": {"height": 79, "width": 114, "x": 0, "y": 0},
                },
                {
                    "direction": "right",
                    "ratio": 0.5,
                    "rect": {"height": 79, "width": 57, "x": 0, "y": 0},
                },
            ],
        }

        steps = mod.equal_axis_resize_steps(layout, axis="width")

        self.assertEqual([step[0] for step in steps], ["pC", "pD", "pE"])
        self.assertAlmostEqual(steps[0][1], 0.3)
        self.assertAlmostEqual(steps[1][1], 0.25)
        self.assertAlmostEqual(steps[2][1], 1 / 6)

    def test_team_passes_per_agent_model_args(self):
        mod = load_script("spawn_team")
        fake = FakeHerdr()
        team = {
            "workers": [
                {
                    "name": "reader",
                    "task": "read",
                    "model": "fireworks/accounts/fireworks/routers/glm-fast-latest",
                },
                {
                    "name": "coder",
                    "task": "code",
                    "model": "fixture/reviewer",
                    "agent_args": ["--thinking", "high"],
                },
            ],
        }
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(
                os.environ,
                {
                    "HERDR_ENV": "1",
                    "HERDR_WORKSPACE_ID": "w-test",
                    "HERDR_PANE_ID": MINE,
                },
            ),
            patch.object(mod.subprocess, "run", fake.run),
        ):
            cwd = Path(tmp)
            team_file = cwd / "team.json"
            team_file.write_text(json.dumps(team))
            argv = [
                "spawn_team.py",
                "--team-file",
                str(team_file),
                "--handoff-dir",
                str(cwd / "handoffs"),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(Path, "cwd", return_value=cwd),
            ):
                self.assertEqual(mod.main(), 0)

        reader_start = start_commands(fake, "reader")[0]
        self.assertEqual(
            reader_start[:12],
            [
                "herdr",
                "agent",
                "start",
                "reader",
                "--kind",
                "pi",
                "--pane",
                "root-pane",
                "--",
                "--model",
                "fireworks/accounts/fireworks/routers/glm-fast-latest",
                "--session-id",
            ],
        )
        self.assertEqual(str(uuid.UUID(reader_start[12])), reader_start[12])
        coder_start = start_commands(fake, "coder")[0]
        self.assertEqual(
            coder_start[:14],
            [
                "herdr",
                "agent",
                "start",
                "coder",
                "--kind",
                "pi",
                "--pane",
                "pane-4",
                "--",
                "--model",
                "fixture/reviewer",
                "--thinking",
                "high",
                "--session-id",
            ],
        )


if __name__ == "__main__":
    unittest.main()
