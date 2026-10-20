# Build spec: cutting the thumbnail service's cost per image

Draft for review, 2026-01-12. A spec only: nothing here is built. Each fact is
marked: **V** verified, **I** inference, **R** a ruling by the owner.

## 1. Purpose

Rendering costs **$0.042 per thumbnail against the $0.010 we charge** (V: `cost.py`,
scenario T0). Two phases close the gap:

- **A. Skip images whose source has not changed.** These are 70% of each nightly batch.
- **B. Move resizing to a cheaper instance class**, once the colour-profile bugs are
  fixed.

## 2. What this builds on

| Fact | Mark |
| --- | --- |
| 70% of last night's 12,000 images had an unchanged source hash. | V: `batch-2026-01-11.json` |
| Unchanged images are never billed. | R, 10 Jan |
| The cheaper class is about 40% slower per image. | I |

## 3. Decision register

### Decided

| Id | Decision | Source |
| --- | --- | --- |
| R1 | Skip on an unchanged source hash *and* an unchanged preset. | Owner, 10 Jan |
| S1 | A missing hash is never evidence of no change (I). | This spec |

### Open

| Id | Question | Owner |
| --- | --- | --- |
| O1 | Does a preset change force a full re-render? | Owner |

## 4. Phase A: skip unchanged images

### 4.1 Goal and cost

| Configuration | $ per image | Spend per week |
| --- | --- | --- |
| T0 today | 0.042 | $3,528 |
| **A: skip unchanged** | **0.013** | **$1,092** |

### 4.2 Steps

1. **Hash the source.** Store `source_sha256` beside each output.
2. **Compare before rendering:**
   - same hash and preset: skip, and log the skip;
   - otherwise: render as today.
3. **Measure** two batches after release:
   1. the skip share;
   2. the cost per image.

## 5. Order

```text
A hash ─▶ A skip ─▶ two measured batches ─▶ B resize class
```
