# Granola meeting notes

## What this source contains

- Recorded and summarised meetings: product decisions, design reviews, incident reviews, customer calls
- Speaker-attributed notes and transcripts, which is where a decision is often stated in someone's own words
- Follow-ups and action items that became tickets

Granola covers the deliberation that never reached a document: the meeting where one approach was ruled out and nobody wrote a spec afterwards. It is usually a second-order source: stronger than inference, weaker than a spec or a pull request description.

## How to search it

Use the Granola MCP. Probe the tool schemas first; they are newer than the older docs suggest.

1. **Search by the decision's words.** The feature name, the symbol under investigation, the person who likely decided it, and any date range around the ship date. Try the phrasing a speaker would use, not the phrasing the code uses.
2. **Read the whole note.** Rationale is usually far from the summary: somewhere in the discussion, stated once.
3. **Follow into Notion.** Granola notes are often synced into Notion; if a note is thin, search Notion for the same meeting date and title.
4. **Anchor on dates.** A meeting the week before the pull request merged is strong circumstantial evidence about what motivated it.

## What good evidence looks like here

- A named person saying what was decided and why, quoted verbatim with the meeting title and date
- An action item that matches the code's shape
- A ruled-out alternative, which is often the most useful part of the answer

## Common pitfalls

- **Summary prose is generated.** Treat a summary line as a lead; quote the transcript where the claim is specific.
- **Meetings restate rather than decide.** A weekly update repeating a decision is not where the decision was made; keep searching for the earlier meeting.
- **No note is a gap, not a null.** Recurring meetings often have no note at all.

## What to return

For each relevant note:
- Meeting title and date
- The speakers whose words you quote
- The motivation or decision, verbatim, with the passage's location in the note
- Whether the note is a transcript or a generated summary
