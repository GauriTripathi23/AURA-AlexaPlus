
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