"""bin/skill-lint's structural pass: every SKILL.md, curated or not.

Ported from the retired bin/check-skill-frontmatter. The skills here carry no
`upstream:` key, so only the structural checks run on them.
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "skill_lint", REPO_ROOT / "bin" / "skill_lint.py"
)
assert SPEC is not None and SPEC.loader is not None
skill_lint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skill_lint)

GOOD = """---
name: {name}
description: Use when testing the structural lint.
---

# Demo
"""


def skill(name):
    return GOOD.format(name=name)


def run(root, capsys):
    code = skill_lint.main(["--root", str(root)])
    return code, capsys.readouterr().out


def make_repo(root, *skills):
    (root / "UPSTREAMS.json").write_text('{"upstreams": {}}\n')
    for dir_name, text in skills:
        path = root / ".agents" / "skills" / dir_name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def test_clean_tree_passes(tmp_path, capsys):
    root = make_repo(tmp_path, ("alpha", skill("alpha")), ("beta", skill("beta")))

    code, out = run(root, capsys)

    assert code == 0, out
    assert out == ""


def test_real_skills_pass_the_structural_checks():
    problems = []
    owners = {}
    for skill_md in sorted((REPO_ROOT / ".agents" / "skills").glob("*/SKILL.md")):
        label = skill_lint.skill_label(skill_md.parent.name)
        name, _ = skill_lint.check_structure(skill_md, label, problems)
        owners.setdefault(name, []).append(label)
    skill_lint.check_names(owners, problems)
    assert problems == []


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param(
            "---\nname: demo\ndescription: [unclosed\n---\n",
            "not valid YAML",
            id="invalid-yaml",
        ),
        pytest.param(
            "---\nname: demo\ndescription: Use when: it breaks\n---\n",
            "quote the description",
            id="unquoted-colon",
        ),
        pytest.param("# Demo\n", "no frontmatter", id="no-front-matter"),
        pytest.param("---\n- a\n- b\n---\n", "not a YAML mapping", id="not-a-mapping"),
        pytest.param(
            "---\ndescription: Use when testing.\n---\n",
            "name missing from frontmatter",
            id="missing-name",
        ),
        pytest.param(
            "---\nname: demo\ndescription: ''\n---\n",
            "description missing from frontmatter",
            id="empty-description",
        ),
        pytest.param(
            "---\nname: demo\n---\n",
            "description missing from frontmatter",
            id="missing-description",
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
def test_broken_front_matter_is_reported(tmp_path, capsys, text, expected):
    root = make_repo(tmp_path, ("demo", text))

    code, out = run(root, capsys)

    assert code == 1, out
    assert expected in out
    assert ".agents/skills/demo/SKILL.md" in out


def test_name_must_match_directory(tmp_path, capsys):
    root = make_repo(tmp_path, ("demo", skill("other")))

    code, out = run(root, capsys)

    assert code == 1, out
    assert "does not match directory" in out


def test_duplicate_names_are_reported(tmp_path, capsys):
    root = make_repo(tmp_path, ("demo", skill("demo")), ("demo-again", skill("demo")))

    code, out = run(root, capsys)

    assert code == 1, out
    assert "duplicate skill name" in out


def test_upstream_must_be_a_list_of_mappings(tmp_path, capsys):
    root = make_repo(
        tmp_path,
        ("demo", "---\nname: demo\ndescription: Use when testing.\nupstream: x\n---\n"),
        (
            "other",
            "---\nname: other\ndescription: Use when testing.\nupstream:\n  - x\n---\n",
        ),
    )

    code, out = run(root, capsys)

    assert code == 1, out
    assert ".agents/skills/demo/SKILL.md: upstream is not a list" in out
    assert ".agents/skills/other/SKILL.md: upstream entry 1 is not a mapping" in out


def test_broken_yaml_in_a_curated_skill_is_reported_once(tmp_path, capsys):
    text = (
        "---\nname: demo\ndescription: Use when: it breaks\nupstream:\n"
        "  - repo: nowhere\n    path: x\n    sha: abc\n---\n"
    )
    root = make_repo(tmp_path, ("demo", text))

    code, out = run(root, capsys)

    assert code == 1, out
    assert out.splitlines() == [
        ".agents/skills/demo/SKILL.md: description has ': ' in an unquoted scalar,"
        " which YAML reads as a nested mapping; quote the description"
    ]


def test_folded_description_passes(tmp_path, capsys):
    text = (
        "---\nname: demo\ndescription: >-\n  Use when testing a folded\n"
        "  description, which is valid YAML.\n---\n"
    )
    root = make_repo(tmp_path, ("demo", text))

    code, out = run(root, capsys)

    assert code == 0, out
