"""
Human-in-the-Loop (HITL) Workflow Manager for IvyQuest v13.0

Enables human review and approval for high-stakes agent decisions.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Status of a HITL workflow request."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"


@dataclass
class HITLRequest:
    """
    A request for human review of an agent action.

    Attributes:
        id: Unique request ID
        agent_id: Agent requesting review
        profile_id: Associated student profile
        action_type: Type of action being reviewed
        proposed_action: The action the agent wants to take
        confidence: Agent's confidence in the action (0-1)
        reasoning: Agent's reasoning for the action
        status: Current workflow status
        reviewer_id: ID of human reviewer (if reviewed)
        review_notes: Notes from reviewer
        modified_action: Modified action (if status is MODIFIED)
        created_at: When request was created
        reviewed_at: When request was reviewed
    """
    id: str
    agent_id: str
    profile_id: str
    action_type: str
    proposed_action: dict
    confidence: float
    reasoning: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    reviewer_id: Optional[str] = None
    review_notes: Optional[str] = None
    modified_action: Optional[dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to serializable dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "profile_id": self.profile_id,
            "action_type": self.action_type,
            "proposed_action": self.proposed_action,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "status": self.status.value,
            "reviewer_id": self.reviewer_id,
            "review_notes": self.review_notes,
            "modified_action": self.modified_action,
            "created_at": self.created_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HITLRequest":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            agent_id=data["agent_id"],
            profile_id=data["profile_id"],
            action_type=data["action_type"],
            proposed_action=data["proposed_action"],
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            status=WorkflowStatus(data.get("status", "pending")),
            reviewer_id=data.get("reviewer_id"),
            review_notes=data.get("review_notes"),
            modified_action=data.get("modified_action"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            reviewed_at=datetime.fromisoformat(data["reviewed_at"]) if data.get("reviewed_at") else None,
        )


class HITLWorkflowManager:
    """
    Manages human-in-the-loop workflows for agent actions.

    High-stakes decisions require human approval before execution.
    The manager:
    - Creates review requests
    - Routes to appropriate reviewers
    - Tracks review status
    - Enforces auto-approval thresholds
    """

    # Default confidence thresholds for auto-approval
    REVIEW_THRESHOLDS = {
        "narrative.brand_statement": 0.85,
        "awards.portfolio_change": 0.80,
        "awards.application_submit": 0.90,
        "crisis.major_pivot": 0.70,
        "opportunity.expensive_program": 0.95,
        "opportunity.program_redirect": 0.80,
        "default": 0.85,
    }

    def __init__(
        self,
        supabase_client=None,
        notification_service=None,
        event_bus=None,
    ):
        self.supabase = supabase_client
        self.notifications = notification_service
        self.event_bus = event_bus

        # In-memory store for requests (fallback if no Supabase)
        self._requests: dict[str, HITLRequest] = {}

    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return f"hitl_{uuid.uuid4().hex[:12]}"

    def _get_threshold(self, action_type: str) -> float:
        """Get confidence threshold for an action type."""
        return self.REVIEW_THRESHOLDS.get(
            action_type,
            self.REVIEW_THRESHOLDS["default"]
        )

    async def request_review(
        self,
        agent_id: str,
        profile_id: str,
        action_type: str,
        proposed_action: dict,
        confidence: float,
        reasoning: str,
    ) -> HITLRequest:
        """
        Create a HITL review request.

        If confidence exceeds threshold, auto-approves.
        Otherwise, creates a pending review request.

        Args:
            agent_id: Agent requesting review
            profile_id: Student profile ID
            action_type: Type of action
            proposed_action: Action to be reviewed
            confidence: Agent's confidence (0-1)
            reasoning: Why the agent wants to take this action

        Returns:
            HITLRequest: The created request (may be auto-approved)
        """
        threshold = self._get_threshold(action_type)

        request = HITLRequest(
            id=self._generate_request_id(),
            agent_id=agent_id,
            profile_id=profile_id,
            action_type=action_type,
            proposed_action=proposed_action,
            confidence=confidence,
            reasoning=reasoning,
        )

        # Auto-approve if confidence exceeds threshold
        if confidence >= threshold:
            request.status = WorkflowStatus.APPROVED
            request.review_notes = f"Auto-approved: confidence {confidence:.2f} >= threshold {threshold:.2f}"
            request.reviewed_at = datetime.utcnow()

            logger.info(f"HITL request {request.id} auto-approved (confidence: {confidence:.2f})")
        else:
            logger.info(f"HITL request {request.id} requires human review (confidence: {confidence:.2f} < {threshold:.2f})")

            # Send notification if service available
            if self.notifications:
                await self._send_review_notification(request)

            # Publish event if bus available
            if self.event_bus:
                from .events import AgentEvent, EventTypes
                await self.event_bus.publish(AgentEvent(
                    source_agent=agent_id,
                    event_type=EventTypes.HITL_REVIEW_REQUESTED,
                    payload=request.to_dict(),
                    profile_id=profile_id,
                ))

        # Store request
        await self._store_request(request)

        return request

    async def _store_request(self, request: HITLRequest) -> None:
        """Store request in database or memory."""
        self._requests[request.id] = request

        if self.supabase:
            try:
                await self.supabase.table("hitl_requests").upsert(
                    request.to_dict()
                ).execute()
            except Exception as e:
                logger.error(f"Failed to store HITL request: {e}")

    async def _send_review_notification(self, request: HITLRequest) -> None:
        """Send notification about pending review."""
        if not self.notifications:
            return

        try:
            await self.notifications.send(
                type="hitl_review_needed",
                profile_id=request.profile_id,
                data={
                    "request_id": request.id,
                    "action_type": request.action_type,
                    "agent_id": request.agent_id,
                    "confidence": request.confidence,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to send HITL notification: {e}")

    async def submit_review(
        self,
        request_id: str,
        reviewer_id: str,
        decision: WorkflowStatus,
        notes: str | None = None,
        modified_action: dict | None = None,
    ) -> HITLRequest:
        """
        Submit a human review decision.

        Args:
            request_id: ID of the request to review
            reviewer_id: ID of the human reviewer
            decision: Approval decision
            notes: Optional review notes
            modified_action: Modified action (required if decision is MODIFIED)

        Returns:
            HITLRequest: Updated request

        Raises:
            ValueError: If request not found or invalid decision
        """
        request = await self.get_request(request_id)
        if not request:
            raise ValueError(f"HITL request not found: {request_id}")

        if request.status not in [WorkflowStatus.PENDING, WorkflowStatus.IN_REVIEW]:
            raise ValueError(f"Request already resolved: {request.status}")

        # Validate MODIFIED decision
        if decision == WorkflowStatus.MODIFIED and not modified_action:
            raise ValueError("Modified action required for MODIFIED decision")

        # Update request
        request.status = decision
        request.reviewer_id = reviewer_id
        request.review_notes = notes
        request.reviewed_at = datetime.utcnow()

        if modified_action:
            request.modified_action = modified_action

        # Store updated request
        await self._store_request(request)

        # Publish event
        if self.event_bus:
            from .events import AgentEvent, EventTypes
            await self.event_bus.publish(AgentEvent(
                source_agent="hitl_manager",
                event_type=EventTypes.HITL_REVIEW_COMPLETE,
                payload=request.to_dict(),
                profile_id=request.profile_id,
            ))

        logger.info(f"HITL request {request_id} reviewed: {decision.value}")

        return request

    async def get_request(self, request_id: str) -> HITLRequest | None:
        """Get a HITL request by ID."""
        # Check memory first
        if request_id in self._requests:
            return self._requests[request_id]

        # Check database
        if self.supabase:
            try:
                result = await self.supabase.table("hitl_requests")\
                    .select("*")\
                    .eq("id", request_id)\
                    .single()\
                    .execute()

                if result.data:
                    request = HITLRequest.from_dict(result.data)
                    self._requests[request_id] = request
                    return request
            except Exception as e:
                logger.warning(f"Failed to fetch HITL request: {e}")

        return None

    async def get_pending_requests(
        self,
        profile_id: str | None = None,
        agent_id: str | None = None,
        limit: int = 50,
    ) -> list[HITLRequest]:
        """
        Get pending HITL requests.

        Args:
            profile_id: Filter by profile
            agent_id: Filter by agent
            limit: Max requests to return

        Returns:
            list[HITLRequest]: Pending requests
        """
        if self.supabase:
            try:
                query = self.supabase.table("hitl_requests")\
                    .select("*")\
                    .eq("status", WorkflowStatus.PENDING.value)\
                    .order("created_at", desc=True)\
                    .limit(limit)

                if profile_id:
                    query = query.eq("profile_id", profile_id)
                if agent_id:
                    query = query.eq("agent_id", agent_id)

                result = await query.execute()

                return [HITLRequest.from_dict(r) for r in result.data or []]
            except Exception as e:
                logger.warning(f"Failed to fetch pending requests: {e}")

        # Fallback to memory
        pending = [
            r for r in self._requests.values()
            if r.status == WorkflowStatus.PENDING
        ]

        if profile_id:
            pending = [r for r in pending if r.profile_id == profile_id]
        if agent_id:
            pending = [r for r in pending if r.agent_id == agent_id]

        return sorted(pending, key=lambda r: r.created_at, reverse=True)[:limit]

    async def get_request_history(
        self,
        profile_id: str,
        limit: int = 100,
    ) -> list[HITLRequest]:
        """Get HITL request history for a profile."""
        if self.supabase:
            try:
                result = await self.supabase.table("hitl_requests")\
                    .select("*")\
                    .eq("profile_id", profile_id)\
                    .order("created_at", desc=True)\
                    .limit(limit)\
                    .execute()

                return [HITLRequest.from_dict(r) for r in result.data or []]
            except Exception as e:
                logger.warning(f"Failed to fetch request history: {e}")

        # Fallback to memory
        history = [
            r for r in self._requests.values()
            if r.profile_id == profile_id
        ]
        return sorted(history, key=lambda r: r.created_at, reverse=True)[:limit]

    async def mark_in_review(
        self,
        request_id: str,
        reviewer_id: str,
    ) -> HITLRequest:
        """
        Mark a request as being actively reviewed.

        Prevents multiple reviewers from working on the same request.
        """
        request = await self.get_request(request_id)
        if not request:
            raise ValueError(f"HITL request not found: {request_id}")

        if request.status != WorkflowStatus.PENDING:
            raise ValueError(f"Request not pending: {request.status}")

        request.status = WorkflowStatus.IN_REVIEW
        request.reviewer_id = reviewer_id

        await self._store_request(request)
        return request

    def get_approval_rate(
        self,
        agent_id: str | None = None,
    ) -> dict:
        """
        Get approval statistics.

        Returns:
            dict: Approval rate statistics
        """
        requests = list(self._requests.values())

        if agent_id:
            requests = [r for r in requests if r.agent_id == agent_id]

        total = len(requests)
        if total == 0:
            return {"total": 0, "approval_rate": 0, "auto_approved": 0}

        approved = sum(1 for r in requests if r.status == WorkflowStatus.APPROVED)
        auto_approved = sum(
            1 for r in requests
            if r.status == WorkflowStatus.APPROVED
            and r.review_notes and "Auto-approved" in r.review_notes
        )
        rejected = sum(1 for r in requests if r.status == WorkflowStatus.REJECTED)
        modified = sum(1 for r in requests if r.status == WorkflowStatus.MODIFIED)

        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "modified": modified,
            "pending": total - approved - rejected - modified,
            "auto_approved": auto_approved,
            "approval_rate": approved / total if total > 0 else 0,
        }
