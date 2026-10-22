"""bin/skill-lint: one fixture repo per check, real git, no mocks of the logic."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "skill_lint", REPO_ROOT / "bin" / "skill_lint.py"
)
assert SPEC is not None and SPEC.loader is not None
skill_lint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skill_lint)

SKILL_PATH = ".claude/skills/demo/SKILL.md"
FEED_PATH = "skill/SKILL.md"
USE_DESCRIPTION = "Use when testing the linter."


def git(cwd, *args):
    import subprocess

    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "Test")
    return path


def commit_all(path, message):
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", message)
    return git(path, "rev-parse", "HEAD")


def make_upstream(root, name="demo", path=FEED_PATH):
    clone = init_repo(root / "upstream" / name)
    feed = clone / path
    feed.parent.mkdir(parents=True, exist_ok=True)
    feed.write_text("upstream v1\n")
    return commit_all(clone, "first")


def write_registry(root, entries):
    path = root / "UPSTREAMS.json"
    path.write_text(json.dumps({"upstreams": entries}, indent=2) + "\n")
    return path


def write_skill(
    root,
    name="demo",
    dir_name=None,
    description=USE_DESCRIPTION,
    feeds=(),
    frontmatter=(),
    body="# Demo\n",
):
    path = root / ".claude/skills" / (dir_name or name) / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    if name is not None:
        lines.append(f"name: {name}")
    if description is not None:
        lines.append(f"description: {description}")
    if feeds is not None:
        if not feeds:
            lines.append("upstream: []")
        else:
            lines.append("upstream:")
            for repo, feed_path, sha in feeds:
                lines += [
                    f"  - repo: {repo}",
                    f"    path: {feed_path}",
                    f"    sha: {sha}",
                ]
    lines += list(frontmatter)
    lines += ["---", "", body]
    path.write_text("\n".join(lines))
    return path


def run(root, *names):
    return skill_lint.main(["--root", str(root), *names])


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    rules = tmp_path / "denylist.txt"
    rules.write_text("# planted private name\n\\bzzplantedname\\b\n")
    monkeypatch.setenv("PUBLIC_DENYLIST", str(rules))
    monkeypatch.setenv(
        "SKILL_UPSTREAM_LOCAL_CONFIG", str(tmp_path / "absent-local-config.json")
    )
    return rules


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    sha = make_upstream(root)
    write_registry(root, {"demo": {"url": "https://example.invalid/demo", "sha": sha}})
    write_skill(root, feeds=[("demo", FEED_PATH, sha)])
    return root


@pytest.fixture
def sha_of():
    def read(root, name="demo"):
        return git(root / "upstream" / name, "rev-parse", "HEAD")

    return read


def test_clean_fixture_passes(repo, capsys):
    assert run(repo) == 0
    assert capsys.readouterr().out == ""


def test_clean_fixture_passes_for_a_named_skill(repo, capsys):
    assert run(repo, "demo") == 0
    assert capsys.readouterr().out == ""


def test_directory_path_at_sha_is_fine(repo, sha_of):
    sha = sha_of(repo)
    write_skill(repo, feeds=[("demo", "skill", sha)])
    assert run(repo) == 0


def test_unknown_skill_name_is_a_usage_error(repo, capsys):
    assert run(repo, "nope") == 2
    assert "unknown curated skill" in capsys.readouterr().err


def test_non_curated_skills_are_ignored(repo):
    write_skill(repo, name="retired", description="no when-to-use here", feeds=None)
    assert run(repo) == 0


def test_empty_upstream_list_still_counts_as_curated(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    write_registry(root, {})
    write_skill(root, description="Not phrased as a trigger.", feeds=[])
    assert run(root) == 1


def test_name_mismatch_fails(repo, sha_of, capsys):
    write_skill(
        repo, name="other", dir_name="demo", feeds=[("demo", FEED_PATH, sha_of(repo))]
    )
    assert run(repo) == 1
    out = capsys.readouterr().out
    assert f"{SKILL_PATH}: name 'other' does not match directory 'demo'" in out


def test_missing_name_fails(repo, sha_of, capsys):
    write_skill(
        repo, name=None, dir_name="demo", feeds=[("demo", FEED_PATH, sha_of(repo))]
    )
    assert run(repo) == 1
    assert "name missing from frontmatter" in capsys.readouterr().out


def test_description_without_a_use_sentence_fails(repo, sha_of, capsys):
    write_skill(
        repo, description="Plans the build.", feeds=[("demo", FEED_PATH, sha_of(repo))]
    )
    assert run(repo) == 1
    assert "not phrased as when-to-use" in capsys.readouterr().out


def test_missing_description_fails(repo, sha_of, capsys):
    write_skill(repo, description=None, feeds=[("demo", FEED_PATH, sha_of(repo))])
    assert run(repo) == 1
    assert "description missing from frontmatter" in capsys.readouterr().out


@pytest.mark.parametrize(
    "prefix", ["Use when", "Use whenever", "Use for", "Use after", "Use to", "Use if"]
)
def test_use_sentence_variants_pass(repo, sha_of, prefix):
    write_skill(
        repo,
        description=f"Something. {prefix} testing.",
        feeds=[("demo", FEED_PATH, sha_of(repo))],
    )
    assert run(repo) == 0


def test_unknown_upstream_repo_fails(repo, sha_of, capsys):
    write_skill(repo, feeds=[("nowhere", FEED_PATH, sha_of(repo))])
    assert run(repo) == 1
    assert "is not a key of UPSTREAMS.json" in capsys.readouterr().out


def test_short_sha_fails(repo, capsys):
    write_skill(repo, feeds=[("demo", FEED_PATH, "abc123")])
    assert run(repo) == 1
    assert "sha 'abc123' is not 40 hex" in capsys.readouterr().out


def test_missing_feed_field_fails(repo, sha_of, capsys):
    path = write_skill(repo, feeds=[("demo", "", sha_of(repo))])
    assert run(repo) == 1
    assert "upstream entry 1 has no path" in capsys.readouterr().out
    assert path.exists()


def test_path_absent_at_sha_fails(repo, sha_of, capsys):
    write_skill(repo, feeds=[("demo", "skill/absent.md", sha_of(repo))])
    assert run(repo) == 1
    assert "'skill/absent.md' missing at" in capsys.readouterr().out


def test_sha_not_in_clone_fails(repo, capsys):
    write_skill(repo, feeds=[("demo", FEED_PATH, "0" * 40)])
    assert run(repo) == 1
    assert "not in upstream 'demo'" in capsys.readouterr().out


def test_missing_clone_is_a_problem_not_a_skip(tmp_path, sha_of):
    root = tmp_path / "repo"
    root.mkdir()
    write_registry(
        root, {"demo": {"url": "https://example.invalid/demo", "sha": "0" * 40}}
    )
    write_skill(root, feeds=[("demo", FEED_PATH, "0" * 40)])
    assert run(root) == 1


def test_missing_clone_message_says_sync(repo, capsys):
    import shutil

    sha = git(repo / "upstream" / "demo", "rev-parse", "HEAD")
    shutil.rmtree(repo / "upstream" / "demo")
    write_skill(repo, feeds=[("demo", FEED_PATH, sha)])
    assert run(repo) == 1
    out = capsys.readouterr().out
    assert "clone missing: run bin/skill-upstream sync" in out
    assert out.count("clone missing") == 1


def test_self_upstream_resolves_against_the_repo(repo):
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    root_sha = commit_all(repo, "skills")
    write_registry(repo, {"self": {"self": True}})
    write_skill(repo, feeds=[("self", SKILL_PATH, root_sha)])
    assert run(repo) == 0


def test_unconfigured_local_upstream_is_reported_but_not_fatal(repo, sha_of, capsys):
    sha = sha_of(repo)
    write_registry(repo, {"demo": {"local": True, "sha": "0" * 40}})
    write_skill(repo, feeds=[("demo", FEED_PATH, sha), ("demo", FEED_PATH, sha)])
    assert run(repo) == 0
    out = capsys.readouterr().out
    assert out.count("unconfigured on this machine") == 1


def test_configured_local_upstream_is_linted(repo, sha_of, tmp_path, monkeypatch):
    sha = sha_of(repo)
    write_registry(repo, {"demo": {"local": True, "sha": sha}})
    config = tmp_path / "local.json"
    config.write_text(json.dumps({"demo": {"url": str(repo / "upstream" / "demo")}}))
    monkeypatch.setenv("SKILL_UPSTREAM_LOCAL_CONFIG", str(config))
    write_skill(repo, feeds=[("demo", FEED_PATH, sha)])
    assert run(repo) == 0


def test_planted_private_name_fails_via_check_public(repo, sha_of, capsys):
    write_skill(
        repo,
        feeds=[("demo", FEED_PATH, sha_of(repo))],
        body="# Demo\n\nWorks for ZZPlantedName ltd.\n",
    )
    assert run(repo) == 1
    out = capsys.readouterr().out
    assert "check-public failed" in out
    assert "/SKILL.md:12:" in out


def test_check_public_references_directory_files(repo, sha_of, monkeypatch, capsys):
    sha = sha_of(repo)
    write_skill(repo, feeds=[("demo", FEED_PATH, sha)])
    note = repo / ".claude/skills/demo/references/note.md"
    note.parent.mkdir(parents=True)
    note.write_text("zzplantedname\n")
    assert run(repo) == 1
    assert "check-public" in capsys.readouterr().out


def test_check_public_fails_closed_without_rules(repo, monkeypatch, capsys):
    monkeypatch.setenv("PUBLIC_DENYLIST", str(repo / "absent-rules.txt"))
    assert run(repo) == 1
    assert "failing closed" in capsys.readouterr().out


def test_unreferenced_sub_skill_fails(repo, sha_of, capsys):
    write_skill(
        repo,
        name="hidden",
        feeds=[("demo", FEED_PATH, sha_of(repo))],
        frontmatter=["disable-model-invocation: true"],
    )
    assert run(repo) == 1
    out = capsys.readouterr().out
    assert "no other curated skill calls this one" in out
    assert ".claude/skills/hidden/SKILL.md" in out


def test_referenced_sub_skill_passes(repo, sha_of):
    sha = sha_of(repo)
    write_skill(
        repo,
        name="hidden",
        feeds=[("demo", FEED_PATH, sha)],
        frontmatter=["disable-model-invocation: true"],
    )
    write_skill(
        repo,
        name="caller",
        feeds=[("demo", FEED_PATH, sha)],
        body="# Caller\n\nInvoke hidden before planning.\n",
    )
    assert run(repo) == 0


def test_reference_in_a_references_file_counts(repo, sha_of):
    sha = sha_of(repo)
    write_skill(
        repo,
        name="hidden",
        feeds=[("demo", FEED_PATH, sha)],
        frontmatter=["disable-model-invocation: true"],
    )
    caller = write_skill(repo, name="caller", feeds=[("demo", FEED_PATH, sha)])
    note = caller.parent / "references" / "routing.md"
    note.parent.mkdir(parents=True)
    note.write_text("Route to hidden when the task is small.\n")
    assert run(repo) == 0


def test_named_sub_skill_still_sees_callers_outside_the_selection(repo, sha_of):
    sha = sha_of(repo)
    write_skill(
        repo,
        name="hidden",
        feeds=[("demo", FEED_PATH, sha)],
        frontmatter=["disable-model-invocation: true"],
    )
    write_skill(
        repo,
        name="caller",
        feeds=[("demo", FEED_PATH, sha)],
        body="# Caller\n\nInvoke hidden before planning.\n",
    )
    assert run(repo, "hidden") == 0


PRIVATE_TEXT = (
    "Every ticket names one observable outcome that a reviewer can check without "
    "asking the author, and the outcome is written before any design is chosen. "
    "Evidence is quoted exactly as captured so the reader sees what the system said."
)


def private_upstream(repo, tmp_path, monkeypatch):
    clone = repo / "upstream" / "demo"
    (clone / FEED_PATH).write_text(PRIVATE_TEXT + "\n")
    sha = commit_all(clone, "private text")
    write_registry(repo, {"demo": {"local": True, "sha": sha}})
    config = tmp_path / "local.json"
    config.write_text(json.dumps({"demo": {"url": str(clone)}}))
    monkeypatch.setenv("SKILL_UPSTREAM_LOCAL_CONFIG", str(config))
    return sha


def test_text_copied_from_a_private_feed_fails(repo, tmp_path, monkeypatch, capsys):
    sha = private_upstream(repo, tmp_path, monkeypatch)
    write_skill(repo, feeds=[("demo", FEED_PATH, sha)], body="# Demo\n\n" + PRIVATE_TEXT + "\n")
    assert run(repo) == 1
    assert "copied from a private feed" in capsys.readouterr().out


def test_private_feed_ideas_in_own_words_pass(repo, tmp_path, monkeypatch):
    sha = private_upstream(repo, tmp_path, monkeypatch)
    body = (
        "# Demo\n\nState the result a reviewer could confirm unaided before picking "
        "an approach, and paste what the system printed rather than paraphrasing it.\n"
    )
    write_skill(repo, feeds=[("demo", FEED_PATH, sha)], body=body)
    assert run(repo) == 0


def test_public_feed_text_may_be_copied(repo, sha_of):
    clone = repo / "upstream" / "demo"
    (clone / FEED_PATH).write_text(PRIVATE_TEXT + "\n")
    sha = commit_all(clone, "public text")
    write_skill(repo, feeds=[("demo", FEED_PATH, sha)], body="# Demo\n\n" + PRIVATE_TEXT + "\n")
    assert run(repo) == 0


def test_unquoted_hash_in_description_fails(repo, sha_of, capsys):
    write_skill(
        repo,
        feeds=[("demo", FEED_PATH, sha_of(repo))],
        description='Use when asked to "triage #42".',
    )
    assert run(repo) == 1
    assert "reads as a comment" in capsys.readouterr().out
