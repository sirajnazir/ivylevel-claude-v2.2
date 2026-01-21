"""
Letta Scheduler Jobs
====================

APScheduler jobs for Letta proactive monitoring.

These jobs extend the existing scheduler infrastructure at
agents/scheduler/execution_jobs.py.

Jobs:
- Deadline check (every 15 minutes) - Alert on approaching deadlines
- Opportunity match (hourly) - Find new opportunities for students
- Memory sync (every 5 minutes) - Keep Letta memory blocks fresh
"""

import structlog
from typing import Dict, Any, List
from datetime import datetime

from .config import is_letta_enabled, LETTA_CONFIG

logger = structlog.get_logger()


async def get_active_letta_profile_ids() -> List[str]:
    """Get profile IDs that have active Letta agents."""
    if not is_letta_enabled():
        return []

    try:
        from tools.database import get_supabase_client
        from .config import LETTA_TABLES

        supabase = get_supabase_client()

        result = supabase.table(LETTA_TABLES["agent_registry"]) \
            .select("profile_id") \
            .eq("is_active", True) \
            .execute()

        # Deduplicate profile IDs
        profile_ids = list(set(row["profile_id"] for row in result.data or []))

        return profile_ids

    except Exception as e:
        logger.error("get_letta_profile_ids_error", error=str(e))
        return []


async def job_letta_deadline_check() -> Dict[str, Any]:
    """
    Check for approaching deadlines for Letta-enabled students.

    Runs every 15 minutes.

    For each student with Letta agents:
    1. Check for deadlines in next 48 hours
    2. Check for overdue items
    3. Trigger proactive notifications if needed
    """
    if not is_letta_enabled():
        return {"skipped": True, "reason": "Letta disabled"}

    logger.info("letta_deadline_check_started")

    from .tools.monitoring import check_upcoming_deadlines
    from tools.database import get_supabase_client

    supabase = get_supabase_client()
    profile_ids = await get_active_letta_profile_ids()

    results = []
    alerts_sent = 0

    for profile_id in profile_ids:
        try:
            deadline_result = await check_upcoming_deadlines(
                profile_id=profile_id,
                days_ahead=2,  # Check 48 hours ahead
                include_overdue=True,
                supabase_client=supabase,
            )

            if deadline_result.get("success"):
                summary = deadline_result.get("summary", {})
                needs_attention = summary.get("needs_attention", False)

                if needs_attention:
                    # Create proactive notification
                    overdue = summary.get("total_overdue", 0)
                    urgent = summary.get("total_urgent", 0)

                    message = f"Deadline Alert: You have {overdue} overdue and {urgent} urgent items."

                    try:
                        supabase.table("proactive_notifications").insert({
                            "profile_id": profile_id,
                            "notification_type": "deadline_alert",
                            "message": message,
                            "metadata": {
                                "source": "letta_scheduler",
                                "overdue": overdue,
                                "urgent": urgent,
                            },
                            "created_at": datetime.now().isoformat(),
                        }).execute()

                        alerts_sent += 1
                    except Exception:
                        pass

                results.append({
                    "profile_id": profile_id,
                    "needs_attention": needs_attention,
                    "overdue": summary.get("total_overdue", 0),
                    "urgent": summary.get("total_urgent", 0),
                })

        except Exception as e:
            logger.error(
                "letta_deadline_check_profile_error",
                profile_id=profile_id,
                error=str(e),
            )
            results.append({
                "profile_id": profile_id,
                "error": str(e),
            })

    summary = {
        "job": "letta_deadline_check",
        "run_at": datetime.now().isoformat(),
        "total_profiles": len(profile_ids),
        "alerts_sent": alerts_sent,
    }

    logger.info("letta_deadline_check_completed", **summary)

    return summary


async def job_letta_opportunity_match() -> Dict[str, Any]:
    """
    Find new opportunities for Letta-enabled students.

    Runs every hour.

    For each student:
    1. Match against available opportunities
    2. Notify if new high-relevance matches found
    """
    if not is_letta_enabled():
        return {"skipped": True, "reason": "Letta disabled"}

    logger.info("letta_opportunity_match_started")

    from .tools.monitoring import match_opportunities
    from tools.database import get_supabase_client

    supabase = get_supabase_client()
    profile_ids = await get_active_letta_profile_ids()

    results = []
    matches_found = 0

    for profile_id in profile_ids:
        try:
            match_result = await match_opportunities(
                profile_id=profile_id,
                opportunity_types=["scholarship", "competition"],
                limit=5,
                supabase_client=supabase,
            )

            if match_result.get("success"):
                opportunities = match_result.get("opportunities", [])

                # Filter for high relevance (score > 30)
                high_relevance = [
                    o for o in opportunities
                    if o.get("relevance_score", 0) > 30
                ]

                if high_relevance:
                    matches_found += len(high_relevance)

                    # Create notification for top match
                    top_match = high_relevance[0]
                    message = f"New opportunity match: {top_match.get('name', 'Unknown')}"

                    try:
                        supabase.table("proactive_notifications").insert({
                            "profile_id": profile_id,
                            "notification_type": "opportunity_match",
                            "message": message,
                            "metadata": {
                                "source": "letta_scheduler",
                                "opportunity": top_match,
                                "total_matches": len(high_relevance),
                            },
                            "created_at": datetime.now().isoformat(),
                        }).execute()
                    except Exception:
                        pass

                results.append({
                    "profile_id": profile_id,
                    "matches": len(high_relevance),
                })

        except Exception as e:
            logger.error(
                "letta_opportunity_match_profile_error",
                profile_id=profile_id,
                error=str(e),
            )

    summary = {
        "job": "letta_opportunity_match",
        "run_at": datetime.now().isoformat(),
        "total_profiles": len(profile_ids),
        "total_matches": matches_found,
    }

    logger.info("letta_opportunity_match_completed", **summary)

    return summary


async def job_letta_memory_sync() -> Dict[str, Any]:
    """
    Sync memory blocks for Letta-enabled students.

    Runs every 5 minutes.

    Keeps Letta memory blocks fresh with latest Supabase data.
    """
    if not is_letta_enabled():
        return {"skipped": True, "reason": "Letta disabled"}

    logger.info("letta_memory_sync_started")

    from .memory import MemorySyncService
    from tools.database import get_supabase_client

    supabase = get_supabase_client()
    sync_service = MemorySyncService(supabase)

    profile_ids = await get_active_letta_profile_ids()

    synced = 0
    errors = 0

    for profile_id in profile_ids:
        try:
            # Build memory blocks
            blocks = await sync_service.build_memory_blocks(profile_id)

            # Save snapshot
            success = await sync_service.save_snapshot(profile_id, blocks)

            if success:
                synced += 1
            else:
                errors += 1

        except Exception as e:
            logger.error(
                "letta_memory_sync_profile_error",
                profile_id=profile_id,
                error=str(e),
            )
            errors += 1

    summary = {
        "job": "letta_memory_sync",
        "run_at": datetime.now().isoformat(),
        "total_profiles": len(profile_ids),
        "synced": synced,
        "errors": errors,
    }

    logger.info("letta_memory_sync_completed", **summary)

    return summary


def register_letta_jobs(scheduler) -> None:
    """
    Register Letta jobs with the APScheduler.

    This function extends the existing scheduler at
    agents/scheduler/execution_jobs.py.

    Args:
        scheduler: APScheduler AsyncIOScheduler instance
    """
    if not is_letta_enabled():
        logger.info("letta_jobs_skipped", reason="Letta disabled")
        return

    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger

    # Deadline check every 15 minutes
    scheduler.add_job(
        job_letta_deadline_check,
        IntervalTrigger(minutes=15),
        id="letta_deadline_check",
        name="Letta Deadline Check",
        replace_existing=True,
    )

    # Opportunity match every hour
    scheduler.add_job(
        job_letta_opportunity_match,
        CronTrigger(minute=30),  # At :30 past every hour
        id="letta_opportunity_match",
        name="Letta Opportunity Match",
        replace_existing=True,
    )

    # Memory sync every 5 minutes
    scheduler.add_job(
        job_letta_memory_sync,
        IntervalTrigger(minutes=5),
        id="letta_memory_sync",
        name="Letta Memory Sync",
        replace_existing=True,
    )

    logger.info("letta_jobs_registered", job_count=3)
