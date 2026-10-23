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
What belongs here: the modules built or modified and the interfaces of those modified,
technical clarifications from him, architectural decisions, schema changes, API contracts,
specific interactions.

## Left to the builder
Choices a sensible builder makes without asking. Calls marked "my call" from the builder check go here too.

## Acceptance
Per workstream: the case and the expected result, observable at the seam named.
Unknown result => case id + owner who decides it.
A good test here tests external behaviour, not implementation detail:
name the modules tested and the prior art for those tests in the codebase.

## Design
Only when UI/UX changes materially. What the design-review gate reviews: screens, flows, states.

## Out of scope
Each with a reason.

## Open items
| Item | Owner | Consequence if unresolved |
These become needs-human on the tickets that depend on them.

## Further notes
Anything about the feature that no other section holds; never a second home
for a decision or an open item.
```

Write it plainly. No user-story lists, no file paths or code snippets except a prototype snippet that encodes a decision more precisely than prose (a state machine, a schema, a type), trimmed and labelled as from the prototype.
