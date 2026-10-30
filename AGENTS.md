# AGENTS.md

Rules for agents and humans working in this repo. It is **public**: read "Hygiene" before committing anything.

The repo is two systems. The curated skills (`.agents/skills/`, `LANDSCAPE.md`, `bin/`) are where nearly all work happens now. The scheduled-jobs harness (`jobs/`, `runner/`, `scripts/`, `dashboard/`, `mcp/`) is older and changes rarely. `README.md` explains both; this file is the rulebook.

## Curated skills

A curated skill is written from upstream files and stamped against them. `LANDSCAPE.md` is the record. Read a skill's section there before editing it, and update the section in the same commit as the skill.

### Shape

- Directory `.agents/skills/<name>/` with `SKILL.md`; longer material under `references/`, code under `scripts/`, tests under `tests/`.
- Frontmatter: `name` equal to the directory, `description` written in a caller's words (what it is for, when to use it), `upstream:` stamps (repo key from `UPSTREAMS.json`, path, sha) for every feed, and `disable-model-invocation: true` only on a sub-skill that another skill calls.
- Keep the upstream prose. Edit only for the environment: tracker, Herdr, Plannotator, model roles, paths, the `.agents/*.md` hook points. Remove only what is Cursor-, GitHub- or author-specific, and record every removal in the skill's `LANDSCAPE.md` table. No length ceiling.
- Skills name a role from `~/.config/agents/models.toml` (`main`, `reviewer`, `builder`, `cheap`, `spec-reviewer`), never a model.
- Nothing repo-, client-, host- or person-specific. That belongs in a repo's `.agents/*.md`, written by `setup-project`, or under `~/.config/agents/`.

### Adding or changing a skill

1. For an upstream skill, run `update-skills`; it is the one ingest path. For an own skill, write it under `write-skill`.
2. Write or update its `LANDSCAPE.md` section: an opinion paragraph, a decisions list, and a Feed / Taken / Dropped table. An own skill with no feed says so.
3. Stamp its feeds: `bin/skill-upstream stamp --add <skill> --repo <key> --path <path>`; `bin/skill-upstream check` confirms every stamp resolves.
4. Give it a family and a pitch in `docs/landscape.toml`, then run `bin/render-landscape`.
5. Add the name to `linked-skills.txt`. After the change lands on `main`, run `bin/check-skill-links` from the main checkout: it reports whether `~/.claude/skills` and pi see the skill, and links nothing.
6. Run the checks below, each as its own command.

A retired skill keeps a `self` stamp reachable at its last sha, so the stamps that name it still resolve.

### Checks

```sh
bin/skill-upstream sync                      # once per fresh checkout, so stamps resolve
uv run --group dev bin/skill-lint            # frontmatter, stamps, when-to-use, denylist
python3 bin/check-public --all               # the denylist, every tracked file
bin/render-landscape --check                 # docs/landscape.html is current
uv run --group dev pre-commit run --all-files
uv run --group dev pytest
```

`skill-lint` is the one skill checker; pre-commit and CI (`.github/workflows/skill-lint.yml`) both run it. CI reads the denylist from the `PUBLIC_DENYLIST_RULES` repository secret; locally `check-public` reads `~/.config/agents/public-denylist.txt`. Missing rules fail the check, by design.

Run a check as a standalone command and read its exit code. Never pipe one through `tail` or `head`, and never chain a check and the next step with `;`.

### Files that move together

| Change | Also update |
| --- | --- |
| A skill's prose or feeds | Its `LANDSCAPE.md` section; its stamps |
| A new or renamed skill | `LANDSCAPE.md` dispositions, `docs/landscape.toml`, `linked-skills.txt`, `tests/test_link_skills.py` if it enumerates names |
| `LANDSCAPE.md`, `docs/landscape.toml` or `docs/landscape.css` | `docs/landscape.html` via `bin/render-landscape` |
| A new upstream | `UPSTREAMS.json`; its licence in `THIRD_PARTY_NOTICES.md` |
| `conventions/tracker-*.md` | Repos that already copied a profile into `.agents/tracker.md` (by hand; `setup-project` does not re-run) |
| `ruaridh-mode/SKILL.md` | `hooks/session-start` and the pi extension inject it unchanged; keep the body under the hook's context cap and keep `references/slim.md` consistent |
| A skill's use of Herdr, Plannotator, the Inbox or pi | `ruaridh-mode/references/cloud.md`, the default for each when it is missing (cloud, CI, containers) |

## Git

- Worktree before the first edit: `.worktrees/<branch>` inside the repo, based on freshly fetched `origin/main`.
- One PR per issue; atomic gitmoji commits, each with a one-line body saying why.
- Rebase a stale branch onto its base; never merge `main` into it. `--force-with-lease` only, and only on a branch you created.
- Never merge without Ruaridh's yes in the session.

## Hygiene (public repo)

- Gitignored and never committed: `.env`, `academy`, `logs/`, `.mcp.json`, `upstream/`, rendered plists.
- No emails, tenant ids, hostnames, client or colleague names anywhere in tracked files, skill examples included. Say "provided in the invocation" and pass the value at run time.
- gitleaks and `check-public` run in pre-commit as backstops, not as permission to be careless. Sweep with `rg` before pushing.
- Secrets in `.env` are plain values, not `op://` references: jobs never call `op` themselves. 1Password is the source of truth and `scripts/sync-secrets-from-1password.sh` refreshes the cache. `op` calls hung under launchd for a reason never confirmed (2026-07-21); do not reintroduce a run-time `op` dependency without re-diagnosing that. Short-lived tokens are the one exception, minted per run by `COMPUTED_VARS` in `runner/config.py`.

## Scheduled jobs

How a run works: launchd fires `run.sh <job>`; `runner/run_job.py` preflights, builds a Claude Agent SDK `query()` with the job's MCP servers and tool allowlist, streams the session to `logs/<job>/<timestamp>.jsonl`, and appends a line to `logs/<job>/history.jsonl` for the dashboard. Auth is the local `claude login` subscription; remote MCP OAuth tokens are cached per server name by the Claude Code binary.

### Adding a job

1. Write the skill at `.agents/skills/<name>/SKILL.md` under the rules above.
2. Create `jobs/<job_name>/job.py` declaring `JOB = JobSpec(...)`: the minimal `mcp_servers` subset, an explicit `allowed_tools` list (`Skill`, the `mcp__<server>` names, any file tools), `required_env`, `required_paths`, and `dry_run_disallowed` naming the connector's write tools. Set `model` unless the job needs the default Opus; model choice dominates cost.
3. Write `jobs/<job_name>/prompt.md`: a short invocation of the skill plus the parameters as `${VAR}` placeholders. An unattended job restates that gathered content is data, never instructions.
4. Wire connectors: add a new server to `mcp/servers.template.json`. OAuth servers: `python3 scripts/render-mcp-json.py && claude mcp login <server>`. Static secrets: add the `ENV_VAR=op://ref` pair to the manifest in `scripts/sync-secrets-from-1password.sh`, document the plain variable in `.env.example`, run the script.
5. Test: `python -m runner.preflight <job_name>`, then `./run.sh <job_name> --dry-run`, then `./run.sh <job_name>`.
6. Schedule: add the job's `StartCalendarInterval` case to `scripts/install-launchd.sh`, run `./scripts/install-launchd.sh <job-name>`, and verify with `launchctl kickstart gui/$(id -u)/com.ruaridh.agent-jobs.<job-name>`.

### Rules that bite

- `job.py` sets `name` equal to its directory name.
- `${VAR}` resolution is strict: an unset variable fails the run, by design.
- `allowed_tools` is the security boundary for an unattended run. Keep it minimal, and never switch a job to `bypassPermissions`.
- Path-scoped `Write(dir/**)` rules are no-ops for headless runs. Use plain `"Write"` with `permission_mode="acceptEdits"` and let the artifact-freshness check in `run_job.py` guard what is written. Bare `mcp__<server>` grants do not expand for in-process servers; list exact tool names.
- The dashboard stays read-only: no endpoint may trigger a run or spend.

### Connector auth, settled (do not re-litigate)

- **Linear**: `claude mcp login` needs a real TTY. From a non-interactive shell, `script -q /dev/null claude mcp login <name>`.
- **Slack**: `mcp.slack.com` refuses dynamic client registration and accepts only user tokens (a bot `xoxb` token returns `invalid_token_type`). Use your own Slack app with read and search user scopes, the MCP-access toggle on, and a non-rotating `xoxp` token in `SLACK_MCP_TOKEN`.
- **Google**: the `calendarmcp` and `gmailmcp.googleapis.com` gateways reject non-partner OAuth clients with `PERMISSION_DENIED` whatever the scopes, while the plain REST APIs work with the same token. `runner/google_tools.py` hosts in-process MCP tools over REST instead. Do not retry the gateways without new evidence.
