# Convention file templates

Fill the angle brackets. Keep each file short: a skill reads it every time.

The domain file is not here: its seed and its consumer rules are in `references/domain.md`.

## build-loop.md (code, the default; write only to change commands)

```markdown
# Build loop: code
Steps per task: write the failing test → run `<single-test command>` (FAIL) → implement →
run it (PASS) → run `<suite command>` → commit (gitmoji + why line).
Typecheck: `<command>`. Lint: `<command>`.
```

## build-loop.md (pointer to a template's loop)

```markdown
# Build loop
This repo's change cycle is not test-first code. Follow `<path to the loop skill>` for each task:
change one surface → push → prove it landed → run the case → compare with the expected result → commit.
```

## prove-landed.md

Default (omit the file): the suite on the merged sha of the default branch.

```markdown
# Proving a ticket landed
Merged is not done. A ticket is done when its Done-when is observed:
1. <how to confirm the merged change is what is running: a deploy check, a read-back, `<path to proof skill>`>
2. <run the case named in Done-when and compare with its expected result>
Record the evidence in the close message.
```

## deploy.md

```markdown
# Deploy
How a merged change reaches where it runs: <command or pipeline>.
Who authorises it: <Ruaridh / the other party>; never deploy without that yes in this session.
What to check after: <smoke check>.
```

## design-review.md

```markdown
# Design review
Applies when a change alters what users see or do materially.
Before tickets: mocks or screenshots of each changed screen and state in the spec's Design section,
reviewed by <who> in <Plannotator / a design tool>.
Before merge: before/after screenshots at the sizes used, in the PR.
```
