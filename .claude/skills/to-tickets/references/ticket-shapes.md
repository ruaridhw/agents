# Ticket shapes

## Ticket

Title: imperative, short, in the project's vocabulary.

```
## What
The end-to-end behaviour this ticket makes work, from the user's side. Not a layer-by-layer task list.

## Why now
One or two sentences: what it unblocks or what goes wrong without it.

## Done when
One observable, copied from the spec's Acceptance: the case and its expected result.
Something a reviewer can look at and agree about, not the change you happen to have in mind.

## Blocked by
Only when the tracker has no native blocked-by edges: the refs, or omit.
```

Parent: the spec ref. Labels and priority (1 high, 2 medium, 3 low) from `.agents/tracker.md`. Idempotency key `<spec-ref>/<slug>`. No file paths or code snippets, except a prototype snippet that encodes a decision more precisely than prose, labelled as such.

## Fix ticket

```
## Symptom
What happened, in one paragraph.

## Evidence
Quoted verbatim from the run, log or reproduction, with its id or location. A paraphrase is a second copy that drifts.

## Why it happens
Only if known. "Unclear" is a legitimate answer.

## Fix
The smallest change on one surface that makes every observed case right; list those cases.
```

Label `fix`; idempotency key `fix/<evidence id>/<slug>`. Where two symptoms look alike, say which is which: a value the evidence cannot settle wants a question asked, a wrong choice wants a correction.

## Stopping short

Not a close: label `needs-review` and comment what was attempted and what remains.
