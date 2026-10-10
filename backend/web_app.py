
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from mcp import ClientSession

try:
    from mcp.client.streamable_http import streamablehttp_client
except ImportError:
    from mcp.client.streamable_http import (
        streamable_http_client as streamablehttp_client,
    )


MCP_URL = "http://127.0.0.1:8000/mcp"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_FILE = PROJECT_ROOT / "frontend" / "index.html"

app = FastAPI(title="AURA Web Demo")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


@app.get("/")
async def home():
    """Serve the AURA demo interface."""
    if not FRONTEND_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="frontend/index.html was not found.",
        )

    return FileResponse(FRONTEND_FILE)


@app.get("/api/health")
async def health():
    """Report that the web application is running."""
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Send a goal to the LangGraph agent through MCP."""
    goal = request.message.strip()

    if not goal:
        raise HTTPException(
            status_code=400,
            detail="Please enter a goal.",
        )

    try:
        async with streamablehttp_client(MCP_URL) as streams:
            read_stream, write_stream = streams[0], streams[1]

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:
                await session.initialize()

                result = await session.call_tool(
                    "run_aura_agent",
                    arguments={"goal": goal},
                )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not reach AURA's MCP server. "
                "Make sure the MCP server is running on port 8000."
            ),
        ) from exc

    if getattr(result, "isError", False):
        raise HTTPException(
            status_code=502,
            detail="The AURA agent reported a tool error.",
        )

    for item in result.content:
        text = getattr(item, "text", None)

        if not text:
            continue

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue

        if isinstance(data, dict):
            return data

    raise HTTPException(
        status_code=502,
        detail="AURA returned no valid JSON result.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.web_app:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
    )