"""Weekday 08:00 morning brief (read-only across connectors; writes one HTML file)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runner.config import JobSpec

JOB = JobSpec(
    name="morning_brief",
    description="Render the styled HTML morning brief from calendar, email, "
                "chat and tracker connectors",
    mcp_servers=["gcal", "gmail", "slack", "linear", "notion", "granola", "box"],
    allowed_tools=[
        "Skill",
        "Read",
        "Write(logs/morning_brief/**)",
        "mcp__gcal",
        "mcp__gmail",
        "mcp__slack",
        "mcp__linear",
        "mcp__notion",
        "mcp__granola",
        "mcp__box",
    ],
    required_env=[
        "USER_FIRST_NAME",
        "HOME_TIMEZONE",
        "SLACK_BOT_TOKEN",
        "SLACK_TEAM_ID",
        "GOOGLE_OAUTH_CREDENTIALS",
    ],
    post_run_open="logs/morning_brief/latest.html",
    browser="Firefox",
)
