---
name: technical-writing
description: "The writing standard for client-facing documentation: Diátaxis structure, Google developer style sentences, Simplified Technical English instructions, Global English syntax, an unslop pass, and the copy-review pass last. Use when writing or reviewing documentation, a readme, a runbook, a guide, an RFC or a client-facing report, when a doc needs its structure or its sentences fixed, when asked to tighten this copy, de-AI this or make it sound human, and on any prose longer than about 100 characters that this skill writes or edits."
upstream:
  - repo: pstack
    path: pstack/skills/technical-writing/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/unslop/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
---

# technical-writing

Write so a tired engineer understands on the first read. Apply all four layers.

This is for **client-facing documentation**: style and structure only. It does not decide what the documentation says, and it does not design the product. A doc that is accurate and badly structured fails its reader exactly as a wrong one does.

Four layers, applied in order, then two passes at the end:

1. **Structure**: Diátaxis. One document, one mode.
2. **Sentences**: Google developer style. Write to the reader.
3. **Load**: Simplified Technical English, leaned on. One thought at a time.
4. **Ambiguity**: Global English. Leave no sentence open to two readings.
5. **Slop**: the unslop pass.
6. **Copy review**: the copy-review pass, last of all.

`references/style-foundations.md` goes deeper on the four layers: what each mode of documentation is for, and the reasoning behind the sentence, instruction and syntax rules. It is written for this skill, not taken from a feed, and `SKILL.md` always wins where they differ.

`references/copy-review.md` is the last pass, with its scan list in `references/copy-review-word-list.md`.

Three rules sit above the layers:

- **Cut every word that does no work.** If the sentence survives without a word, the word goes. "In order to" is "to". "It is important to note that" is nothing.
- **Use the short, everyday word.** "Use", not "utilize". "Help", not "facilitate". "Do", not "perform". A long word has to buy its length with precision.
- **When a rule makes a sentence worse, fix the sentence another way or leave it alone.** A sentence that follows every rule and sounds like a machine wrote it has failed.

The codebase is the word list. Write the real symbol, file, flag or command name, not a synonym or a description of it.

Don't invent jargon. Use the words a developer would say out loud: "move", "delete", "a budget that only decreases", not "evacuate", "ratchet", or "endgame". A named pattern is fine when the doc says what it means the first time. Propose a new offender and its replacement as an addition to the unslop pass in your reply, with the diff. Don't edit the reference yourself.

## Vary the rhythm

A doc can obey every layer and still read machine-written: every sentence clipped short, no view anywhere, nothing specific.

- Mix sentence lengths on purpose. Short sentences land a point. Longer ones carry a fact with its condition or consequence.
- One thought per sentence does not mean one length per sentence. Split the sentence that carries two thoughts. Keep the long sentence that carries one.
- Have a view where the mode allows it. Explanation weighs trade-offs, so say what you make of them instead of listing pros and cons. Reference stays dry.
- Be specific over sterile. Not "schema changes can cause issues" but "a column rename fails the build".

## Pick the mode first (Diátaxis)

One document, one mode. Two questions pick it: does the content inform action (doing) or understanding (thinking), and does it serve learning or work?

- Action + learning: **tutorial**.
- Action + work: **how-to**.
- Understanding + work: **reference**.
- Understanding + learning: **explanation**.

Use the compass on a whole document or on one sentence.

**Tutorial: learning by doing.** The learner's success is your job, not theirs. Open by saying what the learner will build, not what they will "learn". Every step produces a visible result, early and often. Tell them what they should see: the expected output, the prompt change, the log line. Cut explanation to one clause and a link. Stay concrete. Write as "we", in commands: "First, do x. Now, do y."

**How-to: steps to a goal.** Solve a problem a person has, not an operation the machine can perform. Assume competence and skip teaching. Action only: no digressions, no background, no completeness for its own sake. Link those instead. Allow forks and judgment: "If you want x, do y." Name the guide by the task: "How to calibrate the radar array", not "Radar array calibration".

**Reference: facts for lookup.** Only describe. No instruction, no persuasion, no opinion. Be dry, complete, and sure. State facts, options, limits and errors with no hedging. Mirror the structure of the thing described, so code and docs can be navigated together. Put material where readers expect it. Generate from code where possible.

**Explanation: understanding and why.** One bounded topic, readable away from the product. Each title should tolerate an implicit "About..." in front. Anchor on a real why question. Give context: design decisions, history, constraints, alternatives. Opinion is allowed here and nowhere else.

Don't mix modes: no reference tables inside a tutorial, no tutorial hand-holding inside reference, no arguing inside a how-to. Split and link instead.

## Write sentences to the reader (Google developer style)

- Talk to the reader as "you", in the present tense. "Will" only for things that genuinely happen later.
- Say who does what: "the compiler checks", not "is checked". Passive is fine only when the actor is unknown or beside the point.
- Write instructions as commands: "Click Submit." State facts plainly. Never "should be done".
- Put the condition before the instruction: "To delete the document, click Delete."
- Put the common case first. Exceptions after.
- Sound like a knowledgeable friend. No buzzwords, no figurative language, no "please" in instructions, and never "simply", "easy" or "quickly" in a procedure. If it were simple, the reader would not be here.
- Don't pre-announce ("we will soon support...") and don't start consecutive sentences with the same phrase.
- Link with words that say where the link goes: the page title or a short description. Never "click here". Prefer a sentence of context on the page over a link off it.
- Headings carry the point, not just the topic ("Pick the mode first", not "Modes"). Sentence case. A task heading is a bare verb phrase ("Create an instance"). A concept heading is a noun phrase. One h1 per page, no skipped levels.
- Numbered lists for sequences, bullets for everything else. Introduce a list with a complete sentence. Keep items parallel.
- Code goes in code font. UI elements go in bold. Use serial commas. Drop "etc." and say up front that a list is partial.

## Make statements load one at a time (STE rules)

- One instruction per sentence. One thought per sentence everywhere else.
- Split instructions longer than about 20 words and other sentences longer than about 25.
- Put the warning or condition before the step it guards: "If hot oil touches your skin, injuries can occur."
- Keep "the" and "a": "Remove backup file" reads two ways. "Remove the backup file" reads one.
- Give each word one meaning and one job, then keep it. If "check" means inspect, don't also use it for restrain.
- Pick one word per action and stick to it: "start", not "start" here and "initiate" there.
- Write procedures as direct commands, never as narration and never in the passive: "Install the component", not "the component must be installed".
- Avoid "-ing" words where you can.

Lean on this layer rather than enforcing it: STE is flat and repetitive on purpose, which is right in a procedure and wrong in prose meant to persuade. The instructions get it in full; the explanation takes the habits and keeps its own voice.

## Leave no sentence open to two readings (Global English)

- Keep words like "only" and "not" next to the word they change: "only fails on growth" and "fails only on growth" say different things.
- Break up long noun strings: "the proto import budget check script" becomes "the script that checks the proto-import budget".
- Make every "it", "they" and "this" point at one obvious thing. Repeat the noun when in doubt. Never use "this" or "which" to point at a whole clause.
- Don't drop verbs: "Phase 1 moves the converters and Phase 2 the runtime" leaves Phase 2 without one. Give it one.
- Keep the small words that show structure, such as "that" in "Ensure that the switch is off". Never trade clarity for word count.
- Repeat the article in a series when it prevents a misread: "the client and the host", not "the client and host", when they are two things.
- Say which parts "and" or "or" joins when a sentence can group two ways. "Both...and", "either...or" and "if...then" are free disambiguators.
- Use periods, not semicolons. Replace an em dash with a new sentence.
- Make text in parentheses a full grammatical unit or its own sentence. Never form plurals with "(s)".
- No slashes: write "a, b, or both" instead of "a/b" or "and/or".
- Call each thing by one name, everywhere. A doc that says "the gate", "the ratchet" and "the budget check" for one thing teaches three things. Don't churn what didn't change.
- Skip idioms, colloquialisms, Latin abbreviations and metaphors.

## The unslop pass

Apply the unslop pass in `references/unslop.md` to every doc this skill touches, after the four layers. It owns the slop-pattern catalog: AI vocabulary, filler, hedging, formatting tells, the plain-speech rules and the active-voice rule. Run it after the four layers because it removes the tells they leave behind, and run it as a pass of its own rather than as a rewrite: the meaning does not change, the surface does.

## The copy-review pass, last of all

Then run the copy-review pass in `references/copy-review.md`. It attacks the same family of AI tells from the other direction: quote the line, name the tell, cut or rewrite. Run it after unslop because unslop removes vocabulary and surface, and copy review catches what survives that: the shapes, the kickers, the invented number, the third item added for rhythm. The scan list is `references/copy-review-word-list.md`, and the pass carries its own worked example.

This pass is not only for client documentation. Run it on its own on any prose longer than about 100 characters that this skill writes or edits, whatever the format: a Slack message, a PR body, a commit body, a reply. Short copy is where the tells show most, and the pass costs one re-read.

The two passes are kept as two whole files rather than merged, so a rule appears in both where they overlap, and both passes run. Where a copy-review rule and an unslop rule disagree, the copy-review rule wins: it runs last, and its Calibration section is the guard against overcorrecting. The four layers above both still hold, so the Global English rule that replaces an em dash with a new sentence stays the default in documentation prose, and copy review's tolerance for em dashes does not override it.

## Voice and repo specifics

- A PR description and a commit message are writing too. Every layer except Diátaxis applies to them. A PR body is a briefing a reviewer can read in under a minute. Do not paste worker logs, sha lists or metric tables. Link them.
- Product UI strings are not documentation. Use the product's copy guidelines for those.
- Indent code snippets with tabs. Write real paths. Make every count or tree claim true at the commit that lands it, and include the command that regenerates it.
- The client's own style, voice and terminology win where the client has them: a house style guide, a glossary of their terms, a required doc template. Match it, and keep the four layers underneath it. Their vocabulary beats this skill's examples.
- The project's `GLOSSARY.md` (or the client's equivalent) is the word list for domain terms, the same way the codebase is the word list for symbols. `domain` owns that vocabulary; this skill uses it and does not rename it.
- Diátaxis decides the shape of a document, not the shape of a repository's documentation set: how many guides there are, and where they live, is the client's decision.

## Worked example

Before:

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.
