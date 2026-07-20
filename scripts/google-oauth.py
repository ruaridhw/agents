#!/usr/bin/env python3
"""Mint Google access tokens for the first-party remote MCP endpoints.

Google's gmailmcp/calendarmcp endpoints speak standard bearer auth against
accounts.google.com, but accounts.google.com has no dynamic client
registration, so `claude mcp login` can't drive the flow. This helper uses
your own OAuth *desktop* client instead (stdlib only):

  authorize   one-time: browser consent via loopback redirect; stores the
              refresh token at ~/.config/google/mcp-token.json
  token       prints a valid access token (cached; silently refreshed) —
              runner/config.py calls this to fill ${GOOGLE_MCP_ACCESS_TOKEN}

Client JSON path comes from $GOOGLE_OAUTH_CREDENTIALS
(default ~/.config/google/oauth-client.json). Scopes are read-only: the
morning brief only reads mail and calendar.
"""

import json
import os
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]
CLIENT_JSON = Path(
    os.environ.get("GOOGLE_OAUTH_CREDENTIALS")
    or Path.home() / ".config" / "google" / "oauth-client.json"
).expanduser()
TOKEN_FILE = Path.home() / ".config" / "google" / "mcp-token.json"


def load_client() -> dict:
    if not CLIENT_JSON.exists():
        sys.exit(f"missing OAuth client JSON at {CLIENT_JSON} — set GOOGLE_OAUTH_CREDENTIALS")
    data = json.loads(CLIENT_JSON.read_text())
    return data.get("installed") or data.get("web") or sys.exit("unrecognised client JSON")


def post_form(url: str, params: dict) -> dict:
    body = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def save_tokens(tokens: dict) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
    TOKEN_FILE.chmod(0o600)


def authorize() -> None:
    client = load_client()
    code_holder: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code_holder.update({k: v[0] for k, v in query.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Authorised &mdash; you can close this tab.</h2>")

        def log_message(self, *args):
            pass

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = HTTPServer(("127.0.0.1", port), Handler)
    redirect = f"http://localhost:{port}"

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client["client_id"],
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    })
    print(f"Opening browser for consent (redirect on port {port})…")
    subprocess.run(["open", auth_url], check=False)

    server.timeout = 300
    while "code" not in code_holder and "error" not in code_holder:
        server.handle_request()
    server.server_close()
    if "error" in code_holder:
        sys.exit(f"consent failed: {code_holder['error']}")

    tokens = post_form(client["token_uri"], {
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "code": code_holder["code"],
        "grant_type": "authorization_code",
        "redirect_uri": redirect,
    })
    if "refresh_token" not in tokens:
        sys.exit(f"no refresh token in response: {tokens}")
    tokens["expires_at"] = time.time() + tokens.get("expires_in", 0)
    save_tokens(tokens)
    print(f"stored refresh token at {TOKEN_FILE}")


def token() -> None:
    if not TOKEN_FILE.exists():
        sys.exit(f"no token file at {TOKEN_FILE} — run: python3 scripts/google-oauth.py authorize")
    tokens = json.loads(TOKEN_FILE.read_text())
    if tokens.get("expires_at", 0) - time.time() > 120:
        print(tokens["access_token"])
        return
    client = load_client()
    fresh = post_form(client["token_uri"], {
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token",
    })
    tokens["access_token"] = fresh["access_token"]
    tokens["expires_at"] = time.time() + fresh.get("expires_in", 0)
    save_tokens(tokens)
    print(tokens["access_token"])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "authorize":
        authorize()
    elif mode == "token":
        token()
    else:
        sys.exit("usage: google-oauth.py {authorize|token}")
