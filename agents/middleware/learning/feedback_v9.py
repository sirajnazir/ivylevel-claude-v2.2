"""
Feedback Loop - Collect and process user feedback.

Pattern: I1
3P: Supabase (storage)
Lines: ~100 (thin wrapper)

Features:
- Collect explicit feedback
- Track implicit signals
- Aggregate feedback scores
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Feedback(BaseModel):
    """A feedback record."""
    feedback_type: str = "explicit"  # explicit, implicit, correction
    sentiment: str = "neutral"  # positive, negative, neutral
    score: float = 0.5  # 0-1 scale
    context: Optional[str] = None
    message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackLoop:
    """
    Collects and processes user feedback.

    Pattern I1: Feedback Loop
    3P: Supabase (storage)

    Thin wrapper - delegates storage to Supabase, aggregation in memory.
    """

    TABLE = "phase3_feedback"

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._initialized = True  # Always available with in-memory fallback
        self._session_feedback: List[Feedback] = []

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def record(
        self,
        profile_id: str,
        feedback_type: str = "explicit",
        sentiment: str = "neutral",
        score: float = 0.5,
        context: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """Record feedback."""
        feedback = Feedback(
            feedback_type=feedback_type,
            sentiment=sentiment,
            score=max(0.0, min(1.0, score)),
            context=context,
            message=message,
            metadata=metadata or {},
        )

        # Store in session
        self._session_feedback.append(feedback)

        # Persist to Supabase if available
        if self.supabase:
            try:
                self.supabase.table(self.TABLE).insert({
                    "profile_id": profile_id,
                    "feedback_type": feedback_type,
                    "sentiment": sentiment,
                    "score": feedback.score,
                    "context": context,
                    "message": message,
                    "metadata": metadata or {},
                    "created_at": feedback.created_at.isoformat(),
                }).execute()
            except Exception as e:
                logger.warning(f"Failed to persist feedback: {e}")

        return feedback

    async def record_positive(
        self,
        profile_id: str,
        context: Optional[str] = None,
        message: Optional[str] = None,
    ) -> Feedback:
        """Record positive feedback."""
        return await self.record(
            profile_id=profile_id,
            feedback_type="explicit",
            sentiment="positive",
            score=0.9,
            context=context,
            message=message,
        )

    async def record_negative(
        self,
        profile_id: str,
        context: Optional[str] = None,
        message: Optional[str] = None,
    ) -> Feedback:
        """Record negative feedback."""
        return await self.record(
            profile_id=profile_id,
            feedback_type="explicit",
            sentiment="negative",
            score=0.1,
            context=context,
            message=message,
        )

    async def record_implicit(
        self,
        profile_id: str,
        signal_type: str,
        score: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Feedback:
        """Record implicit feedback signal."""
        sentiment = "positive" if score > 0.5 else "negative" if score < 0.5 else "neutral"

        return await self.record(
            profile_id=profile_id,
            feedback_type="implicit",
            sentiment=sentiment,
            score=score,
            metadata={"signal_type": signal_type, **(metadata or {})},
        )

    def get_session_score(self) -> float:
        """Get average score for current session."""
        if not self._session_feedback:
            return 0.5

        scores = [f.score for f in self._session_feedback]
        return sum(scores) / len(scores)

    def get_session_sentiment(self) -> str:
        """Get overall sentiment for current session."""
        score = self.get_session_score()
        if score > 0.6:
            return "positive"
        elif score < 0.4:
            return "negative"
        return "neutral"

    def get_feedback_count(self) -> Dict[str, int]:
        """Get feedback counts by type."""
        counts = {"explicit": 0, "implicit": 0, "correction": 0}
        for f in self._session_feedback:
            if f.feedback_type in counts:
                counts[f.feedback_type] += 1
        return counts

    def clear_session(self) -> None:
        """Clear session feedback."""
        self._session_feedback.clear()
