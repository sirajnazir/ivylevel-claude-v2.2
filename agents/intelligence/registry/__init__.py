"""
Intelligence Registry - CRUD and selection logic for coaching assets and student profiles.

Provides:
- AssetRegistry: Database operations for coaching assets
- AssetSelector: Intelligent asset selection based on context
- StudentIntelligenceManager: Student profile management
- GoalManager: Outcome-driven goal management
"""

from .asset_registry import AssetRegistry
from .asset_selector import AssetSelector, SelectionResult
from .student_intelligence import StudentIntelligenceManager
from .goal_manager import GoalManager

__all__ = [
    "AssetRegistry",
    "AssetSelector",
    "SelectionResult",
    "StudentIntelligenceManager",
    "GoalManager",
]
