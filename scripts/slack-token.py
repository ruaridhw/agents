#!/usr/bin/env python3
"""Maintain a rotating Slack user token for the mcp.slack.com bearer header.

The Slack app has token rotation enabled: access tokens (xoxe.xoxp-…) expire
~12h and refresh tokens are single-use, so the pair must be re-persisted after
every refresh. State lives at ~/.config/slack/mcp-token.json, seeded once from
1Password.

  seed    read access_token/refresh_token (+ client_id/client_secret) from the
          1Password item and write the local state file
  token   print a valid access token, refreshing (and persisting the rotated
          pair) if it expires within 30 minutes

runner/config.py calls `token` to fill ${SLACK_MCP_TOKEN}. 1Password access
uses the op CLI with the service-account token from the macOS Keychain
(item: op-service-account), matching the repo's Todoist pattern.
"""

import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OP_ITEM = "op://Duvo/SlackApp"
STATE_FILE = Path.home() / ".config" / "slack" / "mcp-token.json"
REFRESH_MARGIN_S = 30 * 60


def op_read(field: str) -> str:
    keychain = subprocess.run(
        ["security", "find-generic-password", "-s", "op-service-account", "-w"],
        capture_output=True, text=True,
    )
    proc = subprocess.run(
        ["op", "read", f"{OP_ITEM}/{field}"],
        capture_output=True, text=True,
        env={"OP_SERVICE_ACCOUNT_TOKEN": keychain.stdout.strip(), "PATH": "/opt/homebrew/bin:/usr/bin:/bin"},
    )
    if proc.returncode != 0:
        sys.exit(f"op read {OP_ITEM}/{field} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def save(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))
    STATE_FILE.chmod(0o600)


def seed() -> None:
    state = {
        "access_token": op_read("access_token"),
        "refresh_token": op_read("refresh_token"),
        "client_id": op_read("client_id"),
        "client_secret": op_read("client_secret"),
        # Unknown remaining validity of the seeded token: mark it stale so the
        # first `token` call refreshes and learns the real expiry.
        "expires_at": 0,
    }
    save(state)
    print(f"seeded {STATE_FILE} from {OP_ITEM}")


def refresh(state: dict) -> dict:
    body = urllib.parse.urlencode({
        "client_id": state["client_id"],
        "client_secret": state["client_secret"],
        "grant_type": "refresh_token",
        "refresh_token": state["refresh_token"],
    }).encode()
    req = urllib.request.Request("https://slack.com/api/oauth.v2.access", data=body, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    if not data.get("ok"):
        sys.exit(f"slack token refresh failed: {data.get('error')} — re-run seed after re-installing the app")
    token_home = data.get("authed_user", data)  # user-token rotation nests under authed_user
    state["access_token"] = token_home["access_token"]
    state["refresh_token"] = token_home["refresh_token"]
    state["expires_at"] = time.time() + token_home.get("expires_in", 0)
    save(state)
    return state


def token() -> None:
    if not STATE_FILE.exists():
        sys.exit(f"no state at {STATE_FILE} — run: python3 scripts/slack-token.py seed")
    state = json.loads(STATE_FILE.read_text())
    if state.get("expires_at", 0) - time.time() < REFRESH_MARGIN_S:
        state = refresh(state)
    print(state["access_token"])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "seed":
        seed()
    elif mode == "token":
        token()
    else:
        sys.exit("usage: slack-token.py {seed|token}")
