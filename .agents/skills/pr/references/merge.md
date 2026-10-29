# Merge recipe

1. **Read the checks** in their own command: `gh pr checks <n>`. Anything red or pending: stop. Never chain checks and merge with `;`. Confirm the base first (`gh pr view <n> --json baseRefName`): merging into the wrong base is expensive to undo.
2. **Stack order**: merge the lowest unmerged PR first.
3. **Merge**:
   - Registered GitHub stack (or `gh pr merge` refuses with "part of a stack"):
     ```bash
     gh api -X PUT repos/<o>/<r>/pulls/<n>/merge-async -f merge_method=rebase
     gh api repos/<o>/<r>/pulls/<n>/merge-async/<uuid> --jq .status   # pending -> merged
     ```
     The uuid may be nested at `.details.uuid`. History is linear: use `merge_method=rebase`, or `squash` where the repo allows no rebase merge, never `merge`. Check which the repo allows with `gh api repos/<o>/<r> --jq '{rebase: .allow_rebase_merge, squash: .allow_squash_merge}'`. A rebase or squash merge gives the parent's commits new shas on the default branch, so children are rewritten: step 5 adopts them.
   - Ordinary PR: `gh pr merge <n> --rebase` (or `--squash`).
   - A chain made by retargeting bases by hand is not a registered stack: merging its top merges only into its base branch. Merge bottom up, or retarget the top to the default branch (its branch contains every parent) and merge that.
4. **After each merge**: `gh pr view <n> --json state,mergeCommit`. Record the resulting sha on the default branch (a rebase merge has no merge commit of its own: use `git log -1 <remote>/<default>` after a fetch).
5. **Adopt remote heads** before touching any child: GitHub retargets children to the default branch and may rewrite them onto it with new shas. With no local-only commits: `git fetch <remote> && git reset --hard <remote>/<child-branch>` (the sanctioned reset of a branch you do not own). Never `git rebase --onto` with a parent sha from your local copy; rebase onto the remote base instead.
6. **Wait for the retargeted child's checks** to re-run against the new base, then repeat from step 1 for it.
7. **Ticket**: label `merged` and comment the PR and merge sha (per `.agents/tracker.md`). `done` waits for proof.
8. **Branches**: before deleting a branch, retarget every open PR based on it; deleting a base closes its PRs. Remove only worktrees you created, after their commits are on the default branch.
