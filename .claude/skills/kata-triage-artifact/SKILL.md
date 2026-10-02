---
name: kata-triage-artifact
description: >-
  Use when a batch of proposed Kata tickets awaits operator review before
  publication, or when Plannotator annotations require another review of that batch.
---

# Review a proposed ticket wave

Keep the ticket data local until the operator approves the rendered wave.
This skill prepares review; publishing belongs to the calling workflow.

## Steps

1.  Assemble one JSON file from the proposed publishing data. Preserve each exact
    ticket body, its implementing spec section, source quotes and operator rulings.
    Include closes/comments under `other_actions`, and deploy gates, rollout and
    no-ticket items under `panels`. Read [input.md](references/input.md) when constructing the
    JSON; [examples/triage.json](examples/triage.json) is a neutral worked input.
    Done when every proposed action is accounted for and each ticket's context
    is present, or its absent evidence is explicitly visible.
2.  Resolve this skill's directory as `<skill-dir>` and render:

        python3 <skill-dir>/scripts/render_triage.py <draft.json> <review.html>

    Compare every sheet against the publishing data and spec; check rank order,
    source quotes, list nesting and all closing panels. The page has no collapsed
    content or network dependencies. Use the same data for review and publication,
    rather than rewriting the ticket body after approval.
    Done when the renderer exits zero and the page faithfully shows the whole wave.

3.  Open a background approval gate using [serving.md](references/serving.md). It covers
    Plannotator prerequisites, the port printed in its log, tailnet access and the
    decision file. Give the operator the review URL and wait for their submission.
    Done when that session's decision JSON exists; a timeout or dismissed session
    leaves the wave unpublished.
4.  Read `decision` and all `feedback`, including notes on approval. Feedback is
    Markdown, with `Feedback on: <quoted span>` entries. Match each span to its
    ticket key/spec/source; ask the operator when a repeated span is ambiguous.
    Apply rulings to the canonical spec and proposed publishing data together,
    retaining source quotes verbatim and recording interpretations in `rulings`.
    Regenerate and re-review material changes with a fresh result-file path.
    Done when every annotation has a recorded disposition, the specs and data
    agree, and the operator has approved this version. Hand that exact data and
    decision record back to the publishing workflow; this renderer writes no Kata issues.

When changing the renderer or visual design, read
[development.md](references/development.md) for formatting, lint and smoke checks.
