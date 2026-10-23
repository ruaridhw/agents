---
name: debug
description: Find a bug's root cause before touching the fix, with a red-capable reproduction committed first and a stop after three failed fixes. Use when something is broken, throwing, failing, flaky or slow, when a test fails for an unexplained reason, or when a diagnosis is asked for with no fix wanted.
upstream:
  - repo: superpowers
    path: skills/systematic-debugging
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: mattpocock
    path: skills/engineering/diagnosing-bugs/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/diagnosing-bugs/scripts/hitl-loop.template.sh
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/bug-fix.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/runtime-forensics.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/trace-forensics.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/perf-issue.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
---

# debug

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

**Announce at start:** "Using debug to find the root cause." When the ask is explain, review or diagnose, this skill runs read-only (`ruaridh-mode`, non-negotiable 2): produce the diagnosis, no fix.

## The loop this repo binds

Read `.agents/debug-loop.md` in the repo you are in. It wins over the default below, because a repo whose change cycle is not code (a prompt or process repo, say) debugs its own surface: its loop might be "read the failing run first, then the prompt it was built from". That binding belongs in the repo's file, never here.

The default, when the file is missing:

1. **Root cause before any fix.** No edit until Phase 1 is complete.
2. **Reproduce on the real surface.** The matching test, the real command, the actual run — not a reading of the source that sounds right.
3. **Commit the failing repro before the fix.** The failing test and the fix are two commits, in that order, so git history carries the proof that the bug was real and is gone.
4. **After three failed fixes, stop and talk.** Three failed fixes is a wrong architecture, not a bad hypothesis. When Ruaridh is away, ask per the Inbox convention and wait; do not attempt a fourth.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:

- Test failures
- Bugs in production
- Unexpected behaviour
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**

- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**

- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

Asking for a diagnosis only is this skill with Phase 5's fix held back.

## Redact

You will show commands, outputs and captured artifacts. **Redact every secret first**: write `<REDACTED>` in its place. Build loops against env vars, so the credential stays in the environment rather than in what you show. Captured artifacts carry auth headers: quote only the lines that carry the signal.

If the redacted output is not enough to diagnose the bug, say so and ask.

## Phase 1: Build a feedback loop and investigate

**This phase is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug (one that goes red on _this_ bug), you will find the cause; bisection, hypothesis-testing, and instrumentation all just consume it. If you don't have one, no amount of staring at code will save you.

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → gather more data, don't guess

   Spend disproportionate effort here. **Be aggressive. Be creative. Refuse to give up.** Ways to construct a loop, in roughly this order:

   1. **Failing test** at whatever seam reaches the bug: unit, integration, e2e.
   2. **Curl / HTTP script** against a running dev server.
   3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
   4. **Headless browser script** (Playwright / Puppeteer) that drives the UI and asserts on DOM/console/network.
   5. **Replay a captured trace.** Save a real network request / payload / event log to disk; replay it through the code path in isolation.
   6. **Throwaway harness.** Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
   7. **Property / fuzz loop.** If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
   8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so you can `git bisect run` it.
   9. **Differential loop.** Run the same input through old-version vs new-version (or two configs) and diff outputs.
   10. **HITL bash script.** Last resort. If a human must click, drive _them_ with `references/hitl-loop.template.sh` so the loop is still structured. Captured output feeds back to you.

   Build the right feedback loop, and the bug is 90% fixed.

   **Tighten the loop.** Treat the loop as a product. Once you have _a_ loop, tighten it: make it faster (cache setup, skip unrelated init, narrow the test scope), make the signal sharper (assert on the specific symptom, not "didn't crash"), make it more deterministic (pin time, seed RNG, isolate filesystem, freeze network). A 30-second flaky loop is barely better than no loop; a 2-second deterministic one is tight, a debugging superpower.

   **Non-deterministic bugs.** The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100×, parallelise, add stress, narrow timing windows, inject sleeps. A 50%-flake bug is debuggable; 1% is not, so keep raising the rate until it's debuggable.

   **When you genuinely cannot build a loop**, stop and say so explicitly. List what you tried. Ask for: (a) access to whatever environment reproduces it, (b) a redacted captured artifact (HAR file, log dump, core dump, screen recording with timestamps), or (c) permission to add temporary instrumentation where it runs. Do **not** proceed to hypothesise without a loop.

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes
   - Environmental differences

4. **Gather Evidence in Multi-Component Systems**

   **WHEN system has multiple components (CI → build → signing, API → service → database):**

   **BEFORE proposing fixes, add diagnostic instrumentation:**

   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **Example (multi-layer system):**

   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available in workflow: ==="
   echo "IDENTITY: $([ -n "${IDENTITY:-}" ] && echo SET || echo UNSET)"

   # Layer 2: Build script
   echo "=== Env vars in build script: ==="
   printenv IDENTITY >/dev/null 2>&1 && echo "IDENTITY in environment" || echo "IDENTITY not in environment"

   # Layer 3: Signing script
   echo "=== Keychain state: ==="
   security list-keychains
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

   **This reveals:** Which layer fails (secrets → workflow ✓, workflow → build ✗)

5. **Trace Data Flow**

   **WHEN error is deep in call stack:** see `references/root-cause-tracing.md` for the complete backward tracing technique.

   **Quick version:**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

### Phase 1 is done when one command goes red

You can name **one command** (a script path, a test invocation, a curl) that you have **already run at least once** (show the invocation and its output, redacted), and that is:

- [ ] **Red-capable**: it drives the actual bug code path and asserts the **exact symptom**, so it can go red on this bug and green once fixed. Not "runs without erroring"; it must be able to _catch this specific bug_.
- [ ] **Deterministic**: same verdict every run (flaky bugs: a pinned, high reproduction rate, per above).
- [ ] **Fast**: seconds, not minutes.
- [ ] **Agent-runnable**: you can run it unattended; a human in the loop only via `references/hitl-loop.template.sh`.

If you catch yourself reading code to build a theory before this command exists, **stop: jumping straight to a hypothesis is the exact failure this skill prevents.** No red-capable command, no Phase 2.

## Phase 2: Reproduce and minimise

Run the loop. Watch it go red as the bug appears. Confirm:

- [ ] The loop produces the failure mode the **reporter** described, not a different failure that happens to be nearby. Wrong bug = wrong fix.
- [ ] The failure is reproducible across multiple runs (or, for non-deterministic bugs, reproducible at a high enough rate to debug against).
- [ ] You have captured the exact symptom (error message, wrong output, slow timing) so later phases can verify the fix actually addresses it.

**Minimise.** Once it's red, shrink the repro to the **smallest scenario that still goes red**. Cut inputs, callers, config, data, and steps **one at a time**, re-running the loop after each cut, and keep only what's load-bearing for the failure.

A minimal repro shrinks the hypothesis space in Phase 4 (fewer moving parts left to suspect) and becomes the clean regression test in Phase 5. Done when **every remaining element is load-bearing**: removing any one of them makes the loop go green.

Do not proceed until you have reproduced **and** minimised.

## Phase 3: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim - read every line
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

## Phase 4: Hypothesise, then instrument

Generate **3-5 ranked hypotheses** before testing any of them. Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If \<X\> is the cause, then \<changing Y\> will make the bug disappear / \<changing Z\> will make it worse."

If you cannot state the prediction, the hypothesis is a vibe: discard or sharpen it.

**Show the ranked list before testing it.** Ruaridh often has domain knowledge that re-ranks instantly ("we just deployed a change to #3"), or knows hypotheses already ruled out. Cheap checkpoint, big time saver. Don't block on it; proceed with your ranking when he is away.

Then test **one variable at a time**, minimally:

- **State the hypothesis clearly** and write it down. Be specific, not vague.
- **Make the SMALLEST possible change to test it.** Don't fix multiple things at once.
- **Verify before continuing.** Did it work? Yes → Phase 5. Didn't work? Form a NEW hypothesis. DON'T add more fixes on top.
- **When You Don't Know:** say "I don't understand X". Don't pretend to know. Ask for help. Research more.

Each probe must map to a specific prediction from the ranked list. **Change one variable at a time.** Tool preference: a **debugger or REPL inspection** if the environment supports it (one breakpoint beats ten logs), then **targeted logs** at the boundaries that distinguish hypotheses. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep. Untagged logs survive; tagged logs die.

Binary-search where the evidence lets you. Seed the candidate list from the affected subsystem and from the regression history (`git log` over the changed area). Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate what dies. **Confirm the surviving *mechanism* with runtime evidence before planning the fix.**

## Phase 5: Fix, and the regression test

**Be scientific. Every shipped line traces to runtime evidence.** Belt-and-suspenders that "might help" is a hypothesis, not a fix: it does not ship. When evidence refutes a hypothesis, revert what it motivated. The smallest change the evidence justifies ships, nothing more.

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing
   - Write the regression test **before the fix**, but only if there is a **correct seam** for it (the rules are in `tdd`)

   Write the test from the minimised repro, in its own commit, and watch it fail. If you forced the red by mutating code or a fixture, `diff` against a pristine copy to prove the mutation landed before you trust it.

   **If no correct seam exists, that itself is the finding.** Note it: the codebase's architecture is preventing the bug from being locked down. Flag it for the next phase, and use the closest executable check there is.

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring
   - Commit the fix separately from the failing repro

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?
   - Re-run the Phase 1 feedback loop against the original, un-minimised scenario
   - `verify` governs the claim before you say it is fixed

4. **If Fix Doesn't Work**
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - **If ≥ 3: STOP and question the architecture (step 5 below)**
   - DON'T attempt Fix #4 without architectural discussion

5. **If 3+ Fixes Failed: Question Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   **Discuss before attempting more fixes.** In chat when Ruaridh is here; per the Inbox convention when he is away, then wait.

   This is NOT a failed hypothesis - this is a wrong architecture.

## Phase 6: Cleanup

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or the absence of a correct seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix)
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug location)
- [ ] The hypothesis that turned out correct is stated in the commit / PR message, so the next debugger learns

**Verify the fix on the same surface the bug was reported on.** "Inconclusive" or wrong-surface is not a pass; flag it. Unit tests show branch behaviour, not bug absence. In a `debug` run the fixing PR is `implement`'s landing or `pr`'s, so hand back the evidence it needs: the root cause, the failing-then-passing output verbatim, and the loop's command.

## After a root-cause fix: defense in depth

When the bug was caused by invalid data, one validation point feels sufficient, but that single check can be bypassed by different code paths, refactoring or mocks. After the root cause is fixed, `references/defense-in-depth.md` adds validation at every layer the data passes through, so the bug becomes structurally impossible rather than merely fixed.

## Flaky tests and arbitrary waits

Arbitrary delays in tests guess at timing. `references/condition-based-waiting.md` replaces them with waiting for the condition, which is also how you make a non-deterministic bug's loop tight enough to debug. The worked implementation is `references/condition-based-waiting-example.ts`.

## Diagnosis only: forensics

When the deliverable is a cited diagnosis rather than a fix — a spinning process, a leak, a visual glitch, a captured trace somebody handed you — read `references/forensics.md`. It keeps pstack's two playbooks: instrument the live process, or read the artifact that already exists. A read-only forensics run reports `throughput checkpoint: n/a, read-only forensics`, hands back the source location and the artifact paths, and routes the fix here or to `implement` once the cause is known.

## A performance issue

**You own the measurement story. Tie every fix to a measurement; don't read source instead of measuring.**

1. Capture a baseline trace on the matching surface. Vet the baseline, and each later number, with `verify`'s benchmark checklist: **any number you report for a slowness goes through it first** (`ruaridh-mode` intake routes a measured slowness here for exactly this).
2. Ground hypotheses in the code you have read. Don't claim a performance ceiling without running it first. Try the performance mantras in order, cheapest first:
   1. Don't do it. Stop work whose result nothing uses rather than cheapening it.
   2. Do it, but don't do it again.
   3. Do it less.
   4. Do it later.
   5. Do it when they're not looking.
   6. Do it concurrently.
   7. Do it cheaper.

   When an earlier mantra meets the target, stop.
3. Plan the fix from the trace. If it crosses a function boundary, settle the shape before the move (`architect` on the map, or `to-plan` when it forks the design). Then apply Phase 5's cadence: the failing measurement or regression test first, the smallest fix, a post-fix trace.
4. Parse and compare the artifacts (JSON to sqlite, diff). "Inconclusive" or wrong-surface is not a pass. Flag it.
5. Cite the measurement in the PR: one primary number with its unit, before → after, and the artifact path.

For sustained improvement against a metric rather than a one-off fix, that is a ticket wave through `to-plan`, not one debug run.

**Reply:** baseline number, post-fix number, delta, artifact path.

## Red Flags - STOP and Follow Process

If you catch yourself thinking:

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 5.5).

## Signals from Ruaridh that you are doing it wrong

**Watch for these redirections:**

- "Is that not happening?" - You assumed without verifying
- "Will it show us...?" - You should have added evidence gathering
- "Stop guessing" - You're proposing fixes without understanding
- "Ultra-think this" - Question fundamentals, not just symptoms
- "We're stuck?" (frustrated) - Your approach isn't working

**When you see these:** STOP. Return to Phase 1.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause + loop** | Read errors, reproduce, check changes, gather evidence | One red-capable command you have run |
| **2. Reproduce + minimise** | Shrink the repro until every element is load-bearing | The reported symptom, at its smallest |
| **3. Pattern** | Find working examples, compare | Identify differences |
| **4. Hypothesis** | Rank 3-5 falsifiable theories, instrument, test minimally | Confirmed or new hypothesis |
| **5. Implementation** | Create test, fix, verify | Bug resolved, tests pass |
| **6. Cleanup** | Remove instrumentation, state the cause | Nothing tagged left; the next debugger learns |

## When Process Reveals "No Root Cause"

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

## Supporting files

- **`references/root-cause-tracing.md`** - Trace bugs backward through call stack to find original trigger
- **`references/defense-in-depth.md`** - Add validation at multiple layers after finding root cause
- **`references/condition-based-waiting.md`** - Replace arbitrary timeouts with condition polling
- **`references/condition-based-waiting-example.ts`** - The worked implementation of those wait helpers
- **`references/forensics.md`** - Diagnosis from a live process or an already-captured artifact
- **`references/hitl-loop.template.sh`** - A structured human-in-the-loop loop, when only a person can drive it
- **`scripts/find-polluter.sh`** - Bisection script for the test that creates unwanted files or state
