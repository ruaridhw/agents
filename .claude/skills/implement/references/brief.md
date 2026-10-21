# Builder brief

Write it to a file (`.herdr-handoffs/brief-<unit>.md`) and spawn with `--task-file`. Collapse it to a paragraph for a one-command unit, but keep goal, scope, verify and report.

```
ruaridh-mode: worker

GOAL        One sentence: the outcome, executable by someone with no access to this chat.
SCOPE       Worktree and branch (exclusive to this unit). Paths it may write. Paths it may not.
CONTEXT     Pointers: ticket <ref>, spec <path#section>, plan task <path#Task N>, relevant commits and files.
            Upstream unit reports pasted in full when this unit depends on them.
            Skill files it must read, by absolute path (lean workers cannot discover skills).
ACCEPTANCE  Checkable criteria, one per line: the ticket's Done-when and the plan task's tests.
VERIFY      Exact commands and what passing looks like; known gotchas.
TIMEBOX     Rough cap. On expiry: commit what is green, write the summary with what remains, stop.
FORBIDDEN   No merges, PR retargets, rebases or force-pushes; no tracker writes; no edits outside SCOPE;
            no reset, stash or discard of work you did not create. Plus unit-specific bans.
REPORT      Summary file <abs path> and raw log <abs path>: status, branch, head sha, what you ran and
            its output, deviations (as Ruling: lines), suggested follow-ups. End with
            HANDOFF_WRITTEN <summary> <raw>.
STANDING    The repo's standing rules: commit style (gitmoji + why line), build loop
            (.agents/build-loop.md), anything Ruaridh has said for this program.
```

Roster (teams only): the team spawner writes `.herdr-handoffs/team-*/roster.md` with each member's name, role, task, summary and raw paths; every member gets it. Sibling communication goes upward through the coordinator.
