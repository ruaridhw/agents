---
name: handoff
description: Pause in-flight work so another session can resume it cleanly, or pick up work an earlier session paused. Use when told to "stop", "pause" or "hand this off", when context is nearly spent, or when a session ends with work in flight; use when intake finds a handoff summary in `.herdr-handoffs/` or a ticket with `work.branch`. Also owns the summary and raw-log shapes every worker writes.
upstream:
  - repo: mattpocock
    path: skills/productivity/handoff/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/pause-safely.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/session-pickup.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: self
    path: .agents/skills/herdr-agent-handoff/SKILL.md
    sha: 79c8a819b683ca3451b74586b4dc45655e1ec092
---

# handoff

> **Without Herdr** (`HERDR_ENV` is not `1`, for example Claude Code on the web): there are no panes to stop or close, and the checkout is discarded with the session, so commit the summary to the session branch. See `<skills dir>/ruaridh-mode/references/cloud.md`.

Work crosses a session boundary in one of two directions: a session stops and
hands over, or a session picks up what an earlier one stopped. This skill owns
both directions, and the two files every delegated agent writes along the way.

Each half rests on one idea. **You own a clean stop:** leave a checkpoint a
cold-start agent can resume from. **You own the resume point:** read the prior
trail, don't redo it.

The record lives in `.herdr-handoffs/` at the root of the repo the work belongs
to, gitignored there, and every path this skill hands on is absolute, so cwd
drift cannot lose a handoff. A repo that does not ignore the directory yet gets
the line added before the first write.

## Pause

**You own a clean stop. Leave a checkpoint a cold-start agent can resume from.**

Explicit only. On "keep going", "going to bed, keep going" or "don't stop", do
not pause: those mean continue. The other triggers are context that is nearly
spent, and a session that is about to end with work in flight.

1. **Stop at a safe boundary.** Finish the current atomic step, or back out of
   it. Start nothing new, and tell every worker you started in a Herdr pane to
   stop at a safe boundary and write its two files (`herdr`).
2. **Take no irreversible action to pause.** No PR and no merge to pause; no
   push you did not already have out.
3. **Make the work durable.** Commit uncommitted edits as one clear
   `🚧 wip: <what is in flight>` commit on the current branch, in the ticket's
   worktree, with a one-line body saying why, so nothing is lost. If the tree
   is broken, say so in the commit body in one line. Push it only if the branch
   is already pushed.
4. **Close the panes you created** through `herdr` (`panes.py close --mine`),
   which records each worker's session before closing, so pickup can bring back
   the same session. Close only what this session created.
5. **Write the summary** to `.herdr-handoffs/<YYYY-MM-DD>-<slug>-summary.md`, in
   the shape in `references/shapes.md`: intent, where you are, progress and what
   is verified, current state, next step, key files, gotchas. Capture it
   off-context. Where a decision trail already exists (the plan, the progress
   ledger, the ticket comments), point at it instead of duplicating it. Point at
   specs, plans and commits by path or ref; never copy them. Redact secrets.
6. **Signal the ticket** as its own profile says (`.agents/tracker.md`): comment
   the summary path and the resume point, leave the branch recorded, raise
   attention when a human decision is what blocks resumption, and mark it
   `needs-review` if the work stops short with no next session planned.
7. **Reply**: where you are in the loop, what is on disk versus still in your
   head (paths, no diff dumps), the commits you made and whether the tree is
   clean, and the first action on resume. This is a pause, not a final report.

A pause that leaves a decision owed which the next session cannot make either
goes to Ruaridh: ask per the Inbox convention before you stop.

## Pickup

**You own the resume point. Read the prior trail, don't redo it.**

Triggered when intake finds a summary in `.herdr-handoffs/`, a ticket with
`work.branch`, or when asked to continue someone else's work.

1. **Locate the prior trail.** The summary first, then the ticket and its
   comments, the branch, the plan, the ledger. Read the overview and the last
   messages first, then scan back for the decision points. For history beyond
   what they carry, search AgentsView rather than grepping session transcripts;
   parse a long trail in a Herdr pane and keep the reduced timeline in this
   thread, choosing the pane's model by role (`~/.config/agents/models.toml`).
2. **Reconstruct operational state.** The branch and worktree, what already
   landed (`git log`, `git diff` against the base), the open todos, the
   decisions made, the panes that were closed with their sessions recorded. The
   prior trail is authoritative input: resist the bias to re-derive it. If the
   branch moved and you have no local commits, adopt the remote head.
3. **Diff done vs pending.** Compare what shipped against what was planned, name
   the resume point, do not re-run the prior repro or redo completed work. A
   "let me verify from scratch" pass means you are treating the trail as
   untrustworthy when it is authoritative.
4. **Route the remaining work** to the curated skill that owns it (`implement`
   to continue the build, `pr` to land what is finished, `verify` to prove it,
   `debug` for a failure the trail left open, `triage` for what the pause
   surfaced) and pick the verdict: continue the execution, ship a finished
   recommendation, ratify or override a prior conclusion, or postmortem a
   failed run. Pickup ends here; the routed skill owns the rest.
5. **Verify the inherited claims the next step depends on** against the original
   goal on the real artifact: run the tests the summary says pass (`verify`). A
   passing prior self-report is not the proof. A re-derivation of everything is
   waste.
6. **Resume the panes the next step needs** with `herdr`
   (`panes.py resume <name>`), each worker back in its own session. The `wip:`
   commit stays in history; follow it with a real commit.

**Reply:** where the prior agent stopped, what you inherited versus what you
redid (ideally nothing redone), the resume point, and the outcome.

Where the trail and the artifact disagree about a decision only Ruaridh can
make, ask per the Inbox convention and carry on with the rest.

## The handoff document

Write the handoff summary so a fresh agent can continue the work: the pause
shape above is that document. Do not duplicate content already captured in
other artifacts (specs, plans, ADRs, issues, commits, diffs); reference them by
path or URL instead.

Redact any sensitive information, such as API keys, passwords or personally
identifiable information.

When the handoff names what the next session is for ("hand this off for the
merge", "someone else picks up the UI"), treat that as a description of what
the next session will focus on and tailor the document to it.

## Two files every worker writes

Delegate work without importing worker transcripts. Every delegated agent
writes a concise summary for ingestion and a raw log for audit and debugging.
The pause writes the same summary shape, so a session and a worker hand over in
one form.

Both paths are absolute and come from the brief. Read a raw log only when the
summary says blocked or uncertain, or when exact evidence is needed; never paste
one into chat. Before its final reply, a worker sends `(aimsg) DONE <name>
<summary path>` to the pane that created it, then the summary text and
`HANDOFF_WRITTEN <summary path> <raw path>`.

The shapes are in `references/shapes.md`. Spawning and the brief are not this
skill: those are `herdr` and `implement`.
