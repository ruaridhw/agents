---
name: write-skill
description: "Write an agent skill, an `AGENTS.md` line, or any document an agent reads by pointer, so the agent takes the same process every run. Use when creating a skill of Ruaridh's own, editing one, sharpening a description that fails to trigger, or writing or pruning agent instructions."
upstream:
  - repo: mattpocock
    path: skills/productivity/writing-for-agents/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/productivity/writing-for-agents/SKILL-MECHANICS.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/productivity/writing-great-skills/SKILL.md
    sha: 6bcbcb09e2f1ed5fa20b4e890c732ecbb58c6b64
  - repo: mattpocock
    path: skills/productivity/writing-great-skills/GLOSSARY.md
    sha: 6bcbcb09e2f1ed5fa20b4e890c732ecbb58c6b64
  - repo: mattpocock
    path: skills/productivity/write-a-skill/SKILL.md
    sha: ab7196a1584ac60688aeb63cf0b56a5114c4a6f3
  - repo: superpowers
    path: skills/writing-skills/SKILL.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: superpowers
    path: skills/writing-skills/anthropic-best-practices.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: superpowers
    path: skills/writing-skills/persuasion-principles.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: superpowers
    path: skills/writing-skills/testing-skills-with-subagents.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/authoring-a-skill.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: anthropic
    path: skills/skill-creator/SKILL.md
    sha: dbd4588f9e1033efb41dad4bef2f7947c8993d44
---

# write-skill

How to write a document an agent consumes: a skill, an `AGENTS.md` or `CLAUDE.md` line, a doc reached by a pointer. The packaging differs and the writing does not. The same levers make each one predictable, because the agent takes the same **process** every run rather than producing the same output.

This skill is for **ad-hoc skills of Ruaridh's own**, and for the prose of agent instructions. Three things are deliberately not here:

- **Ingesting upstream text** is `update-skills`. It is the one ingest path, and it keeps the upstream prose, records every removal and stamps each feed.
- **Format rules** (frontmatter keys, when-to-use descriptions, stamp shas) are `bin/skill-lint`'s. The lint is the source of truth because it can fail a commit; a paragraph here cannot. This supersedes the earlier plan line that made `write-skill` the source of truth for the format rules.
- **The public-repo rule** (no client, employer-internal, host or personal detail in a tracked file) is `bin/check-public`'s. Same reason: it runs in pre-commit and fails the commit.

**No skill evals yet.** That is Ruaridh's decision (2026-10-22). `references/testing-skills.md` is kept for when it changes; nothing in this skill requires an eval run before a skill lands.

**The 150-line rule.** A skill's `SKILL.md` stays within 150 lines. Past that, reference goes behind a pointer or the skill splits. The ceiling is not about tokens alone: it is what keeps the top of the document legible enough that an agent attends to the steps.

## Predictability is the root virtue

Every lever below serves one thing: the agent taking the same **process** every run, not producing the same output. A brainstorming skill should predictably diverge; its tokens vary and its behaviour does not. Cost and maintainability are symptoms of predictability, not rivals to it.

The vocabulary is defined in `references/glossary.md`: predictability, model-invoked and user-invoked, description, context pointer, context load, cognitive load, router skill, granularity, the information hierarchy, steps, reference, external reference, progressive disclosure, co-location, sprawl, branch, leading word, completion criterion, legwork, post-completion steps, premature completion, negation, single source of truth, duplication, relevance, sediment, no-op. Read a term there when the short form here is not enough.

## Context pointers

A **context pointer** is a reference held in the agent's context that names some out-of-context material and encodes the condition for reaching it. A skill's description is one; a line in `AGENTS.md` naming a doc is the same object. The pointer's *wording*, not its target, decides when the agent reaches the material, and how reliably. A must-have target behind a weakly worded pointer is a variance bug: sharpen the wording first, and inline the material only if sharpening fails.

A pointer does two jobs: state what the material is, and list the **branches** that should trigger reaching it (a branch is a distinct case the document handles, so different runs take different paths through it). Every word of an always-loaded pointer costs on every turn, so it earns even harder pruning than the body:

- **Front-load the leading word**: the pointer is where it does its triggering work.
- **One trigger per branch.** Synonyms that rename a single branch are one branch written twice; collapse them and keep only genuinely distinct branches.
- **Cut identity the body already carries.**

## The two loads

Every document and pointer you add spends one of two budgets:

- **Context load** is the cost of always-loaded material on the agent's window: an `AGENTS.md` line, a skill description, anything sitting in context every turn, spending tokens and attention whether or not it fires.
- **Cognitive load** is the cost on the human: which documents exist and when to reach for each. The human is the index. Not a cost to minimise: it is the price of human agency; spend it where human judgement matters, remove it where it does not.

Material reached only through a pointer escapes context load at the price of the pointer's own line; material with no pointer at all rides entirely on cognitive load.

## Information hierarchy

A document is built from two content types: **steps** (the ordered actions the agent performs) and **reference** (definitions, rules, facts consulted on demand). The two mix freely: all steps (a recipe), all reference (a review's rules), or both. The core decision is where each piece sits on the **information hierarchy**, a ladder ranked by how immediately the agent needs the material:

1. **In-file step** is the primary tier: what the agent does, in order.
2. **In-file reference** is consulted on demand. Often a legitimately flat peer-set (every rule of a review on one rung), which is a fine arrangement, not a smell.
3. **Disclosed reference** is pushed out into a separate file, reached by a context pointer, loaded only when the pointer fires. Spans a sibling file in the same folder through fully external reference that lives anywhere and any document can point at.

Push too little down and the top bloats; push too much and you hide material the agent actually needs. That tension is the whole decision.

**Progressive disclosure** is the move down the ladder (out of the main file and behind a pointer) so the top stays legible. Not primarily a token optimisation: it is how the hierarchy is protected. Branching is the cleanest disclosure test: inline what every branch needs, and push behind a pointer what only some branches reach. When a document has steps, in-file reference that should be disclosed buries them and turns attending to them into a coin-flip: a variance lever, not just a legibility one.

**Co-location** is the within-file companion: where the ladder decides *how far down* a piece sits, co-location decides *what sits beside it* once there. Keep a concept's definition, rules and caveats under one heading rather than scattered, so reading one part brings its neighbours with it. The test: the document should read like documentation written for the agent. Grouped material reads that way; scattered material does not. (Distinct from duplication: that repeats one meaning in two places; scattering fragments one meaning across many.)

**Sprawl** is the failure mode here: a document simply too long, even when every line is live and unique. Attention thins across the excess, and every extra line is one more to keep relevant. The cure is the ladder: disclose reference behind pointers, and split by branch or sequence so each path carries only what it needs.

## Steps and completion criteria

Every step ends on a **completion criterion**, the condition that tells the agent the work is done. Two properties make it a lever:

- **Clarity**: can the agent tell done from not-done? A vague bound ("understanding reached") invites **premature completion**: ending the step before it is genuinely done, attention slipping to *being done*. The visible steps still ahead (the **post-completion steps**) supply the pull; the criterion's clarity is the resistance. Defend in order: **sharpen the bound first** (local and cheap); only if it is irreducibly fuzzy *and* you observe the rush, hide the later steps by splitting the sequence. Hiding only works across a real context boundary (a hand-off or a worker dispatch; an inline call leaves the later steps in context and clears nothing).
- **Demand**: how much it requires. "Every modified model accounted for" forces thorough work where "produce a change list" does not. Demand drives **legwork** (the digging the agent does within the work, latent in the wording rather than written as its own step), and it is not step-bound: "every rule applied" binds a body of flat reference just as "every step done" binds a sequence, which is how an all-reference document still carries an exhaustiveness bar.

The strongest criteria are both checkable and exhaustive.

## When to split

Splitting one document into two spends one of the two loads, so split only when the cut earns it:

- **By sequence**: split a run of steps where the post-completion steps tempt the agent to rush the one in front of it. Keeping them out of view drives more legwork on the current task. Beware the reverse: merging sequences exposes each step's later steps to what follows, inviting premature completion.
- **By invocation**: the skill-specific cut. `references/skill-mechanics.md` has it in full: model-invoked versus user-invoked, the description's job, and router skills.

## Leading words

A **leading word** is a compact concept already living in the model's pretraining that the agent thinks with while running the document (*lesson*, *fog of war*, *tracer bullets*). Repeated as a token, never as a sentence, it accumulates a distributed definition and anchors a whole region of behaviour in the fewest tokens, by recruiting priors the model already holds. Coining your own works if you define it clearly, but a made-up word recruits no priors: you pay in definition tokens what a pretrained word gives free; reach for an existing word first.

It anchors twice. In the body, *execution*: the agent reaches for the same behaviour every time the word appears, and inside flat reference it focuses attention on a class of thing to look for. In a pointer, *invocation*: when the same word lives in your prompts, your docs and your codebase, the agent links that shared language to the material and reaches it more reliably.

Hunt for opportunities to refactor with leading words. A triad spelled out at three sites, a pointer spending a sentence to gesture at one idea. Each is a passage begging to collapse into a single token:

- "fast, deterministic, low-overhead" → *tight* (a *tight* loop).
- "a loop you believe in" → *red*, turning a fuzzy gate into a binary observable state (the loop goes *red* on the bug, or it doesn't).

You win twice: fewer tokens, and a sharper hook for the agent to hang its thinking on. Assume every document is carrying restatements that leading words retire. Go find them.

**Negation** is the failure mode beside this lever: steering by prohibition drags the forbidden behaviour into context and makes it *more* available, not less. *Don't think of an elephant*, and the elephant is all there is; the negation is a weak modifier the strongly-activated concept overruns, so the ban half-reads as an instruction to do the thing. Prompt the **positive**: state the target behaviour ("write one-line comments") so the banned one is never spoken. A prohibition earns its place only as a hard guardrail you cannot phrase positively; even then, pair it with the positive target so attention lands on what to do.

## Writing the description

A model-invoked **description** does two jobs: state what the skill is, and list the branches that should trigger it. It sits in the window every turn, so it earns even harder pruning than the body. The rules are the context-pointer rules above, applied to the one pointer that is always loaded:

- **Front-load the skill's leading word.**
- **One trigger per branch**, not three synonyms for one.
- **Triggers, not a workflow summary.** A description that summarises the skill's process becomes a shortcut the agent follows instead of reading the skill, and the body is then documentation nobody reads. Say *when* to use it; let the body say what happens.
- **Words the agent would search for**: error strings, symptoms, the verbs Ruaridh uses, the tools and file types involved.

Pick **model-invocation** only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and pay no context load. The mechanics, and when to split a skill off on its own trigger word, are in `references/skill-mechanics.md`.

## Pruning

- Keep each meaning in a **single source of truth**: one authoritative place, so changing the behaviour is a one-place edit. **Duplication** (the same meaning in more than one place) costs maintenance and tokens, and inflates a meaning's prominence on the ladder past its real rank. (The accidental inverse of a leading word, which repeats a token on purpose, never the meaning.)
- The **environment** is a source of truth too (`package.json` scripts, config files, the directory layout, `--help` output), and a document that restates it is a **cache**: a copy of a lookup, earning its load only when the lookup is expensive. Cache what the agent cannot find by looking: the unwritten convention, the reason behind a choice, the gotcha no config confesses. Leave the one-file, one-command lookups to the environment, where they cannot go stale.
- Check every line for **relevance**: does it still bear on what the document does? A line loses relevance by never bearing on the task (mere exposition, or a branch that should be disclosed) or by going stale as the behaviour or world it describes changes. Shorter documents are easier to keep relevant. Without a pruning discipline the default fate is **sediment**: stale layers that settle because adding feels safe and removing feels risky, until you must core down through them to find what is still live.
- Hunt **no-ops** sentence by sentence: an instruction the model already obeys by default pays load to say nothing. The test (does it change behaviour versus the default?) is model-relative, not reader-relative: two people disagreeing about a no-op disagree about the default, and settle it by running the document, not by debate. When a sentence fails, delete the whole sentence rather than trim words from it. The test also grades leading words: a word too weak to beat the default (*be thorough* when the agent is already thorough-ish) is a no-op, and the fix is a stronger word (*relentless*), not a different technique.

When in doubt, delete. Keep only prose that changes a decision. Tell it to do the thing and skip the reason; explain only when the rule is confusing without one. Match the tone to the scope. Point at the structural source (a type, a readme, a config file) rather than restating it, and delegate to another skill by path rather than copying its content.

## Match the form to the failure

Before writing guidance, classify the failure you are trying to prevent. The form that bulletproofs one failure type measurably backfires on another.

| Baseline failure | Right form | Wrong form |
| --- | --- | --- |
| Skips or violates a rule under pressure (knows better, does it anyway) | Prohibition, rationalization table, red flags | Soft guidance ("prefer…", "consider…") |
| Complies, but the output has the wrong shape (a bloated prompt, a buried verdict) | Positive recipe or contract: state what the output is, its parts in order | A prohibition list ("don't restate", "never narrate") |
| Omits a required element from something it already produces | Structural: a required field or slot in the template it fills in | A prose reminder near the template |
| Behaviour should depend on a condition | A conditional keyed to an observable predicate | An unconditional rule plus exemption clauses |

Why prohibitions backfire on shaping problems: under a competing incentive, an agent negotiates with "don't X". A recipe leaves nothing to negotiate, because the output either matches the stated shape or it does not.

**No nuance clauses.** "Don't X unless it matters" reopens the negotiation; express a real exception as its own conditional on an observable predicate. **Exemption clauses do not scope.** "This limit doesn't apply to code blocks" still suppresses code blocks; if part of the output must be exempt, restructure so the rule cannot reach it.

### Bulletproofing a discipline rule

For a rule the agent knows and skips under pressure:

- **Close every loophole explicitly.** State the rule, then forbid the workarounds by name: "Delete it. Start over. No exceptions: don't keep it as reference, don't adapt it while writing the test, delete means delete."
- **Settle the spirit-and-letter argument early**: "Violating the letter of the rules is violating the spirit of the rules."
- **Keep a rationalization table.** Every excuse seen in practice goes in the table with its reality, so the next agent meets the excuse and its answer together.
- **Keep a red-flags list** the agent can check itself against, ending in the action: "All of these mean: delete the code and start over."
- `references/persuasion-principles.md` is the research behind why these work (authority, commitment, scarcity, social proof, unity); it is background, not a checklist.

## The process

The order to write in, the directory shape, the output-format and example patterns, and the pre-landing checklist are in `references/authoring-process.md`. `references/anthropic-best-practices.md` is Anthropic's official authoring guidance: concise is key, assume the agent is already smart, set the degree of freedom, and the patterns it lists. Both are references, not steps: a small skill needs neither.

## Rules

- This skill writes prose for agents. It does not decide frontmatter or stamps (`bin/skill-lint`), it does not enforce the public-repo rule (`bin/check-public`), and it does not ingest upstream text (`update-skills`).
- A curated skill's shape is the curation principle's: the upstream prose kept, every removal recorded. `write-skill` never edits a curated skill; a redo is an `update-skills` run.
- The 150-line rule applies to the `SKILL.md` of an ad-hoc skill. A curated skill's length is the curation principle's to decide.
- A skill whose prose was not read back by Ruaridh has not landed. The draft is shown, and his edits win.
- When a rule here and the lint disagree about format, the lint wins and this file gets fixed.
