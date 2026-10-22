---
name: prototype
description: "Build a throwaway prototype to settle one design question: a shareable logic demo, or several radically different UI variants behind one switcher, or competing candidates judged and grafted. Use when a layout, interaction, state model or behaviour needs testing before it is built, when a spike would settle what Ruaridh wants, or when one attempt at a non-trivial artefact would lock in the wrong shape."
upstream:
  - repo: mattpocock
    path: skills/engineering/prototype/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/prototype/LOGIC.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/prototype/UI.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/prototype.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/arena/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: superpowers
    path: skills/brainstorming/SKILL.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
---

# prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

**You own the design decision, not the code.** The prototype is a throwaway instrument: this is the one place where "smallest change" and the verification bar invert, so speed beats polish and code quality does not matter. The rigour is in picking the right design cheaply. Propose variations nobody asked for, throw an approach away and try another.

**Announce at start:** "Using prototype to settle this before we build it."

## Scope the decision first

No decision means no prototype: `implement` takes the work instead.

1. **Name the decision.** Which layout, which interaction, which density — or, for an empirical fork, which behaviour, timing or approach. Write it in one line at the top of the prototype and in the ticket comment when there is a ticket.
2. **Gather references when the design space is open.** Search for prior art, summarise the themes, palettes and layouts, and let Ruaridh pick directions before anything is built. Skip this when the direction is already set.
3. **Choose where it lives.** The code sits next to the thing it prototypes for, so its context is obvious, and on a throwaway branch (`worktree` cuts the tree). The question, the screenshots and the notes go in `.scratch/prototypes/<slug>/`, which Ruaridh can open and which no skill deletes. Main never keeps the prototype.

## Pick a branch

Identify which question is being answered, using the prompt, the surrounding code, or by asking if Ruaridh is around:

- **"Does this logic / state model feel right?"** → read `references/logic.md`. Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → read `references/ui.md`. Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.
- **"Which of these attempts is the right shape?"** → the arena, below. Several candidates at the same task, judged against a rubric, then grafted.

The branches produce very different artefacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and Ruaridh isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious, but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner: `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file Ruaridh double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE, wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so Ruaridh can see what changed.
6. **Capture it when done.** Fold any validated decision into the real code, then capture the prototype itself as a **primary source**: commit it to a throwaway branch, out of main, and leave a context pointer to that branch on the implementation ticket (`implement`, per `.agents/tracker.md`). Capture the answer too (the verdict and the question it settled) in the ticket or a commit. The main branch keeps only the validated decision.

## Competing candidates: the arena

Use the arena when one attempt at a non-trivial artefact would lock in the wrong shape, or when several design directions are cheap to try at once. Each candidate runs in its own Herdr pane (`herdr`, the `builder` role) and its own worktree (`.worktrees/arena-<slug>-<n>`), so no two writers share state.

Open a todo per phase — Frame, Fan out, Cross-judge, Pick, Graft, Verify — before launching anything.

### Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artefact each candidate is producing.
2. Derive the rubric: 3-6 concrete gradeable criteria for what success looks like on *this* task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick the roles. `builder` for the candidates; use the same role N times when the work is generation-bound rather than judgment-sensitive, and vary it when the point is to compare models.
4. Give each candidate its own output location (its own worktree and branch).

### Phase B: Fan out

Spawn all N panes in parallel, each with the task, the path to the shared grounding, its own output path, and an instruction to produce the artefact and a short rationale naming the alternatives it considered and what it rejected.

If a candidate produces no output, proceed with N-1 and note the dropout.

### Phase C: Cross-judge

After all candidates finish, spawn one read-only judge — `reviewer`, a different model family from the session where one is available — with the rubric and the candidates by path label. It scores each criterion and recommends a base with rationale. It runs in parallel with your own reading in Phase D. Don't spawn it while candidates are still writing.

### Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous: read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API.

### Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape: no graft is needed. If they wildly diverge, Phase A was under-specified — reframe and re-run rather than averaging the divergence.

### Phase F: Verify

Verify the synthesized artefact like any other output (`verify`). If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

### The synthesis note

Write it in `.scratch/prototypes/<slug>/synthesis.md`: the base and why, the cross-judge's verdict, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.

## Verify on the matching surface

For a visual decision: screenshot each variant and drive the interaction. For a behavioural or timing decision: observe the thing being decided by logging the timing, printing the output or watching the render. **The observation is the test here, not an assertion.** Show Ruaridh the URL, the `?variant=` keys or the file, and read the real feedback: "I want the header from B with the sidebar from C" is the design he actually wants.

## Present and hand on

Present alternatives, tradeoffs and a recommendation. The output is the decision plus the throwaway artefact, never shippable code. Hand the chosen direction to `implement` for the real build, or to `arch` when the shape itself is what got settled.

## Spikes

A quick throwaway build is often the cheapest way to learn what Ruaridh wants or whether something works. Offer one when it would help. When he just wants to spike, get out of the way: spikes get no tests or minimal ones, aren't bulletproof, and skip the plan, implementation and review process. Bring what the spike taught back into the conversation.

A spike stays labelled throwaway, and **keeping what it produced is a new request**: it comes back through the chain as real work, with `implement` and `tdd`, rather than being blessed in place.

## Anti-patterns

- **Skipping the decision.** A prototype with no question answers nothing. Route to `implement`.
- **Promoting the prototype directly.** Variant and demo code was written under prototype constraints (no tests, minimal error handling). Rewrite it properly when folding it in.
- **Shipping the switcher.** It is a prototype tool: hidden in production builds, and pointed at a throwaway branch, never left in main.
- **Adding tests.** A prototype that needs tests is no longer a prototype.
- **Wiring it to the real database.** In-memory state unless persistence is the question.
- **Generalising.** No "what if we wanted to support X later". The prototype answers one question.
- **Variants that differ only in colour or copy**, or that share a layout. That is a tweak, not a prototype.
- **Wiring variants to real mutations.** Read-only prototypes are fine; point a mutation at a stub.
- **Losing the evidence.** A validated decision with no ticket comment, no branch pointer and no synthesis note leaves the next session re-litigating it.
