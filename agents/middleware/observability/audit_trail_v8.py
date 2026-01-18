"""
J3: Audit Trail Pattern - Implementation

Complete audit trail for compliance and debugging.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Types of auditable actions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    LOGIN = "login"
    LOGOUT = "logout"


class AuditActorType(str, Enum):
    """Types of actors."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    COACH = "coach"
    ADMIN = "admin"


class AuditEntry(BaseModel):
    """A single audit trail entry."""
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Actor info
    actor_id: str
    actor_type: AuditActorType

    # Action info
    action: AuditAction
    resource_type: str
    resource_id: Optional[str] = None

    # Details
    details: Dict[str, Any] = Field(default_factory=dict)
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None

    # Context
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Outcome
    success: bool = True
    error_message: Optional[str] = None


class AuditTrailManager:
    """
    Manages audit trail for all system actions.

    Pattern J3: Audit Trail

    GUARDRAILS:
    - NEW class - does not modify existing audit
    - Stores to Supabase for persistence
    - Supports queries for compliance
    """

    def __init__(
        self,
        supabase_client=None,
        enable_read_audits: bool = False,
    ):
        """
        Initialize audit trail manager.

        Args:
            supabase_client: For persistence
            enable_read_audits: Whether to audit read operations
        """
        self.supabase = supabase_client
        self.audit_reads = enable_read_audits
        self._buffer: List[AuditEntry] = []
        self._buffer_size = 100

    async def log(
        self,
        actor_id: str,
        actor_type: AuditActorType,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> AuditEntry:
        """
        Log an audit entry.

        Args:
            actor_id: Who performed the action
            actor_type: Type of actor
            action: What action was performed
            resource_type: Type of resource affected
            resource_id: ID of resource
            details: Additional details
            before_state: State before action
            after_state: State after action
            session_id: Session ID if applicable
            success: Whether action succeeded
            error: Error message if failed

        Returns:
            Created AuditEntry
        """
        # Skip read audits if disabled
        if action == AuditAction.READ and not self.audit_reads:
            return None

        entry = AuditEntry(
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            before_state=before_state,
            after_state=after_state,
            session_id=session_id,
            success=success,
            error_message=error,
        )

        # Buffer entry
        self._buffer.append(entry)

        # Flush if buffer full
        if len(self._buffer) >= self._buffer_size:
            await self.flush()

        return entry

    async def log_agent_action(
        self,
        agent_name: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        success: bool = True,
    ) -> AuditEntry:
        """Log an agent action."""
        return await self.log(
            actor_id=agent_name,
            actor_type=AuditActorType.AGENT,
            action=AuditAction.EXECUTE,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"agent_action": action, **(details or {})},
            session_id=session_id,
            success=success,
        )

    async def log_user_action(
        self,
        user_id: str,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> AuditEntry:
        """Log a user action."""
        return await self.log(
            actor_id=user_id,
            actor_type=AuditActorType.USER,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            session_id=session_id,
        )

    async def log_approval(
        self,
        reviewer_id: str,
        reviewer_type: AuditActorType,
        approved: bool,
        resource_type: str,
        resource_id: str,
        reason: Optional[str] = None,
    ) -> AuditEntry:
        """Log an approval decision."""
        return await self.log(
            actor_id=reviewer_id,
            actor_type=reviewer_type,
            action=AuditAction.APPROVE if approved else AuditAction.REJECT,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"reason": reason},
        )

    async def flush(self) -> int:
        """
        Flush buffer to database.

        Returns:
            Number of entries flushed
        """
        if not self._buffer:
            return 0

        entries_to_flush = self._buffer.copy()
        self._buffer.clear()

        if not self.supabase:
            logger.warning("No Supabase client, audit entries not persisted")
            return 0

        try:
            data = [
                {
                    "entry_id": e.entry_id,
                    "timestamp": e.timestamp.isoformat(),
                    "actor_id": e.actor_id,
                    "actor_type": e.actor_type.value,
                    "action": e.action.value,
                    "resource_type": e.resource_type,
                    "resource_id": e.resource_id,
                    "details": e.details,
                    "session_id": e.session_id,
                    "success": e.success,
                    "error_message": e.error_message,
                }
                for e in entries_to_flush
            ]

            self.supabase.table("phase2b_audit_trail").insert(data).execute()
            logger.debug(f"Flushed {len(entries_to_flush)} audit entries")
            return len(entries_to_flush)

        except Exception as e:
            logger.error(f"Failed to flush audit entries: {e}")
            # Re-add to buffer for retry
            self._buffer.extend(entries_to_flush)
            return 0

    async def query(
        self,
        actor_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """
        Query audit trail.

        Args:
            actor_id: Filter by actor
            action: Filter by action
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum entries to return

        Returns:
            List of matching AuditEntries
        """
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("phase2b_audit_trail").select("*")

            if actor_id:
                query = query.eq("actor_id", actor_id)
            if action:
                query = query.eq("action", action.value)
            if resource_type:
                query = query.eq("resource_type", resource_type)
            if resource_id:
                query = query.eq("resource_id", resource_id)
            if start_time:
                query = query.gte("timestamp", start_time.isoformat())
            if end_time:
                query = query.lte("timestamp", end_time.isoformat())

            query = query.order("timestamp", desc=True).limit(limit)

            result = query.execute()

            return [
                AuditEntry(
                    entry_id=r["entry_id"],
                    timestamp=datetime.fromisoformat(r["timestamp"]),
                    actor_id=r["actor_id"],
                    actor_type=AuditActorType(r["actor_type"]),
                    action=AuditAction(r["action"]),
                    resource_type=r["resource_type"],
                    resource_id=r.get("resource_id"),
                    details=r.get("details", {}),
                    session_id=r.get("session_id"),
                    success=r.get("success", True),
                    error_message=r.get("error_message"),
                )
                for r in result.data
            ]

        except Exception as e:
            logger.error(f"Audit query failed: {e}")
            return []

    async def get_actor_history(
        self,
        actor_id: str,
        limit: int = 50,
    ) -> List[AuditEntry]:
        """Get action history for an actor."""
        return await self.query(actor_id=actor_id, limit=limit)

    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50,
    ) -> List[AuditEntry]:
        """Get change history for a resource."""
        return await self.query(
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit,
        )
