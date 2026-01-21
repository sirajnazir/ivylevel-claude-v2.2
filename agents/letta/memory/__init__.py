"""
Letta Memory Module
===================

Memory block definitions and sync logic for Letta agents.

Blocks:
- student_profile: Core student attributes from profiles table
- coaching_history: Recent coaching interactions and outcomes
- active_gameplan: Current strategic plan and tasks
- outcome_tracker: Goal progress and achievements
- deadline_state: Upcoming deadlines and priorities
"""

from .blocks import (
    MemoryBlock,
    StudentProfileBlock,
    CoachingHistoryBlock,
    ActiveGameplanBlock,
    OutcomeTrackerBlock,
    DeadlineStateBlock,
    MEMORY_BLOCKS,
)
from .sync import MemorySyncService

__all__ = [
    "MemoryBlock",
    "StudentProfileBlock",
    "CoachingHistoryBlock",
    "ActiveGameplanBlock",
    "OutcomeTrackerBlock",
    "DeadlineStateBlock",
    "MEMORY_BLOCKS",
    "MemorySyncService",
]
