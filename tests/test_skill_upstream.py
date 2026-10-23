"""End-to-end tests for bin/skill-upstream against throwaway git repos."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "skill_upstream", REPO_ROOT / "bin" / "skill_upstream.py"
)
assert SPEC is not None and SPEC.loader is not None
skill_upstream = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skill_upstream)

FEED_PATH = "skill/SKILL.md"
SKILL_PATH = ".agents/skills/demo/SKILL.md"


def git(cwd, *args):
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


def write_skill(root, feeds=None, name="demo", key=True, dir_name=None):
    path = root / ".agents/skills" / (dir_name or name) / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"name: {name}", "description: Use when testing the tool."]
    if key:
        lines.append("upstream:" if feeds else "upstream: []")
        for repo, feed_path, sha in feeds or []:
            lines += [
                f"  - repo: {repo}",
                f"    path: {feed_path}",
                f"    sha: {sha}",
            ]
    lines += ["---", "", "# Demo", ""]
    path.write_text("\n".join(lines))
    return path


def run(root, *args):
    return skill_upstream.main(["--root", str(root), *args])


@pytest.fixture(autouse=True)
def isolated_local_config(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "SKILL_UPSTREAM_LOCAL_CONFIG", str(tmp_path / "no-local-config.json")
    )


@pytest.fixture
def repo(tmp_path):
    source = init_repo(tmp_path / "source")
    (source / "skill").mkdir()
    (source / FEED_PATH).write_text("v1\n")
    first = commit_all(source, "first")
    (source / FEED_PATH).write_text("v1\nv2\n")
    second = commit_all(source, "second")

    root = init_repo(tmp_path / "repo")
    registry = {
        "upstreams": {
            "fake": {"url": str(source), "sha": first},
            "self": {"self": True},
        }
    }
    (root / "UPSTREAMS.json").write_text(json.dumps(registry, indent=2) + "\n")
    write_skill(root, [("fake", FEED_PATH, first)])
    head = commit_all(root, "add demo skill")
    return {
        "root": root,
        "source": source,
        "first": first,
        "second": second,
        "head": head,
    }


def synced(repo):
    assert run(repo["root"], "sync", "fake") == 0


def test_sync_resolves_short_sha(tmp_path):
    source = init_repo(tmp_path / "source")
    (source / "skill").mkdir()
    (source / FEED_PATH).write_text("v1\n")
    first = commit_all(source, "first")
    root = init_repo(tmp_path / "repo")
    registry = {"upstreams": {"fake": {"url": str(source), "sha": first[:7]}}}
    (root / "UPSTREAMS.json").write_text(json.dumps(registry, indent=2) + "\n")

    assert run(root, "sync", "fake") == 0

    written = json.loads((root / "UPSTREAMS.json").read_text())
    assert written["upstreams"]["fake"]["sha"] == first
    assert (root / "upstream" / "fake" / FEED_PATH).exists()


def test_status_counts_one_commit(repo, capsys):
    synced(repo)
    capsys.readouterr()
    assert run(repo["root"], "status") == 0
    out = capsys.readouterr().out
    feed_line = next(line for line in out.splitlines() if FEED_PATH in line)
    assert "commits 1" in feed_line
    assert repo["first"][:7] in feed_line
    assert repo["second"][:7] in feed_line


def test_status_json(repo, capsys):
    synced(repo)
    capsys.readouterr()
    assert run(repo["root"], "status", "--json") == 0
    data = json.loads(capsys.readouterr().out)
    assert data["upstreams"][0]["name"] == "fake"
    assert data["skills"][0]["skill"] == "demo"
    assert data["skills"][0]["feeds"][0]["repo"] == "fake"
    assert data["skills"][0]["feeds"][0]["commits"] == 1


def test_diff_shows_hunk(repo, capsys):
    synced(repo)
    capsys.readouterr()
    assert run(repo["root"], "diff", "demo") == 0
    out = capsys.readouterr().out
    assert f"fake:{FEED_PATH}" in out
    assert "+v2" in out


def test_stamp_moves_only_the_sha(repo, capsys):
    synced(repo)
    skill_file = repo["root"] / SKILL_PATH
    before = skill_file.read_text()

    assert run(repo["root"], "stamp", "demo") == 0

    after = skill_file.read_text()
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    assert len(before_lines) == len(after_lines)
    changed = [(a, b) for a, b in zip(before_lines, after_lines) if a != b]
    assert changed == [(f"    sha: {repo['first']}", f"    sha: {repo['second']}")]
    assert repo["second"] in after

    capsys.readouterr()
    assert run(repo["root"], "status") == 0
    feed_line = next(
        line for line in capsys.readouterr().out.splitlines() if FEED_PATH in line
    )
    assert "commits 0" in feed_line


def test_stamp_filters_by_repo_and_path(repo):
    synced(repo)
    skill_file = repo["root"] / SKILL_PATH
    assert run(repo["root"], "stamp", "demo", "--repo", "nope") == 1
    assert f"sha: {repo['first']}" in skill_file.read_text()


def test_check_passes(repo, capsys):
    synced(repo)
    capsys.readouterr()
    assert run(repo["root"], "check") == 0
    assert capsys.readouterr().out == ""


def test_check_rejects_unknown_repo(repo, capsys):
    write_skill(repo["root"], [("nope", FEED_PATH, repo["first"])])
    assert run(repo["root"], "check") == 1
    assert "unknown upstream" in capsys.readouterr().out


def test_check_rejects_short_sha(repo, capsys):
    write_skill(repo["root"], [("fake", FEED_PATH, repo["first"][:7])])
    assert run(repo["root"], "check") == 1
    assert "not 40 hex" in capsys.readouterr().out


def test_check_rejects_name_dir_mismatch(repo, capsys):
    write_skill(
        repo["root"],
        [("fake", FEED_PATH, repo["first"])],
        name="other",
        dir_name="demo",
    )
    (repo["root"] / "UPSTREAMS.json").write_text(
        json.dumps(
            {"upstreams": {"fake": {"url": str(repo["source"]), "sha": repo["first"]}}},
            indent=2,
        )
        + "\n"
    )
    assert run(repo["root"], "check") == 1
    assert "does not match directory" in capsys.readouterr().out


def test_check_rejects_duplicate_feeds(repo, capsys):
    write_skill(
        repo["root"],
        [("fake", FEED_PATH, repo["first"]), ("fake", FEED_PATH, repo["first"])],
    )
    assert run(repo["root"], "check") == 1
    assert "duplicate feed" in capsys.readouterr().out


def test_stamp_add_creates_block(repo, capsys):
    skill_file = write_skill(repo["root"], key=False)
    synced(repo)
    capsys.readouterr()

    assert (
        run(
            repo["root"],
            "stamp",
            "--add",
            "demo",
            "--repo",
            "fake",
            "--path",
            FEED_PATH,
        )
        == 0
    )

    text = skill_file.read_text()
    assert "upstream:\n  - repo: fake\n    path: skill/SKILL.md\n" in text
    assert f"    sha: {repo['second']}" in text
    assert run(repo["root"], "check") == 0


def test_stamp_add_rewrites_empty_list(repo):
    skill_file = write_skill(repo["root"], key=True)
    synced(repo)
    assert (
        run(
            repo["root"],
            "stamp",
            "--add",
            "demo",
            "--repo",
            "fake",
            "--path",
            FEED_PATH,
        )
        == 0
    )
    text = skill_file.read_text()
    assert "upstream: []" not in text
    assert "  - repo: fake" in text


def test_unconfigured_local_upstream_is_reported_not_fatal(repo, capsys, tmp_path):
    registry = json.loads((repo["root"] / "UPSTREAMS.json").read_text())
    registry["upstreams"]["hidden"] = {"local": True, "sha": None}
    (repo["root"] / "UPSTREAMS.json").write_text(json.dumps(registry, indent=2) + "\n")
    write_skill(repo["root"], [("hidden", "x/SKILL.md", repo["first"])])
    (tmp_path / "no-local-config.json").unlink(missing_ok=True)

    assert run(repo["root"], "sync", "hidden") == 0
    assert "unconfigured" in capsys.readouterr().out

    assert run(repo["root"], "status") == 0
    out = capsys.readouterr().out
    feed_line = next(line for line in out.splitlines() if "x/SKILL.md" in line)
    assert "unconfigured" in feed_line


def test_self_feed_uses_own_history(repo, capsys):
    skill_file = repo["root"] / SKILL_PATH
    write_skill(repo["root"], [("self", SKILL_PATH, repo["head"])])
    head = commit_all(repo["root"], "stamp self feed")
    write_skill(repo["root"], [("self", SKILL_PATH, head)])

    assert run(repo["root"], "status") == 0
    feed_line = next(
        line for line in capsys.readouterr().out.splitlines() if SKILL_PATH in line
    )
    assert "commits 0" in feed_line

    skill_file.write_text(skill_file.read_text() + "\nnote\n")
    commit_all(repo["root"], "touch the skill")
    capsys.readouterr()
    assert run(repo["root"], "status") == 0
    feed_line = next(
        line for line in capsys.readouterr().out.splitlines() if SKILL_PATH in line
    )
    assert "commits 1" in feed_line
    assert head[:7] in feed_line


def test_status_flags_missing_at_head(repo, capsys):
    synced(repo)
    write_skill(repo["root"], [("fake", "gone/SKILL.md", repo["first"])])
    capsys.readouterr()
    assert run(repo["root"], "status") == 0
    feed_line = next(
        line for line in capsys.readouterr().out.splitlines() if "gone/SKILL.md" in line
    )
    assert "missing-at-head" in feed_line


def test_unknown_skill_is_an_error(repo, capsys):
    assert run(repo["root"], "diff", "nope") == 1
    assert "unknown curated skill" in capsys.readouterr().err
    assert run(repo["root"], "stamp", "nope") == 1


def test_missing_registry_is_a_usage_error(tmp_path, capsys):
    root = init_repo(tmp_path / "empty")
    assert run(root, "status") == 2
    assert "not found" in capsys.readouterr().err
