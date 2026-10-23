---
name: worktree
description: Set up the isolated workspace before the first edit, at .worktrees/<ticket> inside the repo and based on the freshly fetched remote default branch, then clean worktrees up only once their work is merged. Use before starting a ticket's work, when picking up a handoff, when a second builder or a prototype needs its own tree, and when deciding which worktrees are safe to remove.
upstream:
  - repo: superpowers
    path: skills/using-git-worktrees/SKILL.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/worktree-cleanup.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/poteto-mode/scripts/worktree-audit.sh
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: kit
    path: template/.agents/skills/kit/working-alongside-another-agent/SKILL.md
    sha: 1d552609f50102184079aa622beb727e38b02341
---

# worktree

Ensure work happens in an isolated workspace. Here that workspace is always a git worktree at a fixed place in the repo: there is no native worktree tool to prefer and no consent question to ask, because the tree comes before the first edit.

**Core principle:** Detect existing isolation first. Then create the tree at the decided path, on the decided base. Never fight the harness.

**Announce at start:** "Using worktree to set up the isolated workspace."

## When this runs

- Before the first edit of any ticket work (`ruaridh-mode`, non-negotiable 1). `implement` runs it as its step 2; a handoff pickup runs it when the recorded branch has no tree.
- When a second writer needs a tree of its own: a parallel `builder` pane, a `prototype` variant, an arena candidate. One writer per worktree or branch.
- Read-only work — explain, review, diagnose with nothing to change — needs no tree. A quick task that edits one line still does: that is the rule, not a judgement call.

## Step 0: Detect Existing Isolation

**Before creating anything, check if you are already in an isolated workspace.**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule guard:** `GIT_DIR != GIT_COMMON` is also true inside git submodules. Before concluding "already in a worktree", verify you are not in a submodule:

```bash
# If this returns a path, you're in a submodule, not a worktree — treat as normal repo
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**If `GIT_DIR != GIT_COMMON` (and not a submodule):** You are already in a linked worktree. Skip to Step 2 (Project Setup). Do NOT create another worktree.

Report with branch state:

- On a branch: "Already in isolated workspace at `<path>` on branch `<name>`."
- Detached HEAD: "Already in isolated workspace at `<path>` (detached HEAD, externally managed). Branch creation needed at finish time."

**If `GIT_DIR == GIT_COMMON` (or in a submodule):** You are in a normal repo checkout. Go to Step 1.

## Step 1: Create the tree

### 1a. Where it goes

`.worktrees/<ticket>` at the repo root, with a branch of the same name. `<ticket>` is the tracker ref, and a slug may follow it when the ref alone is unreadable (`.worktrees/<ticket-ref>-<slug>`). The tree lives inside the repo, never in a sibling directory: the ignore check below assumes it, and `handoff` and `pr` find it there.

### 1b. What it is based on

The freshly fetched remote default branch, unless an outstanding PR awaiting Ruaridh's merge is the real latest base, in which case stack on it.

```bash
git remote -v                        # the default remote may not be called origin
git fetch <remote>                   # fresh, always
git symbolic-ref --short refs/remotes/<remote>/HEAD   # the remote's default branch
```

- **Default branch, the normal case:** `git worktree add .worktrees/<ticket> -b <ticket> <remote>/<default>`.
- **Stacked:** when the previous ticket's PR is open and awaiting Ruaridh's merge and this ticket builds on it, base on that branch instead: fetch it and cut from `<remote>/<previous-ticket>`. Never base on your own local copy of a branch that has been merged or retargeted; adopt the remote head (`ruaridh-mode`'s tooling rules).
- **A dependent ticket with no stack:** base on the default branch and say so; do not silently stack.

History stays linear: the base is the fork point, and this branch never has the default branch merged into it. A stale branch is rebased onto its new base (`pr` owns the stack mechanics).

### 1c. Safety verification

**MUST verify the directory is ignored before creating the worktree:**

```bash
git check-ignore -q .worktrees/
```

**If NOT ignored:** Add `.worktrees/` to `.gitignore`, commit that change, then proceed.

Keep the trailing slash: a `.worktrees/` pattern only matches a directory, so `git check-ignore .worktrees` (no slash) reports nothing while the directory does not exist yet, and a script that trusts it sees "not ignored" on every fresh clone.

**Why critical:** Prevents accidentally committing worktree contents to the repository.

### 1d. Create it

```bash
git worktree add .worktrees/<ticket> -b <ticket> <base>
cd .worktrees/<ticket>
```

**Sandbox fallback:** If `git worktree add` fails with a permission error (the Codex sandbox denies it, say), say so plainly and do not silently work in place: the isolation is a non-negotiable, so tell Ruaridh the sandbox blocked it and what you are doing instead before the first edit.

## Step 2: Project Setup

Auto-detect and run appropriate setup, from inside the new tree:

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then uv sync; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

The repo's `AGENTS.md`, or its `.agents/build-loop.md`, may name the setup command: that one wins. Skip the step when none of these files exist.

## Step 3: Verify Clean Baseline

Run tests to ensure workspace starts clean:

```bash
# Use project-appropriate command, from .agents/build-loop.md when it names one
npm test / cargo test / pytest / go test ./...
```

**If tests fail:** Report failures, and ask whether to proceed or investigate (`debug` investigates; per the Inbox convention when Ruaridh is away). A dirty baseline makes every later failure ambiguous.

**If tests pass:** Report ready.

### Report

```
Worktree ready at <full-path>
Base <remote>/<branch> at <sha7>
Tests passing (<N> tests, 0 failures)
Ready to implement <ticket>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| Already in linked worktree | Skip creation (Step 0) |
| In a submodule | Treat as normal repo (Step 0 guard) |
| `.worktrees/` missing from `.gitignore` | Add it, commit, then create |
| Previous ticket's PR awaiting merge, this ticket builds on it | Stack on its remote branch |
| Otherwise | Base on the freshly fetched remote default branch |
| Detached HEAD in the tree | Branch needed at finish time (`pr`) |
| Permission error on create | Say so; never silently work in place |
| Tests fail during baseline | Report failures; `debug` investigates |
| No package.json/Cargo.toml/pyproject/go.mod | Skip dependency install |
| Work in the worktree finished and merged | Cleanup, below |
| Work finished but not merged | Not removable; `handoff` or wait |

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'm obviously not in a worktree — no need to check" | Run Step 0. Harness-created isolation and submodules both fool eyeballing; the detection commands settle it. |
| "`git worktree add` is quicker than checking the base" | The base is the whole point. A tree cut from a stale local branch makes every diff and every PR base wrong. |
| "The worktree directory is surely ignored already" | Run `git check-ignore` on `.worktrees/` (with the slash). An unignored worktree directory commits the whole tree into the repo. |
| "The workspace is fresh — baseline tests can wait" | A dirty baseline makes every later failure ambiguous. Run the tests now; proceeding past failures is Ruaridh's call. |
| "I'll just fix one line here, no need for a tree" | Worktree before the first edit, `ruaridh-mode` non-negotiable 1. |
| "This other tree looks stale, I'll remove it" | Cleanup is gated on merged state and on nobody else using it. A big old directory is not permission. |

## What a worktree does not isolate

**The working tree is isolated; almost nothing outside it is.** A checkout on disk is only part of what a change touches, and the rest is shared by everyone: a platform, a remote branch, a running system, another person's account. Treating the tree as total isolation is how a careful agent becomes careless.

- **A shared remote branch or a live system** does not know which tree you are in. Two trees pushing the same object collide, and only one should push or publish it at a time: agree which, in the ticket or in the pane.
- **A cached view of the remote can belong to one tree.** If a tree remembers the state of the remote as of its last pull, then two trees can hold different facts about what is live, and neither diff is lying. Before forcing anything over a difference, find which tree moved it: a force asserts that your copy is right, and that assertion can land on top of somebody else's work.
- **Any claim about live behaviour ages as soon as another tree publishes.** Record the revision you actually observed beside the claim, so a later reader can re-run it instead of trusting a memory.
- **Stage explicit paths. Never `git add -A`** in a tree another session may share: it stages the whole working tree, including another session's files in flight. (The general git rules are `ruaridh-mode`'s `references/tooling.md`.)
- **One writer per worktree or branch.** When two workstreams share mutable state, split the target rather than serialising on it.

## Cleanup, gated on the merged state

You may remove a worktree when its work is **merged**: its branch's head is an ancestor of the base, or its PR is merged and the remote head is adopted. Anything else is a question, not a chore.

1. **Audit before touching anything.** `scripts/worktree-audit.sh` is read-only. It reads paths from `git worktree list`, never hand-typed, so a tree in an unexpected place is not missed, and classifies each by size, age, merge state, uncommitted work, remote state and PR state.

   ```bash
   bash scripts/worktree-audit.sh [-b <base-ref>] [repo-path]
   ```

   Without `-b` it checks `MERGED` against `origin/HEAD`, then `origin/main`, then `origin/master`; pass `-b <remote>/<branch>` when PRs target another branch. It warns and fetches the base before checking.

2. **The bucket is advice, not permission.** Anything you know is in use — a pane still working in it, a branch Ruaridh is reviewing, a prototype he has not looked at yet — wins over the script's suggestion.

3. **Verify usage before deleting.** A tree with an open PR is in use. A tree whose branch is not merged is in use by definition. When in doubt, read the pane list (`herdr`) and the ticket before deciding.

4. **Pause on irreversible loss.** `wip:N` is N tracked uncommitted edits. Show the diff and get a decision first: removing a clean worktree is recoverable from its branch, but uncommitted work is gone. `scratch:N` is untracked throwaway, safe to drop, but name the files. **Never reset, stash or discard to make a tree clean** (`ruaridh-mode`, non-negotiable 4): make the work durable with a `wip:` commit (`handoff`) or leave the tree alone.

5. **Prune the confirmed set.** Per path, `git worktree remove <path>` (add `--force` only for a tree you have confirmed has no uncommitted tracked work). If the directory survives on ignored build artifacts, remove it, then `git worktree prune`. Branch refs survive, so no commits are lost.

6. **Confirm and report.** Space reclaimed, the worktrees pruned, and a one-line reason for each one held back (in use by which pane, or uncommitted work, or not merged). The reply shape is the point: a bare "cleaned up" hides the tree you decided to keep.

Removing a worktree is the one step in this family with no code review behind it, so the gates above are the review.
