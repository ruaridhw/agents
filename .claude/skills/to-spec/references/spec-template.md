# Spec template

```
# <Title>
Spec issue: <ref, once published>   Date: <YYYY-MM-DD>

## Intent
What this is and why now, in one paragraph.

## Goals / Non-goals / Anti-goals
Goals: what success is. Non-goals: what this deliberately does not do.
Anti-goals: what would make it a failure even if it technically works.

## Constraints
Hard limits: deadlines, systems that must not change, compatibility, cost.

## Decisions
| Decision | Source | Consequence |
| --- | --- | --- |
Authority order: Ruaridh's correction > an agreed decision with the other party > other evidence.
Name what each superseded decision was.

## Left to the builder
Choices a sensible builder makes without asking. Calls marked "my call" from the builder check go here too.

## Acceptance
Per workstream: the case and the expected result, observable at the seam named.
Unknown result => case id + owner who decides it.

## Design
Only when UI/UX changes materially. What the design-review gate reviews: screens, flows, states.

## Out of scope
Each with a reason.

## Open items
| Item | Owner | Consequence if unresolved |
These become needs-human on the tickets that depend on them.
```

Write it plainly. No user-story lists, no file paths or code snippets except a prototype snippet that encodes a decision more precisely than prose (a state machine, a schema, a type), trimmed and labelled as from the prototype.
