"""
Pattern Recognition - Recognize patterns in user behavior.

Pattern: I3
3P: Supabase (storage)
Lines: ~120 (thin wrapper)

Features:
- Detect recurring patterns
- Track pattern frequency
- Predict user needs
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class RecognizedPattern(BaseModel):
    """A recognized behavioral pattern."""
    pattern_type: str  # time_of_day, topic_sequence, question_style, etc.
    pattern_value: str
    frequency: int = 1
    confidence: float = 0.5
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PatternRecognizer:
    """
    Recognizes patterns in user behavior.

    Pattern I3: Pattern Recognition
    3P: Supabase (storage)

    Thin wrapper - tracks patterns in memory, persists to Supabase.
    """

    TABLE = "phase3_recognized_patterns"
    MIN_FREQUENCY_FOR_PATTERN = 3

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._initialized = True
        self._patterns: Dict[str, Dict[str, RecognizedPattern]] = {}  # {type: {value: pattern}}
        self._observations: Dict[str, List[str]] = {}  # {type: [values]}

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def observe(
        self,
        profile_id: str,
        pattern_type: str,
        value: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[RecognizedPattern]:
        """Record an observation and check for patterns."""
        # Track observation
        if pattern_type not in self._observations:
            self._observations[pattern_type] = []
        self._observations[pattern_type].append(value)

        # Limit observations to recent ones
        if len(self._observations[pattern_type]) > 100:
            self._observations[pattern_type] = self._observations[pattern_type][-50:]

        # Check if this forms a pattern
        counter = Counter(self._observations[pattern_type])
        frequency = counter[value]

        if frequency >= self.MIN_FREQUENCY_FOR_PATTERN:
            return await self._record_pattern(
                profile_id=profile_id,
                pattern_type=pattern_type,
                pattern_value=value,
                frequency=frequency,
                metadata=metadata,
            )

        return None

    async def _record_pattern(
        self,
        profile_id: str,
        pattern_type: str,
        pattern_value: str,
        frequency: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RecognizedPattern:
        """Record a recognized pattern."""
        # Calculate confidence based on frequency
        total_observations = len(self._observations.get(pattern_type, []))
        confidence = min(0.95, frequency / total_observations if total_observations > 0 else 0.5)

        pattern = RecognizedPattern(
            pattern_type=pattern_type,
            pattern_value=pattern_value,
            frequency=frequency,
            confidence=confidence,
            metadata=metadata or {},
        )

        # Store pattern
        if pattern_type not in self._patterns:
            self._patterns[pattern_type] = {}
        self._patterns[pattern_type][pattern_value] = pattern

        # Persist to Supabase if available
        if self.supabase:
            try:
                self.supabase.table(self.TABLE).upsert({
                    "profile_id": profile_id,
                    "pattern_type": pattern_type,
                    "pattern_value": pattern_value,
                    "frequency": frequency,
                    "confidence": confidence,
                    "metadata": metadata or {},
                    "last_seen": datetime.utcnow().isoformat(),
                }).execute()
            except Exception as e:
                logger.warning(f"Failed to persist pattern: {e}")

        return pattern

    def get_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_confidence: float = 0.5,
    ) -> List[RecognizedPattern]:
        """Get recognized patterns."""
        patterns = []

        if pattern_type:
            type_patterns = self._patterns.get(pattern_type, {})
            patterns = list(type_patterns.values())
        else:
            for type_patterns in self._patterns.values():
                patterns.extend(type_patterns.values())

        return [p for p in patterns if p.confidence >= min_confidence]

    def get_strongest_pattern(
        self,
        pattern_type: str,
    ) -> Optional[RecognizedPattern]:
        """Get the strongest pattern of a type."""
        type_patterns = self._patterns.get(pattern_type, {})
        if not type_patterns:
            return None

        return max(type_patterns.values(), key=lambda p: p.confidence)

    def predict_next(
        self,
        pattern_type: str,
    ) -> Optional[str]:
        """Predict the most likely next value for a pattern type."""
        pattern = self.get_strongest_pattern(pattern_type)
        if pattern and pattern.confidence >= 0.6:
            return pattern.pattern_value
        return None

    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get a summary of all patterns."""
        summary = {
            "total_pattern_types": len(self._patterns),
            "total_patterns": sum(len(p) for p in self._patterns.values()),
            "by_type": {},
        }

        for pattern_type, patterns in self._patterns.items():
            summary["by_type"][pattern_type] = {
                "count": len(patterns),
                "strongest": max(patterns.values(), key=lambda p: p.confidence).pattern_value
                if patterns else None,
            }

        return summary

    def clear(self) -> None:
        """Clear all patterns and observations."""
        self._patterns.clear()
        self._observations.clear()
