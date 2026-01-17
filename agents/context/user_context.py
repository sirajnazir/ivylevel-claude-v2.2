"""
Pattern C2: User Context Loader
v5.4 True Autonomous Agents

3P: Supabase for storage
USP: Custom context selection based on task type
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from .types import (
    StudentContext,
    ContextSelection,
    CommunicationStyle,
    MotivationType,
)

logger = logging.getLogger(__name__)


class UserContextLoader:
    """
    Loads and manages user context for personalized coaching.

    Pattern C2: User Context (3P: Supabase + Custom Selection)

    This is a critical pattern because:
    - Every agent needs to know WHO they're helping
    - Personalization is our USP (unique selling proposition)
    - Without context, agents give generic advice
    """

    def __init__(self, supabase_client):
        """
        Initialize with Supabase client.

        Args:
            supabase_client: Authenticated Supabase client
        """
        self.supabase = supabase_client
        self._cache: Dict[str, StudentContext] = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_timestamps: Dict[str, datetime] = {}

    async def load_context(
        self,
        profile_id: str,
        selection: Optional[ContextSelection] = None,
    ) -> StudentContext:
        """
        Load complete student context from Supabase.

        Args:
            profile_id: Student profile ID
            selection: What context to include (defaults to all)

        Returns:
            StudentContext with all relevant data
        """
        if selection is None:
            selection = ContextSelection()

        # Check cache first
        if self._is_cache_valid(profile_id):
            logger.debug(f"Using cached context for {profile_id}")
            return self._apply_selection(self._cache[profile_id], selection)

        # Load from Supabase
        context = await self._load_from_db(profile_id)

        # Cache it
        self._cache[profile_id] = context
        self._cache_timestamps[profile_id] = datetime.utcnow()

        # Apply selection filter
        return self._apply_selection(context, selection)

    async def _load_from_db(self, profile_id: str) -> StudentContext:
        """Load student context from Supabase."""
        try:
            # Load profile data
            profile_response = self.supabase.table("profiles").select(
                "id, name, grade, gpa, target_schools, intended_major, constraints"
            ).eq("id", profile_id).single().execute()

            profile_data = profile_response.data or {}

            # Load identity synthesis (from EC Agent results)
            identity_response = self.supabase.table("identity_synthesis").select(
                "archetype, archetype_confidence, spike, pillars, narrative_dna"
            ).eq("profile_id", profile_id).order(
                "created_at", desc=True
            ).limit(1).execute()

            identity_data = (identity_response.data or [{}])[0] if identity_response.data else {}

            # Load activities
            activities_response = self.supabase.table("activities").select(
                "id, name, category, hours_per_week, leadership_level, impact_score"
            ).eq("profile_id", profile_id).execute()

            activities = activities_response.data or []

            # Load user preferences (USP - coaching style)
            preferences_response = self.supabase.table("user_preferences").select(
                "communication_style, motivation_type, stress_indicators"
            ).eq("profile_id", profile_id).single().execute()

            preferences = preferences_response.data or {}

            # Build context
            return StudentContext(
                profile_id=profile_id,
                name=profile_data.get("name", ""),
                grade=profile_data.get("grade", 11),

                # Identity synthesis
                archetype=identity_data.get("archetype"),
                archetype_confidence=identity_data.get("archetype_confidence"),
                spike=identity_data.get("spike"),
                pillars=identity_data.get("pillars"),
                narrative_dna=identity_data.get("narrative_dna"),

                # Preferences (USP)
                communication_style=CommunicationStyle(
                    preferences.get("communication_style", "balanced")
                ),
                motivation_type=MotivationType(
                    preferences.get("motivation_type", "achievement")
                ),
                stress_indicators=preferences.get("stress_indicators", []),

                # Academic
                gpa=profile_data.get("gpa"),
                target_schools=profile_data.get("target_schools", []),
                intended_major=profile_data.get("intended_major"),

                # Activities
                activities=activities,
                activity_count=len(activities),

                # Constraints
                constraints=profile_data.get("constraints", {}),
            )

        except Exception as e:
            logger.error(f"Error loading context for {profile_id}: {e}")
            # Return minimal context on error
            return StudentContext(profile_id=profile_id)

    def _is_cache_valid(self, profile_id: str) -> bool:
        """Check if cached context is still valid."""
        if profile_id not in self._cache:
            return False

        if profile_id not in self._cache_timestamps:
            return False

        age = (datetime.utcnow() - self._cache_timestamps[profile_id]).total_seconds()
        return age < self._cache_ttl

    def _apply_selection(
        self,
        context: StudentContext,
        selection: ContextSelection,
    ) -> StudentContext:
        """
        Apply context selection filter.

        USP: Smart context selection - agents only get what they need.
        """
        # Create a copy to avoid mutating cached version
        filtered = context.model_copy()

        if not selection.include_activities:
            filtered.activities = []
            filtered.activity_count = 0

        if not selection.include_academics:
            filtered.gpa = None
            filtered.target_schools = []
            filtered.intended_major = None

        if not selection.include_constraints:
            filtered.constraints = {}

        return filtered

    def invalidate_cache(self, profile_id: str) -> None:
        """Invalidate cached context for a profile."""
        self._cache.pop(profile_id, None)
        self._cache_timestamps.pop(profile_id, None)

    def clear_cache(self) -> None:
        """Clear all cached contexts."""
        self._cache.clear()
        self._cache_timestamps.clear()


# Convenience function for quick context loading
async def load_student_context(
    supabase_client,
    profile_id: str,
    selection: Optional[ContextSelection] = None,
) -> StudentContext:
    """
    Quick helper to load student context.

    Usage:
        context = await load_student_context(supabase, profile_id)
    """
    loader = UserContextLoader(supabase_client)
    return await loader.load_context(profile_id, selection)
