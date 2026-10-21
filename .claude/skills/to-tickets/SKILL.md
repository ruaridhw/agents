---
name: to-tickets
description: Break a published spec into tracer-bullet tickets sized to one session, with Done-when copied from the spec's Acceptance and only real blocked-by edges; gate the wave through triage, then publish it under the spec issue. Also turns a bug report into fix tickets. Use after to-spec, when given a spec ref, or when asked to "ticket this", "break this into tickets" or "file a fix".
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

The wave is the second human gate. Nothing is published until Ruaridh approves the rendered wave, and publishing is idempotent: a re-run finds what exists and creates nothing twice.

Read `.agents/tracker.md` first: it gives the tracker, labels, priorities and the exact create and link commands. Without it, ask him to run `setup-project`.

## Steps

1. **Read the spec issue** (body and comments) and the `.scratch/specs/` file it came from. Read the code where the tickets will land; use the project's vocabulary (`.agents/domain.md`).
2. **Slice tracer bullets.**
   - Each ticket is a narrow but complete path through every layer it touches, verifiable on its own, sized to one fresh session.
   - Prefactoring ("make the change easy, then make the easy change") comes first, as its own ticket.
   - A wide mechanical change whose blast radius breaks everything at once is the exception: expand (add the new form beside the old), migrate in batches sized by blast radius (each blocked by the expand), contract (blocked by every batch).
   - `--blocked-by` only for a real prerequisite: the blocked ticket cannot start or cannot pass without it. Order and preference are not edges.
3. **Write each ticket** in the shape in `references/ticket-shapes.md`. `## Done when` is copied from the spec's Acceptance for that workstream, one observable; never invented here. If a workstream has no Acceptance, stop and add the missing case to the spec issue (comment, and the `.scratch` file) before ticketing it. Open items from the spec go on the tickets they block as `needs-human`, naming the item.
4. **Build the wave file** `.scratch/tickets/<YYYY-MM-DD>-<slug>.wave.json` in `triage`'s wave format, one entry per ticket, carrying also: `labels`, `priority` (1|2|3), `parent` (the spec ref), `blocked_by` (wave keys), `idempotency_key` (`<spec-ref>/<slug>`). Closes, comments and supersessions of existing tickets go in `other_actions`; no-ticket dispositions in `panels`.
5. **Gate through `triage`** (wave input): it renders the page, opens the Plannotator gate and returns his decision and annotations. Apply every annotation to the wave file and, where it changes a decision, to the spec issue too. Re-render material changes. Continue only on approval of this version.
6. **Publish** in dependency order (blockers first) so edges can reference real refs:
   - Search for each idempotency key first; an existing ticket is updated, not duplicated. Write each published ref back into the wave file (`published_ref`).
   - Create with the parent as the spec issue (kata `--parent`; GitHub sub-issue), labels and priority from the file, `ready-for-agent`, blocked-by edges as native links (or a `## Blocked by` section where the tracker has none).
   - Apply `other_actions` exactly as approved.
   - Never close or edit the spec issue's body here; comment the list of created refs on it.
7. **Report** the refs in rank order and the ready frontier (tickets with no open blocker), then hand to `to-plan`, or straight to `implement` when every ticket is small enough to execute directly.

A re-run with the same wave is a no-op: every key is found, nothing is created.

## Fix tickets from a bug report

For a finding with evidence (a failing run, a log, a reproduction), skip the spec: write one ticket per root cause in the fix shape (`references/ticket-shapes.md`), quoting the evidence verbatim. Name every observed case the fix must make right; scope the fix to those, not to a general mechanism one case cannot justify. Without evidence it is a chore ticket, not a fix. Single tickets still go through the triage gate unless Ruaridh asked for the ticket directly.
