"""
Proactive Scheduler Registration v10.0
======================================

Registers proactive autonomy jobs with APScheduler.
All jobs respect feature flags and gracefully skip when disabled.

Jobs:
- opportunity_match: Hourly opportunity matching (default: disabled)
- deadline_alerts: Deadline proximity alerts every 6 hours (default: disabled)
- daily_stall_check: Daily stall detection at configured hour (default: disabled)

IMPORTANT: This module is ADDITIVE. It does not modify existing scheduler jobs.
"""

from typing import Optional
import structlog

from .config import PROACTIVE_CONFIG, is_proactive_enabled, is_feature_enabled
from .opportunity_matcher import job_opportunity_match

logger = structlog.get_logger()


def register_proactive_jobs(scheduler, supabase_client) -> bool:
    """
    Register proactive autonomy jobs with the scheduler.

    Args:
        scheduler: APScheduler AsyncIOScheduler instance
        supabase_client: Supabase client for database operations

    Returns:
        True if at least one job was registered
    """
    if not is_proactive_enabled():
        logger.info(
            "proactive_jobs_skipped",
            reason="PROACTIVE_ENABLED=false",
            config=PROACTIVE_CONFIG.to_dict(),
        )
        return False

    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger

    jobs_registered = 0

    # Job 1: Opportunity Matching (hourly)
    if is_feature_enabled("opportunity_match"):
        async def opportunity_match_job():
            return await job_opportunity_match(supabase_client)

        scheduler.add_job(
            opportunity_match_job,
            IntervalTrigger(hours=PROACTIVE_CONFIG.opportunity_match_interval_hours),
            id="proactive_opportunity_match",
            name="Proactive Opportunity Matcher",
            replace_existing=True,
        )
        jobs_registered += 1
        logger.info(
            "proactive_job_registered",
            job="opportunity_match",
            interval_hours=PROACTIVE_CONFIG.opportunity_match_interval_hours,
        )

    # Job 2: Deadline Alerts (every N hours)
    if is_feature_enabled("deadline_alerts"):
        async def deadline_alerts_job():
            return await _job_deadline_alerts(supabase_client)

        scheduler.add_job(
            deadline_alerts_job,
            IntervalTrigger(hours=PROACTIVE_CONFIG.deadline_check_interval_hours),
            id="proactive_deadline_alerts",
            name="Proactive Deadline Alerts",
            replace_existing=True,
        )
        jobs_registered += 1
        logger.info(
            "proactive_job_registered",
            job="deadline_alerts",
            interval_hours=PROACTIVE_CONFIG.deadline_check_interval_hours,
        )

    # Job 3: Daily Stall Detection
    if is_feature_enabled("stall_detection"):
        async def stall_detection_job():
            return await _job_stall_detection(supabase_client)

        scheduler.add_job(
            stall_detection_job,
            CronTrigger(hour=PROACTIVE_CONFIG.stall_check_daily_hour, minute=0),
            id="proactive_stall_detection",
            name="Proactive Stall Detection",
            replace_existing=True,
        )
        jobs_registered += 1
        logger.info(
            "proactive_job_registered",
            job="stall_detection",
            daily_hour=PROACTIVE_CONFIG.stall_check_daily_hour,
        )

    # Job 4: Inactivity Check-ins (daily at noon)
    if is_feature_enabled("inactivity_check"):
        async def inactivity_check_job():
            return await _job_inactivity_check(supabase_client)

        scheduler.add_job(
            inactivity_check_job,
            CronTrigger(hour=12, minute=0),
            id="proactive_inactivity_check",
            name="Proactive Inactivity Check",
            replace_existing=True,
        )
        jobs_registered += 1
        logger.info(
            "proactive_job_registered",
            job="inactivity_check",
            daily_hour=12,
        )

    logger.info(
        "proactive_jobs_registration_complete",
        jobs_registered=jobs_registered,
        config=PROACTIVE_CONFIG.to_dict(),
    )

    return jobs_registered > 0


async def _job_deadline_alerts(supabase_client) -> dict:
    """
    Check for approaching deadlines and create alerts.

    Uses existing execution_scheduler functions for deadline checking.
    """
    if not is_feature_enabled("deadline_alerts"):
        return {"skipped": True, "reason": "Feature disabled"}

    logger.info("proactive_deadline_alerts_started")

    try:
        # Import the existing deadline check function
        from services.execution_scheduler import _check_deadlines

        # Get active profiles
        profiles_result = supabase_client.table("profiles").select(
            "id"
        ).eq("is_active", True).execute()

        profiles = profiles_result.data or []
        total_nudges = 0

        for profile in profiles:
            profile_id = profile["id"]
            nudges = await _check_deadlines(supabase_client, profile_id)

            for nudge in nudges:
                # Check for duplicates
                existing = supabase_client.table("nudge_queue").select("id").eq(
                    "profile_id", profile_id
                ).eq("nudge_type", nudge["nudge_type"]).eq(
                    "status", "pending"
                ).execute()

                if not existing.data:
                    supabase_client.table("nudge_queue").insert(nudge).execute()
                    total_nudges += 1

        logger.info(
            "proactive_deadline_alerts_completed",
            profiles_checked=len(profiles),
            nudges_created=total_nudges,
        )

        return {
            "profiles_checked": len(profiles),
            "nudges_created": total_nudges,
        }

    except Exception as e:
        logger.error("proactive_deadline_alerts_error", error=str(e))
        return {"error": str(e)}


async def _job_stall_detection(supabase_client) -> dict:
    """
    Detect stalled projects and create nudges.

    Uses existing execution_scheduler functions for stall detection.
    """
    if not is_feature_enabled("stall_detection"):
        return {"skipped": True, "reason": "Feature disabled"}

    logger.info("proactive_stall_detection_started")

    try:
        # Import the existing stall check function
        from services.execution_scheduler import _check_stalled_projects

        # Get active profiles
        profiles_result = supabase_client.table("profiles").select(
            "id"
        ).eq("is_active", True).execute()

        profiles = profiles_result.data or []
        total_nudges = 0

        for profile in profiles:
            profile_id = profile["id"]
            nudges = await _check_stalled_projects(supabase_client, profile_id)

            for nudge in nudges:
                # Check for duplicates
                existing = supabase_client.table("nudge_queue").select("id").eq(
                    "profile_id", profile_id
                ).eq("nudge_type", nudge["nudge_type"]).eq(
                    "project_id", nudge.get("project_id")
                ).eq("status", "pending").execute()

                if not existing.data:
                    supabase_client.table("nudge_queue").insert(nudge).execute()
                    total_nudges += 1

        logger.info(
            "proactive_stall_detection_completed",
            profiles_checked=len(profiles),
            nudges_created=total_nudges,
        )

        return {
            "profiles_checked": len(profiles),
            "nudges_created": total_nudges,
        }

    except Exception as e:
        logger.error("proactive_stall_detection_error", error=str(e))
        return {"error": str(e)}


async def _job_inactivity_check(supabase_client) -> dict:
    """
    Check for inactive students and create check-in nudges.

    Uses existing execution_scheduler functions for inactivity detection.
    """
    if not is_feature_enabled("inactivity_check"):
        return {"skipped": True, "reason": "Feature disabled"}

    logger.info("proactive_inactivity_check_started")

    try:
        # Import the existing inactivity check function
        from services.execution_scheduler import _check_inactivity

        # Get active profiles
        profiles_result = supabase_client.table("profiles").select(
            "id"
        ).eq("is_active", True).execute()

        profiles = profiles_result.data or []
        total_nudges = 0

        for profile in profiles:
            profile_id = profile["id"]
            nudge = await _check_inactivity(supabase_client, profile_id)

            if nudge:
                # Check for duplicates
                existing = supabase_client.table("nudge_queue").select("id").eq(
                    "profile_id", profile_id
                ).eq("nudge_type", "check_in").eq(
                    "status", "pending"
                ).execute()

                if not existing.data:
                    supabase_client.table("nudge_queue").insert(nudge).execute()
                    total_nudges += 1

        logger.info(
            "proactive_inactivity_check_completed",
            profiles_checked=len(profiles),
            nudges_created=total_nudges,
        )

        return {
            "profiles_checked": len(profiles),
            "nudges_created": total_nudges,
        }

    except Exception as e:
        logger.error("proactive_inactivity_check_error", error=str(e))
        return {"error": str(e)}
