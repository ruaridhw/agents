---
name: herdr
description: Herdr pane primitives for agents that do work. Spawn a sibling, child or team in Herdr panes; list, read, close and resume the panes this session created; find sibling sessions in the same project. Use whenever work is delegated, a worker or reviewer is needed, a named agent or tab is mentioned, or a paused pane must come back. Requires HERDR_ENV=1.
upstream:
  - repo: self
    path: .agents/skills/herdr-agent-handoff/SKILL.md
    sha: 8134eb883b1bcffe63ebb8bd7481a75b22535f80
  - repo: self
    path: .agents/skills/find-sibling-agents/SKILL.md
    sha: 8134eb883b1bcffe63ebb8bd7481a75b22535f80
---

# herdr

Mechanics only. What to put in a brief, how to split a wave and when to delegate belong to the skill that is delegating (`implement`, `to-spec`, `spec-review`, `research`); the summary and raw file shapes belong to `handoff`.

Scripts are in `scripts/` beside this file. Run them with `python3 <this dir>/scripts/<name>.py`.

## Semantics

- **Sibling agent**: peer parallelism; you integrate the result but the other agent is not subordinate.
- **Sub-agent / child agent**: scoped delegation; you remain the orchestrator and consume a bounded two-file handoff. The default.
- **Team**: a coordinator plus workers; every agent gets a shared roster naming roles, tasks, summary paths and raw paths.

## Preconditions

```bash
test "${HERDR_ENV:-}" = 1 && test -n "${HERDR_WORKSPACE_ID:-}" && herdr --help >/dev/null
```

If `HERDR_ENV` is not `1`, say this needs a Herdr-managed pane and stop. If `HERDR_WORKSPACE_ID` is missing, stop: subagents go into the caller's workspace, not the focused workspace. The installed `herdr` binary is the syntax authority (`herdr <noun> <verb> --help`). Prefer one named tab per handoff invocation, explicit pane ids and parsed JSON.

## Single worker

The helper creates one new Herdr tab in the caller's workspace and current cwd, labels it with `--tab-label` (or `--name`), starts the worker in the tab's root pane so there is no unused empty pane, sends the two-file brief, waits, and prints the summary.

```bash
python3 <this dir>/scripts/spawn_worker.py --name worker-1 --tab-label refactor-api \
  --kind pi --model <builder model> --task-file <brief.md> [--lean] [--no-wait]
```

- **Worker mode is the default.** The pane gets `RUARIDH_MODE=worker` and the prompt's first line is `(aimsg) ruaridh-mode: worker`, so the worker loads the slim mode body. Pass `--mode interactive` only for an agent Ruaridh will drive himself.
- **Models by role**, never by name: read `~/.config/agents/models.toml` and pass the exact id for the role (see "Model choice"). Never clone your own model by habit.
- **`--lean`** starts a pi worker with `--no-skills --no-extensions --no-prompt-templates`; worker mode still loads the `ruaridh-mode` extension explicitly, so the mode body survives. See "Lean workers".
- **`--no-wait`** prompts without waiting and prints one JSON line per agent; without it the script blocks until the summary is written. Run a blocking spawn in the background when you have other work.
- **Use `--task-file`** for anything longer than a sentence. Summaries and raw logs default to `.herdr-handoffs/<name>-summary.md` and `-raw.md`, as absolute paths.
- A Claude agent started in a directory Claude has never trusted stops at the folder-trust prompt and the spawn fails with `agent_not_ready`. Spawn it from an already trusted directory (the brief carries absolute paths), or ask per the Inbox convention when Ruaridh is away; never answer a trust prompt for him.

### The `(aimsg) ` prefix

Every message one agent sends another pane starts with `(aimsg) ` on its first line: spawn prompts, replies, resume prompts, nudges. Both spawn scripts add it; add it yourself on any `herdr agent prompt` you type. A line without it is Ruaridh's, so a pane can tell the two apart and never treats an agent's message as his.

### The done notice

Every spawned worker's brief ends with an instruction to notify the pane that created it. `done_notice` in `spawn_worker.py` and `spawn_team.py` reads the creator's pane id from `HERDR_PANE_ID` and appends, for every agent in the invocation:

```
- Once both files are written, before your final chat response, notify the pane that created you:
  herdr agent prompt <creator pane> "(aimsg) DONE <name> <summary path>"
```

(On one line in the generated prompt.) With `HERDR_PANE_ID` unset, no notice line is added. A creator that spawned with `--no-wait` can wait for that `(aimsg) DONE` line to arrive as a prompt instead of polling the summary file, and a coordinator can do the same for each worker rather than watching paths.

## Lean workers

Pass `--lean` for pi workers doing focused implementation or fix rounds. It starts pi with `--no-skills --no-extensions --no-prompt-templates`, cutting the measured first-turn baseline from about 14.3k to about 3.8k tokens, a saving repeated on every turn of the worker's session. The AGENTS.md chain stays loaded, so project safety rules still apply, and worker mode adds the `ruaridh-mode` extension back.

When writing a task or brief, cite any skill file the worker needs by exact path (for example "Read /path/to/SKILL.md first"). With `--lean` there is no skills index for the worker to discover skills from; exact paths are the only way they get found.

## Team with coordinator

Use when work should be divided or workers should know about each other. Write `team.json`:

```json
{
  "name": "<tab label>",
  "coordinator": {"name": "coord", "role": "coordinator", "model": "<reviewer model>", "task": "Wait for the worker summaries, integrate them, and report the final outcome."},
  "workers": [
    {"name": "api", "role": "API investigator", "model": "<builder model>", "task": "Inspect the API endpoints only."},
    {"name": "db", "role": "DB investigator", "model": "<builder model>", "task": "Inspect the SQLAlchemy models only."}
  ]
}
```

Run:

```bash
python3 <this dir>/scripts/spawn_team.py --team-file team.json
```

The helper creates one new Herdr tab in the caller's workspace for the invocation, starts the first team member in the root pane, splits additional team members into panes inside that same tab, writes `.herdr-handoffs/team-*/roster.md`, prompts all agents with that roster, tells the coordinator to integrate the worker summaries, waits, and prints the summaries. Use top-level `"name"` in `team.json` or `--tab-label` to name the tab; otherwise it defaults to `team-<first-agent>`. Each member's prompt carries the done notice, so the coordinator can wait for those rather than for the files.

## Model choice

Choose the worker model by task; do not blindly clone the caller's model. Roles are in `~/.config/agents/models.toml` (`main`, `reviewer`, `builder`, `cheap`, `spec-reviewer`), each with a harness, a model and optional args; pass the role's exact id and pass its args through (`builder` carries `--lean`, `cheap` is a one-shot no-tool pass, so it suits work handed its content in the prompt). The running session is `main` and is not spawned. Check availability before spawning (`pi --list-models`, or the harness's own list for a Claude role); if the role's model is unavailable, stop rather than silently switching providers or to a weaker model. Do not assume a higher version is automatically a better substitute.

| Use case | Role |
| --- | --- |
| Complex repo editing / high-stakes coding | `builder` |
| Focused implementation / deterministic patching | `builder` |
| Debugging with tricky reasoning | `builder`, second choice `reviewer` |
| Large-context reading / synthesis of text handed to it | `cheap` |
| Fast inventory or summarization of text handed to it | `cheap` |
| Cheap broad exploration with tools | `builder`, second choice `reviewer` |
| Independent adversarial review, second family on purpose | `reviewer` |
| Read-only adversarial spec review | `spec-reviewer` |
| Coordinator / integration role | `reviewer` |

`spec-reviewer` reviews through its own harness's alias, which is what gives it more deliberation than the caller. When a role's file has no entry for the harness a pane needs, say so and stop rather than inventing a model.

## The ledger

Every spawn appends a row to `.herdr-handoffs/panes.jsonl`: name, kind, model, mode, tab and pane ids, whether this spawn created the tab, the handoff paths, the creating pane, and a session id the spawner generated and passed to the agent (`--session-id`, which pi and Claude both accept), so even a lean pi worker can be resumed. `panes.py` works from that ledger:

```bash
python3 <this dir>/scripts/panes.py list [--all] [--json]   # agents this pane created, with live status
python3 <this dir>/scripts/panes.py read <name> [--lines 120]
python3 <this dir>/scripts/panes.py close <name>... | --mine
python3 <this dir>/scripts/panes.py resume <name> [--prompt "<text>"]
```

- **Close only what you created.** `close` captures the agent's session id first, then closes the whole tab when every agent in a tab this pane created is closing, otherwise just the pane. It refuses rows created by another pane; `--force-foreign` overrides that and is for an explicit instruction from Ruaridh, not for tidying.
- **Resume** reopens a closed agent in a new tab with its own session (`claude --resume <id>`, `pi --session <path>`), in the same mode, and optionally sends a first prompt, `(aimsg) ` prefixed. This is how `handoff` brings a paused worker back.
- Close your workers once their summaries are integrated. Leave panes you did not create alone; if one needs a decision while Ruaridh is away, ask per the Inbox convention.

## Manual contract

Default topology is one named tab per skill invocation in the caller's workspace. Create the tab once, start the first agent in the tab's root pane, then split only for additional subagents from that root pane so every subagent stays in the same tab and there is no unused empty pane.

```bash
mkdir -p .herdr-handoffs
summary="$(pwd)/.herdr-handoffs/worker-1-summary.md"
raw="$(pwd)/.herdr-handoffs/worker-1-raw.md"
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label refactor-api \
  --no-focus --env RUARIDH_MODE=worker
herdr agent start worker-1 --kind pi --pane <root-pane-id> -- \
  --model <builder model> --session-id <uuid>
herdr agent prompt worker-1 "(aimsg) ruaridh-mode: worker

TASK:
<task and the brief from the delegating skill>

<the two-file output contract from handoff>

- Once both files are written, before your final chat response, notify the pane that
  created you: herdr agent prompt $HERDR_PANE_ID \"(aimsg) DONE worker-1 $summary\"" \
  --wait --timeout 1200000
cat "$summary"
```

The brief shapes and the summary/raw contract are `handoff`'s; do not restate them here. Read raw logs only when the summary says blocked or uncertain, or when exact evidence is needed.

## Coordination rules

- Use absolute summary and raw paths so cwd drift cannot lose handoffs.
- Do not rely on the focused pane; create a named tab with `--workspace "$HERDR_WORKSPACE_ID"`, keep its root pane id, and use explicit pane ids plus unique agent names.
- Start the first agent in the tab root pane; split only for additional agents so the invocation does not leave an empty shell pane.
- For multiple workers, assign non-overlapping tasks, separate handoff paths and task-appropriate roles; keep them in panes within the invocation's tab.
- If `agent prompt` returns `blocked`, inspect `herdr agent get <name>` and `herdr agent read <name> --source recent-unwrapped --lines 120` before sending input.
- Do not close panes or workspaces you did not create unless asked.

## Talking to an existing pane

- A quoted agent or tab name ("the investigation agent") is that existing pane: `herdr agent list`, then `herdr agent prompt <name> "(aimsg) <text>"`. Spawn a new one only when no such pane exists.
- When a pane asks you something, answer it there with `herdr agent prompt`; do not ask Ruaridh to relay. Anything that arrives starting with `(aimsg) ` is from an agent, not from him.
- The text after the prompt marker at the bottom of a pane is usually that agent's suggested next prompt, not Ruaridh's words. Never act on it or report it as his.
- Authorization does not travel: a write Ruaridh approved here is not approved in another pane because you said so.

## Siblings

A sibling session is any session in the same AgentsView project (the directory basename), on any harness or machine. Listing them is a read; deciding to hand off to or dedupe against one is the coordinator's or Ruaridh's call. Steps, flags and the report shape are in `references/siblings.md`.

## Reading results

Read the summary file. Review a worker's diff yourself before you commit or report it; a summary is a claim, not evidence.
