"""
Pattern B1: Working Memory Manager
v5.4 True Autonomous Agents

3P: Redis for ephemeral storage
USP: Coaching signal detection
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import json
import uuid

from context.types import (
    WorkingMemory,
    ConversationTurn,
    ConversationRole,
    DetectedSignal,
)

logger = logging.getLogger(__name__)


# Signal detection patterns (USP)
STRESS_INDICATORS = [
    "overwhelmed", "stressed", "anxious", "worried", "scared",
    "too much", "can't handle", "impossible", "give up",
    "don't know what to do", "falling behind", "deadline",
]

CONFUSION_INDICATORS = [
    "don't understand", "confused", "what do you mean",
    "not sure", "unclear", "lost", "help me understand",
]

EXCITEMENT_INDICATORS = [
    "excited", "amazing", "awesome", "can't wait", "love it",
    "perfect", "great news", "thrilled",
]

FRUSTRATION_INDICATORS = [
    "frustrated", "annoying", "hate this", "stupid", "pointless",
    "waste of time", "not working", "broken",
]


class WorkingMemoryManager:
    """
    Manages working memory for current session.

    Pattern B1: Working Memory (3P: Redis)

    This is critical because:
    - Agents need conversation context
    - Coaching requires detecting student emotional state
    - Session state enables multi-turn reasoning
    """

    def __init__(self, redis_client=None):
        """
        Initialize working memory manager.

        Args:
            redis_client: Optional Redis client for persistence
        """
        self.redis = redis_client
        self._memories: Dict[str, WorkingMemory] = {}
        self._session_ttl = 3600  # 1 hour session timeout

    async def get_or_create(
        self,
        session_id: str,
        profile_id: str,
    ) -> WorkingMemory:
        """
        Get existing working memory or create new one.

        Args:
            session_id: Current session ID
            profile_id: Student profile ID

        Returns:
            WorkingMemory instance
        """
        # Try Redis first
        if self.redis:
            cached = await self._load_from_redis(session_id)
            if cached:
                return cached

        # Try local cache
        if session_id in self._memories:
            return self._memories[session_id]

        # Create new
        memory = WorkingMemory(
            session_id=session_id,
            profile_id=profile_id,
        )

        self._memories[session_id] = memory

        if self.redis:
            await self._save_to_redis(memory)

        logger.info(f"Created new working memory for session {session_id}")
        return memory

    async def add_turn(
        self,
        session_id: str,
        role: ConversationRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkingMemory:
        """
        Add a conversation turn to working memory.

        Args:
            session_id: Session to update
            role: Who said it (user/assistant/system)
            content: What was said
            metadata: Optional additional data

        Returns:
            Updated WorkingMemory
        """
        memory = self._memories.get(session_id)
        if not memory:
            raise ValueError(f"Session {session_id} not found")

        turn = ConversationTurn(
            role=role,
            content=content,
            metadata=metadata or {},
        )

        memory.conversation_buffer.append(turn)

        # Trim buffer if too long
        if len(memory.conversation_buffer) > memory.max_buffer_size:
            memory.conversation_buffer = memory.conversation_buffer[-memory.max_buffer_size:]

        # Detect signals from user messages (USP)
        if role == ConversationRole.USER:
            await self._detect_signals(memory, content)

        # Save to Redis
        if self.redis:
            await self._save_to_redis(memory)

        return memory

    async def _detect_signals(
        self,
        memory: WorkingMemory,
        content: str,
    ) -> None:
        """
        Detect coaching-relevant signals from student message.

        USP: This is our coaching intelligence - detecting emotional state.
        """
        content_lower = content.lower()
        signals_detected: List[DetectedSignal] = []

        # Check for stress
        stress_score = self._calculate_indicator_score(content_lower, STRESS_INDICATORS)
        if stress_score > 0:
            signals_detected.append(DetectedSignal(
                signal_type="stress",
                confidence=min(stress_score, 1.0),
                evidence=self._find_evidence(content_lower, STRESS_INDICATORS),
            ))

        # Check for confusion
        confusion_score = self._calculate_indicator_score(content_lower, CONFUSION_INDICATORS)
        if confusion_score > 0:
            signals_detected.append(DetectedSignal(
                signal_type="confusion",
                confidence=min(confusion_score, 1.0),
                evidence=self._find_evidence(content_lower, CONFUSION_INDICATORS),
            ))

        # Check for excitement
        excitement_score = self._calculate_indicator_score(content_lower, EXCITEMENT_INDICATORS)
        if excitement_score > 0:
            signals_detected.append(DetectedSignal(
                signal_type="excitement",
                confidence=min(excitement_score, 1.0),
                evidence=self._find_evidence(content_lower, EXCITEMENT_INDICATORS),
            ))

        # Check for frustration
        frustration_score = self._calculate_indicator_score(content_lower, FRUSTRATION_INDICATORS)
        if frustration_score > 0:
            signals_detected.append(DetectedSignal(
                signal_type="frustration",
                confidence=min(frustration_score, 1.0),
                evidence=self._find_evidence(content_lower, FRUSTRATION_INDICATORS),
            ))

        # Update memory with detected signals
        memory.recent_signals.extend(signals_detected)

        # Keep only recent signals (last 10)
        memory.recent_signals = memory.recent_signals[-10:]

        # Update overall sentiment based on signals
        memory.detected_sentiment = self._calculate_overall_sentiment(signals_detected)

        # Update engagement level
        memory.engagement_level = self._estimate_engagement(memory)

        if signals_detected:
            logger.info(
                f"Detected signals in session {memory.session_id}: "
                f"{[s.signal_type for s in signals_detected]}"
            )

    def _calculate_indicator_score(
        self,
        content: str,
        indicators: List[str],
    ) -> float:
        """Calculate how strongly content matches indicators."""
        matches = sum(1 for ind in indicators if ind in content)
        if matches == 0:
            return 0.0
        # Scale: 1 match = 0.3, 2 = 0.5, 3+ = 0.7+
        return min(0.3 + (matches - 1) * 0.2, 1.0)

    def _find_evidence(
        self,
        content: str,
        indicators: List[str],
    ) -> str:
        """Find the first matching indicator as evidence."""
        for ind in indicators:
            if ind in content:
                return ind
        return ""

    def _calculate_overall_sentiment(
        self,
        signals: List[DetectedSignal],
    ) -> str:
        """Calculate overall sentiment from signals."""
        if not signals:
            return "neutral"

        # Priority: stress/frustration > confusion > excitement > neutral
        for signal in signals:
            if signal.signal_type in ["stress", "frustration"]:
                return "stressed"
            if signal.signal_type == "confusion":
                return "confused"
            if signal.signal_type == "excitement":
                return "positive"

        return "neutral"

    def _estimate_engagement(self, memory: WorkingMemory) -> float:
        """
        Estimate student engagement level.

        USP: Engagement tracking for coaching adaptation.
        """
        # Factors that increase engagement
        engagement = 0.5  # Base

        # More conversation = more engagement
        turn_count = len(memory.conversation_buffer)
        if turn_count > 5:
            engagement += 0.1
        if turn_count > 10:
            engagement += 0.1

        # Excitement increases engagement
        excitement_signals = [s for s in memory.recent_signals if s.signal_type == "excitement"]
        if excitement_signals:
            engagement += 0.2

        # Frustration/stress decreases engagement
        negative_signals = [
            s for s in memory.recent_signals
            if s.signal_type in ["frustration", "stress"]
        ]
        if negative_signals:
            engagement -= 0.2

        return max(0.0, min(1.0, engagement))

    def set_current_task(
        self,
        session_id: str,
        task_id: str,
    ) -> None:
        """Set the current task for this session."""
        memory = self._memories.get(session_id)
        if memory:
            memory.current_task = task_id

    def set_current_agent(
        self,
        session_id: str,
        agent_name: str,
    ) -> None:
        """Set the current agent for this session."""
        memory = self._memories.get(session_id)
        if memory:
            memory.current_agent = agent_name

    def add_fact(
        self,
        session_id: str,
        fact: str,
    ) -> None:
        """
        Add a fact learned during this session.

        USP: Facts persist for the session and inform future responses.
        """
        memory = self._memories.get(session_id)
        if memory and fact not in memory.session_facts:
            memory.session_facts.append(fact)
            logger.debug(f"Session {session_id} learned: {fact}")

    def get_recent_context(
        self,
        session_id: str,
        max_turns: int = 5,
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation context for LLM.

        Args:
            session_id: Session to get context from
            max_turns: Maximum turns to include

        Returns:
            List of {role, content} dicts
        """
        memory = self._memories.get(session_id)
        if not memory:
            return []

        recent = memory.conversation_buffer[-max_turns:]
        return [
            {"role": turn.role.value, "content": turn.content}
            for turn in recent
        ]

    def update_scratchpad(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> None:
        """Update agent scratchpad with intermediate results."""
        memory = self._memories.get(session_id)
        if memory:
            memory.scratchpad[key] = value

    def get_scratchpad(
        self,
        session_id: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get value from agent scratchpad."""
        memory = self._memories.get(session_id)
        if memory:
            return memory.scratchpad.get(key, default)
        return default

    async def _load_from_redis(self, session_id: str) -> Optional[WorkingMemory]:
        """Load working memory from Redis."""
        try:
            data = await self.redis.get(f"memory:{session_id}")
            if data:
                return WorkingMemory.model_validate_json(data)
            return None
        except Exception as e:
            logger.error(f"Error loading from Redis: {e}")
            return None

    async def _save_to_redis(self, memory: WorkingMemory) -> None:
        """Save working memory to Redis."""
        try:
            await self.redis.set(
                f"memory:{memory.session_id}",
                memory.model_dump_json(),
                ex=self._session_ttl,
            )
        except Exception as e:
            logger.error(f"Error saving to Redis: {e}")

    async def clear_session(self, session_id: str) -> None:
        """Clear working memory for a session."""
        self._memories.pop(session_id, None)
        if self.redis:
            await self.redis.delete(f"memory:{session_id}")
        logger.info(f"Cleared working memory for session {session_id}")


def create_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


# Convenience functions
async def get_working_memory(
    redis_client,
    session_id: str,
    profile_id: str,
) -> WorkingMemory:
    """Quick helper to get working memory."""
    manager = WorkingMemoryManager(redis_client)
    return await manager.get_or_create(session_id, profile_id)
