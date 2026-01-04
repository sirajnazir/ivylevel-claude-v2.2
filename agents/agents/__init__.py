"""
IvyQuest v10.0 Agents
=====================
5-Agent Architecture with 3P Stack (Agno + LangGraph + AutoGen)

Agents:
1. ExecutionAgent (P0 CRITICAL) - Bridges strategy-execution gap
2. AssessmentAgent - Synthesizes identity & computes readiness
3. GamePlanAgent - Creates strategic activity plans
4. AwardsAgent - Matches and optimizes award applications
5. OpportunityAgent - Matches summer programs and opportunities
"""

from .base import BaseAgent
from .execution import ExecutionAgent
from .assessment import AssessmentAgent
from .gameplan import GamePlanAgent
from .awards import AwardsAgent
from .opportunity import OpportunityAgent

__all__ = [
    "BaseAgent",
    "ExecutionAgent",
    "AssessmentAgent",
    "GamePlanAgent",
    "AwardsAgent",
    "OpportunityAgent",
]
