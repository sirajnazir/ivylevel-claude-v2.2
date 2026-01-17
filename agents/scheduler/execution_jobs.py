"""
APScheduler Jobs for Proactive Execution Management v5.3
========================================================

Jobs:
- Daily execution check (9 AM) - Detect stalls, send nudges
- Weekly plan generation (Sunday 6 PM) - Generate P0/P1/P2 plans
- EDS threshold check (every 6 hours) - Alert on critical EDS
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


async def get_active_profile_ids() -> List[str]:
    """Get all active student profile IDs."""
    try:
        from tools.database import get_supabase_client
        supabase = get_supabase_client()

        result = supabase.table("profiles") \
            .select("id") \
            .eq("is_active", True) \
            .execute()

        return [p["id"] for p in result.data or []]
    except Exception as e:
        logger.error("get_active_profiles_error", error=str(e))
        return []


async def job_daily_execution_check() -> Dict[str, Any]:
    """
    Daily execution check for all active students.
    Runs at 9 AM UTC.

    Uses the LangGraph execution workflow to:
    1. Assess execution state
    2. Detect stalls
    3. Send nudges or escalate crises
    4. Celebrate progress
    """
    logger.info("daily_execution_check_started")

    from graphs.execution_workflow import run_execution_workflow

    profile_ids = await get_active_profile_ids()
    results = []

    for profile_id in profile_ids:
        try:
            result = await run_execution_workflow(
                profile_id=profile_id,
                trigger="scheduled_daily",
            )
            results.append({
                "profile_id": profile_id,
                "success": True,
                "nudges": len(result.get("nudges_sent", [])),
                "crises": len(result.get("crises_created", [])),
                "celebrations": len(result.get("celebrations", [])),
            })
            logger.info(
                "execution_check_completed",
                profile_id=profile_id,
                nudges=len(result.get("nudges_sent", [])),
            )
        except Exception as e:
            logger.error(
                "execution_check_failed",
                profile_id=profile_id,
                error=str(e),
            )
            results.append({
                "profile_id": profile_id,
                "success": False,
                "error": str(e),
            })

    summary = {
        "job": "daily_execution_check",
        "run_at": datetime.now().isoformat(),
        "total_profiles": len(profile_ids),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "total_nudges": sum(r.get("nudges", 0) for r in results),
        "total_crises": sum(r.get("crises", 0) for r in results),
    }

    logger.info("daily_execution_check_completed", **summary)

    return summary


async def job_weekly_plan_generation() -> Dict[str, Any]:
    """
    Generate weekly plans for all active students.
    Runs Sunday at 6 PM UTC.
    """
    logger.info("weekly_plan_generation_started")

    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    profile_ids = await get_active_profile_ids()
    results = []

    for profile_id in profile_ids:
        try:
            result = await agent.tool_generate_weekly_plan(profile_id)
            results.append({
                "profile_id": profile_id,
                "success": result.get("success", False),
                "p0_count": len(result.get("plan", {}).get("p0_tasks", [])),
            })
            logger.info(
                "weekly_plan_generated",
                profile_id=profile_id,
            )
        except Exception as e:
            logger.error(
                "weekly_plan_generation_failed",
                profile_id=profile_id,
                error=str(e),
            )
            results.append({
                "profile_id": profile_id,
                "success": False,
                "error": str(e),
            })

    summary = {
        "job": "weekly_plan_generation",
        "run_at": datetime.now().isoformat(),
        "total_profiles": len(profile_ids),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
    }

    logger.info("weekly_plan_generation_completed", **summary)

    return summary


async def job_eds_threshold_check() -> Dict[str, Any]:
    """
    Check EDS thresholds and send alerts.
    Runs every 6 hours.
    """
    logger.info("eds_threshold_check_started")

    from agents.execution_chat import ExecutionChatAgent

    agent = ExecutionChatAgent()
    profile_ids = await get_active_profile_ids()
    alerts_sent = 0
    critical_count = 0

    for profile_id in profile_ids:
        try:
            eds = await agent.tool_calculate_eds(profile_id)

            if eds.get("status") == "critical":
                critical_count += 1
                await agent.tool_create_nudge(
                    profile_id=profile_id,
                    message=f"⚠️ EDS Alert: Your Execution Debt Score is {eds.get('eds_score', 0)}. Let's tackle this together!",
                    nudge_type="eds_threshold",
                    priority="high",
                )
                alerts_sent += 1
        except Exception as e:
            logger.error(
                "eds_check_failed",
                profile_id=profile_id,
                error=str(e),
            )

    summary = {
        "job": "eds_threshold_check",
        "run_at": datetime.now().isoformat(),
        "total_profiles": len(profile_ids),
        "critical_count": critical_count,
        "alerts_sent": alerts_sent,
    }

    logger.info("eds_threshold_check_completed", **summary)

    return summary


def register_execution_jobs(scheduler) -> None:
    """
    Register execution jobs with the scheduler.

    Args:
        scheduler: APScheduler AsyncIOScheduler instance
    """
    from apscheduler.triggers.cron import CronTrigger

    # Daily execution check at 9 AM UTC
    scheduler.add_job(
        job_daily_execution_check,
        CronTrigger(hour=9, minute=0),
        id="execution_daily_check",
        name="Daily Execution Check",
        replace_existing=True,
    )

    # Weekly plan generation Sunday 6 PM UTC
    scheduler.add_job(
        job_weekly_plan_generation,
        CronTrigger(day_of_week="sun", hour=18, minute=0),
        id="execution_weekly_plan",
        name="Weekly Plan Generation",
        replace_existing=True,
    )

    # EDS threshold check every 6 hours
    scheduler.add_job(
        job_eds_threshold_check,
        CronTrigger(hour="*/6", minute=0),
        id="execution_eds_check",
        name="EDS Threshold Check",
        replace_existing=True,
    )

    logger.info("execution_jobs_registered")
