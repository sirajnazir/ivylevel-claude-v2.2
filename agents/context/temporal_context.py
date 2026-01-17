"""
Pattern C6: Temporal Context Loader
v5.4 True Autonomous Agents

3P: Supabase for deadline storage
USP: Admissions calendar awareness
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from .types import (
    TemporalContext,
    Deadline,
    DeadlinePriority,
    DeadlineStatus,
    DeadlineCategory,
    AdmissionsPhase,
)

logger = logging.getLogger(__name__)


# Admissions calendar phases by month
ADMISSIONS_CALENDAR = {
    1: AdmissionsPhase.SUMMER_PROGRAMS,   # Jan: Summer program apps
    2: AdmissionsPhase.SUMMER_PROGRAMS,   # Feb: Summer program apps
    3: AdmissionsPhase.SUMMER_PROGRAMS,   # Mar: Summer program apps
    4: AdmissionsPhase.ACTIVITIES,        # Apr: Activity building
    5: AdmissionsPhase.ACTIVITIES,        # May: Activity building
    6: AdmissionsPhase.ESSAYS,            # Jun: Essay work begins
    7: AdmissionsPhase.ESSAYS,            # Jul: Essay drafts
    8: AdmissionsPhase.ESSAYS,            # Aug: Essay refinement
    9: AdmissionsPhase.ESSAYS,            # Sep: Final essay polish
    10: AdmissionsPhase.APPLICATIONS,     # Oct: EA/ED apps
    11: AdmissionsPhase.APPLICATIONS,     # Nov: ED deadlines
    12: AdmissionsPhase.APPLICATIONS,     # Dec: RD prep
}

# Standard ED deadline (Nov 1 or Nov 15)
STANDARD_ED_DEADLINE = (11, 1)  # November 1


class TemporalContextLoader:
    """
    Loads time-sensitive context for deadline awareness.

    Pattern C6: Temporal Context (3P: Supabase)

    This is critical because:
    - College admissions is highly time-sensitive
    - Missing deadlines = missing opportunities
    - Agents need to prioritize by urgency
    """

    def __init__(self, supabase_client):
        """
        Initialize with Supabase client.

        Args:
            supabase_client: Authenticated Supabase client
        """
        self.supabase = supabase_client

    async def load_context(self, profile_id: str) -> TemporalContext:
        """
        Load temporal context including deadlines and current phase.

        Args:
            profile_id: Student profile ID

        Returns:
            TemporalContext with deadlines and phase info
        """
        now = datetime.utcnow()
        current_phase = self._get_current_phase(now)

        # Load deadlines from database
        deadlines = await self._load_deadlines(profile_id, now)

        # Categorize deadlines
        imminent = [d for d in deadlines if d.days_until <= 7 and d.status != DeadlineStatus.COMPLETED]
        overdue = [d for d in deadlines if d.status == DeadlineStatus.OVERDUE]
        urgent_count = len([d for d in deadlines if d.priority in [DeadlinePriority.CRITICAL, DeadlinePriority.HIGH]])

        # Calculate days until ED
        days_until_ed = self._calculate_days_until_ed(now)

        return TemporalContext(
            profile_id=profile_id,
            current_phase=current_phase,
            current_date=now,
            deadlines=deadlines,
            imminent_deadlines=imminent,
            overdue_deadlines=overdue,
            urgent_count=urgent_count,
            total_deadlines=len(deadlines),
            days_until_ed=days_until_ed,
        )

    async def _load_deadlines(
        self,
        profile_id: str,
        now: datetime,
    ) -> List[Deadline]:
        """Load and process deadlines from database."""
        try:
            response = self.supabase.table("deadlines").select(
                "id, name, due_date, category, priority, status, related_task_id, notes"
            ).eq("profile_id", profile_id).gte(
                "due_date", (now - timedelta(days=30)).isoformat()  # Include recent past
            ).order("due_date").execute()

            deadlines = []
            for row in response.data or []:
                due_date = datetime.fromisoformat(row["due_date"].replace("Z", "+00:00"))
                days_until = (due_date.date() - now.date()).days

                # Determine status
                status = self._determine_status(row.get("status"), days_until)

                # Determine priority based on days remaining
                priority = self._determine_priority(
                    row.get("priority"),
                    days_until,
                    row.get("category"),
                )

                deadlines.append(Deadline(
                    id=row["id"],
                    name=row["name"],
                    due_date=due_date,
                    category=DeadlineCategory(row.get("category", "other")),
                    priority=priority,
                    status=status,
                    days_until=days_until,
                    related_task_id=row.get("related_task_id"),
                    notes=row.get("notes"),
                ))

            return deadlines

        except Exception as e:
            logger.error(f"Error loading deadlines for {profile_id}: {e}")
            return []

    def _get_current_phase(self, now: datetime) -> AdmissionsPhase:
        """Get current admissions phase based on month."""
        return ADMISSIONS_CALENDAR.get(now.month, AdmissionsPhase.ACTIVITIES)

    def _determine_status(
        self,
        stored_status: Optional[str],
        days_until: int,
    ) -> DeadlineStatus:
        """Determine deadline status based on time remaining."""
        if stored_status == "completed":
            return DeadlineStatus.COMPLETED

        if days_until < 0:
            return DeadlineStatus.OVERDUE
        elif days_until <= 3:
            return DeadlineStatus.IMMINENT
        else:
            return DeadlineStatus.UPCOMING

    def _determine_priority(
        self,
        stored_priority: Optional[str],
        days_until: int,
        category: Optional[str],
    ) -> DeadlinePriority:
        """
        Determine deadline priority.

        USP: Smart priority calculation based on:
        - Time remaining
        - Deadline category (applications are higher priority)
        - Stored priority (user override)
        """
        # If user set priority, respect it for non-imminent deadlines
        if stored_priority and days_until > 3:
            return DeadlinePriority(stored_priority)

        # Auto-escalate based on time
        if days_until <= 3:
            return DeadlinePriority.CRITICAL
        elif days_until <= 7:
            return DeadlinePriority.HIGH
        elif days_until <= 14:
            return DeadlinePriority.MEDIUM
        else:
            # Application deadlines are inherently higher priority
            if category in ["application", "essay", "recommendation"]:
                return DeadlinePriority.MEDIUM
            return DeadlinePriority.LOW

    def _calculate_days_until_ed(self, now: datetime) -> Optional[int]:
        """Calculate days until Early Decision deadline."""
        ed_month, ed_day = STANDARD_ED_DEADLINE

        # Build ED date for current or next cycle
        ed_year = now.year
        ed_date = datetime(ed_year, ed_month, ed_day)

        # If ED already passed this year, use next year
        if now > ed_date:
            ed_date = datetime(ed_year + 1, ed_month, ed_day)

        return (ed_date.date() - now.date()).days


def get_phase_recommendations(phase: AdmissionsPhase) -> Dict[str, Any]:
    """
    Get phase-specific recommendations.

    USP: Calendar-aware coaching guidance.
    """
    recommendations = {
        AdmissionsPhase.SUMMER_PROGRAMS: {
            "focus": "Summer program applications",
            "actions": [
                "Research selective summer programs",
                "Prepare application materials",
                "Request recommendations early",
            ],
            "avoid": "Starting college essays too early",
        },
        AdmissionsPhase.ACTIVITIES: {
            "focus": "Activity building and leadership",
            "actions": [
                "Take on leadership roles",
                "Start meaningful projects",
                "Document achievements",
            ],
            "avoid": "Overcommitting to too many activities",
        },
        AdmissionsPhase.ESSAYS: {
            "focus": "Personal statement and supplements",
            "actions": [
                "Brainstorm essay topics",
                "Write multiple drafts",
                "Get feedback from trusted readers",
            ],
            "avoid": "Generic topics, cliches",
        },
        AdmissionsPhase.APPLICATIONS: {
            "focus": "Application completion and submission",
            "actions": [
                "Finalize school list",
                "Complete Common App sections",
                "Submit before deadlines",
            ],
            "avoid": "Last-minute rushing, missing deadlines",
        },
        AdmissionsPhase.DECISIONS: {
            "focus": "Decision responses and next steps",
            "actions": [
                "Review financial aid offers",
                "Visit admitted student events",
                "Make final decision by May 1",
            ],
            "avoid": "Waiting until the last minute to decide",
        },
    }
    return recommendations.get(phase, {})


# Convenience function
async def load_temporal_context(
    supabase_client,
    profile_id: str,
) -> TemporalContext:
    """Quick helper to load temporal context."""
    loader = TemporalContextLoader(supabase_client)
    return await loader.load_context(profile_id)
