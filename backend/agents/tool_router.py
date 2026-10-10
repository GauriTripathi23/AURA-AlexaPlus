
import re


def normalize_goal(goal: str) -> str:
    """Normalize user input before classifying the intent."""
    return re.sub(r"\s+", " ", goal.lower()).strip()


def select_tool(goal: str) -> str:
    """
    Route a user's request to the appropriate AURA tool.

    Completion intent is checked first so phrases such as
    'I completed a task' are not mistaken for status queries.
    """
    text = normalize_goal(goal)

    if not text:
        return "create_action_plan"

    # 1. Requests that explicitly complete or mark a task done.
    completion_patterns = [
        r"\b(?:i\s+)?(?:have\s+)?(?:just\s+)?"
        r"(?:completed|finished)\s+"
        r"(?:a|the|one|another|my)?\s*"
        r"(?:preparation\s+)?task\b",

        r"\b(?:complete|finish)\s+"
        r"(?:a|the|one|another|my)?\s*"
        r"(?:preparation\s+)?task\b",

        r"\b(?:mark|set)\s+"
        r"(?:this|that|the|my)?\s*task\s+"
        r"(?:as\s+)?(?:complete|completed|done)\b",

        r"\b(?:i'?m|i am)\s+done\s+with\s+"
        r"(?:the\s+)?(?:preparation\s+)?task\b",

        r"\btask\s+(?:is\s+)?(?:complete|completed|done)\b",
    ]

    if any(re.search(pattern, text) for pattern in completion_patterns):
        return "complete_preparation_task"

    # 2. Requests to inspect progress or readiness.
    status_patterns = [
        r"\bprepared\b",
        r"\bpreparation\s+(?:status|progress)\b",
        r"\bcheck\s+(?:my\s+)?progress\b",
        r"\b(?:check|show|get|view)\s+(?:my\s+)?status\b",
        r"\b(?:progress|status|remaining|left)\b",
        r"\bready\b",
        r"\bhow\s+many\s+tasks?\b",
        r"\bwhat\s+(?:is|are)\s+(?:left|remaining)\b",
        r"\bwhat\s+have\s+i\s+completed\b",
        r"\bhow\s+much\s+(?:have\s+i\s+)?(?:finished|completed)\b",
        r"\bam\s+i\s+(?:done|finished|ready)\b",
    ]

    if any(re.search(pattern, text) for pattern in status_patterns):
        return "get_preparation_status"

    # 3. Default to creating a plan for other goals.
    return "create_action_plan"
