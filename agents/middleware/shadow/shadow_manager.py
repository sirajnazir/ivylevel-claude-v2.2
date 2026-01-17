"""
G5: Human Shadow Mode - Implementation

Manages human shadow mode for agent outputs.
"""

from typing import Optional, List, Dict, Any, Callable, Awaitable
from datetime import datetime, timedelta
import logging
import asyncio
import uuid

from .types import (
    ShadowMode,
    ShadowProposal,
    ShadowReview,
    ShadowConfig,
)

logger = logging.getLogger(__name__)


# Default shadow configurations (USP: IvyLevel coaching workflow)
DEFAULT_SHADOW_CONFIGS: List[ShadowConfig] = [
    # New students start with full review
    ShadowConfig(
        profile_id=None,
        agent_name=None,
        shadow_mode=ShadowMode.ADVISORY,
        upgrade_to_review_if=[
            "student_is_new",
            "high_stakes_action",
            "low_agent_confidence",
        ],
        upgrade_to_approval_if=[
            "crisis_detected",
            "application_submission",
        ],
    ),
]


class HumanShadowManager:
    """
    Manages human shadow mode for agent outputs.

    Pattern G5: Human Shadow Mode (USP)

    Shadow Levels:
    1. OFF: Agent acts autonomously
    2. ADVISORY: Coach sees but agent proceeds
    3. REVIEW: Coach can modify before sending
    4. APPROVAL: Coach must approve before sending

    Integration with Critical 15:
    - Uses G1 Decision Rights to determine base shadow level
    - Uses G2 Approval Gates for blocking actions
    - Feeds I3 Goal Monitoring with coach feedback
    """

    def __init__(
        self,
        supabase_client=None,
        configs: Optional[List[ShadowConfig]] = None,
        notify_coach: Optional[Callable[[ShadowProposal], Awaitable[None]]] = None,
    ):
        """
        Initialize shadow manager.

        Args:
            supabase_client: For persistence
            configs: Shadow configurations
            notify_coach: Callback to notify coach of proposals
        """
        self.supabase = supabase_client
        self.configs = configs or DEFAULT_SHADOW_CONFIGS
        self.notify_coach = notify_coach
        self._pending_proposals: Dict[str, ShadowProposal] = {}

    def get_shadow_mode(
        self,
        profile_id: str,
        agent_name: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ShadowMode:
        """
        Determine shadow mode for this interaction.

        Args:
            profile_id: Student profile
            agent_name: Which agent
            context: Additional context for rule evaluation

        Returns:
            Appropriate ShadowMode
        """
        # Find matching config
        config = self._find_config(profile_id, agent_name)
        base_mode = config.shadow_mode

        # Check for upgrades
        context = context or {}

        # Check approval-level conditions first
        for condition in config.upgrade_to_approval_if:
            if self._check_condition(condition, context):
                logger.info(f"Shadow mode upgraded to APPROVAL: {condition}")
                return ShadowMode.APPROVAL

        # Check review-level conditions
        for condition in config.upgrade_to_review_if:
            if self._check_condition(condition, context):
                logger.info(f"Shadow mode upgraded to REVIEW: {condition}")
                return ShadowMode.REVIEW

        return base_mode

    async def submit_proposal(
        self,
        profile_id: str,
        agent_name: str,
        proposal_type: str,
        proposed_content: str,
        proposed_payload: Optional[Dict[str, Any]] = None,
        student_message: Optional[str] = None,
        relevant_context: Optional[Dict[str, Any]] = None,
        agent_reasoning: str = "",
        confidence_score: float = 0.7,
        alternative_responses: Optional[List[Dict[str, Any]]] = None,
    ) -> ShadowProposal:
        """
        Submit a proposal for shadow review.

        Args:
            profile_id: Student profile
            agent_name: Proposing agent
            proposal_type: Type of proposal
            proposed_content: The proposed response/action
            proposed_payload: Additional data
            student_message: What student said (for context)
            relevant_context: Other context for reviewer
            agent_reasoning: Why agent chose this
            confidence_score: Agent's confidence
            alternative_responses: Other options considered

        Returns:
            ShadowProposal
        """
        # Determine shadow mode
        shadow_mode = self.get_shadow_mode(
            profile_id,
            agent_name,
            {
                "confidence": confidence_score,
                "proposal_type": proposal_type,
                **(relevant_context or {}),
            }
        )

        proposal = ShadowProposal(
            proposal_id=str(uuid.uuid4()),
            profile_id=profile_id,
            agent_name=agent_name,
            proposal_type=proposal_type,
            proposed_content=proposed_content,
            proposed_payload=proposed_payload or {},
            student_message=student_message,
            relevant_context=relevant_context or {},
            agent_reasoning=agent_reasoning,
            confidence_score=confidence_score,
            alternative_responses=alternative_responses or [],
            shadow_mode=shadow_mode,
        )

        # Store proposal
        self._pending_proposals[proposal.proposal_id] = proposal

        # Persist
        if self.supabase:
            await self._persist_proposal(proposal)

        # Notify coach if not OFF mode
        if shadow_mode != ShadowMode.OFF and self.notify_coach:
            await self.notify_coach(proposal)

        logger.info(
            f"Shadow proposal submitted: {proposal.proposal_id} "
            f"({shadow_mode.value}, confidence={confidence_score})"
        )

        return proposal

    async def await_review(
        self,
        proposal: ShadowProposal,
        timeout_seconds: Optional[int] = None,
    ) -> ShadowProposal:
        """
        Wait for shadow review if required.

        Args:
            proposal: The proposal to review
            timeout_seconds: Max wait time

        Returns:
            Updated proposal with final content
        """
        # OFF mode - proceed immediately
        if proposal.shadow_mode == ShadowMode.OFF:
            proposal.final_content = proposal.proposed_content
            return proposal

        # ADVISORY mode - proceed but log
        if proposal.shadow_mode == ShadowMode.ADVISORY:
            proposal.final_content = proposal.proposed_content
            logger.info(f"Advisory shadow: proceeding with proposal {proposal.proposal_id}")
            return proposal

        # REVIEW or APPROVAL mode - wait for coach
        config = self._find_config(proposal.profile_id, proposal.agent_name)
        timeout = timeout_seconds or (config.review_timeout_minutes * 60)

        start = datetime.utcnow()
        while (datetime.utcnow() - start).total_seconds() < timeout:
            # Check for review
            review = await self._check_review(proposal.proposal_id)
            if review:
                return self._apply_review(proposal, review)

            await asyncio.sleep(5)

        # Timeout reached
        if config.auto_proceed_on_timeout:
            logger.warning(
                f"Shadow review timeout: proceeding with original "
                f"({proposal.proposal_id})"
            )
            proposal.final_content = proposal.proposed_content
            return proposal
        else:
            logger.warning(
                f"Shadow review timeout: blocking "
                f"({proposal.proposal_id})"
            )
            proposal.final_content = None  # Block the response
            return proposal

    async def submit_review(
        self,
        proposal_id: str,
        reviewer_id: str,
        action: str,
        modified_content: Optional[str] = None,
        modifications_description: Optional[List[str]] = None,
        quality_rating: Optional[int] = None,
        feedback_for_agent: Optional[str] = None,
    ) -> ShadowReview:
        """
        Submit coach review of a proposal.

        Args:
            proposal_id: Proposal being reviewed
            reviewer_id: Coach ID
            action: "approve", "modify", "reject", "escalate"
            modified_content: Modified version if action="modify"
            modifications_description: What was changed
            quality_rating: 1-5 rating of agent output
            feedback_for_agent: Feedback for agent improvement

        Returns:
            ShadowReview
        """
        review = ShadowReview(
            proposal_id=proposal_id,
            reviewer_id=reviewer_id,
            action=action,
            modified_content=modified_content,
            modifications_description=modifications_description or [],
            quality_rating=quality_rating,
            feedback_for_agent=feedback_for_agent,
        )

        # Persist review
        if self.supabase:
            await self._persist_review(review)

        # Update proposal in memory
        if proposal_id in self._pending_proposals:
            proposal = self._pending_proposals[proposal_id]
            self._apply_review(proposal, review)

        logger.info(
            f"Shadow review submitted: {proposal_id} -> {action} "
            f"by {reviewer_id}"
        )

        return review

    def _find_config(
        self,
        profile_id: str,
        agent_name: str,
    ) -> ShadowConfig:
        """Find most specific matching config."""
        # Look for exact match first
        for config in self.configs:
            if config.profile_id == profile_id and config.agent_name == agent_name:
                return config

        # Profile-specific, any agent
        for config in self.configs:
            if config.profile_id == profile_id and config.agent_name is None:
                return config

        # Agent-specific, any profile
        for config in self.configs:
            if config.profile_id is None and config.agent_name == agent_name:
                return config

        # Global default
        for config in self.configs:
            if config.profile_id is None and config.agent_name is None:
                return config

        # Fallback
        return ShadowConfig()

    def _check_condition(
        self,
        condition: str,
        context: Dict[str, Any],
    ) -> bool:
        """Check if a condition is met."""
        condition_checks = {
            # Only trigger if session_count is explicitly provided and low
            "student_is_new": lambda c: "session_count" in c and c.get("session_count", 999) < 3,
            "high_stakes_action": lambda c: c.get("proposal_type") in [
                "submit_application", "change_college_list", "finalize_essay"
            ],
            "low_agent_confidence": lambda c: c.get("confidence", 1.0) < 0.6,
            "crisis_detected": lambda c: c.get("crisis_detected", False),
            "application_submission": lambda c: "submit" in c.get("proposal_type", ""),
        }

        checker = condition_checks.get(condition)
        if checker:
            return checker(context)
        return False

    def _apply_review(
        self,
        proposal: ShadowProposal,
        review: ShadowReview,
    ) -> ShadowProposal:
        """Apply review to proposal."""
        proposal.reviewed_at = review.reviewed_at
        proposal.reviewer_id = review.reviewer_id
        proposal.modifications_made = review.modifications_description

        if review.action == "approve":
            proposal.final_content = proposal.proposed_content
        elif review.action == "modify":
            proposal.final_content = review.modified_content
        elif review.action == "reject":
            proposal.final_content = None
        elif review.action == "escalate":
            proposal.final_content = None
            proposal.coach_notes = "Escalated for further review"

        return proposal

    async def _check_review(self, proposal_id: str) -> Optional[ShadowReview]:
        """Check if review exists for proposal."""
        if self.supabase:
            try:
                result = self.supabase.table("shadow_reviews").select(
                    "*"
                ).eq("proposal_id", proposal_id).single().execute()

                if result.data:
                    return ShadowReview(**result.data)
            except Exception:
                pass
        return None

    async def _persist_proposal(self, proposal: ShadowProposal) -> None:
        """Persist proposal to database."""
        try:
            self.supabase.table("shadow_proposals").insert({
                "id": proposal.proposal_id,
                "profile_id": proposal.profile_id,
                "agent_name": proposal.agent_name,
                "proposal_type": proposal.proposal_type,
                "proposed_content": proposal.proposed_content,
                "proposed_payload": proposal.proposed_payload,
                "student_message": proposal.student_message,
                "relevant_context": proposal.relevant_context,
                "agent_reasoning": proposal.agent_reasoning,
                "confidence_score": proposal.confidence_score,
                "alternative_responses": proposal.alternative_responses,
                "shadow_mode": proposal.shadow_mode.value,
                "created_at": proposal.created_at.isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to persist shadow proposal: {e}")

    async def _persist_review(self, review: ShadowReview) -> None:
        """Persist review to database."""
        try:
            self.supabase.table("shadow_reviews").insert({
                "proposal_id": review.proposal_id,
                "reviewer_id": review.reviewer_id,
                "action": review.action,
                "modified_content": review.modified_content,
                "modifications_description": review.modifications_description,
                "quality_rating": review.quality_rating,
                "feedback_for_agent": review.feedback_for_agent,
                "reviewed_at": review.reviewed_at.isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to persist shadow review: {e}")
