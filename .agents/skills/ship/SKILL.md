---
name: ship
description: "Land a stack of reviewed PRs: drive each to READY through babysit, merge bottom-up with the merge-async recipe, confirm each merge with git patch-id, run each ticket's proof of landing and close it with evidence. Ruaridh invokes this skill and the invocation is the authorization. Use when Ruaridh says to ship, land the stack, or merge it."
disable-model-invocation: true
upstream:
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/shipping.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/poteto-mode/playbooks/babysit.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
---

# ship

**You own what lands. Verify each PR independently, land only the verified run from the root, then keep your hands off the stack.**

Ruaridh invokes this skill. That invocation, for that stack, is the authorization the merge needs; nothing else is. A yes for one PR is not a yes for the stack, and a yes relayed from another pane is not a yes at all (`ruaridh-mode`). When the invocation is ambiguous about which stack, ask before touching anything.

The merge itself is the `pr` recipe in `.agents/skills/pr/references/merge.md`, and the gating rule is `ruaridh-mode` non-negotiable 6 (checks and merges are separate commands, read the check before the next step). This skill does not restate either: it says when, and in what order.

## 1. Resolve the stack and drive it to READY

List the stack bottom-up: the lowest unmerged PR and each PR whose base is the one below it. If the chain was built by retargeting bases by hand, it is not a registered stack, and the top one would merge only into its base; say so and merge bottom-up by hand per `pr`.

Then `.agents/skills/babysit/SKILL.md` in `drive` mode, one PR at a time, lowest first. `ship` never fixes code itself: a failing check, a conflict or a review thread is `babysit`'s to classify and fix, and a conflict or stale base that needs a rebase comes back here as a report for the owner.

## 2. Verify each PR independently before it lands

Green CI and an approving review are inputs, not verdicts: neither runs the change the way a user would. The verdict for a PR here is `verify`'s evidence block on its head, plus whatever the repo's `.agents/prove-landed.md` says proves the behaviour. A PR without that evidence waits; `babysit` to READY is not the same as proof.

Only a verdict from an agent that did not write the code counts, because an author checks what they meant to build. When the evidence on a PR is the author's own summary, `verify` that claim against the diff or hand it to `review` before trusting it.

## 3. Land only the contiguous verified run rooted at the bottom

Walk up from the lowest unmerged PR and stop at the first one without its verdict. The PRs below it are the run, and the top one is the ceiling. A verified PR above an unverified one waits, because it cannot land without the code below it. One whose branch neither holds nor needs that code can move onto the default branch and land on its own, but it needs a fresh verdict first, because its old one ran with that code beneath it and the default branch does not have it.

## 4. Re-check that the verdicts still describe the code

A verdict covers a patch, and a chain rebase moves every PR above it to a new SHA without failing any check. Compare `git patch-id` at the verdict SHA with the current head before trusting an older verdict.

When the patches differ only in tests, docs or lint config, the result stands if what it ran builds the same at both SHAs apart from noise. Noise is a difference that also shows up between two builds of the verdict SHA, or an embedded commit SHA. Report each kind of noise with its files, so a reader can check the call. The change itself still gets fresh checks and a review, because the old verdict never saw it. A lane with no build output, such as a dev server, cannot show this, so rerun it, and re-verify anything else that drifted.

## 5. Land bottom-up, one PR at a time

Always merge the run's lowest unmerged PR, by the recipe in `pr/references/merge.md`: merge-async, poll the uuid until `merged`, then read the PR back. A merge command can report success when it only queued the PR, and a requested auto-merge is not a merge. A landed PR reads merged with the default branch as its base, not its parent's branch.

Then adopt the remote heads before touching the child: `git fetch` and, on a branch with no local-only commits, `git reset --hard <remote>/<branch>`. **That is the one sanctioned reset of a branch you do not own**, and it is sanctioned here because the merge already landed and the only thing being discarded is a local copy of the old base. Never cascade with `git rebase --onto` using a parent SHA from your local copy. Never retarget a child by hand when GitHub's stacked-PR support is retargeting it: GitHub moves the child to the default branch and re-runs its checks against the new base, and a hand retarget fights that.

Arm auto-merge only on a PR whose verdict covers its current head, because it lands whatever head is ready. Merge the next PR once its checks pass on the adopted head and step 4's patch-id rule says its verdict survives.

## 6. Leave the stack alone while it lands

Step 5's adoption of the next PR's head is the only change to a branch or base, because a merge lands whatever its branch and base hold at that moment, verdict or not. Watch the run with `babysit`'s queued watcher (`scripts/watch-pr/watch-pr --queued-stack --stack-prs <bottom,to,top>` under `/loop`) until it reports `COMPLETE` at the ceiling, then read each PR back. A base that moves to the default branch when its parent merges is expected, not damage to repair. If a merge stalls, find out why before you change anything.

## 7. Stop at the ceiling

Extending the run takes new verdicts, so it is a new pass through steps 1 to 4. Merging one more PR because it is "obviously ready" is how an unverified commit lands.

## 8. Prove each ticket landed, then close it

Merged and done are separate states. For each ticket in the stack, run its proof of landing, `.agents/prove-landed.md` (default: the tests on the merged sha). Mark the ticket `merged` on the merge, and `done` only when that proof passes, with the evidence the tracker profile asks for: what was observed, the commit, the PR, the test command. `kata` and GitHub profiles are in `conventions/`; `.agents/tracker.md` owns the commands.

**Ask first when the proof writes to a client remote.** A read-only read-back needs no permission; a run that pushes, promotes, deploys or comments somewhere a client can see is a write, and it needs Ruaridh's explicit yes in this session, per the Inbox convention when he is away. A proof that cannot run without that write leaves the ticket `merged` with a comment saying what is waiting, never `done`.

Close one ticket at a time, never in a batch, as soon as its Done-when is observed.

## Reply

The verified run and its ceiling, each PR's verdict and who produced it, what landed and how you confirmed it, and what the next gap needs. Then the tickets closed, each with its evidence, and the ones left `merged` with the reason.
