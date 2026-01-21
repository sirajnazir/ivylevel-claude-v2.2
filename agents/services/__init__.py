"""
Intelligence Services - High-level services for autonomous coaching.

Provides:
- AutonomousMonitorService: Main orchestration service for autonomous coaching
- sync_gameplan_to_projects: Sync game plan items to projects table
- ExecutionScheduler: Proactive nudging and deadline tracking
- EC Onboarding: First session setup when game plan is generated
"""

from .autonomous_monitor import AutonomousMonitorService
from .gameplan_sync import sync_gameplan_to_projects, get_synced_projects_count
from .execution_scheduler import (
    daily_execution_check,
    get_pending_nudges_for_profile,
    mark_nudge_delivered,
    mark_nudge_dismissed,
    register_ec_scheduler_jobs,
)
from .ec_onboarding import (
    trigger_ec_onboarding,
    check_and_trigger_onboarding,
    FIRST_SESSION_AGENDA,
)

__all__ = [
    "AutonomousMonitorService",
    "sync_gameplan_to_projects",
    "get_synced_projects_count",
    "daily_execution_check",
    "get_pending_nudges_for_profile",
    "mark_nudge_delivered",
    "mark_nudge_dismissed",
    "register_ec_scheduler_jobs",
    "trigger_ec_onboarding",
    "check_and_trigger_onboarding",
    "FIRST_SESSION_AGENDA",
]
