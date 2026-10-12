
import json
import re
from pathlib import Path
from typing import Optional


DEFAULT_TOTAL_TASKS = 5

# Project root: AURA-AlexaPlus/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = PROJECT_ROOT / "data" / "preparation_state.json"


def get_goal_key(goal: str) -> str:
    """Normalize related requests to one stable goal key."""
    text = re.sub(r"[^a-z0-9\s]", " ", (goal or "").lower())
    text = re.sub(r"\s+", " ", text).strip()

    # Remove a trailing request to check progress or status.
    text = re.sub(
        r"\s+(?:and|then)\s+(?:please\s+)?(?:also\s+)?"
        r"(?:check|show|get|view|tell me|give me|display)\s+"
        r"(?:my\s+)?(?:preparation\s+)?"
        r"(?:progress|status|readiness)\b.*$",
        "",
        text,
    ).strip()

    # Normalize numbered task commands, preserving the goal.
    text = re.sub(
        r"^(?:please\s+)?(?:complete|finish)\s+"
        r"task\s*#?\d+\s+(?:for|of|in)\s+",
        "",
        text,
    ).strip()

    text = re.sub(
        r"^(?:please\s+)?mark\s+task\s*#?\d+\s+"
        r"(?:as\s+)?(?:complete|completed|done)\s+(?:for|of|in)\s+",
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
        "create a plan for ",
        "make a plan for ",
        "prepare for ",
        "plan for ",
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

    generic_goals = {
        "",
        "task",
        "preparation task",
        "a preparation task",
        "i finished a preparation task",
        "create a plan",
        "make a plan",
        "check progress",
        "check status",
    }

    if text in generic_goals:
        return "general preparation"

    return text


def task_titles_for_goal(goal_key: str) -> list[str]:
    """Return a starter checklist appropriate to the goal."""
    key = goal_key.lower()

    if any(
        word in key
        for word in ("hackathon", "presentation", "pitch", "demo")
    ):
        return [
            "Finalize the problem statement and target user",
            "Prepare the solution architecture and key workflow",
            "Build and test the demo end to end",
            "Prepare slides covering innovation, implementation, and impact",
            "Rehearse the pitch and prepare for judge questions",
        ]

    if any(word in key for word in ("exam", "test", "study")):
        return [
            "List the syllabus topics and exam deadlines",
            "Prioritize difficult and high-weight topics",
            "Study the first priority topic and make concise notes",
            "Solve practice questions and review mistakes",
            "Take a timed self-test and revise weak areas",
        ]

    return [
        "Define the goal and intended outcome",
        "Break the goal into smaller actionable tasks",
        "Gather the tools, information, and resources needed",
        "Complete the highest-priority action",
        "Review progress and identify the next step",
    ]


def make_tasks(
    goal_key: str,
    total_tasks: int = DEFAULT_TOTAL_TASKS,
    completed_tasks: int = 0,
    saved_tasks: Optional[list] = None,
) -> list[dict]:
    """Build checklist records, preserving saved completion states."""
    total_tasks = max(1, total_tasks)
    completed_tasks = max(0, min(completed_tasks, total_tasks))

    if isinstance(saved_tasks, list) and saved_tasks:
        tasks = []

        for index, item in enumerate(saved_tasks[:total_tasks], start=1):
            if isinstance(item, dict) and isinstance(item.get("title"), str):
                tasks.append({
                    "id": index,
                    "title": item["title"],
                    "completed": bool(item.get("completed", False)),
                })
            elif isinstance(item, str):
                tasks.append({
                    "id": index,
                    "title": item,
                    "completed": index <= completed_tasks,
                })

        if tasks:
            defaults = task_titles_for_goal(goal_key)

            while len(tasks) < total_tasks:
                index = len(tasks)
                tasks.append({
                    "id": index + 1,
                    "title": defaults[index % len(defaults)],
                    "completed": False,
                })

            return tasks

    titles = task_titles_for_goal(goal_key)

    return [
        {
            "id": index + 1,
            "title": titles[index % len(titles)],
            "completed": index < completed_tasks,
        }
        for index in range(total_tasks)
    ]


def load_preparation_state() -> dict:
    """Load saved state and migrate older counter-only records."""
    if not STATE_FILE.exists():
        return {"goals": {}}

    try:
        saved = json.loads(STATE_FILE.read_text(encoding="utf-8"))

        if isinstance(saved, dict) and isinstance(saved.get("goals"), dict):
            goals = {}

            for key, value in saved["goals"].items():
                if not isinstance(value, dict):
                    continue

                try:
                    total = max(
                        1,
                        int(value.get("total_tasks", DEFAULT_TOTAL_TASKS)),
                    )
                    completed = max(
                        0,
                        int(value.get("completed_tasks", 0)),
                    )
                except (TypeError, ValueError):
                    continue

                tasks = make_tasks(
                    str(key),
                    total_tasks=total,
                    completed_tasks=completed,
                    saved_tasks=value.get("tasks"),
                )

                done = sum(task["completed"] for task in tasks)

                goals[str(key)] = {
                    "total_tasks": len(tasks),
                    "completed_tasks": done,
                    "tasks": tasks,
                }

            return {"goals": goals}

        # Migrate the earlier single-counter data format.
        if isinstance(saved, dict) and "completed_tasks" in saved:
            total = max(
                1,
                int(saved.get("total_tasks", DEFAULT_TOTAL_TASKS)),
            )
            completed = max(0, int(saved.get("completed_tasks", 0)))
            key = "general preparation"
            tasks = make_tasks(key, total, completed)

            return {
                "goals": {
                    key: {
                        "total_tasks": len(tasks),
                        "completed_tasks": sum(
                            task["completed"] for task in tasks
                        ),
                        "tasks": tasks,
                    }
                }
            }

    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        pass

    return {"goals": {}}


PREPARATION_STATE = load_preparation_state()


def save_preparation_state() -> None:
    """Persist state to local JSON storage using a temporary file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = STATE_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(PREPARATION_STATE, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(STATE_FILE)


def ensure_goal_state(goal_key: str) -> dict:
    """Create a checklist for a new goal or normalize existing state."""
    if goal_key not in PREPARATION_STATE["goals"]:
        tasks = make_tasks(goal_key)
        PREPARATION_STATE["goals"][goal_key] = {
            "total_tasks": len(tasks),
            "completed_tasks": 0,
            "tasks": tasks,
        }
        save_preparation_state()

    record = PREPARATION_STATE["goals"][goal_key]

    if not isinstance(record.get("tasks"), list):
        record["tasks"] = make_tasks(
            goal_key,
            record.get("total_tasks", DEFAULT_TOTAL_TASKS),
            record.get("completed_tasks", 0),
        )

    record["completed_tasks"] = sum(
        task.get("completed", False)
        for task in record["tasks"]
    )
    record["total_tasks"] = len(record["tasks"])

    return record


def get_preparation_status(goal: str) -> dict:
    """Return progress counts and individual tasks for a goal."""
    goal_key = get_goal_key(goal)
    record = ensure_goal_state(goal_key)

    tasks = [
        {
            "id": task["id"],
            "title": task["title"],
            "completed": task["completed"],
            "status": "completed" if task["completed"] else "pending",
        }
        for task in record["tasks"]
    ]

    completed = record["completed_tasks"]
    remaining = record["total_tasks"] - completed

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
        "tasks": tasks,
    }


def complete_preparation_task(
    goal: str = "general preparation",
    task_id: Optional[int] = None,
) -> dict:
    """Complete one pending task and persist the change."""
    goal_key = get_goal_key(goal)
    record = ensure_goal_state(goal_key)

    if task_id is not None:
        target = next(
            (task for task in record["tasks"] if task["id"] == task_id),
            None,
        )

        if target is None:
            return {
                "goal_key": goal_key,
                "completed_tasks": record["completed_tasks"],
                "remaining_tasks": (
                    record["total_tasks"] - record["completed_tasks"]
                ),
                "message": f"Task ID {task_id} was not found.",
            }
    else:
        target = next(
            (task for task in record["tasks"] if not task["completed"]),
            None,
        )

    if target is None:
        completed = record["completed_tasks"]
        remaining = record["total_tasks"] - completed

        return {
            "goal_key": goal_key,
            "completed_tasks": completed,
            "remaining_tasks": remaining,
            "message": "All preparation tasks are already complete.",
        }

    if target["completed"]:
        completed = record["completed_tasks"]

        return {
            "goal_key": goal_key,
            "completed_tasks": completed,
            "remaining_tasks": record["total_tasks"] - completed,
            "completed_task": target["title"],
            "message": "This task was already completed.",
        }

    target["completed"] = True
    record["completed_tasks"] = sum(
        task["completed"] for task in record["tasks"]
    )
    save_preparation_state()

    completed = record["completed_tasks"]
    remaining = record["total_tasks"] - completed

    return {
        "goal_key": goal_key,
        "completed_tasks": completed,
        "remaining_tasks": remaining,
        "completed_task": target["title"],
        "message": (
            "All preparation tasks are complete."
            if remaining == 0
            else "Preparation task completed successfully."
        ),
    }


def create_action_plan(goal: str) -> dict:
    """Return an action plan based on the saved goal checklist."""
    goal_key = get_goal_key(goal)
    record = ensure_goal_state(goal_key)

    plan = [task["title"] for task in record["tasks"]]
    save_preparation_state()

    return {
        "goal": goal,
        "goal_key": goal_key,
        "plan": plan,
        "tasks": record["tasks"],
        "message": "Action plan and persistent checklist are ready.",
    }
