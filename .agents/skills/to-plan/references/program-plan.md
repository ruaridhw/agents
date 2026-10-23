# Program plan

For a program of several PRs, where the shape is known and the work is long: the plan is a checklist the builders run box by box and Ruaridh audits from the evidence. **You own the plan, not the code. The plan is the deliverable. Do not implement.**

This is the shape a plan takes when it spans more than one PR. A single-wave plan stays in `references/plan-template.md`.

## Steps

1. When the change is one or two files with an obvious approach, skip the plan. Say so and stop.
2. Settle open questions by prototype before you write. Run `prototype` for each. Keep the branch, the sha, and the screenshots for Appendix A. Ask Ruaridh only about a product or preference call that no run can settle. Give options, the recommended one first. Ask per the Inbox convention when he is away.
3. Explore in Herdr panes (`herdr`, cheap role, one per area), each with an explicit brief. Pick each pane's reasoning level and fast or standard speed for the job from the role it runs under. Each returns file pointers, conventions, test commands, and entry points. No inlined dumps.
4. Copy the skeleton below into the plan file and fill every placeholder. Unless Ruaridh names a path, write the file under `.scratch/plans/`. Keep every heading and every sub-block in the order shown. One section per PR. One PR is one change with its own evidence. Name the execution mode in **How to read this**.
5. Write it under the prose rules in the skill: the body is one how-to, how-to mode throughout, appendices hold explanation and reference. Each heading states the task or the finding. No long dashes. No mid-sentence colons.
6. Hand back. Post the plan path and what the prototypes proved and what stays unproven, then stop. Execution starts on Ruaridh's explicit go, in the mode he picks.

**Verification.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. That sentence is the verification rule, and every PR section carries it. This reference owns the unit box. The live and perf boxes are `verify`'s: the PR's section names the surface to drive, the scenario and the metric, and `verify` fills in how they are checked. A PR that changes no interaction still names its unit evidence.

```markdown
# <Program> plan

<Under ten lines. What changes, for whom, the rule the program enforces, and the ticket refs in order.>

## How to read this

One box is one unit of work. Every box names the evidence that checks it. A nested box is a sub-step of the box above it. Check a box only when its evidence exists, a file, a log line, a screenshot, a test run, or a SHA. The body is a how-to. The appendices explain and record.

The program runs `implement` in the mode Ruaridh picked, and each PR lands by `pr`. <Who merges, and which ticket refs are the items that stop at merge-ready.>

Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

## Program checklist

### Arm the program

- [ ] State the protocol and this plan to Ruaridh, then stop. Start execution only on his explicit go.
- [ ] Read these at program start, and re-read them at every tick.
  - [ ] `.agents/build-loop.md`
  - [ ] `.agents/prove-landed.md`
  - [ ] `.agents/deploy.md`
  - [ ] `.agents/design-review.md`
  - [ ] `.agents/domain.md`
  - [ ] `.agents/tracker.md`
- [ ] On his go, arm the audit tick as `/loop 1h` with the tick prompt below. Never leave the cadence to memory.
- [ ] Use this tick prompt, verbatim. "Re-read the repo's convention files and the execution mode. Audit the operation against them and fix drift in this tick. Probe every active builder pane and judge progress by side effects only. Stand down a stuck pane and dispatch its replacement now. Then post a short status message to Ruaridh in chat only when the audit found a tracked change that no earlier status message reported, such as a PR opened, a code-ready head, a review round launched or closed, a verdict, a merge, a stuck agent and the action taken, a blocker added or cleared, or a decision only he can make. Name every such change and nothing else. Do not repeat a table, the merged list, or an unchanged blocker. If the audit found none, end the turn with no reply text. Either way, log this tick's row in your decision trail. The row names the items reported, or none."
- [ ] On his hold or stand-down, send every builder a zero-writes order at once.

### Spawn builders

- [ ] Spawn one builder per PR in a Herdr pane (`herdr`, builder role, `--lean`), with the full lifecycle this plan names.
- [ ] Follow this dependency graph. Start dependent work only after its parent merges, or base it on the parent branch when the stack calls for it.
  - [ ] <ticket ref> and <ticket ref> are independent and first. Both branch from the default branch.
  - [ ] <ticket ref> after <ticket ref>.
- [ ] Hold the file boundaries. <ticket ref or class> touches only `<glob>`.
- [ ] Hold the review gate. <ticket refs> change an interaction. They wait for Ruaridh's review under `.agents/design-review.md` before merge.

### PR mechanics, for every PR

- [ ] Land it by `pr`: one PR per ticket, on the stack base, ready rather than draft.
- [ ] Run the repo's lint and typecheck once before the PR-facing push. Push with hooks on.
- [ ] Comment on the ticket with what changed and its evidence, per `.agents/tracker.md`.

### Verdict and merge, for every PR

- [ ] One reviewer-role pass (`~/.config/agents/models.toml`) at the code-ready head. Another runs only for new behavior, a redesign, or a large new diff. A rebase, a merge-conflict resolution, or a minor fix gets a single verifier at the new head.
- [ ] Clean only when every finding is fixed or ruled out with a reason. Findings go back to the owning builder. A new head gets a fresh verdict.
- [ ] Merge by `pr`, with Ruaridh's yes.

## <Task as a verb phrase> (<ticket ref>)

**Depends on.** <ticket ref, or None.>

**Files.**

- [ ] Edit `<path>`.
- [ ] Create `<path>`.
- [ ] Delete `<path>`.

**Build.**

- [ ] <One change. Name the symbol and the file.>

**You see.**

- [ ] <One observable result, with the exact log line or screen state.>

**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] <Test file and the case it gains.> Run `<command>`.

**Verify, live and perf.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] Surface. <What `verify` drives to reach the change.>
- [ ] Scenario. <The input and the behavior a person expects.>
- [ ] Metric. <What is measured for the perf box, and where.>

**Review gate.** The design review under `.agents/design-review.md` before merge, or `None. <ticket ref> changes no interaction.`

- [ ] <What Ruaridh is shown, and where it is saved.>
- [ ] Stop at merge-ready. Wait for his yes.

**Merge.**

- [ ] Reviewer's clean verdict at the exact head SHA.
- [ ] Rebased onto the current default branch after the verdict, patch-id unchanged.
- [ ] <The builder merges its own PR, or the stack lands bottom up.>

## Close the program

- [ ] Every box above is checked with its evidence.
- [ ] Reply to Ruaridh with the report this plan names.

## Appendix A. Prototype evidence

<Each open question a prototype answered, with the branch, the sha, and the artifact links. Each question that stays unproven.>

## Appendix B. Alternatives rejected

<Each approach weighed and why it lost.>

## Appendix C. Risks

<Each risk with the PR it lands in and what the builder watches.>

## Appendix D. Links and reading list

<Docs to read before editing. Which PRs get which skills. The decision trail for the program.>
```

## Appendices

Appendix A records what the prototypes proved, with the branch, the sha and the artifact. Appendix B is the alternatives weighed, and why each lost. Appendix C is the risks, each with the PR it lands in. Appendix D is the reading list and the decision trail; `verify` owns the trail's shape once curated, until then `implement`'s ledger carries the `Ruling:` lines.
