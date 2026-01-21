"""
Letta Agents Module
===================

Specialist agents for IvyLevel coaching.

Agents:
- OrchestratorAgent: Routes conversations to appropriate specialists
- GamePlanAgent: Strategic planning and milestone setting
- ExecutionAgent: Task tracking, nudges, deadline management
- AwardsAgent: Award recommendations and scholarship tracking
- EssayAgent: Narrative coaching and essay feedback
- AssessmentAgent: DORMANT - Phase 2 future implementation
"""

from .orchestrator import OrchestratorAgent, ORCHESTRATOR_CONFIG
from .gameplan import GamePlanSpecialist, GAMEPLAN_AGENT_CONFIG
from .execution import ExecutionSpecialist, EXECUTION_AGENT_CONFIG
from .awards import AwardsSpecialist, AWARDS_AGENT_CONFIG
from .essay import EssaySpecialist, ESSAY_AGENT_CONFIG
from .assessment import AssessmentSpecialist, ASSESSMENT_AGENT_CONFIG

__all__ = [
    "OrchestratorAgent",
    "ORCHESTRATOR_CONFIG",
    "GamePlanSpecialist",
    "GAMEPLAN_AGENT_CONFIG",
    "ExecutionSpecialist",
    "EXECUTION_AGENT_CONFIG",
    "AwardsSpecialist",
    "AWARDS_AGENT_CONFIG",
    "EssaySpecialist",
    "ESSAY_AGENT_CONFIG",
    "AssessmentSpecialist",
    "ASSESSMENT_AGENT_CONFIG",
]
