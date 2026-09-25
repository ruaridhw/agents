---
name: searching-shared-agentsview-history
description: Use when finding prior agent sessions, searching AgentsView history, recovering past decisions or transcripts, or using agentsview-finding-history on either the collector host or a laptop.
---

# Search the shared AgentsView archive

**REQUIRED SUB-SKILL:** Load `agentsview-finding-history` for its search, evidence, and citation workflow. This skill only selects the archive; apply it before running any CLI probes from that workflow.

## Select the archive

Use the single shared collector for cross-machine history. Pass both `--server` and `--server-token-file` explicitly to every AgentsView CLI search, list, get, messages, or tool-calls command. A bare CLI command may select a different, machine-local archive and falsely report missing sessions.

- **On the collector host:** use `http://127.0.0.1:8461` and `/opt/homelab/agentsview/mcp-token`. Alternatively, run the CLI inside the collector container as documented in the homelab setup guide.
- **On a laptop:** use the collector's tailnet URL and the *collector* bearer token file provisioned on that laptop, not its own daemon token. Get the URL and token-file location from the machine's setup instructions or the user's invocation; if either is unknown, ask for it rather than falling back to the local archive.

For example, once the correct URL and token file are known:

```bash
agentsview --server "$COLLECTOR_URL" --server-token-file "$COLLECTOR_TOKEN_FILE" \
  session search "<query>" --hybrid --context 2 --json --limit 8
```

For a session imported from another machine, use its collector ID (which may have a machine prefix). If a search appears to miss it, verify a known cross-machine ID with `session get` against the same collector, then check search scope/filters and sync status. Investigate a genuinely absent session through the supported remote-sync path. **Do not copy transcript/session files between machines or place them in a watched session directory as a search workaround.**
