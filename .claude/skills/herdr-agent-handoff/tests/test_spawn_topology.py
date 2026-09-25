#!/usr/bin/env python3
"""Tests for Herdr handoff helper topology."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL_DIR = Path(__file__).resolve().parents[1]


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
            return Completed(cmd, json.dumps({"result": {"tab": {"tab_id": "tab-1"}, "root_pane": {"pane_id": "root-pane"}}}))
        if cmd[:3] == ["herdr", "pane", "split"]:
            return Completed(cmd, json.dumps({"result": {"pane": {"pane_id": f"pane-{len(self.commands)}"}}}))
        if cmd[:3] == ["herdr", "agent", "start"]:
            name = cmd[3]
            if self.busy_starts.get(name, 0) > 0:
                self.busy_starts[name] -= 1
                return Completed(cmd, stderr='{"error":{"code":"agent_pane_busy","message":"agent target pane is not an available shell"}}', returncode=1)
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


class SpawnTopologyTest(unittest.TestCase):
    def test_single_worker_creates_named_tab_for_invocation(self):
        mod = load_script("spawn_worker")
        fake = FakeHerdr(busy_starts={"api": 1})
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"HERDR_ENV": "1", "HERDR_WORKSPACE_ID": "w-test"}), patch.object(sys, "argv", ["spawn_worker.py", "--name", "api", "--task", "check api", "--model", "fireworks/accounts/fireworks/routers/kimi-latest"]), patch.object(mod.subprocess, "run", fake.run), patch.object(mod.time, "sleep"), patch("os.getcwd", return_value=tmp):
            cwd = os.getcwd()
            with patch.object(Path, "cwd", return_value=Path(cwd)):
                self.assertEqual(mod.main(), 0)

        self.assertIn(["herdr", "tab", "create", "--workspace", "w-test", "--cwd", cwd, "--label", "api", "--no-focus"], fake.commands)
        self.assertNotIn(["herdr", "pane", "split", "--pane", "root-pane", "--direction", "right", "--cwd", cwd, "--no-focus"], fake.commands)
        self.assertEqual(fake.commands.count(["herdr", "agent", "start", "api", "--kind", "pi", "--pane", "root-pane", "--", "--model", "fireworks/accounts/fireworks/routers/kimi-latest"]), 2)

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
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"HERDR_ENV": "1", "HERDR_WORKSPACE_ID": "w-test"}), patch.object(mod.subprocess, "run", fake.run):
            cwd = Path(tmp)
            team_file = cwd / "team.json"
            team_file.write_text(json.dumps(team))
            argv = ["spawn_team.py", "--team-file", str(team_file), "--handoff-dir", str(cwd / "handoffs")]
            with patch.object(sys, "argv", argv), patch.object(Path, "cwd", return_value=cwd):
                self.assertEqual(mod.main(), 0)

        tab_creates = [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "tab", "create"]]
        self.assertEqual(tab_creates, [["herdr", "tab", "create", "--workspace", "w-test", "--cwd", str(cwd), "--label", "team-coord", "--no-focus"]])
        splits = [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "pane", "split"]]
        self.assertEqual(len(splits), 2)
        for cmd in splits:
            self.assertIn("--pane", cmd)
            self.assertIn("root-pane", cmd)
        self.assertIn(["herdr", "agent", "start", "coord", "--kind", "pi", "--pane", "root-pane"], fake.commands)

    def test_worker_requires_workspace_context(self):
        mod = load_script("spawn_worker")
        fake = FakeHerdr()
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"HERDR_ENV": "1"}, clear=True), patch.object(sys, "argv", ["spawn_worker.py", "--name", "api", "--task", "check api"]), patch.object(mod.subprocess, "run", fake.run), patch.object(Path, "cwd", return_value=Path(tmp)):
            self.assertEqual(mod.main(), 2)

        self.assertEqual(fake.commands, [])

    def test_team_passes_per_agent_model_args(self):
        mod = load_script("spawn_team")
        fake = FakeHerdr()
        team = {
            "workers": [
                {"name": "reader", "task": "read", "model": "fireworks/accounts/fireworks/routers/glm-fast-latest"},
                {"name": "coder", "task": "code", "model": "fixture/reviewer", "agent_args": ["--thinking", "high"]},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"HERDR_ENV": "1", "HERDR_WORKSPACE_ID": "w-test"}), patch.object(mod.subprocess, "run", fake.run):
            cwd = Path(tmp)
            team_file = cwd / "team.json"
            team_file.write_text(json.dumps(team))
            argv = ["spawn_team.py", "--team-file", str(team_file), "--handoff-dir", str(cwd / "handoffs")]
            with patch.object(sys, "argv", argv), patch.object(Path, "cwd", return_value=cwd):
                self.assertEqual(mod.main(), 0)

        self.assertIn(["herdr", "agent", "start", "reader", "--kind", "pi", "--pane", "root-pane", "--", "--model", "fireworks/accounts/fireworks/routers/glm-fast-latest"], fake.commands)
        self.assertIn(["herdr", "agent", "start", "coder", "--kind", "pi", "--pane", "pane-4", "--", "--model", "fixture/reviewer", "--thinking", "high"], fake.commands)


if __name__ == "__main__":
    unittest.main()
