
PREPARATION_STATE = {
    "completed_tasks": 0,
    "total_tasks": 5,
}


def get_preparation_status(goal: str) -> dict:
    completed = PREPARATION_STATE["completed_tasks"]
    total = PREPARATION_STATE["total_tasks"]
    remaining = total - completed

    return {
        "goal": goal,
        "status": (
            "Preparation completed" if remaining == 0
            else "Preparation in progress" if completed > 0
            else "Preparation has not started"
        ),
        "completed_tasks": completed,
        "remaining_tasks": remaining,
        "message": (
            "All preparation tasks are complete."
            if remaining == 0
            else f"{remaining} preparation tasks remain."
        ),
    }


def complete_preparation_task() -> dict:
    if PREPARATION_STATE["completed_tasks"] < PREPARATION_STATE["total_tasks"]:
        PREPARATION_STATE["completed_tasks"] += 1

    completed = PREPARATION_STATE["completed_tasks"]
    remaining = PREPARATION_STATE["total_tasks"] - completed

    return {
        "completed_tasks": completed,
        "remaining_tasks": remaining,
        "message": (
            "Preparation task completed successfully."
            if remaining > 0
            else "All preparation tasks are complete."
        ),
    }


def create_action_plan(goal: str) -> dict:
    plan = [
        f"Understand the objective: {goal}",
        "Break the objective into smaller actionable tasks",
        "Identify the required tools and resources",
        "Execute the required actions",
        "Review the result and identify missing steps",
    ]

    return {
        "goal": goal,
        "plan": plan,
        "message": "Action plan created successfully.",
    }