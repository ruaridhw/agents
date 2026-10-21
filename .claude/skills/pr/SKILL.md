---
name: pr
description: Open, describe and merge pull requests the stacked way - one PR per ticket on the previous ticket's branch, gitmoji title, a one-minute body with before/after evidence and merge danger, merged only with Ruaridh's yes by the async recipe. Use whenever writing a PR body, opening a PR, or merging one.
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

## Before opening

1. **Green first.** Run the repo's checks in their own command and read the result. Failing checks: stop and fix, or report; never open a PR over red.
2. **Commits tell the story**: small, ordered, each landable; gitmoji subject in the imperative, one-line body saying why. New commits for follow-ups; no amends, no squashes unless Ruaridh asks.
3. **Base**: the previous ticket's branch while its PR awaits merge, otherwise the freshly fetched remote default branch. Rebase onto the base if it moved; never merge the default branch into the PR branch.

## Open

```bash
git push -u <remote> <branch>
gh pr create --base <base branch> --title "<gitmoji> <imperative summary>" --body-file <body.md>
```

- Open ready, never draft. One PR per ticket; five narrow PRs beat one wide one.
- Body in the shape below, written to a file first. Keep it a one-minute briefing for someone with the diff open.
- Do not write `Closes #N` / `Fixes #N`: merged is not done. The ticket moves to `merged` on merge and to `done` when proved (`implement`).
- Post the URL and keep building. Opening a PR does not start babysitting; that is a separate ask.
- If `gh pr edit` fails on the classic-projects deprecation, patch the body with `gh api -X PATCH repos/<o>/<r>/pulls/<n> -F body=@body.md`.

## Body

```markdown
## Why
The problem and the approach, one to three sentences.

## What changed
One to three bullets. Name a symbol or path only when it carries the change.

<the smallest visual that makes the point: a diff-sketch of a call tree, file tree, state flow or component tree; a mermaid sequence; pseudocode. Optional.>

## Scope
What it covers and what it deliberately leaves out.

## Evidence
- **Before:** <failing test run, output, screenshot>
- **After:** <passing run, output, screenshot>

## Merge danger
**Door:** one-way | two-way. <why, if not obvious>
**Blast radius:** <one word>. <who or what it touches, and why that is safe or risky>

## Verification
- <command or path actually run> → <result>

Ticket: <ref>   Stack: <base PR or "none">
```

Drop a section that has nothing to say, except Scope, Evidence and Merge danger. Screenshots are the best evidence for a visual change (before and after, at the size it is used); a test run that went red then green is next. Full shas, rebase history and file-by-file lists stay out.

## Merge

Only with Ruaridh's yes, given in this session for this PR (or this stack). Then follow `references/merge.md`: checks read first in a separate command, async merge for stacks, base first, poll until merged, adopt the remote heads, mark the ticket `merged`.

## Finishing without a PR

When he chooses to keep the branch or merge locally instead, do exactly that and report where the worktree is. Discarding work happens only when he asks for it by name.
