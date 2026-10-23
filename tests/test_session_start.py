"""The Claude Code SessionStart hook that injects ruaridh-mode."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / "hooks" / "session-start"

# Claude Code shows only a short preview of SessionStart context longer than
# 10,000 characters and saves the rest to a file, so the real bodies stay under
# it with room for a longer skills-directory path in the header.
CONTEXT_LIMIT = 9_800

FULL_BODY = "FULL-BODY: route this request.\n\nSee references/tooling.md."
SLIM_BODY = "SLIM-BODY: chain in ten lines."


def make_layout(root: Path, full: bool = True, slim: bool = True) -> None:
    skill_dir = root / "ruaridh-mode"
    (skill_dir / "references").mkdir(parents=True)
    if full:
        (skill_dir / "SKILL.md").write_text(
            "---\nname: ruaridh-mode\ndescription: routing\n---\n\n" + FULL_BODY + "\n",
            encoding="utf-8",
        )
    if slim:
        (skill_dir / "references" / "slim.md").write_text(
            SLIM_BODY + "\n", encoding="utf-8"
        )


def run_hook(root: Path, mode: str | None = None) -> str:
    env = {key: value for key, value in os.environ.items() if key != "RUARIDH_MODE"}
    env["RUARIDH_MODE_ROOT"] = str(root)
    if mode is not None:
        env["RUARIDH_MODE"] = mode
    result = subprocess.run(
        [str(HOOK)],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return result.stdout


def additional_context(stdout: str) -> str:
    payload = json.loads(stdout)
    output = payload["hookSpecificOutput"]
    assert output["hookEventName"] == "SessionStart"
    return output["additionalContext"]


class SessionStartHookTest(unittest.TestCase):
    def test_injects_full_body_without_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_layout(root)

            context = additional_context(run_hook(root))

            self.assertIn("ruaridh-mode bootstrap", context)
            self.assertIn(FULL_BODY, context)
            self.assertIn(str(root / "ruaridh-mode" / "references"), context)
            self.assertNotIn("description: routing", context)
            self.assertNotIn("name: ruaridh-mode", context)
            self.assertNotIn(SLIM_BODY, context)

    def test_worker_mode_injects_slim_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_layout(root)

            context = additional_context(run_hook(root, mode="worker"))

            self.assertIn(SLIM_BODY, context)
            self.assertNotIn(FULL_BODY, context)

    def test_missing_body_injects_notice_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_layout(root, full=False, slim=True)

            context = additional_context(run_hook(root))

            self.assertIn("Could not read the ruaridh-mode skill", context)
            self.assertIn(str(root / "ruaridh-mode" / "SKILL.md"), context)

    def test_real_bodies_fit_the_injected_context_limit(self):
        skills = REPO_ROOT / ".claude" / "skills"
        for mode in (None, "worker"):
            context = additional_context(run_hook(skills, mode=mode))
            self.assertLess(len(context), CONTEXT_LIMIT, f"mode={mode}")


if __name__ == "__main__":
    unittest.main()
