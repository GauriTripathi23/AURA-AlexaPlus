import json
from pathlib import Path


DEFAULT_STATE = {
    "completed_tasks": 0,
    "total_tasks": 5,
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = PROJECT_ROOT / "data" / "preparation_state.json"


def load_preparation_state() -> dict:
    """Load saved progress, or use the default state."""
    if not STATE_FILE.exists():
        return DEFAULT_STATE.copy()

    try:
        saved = json.loads(STATE_FILE.read_text(encoding="utf-8"))

        total = int(saved.get("total_tasks", 5))
        completed = int(saved.get("completed_tasks", 0))

        if total < 1 or completed < 0:
            return DEFAULT_STATE.copy()

        return {
            "completed_tasks": min(completed, total),
            "total_tasks": total,
        }

    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return DEFAULT_STATE.copy()


PREPARATION_STATE = load_preparation_state()


def save_preparation_state() -> None:
    """Persist progress to a local JSON file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = STATE_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(PREPARATION_STATE, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(STATE_FILE)


def get_preparation_status(goal: str) -> dict:
    """Check the user's current preparation status."""
    completed = PREPARATION_STATE["completed_tasks"]
    total = PREPARATION_STATE["total_tasks"]
    remaining = total - completed

    return {
        "goal": goal,
        "status": (
            "Preparation completed"
            if remaining == 0
            else "Preparation in progress"
            if completed > 0
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
    """Complete one task and save the updated progress."""
    if PREPARATION_STATE["completed_tasks"] < PREPARATION_STATE["total_tasks"]:
        PREPARATION_STATE["completed_tasks"] += 1
        save_preparation_state()

    completed = PREPARATION_STATE["completed_tasks"]
    remaining = PREPARATION_STATE["total_tasks"] - completed

    return {
        "completed_tasks": completed,
        "remaining_tasks": remaining,
        "message": (
            "All preparation tasks are complete."
            if remaining == 0
            else "Preparation task completed successfully."
        ),
    }


def create_action_plan(goal: str) -> dict:
    """Create a practical action plan for a user's goal."""
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