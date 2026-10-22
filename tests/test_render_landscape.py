"""bin/render-landscape builds docs/landscape.html from LANDSCAPE.md and its data file."""

import contextlib
import copy
import importlib.util
import io
import sys
import tempfile
import tomllib
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "bin" / "render-landscape"


def load_module():
    loader = SourceFileLoader("render_landscape", str(SCRIPT))
    spec = importlib.util.spec_from_loader("render_landscape", loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["render_landscape"] = module
    loader.exec_module(module)
    return module


rl = load_module()
MARKDOWN = (REPO_ROOT / "LANDSCAPE.md").read_text()
DATA = tomllib.loads((REPO_ROOT / "docs" / "landscape.toml").read_text())


class RenderTests(unittest.TestCase):
    def test_every_landscape_skill_appears_with_its_record_link(self):
        page = rl.build(MARKDOWN, DATA)
        skills = rl.parse_landscape(MARKDOWN).skills
        self.assertGreater(len(skills), 30)
        for name in skills:
            with self.subTest(skill=name):
                self.assertIn(f'id="skill-{name}"', page)
                self.assertIn(f"LANDSCAPE.md#{name}", page)

    def test_skill_without_pitch_fails(self):
        data = copy.deepcopy(DATA)
        del data["pitches"]["grill"]
        with self.assertRaisesRegex(rl.RenderError, "grill"):
            rl.build(MARKDOWN, data)

    def test_skill_without_family_fails(self):
        data = copy.deepcopy(DATA)
        for family in data["families"]:
            if "tdd" in family["skills"]:
                family["skills"].remove("tdd")
        with self.assertRaisesRegex(rl.RenderError, "tdd"):
            rl.build(MARKDOWN, data)

    def test_data_naming_unknown_skill_fails(self):
        data = copy.deepcopy(DATA)
        data["families"][0]["skills"].append("no-such-skill")
        data["pitches"]["no-such-skill"] = "Not in the landscape."
        with self.assertRaisesRegex(rl.RenderError, "no-such-skill"):
            rl.build(MARKDOWN, data)

    def test_check_passes_on_fresh_output_and_fails_on_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "landscape.html"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(rl.main([], target=target), 0)
                self.assertEqual(rl.main(["--check"], target=target), 0)
                target.write_text(target.read_text() + "<!-- stale -->")
                self.assertEqual(rl.main(["--check"], target=target), 1)


if __name__ == "__main__":
    unittest.main()
