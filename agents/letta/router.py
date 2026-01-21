"""
Letta API Router
================

FastAPI router for Letta endpoints.
All endpoints are under /api/letta/* namespace.

Endpoints:
- POST /api/letta/chat/{profile_id} - Chat with Letta agents
- GET /api/letta/status/{profile_id} - Get Letta status for student
- GET /api/letta/agents/{profile_id} - List agents for student
- POST /api/letta/approve/{approval_id} - Approve a pending request
- POST /api/letta/reject/{approval_id} - Reject a pending request
- GET /api/letta/approvals/{profile_id} - List pending approvals
- GET /api/letta/health - Health check
"""

import structlog
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

from .config import (
    LETTA_CONFIG,
    LETTA_API_PREFIX,
    is_letta_enabled,
    AgentType,
)
from .client import LettaClientWrapper, LettaResponse
from .tools.hitl import (
    approve_request,
    reject_request,
    list_pending_approvals,
)

logger = structlog.get_logger()

# Create router with prefix
letta_router = APIRouter(
    prefix=LETTA_API_PREFIX,
    tags=["letta"],
)

# Global client instance (initialized on first use)
_letta_client: Optional[LettaClientWrapper] = None


async def get_letta_client() -> LettaClientWrapper:
    """Get or create the Letta client singleton."""
    global _letta_client
    if _letta_client is None:
        from tools.database import get_supabase_client
        supabase = get_supabase_client()
        _letta_client = LettaClientWrapper(supabase)
    return _letta_client


def require_letta_enabled():
    """Dependency that requires Letta to be enabled."""
    if not is_letta_enabled():
        raise HTTPException(
            status_code=503,
            detail="Letta integration is not enabled. Set LETTA_ENABLED=true and provide LETTA_API_KEY.",
        )
    return True


# =============================================================================
# Request/Response Models
# =============================================================================


class ChatRequest(BaseModel):
    """Request to chat with Letta agents."""
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response from Letta chat."""
    success: bool
    message: str
    agent_type: str
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ApprovalActionRequest(BaseModel):
    """Request to approve or reject."""
    reason: Optional[str] = None


class StatusResponse(BaseModel):
    """Letta status response."""
    letta_enabled: bool
    initialized: bool
    config: Dict[str, Any]
    agents: Dict[str, Any]


# =============================================================================
# Chat Endpoints
# =============================================================================


@letta_router.post("/chat/{profile_id}", response_model=ChatResponse)
async def chat_with_letta(
    profile_id: str,
    request: ChatRequest,
    _: bool = Depends(require_letta_enabled),
):
    """
    Chat with Letta agents.

    The Orchestrator routes the message to the appropriate specialist.
    """
    try:
        client = await get_letta_client()
        response = await client.chat(
            profile_id=profile_id,
            message=request.message,
            context=request.context,
        )

        logger.info(
            "letta_chat_endpoint",
            profile_id=profile_id,
            success=response.success,
        )

        return ChatResponse(
            success=response.success,
            message=response.message,
            agent_type=response.agent_type.value,
            agent_id=response.agent_id,
            metadata=response.metadata,
            error=response.error,
        )

    except Exception as e:
        logger.error("letta_chat_endpoint_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Status Endpoints
# =============================================================================


@letta_router.get("/status/{profile_id}")
async def get_letta_status(profile_id: str):
    """Get Letta integration status for a student."""
    try:
        client = await get_letta_client()
        status = await client.get_status(profile_id)

        return {
            "profile_id": profile_id,
            **status,
        }

    except Exception as e:
        logger.error("letta_status_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@letta_router.get("/agents/{profile_id}")
async def list_letta_agents(
    profile_id: str,
    _: bool = Depends(require_letta_enabled),
):
    """List Letta agents for a student."""
    try:
        client = await get_letta_client()
        agents = await client.get_or_create_agents(profile_id)

        return {
            "profile_id": profile_id,
            "agents": {
                agent_type.value: {
                    "agent_id": agent_id,
                    "status": "active" if not agent_id.startswith("dormant_") else "dormant",
                }
                for agent_type, agent_id in agents.items()
            },
            "count": len(agents),
        }

    except Exception as e:
        logger.error("letta_agents_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Approval Endpoints (HITL)
# =============================================================================


@letta_router.get("/approvals/{profile_id}")
async def get_pending_approvals(
    profile_id: str,
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get pending approval requests for a student."""
    try:
        from tools.database import get_supabase_client
        supabase = get_supabase_client()

        result = await list_pending_approvals(
            profile_id=profile_id,
            limit=limit,
            supabase_client=supabase,
        )

        return result

    except Exception as e:
        logger.error("letta_approvals_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@letta_router.post("/approve/{approval_id}")
async def approve_letta_request(
    approval_id: str,
    request: ApprovalActionRequest,
):
    """Approve a pending HITL request."""
    try:
        from tools.database import get_supabase_client
        supabase = get_supabase_client()

        result = await approve_request(
            approval_id=approval_id,
            approved_by="user",  # In production, get from auth
            supabase_client=supabase,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("letta_approve_error", approval_id=approval_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@letta_router.post("/reject/{approval_id}")
async def reject_letta_request(
    approval_id: str,
    request: ApprovalActionRequest,
):
    """Reject a pending HITL request."""
    try:
        from tools.database import get_supabase_client
        supabase = get_supabase_client()

        result = await reject_request(
            approval_id=approval_id,
            rejected_by="user",  # In production, get from auth
            reason=request.reason,
            supabase_client=supabase,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("letta_reject_error", approval_id=approval_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Health Endpoints
# =============================================================================


@letta_router.get("/health")
async def letta_health():
    """Check health of Letta integration."""
    try:
        client = await get_letta_client()

        return {
            "status": "healthy" if is_letta_enabled() else "disabled",
            "letta_enabled": is_letta_enabled(),
            "config": LETTA_CONFIG.to_dict(),
            "version": "1.0.0",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@letta_router.get("/config")
async def get_letta_config():
    """Get Letta configuration (non-sensitive)."""
    return {
        "enabled": LETTA_CONFIG.enabled,
        "has_api_key": bool(LETTA_CONFIG.api_key),
        "base_url": LETTA_CONFIG.base_url,
        "agents": {
            agent_type.value: {
                "name": config.name,
                "status": config.status.value,
                "enabled": config.is_enabled(),
            }
            for agent_type, config in LETTA_CONFIG.agents.items()
        },
    }


# =============================================================================
# Debug Endpoints
# =============================================================================


@letta_router.get("/debug/memory/{profile_id}")
async def debug_memory_blocks(profile_id: str):
    """
    Debug endpoint to view memory blocks for a profile.

    Returns the memory blocks that would be synced to Letta agents.
    """
    try:
        from tools.database import get_supabase_client
        from .memory.sync import MemorySyncService

        supabase = get_supabase_client()
        sync_service = MemorySyncService(supabase)
        blocks = await sync_service.build_memory_blocks(profile_id)

        return {
            "profile_id": profile_id,
            "block_count": len(blocks),
            "blocks": {
                name: {
                    "content": content,
                    "length": len(content),
                }
                for name, content in blocks.items()
            },
        }

    except Exception as e:
        logger.error("letta_debug_memory_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
