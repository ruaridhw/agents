---
name: find-sibling-agents
description: List other agent sessions that share the same AgentsView project, across harnesses, machines, and directories. Use when asked who else has been working in this repo, whether a sibling agent is running or recently active, or when you want to compare concurrent or historical work against your own session. Branch values identify a session's recorded context, not recent activity on that Git branch. A plain read — the decision to hand off to or dedupe against a sibling is left to the user.
---

# Finding Sibling Agents

A "sibling" is any agent session that shares the current AgentsView `project`
— possibly a different harness (`pi`, `claude`, `codex`…), a different
machine, or a different working directory. This skill lists them. It does not
take an operational action (spawn, hand off, dedupe); that is the user's call
once they see who the siblings are.

Use the AgentsView CLI, not the MCP server: `session list` returns up to 500
rows with fields the MCP `list_sessions` tool caps off (parent/child
relationships, one-shot sessions, exact `cwd`), and the CLI is directly
executable from the harness.

## Core workflow

1. **Resolve the project.** Default to the current working directory's name,
   which is AgentsView's project key (repo/dir basename):

   ```bash
   agentsview projects          # list projects and their session counts
   agentsview session list --project "$(basename "$PWD")" --limit 40
   ```

   Override with an explicit project: `--project <name>`. Accept a name even
   when it differs from `cwd` — a user may want siblings from another repo on
   another machine.

2. **Rank by activity first.** When the question concerns a live branch or
   concurrent work, list resumable sessions newest-first:

   ```bash
   agentsview session list --project "$(basename "$PWD")" --resume --sort recent:desc --limit 40
   ```

   Exclude yourself, then inspect the newest transcript message for every
   returned sibling before considering a branch:

   ```bash
   agentsview session messages <id> --direction desc --limit 1
   ```

   Sort every returned sibling by that timestamp. The newest message leads the
   report unless it positively establishes unrelated work. `BRANCH`, ticket and
   artifact matches are supporting material after this activity pass; they must
   never hide a more recent sibling.

3. **Exclude yourself by id.** `●` marks a resumable session, not necessarily
   this session. In Pi, its row id is `pi:$PI_SESSION_ID`; in another harness,
   identify the current session from its own environment or transcript. A
   sibling is every other row.

4. **Report.** Lead with who the siblings are, the obvious ones first. Show
   the harness (`AGENT`), recorded context (`NAME`/`BRANCH`), and the newest
   message's timestamp and subject. Name the project you searched. If the
   question is about a Git branch, call a matching `BRANCH` a candidate, not
   proof: report current branch activity separately from `git log -1 <branch>`.
   If none share the project, say so plainly rather than implying one.

## Branch evidence

**Rank activity, then relevance, then recorded branch.** A branch-related ask
still begins with every resumable sibling, sorted by newest transcript message.
Inspect those messages for the named branch, ticket, paths, or the work's
distinctive terms as supporting material. State uncertainty where the latest
message does not establish relevance.

AgentsView tracks sessions, not Git branches. A session can start in one branch
or worktree, later operate through another worktree, and still retain its
original `BRANCH` or `—`; a commit can therefore be newer than every session
that names its branch. Use `--resume` to narrow current sessions, then the newest
transcript message to establish a sibling's last activity. Use the session's
`CWD` only to locate its recorded context, and Git history to establish when the
branch last changed. Do not describe `AGE` as the branch's or session's exact
last activity.

## Adjusting the list

The default is the recent snapshot. Use these only when the user asks for
more, not on every call.

| Need | Flags |
| --- | --- |
| See every session, not just recent | `--date-from <YYYY-MM-DD>`, or `--since 14d / 3m / 1y` |
| Limit to one harness | `--agent pi` / `--agent claude` / `--agent codex` |
| Include the shorter/one-shot ones the default hides | `--include-one-shot` (one-shot sessions are excluded by default) |
| Include subagent/child sessions | `--include-children` |
| More than the default 200 | `--limit 500` (hard ceiling) |
| Only sessions someone is actively using | `--resume` (active in the last 15 min) |
| Order by something other than recency | `--sort <key:asc\|desc>` on `recent, started, messages, failures, outcome, health` |

## Picking a sibling with the most context later

`session list` only shows the surface. When a user picks a sibling and wants
its history, deep-dive it with the AgentsView tools (see
`agentsview-finding-history` for the evidence-reading workflow):

```bash
agentsview session get <id>                                        # metadata, signals
agentsview session messages <id> --around <ordinal> --before 8 --after 8
```

## Rationalization Table

| Rationalization | Reality |
| --- | --- |
| "The current session in my list is a bug." | It is the newest row and marked `●`; exclude it — everyone else is a sibling. |
| "MCP is the interface." | Use the CLI. `session list` returns 500 rows and richer fields; `list_sessions` caps at 100 and drops relationship/one-shot detail. |
| "Sibling means same harness/machine." | It means same `project`. Harness, machine, and `cwd` are *attributes* of a sibling, not the grouping key. |
| "I must hand off or dedupe." | No. This is a read. Report the siblings and stop; the user decides whether to act. |
| "The row with the matching `BRANCH` comes first." | Start with the newest non-self resumable sessions and their messages; stale branch metadata must not hide active work. |
| "`●` identifies my own row." | It identifies a resumable session. Exclude the known current session id instead. |
| "`AGE` tells me when the sibling last worked." | Read the newest transcript message and report its timestamp; `AGE` is only a relative list summary. |
| "A session that names a branch proves somebody is working on it now." | `BRANCH` is recorded session context. Use `--resume`, then recent messages, for session activity and Git history for branch activity. |
| "Name the project after the repo." | AgentsView's project key is the directory basename, not the git remote. `agentsview projects` shows the exact keys. |

## Output shape

```markdown
## Sibling agents in `<project>`

- `<id>` (`<agent>`, `<machine>`, recorded branch/name) — newest message `<timestamp>`: what it was doing
- ... (Excluded: the current session.)

## Notes
- N sessions in the project, M returned (limit/date window).
- One sibling on a different machine/directory, if present.
```
