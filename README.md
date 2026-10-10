
# AURA — Adaptive Unified Response Agent

AURA is a goal-oriented AI assistant prototype built for the Build, Ship, Shape: Amazon Developer Hackathon. It combines a self-hosted Model Context Protocol (MCP) server, a LangGraph-based workflow, persistent goal-specific task tracking, and a web interface inspired by conversational assistants.

**AURA's goal:** Turn a user's request into an action plan, execute appropriate tools, retain progress across sessions, and verify returned results.

> **Project type:** Simulated Alexa+-style web experience backed by an MCP-enabled agent. This is an independent prototype, not an official Amazon Alexa+ integration.

## Key Features

- **Goal understanding:** Accepts natural-language requests through a web chat interface.
- **Intent-based routing:** Selects action planning, preparation-status checking, or task completion.
- **Multi-step execution:** Executes selected tools in sequence for compound requests.
- **Persistent progress:** Stores preparation progress locally in JSON, separately for normalized goals.
- **Result verification:** Validates tool results before returning a verification message.
- **MCP integration:** Exposes agent tools through a self-hosted Streamable HTTP MCP server.
- **Web interface:** Displays plans, tool execution order, results, task counts, and verification output.

## Architecture

```text
User
 |
 v
AURA Web Interface (HTML, CSS, JavaScript)
 |
 v
FastAPI Web Bridge (port 8001)
 |
 v
MCP Client
 |
 v
Self-hosted MCP Server (port 8000)
 |
 v
LangGraph Agent Workflow
 |
 +--> Intent Router
 |
 +--> Create Action Plan
 |
 +--> Check Preparation Status
 |
 +--> Complete Preparation Task
 |
 v
Result Validation
 |
 v
Persistent Local JSON State
```

## Technology Stack

| Component | Technology |
|---|---|
| Agent workflow | LangGraph |
| Tool integration | Model Context Protocol (MCP) |
| MCP transport | Streamable HTTP |
| Web bridge | FastAPI |
| Web interface | HTML, CSS, JavaScript |
| State persistence | Local JSON file |
| Language | Python |

## Repository Structure

```text
AURA-AlexaPlus/
├── backend/
│   ├── agents/
│   │   └── tool_router.py
│   ├── graph/
│   │   └── workflow.py
│   ├── mcp/
│   │   ├── server.py
│   │   ├── tools.py
│   │   └── tool_functions.py
│   └── web_app.py
├── frontend/
│   └── index.html
├── data/
│   └── preparation_state.json   # local runtime data; do not commit
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python and pip
- Git
- A terminal such as PowerShell
- A modern web browser

### 1. Clone the repository

```powershell
git clone https://github.com/GauriTripathi23/AURA-AlexaPlus.git
cd AURA-AlexaPlus
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the MCP server

Open Terminal 1 in the project directory:

```powershell
python -m backend.mcp.server
```

Keep the terminal open. The MCP server should listen at:

```text
http://127.0.0.1:8000/mcp
```

### 5. Start the web application

Open Terminal 2 in the same project directory and activate the virtual environment if necessary.

```powershell
python -m backend.web_app
```

The web interface should be available at:

```text
http://127.0.0.1:8001
```

Keep both servers running while using the demo.

## Try the Demo

### Create an action plan

Enter:

```text
Prepare for my hackathon presentation
```

Expected behaviour: AURA selects the planning tool and returns a five-step plan.

### Check preparation progress

Enter:

```text
Am I prepared for my hackathon presentation?
```

Expected behaviour: AURA retrieves the saved progress for that goal.

### Complete a task and check progress

Enter:

```text
I finished a preparation task for my hackathon presentation and check progress
```

Expected behaviour: AURA completes one task, checks the updated progress, and displays the execution sequence and tool results.

### Test separate goals

Check exam preparation after recording progress for the hackathon presentation. The two goals should maintain separate task counters.

## Testing

Run the router's unit-style smoke tests:

```powershell
python -c "from backend.agents.tool_router import select_tools; tests = [('Prepare for my hackathon presentation', ['create_action_plan']), ('Am I prepared for my hackathon presentation?', ['get_preparation_status']), ('I finished a preparation task for my hackathon presentation', ['complete_preparation_task']), ('Create a plan and check progress', ['create_action_plan', 'get_preparation_status']), ('I completed a task and check progress', ['complete_preparation_task', 'get_preparation_status'])]; [(print(('PASS' if select_tools(q) == expected else 'FAIL'), '|', q, '|', select_tools(q))) for q, expected in tests]"
```

Run the LangGraph workflow smoke test:

```powershell
python -m backend.graph.workflow
```

The workflow test should display both selected tools and a verification summary for a compound request.

## State and Privacy

- Preparation progress is stored in `data/preparation_state.json`.
- The state file is intended to remain local and should be excluded from Git.
- The application uses localhost endpoints for the development demo.
- Do not expose the development servers publicly without adding suitable authentication, access controls, and production configuration.
- Verification checks returned data; it does not independently prove that an external action occurred.

## Current Scope and Limitations

- Intent routing currently uses explicit rules rather than an LLM-based planner.
- The action plan is a basic template, not a dynamic plan generated from external research.
- The local JSON state is suitable for a prototype, not concurrent multi-user deployment.
- The simulated web interface is not connected to an actual Alexa+ account or device.

## Future Work

- Add goal-aware task decomposition and execution policies.
- Add robust state management and automated integration tests.
- Add explicit handling for failed tools and partial workflow completion.
- Improve planning using richer context and user preferences.
- Prepare a recorded end-to-end demo and a clear architecture walkthrough.

## Hackathon Context

Built as a simulated Alexa+-style experience using an agentic workflow and MCP tool integration for the Build, Ship, Shape: Amazon Developer Hackathon.
