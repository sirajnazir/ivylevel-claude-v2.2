"""
Database Tools
==============

Read-only database tools for Letta agents to access student data.

These tools wrap existing Supabase queries without modifying data.
"""

import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = structlog.get_logger()


# Letta tool definitions for database access
DATABASE_TOOLS = [
    {
        "name": "get_student_profile",
        "description": "Get the complete student profile including assessment data, archetype, and goals.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile_id": {
                    "type": "string",
                    "description": "Student profile ID",
                },
            },
            "required": ["profile_id"],
        },
    },
    {
        "name": "get_active_gameplan",
        "description": "Get the student's current active gameplan with tasks and milestones.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile_id": {
                    "type": "string",
                    "description": "Student profile ID",
                },
            },
            "required": ["profile_id"],
        },
    },
    {
        "name": "get_recent_interactions",
        "description": "Get recent coaching interactions and conversations with the student.",
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
                    "description": "Maximum interactions to return",
                },
            },
            "required": ["profile_id"],
        },
    },
    {
        "name": "get_goal_progress",
        "description": "Get progress on the student's goals including completion status and milestones.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile_id": {
                    "type": "string",
                    "description": "Student profile ID",
                },
            },
            "required": ["profile_id"],
        },
    },
]


async def get_student_profile(
    profile_id: str,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Get the complete student profile.

    Args:
        profile_id: Student profile ID
        supabase_client: Supabase client

    Returns:
        Dictionary with profile data
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        # Fetch main profile
        profile_result = supabase_client.table("profiles") \
            .select("*") \
            .eq("id", profile_id) \
            .single() \
            .execute()

        if not profile_result.data:
            return {
                "success": False,
                "error": f"Profile {profile_id} not found",
                "profile": None,
            }

        profile = profile_result.data

        # FIX: Build name from first_name + last_name (no "name" column exists)
        name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Unknown"

        # FIX: Build test_scores from individual columns (no "test_scores" dict exists)
        test_scores = {}
        if profile.get('sat_score'):
            test_scores['sat'] = profile['sat_score']
        if profile.get('act_score'):
            test_scores['act'] = profile['act_score']

        # TODO: student_intelligence table doesn't exist yet
        # When created, uncomment: intel_result = supabase_client.table("student_intelligence")...
        intelligence = {}
        logger.debug("letta_student_intelligence_skipped", reason="table not yet created")

        logger.info("letta_get_student_profile", profile_id=profile_id)

        return {
            "success": True,
            "profile": {
                "id": profile_id,
                "name": name,  # FIX: built from first_name + last_name
                "grade": profile.get("grade", ""),
                "school_type": profile.get("school_type", ""),
                "gpa": profile.get("gpa"),
                "test_scores": test_scores,  # FIX: built from sat_score, act_score
                "target_schools": profile.get("target_schools") or [],
                "intended_major": profile.get("intended_major") or profile.get("target_major", ""),
                "activities": [],  # TODO: activities table exists but may be empty
                "awards": [],  # TODO: need awards tracking table
                "created_at": profile.get("created_at"),
            },
            "assessment": {
                # FIX: Use profile's narrative_* columns (assessment_narratives table doesn't exist)
                "archetype": profile.get("archetype", "Undetermined"),
                "narrative_dna": profile.get("narrative_dna", ""),
                "cri_score": profile.get("cri_score"),
                "strengths": profile.get("narrative_themes") or [],
                "growth_areas": [],  # TODO: track growth areas
            },
            "intelligence": {
                "patterns": intelligence.get("patterns", []),
                "adaptations": intelligence.get("coaching_adaptations", {}),
                "last_updated": intelligence.get("updated_at"),
            },
        }

    except Exception as e:
        logger.error("letta_get_student_profile_error", profile_id=profile_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "profile": None,
        }


async def get_active_gameplan(
    profile_id: str,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Get the student's active gameplan.

    Args:
        profile_id: Student profile ID
        supabase_client: Supabase client

    Returns:
        Dictionary with gameplan and tasks
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        # Fetch active gameplan
        # FIX: Table is "game_plans" not "gameplans", column is "plan_status" not "status"
        gameplan_result = supabase_client.table("game_plans") \
            .select("*") \
            .eq("profile_id", profile_id) \
            .eq("plan_status", "active") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if not gameplan_result.data:
            return {
                "success": True,
                "has_gameplan": False,
                "gameplan": None,
                "tasks": [],
                "message": "No active gameplan found for this student",
            }

        gp = gameplan_result.data[0]

        # TODO: tasks table doesn't exist yet - return empty for now
        # When tasks table is created, uncomment this:
        # tasks_result = supabase_client.table("tasks").select("*").eq("gameplan_id", gp["id"]).execute()
        tasks = []
        logger.info("letta_get_active_gameplan_tasks_skipped", reason="tasks table not yet created")

        # Organize tasks by priority (empty for now)
        p0_tasks = [t for t in tasks if t.get("priority") == "P0"]
        p1_tasks = [t for t in tasks if t.get("priority") == "P1"]
        p2_tasks = [t for t in tasks if t.get("priority") == "P2"]

        # Calculate completion stats
        total = len(tasks)
        completed = len([t for t in tasks if t.get("status") == "completed"])

        logger.info("letta_get_active_gameplan", profile_id=profile_id, task_count=total)

        # FIX: Map actual column names to expected field names
        plan_data = gp.get("plan_data") or {}

        return {
            "success": True,
            "has_gameplan": True,
            "gameplan": {
                "id": gp["id"],
                "phase": gp.get("current_phase", ""),  # FIX: was "phase"
                "strategic_focus": plan_data.get("strategic_focus", ""),  # FIX: extract from plan_data
                "status": gp.get("plan_status"),  # FIX: was "status"
                "created_at": gp.get("created_at"),
                "milestones": plan_data.get("milestones", []),  # FIX: extract from plan_data
            },
            "tasks": {
                "p0": [_format_task(t) for t in p0_tasks],
                "p1": [_format_task(t) for t in p1_tasks],
                "p2": [_format_task(t) for t in p2_tasks],
            },
            "stats": {
                "total": total,
                "completed": completed,
                "pending": total - completed,
                "completion_rate": round((completed / total * 100) if total > 0 else 0, 1),
            },
        }

    except Exception as e:
        logger.error("letta_get_active_gameplan_error", profile_id=profile_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "gameplan": None,
        }


def _format_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Format a task for output."""
    return {
        "id": task.get("id"),
        "title": task.get("title", ""),
        "description": task.get("description", "")[:200],
        "status": task.get("status", "pending"),
        "priority": task.get("priority", "P2"),
        "due_date": task.get("due_date"),
        "completed_at": task.get("completed_at"),
    }


async def get_recent_interactions(
    profile_id: str,
    limit: int = 10,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Get recent coaching interactions.

    Args:
        profile_id: Student profile ID
        limit: Maximum interactions to return
        supabase_client: Supabase client

    Returns:
        Dictionary with interaction history
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        interactions = []

        # Fetch from proactive_notifications
        try:
            result = supabase_client.table("proactive_notifications") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()

            for row in result.data or []:
                interactions.append({
                    "id": row.get("id"),
                    "type": row.get("notification_type", "notification"),
                    "message": row.get("message", "")[:300],
                    "timestamp": row.get("created_at"),
                    "source": "notification",
                })
        except Exception:
            pass

        # Fetch from execution_logs
        try:
            result = supabase_client.table("execution_logs") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()

            for row in result.data or []:
                interactions.append({
                    "id": row.get("id"),
                    "type": "execution",
                    "message": row.get("action", ""),
                    "timestamp": row.get("created_at"),
                    "source": "execution_log",
                    "technique_used": row.get("technique_used"),
                })
        except Exception:
            pass

        # Sort by timestamp
        interactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        interactions = interactions[:limit]

        logger.info(
            "letta_get_recent_interactions",
            profile_id=profile_id,
            count=len(interactions),
        )

        return {
            "success": True,
            "profile_id": profile_id,
            "interactions": interactions,
            "count": len(interactions),
        }

    except Exception as e:
        logger.error("letta_get_recent_interactions_error", profile_id=profile_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "interactions": [],
        }


async def get_goal_progress(
    profile_id: str,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Get progress on student's goals.

    Args:
        profile_id: Student profile ID
        supabase_client: Supabase client

    Returns:
        Dictionary with goal progress
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        # Fetch all goals
        result = supabase_client.table("outcome_driven_goals") \
            .select("*") \
            .eq("profile_id", profile_id) \
            .order("created_at", desc=True) \
            .execute()

        goals = result.data or []

        active_goals = []
        achieved_goals = []
        at_risk_goals = []

        today = datetime.now()

        for goal in goals:
            goal_data = {
                "id": goal.get("id"),
                "primary_outcome": goal.get("primary_outcome", ""),
                "goal_type": goal.get("goal_type", "achieve"),
                "status": goal.get("status", "active"),
                "progress": goal.get("progress", 0),
                "target_date": goal.get("target_date"),
                "created_at": goal.get("created_at"),
            }

            if goal.get("status") == "achieved":
                goal_data["achieved_at"] = goal.get("achieved_at")
                achieved_goals.append(goal_data)
            elif goal.get("status") == "active":
                active_goals.append(goal_data)

                # Check if at risk
                target_date = goal.get("target_date")
                if target_date:
                    try:
                        target = datetime.fromisoformat(target_date.replace("Z", "+00:00"))
                        days_remaining = (target - today).days
                        progress = goal.get("progress", 0)

                        if days_remaining <= 7 and progress < 70:
                            goal_data["days_remaining"] = days_remaining
                            goal_data["risk_reason"] = f"{days_remaining} days left, {progress}% done"
                            at_risk_goals.append(goal_data)
                    except Exception:
                        pass

        logger.info(
            "letta_get_goal_progress",
            profile_id=profile_id,
            active=len(active_goals),
            achieved=len(achieved_goals),
            at_risk=len(at_risk_goals),
        )

        return {
            "success": True,
            "profile_id": profile_id,
            "goals": {
                "active": active_goals,
                "achieved": achieved_goals,
                "at_risk": at_risk_goals,
            },
            "summary": {
                "total_goals": len(goals),
                "active_count": len(active_goals),
                "achieved_count": len(achieved_goals),
                "at_risk_count": len(at_risk_goals),
            },
        }

    except Exception as e:
        logger.error("letta_get_goal_progress_error", profile_id=profile_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "goals": {},
        }
