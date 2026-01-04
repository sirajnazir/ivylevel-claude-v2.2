"""
IvyQuest v10.0 Agent Service - FastAPI Entry Point
==================================================
Multi-agent coaching platform powered by Agno + LangGraph + AutoGen

3P Stack:
- Agno: Runtime spine (stateful agents, memory, workflows, HITL)
- LangGraph: Deliberative reasoning (Crisis Alchemy, planning graphs)
- AutoGen: Selective debates (offline narrative experiments only)

Agents:
1. ExecutionAgent (P0 CRITICAL) - Bridges strategy-execution gap
2. AssessmentAgent - Synthesizes identity & computes readiness
3. GamePlanAgent - Creates strategic activity plans
4. AwardsAgent - Matches and optimizes award applications
5. OpportunityAgent - Matches summer programs and opportunities
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import structlog

from config import settings
from agents.execution import ExecutionAgent
from agents.assessment import AssessmentAgent
from agents.gameplan import GamePlanAgent
from agents.awards import AwardsAgent
from agents.opportunity import OpportunityAgent

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="IvyQuest Agent Service",
    version=settings.service_version,
    description="Multi-agent coaching platform for college admissions (v10.0)",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
execution_agent = ExecutionAgent()
assessment_agent = AssessmentAgent()
gameplan_agent = GamePlanAgent()
awards_agent = AwardsAgent()
opportunity_agent = OpportunityAgent()


# =====================================================
# Request/Response Models
# =====================================================

class ProfileInput(BaseModel):
    profile_id: str
    data: Optional[Dict[str, Any]] = None


class ProjectInput(BaseModel):
    profile_id: str
    project_data: Dict[str, Any]


class CrisisInput(BaseModel):
    profile_id: str
    crisis_type: str = "blocker"
    description: str
    urgency: int = 3


class HandoffInput(BaseModel):
    crisis_id: str
    approved: bool
    rationale: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    agents_enabled: bool


# =====================================================
# Health & Status Endpoints
# =====================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.service_version,
        agents_enabled=settings.enable_agents,
    )


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "IvyQuest Agent Service",
        "version": settings.service_version,
        "agents": ["Execution", "Assessment", "GamePlan", "Awards", "Opportunity"],
        "status": "running",
        "features": {
            "agents_enabled": settings.enable_agents,
            "execution_agent": settings.enable_execution_agent,
            "crisis_alchemy": settings.enable_crisis_alchemy,
            "cri_scoring": settings.enable_cri_scoring,
        },
    }


# =====================================================
# Assessment Agent Endpoints
# =====================================================

@app.post("/agents/assessment/enhance")
async def enhance_assessment(input: ProfileInput):
    """
    Run full assessment enhancement.

    - Synthesizes Narrative DNA
    - Detects Archetype with confidence/rationale
    - Computes CRI
    - Calculates Hidden Probabilities
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        result = await assessment_agent.enhance(input.profile_id, input.data)
        return result
    except Exception as e:
        logger.error("assessment_enhance_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Execution Agent Endpoints (P0 CRITICAL)
# =====================================================

@app.post("/agents/execution/scaffold")
async def scaffold_project(input: ProjectInput):
    """
    Break project into microsteps with Strategic Overwhelm.

    ACP-004: Assigns 1.4x tasks, expects 73% completion.
    """
    if not settings.enable_execution_agent:
        raise HTTPException(status_code=503, detail="Execution Agent is disabled")

    try:
        result = await execution_agent.scaffold_project(
            input.profile_id,
            input.project_data
        )
        return result
    except Exception as e:
        logger.error("scaffold_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/execution/crisis")
async def handle_crisis(input: CrisisInput):
    """
    Execute Crisis Alchemy Protocol via LangGraph.

    4-Step Protocol:
    1. Validate (2s) - Acknowledge emotion
    2. Act (10s) - Micro-action to restore agency
    3. Reframe (30s) - Find opportunity angle
    4. Create (2min) - Design new activity/pivot

    Returns: Proposed response awaiting HITL approval.
    """
    if not settings.enable_crisis_alchemy:
        raise HTTPException(status_code=503, detail="Crisis Alchemy is disabled")

    try:
        result = await execution_agent.handle_crisis(
            input.profile_id,
            input.crisis_type,
            input.description,
            input.urgency
        )
        return result
    except Exception as e:
        logger.error("crisis_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/handoff/approve")
async def approve_handoff(input: HandoffInput):
    """
    Process HITL approval/rejection for crisis response.

    Human Shadow Mode: Coach approves within 1 hour.
    """
    try:
        result = await execution_agent.process_handoff(
            input.crisis_id,
            input.approved,
            input.rationale
        )
        return result
    except Exception as e:
        logger.error("handoff_error", error=str(e), crisis_id=input.crisis_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/execution/blockers/{profile_id}")
async def detect_blockers(profile_id: str):
    """
    Detect projects with >5 days inactivity.

    Returns list of blocked projects for intervention.
    """
    try:
        result = await execution_agent.detect_blockers(profile_id)
        return result
    except Exception as e:
        logger.error("blockers_error", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/execution/eds/{profile_id}")
async def get_eds(profile_id: str):
    """
    Get Execution Debt Score for profile.

    Target: EDS < 50 (Huda benchmark: 12)
    """
    try:
        eds = await execution_agent.compute_eds(profile_id)
        return {
            "profile_id": profile_id,
            "eds": eds,
            "status": "healthy" if eds < 50 else "at_risk" if eds < 100 else "critical",
        }
    except Exception as e:
        logger.error("eds_error", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Game Plan Agent Endpoints
# =====================================================

@app.post("/agents/gameplan/generate")
async def generate_gameplan(input: ProfileInput):
    """
    Generate comprehensive game plan.

    - Filters activities by ROI (4+ touchpoints)
    - Plants identity seeds (6-12mo ahead)
    - Applies Strategic Overwhelm (1.4x)
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        result = await gameplan_agent.generate(input.profile_id)
        return result
    except Exception as e:
        logger.error("gameplan_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Awards Agent Endpoints
# =====================================================

@app.get("/agents/awards/match/{profile_id}")
async def match_awards(profile_id: str):
    """
    Match profile to awards with ROI calculation.

    Returns: Portfolio balanced with likely + stretch + skip.
    Target: >40% win rate (Huda: 62.5%)
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        result = await awards_agent.match(profile_id)
        return result
    except Exception as e:
        logger.error("awards_error", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Opportunity Agent Endpoints
# =====================================================

@app.get("/agents/opportunities/match/{profile_id}")
async def match_opportunities(profile_id: str):
    """
    Match profile to summer programs and opportunities.

    Returns: Top matches with advance alerts and backup cascade.
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        result = await opportunity_agent.match(profile_id)
        return result
    except Exception as e:
        logger.error("opportunities_error", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Main Entry Point
# =====================================================

if __name__ == "__main__":
    logger.info(
        "starting_agent_service",
        version=settings.service_version,
        port=settings.port,
        agents_enabled=settings.enable_agents,
    )

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )
