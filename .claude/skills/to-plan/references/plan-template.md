# Plan template

```
# <Feature> plan
Spec: <tracker ref>   Tickets: <refs in order>   Date: <YYYY-MM-DD>

Goal: <one sentence>
Architecture: <two or three sentences>
Tech stack: <key technologies>

## Global constraints
The spec's project-wide requirements, one line each, exact values copied from the spec.
Every task implicitly includes this section.

## Review focus
The few untested inputs or failure modes most likely to bite, most likely first, one line each.
Each line's test is added to the task that owns the code.

## Task N: <component>   (ticket <ref>)
Files: create `<path>` / modify `<path>` / test `<path>`
Interfaces:
  Consumes: <exact signatures from earlier tasks>
  Produces: <exact names, parameters, return types later tasks rely on>
Steps (from build-loop.md):
  - [ ] Write the failing test `<name>` asserting <exact values>
  - [ ] Run `<command>`; expect FAIL with "<message>"
  - [ ] Implement `<signature>` in `<path>` (one line on the approach where the test leaves a choice)
  - [ ] Run `<command>`; expect PASS
  - [ ] Commit: `<gitmoji> <imperative summary>` + why line
Acceptance: cites spec case <name/id>; Done-when of ticket <ref>.

## Execution
Proposed: inline | delegated.
Split (delegated): builder A → tasks 1, 3; builder B → task 2 (parallel); task 4 after 1 merges.
Reason: <one sentence>.
Awaiting pick.
```

A step is done when the builder can write exactly one reasonable thing from it. A test step carries the test name and assertions with the spec's values; a code step carries the signature, file and pinned values, and a body only for an algorithm the signature and test do not determine; a verification step carries the command and the passing output; a reference to another task points at its Interfaces block.
