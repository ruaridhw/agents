# Ledger

`.scratch/plans/<slug>.ledger.md`. One line per event, written in the same step as the commit it records.

```
# Ledger: <plan path or ticket ref>
Spec: <ref>   Branch: <branch>   Base: <sha>
Pre-flight: <task pairs sharing interfaces and what was found, or "no shared interfaces">
Task 1: Ruling: <what was decided> — <why> — <cost if wrong>
Task 1: complete (commits <base7>..<head7>, tests: <command> → <result>)
Final: fixed <finding> — <test> RED→GREEN, suite <n>/<n>
Final: minor (deferred): <one line>
Final: Ruling: <finding not fixed> — <why the code stands> — <cost if wrong>
```

Before Task 1, scan the plan's Interfaces blocks: one pre-flight row per pair of tasks where one consumes what another produces. Rule on any conflict against the spec.
