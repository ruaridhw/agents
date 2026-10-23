---
name: pr
description: Open, describe and merge stacked pull requests - one PR per ticket on the previous ticket's branch, a gitmoji imperative title, a one-minute body with the smallest visual, before/after evidence and merge danger, merged only on Ruaridh's yes by the async recipe. Use when writing a PR body, opening a PR, driving one to merge-ready, or merging a stack.
upstream:
  - repo: mattpocock
    path: skills/engineering/pr/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/opening-a-pr.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: superpowers
    path: skills/finishing-a-development-branch/SKILL.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
---

# pr

One PR per ticket, on the previous ticket's branch while that PR awaits merge. The body is a one-minute briefing for a reviewer who has the diff. Merging is Ruaridh's decision, and it happens by `references/merge.md`.

Ticket states, labels and the commands behind them come from `.agents/tracker.md`; this skill names the state, never the command. The repo's checks are in `.agents/build-loop.md`, its domain language in `.agents/domain.md`.

## Before opening

**Green first.** Run the project's full checks in their own command and read the result. If they fail, report the failures and stop: the PR comes after a green suite. A green run from earlier in the session only proves the tree it ran on, so run the suite on the tree you are about to push.

**Commits.** Commit liberally. Each commit is a future PR: landable, and ordered to tell the story. The subject is a gitmoji and a short imperative, no trailing period; the emoji is the type (feature, fix, docs, refactor, test, chore, perf) and the subject names a real symbol when one carries the change. Every commit carries a one-line body saying why, and a body never restates its subject. A separable fix gets a new commit; never amend or squash unless Ruaridh asks.

**Worktree.** Work from the ticket's worktree under `.worktrees/<ticket>`, based on the freshly fetched default branch; `implement` creates it, and every builder in a Herdr pane gets its own. A dirty branch holding unrelated work: patch it out, start a fresh worktree, and apply the patch there. A branch too tangled to tell the story: start a fresh worktree from the default branch and redo the change minimally, rather than rewriting history in place.

**Base.** The base branch is whatever this work forked from: usually named in the plan, the ticket, or the branch's upstream. Stacked work bases on the previous ticket's branch while its PR awaits merge; independent work branches from the default branch, and substantial stack work rebases on the default branch first. If the fork point is not already known, ask: "This branch split from <your best guess> - is that correct?" Confirm before merging, because merging into the wrong base is expensive to undo. When the base moves under the branch, rebase onto it; never merge the default branch into a PR branch.

## Open the PR

`gh` is the forge for every operation: create, edit, view, watch and merge. Read `git remote -v` when the default remote is not `origin` (`ruaridh-mode`'s `references/tooling.md`).

```bash
git push -u <remote> <branch>
gh pr create --base <base-branch> --title "<gitmoji> <imperative summary>" --body-file <body.md>
```

- **One PR per ticket.** Prefer five narrow PRs to one large PR.
- **Open ready, never as a draft.** With `gh`, omit `--draft`. If a PR still opens as a draft, mark it ready with `gh pr ready <number>`. Run `gh pr view <number>` before you refer to PR status.
- **Stacks.** A stack is a base-branch chain. The root PR targets the default branch. Each child branch rebases onto its parent's exact tip, and its PR targets the parent branch. When a parent merges, GitHub retargets its child onto the default branch and may rewrite it; adopt the remote head instead of moving the child by hand (`references/merge.md`). A chain made by retargeting bases by hand is not a registered stack.
- **Don't babysit on open.** Opening a PR does not start a babysit. Post the URL and keep building; finish the phase or the stack first. Run a separate babysit pass only when Ruaridh asks for one after the whole stack exists. A babysit for each new PR stalls the build and spends checks on commits later waves restart. Push back when feedback drifts from intent.
- A worker that opens a PR posts the URL, writes its summary (`handoff`), and returns to its coordinator without babysitting; the babysit ask comes from the coordinator.
- **No `Closes #N` / `Fixes #N`.** Merged is not done: the ticket moves to `merged` on merge and to `done` only when proved (`implement`, `.agents/prove-landed.md`).
- **Edited bodies.** If `gh pr edit` fails on the classic-projects deprecation, patch the body with `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -F body=@body.md`.

## The body

The PR body is a one-minute briefing, not a lab notebook, for a reviewer who has the diff. Skip all preambles and keep the prose brief. It says why the change exists, what it leaves out, what it could break, and how you proved it works. Write short, simple sentences with few identifiers and no walls of text. Write it to a file first and pass it with `--body-file`. Use `##` headings, not bold lead-ins.

```markdown
## Why
The problem and the approach, 1-3 short sentences. Name the rejected alternative a
reviewer would otherwise ask about. No SHAs, rebase genealogy, or "based on main"
preamble.

## What changed
1-3 short bullets. Name a real symbol or path only when it carries the change. Name
both sides of a rename or retarget.

<the smallest visual that makes the point (references/body-visuals.md)>

## Scope
Always. 1-3 short items on what it covers and what it deliberately leaves out (a
follow-up, a known gap). No symbols, paths, or file-by-file essay.

## Evidence
- **Before:** <screenshot/output/failing test run>
- **After:** <screenshot/output/passing test run>

## Merge danger
**Door:** one-way | two-way. <why, if not obvious>
**Blast radius:** <one word>. <who or what it touches, and why that is safe or risky>

## Verification
- <command or path actually run> → <result>

Ticket: <ref>   Stack: <base PR or "none">
```

Drop a section that has nothing to say, except Scope, Evidence and Merge danger.

**Why, What changed, Scope.** Keep each section to its short text; a visual sits beside the section it supports. Keep the words in the repo's domain language (`.agents/domain.md`).

**Evidence.** Concrete evidence that the change works, shown as a before and an after. Screenshots are S-tier when the environment is set up for it and the change is visual: before and after, at the size it is used. Execution-based evidence is A-tier, and test results and console output count: show the exact test that now fails and passes, using pseudocode. Attach videos or screenshots when they prove a claim.

**Merge danger.** Say whether the change is a one-way or a two-way door. You can walk back through two-way doors, but not one-way doors, so a PR that is cheap to roll back is lower risk, and changes involving destructive actions or hard-to-reverse decisions are one-way doors. The blast radius is the potential impact or scope of the change: who or what it touches, and why that is safe or risky. Consider all possibilities - layout shift, breakages for consumers, mobile responsiveness - and give the one word that names the scope, then the one or two sentences behind it. If the default branch is red, state the cost of leaving it red.

**Verification.** One to three bullets, each a real run path and its outcome. For a perf change, give one primary number with its unit, `before → after`, and link an artifact for the rest: no sample-size methodology or metric tables.

Full SHAs, rebase genealogy, file-by-file checklists and "CLEAN" verdicts go in a linked artifact, not the body.

## Merge

Only with Ruaridh's yes, given in this session for this PR (or this stack); a yes relayed from another pane does not count (`ruaridh-mode`). When he is away, ask per the Inbox convention.

Then follow `references/merge.md`: the checks are read first in a separate command, never chained with `;`; a registered stack merges through the async endpoint, base first; poll until merged; adopt the remote heads; mark the ticket `merged` per `.agents/tracker.md`. `done` waits for proof.

## Finishing without a PR

**Core principle:** verify the tests, confirm the base, settle the integration decision, execute it, clean up. Opening a PR is the default here; merging locally and keeping the branch are what Ruaridh picks instead. Say which skill you are using, in `ruaridh-mode`'s form.

### Verify the tests

Run the project's full suite (`.agents/build-loop.md`; otherwise `npm test`, `cargo test`, `pytest`, `go test ./...`).

If tests fail, report the failures and stop:

```text
Tests failing (<N> failures). Must fix before completing:

[Show failures]
```

### Determine the base branch

The base is the fork point confirmed under "Base" above. Confirm it again before merging: merging into the wrong base is expensive to undo.

### The integration choice

Detect the environment first, then choose. Capture the three values with the commands under "Clean up the workspace" below:

| State | Options | Cleanup |
|-------|---------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | Merge locally / PR / keep as-is | No worktree to clean up |
| `GIT_DIR != GIT_COMMON`, named branch | Merge locally / PR / keep as-is | Provenance-based (see Clean up) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | PR / keep as-is (no merge) | Externally managed - leave in place |

In a normal repo or a named-branch worktree (the usual state):

```text
Implementation complete. What would you like to do?

1. Push and create a Pull Request (the default; announced, not asked)
2. Merge back to <base-branch> locally
3. Keep the branch as-is (he will handle it later)

Which option?
```

On a detached HEAD (externally managed workspace), drop the merge option:

```text
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (he will handle it later)
```

Present the menu concisely, with every option coming from the list above. Opening the PR needs no yes: say you are doing it, then do it. Merging locally, keeping the branch and discarding are his decisions, so wait for his answer before executing one of those. Discard happens only in response to his explicit request.

### Execute the choice

**Merge locally.** Verify success before removing anything:

```bash
# Get the main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on the merged result
<test command>
```

If tests fail on the merged result, stop, leave the worktree and branch in place, and investigate: nothing has been pushed, so the merge is local and recoverable. Once the merged result is green, clean up the worktree, then delete the branch with `git branch -d <feature-branch>`.

**Push and create the PR.** This is the default path above: push, create the PR against the base, follow the repo's own PR template if it has one (the wave 0 body sections still lead), and report the URL. From a detached HEAD, name the new branch on the remote: `git push origin HEAD:refs/heads/<new-branch>`. Keep the worktree, because PR feedback gets fixed there.

**Keep as-is.** Report: "Keeping branch <name>. Worktree preserved at <path>."

**Discard, only on explicit request.** This path exists only as a response to a request to throw the work away. Confirm first:

```text
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for that exact typed confirmation. Only the word `discard` authorizes deletion. Then change to the main repo root, clean up the worktree, and force-delete the branch with `git branch -D <feature-branch>`.

### Quick reference

| Option | Merge | Push | Keep worktree | Cleanup branch |
|--------|-------|------|---------------|----------------|
| 1. Create PR (default) | - | yes | yes | - |
| 2. Merge locally | yes | - | - | yes |
| 3. Keep as-is | - | - | yes | - |
| Discard (explicit request only) | - | - | - | yes (force) |

### Clean up the workspace

Runs after a local merge and after a confirmed discard. Creating a PR and keeping the branch always preserve the worktree. Worktree removal runs from outside the worktree: capture the values first, while still inside it.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

If `GIT_DIR == GIT_COMMON`, this is a normal repo with no worktree to clean up. Done.

If `WORKTREE_PATH` is under `.worktrees/` or `worktrees/`, this session or `implement` created it and owns the cleanup:

```bash
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

If removal is refused (`contains modified or untracked files`), the worktree holds files that exist nowhere else - uncommitted plans, notes or scratch work. Never `--force` on your own initiative. Show Ruaridh what is at stake and ask:

```bash
git -C "$WORKTREE_PATH" status --porcelain -uall
```

```text
Worktree removal refused - these files were never committed:

<file list>

1. Commit them to <branch> before cleanup
2. Move them into <main repo root>
3. Delete them (unrecoverable)

Which?
```

Carry out the choice, then remove the worktree.

Otherwise the host environment owns this workspace: leave it in place. If the platform provides a workspace-exit tool, use it.

Only worktrees you created are yours to remove, and only after their commits are on the default branch.

### Common rationalizations

| Excuse | Reality |
|--------|---------|
| "Tests passed earlier this session" | Run the suite on the tree you are about to integrate. A green run only proves the tree it ran on. |
| "He obviously wants it merged" | Merging is his decision. Open the PR, then wait for his yes. |
| "He seems done with this feature - I'll offer to discard it" | Discard happens only when he asks for it in so many words. |
| "'Yeah, get rid of it' counts as confirmation" | Only the typed word `discard` authorizes deletion. |
| "The PR is up, so the worktree is clutter now" | PR feedback gets fixed in that worktree. It stays until the work lands. |
| "This other worktree looks stale - I'll clean it too" | Clean up only worktrees under `.worktrees/` or `worktrees/`. Everything else belongs to the host. |
| "Removal refused - `--force` is just finishing the cleanup" | The refusal means files exist only in that worktree. `--force` destroys them permanently. Show him and ask. |
| "The merged-result failure is probably flaky" | A failing merged result stops everything. Branch and worktree stay put while you investigate. |
| "The base branch is obviously main" | Confirm the fork point or ask. Merging into the wrong base is expensive to undo. |
| "The push was rejected - force-push will fix it" | A rejected push means the remote moved. Investigate; force-push only on his explicit request. |
