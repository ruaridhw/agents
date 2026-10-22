# Builder brief

The brief is the product. A vague brief fails quietly, because a worker cannot ask you a question it does not know it has. Every spawn carries all of it, and a field you cannot fill is a unit you have not scoped yet.

Write it to `.herdr-handoffs/brief-<unit>.md` and spawn with `--task-file`. Collapse it to a paragraph for a one-command unit, but keep goal, scope, verify and report. A 4KB scaffold around a two-line edit costs more to write and obey than the edit.

```
ruaridh-mode: worker

GOAL        One sentence: the outcome, executable by someone with no access to this chat.
SCOPE       Worktree and branch (exclusive to this unit). Paths it may write. Paths it may not.
CONTEXT     Pointers: ticket <ref>, spec <path#section>,
            plan task <path#Task N> extracted to <brief path>,
            relevant commits and files.
            Upstream unit reports pasted in full when this unit depends on them.
            Skill files it must read, by absolute path (lean workers cannot discover skills).
ACCEPTANCE  Checkable criteria, one per line: the ticket's Done-when and the plan task's tests.
VERIFY      Exact commands and what passing looks like; known gotchas.
TIMEBOX     Rough cap. On expiry: commit what is green, write the summary with what remains, stop.
FORBIDDEN   No merges, PR retargets, rebases or force-pushes; no tracker writes;
            no edits outside SCOPE; no reset, stash or discard of work you did not create.
            Plus unit-specific bans.
REPORT      Summary file <abs path> and raw log <abs path>: status, branch, head sha,
            what you ran and its output, deviations (as Ruling: lines), suggested follow-ups.
            End with HANDOFF_WRITTEN <summary> <raw>.
STANDING    The repo's standing rules: commit style (gitmoji + why line), build loop
            (.agents/build-loop.md), anything Ruaridh has said for this program.
```

## Filling the fields

- **CONTEXT points at context; it does not copy it.** The plan's task text is extracted to `.scratch/plans/<plan-basename>/task-<N>-brief.md` and introduced as "read this first — it is your requirements, with the exact values to use verbatim". Exact values (numbers, magic strings, signatures, test cases) appear only there, never in two places that can drift.
- **The dispatch adds only what the brief cannot know**: one line on where this task fits in the project; interfaces and decisions from earlier tasks; your resolution of any ambiguity you noticed in the task text; a pointer to a parked ledger finding in the area this task touches; the report-file path. A dispatch describes one task, not the session's history. Never paste accumulated prior-task summaries: a real one reached 42k characters of which 99% was pasted history.
- **A dependency is a context relay, not just ordering.** When this unit consumes an upstream unit's output, that unit's report is pasted in full. Undeclared upstream context makes the builder guess.
- **A unit that scopes to several files** lists every file and its change, and the reviewer checks the diff file by file: a listed file the diff never touches is a missing finding, however clean the rest looks.
- **Carry `references/builder.md`** by absolute path in every brief: the standing instructions every builder works under (ask first, self-review, escalate, the no-panes contract, the report shape).
- **Standing orders go in every spawn and every resume, verbatim.** Directives decay across rounds, and each dropped one costs a human turn. When you catch yourself restating an instruction, add it to the standing-orders text before you act.

## Auditing briefs

Quality decays late in a run, so audit one sampled brief per builder per wave, alongside the wave it samples and never as a gate in front of it. A failing brief stops that track and fixes your own brief template, not just the worker's instructions: the brief is the coordinator's product.

## Roster (teams only)

The team spawner writes `.herdr-handoffs/team-*/roster.md` with each member's name, role, task, summary and raw paths; every member gets it. Sibling communication goes upward through the coordinator.
