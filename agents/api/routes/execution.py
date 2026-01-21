"""
Execution Agent API Routes v5.4
===============================

Endpoints for chat, workflow, proactive engagement, and utility operations.

Chat Endpoints:
- POST /api/execution/chat/stream - SSE streaming chat
- POST /api/execution/chat - Non-streaming chat
- GET /api/execution/conversations/{profile_id} - Get conversation history

Workflow Endpoints:
- POST /api/execution/workflow/run - Manual workflow trigger
- POST /api/execution/weekly-plan/generate - Generate weekly plan

Utility Endpoints:
- GET /api/execution/weekly-focus/{profile_id} - Get weekly focus
- GET /api/execution/eds/{profile_id} - Get EDS score
- GET /api/execution/stalls/{profile_id} - Get stalled projects
- GET /api/execution/projects/{profile_id} - Get active projects

Proactive Engagement Endpoints (EC Agent Plumbing):
- GET /api/execution/welcome/{profile_id} - Check for proactive welcome
- POST /api/execution/welcome/deliver - Deliver welcome and mark as delivered
- GET /api/execution/first-session/{profile_id} - Get first session context
- GET /api/execution/nudges/{profile_id} - Get pending nudges
- POST /api/execution/nudges/delivered - Mark nudge as delivered
- POST /api/execution/nudges/dismissed - Mark nudge as dismissed
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


# =========================================================================
# PROACTIVE ENGAGEMENT ENDPOINTS (EC Agent Plumbing)
# =========================================================================


@router.get("/welcome/{profile_id}")
async def get_proactive_welcome(profile_id: str):
    """
    Check for proactive welcome message for new students.

    Called when Execution tab loads to check if there's a welcome
    message waiting (from EC onboarding after game plan generation).

    Returns:
        Welcome message data or None if no welcome pending
    """
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.get_proactive_welcome(profile_id)


class DeliverWelcomeRequest(BaseModel):
    profile_id: str
    nudge_id: str


@router.post("/welcome/deliver")
async def deliver_welcome(request: DeliverWelcomeRequest):
    """
    Deliver the welcome message and mark nudge as delivered.

    Called after the frontend displays the welcome message.

    Args:
        profile_id: Student's profile UUID
        nudge_id: Welcome nudge UUID

    Returns:
        Result with success status
    """
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.deliver_welcome_and_mark(
        profile_id=request.profile_id,
        nudge_id=request.nudge_id,
    )


@router.get("/first-session/{profile_id}")
async def get_first_session_context(profile_id: str):
    """
    Get first session context for new students.

    Returns session agenda and priority focus for the first conversation.

    Args:
        profile_id: Student's profile UUID

    Returns:
        First session agenda and priorities
    """
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.get_first_session_context(profile_id)


@router.get("/nudges/{profile_id}")
async def get_pending_nudges(profile_id: str):
    """
    Get pending nudges for a profile.

    Used at start of conversation to know what proactive topics to raise.

    Args:
        profile_id: Profile UUID

    Returns:
        List of pending nudges, ordered by priority and creation time
    """
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_get_pending_nudges(profile_id)


class MarkNudgeRequest(BaseModel):
    nudge_id: str


@router.post("/nudges/delivered")
async def mark_nudge_delivered(request: MarkNudgeRequest):
    """
    Mark a nudge as delivered after it's been raised in conversation.

    Args:
        nudge_id: UUID of the nudge to mark as delivered

    Returns:
        Result with success status
    """
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_mark_nudge_delivered(request.nudge_id)


@router.post("/nudges/dismissed")
async def mark_nudge_dismissed(request: MarkNudgeRequest):
    """
    Mark a nudge as dismissed (user acknowledged but didn't act).

    Args:
        nudge_id: UUID of the nudge to dismiss

    Returns:
        Result with success status
    """
    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    return await agent.tool_mark_nudge_dismissed(request.nudge_id)


# =========================================================================
# EC ONBOARDING ENDPOINT
# =========================================================================


class TriggerOnboardingRequest(BaseModel):
    profile_id: str
    game_plan_id: str


@router.post("/onboarding/trigger")
async def trigger_onboarding(request: TriggerOnboardingRequest):
    """
    Trigger EC onboarding for a profile after game plan is created.

    This endpoint should be called by the frontend after saving a game plan
    to Supabase. It will:
    1. Sync game plan to projects
    2. Create welcome nudge
    3. Set up first session context

    Args:
        profile_id: Student's profile UUID
        game_plan_id: The game plan UUID that was just created

    Returns:
        Onboarding results including projects created and welcome nudge status
    """
    from tools.database import get_supabase_client
    from services.ec_onboarding import trigger_ec_onboarding
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"[EC Onboarding] Trigger received for profile={request.profile_id}, game_plan={request.game_plan_id}")

    try:
        supabase = get_supabase_client()

        # Fetch the game plan data
        gp_result = supabase.table("game_plans").select(
            "plan_data"
        ).eq("id", request.game_plan_id).single().execute()

        if not gp_result.data or not gp_result.data.get("plan_data"):
            logger.warning(f"[EC Onboarding] Game plan {request.game_plan_id} not found or has no plan_data")
            return {
                "success": False,
                "error": f"Game plan {request.game_plan_id} not found or has no plan_data"
            }

        plan_data = gp_result.data["plan_data"]
        logger.info(f"[EC Onboarding] Plan data keys: {list(plan_data.keys()) if isinstance(plan_data, dict) else 'not a dict'}")

        # Trigger EC onboarding
        result = await trigger_ec_onboarding(
            supabase_client=supabase,
            profile_id=request.profile_id,
            plan_data=plan_data,
        )

        logger.info(f"[EC Onboarding] Result: projects={result.get('projects_created', 0)}, nudge={result.get('welcome_nudge_created', False)}, errors={result.get('errors', [])}")

        return {
            "success": True,
            "projects_created": result.get("projects_created", 0),
            "welcome_nudge_created": result.get("welcome_nudge_created", False),
            "errors": result.get("errors", []),
        }

    except Exception as e:
        logger.error(f"[EC Onboarding] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
