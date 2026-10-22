# The decision trail

Keep one canonical log per ticket.

A run is one agent conversation, including its later turns and any summary of it. A pickup, a replacement agent, or a new chat starts a new run. The trail is how a reader reconstructs what a long or unattended run decided, and it is what the ticket comment quotes.

## The format

A single TSV file, one row per decision, at `.scratch/decisions/<ticket>.tsv` in the repo. Cells stay single-line. Evidence is a pointer, not prose.

Append with `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>`; it writes the header on first use. The header row is also in `references/decision-log-template.tsv`. Columns:

- **ts.** ISO8601 timestamp, written by the script.
- **phase.** The phase or workstream.
- **decision.** What was chosen or done, one line.
- **why.** The reason in plain words. If a principle drove it, say it plainly, not as a jargon tag.
- **evidence.** A link or path that proves it: commit SHA, PR number, `file:line`, or an artifact, trace, or screenshot path. Never a paragraph.
- **result.** The outcome or predicate state: `tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

An example, plain-spoken so a reviewer reads it at a glance.

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the work first, about 100 components and roughly 75 hours	wanted to know the size before starting a long run	commit 3a9f1c2	found 5 things to sort out before starting
2026-05-24T09:40:00Z	harness	took screenshots of the old version before changing anything	so we can compare old against new and catch any visual change	scripts/snapshot.sh, baseline/	saved 120 reference screenshots
2026-05-24T11:15:00Z	widget	moved the widget styles over without changing how it looks	keep the change small and the result identical	commit 7c21e0a, pixel-diff 0	looks identical, tests pass
2026-05-24T12:30:00Z	widget	threw out a helper's work because its screenshots were blank	checked the real files instead of trusting its summary	worktree reset	reverted, tightened the instructions for next time
```

The log is a working artifact, not committed. It lives under `.scratch/`, which is gitignored, and it stays there after the run so a reviewer can read it. A trail worth keeping in history belongs in the summary or the ticket, not in a commit.

## Logging a row

Write each entry the way you would tell a teammate what you did. Plain words, concrete actions, no AI speak or abstract jargon (`review`'s prose pass applies to log text too).

The script strips stray tabs, newlines and carriage returns so cells stay on one line, and prefixes any cell whose first character a spreadsheet would parse as a formula (`=`, `+`, `-`, `@`) with a single quote. Evidence can come from a PR title, a filename or generated text, so it must not become formula execution when a reviewer opens the file in a spreadsheet. A bare `printf` appending a row works too, but mind those same bytes.

### Which rows are worth writing

Log decision points and checkpoints, not every action: a fork chosen, a unit completed with its verification result, a pivot or revert with its trigger, a blocker surfaced, a gate fixed. Skip the trivial and self-evident.

That is the rule. The precise split used when the trail goes to the ticket is:

- A row is **routine** when it records `.agents/build-loop.md` executing exactly as written, with no alternative considered: the failing test written, the run that failed, the implementation, the run that passed, the commit. A `start` row is bookkeeping and never routine or non-routine.
- A row is **non-routine** whenever a reader could disagree with it, which means any row that records a choice between defensible options or a result that changed the next step: a fork, a deviation from the plan or spec (a `Ruling:`), a pivot, a revert, a blocker surfaced, an escalation or a question, a gate fixed, or a task whose verification failed. When in doubt it is non-routine; the cost of one extra line in a ticket comment is small.

### The `start` rule

When a run adds to a log that already has rows, its first row has phase `start`, and so does its first row after another run's `start` row. A run that comes back to a log in a later turn first reads the log's last rows to see whether another run wrote since. A `start` row names the `ts` range of the rows before it that this run did not write, and its evidence names this run, such as its agent id or session file. Use phase `start` for nothing else.

## Surfacing it on the ticket

One comment per run or pause, posted per `.agents/tracker.md` (kata: `kata comment <ref> --body-file <path>`; GitHub: `gh api` on the issue, body from a file). The comment has three parts, in this fixed order:

1. A header line: the run, the row count, and the non-routine count.
2. One line per non-routine row, in the form `phase: decision — why → result`.
3. A pointer line: the trail's path and the run summary's path.

```
Decision trail: run of 2026-05-24 09:00, 14 rows, 3 non-routine. Trail `.scratch/decisions/abc4.tsv`.
- widget: moved styles without changing appearance — keep the change small and the result identical → pixel-diff 0, tests pass
- widget: threw out a helper's work — its screenshots were blank, the real files were not → reverted
- ship: held the merge — checks green but the ticket's Done-when was never observed → open
Summary: `.scratch/plans/abc4/abc4-summary.md`.
```

Routine rows stay in the file and out of the comment: the comment is for the calls a reader should weigh, and a wall of "wrote the test / it passed" buries them. The pointer line is what lets a reader open the rest.

Do not edit or delete the comment after posting. A later run posts its own comment, with its own `start` row accounting for the rows before it.

## Rules

- Append-only. A wrong call gets a new row that supersedes it. Never edit or delete history.
- Prefer evidence produced by committed scripts over hand-made one-offs. A script can be re-run by the reviewer; a screenshot you took once cannot.
- The trail is part of every `implement` run, whether inline or delegated. A delegated run's workers append their own rows; the coordinator's rows sit beside them.

## Audit the log against the transcript

At the end of the run, before handing back, check that the log told the truth. Search this run's transcript through AgentsView (the tooling rules in `ruaridh-mode` own how), not by grepping session files. Walk this run's rows against what actually happened. Each stretch of them begins at one of this run's `start` rows, or at the first row if this run created the log, and ends at the next `start` row of another run:

- Check that every row maps to a real decision or action.
- Check that each row's evidence resolves and shows what the row claims.
- A fork, pivot, or abandoned approach that shaped the work but is not logged is a gap. Add it.

Correct the log, not the story. The audit never edits or removes a row, even an invented one. When a row records neither a real decision nor a real action, or its claim or evidence is wrong, add a row that supersedes it with what actually happened and a pointer that resolves. This audit does not check rows outside this run's stretches. If this run's own work shows one of them is wrong, supersede it like any wrong call.

## The second-family read

Before handing back a run that produced a trail, have a model from a different family read it against the diff and the transcript. Self-review is not a substitute, and this is `review`'s reviewer pass, not a spawn from here: `review` owns the pane, the brief and the read-only rule.

- Decisions logged with weak or absent evidence.
- Verification steps skipped or claimed without proof in the transcript.
- Choices that look risky in hindsight: premature, scope-creeping, papering over a symptom.
- Gaps a reader would otherwise miss on a casual skim.

Lead the review file with the reviewer's model on its own line, then each flag pointing to specific rows or moments. "No flags" is a valid value.

## Reviewing the trail

Read top to bottom, follow the evidence pointers, spot-check. GitHub renders a committed TSV as a table; `column -s$'\t' -t <logfile>` renders it in a terminal. A row whose evidence does not resolve is a finding, not a formatting problem.

## Composing this skill

Other skills route their audit trail here instead of inventing one. Reference it by name and let it own the format. Do not restate the columns.
