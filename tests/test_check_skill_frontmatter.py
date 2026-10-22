"""bin/check-skill-frontmatter passes a clean skill tree and flags every broken rule."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin" / "check-skill-frontmatter"

GOOD = """---
name: {name}
description: Use when testing the front-matter lint.
upstream:
  - repo: self
    path: .claude/skills/{name}/SKILL.md
    sha: {sha}
---

# Demo
"""

SHA = "0123456789abcdef0123456789abcdef01234567"


def skill(name):
    return GOOD.format(name=name, sha=SHA)


def run(root):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def make_repo(root, *skills):
    for dir_name, text in skills:
        path = root / ".claude" / "skills" / dir_name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def output(result):
    return result.stdout + result.stderr


def test_clean_tree_passes(tmp_path):
    root = make_repo(tmp_path, ("alpha", skill("alpha")), ("beta", skill("beta")))

    result = run(root)

    assert result.returncode == 0, output(result)
    assert result.stdout == ""


def test_real_skills_pass():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, output(result)


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param(
            "---\nname: demo\ndescription: Use when: it breaks\n---\n",
            "not valid YAML",
            id="invalid-yaml",
        ),
        pytest.param("# Demo\n", "no front matter", id="no-front-matter"),
        pytest.param(
            "---\ndescription: Use when testing.\n---\n",
            "missing name",
            id="missing-name",
        ),
        pytest.param(
            "---\nname: demo\ndescription: ''\n---\n",
            "missing description",
            id="empty-description",
        ),
        pytest.param(
            "---\nname: demo\n---\n", "missing description", id="missing-description"
        ),
        pytest.param(
            "---\nname: Demo_Skill\ndescription: Use when testing.\n---\n",
            "not lowercase-hyphen",
            id="bad-name-chars",
        ),
        pytest.param(
            f"---\nname: {'a' * 65}\ndescription: Use when testing.\n---\n",
            "longer than 64",
            id="name-too-long",
        ),
        pytest.param(
            f"---\nname: demo\ndescription: {'x' * 1025}\n---\n",
            "longer than 1024",
            id="description-too-long",
        ),
    ],
)
def test_broken_front_matter_is_reported(tmp_path, text, expected):
    root = make_repo(tmp_path, ("demo", text))

    result = run(root)

    assert result.returncode == 1, output(result)
    assert expected in result.stdout
    assert ".claude/skills/demo/SKILL.md" in result.stdout


def test_name_must_match_directory(tmp_path):
    root = make_repo(tmp_path, ("demo", skill("other")))

    result = run(root)

    assert result.returncode == 1, output(result)
    assert "does not match directory" in result.stdout


def test_duplicate_names_are_reported(tmp_path):
    root = make_repo(tmp_path, ("demo", skill("demo")), ("demo-again", skill("demo")))

    result = run(root)

    assert result.returncode == 1, output(result)
    assert "duplicate skill name" in result.stdout


@pytest.mark.parametrize("missing", ["repo", "path", "sha"])
def test_upstream_entries_need_all_fields(tmp_path, missing):
    entry = {"repo": "self", "path": "x/SKILL.md", "sha": SHA}
    entry.pop(missing)
    (first_key, first_value), *rest = entry.items()
    block = f"  - {first_key}: {first_value}\n"
    block += "".join(f"    {key}: {value}\n" for key, value in rest)
    text = f"---\nname: demo\ndescription: Use when testing.\nupstream:\n{block}---\n"
    root = make_repo(tmp_path, ("demo", text))

    result = run(root)

    assert result.returncode == 1, output(result)
    assert f"upstream entry 1 missing {missing}" in result.stdout


def test_folded_description_passes(tmp_path):
    text = (
        "---\nname: demo\ndescription: >-\n  Use when testing a folded\n"
        "  description, which is valid YAML.\n---\n"
    )
    root = make_repo(tmp_path, ("demo", text))

    result = run(root)

    assert result.returncode == 0, output(result)
