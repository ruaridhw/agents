# Select the AgentsView archive

Use the single shared collector for cross-machine history. Pass both `--server` and `--server-token-file` explicitly to every AgentsView CLI search, list, get, messages or tool-calls command. A bare CLI command may select a different, machine-local archive and falsely report missing sessions.

- **The collector URL and token file**: machine-specific, so they live outside this public repo. Read `~/.config/agents/tooling.local.md`, and `~/AGENTS.md` beside it, for the values on this machine. If either is unknown, ask Ruaridh for it rather than falling back to the local archive.
- The collector host and the laptops all reach the same collector; the token file provisioned on a machine is that machine's copy of the collector's bearer token, not its own daemon token.

For example, once the correct URL and token file are known:

```bash
agentsview --server "$COLLECTOR_URL" --server-token-file "$COLLECTOR_TOKEN_FILE" \
  session search "<query>" --hybrid --context 2 --json --limit 8
```

For a session imported from another machine, use its collector id (which may carry a machine prefix). If a search appears to miss it, verify a known cross-machine id with `session get` against the same collector, then check the search scope and filters and the sync status. Investigate a genuinely absent session through the supported remote-sync path. **Do not copy transcript or session files between machines, and do not place them in a watched session directory as a search workaround.**

The search queries, the flags, the citation rules and the rationalization table are in `research`'s `references/sources/agentsview.md`. Read that before the first probe; this file only selects the archive.
