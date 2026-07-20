"""Weekday 08:00 morning brief (read-only across connectors; writes one HTML file)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runner.config import JobSpec

_REPO = Path(__file__).resolve().parents[2]

JOB = JobSpec(
    name="morning_brief",
    description="Render the styled HTML morning brief from calendar, email, "
    "chat and tracker connectors",
    mcp_servers=["gcal", "gmail", "slack", "linear", "notion", "granola"],
    allowed_tools=[
        "Skill",
        "Read",
        # Path-scoped Write(...) rules are ignored by the SDK's allowed_tools
        # (proven by probes 2026-07-20): plain Write + acceptEdits is the only
        # combination that works headless. The artifact check in run_job and
        # the prompt confine what actually gets written.
        "Write",
        "mcp__gcal",
        "mcp__gmail",
        "mcp__slack",
        "mcp__linear",
        "mcp__notion",
        "mcp__granola",
    ],
    permission_mode="acceptEdits",
    required_env=[
        "USER_FIRST_NAME",
        "HOME_TIMEZONE",
    ],
    post_run_open="logs/morning_brief/latest.html",
    browser="Firefox",
)
