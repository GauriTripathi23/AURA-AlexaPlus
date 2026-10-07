from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from backend.mcp.tool_functions import get_preparation_status

# ---------------------------------
# AURA Agent State
# ---------------------------------

class AgentState(TypedDict):
    goal: str
    understanding: str
    plan: list[str]
    preparation_status: dict
    verification: str


# ---------------------------------
# 1. Understand the Goal
# ---------------------------------

def understand_goal(state: AgentState):

    goal = state["goal"]

    return {
        "understanding": (
            f"AURA understood the user's goal as: {goal}"
        )
    }


# ---------------------------------
# 2. Create an Action Plan
# ---------------------------------

def create_plan(state: AgentState):

    plan = [
        "Understand the user's objective and expected outcome",
        "Break the objective into practical actionable tasks",
        "Identify the tools and resources required",
        "Execute the required actions",
        "Review the result for missing or incomplete steps",
    ]

    return {
        "plan": plan
    }


# ---------------------------------
# 3. Check Preparation Status
# ---------------------------------

def check_preparation(state: AgentState):

    result = get_preparation_status(state["goal"])

    return {
        "preparation_status": result
    }


# ---------------------------------
# 4. Verify the Result
# ---------------------------------

def verify_result(state: AgentState):

    status = state["preparation_status"]

    return {
        "verification": (
            f"AURA checked the preparation status. "
            f"Current status: {status['status']}. "
            f"Remaining tasks: {status['remaining_tasks']}."
        )
    }


# ---------------------------------
# Build AURA LangGraph
# ---------------------------------

builder = StateGraph(AgentState)

builder.add_node("understand_goal", understand_goal)
builder.add_node("create_plan", create_plan)
builder.add_node("check_preparation", check_preparation)
builder.add_node("verify_result", verify_result)

builder.add_edge(START, "understand_goal")
builder.add_edge("understand_goal", "create_plan")
builder.add_edge("create_plan", "check_preparation")
builder.add_edge("check_preparation", "verify_result")
builder.add_edge("verify_result", END)

workflow = builder.compile()


# ---------------------------------
# Local Test
# ---------------------------------

if __name__ == "__main__":

    result = workflow.invoke(
        {
            "goal": "Prepare for my hackathon presentation tomorrow",
            "understanding": "",
            "plan": [],
            "preparation_status": {},
            "verification": "",
        }
    )

    print("\n========== AURA AGENT ==========\n")

    print("UNDERSTANDING:")
    print(result["understanding"])

    print("\nACTION PLAN:")

    for index, step in enumerate(result["plan"], start=1):
        print(f"{index}. {step}")

    print("\nPREPARATION STATUS:")
    print(result["preparation_status"])

    print("\nVERIFICATION:")
    print(result["verification"])