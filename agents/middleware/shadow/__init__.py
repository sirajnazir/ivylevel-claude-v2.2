"""
G5: Human Shadow Mode Pattern - Phase 2A

Coach reviews and can modify agent proposals before they reach the student.
Enables oversight with graduated autonomy levels.

Usage:
    from middleware.shadow import HumanShadowManager, ShadowMode

    manager = HumanShadowManager(supabase_client)
    mode = manager.get_shadow_mode(profile_id, agent_name, context)

    if mode != ShadowMode.OFF:
        proposal = await manager.submit_proposal(...)
        reviewed = await manager.await_review(proposal)
"""

from .types import (
    ShadowMode,
    ShadowProposal,
    ShadowReview,
    ShadowConfig,
)
from .shadow_manager import (
    HumanShadowManager,
    DEFAULT_SHADOW_CONFIGS,
)

__all__ = [
    # Types
    "ShadowMode",
    "ShadowProposal",
    "ShadowReview",
    "ShadowConfig",
    # Manager
    "HumanShadowManager",
    "DEFAULT_SHADOW_CONFIGS",
]
