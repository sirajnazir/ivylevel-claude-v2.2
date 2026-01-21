"""
Human-in-the-Loop (HITL) Approval Tools
=======================================

Tools for managing human approval workflows for critical decisions.

These tools allow Letta agents to:
- Request approval for high-stakes actions
- Check approval status
- List pending approvals
"""

import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from ..config import LETTA_TABLES

logger = structlog.get_logger()


# Letta tool definitions for HITL
HITL_TOOLS = [
    {
        "name": "request_approval",
        "description": "Request human approval for a critical action before executing it. Use this for high-stakes decisions like application submissions, major plan changes, or financial commitments.",
        "parameters": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": [
                        "submit_application",
                        "major_plan_change",
                        "deadline_extension",
                        "school_list_change",
                        "financial_commitment",
                        "essay_final_submission",
                        "other_critical",
                    ],
                    "description": "Type of action requiring approval",
                },
                "action_description": {
                    "type": "string",
                    "description": "Clear description of what action will be taken if approved",
                },
                "rationale": {
                    "type": "string",
                    "description": "Why this action is recommended",
                },
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                    "description": "How urgent is this approval",
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional context (e.g., school name, deadline)",
                },
            },
            "required": ["action_type", "action_description", "rationale"],
        },
    },
    {
        "name": "check_approval_status",
        "description": "Check the status of a pending approval request.",
        "parameters": {
            "type": "object",
            "properties": {
                "approval_id": {
                    "type": "string",
                    "description": "The approval request ID",
                },
            },
            "required": ["approval_id"],
        },
    },
    {
        "name": "list_pending_approvals",
        "description": "List all pending approval requests for a student.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile_id": {
                    "type": "string",
                    "description": "Student profile ID",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum number of approvals to return",
                },
            },
            "required": ["profile_id"],
        },
    },
]


async def request_approval(
    profile_id: str,
    action_type: str,
    action_description: str,
    rationale: str,
    requesting_agent: str,
    urgency: str = "medium",
    metadata: Optional[Dict[str, Any]] = None,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Request human approval for a critical action.

    Args:
        profile_id: Student profile ID
        action_type: Type of action (submit_application, major_plan_change, etc.)
        action_description: Clear description of the proposed action
        rationale: Why this action is recommended
        requesting_agent: Name of the agent requesting approval
        urgency: Urgency level (low, medium, high, critical)
        metadata: Additional context
        supabase_client: Supabase client

    Returns:
        Dictionary with approval request ID and status
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        approval_id = str(uuid4())

        # Build approval record
        record = {
            "id": approval_id,
            "profile_id": profile_id,
            "action_type": action_type,
            "action_payload": {
                "description": action_description,
                "rationale": rationale,
                "urgency": urgency,
                "metadata": metadata or {},
            },
            "requested_by": requesting_agent,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }

        # Insert into approval queue
        supabase_client.table(LETTA_TABLES["approval_queue"]) \
            .insert(record) \
            .execute()

        # Create notification for user
        notification = {
            "profile_id": profile_id,
            "notification_type": "approval_request",
            "message": f"Action Requires Approval: {action_description}",
            "metadata": {
                "approval_id": approval_id,
                "action_type": action_type,
                "urgency": urgency,
                "requesting_agent": requesting_agent,
            },
            "created_at": datetime.now().isoformat(),
        }

        try:
            supabase_client.table("proactive_notifications") \
                .insert(notification) \
                .execute()
        except Exception:
            # Notification table might not exist, continue
            pass

        logger.info(
            "letta_approval_requested",
            profile_id=profile_id,
            approval_id=approval_id,
            action_type=action_type,
            urgency=urgency,
        )

        return {
            "success": True,
            "approval_id": approval_id,
            "status": "pending",
            "message": f"Approval request created. The user will be notified to review this {urgency} priority request.",
            "next_steps": [
                "Wait for human approval before proceeding",
                "Use check_approval_status to monitor the request",
                "Do NOT execute the action until approved",
            ],
        }

    except Exception as e:
        logger.error(
            "letta_approval_request_error",
            profile_id=profile_id,
            action_type=action_type,
            error=str(e),
        )
        return {
            "success": False,
            "error": str(e),
            "approval_id": None,
        }


async def check_approval_status(
    approval_id: str,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Check the status of an approval request.

    Args:
        approval_id: The approval request ID
        supabase_client: Supabase client

    Returns:
        Dictionary with approval status and details
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        result = supabase_client.table(LETTA_TABLES["approval_queue"]) \
            .select("*") \
            .eq("id", approval_id) \
            .single() \
            .execute()

        if not result.data:
            return {
                "success": False,
                "error": f"Approval request {approval_id} not found",
                "status": None,
            }

        approval = result.data

        return {
            "success": True,
            "approval_id": approval_id,
            "status": approval.get("status", "unknown"),
            "action_type": approval.get("action_type"),
            "requested_by": approval.get("requested_by"),
            "requested_at": approval.get("created_at"),
            "resolved_at": approval.get("resolved_at"),
            "approved_by": approval.get("approved_by"),
            "can_proceed": approval.get("status") == "approved",
        }

    except Exception as e:
        logger.error("letta_check_approval_error", approval_id=approval_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "status": None,
        }


async def list_pending_approvals(
    profile_id: str,
    limit: int = 10,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    List all pending approval requests for a student.

    Args:
        profile_id: Student profile ID
        limit: Maximum number of approvals to return
        supabase_client: Supabase client

    Returns:
        Dictionary with list of pending approvals
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        result = supabase_client.table(LETTA_TABLES["approval_queue"]) \
            .select("*") \
            .eq("profile_id", profile_id) \
            .eq("status", "pending") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        approvals = []
        for row in result.data or []:
            payload = row.get("action_payload", {})
            approvals.append({
                "approval_id": row.get("id"),
                "action_type": row.get("action_type"),
                "description": payload.get("description", ""),
                "urgency": payload.get("urgency", "medium"),
                "requested_by": row.get("requested_by"),
                "requested_at": row.get("created_at"),
            })

        return {
            "success": True,
            "profile_id": profile_id,
            "pending_approvals": approvals,
            "count": len(approvals),
        }

    except Exception as e:
        logger.error("letta_list_approvals_error", profile_id=profile_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "pending_approvals": [],
        }


async def approve_request(
    approval_id: str,
    approved_by: str,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Approve a pending request (called from API, not directly by agents).

    Args:
        approval_id: The approval request ID
        approved_by: Who approved the request
        supabase_client: Supabase client

    Returns:
        Dictionary with result
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        supabase_client.table(LETTA_TABLES["approval_queue"]) \
            .update({
                "status": "approved",
                "approved_by": approved_by,
                "resolved_at": datetime.now().isoformat(),
            }) \
            .eq("id", approval_id) \
            .execute()

        logger.info("letta_approval_approved", approval_id=approval_id, approved_by=approved_by)

        return {
            "success": True,
            "approval_id": approval_id,
            "status": "approved",
        }

    except Exception as e:
        logger.error("letta_approve_error", approval_id=approval_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
        }


async def reject_request(
    approval_id: str,
    rejected_by: str,
    reason: Optional[str] = None,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Reject a pending request (called from API, not directly by agents).

    Args:
        approval_id: The approval request ID
        rejected_by: Who rejected the request
        reason: Optional rejection reason
        supabase_client: Supabase client

    Returns:
        Dictionary with result
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        update_data = {
            "status": "rejected",
            "approved_by": rejected_by,  # Reusing field for who resolved
            "resolved_at": datetime.now().isoformat(),
        }

        # Get current payload to add rejection reason
        current = supabase_client.table(LETTA_TABLES["approval_queue"]) \
            .select("action_payload") \
            .eq("id", approval_id) \
            .single() \
            .execute()

        if current.data:
            payload = current.data.get("action_payload", {})
            payload["rejection_reason"] = reason
            update_data["action_payload"] = payload

        supabase_client.table(LETTA_TABLES["approval_queue"]) \
            .update(update_data) \
            .eq("id", approval_id) \
            .execute()

        logger.info("letta_approval_rejected", approval_id=approval_id, rejected_by=rejected_by)

        return {
            "success": True,
            "approval_id": approval_id,
            "status": "rejected",
        }

    except Exception as e:
        logger.error("letta_reject_error", approval_id=approval_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
        }
