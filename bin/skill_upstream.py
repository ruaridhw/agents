"""Track the upstream files each curated skill was written from, and report drift."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

SKILLS_DIR = ".agents/skills"
# Where the skills lived before they moved; a self feed stamped before the move
# keeps its sha, so its path is looked up here as well.
LEGACY_SKILLS_DIR = ".claude/skills"
UPSTREAMS_FILE = "UPSTREAMS.json"
CLONES_DIR = "upstream"
LOCAL_CONFIG_ENV = "SKILL_UPSTREAM_LOCAL_CONFIG"
DEFAULT_LOCAL_CONFIG = Path("~/.config/agents/upstreams.local.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class UsageError(Exception):
    """Bad invocation or unusable config: exit 2."""


class GitError(Exception):
    """A git command that should have succeeded did not."""


class Feed(NamedTuple):
    repo: str
    path: str
    sha: str
    sha_line: int | None = None


def git(args, cwd, check=True):
    proc = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise GitError(f"git {' '.join(args)} failed in {cwd}: {detail}")
    return proc


def git_out(args, cwd):
    return git(args, cwd).stdout.strip()


def git_ok(args, cwd):
    return git(args, cwd, check=False).returncode == 0


def rev(cwd, ref):
    proc = git(
        ["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd, check=False
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def head_of(cwd):
    proc = rev(cwd, "origin/HEAD")
    if proc:
        return proc
    return rev(cwd, "HEAD")


def short(sha):
    return sha[:7] if sha else ""


def load_registry(root):
    path = root / UPSTREAMS_FILE
    if not path.exists():
        raise UsageError(f"{path} not found")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise UsageError(f"{path} is not valid JSON: {exc}") from exc
    return data["upstreams"]


def write_registry(root, registry):
    (root / UPSTREAMS_FILE).write_text(
        json.dumps({"upstreams": registry}, indent=2) + "\n"
    )


def local_config_path():
    return Path(os.environ.get(LOCAL_CONFIG_ENV) or DEFAULT_LOCAL_CONFIG).expanduser()


def load_local_config():
    path = local_config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise UsageError(f"{path} is not valid JSON: {exc}") from exc


def upstream_url(name, entry, local):
    if entry.get("local"):
        return (local.get(name) or {}).get("url")
    return entry.get("url")


def clone_dir(root, name):
    return root / CLONES_DIR / name


def upstream_flags(root, name, entry, local):
    if entry.get("self"):
        return []
    if upstream_url(name, entry, local) is None:
        return ["unconfigured"]
    if not clone_dir(root, name).exists():
        return ["unsynced"]
    return []


def upstream_cwd(root, name, entry):
    if entry.get("self"):
        return root
    return clone_dir(root, name)


def feed_paths(feed, entry):
    if entry.get("self") and feed.path.startswith(SKILLS_DIR + "/"):
        return [feed.path, LEGACY_SKILLS_DIR + feed.path[len(SKILLS_DIR) :]]
    return [feed.path]


def scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_feed(lines, index, end):
    values = {}
    sha_line = None
    line = lines[index].rstrip("\n")
    indent = len(line) - len(line.lstrip())
    key, _, value = line.strip()[2:].partition(":")
    values[key.strip()] = scalar(value)
    index += 1
    while index < end:
        line = lines[index].rstrip("\n")
        if not line.strip():
            index += 1
            continue
        if len(line) - len(line.lstrip()) <= indent or line.strip().startswith("- "):
            break
        key, _, value = line.strip().partition(":")
        key = key.strip()
        values[key] = scalar(value)
        if key == "sha":
            sha_line = index
        index += 1
    feed = Feed(
        values.get("repo", ""), values.get("path", ""), values.get("sha", ""), sha_line
    )
    return feed, index


def parse_upstream(lines, index, end, info):
    value = lines[index].split(":", 1)[1].strip()
    info["upstream_line"] = index
    insert_at = index + 1
    index += 1
    if value not in ("", "[]"):
        info["upstream_end"] = insert_at
        return index
    while index < end:
        line = lines[index].rstrip("\n")
        if not line.strip():
            index += 1
            continue
        if not line[:1].isspace():
            break
        if line.strip().startswith("- "):
            feed, index = parse_feed(lines, index, end)
            info["feeds"].append(feed)
            insert_at = index
        else:
            index += 1
    info["upstream_end"] = insert_at
    return index


def parse_skill(text):
    lines = text.splitlines(keepends=True)
    fences = [i for i, line in enumerate(lines) if line.strip() == "---"]
    if len(fences) < 2:
        return None
    start, end = fences[0], fences[1]
    info = {
        "lines": lines,
        "start": start,
        "end": end,
        "name": None,
        "description": None,
        "feeds": [],
        "has_upstream": False,
        "upstream_line": None,
        "upstream_end": None,
    }
    index = start + 1
    while index < end:
        line = lines[index].rstrip("\n")
        if line[:1].isspace():
            index += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key == "name":
            info["name"] = scalar(value)
        elif key == "description":
            info["description"] = scalar(value)
        elif key == "upstream":
            info["has_upstream"] = True
            index = parse_upstream(lines, index, end, info)
            continue
        index += 1
    return info


def all_skills(root):
    base = root / SKILLS_DIR
    if not base.is_dir():
        return []
    skills = []
    for skill_md in sorted(base.glob("*/SKILL.md")):
        info = parse_skill(skill_md.read_text())
        if info is None:
            continue
        info["file"] = skill_md
        info["dir_name"] = skill_md.parent.name
        skills.append(info)
    return skills


def curated_skills(root):
    return [info for info in all_skills(root) if info["has_upstream"]]


def find_skill(root, name, require_key=True):
    pool = curated_skills(root) if require_key else all_skills(root)
    for info in pool:
        if info["dir_name"] == name or info["name"] == name:
            return info
    return None


def flag_text(flags):
    return f"  [{', '.join(flags)}]" if flags else ""


def count_commits(cwd, base, head, *paths):
    out = git_out(["rev-list", "--count", f"{base}..{head}", "--", *paths], cwd)
    return int(out or 0)


def cmd_sync(root, names):
    registry = load_registry(root)
    local = load_local_config()
    selected = names or list(registry)
    unknown = [name for name in selected if name not in registry]
    if unknown:
        raise UsageError(f"unknown upstream(s): {', '.join(unknown)}")
    changed = False
    for name in selected:
        entry = registry[name]
        if entry.get("self"):
            print(f"{name}: self, no clone")
            continue
        url = upstream_url(name, entry, local)
        if url is None:
            print(f"{name}: unconfigured (local upstream, no local config)")
            continue
        dest = clone_dir(root, name)
        if dest.exists():
            git(["fetch", "--prune", "--quiet", "origin"], dest)
            git(["remote", "set-head", "origin", "--auto"], dest, check=False)
            print(f"{name}: fetched")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            git(["clone", "--filter=blob:none", "--quiet", url, str(dest)], root)
            print(f"{name}: cloned")
        head = head_of(dest)
        stamped = entry.get("sha")
        full = rev(dest, stamped) if stamped else None
        if full and full != stamped:
            registry[name]["sha"] = full
            changed = True
            print(f"{name}: sha {stamped} -> {full}")
        if head:
            print(f"{name}: head {short(head)}")
    if changed:
        write_registry(root, registry)
    return 0


def upstream_row(root, name, entry, local):
    row = {
        "name": name,
        "audited": entry.get("sha"),
        "head": None,
        "commits": None,
        "flags": upstream_flags(root, name, entry, local),
    }
    if row["flags"]:
        return row
    cwd = upstream_cwd(root, name, entry)
    head = rev(cwd, "HEAD") if entry.get("self") else head_of(cwd)
    row["head"] = head
    base = rev(cwd, entry["sha"]) if entry.get("sha") else None
    if base and head:
        row["commits"] = count_commits(cwd, base, head, ".")
    return row


def feed_row(root, feed, registry, local):
    row = {
        "repo": feed.repo,
        "path": feed.path,
        "sha": feed.sha,
        "head": None,
        "commits": None,
        "flags": [],
    }
    entry = registry.get(feed.repo)
    if entry is None:
        row["flags"].append("unknown-repo")
        return row
    row["flags"].extend(upstream_flags(root, feed.repo, entry, local))
    if row["flags"]:
        return row
    cwd = upstream_cwd(root, feed.repo, entry)
    head = rev(cwd, "HEAD") if entry.get("self") else head_of(cwd)
    row["head"] = head
    base = rev(cwd, feed.sha) if feed.sha else None
    if head is None or base is None:
        row["flags"].append("unsynced")
        return row
    row["commits"] = count_commits(cwd, base, head, *feed_paths(feed, entry))
    if not git_ok(["cat-file", "-e", f"{head}:{feed.path}"], cwd):
        row["flags"].append("missing-at-head")
    return row


def print_status(up_rows, skill_rows):
    name_width = max([len(row["name"]) for row in up_rows] or [1])
    print("UPSTREAMS")
    for row in up_rows:
        audited = short(row["audited"]) or "-"
        line = f"  {row['name']:<{name_width}}  audited {audited}"
        if row["head"]:
            commits = "-" if row["commits"] is None else row["commits"]
            line += f"  head {short(row['head'])}  commits {commits}"
        print(line + flag_text(row["flags"]))
    print()
    print("SKILLS")
    feeds = [feed for skill in skill_rows for feed in skill["feeds"]]
    repo_width = max([len(feed["repo"]) for feed in feeds] or [1])
    path_width = max([len(feed["path"]) for feed in feeds] or [1])
    for skill in skill_rows:
        if not skill["feeds"]:
            print(f"  {skill['skill']}  curated without feeds")
            continue
        print(f"  {skill['skill']}")
        for feed in skill["feeds"]:
            head = short(feed["head"]) or "-"
            commits = "-" if feed["commits"] is None else feed["commits"]
            print(
                f"    {feed['repo']:<{repo_width}}  {feed['path']:<{path_width}}"
                f"  {short(feed['sha'])} -> {head}  commits {commits}"
                f"{flag_text(feed['flags'])}"
            )


def cmd_status(root, skill_names, as_json):
    registry = load_registry(root)
    local = load_local_config()
    up_rows = [
        upstream_row(root, name, entry, local) for name, entry in registry.items()
    ]
    skills = curated_skills(root)
    if skill_names:
        known = {info["dir_name"] for info in skills}
        missing = [name for name in skill_names if name not in known]
        if missing:
            print(f"unknown curated skill(s): {', '.join(missing)}", file=sys.stderr)
            return 1
        skills = [info for info in skills if info["dir_name"] in skill_names]
    skill_rows = [
        {
            "skill": info["dir_name"],
            "feeds": [feed_row(root, feed, registry, local) for feed in info["feeds"]],
        }
        for info in skills
    ]
    if as_json:
        print(json.dumps({"upstreams": up_rows, "skills": skill_rows}, indent=2))
        return 0
    print_status(up_rows, skill_rows)
    return 0


def cmd_diff(root, skill_name, repo, path):
    info = find_skill(root, skill_name)
    if info is None:
        print(f"unknown curated skill: {skill_name}", file=sys.stderr)
        return 1
    registry = load_registry(root)
    local = load_local_config()
    selected = [
        feed
        for feed in info["feeds"]
        if (repo is None or feed.repo == repo) and (path is None or feed.path == path)
    ]
    if not selected:
        print("no feeds matched", file=sys.stderr)
        return 1
    for feed in selected:
        row = feed_row(root, feed, registry, local)
        header = (
            f"{feed.repo}:{feed.path}  {short(feed.sha)}..{short(row['head']) or '-'}"
        )
        print(header + flag_text(row["flags"]))
        if row["flags"]:
            continue
        entry = registry[feed.repo]
        cwd = upstream_cwd(root, feed.repo, entry)
        diff = git(
            ["diff", "-M", f"{feed.sha}..{row['head']}", "--", *feed_paths(feed, entry)],
            cwd,
        ).stdout
        print(diff.rstrip("\n") if diff.strip() else "(no changes)")
    return 0


def insert_at(lines, index, new_lines):
    if index > 0 and not lines[index - 1].endswith("\n"):
        lines[index - 1] += "\n"
    lines[index:index] = new_lines


def stamp_sha(root, repo, sha, registry, local):
    entry = registry.get(repo)
    if entry is None:
        raise UsageError(f"unknown upstream: {repo}")
    cwd = upstream_cwd(root, repo, entry)
    usable = entry.get("self") or not upstream_flags(root, repo, entry, local)
    if sha:
        full = rev(cwd, sha) if usable else None
        return full or sha
    if not usable:
        raise UsageError(f"{repo} is not synced; run sync or pass --sha")
    head = rev(cwd, "HEAD") if entry.get("self") else head_of(cwd)
    if head is None:
        raise UsageError(f"cannot resolve HEAD for {repo}")
    return head


def set_sha_lines(lines, feeds, sha):
    for feed in feeds:
        if feed.sha_line is None:
            raise UsageError(f"feed {feed.repo}:{feed.path} has no sha line")
        line = lines[feed.sha_line]
        indent = line[: len(line) - len(line.lstrip())]
        ending = "\n" if line.endswith("\n") else ""
        lines[feed.sha_line] = f"{indent}sha: {sha}{ending}"


def add_feed(root, info, repo, path, sha, registry, local):
    if repo not in registry:
        raise UsageError(f"unknown upstream: {repo}")
    if any(feed.repo == repo and feed.path == path for feed in info["feeds"]):
        print(f"feed already stamped: {repo}:{path}", file=sys.stderr)
        return 1
    sha = stamp_sha(root, repo, sha, registry, local)
    lines = info["lines"]
    entry = [
        f"  - repo: {repo}\n",
        f"    path: {path}\n",
        f"    sha: {sha}\n",
    ]
    if not info["has_upstream"]:
        insert_at(lines, info["end"], ["upstream:\n", *entry])
    elif (
        not info["feeds"]
        and lines[info["upstream_line"]].split(":", 1)[1].strip() == "[]"
    ):
        line = lines[info["upstream_line"]]
        indent = line[: len(line) - len(line.lstrip())]
        ending = "\n" if line.endswith("\n") else ""
        lines[info["upstream_line"]] = f"{indent}upstream:{ending}"
        insert_at(lines, info["upstream_line"] + 1, entry)
    else:
        insert_at(lines, info["upstream_end"], entry)
    info["file"].write_text("".join(lines))
    print(f"stamped {repo}:{path} at {short(sha)}")
    return 0


def cmd_stamp(root, skill_name, repo, path, sha, add):
    info = find_skill(root, skill_name, require_key=not add)
    if info is None:
        print(f"unknown curated skill: {skill_name}", file=sys.stderr)
        return 1
    registry = load_registry(root)
    local = load_local_config()
    if add:
        if not repo or not path:
            raise UsageError("stamp --add needs --repo and --path")
        return add_feed(root, info, repo, path, sha, registry, local)
    selected = [
        feed
        for feed in info["feeds"]
        if (repo is None or feed.repo == repo) and (path is None or feed.path == path)
    ]
    if not selected:
        print("no feeds matched", file=sys.stderr)
        return 1
    for feed in selected:
        new_sha = stamp_sha(root, feed.repo, sha, registry, local)
        set_sha_lines(info["lines"], [feed], new_sha)
        print(f"{feed.repo}:{feed.path} -> {new_sha}")
    info["file"].write_text("".join(info["lines"]))
    return 0


def cmd_check(root):
    registry = load_registry(root)
    problems = []
    for info in curated_skills(root):
        label = f"{SKILLS_DIR}/{info['dir_name']}/SKILL.md"
        if info["name"] != info["dir_name"]:
            problems.append(
                f"{label}: name {info['name']!r} does not match directory {info['dir_name']!r}"
            )
        if not info["description"]:
            problems.append(f"{label}: missing description")
        seen = set()
        for feed in info["feeds"]:
            entry = registry.get(feed.repo)
            if entry is None:
                problems.append(f"{label}: unknown upstream {feed.repo!r}")
            if not SHA_RE.match(feed.sha or ""):
                problems.append(f"{label}: sha {feed.sha!r} is not 40 hex")
            key = (feed.repo, feed.path)
            if key in seen:
                problems.append(f"{label}: duplicate feed {feed.repo}:{feed.path}")
            seen.add(key)
            if entry is None:
                continue
            cwd = upstream_cwd(root, feed.repo, entry)
            if not entry.get("self") and not cwd.exists():
                continue
            if not SHA_RE.match(feed.sha or ""):
                continue
            if not any(
                git_ok(["cat-file", "-e", f"{feed.sha}:{path}"], cwd)
                for path in feed_paths(feed, entry)
            ):
                problems.append(
                    f"{label}: {feed.path} missing at {short(feed.sha)} in {feed.repo}"
                )
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="skill-upstream",
        description="Track upstream files behind curated skills and report drift.",
    )
    parser.add_argument("--root", help="repo root (default: parent of this script)")
    sub = parser.add_subparsers(dest="command", required=True)

    sync = sub.add_parser("sync", help="clone or fetch upstream repos")
    sync.add_argument("names", nargs="*")

    status = sub.add_parser("status", help="report drift per skill and upstream")
    status.add_argument("skills", nargs="*")
    status.add_argument("--json", action="store_true")

    diff = sub.add_parser("diff", help="show upstream changes since a stamp")
    diff.add_argument("skill")
    diff.add_argument("--repo")
    diff.add_argument("--path")

    stamp = sub.add_parser("stamp", help="move a stamp to a newer sha")
    stamp.add_argument("skill")
    stamp.add_argument("--repo")
    stamp.add_argument("--path")
    stamp.add_argument("--sha")
    stamp.add_argument("--add", action="store_true")

    sub.add_parser("check", help="validate stamps and skill frontmatter")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = (
        Path(args.root).resolve()
        if args.root
        else Path(__file__).resolve().parent.parent
    )
    try:
        if args.command == "sync":
            return cmd_sync(root, args.names)
        if args.command == "status":
            return cmd_status(root, args.skills, args.json)
        if args.command == "diff":
            return cmd_diff(root, args.skill, args.repo, args.path)
        if args.command == "stamp":
            return cmd_stamp(root, args.skill, args.repo, args.path, args.sha, args.add)
        return cmd_check(root)
    except (UsageError, GitError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
