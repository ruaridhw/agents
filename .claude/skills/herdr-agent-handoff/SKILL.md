---
name: herdr-agent-handoff
description: Spawn and coordinate sibling, child, or team coding agents in a Herdr runtime using concise summary files plus optional raw logs. Use when the user asks to delegate, parallelize, spawn workers, create sibling/sub-agents, form an agent team with a coordinator, run background agents, or mentions Herdr orchestration; requires HERDR_ENV=1.
---

# Herdr Agent Handoff

Delegate work without importing worker transcripts. Every agent writes a concise summary for ingestion and a raw log for audit/debug.

## Semantics

- **Sibling agent**: peer parallelism; Pi integrates results but the other agent is not subordinate.
- **Sub-agent / child agent**: scoped delegation; Pi remains orchestrator and consumes a bounded two-file handoff.
- **Team**: coordinator plus workers; every agent gets a shared roster naming roles, tasks, summary paths, and raw paths.

## Preconditions

```bash
test "${HERDR_ENV:-}" = 1
herdr --help
herdr agent
herdr tab
herdr pane
```

If `HERDR_ENV` is not `1`, say this needs a Herdr-managed pane and stop. If `HERDR_WORKSPACE_ID` is missing, stop; subagents must be spawned into the caller's workspace, not the focused workspace. The installed `herdr` binary is the syntax authority. Prefer one named tab per handoff invocation, explicit pane IDs, and parsed JSON.

## Single worker

```bash
python3 /home/ruaridh/.agents/skills/herdr-agent-handoff/scripts/spawn_worker.py \
  --name worker-1 \
  --tab-label refactor-api \
  --kind pi \
  --model fireworks/accounts/fireworks/routers/kimi-latest \
  --task "Refactor the FastAPI endpoints."
```

The helper creates one new Herdr tab in the caller's workspace and current cwd, labels it with `--tab-label` (or `--name`), starts the worker in the tab's root pane so there is no unused empty pane, sends the two-file prompt, waits, and prints the summary.

## Lean workers

Pass `--lean` to `spawn_worker.py` for pi workers doing focused implementation or fix rounds. It starts pi with `--no-skills --no-extensions --no-prompt-templates`, cutting the measured first-turn baseline from ~14.3k to ~3.8k tokens — a saving repeated on every turn of the worker's session. The AGENTS.md chain stays loaded, so project safety rules still apply.

When writing a task or brief, cite any skill file the worker needs by exact path (e.g. "Read /path/to/SKILL.md first"). With `--lean` there is no skills index for the worker to discover skills from; exact paths are the only way they get found.

## Team with coordinator

Use when work should be divided or workers should know about each other. Write `team.json`:

```json
{
  "coordinator": {"name": "coord", "model": "openai-codex/gpt-5.6-sol", "task": "Wait for worker summaries, integrate them, and report final outcome."},
  "workers": [
    {"name": "api", "role": "API investigator", "model": "fireworks/accounts/fireworks/routers/kimi-latest", "task": "Inspect FastAPI endpoints only."},
    {"name": "db", "role": "DB investigator", "model": "fireworks/accounts/fireworks/routers/glm-fast-latest", "task": "Inspect SQLAlchemy models only."}
  ]
}
```

Run:

```bash
python3 /home/ruaridh/.agents/skills/herdr-agent-handoff/scripts/spawn_team.py --team-file team.json
```

The helper creates one new Herdr tab in the caller's workspace for the invocation, starts the first team member in the root pane, splits additional team members into panes inside that same tab, writes `.herdr-handoffs/team-*/roster.md`, prompts all agents with that roster, tells the coordinator to integrate worker summaries, waits, and prints summaries. Use top-level `"name"` in `team.json` or `--tab-label` to name the tab; otherwise it defaults to `team-<first-agent>`.

## Model choice

Choose the worker model by task; do not blindly clone the caller's model. Use explicit `model` fields in `team.json` or `--model` for single workers. Two good choices per common use case:

| Use case | First choice | Second choice |
| --- | --- | --- |
| Complex repo editing / high-stakes coding | `openai-codex/gpt-5.6-sol` | `openai-codex/gpt-5.6-terra` |
| Focused implementation / deterministic patching | `fireworks/accounts/fireworks/routers/deepseek-flash-latest` | `openai-codex/gpt-5.6-sol` |
| Large-context reading / synthesis | `fireworks/accounts/fireworks/routers/kimi-latest` | `fireworks/accounts/fireworks/routers/glm-latest` |
| Fast search / summarization / inventory | `fireworks/accounts/fireworks/routers/glm-flash-latest` | `fireworks/accounts/fireworks/routers/kimi-fast-latest` |
| Debugging with tricky reasoning | `openai-codex/gpt-5.6-sol` | `fireworks/accounts/fireworks/routers/deepseek-pro-latest` |
| Parallel worker when caller is already sol | `fireworks/accounts/fireworks/routers/kimi-latest` | `fireworks/accounts/fireworks/routers/glm-fast-latest` |
| Cheap broad exploration before handoff | `fireworks/accounts/fireworks/routers/glm-flash-latest` | `fireworks/accounts/fireworks/routers/deepseek-flash-latest` |
| Coordinator / integration role | `openai-codex/gpt-5.6-sol` | `openai-codex/gpt-5.6-terra` |

Re-check names with `pi --list-models` before spawning if model catalogs may have changed.

## Manual contract

Default topology is one named tab per skill invocation in the caller's workspace. Create the tab once, start the first agent in the tab's root pane, then split only for additional subagents from that root pane so every subagent stays in the same tab and there is no unused empty pane.

```bash
mkdir -p .herdr-handoffs
summary="$(pwd)/.herdr-handoffs/worker-1-summary.md"
raw="$(pwd)/.herdr-handoffs/worker-1-raw.md"
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label refactor-api --no-focus
herdr agent start worker-1 --kind pi --pane <root-pane-id> -- --model fireworks/accounts/fireworks/routers/kimi-latest
herdr agent prompt worker-1 "TASK: <task>

Shell discipline:
- Batch independent probes into one bash call; one pipeline answers what would otherwise take several tool calls.
- Locate with rg first, then read with offset/limit around the hits.
- Read each file once; note the line ranges in your raw log so later steps work from those notes.

Output contract:
- Write detailed reasoning, commands, diffs, errors, and evidence to: $raw
- Write a concise high-level summary to: $summary
- Summary includes: outcome, files changed, verification run, blockers, and whether raw log is needed.
- Do not paste raw log in chat. Final chat only: HANDOFF_WRITTEN $summary $raw" --wait --timeout 1200000
python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).read_text())' "$summary"
```

Read raw logs only when the summary says blocked/uncertain or exact evidence is needed.

## Coordination rules

- Use absolute summary/raw paths so cwd drift cannot lose handoffs.
- Do not rely on focused pane; create a named tab with `--workspace "$HERDR_WORKSPACE_ID"`, keep its root pane ID, and use explicit pane IDs plus unique agent names.
- Start the first agent in the tab root pane; split only for additional agents so the invocation does not leave an empty shell pane.
- For multiple workers, assign non-overlapping tasks, separate handoff paths, and task-appropriate models; keep them in panes within the invocation's tab.
- If `agent prompt` returns `blocked`, inspect `herdr agent get <name>` and `herdr agent read <name> --source recent-unwrapped --lines 120` before sending input.
- Do not close panes/workspaces you did not create unless asked.
