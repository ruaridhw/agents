---
name: to-tickets
description: Break a published spec, a plan or the current conversation into tracer-bullet tickets sized to one session, each with only its real blocked-by edges and its Done-when copied from the spec's Acceptance; gate the wave through triage, then publish it under the spec issue. Also turns an evidenced bug into fix tickets. Use after to-spec, when given a spec ref, or when asked to "ticket this", "break this into tickets" or "file a fix".
upstream:
  - repo: mattpocock
    path: skills/engineering/to-tickets/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
  - repo: kit
    path: template/.agents/skills/kit/new-ticket/SKILL.md
    sha: 1d552609f50102184079aa622beb727e38b02341
  - repo: kit
    path: template/.agents/skills/kit/new-fix/SKILL.md
    sha: 1d552609f50102184079aa622beb727e38b02341
---

# to-tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

The wave is the second human gate. Nothing is published until Ruaridh approves the rendered wave, and publishing is idempotent: a re-run of the same wave finds what exists and creates nothing twice.

Read `.agents/tracker.md` first. It gives the tracker, its label vocabulary, the priorities and the exact create, link and sub-issue commands. Without it, ask him to run `setup-project`.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

The spec behind the work is the authority for what the tickets say, and its Acceptance is where their `Done when` comes from.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary (`.agents/domain.md`), and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately. A blocked-by edge is only for a real prerequisite: the blocked ticket cannot start, or cannot pass, without it. Order and preference are not edges.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Write each ticket

Give each ticket the shape in `references/ticket-shapes.md`: what it delivers, its blocking edges, and its labels.

Avoid specific file paths or code snippets in a ticket: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (a state machine, a reducer, a schema, a type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

`## Done when` has exactly one source: the Acceptance entry for that workstream in the spec. Carry over the case and the result it expects, as a single observable; nothing about a ticket's Done-when originates in this skill. Where a workstream has no Acceptance entry, stop and send the missing case back to the spec issue (a comment, plus the `.scratch/specs/` file) before ticketing that workstream.

Where the spec left a question for Ruaridh to settle, the tickets it holds up carry `needs-human`, naming the open item and the person who decides it.

Priority is the tracker profile's scale — 1 high, 2 medium, 3 low — and labels come from `.agents/tracker.md` too. Each ticket gets an idempotency key of `<spec-ref>/<slug>`, decided once and then fixed for the ticket's life; look for that key in the tracker before you create anything.

### 5. Build the wave file

Write the wave to `.scratch/tickets/<YYYY-MM-DD>-<slug>.wave.json` in the input contract `triage` renders (the `references/input.md` beside its `SKILL.md`): one entry per ticket, with every ticket's exact body, its spec section and its source quotes. Each entry also carries the publisher fields — `labels`, `priority`, `parent` (the spec ref), `blocked_by` (wave keys) and `idempotency_key` — which ride along unrendered.

Closes, comments and supersessions of existing tickets go in `other_actions`; dispositions that create no ticket go in `panels`. Every proposed action must be in the file, so that an absence is visible to him rather than silent.

### 6. Gate the wave through `triage`

Hand the wave file to `triage` as its wave input. It renders the self-contained page, opens the Plannotator gate and returns his decision with annotations. The tickets, their blocked-by edges and what each delivers are what he reads there; there is no separate in-chat round of questions to answer first.

Apply every annotation to the wave file and, where it changes a decision, to the spec issue too. Re-render material changes and gate again. Continue only on approval of this version; a timeout or dismissal leaves the wave unpublished. When he is away, ask per the Inbox convention.

### 7. Publish in dependency order

Publish the approved tickets, blockers first, so that each ticket's blocking edges can reference real identifiers.

- Search for each idempotency key first; an existing ticket is updated, not duplicated. Write each published ref back into the wave file as `published_ref`.
- Create each ticket with the parent set to the spec issue (`--parent` on kata, a sub-issue on GitHub), labels and priority from the file, and the `ready-for-agent` triage label: the tickets are agent-grabbable by construction.
- Use the tracker's native blocking relationship where it has one; otherwise set each ticket's `## Blocked by` to the blocking issues.
- Apply `other_actions` exactly as approved.

Do NOT close or modify any parent issue. Never edit the spec issue's body here: comment the list of created refs on it.

### 8. Report and hand off

Report the refs in rank order and the ready frontier — any ticket whose blockers are all done, which for a purely linear chain means top to bottom — then hand to `to-plan`, or straight to `implement` when every ticket is small enough to execute directly.

A re-run with the same wave is a no-op: every key is found, nothing is created. A ticket created on its own takes the same steps, with the parent left off and, for a fix, the evidence as its source.

## Fix tickets from a bug report

Evidence is the test of whether an entry is a fix at all. Where it exists — a failing run, a log, a screenshot, a reproduction — the spec can be skipped: write the ticket straight into the fix shape in `references/ticket-shapes.md`, one per root cause, with the observation quoted word for word. With the cause still unknown, run it through `debug` first; either way the ticket has to name the surface it changes.

Where it does not exist, the entry is a chore. A tracker where any entry may call itself a fix leaves that label worthless as a filter, so ask for the observation instead of building on somebody's recollection of what they think they saw. Somebody else having to act on it makes it the tracker profile's blocker kind (`client-blocker` on kata), never a fix.

Before picking where to change anything, list the cases the finding actually shows. A mechanism broad enough to cover everything needs at least two cases on record: with one, the grounds are there for correcting that one and nothing else — not a shared rule, not a lookup table, not a field added for situations nobody has met yet. Widened like that, a bug report turns into a rewrite argued from a single example. Too narrow is the opposite failure, and the ticket pays for it later on, which is why the case list is what a reviewer holds the change against. Land on the one place that can put every recorded case right; if it takes several places, that is a refactor, and the ticket should say so.

Symptoms that look the same still need separating. A field nobody's evidence can pin down and a field that took a wrong branch show up identically in a transcript and are not the same problem: one calls for somebody to be asked, the other for a value to be corrected. Write them as one ticket and you will end up building a general rule where a single correction was enough.

Describe the shape you want in its own terms. Pointing at another line — "same as above", "the way that rule does it" — delegates the meaning to that line: whoever comes next will copy its surface form and not the reasoning under it, spreading the mistake if it had one, and leaving no record of what mattered if it did not.

Single tickets still go through the gate unless Ruaridh asked for the ticket directly.
