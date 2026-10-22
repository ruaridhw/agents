"""bin/check-public fails on a planted private name and fails closed without rules."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bin" / "check-public"


def run(*files, rules=None, rules_env=None):
    env = {"PATH": "/usr/bin:/bin", "PUBLIC_DENYLIST": str(rules)}
    if rules_env is not None:
        env["PUBLIC_DENYLIST_RULES"] = rules_env
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, files)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def write_rules(tmp_path, text="# clients\n\\bacmewidgets\\b\n"):
    rules = tmp_path / "denylist.txt"
    rules.write_text(text)
    return rules


def test_planted_client_name_fails(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("line one\nWork for AcmeWidgets ltd.\n")
    result = run(skill, rules=write_rules(tmp_path))
    assert result.returncode == 1
    assert f"{skill}:2:" in result.stdout


def test_clean_file_passes(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("Nothing private here; acmewidgetsandmore is a different word.\n")
    assert run(skill, rules=write_rules(tmp_path)).returncode == 0


def test_missing_rules_file_fails_closed(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("clean\n")
    result = run(skill, rules=tmp_path / "absent.txt")
    assert result.returncode != 0
    assert "failing closed" in result.stderr


def test_rules_file_with_only_comments_fails_closed(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("clean\n")
    result = run(skill, rules=write_rules(tmp_path, "# nothing\n\n"))
    assert result.returncode != 0
    assert "no rules" in result.stderr


def test_binary_files_are_skipped(tmp_path):
    blob = tmp_path / "font.woff2"
    blob.write_bytes(b"\0acmewidgets\0")
    assert run(blob, rules=write_rules(tmp_path)).returncode == 0


def test_rules_from_env_content_win_over_file(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("Work for AcmeWidgets ltd.\n")
    result = run(skill, rules=tmp_path / "absent.txt", rules_env="\\bacmewidgets\\b\n")
    assert result.returncode == 1
    assert "acmewidgets" in result.stdout


def test_empty_env_content_fails_closed(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("clean\n")
    result = run(skill, rules=write_rules(tmp_path), rules_env="# nothing\n")
    assert result.returncode != 0
    assert "failing closed" in result.stderr
