"""Fail loudly before a run instead of silently erroring at 08:00.

Checks, in order:
  1. Claude credentials exist (subscription login or ANTHROPIC_API_KEY).
  2. The job's required env vars are set.
  3. The job's required paths resolve (e.g. the academy/ wiki symlink).
  4. Remote MCP hosts for the job are reachable (TCP, not auth).

Usable standalone (`python -m runner.preflight <job>`) or via run_job.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from .config import REPO_ROOT, JobSpec, load_env, load_job, load_mcp_servers

KEYCHAIN_SERVICE = "Claude Code-credentials"
CREDENTIALS_FILE = Path.home() / ".claude" / ".credentials.json"


class PreflightError(Exception):
    pass


def _read_credentials() -> dict | None:
    """Read `claude login` credentials from the macOS keychain or ~/.claude."""
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return json.loads(out.stdout)
    except (OSError, json.JSONDecodeError, subprocess.TimeoutExpired):
        pass
    if CREDENTIALS_FILE.exists():
        try:
            return json.loads(CREDENTIALS_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return None


def check_auth(env: dict[str, str]) -> str:
    if env.get("ANTHROPIC_API_KEY"):
        return "auth: ANTHROPIC_API_KEY set — runs bill pay-as-you-go, not the subscription"
    creds = _read_credentials()
    oauth = (creds or {}).get("claudeAiOauth") or {}
    if not oauth.get("accessToken"):
        raise PreflightError(
            "no Claude credentials found — run `claude login` interactively on "
            "this machine (or set ANTHROPIC_API_KEY in .env)"
        )
    expires_at = oauth.get("expiresAt", 0) / 1000
    if expires_at and expires_at < time.time() and not oauth.get("refreshToken"):
        raise PreflightError(
            "Claude access token is expired and no refresh token is stored — "
            "run `claude login` again"
        )
    return "auth: subscription credentials present"


def check_env(spec: JobSpec, env: dict[str, str]) -> str:
    missing = [v for v in spec.required_env if not env.get(v)]
    if missing:
        raise PreflightError(
            f"missing env vars for {spec.name}: {', '.join(missing)} — "
            f"fill them in .env (see .env.example)"
        )
    return f"env: {len(spec.required_env)} required vars set"


def check_paths(spec: JobSpec) -> str:
    for rel in spec.required_paths:
        path = REPO_ROOT / rel
        if not path.exists():  # a broken symlink also fails exists()
            raise PreflightError(
                f"required path {rel!r} is missing or a broken symlink — "
                f"expected at {path}"
            )
    return f"paths: {len(spec.required_paths)} required paths resolve"


def check_mcp_reachable(spec: JobSpec, env: dict[str, str]) -> str:
    servers = load_mcp_servers(spec.mcp_servers, env)
    unreachable = []
    for name, cfg in servers.items():
        url = cfg.get("url")
        if not url:
            continue  # stdio server — spawned on demand, nothing to probe
        parsed = urlparse(url)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            with socket.create_connection((parsed.hostname, port), timeout=5):
                pass
        except OSError as err:
            unreachable.append(f"{name} ({parsed.hostname}: {err})")
    if unreachable:
        raise PreflightError("MCP hosts unreachable: " + "; ".join(unreachable))
    return f"mcp: {len(servers)} servers configured, remote hosts reachable"


def run_checks(spec: JobSpec, env: dict[str, str]) -> list[str]:
    return [
        check_auth(env),
        check_env(spec, env),
        check_paths(spec),
        check_mcp_reachable(spec, env),
    ]


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python -m runner.preflight <job-name>", file=sys.stderr)
        sys.exit(2)
    env = load_env()
    spec = load_job(sys.argv[1])
    try:
        for line in run_checks(spec, env):
            print(f"ok    {line}")
    except PreflightError as err:
        print(f"FAIL  {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
