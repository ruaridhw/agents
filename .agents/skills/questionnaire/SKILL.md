---
name: questionnaire
description: "Turn a decision the agent cannot answer alone into a questionnaire delivered as Plannotator Inbox question blocks: ask only about the send, then write the questions that pull the missing knowledge out of the person who has it. Use when a decision needs information from Ruaridh or a third party, when an async hand-off needs a fillable set of questions, or when asked to make a questionnaire."
upstream:
  - repo: mattpocock
    path: skills/productivity/to-questionnaire/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
---

# questionnaire

Turn something the agent cannot answer alone into a **questionnaire**: a set of questions for the one person who holds the knowledge. They answer async, or in a meeting, and the agent gets back a decision it could not make.

Two deliveries, and the first is the default:

- **Plannotator Inbox question blocks**, when Ruaridh is the one answering. Each question is a `:::question` block in one Inbox message, on one thread, and the answers come back in the session by themselves.
- **A Markdown document**, when the recipient is a third party who will not open Plannotator. `references/paper-questionnaire.md` is the shape, and the questions still get written here.

**Grill the send, not the subject.** Interview Ruaridh only about the *send*, which he can always answer: who it goes to, and what he needs back. The questions in the questionnaire then target the **gap** between what the recipient knows and what he needs.

1. **Who is it going to?** Ask, in one exchange, the recipient's role, expertise and relationship to the sender. This fixes the tone and how much context the questionnaire must carry. **Done when** you know who the recipient is and what they know that he does not. When the recipient is Ruaridh, this step is one line: he is the one answering, and the questions are aimed at what he knows and the agent does not.
2. **What do you need back?** Ask, in one exchange, the specific decisions or facts he cannot resolve alone and needs from this person. **Done when** you have a concrete list of what he must be able to do or decide afterwards.
3. **Write the questionnaire.** Draft questions aimed at the gap from steps 1 and 2. **Done when** every item he named in step 2 is covered by a question, and each question is one idea.

## Writing it for the Inbox

One Inbox message, one thread (`<repo> · <ticket or spec ref>`, per the Inbox convention in `ruaridh-mode` and its `references/tooling.md`). Look for an existing thread with that name and post into it rather than opening a second one.

- **One `:::question` block per question**, `:::question-multi` when any number of choices apply, `:::question-text` for free text. The first line is the question; the lines below it are the context.
- **Never a bare question.** One to three short sentences say what the choice affects, what the agent already knows or tried, and why it recommends what it does. The reader switches in cold and cannot see what the agent sees.
- **Choices carry their consequence**: `- [ ] label — why`. Three or so, the real options rather than a spread of plausible ones.
- **`Recommended:` names one option**, worded so accepting it is one click. If the recommendation is not a choice, it shows as a suggested answer, which is a weaker outcome than a real choice.
- **About eight questions a round at most.** More than that is a spec, and it belongs in `to-spec`.
- **`Stopped: <why>`** only when the work genuinely cannot continue without the answer; **`Holds up: <work>; <work>`** when the work goes on and the named work waits. A new question that supersedes an open one names it, so the old one stops holding the thread.
- **Blank lines between the parts**, so the block also reads well on GitHub.
- **`- [x]` marks a settled choice.** On a resubmit, check the chosen answer or drop the block and state the decision in prose.
- A visual question carries a screenshot (`![alt](path)`) or a link that shows it better (a mock, a plan), and the file is attached too.

Questions come back under "Answers to your questions", each as `### Q2. <question> (line N)` with `Answer: <choice>` (marked `(your recommendation)` when the recommendation was taken), `Other: …`, free text in a quote, or `Skipped`, plus any `Note:`. Unanswered questions are listed under "Unanswered". Read every one before acting: a skip is an answer, and an "Other" outranks the recommendation.

## Writing the questions

The question craft is the same for both deliveries:

- **One idea per question.** A compound question gets one half answered.
- **Most important first.** Async means one pass.
- **Ask for what the recipient knows and the agent cannot derive.** A question the codebase, the tracker or the repository would answer is the agent's job, and asking it spends the reader's goodwill.
- **No rhetorical questions, and no questions whose answer is a preference the agent could default.** A default taken silently is worse than a choice offered; a default offered as a question is noise.
- **Ask at the level the recipient thinks at.** A product decision is not a question about a function signature.
- **A "why this matters" line only where the question could be misread** or invite a throwaway answer.
- **A closing catch-all**, as the last block: "Anything we did not ask that we should know?" That is the one question that regularly returns the most.
- Group by theme with more than a handful of questions: several blocks read in order on one thread, or a paper questionnaire with `##` headings when it goes out as a document.

## What changed from the upstream format

The upstream `to-questionnaire` writes a Markdown document, `to-questionnaire-<slug>.md`, handed to one person to fill in. Here:

- The **delivery** is an Inbox message of question blocks, so the answers come back into the session and the thread keeps the history; the Markdown document survives only for a third party who will not open Plannotator (`references/paper-questionnaire.md`).
- The document's **header** (title, purpose, from, to, how the answers are used) becomes the message's opening lines and the thread's name.
- The document's **"How to answer"** section disappears: the Inbox carries its own affordances (Other, a note, Skip, accept the recommendation), so explaining them again would be a second interface.
- Each question's **answer stub** becomes the block's choice list, with the recommendation marked rather than left implicit.
- The **closing catch-all** becomes a `:::question-text` block, so it is answerable in the same pass rather than in a separate document.
- The **file is not written** when Ruaridh is the recipient. Nothing lands in the working directory, so nothing has to be cleaned up.
- **About eight questions a round** is added: the Inbox's own guidance, and what keeps a questionnaire from becoming a spec.

The upstream's interview (grill the send, the two exchanges, the done criteria), its one-idea-per-question rule, its ordering and its "why this matters" discipline are kept unchanged.

## Rules

- A worker never writes to the Inbox: it asks its coordinator, which sends the questionnaire. The Inbox belongs to the coordinator's session.
- Never write a question the agent could answer itself. Research first, then ask about the gap.
- Every question that reaches the person is one they can answer without opening anything else.
- Read every answer, including the skips and the "Other"s, and record the decisions they settle where they belong: the spec's Decisions table, the glossary (`domain`), or an ADR.
- A regression round for answers already settled is not a questionnaire. A decision that contradicts an earlier answer names the earlier one.
