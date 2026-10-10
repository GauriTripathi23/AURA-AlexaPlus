
from backend.graph.workflow import workflow

from backend.mcp.tool_functions import (
    create_action_plan as create_action_plan_fn,
    complete_preparation_task as complete_preparation_task_fn,
)


def create_action_plan(goal: str) -> dict:
    """Create an actionable plan for the user's goal."""
    return create_action_plan_fn(goal)



def complete_preparation_task(goal: str) -> dict:
    """Complete one preparation task for a specific goal."""
    return complete_preparation_task_fn(goal)



def run_agent(goal: str) -> dict:
    """Run the AURA LangGraph agent and return its complete execution trace."""
    result = workflow.invoke(
        {
            "goal": goal,
            "understanding": "",
            "plan": [],
            "selected_tool": "",
            "selected_tools": [],
            "preparation_status": {},
            "tool_results": {},
            "verification": "",
        }
    )

    return {
        "goal": result["goal"],
        "understanding": result["understanding"],
        "selected_tool": result["selected_tool"],
        "selected_tools": result.get("selected_tools", []),
        "plan": result["plan"],
        "preparation_status": result["preparation_status"],
        "tool_results": result.get("tool_results", {}),
        "verification": result["verification"],
    }


    return {
        "goal": result["goal"],
        "understanding": result["understanding"],
        "selected_tool": result["selected_tool"],
        "plan": result["plan"],
        "preparation_status": result["preparation_status"],
        "verification": result["verification"],
    }