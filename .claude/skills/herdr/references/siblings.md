# Finding sibling sessions

Use the AgentsView CLI (it returns more rows and fields than the MCP `list_sessions`). Pass the collector server and token flags on every call; their values are in the local tooling file named in `ruaridh-mode`'s `tooling.md`.

1. **Project key**: the directory basename, not the git remote. `agentsview projects` shows exact keys. Accept an explicit other project when asked.
2. **Rank by activity**, newest first, excluding yourself by session id (`●` marks any resumable session, not necessarily yours):

   ```bash
   agentsview session list --project "$(basename "$PWD")" --resume --sort recent:desc --limit 40
   agentsview session messages <id> --direction desc --limit 1
   ```

   Sort by the newest transcript message. A matching `BRANCH` is supporting evidence only: sessions keep the branch they started on. Use `git log -1 <branch>` for branch activity.
3. **Report**: who the siblings are, harness, recorded name or branch, newest message time and subject, and the project searched. Say plainly when there are none.

| Need | Flags |
| --- | --- |
| Older sessions | `--since 14d` or `--date-from YYYY-MM-DD` |
| One harness | `--agent pi` / `--agent claude` |
| One-shot sessions | `--include-one-shot` |
| Child sessions | `--include-children` |
| Only live ones | `--resume` (active in the last 15 minutes) |

For a sibling's history: `agentsview session get <id>`, `agentsview session messages <id> --around <ordinal> --before 8 --after 8`.
