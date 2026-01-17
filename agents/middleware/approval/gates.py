"""
G2: Approval Gates - Implementation

Manages approval gates for agent actions.
"""

from typing import Optional, List, Dict, Any, Callable, Awaitable
from datetime import datetime, timedelta
import logging
import re
import uuid

from .types import (
    ApprovalRequest,
    ApprovalDecision,
    ApprovalRule,
    ApprovalCategory,
    ApprovalUrgency,
    ApprovalStatus,
)

logger = logging.getLogger(__name__)


# Default approval rules for IvyLevel (USP)
DEFAULT_APPROVAL_RULES: List[ApprovalRule] = [
    # Strategic changes
    ApprovalRule(
        rule_id="strategic_college_list",
        action_pattern="change_college_list|remove_school|add_reach_school",
        category=ApprovalCategory.STRATEGIC,
        urgency=ApprovalUrgency.SAME_DAY,
        description="College list modifications require coach review",
    ),
    ApprovalRule(
        rule_id="strategic_major_pivot",
        action_pattern="change_spike|pivot_narrative|change_archetype",
        category=ApprovalCategory.STRATEGIC,
        urgency=ApprovalUrgency.STANDARD,
        min_confidence_bypass=0.95,
        description="Identity/narrative changes need review unless very confident",
    ),

    # Content approval
    ApprovalRule(
        rule_id="content_final_essay",
        action_pattern="finalize_essay|submit_essay",
        category=ApprovalCategory.CONTENT,
        urgency=ApprovalUrgency.SAME_DAY,
        description="Final essay versions require coach approval",
    ),
    ApprovalRule(
        rule_id="content_application_submit",
        action_pattern="submit_application",
        category=ApprovalCategory.CONTENT,
        urgency=ApprovalUrgency.IMMEDIATE,
        description="Application submission requires explicit approval",
    ),

    # Crisis handling
    ApprovalRule(
        rule_id="crisis_mental_health",
        action_pattern="crisis_response|mental_health_referral",
        category=ApprovalCategory.CRISIS,
        urgency=ApprovalUrgency.IMMEDIATE,
        description="Mental health situations require immediate coach involvement",
    ),

    # Deadline changes
    ApprovalRule(
        rule_id="deadline_extension",
        action_pattern="extend_deadline|modify_timeline",
        category=ApprovalCategory.DEADLINE,
        urgency=ApprovalUrgency.STANDARD,
        min_confidence_bypass=0.9,
        description="Deadline changes need review",
    ),
]


class ApprovalGateManager:
    """
    Manages approval gates for agent actions.

    Pattern G2: Approval Gates

    Integration with Critical 15:
    - Uses G1 DecisionRights to determine autonomy level
    - Uses G3 Escalation to route approval requests
    - Works with MiddlewareStack for context
    """

    def __init__(
        self,
        supabase_client=None,
        rules: Optional[List[ApprovalRule]] = None,
        notification_callback: Optional[Callable[[ApprovalRequest], Awaitable[None]]] = None,
    ):
        """
        Initialize approval gate manager.

        Args:
            supabase_client: For persisting approval requests
            rules: Custom approval rules (defaults to IvyLevel rules)
            notification_callback: Called when approval is needed
        """
        self.supabase = supabase_client
        self.rules = rules or DEFAULT_APPROVAL_RULES
        self.notify = notification_callback
        self._pending_requests: Dict[str, ApprovalRequest] = {}

    def check_requires_approval(
        self,
        action_type: str,
        agent_confidence: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ApprovalRule]:
        """
        Check if an action requires approval.

        Args:
            action_type: Type of action being performed
            agent_confidence: Agent's confidence in the action
            context: Additional context for rule evaluation

        Returns:
            ApprovalRule if approval needed, None otherwise
        """
        for rule in self.rules:
            if not rule.enabled:
                continue

            # Check action pattern match
            if re.match(rule.action_pattern, action_type):
                # Check confidence bypass
                if agent_confidence >= rule.min_confidence_bypass:
                    logger.debug(
                        f"Action {action_type} bypassed approval "
                        f"(confidence {agent_confidence} >= {rule.min_confidence_bypass})"
                    )
                    continue

                # Check conditional rules
                if rule.requires_approval_if:
                    if not self._evaluate_condition(rule.requires_approval_if, context):
                        continue

                logger.info(f"Action {action_type} requires approval: {rule.rule_id}")
                return rule

        return None

    async def request_approval(
        self,
        profile_id: str,
        agent_name: str,
        action_type: str,
        action_description: str,
        action_payload: Dict[str, Any],
        rule: ApprovalRule,
        agent_confidence: float = 0.5,
        agent_reasoning: str = "",
        alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> ApprovalRequest:
        """
        Create and submit an approval request.

        Args:
            profile_id: Student profile
            agent_name: Requesting agent
            action_type: Type of action
            action_description: Human-readable description
            action_payload: The actual action data
            rule: The rule that triggered approval
            agent_confidence: Agent's confidence
            agent_reasoning: Why agent wants to do this
            alternatives: Other options considered

        Returns:
            ApprovalRequest with pending status
        """
        # Calculate expiration
        expiry_map = {
            ApprovalUrgency.IMMEDIATE: timedelta(hours=1),
            ApprovalUrgency.SAME_DAY: timedelta(hours=24),
            ApprovalUrgency.STANDARD: timedelta(days=5),
            ApprovalUrgency.ADVISORY: timedelta(days=14),
        }
        expires_at = datetime.utcnow() + expiry_map.get(rule.urgency, timedelta(days=5))

        request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            profile_id=profile_id,
            agent_name=agent_name,
            category=rule.category,
            action_type=action_type,
            action_description=action_description,
            action_payload=action_payload,
            urgency=rule.urgency,
            reason=rule.description,
            agent_confidence=agent_confidence,
            agent_reasoning=agent_reasoning,
            alternatives=alternatives or [],
            expires_at=expires_at,
        )

        # Store request
        self._pending_requests[request.request_id] = request

        # Persist to database
        if self.supabase:
            await self._persist_request(request)

        # Notify reviewer
        if self.notify:
            await self.notify(request)

        logger.info(
            f"Approval request created: {request.request_id} "
            f"({request.category.value}, {request.urgency.value})"
        )

        return request

    async def await_approval(
        self,
        request: ApprovalRequest,
        timeout_seconds: Optional[int] = None,
        poll_interval: int = 5,
    ) -> ApprovalDecision:
        """
        Wait for approval decision.

        Args:
            request: The approval request
            timeout_seconds: Max time to wait (None = wait until expiry)
            poll_interval: Seconds between status checks

        Returns:
            ApprovalDecision when received or expired
        """
        import asyncio

        timeout = timeout_seconds or int(
            (request.expires_at - datetime.utcnow()).total_seconds()
        )

        start = datetime.utcnow()
        while (datetime.utcnow() - start).total_seconds() < timeout:
            # Check for decision
            decision = await self._check_decision(request.request_id)
            if decision:
                return decision

            # Check expiration
            if datetime.utcnow() > request.expires_at:
                return ApprovalDecision(
                    request_id=request.request_id,
                    status=ApprovalStatus.EXPIRED,
                    reviewer_id="system",
                    reviewer_role="system",
                    decision_reason="Request expired without response",
                )

            await asyncio.sleep(poll_interval)

        # Timeout
        return ApprovalDecision(
            request_id=request.request_id,
            status=ApprovalStatus.EXPIRED,
            reviewer_id="system",
            reviewer_role="system",
            decision_reason="Approval timeout exceeded",
        )

    async def submit_decision(
        self,
        request_id: str,
        approved: bool,
        reviewer_id: str,
        reviewer_role: str,
        reason: Optional[str] = None,
        modifications: Optional[Dict[str, Any]] = None,
    ) -> ApprovalDecision:
        """
        Submit a decision on an approval request.

        Args:
            request_id: The request being decided
            approved: True = approved, False = rejected
            reviewer_id: Who is deciding
            reviewer_role: Their role
            reason: Why this decision
            modifications: Changes to the original action

        Returns:
            ApprovalDecision
        """
        decision = ApprovalDecision(
            request_id=request_id,
            status=ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            decision_reason=reason,
            modifications=modifications,
        )

        # Update request status
        if request_id in self._pending_requests:
            self._pending_requests[request_id].status = decision.status

        # Persist decision
        if self.supabase:
            await self._persist_decision(decision)

        logger.info(
            f"Approval decision: {request_id} = {decision.status.value} "
            f"by {reviewer_role}/{reviewer_id}"
        )

        return decision

    def get_pending_requests(
        self,
        profile_id: Optional[str] = None,
        category: Optional[ApprovalCategory] = None,
    ) -> List[ApprovalRequest]:
        """Get pending approval requests, optionally filtered."""
        requests = list(self._pending_requests.values())

        if profile_id:
            requests = [r for r in requests if r.profile_id == profile_id]
        if category:
            requests = [r for r in requests if r.category == category]

        # Filter out non-pending
        requests = [r for r in requests if r.status == ApprovalStatus.PENDING]

        return sorted(requests, key=lambda r: r.created_at)

    def _evaluate_condition(
        self,
        condition: str,
        context: Optional[Dict[str, Any]],
    ) -> bool:
        """Evaluate a conditional rule expression."""
        if not context:
            return False  # No context means condition cannot be met
        # Simple key=value evaluation for now
        # Can be extended to support more complex expressions
        try:
            key, value = condition.split("=")
            key = key.strip()
            expected = value.strip()
            # Key must exist in context
            if key not in context:
                return False
            actual = context.get(key)
            # Case-insensitive comparison for boolean strings
            return str(actual).lower() == expected.lower()
        except Exception:
            return False

    async def _persist_request(self, request: ApprovalRequest) -> None:
        """Persist approval request to database."""
        try:
            self.supabase.table("approval_requests").insert({
                "id": request.request_id,
                "profile_id": request.profile_id,
                "agent_name": request.agent_name,
                "category": request.category.value,
                "action_type": request.action_type,
                "action_description": request.action_description,
                "action_payload": request.action_payload,
                "urgency": request.urgency.value,
                "reason": request.reason,
                "agent_confidence": request.agent_confidence,
                "agent_reasoning": request.agent_reasoning,
                "alternatives": request.alternatives,
                "status": request.status.value,
                "expires_at": request.expires_at.isoformat() if request.expires_at else None,
                "created_at": request.created_at.isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to persist approval request: {e}")

    async def _persist_decision(self, decision: ApprovalDecision) -> None:
        """Persist approval decision to database."""
        try:
            self.supabase.table("approval_requests").update({
                "status": decision.status.value,
                "reviewer_id": decision.reviewer_id,
                "reviewer_role": decision.reviewer_role,
                "decision_reason": decision.decision_reason,
                "modifications": decision.modifications,
                "decided_at": decision.decided_at.isoformat(),
            }).eq("id", decision.request_id).execute()
        except Exception as e:
            logger.error(f"Failed to persist approval decision: {e}")

    async def _check_decision(self, request_id: str) -> Optional[ApprovalDecision]:
        """Check if a decision has been made on a request."""
        if request_id not in self._pending_requests:
            return None

        request = self._pending_requests[request_id]
        if request.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
            # Decision exists in memory
            return ApprovalDecision(
                request_id=request_id,
                status=request.status,
                reviewer_id="unknown",
                reviewer_role="unknown",
            )

        # Check database for external updates
        if self.supabase:
            try:
                result = self.supabase.table("approval_requests").select(
                    "status, reviewer_id, reviewer_role, decision_reason, modifications, decided_at"
                ).eq("id", request_id).single().execute()

                if result.data and result.data.get("status") in ["approved", "rejected"]:
                    return ApprovalDecision(
                        request_id=request_id,
                        status=ApprovalStatus(result.data["status"]),
                        reviewer_id=result.data.get("reviewer_id", "unknown"),
                        reviewer_role=result.data.get("reviewer_role", "unknown"),
                        decision_reason=result.data.get("decision_reason"),
                        modifications=result.data.get("modifications"),
                    )
            except Exception as e:
                logger.error(f"Failed to check approval decision: {e}")

        return None


# Convenience decorator for agents
def requires_approval(
    category: ApprovalCategory,
    urgency: ApprovalUrgency = ApprovalUrgency.STANDARD,
    description: str = "Action requires approval",
):
    """
    Decorator to mark agent methods that require approval.

    Usage:
        @requires_approval(ApprovalCategory.STRATEGIC, ApprovalUrgency.SAME_DAY)
        async def change_college_list(self, profile_id, changes):
            ...
    """
    def decorator(func):
        func._approval_required = True
        func._approval_category = category
        func._approval_urgency = urgency
        func._approval_description = description
        return func
    return decorator
