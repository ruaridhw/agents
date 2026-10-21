# Handoff file shapes

Every delegated agent writes two files with absolute paths given in its brief: a summary for the coordinator to ingest and a raw log for audit. A pause writes the summary shape below.

## Summary (pause)

`.herdr-handoffs/<YYYY-MM-DD>-<slug>-summary.md`

```markdown
# <slug>: handoff summary

## Intent
What this work is for and the ticket/spec it serves (<refs>).

## Where I am
The step in the plan or loop, and what was verified (labelled verified / inferred / assumed).

## On disk vs only in my head
- On disk: <paths, refs, commits>
- In my head (now written here): <decisions not yet recorded elsewhere, hunches, half-formed next steps>

## Commits and tree state
Branch <b> at <sha>; `wip:` commit <sha> (clean | broken: <why>); pushed: yes/no.

## First action on resume
One concrete command or step.

## Key files
- <path>: why it matters

## Gotchas
Traps the next session will hit: flaky tests, a command that needs stdin redirected, a pane to resume (<name>, session recorded).
```

## Summary (worker report)

```markdown
# <agent>: summary
**Outcome:** done | partial | blocked, in one or two sentences.
**Files changed:** paths, one line each.
**Verification run:** commands and results.
**Rulings / deviations:** `Ruling: <what> — <why> — <cost if wrong>` lines.
**Blockers / questions for the coordinator:** or none.
**Raw log needed?** yes (why) / no.
```

The worker ends its final chat message with the summary text and `HANDOFF_WRITTEN <summary path> <raw path>`.

## Raw log

`.herdr-handoffs/<agent>-raw.md`: commands run, their outputs (trimmed to what matters), diffs, errors, the line ranges read, and the reasoning behind decisions. Never pasted into chat. The coordinator reads it only when the summary says blocked or uncertain, or exact evidence is needed.
