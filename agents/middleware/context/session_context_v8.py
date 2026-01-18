"""
C1: Session Context Pattern - Implementation

Track current interaction state within a session.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class SessionMessage(BaseModel):
    """A single message in the session."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionContext(BaseModel):
    """
    Session-level context for tracking current interaction state.

    Pattern C1: Session Context

    GUARDRAILS:
    - NEW class - does not modify existing context
    - Optional Redis backend for clustering
    - Falls back to in-memory if Redis unavailable
    """

    session_id: str
    profile_id: str

    # Session state
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0

    # Current topic tracking
    current_topic: Optional[str] = None
    topic_history: List[str] = Field(default_factory=list)

    # Active agents in session
    active_agent: Optional[str] = None
    agent_switches: int = 0

    # Session messages (sliding window)
    messages: List[SessionMessage] = Field(default_factory=list)
    max_messages: int = 50

    # Context flags
    requires_clarification: bool = False
    pending_action: Optional[str] = None

    # Accumulated context
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    inferred_intent: Optional[str] = None


class SessionContextManager:
    """
    Manages session context with optional Redis backend.

    GUARDRAILS:
    - NEW class - does not modify existing managers
    - Graceful degradation without Redis
    """

    def __init__(
        self,
        redis_client=None,
        supabase_client=None,
        ttl_seconds: int = 3600,
    ):
        """
        Initialize session context manager.

        Args:
            redis_client: Optional Redis client for distributed caching
            supabase_client: For persisting session history
            ttl_seconds: Session TTL in seconds (default 1 hour)
        """
        self.redis = redis_client
        self.supabase = supabase_client
        self.ttl = ttl_seconds
        self._local_cache: Dict[str, SessionContext] = {}

    def _cache_key(self, session_id: str) -> str:
        """Generate cache key for session."""
        return f"session_context:{session_id}"

    async def get_session(
        self,
        session_id: str,
        profile_id: str,
    ) -> SessionContext:
        """
        Get or create session context.

        Args:
            session_id: Session identifier
            profile_id: Student profile ID

        Returns:
            SessionContext for the session
        """
        # Try Redis first
        if self.redis:
            try:
                cached = await self.redis.get(self._cache_key(session_id))
                if cached:
                    return SessionContext.model_validate_json(cached)
            except Exception as e:
                logger.warning(f"Redis get failed, using local: {e}")

        # Try local cache
        if session_id in self._local_cache:
            return self._local_cache[session_id]

        # Create new session
        session = SessionContext(
            session_id=session_id,
            profile_id=profile_id,
        )

        await self._save_session(session)
        return session

    async def _save_session(self, session: SessionContext) -> None:
        """Save session to cache(s)."""
        self._local_cache[session.session_id] = session

        if self.redis:
            try:
                await self.redis.setex(
                    self._cache_key(session.session_id),
                    self.ttl,
                    session.model_dump_json(),
                )
            except Exception as e:
                logger.warning(f"Redis save failed: {e}")

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[SessionContext]:
        """
        Add message to session context.

        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata

        Returns:
            Updated SessionContext or None if session not found
        """
        session = self._local_cache.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None

        message = SessionMessage(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        session.messages.append(message)

        # Enforce sliding window
        if len(session.messages) > session.max_messages:
            session.messages = session.messages[-session.max_messages:]

        session.message_count += 1
        session.last_activity = datetime.now(timezone.utc)

        await self._save_session(session)
        return session

    async def update_topic(
        self,
        session_id: str,
        topic: str,
    ) -> Optional[SessionContext]:
        """
        Update current conversation topic.

        Args:
            session_id: Session identifier
            topic: New topic

        Returns:
            Updated SessionContext or None
        """
        session = self._local_cache.get(session_id)
        if not session:
            return None

        if session.current_topic and session.current_topic != topic:
            session.topic_history.append(session.current_topic)

        session.current_topic = topic
        await self._save_session(session)
        return session

    async def switch_agent(
        self,
        session_id: str,
        agent_name: str,
    ) -> Optional[SessionContext]:
        """
        Track agent switch within session.

        Args:
            session_id: Session identifier
            agent_name: New agent name

        Returns:
            Updated SessionContext or None
        """
        session = self._local_cache.get(session_id)
        if not session:
            return None

        if session.active_agent and session.active_agent != agent_name:
            session.agent_switches += 1

        session.active_agent = agent_name
        await self._save_session(session)
        return session

    async def extract_entity(
        self,
        session_id: str,
        entity_type: str,
        entity_value: Any,
    ) -> Optional[SessionContext]:
        """
        Record extracted entity from conversation.

        Args:
            session_id: Session identifier
            entity_type: Type of entity (e.g., "school", "deadline")
            entity_value: Extracted value

        Returns:
            Updated SessionContext or None
        """
        session = self._local_cache.get(session_id)
        if not session:
            return None

        session.extracted_entities[entity_type] = entity_value
        await self._save_session(session)
        return session

    async def set_pending_action(
        self,
        session_id: str,
        action: Optional[str],
    ) -> Optional[SessionContext]:
        """
        Set or clear pending action for session.

        Args:
            session_id: Session identifier
            action: Action pending, or None to clear

        Returns:
            Updated SessionContext or None
        """
        session = self._local_cache.get(session_id)
        if not session:
            return None

        session.pending_action = action
        await self._save_session(session)
        return session

    async def end_session(
        self,
        session_id: str,
    ) -> None:
        """
        End session and persist to Supabase.

        Args:
            session_id: Session identifier
        """
        session = self._local_cache.get(session_id)
        if not session:
            return

        if self.supabase:
            try:
                self.supabase.table("phase2b_session_history").insert({
                    "session_id": session.session_id,
                    "profile_id": session.profile_id,
                    "started_at": session.started_at.isoformat(),
                    "ended_at": datetime.now(timezone.utc).isoformat(),
                    "message_count": session.message_count,
                    "agent_switches": session.agent_switches,
                    "topics": session.topic_history + (
                        [session.current_topic] if session.current_topic else []
                    ),
                }).execute()
            except Exception as e:
                logger.error(f"Failed to persist session: {e}")

        self._local_cache.pop(session_id, None)

        if self.redis:
            try:
                await self.redis.delete(self._cache_key(session_id))
            except Exception:
                pass

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary of session for context.

        Args:
            session_id: Session identifier

        Returns:
            Session summary dict or None
        """
        session = self._local_cache.get(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "profile_id": session.profile_id,
            "duration_minutes": int(
                (datetime.now(timezone.utc) - session.started_at).total_seconds() / 60
            ),
            "message_count": session.message_count,
            "current_topic": session.current_topic,
            "active_agent": session.active_agent,
            "pending_action": session.pending_action,
            "entities": session.extracted_entities,
        }
