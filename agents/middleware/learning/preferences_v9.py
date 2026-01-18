"""
Preference Learning - Learn and apply user preferences.

Pattern: I5
3P: Supabase (storage)
Lines: ~100 (thin wrapper)

Features:
- Infer preferences from behavior
- Store explicit preferences
- Apply preferences to responses
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Preference(BaseModel):
    """A user preference."""
    preference_key: str
    preference_value: Any
    source: str = "inferred"  # explicit, inferred, default
    confidence: float = 0.5
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PreferenceLearner:
    """
    Learns and applies user preferences.

    Pattern I5: Preference Learning
    3P: Supabase (storage) + Long-term Memory (B4)

    Thin wrapper - learns preferences from feedback and behavior.
    """

    # Default preferences
    DEFAULT_PREFERENCES = {
        "response_length": "medium",
        "technical_depth": "medium",
        "example_frequency": "moderate",
        "formality": "semi-formal",
        "encouragement": True,
        "show_sources": False,
    }

    def __init__(
        self,
        supabase_client=None,
        longterm_memory=None,
    ):
        self.supabase = supabase_client
        self.longterm = longterm_memory
        self._initialized = True
        self._preferences: Dict[str, Preference] = {}

        # Initialize with defaults
        for key, value in self.DEFAULT_PREFERENCES.items():
            self._preferences[key] = Preference(
                preference_key=key,
                preference_value=value,
                source="default",
                confidence=0.3,
            )

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def set_preference(
        self,
        profile_id: str,
        key: str,
        value: Any,
        source: str = "explicit",
        confidence: float = 0.9,
    ) -> Preference:
        """Set a preference explicitly."""
        preference = Preference(
            preference_key=key,
            preference_value=value,
            source=source,
            confidence=confidence,
        )

        self._preferences[key] = preference

        # Store in long-term memory if available
        if self.longterm:
            await self.longterm.remember(
                profile_id=profile_id,
                key=f"preference_{key}",
                value=value,
                memory_type="preference",
                importance=confidence,
            )

        return preference

    async def infer_preference(
        self,
        profile_id: str,
        key: str,
        value: Any,
        evidence: Optional[str] = None,
    ) -> Preference:
        """Infer a preference from behavior."""
        # Get existing preference
        existing = self._preferences.get(key)

        if existing and existing.source == "explicit":
            # Don't override explicit preferences with inferred ones
            return existing

        # Calculate confidence based on existing data
        if existing and existing.source == "inferred":
            # Increase confidence if same value inferred again
            if existing.preference_value == value:
                confidence = min(0.9, existing.confidence + 0.1)
            else:
                confidence = 0.5  # Reset on conflicting inference
        else:
            confidence = 0.5

        return await self.set_preference(
            profile_id=profile_id,
            key=key,
            value=value,
            source="inferred",
            confidence=confidence,
        )

    def get_preference(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get a preference value."""
        pref = self._preferences.get(key)
        if pref:
            return pref.preference_value
        return default if default is not None else self.DEFAULT_PREFERENCES.get(key)

    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all preferences as a dictionary."""
        return {k: p.preference_value for k, p in self._preferences.items()}

    def get_high_confidence_preferences(
        self,
        min_confidence: float = 0.7,
    ) -> Dict[str, Any]:
        """Get preferences with high confidence."""
        return {
            k: p.preference_value
            for k, p in self._preferences.items()
            if p.confidence >= min_confidence
        }

    async def load_from_memory(
        self,
        profile_id: str,
    ) -> int:
        """Load preferences from long-term memory."""
        if not self.longterm:
            return 0

        loaded = 0
        memories = await self.longterm.recall_all(
            profile_id=profile_id,
            memory_type="preference",
        )

        for memory in memories:
            if memory.key.startswith("preference_"):
                key = memory.key.replace("preference_", "")
                self._preferences[key] = Preference(
                    preference_key=key,
                    preference_value=memory.value,
                    source="stored",
                    confidence=memory.importance,
                )
                loaded += 1

        return loaded

    def apply_to_system_prompt(
        self,
        base_prompt: str,
    ) -> str:
        """Apply preferences to system prompt."""
        additions = []

        # Response length
        length = self.get_preference("response_length")
        if length == "short":
            additions.append("Keep responses brief and to the point.")
        elif length == "long":
            additions.append("Provide comprehensive, detailed responses.")

        # Technical depth
        depth = self.get_preference("technical_depth")
        if depth == "high":
            additions.append("Use technical language and detailed explanations.")
        elif depth == "low":
            additions.append("Keep explanations simple and avoid jargon.")

        # Examples
        examples = self.get_preference("example_frequency")
        if examples == "high":
            additions.append("Include many examples to illustrate points.")
        elif examples == "low":
            additions.append("Minimize examples unless specifically asked.")

        # Formality
        formality = self.get_preference("formality")
        if formality == "formal":
            additions.append("Use formal, professional language.")
        elif formality == "casual":
            additions.append("Use casual, conversational language.")

        if additions:
            return f"{base_prompt}\n\nUser preferences:\n" + "\n".join(f"- {a}" for a in additions)

        return base_prompt

    def reset(self) -> None:
        """Reset preferences to defaults."""
        self._preferences.clear()
        for key, value in self.DEFAULT_PREFERENCES.items():
            self._preferences[key] = Preference(
                preference_key=key,
                preference_value=value,
                source="default",
                confidence=0.3,
            )
