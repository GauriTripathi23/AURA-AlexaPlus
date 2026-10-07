from backend.graph.workflow import workflow


def create_action_plan(goal: str) -> dict:
    """
    Create an actionable plan for a user's goal
    using the AURA LangGraph workflow.
    """

    result = workflow.invoke(
        {
            "goal": goal,
            "plan": [],
        }
    )

    return {
        "goal": goal,
        "plan": result["plan"],
    }