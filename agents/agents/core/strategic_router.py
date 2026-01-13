"""
Strategic Router - Deterministic Approach Selection
====================================================
Determines the best strategic approach for a student based on their context.

NOTE: This is pure rule-based routing, no LLM calls.

Routes:
- BUILD_FRESH: No activities, be prescriptive
- OPTIMIZE: Strong foundation, enhance positioning
- REFRAME: Has activities but needs narrative pivot
- URGENT_TRIAGE: Limited time, focus on quick wins
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class StrategicApproach(Enum):
    """Strategic approaches for student coaching."""
    BUILD_FRESH = "BUILD_FRESH"
    OPTIMIZE = "OPTIMIZE"
    REFRAME = "REFRAME"
    URGENT_TRIAGE = "URGENT_TRIAGE"


@dataclass
class StrategicRoute:
    """Result of strategic routing decision."""
    choice: StrategicApproach
    reasoning: str
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "choice": self.choice.value,
            "reasoning": self.reasoning,
            "config": self.config,
        }


# Route configurations
ROUTE_CONFIGS = {
    StrategicApproach.BUILD_FRESH: {
        "be_prescriptive": True,
        "recommend_activities": True,
        "timeline_horizon": "long",
        "tier_targets": {"T1": 2, "T2": 3, "T3": 3, "T4": 2},
        "focus": ["activity_building", "spike_development", "portfolio_foundation"],
    },
    StrategicApproach.OPTIMIZE: {
        "be_prescriptive": False,
        "recommend_activities": False,
        "timeline_horizon": "medium",
        "focus": ["positioning", "narrative", "impact_evidence", "differentiation"],
    },
    StrategicApproach.REFRAME: {
        "be_prescriptive": False,
        "recommend_activities": True,  # 1-2 strategic additions
        "timeline_horizon": "medium",
        "focus": ["narrative_pivot", "connect_dots", "spike_identification", "coherence"],
    },
    StrategicApproach.URGENT_TRIAGE: {
        "be_prescriptive": True,
        "recommend_activities": False,  # No time for new activities
        "timeline_horizon": "short",
        "max_recommendations": 3,
        "focus": ["positioning", "quick_wins", "narrative", "immediate_impact"],
    },
}


class StrategicRouter:
    """
    Routes students to appropriate strategic approach.

    Uses deterministic rules based on:
    - Activity count
    - Activity tier levels (T1/T2)
    - Time until Early Decision
    - Grade level
    """

    def __init__(self):
        pass  # No state needed for deterministic routing

    async def decide_route(self, context: Dict[str, Any]) -> StrategicRoute:
        """
        Decide strategic approach based on student context.

        Args:
            context: Dict with keys:
                - grade: int (9-12)
                - activity_count: int
                - has_tier1: bool
                - has_tier2: bool
                - months_to_ed: int
                - portfolio_diagnosis: str (optional)

        Returns:
            StrategicRoute with choice, reasoning, and config
        """
        grade = context.get("grade", 11)
        activity_count = context.get("activity_count", 0)
        has_tier1 = context.get("has_tier1", False)
        has_tier2 = context.get("has_tier2", False)
        months_to_ed = context.get("months_to_ed", 20)

        # Rule 1: Urgent triage if very limited time
        if months_to_ed < 6:
            return StrategicRoute(
                choice=StrategicApproach.URGENT_TRIAGE,
                reasoning=f"Only {months_to_ed} months to Early Decision - focus on quick wins",
                config=ROUTE_CONFIGS[StrategicApproach.URGENT_TRIAGE],
            )

        # Rule 2: Build fresh if minimal activities
        if activity_count < 3:
            return StrategicRoute(
                choice=StrategicApproach.BUILD_FRESH,
                reasoning=f"Only {activity_count} activities - need to build foundation",
                config=ROUTE_CONFIGS[StrategicApproach.BUILD_FRESH],
            )

        # Rule 3: Optimize if strong T1/T2 foundation
        if has_tier1 or (has_tier2 and activity_count >= 5):
            return StrategicRoute(
                choice=StrategicApproach.OPTIMIZE,
                reasoning="Strong activity foundation with T1/T2 achievements - focus on positioning",
                config=ROUTE_CONFIGS[StrategicApproach.OPTIMIZE],
            )

        # Rule 4: Default to reframe
        return StrategicRoute(
            choice=StrategicApproach.REFRAME,
            reasoning=f"Have {activity_count} activities but may need narrative repositioning",
            config=ROUTE_CONFIGS[StrategicApproach.REFRAME],
        )

    def get_route_config(self, approach: StrategicApproach) -> Dict[str, Any]:
        """Get configuration for a specific approach."""
        return ROUTE_CONFIGS.get(approach, {})


def calculate_months_to_ed(grade: int) -> int:
    """
    Calculate approximate months until Early Decision deadline.

    Assumes:
    - ED deadline: November 1 of senior year
    - Current month: January
    """
    if grade == 12:
        return 0  # Already senior year
    elif grade == 11:
        return 10  # ~10 months to Nov of senior year
    elif grade == 10:
        return 22  # ~22 months
    elif grade == 9:
        return 34  # ~34 months
    else:
        return 46  # Gap year or earlier


# Backwards compatibility alias
LLMRouter = StrategicRouter
