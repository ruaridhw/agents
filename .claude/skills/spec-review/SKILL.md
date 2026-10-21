---
name: spec-review
description: Adversarial review of a draft spec by an independent reviewer in a sibling Herdr pane, answered by the author from the project's decision history, before the spec issue is created. Use when to-spec offers it, or when asked to "review the spec", "challenge this spec" or "red-team the spec".
upstream:
  - repo: self
    path: .claude/skills/adversarial-spec-review/SKILL.md
    sha: 51fe9394d52c50b26c417273b7b027e81abf1dff
---

# spec-review

A reviewer with fresh context challenges the draft; you, the author, answer from what was decided. The output is a ledger of material gaps and their dispositions, not a quota of questions. You alone edit the spec. Runs between the `to-spec` gate and publishing the spec issue.

## Steps

1. **Set up the review file** beside the spec: `.scratch/specs/<date>-<slug>.review.md`. It is the reviewer's only write destination.
2. **Spawn the reviewer** in a sibling pane (`herdr`), using the spec-reviewer role from `~/.config/agents/models.toml`, with `references/reviewer-brief.md` filled in. Give it pointers, not copies: the spec path, the repo, tracker refs, meeting notes and prior-session refs (AgentsView), Ruaridh's original prompts and annotations. State the authority order: his decisions and corrections, then agreed decisions with the other party, then other evidence.
   - Access is granted by class: it may run anything that reads (files, tests, dry runs, VCS and tracker reads, AgentsView); it mutates nothing outside the review file, so no repo or tracker writes, no builds, formatters or hooks that rewrite files. Name the forbidden effects; never hand it a command allowlist.
   - Where a system cannot be read safely, export the evidence for it or say in the ledger that it was not inspected.
   - If no independent reviewer can be spawned, say so; a self-review is labelled as such.
3. **Wait for the first pass.** Each question in the review file gives the gap, its consequence, the source and a proposed resolution; instances of one defect are grouped.
4. **Answer every question in the review file**, one of:
   - **Amend**: a source-backed change to the spec file, with its location.
   - **Reject**: evidence that the spec already holds, with the source.
   - **Escalate**: the choice, its consequence and owner, added to the spec's Open items. Escalations go to Ruaridh in one message (Inbox question blocks if he is away).
5. **Second pass.** Prompt the reviewer (`herdr agent prompt`) to read the answers and the revised spec, push back on unsupported answers and look again where gaps remain. Repeat until every question has a disposition the reviewer has inspected. No fixed round limit.
6. **Close out.** The reviewer ends the file with a ledger: gaps resolved with spec locations, decisions for Ruaridh, and evidence it could not inspect. Close its pane. Reconcile the ledger with the spec; show him the escalations.

A complete review means a fresh pass found no identified material gap across the evidence it could reach. A time or access limit produces an **incomplete** review with its open challenges listed, never a clean verdict.

Then return to `to-spec` step 9: the spec issue is created from the amended file.

## What qualifies as a question

A specific defect that could change a build choice, an outcome, an acceptance judgment or a safe rollout. Not wording, not style, not questions the spec already answers. Expect some of the reviewer's points to re-ask settled decisions: reject those with the source, briefly.
