"""
Intelligence Patterns - v5.4 True Autonomous Agents

Patterns implemented:
- A12: Prioritization (USP: Custom coaching intelligence)
- I3: Goal Monitoring (USP: Progress tracking)

These are BUILD, not buy - our competitive advantage.
"""

from .prioritization import (
    Prioritizer,
    PrioritizedItem,
    PriorityLevel,
    RecommendationType,
    prioritize_recommendations,
    PRIORITY_WEIGHTS,
    URGENCY_MULTIPLIERS,
)

from .goal_monitoring import (
    GoalMonitor,
    Goal,
    GoalStatus,
    GoalCategory,
    GoalProgressReport,
    get_goal_progress,
    GOAL_TEMPLATES_BY_GRADE,
)

__all__ = [
    # Prioritization
    "Prioritizer",
    "PrioritizedItem",
    "PriorityLevel",
    "RecommendationType",
    "prioritize_recommendations",
    "PRIORITY_WEIGHTS",
    "URGENCY_MULTIPLIERS",
    # Goal Monitoring
    "GoalMonitor",
    "Goal",
    "GoalStatus",
    "GoalCategory",
    "GoalProgressReport",
    "get_goal_progress",
    "GOAL_TEMPLATES_BY_GRADE",
]
