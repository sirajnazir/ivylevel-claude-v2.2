"""
Pattern C2 Extension: Context Selector
v5.4 True Autonomous Agents

USP: Smart context selection based on task type.
This is OUR custom logic - no 3P for this.
"""

from typing import Dict, Any, List
from enum import Enum
import logging

from .types import (
    StudentContext,
    ContextSelection,
    TaskType,
)

logger = logging.getLogger(__name__)


class ContextRelevance(str, Enum):
    """How relevant a context piece is to the current task."""
    CRITICAL = "critical"   # Must include
    HELPFUL = "helpful"     # Should include if available
    OPTIONAL = "optional"   # Include if space allows
    EXCLUDE = "exclude"     # Don't include


# Context relevance matrix: task_type -> context_field -> relevance
CONTEXT_RELEVANCE_MATRIX: Dict[TaskType, Dict[str, ContextRelevance]] = {
    TaskType.ASSESSMENT: {
        "activities": ContextRelevance.CRITICAL,
        "academics": ContextRelevance.HELPFUL,
        "goals": ContextRelevance.HELPFUL,
        "constraints": ContextRelevance.OPTIONAL,
        "history": ContextRelevance.OPTIONAL,
        "identity": ContextRelevance.CRITICAL,
        "preferences": ContextRelevance.OPTIONAL,
    },
    TaskType.GAMEPLAN: {
        "activities": ContextRelevance.CRITICAL,
        "academics": ContextRelevance.CRITICAL,
        "goals": ContextRelevance.CRITICAL,
        "constraints": ContextRelevance.CRITICAL,
        "history": ContextRelevance.HELPFUL,
        "identity": ContextRelevance.CRITICAL,
        "preferences": ContextRelevance.HELPFUL,
    },
    TaskType.EXECUTION: {
        "activities": ContextRelevance.HELPFUL,
        "academics": ContextRelevance.OPTIONAL,
        "goals": ContextRelevance.CRITICAL,
        "constraints": ContextRelevance.CRITICAL,
        "history": ContextRelevance.HELPFUL,
        "identity": ContextRelevance.HELPFUL,
        "preferences": ContextRelevance.CRITICAL,  # Communication style matters
    },
    TaskType.CRISIS: {
        "activities": ContextRelevance.OPTIONAL,
        "academics": ContextRelevance.HELPFUL,
        "goals": ContextRelevance.HELPFUL,
        "constraints": ContextRelevance.CRITICAL,  # Know their limits
        "history": ContextRelevance.CRITICAL,      # What led here
        "identity": ContextRelevance.HELPFUL,
        "preferences": ContextRelevance.CRITICAL,  # How to communicate
    },
    TaskType.CHAT: {
        "activities": ContextRelevance.HELPFUL,
        "academics": ContextRelevance.OPTIONAL,
        "goals": ContextRelevance.HELPFUL,
        "constraints": ContextRelevance.OPTIONAL,
        "history": ContextRelevance.CRITICAL,      # Conversation context
        "identity": ContextRelevance.HELPFUL,
        "preferences": ContextRelevance.CRITICAL,
    },
    TaskType.GENERAL: {
        "activities": ContextRelevance.HELPFUL,
        "academics": ContextRelevance.HELPFUL,
        "goals": ContextRelevance.HELPFUL,
        "constraints": ContextRelevance.HELPFUL,
        "history": ContextRelevance.OPTIONAL,
        "identity": ContextRelevance.HELPFUL,
        "preferences": ContextRelevance.HELPFUL,
    },
}


class ContextSelector:
    """
    Intelligently selects what context to include based on task.

    USP: This is our custom logic - knowing what's relevant.

    Why this matters:
    - Too much context = slower, more expensive, less focused
    - Too little context = generic, unhelpful advice
    - Smart selection = personalized AND efficient
    """

    def __init__(self, max_context_tokens: int = 4000):
        """
        Initialize context selector.

        Args:
            max_context_tokens: Maximum tokens for context (budget)
        """
        self.max_tokens = max_context_tokens
        self._token_estimates = {
            "activities": 100,      # Per activity
            "academics": 200,       # Academic profile
            "goals": 150,           # Goals section
            "constraints": 100,     # Constraints
            "history": 50,          # Per history item
            "identity": 300,        # Identity synthesis
            "preferences": 100,     # User preferences
        }

    def select_for_task(
        self,
        task_type: TaskType,
        available_context: Dict[str, bool],
    ) -> ContextSelection:
        """
        Generate context selection based on task type.

        Args:
            task_type: Type of task being performed
            available_context: What context data is available

        Returns:
            ContextSelection with appropriate flags
        """
        relevance_map = CONTEXT_RELEVANCE_MATRIX.get(
            task_type,
            CONTEXT_RELEVANCE_MATRIX[TaskType.GENERAL]
        )

        # Start with critical items
        include_activities = (
            relevance_map.get("activities") in [ContextRelevance.CRITICAL, ContextRelevance.HELPFUL]
            and available_context.get("activities", False)
        )
        include_academics = (
            relevance_map.get("academics") in [ContextRelevance.CRITICAL, ContextRelevance.HELPFUL]
            and available_context.get("academics", False)
        )
        include_goals = (
            relevance_map.get("goals") in [ContextRelevance.CRITICAL, ContextRelevance.HELPFUL]
            and available_context.get("goals", False)
        )
        include_constraints = (
            relevance_map.get("constraints") in [ContextRelevance.CRITICAL, ContextRelevance.HELPFUL]
            and available_context.get("constraints", False)
        )

        # History is special - use sparingly
        include_history = (
            relevance_map.get("history") == ContextRelevance.CRITICAL
            and available_context.get("history", False)
        )

        # Determine history limit
        max_history = 3 if relevance_map.get("history") == ContextRelevance.CRITICAL else 0
        if relevance_map.get("history") == ContextRelevance.HELPFUL:
            max_history = 2

        return ContextSelection(
            include_activities=include_activities,
            include_academics=include_academics,
            include_goals=include_goals,
            include_history=include_history,
            max_history_items=max_history,
            include_constraints=include_constraints,
        )

    def estimate_tokens(
        self,
        context: StudentContext,
        selection: ContextSelection,
    ) -> int:
        """
        Estimate token count for selected context.

        Args:
            context: Full student context
            selection: What's being included

        Returns:
            Estimated token count
        """
        tokens = 0

        if selection.include_activities:
            tokens += len(context.activities) * self._token_estimates["activities"]

        if selection.include_academics:
            tokens += self._token_estimates["academics"]

        if selection.include_goals:
            tokens += self._token_estimates["goals"]

        if selection.include_constraints:
            tokens += self._token_estimates["constraints"]

        if selection.include_history:
            tokens += selection.max_history_items * self._token_estimates["history"]

        # Always include identity if available
        if context.spike or context.archetype:
            tokens += self._token_estimates["identity"]

        return tokens

    def optimize_selection(
        self,
        context: StudentContext,
        task_type: TaskType,
    ) -> ContextSelection:
        """
        Optimize context selection within token budget.

        USP: Smart pruning to fit context budget while keeping essentials.

        Args:
            context: Full student context
            task_type: Type of task

        Returns:
            Optimized ContextSelection
        """
        # Get available context
        available = {
            "activities": len(context.activities) > 0,
            "academics": context.gpa is not None or context.intended_major is not None,
            "goals": len(context.target_schools) > 0,
            "constraints": len(context.constraints) > 0,
            "history": False,  # Would need to check working memory
            "identity": context.spike is not None or context.archetype is not None,
            "preferences": context.communication_style is not None,
        }

        # Start with task-appropriate selection
        selection = self.select_for_task(task_type, available)

        # Check if within budget
        estimated = self.estimate_tokens(context, selection)

        if estimated <= self.max_tokens:
            return selection

        # Over budget - start pruning non-critical items
        relevance_map = CONTEXT_RELEVANCE_MATRIX.get(
            task_type,
            CONTEXT_RELEVANCE_MATRIX[TaskType.GENERAL]
        )

        # Prune optional items first
        if estimated > self.max_tokens:
            if relevance_map.get("history") == ContextRelevance.OPTIONAL:
                selection.include_history = False
                selection.max_history_items = 0

        if estimated > self.max_tokens:
            if relevance_map.get("constraints") == ContextRelevance.OPTIONAL:
                selection.include_constraints = False

        # Log if we had to prune
        if estimated > self.max_tokens:
            logger.warning(
                f"Context still over budget after pruning: {estimated} > {self.max_tokens}"
            )

        return selection


def get_agent_context_needs(agent_name: str) -> Dict[str, ContextRelevance]:
    """
    Get context needs for a specific agent.

    USP: Agent-specific context awareness.
    """
    agent_needs = {
        "ec_agent": {
            "activities": ContextRelevance.CRITICAL,
            "identity": ContextRelevance.CRITICAL,
            "academics": ContextRelevance.HELPFUL,
        },
        "awards_agent": {
            "identity": ContextRelevance.CRITICAL,
            "activities": ContextRelevance.CRITICAL,
            "constraints": ContextRelevance.HELPFUL,
        },
        "programs_agent": {
            "identity": ContextRelevance.CRITICAL,
            "constraints": ContextRelevance.CRITICAL,
            "goals": ContextRelevance.HELPFUL,
        },
        "gameplan_agent": {
            "identity": ContextRelevance.CRITICAL,
            "goals": ContextRelevance.CRITICAL,
            "constraints": ContextRelevance.CRITICAL,
            "activities": ContextRelevance.HELPFUL,
        },
        "coaching_agent": {
            "preferences": ContextRelevance.CRITICAL,
            "identity": ContextRelevance.HELPFUL,
            "history": ContextRelevance.CRITICAL,
        },
    }
    return agent_needs.get(agent_name, {})
