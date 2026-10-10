
from mcp.server.fastmcp import FastMCP

from backend.mcp.tools import (
    create_action_plan,
    complete_preparation_task,
    run_agent,
)

mcp = FastMCP("AURA")


@mcp.tool()
def action_plan(goal: str) -> dict:
    """Create an actionable plan for the user's goal."""
    return create_action_plan(goal)



@mcp.tool()
def mark_preparation_task_complete(goal: str) -> dict:
    """Mark one preparation task as completed for a specific goal."""
    return complete_preparation_task(goal)


@mcp.tool()
def run_aura_agent(goal: str) -> dict:
    """Run the AURA LangGraph agent for a user's goal."""
    return run_agent(goal)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")