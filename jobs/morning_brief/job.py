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
        # Both forms: the agent writes absolute paths, which the relative
        # gitignore-style rule does not match (proven in the first live run).
        "Write(logs/morning_brief/**)",
        f"Write(/{_REPO}/logs/morning_brief/**)",
        "mcp__gcal",
        "mcp__gmail",
        "mcp__slack",
        "mcp__linear",
        "mcp__notion",
        "mcp__granola",
    ],
    required_env=[
        "USER_FIRST_NAME",
        "HOME_TIMEZONE",
    ],
    post_run_open="logs/morning_brief/latest.html",
    browser="Firefox",
)
