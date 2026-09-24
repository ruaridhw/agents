# Example: five-phase document review build (fictional)

| Phase PR | Work | Why this order |
| --- | --- | --- |
| 1 | Shared schema and reference matcher | All later phases consume this contract. |
| 2 | Several policy rewrites, each on its own builder branch | Coordinator integrates the parallel commits into one phase PR. |
| 3 | Pure row projection and spreadsheet I/O checks | Code tests prove writes without a production spreadsheet. |
| 4 | Approvals, verifier and documentation | Adds the acceptance path before activation. |
| 5 | Publisher integration switch | If this misses the deadline, the preceding policy path still works. |

Each PR bases on the previous one. An isolated QA agent runs synthetic document fixtures against the latest policies and records Run IDs; it does not open the production spreadsheet. A real reported row with an unsettled expected cell is harvested as `expected: null` with an owner, not passed in QA. The human reviews the stack and authorizes deployment from its top; default-branch merges wait for the approved window. The ticket closes only after the promoted output passes post-run comparison.
