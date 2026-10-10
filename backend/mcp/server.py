
from mcp.server.fastmcp import FastMCP

from backend.mcp.tools import (
    create_action_plan,
    complete_preparation_task,
)

mcp = FastMCP("AURA")


@mcp.tool()
def action_plan(goal: str) -> dict:
    """Create an actionable plan for a user's goal."""
    return create_action_plan(goal)


@mcp.tool()
def mark_preparation_task_complete() -> dict:
    """Mark one preparation task as completed."""
    return complete_preparation_task()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")