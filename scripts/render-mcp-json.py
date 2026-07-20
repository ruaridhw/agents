#!/usr/bin/env python3
"""Render mcp/servers.template.json → .mcp.json (gitignored).

The rendered file lets an *interactive* `claude` session in this repo see the
same servers the jobs use, so you can complete each remote server's OAuth once
(via /mcp). Headless SDK runs then reuse the cached tokens.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runner.config import MCP_TEMPLATE, REPO_ROOT, load_env, resolve  # noqa: E402

env = load_env()
template = json.loads(MCP_TEMPLATE.read_text())
servers = {}
for name, cfg in template["servers"].items():
    if cfg.get("type") == "sdk":
        print(
            f"skipping {name}: in-process sdk server (not usable by the CLI)",
            file=sys.stderr,
        )
        continue
    try:
        servers[name] = json.loads(resolve(json.dumps(cfg), env, context=name))
    except Exception as err:
        print(f"skipping {name}: {err}", file=sys.stderr)

out = REPO_ROOT / ".mcp.json"
out.write_text(json.dumps({"mcpServers": servers}, indent=2) + "\n")
print(f"wrote {out} with {len(servers)} servers (gitignored)")
