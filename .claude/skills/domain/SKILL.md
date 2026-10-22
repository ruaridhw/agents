---
name: domain
description: "Build and sharpen a project's domain model: challenge and settle terminology, write `GLOSSARY.md`, and record decisions as ADRs in `docs/adr/`. Use when a term is contested, when asked to define domain terms or build a glossary, when writing or editing an ADR, or when another skill needs the deep-module vocabulary."
upstream:
  - repo: mattpocock
    path: skills/engineering/domain-modeling/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/domain-modeling/GLOSSARY-FORMAT.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/domain-modeling/ADR-FORMAT.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/deprecated/ubiquitous-language/SKILL.md
    sha: f958fa17c1b62c3f7be38fc09512669acf6b64fc
  - repo: mattpocock
    path: skills/engineering/codebase-design/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
---

# domain

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* `GLOSSARY.md` for vocabulary is not this skill: that is a one-line habit any skill can do. This skill is for when you are changing the model, not just consuming it.

`domain` owns vocabulary. `arch` owns shape. When a question is about what a word means, or about a decision that is hard to reverse, it is this skill's; when it is about how a module is cut, it is `arch`'s, and `arch` reads the vocabulary here.

Two things get written, and nothing else:

- **`GLOSSARY.md`**, the one glossary, at the repo root.
- **ADRs**, in `docs/adr/`, numbered `NNNN-<slug>.md`.

Both are created lazily, only when there is something real to write. Never create an empty `GLOSSARY.md` or an empty `docs/adr/` because a skill mentioned one; if the files are absent, work proceeds silently without them.

## Where it is called from

- `grill` and `to-spec` call `domain` when a term in the conversation is contested: the same word meaning two things, two words for one thing, a vague or overloaded term, or a phrase that contradicts what the repo already settled.
- `arch` settles structure, and records its settled decisions here as ADRs, in the same numbering.
- Any skill that needs the deep-module vocabulary reads `references/deep-module-vocabulary.md`.
- Anyone may invoke it directly: build a glossary from a conversation, settle a term, record a decision.

## File structure

```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

`GLOSSARY.md` at the root, `docs/adr/` beside it. One glossary per repo, one ADR sequence. A repo whose `.agents/domain.md` names other paths wins; the file still points at one glossary and one ADR directory, and `setup-project` writes it. The formats are in `references/glossary-format.md` and `references/adr-format.md`.

## During the session

### Challenge against the glossary

When someone uses a term that conflicts with the existing language in `GLOSSARY.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When someone uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the speaker to be precise about the boundaries between concepts.

### Cross-reference with code

When someone states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update GLOSSARY.md inline

When a term is resolved, update `GLOSSARY.md` right there. Don't batch these up: capture them as they happen. Use the format in `references/glossary-format.md`.

`GLOSSARY.md` should be totally devoid of implementation details. Do not treat it as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer an ADR sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful.
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and one was picked for specific reasons.

If any of the three is missing, skip the ADR. Use the format in `references/adr-format.md`.

## ADR numbering

ADRs share one sequence, `0001`, `0002`, …, across `domain` and `arch`: the directory is the record of both vocabulary decisions and structure decisions, and a reader expects one timeline.

Before writing one, list `docs/adr/` and take the highest existing number plus one. Never reuse a number, never renumber an existing ADR, and never overwrite one: a decision that is revisited gets a new ADR whose Status line names the one it supersedes (`superseded by ADR-NNNN`). That is the only way an old ADR changes.

## The extraction pass

For a whole conversation rather than one contested term: scan it for the domain-relevant nouns, verbs and concepts, find the ambiguities and synonyms, propose a canonical set, write `GLOSSARY.md`, and summarise inline. The process, its rules (opinionated choices, an `_Avoid_` list per term, tight definitions, relationships, an example dialogue, flagged ambiguities) and how to re-run it are in `references/glossary-pass.md`.

The pass is what `grill` reaches for when a conversation has produced more vocabulary than the glossary holds, and what a first glossary in a repo usually comes from.

## Output

- `GLOSSARY.md` changes are made inline, as terms settle, and the reply says which terms were added or changed.
- An ADR is one file per decision, numbered in the shared sequence, and the reply names the number and the decision.
- A summary of the pass, inline in the conversation, names the canonical terms, the flagged ambiguities and where the file is.
- Both files are the repo's, so they are committed with the work that prompted them, in a gitmoji commit with a why line, not as a separate curation.

## Rules

- Neither file is generated speculatively. No term resolved, no glossary entry; no decision that passes the three tests, no ADR.
- The glossary holds domain language only: no implementation detail, no general programming concepts, no module or class names unless they mean something to a domain expert.
- A term the glossary avoids is written down as avoided. That list is what stops the synonyms coming back.
- A decision that contradicts an existing ADR is surfaced, never silently overridden: "This contradicts ADR-0007, and I think it should be reopened because …".
- If Ruaridh is away and the term or the decision is genuinely his to settle, ask per the Inbox convention and carry on with what does not depend on the answer.
