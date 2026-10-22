---
name: review
description: "Review a branch, a PR or work in progress with other eyes: two axes (Standards and Spec), an adversarial second-family pass in a reviewer pane, the receiving-side rules, then a prose pass, all folded into one ranked list that ends with a ready-to-merge verdict. Use when reviewing a branch or PR, before merging, or when asked to review since a fixed point."
upstream:
  - repo: mattpocock
    path: skills/engineering/code-review/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: superpowers
    path: skills/requesting-code-review/SKILL.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: superpowers
    path: skills/requesting-code-review/code-reviewer.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: superpowers
    path: skills/receiving-code-review/SKILL.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: pstack
    path: pstack/skills/interrogate/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/interrogate/references/reviewer-prompt.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/interrogate/references/rubric.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/interrogate/references/code-quality-review.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/interrogate/references/lead-judgment.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/no-comments/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
---

# review

`review` is other eyes. `verify` is the evidence you gather on your own work; a review is what a context that did not write the code can see. The two are separate passes and the same session can run both, but an author reading their own diff is `verify`, not this.

The review file goes in `.scratch/reviews/`, which is gitignored and never cleaned by a skill. Its one job is to end with a single verdict line.

## 1. Pin the fixed point

Whatever Ruaridh named is the fixed point (a commit SHA, branch name, tag, the default branch, `HEAD~5`). If he did not name one, ask.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff fails here, not inside two parallel reviewers.

## 2. Identify the spec source

Look for the originating spec, in this order:

1. The ticket or PR reference in the commit messages or the branch, fetched per `.agents/tracker.md`.
2. A path Ruaridh passed as an argument.
3. A spec file under `.scratch/specs/` matching the branch name or the feature.
4. If nothing is found, ask where the spec is. If there is none, the Spec axis is skipped and the report says "no spec available".

The spec is a vision document. It says what the software must do; it does not enumerate every input, environment or condition the software will meet. For behaviour the spec is silent on, judge by what a reasonable person using this software would expect: that expectation is a requirement, and silence is not permission. Grade such a finding by its effect on that person, not by whether the spec names the trigger.

## 3. Identify the standards sources

**`.agents/review.md` first.** When the repo has it, it names, per surface (a path pattern), the checks that must run on every review of a diff touching that surface and the rules that are hard violations there. Match the diff's files against its surfaces, run the named checks (a skill by path, a script, a lint) before the Standards axis, and carry their findings into step 7 as Act-on findings; the file's rules join the standards sources below as documented repo rules. A missing file means no mandatory per-surface checks.

Search the repo for every file that documents how code should be written. When `CODING_STANDARDS.md` or `CONTRIBUTING.md` exists, it must be on the list. `.agents/` files count where they carry rules (a build loop's commit rules, a tracker's comment rules), and a documented `AGENTS.md` rule is a standard.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

## 4. Run the two axes

Both axes run as **parallel reviewers in Herdr panes** so they don't pollute each other's context, then this skill aggregates their findings. Spawning is `herdr`'s: one named tab for the review, panes inside it, a worker brief, and the two-file summary and raw paths. Use the `reviewer` role for the Standards axis; the `cheap` role takes the Spec axis when the spec is small enough to hand over whole, otherwise `reviewer` too. Never invent a model id.

**Standards reviewer** gets, in its brief: the full diff command and the commit list; the list of standards-source files found in step 3, **plus the smell baseline from step 3 pasted in full** (the pane has no other access to it); and this ask:

> Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words.

**Spec reviewer** gets: the diff command and commit list; the path or fetched contents of the spec; and this ask:

> Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words.

If the spec is missing, skip the Spec reviewer and note it in the final report.

## 5. The adversarial pass

The axes ask whether the change does what the repo asks and what the spec asks. The adversarial pass asks what is wrong with it that neither question catches, and its signal comes from a different model family, not from assigned personas.

Before spawning, state the intent in one clear paragraph, from Ruaridh's ask, the commit messages, the PR body if there is one, and the code. If the intent is unclear, ask before proceeding. The reviewers are told to challenge the execution and not the intent.

Spawn one reviewer per configured reviewer entry in `~/.config/agents/models.toml` (usually one). Roles, not model ids, and if the role's model is unavailable, say so and stop rather than substituting a weaker one. Each pane is **read-only**: do not let it mutate the checkout, the index, HEAD or branch state, and tell it so in the brief.

Fill `references/interrogate/reviewer-prompt.md` with the stated intent, the diff or file contents, the rubric from `references/interrogate/rubric.md` and the code-quality lens from `references/interrogate/code-quality-review.md`. Add the house rules from `references/reviewer-brief.md`: read-only, the spec is a vision document, "Declined to judge" before the verdict, and no subagents of its own.

As the findings come back, build one picture. Merge findings that describe the same issue differently and note which reviewer raised each one. A finding two reviewers raised independently is the highest signal; a lone finding is read but weighed accordingly. Note disagreements: where one reviewer flags something and another says the opposite, that is context for the verdict.

## 6. Lead judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator. `references/interrogate/lead-judgment.md` holds the framework: nitpick gravity, hypothetical against actual, premature-abstraction warnings, "I would have done it differently", missing-context signals, and when reviewers are right.

Put every finding, from both axes and the adversarial pass, in one of these buckets, with the reviewer(s) that raised it and a one-line rationale:

- **Act on.** Real issues affecting correctness, security, or maintainability given the actual goals. They would block a real PR.
- **Consider.** Legitimate, but you are not sure they outweigh the cost of addressing them now. Worth Ruaridh's attention.
- **Noted.** Technically valid but not actionable. Context-dependent, premature optimization, or low-impact at this stage.
- **Dismissed.** Wrong, nitpicky, or missing context, with a brief reason.

Do **not** keep the axes separate in the final list. The separation was there so neither masked the other while the findings were being gathered; the ranked list is where they meet, ordered by effect. Rank by what a reasonable person using this software gets if the finding ships, not by which axis or reviewer produced it.

The one exception to ranking: a finding from the Standards axis that cites a documented repo rule is a hard violation unless a documented rule contradicts it, so it ranks with the Act-on findings rather than disappearing among the smells.

## 7. The one ranked list

Write the review to `.scratch/reviews/<YYYY-MM-DD>-<slug>.md`. Its shape:

```markdown
## Intent
> <the paragraph from step 5, when there was an adversarial pass>

## Reviewers
- <role> (<model>): <N findings>
- ...

## Act on
1. <finding>, raised by <reviewer>. Why it matters.
2. ...

## Consider
...

## Noted
...

## Dismissed
...

## Agreement map
<where reviewers agreed and diverged, and what that pattern says. One short paragraph.>

ready to merge: <yes | no | with fixes>
```

The file ends with exactly one of `ready to merge: yes`, `ready to merge: no` or `ready to merge: with fixes`, on its own last line, and nothing after it:

- `no` when any Act-on finding is still open. A blocking bug is a no however clean the rest is.
- `with fixes` when nothing blocks but at least one Consider finding should be fixed before merge. Name the fixes in the list; the verdict line does not enumerate them.
- `yes` when everything actionable is Noted or Dismissed, and the prose pass below is done.

An author who disagrees with a `no` argues it in the findings, not by changing the line. A review file without the line is not finished.

## 8. The prose pass

Last, not first: the comment pass over the code, then the prose pass over the review file and the PR text.

**Comments.** Read `references/no-comments.md` and run the pass. Working comments explain a constraint the code cannot express; everything else is either dead (delete it), a workaround (fix the root cause in scope, or report it open), or a comment standing in for structure (offer the cheapest type, runtime, test or CI check that enforces the constraint instead, then delete it). Restore a deleted comment only with an exact exception and scoped proof. Where the upstream pass would ask `how` or `why` about a thin `do not remove`, read the call sites and the history here instead; where it would run `architect` for a shape, that is `arch`.

**Prose.** Read `<skills dir>/technical-writing/references/unslop.md` and apply its stable-id rules to the review file and to the PR text this pass produces. That one file is the whole catalog for the repo: this skill keeps no copy of it. Commit bodies and chat are out of scope. The rule numbers are cited by other skills, so a gap in the numbering is deliberate.

## 9. Receiving a review

The rules for the author are in `references/receiving.md`, kept whole from superpowers. The parts that decide most reviews:

- **No performative agreement.** "You're absolutely right", "great point", thanks: none of it. Restate the technical requirement or just fix it.
- **Verify before implementing.** Check every suggestion against this codebase before acting on it. If an item is unclear, stop and ask about all unclear items before implementing any of them; partial understanding produces the wrong implementation.
- **Push back with reasons.** A reviewer working from a diff lacks context. Say what the code actually does, cite the test that proves it, ask a specific question. Technical correctness over social comfort.
- **YAGNI check.** When a reviewer asks for a "proper" version of something nothing calls, check for callers first and say what the search found.
- **Order the work.** Clarify everything unclear first, then blocking issues, then simple fixes, then complex ones. Test each fix; verify no regressions. Never batch-apply untested.
- **Reply in the thread** on the tracker: an inline thread gets an inline reply, per `.agents/tracker.md` (GitHub: the pull-request review-comment replies endpoint, never a new top-level comment).
- **Correct your own pushback** factually if you were wrong, in one line, then move on.

A reviewer's verdict is advice. The author decides what to fix, chains `verify` on the fixes, and says what they declined and why.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll just review the diff myself instead of spawning a reviewer" | You are the author here. Reading your own diff burns the context you need to drive the work, and it is `verify`, not `review`. |
| "The reviewer needs my whole session history to understand the change" | Hand it precisely crafted context, never your session's history. That keeps it on the work product, not your thought process. |
| "It's a simple change, review is overkill" | Never skip review because it is simple. Small diffs are where context is missing and where the author is most confident. |
| "Green CI is the review" | CI answers whether the checks pass, not whether the change is right. |
| "The reviewer said it, so it must be true" | A reviewer working from a diff lacks context, and a third of its points re-ask settled decisions. Verify each one. |
| "I'll note the Important findings for later" | Important findings are fixed before merge, or declared with a reason. Critical ones are fixed now. |
| "The review file can end with a summary paragraph" | It ends with the verdict line, exactly one of the three. |
