# agent-jobs

**Your Mac, quietly working for you before you sit down.**

agent-jobs turns a laptop and a Claude subscription into a small fleet of
scheduled AI agents. While you make coffee, they've already read your calendar,
mail, chat and meeting notes — and handed back the results: a hand-drawn
morning brief waiting in your browser at 08:00, every meeting filed into
Notion with names spelled right, and each action item already sitting in your
to-do list. Before a meeting is written to Notion, it is corrected against the
local "second-brain" wiki (here, a gitignored separately maintained repo,
"academy"), so misheard names, companies and acronyms are fixed against your
private source of truth without any of it leaving your machine.

No cloud runner, no server, no new inbox to check. Each job is a prompt, a
schedule, and a strict tool allowlist: launchd fires it, the Claude Agent SDK
runs it with only the connectors it needs, and everything it does is logged
locally and visible on a read-only dashboard. Secrets live in 1Password and
never touch the repo, logs and briefs stay on your machine, and a cheap
pre-check probe skips runs with nothing to do. Add a skill, add a schedule —
and the machine takes one more chore off your plate.

---

Scheduled local agent jobs on the **Python Claude Agent SDK**, driven by
**launchd** on a Mac, authenticated against a Claude subscription via
`claude login`. Migrated out of Cowork's scheduled-task harness.

| Job | Schedule | What it does |
|---|---|---|
| `morning_brief` | 08:00 Mon–Fri | Renders the styled HTML morning brief (read-only across calendar/email/chat/tracker connectors) and opens it in Firefox. |
| `granola_notion_sync` | hourly 08:00–18:00 Mon–Fri | Syncs the last 7 days of Granola meetings into the Notion Meetings DB, correcting ASR mishearings against the local wiki first. Create-only, dedup by Granola ID. |
| `notion_todoist_sync` | 07:00 Mon–Fri | Full reconciliation of meeting action items → Notion Tasks DB → Todoist: re-scans all meeting pages, pushes new tasks, pulls back completions/edits/sections (Todoist is source of truth once synced). Also chained in fast mode after each `granola_notion_sync` run. |
| `hello` | manual | Trivial round-trip to verify auth + scheduling (Phase-1 spike). |

Everything identifying stays out of git: `.env` (secrets/IDs), `academy`
(a symlink to the private wiki), and `logs/` are all gitignored.

## Layout

```
jobs/<name>/job.py        job spec: MCP servers, allowed tools, required env
jobs/<name>/prompt.md     invocation prompt; ${VAR}s resolved from .env
runner/run_job.py         entrypoint: preflight → query() → jsonl logs
runner/config.py          .env loading, ${VAR} resolution, MCP subsetting
runner/preflight.py       auth/env/paths/MCP checks that fail loudly
.claude/skills/           the `morning` and `granola-notion` skills
mcp/servers.template.json MCP server defs with ${ENV_VAR} placeholders
launchd + scripts/        LaunchAgent renderer/installer, hooks, mcp render
dashboard/                read-only TS/Docker view over logs/
academy -> …              gitignored symlink to the private wiki
```

## Setup

```sh
# 1. deps + git hooks
uv sync
uv run pre-commit install           # ruff format/check, ty, uv-lock, gitleaks on every commit

# 2. private bits (both gitignored)
cp .env.example .env                # fill in values
ln -s ~/Documents/academy academy   # or wherever the wiki lives

# 3. subscription auth — once, interactively
claude login

# 4. remote MCP OAuth — once per connector, from an interactive terminal
python3 scripts/render-mcp-json.py  # renders .mcp.json (gitignored)
claude mcp login granola            # repeat for: notion linear slack gcal gmail
                                    # tokens are cached and reused by headless runs

# 5. smoke test, then schedule
./run.sh hello
./scripts/install-launchd.sh
```

Preflight (`python -m runner.preflight <job>`) checks credentials, required
env vars, the `academy` symlink, and remote MCP reachability — a scheduled run
aborts with a clear message in `logs/` instead of failing silently at 08:00.

## Why launchd, not cron

cron silently skips any run scheduled while the Mac is asleep. launchd's
`StartCalendarInterval` fires a missed run **once** on the next wake — so the
brief pops up in Firefox shortly after the laptop opens, and the hourly sync
gets one catch-up run (fine: it looks back 3 days and dedupes). On an
always-on box the same `run.sh` works under plain cron; the plists are the
only Mac-specific piece.

## Logs & dashboard

Each run writes `logs/<job>/<timestamp>.jsonl` (full SDK message stream;
pruned after 30 days) and appends one line to `logs/<job>/history.jsonl`
(status, duration, cost, short result — capped at 500 lines). The dashboard
reads only those files:

```sh
cd dashboard && docker compose up -d   # http://localhost:8787
```

It is deliberately read-only — no "run now" button — so it can never trigger
spend or actions.

## Billing & auth notes

- Runs draw on the Claude subscription allowance via `claude login`
  credentials (supported for headless SDK use). Never hand-extract OAuth
  tokens into other tools — that violates the Consumer ToS. Watch usage in
  week one; the brief fans out across 6 connectors.
- Setting `ANTHROPIC_API_KEY` in `.env` switches all runs to pay-as-you-go
  API billing. Decide deliberately.

## Public-repo hygiene

- `.env`, `academy`, `logs/`, and the rendered `.mcp.json` are gitignored.
- Prompts and skills carry no emails, IDs, client names, or tokens — those are
  supplied at runtime from `.env` and the local wiki.
- Pre-commit hooks (`.pre-commit-config.yaml`) run gitleaks on every commit as
  a backstop against accidental secret commits, alongside ruff and ty.
