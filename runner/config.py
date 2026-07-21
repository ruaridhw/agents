"""Repo paths, .env loading, ${VAR} resolution, job specs, MCP config."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from claude_agent_sdk import PermissionMode

REPO_ROOT = Path(__file__).resolve().parent.parent
JOBS_DIR = REPO_ROOT / "jobs"
LOGS_DIR = REPO_ROOT / "logs"
MCP_TEMPLATE = REPO_ROOT / "mcp" / "servers.template.json"

_PLACEHOLDER = re.compile(r"\$\{([A-Z0-9_]+)\}")

# Placeholders filled by running a command instead of reading .env — for
# short-lived credentials that must never sit in a file. Computed lazily, only
# when a selected server/prompt actually references them.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
COMPUTED_VARS = {
    "GOOGLE_MCP_ACCESS_TOKEN": [
        sys.executable,
        str(_SCRIPTS / "google-oauth.py"),
        "token",
    ],
}


class ConfigError(Exception):
    pass


def load_env() -> dict[str, str]:
    """Parse .env into os.environ (without clobbering) and return the merged view."""
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("'\"")
            os.environ.setdefault(key, value)
    return dict(os.environ)


def _keychain_get(service: str) -> str | None:
    proc = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-w"],
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() or None if proc.returncode == 0 else None


def _keychain_set(service: str, secret: str) -> None:
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-U",
            "-s",
            service,
            "-a",
            "agent-jobs",
            "-w",
            secret,
        ],
        capture_output=True,
        text=True,
    )


def op_read(ref: str, *, context: str = "") -> str:
    """Resolve an op:// secret reference via the 1Password CLI.

    1Password is the source of truth, but `op` is flaky under launchd (times
    out even with a full env — 2026-07-21), so every successful read is
    cached in the macOS Keychain and the cache is the fallback. Keychain
    reads are reliable under launchd (the op-service-account item proves it).
    """
    cache_service = f"agent-jobs-op-cache:{ref}"
    token = _keychain_get("op-service-account")
    if token and not os.environ.get("AGENT_JOBS_FORCE_OP_CACHE"):
        # Inherit the full environment: op needs HOME etc.
        env = dict(os.environ)
        env["OP_SERVICE_ACCOUNT_TOKEN"] = token
        env["PATH"] = env.get("PATH", "") + ":/opt/homebrew/bin:/usr/bin:/bin"
        try:
            proc = subprocess.run(
                ["op", "read", ref],
                capture_output=True,
                text=True,
                timeout=90,
                env=env,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                value = proc.stdout.strip()
                _keychain_set(cache_service, value)
                return value
        except subprocess.TimeoutExpired:
            pass
    cached = _keychain_get(cache_service)
    if cached:
        return cached
    raise ConfigError(
        f"{context}: op read {ref} failed and no keychain cache exists — "
        f"run any job (or `python -m runner.preflight <job>`) interactively "
        f"once to seed the cache"
    )


def resolve(text: str, env: dict[str, str], *, context: str) -> str:
    """Replace ${VAR} placeholders; a missing variable is a hard error.

    A value that is itself an op:// reference is resolved through the
    1Password CLI — lazily, so a job only touches the secrets it uses.
    """

    def _sub(match: re.Match) -> str:
        name = match.group(1)
        if not env.get(name) and name in COMPUTED_VARS:
            proc = subprocess.run(
                COMPUTED_VARS[name],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if proc.returncode != 0:
                raise ConfigError(
                    f"{context}: computing ${{{name}}} failed: "
                    f"{proc.stderr.strip() or proc.stdout.strip()}"
                )
            env[name] = proc.stdout.strip()
        if name not in env or env[name] == "":
            raise ConfigError(
                f"{context}: ${{{name}}} is not set — add it to .env (see .env.example)"
            )
        # Vars named *_OP_REF are pass-by-reference on purpose (the agent
        # op-reads them itself at run time) — never dereference those here.
        if env[name].startswith("op://") and not name.endswith("_OP_REF"):
            env[name] = op_read(env[name], context=f"{context}: ${{{name}}}")
        return env[name]

    return _PLACEHOLDER.sub(_sub, text)


@dataclass
class JobSpec:
    name: str
    description: str
    mcp_servers: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    permission_mode: PermissionMode = "default"
    # SDK model override (e.g. "claude-sonnet-5"); None = subscription default.
    model: str | None = None
    max_turns: int | None = None
    # Model for the cheap pre-check probe (jobs/<name>/precheck.md, if present).
    precheck_model: str = "claude-haiku-4-5-20251001"
    precheck_max_turns: int = 8
    required_env: list[str] = field(default_factory=list)
    required_paths: list[str] = field(default_factory=list)
    # "module:function" run after a successful query, before the artifact
    # check — e.g. deterministic template rendering of agent-written JSON.
    post_render: str | None = None
    # Repo-relative file to `open -a <browser>` after a successful run.
    post_run_open: str | None = None
    browser: str = "Firefox"
    # Tools blocked when running with --dry-run (e.g. the connector's writes).
    dry_run_disallowed: list[str] = field(default_factory=list)

    @property
    def prompt_path(self) -> Path:
        return JOBS_DIR / self.name / "prompt.md"

    @property
    def precheck_path(self) -> Path:
        return JOBS_DIR / self.name / "precheck.md"

    def load_precheck(self, env: dict[str, str]) -> str | None:
        if not self.precheck_path.exists():
            return None
        raw = self.precheck_path.read_text()
        return resolve(raw, env, context=f"jobs/{self.name}/precheck.md")

    def load_prompt(self, env: dict[str, str]) -> str:
        raw = self.prompt_path.read_text()
        return resolve(raw, env, context=f"jobs/{self.name}/prompt.md")


def load_job(name: str) -> JobSpec:
    job_py = JOBS_DIR / name / "job.py"
    if not job_py.exists():
        available = sorted(p.parent.name for p in JOBS_DIR.glob("*/job.py"))
        raise ConfigError(f"unknown job {name!r} — available: {', '.join(available)}")
    module_spec = importlib.util.spec_from_file_location(f"jobs.{name}", job_py)
    if module_spec is None or module_spec.loader is None:
        raise ConfigError(f"could not load jobs/{name}/job.py as a module")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    job: JobSpec = module.JOB
    if job.name != name:
        raise ConfigError(f"jobs/{name}/job.py declares name {job.name!r}")
    return job


def load_mcp_servers(names: list[str], env: dict[str, str]) -> dict:
    """Return the subset of the MCP template this job needs, ${VAR}s resolved.

    Only the selected servers are resolved, so a job never fails on secrets
    belonging to connectors it doesn't use.
    """
    template = json.loads(MCP_TEMPLATE.read_text())
    servers = template["servers"]
    missing = [n for n in names if n not in servers]
    if missing:
        raise ConfigError(f"MCP servers not in {MCP_TEMPLATE.name}: {missing}")
    resolved = {}
    for name in names:
        cfg = servers[name]
        if cfg.get("type") == "sdk":
            # In-process server: import "module:factory" and instantiate.
            module_name, _, factory_name = cfg["factory"].partition(":")
            module = importlib.import_module(module_name)
            resolved[name] = getattr(module, factory_name)()
            continue
        raw = json.dumps(cfg)
        resolved[name] = json.loads(resolve(raw, env, context=f"mcp server {name!r}"))
    return resolved
