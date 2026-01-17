"""
Pattern G1: Decision Rights
v5.4 True Autonomous Agents

3P: Pydantic for validation
USP: Who can decide what, based on student safety
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class DecisionLevel(str, Enum):
    """Levels of decision authority."""
    AUTONOMOUS = "autonomous"         # Agent decides alone
    SUPERVISED = "supervised"         # Agent decides, human reviews
    COLLABORATIVE = "collaborative"   # Agent proposes, human approves
    ESCALATE = "escalate"            # Human must decide


class DecisionCategory(str, Enum):
    """Categories of decisions."""
    RECOMMENDATION = "recommendation"     # Suggesting awards/programs
    ASSESSMENT = "assessment"            # Evaluating student profile
    COMMUNICATION = "communication"      # What to say to student
    PRIORITIZATION = "prioritization"    # What to focus on
    DEADLINE = "deadline"               # Deadline-related decisions
    CRISIS = "crisis"                   # Urgent/sensitive situations
    DATA_CHANGE = "data_change"         # Modifying student data


class Decision(BaseModel):
    """A decision that needs to be made."""
    id: str
    category: DecisionCategory
    description: str
    proposed_action: str
    confidence: float = Field(ge=0.0, le=1.0)
    agent_name: str
    requires_approval: bool = False
    approved: Optional[bool] = None
    approved_by: Optional[str] = None
    rationale: str = ""


# Decision rights matrix (USP)
# Maps (category, context_factor) -> decision_level
DECISION_RIGHTS_MATRIX: Dict[DecisionCategory, Dict[str, DecisionLevel]] = {
    DecisionCategory.RECOMMENDATION: {
        "default": DecisionLevel.AUTONOMOUS,
        "low_confidence": DecisionLevel.SUPERVISED,
        "financial_impact": DecisionLevel.COLLABORATIVE,
    },
    DecisionCategory.ASSESSMENT: {
        "default": DecisionLevel.AUTONOMOUS,
        "contradicts_history": DecisionLevel.SUPERVISED,
        "significant_change": DecisionLevel.COLLABORATIVE,
    },
    DecisionCategory.COMMUNICATION: {
        "default": DecisionLevel.AUTONOMOUS,
        "sensitive_topic": DecisionLevel.SUPERVISED,
        "crisis_detected": DecisionLevel.COLLABORATIVE,
    },
    DecisionCategory.PRIORITIZATION: {
        "default": DecisionLevel.AUTONOMOUS,
        "multiple_deadlines": DecisionLevel.SUPERVISED,
        "conflicting_goals": DecisionLevel.COLLABORATIVE,
    },
    DecisionCategory.DEADLINE: {
        "default": DecisionLevel.AUTONOMOUS,
        "missed_deadline": DecisionLevel.SUPERVISED,
        "application_deadline": DecisionLevel.COLLABORATIVE,
    },
    DecisionCategory.CRISIS: {
        "default": DecisionLevel.ESCALATE,
        "mild_stress": DecisionLevel.SUPERVISED,
        "severe_stress": DecisionLevel.ESCALATE,
    },
    DecisionCategory.DATA_CHANGE: {
        "default": DecisionLevel.COLLABORATIVE,
        "minor_update": DecisionLevel.SUPERVISED,
        "major_change": DecisionLevel.ESCALATE,
    },
}

# Confidence thresholds for decision levels
CONFIDENCE_THRESHOLDS = {
    DecisionLevel.AUTONOMOUS: 0.85,
    DecisionLevel.SUPERVISED: 0.70,
    DecisionLevel.COLLABORATIVE: 0.50,
    DecisionLevel.ESCALATE: 0.0,  # Always escalate below 50%
}


class DecisionRightsManager:
    """
    Manages who can decide what.

    Pattern G1: Decision Rights (3P: Pydantic)

    Why this matters for minors:
    - Students are vulnerable
    - Bad advice can have lasting impact
    - Parents/counselors need oversight
    - Some decisions require human judgment
    """

    def __init__(
        self,
        rights_matrix: Optional[Dict] = None,
        confidence_thresholds: Optional[Dict] = None,
    ):
        """
        Initialize decision rights manager.

        Args:
            rights_matrix: Custom rights matrix (defaults to DECISION_RIGHTS_MATRIX)
            confidence_thresholds: Custom thresholds (defaults to CONFIDENCE_THRESHOLDS)
        """
        self.rights_matrix = rights_matrix or DECISION_RIGHTS_MATRIX
        self.thresholds = confidence_thresholds or CONFIDENCE_THRESHOLDS
        self._pending_decisions: Dict[str, Decision] = {}
        self._approval_handlers: List[Callable[[Decision], None]] = []

    def determine_decision_level(
        self,
        category: DecisionCategory,
        confidence: float,
        context_factors: Optional[List[str]] = None,
    ) -> DecisionLevel:
        """
        Determine what level of authority is needed.

        Args:
            category: Type of decision
            confidence: Agent's confidence (0-1)
            context_factors: Situational factors (e.g., "low_confidence", "crisis_detected")

        Returns:
            Required DecisionLevel
        """
        context_factors = context_factors or []

        # Start with category defaults
        category_rights = self.rights_matrix.get(
            category,
            {"default": DecisionLevel.SUPERVISED}
        )

        # Check for context-specific rules
        level = category_rights.get("default", DecisionLevel.SUPERVISED)
        for factor in context_factors:
            if factor in category_rights:
                factor_level = category_rights[factor]
                # Take the more restrictive level
                if self._is_more_restrictive(factor_level, level):
                    level = factor_level

        # Check confidence threshold
        if confidence < self.thresholds.get(DecisionLevel.COLLABORATIVE, 0.5):
            level = DecisionLevel.ESCALATE
        elif confidence < self.thresholds.get(DecisionLevel.SUPERVISED, 0.7):
            if level == DecisionLevel.AUTONOMOUS:
                level = DecisionLevel.SUPERVISED
        elif confidence < self.thresholds.get(DecisionLevel.AUTONOMOUS, 0.85):
            if level == DecisionLevel.AUTONOMOUS:
                level = DecisionLevel.SUPERVISED

        logger.debug(
            f"Decision level for {category.value}: {level.value} "
            f"(confidence: {confidence}, factors: {context_factors})"
        )

        return level

    def _is_more_restrictive(
        self,
        level_a: DecisionLevel,
        level_b: DecisionLevel,
    ) -> bool:
        """Check if level_a is more restrictive than level_b."""
        order = [
            DecisionLevel.AUTONOMOUS,
            DecisionLevel.SUPERVISED,
            DecisionLevel.COLLABORATIVE,
            DecisionLevel.ESCALATE,
        ]
        return order.index(level_a) > order.index(level_b)

    def can_agent_decide(
        self,
        agent_name: str,
        category: DecisionCategory,
        confidence: float,
        context_factors: Optional[List[str]] = None,
    ) -> tuple[bool, DecisionLevel]:
        """
        Check if an agent can make this decision autonomously.

        Args:
            agent_name: Name of the agent
            category: Type of decision
            confidence: Agent's confidence
            context_factors: Situational factors

        Returns:
            Tuple of (can_decide_alone, required_level)
        """
        level = self.determine_decision_level(category, confidence, context_factors)

        can_decide = level == DecisionLevel.AUTONOMOUS

        if not can_decide:
            logger.info(
                f"Agent {agent_name} cannot decide {category.value} autonomously. "
                f"Level: {level.value}, Confidence: {confidence}"
            )

        return can_decide, level

    def request_approval(
        self,
        decision: Decision,
    ) -> str:
        """
        Submit a decision for approval.

        Args:
            decision: The decision needing approval

        Returns:
            Decision ID for tracking
        """
        decision.requires_approval = True
        self._pending_decisions[decision.id] = decision

        logger.info(
            f"Decision {decision.id} pending approval: {decision.description}"
        )

        # Notify handlers
        for handler in self._approval_handlers:
            try:
                handler(decision)
            except Exception as e:
                logger.error(f"Error in approval handler: {e}")

        return decision.id

    def approve_decision(
        self,
        decision_id: str,
        approved_by: str,
        approved: bool = True,
        rationale: str = "",
    ) -> Decision:
        """
        Approve or reject a pending decision.

        Args:
            decision_id: ID of the decision
            approved_by: Who approved it
            approved: Whether it's approved
            rationale: Reason for decision

        Returns:
            Updated Decision
        """
        decision = self._pending_decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")

        decision.approved = approved
        decision.approved_by = approved_by
        decision.rationale = rationale

        logger.info(
            f"Decision {decision_id} {'approved' if approved else 'rejected'} "
            f"by {approved_by}: {rationale}"
        )

        return decision

    def get_pending_decisions(
        self,
        category: Optional[DecisionCategory] = None,
    ) -> List[Decision]:
        """Get all pending decisions, optionally filtered by category."""
        decisions = list(self._pending_decisions.values())
        if category:
            decisions = [d for d in decisions if d.category == category]
        return [d for d in decisions if d.approved is None]

    def add_approval_handler(
        self,
        handler: Callable[[Decision], None],
    ) -> None:
        """Add a handler to be notified of pending approvals."""
        self._approval_handlers.append(handler)


def detect_context_factors(
    category: DecisionCategory,
    context: Dict[str, Any],
) -> List[str]:
    """
    Detect context factors that affect decision rights.

    USP: Intelligent factor detection based on situation.
    """
    factors = []

    # Check confidence
    confidence = context.get("confidence", 1.0)
    if confidence < 0.7:
        factors.append("low_confidence")

    # Check for crisis signals
    sentiment = context.get("detected_sentiment", "neutral")
    if sentiment in ["stressed", "crisis"]:
        factors.append("crisis_detected")
    if sentiment == "stressed":
        factors.append("mild_stress")

    # Check for financial impact
    if context.get("has_financial_impact", False):
        factors.append("financial_impact")

    # Check for deadline proximity
    if context.get("days_until_deadline", 999) < 7:
        if category == DecisionCategory.DEADLINE:
            factors.append("application_deadline")

    # Check for significant changes
    if context.get("contradicts_previous", False):
        factors.append("contradicts_history")

    if context.get("is_major_change", False):
        factors.append("major_change")
        factors.append("significant_change")

    return factors


# Convenience function
def check_decision_rights(
    agent_name: str,
    category: DecisionCategory,
    confidence: float,
    context: Dict[str, Any],
) -> tuple[bool, DecisionLevel, List[str]]:
    """
    Quick check of decision rights.

    Returns:
        Tuple of (can_decide, level, factors)
    """
    factors = detect_context_factors(category, context)
    manager = DecisionRightsManager()
    can_decide, level = manager.can_agent_decide(
        agent_name,
        category,
        confidence,
        factors,
    )
    return can_decide, level, factors
