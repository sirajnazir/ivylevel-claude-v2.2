"""
StudentIntelligenceManager - Manages psychobehavioral profiles for students.

Provides:
- CRUD operations for student intelligence profiles
- Pattern learning from interactions
- Adaptation recommendations
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
import logging
from datetime import datetime

from ..student import StudentIntelligenceProfile, LearnedInteraction

logger = logging.getLogger(__name__)


class StudentIntelligenceManager:
    """
    Manages student psychobehavioral profiles in the database.

    This manager handles:
    - Profile creation and retrieval
    - Learning patterns from interactions
    - Providing coaching adaptations
    """

    def __init__(self, supabase_client):
        """
        Initialize the manager with a Supabase client.

        Args:
            supabase_client: Initialized Supabase client
        """
        self.db = supabase_client
        self.table = "student_psychobehavioral"

    async def get_or_create(self, profile_id: UUID) -> StudentIntelligenceProfile:
        """
        Get existing profile or create a new one with defaults.

        Args:
            profile_id: The student's profile ID

        Returns:
            StudentIntelligenceProfile instance
        """
        existing = await self.get(profile_id)
        if existing:
            return existing

        # Create new profile with defaults
        new_profile = StudentIntelligenceProfile.create_default(profile_id)
        await self.create(new_profile)
        return new_profile

    async def get(self, profile_id: UUID) -> Optional[StudentIntelligenceProfile]:
        """Get a student intelligence profile by ID."""
        try:
            result = self.db.table(self.table).select("*").eq("profile_id", str(profile_id)).single().execute()

            if result.data:
                return StudentIntelligenceProfile.from_db_row(result.data)
            return None

        except Exception as e:
            logger.warning(f"Failed to get student profile {profile_id}: {e}")
            return None

    async def create(self, profile: StudentIntelligenceProfile) -> StudentIntelligenceProfile:
        """Create a new student intelligence profile."""
        try:
            data = profile.to_db_dict()
            result = self.db.table(self.table).insert(data).execute()

            if result.data:
                logger.info(f"Created student intelligence profile: {profile.profile_id}")
                return StudentIntelligenceProfile.from_db_row(result.data[0])
            else:
                raise Exception("Failed to create profile - no data returned")

        except Exception as e:
            logger.error(f"Failed to create student profile: {e}")
            raise

    async def update(self, profile: StudentIntelligenceProfile) -> StudentIntelligenceProfile:
        """Update an existing student intelligence profile."""
        try:
            profile.updated_at = datetime.utcnow()
            data = profile.to_db_dict()

            result = self.db.table(self.table).update(data).eq("profile_id", str(profile.profile_id)).execute()

            if result.data:
                logger.info(f"Updated student intelligence profile: {profile.profile_id}")
                return StudentIntelligenceProfile.from_db_row(result.data[0])
            else:
                raise Exception("Failed to update profile - no data returned")

        except Exception as e:
            logger.error(f"Failed to update student profile: {e}")
            raise

    async def learn_from_interaction(
        self,
        profile_id: UUID,
        pattern_type: str,
        observation: str,
        confidence: float = 0.5,
        interaction_id: Optional[str] = None,
    ) -> bool:
        """
        Learn a pattern from an interaction and update the profile.

        Args:
            profile_id: The student's profile ID
            pattern_type: Type of pattern (e.g., "response_to_deadline", "feedback_reaction")
            observation: What was observed
            confidence: Confidence in this observation (0-1)
            interaction_id: Optional ID of the source interaction

        Returns:
            True if successful
        """
        try:
            profile = await self.get_or_create(profile_id)
            profile.learn_pattern(pattern_type, observation, confidence, interaction_id)
            await self.update(profile)

            logger.info(f"Learned pattern '{pattern_type}' for profile {profile_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to learn pattern: {e}")
            return False

    async def update_trait(
        self,
        profile_id: UUID,
        trait_name: str,
        trait_value: Any,
    ) -> bool:
        """
        Update a specific trait in the profile.

        Args:
            profile_id: The student's profile ID
            trait_name: Name of the trait to update
            trait_value: New value for the trait

        Returns:
            True if successful
        """
        try:
            profile = await self.get_or_create(profile_id)

            if hasattr(profile, trait_name):
                setattr(profile, trait_name, trait_value)
                await self.update(profile)
                logger.info(f"Updated trait '{trait_name}' for profile {profile_id}")
                return True
            else:
                logger.warning(f"Unknown trait: {trait_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to update trait: {e}")
            return False

    async def get_coaching_adaptations(
        self,
        profile_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get coaching adaptations for a student.

        Args:
            profile_id: The student's profile ID

        Returns:
            Dictionary of adaptations to apply to coaching
        """
        profile = await self.get_or_create(profile_id)
        return profile.get_coaching_adaptations()

    async def get_optimal_notification_time(
        self,
        profile_id: UUID,
    ) -> str:
        """Get the optimal time to send notifications to a student."""
        profile = await self.get_or_create(profile_id)
        return profile.get_optimal_notification_time()

    async def should_send_notification(
        self,
        profile_id: UUID,
        urgency: str,
        last_contact_days: int,
    ) -> bool:
        """Determine if a notification should be sent."""
        profile = await self.get_or_create(profile_id)
        return profile.should_send_notification(urgency, last_contact_days)

    async def get_learned_patterns(
        self,
        profile_id: UUID,
        pattern_type: Optional[str] = None,
    ) -> List[LearnedInteraction]:
        """Get learned patterns for a student."""
        profile = await self.get(profile_id)
        if not profile:
            return []
        return profile.get_learned_patterns(pattern_type)

    async def infer_archetype(
        self,
        profile_id: UUID,
    ) -> str:
        """
        Infer the student's archetype based on their profile.

        Archetypes:
        - achiever: High performer, thrives under pressure
        - scholar: Intrinsically motivated learner
        - collaborator: Socially motivated, team-oriented
        - sprinter: Deadline-driven, quick recoverer
        - perfectionist: Risk-averse, needs support
        - balanced: Well-rounded across traits
        """
        profile = await self.get_or_create(profile_id)

        # Simple archetype inference based on key traits
        if profile.pressure_response == "thrives" and profile.risk_tolerance == "high":
            return "achiever"
        elif profile.motivation_style == "intrinsic" and profile.feedback_reception == "direct":
            return "scholar"
        elif profile.motivation_style == "social" and profile.celebration_preference == "shared":
            return "collaborator"
        elif profile.task_approach == "deadline_driven" and profile.failure_recovery == "quick":
            return "sprinter"
        elif profile.risk_tolerance in ["low", "very_low"] and profile.failure_recovery == "slow":
            return "perfectionist"
        else:
            return "balanced"

    async def get_profile_summary(
        self,
        profile_id: UUID,
    ) -> Dict[str, Any]:
        """Get a summary of the student's intelligence profile."""
        profile = await self.get_or_create(profile_id)
        archetype = await self.infer_archetype(profile_id)
        adaptations = profile.get_coaching_adaptations()

        return {
            "profile_id": str(profile_id),
            "archetype": archetype,
            "key_traits": {
                "pressure_response": profile.pressure_response,
                "motivation_style": profile.motivation_style,
                "communication_style": profile.communication_style,
                "risk_tolerance": profile.risk_tolerance,
            },
            "work_patterns": {
                "energy_pattern": profile.energy_pattern,
                "task_approach": profile.task_approach,
                "optimal_pace": profile.optimal_pace,
                "overwhelm_threshold": profile.overwhelm_threshold,
            },
            "adaptations": adaptations,
            "learned_patterns_count": len(profile.learned_from_interactions),
            "optimal_notification_time": profile.get_optimal_notification_time(),
        }

    async def batch_update_from_feedback(
        self,
        profile_id: UUID,
        feedback_data: List[Dict[str, Any]],
    ) -> int:
        """
        Update profile based on multiple feedback items.

        Args:
            profile_id: The student's profile ID
            feedback_data: List of feedback dictionaries with 'type' and 'observation'

        Returns:
            Number of patterns learned
        """
        learned_count = 0

        for feedback in feedback_data:
            success = await self.learn_from_interaction(
                profile_id=profile_id,
                pattern_type=feedback.get("type", "feedback"),
                observation=feedback.get("observation", ""),
                confidence=feedback.get("confidence", 0.5),
                interaction_id=feedback.get("interaction_id"),
            )
            if success:
                learned_count += 1

        return learned_count
