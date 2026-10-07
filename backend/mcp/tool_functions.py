def get_preparation_status(goal: str) -> dict:
    """
    Check the user's current preparation status.
    """

    return {
        "goal": goal,
        "status": "Preparation has not started",
        "completed_tasks": 0,
        "remaining_tasks": 5,
        "message": "The user needs to begin preparation."
    }
