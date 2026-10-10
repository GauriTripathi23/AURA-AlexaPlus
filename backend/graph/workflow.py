
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from backend.mcp.tool_functions import (
    get_preparation_status,
    create_action_plan,
    complete_preparation_task,
)
from backend.agents.tool_router import select_tools


class AgentState(TypedDict):
    goal: str
    understanding: str
    plan: list[str]
    selected_tool: str
    selected_tools: list[str]
    preparation_status: dict
    tool_results: dict
    verification: str


# 1. Understand the user's goal
def understand_goal(state: AgentState) -> dict:
    goal = state["goal"]

    return {
        "understanding": (
            f"AURA understood the user's goal as: {goal}"
        )
    }


# 2. Select one or more tools
def select_agent_tool(state: AgentState) -> dict:
    tools = select_tools(state["goal"])

    if not tools:
        tools = ["create_action_plan"]

    return {
        "selected_tools": tools,
        "selected_tool": tools[0],
    }


# 3. Execute all selected tools in order
def execute_selected_tools(state: AgentState) -> dict:
    goal = state["goal"]
    selected_tools = state.get("selected_tools") or [
        state.get("selected_tool", "create_action_plan")
    ]

    plan = list(state.get("plan", []))
    preparation_status = dict(state.get("preparation_status", {}))
    tool_results = {}

    for tool_name in selected_tools:
        if tool_name == "create_action_plan":
            result = create_action_plan(goal)
            tool_results[tool_name] = result

            if isinstance(result.get("plan"), list):
                plan = result["plan"]

        elif tool_name == "get_preparation_status":
            result = get_preparation_status(goal)
            tool_results[tool_name] = result
            preparation_status = result

        elif tool_name == "complete_preparation_task":
            result = complete_preparation_task(goal)
            tool_results[tool_name] = result
            preparation_status = result

        else:
            tool_results[tool_name] = {
                "error": f"Unsupported tool: {tool_name}"
            }

    return {
        "plan": plan,
        "preparation_status": preparation_status,
        "tool_results": tool_results,
    }


# 4. Verify each tool's returned result
def verify_result(state: AgentState) -> dict:
    selected_tools = state.get("selected_tools") or [
        state.get("selected_tool", "")
    ]
    results = state.get("tool_results", {})
    errors = []

    for tool_name in selected_tools:
        result = results.get(tool_name, {})

        if not isinstance(result, dict) or result.get("error"):
            errors.append(f"{tool_name}: missing or invalid result")
            continue

        if tool_name == "create_action_plan":
            steps = result.get("plan")

            valid = (
                isinstance(steps, list)
                and len(steps) > 0
                and all(
                    isinstance(step, str) and step.strip()
                    for step in steps
                )
            )

            if not valid:
                errors.append(f"{tool_name}: invalid action plan")

        elif tool_name in {
            "get_preparation_status",
            "complete_preparation_task",
        }:
            completed = result.get("completed_tasks")
            remaining = result.get("remaining_tasks")

            valid = (
                isinstance(completed, int)
                and not isinstance(completed, bool)
                and isinstance(remaining, int)
                and not isinstance(remaining, bool)
                and completed >= 0
                and remaining >= 0
            )

            if not valid:
                errors.append(f"{tool_name}: invalid task counts")

    if errors:
        message = "Verification failed: " + "; ".join(errors) + "."

    else:
        names = " -> ".join(selected_tools)
        message = (
            f"Verification passed: {len(selected_tools)} tool "
            f"result(s) validated. Execution order: {names}."
        )

    return {"verification": message}


# 5. Build the graph
builder = StateGraph(AgentState)

builder.add_node("understand_goal", understand_goal)
builder.add_node("select_agent_tool", select_agent_tool)
builder.add_node("execute_selected_tools", execute_selected_tools)
builder.add_node("verify_result", verify_result)

builder.add_edge(START, "understand_goal")
builder.add_edge("understand_goal", "select_agent_tool")
builder.add_edge("select_agent_tool", "execute_selected_tools")
builder.add_edge("execute_selected_tools", "verify_result")
builder.add_edge("verify_result", END)

workflow = builder.compile()


# Local test
if __name__ == "__main__":
    result = workflow.invoke(
        {
            "goal": "Create a plan and check progress",
            "understanding": "",
            "plan": [],
            "selected_tool": "",
            "selected_tools": [],
            "preparation_status": {},
            "tool_results": {},
            "verification": "",
        }
    )

    print("\n========== AURA AGENT ==========\n")
    print("UNDERSTANDING:", result["understanding"])
    print("SELECTED TOOLS:", result["selected_tools"])
    print("ACTION PLAN:", result["plan"])
    print("PREPARATION STATUS:", result["preparation_status"])
    print("TOOL RESULTS:", result["tool_results"])
    print("VERIFICATION:", result["verification"])
