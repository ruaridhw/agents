---
name: handoff
description: Pause in-flight work cleanly so another session can resume it, or pick up work a previous session paused. Use when told to "stop", "pause" or "hand this off", when context is nearly spent, or when a session ends with work in flight (pause); use when intake finds a handoff summary or a ticket with work.branch (pickup). Also defines the summary and raw-log shapes every worker writes.
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
    path: .claude/skills/herdr-agent-handoff/SKILL.md
    sha: 79c8a819b683ca3451b74586b4dc45655e1ec092
---

# handoff

## Pause

Triggered by an explicit stop or pause, context that is nearly spent, or a session about to end with work in flight. Not triggered by "keep going", "don't stop" or "going to bed, carry on": those mean continue.

1. **Stop at a safe boundary.** Finish the atomic step you are in, or back out of it. Start nothing new.
2. **Nothing irreversible to pause**: no new PR, no merge, no push you did not already have out.
3. **Make it durable.** Commit uncommitted edits in the ticket's worktree as one `🚧 wip: <what is in flight>` commit with a why line; if the tree is broken, say so in the body. Push it only if the branch is already pushed.
4. **Panes you created**: tell each worker to stop at a safe boundary and write its summary, then close them with `herdr` (`panes.py close --mine`), which records their sessions so pickup can resume them.
5. **Write the summary** to `.herdr-handoffs/<YYYY-MM-DD>-<slug>-summary.md` in the shape in `references/shapes.md`. Point at specs, plans, ledgers, tickets and commits by path or ref; never copy them. Redact secrets.
6. **Signal the ticket**: comment the summary path and resume point; `work.branch` stays set; set `work.attention` when a human decision is what blocks resumption; add `needs-review` if the work stops short with no next session planned.
7. **Reply**: where you are, what is on disk versus only in your head, the commits and whether the tree is clean, and the first action on resume. A pause is not a final report.

## Pickup

Triggered when intake finds a summary in `.herdr-handoffs/`, a ticket with `work.branch`, or when asked to continue someone's work.

1. **Read the trail, do not redo it**: the summary, then the ticket and its comments, the branch (`git log` and `git diff` against its base), the ledger, the plan. For history beyond that, search AgentsView (never by grepping transcripts), in a Herdr pane if it is long.
2. **Rebuild state**: worktree and branch (adopt the remote head if the branch moved and you have no local commits), what landed, open decisions, panes that were closed with recorded sessions.
3. **Name the resume point** in one line, and what you inherited versus what you are redoing (ideally nothing).
4. **Verify the inherited claims that the next step depends on** against the real artifact (run the tests the summary says pass). A prior self-report is not proof; a re-derivation of everything is waste.
5. **Resume panes** that the next step needs with `herdr` (`panes.py resume <name>`), and continue in the skill that owns the work (usually `implement`). The `wip:` commit stays in history; follow it with a real commit.

## Shapes

The summary and raw-log shapes, used by every worker's report and by a pause, are in `references/shapes.md`.
