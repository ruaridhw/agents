"""Repo paths, .env loading, ${VAR} resolution, job specs, MCP config."""

from __future__ import annotations

import importlib.util
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JOBS_DIR = REPO_ROOT / "jobs"
LOGS_DIR = REPO_ROOT / "logs"
MCP_TEMPLATE = REPO_ROOT / "mcp" / "servers.template.json"

_PLACEHOLDER = re.compile(r"\$\{([A-Z0-9_]+)\}")


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


def resolve(text: str, env: dict[str, str], *, context: str) -> str:
    """Replace ${VAR} placeholders; a missing variable is a hard error."""

    def _sub(match: re.Match) -> str:
        name = match.group(1)
        if name not in env or env[name] == "":
            raise ConfigError(
                f"{context}: ${{{name}}} is not set — add it to .env "
                f"(see .env.example)"
            )
        return env[name]

    return _PLACEHOLDER.sub(_sub, text)


@dataclass
class JobSpec:
    name: str
    description: str
    mcp_servers: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    permission_mode: str = "default"
    max_turns: int | None = None
    required_env: list[str] = field(default_factory=list)
    required_paths: list[str] = field(default_factory=list)
    # Repo-relative file to `open -a <browser>` after a successful run.
    post_run_open: str | None = None
    browser: str = "Firefox"

    @property
    def prompt_path(self) -> Path:
        return JOBS_DIR / self.name / "prompt.md"

    def load_prompt(self, env: dict[str, str]) -> str:
        raw = self.prompt_path.read_text()
        return resolve(raw, env, context=f"jobs/{self.name}/prompt.md")


def load_job(name: str) -> JobSpec:
    job_py = JOBS_DIR / name / "job.py"
    if not job_py.exists():
        available = sorted(p.parent.name for p in JOBS_DIR.glob("*/job.py"))
        raise ConfigError(f"unknown job {name!r} — available: {', '.join(available)}")
    module_spec = importlib.util.spec_from_file_location(f"jobs.{name}", job_py)
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
        raw = json.dumps(servers[name])
        resolved[name] = json.loads(resolve(raw, env, context=f"mcp server {name!r}"))
    return resolved
