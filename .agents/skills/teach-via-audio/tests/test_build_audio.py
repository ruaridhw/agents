"""Behaviour of the voicenote builder that needs no network: parsing, lint, stitch plan, key handling."""

import os
import runpy
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts/build_audio.py"
EXAMPLE = SKILL / "examples/script.md"
mod = runpy.run_path(str(SCRIPT))
GAPS = {"title_after": 2.0, "heading_before": 2.2, "heading_after": 1.5, "para": 0.8}


def no_key_env():
    return {k: v for k, v in os.environ.items() if k != "ELEVENLABS_API_KEY"}


class Parse(unittest.TestCase):
    def test_kinds(self):
        parts = mod["parse"]("# T\n\n## H\n\nOne.\n\n\nTwo.\n")
        self.assertEqual(parts, [("title", "T"), ("heading", "H"), ("para", "One."), ("para", "Two.")])

    def test_example_is_lint_clean(self):
        parts = mod["parse"](EXAMPLE.read_text())
        self.assertEqual(mod["lint"](parts), [])
        self.assertEqual(parts[0][0], "title")

    def test_lint_flags_ear_hostile_text(self):
        parts = mod["parse"]("# T\n\nCosts 40 pounds (roughly).\n\n- a bullet\n\nSee https://x.test and `code`.")
        issues = " ".join(mod["lint"](parts))
        for needle in ("parentheses", "digits", "list markers", "markdown or URL"):
            self.assertIn(needle, issues)


class Plan(unittest.TestCase):
    def test_gaps(self):
        parts = [("title", "T"), ("heading", "H"), ("para", "a"), ("para", "b"), ("heading", "H2"), ("para", "c")]
        self.assertEqual(mod["plan"](parts, GAPS), [
            ("say", 0), ("pause", 2.2), ("say", 1), ("pause", 1.5), ("say", 2), ("pause", 0.8),
            ("say", 3), ("pause", 2.2), ("say", 4), ("pause", 1.5), ("say", 5)])

    def test_no_trailing_or_leading_pause(self):
        steps = mod["plan"]([("heading", "H"), ("para", "a")], GAPS)
        self.assertEqual(steps[0], ("say", 0))
        self.assertEqual(steps[-1], ("say", 1))


class Key(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.cache = Path(self.dir.name) / "key"

    def tearDown(self):
        self.dir.cleanup()

    def test_env_wins(self):
        with mock.patch.dict(os.environ, {"ELEVENLABS_API_KEY": " k1 "}):
            self.assertEqual(mod["get_key"](None, self.cache), "k1")
        self.assertFalse(self.cache.exists())

    def test_key_cmd_is_cached_with_mode_0600_and_run_once(self):
        with mock.patch.dict(os.environ, no_key_env(), clear=True):
            self.assertEqual(mod["get_key"]("echo secret", self.cache), "secret")
            self.assertEqual(stat.S_IMODE(self.cache.stat().st_mode), 0o600)
            self.assertEqual(mod["get_key"]("exit 1", self.cache), "secret")

    def test_missing_key_exits_with_guidance(self):
        with mock.patch.dict(os.environ, no_key_env(), clear=True), self.assertRaises(SystemExit) as cm:
            mod["get_key"](None, self.cache)
        self.assertIn("--key-cmd", str(cm.exception))


class Cli(unittest.TestCase):
    def test_dry_run_needs_no_key_and_reports_length(self):
        r = subprocess.run([sys.executable, str(SCRIPT), str(EXAMPLE), "--dry-run"],
                           capture_output=True, text=True, env=no_key_env())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("words, about", r.stdout)
        self.assertIn("lint clean", r.stdout)


if __name__ == "__main__":
    unittest.main()
