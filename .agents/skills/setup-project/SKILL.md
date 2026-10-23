---
name: setup-project
description: Configure a repo for the curated skills by writing its .agents/ convention files (tracker, build loop, debug loop, proof of landing, deploy, design review, domain), creating tracker labels and linking the rare skills it uses. Use once per repo before the first to-spec, to-tickets, triage, implement or debug there, when a skill reports a missing .agents/tracker.md, or to switch a repo's tracker.
upstream:
  - repo: mattpocock
    path: skills/engineering/setup-matt-pocock-skills/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
---

# setup-project

Scaffold the per-repo configuration that the curated skills assume:

- **Issue tracker**: where tickets live — the tracker, its project, refs, labels, priorities, states and exact commands
- **Build loop**: the steps each task goes through
- **Debug loop**: how a bug is run down here, when it is not the default
- **Proof of landing**: what makes a merged ticket `done`
- **Deploy**: how and when a change reaches where it runs, and who authorises it
- **Design review**: the gate for material UI/UX change
- **Domain docs**: where the glossary and the ADRs live, and the rules for reading them

General skills name these hook points and fall back to a default when one is missing; this skill binds them for one repo. Every file lives in `.agents/` at the repo root. A missing file means the skill's default, so write only what differs from the default or what a skill needs (the tracker always).

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with Ruaridh, then write. Re-run it only to switch a profile; edit the files directly for small changes.

## Files

| File | What it binds | Default when missing |
| --- | --- | --- |
| `tracker.md` | Which tracker, project, labels, priorities, states, commands | none: required by `to-spec`, `to-tickets`, `triage`, `implement` |
| `build-loop.md` | The step list `to-plan` and `implement` use | code: failing test → run → implement → run → commit |
| `debug-loop.md` | How `debug` runs a bug down in this repo | root cause before fix; reproduce on the real surface; commit the failing repro before the fix; after three failed fixes, stop and talk |
| `prove-landed.md` | What makes a merged ticket `done` | the tests, run on the merged sha of the default branch |
| `deploy.md` | How and when a change reaches where it runs, and who authorises it | no deploy step |
| `design-review.md` | The gate for material UI/UX change | Design section reviewed in the spec gate |
| `domain.md` | Where the glossary and ADRs live, and the vocabulary rules | `GLOSSARY.md` and `docs/adr/` at the root, if present |
| `review.md` | Per surface: the checks `review` must run and the rules that are hard violations there | no mandatory per-surface checks |
| `references.md` | Per surface: the references `implement` must read before the first edit | none |

The tracker profiles are `conventions/tracker-kata.md` and `conventions/tracker-github.md` in the curated-skills repo this skill lives in: one of them is copied into the target repo and its Project block filled. The seeds for the other files are `references/templates.md` and, for the domain file, `references/domain.md`, both beside this `SKILL.md`. Skills read the target repo's copies, never these sources.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config`: is this a GitHub repo? Which one? Which remote is the default, since it may not be `origin`?
- `gh repo view`, and whether a kata workspace is bound already (`kata projects list`, `kata quickstart`)
- `AGENTS.md` and `CLAUDE.md` at the repo root: does either exist? Is there already an `## Agent conventions` section in either? Does either already point at `.agents/`?
- `.agents/`: does this skill's prior output already exist?
- An older tracker doc to migrate, for example `docs/agents/issue-tracker.md`
- `GLOSSARY.md` at the repo root, and `docs/adr/`
- The test and lint commands (`Makefile`, `package.json`, `pyproject.toml`)
- Whether the repo has a UI, and whether it deploys
- Which services the repo uses (cloud SDKs, config files, IaC), for the rare skills
- Whether a parent template (a kit or a scaffold) already ships convention files

### 2. Present findings and ask

Summarise what's present and what's missing. Then take the sections in order. One section, one answer, then the next.

Lead each section with the recommended answer so Ruaridh can accept it in a word. Give a one-line explainer only when the choice genuinely branches; skip the section entirely when exploration already settled it (Section F when the repo does not deploy, Section G when it has no UI, Section H when it uses no service skill).

When he is away, put the round out per the Inbox convention and carry on with what an unanswered section defaults to.

**Section A: Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-spec`, `to-tickets`, `triage` and `implement` read from and write to it. They need to know whether to call `kata create`, `gh issue create`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

Default posture: propose what the repo already uses, which usually settles it. A repo with a bound kata workspace, or a kata project named beside it, gets kata (`conventions/tracker-kata.md`). A `git remote` that points at GitHub and no kata project gets GitHub (`conventions/tracker-github.md`). Where the two disagree, or neither is there, ask, and offer:

- **kata**: tickets live in the kata workspace for this repo. The `kata` CLI brings refs, states, priorities, blocking edges and idempotency keys with it.
- **GitHub**: issues live in the repo's GitHub Issues (uses the `gh` CLI).
- **Something else** (Jira, Linear, …): ask him to describe the workflow in one paragraph; record it as freeform prose, and say that no profile covers it yet, so that prose is what the skills will follow.

Record the choice in `.agents/tracker.md`, with the profile's Project block filled. The profile carries the rest: refs, creating (search first, never a duplicate, an idempotency key on every create), kinds, priorities, `open → merged → done`, and the comments that mark progress.

**Section B: Triage labels.** Write these, don't ask. `triage` is a curated skill and so always available, and the profile fixes its vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, one at a time. A repo that already uses other strings for those four roles gets a note to that effect in `.agents/tracker.md`, so `triage` applies the labels that exist instead of creating duplicates.

**Section C: Domain docs.** Default to **single-context**: one `GLOSSARY.md` and `docs/adr/` at the repo root. That fits almost every repo, so settle it without asking. Write `.agents/domain.md` when a skill needs it spelled out anyway, because the paths differ or a term's owner has to be named; the file carries the paths and the consumer rules from `references/domain.md`.

**Section D: Loops.** Two files, one for building and one for debugging; neither needs a file when the repo matches the default.

- **Build loop.** Default to **code**, which needs no file: failing test → run → implement → run → commit. Ask only when the repo's change cycle is not test-first code (a change to a surface that has to be pushed and then observed, say), and then point at the loop skill the repo's template ships (`references/templates.md`).
- **Debug loop.** Default to what `debug` states, which needs no file: root cause before any fix; reproduce on the real surface; commit the failing repro before the fix; after three failed fixes, stop and talk. **Ask whether the repo's debug loop differs from that**, and write `.agents/debug-loop.md` only when it does. It usually does when the build loop isn't code: a prompt or process repo's debug loop might be "read the failing run first, then the prompt it was built from", and `references/templates.md` has the shape.

**Section E: Proof of landing.** Default to the suite on the merged sha of the default branch, which needs no file. Ask when a ticket's `Done-when` can only be observed where the change runs; then write the file with the check and the case to run (`references/templates.md`).

**Section F: Deploy.** Ask when the repo deploys: how a merged change reaches where it runs, who authorises it, and what to check after.

**Section G: Design review.** Ask when a change alters what users see or do materially: who reviews, where the mocks or screenshots go, and what the PR carries.

**Section I: Review gate.** Ask which surfaces carry rules a reviewer must apply every time (a prompt directory with its own lint and audit skills, a schema directory with a compatibility check), and for each: the path pattern, the checks to run (skill path, script or lint) and the rules that are hard violations. The strict version of any authoring rule belongs here rather than in the build loop: `review` is the gate, the loop is only the how-to. Write `.agents/review.md` only when a surface has such rules (`references/templates.md`).

**Section J: References.** Ask which surfaces have a reference an agent must read before editing them (CLI quirks, trap lists, workbook layouts, a sibling-agent protocol), and write `.agents/references.md` as path pattern → references. Skip the file when nothing needs reading first.

**Section H: Rare skills.** Offer the service skills in `~/.agents/rare/` that match what exploration found the repo using (`rare-skills` reads them; this links the ones a repo needs). Two or three, named, never the whole list.

When a parent template already ships a convention file, write only the repo's specifics on top of it.

### 3. Confirm and edit

Show a draft of:

- The `## Agent conventions` block to add to whichever of `AGENTS.md` / `CLAUDE.md` is being edited (step 4 has the selection rules)
- The contents of each `.agents/*.md` file being written

Let him edit before writing.

### 4. Write

**Pick the file to edit:**

- If `AGENTS.md` exists, edit it.
- Else if `CLAUDE.md` exists, edit it.
- If neither exists, ask which one to create; don't pick for him.

Never create `CLAUDE.md` when `AGENTS.md` already exists (or vice versa); always edit the one that's already there.

If an `## Agent conventions` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite edits to the surrounding sections.

The block, with a sub-block for each file actually written (the tracker's is always there):

```markdown
## Agent conventions

### Issue tracker

[one-line summary of where tickets are tracked]. See `.agents/tracker.md`.

### Build loop

[one-line summary of the loop, or "the default code loop"]. See `.agents/build-loop.md`.

### Debug loop

[one-line summary of how a bug is run down here, or "the default debug loop"]. See `.agents/debug-loop.md`.

### Proof of landing

[what makes a ticket done here]. See `.agents/prove-landed.md`.

### Deploy

[how a change reaches where it runs, and who authorises it]. See `.agents/deploy.md`.

### Design review

[when the gate applies and who reviews]. See `.agents/design-review.md`.

### Domain docs

[one-line summary of where the glossary and ADRs live]. See `.agents/domain.md`.

### Review gate

[which surfaces carry mandatory checks]. See `.agents/review.md`.

### References

[which surfaces need reading first]. See `.agents/references.md`.
```

Then write the files themselves, from the profile or the seed references.

If an older tracker doc exists, migrate its content into `.agents/tracker.md` and replace the old file's body with a one-line pointer to the new one.

Create the labels the tracker is missing: on GitHub, `gh label create` for each kind, priority, state and triage label the profile names. kata creates its labels on first use, so there is nothing to do. A repo already using other strings keeps them (Section B).

Link the rare skills chosen in Section H: symlink each `~/.agents/rare/<name>` into the repo's `.claude/skills/<name>` and add those paths to `.gitignore`, since the links point outside the repo.

Commit in a worktree on a branch (`🔧 Configure agent conventions` with a why line) and open a PR with `pr`. The files are the repo's, not yours.

### 5. Done

Tell him the setup is complete and which curated skills now read which file. Mention that he can edit `.agents/*.md` directly later; re-running this skill is only necessary to switch a tracker or build-loop profile, or to start over.
