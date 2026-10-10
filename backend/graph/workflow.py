from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from backend.mcp.tool_functions import (
    get_preparation_status,
    create_action_plan,
    complete_preparation_task,
)
from backend.agents.tool_router import select_tool
# ---------------------------------
# AURA Agent State
# ---------------------------------

class AgentState(TypedDict):
    goal: str
    understanding: str
    plan: list[str]
    selected_tool: str
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
# 2. Select the Best Tool
# ---------------------------------

def select_agent_tool(state: AgentState):

    selected_tool = select_tool(state["goal"])

    return {
        "selected_tool": selected_tool
    }
# ---------------------------------
# 3. Execute Selected Tool
# ---------------------------------

def execute_selected_tool(state: AgentState):

    selected_tool = state["selected_tool"]

    if selected_tool == "get_preparation_status":

        result = get_preparation_status(state["goal"])

        return {
            "preparation_status": result
        }

    if selected_tool == "create_action_plan":

        result = create_action_plan(state["goal"])

        return {
            "plan": result["plan"],
            "preparation_status": {}
        }
    if selected_tool == "complete_preparation_task":

        result = complete_preparation_task(state["goal"])

        return {
        "preparation_status": result
    }

    return {
        "preparation_status": {}
    }
# ---------------------------------
# 4. Create an Action Plan
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




# ---------------------------------
# 4. Verify the Result
# ---------------------------------


def verify_result(state: AgentState):
    """Validate the result returned by the selected tool."""

    selected_tool = state["selected_tool"]
    status = state["preparation_status"]
    plan = state["plan"]

    if selected_tool == "create_action_plan":
        if (
            isinstance(plan, list)
            and len(plan) > 0
            and all(
                isinstance(step, str) and step.strip()
                for step in plan
            )
        ):
            message = (
                f"Verification passed: action plan contains "
                f"{len(plan)} valid steps."
            )
        else:
            message = (
                "Verification failed: the action plan is "
                "empty or invalid."
            )

    elif selected_tool == "get_preparation_status":
        valid = (
            isinstance(status, dict)
            and isinstance(status.get("completed_tasks"), int)
            and isinstance(status.get("remaining_tasks"), int)
            and isinstance(status.get("status"), str)
            and status["completed_tasks"] >= 0
            and status["remaining_tasks"] >= 0
        )

        if valid:
            message = (
                "Verification passed: preparation status is valid. "
                f"Completed: {status['completed_tasks']}; "
                f"remaining: {status['remaining_tasks']}."
            )
        else:
            message = (
                "Verification failed: preparation status "
                "is missing or invalid."
            )

    elif selected_tool == "complete_preparation_task":
        valid = (
            isinstance(status, dict)
            and isinstance(status.get("completed_tasks"), int)
            and isinstance(status.get("remaining_tasks"), int)
            and isinstance(status.get("message"), str)
            and status["completed_tasks"] >= 0
            and status["remaining_tasks"] >= 0
        )

        if valid:
            message = (
                "Verification passed: the completion tool "
                "returned valid task counts. "
                f"Completed: {status['completed_tasks']}; "
                f"remaining: {status['remaining_tasks']}."
            )
        else:
            message = (
                "Verification failed: the completion result "
                "is missing or invalid."
            )

    else:
        message = (
            f"Verification failed: unsupported tool "
            f"'{selected_tool}'."
        )

    return {"verification": message}


# ---------------------------------
# Build AURA LangGraph
# ---------------------------------

builder = StateGraph(AgentState)

builder = StateGraph(AgentState)

builder.add_node("understand_goal", understand_goal)
builder.add_node("select_agent_tool", select_agent_tool)
builder.add_node("execute_selected_tool", execute_selected_tool)
builder.add_node("create_plan", create_plan)
builder.add_node("verify_result", verify_result)

builder.add_edge(START, "understand_goal")
builder.add_edge("understand_goal", "select_agent_tool")
builder.add_edge("select_agent_tool", "execute_selected_tool")
builder.add_edge("execute_selected_tool", "verify_result")
builder.add_edge("verify_result", END)

workflow = builder.compile()

workflow = builder.compile()


# ---------------------------------
# Local Test
# ---------------------------------

if __name__ == "__main__":

    result = workflow.invoke(
        {
            "goal": "I finished a preparation task",
            "understanding": "",
            "plan": [],
            "selected_tool": "",
            "preparation_status": {},
            "verification": "",
        }
    )

    print("\n========== AURA AGENT ==========\n")

    print("UNDERSTANDING:")
    print(result["understanding"])
    
    print("\nSELECTED TOOL:")
    print(result["selected_tool"])

    print("\nACTION PLAN:")

    for index, step in enumerate(result["plan"], start=1):
        print(f"{index}. {step}")

    print("\nPREPARATION STATUS:")
    print(result["preparation_status"])

    print("\nVERIFICATION:")
    print(result["verification"])