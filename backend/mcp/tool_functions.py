
import json
import re
from pathlib import Path


DEFAULT_TOTAL_TASKS = 5

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = PROJECT_ROOT / "data" / "preparation_state.json"



def get_goal_key(goal: str) -> str:
    """Normalize requests so the same goal shares one progress counter."""
    text = re.sub(r"[^a-z0-9\s]", " ", (goal or "").lower())
    text = re.sub(r"\s+", " ", text).strip()

    # Remove a trailing status request from a compound command.
    text = re.sub(
        r"\s+(?:and|then)\s+(?:please\s+)?(?:also\s+)?"
        r"(?:check|show|get|view|tell me|give me|display)\s+"
        r"(?:my\s+)?(?:preparation\s+)?"
        r"(?:progress|status|readiness)\b.*$",
        "",
        text,
    ).strip()

    prefixes = (
        "i finished a preparation task for ",
        "i completed a preparation task for ",
        "i finished a task for ",
        "i completed a task for ",
        "am i prepared for ",
        "am i ready for ",
        "check my preparation for ",
        "check preparation status for ",
        "i want to prepare for ",
        "prepare for ",
    )

    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    if text.startswith("my "):
        text = text[3:].strip()

    for suffix in (" tomorrow", " today"):
        if text.endswith(suffix):
            text = text[:-len(suffix)].strip()

    if not text or text in {
        "task",
        "preparation task",
        "a preparation task",
        "i finished a preparation task",
    }:
        return "general preparation"

    return text



def load_preparation_state() -> dict:
    """Load saved progress, migrating the earlier single-counter format."""
    if not STATE_FILE.exists():
        return {"goals": {}}

    try:
        saved = json.loads(STATE_FILE.read_text(encoding="utf-8"))

        # Current format: progress stored separately for each goal.
        if isinstance(saved, dict) and isinstance(saved.get("goals"), dict):
            goals = {}

            for key, value in saved["goals"].items():
                if not isinstance(value, dict):
                    continue

                try:
                    total = int(value.get("total_tasks", DEFAULT_TOTAL_TASKS))
                    completed = int(value.get("completed_tasks", 0))
                except (TypeError, ValueError):
                    continue

                if total < 1 or completed < 0:
                    continue

                goals[str(key)] = {
                    "completed_tasks": min(completed, total),
                    "total_tasks": total,
                }

            return {"goals": goals}

        # Migrate the earlier format without discarding its progress.
        if isinstance(saved, dict) and "completed_tasks" in saved:
            total = int(saved.get("total_tasks", DEFAULT_TOTAL_TASKS))
            completed = int(saved.get("completed_tasks", 0))

            if total >= 1 and completed >= 0:
                return {
                    "goals": {
                        "general preparation": {
                            "completed_tasks": min(completed, total),
                            "total_tasks": total,
                        }
                    }
                }

    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        pass

    return {"goals": {}}


PREPARATION_STATE = load_preparation_state()


def save_preparation_state() -> None:
    """Persist progress to the local JSON file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = STATE_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(PREPARATION_STATE, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(STATE_FILE)


def get_preparation_status(goal: str) -> dict:
    """Return progress for the requested goal only."""
    goal_key = get_goal_key(goal)
    state = PREPARATION_STATE["goals"].get(
        goal_key,
        {
            "completed_tasks": 0,
            "total_tasks": DEFAULT_TOTAL_TASKS,
        },
    )

    completed = state["completed_tasks"]
    total = state["total_tasks"]
    remaining = total - completed

    return {
        "goal": goal,
        "goal_key": goal_key,
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


def complete_preparation_task(
    goal: str = "general preparation",
) -> dict:
    """Complete one task for a specific goal and save the progress."""
    goal_key = get_goal_key(goal)

    state = PREPARATION_STATE["goals"].setdefault(
        goal_key,
        {
            "completed_tasks": 0,
            "total_tasks": DEFAULT_TOTAL_TASKS,
        },
    )

    if state["completed_tasks"] < state["total_tasks"]:
        state["completed_tasks"] += 1
        save_preparation_state()

    completed = state["completed_tasks"]
    remaining = state["total_tasks"] - completed

    return {
        "goal_key": goal_key,
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