"""
H4: Pivot Strategy Pattern - Phase 2A

Alternative approaches when current approach fails.
Graceful recovery with new direction.

Usage:
    from middleware.recovery import PivotStrategy, PivotOption

    pivot = PivotStrategy(episodic_memory)

    # Check if pivot needed
    should_pivot, reason = await pivot.should_pivot(context)

    if should_pivot:
        options = await pivot.get_pivot_options(profile_id, current_approach, context)
        result = await pivot.execute_pivot(
            profile_id, current_approach, options[0], execute_func
        )
"""

from .pivot import (
    PivotStrategy,
    PivotTrigger,
    PivotOption,
    PivotResult,
)

__all__ = [
    "PivotStrategy",
    "PivotTrigger",
    "PivotOption",
    "PivotResult",
]
