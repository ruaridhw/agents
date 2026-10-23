# AgentsView agent history

## What this source contains

Every recorded agent session on every machine: the user's messages (intent, constraints, corrections), the assistant's rationale, tool calls and their results, and, through the session list, which project, branch and pane a session belonged to. It is the only source that records what was decided while working, as opposed to what was written down afterwards.

Use AgentsView as an evidence source for past agent behaviour: find relevant recorded sessions, inspect the surrounding conversation, and extract decisions, instructions or patterns. A snippet is a lead, not an answer.

## Core workflow

Delegate to a Herdr pane if the harness supports one (see the skill body); otherwise run the bounded probes yourself in order.

1. Translate the ask into a target behaviour and desired evidence: likely projects, agents, time windows, vocabulary.
2. Concept questions ("why did we…", "how did we handle…") start with hybrid search. Exact identifiers (ids, paths, commands, error strings, tool names) start with plain substring search over tool inputs and results; full-text search covers messages only and cannot find identifiers stored only in tool calls:

   ```bash
   agentsview session search "<concept query>" --hybrid --context 2 --json --limit 8
   agentsview session search "<exact string>" --in tool_input,tool_result --json --limit 8
   ```

3. Narrow by recency when the ask implies it: `--since 14d`, `--since 3m` (h/d/w/m/y units; `m` is months, not minutes). Widen or drop `--since` if results are thin.
4. Triage from the inline `context_before`/`context_after` in the results. Every hit, in every mode, carries an `ordinal_range` conversation-unit span (`[start, end]`; a run of assistant messages when end > start) with `ordinal` as the anchor message; centre the window on the anchor. Deep-dive only the strongest candidates:

   ```bash
   agentsview session messages <session-id> --around <ordinal> --before 8 --after 8 --role user,assistant --json
   ```

5. Give the search a mechanical budget: 4-6 probes, top 2-4 sessions, one window per session, then stop and report.
6. Answer from evidence, citing session ids and ordinals. Cite the session plus the hit's `ordinal_range` with the `@ordinal` anchor (e.g. `#12-40 @19`), in every mode, not just the single anchor ordinal.
7. A hit marked `subordinate` (sidechain or subagent/fork content) is supporting evidence only: corroborate it from its parent session (`parent_session_id`) before treating it as a decision or instruction.

## Mode fallbacks

- "semantic search not available" (HTTP 501): embeddings are not set up on this archive. Fall back to full-text probes; several short queries with synonyms beat one long phrase:

  ```bash
  agentsview session search "<two or three words>" --fts --json --limit 8
  ```

- "temporarily unavailable" (HTTP 503): the embeddings endpoint is down. Retry once; if it persists, say so and continue with full-text search. Do not silently downgrade: the reader should know their embeddings are broken.

## Reconstructing a decision

1. Find the earliest substantive mention: hybrid query for the decision's subject with `--scope top` (delegated sessions echo their parent's instructions and bury the conversation where the decision was made), starting `--since 3m` and widening (6m, 1y, none) until the origin appears.
2. Walk forward from the origin with message windows. User messages carry intent and constraints; assistant messages carry rationale, options considered and trade-offs.
3. Watch for durable artefacts referenced in the conversation (spec or plan documents, ADRs, pull request descriptions) and read those files if they still exist.
4. Produce a decision record: what was decided, when, by whom, the stated reasons, alternatives that were rejected, and citations (`session-id` plus ordinals) for each claim.

## Rationalization table

| Rationalization | Reality |
| --- | --- |
| "One good snippet is enough." | Snippets are leads. Inspect a window before extracting a pattern. |
| "A longer query is more semantic." | Hybrid works best with a focused phrase; full-text works best with 2-3 word probes. |
| "Full-text is best for exact identifiers." | Full-text searches messages only. Use plain search with `--in tool_input,tool_result` for ids, paths, commands, errors and tool names. |
| "This current session mentions it, so it counts." | Down-rank active-session echoes; historical evidence needs older sessions. |
| "A subordinate hit settles it." | Sidechain or subagent hits restate delegated work; confirm against the parent session before citing. |
| "Keep searching until certain." | Return a bounded, evidence-backed pass and list follow-ups. |

## Output shape

```markdown
## Searches
- `query` (mode) -> why it was useful or not

## Strong Matches
- `<session-id>` (`project`, `agent`, ordinals N-M): finding and evidence

## Synthesis
- Decision/pattern grounded in the matches, with citations

## Gaps / Follow-ups
- What was not found and the next narrower probe
```
