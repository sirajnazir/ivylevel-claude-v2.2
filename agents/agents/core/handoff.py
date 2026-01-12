# agents/agents/core/handoff.py
"""
IvyQuest v13.2 - Agent Handoff Protocol

This module implements state transfer between agents for multi-agent
workflows. When Agent A needs Agent B to continue a task, it creates
a handoff containing all context B needs to work effectively.

Handoffs are stored in Redis with a 24-hour TTL and include:
- Context from the originating agent
- Task description and reason for handoff
- Profile snapshot at time of handoff
- Decisions already made
- Pending actions
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentHandoff:
    """
    State transfer between agents for multi-agent workflows.
    
    When Agent A needs Agent B to continue a task, it creates a handoff
    containing all context B needs to work effectively.
    
    Example workflow:
        AssessmentAgent completes → creates handoff to GamePlanAgent
        GamePlanAgent receives handoff → has full profile context
    """
    from_agent: str
    to_agent: str
    profile_id: str
    timestamp: datetime

    # What Agent A knows
    context: Dict[str, Any]

    # What Agent B should do
    task: str
    reason: str

    # Current profile state
    profile_snapshot: Dict[str, Any] = field(default_factory=dict)

    # Decisions already made
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)

    # Actions pending
    pending_actions: List[Dict[str, Any]] = field(default_factory=list)

    # Priority/urgency
    priority: str = "normal"  # low, normal, high, urgent

    # Expiry (handoffs expire after 24h by default)
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        """Set expiry if not provided."""
        if self.expires_at is None:
            self.expires_at = self.timestamp + timedelta(hours=24)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "profile_id": self.profile_id,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "task": self.task,
            "reason": self.reason,
            "profile_snapshot": self.profile_snapshot,
            "decisions_made": self.decisions_made,
            "pending_actions": self.pending_actions,
            "priority": self.priority,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentHandoff":
        """Deserialize from storage."""
        return cls(
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            profile_id=data["profile_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=data["context"],
            task=data["task"],
            reason=data["reason"],
            profile_snapshot=data.get("profile_snapshot", {}),
            decisions_made=data.get("decisions_made", []),
            pending_actions=data.get("pending_actions", []),
            priority=data.get("priority", "normal"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
        )

    def is_expired(self) -> bool:
        """Check if handoff has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def time_until_expiry(self) -> Optional[timedelta]:
        """Get time remaining until expiry."""
        if self.expires_at is None:
            return None
        remaining = self.expires_at - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def add_decision(self, decision: str, rationale: str, confidence: float) -> None:
        """Add a decision to the handoff."""
        self.decisions_made.append({
            "decision": decision,
            "rationale": rationale,
            "confidence": confidence,
            "made_at": datetime.utcnow().isoformat(),
        })

    def add_pending_action(self, action: str, priority: str = "normal") -> None:
        """Add a pending action to the handoff."""
        self.pending_actions.append({
            "action": action,
            "priority": priority,
            "added_at": datetime.utcnow().isoformat(),
        })

    def __repr__(self) -> str:
        return (
            f"AgentHandoff({self.from_agent} -> {self.to_agent}, "
            f"task='{self.task[:30]}...', "
            f"expired={self.is_expired()})"
        )


class HandoffManager:
    """
    Manages agent handoffs via Redis short-term storage.
    
    Handoffs are stored with a 24-hour TTL and keyed by:
    handoff:{profile_id}:{from_agent}:{to_agent}
    
    Usage:
        manager = HandoffManager(redis_client)
        
        # Create handoff
        handoff = await manager.create_handoff(
            from_agent="assessment",
            to_agent="gameplan",
            profile_id="abc123",
            context={"archetype": "DoubleDown"},
            task="Create game plan based on assessment",
            reason="Assessment complete",
        )
        
        # Retrieve handoff
        handoff = await manager.get_handoff("abc123", "gameplan")
        
        # Acknowledge (delete) handoff
        await manager.acknowledge_handoff("abc123", "assessment", "gameplan")
    """

    def __init__(self, redis_client):
        """
        Initialize HandoffManager.
        
        Args:
            redis_client: Async Redis client
        """
        self.redis = redis_client
        self.default_ttl = 86400  # 24 hours in seconds

    async def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        profile_id: str,
        context: Dict[str, Any],
        task: str,
        reason: str,
        profile_snapshot: Dict[str, Any] = None,
        decisions_made: List[Dict[str, Any]] = None,
        pending_actions: List[Dict[str, Any]] = None,
        priority: str = "normal",
    ) -> AgentHandoff:
        """
        Create and store a handoff.
        
        Args:
            from_agent: Agent creating the handoff
            to_agent: Agent receiving the handoff
            profile_id: Profile ID this handoff is for
            context: Context dict to pass to receiving agent
            task: Description of what the receiving agent should do
            reason: Why the handoff is happening
            profile_snapshot: Optional snapshot of profile at handoff time
            decisions_made: Optional list of decisions already made
            pending_actions: Optional list of pending actions
            priority: Priority level (low/normal/high/urgent)
            
        Returns:
            The created AgentHandoff
        """
        handoff = AgentHandoff(
            from_agent=from_agent,
            to_agent=to_agent,
            profile_id=profile_id,
            timestamp=datetime.utcnow(),
            context=context,
            task=task,
            reason=reason,
            profile_snapshot=profile_snapshot or {},
            decisions_made=decisions_made or [],
            pending_actions=pending_actions or [],
            priority=priority,
        )

        # Store in Redis
        key = f"handoff:{profile_id}:{from_agent}:{to_agent}"
        await self.redis.setex(
            key,
            self.default_ttl,
            json.dumps(handoff.to_dict()),
        )

        logger.info(
            f"Created handoff: {from_agent} -> {to_agent} "
            f"for profile {profile_id} (task: {task[:50]}...)"
        )

        return handoff

    async def get_handoff(
        self,
        profile_id: str,
        to_agent: str,
        from_agent: Optional[str] = None,
    ) -> Optional[AgentHandoff]:
        """
        Get the latest handoff to an agent.
        
        Args:
            profile_id: Profile ID
            to_agent: Agent receiving the handoff
            from_agent: Optional specific source agent
            
        Returns:
            AgentHandoff if found and not expired, else None
        """
        if from_agent:
            # Get specific handoff
            key = f"handoff:{profile_id}:{from_agent}:{to_agent}"
            data = await self.redis.get(key)
            if data:
                handoff = AgentHandoff.from_dict(json.loads(data))
                if not handoff.is_expired():
                    return handoff
            return None

        # Scan for any handoff to this agent
        pattern = f"handoff:{profile_id}:*:{to_agent}"
        cursor = 0
        latest = None

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    handoff = AgentHandoff.from_dict(json.loads(data))
                    if not handoff.is_expired():
                        if latest is None or handoff.timestamp > latest.timestamp:
                            latest = handoff
            if cursor == 0:
                break

        return latest

    async def acknowledge_handoff(
        self,
        profile_id: str,
        from_agent: str,
        to_agent: str,
    ) -> bool:
        """
        Mark handoff as received (delete from Redis).
        
        Call this after the receiving agent has processed the handoff.
        
        Args:
            profile_id: Profile ID
            from_agent: Agent that created the handoff
            to_agent: Agent that received the handoff
            
        Returns:
            True if handoff was deleted, False if not found
        """
        key = f"handoff:{profile_id}:{from_agent}:{to_agent}"
        result = await self.redis.delete(key)
        
        if result > 0:
            logger.info(
                f"Acknowledged handoff: {from_agent} -> {to_agent} "
                f"for profile {profile_id}"
            )
            return True
        return False

    async def get_pending_handoffs(
        self,
        profile_id: str,
    ) -> List[AgentHandoff]:
        """
        Get all pending handoffs for a profile.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            List of pending handoffs, sorted by timestamp (newest first)
        """
        pattern = f"handoff:{profile_id}:*:*"
        cursor = 0
        handoffs = []

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    handoff = AgentHandoff.from_dict(json.loads(data))
                    if not handoff.is_expired():
                        handoffs.append(handoff)
            if cursor == 0:
                break

        return sorted(handoffs, key=lambda h: h.timestamp, reverse=True)

    async def get_handoffs_from_agent(
        self,
        profile_id: str,
        from_agent: str,
    ) -> List[AgentHandoff]:
        """
        Get all pending handoffs from a specific agent.
        
        Args:
            profile_id: Profile ID
            from_agent: Agent that created the handoffs
            
        Returns:
            List of pending handoffs from that agent
        """
        pattern = f"handoff:{profile_id}:{from_agent}:*"
        cursor = 0
        handoffs = []

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    handoff = AgentHandoff.from_dict(json.loads(data))
                    if not handoff.is_expired():
                        handoffs.append(handoff)
            if cursor == 0:
                break

        return handoffs

    async def cleanup_expired(self, profile_id: str) -> int:
        """
        Clean up expired handoffs for a profile.
        
        Note: Redis TTL should handle this automatically, but this
        can be called for explicit cleanup.
        
        Returns:
            Number of expired handoffs cleaned up
        """
        pattern = f"handoff:{profile_id}:*:*"
        cursor = 0
        cleaned = 0

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    handoff = AgentHandoff.from_dict(json.loads(data))
                    if handoff.is_expired():
                        await self.redis.delete(key)
                        cleaned += 1
            if cursor == 0:
                break

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired handoffs for profile {profile_id}")

        return cleaned
