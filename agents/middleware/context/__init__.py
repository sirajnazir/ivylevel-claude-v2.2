"""
C5: Context Engineering Pattern - Phase 2A

Build rich, comprehensive context for every agent interaction.
Quality of output directly depends on quality of context.

Usage:
    from middleware.context import ContextEngineer, EngineeredContext

    engineer = ContextEngineer(supabase_client, redis_client)
    ctx = await engineer.engineer_context(profile_id, session_id, task_type)
    prompt_context = ctx.to_prompt_context(max_tokens=4000)
"""

from .engineering import (
    ContextEngineer,
    EngineeredContext,
)

__all__ = [
    "ContextEngineer",
    "EngineeredContext",
]
