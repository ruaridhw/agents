# Plan template

Write the plan to `.scratch/plans/<YYYY-MM-DD>-<slug>.md` in this shape, and fill every placeholder. Keep every heading and every sub-block in the order shown. The rules behind each part are in the skill body.

```markdown
# <Feature> implementation plan

**Goal:** <one sentence describing what this builds>

**Architecture:** <2-3 sentences about the approach>

**Tech Stack:** <key technologies and libraries>

**Spec:** <tracker ref> and `.scratch/specs/<YYYY-MM-DD>-<slug>.md`
The plan argues from the spec, so the spec travels with it; executors read both.

**Tickets:** <refs in dependency order>

## Global Constraints

<The spec's project-wide requirements — version floors, dependency limits, naming
and copy rules, platform requirements — one line each, with exact values copied
verbatim from the spec. Every task's requirements implicitly include this section.>

## Review Focus

<The five input classes or failure modes the spec implies but no task's tests
exercise that are most likely to bite a person using this software — one line
each, naming the input or condition and the behavior a reasonable person would
expect, most likely first. Each line's test is added to the task that owns the
code. An empty section says you checked and found none.>

## Task 1: <component> (ticket <ref>)

**Files:**
- Create: `<exact/path>`
- Modify: `<exact/path>:<lines>`
- Test: `<exact/path>`

**Interfaces:**
- Consumes: <what this task uses from earlier tasks — exact signatures>
- Produces: <what later tasks rely on — exact function names, parameter and
  return types. A task's implementer sees only their own task; this block is
  how they learn the names and types neighboring tasks use.>

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `<command>`
Expected: FAIL with "<message the spec or the signature implies>"

- [ ] **Step 3: Implement `<signature>` in `<path>`**

One line on the approach when the signature and the test leave a choice
(which library call, which data structure); a code block only for an
algorithm they do not determine, or exact copy the spec fixes.

- [ ] **Step 4: Run test to verify it passes**

Run: `<command>`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add <explicit paths>
git commit -m "<gitmoji> <imperative summary>" -m "<why the change is made>"
```

**Acceptance:** cites the spec's case by name and the ticket's Done-when; it adds nothing either of them does not say.

## Task 2: <component> (ticket <ref>)

<Same shape. Steps follow the repo's build loop, `.agents/build-loop.md`.>

## Execution

Proposed: inline | delegated.
Split (delegated): builder A → tasks 1, 3; builder B → task 2 (parallel); task 4 after 1 merges.
Reason: <one sentence: how much the tasks depend on each other's interfaces, how many there are, what a shipped mistake would cost>.
Awaiting <Ruaridh's> pick.
```

## What a step contains

A step is done when the builder can write exactly one reasonable thing from it. A test step carries the test's name and its assertions, as code, with the spec's exact values in them. A code step carries the signature, the file and the values the spec pins, and a body only for an algorithm the signature and test do not determine. A verification step carries the command and the output that means it passed. A reference to another task points at its Interfaces block instead of repeating its code.

## Appendices

When the plan is a program of several PRs, the appendices are in `references/program-plan.md`: prototype evidence, alternatives rejected, risks, and the reading list. A single-wave plan carries them as trailing sections when it has any.
