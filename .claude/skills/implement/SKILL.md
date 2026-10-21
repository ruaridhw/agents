---
name: implement
description: Build one ticket, or a wave of tickets, from fetch to merged and done. Inline in this session with a progress ledger and recorded rulings, or delegated to Herdr builders with written briefs while you coordinate. Use when given a ticket ref, several refs or "a wave", or after to-plan once Ruaridh has picked inline or delegated.
upstream:
  - repo: mattpocock
    path: skills/engineering/implement/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
  - repo: mattpocock
    path: skills/engineering/implement-spec/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
  - repo: superpowers
    path: skills/executing-plans/SKILL.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: superpowers
    path: skills/subagent-driven-development/SKILL.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: superpowers
    path: skills/dispatching-parallel-agents/SKILL.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/feature.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/refactoring.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/orchestrate.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: self
    path: .claude/skills/orchestrating-reviewed-build
    sha: bed823f3b85b9dfd360f434cd62172bfc6d5495b
  - repo: self
    path: .claude/skills/herdr-agent-handoff/SKILL.md
    sha: bed823f3b85b9dfd360f434cd62172bfc6d5495b
---

# implement

The ticket is the contract, the spec is the authority behind it, the plan is its argument. You prove each step with a test (or the repo's loop) you watched fail and then pass, and you leave a record that survives your own forgetting.

## Start

1. **Fetch the ticket** per `.agents/tracker.md` and state its title in one line. If the ref is ambiguous, ask. Read its parent spec and any comments; if a handoff summary or a `work.branch` exists for it, this is a pickup: run `handoff` (pickup) first.
2. **Worktree before the first edit**: `.worktrees/<ticket-ref>-<slug>` in the repo, branch of the same name, based on the freshly fetched remote default branch, or on the previous ticket's branch when that PR is still awaiting Ruaridh's merge (the stack). Set `work.branch` on the ticket.
3. **The task list**: the plan's tasks for this ticket (`.scratch/plans/`), or, with no plan, one task you derive from the ticket: files, the test that proves the Done-when, steps from `.agents/build-loop.md`.
4. **Mode**: whatever Ruaridh picked at the end of `to-plan`. A single small ticket with no plan runs inline. Several refs or "a wave" run delegated.

## Inline

- **Ledger** at `.scratch/plans/<slug>.ledger.md`, first line `# Ledger: <plan or ticket>`. A task with a `Task N: complete` line is done: after compaction trust the ledger and `git log`, never your memory. Shape in `references/ledger.md`.
- **Continuous**: do not stop to check in between tasks. Narrate at most a line between tool calls.
- **Rulings, not stalls.** When the plan contradicts the spec, an interface does not match, or a command cannot work, decide the smallest change the spec allows and write `Ruling: <what> — <why> — <cost if wrong>` in the ledger. An unledgered deviation is a decision made in secret.
- **Four things stop you**: an irreversible or destructive step; a security-sensitive action; a side effect outside the worktree that needs asking (merge, push to a shared branch, publish); a plan so broken every path is a guess. Ask in chat, or the Inbox if he is away.
- **Per task**: work the steps in order under the build loop. Every command has an expected result; compare. Wrong code → `debug`; wrong plan → ruling. Commit per the plan (gitmoji, why line). The task is complete only when every named test ran in this task and you read the output, the final run passed, and every deviation has a ruling. Then the ledger line.
- **Final review**: spawn the reviewer role in a Herdr pane on the whole branch (base..head), with the spec, the plan's Review focus and the ledger's rulings. Re-grade its findings by what a person using the result would get. Critical and important: one fix pass, each fix with a test that failed first and a green suite. Minor: ledgered as deferred. A finding you will not fix is a ruling.
- **Report**: "Rulings I made" and "Deferred minors", exhaustive, in order.

## Delegated

You coordinate; you do not write the code.

1. **Split** the wave into units with disjoint files, one worktree and branch per unit. Blocking first steps run before fan-out; shared writes serialize; shared contracts before the parallel work; a risky switch last. Name why when one builder is best.
2. **Brief** each unit with `references/brief.md`. A field you cannot fill is a unit not yet scoped. Briefs point at context (ticket, spec, plan task, commits) instead of copying it; paste an upstream unit's report in full when this one depends on it.
3. **Spawn** builders with `herdr` (builder role, `--lean`, worker mode, `--no-wait`), a rolling window of a handful at a time, refilled as units finish. For a team that must know each other, use the team spawner and its roster.
4. **On each completion**: read the summary, then the diff. Run its verify commands yourself if the stakes warrant. Send fixes back to the same builder (`herdr agent prompt`), or respawn fresh with consolidated scope after two failed rounds; never chain resumes on a muddled brief.
5. **Review each integrated phase** with the reviewer role in a separate pane; findings come to you, not to builders. Triage each against the spec, return actionable ones to the owning builder, record rejections.
6. **Close every pane you created** once its work is integrated (`panes.py close`).

## Landing

1. When the branch is ready: `review` (see `ruaridh-mode` for the current stand-in), then `pr`, one PR per ticket on the stack base.
2. Merge only with Ruaridh's yes, by the recipe in `pr`. Then mark the ticket `merged` with the PR and merge sha.
3. Prove it per `.agents/prove-landed.md` (default: the tests on the merged sha). Close as `done` only when the ticket's Done-when is observed; one ticket at a time, as soon as it is.
4. Stopping short for any reason: `handoff` (pause). Never end the session with a stale ticket state or `work.*` signal.
