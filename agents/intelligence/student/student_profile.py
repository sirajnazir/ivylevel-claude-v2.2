"""
StudentIntelligenceProfile - Psychobehavioral Profile for Adaptive Coaching

This wraps the student_psychobehavioral table and provides methods for
learning and adapting to student patterns over time.

Key patterns tracked:
- Response patterns (pressure, feedback, motivation, celebration)
- Work patterns (energy, task approach, overwhelm, pace)
- Communication patterns (style, check-in frequency)
- Risk patterns (tolerance, failure recovery)
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from enum import Enum


class PressureResponse(str, Enum):
    """How student responds to pressure."""
    THRIVES = "thrives"      # Performs better under pressure
    NEUTRAL = "neutral"      # No significant impact
    STRUGGLES = "struggles"  # Needs support under pressure


class FeedbackReception(str, Enum):
    """How student prefers to receive feedback."""
    DIRECT = "direct"        # Wants honest, direct feedback
    SANDWICH = "sandwich"    # Prefers positive-negative-positive
    GENTLE = "gentle"        # Needs encouraging framing
    DATA_DRIVEN = "data_driven"  # Responds to metrics and evidence


class MotivationStyle(str, Enum):
    """What motivates the student."""
    INTRINSIC = "intrinsic"  # Self-motivated, loves learning
    EXTRINSIC = "extrinsic"  # Motivated by rewards, recognition
    SOCIAL = "social"        # Motivated by peer/family expectations
    FEAR = "fear"            # Motivated by avoiding negative outcomes


class CelebrationPreference(str, Enum):
    """How student prefers to celebrate wins."""
    PRIVATE = "private"      # Quiet acknowledgment
    PUBLIC = "public"        # Loves recognition
    SHARED = "shared"        # Wants to celebrate with team/family
    MINIMAL = "minimal"      # Prefers to move on quickly


class EnergyPattern(str, Enum):
    """When student is most productive."""
    MORNING = "morning"      # Peak: 6am-12pm
    AFTERNOON = "afternoon"  # Peak: 12pm-6pm
    EVENING = "evening"      # Peak: 6pm-12am
    NIGHT_OWL = "night_owl"  # Peak: 12am-6am
    VARIABLE = "variable"    # Depends on day/mood


class TaskApproach(str, Enum):
    """How student approaches tasks."""
    SEQUENTIAL = "sequential"  # One thing at a time
    PARALLEL = "parallel"      # Multiple tasks simultaneously
    DEADLINE_DRIVEN = "deadline_driven"  # Procrastinates then sprints
    FRONT_LOADED = "front_loaded"  # Does hard stuff first


class CommunicationStyle(str, Enum):
    """Preferred communication style."""
    CONCISE = "concise"      # Short, to the point
    DETAILED = "detailed"    # Wants full context
    VISUAL = "visual"        # Prefers diagrams, charts
    CONVERSATIONAL = "conversational"  # Back-and-forth dialogue


class CheckInFrequency(str, Enum):
    """How often student wants check-ins."""
    DAILY = "daily"
    EVERY_OTHER_DAY = "every_other_day"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    AS_NEEDED = "as_needed"


class RiskTolerance(str, Enum):
    """Student's tolerance for risk."""
    HIGH = "high"            # Willing to take big swings
    BALANCED = "balanced"    # Calculated risks
    LOW = "low"              # Prefers safe choices
    VERY_LOW = "very_low"    # Risk-averse


class FailureRecovery(str, Enum):
    """How student recovers from failure."""
    QUICK = "quick"          # Bounces back fast
    MODERATE = "moderate"    # Needs some processing time
    SLOW = "slow"            # Needs significant support
    AVOIDANT = "avoidant"    # Tends to avoid trying again


class LearnedInteraction(BaseModel):
    """A learned pattern from an interaction."""
    pattern_type: str
    observation: str
    confidence: float = 0.5
    learned_at: datetime = Field(default_factory=datetime.utcnow)
    source_interaction_id: Optional[str] = None


class StudentIntelligenceProfile(BaseModel):
    """
    Psychobehavioral profile for a student.

    This profile learns and adapts over time based on interactions,
    enabling truly personalized coaching.
    """
    profile_id: UUID

    # Response Patterns
    pressure_response: PressureResponse = PressureResponse.THRIVES
    feedback_reception: FeedbackReception = FeedbackReception.DIRECT
    motivation_style: MotivationStyle = MotivationStyle.INTRINSIC
    celebration_preference: CelebrationPreference = CelebrationPreference.PRIVATE

    # Work Patterns
    energy_pattern: EnergyPattern = EnergyPattern.EVENING
    task_approach: TaskApproach = TaskApproach.SEQUENTIAL
    overwhelm_threshold: float = 0.7  # 0-1, where 1 = very high tolerance
    optimal_pace: float = 5.0  # Tasks per week

    # Communication
    communication_style: CommunicationStyle = CommunicationStyle.CONCISE
    check_in_frequency: CheckInFrequency = CheckInFrequency.WEEKLY

    # Risk
    risk_tolerance: RiskTolerance = RiskTolerance.BALANCED
    failure_recovery: FailureRecovery = FailureRecovery.QUICK

    # Learned patterns (accumulated over time)
    learned_from_interactions: Dict[str, LearnedInteraction] = Field(default_factory=dict)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    def learn_pattern(
        self,
        pattern_type: str,
        observation: str,
        confidence: float = 0.5,
        interaction_id: Optional[str] = None,
    ) -> None:
        """Learn a new pattern from an interaction."""
        key = f"{pattern_type}:{hash(observation) % 10000}"
        self.learned_from_interactions[key] = LearnedInteraction(
            pattern_type=pattern_type,
            observation=observation,
            confidence=confidence,
            source_interaction_id=interaction_id,
        )
        self.updated_at = datetime.utcnow()

    def get_learned_patterns(self, pattern_type: Optional[str] = None) -> List[LearnedInteraction]:
        """Get learned patterns, optionally filtered by type."""
        patterns = list(self.learned_from_interactions.values())
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        return sorted(patterns, key=lambda p: p.confidence, reverse=True)

    def get_coaching_adaptations(self) -> Dict[str, Any]:
        """Get adaptations to apply to coaching based on profile."""
        adaptations = {}

        # Feedback style adaptation
        if self.feedback_reception == FeedbackReception.SANDWICH:
            adaptations["feedback_format"] = "Start with strengths, then areas to improve, end with encouragement"
        elif self.feedback_reception == FeedbackReception.GENTLE:
            adaptations["feedback_format"] = "Use encouraging language, focus on growth potential"
        elif self.feedback_reception == FeedbackReception.DATA_DRIVEN:
            adaptations["feedback_format"] = "Lead with metrics and evidence"
        else:
            adaptations["feedback_format"] = "Be direct and honest"

        # Pressure adaptation
        if self.pressure_response == PressureResponse.STRUGGLES:
            adaptations["deadline_buffer"] = 1.5  # Add 50% more time
            adaptations["milestone_frequency"] = "high"  # More frequent check-ins
        elif self.pressure_response == PressureResponse.THRIVES:
            adaptations["deadline_buffer"] = 0.9  # Slightly tighter deadlines
            adaptations["milestone_frequency"] = "normal"

        # Communication adaptation
        if self.communication_style == CommunicationStyle.CONCISE:
            adaptations["message_length"] = "short"
            adaptations["bullet_points"] = True
        elif self.communication_style == CommunicationStyle.DETAILED:
            adaptations["message_length"] = "detailed"
            adaptations["include_rationale"] = True
        elif self.communication_style == CommunicationStyle.VISUAL:
            adaptations["include_visuals"] = True
            adaptations["use_tables"] = True

        # Task load adaptation
        adaptations["max_concurrent_tasks"] = int(self.optimal_pace * self.overwhelm_threshold)
        adaptations["check_in_frequency"] = self.check_in_frequency

        # Risk adaptation
        if self.risk_tolerance == RiskTolerance.LOW or self.risk_tolerance == RiskTolerance.VERY_LOW:
            adaptations["recommendation_style"] = "safe"
            adaptations["include_backup_options"] = True
        elif self.risk_tolerance == RiskTolerance.HIGH:
            adaptations["recommendation_style"] = "ambitious"
            adaptations["encourage_stretch_goals"] = True

        # Failure recovery adaptation
        if self.failure_recovery == FailureRecovery.SLOW or self.failure_recovery == FailureRecovery.AVOIDANT:
            adaptations["crisis_response"] = "supportive"
            adaptations["reframe_emphasis"] = "high"
        else:
            adaptations["crisis_response"] = "action_oriented"

        return adaptations

    def get_optimal_notification_time(self) -> str:
        """Get optimal time to send notifications based on energy pattern."""
        time_mapping = {
            EnergyPattern.MORNING: "08:00",
            EnergyPattern.AFTERNOON: "14:00",
            EnergyPattern.EVENING: "19:00",
            EnergyPattern.NIGHT_OWL: "22:00",
            EnergyPattern.VARIABLE: "10:00",  # Safe default
        }
        return time_mapping.get(self.energy_pattern, "10:00")

    def should_send_notification(self, urgency: str, last_contact_days: int) -> bool:
        """Determine if a notification should be sent based on preferences."""
        frequency_days = {
            CheckInFrequency.DAILY: 1,
            CheckInFrequency.EVERY_OTHER_DAY: 2,
            CheckInFrequency.WEEKLY: 7,
            CheckInFrequency.BIWEEKLY: 14,
            CheckInFrequency.AS_NEEDED: 30,  # Only urgent
        }

        threshold = frequency_days.get(self.check_in_frequency, 7)

        # Always send for urgent
        if urgency == "critical":
            return True

        # Check against preference
        return last_contact_days >= threshold

    def to_db_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            "profile_id": str(self.profile_id),
            "pressure_response": self.pressure_response,
            "feedback_reception": self.feedback_reception,
            "motivation_style": self.motivation_style,
            "celebration_preference": self.celebration_preference,
            "energy_pattern": self.energy_pattern,
            "task_approach": self.task_approach,
            "overwhelm_threshold": self.overwhelm_threshold,
            "optimal_pace": self.optimal_pace,
            "communication_style": self.communication_style,
            "check_in_frequency": self.check_in_frequency,
            "risk_tolerance": self.risk_tolerance,
            "failure_recovery": self.failure_recovery,
            "learned_from_interactions": {
                k: v.model_dump() for k, v in self.learned_from_interactions.items()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "StudentIntelligenceProfile":
        """Create from database row."""
        learned = {}
        if row.get("learned_from_interactions"):
            for k, v in row["learned_from_interactions"].items():
                learned[k] = LearnedInteraction(**v)

        return cls(
            profile_id=UUID(row["profile_id"]) if isinstance(row["profile_id"], str) else row["profile_id"],
            pressure_response=row.get("pressure_response", PressureResponse.THRIVES),
            feedback_reception=row.get("feedback_reception", FeedbackReception.DIRECT),
            motivation_style=row.get("motivation_style", MotivationStyle.INTRINSIC),
            celebration_preference=row.get("celebration_preference", CelebrationPreference.PRIVATE),
            energy_pattern=row.get("energy_pattern", EnergyPattern.EVENING),
            task_approach=row.get("task_approach", TaskApproach.SEQUENTIAL),
            overwhelm_threshold=row.get("overwhelm_threshold", 0.7),
            optimal_pace=row.get("optimal_pace", 5.0),
            communication_style=row.get("communication_style", CommunicationStyle.CONCISE),
            check_in_frequency=row.get("check_in_frequency", CheckInFrequency.WEEKLY),
            risk_tolerance=row.get("risk_tolerance", RiskTolerance.BALANCED),
            failure_recovery=row.get("failure_recovery", FailureRecovery.QUICK),
            learned_from_interactions=learned,
            created_at=row.get("created_at", datetime.utcnow()),
            updated_at=row.get("updated_at", datetime.utcnow()),
        )

    @classmethod
    def create_default(cls, profile_id: UUID) -> "StudentIntelligenceProfile":
        """Create a new profile with sensible defaults."""
        return cls(profile_id=profile_id)
