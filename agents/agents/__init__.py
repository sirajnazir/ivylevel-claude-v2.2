"""
IvyQuest v10.0 Agents
=====================
6-Agent Architecture with Strategic Intelligence

Agents:
1. ExecutionAgent (P0 CRITICAL) - Bridges strategy-execution gap
2. AssessmentAgent - Synthesizes identity & computes readiness
3. ExtracurricularsAgent - Portfolio analysis, identity synthesis (runs FIRST)
4. GamePlanAgent - Creates strategic activity plans
5. AwardsAgent - Matches awards with enriched strategic intelligence
6. ProgramsAgent - Matches programs with enriched strategic intelligence

Orchestration Flow:
EC Agent (FIRST) → identity_synthesis → Awards + Programs (PARALLEL)
"""

from .base import BaseAgent
from .execution import ExecutionAgent, execution_agent
from .assessment import AssessmentAgent, assessment_agent
from .extracurriculars import ExtracurricularsAgent, extracurriculars_agent
from .gameplan import GamePlanAgent, gameplan_agent
from .awards import AwardsAgent, awards_agent
from .programs import ProgramsAgent, programs_agent, OpportunityAgent, opportunity_agent
from .narrative_synthesis import NarrativeSynthesisAgent, narrative_synthesis_agent

__all__ = [
    "BaseAgent",
    "ExecutionAgent",
    "AssessmentAgent",
    "ExtracurricularsAgent",
    "GamePlanAgent",
    "AwardsAgent",
    "ProgramsAgent",
    "OpportunityAgent",  # Backward compatibility alias
    "NarrativeSynthesisAgent",
    # Singleton instances
    "execution_agent",
    "assessment_agent",
    "extracurriculars_agent",
    "gameplan_agent",
    "awards_agent",
    "programs_agent",
    "opportunity_agent",  # Backward compatibility alias
    "narrative_synthesis_agent",
]
