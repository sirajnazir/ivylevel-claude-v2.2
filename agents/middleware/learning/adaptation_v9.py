"""
Behavior Adaptation - Adapt behavior based on feedback.

Pattern: I2
3P: Supabase (storage)
Lines: ~120 (thin wrapper)

Features:
- Store behavior adaptations
- Apply adaptations to prompts
- Track adaptation effectiveness
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Adaptation(BaseModel):
    """A behavior adaptation."""
    adaptation_type: str  # tone, detail_level, explanation_style, etc.
    old_value: Optional[str] = None
    new_value: str
    reason: Optional[str] = None
    effectiveness: float = 0.5  # 0-1 scale
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BehaviorAdapter:
    """
    Adapts behavior based on feedback and preferences.

    Pattern I2: Behavior Adaptation
    3P: Supabase (storage)

    Thin wrapper - stores adaptations and applies them to system behavior.
    """

    TABLE = "phase3_behavior_adaptations"

    # Default adaptation parameters
    DEFAULT_PARAMS = {
        "tone": "professional",
        "detail_level": "medium",
        "explanation_style": "balanced",
        "encouragement_level": "moderate",
        "example_usage": "when_helpful",
    }

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._initialized = True
        self._adaptations: Dict[str, Adaptation] = {}
        self._current_params = self.DEFAULT_PARAMS.copy()

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def adapt(
        self,
        profile_id: str,
        adaptation_type: str,
        new_value: str,
        reason: Optional[str] = None,
    ) -> Adaptation:
        """Record and apply a behavior adaptation."""
        old_value = self._current_params.get(adaptation_type)

        adaptation = Adaptation(
            adaptation_type=adaptation_type,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
        )

        # Apply adaptation
        self._adaptations[adaptation_type] = adaptation
        self._current_params[adaptation_type] = new_value

        # Persist to Supabase if available
        if self.supabase:
            try:
                self.supabase.table(self.TABLE).upsert({
                    "profile_id": profile_id,
                    "adaptation_type": adaptation_type,
                    "old_value": old_value,
                    "new_value": new_value,
                    "reason": reason,
                    "effectiveness": 0.5,
                    "active": True,
                    "updated_at": datetime.utcnow().isoformat(),
                }).execute()
            except Exception as e:
                logger.warning(f"Failed to persist adaptation: {e}")

        return adaptation

    async def update_effectiveness(
        self,
        profile_id: str,
        adaptation_type: str,
        effectiveness: float,
    ) -> bool:
        """Update the effectiveness score of an adaptation."""
        if adaptation_type in self._adaptations:
            self._adaptations[adaptation_type].effectiveness = max(0.0, min(1.0, effectiveness))

            # Persist to Supabase if available
            if self.supabase:
                try:
                    self.supabase.table(self.TABLE).update({
                        "effectiveness": effectiveness,
                        "updated_at": datetime.utcnow().isoformat(),
                    }).eq("profile_id", profile_id).eq(
                        "adaptation_type", adaptation_type
                    ).execute()
                except Exception as e:
                    logger.warning(f"Failed to update effectiveness: {e}")

            return True
        return False

    async def revert(
        self,
        profile_id: str,
        adaptation_type: str,
    ) -> bool:
        """Revert an adaptation to its previous value."""
        if adaptation_type in self._adaptations:
            adaptation = self._adaptations[adaptation_type]

            if adaptation.old_value:
                self._current_params[adaptation_type] = adaptation.old_value
            else:
                self._current_params[adaptation_type] = self.DEFAULT_PARAMS.get(
                    adaptation_type, ""
                )

            adaptation.active = False
            return True
        return False

    def get_current_params(self) -> Dict[str, str]:
        """Get current behavior parameters."""
        return self._current_params.copy()

    def get_adaptation(
        self,
        adaptation_type: str,
    ) -> Optional[Adaptation]:
        """Get a specific adaptation."""
        return self._adaptations.get(adaptation_type)

    def get_active_adaptations(self) -> List[Adaptation]:
        """Get all active adaptations."""
        return [a for a in self._adaptations.values() if a.active]

    def apply_to_prompt(
        self,
        base_prompt: str,
    ) -> str:
        """Apply current adaptations to a system prompt."""
        additions = []

        # Add tone instruction
        tone = self._current_params.get("tone")
        if tone and tone != "professional":
            additions.append(f"Use a {tone} tone.")

        # Add detail level instruction
        detail = self._current_params.get("detail_level")
        if detail == "high":
            additions.append("Provide detailed, thorough explanations.")
        elif detail == "low":
            additions.append("Keep responses concise and brief.")

        # Add explanation style
        style = self._current_params.get("explanation_style")
        if style == "examples_heavy":
            additions.append("Use many examples to illustrate points.")
        elif style == "conceptual":
            additions.append("Focus on concepts and principles.")

        # Add encouragement level
        encouragement = self._current_params.get("encouragement_level")
        if encouragement == "high":
            additions.append("Be very encouraging and supportive.")
        elif encouragement == "low":
            additions.append("Be direct without unnecessary encouragement.")

        if additions:
            return f"{base_prompt}\n\nBehavior adaptations:\n" + "\n".join(f"- {a}" for a in additions)

        return base_prompt

    def reset(self) -> None:
        """Reset all adaptations to defaults."""
        self._adaptations.clear()
        self._current_params = self.DEFAULT_PARAMS.copy()
