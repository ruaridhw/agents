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

## debug-loop.md

Write it only when the repo's debug loop differs from `debug`'s default (root cause before fix;
reproduce on the real surface; commit the failing repro before the fix; after three failed fixes,
stop and talk). Keep the default's four rules and replace or add what this repo does instead.

```markdown
# Debug loop
Steps for a bug here:
1. <how the failure is seen on the real surface: which command, run or tool reads it first>
2. <where the root cause is recorded before any fix: the ticket comment, the run log, the prompt diff>
3. <how the failing repro is captured: a test, a frozen case, the failing run pinned in `.scratch/`>
4. <what counts as a fix, and how it is proved: the same surface re-run, the case replayed>
After three failed fixes: stop and talk (<who>, or the Inbox convention when Ruaridh is away).
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

## review.md

```markdown
# Review gate
Per surface, the checks every review of a diff touching it must run first, and the rules that are hard violations there.

## <surface name>  (paths: <glob>, <glob>)
Checks, in order:
- <skill path, script or lint> — <what it catches>
Hard violations (cite the rule):
- <rule, one line>
```

For high-risk code surfaces, offer this additional review-gate block. Fill it with commands verified against the repo's installed tool versions; omit it for unrelated surfaces. `review` and `full-stack-e2e-review` share the protocol in `<skills dir>/verify/references/test-strength.md`.

```markdown
## Test strength (paths: <domain/parser/authorization/billing/state-machine globs>)
Checks, in order:
- `<covering test command>` — green baseline for the selected invariants.
- `<mutation command scoped to the reviewed base/head diff or enclosing module>` — test sensitivity to realistic breaks.
- `<property/fuzz command with reproducible seed and bounded run profile>` — generated boundary/adversarial cases against independent invariants.
Scope/budget: record base/head, selected modules/tests and <time/case budget> before running.
If no mutation runner exists, use isolated targeted manual mutants and report that narrower scope.
Hard violations:
- A demonstrated coverage gap or falsified contract property remains open.
- A mandatory check is unresolved or blocked but reported as passed.
Evidence: commands, scope, mutant dispositions, seeds/cases, shrunk counterexamples and restored green run.
Justify equivalent/out-of-contract survivors; classify timeouts and tool errors separately from killed mutants.
```

## references.md

```markdown
# References by surface
Read the named references before the first edit to a matching file.

- <glob> → <path to the reference>, <path>
```
