"""Single entrypoint: python -m runner.run_job <job-name>.

Runs preflight, streams the SDK session to logs/<job>/<timestamp>.jsonl,
appends a one-line summary to logs/<job>/history.jsonl (what the dashboard
reads), and exits non-zero on any failure so launchd surfaces it.
"""

from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import json
import subprocess
import sys
import traceback

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from . import preflight
from .config import LOGS_DIR, REPO_ROOT, ConfigError, JobSpec, load_env, load_job, load_mcp_servers

HISTORY_KEEP = 500  # one-line summaries kept per job
RUN_LOG_KEEP_DAYS = 30  # full per-run jsonl logs older than this are pruned

DRY_RUN_SUFFIX = """

---
DRY RUN — report-only. Do everything above EXCEPT writing: do not create,
update, move, or comment on anything in Notion (those tools are blocked and
will be denied — do not retry them). Instead, finish with a report of exactly
what a real run would have done: which meetings would be created (title,
date, attendees, topics, type), each correction that would be applied
(was → now), each ambiguity that would be flagged, and which meetings would
be skipped as already synced."""


def _jsonable(obj):
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {"_type": type(obj).__name__, **dataclasses.asdict(obj)}
    if isinstance(obj, (dt.datetime, dt.date)):
        return obj.isoformat()
    return repr(obj)


def _prune_run_logs(job_dir) -> None:
    cutoff = dt.datetime.now().timestamp() - RUN_LOG_KEEP_DAYS * 86400
    for old in job_dir.glob("*.jsonl"):
        if old.name != "history.jsonl" and old.stat().st_mtime < cutoff:
            old.unlink(missing_ok=True)


def _append_history(job_dir, entry: dict) -> None:
    history = job_dir / "history.jsonl"
    lines = history.read_text().splitlines() if history.exists() else []
    lines.append(json.dumps(entry))
    history.write_text("\n".join(lines[-HISTORY_KEEP:]) + "\n")


async def run(job_name: str, *, dry_run: bool = False) -> int:
    env = load_env()
    spec = load_job(job_name)

    started = dt.datetime.now().astimezone()
    job_dir = LOGS_DIR / spec.name
    job_dir.mkdir(parents=True, exist_ok=True)
    run_log = job_dir / f"{started.strftime('%Y-%m-%dT%H-%M-%S')}.jsonl"
    _prune_run_logs(job_dir)

    def finish(status: str, *, result: ResultMessage | None = None, error: str | None = None) -> int:
        ended = dt.datetime.now().astimezone()
        summary = {
            "ts": started.isoformat(timespec="seconds"),
            "job": spec.name,
            "status": status,
            "duration_s": round((ended - started).total_seconds(), 1),
            "cost_usd": getattr(result, "total_cost_usd", None),
            "num_turns": getattr(result, "num_turns", None),
            "result": (getattr(result, "result", None) or error or "")[:300],
            "log": run_log.name,
        }
        _append_history(job_dir, summary)
        print(f"[{spec.name}] {status} in {summary['duration_s']}s — {run_log}")
        return 0 if status in ("ok", "dry_run_ok", "skipped_no_work") else 1

    with run_log.open("w") as log:
        def emit(record: dict) -> None:
            log.write(json.dumps(record, default=_jsonable) + "\n")
            log.flush()

        emit({"event": "start", "job": spec.name, "ts": started.isoformat(),
              "dry_run": dry_run})

        try:
            checks = preflight.run_checks(spec, env)
            emit({"event": "preflight", "checks": checks})
        except (preflight.PreflightError, ConfigError) as err:
            emit({"event": "error", "stage": "preflight", "error": str(err)})
            print(f"[{spec.name}] preflight failed: {err}", file=sys.stderr)
            return finish("preflight_failed", error=str(err))

        # Cheap pre-check: a small read-only probe decides whether the full
        # session is needed at all. NO_WORK skips the run; anything else —
        # including a probe failure — falls through to the real run (fail-open).
        precheck_prompt = spec.load_precheck(env)
        if precheck_prompt and not dry_run:
            pre_options = ClaudeAgentOptions(
                cwd=str(REPO_ROOT),
                mcp_servers=load_mcp_servers(spec.mcp_servers, env),
                allowed_tools=spec.allowed_tools,
                disallowed_tools=spec.dry_run_disallowed,  # probe never writes
                permission_mode=spec.permission_mode,
                model=spec.precheck_model,
                max_turns=spec.precheck_max_turns,
            )
            pre_result: ResultMessage | None = None
            try:
                async for message in query(prompt=precheck_prompt, options=pre_options):
                    emit({"event": "precheck_message", "message": message})
                    if isinstance(message, ResultMessage):
                        pre_result = message
            except Exception as err:
                emit({"event": "error", "stage": "precheck_probe", "error": str(err)})
            verdict = (getattr(pre_result, "result", None) or "").strip()
            if verdict and verdict.splitlines()[-1].strip() == "NO_WORK":
                return finish("skipped_no_work", result=pre_result)

        options = ClaudeAgentOptions(
            cwd=str(REPO_ROOT),
            mcp_servers=load_mcp_servers(spec.mcp_servers, env),
            allowed_tools=spec.allowed_tools,
            disallowed_tools=spec.dry_run_disallowed if dry_run else [],
            permission_mode=spec.permission_mode,
            model=spec.model,
            setting_sources=["project"],  # loads .claude/skills/ from this repo
            max_turns=spec.max_turns,
        )

        prompt = spec.load_prompt(env)
        if dry_run:
            prompt += DRY_RUN_SUFFIX

        result: ResultMessage | None = None
        try:
            async for message in query(prompt=prompt, options=options):
                emit({"event": "message", "message": message})
                if isinstance(message, ResultMessage):
                    result = message
        except Exception as err:  # SDK/transport failure — log it, don't swallow it
            emit({"event": "error", "stage": "query", "error": str(err),
                  "traceback": traceback.format_exc()})
            print(f"[{spec.name}] run failed: {err}", file=sys.stderr)
            return finish("error", error=str(err))

        if result is None or result.is_error:
            return finish("error", result=result,
                          error=getattr(result, "result", None) or "no result message")

    if not dry_run:
        _post_run(spec)
    return finish("dry_run_ok" if dry_run else "ok", result=result)


def _post_run(spec: JobSpec) -> None:
    if not spec.post_run_open:
        return
    target = REPO_ROOT / spec.post_run_open
    if target.exists():
        subprocess.run(["open", "-a", spec.browser, str(target)], check=False)


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry_run = "--dry-run" in sys.argv[1:]
    if len(args) != 1:
        print("usage: python -m runner.run_job <job-name> [--dry-run]", file=sys.stderr)
        sys.exit(2)
    sys.exit(asyncio.run(run(args[0], dry_run=dry_run)))


if __name__ == "__main__":
    main()
