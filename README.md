# ruaridhw/agents

One way of working for coding agents, written down as skills.

This repository holds an opinionated set of agent skills for one engineer's environment, curated from [mattpocock/skills](https://github.com/mattpocock/skills), [obra/superpowers](https://github.com/obra/superpowers) and the `pstack` plugin in [cursor/plugins](https://github.com/cursor/plugins), with the author's own skills alongside. The same skills load into Claude Code and into pi. A second, older part of the repo schedules local agent jobs on a Mac; it has its own chapter at the end.

The short version of the whole set is the landscape page, `docs/landscape.html`: open it in a browser for the chain, the gates and a one-line pitch per skill. The long version is `LANDSCAPE.md`, which records every decision behind every skill.

## The ideas

**One router, always on.** Every session starts with `ruaridh-mode`, injected by a Claude Code SessionStart hook or by the pi extension. It classifies what arrived (a ticket ref, a bug, a vague idea, a spec, a PR), names the route in one line, and holds the general rules that apply to every session: worktree before the first edit, evidence before any "done" claim, never merge without a yes, one PR per issue. A worker spawned to do one task gets a slim body of the same skill.

**A chain with gates where a human decides.** A project runs `grill` → `to-spec` → `spec-review` → `to-tickets` → `to-plan` → `implement` → `review` → `pr` → `ship`. A human decides at two points, the spec and the ticket wave, and at a third when the UI changes materially. The plan is not gated. A quick task is just done, and a small change goes through `clarify` to `implement`. Side doors (`debug`, `prototype`, `research`, `handoff`, `wayfinder`) open from any step.

**Skills name hook points; repos bind them.** No curated skill mentions a tracker, a deploy target or an employer. Each reads a convention file in the repo it runs in: `.agents/tracker.md`, `build-loop.md`, `debug-loop.md`, `prove-landed.md`, `deploy.md`, `design-review.md`, `domain.md`, `review.md`, `references.md`. A missing file means the skill's default. `setup-project` writes these files once per repo, and the two tracker profiles in `conventions/` are what it copies in.

**Curated, not forked.** A curated skill is written from one or more upstream files and stamped with their repo, path and sha in its frontmatter. The upstream prose stays; edits are for the environment only (tracker, Herdr panes, model roles, paths), and every removal is on the record in `LANDSCAPE.md`. `update-skills` syncs the upstream clones, shows the drift per skill, and proposes a merge for approval, so the set keeps up without being rewritten.

**Agents do work in panes, not in subagents.** Builders, reviewers and explorers run as full sessions in Herdr panes, spawned through the `herdr` skill with a written brief and a two-file handoff (summary and raw log). Every message between panes starts with `(aimsg) `, so a pane can tell an agent's message from a human's.

**Public repo, private rules.** Nothing here names a client, a host or a person. `bin/check-public` scans every public-facing file against a denylist kept outside the repo (a local file, or a repository secret in CI) and fails closed when the rules are missing.

## What is here

| Path | What |
| --- | --- |
| `.agents/skills/<name>/` | The skills. `.claude/skills` is a link to it, so Claude Code finds them. |
| `LANDSCAPE.md` | The record: per skill, the opinion, the decisions and, per upstream feed, what was taken and what was dropped. |
| `docs/landscape.html` | The shareable page rendered from `LANDSCAPE.md` and `docs/landscape.toml`. |
| `UPSTREAMS.json` | The upstream repos and their audited shas. Clones live in `upstream/`, gitignored. |
| `conventions/` | Tracker profiles (kata, GitHub Issues) that `setup-project` copies into a repo. |
| `hooks/session-start` | The Claude Code hook that injects `ruaridh-mode`. |
| `.pi/extensions/ruaridh-mode.ts`, `package.json` | The pi package: the same injection, plus the skills directory registered with pi. |
| `linked-skills.txt` | The skills linked into `~/.claude/skills` and registered with pi. |
| `bin/` | `skill-upstream`, `skill-lint`, `check-public`, `link-skills`, `render-landscape`, `memcap`. |
| `THIRD_PARTY_NOTICES.md` | The upstream licences. |
| `jobs/`, `runner/`, `scripts/`, `dashboard/`, `mcp/` | The scheduled-jobs harness (see below). |

## The skills

Grouped as the landscape page groups them. Each name is a directory under `.agents/skills/`.

- **Operating**: `ruaridh-mode`, `herdr`, `handoff`, `worktree`, `recall`, `rare-skills`.
- **Thinking and shaping**: `clarify`, `grill`, `prototype`, `research`, `domain`, `arch`, `questionnaire`, `bro`, `teach`.
- **Planning and ticketing**: `to-spec`, `spec-review`, `spec-page`, `to-tickets`, `triage`, `to-plan`, `wayfinder`.
- **Building**: `implement`, `tdd`, `debug`, `verify`, `wizard`.
- **Quality and shipping**: `review`, `pr`, `babysit`, `ship`, `technical-writing`.
- **Meta**: `update-skills`, `write-skill`, `retro`, `setup-project`.

Skills for services used rarely (cloud providers and the like) sit outside the repo under `~/.agents/rare/` and are reached through `rare-skills`.

## Install

The skills assume the environment they were written for: a tracker (kata or GitHub Issues), Herdr for panes, Plannotator for review gates and the Inbox, AgentsView for session history. Without those, the ideas still read; the skills partly run.

1. Clone the repo and install the Python tooling:

   ```sh
   git clone https://github.com/ruaridhw/agents ~/code/agents
   cd ~/code/agents
   uv sync
   uv run pre-commit install
   bin/skill-upstream sync        # clones the upstreams so the stamps resolve
   ```

2. Link the skills for Claude Code and add the hook. `bin/link-skills` links every name in `linked-skills.txt` into `~/.claude/skills`. Then register the hook in `~/.claude/settings.json`:

   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "matcher": "startup|clear|compact",
           "hooks": [ { "type": "command", "command": "exec bash /home/you/code/agents/hooks/session-start", "timeout": 10 } ]
         }
       ]
     }
   }
   ```

3. For pi, install the repo as a package. It registers the extension and the skills directory:

   ```sh
   pi install git:github.com/ruaridhw/agents
   ```

4. Write the host-specific files the skills read. None of these are in the repo:

   | File | Holds |
   | --- | --- |
   | `~/.config/agents/models.toml` | Model roles: `main`, `reviewer`, `builder`, `cheap`, `spec-reviewer`. Skills name a role, never a model. |
   | `~/.config/agents/tooling.local.md` | Hostnames, collector URLs, token paths. |
   | `~/.config/agents/public-denylist.txt` | The regexes `check-public` scans for. |
   | `~/.config/agents/upstreams.local.json` | Private upstreams, such as an employer's skill kit. |

5. In each repo the skills will run in, run `setup-project` once. It asks which tracker and which build loop apply, writes `.agents/*.md`, creates the tracker labels and links any rare skills the repo uses.

## Keeping up with the upstreams

```sh
bin/skill-upstream sync       # fetch the upstream clones at the recorded shas
bin/skill-upstream status     # drift per curated skill
bin/skill-upstream diff NAME  # the upstream diff behind one skill's stamps
bin/skill-upstream check      # every stamp resolves
```

The `update-skills` skill runs the full loop: per feed, read the diff against the skill's section in `LANDSCAPE.md`, classify each hunk as adopted, dropped or new, draft the merge as a patch for review, apply on approval, and re-stamp. A new upstream skill gets a landscape row before it gets a copy.

## Checks

Pre-commit runs ruff, ty, uv-lock, gitleaks, `check-public`, `skill-lint` and a staleness check on the landscape page. CI runs `skill-lint` and `check-public --all` on every pull request, with the denylist from a repository secret. `skill-lint` is the one skill checker: frontmatter, stamps, when-to-use text and the denylist.

```sh
uv run --group dev pre-commit run --all-files
uv run --group dev pytest
```

## Scheduled local jobs

The older half of the repo turns a Mac and a Claude subscription into a few scheduled agents: a morning brief rendered to HTML before you sit down, meeting notes filed into Notion with names corrected against a private wiki, and action items pushed to a to-do list. No server and no cloud runner: launchd fires `run.sh <job>`, the Python Claude Agent SDK runs the job with only the connectors it needs, and every run is logged locally and shown on a read-only dashboard.

| Job | Schedule | What it does |
| --- | --- | --- |
| `morning_brief` | 08:00 Mon–Fri | Renders the morning brief (read-only across calendar, mail, chat and tracker connectors) and opens it in a browser. |
| `granola_notion_sync` | hourly 08:00–18:00 Mon–Fri | Files the last 7 days of Granola meetings into a Notion database, correcting transcription errors against the local wiki first. Create-only, deduplicated by Granola id. |
| `notion_todoist_sync` | 07:00 Mon–Fri | Reconciles meeting action items through a Notion tasks database into Todoist, which is the source of truth once synced. Also chained after each `granola_notion_sync` run. |
| `hello` | manual | A round trip that checks auth and scheduling. |

Each job is a directory under `jobs/`: `job.py` declares the MCP servers, the allowed tools and the required environment; `prompt.md` is the invocation with `${VAR}` placeholders resolved from `.env`; an optional `precheck.md` is a cheap probe that skips the run when there is nothing to do.

Setup, once the skills tooling above is installed:

```sh
cp .env.example .env                # secrets and ids, gitignored
ln -s ~/Documents/academy academy   # the private wiki, gitignored
claude login                        # subscription auth, once
python3 scripts/render-mcp-json.py  # renders .mcp.json, gitignored
claude mcp login granola            # once per OAuth connector
./run.sh hello                      # smoke test
./scripts/install-launchd.sh        # schedule
```

`python -m runner.preflight <job>` checks credentials, environment, the wiki link and MCP reachability, so a scheduled run fails with a message in `logs/` instead of silently at 08:00. launchd rather than cron because launchd fires a run missed during sleep once on the next wake. The dashboard (`cd dashboard && docker compose up -d`) reads `logs/` and has no "run now" button, so it can never trigger spend.

Runs draw on the subscription through `claude login`. Setting `ANTHROPIC_API_KEY` in `.env` switches every run to pay-as-you-go billing.

## Hygiene

`.env`, `academy`, `logs/`, `.mcp.json`, `upstream/` and `.scratch/` are gitignored. No tracked file carries an email, a tenant id, a client or colleague name, or a token; prompts and skills get those values at run time. gitleaks and `check-public` are backstops, not permission to be careless.

## Licences

The curated skills keep prose from MIT-licensed upstreams; their notices are in `THIRD_PARTY_NOTICES.md`.
