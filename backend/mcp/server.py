from mcp.server.fastmcp import FastMCP

from backend.mcp.tools import create_action_plan


mcp = FastMCP("AURA")


@mcp.tool()
def action_plan(goal: str) -> dict:
    """
    Create an actionable plan for a user's goal.
    """
    return create_action_plan(goal)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")