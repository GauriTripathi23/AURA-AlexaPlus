def select_tool(goal: str) -> str:
    """
    Select the most appropriate AURA tool
    based on the user's goal.
    """

    goal_lower = goal.lower()

    if any(word in goal_lower for word in [
        "complete task",
        "finish task",
        "mark complete",
        "done with",
        "finished a",
        "finished the",

    ]):
        return "complete_preparation_task"

    status_keywords = [
        "prepared",
        "preparation",
        "ready",
        "progress",
        "status",
        "completed",
        "done",
    ]

    if any(word in goal_lower for word in status_keywords):
        return "get_preparation_status"

    return "create_action_plan"