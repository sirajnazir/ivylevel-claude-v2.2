"""
Intelligence Primitives - Core data structures for autonomous coaching.

These are the atomic building blocks:
- CoachingAsset: Universal primitive for coaching IP
- OutcomeDrivenGoal: Goals focused on WINS, not just progress
"""

from .coaching_asset import (
    CoachingAsset,
    AssetType,
    AssetDomain,
    TriggerCondition,
    Applicability,
    Provenance,
    Effectiveness,
    ArchetypeEffectiveness,
)

from .goal import (
    OutcomeDrivenGoal,
    GoalType,
    GoalStatus,
    SecondaryMetric,
    GOAL_TEMPLATES,
)

__all__ = [
    # Coaching Asset
    "CoachingAsset",
    "AssetType",
    "AssetDomain",
    "TriggerCondition",
    "Applicability",
    "Provenance",
    "Effectiveness",
    "ArchetypeEffectiveness",
    # Goals
    "OutcomeDrivenGoal",
    "GoalType",
    "GoalStatus",
    "SecondaryMetric",
    "GOAL_TEMPLATES",
]
