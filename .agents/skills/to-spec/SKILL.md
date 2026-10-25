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
    path: .agents/skills/writing-build-spec/SKILL.md
    sha: a70eb44460392eba7f184b60011df4d2b7855ba0
  - repo: mattpocock
    path: skills/engineering/to-spec/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
---

# to-spec

A builder's contract, not a generic PRD: each consequential decision has a source, a change or disposition, and a way to tell whether it worked. Use existing project spec conventions where they meet this contract.

This skill takes the current conversation, the codebase understanding and the sources gathered around it and produces a spec. Do NOT interview Ruaridh; synthesize what you already know. A decision that is missing and that only he can make becomes an Open item with an owner, never a guessed requirement.

Read `.agents/tracker.md` for the tracker, its labels and its commands; without one, ask him to run `setup-project`. Read `.agents/domain.md` where the repo has one, and use its vocabulary throughout the spec.

## Steps

1. **Reconcile the sources.** Gather current code and policy, tracker items, proof artifacts, meeting notes, prior sessions and his original instructions and annotations. Search the archive of prior sessions through AgentsView (the MCP tools first; see `ruaridh-mode`'s `references/tooling.md`) when it holds relevant decisions. A clear later correction from Ruaridh governs over an earlier statement or meeting note; record what it supersedes. Classify each in-scope finding as decided, superseded, open or out of scope (with a reason). This step ends when every finding has a disposition and every decision cites its source; missing sources are named gaps, not inferred facts.

2. **Separate decided from undecided.** Distinguish working behaviour, merged-but-not-running changes, and work still needed. Take a stance where his established decisions settle it. List each choice actually raised by the evidence that only he can make, with its consequence and owner; leave unexamined dimensions unasserted. This step ends when the builder has no implicit choice to make; a question needing him remains an explicit open item, not a guessed requirement or an invented approval gate.

3. **Find the seams.** Sketch out the seams at which you are going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better: the ideal number is one. Record the testing decisions these imply: what makes a good test here (only external behaviour, not implementation details), which modules will be tested, and the prior art for those tests in the codebase. Name the seams you chose when the draft goes to the gate, so he can check them while reading.

4. **Write the spec.** A plain document a talented builder in the domain could plan from without going back to him: intent and the why; goals, non-goals and anti-goals; constraints; the parts of the how he decided, as he decided them; what is left to the builder. Record purpose and deadline, the hard constraints, the decision register, workstreams with their affected surfaces and expected behaviour, dependencies, rollout and verification gates. For each workstream, give a case and an expected result; if the result is unknown, record the case id and who will decide it, as a harvest rather than a passing test. This step ends when every workstream has a checkable outcome or an owned proof gap, and all dependencies are ordered.

   Write it to `.scratch/specs/<YYYY-MM-DD>-<slug>.md` in the shape in `references/spec-template.md`. In the Decisions section, record the modules that will be built or modified and the interfaces of those that will be modified, technical clarifications from him, architectural decisions, schema changes, API contracts and specific interactions. The rule against file paths and code snippets, and the one exception for a prototype snippet, are in the template.

   **Design, only when UI or UX changes materially.** Fill the Design section and follow `.agents/design-review.md` where the repo has one. Without one, say in the gate message that the Design section is what needs his eye. The design-review gate remains an open item, his call to make.

5. **Reconcile the issue tracker, when present.** Give each relevant open or overdue item a disposition; distinguish merged from promoted and proved running before marking anything done. Link replacements to superseded issues under the project's rules. This step ends when no relevant item is silently omitted; the spec records intended dispositions, not issue mutations.

6. **Builder check.** Dispatch a fresh worker in a Herdr pane (`herdr`, builder role) once the spec exists, with `references/builder-check.md` filled in: the domain, the spec path and the summary path. The worker reads the spec as a talented builder in the domain who cannot talk to its author. When you tell Ruaridh that you are writing the spec up, say that a reviewer will read it first and that you may come back once with a few questions. Do not hand over the document until the check is back. Sort what the builder asks into three piles:

   - **Answered already** by the conversation or the project: put the answer in the document.
   - **Minor**: a sensible builder could settle it without changing what gets built. Settle it yourself and mark it in the document as your call.
   - **His**: only Ruaridh can answer it, and the answer changes what gets built.

   Bring the "his" pile in one message, most important first; ask per the Inbox convention when he is away. Update the document with his answers, then hand it over with a short list of the calls you made so he can check those while reading. That is the only round of questions the check produces. Close the worker with `herdr`. If no fresh pane can be spawned, read the document as that builder yourself and label it a self-check.

7. **Audit the handoff.** For every source decision, find its workstream or its non-build disposition; for every workstream, find its proof and its dependencies. If a policy changes, compare client-facing wording and domain documentation with the rule. Fix the gaps in the file. Share the draft for the gate with its path and status, its decision escalations, its dependency map, its proof gaps and the issues awaiting action.

8. **Gate.** Open the draft with `plannotator annotate <spec path>` in the background, give him the link, and apply every annotation to the file. Repeat until he approves the file as it stands. Name the calls that were yours and the seams you chose so he can check those while reading. When the draft is long or table-heavy, render it with `spec-page` and annotate the HTML file path instead (never its URL); the Markdown stays the file that is edited and approved.

   **Offer `spec-review`.** One line, recommending it when the work is client-facing, hard to reverse or spans many workstreams. If he takes it, run it now; its amendments land in the same file, and publishing resumes from the amended file.

9. **Publish the spec issue** from the final file, per `.agents/tracker.md`: kind `spec`, title `Spec: <title>`, body = the file, idempotency key `spec/<YYYY-MM-DD>-<slug>`. Search first; a re-run finds the existing issue and updates its body instead of creating a second. Record the ref at the top of the spec file.

10. **Hand to `to-tickets`** with the spec ref.

The `.scratch/` file stays where it is; skills never delete it. The tracker issue is the record from here on.

## Red flags

| Thought | Reality |
| --- | --- |
| "I'll ask him a few things to firm it up" | No interview. Missing decisions are Open items with an owner; only the builder check's "his" pile is asked, once. |
| "Acceptance can be worked out in the plan" | Acceptance is decided here and copied into tickets. `to-plan` cites it, never invents it. |
| "The seam choice is the builder's" | Seams are a testing decision made here; name them at the gate so he can check them. |
| "The meeting note says X" | A later correction from him governs it; record what it supersedes. |
| "It's approved, he said it looks good" | Approval is the Plannotator gate on the file as it stands. |
