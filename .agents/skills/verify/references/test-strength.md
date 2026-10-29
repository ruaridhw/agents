# Heavy pre-merge test-strength sweep

Read during a heavy pre-merge or full-stack end-to-end review. This checks whether tests reject plausible breaks and whether invariants hold over generated inputs. It supplements live API/browser evidence; it does not replace it or run inside every red-green cycle.

## Select and run

1. Pin the reviewed base and head, then map changed domain calculations, parsers/codecs, authorization boundaries, billing/quotas and state transitions to their tests. Read `.agents/review.md` for mandatory surface checks and the repo's existing tool configuration. Record selected invariants, test seams, commands, scope and a time/case budget before running.
2. Run scoped mutation checks following `verify/SKILL.md`'s **Diff-scoped mutation proof** protocol. Mutate changed logic while allowing any relevant tests to kill it; restricting mutations to the diff does not mean restricting tests to newly added files. Where a tool cannot target changed lines, use the smallest enclosing module/function and report the broader scope. Without a runner, use targeted manual mutants for the selected invariants and label the narrower evidence.
3. Run the configured property/fuzz suites for those surfaces. For a changed invariant with no existing suite, add a focused property test only when edits are authorized and there is a practical existing test seam; otherwise record the gap and proposed test. Choose an independent oracle: round-trip, idempotence, conservation, isolation, valid state transitions, or comparison with a trusted reference. Generated inputs alone are not a property, and recomputing the implementation's answer is not an oracle.
4. Include boundary, invalid and adversarial inputs, not just typical valid data. Use reproducible seeds and a bounded run profile; record seed, case count, time budget and generator constraints. Replay and shrink a failing input, then retain the smallest counterexample as a regression case when edits are authorized. A passing generated sample proves only the exercised cases, not all possible inputs.
5. Triage every surviving mutant and falsified property. A demonstrated protection gap or contract violation is an Act-on finding in `review` and a failure to close in an end-to-end review. Equivalent mutants and mutations outside the contract need explicit justification, not assertions added solely to kill them. Classify tool/harness failures separately and mark unresolved mutants, timeouts, missing tools or exhausted budgets blocked/limited, never passed. A repository's explicit hard gate still applies.
6. After authorized fixes, rerun the targeted checks and affected regression suites. Verify mutation restoration and the final diff. Record remaining gaps in the review matrix and report.

## Evidence to return

- Base/head and selected surfaces/invariants; checks not applicable and why.
- Commands, test selection, mutation scope and budget; killed, surviving, untested, timed-out and invalid/error outcomes, with survivor dispositions.
- Property oracle and generator constraints; seed, cases, shrunk counterexamples and regression paths.
- Restoration check, reruns, real findings and honest limitations. Do not claim all mutants were killed from one manually flipped guard.
