# Style foundations

**Not from a feed.** The upstream `technical-writing` skill states the four style layers as rules, and the rules are kept in `SKILL.md` word for word. This reference fills in what those rules assume: what each mode of documentation is for, the Google developer-style decisions behind the sentence rules, the Simplified Technical English rules the instruction layer is drawn from, and the Global English rules for unambiguous syntax. It was written for this skill; nothing here is upstream text. Where the two disagree, `SKILL.md` wins, because it is the stamped copy.

## Diátaxis: the four modes

Diátaxis separates documentation by what the reader needs, on two axes: **action versus understanding**, and **learning versus work**. The four modes are the four combinations, and a document has exactly one.

|  | Learning | Work |
| --- | --- | --- |
| **Action** | Tutorial | How-to guide |
| **Understanding** | Explanation | Reference |

**Tutorial.** A lesson the reader follows to learn by doing. The learner's success is the author's responsibility: every step works on a clean machine, every step produces a visible result, and the reader is told what that result should look like. A tutorial teaches one skill, on one path, with no branches. It does not explain why beyond a clause and a link, because explanation interrupts doing.

**How-to guide.** Steps to reach a goal the reader already has in mind. It assumes competence, so it teaches nothing that the goal does not require, and it can branch ("if your cluster is remote, do this instead"). It solves a problem a person has, not an operation a program can perform, and its title names the task.

**Reference.** Facts the reader looks up while working. It describes and never instructs or persuades. It is complete within its own scope, dry, and consistent, because a reference is only useful if the reader can trust that the answer is somewhere in it. Its structure mirrors the thing described, so the reader can move between the code and the description without re-orienting.

**Explanation.** Understanding, usually of a why: a design, a constraint, a trade-off, a history. It can be read away from the product. It is the one mode where an opinion belongs, and the one mode where completeness is not required, because its job is to make something make sense, not to cover a surface.

**Applying the compass.** Ask the two questions of a whole document, then of a section, then of a sentence that feels wrong. Two modes in one document split into two documents that link to each other. The common failure is a reference with a tutorial inside it, or a how-to that stops to explain the architecture: both leave the reader unsure whether they are meant to be reading or doing.

**Quality without a mode.** A document that mixes modes cannot be judged, because the standard it is held to depends on the mode. Fix the mode first. Every other rule in `SKILL.md` applies to all four modes.

## Google developer style: what the sentence rules are for

The Google developer documentation style guide is a house style for documentation that a developer reads while working. The rules kept in `SKILL.md` come from three of its decisions:

**Second person, present tense, active voice.** "You" puts the reader in the sentence, and the present tense describes the software as it is now. The active voice names the actor because the actor is usually the piece of software the reader is trying to understand, and a passive sentence hides it.

**The condition before the instruction.** A procedure is easier to follow when the reader knows why they are doing the step before they do it. So the "if" clause comes first, and the exception comes after the common case.

**Headings that carry a point.** A heading is a navigation label and an outline entry at once. "Pick the mode first" tells a skimming reader what the section concludes. "Modes" makes them read to find out.

Two further Google-style decisions are worth knowing because they explain the harder calls:

- **Timeless documentation.** Do not write "currently" or "soon": documentation is read out of date with no warning, and a word that dates it makes the whole page suspect.
- **Code and UI typography are separate.** Code font for anything the reader types or that the program prints, bold for the name of a control. Mixing them turns a click into a search.

## Simplified Technical English: the rules behind the instruction layer

Simplified Technical English (STE, originally AECMA Simplified English, now maintained as ASD-STE100) is a controlled language for maintenance documentation, where a misread instruction damages equipment or people. It is a strict standard with a dictionary of approved words; leaning on it means taking its habits, not enforcing its dictionary.

The habits, which are what `SKILL.md`'s instruction layer states:

- **One instruction per sentence.** Two actions in one sentence produce a reader who does the second before reading it, or does neither.
- **Approved, common verbs with one meaning each.** Use "start", "stop", "remove", "install", "check". Do not use the same verb for two actions, and do not use two verbs for one action in the same document.
- **Active voice and the imperative for procedures.** "Install the component", not "the component must be installed". A procedure written in the passive leaves the actor unnamed, which is exactly the fact the reader needs.
- **The warning before the step.** A condition that makes a step dangerous or impossible belongs in front of the step, in its own sentence.
- **Keep the article.** "Remove backup file" can be read as an instruction about a thing called "backup file" or as a malformed "remove the backup file". The article costs one word and removes the reading.
- **Short sentences, and split rather than join.** Roughly 20 words for an instruction and 25 for a description; longer than that, split.
- **One term per thing, one thing per term.** STE's dictionary is the extreme form of the rule every style guide has: a synonym is a second name for something the reader has to learn.
- **No "-ing" clauses that carry an action.** "Before installing, stop the service" makes the reader work out which action comes first. "Stop the service. Then install it."

The register matters for client-facing docs: STE is deliberately flat and repetitive. That is a feature in a procedure, where the reader is not reading for pleasure, and a fault in prose meant to persuade. Lean on it in the instructions, not in the explanation.

## Global English: unambiguous syntax

Global English is the set of writing choices that keep a sentence readable for someone reading in a second language, or reading under time pressure, or parsing a sentence with a machine. It is less a standard than a convergence of the rules that survive translation.

The categories, which `SKILL.md` states as rules:

- **Scope words next to what they scope.** "Only" and "not" change meaning by position: "the check fails only on growth" and "only the check fails on growth" are different facts.
- **Short noun phrases.** Long noun strings ("the proto import budget check script") force the reader to work out which words modify which. Turn one of them into a clause.
- **Explicit reference.** Every "it", "this", "they" points at one obvious noun. "This" as a stand-in for a whole previous sentence is the most common ambiguity in technical prose, and the fix is a noun.
- **Verbs present.** Ellipsis saves words and costs a reading: "Phase 1 moves the converters and Phase 2 the runtime" leaves the second clause without a verb.
- **Structure words kept.** "That" in "ensure that the switch is off" marks where the subordinate clause starts. Dropping it is a style tic, not an economy.
- **One reading for "and" and "or".** "Both … and", "either … or" and "if … then" are free and remove the question of what is joined to what.
- **One punctuation mark, one job.** Semicolons and em dashes each ask the reader to hold two clauses at once. A full stop does not.
- **One name per thing, for the whole document.** A renamed concept reads as a new concept. Consistency is also what makes a search work.
- **No idioms, no Latin, no metaphor.** "Under the hood", "e.g.", "a stone's throw" and "the ratchet" all assume a shared language game the reader may not be playing.

## Using the four together

They are layers, not alternatives, and they apply in order:

1. **Structure**: is this document one mode, and is it the right mode? Nothing below fixes a document in the wrong mode.
2. **Sentences**: second person, present tense, active voice, condition first, the reader's common case first.
3. **Load**: one instruction or one thought per sentence, with the approved verbs and the articles kept.
4. **Ambiguity**: scope words, references, joined clauses and names, so a careful reader cannot read it two ways.
5. **Slop**: the unslop pass in `unslop.md`, last, because it removes the tells that survive the other four.

When a rule makes a sentence worse, fix the sentence another way. A document that obeys every rule and reads like a machine wrote it has failed at the job the rules exist for.
