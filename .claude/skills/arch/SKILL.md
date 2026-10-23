---
name: arch
description: "Design and review the structure of code: settle types, module shape and the caller's usage before code crosses a boundary, generate competing designs and compare them, or scan a codebase for deepening opportunities. Use when asked to \"architect this\", design a module or interface, compare design options, or review whether the current shape should change before building on it."
upstream:
  - repo: pstack
    path: pstack/skills/architect/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/architect/references/design-red-flags.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/architect/references/rationale-template.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/architect/references/runner-prompt.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: mattpocock
    path: skills/deprecated/design-an-interface/SKILL.md
    sha: f958fa17c1b62c3f7be38fc09512669acf6b64fc
  - repo: mattpocock
    path: skills/engineering/codebase-design/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/codebase-design/DESIGN-IT-TWICE.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/codebase-design/DEEPENING.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/improve-codebase-architecture/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/improve-codebase-architecture/HTML-REPORT.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: superpowers
    path: skills/brainstorming/SKILL.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
---

# arch

Design and review the **shape** of code. `domain` owns the words a thing is called; `arch` owns how it is cut, where the seam goes, and what the caller has to know.

Two jobs, both here because both settle the same thing (structure) with the same vocabulary (module, interface, implementation, depth, seam, adapter, leverage, locality, in `domain`'s `references/deep-module-vocabulary.md`):

- **Design a new shape.** Sketch types, function signatures and module boundaries with `not implemented` bodies and pseudocode, from two or more structurally distinct candidates, before code crosses a boundary. Then implement against the sketch.
- **Review an existing shape.** Scan a codebase for **deepening opportunities**: refactors that turn shallow modules into deep ones, judged by the design red flags and the deletion test.

Read `domain`'s `references/deep-module-vocabulary.md` before using any of those words, and `references/design-red-flags.md` before judging a candidate. Both are load-bearing: the value of this skill is a comparison written in one vocabulary, not a prose taste test.

Outputs:

- A **comparison** at `.scratch/arch/<YYYY-MM-DD>-<slug>.md`: the problem, the candidates, what each hides, the comparison, the recommendation. Gitignored. Optionally rendered as an HTML report beside it (`references/report.md`).
- **Settled decisions as ADRs**, in the repo's `docs/adr/`, numbered `NNNN-<slug>.md` in the one sequence shared with `domain`. An ADR is written only when the decision passes `domain`'s three tests, and `domain`'s `references/adr-format.md` is the format.

## Designing a new shape

Five phases. Open a todo per phase before starting.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

### Phase A: Ground the problem

Build a real mental model of every system the new code touches. Run `research`'s how-mode over the relevant subsystems. Naming a file isn't grounding: the output is the architectural explanation `research` prescribes. If the design redefines ownership or layering, also run `research`'s why-mode over the existing shape, so the rationale becomes a constraint rather than a guess.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

Read the project's `GLOSSARY.md` and the ADRs in the area first. Use the glossary's terms for domain concepts, and do not re-litigate a decision an ADR already records: a candidate that contradicts one is surfaced with the contradiction named, not proposed as if it were new (`domain` is where a term or a settled decision is changed).

### Phase B: Sketch

Generate competing designs in parallel, then compare them. This is the whole point: **design it twice**. The first idea is rarely the best one, and the comparison is the artefact.

1. Write the problem space into the comparison file: the constraints any new interface must satisfy, the dependencies it will rely on and their category (`references/deepening.md`), and a rough illustrative code sketch to make the constraints concrete. That sketch is not a proposal.
2. Spawn three or more candidates **in parallel Herdr panes** through `herdr`, each in its own worktree or subdirectory, so no candidate can see another's work. Use the `builder` role; where the run allows it, put the candidates on different models, because differences between candidates are the signal. Give each a different design constraint:
   - Runner 1: "Minimise the interface: 1-3 entry points, maximum leverage per entry point."
   - Runner 2: "Maximise flexibility: support many use cases and extension."
   - Runner 3: "Optimise for the most common caller: make the default case trivial."
   - Runner 4, where it applies: "Design around ports and adapters for the cross-seam dependencies."
3. Each runner's prompt is `references/runner-prompt.md` with the task, the Phase A grounding artefacts, its working directory and its output path filled in. Each returns a candidate design package: the caller's usage first, then the type sketch, then the module map, then the rationale shaped per `references/rationale-template.md`.

Require at least two **structurally distinct** candidates before synthesis, even when the first looks sufficient. Whole-shape alternatives, not point fixes inside one shape. An agent that returns a flavour of another candidate has not done the job, and the constraint it was given is what to restate.

Screen every candidate against `references/design-red-flags.md` before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on **interface depth**. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers, so depth beats a shallow module with many small methods.

Then **synthesize**: one recommended design, naming which candidate became the base and why, what was adapted from the others, and what was rejected and why. That paragraph is the comparison file's Synthesis decision section. Be opinionated: a strong read, not a menu.

For a smaller design where one candidate is clearly enough, the parallel pass still happens, at the same three-pane minimum. The pass is cheap next to building the wrong shape.

### Phase C: Agree (opt-in)

Default: proceed directly to implementation with the synthesized design. No human checkpoint.

Opt in to a checkpoint when Ruaridh explicitly asks for one ("stop and show me before implementing", "with a checkpoint"). Then surface the synthesized design and pause for sign-off; away from chat, ask per the Inbox convention. A checkpoint may also be a Plannotator review of the comparison file when the design is material and he wants to read it.

The synthesis can ship as its own commit either way, as scaffolding first. Planned and scoped breakage during fill-in is fine. For adversarial pressure on the design before implementing, run `review` on the sketch.

If Ruaridh pushes back on the shape, in a checkpoint or after the fact, treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

### Phase D: Implement against the sketch

Replace `not implemented` bodies with code, and pseudocode with logic. The synthesized sketch is the contract. Deviations from it are a signal to surface, not friction to absorb silently. If a function needs a parameter the sketch did not anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

### Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch cannot absorb, throw the sketch out. Don't bolt fixes onto a wrong design.

The signal is a *pattern*, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state was not shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the implementation.

Use judgment. A few edge cases do not condemn an architecture. Some problems are legitimately complex: complexity in the data is not complexity in the design.

When you scrap:

1. Re-run `research`'s how-mode over what has been built.
2. Redesign as if the new constraints had been day-one assumptions.
3. Subtract before adding. The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and re-run the parallel pass.

### The spike rule

A quick throwaway build is often the cheapest way to learn whether a shape works. Offer one when it would help, and when Ruaridh just wants to spike, get out of the way: a spike gets no tests or minimal ones, is not bulletproof, and skips the plan, implementation and review process. Bring what the spike taught back into the comparison, and never let the spike become the implementation by inertia. Keeping what it produced is a new request, decided against the sketch.

## Reviewing an existing shape

Scan for **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If Ruaridh named a direction (a module, a subsystem, a pain point), take it and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the hot spots, the files and areas that keep coming up, and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Read the project's `GLOSSARY.md` and any ADRs in the area you are touching first.

Then walk the codebase, or send a `research` how-mode explorer through it. Don't follow rigid heuristics; explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow**, with an interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they are called (no **locality**)?
- Where do tightly coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? "It concentrates" is the signal you want.

### 2. Write the candidates into the comparison

One entry per candidate in `.scratch/arch/<date>-<slug>.md`:

- **Files**: which files and modules are involved.
- **Problem**: why the current architecture causes friction, one sentence.
- **Solution**: plain English, what would change, one sentence.
- **Benefits**: in terms of locality and leverage, and how tests would improve.
- **Before and after**: a diagram, or a short description when a diagram would not earn its space.
- **Recommendation strength**: `Strong`, `Worth exploring`, or `Speculative`.
- **ADR callout**, when the candidate contradicts one: one line, naming the ADR and why it is worth reopening.

Use `GLOSSARY.md` vocabulary for the domain and the deep-module vocabulary for the architecture. If `GLOSSARY.md` defines "Order", talk about "the Order intake module", not "the FooBarHandler", and not "the Order service".

Do not propose interfaces yet. End the file with a **Top recommendation**: which candidate you would tackle first and why. Ask which one to explore. `references/report.md` has the optional HTML rendering of the same cards, for when seeing the before and after matters more than reading it.

### 3. Grill the chosen candidate

Once one is picked, run `grill` to walk the decision tree with Ruaridh: constraints, dependencies, the shape of the deepened module, what sits behind the seam, which tests survive.

Side effects happen inline as decisions crystallise, through `domain`:

- **A deepened module named after a concept not in `GLOSSARY.md`?** Add the term.
- **A fuzzy term sharpened during the conversation?** Update the glossary there.
- **The candidate rejected with a load-bearing reason?** Offer an ADR framed as "record this so a future review does not re-suggest it?". Only when the reason is one a future explorer would need in order to avoid the same suggestion; skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Alternative interfaces for the deepened module?** That is Phase B: the parallel pass over `references/design-it-twice.md`, then the comparison.

## Output

The comparison file is the deliverable of a design or a scan. Its shape:

1. **Problem**: one paragraph, including the constraints Phase A surfaced and the ADRs in play.
2. **Usage (the caller's view)**, written first, before any type sketch: what a caller imports, calls and gets back, with two or three realistic call sites. The types in the shape are derived from this; when they disagree, the usage wins. The caller's experience is the spec.
3. **Shape**: data structures first, then how data flows through the signatures, the load-bearing decisions, what is encoded in types, where validation lives, and what the system deliberately does not do.
4. **Synthesis decision**: which candidate became the base, what was adapted, what was rejected and why.
5. **Tradeoffs accepted**: one bullet per trade-off, in the form "we accept X in exchange for Y". Name anything a future reader might mistake for an oversight.
6. **Alternatives considered**: required. At least one concrete alternative shape with one line on why it lost, judged on interface depth rather than implementation effort. Flavours of the same shape do not count. One is fine when the constraints forced the answer, phrased as "this was the only viable shape because …".
7. **Open questions and risks**, phrased as questions so the answer is the resolution.
8. **Next implementation step**: one sentence.

`references/rationale-template.md` holds the same sections as the prose skeleton to fill in. For a scan, the same file carries the candidate cards instead, and the top recommendation closes it.

Then, for each decision that passes `domain`'s three tests, an ADR in `docs/adr/`, numbered in the shared sequence. The comparison file stays scratch; the ADR is the durable record.

## Rules

- `arch` settles shape; it does not settle vocabulary. A new word goes to `domain`, and a contested one is settled there before the sketch uses it.
- Nothing here re-litigates a recorded decision silently. An ADR in the way is named in the candidate, with why it might be reopened.
- The comparison is prose, not a table of scores. Tables flatten the difference that matters (what each design hides), and the recommendation is a judgement, not a sum.
- Never implement inside Phase B. The candidates are sketches with `not implemented` bodies; the point is the comparison, and code locks in a shape before it is chosen.
- Do not propose a deepening without a strength label, and do not label one `Strong` without a red-flag screen and the deletion test behind it.
- Never edit the codebase during a scan. The scan reports; `implement` changes.
