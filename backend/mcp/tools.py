
from backend.graph.workflow import workflow

from backend.mcp.tool_functions import (
    create_action_plan as create_action_plan_fn,
    complete_preparation_task as complete_preparation_task_fn,
)


def create_action_plan(goal: str) -> dict:
    """Create an actionable plan for the user's goal."""
    return create_action_plan_fn(goal)


def complete_preparation_task() -> dict:
    """Mark one preparation task as completed."""
    return complete_preparation_task_fn()


def run_agent(goal: str) -> dict:
    """Run the AURA LangGraph agent for a user's goal."""
    result = workflow.invoke(
        {
            "goal": goal,
            "understanding": "",
            "plan": [],
            "selected_tool": "",
            "preparation_status": {},
            "verification": "",
        }
    )

    return {
        "goal": result["goal"],
        "understanding": result["understanding"],
        "selected_tool": result["selected_tool"],
        "plan": result["plan"],
        "preparation_status": result["preparation_status"],
        "verification": result["verification"],
    }