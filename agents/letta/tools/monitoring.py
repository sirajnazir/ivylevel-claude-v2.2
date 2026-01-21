"""
Monitoring Tools
================

Tools for deadline checking, opportunity matching, and execution state monitoring.

These tools enable proactive coaching by detecting:
- Upcoming and overdue deadlines
- Relevant opportunities (scholarships, programs, competitions)
- Execution drift and stalls
"""

import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = structlog.get_logger()


# Letta tool definitions for monitoring
MONITORING_TOOLS = [
    {
        "name": "check_upcoming_deadlines",
        "description": "Check for upcoming deadlines within a specified time window. Returns tasks, application deadlines, and milestones.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile_id": {
                    "type": "string",
                    "description": "Student profile ID",
                },
                "days_ahead": {
                    "type": "integer",
                    "default": 7,
                    "description": "Number of days ahead to check",
                },
                "include_overdue": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include overdue items",
                },
            },
            "required": ["profile_id"],
        },
    },
    {
        "name": "match_opportunities",
        "description": "Find relevant opportunities (scholarships, programs, competitions) for the student based on their profile.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile_id": {
                    "type": "string",
                    "description": "Student profile ID",
                },
                "opportunity_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["scholarship", "program", "competition"],
                    "description": "Types of opportunities to search for",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum opportunities to return",
                },
            },
            "required": ["profile_id"],
        },
    },
    {
        "name": "get_execution_state",
        "description": "Get the current execution state for a student, including EDS (Execution Debt Score), task completion rate, and momentum indicators.",
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


async def check_upcoming_deadlines(
    profile_id: str,
    days_ahead: int = 7,
    include_overdue: bool = True,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Check for upcoming deadlines.

    Args:
        profile_id: Student profile ID
        days_ahead: Number of days to look ahead
        include_overdue: Whether to include overdue items
        supabase_client: Supabase client

    Returns:
        Dictionary with deadline information
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        today = datetime.now()
        cutoff_date = today + timedelta(days=days_ahead)

        deadlines = {
            "overdue": [],
            "urgent": [],  # 0-2 days
            "soon": [],    # 3-7 days
            "upcoming": [], # 7+ days
        }

        # Fetch tasks with due dates
        try:
            result = supabase_client.table("tasks") \
                .select("id, title, due_date, status, priority") \
                .eq("profile_id", profile_id) \
                .neq("status", "completed") \
                .order("due_date") \
                .execute()

            for task in result.data or []:
                due_date = task.get("due_date")
                if not due_date:
                    continue

                try:
                    due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    days_until = (due.date() - today.date()).days

                    item = {
                        "id": task["id"],
                        "title": task.get("title", "Unknown"),
                        "due_date": due_date[:10],
                        "days_until": days_until,
                        "priority": task.get("priority", "P2"),
                        "type": "task",
                    }

                    if days_until < 0 and include_overdue:
                        item["days_overdue"] = abs(days_until)
                        deadlines["overdue"].append(item)
                    elif 0 <= days_until <= 2:
                        deadlines["urgent"].append(item)
                    elif 3 <= days_until <= 7:
                        deadlines["soon"].append(item)
                    elif days_until <= days_ahead:
                        deadlines["upcoming"].append(item)

                except Exception:
                    continue

        except Exception as e:
            logger.warning("fetch_task_deadlines_error", error=str(e))

        # Fetch goal deadlines
        try:
            result = supabase_client.table("outcome_driven_goals") \
                .select("id, primary_outcome, target_date, status") \
                .eq("profile_id", profile_id) \
                .eq("status", "active") \
                .execute()

            for goal in result.data or []:
                target_date = goal.get("target_date")
                if not target_date:
                    continue

                try:
                    target = datetime.fromisoformat(target_date.replace("Z", "+00:00"))
                    days_until = (target.date() - today.date()).days

                    item = {
                        "id": goal["id"],
                        "title": goal.get("primary_outcome", "Unknown Goal"),
                        "due_date": target_date[:10],
                        "days_until": days_until,
                        "type": "goal",
                    }

                    if days_until < 0 and include_overdue:
                        item["days_overdue"] = abs(days_until)
                        deadlines["overdue"].append(item)
                    elif 0 <= days_until <= 2:
                        deadlines["urgent"].append(item)
                    elif 3 <= days_until <= 7:
                        deadlines["soon"].append(item)
                    elif days_until <= days_ahead:
                        deadlines["upcoming"].append(item)

                except Exception:
                    continue

        except Exception as e:
            logger.warning("fetch_goal_deadlines_error", error=str(e))

        # Calculate summary
        total_urgent = len(deadlines["overdue"]) + len(deadlines["urgent"])

        logger.info(
            "letta_check_deadlines",
            profile_id=profile_id,
            overdue=len(deadlines["overdue"]),
            urgent=len(deadlines["urgent"]),
            soon=len(deadlines["soon"]),
        )

        return {
            "success": True,
            "profile_id": profile_id,
            "as_of": today.isoformat(),
            "deadlines": deadlines,
            "summary": {
                "total_overdue": len(deadlines["overdue"]),
                "total_urgent": total_urgent,
                "total_soon": len(deadlines["soon"]),
                "total_upcoming": len(deadlines["upcoming"]),
                "needs_attention": total_urgent > 0,
            },
        }

    except Exception as e:
        logger.error("letta_check_deadlines_error", profile_id=profile_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "deadlines": {},
        }


async def match_opportunities(
    profile_id: str,
    opportunity_types: Optional[List[str]] = None,
    limit: int = 10,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Find relevant opportunities for the student.

    Args:
        profile_id: Student profile ID
        opportunity_types: Types of opportunities to search for
        limit: Maximum number of opportunities
        supabase_client: Supabase client

    Returns:
        Dictionary with matched opportunities
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        if opportunity_types is None:
            opportunity_types = ["scholarship", "program", "competition"]

        # Fetch student profile for matching
        profile_result = supabase_client.table("profiles") \
            .select("assessment_data") \
            .eq("id", profile_id) \
            .single() \
            .execute()

        if not profile_result.data:
            return {
                "success": False,
                "error": "Profile not found",
                "opportunities": [],
            }

        profile_data = profile_result.data.get("assessment_data", {})

        # Extract matching criteria
        interests = profile_data.get("academic_interests", [])
        grade = profile_data.get("grade", "")
        activities = profile_data.get("activities", [])

        opportunities = []

        # Fetch opportunities from database
        try:
            result = supabase_client.table("opportunities") \
                .select("*") \
                .in_("opportunity_type", opportunity_types) \
                .eq("is_active", True) \
                .limit(limit * 2) \
                .execute()

            for opp in result.data or []:
                # Simple relevance scoring
                relevance_score = 0

                opp_tags = opp.get("tags", [])
                for interest in interests:
                    if interest.lower() in [t.lower() for t in opp_tags]:
                        relevance_score += 20

                # Grade eligibility
                eligible_grades = opp.get("eligible_grades", [])
                if not eligible_grades or grade in eligible_grades:
                    relevance_score += 10

                if relevance_score > 0:
                    opportunities.append({
                        "id": opp.get("id"),
                        "name": opp.get("name", "Unknown"),
                        "type": opp.get("opportunity_type", "other"),
                        "description": opp.get("description", "")[:200],
                        "deadline": opp.get("deadline"),
                        "relevance_score": relevance_score,
                        "tags": opp_tags[:5],
                        "url": opp.get("url"),
                    })

            # Sort by relevance
            opportunities.sort(key=lambda x: x["relevance_score"], reverse=True)
            opportunities = opportunities[:limit]

        except Exception as e:
            logger.warning("fetch_opportunities_error", error=str(e))
            # Return empty list if opportunities table doesn't exist
            pass

        logger.info(
            "letta_match_opportunities",
            profile_id=profile_id,
            types=opportunity_types,
            matched=len(opportunities),
        )

        return {
            "success": True,
            "profile_id": profile_id,
            "opportunity_types": opportunity_types,
            "opportunities": opportunities,
            "count": len(opportunities),
        }

    except Exception as e:
        logger.error("letta_match_opportunities_error", profile_id=profile_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "opportunities": [],
        }


async def get_execution_state(
    profile_id: str,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Get the current execution state for a student.

    Calculates:
    - EDS (Execution Debt Score)
    - Task completion rate
    - Momentum indicators
    - Stall detection

    Args:
        profile_id: Student profile ID
        supabase_client: Supabase client

    Returns:
        Dictionary with execution state
    """
    try:
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        today = datetime.now()
        week_ago = today - timedelta(days=7)

        # Fetch task statistics
        total_tasks = 0
        completed_tasks = 0
        overdue_tasks = 0
        completed_this_week = 0

        try:
            # All active tasks
            result = supabase_client.table("tasks") \
                .select("status, due_date, completed_at") \
                .eq("profile_id", profile_id) \
                .execute()

            for task in result.data or []:
                total_tasks += 1

                if task.get("status") == "completed":
                    completed_tasks += 1
                    completed_at = task.get("completed_at")
                    if completed_at:
                        try:
                            completed_date = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                            if completed_date >= week_ago:
                                completed_this_week += 1
                        except Exception:
                            pass
                else:
                    due_date = task.get("due_date")
                    if due_date:
                        try:
                            due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                            if due < today:
                                overdue_tasks += 1
                        except Exception:
                            pass

        except Exception as e:
            logger.warning("fetch_task_stats_error", error=str(e))

        # Calculate EDS (Execution Debt Score)
        # Higher is worse - more execution debt
        eds_score = 0
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            eds_score = max(0, 100 - completion_rate) + (overdue_tasks * 10)
        else:
            completion_rate = 0

        # Determine status
        if eds_score >= 70:
            eds_status = "critical"
        elif eds_score >= 50:
            eds_status = "warning"
        elif eds_score >= 30:
            eds_status = "moderate"
        else:
            eds_status = "healthy"

        # Detect stalls (no completions in past week with pending tasks)
        is_stalled = completed_this_week == 0 and (total_tasks - completed_tasks) > 0

        # Momentum indicator
        if completed_this_week >= 5:
            momentum = "strong"
        elif completed_this_week >= 2:
            momentum = "moderate"
        elif completed_this_week >= 1:
            momentum = "low"
        else:
            momentum = "stalled"

        logger.info(
            "letta_execution_state",
            profile_id=profile_id,
            eds_score=eds_score,
            eds_status=eds_status,
            momentum=momentum,
        )

        return {
            "success": True,
            "profile_id": profile_id,
            "as_of": today.isoformat(),
            "execution_state": {
                "eds_score": round(eds_score, 1),
                "eds_status": eds_status,
                "momentum": momentum,
                "is_stalled": is_stalled,
            },
            "metrics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": total_tasks - completed_tasks,
                "overdue_tasks": overdue_tasks,
                "completed_this_week": completed_this_week,
                "completion_rate": round(completion_rate, 1),
            },
            "recommendations": _get_execution_recommendations(eds_status, is_stalled, overdue_tasks),
        }

    except Exception as e:
        logger.error("letta_execution_state_error", profile_id=profile_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "execution_state": {},
        }


def _get_execution_recommendations(
    eds_status: str,
    is_stalled: bool,
    overdue_tasks: int,
) -> List[str]:
    """Generate execution recommendations based on state."""
    recommendations = []

    if is_stalled:
        recommendations.append("Student appears stalled - consider gentle check-in")
        recommendations.append("Review blockers and offer to break down tasks")

    if eds_status == "critical":
        recommendations.append("CRITICAL: High execution debt - prioritize P0 tasks only")
        recommendations.append("Consider deadline extensions for non-critical items")

    elif eds_status == "warning":
        recommendations.append("Warning: Execution debt building - focus on quick wins")
        recommendations.append("Identify and remove blockers")

    if overdue_tasks > 0:
        recommendations.append(f"Address {overdue_tasks} overdue task(s) immediately")

    if not recommendations:
        recommendations.append("Execution is healthy - maintain momentum")

    return recommendations
