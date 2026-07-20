"""Phase-1 auth spike: proves headless subscription auth + launchd wiring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from runner.config import JobSpec

JOB = JobSpec(
    name="hello",
    description="Trivial SDK round-trip to verify auth and scheduling",
    mcp_servers=[],
    allowed_tools=[],
    max_turns=1,
)
