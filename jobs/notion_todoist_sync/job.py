"""Daily full-mode Notion Tasks ↔ Todoist reconciliation (writes to both)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runner.config import JobSpec

JOB = JobSpec(
    name="notion_todoist_sync",
    description="Re-scan all Notion meeting pages for action items, diff into "
                "the Tasks DB, and sync both directions with Todoist",
    mcp_servers=["notion"],
    allowed_tools=[
        "Skill",
        "Read",
        "Grep",
        "Glob",
        # Todoist has no MCP: the skill drives its REST API via curl, with the
        # token fetched from 1Password (op) bootstrapped off the Keychain.
        "Bash(security find-generic-password:*)",
        "Bash(op read:*)",
        "Bash(curl:*)",
        "Bash(python3:*)",  # Sync Key sha1 hashing
        "mcp__notion",
    ],
    required_env=[
        "NOTION_MEETINGS_PAGE_ID",
        "NOTION_MEETINGS_DATA_SOURCE_ID",
        "NOTION_TASKS_DATA_SOURCE_ID",
        "TODOIST_PROJECT_ID",
        "TODOIST_TOKEN_OP_REF",
        "USER_FULL_NAME",
    ],
    dry_run_disallowed=[
        "mcp__notion__notion-create-pages",
        "mcp__notion__notion-update-page",
        "mcp__notion__notion-create-database",
        "mcp__notion__notion-update-data-source",
        "mcp__notion__notion-move-pages",
        "mcp__notion__notion-duplicate-page",
        "mcp__notion__notion-create-comment",
        # Blocks ALL Todoist calls (reads too) — a dry run reports Notion-side
        # diffs only, since curl can't be write-scoped by tool name.
        "Bash(curl:*)",
    ],
)
