from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ---------------------------------
# AURA Agent State
# ---------------------------------

class AgentState(TypedDict):
    goal: str
    understanding: str
    plan: list[str]
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
# 3. Verify the Result
# ---------------------------------

def verify_result(state: AgentState):

    return {
        "verification": (
            "AURA reviewed the generated plan and confirmed "
            "that the goal has actionable next steps."
        )
    }


# ---------------------------------
# Build AURA LangGraph
# ---------------------------------

builder = StateGraph(AgentState)

builder.add_node("understand_goal", understand_goal)
builder.add_node("create_plan", create_plan)
builder.add_node("verify_result", verify_result)

builder.add_edge(START, "understand_goal")
builder.add_edge("understand_goal", "create_plan")
builder.add_edge("create_plan", "verify_result")
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
            "verification": "",
        }
    )

    print("\n========== AURA AGENT ==========\n")

    print("UNDERSTANDING:")
    print(result["understanding"])

    print("\nACTION PLAN:")

    for index, step in enumerate(result["plan"], start=1):
        print(f"{index}. {step}")

    print("\nVERIFICATION:")
    print(result["verification"])