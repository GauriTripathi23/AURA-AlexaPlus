
import re


def normalize_goal(goal: str) -> str:
    """Normalize user input before intent classification."""
    return re.sub(r"\s+", " ", (goal or "").lower()).strip()


def _asks_to_complete(text: str) -> bool:
    """Detect requests to mark a preparation task complete."""
    patterns = [
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
    return any(re.search(pattern, text) for pattern in patterns)


def _asks_for_status(text: str) -> bool:
    """Detect requests to inspect progress or readiness."""
    patterns = [
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
    return any(re.search(pattern, text) for pattern in patterns)


def _asks_for_plan(text: str) -> bool:
    """Detect an explicit request to create a plan."""
    patterns = [
        r"\bplan\b",
        r"\bmake\s+(?:me\s+)?a\s+plan\b",
        r"\bcreate\s+(?:me\s+)?a\s+plan\b",
        r"\bbreak\s+(?:it|this|that|my\s+goal)\s+down\b",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def select_tools(goal: str) -> list[str]:
    """
    Select an ordered sequence of tools for the user's request.

    Explicit compound requests can execute multiple tools in order.
    Single-intent requests continue to select one tool.
    """
    text = normalize_goal(goal)

    if not text:
        return ["create_action_plan"]

    wants_completion = _asks_to_complete(text)
    wants_status = _asks_for_status(text)
    wants_plan = _asks_for_plan(text)

    selected = []

    # Complete first when requested, then check the updated progress
    # if the user also asks for a status update.
    if wants_completion:
        selected.append("complete_preparation_task")

        if wants_status:
            selected.append("get_preparation_status")

        return selected

    # If the user explicitly asks for a plan and a status check,
    # generate the plan first and check status second.
    if wants_plan and wants_status:
        return ["create_action_plan", "get_preparation_status"]

    if wants_status:
        return ["get_preparation_status"]

    return ["create_action_plan"]


def select_tool(goal: str) -> str:
    """Backward-compatible helper returning the first selected tool."""
    return select_tools(goal)[0]
