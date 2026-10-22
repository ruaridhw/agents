---
name: verify
description: "Evidence before any completion claim: run the command in this message, read its output, label every claim verified, inferred or assumed, and prove the one fact the work is safe because of. Use when about to say work is done, fixed, passing or landed, before committing or opening a PR, when reporting a number, or when a worker reports success."
upstream:
  - repo: superpowers
    path: skills/verification-before-completion/SKILL.md
    sha: bb92a77741419a4ab5f06e711a283343f1ada0c3
  - repo: pstack
    path: pstack/skills/principle-prove-it-works/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/blast-radius/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/benchmark-checklist/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/show-me-your-work/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/show-me-your-work/references/decision-log-template.tsv
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/show-me-your-work/scripts/log.sh
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: mattpocock
    path: skills/deprecated/qa/SKILL.md
    sha: f958fa17c1b62c3f7be38fc09512669acf6b64fc
  - repo: kit
    path: template/.agents/skills/kit/prove-prompt-landed/SKILL.md
    sha: 1d552609f50102184079aa622beb727e38b02341
---

# verify

`verify` is self-evidence: what you do before any claim that work is complete, fixed, passing, landed or fast. It is not other eyes; a second opinion is `review`'s job, and this skill says so at the end.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

Run each check as its own command and read its exit before the next. Never chain a check, a commit and a push with `;`: a chained run reports the exit of the last command, not the check.

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Worker completed | VCS diff shows changes | The worker reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit, push or open a PR without verification
- Trusting a worker's success report
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence is not evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter is not compiler |
| "The worker said success" | Verify independently |
| "I'm tired" | Exhaustion is not an excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Worker delegation:**
```
✅ Worker reports success → Check the diff → Verify the changes → Report actual state
❌ Trust the worker's report
```

## When To Apply

**ALWAYS before:**
- ANY variation of success or completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, opening a PR, finishing a task
- Moving to the next task
- Delegating to another agent

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion or correctness

## Label every claim

A completion claim carries one of three labels, and an unlabelled one is a red flag:

- **verified**: you ran a command or read the artifact in this session, and the evidence is above it.
- **inferred**: it follows from what you verified, by reasoning you can state. Say the reasoning.
- **assumed**: you did not check, and you know it. Say what would check it.

Tests passing is `verified`. "That also fixes the other caller" is `inferred`. "Nobody else imports this" is `assumed` until a search says otherwise. A report to Ruaridh, a ticket comment and a PR body all use the labels, because a reader who sees one can weigh it.

The repo's own definition of done is `.agents/prove-landed.md`; the default is the tests on the merged sha, in the place the ticket names. A missing file means that default. Run it before the word "done", not before the word "merged": merging and proving are separate states.

## Prove it on the real thing

Verify every task output by checking the real thing directly. Do not infer from proxies, self-reports, or "it compiles".

**Why:** Unverified work has unknown correctness. Indirect verification (file mtimes, output freshness, an agent's self-report, cached screenshots) feels cheaper than direct observation. Acting on a wrong inference costs far more than checking the source.

Check the real thing, not a proxy:

- Check process liveness directly, not through derived state
- Read the actual value, not a cached or derived representation
- When verification fails, suspect the observation method before suspecting the system

**Script the check when you can.** The strongest proof is a deterministic script that re-runs the same comparison, not a one-time eyeball. Write the script, run it, and keep its output as an artifact a reviewer can re-run instead of trusting your word. Keep the artifact visible for Ruaridh and point at it by path; commit it only for large or complex work where the trail has to be auditable later, such as a big port or migration.

## The proof ladder

A writeup that sounds right is worthless, and it reads as convincing whether or not it is true. So do not hand back the writeup alone. Find the one or two facts the whole claim depends on and get each of them as far down this ladder as is cheap. Say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line: a real `file:line`, or the library's own source.
3. You showed the bad case cannot happen: you walked the failure step by step and it does not reach.
4. You ran it: a script or test that calls the real code and fails loud if you are wrong.
5. You reproduced it in the running app.

Most changes that look risky are safe because of a single fact ("this call only drops already-dead cache entries and does nothing else"). Find that fact, prove it, and most of the risk clears at once. Steps 4 and 5 are the rungs a claim of "verified" needs; a rung 2 answer is at best `inferred`. The steps for a full blast-radius pass, and the writeup shape it hands back, are in `references/blast-radius.md`.

## Any number you report

A measured number is a claim with its own checklist, and a benchmark that was not vetted is a number that will be re-litigated. Whenever you report a speedup, a regression, a latency, a threshold or a comparison between two options, read `references/benchmark-checklist.md` in full and answer each question with evidence from a run, not a guess about the code.

Three of its rules decide most cases:

- **Name the limiter.** A result past a limit measured something other than the work: a cache, a no-op, a bug. If a change did not move the number, find the limiter before calling the change useless.
- **Tune both sides.** If one side ran on defaults, you compared configurations, not implementations.
- **Did it even happen?** Confirm the timed region did the work: the request reached the server, the rows were written, the result was used.

A ballpark Ruaridh asked for is one run, still with the error count and the "did it happen" check, and you say it is one run. A choice between options is never a ballpark.

## Landed is not running

Three states exist and only the third counts: the change is written, it is pushed, and it is running. Every response you get covers the second and says nothing about the third.

Compare bytes, not status codes. A push counts as finished only when you have read the live artefact back and held it against what you meant, character for character. A platform can rewrite what it saves, and "it worked" is a fact about the call.

The number of records is not a comparison. Five wrong rows and five right rows are counted the same way. Read the content.

Some platforms need two calls for one change: the first creates a draft, the second makes it live, and only the first answers. A half-applied change looks finished from every response.

On a fresh checkout there may be nothing to compare against. Say you are establishing a baseline; do not report that nothing drifted when you have no data.

The repo's own read-back procedure is `.agents/prove-landed.md`, and its default is the tests on the merged sha. When it writes to a remote that is not yours, ask before running it: a read-only proof needs no permission, a write does.

## The decision trail

Long, unattended and multi-phase runs keep a reviewable trail: one TSV row per decision, appended by `scripts/log.sh`, at `.scratch/decisions/<ticket>.tsv`. It is part of every `implement` run, it stays uncommitted, and its rows are surfaced on the ticket as one comment per run or pause.

`references/decision-trail.md` owns the columns, when a row is worth writing, the `start` row rule, the append-only rule and the exact ticket-comment format. `review` and `handoff` read the trail; nothing restates its columns.

## When verification finds a bug

A problem found while verifying is a finding, not an aside in the summary. Capture it conversationally: at most two or three short questions (what you expected against what happened, the steps that reproduce it, whether it is consistent or intermittent), no over-interviewing. Then decide scope: one behaviour wrong in one place is one ticket; separable concerns that could be worked in parallel are a breakdown, filed in dependency order.

File it with `to-tickets` in the fix-ticket shape, which owns the body: the behaviour in the repo's domain language, reproduction steps, and no file paths or line numbers, because those go stale. Do not ask Ruaridh to review the ticket first; file it and share the refs.

## Second eyes

`verify` is what you do to your own work. It cannot give you a fresh perspective on it, and a claim you are too close to is exactly the one you label `inferred` when it should be `verified`. Hand the branch to `review` when the work is about to merge, and to the `reviewer` role when the claim is load-bearing and you cannot run it yourself.

## Rationalizations about the trail

| Excuse | Reality |
|--------|---------|
| "The log is bureaucracy, the summary says it all" | The summary is one run's narrative; the trail is what a reviewer checks it against. |
| "I'll write the rows at the end" | Rows written at the end record what you remember, not what happened. Append as you go. |
| "This decision is obvious, nobody would ask" | Then the row is one line. The test is whether a reader could disagree, not whether you did. |
| "I fixed the log entry" | Append-only. A wrong row is superseded by a new one, never edited. |
