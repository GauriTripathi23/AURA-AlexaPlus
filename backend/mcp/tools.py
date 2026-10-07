from backend.graph.workflow import workflow
from backend.mcp.tool_functions import get_preparation_status


def create_action_plan(goal: str) -> dict:
    """
    Create an actionable plan for a user's goal
    using the AURA LangGraph workflow.
    """

    result = workflow.invoke(
        {
            "goal": goal,
            "understanding": "",
            "plan": [],
            "preparation_status": {},
            "verification": "",
        }
    )

    return {
        "goal": goal,
        "understanding": result["understanding"],
        "plan": result["plan"],
        "preparation_status": result["preparation_status"],
        "verification": result["verification"],
    }