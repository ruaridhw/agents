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

If `HERDR_ENV` is not `1`, say this needs a Herdr-managed pane and stop. The installed `herdr` binary is the syntax authority. Prefer one named tab per handoff invocation, explicit pane IDs, and parsed JSON.

## Single worker

```bash
python3 /home/ruaridh/.agents/skills/herdr-agent-handoff/scripts/spawn_worker.py \
  --name worker-1 \
  --tab-label refactor-api \
  --kind pi \
  --task "Refactor the FastAPI endpoints."
```

The helper creates one new Herdr tab in the current cwd, labels it with `--tab-label` (or `--name`), starts a Pi agent, sends the two-file prompt, waits, and prints the summary.

## Team with coordinator

Use when work should be divided or workers should know about each other. Write `team.json`:

```json
{
  "coordinator": {"name": "coord", "task": "Wait for worker summaries, integrate them, and report final outcome."},
  "workers": [
    {"name": "api", "role": "API investigator", "task": "Inspect FastAPI endpoints only."},
    {"name": "db", "role": "DB investigator", "task": "Inspect SQLAlchemy models only."}
  ]
}
```

Run:

```bash
python3 /home/ruaridh/.agents/skills/herdr-agent-handoff/scripts/spawn_team.py --team-file team.json
```

The helper creates one new Herdr tab for the invocation, starts every team member in panes inside that tab, writes `.herdr-handoffs/team-*/roster.md`, prompts all agents with that roster, tells the coordinator to integrate worker summaries, waits, and prints summaries. Use top-level `"name"` in `team.json` or `--tab-label` to name the tab; otherwise it defaults to `team-<first-agent>`.

## Manual contract

Default topology is one named tab per skill invocation. Create the tab once, keep its root pane ID, then split one pane per subagent from that root pane so every subagent stays in the same tab.

```bash
mkdir -p .herdr-handoffs
summary="$(pwd)/.herdr-handoffs/worker-1-summary.md"
raw="$(pwd)/.herdr-handoffs/worker-1-raw.md"
herdr tab create --cwd "$PWD" --label refactor-api --no-focus
herdr pane split --pane <root-pane-id> --direction right --cwd "$PWD" --no-focus
herdr agent start worker-1 --kind pi --pane <split-pane-id>
herdr agent prompt worker-1 "TASK: <task>

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
- Do not rely on focused pane; create a named tab, keep its root pane ID, split subagent panes from it, and use explicit pane IDs plus unique agent names.
- For multiple workers, assign non-overlapping tasks and separate handoff paths; keep them in panes within the invocation's tab.
- If `agent prompt` returns `blocked`, inspect `herdr agent get <name>` and `herdr agent read <name> --source recent-unwrapped --lines 120` before sending input.
- Do not close panes/workspaces you did not create unless asked.
