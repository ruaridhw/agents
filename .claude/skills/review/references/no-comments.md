# The comment pass

Fresh eyes on comments, then act on the accepted findings. Defer to that fresh perspective: the author knows why a comment was written, which is exactly the wrong frame for judging whether it earns its place.

## Scope

Use the files or diff the review covers. Otherwise use the current diff against the base branch, the default branch by default, including the working tree.

## Steps

1. Spawn the comment pass as a read-only reviewer pane in a Herdr pane (`herdr`, `reviewer` role), with the scope and the rule that it may read and propose but not edit. Do not restate its rules in the brief; point it at this reference.
2. Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. A flag on a surprise in our own code stays actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions: correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. Before accepting a thin `IMPORTANT` or `do not remove` kill or keep, read the symbol's call sites and history (`debug` and `research` own the how and why of a symbol). If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. Revert and rerun one rejected report with the failure named. Reject a second, report it open, and fail the pass.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, run `arch` once over the accepted set and the surrounding code. Stop at the sketch: `arch` shapes, step 4 implements.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. Fixing the root cause and redesigning from first principles guide the intent; neither authorises widening the fence or fixing instances outside it. Never bolt on symptom guards.
5. Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. Offer the cheapest in-scope type, runtime, test or CI lint that enforces the constraint, then delete the comment. Ask before encoding when Ruaridh is here, and per the Inbox convention when he is away; an unattended run needs his pre-approval for the encoding. If approved, encode it then delete the comment. Otherwise delete the comment, report the constraint open, and sketch the work it needs.
6. Report the deletion count, restored comments, reruns, the sketch, the fixes, encoding offers, encodings, unenforced constraints, and the other open work.
