# Handoff file shapes

Delegate work without importing worker transcripts. Every delegated agent
writes two files at the absolute paths its brief gives: a concise summary for
the coordinator to ingest, and a raw log for audit and debugging. A pause
writes the summary shape too, so a session handing over and a worker reporting
come back in one form.

## Summary (pause)

`.herdr-handoffs/<YYYY-MM-DD>-<slug>-summary.md`, at the root of the repo the
work belongs to.

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

Point at the plan, the ledger, the ticket and the commits instead of copying
them, and redact secrets.

## Summary (worker report)

`.herdr-handoffs/<agent>-summary.md`, named in the brief.

```markdown
# <agent>: summary
**Outcome:** done | partial | blocked, in one or two sentences.
**Files changed:** paths, one line each.
**Verification run:** commands and results.
**Rulings / deviations:** `Ruling: <what> — <why> — <cost if wrong>` lines.
**Blockers / questions for the coordinator:** or none.
**Raw log needed?** yes (why) / no.
```

The worker ends its final chat message with the summary text and
`HANDOFF_WRITTEN <summary path> <raw path>`, after sending
`(aimsg) DONE <name> <summary path>` to the pane that created it (`herdr`).

## Raw log

`.herdr-handoffs/<agent>-raw.md`: commands run, their outputs trimmed to what
matters, diffs, errors, the line ranges read, and the reasoning behind
decisions. Never pasted into chat. The coordinator reads it only when the
summary says blocked or uncertain, or exact evidence is needed.

Three habits keep the log worth reading:

- Batch independent probes into one bash call: one pipeline answers what would
  otherwise take several tool calls.
- Locate with `rg` first, then read with offset and limit around the hits.
- Read each file once, and note the line ranges in the raw log so later steps
  work from those notes.
