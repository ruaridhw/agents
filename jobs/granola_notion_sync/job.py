"""Hourly Granola → Notion meeting sync (writes to Notion; create-only)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runner.config import JobSpec

JOB = JobSpec(
    name="granola_notion_sync",
    description="Sync last-7-days Granola meetings into the Notion Meetings DB, "
    "wiki-correcting mishearings first",
    model="claude-sonnet-5",  # mechanical sync work — Opus not needed
    max_turns=60,  # runaway guard; healthy runs stay well under
    mcp_servers=["granola", "notion"],
    allowed_tools=[
        "Skill",
        "Read",
        "Grep",
        "Glob",
        "mcp__granola",
        "mcp__notion",
        # For the chained notion-todoist-tasks fast pass: Todoist REST goes
        # through the wrapper, which takes the token from its own env.
        "Bash(scripts/todoist-api.sh:*)",
        "Bash(./scripts/todoist-api.sh:*)",
        "Bash(python3:*)",
    ],
    required_env=[
        "GRANOLA_ACCOUNT_EMAIL",
        "NOTION_MEETINGS_PAGE_ID",
        "NOTION_MEETINGS_DATA_SOURCE_ID",
        # Chained task sync
        "NOTION_TASKS_DATA_SOURCE_ID",
        "TODOIST_PROJECT_ID",
        "TODOIST_TOKEN",
        "USER_FULL_NAME",
    ],
    required_paths=["academy/wiki"],
    dry_run_disallowed=[
        "mcp__notion__notion-create-pages",
        "mcp__notion__notion-update-page",
        "mcp__notion__notion-create-database",
        "mcp__notion__notion-update-data-source",
        "mcp__notion__notion-move-pages",
        "mcp__notion__notion-duplicate-page",
        "mcp__notion__notion-create-comment",
    ],
)
