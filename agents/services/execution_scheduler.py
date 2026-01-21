"""
Execution Agent Scheduler - Proactive Nudging and Deadline Tracking
===================================================================

This module provides scheduled jobs for proactive student engagement:
- Deadline reminders (7, 3, 1 day thresholds)
- Stall detection (5+ days no activity)
- Student inactivity checks (3+ days no conversation)
- Weekly summary generation

The scheduler creates nudge entries in the nudge_queue table which
can be delivered to students via notifications or chat.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Threshold constants
DEADLINE_THRESHOLDS = [7, 3, 1]  # Days before deadline to nudge
STALL_THRESHOLD_NUDGE = 5        # Days before first stall nudge
STALL_THRESHOLD_MODERATE = 10    # Days before moderate stall warning
STALL_THRESHOLD_SEVERE = 14      # Days before severe stall/crisis escalation
INACTIVITY_THRESHOLD = 3         # Days of silence before check-in


async def daily_execution_check(supabase_client) -> Dict[str, Any]:
    """
    Daily check for all active students.

    Runs checks for:
    1. Deadline proximity (7, 3, 1 days)
    2. Stalled projects (5+ days no update)
    3. Student inactivity (3+ days no conversation)

    Creates nudge entries in nudge_queue table.

    Args:
        supabase_client: Supabase client instance

    Returns:
        Summary of checks performed and nudges created
    """
    results = {
        "profiles_checked": 0,
        "nudges_created": 0,
        "deadline_nudges": 0,
        "stall_nudges": 0,
        "inactivity_nudges": 0,
        "errors": []
    }

    try:
        # Get all profiles with active projects
        profiles_result = supabase_client.table("profiles").select(
            "id, first_name"
        ).execute()

        profiles = profiles_result.data or []
        logger.info(f"Daily execution check: Checking {len(profiles)} profiles")

        for profile in profiles:
            profile_id = profile["id"]
            nudges = []

            try:
                # Check 1: Deadline proximity
                deadline_nudges = await _check_deadlines(supabase_client, profile_id)
                nudges.extend(deadline_nudges)
                results["deadline_nudges"] += len(deadline_nudges)

                # Check 2: Stalled projects
                stall_nudges = await _check_stalled_projects(supabase_client, profile_id)
                nudges.extend(stall_nudges)
                results["stall_nudges"] += len(stall_nudges)

                # Check 3: Student inactivity
                inactivity_nudge = await _check_inactivity(supabase_client, profile_id)
                if inactivity_nudge:
                    nudges.append(inactivity_nudge)
                    results["inactivity_nudges"] += 1

                # Queue nudges (avoid duplicates)
                for nudge in nudges:
                    try:
                        # Check if similar nudge exists in last 24 hours
                        existing = supabase_client.table("nudge_queue").select("id").eq(
                            "profile_id", profile_id
                        ).eq("nudge_type", nudge["nudge_type"]).eq(
                            "status", "pending"
                        ).gte(
                            "created_at", (datetime.now() - timedelta(days=1)).isoformat()
                        ).execute()

                        if not existing.data:
                            supabase_client.table("nudge_queue").insert(nudge).execute()
                            results["nudges_created"] += 1
                        else:
                            logger.debug(f"Skipping duplicate nudge for {profile_id}: {nudge['nudge_type']}")

                    except Exception as e:
                        results["errors"].append(f"Failed to queue nudge for {profile_id}: {e}")

                results["profiles_checked"] += 1

            except Exception as e:
                logger.error(f"Error checking profile {profile_id}: {e}")
                results["errors"].append(f"Profile {profile_id}: {str(e)}")

    except Exception as e:
        logger.error(f"Daily execution check failed: {e}")
        results["errors"].append(str(e))

    logger.info(f"Daily check complete: {results}")
    return results


async def _check_deadlines(supabase_client, profile_id: str) -> List[Dict[str, Any]]:
    """
    Check for upcoming deadlines at 7, 3, 1 day thresholds.

    Returns list of nudge entries to create.
    """
    nudges = []

    try:
        # Get projects with upcoming deadlines
        # Note: projects table uses 'title' not 'name', 'target_end_date' not 'deadline'
        result = supabase_client.table("projects").select(
            "id, title, target_end_date, category"
        ).eq("profile_id", profile_id).eq("status", "active").not_.is_("target_end_date", "null").execute()

        now = datetime.now()

        for project in result.data or []:
            deadline_str = project.get("target_end_date")
            if not deadline_str:
                continue

            try:
                # Parse deadline
                if isinstance(deadline_str, str):
                    deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00").replace("+00:00", ""))
                else:
                    deadline = deadline_str

                days_until = (deadline.replace(tzinfo=None) - now).days

                # Check against thresholds
                if days_until in DEADLINE_THRESHOLDS:
                    priority = "high" if days_until == 1 else "medium" if days_until == 3 else "low"
                    nudges.append({
                        "profile_id": profile_id,
                        "nudge_type": "deadline_reminder",
                        "project_id": project["id"],
                        "priority": priority,
                        "message_draft": _generate_deadline_message(project["title"], days_until),
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                    })

            except Exception as e:
                logger.warning(f"Failed to parse deadline for project {project['id']}: {e}")

    except Exception as e:
        logger.error(f"Deadline check failed for {profile_id}: {e}")

    return nudges


async def _check_stalled_projects(
    supabase_client,
    profile_id: str,
    threshold_days: int = STALL_THRESHOLD_NUDGE
) -> List[Dict[str, Any]]:
    """
    Check for projects with no activity in threshold_days.

    Returns list of nudge entries to create.
    """
    nudges = []

    try:
        threshold = datetime.now() - timedelta(days=threshold_days)

        # Get all active projects
        # Note: projects table uses 'title' not 'name', 'updated_at' not 'last_update'
        result = supabase_client.table("projects").select(
            "id, title, updated_at, category, created_at"
        ).eq("profile_id", profile_id).eq("status", "active").execute()

        now = datetime.now()

        for project in result.data or []:
            # Use updated_at if available, else created_at
            last_activity_str = (
                project.get("updated_at") or
                project.get("created_at")
            )

            if not last_activity_str:
                continue

            try:
                if isinstance(last_activity_str, str):
                    last_activity = datetime.fromisoformat(
                        last_activity_str.replace("Z", "+00:00").replace("+00:00", "")
                    )
                else:
                    last_activity = last_activity_str

                days_stalled = (now - last_activity.replace(tzinfo=None)).days

                if days_stalled >= threshold_days:
                    # Determine severity and priority
                    if days_stalled >= STALL_THRESHOLD_SEVERE:
                        severity = "severe"
                        priority = "high"
                    elif days_stalled >= STALL_THRESHOLD_MODERATE:
                        severity = "moderate"
                        priority = "high"
                    else:
                        severity = "mild"
                        priority = "medium"

                    nudges.append({
                        "profile_id": profile_id,
                        "nudge_type": "stall_check",
                        "project_id": project["id"],
                        "priority": priority,
                        "message_draft": _generate_stall_message(project["title"], days_stalled, severity),
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                    })

            except Exception as e:
                logger.warning(f"Failed to check stall for project {project['id']}: {e}")

    except Exception as e:
        logger.error(f"Stall check failed for {profile_id}: {e}")

    return nudges


async def _check_inactivity(
    supabase_client,
    profile_id: str,
    threshold_days: int = INACTIVITY_THRESHOLD
) -> Optional[Dict[str, Any]]:
    """
    Check if student hasn't had any conversation in threshold_days.

    Returns a nudge entry or None.
    """
    try:
        threshold = datetime.now() - timedelta(days=threshold_days)

        result = supabase_client.table("conversations").select(
            "created_at"
        ).eq("profile_id", profile_id).order(
            "created_at", desc=True
        ).limit(1).execute()

        if not result.data:
            # No conversations at all - check profile creation date
            profile_result = supabase_client.table("profiles").select(
                "created_at"
            ).eq("id", profile_id).single().execute()

            if profile_result.data:
                created_at_str = profile_result.data.get("created_at")
                if created_at_str:
                    created_at = datetime.fromisoformat(
                        created_at_str.replace("Z", "+00:00").replace("+00:00", "")
                    )
                    days_since_creation = (datetime.now() - created_at.replace(tzinfo=None)).days

                    if days_since_creation >= threshold_days:
                        return {
                            "profile_id": profile_id,
                            "nudge_type": "check_in",
                            "project_id": None,
                            "priority": "low",
                            "message_draft": "Hey! Haven't heard from you yet. I'm here to help you succeed - what would you like to work on today?",
                            "status": "pending",
                            "created_at": datetime.now().isoformat(),
                        }
            return None

        last_convo_str = result.data[0]["created_at"]
        if isinstance(last_convo_str, str):
            last_convo = datetime.fromisoformat(
                last_convo_str.replace("Z", "+00:00").replace("+00:00", "")
            )
        else:
            last_convo = last_convo_str

        days_silent = (datetime.now() - last_convo.replace(tzinfo=None)).days

        if days_silent >= threshold_days:
            return {
                "profile_id": profile_id,
                "nudge_type": "check_in",
                "project_id": None,
                "priority": "low",
                "message_draft": f"Hey! It's been {days_silent} days since we last chatted. How's everything going? What can I help you with?",
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"Inactivity check failed for {profile_id}: {e}")

    return None


def _generate_deadline_message(project_name: str, days_until: int) -> str:
    """Generate appropriate deadline reminder message."""
    if days_until == 1:
        return f"Hey! {project_name} is due TOMORROW! How can I help you finish strong?"
    elif days_until == 3:
        return f"Quick heads up - {project_name} is due in 3 days. How's it coming along? Want to work on it together?"
    else:  # 7 days
        return f"Just a friendly reminder - {project_name} is due in a week. What's your plan to get it done?"


def _generate_stall_message(project_name: str, days_stalled: int, severity: str) -> str:
    """Generate appropriate stall check message."""
    if severity == "severe":
        return f"I noticed {project_name} hasn't had any updates in {days_stalled} days. What's blocking you? Let's figure this out together - even small progress counts!"
    elif severity == "moderate":
        return f"{project_name} has been quiet for {days_stalled} days. Everything okay? Want to break this down into smaller steps?"
    else:
        return f"Hey, just checking in on {project_name}. It's been about a week since the last update. What's your next step?"


async def get_pending_nudges_for_profile(supabase_client, profile_id: str) -> List[Dict[str, Any]]:
    """
    Get all pending nudges for a profile.

    Used at start of conversation to know what proactive topics to raise.

    Args:
        supabase_client: Supabase client instance
        profile_id: Profile UUID

    Returns:
        List of pending nudges, ordered by priority and creation time
    """
    try:
        result = supabase_client.table("nudge_queue").select(
            "id, nudge_type, project_id, priority, message_draft, created_at"
        ).eq("profile_id", profile_id).eq("status", "pending").order(
            "priority", desc=True
        ).order("created_at").execute()

        return result.data or []

    except Exception as e:
        logger.error(f"Failed to get pending nudges for {profile_id}: {e}")
        return []


async def mark_nudge_delivered(supabase_client, nudge_id: str) -> bool:
    """
    Mark a nudge as delivered after it's been sent to the student.

    Args:
        supabase_client: Supabase client instance
        nudge_id: Nudge UUID

    Returns:
        True if successful
    """
    try:
        supabase_client.table("nudge_queue").update({
            "status": "delivered",
            "delivered_at": datetime.now().isoformat(),
        }).eq("id", nudge_id).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to mark nudge {nudge_id} as delivered: {e}")
        return False


async def mark_nudge_dismissed(supabase_client, nudge_id: str) -> bool:
    """
    Mark a nudge as dismissed (user acknowledged but didn't act).

    Args:
        supabase_client: Supabase client instance
        nudge_id: Nudge UUID

    Returns:
        True if successful
    """
    try:
        supabase_client.table("nudge_queue").update({
            "status": "dismissed",
            "dismissed_at": datetime.now().isoformat(),
        }).eq("id", nudge_id).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to mark nudge {nudge_id} as dismissed: {e}")
        return False


def register_ec_scheduler_jobs(scheduler, supabase_client) -> None:
    """
    Register EC Agent scheduler jobs with APScheduler.

    Jobs registered:
    1. Daily execution check at 9 AM local
    2. Optional: Weekly summary on Sundays

    Args:
        scheduler: APScheduler AsyncIOScheduler instance
        supabase_client: Supabase client instance
    """
    from apscheduler.triggers.cron import CronTrigger

    # Wrap the function with supabase client
    async def daily_check_job():
        return await daily_execution_check(supabase_client)

    # Daily execution check at 9 AM
    scheduler.add_job(
        daily_check_job,
        CronTrigger(hour=9, minute=0),
        id="ec_daily_nudge_check",
        name="EC Agent Daily Nudge Check",
        replace_existing=True,
    )

    logger.info("Registered EC Agent scheduler jobs")
