"""
IvyQuest v10.0 Database Tools
=============================
Supabase client and helper functions for agent data operations.
"""

from supabase import create_client, Client
from typing import Dict, List, Any, Optional
from functools import lru_cache
import structlog

from config import settings

logger = structlog.get_logger()


@lru_cache()
def get_supabase_client() -> Client:
    """Get cached Supabase client using service role key."""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )


# Convenience accessor
supabase = get_supabase_client()


# =====================================================
# Profile Operations
# =====================================================

async def get_profile(profile_id: str) -> Optional[Dict]:
    """Get profile by ID."""
    try:
        result = supabase.table("profiles").select("*").eq("id", profile_id).single().execute()
        return result.data
    except Exception as e:
        logger.error("get_profile_error", profile_id=profile_id, error=str(e))
        return None


async def get_profile_with_assessment(profile_id: str) -> Optional[Dict]:
    """
    Get complete profile with assessment data merged.

    This is the preferred method for agents to get profile data.
    It fetches from both profiles and assessments tables and merges them,
    ensuring profile_data from the latest assessment is always included.

    Returns:
        Dict with profile fields + profile_data from latest assessment
    """
    try:
        # Start with profile (may be minimal - just id, email, role)
        profile_result = supabase.table("profiles").select("*").eq("id", profile_id).maybe_single().execute()

        # Get latest completed assessment for this user
        assessment_result = supabase.table("assessments").select(
            "id, profile_data, scores, archetype, completeness_score, completed_at"
        ).eq("user_id", profile_id).order(
            "completed_at", desc=True
        ).limit(1).execute()

        # If no profile and no assessment, user doesn't exist
        if not profile_result.data and (not assessment_result.data or len(assessment_result.data) == 0):
            logger.warning("get_profile_with_assessment: no data found", profile_id=profile_id)
            return None

        # Build merged profile
        profile = profile_result.data if profile_result.data else {"id": profile_id}

        # Merge assessment data if available
        if assessment_result.data and len(assessment_result.data) > 0:
            assessment = assessment_result.data[0]
            profile["profile_data"] = assessment.get("profile_data") or {}
            profile["scores"] = assessment.get("scores") or {}
            profile["archetype"] = assessment.get("archetype")
            profile["completeness_score"] = assessment.get("completeness_score")
            profile["assessment_id"] = assessment.get("id")
            profile["completed_at"] = assessment.get("completed_at")

            logger.info(
                "get_profile_with_assessment: merged data",
                profile_id=profile_id,
                has_profile_data=bool(profile.get("profile_data")),
                assessment_id=assessment.get("id")
            )
        else:
            # No assessment - set empty profile_data
            profile["profile_data"] = {}
            logger.warning("get_profile_with_assessment: no assessment found", profile_id=profile_id)

        return profile

    except Exception as e:
        logger.error("get_profile_with_assessment_error", profile_id=profile_id, error=str(e))
        return None


async def update_profile(profile_id: str, updates: Dict) -> bool:
    """Update profile with new data."""
    try:
        supabase.table("profiles").update(updates).eq("id", profile_id).execute()
        return True
    except Exception as e:
        logger.error("update_profile_error", profile_id=profile_id, error=str(e))
        return False


async def get_profile_by_assessment(assessment_id: str) -> Optional[Dict]:
    """Get profile linked to an assessment."""
    try:
        result = supabase.table("profiles").select("*").eq("assessment_id", assessment_id).single().execute()
        return result.data
    except Exception as e:
        logger.warning("profile_not_found_for_assessment", assessment_id=assessment_id)
        return None


# =====================================================
# Crisis Operations
# =====================================================

async def create_crisis(crisis_data: Dict) -> Optional[Dict]:
    """Create a new crisis record."""
    try:
        result = supabase.table("crises").insert(crisis_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error("create_crisis_error", error=str(e))
        return None


async def get_crisis(crisis_id: str) -> Optional[Dict]:
    """Get crisis by ID."""
    try:
        result = supabase.table("crises").select("*").eq("id", crisis_id).single().execute()
        return result.data
    except Exception as e:
        logger.error("get_crisis_error", crisis_id=crisis_id, error=str(e))
        return None


async def update_crisis(crisis_id: str, updates: Dict) -> bool:
    """Update crisis record."""
    try:
        supabase.table("crises").update(updates).eq("id", crisis_id).execute()
        return True
    except Exception as e:
        logger.error("update_crisis_error", crisis_id=crisis_id, error=str(e))
        return False


async def get_pending_crises(profile_id: str) -> List[Dict]:
    """Get all pending crises for a profile."""
    try:
        result = supabase.table("crises").select("*").eq("profile_id", profile_id).in_("status", ["detected", "proposed"]).execute()
        return result.data or []
    except Exception as e:
        logger.error("get_pending_crises_error", profile_id=profile_id, error=str(e))
        return []


# =====================================================
# Project Operations
# =====================================================

async def get_projects(profile_id: str, status: Optional[str] = None) -> List[Dict]:
    """Get projects for a profile, optionally filtered by status."""
    try:
        query = supabase.table("projects").select("*").eq("profile_id", profile_id)
        if status:
            query = query.eq("status", status)
        result = query.execute()
        return result.data or []
    except Exception as e:
        logger.error("get_projects_error", profile_id=profile_id, error=str(e))
        return []


async def create_project(project_data: Dict) -> Optional[Dict]:
    """Create a new project."""
    try:
        result = supabase.table("projects").insert(project_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error("create_project_error", error=str(e))
        return None


async def get_project_steps(project_id: str) -> List[Dict]:
    """Get all steps for a project."""
    try:
        result = supabase.table("project_steps").select("*").eq("project_id", project_id).order("step_order").execute()
        return result.data or []
    except Exception as e:
        logger.error("get_project_steps_error", project_id=project_id, error=str(e))
        return []


async def create_project_steps(steps: List[Dict]) -> bool:
    """Create multiple project steps."""
    try:
        supabase.table("project_steps").insert(steps).execute()
        return True
    except Exception as e:
        logger.error("create_project_steps_error", error=str(e))
        return False


# =====================================================
# State Versioning Operations
# =====================================================

async def create_state_version(
    profile_id: str,
    agent: str,
    state: Dict,
    event_type: str,
    created_by: str = "agent",
    rationale: Optional[str] = None,
    event_payload: Optional[Dict] = None
) -> Optional[str]:
    """Create a new state version (uses database function)."""
    try:
        result = supabase.rpc("create_state_version", {
            "p_profile_id": profile_id,
            "p_agent": agent,
            "p_state": state,
            "p_event_type": event_type,
            "p_created_by": created_by,
            "p_rationale": rationale,
            "p_event_payload": event_payload
        }).execute()
        return result.data
    except Exception as e:
        logger.error("create_state_version_error", profile_id=profile_id, agent=agent, error=str(e))
        return None


async def get_latest_state(profile_id: str, agent: str) -> Optional[Dict]:
    """Get the latest state for an agent/profile."""
    try:
        result = supabase.rpc("get_latest_state", {
            "p_profile_id": profile_id,
            "p_agent": agent
        }).execute()
        return result.data
    except Exception as e:
        logger.error("get_latest_state_error", profile_id=profile_id, agent=agent, error=str(e))
        return None


# =====================================================
# Archetype Operations
# =====================================================

async def get_archetypes() -> List[Dict]:
    """Get all active archetypes."""
    try:
        result = supabase.table("archetypes").select("*").eq("is_active", True).execute()
        return result.data or []
    except Exception as e:
        logger.error("get_archetypes_error", error=str(e))
        return []


async def get_archetype(archetype_id: str) -> Optional[Dict]:
    """Get archetype by ID."""
    try:
        result = supabase.table("archetypes").select("*").eq("id", archetype_id).single().execute()
        return result.data
    except Exception as e:
        logger.error("get_archetype_error", archetype_id=archetype_id, error=str(e))
        return None


# =====================================================
# Chetty Baselines Operations
# =====================================================

async def get_chetty_baseline_db(zip_code: str, school_id: Optional[str] = None) -> Dict:
    """Get Chetty baseline from database."""
    try:
        result = supabase.rpc("get_chetty_baseline", {
            "p_zip": zip_code,
            "p_school_id": school_id
        }).execute()

        if result.data and len(result.data) > 0:
            return result.data[0]

        # Return default
        return {
            "expected_performance": 0.7,
            "multiplier": 1.0,
            "mobility_rate": 0.5,
            "source": "default"
        }
    except Exception as e:
        logger.error("get_chetty_baseline_error", zip_code=zip_code, error=str(e))
        return {
            "expected_performance": 0.7,
            "multiplier": 1.0,
            "mobility_rate": 0.5,
            "source": "error_fallback"
        }


# =====================================================
# Awards & Opportunities Operations
# =====================================================

async def get_awards(filters: Optional[Dict] = None) -> List[Dict]:
    """Get awards, optionally filtered."""
    try:
        query = supabase.table("awards").select("*").eq("is_active", True)
        if filters:
            if "category" in filters:
                query = query.eq("category", filters["category"])
            if "level" in filters:
                query = query.eq("level", filters["level"])
        result = query.execute()
        return result.data or []
    except Exception as e:
        logger.error("get_awards_error", error=str(e))
        return []


async def get_opportunities(filters: Optional[Dict] = None) -> List[Dict]:
    """Get opportunities, optionally filtered."""
    try:
        query = supabase.table("opportunities").select("*").eq("is_active", True)
        if filters:
            if "type" in filters:
                query = query.eq("type", filters["type"])
        result = query.execute()
        return result.data or []
    except Exception as e:
        logger.error("get_opportunities_error", error=str(e))
        return []
