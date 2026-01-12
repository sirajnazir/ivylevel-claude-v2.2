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
from .execution import ExecutionAgent, execution_agent
from .assessment import AssessmentAgent, assessment_agent
from .gameplan import GamePlanAgent, gameplan_agent
from .awards import AwardsAgent, awards_agent
from .opportunity import OpportunityAgent, opportunity_agent
from .narrative_synthesis import NarrativeSynthesisAgent, narrative_synthesis_agent

__all__ = [
    "BaseAgent",
    "ExecutionAgent",
    "AssessmentAgent",
    "GamePlanAgent",
    "AwardsAgent",
    "OpportunityAgent",
    "NarrativeSynthesisAgent",
    # Singleton instances
    "execution_agent",
    "assessment_agent",
    "gameplan_agent",
    "awards_agent",
    "opportunity_agent",
    "narrative_synthesis_agent",
]
