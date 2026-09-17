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
    def __init__(self):
        self.commands: list[list[str]] = []

    def run(self, cmd, text=True, capture_output=True, check=False, **kwargs):
        self.commands.append(list(cmd))
        if cmd[:3] == ["herdr", "tab", "create"]:
            return Completed(cmd, json.dumps({"result": {"tab": {"tab_id": "tab-1"}, "pane": {"pane_id": "pane-1"}}}))
        if cmd[:3] == ["herdr", "pane", "split"]:
            return Completed(cmd, json.dumps({"result": {"pane": {"pane_id": f"pane-{len(self.commands)}"}}}))
        if cmd[:3] == ["herdr", "agent", "start"]:
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
        fake = FakeHerdr()
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"HERDR_ENV": "1"}), patch.object(sys, "argv", ["spawn_worker.py", "--name", "api", "--task", "check api"]), patch.object(mod.subprocess, "run", fake.run), patch("os.getcwd", return_value=tmp):
            cwd = os.getcwd()
            with patch.object(Path, "cwd", return_value=Path(cwd)):
                self.assertEqual(mod.main(), 0)

        self.assertIn(["herdr", "tab", "create", "--cwd", cwd, "--label", "api", "--no-focus"], fake.commands)
        self.assertNotIn("split", [part for cmd in fake.commands[:1] for part in cmd])
        self.assertIn(["herdr", "agent", "start", "api", "--kind", "pi", "--pane", "pane-1"], fake.commands)

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
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"HERDR_ENV": "1"}), patch.object(mod.subprocess, "run", fake.run):
            cwd = Path(tmp)
            team_file = cwd / "team.json"
            team_file.write_text(json.dumps(team))
            argv = ["spawn_team.py", "--team-file", str(team_file), "--handoff-dir", str(cwd / "handoffs")]
            with patch.object(sys, "argv", argv), patch.object(Path, "cwd", return_value=cwd):
                self.assertEqual(mod.main(), 0)

        tab_creates = [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "tab", "create"]]
        self.assertEqual(tab_creates, [["herdr", "tab", "create", "--cwd", str(cwd), "--label", "team-coord", "--no-focus"]])
        splits = [cmd for cmd in fake.commands if cmd[:3] == ["herdr", "pane", "split"]]
        self.assertEqual(len(splits), 2)
        for cmd in splits:
            self.assertIn("--pane", cmd)
            self.assertIn("pane-1", cmd)
        self.assertIn(["herdr", "agent", "start", "coord", "--kind", "pi", "--pane", "pane-1"], fake.commands)


if __name__ == "__main__":
    unittest.main()
