---
name: to-spec
description: Turn a grilled idea, a decision-heavy meeting, an annotated draft or an investigation into a build-ready spec, gate it with Ruaridh in Plannotator, then publish it as the spec issue. No interview. Use after grill sizes something as a project, or when asked to "write the spec" or "turn this into a spec".
upstream:
  - repo: superpowers
    path: skills/brainstorming/SKILL.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: superpowers
    path: skills/brainstorming/builder-check-prompt.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: self
    path: .claude/skills/writing-build-spec/SKILL.md
    sha: a70eb44460392eba7f184b60011df4d2b7855ba0
  - repo: mattpocock
    path: skills/engineering/to-spec/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
---

# to-spec

A builder's contract: every consequential decision has a source and a consequence, every workstream has a checkable outcome, and nothing is left for the builder to guess that only Ruaridh could decide. No interview: synthesise what was already said and found. If a decision is missing and only he can make it, it becomes an Open item, not a guess.

## Steps

1. **Reconcile the sources.** Gather the conversation, current code and docs, tracker items, meeting notes, prior sessions (AgentsView) and his annotations. A later correction from Ruaridh governs an earlier statement; record what it supersedes. Give every in-scope finding a disposition: decided, superseded, open, out of scope (with a reason). Missing sources are named gaps, not inferred facts. Read `.agents/domain.md` and use the project's vocabulary.
2. **Find the seams.** Decide where the work will be proved: the highest existing seam that can observe the behaviour, a new one only when none can, as few as possible. This feeds Acceptance.
3. **Write the spec** to `.scratch/specs/<YYYY-MM-DD>-<slug>.md` in the shape in `references/spec-template.md`. Distinguish working behaviour, merged-but-not-proved changes and work still needed. Acceptance is decided here, per workstream, as a case and its expected result; when the result is unknown, record the case id and who decides it. If related tracker items are open, give each an intended disposition in the spec (do not mutate them yet).
4. **Design**, only when UI or UX changes materially: fill the Design section and follow `.agents/design-review.md` if the repo has one. Without it, say in the gate message that the Design section is what needs his eye.
5. **Builder check.** Spawn a fresh read-only worker (`herdr`, builder role, `--lean`) with `references/builder-check.md` and the spec path. Sort what it asks into three piles:
   - **Answered**: the conversation or the project already settles it. Put the answer in the spec.
   - **My call**: a sensible builder could settle it without changing what gets built. Decide it and mark it in the spec as your call.
   - **His**: only Ruaridh can answer it and the answer changes what gets built.
   Bring the "his" pile in one message, most important first (Inbox question blocks if he is away). That is the only round of questions the check produces. Close the worker.
6. **Audit before the gate.** Every source decision lands in a workstream or a non-build disposition; every workstream has Acceptance and its dependencies. Fix gaps in the file.
7. **Gate.** Run `plannotator annotate <spec path>` in the background, give him the link, and apply every annotation to the file. Repeat until he approves. Tell him which calls were yours so he can check those while reading.
8. **Offer `spec-review`** in one line, recommending it when the work is client-facing, hard to reverse or spans many workstreams. If he takes it, run it now; its amendments go into the same file.
9. **Publish the spec issue** from the final file, per `.agents/tracker.md`: kind `spec`, title `Spec: <title>`, body = the file, idempotency key `spec/<YYYY-MM-DD>-<slug>`. Search first; a re-run finds the existing issue and updates its body instead of creating a second. Record the ref at the top of the spec file.
10. **Hand to `to-tickets`** with the spec ref.

The `.scratch/` file stays where it is; skills never delete it. The tracker issue is the record from here on.

## Red flags

| Thought | Reality |
| --- | --- |
| "I'll ask him a few things to firm it up" | No interview. Missing decisions are Open items with an owner; only the builder check's "his" pile is asked. |
| "Acceptance can be worked out in the plan" | Acceptance is decided here and copied into tickets. `to-plan` cites it, never invents it. |
| "The meeting note says X" | A later correction from him overrides it; record what was superseded. |
| "It's approved, he said it looks good" | Approval is the Plannotator gate on the file as it stands. |
