"""
IvyQuest v10.0 Base Agent Class
===============================
Abstract base class for all IvyQuest agents.
Provides common functionality: state versioning, event publishing, HITL.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog

from config import settings, AutonomyLevel
from tools.database import (
    get_profile,
    update_profile,
    create_state_version,
    get_latest_state,
)

logger = structlog.get_logger()


class BaseAgent(ABC):
    """
    Abstract base class for all IvyQuest agents.

    Provides:
    - State versioning (every state change is versioned)
    - Event publishing (via Supabase Realtime)
    - HITL (Human-in-the-Loop) support
    - Profile access helpers
    """

    def __init__(self, name: str, autonomy_level: str = AutonomyLevel.HIGH):
        """
        Initialize agent.

        Args:
            name: Agent name (e.g., 'Execution', 'Assessment')
            autonomy_level: One of FULL, HIGH, MEDIUM, LOW
        """
        self.name = name
        self.autonomy_level = autonomy_level
        self.logger = logger.bind(agent=name)

    @abstractmethod
    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Main processing method. Must be implemented by subclasses.

        Args:
            profile_id: Profile UUID to process
            **kwargs: Additional arguments

        Returns:
            Dict with processing results
        """
        pass

    # =========================================
    # Profile Helpers
    # =========================================

    async def _get_profile(self, profile_id: str) -> Optional[Dict]:
        """Get profile by ID with logging."""
        profile = await get_profile(profile_id)
        if not profile:
            self.logger.warning("profile_not_found", profile_id=profile_id)
        return profile

    async def _update_profile(self, profile_id: str, updates: Dict) -> bool:
        """Update profile with new data."""
        success = await update_profile(profile_id, updates)
        if success:
            self.logger.info("profile_updated", profile_id=profile_id, fields=list(updates.keys()))
        else:
            self.logger.error("profile_update_failed", profile_id=profile_id)
        return success

    # =========================================
    # State Versioning (CRITICAL per v9.1)
    # =========================================

    async def _version_state(
        self,
        profile_id: str,
        event_type: str,
        state: Dict,
        created_by: str = "agent",
        rationale: Optional[str] = None,
        event_payload: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Version every state change for rollback/forensics.

        CRITICAL: This must be called on ALL agent state changes per v9.1 spec.

        Args:
            profile_id: Profile UUID
            event_type: Type of event (e.g., 'assessment_enhanced', 'crisis_resolved')
            state: Full state snapshot to version
            created_by: 'agent', 'human', or 'system'
            rationale: Explanation for the change
            event_payload: Original event data

        Returns:
            Version ID if successful, None otherwise
        """
        if not settings.enable_state_versioning:
            self.logger.debug("state_versioning_disabled", profile_id=profile_id)
            return None

        version_id = await create_state_version(
            profile_id=profile_id,
            agent=self.name,
            state=state,
            event_type=event_type,
            created_by=created_by,
            rationale=rationale,
            event_payload=event_payload
        )

        if version_id:
            self.logger.info(
                "state_versioned",
                profile_id=profile_id,
                event_type=event_type,
                version_id=version_id,
                created_by=created_by
            )
        else:
            self.logger.error(
                "state_versioning_failed",
                profile_id=profile_id,
                event_type=event_type
            )

        return version_id

    async def _get_previous_state(self, profile_id: str) -> Optional[Dict]:
        """Get the most recent state for this agent/profile."""
        return await get_latest_state(profile_id, self.name)

    # =========================================
    # Event Publishing
    # =========================================

    async def _publish_event(self, event_type: str, payload: Dict) -> bool:
        """
        Publish event to the event bus.

        Events are used for:
        - Agent-to-agent communication
        - Dashboard updates
        - RLHF logging (SUCCESS_ACHIEVED only)

        Args:
            event_type: Event type (e.g., 'ASSESSMENT_COMPLETED', 'CRISIS_DETECTED')
            payload: Event payload (must include profileId)

        Returns:
            True if published successfully
        """
        if not settings.enable_event_bus:
            self.logger.debug("event_bus_disabled", event_type=event_type)
            return False

        # TODO: Implement Supabase Realtime publishing
        # For now, just log the event
        self.logger.info(
            "event_published",
            event_type=event_type,
            payload=payload
        )
        return True

    # =========================================
    # HITL (Human-in-the-Loop) Support
    # =========================================

    def _requires_hitl(self, context: Dict) -> bool:
        """
        Check if this action requires Human-in-the-Loop approval.

        LOW autonomy actions (crises) always require HITL.
        MEDIUM autonomy actions require HITL if confidence < 0.7.

        Args:
            context: Current context with confidence, is_crisis, etc.

        Returns:
            True if HITL approval is required
        """
        # LOW autonomy = always HITL
        if self.autonomy_level == AutonomyLevel.LOW:
            return True

        # Crisis actions always require HITL
        if context.get("is_crisis", False):
            return True

        # Medium autonomy with low confidence
        if self.autonomy_level == AutonomyLevel.MEDIUM:
            confidence = context.get("confidence", 0.5)
            if confidence < 0.7:
                return True

        return False

    def _get_hitl_deadline(self) -> str:
        """
        Get HITL approval deadline (default: 1 hour from now).

        Per spec: Crisis responses must be approved within 1 hour.

        Returns:
            ISO format datetime string
        """
        deadline = datetime.now() + timedelta(hours=settings.hitl_timeout_hours)
        return deadline.isoformat()

    async def _request_hitl_approval(
        self,
        profile_id: str,
        action_type: str,
        proposed_action: Dict,
        rationale: str
    ) -> Dict:
        """
        Request HITL approval for an action.

        Creates a pending approval record and returns immediately.
        The coach will approve/reject via the handoff API.

        Args:
            profile_id: Profile UUID
            action_type: Type of action needing approval
            proposed_action: The action to be approved
            rationale: Why this action is proposed

        Returns:
            Dict with approval_id, deadline, status
        """
        deadline = self._get_hitl_deadline()

        self.logger.info(
            "hitl_approval_requested",
            profile_id=profile_id,
            action_type=action_type,
            deadline=deadline
        )

        # TODO: Create approval record in database
        # TODO: Send notification to coach

        return {
            "status": "awaiting_approval",
            "deadline": deadline,
            "proposed_action": proposed_action,
            "rationale": rationale,
            "requires_human_approval": True
        }

    # =========================================
    # Confidence & Explainability
    # =========================================

    def _calculate_confidence(self, factors: Dict[str, float]) -> float:
        """
        Calculate overall confidence from multiple factors.

        Used for archetype detection, narrative synthesis, etc.
        Handoff to human if confidence < 0.7.

        Args:
            factors: Dict of factor_name -> confidence_score (0-1)

        Returns:
            Weighted average confidence (0-1)
        """
        if not factors:
            return 0.5

        total_weight = sum(factors.values())
        if total_weight == 0:
            return 0.5

        # Simple average for now
        return sum(factors.values()) / len(factors)

    def _generate_rationale(self, decision: str, factors: Dict[str, Any]) -> str:
        """
        Generate explainable rationale for a decision.

        Per v9.1: All agent decisions must include rationale for transparency.

        Args:
            decision: The decision made
            factors: Factors that influenced the decision

        Returns:
            Human-readable rationale string
        """
        parts = [f"Decision: {decision}"]

        if factors:
            parts.append("Based on:")
            for factor, value in factors.items():
                if isinstance(value, float):
                    parts.append(f"  - {factor}: {value:.2f}")
                else:
                    parts.append(f"  - {factor}: {value}")

        return "\n".join(parts)

    # =========================================
    # Logging Helpers
    # =========================================

    def _log_start(self, operation: str, **kwargs):
        """Log operation start."""
        self.logger.info(f"{operation}_started", **kwargs)

    def _log_complete(self, operation: str, **kwargs):
        """Log operation completion."""
        self.logger.info(f"{operation}_completed", **kwargs)

    def _log_error(self, operation: str, error: Exception, **kwargs):
        """Log operation error."""
        self.logger.error(f"{operation}_error", error=str(error), **kwargs)
