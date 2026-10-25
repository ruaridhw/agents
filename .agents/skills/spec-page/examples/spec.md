# Skip unchanged images in the thumbnail service
Spec issue: (once published)   Date: 2026-01-12

## Intent

Rendering costs **$0.042 per thumbnail against the $0.010 we charge** (V: `cost.py`,
scenario T0), and 70% of each nightly batch is images whose source has not changed.
Skipping those is the cheapest way to close most of the gap before the larger move
to a cheaper instance class.

## Goals / Non-goals / Anti-goals

- **Goals:** cost per thumbnail at or below $0.015 over two measured batches; no
  thumbnail older than its source.
- **Non-goals:** changing how thumbnails are resized; billing for skipped images.
- **Anti-goals:** a stale thumbnail served after its source or preset changed, even
  once. A cheaper batch that does that has failed.

## Constraints

- The nightly batch must still finish inside its four-hour window.
- The thumbnail API and its response shape do not change.
- Existing outputs carry no hash, so the first run after release renders everything.

## Decisions

| Decision | Source | Consequence |
| --- | --- | --- |
| Skip only when the source hash *and* the preset are unchanged. | R: owner, 2026-01-10 | A preset edit re-renders every image that uses it. |
| A missing hash is never evidence of no change. | This spec | The first batch after release is a full render. |
| The batch worker stores `source_sha256` beside each output; the thumbnail API is untouched. | R: owner, 2026-01-10 | Only the worker and the output store change. |
| Each skip is logged with the image id and the reason. | V: `batch-2026-01-11.json` sizes the log at ~8,400 lines a night | Skips can be audited without a new dashboard. |

## Left to the builder

- The hash function's streaming buffer size.
- Where in the worker the comparison sits, as long as no render starts before it.
- The log line's field order. *My call*: id first, so the log greps cleanly.

## Acceptance

### Skip unchanged images

| Case | Expected result | Seam |
| --- | --- | --- |
| A1 | Unchanged source and preset: no render, one skip log line. | Batch worker, run against a fixture store |
| A2 | Changed source: rendered as today, new hash stored. | Batch worker |
| A3 | Missing hash: rendered, hash stored. | Batch worker |

### Measure the saving

| Case | Expected result | Seam |
| --- | --- | --- |
| M1 | Two batches after release average at or below $0.015 per image. | The nightly cost report |
| M2 | Skip share on a batch with a preset change. Result unknown: case kept as a harvest. | Owner decides the threshold |

## Design

No screens change. The worker's decision for each image:

```text
read source ─▶ hash ─▶ stored hash and preset match? ─┬─ yes ─▶ skip, log
                                                       └─ no  ─▶ render, store hash
```

## Out of scope

- **The cheaper instance class.** It waits on two colour-profile fixes and gets its own spec.
- **Backfilling hashes for old outputs.** The first full batch does it for free.

## Open items

| Item | Owner | Consequence if unresolved |
| --- | --- | --- |
| O1 Does a preset change force a full re-render of every image that uses it? | Owner | A3 and M2 cannot be signed off. |
| O2 What skip share counts as healthy? | Owner | M2 stays a harvest with no pass mark. |

## Further notes

> The batch of 2026-01-11 had 12,000 images; 8,400 had an unchanged source hash.
