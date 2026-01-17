"""
Pattern G3: Escalation Protocol
v5.4 True Autonomous Agents

3P: Pydantic for validation
USP: Safe escalation for minors' sensitive situations
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class EscalationLevel(str, Enum):
    """Levels of escalation."""
    NONE = "none"                # No escalation needed
    SUPERVISOR = "supervisor"    # Escalate to supervisor agent
    HUMAN_ASYNC = "human_async"  # Human review (non-urgent)
    HUMAN_SYNC = "human_sync"    # Human review (needs response)
    EMERGENCY = "emergency"      # Immediate human intervention


class EscalationReason(str, Enum):
    """Reasons for escalation."""
    LOW_CONFIDENCE = "low_confidence"
    STUDENT_DISTRESS = "student_distress"
    SAFETY_CONCERN = "safety_concern"
    DEADLINE_CRITICAL = "deadline_critical"
    CONFLICTING_INFO = "conflicting_info"
    OUT_OF_SCOPE = "out_of_scope"
    TECHNICAL_ERROR = "technical_error"
    PARENT_REQUEST = "parent_request"
    QUALITY_FAILURE = "quality_failure"


class Escalation(BaseModel):
    """An escalation request."""
    id: str
    level: EscalationLevel
    reason: EscalationReason
    agent_name: str
    profile_id: str
    description: str
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution: Optional[str] = None


# Escalation triggers (USP: sensitive to minors' needs)
ESCALATION_TRIGGERS = {
    # Distress keywords that require escalation
    "distress_keywords": [
        "want to die", "kill myself", "self-harm", "suicide",
        "can't go on", "end it all", "hurt myself",
        "depressed", "hopeless", "worthless",
    ],
    # Safety keywords
    "safety_keywords": [
        "abuse", "abused", "hitting me", "hurting me",
        "unsafe", "danger", "threatened",
    ],
    # Out of scope topics
    "out_of_scope_keywords": [
        "medical advice", "legal advice", "therapy",
        "medication", "diagnosis",
    ],
}

# Escalation level by reason
REASON_TO_LEVEL: Dict[EscalationReason, EscalationLevel] = {
    EscalationReason.LOW_CONFIDENCE: EscalationLevel.SUPERVISOR,
    EscalationReason.STUDENT_DISTRESS: EscalationLevel.HUMAN_SYNC,
    EscalationReason.SAFETY_CONCERN: EscalationLevel.EMERGENCY,
    EscalationReason.DEADLINE_CRITICAL: EscalationLevel.HUMAN_ASYNC,
    EscalationReason.CONFLICTING_INFO: EscalationLevel.SUPERVISOR,
    EscalationReason.OUT_OF_SCOPE: EscalationLevel.HUMAN_ASYNC,
    EscalationReason.TECHNICAL_ERROR: EscalationLevel.SUPERVISOR,
    EscalationReason.PARENT_REQUEST: EscalationLevel.HUMAN_ASYNC,
    EscalationReason.QUALITY_FAILURE: EscalationLevel.SUPERVISOR,
}


class EscalationProtocol:
    """
    Manages escalation for sensitive situations.

    Pattern G3: Escalation Protocol (3P: Pydantic)

    Critical for minors because:
    - Students may share concerning information
    - Safety must always be prioritized
    - Some situations require adult judgment
    - We have duty of care
    """

    def __init__(
        self,
        triggers: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize escalation protocol.

        Args:
            triggers: Custom escalation triggers
        """
        self.triggers = triggers or ESCALATION_TRIGGERS
        self._escalations: Dict[str, Escalation] = {}
        self._handlers: Dict[EscalationLevel, List[Callable[[Escalation], None]]] = {
            level: [] for level in EscalationLevel
        }

    def check_for_escalation(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> Optional[tuple[EscalationReason, EscalationLevel]]:
        """
        Check if a message requires escalation.

        Args:
            message: Student's message
            context: Additional context

        Returns:
            Tuple of (reason, level) if escalation needed, None otherwise
        """
        message_lower = message.lower()

        # Check for safety concerns (HIGHEST PRIORITY)
        for keyword in self.triggers.get("safety_keywords", []):
            if keyword in message_lower:
                logger.warning(f"Safety keyword detected: {keyword}")
                return (EscalationReason.SAFETY_CONCERN, EscalationLevel.EMERGENCY)

        # Check for distress signals
        for keyword in self.triggers.get("distress_keywords", []):
            if keyword in message_lower:
                logger.warning(f"Distress keyword detected: {keyword}")
                return (EscalationReason.STUDENT_DISTRESS, EscalationLevel.HUMAN_SYNC)

        # Check for out of scope
        for keyword in self.triggers.get("out_of_scope_keywords", []):
            if keyword in message_lower:
                logger.info(f"Out of scope topic detected: {keyword}")
                return (EscalationReason.OUT_OF_SCOPE, EscalationLevel.HUMAN_ASYNC)

        # Check context factors
        if context.get("detected_sentiment") == "stressed":
            stress_level = context.get("stress_level", 0)
            if stress_level > 0.8:
                return (EscalationReason.STUDENT_DISTRESS, EscalationLevel.HUMAN_SYNC)

        # Check for low confidence
        if context.get("confidence", 1.0) < 0.5:
            return (EscalationReason.LOW_CONFIDENCE, EscalationLevel.SUPERVISOR)

        # Check for critical deadline
        if context.get("is_critical_deadline", False):
            return (EscalationReason.DEADLINE_CRITICAL, EscalationLevel.HUMAN_ASYNC)

        return None

    def escalate(
        self,
        agent_name: str,
        profile_id: str,
        reason: EscalationReason,
        description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Escalation:
        """
        Create and process an escalation.

        Args:
            agent_name: Agent initiating escalation
            profile_id: Student's profile ID
            reason: Why escalating
            description: What happened
            context: Additional context

        Returns:
            Created Escalation
        """
        import uuid

        level = REASON_TO_LEVEL.get(reason, EscalationLevel.HUMAN_ASYNC)

        escalation = Escalation(
            id=str(uuid.uuid4()),
            level=level,
            reason=reason,
            agent_name=agent_name,
            profile_id=profile_id,
            description=description,
            context=context or {},
        )

        self._escalations[escalation.id] = escalation

        logger.warning(
            f"ESCALATION [{level.value}]: {reason.value} - {description} "
            f"(Profile: {profile_id}, Agent: {agent_name})"
        )

        # Notify handlers
        self._notify_handlers(escalation)

        return escalation

    def _notify_handlers(self, escalation: Escalation) -> None:
        """Notify registered handlers of escalation."""
        handlers = self._handlers.get(escalation.level, [])
        for handler in handlers:
            try:
                handler(escalation)
            except Exception as e:
                logger.error(f"Error in escalation handler: {e}")

        # Emergency escalations also notify all higher levels
        if escalation.level == EscalationLevel.EMERGENCY:
            for level in [EscalationLevel.HUMAN_SYNC, EscalationLevel.HUMAN_ASYNC]:
                for handler in self._handlers.get(level, []):
                    try:
                        handler(escalation)
                    except Exception as e:
                        logger.error(f"Error in escalation handler: {e}")

    def register_handler(
        self,
        level: EscalationLevel,
        handler: Callable[[Escalation], None],
    ) -> None:
        """Register a handler for a specific escalation level."""
        if level not in self._handlers:
            self._handlers[level] = []
        self._handlers[level].append(handler)

    def resolve(
        self,
        escalation_id: str,
        resolved_by: str,
        resolution: str,
    ) -> Escalation:
        """
        Resolve an escalation.

        Args:
            escalation_id: ID of the escalation
            resolved_by: Who resolved it
            resolution: How it was resolved

        Returns:
            Updated Escalation
        """
        escalation = self._escalations.get(escalation_id)
        if not escalation:
            raise ValueError(f"Escalation {escalation_id} not found")

        escalation.resolved = True
        escalation.resolved_at = datetime.utcnow()
        escalation.resolved_by = resolved_by
        escalation.resolution = resolution

        logger.info(
            f"Escalation {escalation_id} resolved by {resolved_by}: {resolution}"
        )

        return escalation

    def get_pending(
        self,
        level: Optional[EscalationLevel] = None,
    ) -> List[Escalation]:
        """Get pending escalations, optionally filtered by level."""
        pending = [e for e in self._escalations.values() if not e.resolved]
        if level:
            pending = [e for e in pending if e.level == level]
        return sorted(pending, key=lambda e: e.created_at, reverse=True)

    def get_escalation(self, escalation_id: str) -> Optional[Escalation]:
        """Get a specific escalation by ID."""
        return self._escalations.get(escalation_id)


class SafetyResponse:
    """
    Pre-defined safe responses for escalation scenarios.

    USP: Age-appropriate, safety-first responses.
    """

    SAFETY_CONCERN = """
    I'm concerned about what you've shared with me. Your safety is the most important thing.

    Please reach out to a trusted adult - a parent, counselor, or teacher - right away.

    If you're in immediate danger, please call 911 or go to your nearest emergency room.

    You can also reach:
    - National Suicide Prevention Lifeline: 988
    - Crisis Text Line: Text HOME to 741741

    I've notified our team so we can follow up and make sure you're okay.
    """

    DISTRESS = """
    I hear that you're going through a really difficult time. That sounds incredibly hard.

    While I'm here to help with college prep, I think it would be really helpful for you to talk
    to someone who specializes in supporting students through tough times.

    Would you be comfortable talking to your school counselor? They're trained to help with
    exactly these kinds of situations.

    In the meantime, I'm flagging this to our team so we can make sure you get the support you need.
    """

    OUT_OF_SCOPE = """
    I appreciate you sharing that with me, but that's outside my area of expertise.

    I'm designed to help with college admissions - things like activities, essays, and applications.

    For {topic}, I'd recommend talking to a {professional} who can give you proper guidance.

    Is there anything college-related I can help you with?
    """

    @classmethod
    def get_response(
        cls,
        reason: EscalationReason,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Get appropriate response for escalation reason."""
        context = context or {}

        if reason == EscalationReason.SAFETY_CONCERN:
            return cls.SAFETY_CONCERN.strip()

        if reason == EscalationReason.STUDENT_DISTRESS:
            return cls.DISTRESS.strip()

        if reason == EscalationReason.OUT_OF_SCOPE:
            topic = context.get("topic", "that topic")
            professional = context.get("professional", "qualified professional")
            return cls.OUT_OF_SCOPE.format(
                topic=topic,
                professional=professional,
            ).strip()

        return "I've escalated this to our team for review."


# Convenience functions
def check_escalation_needed(
    message: str,
    context: Dict[str, Any],
) -> Optional[tuple[EscalationReason, EscalationLevel]]:
    """Quick check if escalation is needed."""
    protocol = EscalationProtocol()
    return protocol.check_for_escalation(message, context)


def create_escalation(
    agent_name: str,
    profile_id: str,
    reason: EscalationReason,
    description: str,
) -> Escalation:
    """Quick helper to create an escalation."""
    protocol = EscalationProtocol()
    return protocol.escalate(agent_name, profile_id, reason, description)
