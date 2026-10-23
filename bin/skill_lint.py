"""Format-only linter for the curated skills: frontmatter, stamps and denylist.

Lints only curated skills (`.agents/skills/<dir>/SKILL.md` with an `upstream:`
key). Each finding is printed as `<path>: <problem>`; any finding exits 1.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_upstream as su  # noqa: E402

# A when-to-use description says when to reach for the skill.
USE_RE = re.compile(r"\bUse (when|whenever|for|after|before|at|once|on|to|if)\b")
SKILL_FILE = "SKILL.md"
CHECK_PUBLIC = Path(__file__).resolve().parent / "check-public"
CLONE_MISSING = "' clone missing: run bin/skill-upstream sync"
# A private upstream may inform a skill but its text never enters this public repo.
SHINGLE = 8
PRIVATE_RUNS_ALLOWED = 5


def top_level_flags(info):
    """Top-level frontmatter scalar keys, e.g. `disable-model-invocation`."""
    flags = {}
    for line in info["lines"][info["start"] + 1 : info["end"]]:
        if not line.strip() or line[:1].isspace():
            continue
        key, _, value = line.partition(":")
        flags[key.strip()] = su.scalar(value)
    return flags


def check_name(info, label, problems):
    if not info["name"]:
        problems.append(f"{label}: name missing from frontmatter")
    elif info["name"] != info["dir_name"]:
        problems.append(
            f"{label}: name {info['name']!r} does not match directory"
            f" {info['dir_name']!r}"
        )


def raw_description(info):
    """The description value as written, quotes and all, or None."""
    for line in info["lines"][info["start"] + 1 : info["end"]]:
        if line[:1].isspace():
            continue
        key, _, value = line.partition(":")
        if key.strip() == "description":
            return value.strip()
    return None


def check_description(info, label, problems):
    description = info["description"] or ""
    raw = raw_description(info) or ""
    unquoted = raw[:1] not in "\"'>|"
    if not description:
        problems.append(f"{label}: description missing from frontmatter")
    elif unquoted and re.search(r":\s", raw):
        problems.append(
            f"{label}: description has ': ' in an unquoted scalar, which YAML"
            " reads as a nested mapping; quote the description"
        )
    elif unquoted and re.search(r"\s#", raw):
        problems.append(
            f"{label}: description has ' #' in an unquoted scalar, which YAML"
            " reads as a comment and truncates; quote it or reword"
        )
    elif not USE_RE.search(description):
        problems.append(
            f"{label}: description is not phrased as when-to-use (no sentence"
            " starting 'Use when/whenever/for/after/before/at/once/on/to/if')"
        )


def resolve_upstream(root, feed, entry, local, label, problems):
    """Upstream working copy for a feed, or None when it cannot be checked."""
    if entry.get("local") and not entry.get("self"):
        if su.upstream_url(feed.repo, entry, local) is None:
            return None
    cwd = su.upstream_cwd(root, feed.repo, entry)
    if not entry.get("self") and not cwd.exists():
        problems.append(f"{label}: upstream {feed.repo!r}{CLONE_MISSING}")
        return None
    if su.rev(cwd, feed.sha) is None:
        problems.append(
            f"{label}: sha {su.short(feed.sha)} not in upstream {feed.repo!r}:"
            " run bin/skill-upstream sync"
        )
        return None
    return cwd


def check_feeds(root, info, registry, local, label, problems, notes):
    unconfigured = set()
    clone_reported = set()
    for index, feed in enumerate(info["feeds"], 1):
        for field in ("repo", "path", "sha"):
            if not getattr(feed, field):
                problems.append(
                    f"{label}: upstream entry {index} has no {field}"
                    " (repo, path and sha are all required)"
                )
        if not feed.repo or not feed.path or not feed.sha:
            continue
        entry = registry.get(feed.repo)
        if entry is None:
            problems.append(
                f"{label}: upstream {feed.repo!r} is not a key of UPSTREAMS.json"
            )
            continue
        if not su.SHA_RE.match(feed.sha):
            problems.append(f"{label}: sha {feed.sha!r} is not 40 hex")
            continue
        if entry.get("local") and not entry.get("self"):
            if su.upstream_url(feed.repo, entry, local) is None:
                if feed.repo not in unconfigured:
                    unconfigured.add(feed.repo)
                    notes.append(
                        f"{label}: upstream {feed.repo!r} is unconfigured on this"
                        " machine; its feeds were skipped"
                    )
                continue
        if feed.repo in clone_reported:
            continue
        cwd = resolve_upstream(root, feed, entry, local, label, problems)
        if cwd is None:
            if not entry.get("self") and not su.clone_dir(root, feed.repo).exists():
                clone_reported.add(feed.repo)
            continue
        if not any(
            su.git_ok(["cat-file", "-e", f"{feed.sha}:{path}"], cwd)
            for path in su.feed_paths(feed, entry)
        ):
            problems.append(
                f"{label}: {feed.path!r} missing at {su.short(feed.sha)} in"
                f" upstream {feed.repo!r}"
            )


def words(text):
    return re.findall(r"\w+", text.lower())


def shingles(text):
    tokens = words(text)
    return {" ".join(tokens[i : i + SHINGLE]) for i in range(len(tokens) - SHINGLE + 1)}


def private_feed_text(root, feed, entry, local):
    """Text of a private feed at its stamp (a directory feed: every file), or None."""
    if su.upstream_url(feed.repo, entry, local) is None:
        return None
    cwd = su.upstream_cwd(root, feed.repo, entry)
    if not cwd.exists() or not su.git_ok(
        ["cat-file", "-e", f"{feed.sha}:{feed.path}"], cwd
    ):
        return None
    listing = su.git_out(
        ["ls-tree", "-r", "--name-only", feed.sha, "--", feed.path], cwd
    )
    return "\n".join(
        su.git_out(["show", f"{feed.sha}:{path}"], cwd) for path in listing.split()
    )


def check_private_copy(root, info, registry, local, label, problems):
    private = set()
    for feed in info["feeds"]:
        entry = registry.get(feed.repo) or {}
        if not entry.get("local") or entry.get("self"):
            continue
        if not feed.path or not feed.sha or not su.SHA_RE.match(feed.sha):
            continue
        text = private_feed_text(root, feed, entry, local)
        if text:
            private |= shingles(text)
    if not private:
        return
    ours = set()
    for path in skill_files(info):
        if path.suffix == ".md":
            ours |= shingles(path.read_text())
    shared = sorted(ours & private)
    if len(shared) > PRIVATE_RUNS_ALLOWED:
        problems.append(
            f"{label}: {len(shared)} {SHINGLE}-word runs copied from a private feed"
            f" (allowed {PRIVATE_RUNS_ALLOWED}); take its ideas in your own words,"
            f" e.g. {shared[0]!r}"
        )


def skill_files(info):
    base = info["file"].parent
    return [path for path in sorted(base.rglob("*")) if path.is_file()]


def check_denylist(info, label, problems):
    """Delegate the private-name scan to check-public; propagate its failure."""
    files = skill_files(info)
    proc = subprocess.run(
        [str(CHECK_PUBLIC), *map(str, files)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return
    detail = (proc.stdout + proc.stderr).strip()
    lines = detail.splitlines() or [f"exit {proc.returncode} with no output"]
    problems.append(f"{label}: check-public failed: {lines[0]}")
    problems.extend(f"{label}: check-public: {line}" for line in lines[1:])


def referenced_elsewhere(root, info, pool):
    """True when another curated skill names this skill in its text or references."""
    pattern = re.compile(rf"\b{re.escape(info['dir_name'])}\b")
    for other in pool:
        if other["file"] == info["file"]:
            continue
        for path in skill_files(other):
            try:
                text = path.read_text()
            except (OSError, UnicodeDecodeError):
                continue
            if pattern.search(text):
                return True
    return False


def check_sub_skill(root, info, pool, label, problems):
    if top_level_flags(info).get("disable-model-invocation") != "true":
        return
    if not referenced_elsewhere(root, info, pool):
        problems.append(
            f"{label}: disable-model-invocation is set but no other curated skill"
            " calls this one, so it can never be reached"
        )


def lint_skill(root, info, pool, registry, local):
    label = f"{su.SKILLS_DIR}/{info['dir_name']}/{SKILL_FILE}"
    problems = []
    notes = []
    check_name(info, label, problems)
    check_description(info, label, problems)
    check_feeds(root, info, registry, local, label, problems, notes)
    check_denylist(info, label, problems)
    check_private_copy(root, info, registry, local, label, problems)
    check_sub_skill(root, info, pool, label, problems)
    return problems, notes


def cmd_lint(root, names):
    registry = su.load_registry(root)
    local = su.load_local_config()
    pool = everything = su.curated_skills(root)
    if names:
        known = {info["dir_name"] for info in pool}
        missing = [name for name in names if name not in known]
        if missing:
            raise su.UsageError(f"unknown curated skill(s): {', '.join(missing)}")
        pool = [info for info in pool if info["dir_name"] in names]
    problems = []
    notes = []
    for info in pool:
        found, skipped = lint_skill(root, info, everything, registry, local)
        problems.extend(found)
        notes.extend(skipped)
    for problem in problems:
        print(problem)
    for note in notes:
        print(note)
    return 1 if problems else 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="skill-lint",
        description="Lint the curated skills for format problems (no style opinions).",
    )
    parser.add_argument("--root", help="repo root (default: parent of this script)")
    parser.add_argument(
        "skills", nargs="*", help="curated skill names (default: all of them)"
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = (
        Path(args.root).resolve()
        if args.root
        else Path(__file__).resolve().parent.parent
    )
    try:
        return cmd_lint(root, args.skills)
    except (su.UsageError, su.GitError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
