# Ticket shapes

## Ticket

Title: imperative, short, in the project's vocabulary.

```
## What

The end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

## Why now

One or two sentences: what it unblocks, or what goes wrong without it.

## Done when

The case and the result it expects, taken from that workstream's Acceptance in the spec. Keep it to a single thing a reviewer can verify: the behaviour the system should show, described without prescribing the implementation.

## Blocked by

A reference to each blocking ticket, or "None (can start immediately)". Omit this section when the blockers were set as native edges.
```

`## Parent` is a reference to the parent issue on the tracker: the spec issue, or the existing issue the work came from, when there is one. It is set on the tracker as containment (`--parent` on kata, a sub-issue on GitHub) rather than written into the body; omit it when the ticket has no parent.

Done-when describes an outcome, not a design. "The confirmation email names the order reference" is a fact anybody can confirm by looking; "thread an order-reference field through the mailer" is merely one way of producing it. Write the second into the ticket and the cheaper route that would have shown the same thing is closed off — state the outcome and let the implementer find the way.

Priority on the profile's scale (1 high, 2 medium, 3 low) and the labels come from `.agents/tracker.md`. The idempotency key `<spec-ref>/<slug>` travels the way the profile says: a field on the create, or a trailing HTML comment in the body.

## Fix ticket

```
## Symptom

What happened, in a paragraph.

## Evidence

The observation itself, copied word for word from the run, the log, the screenshot or the reproduction, and where it came from (an id, a file, a timestamp). Summarised rather than copied, it turns into a second version that can only lose fidelity.

## Why it happens

Fill this in only if you know. Saying it is unclear is allowed here, and beats asserting a cause you have not established.

## Fix

The one surface to change, and the list of cases it has to put right.
```

Label the tracker's fix kind; idempotency key `fix/<evidence id>/<slug>`. Whether two lookalike symptoms are one ticket or two, and which is which, was settled in `SKILL.md` before this shape was reached; the ticket states which of them it covers.

## Stopping short

Leaving work unfinished is not the same as closing it. The ticket gets `needs-review` and a comment carrying where you got to and what is left, so whoever picks it up reads that instead of reconstructing it from the diff. When a real case has to prove the behaviour before the implementation ticket can close, open a related ticket first (`Verify <observable> live`), not a child one. The states, their commands and the proof each requires live in `.agents/tracker.md`.
