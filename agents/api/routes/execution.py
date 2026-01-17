"""
Execution Agent API Routes v5.3
===============================

Endpoints for chat, workflow, and utility operations.

Endpoints:
- POST /api/execution/chat/stream - SSE streaming chat
- POST /api/execution/chat - Non-streaming chat
- POST /api/execution/workflow/run - Manual workflow trigger
- GET /api/execution/weekly-focus/{profile_id} - Get weekly focus
- GET /api/execution/eds/{profile_id} - Get EDS score
- GET /api/execution/stalls/{profile_id} - Get stalled projects
- GET /api/execution/projects/{profile_id} - Get active projects
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

router = APIRouter(prefix="/api/execution", tags=["execution"])


class ChatRequest(BaseModel):
    profile_id: str
    message: str
    context_type: Optional[str] = None
    context_id: Optional[str] = None
    thread_id: Optional[str] = None


class WorkflowRequest(BaseModel):
    profile_id: str
    trigger: str = "manual"


class WeeklyPlanRequest(BaseModel):
    profile_id: str
    week_start: Optional[str] = None


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response from Execution Agent.

    Uses Server-Sent Events (SSE) for real-time streaming.
    """
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()

    async def generate():
        try:
            # Store user message in conversations table
            from tools.database import get_supabase_client
            from datetime import datetime

            supabase = get_supabase_client()
            supabase.table("conversations").insert({
                "profile_id": request.profile_id,
                "agent_type": "execution",
                "thread_id": request.thread_id,
                "role": "user",
                "content": request.message,
                "context_type": request.context_type or "general",
                "context_id": request.context_id,
                "is_proactive": False,
                "created_at": datetime.now().isoformat(),
            }).execute()

            full_response = ""

            async for chunk in agent.chat(
                profile_id=request.profile_id,
                message=request.message,
                context_type=request.context_type,
                context_id=request.context_id,
                thread_id=request.thread_id,
            ):
                if chunk.get("type") == "content":
                    full_response += chunk.get("content", "")
                    yield f"data: {json.dumps(chunk)}\n\n"
                elif chunk.get("type") == "done":
                    # Store assistant message
                    result = supabase.table("conversations").insert({
                        "profile_id": request.profile_id,
                        "agent_type": "execution",
                        "thread_id": request.thread_id,
                        "role": "assistant",
                        "content": full_response,
                        "context_type": request.context_type or "general",
                        "context_id": request.context_id,
                        "is_proactive": False,
                        "created_at": datetime.now().isoformat(),
                    }).execute()

                    conversation_id = result.data[0]["id"] if result.data else None

                    yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id, 'thread_id': request.thread_id})}\n\n"
                elif chunk.get("type") == "error":
                    yield f"data: {json.dumps(chunk)}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint."""
    from agents.execution_chat import ExecutionChatAgent
    from tools.database import get_supabase_client
    from datetime import datetime

    agent = ExecutionChatAgent()
    supabase = get_supabase_client()

    # Store user message
    supabase.table("conversations").insert({
        "profile_id": request.profile_id,
        "agent_type": "execution",
        "thread_id": request.thread_id,
        "role": "user",
        "content": request.message,
        "context_type": request.context_type or "general",
        "context_id": request.context_id,
        "is_proactive": False,
        "created_at": datetime.now().isoformat(),
    }).execute()

    full_response = ""

    async for chunk in agent.chat(
        profile_id=request.profile_id,
        message=request.message,
        context_type=request.context_type,
        context_id=request.context_id,
    ):
        if chunk.get("type") == "content":
            full_response += chunk.get("content", "")
        elif chunk.get("type") == "error":
            raise HTTPException(status_code=500, detail=chunk.get("error"))

    # Store assistant message
    result = supabase.table("conversations").insert({
        "profile_id": request.profile_id,
        "agent_type": "execution",
        "thread_id": request.thread_id,
        "role": "assistant",
        "content": full_response,
        "context_type": request.context_type or "general",
        "context_id": request.context_id,
        "is_proactive": False,
        "created_at": datetime.now().isoformat(),
    }).execute()

    return {
        "success": True,
        "response": full_response,
        "conversation_id": result.data[0]["id"] if result.data else None,
    }


@router.post("/workflow/run")
async def run_workflow(request: WorkflowRequest):
    """Manually trigger execution workflow."""
    from graphs.execution_workflow import run_execution_workflow

    result = await run_execution_workflow(
        profile_id=request.profile_id,
        trigger=request.trigger,
    )
    return result


@router.get("/weekly-focus/{profile_id}")
async def get_weekly_focus(profile_id: str):
    """Get weekly focus items."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_get_weekly_focus(profile_id)


@router.post("/weekly-plan/generate")
async def generate_weekly_plan(request: WeeklyPlanRequest):
    """Generate a new weekly plan."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_generate_weekly_plan(
        profile_id=request.profile_id,
        week_start=request.week_start,
    )


@router.get("/eds/{profile_id}")
async def get_eds(profile_id: str):
    """Get Execution Debt Score."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_calculate_eds(profile_id)


@router.get("/stalls/{profile_id}")
async def get_stalls(profile_id: str, threshold_days: int = 5):
    """Get stalled projects."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_detect_stalls(profile_id, threshold_days)


@router.get("/projects/{profile_id}")
async def get_projects(profile_id: str):
    """Get active projects."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_get_active_projects(profile_id)


@router.get("/conversations/{profile_id}")
async def get_conversations(profile_id: str, limit: int = 20):
    """Get conversation history."""
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_get_conversation_history(profile_id, limit)
