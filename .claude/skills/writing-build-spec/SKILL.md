---
name: writing-build-spec
description: Use when writing a build-ready spec from a decision-heavy review, meeting, annotated draft or investigation.
---

# Writing a build spec

A builder's contract, not a generic PRD: each consequential decision has a source, a change or disposition, and a way to tell whether it worked. Use existing project spec conventions where they meet this contract.

1. **Reconcile sources.** Gather current code/policy, tracker items, proof artifacts, meeting notes and the user's original instructions and annotations. Use `agentsview-finding-history` when the archive holds relevant decisions. A clear later user correction governs over an earlier statement or meeting note; record what it supersedes. Classify each in-scope finding as decided, superseded, open or out of scope (with a reason). This step ends when every finding has a disposition and every decision cites its source; missing sources are named gaps, not inferred facts.
2. **Separate decided from undecided.** Distinguish working behavior, merged-but-not-running changes, and work still needed. Take a stance where the user's established decisions settle it. List each choice actually raised by the evidence that only the user can make, with its consequence and owner; leave unexamined dimensions unasserted. This step ends when the builder has no implicit choice to make; a question needing the user remains an explicit open item, not a guessed requirement or invented approval gate.
3. **Specify the build.** Record purpose/deadline, hard constraints, decision register, workstreams with affected surfaces and expected behavior, dependencies, rollout and verification gates. For each workstream, give a case and expected result; if the result is unknown, record the case ID and who will decide it, as a harvest rather than a passing test. This step ends when every workstream has a checkable outcome or an owned proof gap, and all dependencies are ordered.
4. **Reconcile the issue tracker, when present.** Give each relevant open or overdue item a disposition; distinguish merged from promoted and proved running before marking done. Link replacements to superseded issues under project rules. This step ends when no relevant item is silently omitted; the spec records intended dispositions, not issue mutations.
5. **Audit the handoff.** For every source decision find its workstream or non-build disposition; for every workstream find its proof and its dependencies. If policy changes, compare client-facing wording and domain documentation with the rule. Share the draft for review with its path/status, decision escalations, dependency map, proof gaps and issues awaiting action. `adversarial-spec-review` handles an independent challenge pass when requested.
