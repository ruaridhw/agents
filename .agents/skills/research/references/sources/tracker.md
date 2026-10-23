# The tracker (kata or GitHub Issues)

## What this source contains

- Tickets describing features, bugs and their motivation
- Specs and plans attached to tickets, often as a parent issue
- Parent/child relationships (a spec issue, its tickets, a map and its decision tickets)
- Comments on tickets (clarifications, scope changes, "why we're doing this" rationale)
- Labels and kinds that signal the type of motivation (`needs-triage`, `incident`, a chore kind)
- State history that explains scope changes
- Linked pull requests, when the tracker links them

The tracker is where the product and business context usually lives: the "we're doing this because the customer asked" or "this is for the compliance deadline" layer. Which tracker a repo uses, its commands, labels, kinds and states all come from `.agents/tracker.md`; the two profiles are `conventions/tracker-kata.md` and `conventions/tracker-github.md`.

## How to search it

Read `.agents/tracker.md` first; it names the tracker, the project and the exact read commands. Then:

1. **Start with linked tickets.** If the seed commits or pull requests reference ticket ids, fetch those first. Read the whole ticket, comments included.
2. **Search by keyword.** Use the profile's search command for the feature name, key symbol or business term. Try several phrasings.
3. **Walk the tree.** If you land on a ticket, fetch its parent. The tickets are tactical; the spec issue or the map often carries the why.
4. **Read the attached spec.** A spec issue, or a `.scratch/specs/` file it points at, is where the decision and its reasons are recorded. Use `domain`'s vocabulary when naming what you find.
5. **Check kinds, labels and states.** Kinds and labels hint at the category of motivation; a `blocked-by` edge or a milestone ties work to a deadline, which often reveals the motive.

## What good evidence looks like here

- A ticket stating the business problem, verbatim: the forcing function, not a restatement of the code
- A comment recording a decision: "we went with B because A would have meant touching the billing service"
- A spec issue with a Decisions table and its sources
- A parent spec titled like an initiative
- Labels or kinds like `incident`, `perf`, `compliance`

## Common pitfalls

- **Scope drift.** The ticket a pull request references may have been closed and reopened with a different scope. Read the whole history.
- **Mechanical templates.** Some repos require a "Why" section and fill it with boilerplate. Generic text ("improve user experience") is probably not a real answer.
- **Stale tickets.** Old tickets often reflect a version of the plan that changed. Check dates against the code's ship date.
- **Closed-as-duplicate chains.** Follow the duplicate-of relationships back to the canonical ticket.
- **Restricted tickets.** If a ticket cannot be read, record it as a gap rather than guessing.

## What to return

For each relevant ticket:
- Ticket reference and title
- The problem and motivation quoted from the description or comments, not paraphrased: the synthesizer needs the exact text to cite
- Labels, kind, parent
- Author, created date, closed date
- Link or command that produced it
