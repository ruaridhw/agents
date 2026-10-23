# Running a wave as a program

For a whole project handed to one standing coordinator session: multi-day, many stacked PRs, dozens of builders, Ruaridh checking in twice a day instead of every five minutes. Route here when the work outlives any single session; work one agent could finish inside the session's budget is not a program, and collapses to the wave loop in `SKILL.md`.

Ceremony must scale with the program. On cheap near-identical units, collapse it as each section says.

Three rules carry the rest.

- Completions are queue events, not interrupts.
- Every spawn and every resume carries the standing orders verbatim.
- The brief is the product. A vague brief fails quietly, because a worker cannot ask you a question.

## Roles and placement

- **Coordinator (this session).** Frames, authors briefs, drains completions, owns the report to Ruaridh, makes judgment calls. It never authors or edits code. Conflicted merges, chain rebases and code changes are always tasks. Mechanically landing a verified unit — a fast-forward or a clean cherry-pick of a builder's commit, then a push — is bookkeeping the coordinator may do itself on repos where local git is cheap; queueing finished work behind an idle stack is how a deadline harvests nothing. State lives where it already lives here: the tracker for units and their states (`.agents/tracker.md`), the Herdr pane ledger for who is where, `.herdr-handoffs/` for reports, the plan's ledger for rulings. Do not invent a second store.
- **Second coordinator, only past one session's drain capacity.** One per track, one track per coordinator; each nested layer re-pays a full orientation and a blocked coordinator hides its children while the parent idles. It owns its track's units and boards, authors its workers' briefs, spawns its own builders and reviewers, and rolls up aggregates at wave boundaries. It never forwards raw child reports. Cap in-flight children at what one drain can process, roughly ten, as a rolling window, never as blocking batches, which cost the slowest child of every batch.
- **Builder / reviewer.** One writer per worktree or branch. Prefer fewer, broader builders. A unit's reviewer runs on a different model family from its builder — that is what the `reviewer` role is for.

Depth stays at coordinator, track, builder. Author the track decomposition per project; build, landing and verification are common cuts, not a required shape. Hard-coded swarm trees were tried and parked as too rigid.

## The brief

`references/brief.md` is the template and its rules; scale it to the unit. A one-command unit gets the template collapsed to a paragraph that still names goal, scope, the verify command and the report shape. A sub-coordinator's brief adds its track boundary and unit list, its spawn budget, the drain protocol and the rollup format (per child: name, status, PR, head SHA, verdict, one line, plus track status and frontier delta).

The pilot exists to falsify your brief template, your verify recipe and your unit size while that costs one builder instead of fifty. Push one unit through the whole path — brief, builder, verification, stack entry, merge — and fix the contract from pilot evidence before any fan-out. On programs of near-identical cheap units, the first unit is the pilot: run it as a normal unit with its verify command inline, and fan out the moment it lands. A dedicated pilot pipeline is for expensive or novel unit shapes.

## Steps

1. **Frame.** State the done predicate as something countable ("all 126 units merged, each ledger-verified or better"). Quantify scope: units, rough effort, expected stacks, the wall-clock budget. Schedule landing against the budget: by roughly 70% of it, stop spawning and land what is verified. Name the tracks. Present the framing once; reversible prep proceeds without waiting.
2. **Write the standing orders** before any spawn: numbered lines, one constraint each — role policy, stack shape and count, verification bar, forbidden paths, escalation policy. They go verbatim into every spawn and every resume; directives decay across resumes, and each dropped one costs a human turn. When you catch yourself restating an instruction, add the line before you act.
3. **Pilot**, as above.
4. **Scale.** Spawn a rolling window of builders up to the in-flight cap, refilling as children finish. Recompute ready work after each drain: `kata ready` (or the tracker's equivalent) is the frontier. Relay upstream reports into downstream briefs. Keep sibling communication upward only. The sampled brief audit runs alongside the wave it samples and stops the next refill on failure, not the current one.
5. **Drain** at every drain point, by the queue discipline below.
6. **Land** continuously, never as a terminal phase. Integration starts with the first verified unit and runs alongside the remaining waves. Stack topology is `pr`'s: one PR per ticket, base chained, merge bottom up on Ruaridh's yes. Keep the frontier green before upper-stack work.
7. **Close.** Drain the final inbox, reconcile every spawned pane to a terminal row (done, abandoned, zombie-reconciled), confirm the predicate on the real artifact (`.agents/prove-landed.md`), confirm every landed PR has a verdict for its current head SHA, encode recurring corrections into the standing orders or the brief template. Leave the workspace intact; it is the postmortem.

## Queue and drain

- On a completion notice, record it and return to what you were doing. Never deep-review inline: a completion that needs review becomes a review unit. Never review a diff inside a drain.
- Drain in batches at four points: the end of a critical section, a track rollup, a tick of a long-running wait, and before a report to Ruaridh. Critical sections you finish first: authoring a brief, a stack operation, a conflict decision, writing a gate, updating the ledger or the frontier. Arrivals during a drain wait for the next one.
- Each drain classifies every pointer (landed, needs-verify, failed, zombie, noise), updates the tracker rows, runs the status query, then spawns the next wave in one message.
- Account for every spawned child at its track's rollup: arrived, respawned, or its scope explicitly absorbed. Silently redoing a missing child's work hides both the wasted spend and the coverage gap its result existed to close.
- A drain ends with three lines: counts against the states, what changed, gates open. Detail lives in the ledger.
- Report to Ruaridh in chat when he is here; otherwise ask per the Inbox convention, batched, never per item.

## Verification

Scale verification to the unit. When VERIFY is a single cheap command, the builder runs it and reports the output, and you spot-check receipts. A dedicated reviewer is for units whose verification is expensive, judgment-laden or high-blast-radius. A reviewer whose entire product would be re-running one command is ceremony, not verification.

Record a verdict per unit keyed by PR number plus head SHA: `live-ui-verified | unit-test-verified | type-check-only | verifier-blocked | verifier-failed`. CI green is an input to a verdict, not a verdict. Behavioural work needs better than `type-check-only`. `verifier-blocked` is not a pass: respawn when the environment heals. `verifier-failed` gets a fix unit, not a re-verify. A builder may self-report; a reviewer overrides it on the same key. A new head SHA voids the row, so re-verify after a restack. The record answers "was this verified", not memory and not the transcript.

A unit is not done until its output is externalized the moment it lands, never batched to the end of the run: a pushed branch, a ledger row, receipts in the workspace. Work that exists only on one machine when that machine dies was never done.

## Liveness and failure

- Never resume a pane to check on it: a resume restarts an idle agent. Probe read-only — the tracker, the reviews, the pushed branches, the pane list.
- A pane that finished without its `(aimsg) DONE` notice, or died silently, gets a synthetic row: unit, failure mode, last evidence, options. Replan on evidence as it arrives; never wait for full quiescence.
- Retry by mode: cap-hit or OOM, respawn with smaller scope. Network drop, retry as-is. Tool error, retry on a different role. Unknown, retry once. Two retries, then abandon the unit and replan around it.
- A zombie that returns hours late reconciles against the current frontier and the reviews before anything is accepted. Salvage unique findings through a fresh unit, never a blind merge.
- When continued spawning would produce garbage tree-wide (bad upstream output, broken acceptance, dead infra), write a stop line at the top of the standing orders, let in-flight work finish, fix the cause, clear it.
- Bound your own retries the same way you bound a child's. After a few consecutive tool aborts, stop retrying, write the durable state (what is done, where it lives, the exact command to resume) through `handoff`, and end the run.
- After a session restart: re-read the standing orders and the tracker, recompute the frontier, reattach work by PR and branch rather than pane id, respawn one coordinator per track from its stored brief plus current state, drain, resume.

## Escalation

Reaches Ruaridh, batched into the status page rather than per item: irreversible actions (force-push to shared branches, deploys, deletions, closing someone else's PR), genuine product or preference calls no experiment settles, a standing order that contradicts observed reality, a program-level dead end that survived a replan. Record each as an open gate before asking, and route work around it.

Never reaches him: frontier nudges, rebase mechanics, retries, CI flake triage, review-thread triage, format fixes, scope the brief already forbids (refuse and continue), and "should I keep going". When in doubt, act and log.

Mid-run discoveries fix only what blocks the frontier. Everything else parks as a follow-up ticket. At this fan-out a small scope leak multiplies into PRs nobody asked for.

## Reply

At checkpoints and close: the predicate and the count against it, tracks and what each landed, the frontier (PR list plus SHAs), the verdict summary, what was abandoned and why, gates awaiting Ruaridh (the only asks), and the workspace path. Numbers from the records, not narrative. Include PR links.
