---
name: setup-project
description: Configure a repo for the curated skills by writing its .agents/ convention files (tracker, build loop, proof of landing, deploy, design review, domain), creating tracker labels and linking the rare skills it uses. Use once per repo before the first to-spec, to-tickets or triage there, when a skill reports a missing .agents/tracker.md, or to switch a repo's tracker.
upstream:
  - repo: mattpocock
    path: skills/engineering/setup-matt-pocock-skills/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
---

# setup-project

General skills name hook points; this skill binds them for one repo. Explore, present what you found with a recommended answer per file, confirm, then write. Re-run only to switch a profile; edit the files directly for small changes.

## Files

All in `.agents/` at the repo root. A missing file means the skill's default, so write only what differs or what a skill needs (tracker always).

| File | What it binds | Default when missing |
| --- | --- | --- |
| `tracker.md` | Which tracker, project, labels, priorities, states, commands | none: required by `to-spec`, `to-tickets`, `triage`, `implement` |
| `build-loop.md` | The step list `to-plan` and `implement` use | code: failing test → run → implement → run → commit |
| `prove-landed.md` | What makes a merged ticket `done` | the tests, run on the merged sha of the default branch |
| `deploy.md` | How and when a change reaches where it runs, and who authorises it | no deploy step |
| `design-review.md` | The gate for material UI/UX change | Design section reviewed in the spec gate |
| `domain.md` | Where the glossary and ADRs live, and the vocabulary rules | `GLOSSARY.md` and `docs/adr/` at the root, if present |

## Steps

1. **Explore.** `git remote -v` (the default remote may not be `origin`); `AGENTS.md` / `CLAUDE.md` and whether they already point at `.agents/`; existing `.agents/*.md`; an older tracker doc (for example `docs/agents/issue-tracker.md`) to migrate; whether a kata workspace is bound (`kata projects list`, `kata quickstart`); `gh repo view`; test and lint commands (`Makefile`, `package.json`, `pyproject.toml`); any UI; glossary and ADR locations; which services the repo uses (cloud SDKs, config files, IaC) for rare skills; whether a parent template (a kit or scaffold) already ships convention files.
2. **Present and ask, one file at a time**, leading with the recommended answer so a word accepts it:
   - **Tracker**: kata (`conventions/tracker-kata.md`) or GitHub (`conventions/tracker-github.md`) from this repo; propose what the repo already uses. Fill the profile's Project block.
   - **Build loop**: code by default; or a pointer to a loop skill the repo's template ships, for repos whose change cycle is not test-first code (`references/templates.md`).
   - **Prove landed**: default, or a pointer to the template's proof skill.
   - **Deploy**, **design review**: only when the repo deploys or has UI.
   - **Domain**: only when the glossary or ADRs live somewhere non-default.
   - **Rare skills**: the service skills in `~/.agents/rare/` that match what the repo uses.
   When a parent template already ships a file, write only the repo's specifics on top of it.
3. **Show the drafts** and let him edit before writing.
4. **Write.**
   - The `.agents/*.md` files, from the profile or `references/templates.md`.
   - Migrate an older tracker doc into `.agents/tracker.md` and replace the old file's body with a one-line pointer.
   - A short `## Agent conventions` block in the repo's existing `AGENTS.md` (or `CLAUDE.md` if only that exists; ask before creating either): one line per file written, pointing at it. Update the block in place on re-runs.
   - **Labels**: GitHub: `gh label create` for each kind, priority, state and triage label the repo lacks. kata: labels are created on first use; nothing to do.
   - **Rare skills**: symlink each chosen `~/.agents/rare/<name>` into the repo's `.claude/skills/<name>` and add those paths to `.gitignore` (the links point outside the repo).
5. **Commit** in a worktree on a branch (`🔧 Configure agent conventions` with a why line) and open a PR with `pr`; the files are the repo's, not yours.
6. **Report** which skills now read which file.
