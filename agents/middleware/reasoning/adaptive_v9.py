"""
Adaptive Prompting - Adapt prompts based on context and history.

Pattern: A5
3P: OpenAI (LLM)
Lines: ~100 (thin wrapper)

Features:
- Adapt prompts to user context
- Incorporate learned preferences
- Dynamic complexity adjustment
- Graceful degradation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AdaptivePrompt(BaseModel):
    """An adapted prompt with metadata."""
    original_prompt: str
    adapted_prompt: str
    adaptations_applied: List[str] = Field(default_factory=list)
    context_used: Dict[str, Any] = Field(default_factory=dict)


class AdaptivePrompter:
    """
    Adapts prompts based on context and user preferences.

    Pattern A5: Adaptive Prompting
    3P: Uses B4 (Long-term Memory), I5 (Preference Learning), I2 (Behavior Adaptation)

    Thin wrapper - composes adaptations from multiple sources.
    """

    def __init__(
        self,
        preference_learner=None,
        behavior_adapter=None,
        longterm_memory=None,
    ):
        self.preferences = preference_learner
        self.adapter = behavior_adapter
        self.longterm = longterm_memory
        self._initialized = True

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def adapt(
        self,
        profile_id: str,
        base_prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AdaptivePrompt:
        """Adapt a prompt based on user context and preferences."""
        adapted = base_prompt
        adaptations = []
        context_used = context or {}

        # Apply preference-based adaptations
        if self.preferences:
            adapted = self.preferences.apply_to_system_prompt(adapted)
            adaptations.append("preferences")
            context_used["preferences"] = self.preferences.get_high_confidence_preferences()

        # Apply behavior adaptations
        if self.adapter:
            adapted = self.adapter.apply_to_prompt(adapted)
            adaptations.append("behavior")
            context_used["behavior_params"] = self.adapter.get_current_params()

        # Add relevant memories
        if self.longterm:
            memories = await self._get_relevant_memories(profile_id)
            if memories:
                memory_context = "\n".join([f"- {m}" for m in memories])
                adapted = f"{adapted}\n\nRelevant context about this user:\n{memory_context}"
                adaptations.append("memories")
                context_used["memory_count"] = len(memories)

        # Add student context if available
        if context:
            student_info = self._format_student_context(context)
            if student_info:
                adapted = f"{adapted}\n\nStudent context:\n{student_info}"
                adaptations.append("student_context")

        return AdaptivePrompt(
            original_prompt=base_prompt,
            adapted_prompt=adapted,
            adaptations_applied=adaptations,
            context_used=context_used,
        )

    async def _get_relevant_memories(
        self,
        profile_id: str,
        limit: int = 5,
    ) -> List[str]:
        """Get relevant memories for prompt context."""
        if not self.longterm:
            return []

        try:
            memories = await self.longterm.recall_all(
                profile_id=profile_id,
                min_importance=0.7,
                limit=limit,
            )
            return [str(m.value) for m in memories]
        except Exception as e:
            logger.warning(f"Failed to get memories: {e}")
            return []

    def _format_student_context(
        self,
        context: Dict[str, Any],
    ) -> str:
        """Format student context for prompt."""
        lines = []

        if context.get("grade_level"):
            lines.append(f"Grade level: {context['grade_level']}")

        if context.get("target_schools"):
            schools = ", ".join(context["target_schools"][:3])
            lines.append(f"Target schools: {schools}")

        if context.get("interests"):
            interests = ", ".join(context["interests"][:3])
            lines.append(f"Interests: {interests}")

        if context.get("strengths"):
            strengths = ", ".join(context["strengths"][:3])
            lines.append(f"Strengths: {strengths}")

        if context.get("areas_to_improve"):
            areas = ", ".join(context["areas_to_improve"][:3])
            lines.append(f"Areas to improve: {areas}")

        return "\n".join(lines)

    async def adapt_for_task(
        self,
        profile_id: str,
        base_prompt: str,
        task_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AdaptivePrompt:
        """Adapt prompt for a specific task type."""
        # Add task-specific instructions
        task_instructions = self._get_task_instructions(task_type)
        enhanced_prompt = f"{base_prompt}\n\n{task_instructions}"

        return await self.adapt(
            profile_id=profile_id,
            base_prompt=enhanced_prompt,
            context=context,
        )

    def _get_task_instructions(
        self,
        task_type: str,
    ) -> str:
        """Get task-specific instructions."""
        instructions = {
            "essay_review": "Focus on constructive feedback. Highlight strengths before suggesting improvements.",
            "brainstorming": "Encourage creativity. Generate diverse ideas without judgment.",
            "planning": "Be structured and organized. Break down tasks into manageable steps.",
            "tutoring": "Be patient and encouraging. Check understanding frequently.",
            "research": "Be thorough and cite sources. Present multiple perspectives.",
        }
        return instructions.get(task_type, "")
