from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    goal: str
    plan: list[str]


def create_plan(state: AgentState):
    """
    Create a practical action plan for the user's goal.

    This is the local MVP planner.
    A real LLM can be plugged in later without
    changing the LangGraph architecture.
    """

    goal = state["goal"]

    plan = [
        f"Understand the goal: {goal}",
        "Break the goal into smaller actionable tasks",
        "Identify the tools and resources required",
        "Execute the required actions",
        "Review the progress and identify missing steps",
        "Verify that the goal has been completed",
    ]

    return {
        "plan": plan
    }


# -----------------------------
# Build AURA LangGraph
# -----------------------------

builder = StateGraph(AgentState)

builder.add_node("create_plan", create_plan)

builder.add_edge(START, "create_plan")
builder.add_edge("create_plan", END)

workflow = builder.compile()


# -----------------------------
# Local test
# -----------------------------

if __name__ == "__main__":

    result = workflow.invoke(
        {
            "goal": "Prepare for my hackathon presentation tomorrow",
            "plan": [],
        }
    )

    print("\n===== AURA PLAN =====\n")

    for index, step in enumerate(result["plan"], start=1):
        print(f"{index}. {step}")