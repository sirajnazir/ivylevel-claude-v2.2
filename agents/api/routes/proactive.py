"""
v10.0 Proactive Autonomy API Routes
===================================

API endpoints for proactive opportunity matching and notifications.

Features:
- GET /proactive/matches/{profile_id} - Get opportunity matches for a profile
- GET /proactive/notifications/{profile_id} - Get proactive notifications
- POST /proactive/trigger/{job_name} - Manually trigger a proactive job
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from tools.database import get_supabase_client
from proactive.config import is_proactive_enabled, is_feature_enabled, PROACTIVE_CONFIG

logger = structlog.get_logger()

router = APIRouter(prefix="/proactive", tags=["proactive"])


# =====================================================
# Request/Response Models
# =====================================================

class TriggerJobResponse(BaseModel):
    success: bool
    job_name: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class OpportunityMatch(BaseModel):
    source: str
    source_id: str
    opportunity_name: str
    opportunity_type: Optional[str]
    organization: Optional[str]
    category: Optional[str]
    deadline: Optional[str]
    prestige_score: Optional[float]
    match_score: float
    match_reasons: List[str]


class MatchesResponse(BaseModel):
    success: bool
    profile_id: str
    matches: List[Dict[str, Any]]
    opportunities_checked: int
    awards_checked: int
    proactive_enabled: bool


# =====================================================
# Status & Config Endpoints
# =====================================================

@router.get("/status")
async def get_proactive_status():
    """
    Get proactive autonomy status and configuration.

    Returns current feature flags and job configuration.
    """
    return {
        "enabled": PROACTIVE_CONFIG.enabled,
        "features": {
            "opportunity_match": PROACTIVE_CONFIG.opportunity_match,
            "deadline_alerts": PROACTIVE_CONFIG.deadline_alerts,
            "stall_detection": PROACTIVE_CONFIG.stall_detection,
            "inactivity_check": PROACTIVE_CONFIG.inactivity_check,
            "outcome_tracking": PROACTIVE_CONFIG.outcome_tracking,
        },
        "schedules": {
            "opportunity_match": f"Every {PROACTIVE_CONFIG.opportunity_match_interval_hours} hour(s)",
            "deadline_alerts": f"Every {PROACTIVE_CONFIG.deadline_check_interval_hours} hours",
            "stall_detection": f"Daily at {PROACTIVE_CONFIG.stall_check_daily_hour}:00",
        },
    }


# =====================================================
# Opportunity Matching Endpoints
# =====================================================

@router.get("/matches/{profile_id}", response_model=MatchesResponse)
async def get_opportunity_matches(
    profile_id: str,
    max_matches: int = Query(default=5, ge=1, le=20),
    include_awards: bool = True,
    include_opportunities: bool = True,
):
    """
    Get proactive opportunity matches for a profile.

    This is the HERO FEATURE for v10.0 - proactively suggests
    opportunities and awards matching the student's profile.

    Args:
        profile_id: Student profile UUID
        max_matches: Maximum matches to return (1-20)
        include_awards: Include awards in matching
        include_opportunities: Include summer programs/opportunities

    Returns:
        List of matched opportunities with scores and reasons
    """
    try:
        from proactive.opportunity_matcher import match_opportunities_for_profile

        db = get_supabase_client()

        # Get matches
        matches = await match_opportunities_for_profile(
            db,
            profile_id,
            max_matches=max_matches,
        )

        # Filter by source if requested
        if not include_awards:
            matches = [m for m in matches if m.get("source") != "award"]
        if not include_opportunities:
            matches = [m for m in matches if m.get("source") != "opportunity"]

        # Count sources checked (from logs or estimate)
        opportunities_checked = len([m for m in matches if m.get("source") == "opportunity"])
        awards_checked = len([m for m in matches if m.get("source") == "award"])

        return MatchesResponse(
            success=True,
            profile_id=profile_id,
            matches=matches,
            opportunities_checked=opportunities_checked,
            awards_checked=awards_checked,
            proactive_enabled=is_proactive_enabled(),
        )

    except Exception as e:
        logger.error("get_matches_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/{profile_id}")
async def get_proactive_notifications(
    profile_id: str,
    status: Optional[str] = Query(default=None, description="Filter by status: pending, sent, dismissed"),
    notification_type: Optional[str] = Query(default=None, description="Filter by type: opportunity_match, deadline_alert, etc."),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Get proactive notifications for a profile.

    Returns stored notifications from nudge_queue and proactive_notifications tables.

    Args:
        profile_id: Student profile UUID
        status: Filter by notification status
        notification_type: Filter by notification type
        limit: Maximum notifications to return
    """
    try:
        db = get_supabase_client()

        # Query proactive_notifications table
        query = db.table("proactive_notifications").select("*").eq(
            "profile_id", profile_id
        ).order("created_at", desc=True).limit(limit)

        if status:
            query = query.eq("status", status)
        if notification_type:
            query = query.eq("notification_type", notification_type)

        result = query.execute()
        notifications = result.data or []

        # Also get from nudge_queue
        nudge_query = db.table("nudge_queue").select("*").eq(
            "profile_id", profile_id
        ).order("created_at", desc=True).limit(limit)

        if status:
            nudge_query = nudge_query.eq("status", status)
        if notification_type:
            nudge_query = nudge_query.eq("nudge_type", notification_type)

        nudge_result = nudge_query.execute()
        nudges = nudge_result.data or []

        return {
            "success": True,
            "profile_id": profile_id,
            "notifications": notifications,
            "nudges": nudges,
            "total_count": len(notifications) + len(nudges),
        }

    except Exception as e:
        logger.error("get_notifications_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/{notification_id}/dismiss")
async def dismiss_notification(notification_id: str):
    """
    Dismiss a proactive notification.

    Args:
        notification_id: Notification UUID
    """
    try:
        db = get_supabase_client()

        result = db.table("proactive_notifications").update({
            "status": "dismissed",
            "dismissed_at": datetime.now().isoformat(),
        }).eq("id", notification_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {
            "success": True,
            "notification_id": notification_id,
            "status": "dismissed",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("dismiss_notification_error", notification_id=notification_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/{notification_id}/action")
async def record_notification_action(
    notification_id: str,
    action: str = Query(..., description="Action taken: clicked, applied, saved, ignored"),
):
    """
    Record user action on a notification.

    Args:
        notification_id: Notification UUID
        action: The action taken (clicked, applied, saved, ignored)
    """
    try:
        db = get_supabase_client()

        # Get notification
        notification = db.table("proactive_notifications").select("*").eq(
            "id", notification_id
        ).single().execute()

        if not notification.data:
            raise HTTPException(status_code=404, detail="Notification not found")

        # Update with action
        metadata = notification.data.get("metadata", {}) or {}
        actions = metadata.get("actions", [])
        actions.append({
            "action": action,
            "timestamp": datetime.now().isoformat(),
        })
        metadata["actions"] = actions

        result = db.table("proactive_notifications").update({
            "status": "actioned" if action in ["clicked", "applied"] else notification.data["status"],
            "metadata": metadata,
        }).eq("id", notification_id).execute()

        return {
            "success": True,
            "notification_id": notification_id,
            "action": action,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("record_action_error", notification_id=notification_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Job Trigger Endpoints (Manual/Testing)
# =====================================================

@router.post("/trigger/{job_name}", response_model=TriggerJobResponse)
async def trigger_proactive_job(job_name: str):
    """
    Manually trigger a proactive job.

    Useful for testing or on-demand execution.

    Args:
        job_name: Name of job to trigger (opportunity_match, deadline_alerts, stall_detection, inactivity_check)
    """
    valid_jobs = ["opportunity_match", "deadline_alerts", "stall_detection", "inactivity_check"]

    if job_name not in valid_jobs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid job name. Valid options: {valid_jobs}"
        )

    try:
        db = get_supabase_client()

        if job_name == "opportunity_match":
            from proactive.opportunity_matcher import job_opportunity_match
            result = await job_opportunity_match(db)

        elif job_name == "deadline_alerts":
            from proactive.scheduler import _job_deadline_alerts
            result = await _job_deadline_alerts(db)

        elif job_name == "stall_detection":
            from proactive.scheduler import _job_stall_detection
            result = await _job_stall_detection(db)

        elif job_name == "inactivity_check":
            from proactive.scheduler import _job_inactivity_check
            result = await _job_inactivity_check(db)

        return TriggerJobResponse(
            success=True,
            job_name=job_name,
            result=result,
        )

    except Exception as e:
        logger.error("trigger_job_error", job_name=job_name, error=str(e))
        return TriggerJobResponse(
            success=False,
            job_name=job_name,
            error=str(e),
        )


@router.post("/trigger/all")
async def trigger_all_proactive_jobs():
    """
    Trigger all proactive jobs at once.

    Useful for initial population or testing.
    """
    results = {}

    for job_name in ["opportunity_match", "deadline_alerts", "stall_detection", "inactivity_check"]:
        try:
            response = await trigger_proactive_job(job_name)
            results[job_name] = {
                "success": response.success,
                "result": response.result,
                "error": response.error,
            }
        except Exception as e:
            results[job_name] = {
                "success": False,
                "error": str(e),
            }

    return {
        "success": all(r["success"] for r in results.values()),
        "results": results,
    }
