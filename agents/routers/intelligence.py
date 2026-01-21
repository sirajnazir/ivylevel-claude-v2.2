"""
Intelligence Router - FastAPI endpoints for the Autonomous Intelligence Layer.

This router exposes the autonomous coaching capabilities:
- Reasoning cycles
- Student intelligence profiles
- Coaching assets
- Outcome-driven goals
- Proactive notifications

All endpoints are prefixed with /intelligence.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import logging

from services import AutonomousMonitorService
from intelligence.primitives import GoalType
from tools.database import get_supabase_client

logger = logging.getLogger(__name__)

# Create router
intelligence_router = APIRouter(
    prefix="/intelligence",
    tags=["intelligence"],
)

# Global service instance (initialized on first use)
_service: Optional[AutonomousMonitorService] = None


async def get_intelligence_service() -> AutonomousMonitorService:
    """Get or create the intelligence service singleton."""
    global _service
    if _service is None:
        client = get_supabase_client()
        _service = AutonomousMonitorService(client)
        await _service.initialize(seed_assets=True)
    return _service


# =============================================================================
# Request/Response Models
# =============================================================================


class RunReasoningRequest(BaseModel):
    """Request to run a reasoning cycle."""
    profile_id: str
    trigger_event: Optional[str] = None


class CreateGoalRequest(BaseModel):
    """Request to create a new goal."""
    profile_id: str
    primary_outcome: str
    goal_type: str = "achieve"
    not_goal: Optional[List[str]] = None
    target_date: Optional[datetime] = None


class RecordOutcomeRequest(BaseModel):
    """Request to record an outcome."""
    profile_id: str
    outcome_type: str
    outcome_data: Dict[str, Any]
    related_asset_ids: Optional[List[str]] = None


class HandleEventRequest(BaseModel):
    """Request to handle an event."""
    event_type: str
    profile_id: str
    event_data: Optional[Dict[str, Any]] = None


class LearnPatternRequest(BaseModel):
    """Request to learn a pattern from interaction."""
    profile_id: str
    pattern_type: str
    observation: str
    confidence: float = 0.5
    interaction_id: Optional[str] = None


# =============================================================================
# Reasoning Endpoints
# =============================================================================


@intelligence_router.post("/reasoning/run")
async def run_reasoning_cycle(request: RunReasoningRequest):
    """
    Run an autonomous reasoning cycle for a student.

    This triggers the MONITOR → PREDICT → DECIDE → ACT → LEARN loop.
    """
    try:
        service = await get_intelligence_service()
        result = await service.run_reasoning_cycle(
            profile_id=request.profile_id,
            trigger_event=request.trigger_event,
        )
        return result
    except Exception as e:
        logger.error(f"Reasoning cycle failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.post("/reasoning/event")
async def handle_event(request: HandleEventRequest):
    """
    Handle an external event that might trigger reasoning.

    Events like task_completed, deadline_approaching, crisis, etc.
    """
    try:
        service = await get_intelligence_service()
        result = await service.handle_event(
            event_type=request.event_type,
            profile_id=request.profile_id,
            event_data=request.event_data,
        )
        return result
    except Exception as e:
        logger.error(f"Event handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Student Intelligence Endpoints
# =============================================================================


@intelligence_router.get("/student/{profile_id}/summary")
async def get_student_summary(profile_id: str):
    """Get a comprehensive summary of a student's intelligence state."""
    try:
        service = await get_intelligence_service()
        summary = await service.get_student_summary(profile_id)
        return summary
    except Exception as e:
        logger.error(f"Failed to get student summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/student/{profile_id}/adaptations")
async def get_coaching_adaptations(profile_id: str):
    """Get coaching adaptations for a student based on their profile."""
    try:
        service = await get_intelligence_service()
        adaptations = await service.student_manager.get_coaching_adaptations(UUID(profile_id))
        return {"profile_id": profile_id, "adaptations": adaptations}
    except Exception as e:
        logger.error(f"Failed to get adaptations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/student/{profile_id}/archetype")
async def get_student_archetype(profile_id: str):
    """Infer the student's archetype based on their profile."""
    try:
        service = await get_intelligence_service()
        archetype = await service.student_manager.infer_archetype(UUID(profile_id))
        return {"profile_id": profile_id, "archetype": archetype}
    except Exception as e:
        logger.error(f"Failed to get archetype: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.post("/student/learn")
async def learn_pattern(request: LearnPatternRequest):
    """Learn a pattern from an interaction."""
    try:
        service = await get_intelligence_service()
        success = await service.student_manager.learn_from_interaction(
            profile_id=UUID(request.profile_id),
            pattern_type=request.pattern_type,
            observation=request.observation,
            confidence=request.confidence,
            interaction_id=request.interaction_id,
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Failed to learn pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Goal Endpoints
# =============================================================================


@intelligence_router.post("/goals/create")
async def create_goal(request: CreateGoalRequest):
    """Create a new outcome-driven goal."""
    try:
        service = await get_intelligence_service()
        goal_type = GoalType(request.goal_type)
        goal = await service.create_goal(
            profile_id=request.profile_id,
            primary_outcome=request.primary_outcome,
            goal_type=goal_type,
            not_goal=request.not_goal,
            target_date=request.target_date,
        )
        return goal.to_db_dict()
    except Exception as e:
        logger.error(f"Failed to create goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/goals/{profile_id}")
async def get_active_goals(
    profile_id: str,
    agent_name: Optional[str] = None,
):
    """Get active goals for a student."""
    try:
        service = await get_intelligence_service()
        goals = await service.goal_manager.get_active_goals(
            UUID(profile_id),
            agent_name=agent_name,
        )
        return {
            "profile_id": profile_id,
            "goals": [g.to_db_dict() for g in goals],
            "count": len(goals),
        }
    except Exception as e:
        logger.error(f"Failed to get goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/goals/{profile_id}/at-risk")
async def get_goals_at_risk(profile_id: str):
    """Get goals that are at risk of missing their deadline."""
    try:
        service = await get_intelligence_service()
        goals = await service.goal_manager.get_goals_at_risk(UUID(profile_id))
        return {
            "profile_id": profile_id,
            "at_risk_goals": [g.to_db_dict() for g in goals],
            "count": len(goals),
        }
    except Exception as e:
        logger.error(f"Failed to get at-risk goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/goals/{profile_id}/summary")
async def get_goals_summary(profile_id: str):
    """Get a summary of goals for a student."""
    try:
        service = await get_intelligence_service()
        summary = await service.goal_manager.get_summary(UUID(profile_id))
        return {"profile_id": profile_id, **summary}
    except Exception as e:
        logger.error(f"Failed to get goals summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.post("/goals/{goal_id}/achieved")
async def mark_goal_achieved(goal_id: str):
    """Mark a goal as achieved."""
    try:
        service = await get_intelligence_service()
        goal = await service.goal_manager.mark_achieved(UUID(goal_id))
        if goal:
            return goal.to_db_dict()
        raise HTTPException(status_code=404, detail="Goal not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark goal achieved: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Notification Endpoints
# =============================================================================


@intelligence_router.get("/notifications/{profile_id}")
async def get_pending_notifications(
    profile_id: str,
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get pending notifications for a student."""
    try:
        service = await get_intelligence_service()
        notifications = await service.get_pending_notifications(profile_id, limit)
        return {
            "profile_id": profile_id,
            "notifications": notifications,
            "count": len(notifications),
        }
    except Exception as e:
        logger.error(f"Failed to get notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.post("/notifications/{notification_id}/viewed")
async def mark_notification_viewed(notification_id: str):
    """Mark a notification as viewed."""
    try:
        service = await get_intelligence_service()
        success = await service.mark_notification_viewed(notification_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Failed to mark notification viewed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Outcome Endpoints
# =============================================================================


@intelligence_router.post("/outcomes/record")
async def record_outcome(request: RecordOutcomeRequest):
    """Record an actual outcome (win, completion, etc.)."""
    try:
        service = await get_intelligence_service()
        success = await service.record_outcome(
            profile_id=request.profile_id,
            outcome_type=request.outcome_type,
            outcome_data=request.outcome_data,
            related_asset_ids=request.related_asset_ids,
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Failed to record outcome: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Asset Endpoints
# =============================================================================


@intelligence_router.get("/assets")
async def list_coaching_assets(
    domain: Optional[str] = None,
    asset_type: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
):
    """List coaching assets with optional filters."""
    try:
        service = await get_intelligence_service()

        from intelligence.primitives import AssetType, AssetDomain

        assets = []

        if domain and asset_type:
            assets = await service.asset_registry.list_by_type(
                AssetType(asset_type),
                AssetDomain(domain),
                limit=limit,
            )
        elif domain:
            assets = await service.asset_registry.list_by_domain(
                AssetDomain(domain),
                limit=limit,
            )
        elif asset_type:
            assets = await service.asset_registry.list_by_type(
                AssetType(asset_type),
                limit=limit,
            )
        else:
            # List techniques by default
            assets = await service.asset_registry.list_by_type(
                AssetType.TECHNIQUE,
                limit=limit,
            )

        return {
            "assets": [a.to_db_dict() for a in assets],
            "count": len(assets),
        }
    except Exception as e:
        logger.error(f"Failed to list assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/assets/{asset_id}")
async def get_coaching_asset(asset_id: str):
    """Get a specific coaching asset by ID."""
    try:
        service = await get_intelligence_service()
        asset = await service.asset_registry.get(UUID(asset_id))
        if asset:
            return asset.to_db_dict()
        raise HTTPException(status_code=404, detail="Asset not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/assets/top-effective")
async def get_top_effective_assets(
    domain: Optional[str] = None,
    archetype: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get the most effective coaching assets."""
    try:
        service = await get_intelligence_service()

        from intelligence.primitives import AssetDomain

        assets = await service.asset_registry.get_top_effective(
            domain=AssetDomain(domain) if domain else None,
            archetype=archetype,
            min_usage=3,
            limit=limit,
        )

        return {
            "assets": [a.to_db_dict() for a in assets],
            "count": len(assets),
            "filters": {"domain": domain, "archetype": archetype},
        }
    except Exception as e:
        logger.error(f"Failed to get top effective assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Health/Status Endpoints
# =============================================================================


@intelligence_router.get("/health")
async def intelligence_health():
    """Check health of the intelligence service."""
    try:
        service = await get_intelligence_service()
        return {
            "status": "healthy",
            "initialized": service.is_initialized,
            "version": "1.0.0",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


# =============================================================================
# Asset Loader Endpoints
# =============================================================================


class SeedAssetsRequest(BaseModel):
    """Request to seed assets from a coach library."""
    coach_id: str
    overwrite: bool = False
    dry_run: bool = False
    skip_validation: bool = False


class ValidateAssetRequest(BaseModel):
    """Request to validate a YAML file path."""
    file_path: str


@intelligence_router.get("/loader/coaches")
async def list_coach_libraries():
    """List available coach asset libraries."""
    try:
        from intelligence.assets.loader import list_available_coaches, DATA_PATH

        coaches = list_available_coaches()

        coach_details = []
        for coach in coaches:
            coach_dir = DATA_PATH / coach
            yaml_files = list(coach_dir.glob("**/*.yaml"))
            coach_details.append({
                "coach_id": coach,
                "yaml_files": len(yaml_files),
                "path": str(coach_dir),
            })

        return {
            "coaches": coach_details,
            "count": len(coaches),
            "data_path": str(DATA_PATH),
        }
    except Exception as e:
        logger.error(f"Failed to list coaches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/loader/summary/{coach_id}")
async def get_coach_summary(coach_id: str):
    """Get summary of assets for a coach."""
    try:
        from intelligence.assets.loader import load_coach_assets, AssetLoader

        assets = load_coach_assets(coach_id, validate=False)

        if not assets:
            raise HTTPException(status_code=404, detail=f"No assets found for coach: {coach_id}")

        loader = AssetLoader()
        summary = loader.get_asset_summary(assets)

        return {
            "coach_id": coach_id,
            "summary": summary,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get coach summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.post("/loader/validate")
async def validate_asset_file_endpoint(request: ValidateAssetRequest):
    """Validate a YAML asset file against the schema."""
    try:
        from pathlib import Path
        from intelligence.assets.loader import validate_asset_file

        yaml_path = Path(request.file_path)

        if not yaml_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

        is_valid, errors = validate_asset_file(yaml_path)

        return {
            "file_path": request.file_path,
            "valid": is_valid,
            "errors": errors[:20] if errors else [],
            "error_count": len(errors),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.post("/loader/seed")
async def seed_coach_assets(request: SeedAssetsRequest, background_tasks: BackgroundTasks):
    """
    Seed assets from a coach library to the database.

    This can be run in the background for large asset libraries.
    """
    try:
        from intelligence.assets.loader import load_coach_assets, AssetLoader

        # Load assets
        assets = load_coach_assets(
            request.coach_id,
            validate=not request.skip_validation,
        )

        if not assets:
            raise HTTPException(
                status_code=404,
                detail=f"No assets found for coach: {request.coach_id}",
            )

        # Get registry
        service = await get_intelligence_service()
        registry = service.asset_registry

        # Seed to database
        loader = AssetLoader()
        summary = await loader.seed_to_database(
            registry=registry,
            assets=assets,
            overwrite=request.overwrite,
            dry_run=request.dry_run,
        )

        return {
            "coach_id": request.coach_id,
            "result": summary,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to seed assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/loader/assets/{coach_id}")
async def list_coach_assets(
    coach_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List assets from a coach library (from files, not database)."""
    try:
        from intelligence.assets.loader import load_coach_assets

        assets = load_coach_assets(coach_id, validate=False)

        if not assets:
            raise HTTPException(
                status_code=404,
                detail=f"No assets found for coach: {coach_id}",
            )

        # Apply pagination
        paginated = assets[offset:offset + limit]

        return {
            "coach_id": coach_id,
            "total": len(assets),
            "offset": offset,
            "limit": limit,
            "assets": [
                {
                    "name": a.name,
                    "asset_type": a.asset_type,
                    "domain": a.domain,
                    "tags": a.tags[:5],  # First 5 tags
                    "technique_id": a.content.get("technique_id", ""),
                }
                for a in paginated
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list coach assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence_router.get("/loader/asset/{coach_id}/{technique_id}")
async def get_coach_asset_by_id(coach_id: str, technique_id: str):
    """Get a specific asset from a coach library by technique ID."""
    try:
        from intelligence.assets.loader import load_coach_assets

        assets = load_coach_assets(coach_id, validate=False)

        for asset in assets:
            if asset.content.get("technique_id") == technique_id:
                return asset.to_db_dict()

        raise HTTPException(
            status_code=404,
            detail=f"Technique {technique_id} not found in {coach_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))
