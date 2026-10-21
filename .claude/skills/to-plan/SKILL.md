---
name: to-plan
description: Write the implementation plan for a set of published tickets, one task per ticket in dependency order, steps from the repo's build loop, acceptance cited from the spec; then propose inline or delegated execution and wait for Ruaridh's pick. With --map, chart work too big for one session as a map of decision tickets instead. Use after to-tickets, or when asked to "plan this" or "plan the build".
upstream:
  - repo: superpowers
    path: skills/writing-plans/SKILL.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/multi-phase-plan.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: mattpocock
    path: skills/engineering/wayfinder/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
---

# to-plan

Write the decisions the builder cannot make alone: which files, which names and signatures, which tests prove each task, which spec values apply. Nothing else. The plan is not gated, but execution does not start until Ruaridh picks how it runs.

Skip the plan, and say so, when every ticket is small enough to execute directly from its body.

## Steps

1. **Read** the spec issue and its `.scratch/specs/` file, every ticket (body, edges, comments) and the code where they land. Read `.agents/build-loop.md` for the step list (default below). Explore broadly in Herdr panes (`herdr`, cheap role), asking each for file pointers, conventions, test commands and entry points, never dumps.
2. **Settle forks by running something.** If a choice could be settled by a quick throwaway prototype, do that and record the result in the plan; ask Ruaridh only what no run can settle.
3. **Map the files** before tasks: what each created or modified file is responsible for. Focused files with one job; follow the codebase's patterns.
4. **Write `.scratch/plans/<YYYY-MM-DD>-<slug>.md`** in the shape in `references/plan-template.md`: one task per ticket, in dependency order. Each task's steps come from the build loop; each step lets the builder write exactly one reasonable thing. Acceptance cites the spec's cases by name and never invents new ones: a missing case found now is added to the spec issue as a comment and to the `.scratch` spec, then cited.
5. **Review focus**: the handful of inputs or failure modes the spec implies but no task's test exercises that are most likely to bite, each with the test added to the task that owns the code.
6. **Self-review** against the spec: every requirement has a task; no step decides nothing ("handle edge cases", "TBD") and none transcribes a body the signature and test already determine; names and types match across tasks; the plan is not longer than the code it describes.
7. **Propose execution** at the end of the plan and in chat, then wait:
   - **Inline**: you implement every task in this session (`implement` inline mode), then one reviewer-role pass over the branch. Cheapest; right for few, tightly coupled tasks.
   - **Delegated**: builders in Herdr panes, one per task or group, with the split written out (which tasks per builder, which can run in parallel, which wait on a merge). Right for many independent tasks.
   Recommend one, with one sentence of reason from the plan (coupling, count, cost of a shipped mistake). Do not start `implement` until he picks.

## Build loops

From `.agents/build-loop.md`; without it, the default **code** loop: write the failing test → run it (FAIL, with the expected message) → implement → run it (PASS) → commit. A repo may bind another, for example: change the surface → push → prove it landed → run the case → compare with the expected result → commit.

## Map mode (`--map`)

For a foggy effort bigger than one session, where the way to the destination is not visible yet: chart it as a map of decision tickets and resolve them one at a time until a spec can be written. It produces decisions, not deliverables, and hands off to `to-spec`. See `references/map-mode.md`.
