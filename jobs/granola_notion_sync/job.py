"""Hourly Granola → Notion meeting sync (writes to Notion; create-only)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runner.config import JobSpec

JOB = JobSpec(
    name="granola_notion_sync",
    description="Sync last-7-days Granola meetings into the Notion Meetings DB, "
                "wiki-correcting mishearings first",
    mcp_servers=["granola", "notion"],
    allowed_tools=[
        "Skill",
        "Read",
        "Grep",
        "Glob",
        "mcp__granola",
        "mcp__notion",
    ],
    required_env=[
        "GRANOLA_ACCOUNT_EMAIL",
        "NOTION_MEETINGS_PAGE_ID",
        "NOTION_MEETINGS_DATA_SOURCE_ID",
    ],
    required_paths=["academy/wiki"],
)
