# Ledger

`.scratch/plans/<plan-basename>/progress.md`, in the plan's workspace beside its task briefs, builder reports and review packages. One line per event, written in the same step as the commit it records.

Conversation memory does not survive compaction. The ledger is what does: the commits it names exist in git even when your context no longer remembers creating them, so after compaction trust the ledger and `git log` over your own recollection.

```
# Ledger — plan: <plan path or ticket ref>
Spec: <ref>   Branch: <branch>   Base: <sha>
Pre-flight: <one row per pair of tasks sharing a file or interface, plus one per task's self-consistency; or "no shared interfaces">
Task 1: Ruling: <what was decided> — <why> — <cost if wrong>
Task 1: complete (commits <base7>..<head7>, tests: <command> → <result>)
Task 2: minor (deferred): <one line>
Task 2: fix round 1/5 (<X> addressed, <Y> open — <finding one-liners>; commits <a7>..<b7>)
Task 2: parked — <finding> — Ruling: <why the code stands>
Task 2: complete (commits <base7>..<head7>, review clean)
Task 2: complete (commits <base7>..<head7>, <K> parked)     # after a tripped breaker
Final: fixed <finding> — <test> RED→GREEN, suite <n>/<n>
Final: minor (deferred): <one line>
Final: Ruling: <finding not fixed> — <why the code stands> — <cost if wrong>
```

## Pre-flight

Before Task 1, scan the plan for conflicts and write down what you checked: one row per pair of tasks that share a file or an interface (the two tasks, what one produces against what the other consumes, and what you found), and one row per task for whether its own text agrees with itself (the tests it specifies against the code it specifies, the files it creates against the files it later touches). Rule on each conflict a row surfaces against the spec, record the ruling beside its row, and start Task 1. A plan whose tasks share nothing gets the single line `Pre-flight: no shared interfaces`.

## Lines

- `Ruling:` — a decision about a conflict or a defect in the plan, with what it costs if wrong. Unledgered deviation is a decision made in secret, and a ruling that dies with the workspace was a decision made in secret too.
- `complete (… tests: …)` — inline mode: the command ran, passed, and its result is on the line. Builder mode: `review clean`, or `<K> parked` after a tripped breaker. A failing test run records nothing.
- `minor (deferred)` — a reviewed Minor. It never enters a fix pass and never becomes a ruling; Ruaridh decides whether it is worth a ticket.
- `fix round <R>/5` — one fix brief plus one scoped re-review, with the counts.
- `parked` — an open finding you adjudicated at the cap, with the ruling that says why the code stands. The final review sees both sides.
- `Final: fixed` — a Critical or Important finding fixed in the one fix pass, with its RED→GREEN test and the suite result.

## Review packages

The diff a reviewer reads is a file, not text in the prompt, so the change never enters the coordinator's context. The recipe and the range guards are in `references/review.md`.
