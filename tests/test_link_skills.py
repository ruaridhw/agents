"""bin/link-skills links the curated skills into a skills directory."""

import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "bin" / "link-skills"


def curated_skill_names():
    """Skills with upstream: stamps, plus own skills that have a LANDSCAPE.md section."""
    names = set()
    for skill_md in (REPO_ROOT / ".agents" / "skills").glob("*/SKILL.md"):
        if re.search(r"^upstream:", skill_md.read_text(encoding="utf-8"), re.M):
            names.add(skill_md.parent.name)
    landscape = (REPO_ROOT / "LANDSCAPE.md").read_text(encoding="utf-8")
    for name in re.findall(r"^## (\S+)$", landscape, re.M):
        if (REPO_ROOT / ".agents" / "skills" / name / "SKILL.md").exists():
            names.add(name)
    return sorted(names)


def load_link_skills():
    loader = SourceFileLoader("link_skills", str(SCRIPT))
    spec = importlib.util.spec_from_loader("link_skills", loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def make_repo(root: Path, names: list[str]) -> Path:
    repo = root / "repo"
    skills = repo / ".agents" / "skills"
    skills.mkdir(parents=True)
    for name in names:
        (skills / name).mkdir()
        (skills / name / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    (repo / "linked-skills.txt").write_text(
        "# curated\n" + "\n".join(names) + "\n", encoding="utf-8"
    )
    return repo


class LinkSkillsTest(unittest.TestCase):
    def setUp(self):
        self.module = load_link_skills()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = make_repo(self.root, ["ruaridh-mode", "clarify"])
        self.module.REPO_ROOT = self.repo
        self.module.SKILLS_LIST = self.repo / "linked-skills.txt"
        self.dest = self.root / "dest"
        self.pi_settings = self.root / "pi" / "settings.json"
        self.pi_dirs = [self.root / "agents-skills", self.root / "pi-skills"]
        self.module.PI_SETTINGS = self.pi_settings
        self.module.PI_SKILL_DIRS = tuple(self.pi_dirs)

    def write_pi_settings(self, packages):
        self.pi_settings.parent.mkdir(parents=True, exist_ok=True)
        self.pi_settings.write_text(
            json.dumps({"packages": packages}), encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.module.main(["--dest", str(self.dest), *args])
        return code, out.getvalue()

    def test_first_run_links_and_second_run_is_idempotent(self):
        code, output = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("link ruaridh-mode", output)
        self.assertEqual(
            (self.dest / "ruaridh-mode").resolve(),
            (self.repo / ".agents" / "skills" / "ruaridh-mode").resolve(),
        )

        code, output = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(
            output.splitlines()[:2], ["ok ruaridh-mode", "ok clarify"], output
        )

    def test_foreign_symlink_is_relinked(self):
        self.dest.mkdir(parents=True)
        foreign = self.root / "elsewhere"
        foreign.mkdir()
        (self.dest / "clarify").symlink_to(foreign)

        code, output = self.run_cli()

        self.assertEqual(code, 0)
        self.assertIn(f"relink clarify: {foreign}", output)
        self.assertEqual(
            (self.dest / "clarify").resolve(),
            (self.repo / ".agents" / "skills" / "clarify").resolve(),
        )

    def test_real_directory_is_a_conflict_and_untouched(self):
        real = self.dest / "clarify"
        real.mkdir(parents=True)
        (real / "keep.txt").write_text("mine", encoding="utf-8")

        code, output = self.run_cli()

        self.assertEqual(code, 1)
        self.assertIn(f"conflict clarify: real directory at {real}", output)
        self.assertFalse(real.is_symlink())
        self.assertEqual((real / "keep.txt").read_text(encoding="utf-8"), "mine")

    def test_check_and_dry_run_change_nothing(self):
        code, output = self.run_cli("--check")
        self.assertEqual(code, 1)
        self.assertIn("would link ruaridh-mode", output)
        self.assertFalse(self.dest.exists())

        code, output = self.run_cli("--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("would link ruaridh-mode", output)
        self.assertFalse(self.dest.exists())

        self.assertEqual(self.run_cli()[0], 0)
        code, output = self.run_cli("--check")
        self.assertEqual(code, 0)
        self.assertEqual(output.splitlines()[:2], ["ok ruaridh-mode", "ok clarify"])

    def test_missing_source_is_skipped(self):
        (self.repo / "linked-skills.txt").write_text(
            "ruaridh-mode\nnot-written-yet\n", encoding="utf-8"
        )

        code, output = self.run_cli()

        self.assertEqual(code, 0)
        self.assertIn("skip not-written-yet: not written yet", output)
        self.assertFalse((self.dest / "not-written-yet").exists())

    def test_pi_package_registered_by_relative_path(self):
        # Pi resolves a relative package against the settings file's directory.
        self.write_pi_settings(["npm:other", {"source": "npm:x"}, "../repo"])

        code, output = self.run_cli()

        self.assertEqual(code, 0)
        self.assertIn("ok pi package", output)

    def test_pi_package_missing_is_reported(self):
        self.write_pi_settings(["npm:pi-recap"])

        code, output = self.run_cli()

        self.assertEqual(code, 1)
        self.assertIn("missing pi package", output)

    def test_no_pi_settings_is_skipped(self):
        code, output = self.run_cli()

        self.assertEqual(code, 0)
        self.assertIn("skip pi package", output)

    def test_pi_dir_copy_collides_but_link_to_repo_does_not(self):
        self.write_pi_settings([str(self.repo)])
        source = self.repo / ".agents" / "skills"
        self.pi_dirs[0].mkdir()
        (self.pi_dirs[0] / "clarify").symlink_to(source / "clarify")
        copy = self.pi_dirs[1] / "ruaridh-mode"
        copy.mkdir(parents=True)
        (copy / "SKILL.md").write_text("# copy\n", encoding="utf-8")

        code, output = self.run_cli()

        self.assertEqual(code, 1)
        self.assertIn(f"duplicate ruaridh-mode: {copy}", output)
        self.assertNotIn("duplicate clarify", output)
        self.assertTrue(copy.exists())

    def test_every_curated_skill_is_listed_once(self):
        listed = self.module.listed_skills(REPO_ROOT / "linked-skills.txt")
        self.assertEqual(len(listed), len(set(listed)), "a name is listed twice")
        self.assertEqual(sorted(listed), curated_skill_names())


if __name__ == "__main__":
    unittest.main()
