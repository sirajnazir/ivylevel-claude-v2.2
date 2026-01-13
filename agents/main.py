"""
IvyQuest v10.0 Agent Service - FastAPI Entry Point
==================================================
Multi-agent coaching platform powered by Agno + LangGraph + AutoGen

3P Stack:
- Agno: Runtime spine (stateful agents, memory, workflows, HITL)
- LangGraph: Deliberative reasoning (Crisis Alchemy, planning graphs)
- AutoGen: Selective debates (offline narrative experiments only)

6-Agent Architecture with Strategic Intelligence (v1.0.0):
1. ExecutionAgent (P0 CRITICAL) - Bridges strategy-execution gap
2. AssessmentAgent - Synthesizes identity & computes readiness
3. ExtracurricularsAgent - Portfolio analysis, identity synthesis (runs FIRST)
4. GamePlanAgent - Orchestrates multi-agent flow, creates strategic plans
5. AwardsAgent - Matches awards with enriched strategic intelligence
6. ProgramsAgent - Matches programs with enriched strategic intelligence

Orchestration Flow:
  EC Agent (FIRST) → identity_synthesis → Awards + Programs (PARALLEL)
"""

# Load environment variables FIRST (before any other imports)
import os
from dotenv import load_dotenv
# Load from parent .env.local first, then local .env to override
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'), override=False)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import structlog

from config import settings
from agents.execution import ExecutionAgent
from agents.assessment import AssessmentAgent
from agents.extracurriculars import ExtracurricularsAgent
from agents.gameplan import GamePlanAgent
from agents.awards import AwardsAgent
from agents.opportunity import OpportunityAgent  # Backward compat shim → ProgramsAgent
from agents.programs import ProgramsAgent
from agents.narrative_synthesis import NarrativeSynthesisAgent
from workflows import WorkflowRunner
from tools.database import get_supabase_client
from evaluation import EvaluationPipeline, GoldenDatasetLoader

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

# Global workflow runner (initialized on startup)
workflow_runner: Optional[WorkflowRunner] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global workflow_runner

    # Startup: Initialize workflow runner
    if settings.enable_agents:
        try:
            db = get_supabase_client()
            workflow_runner = WorkflowRunner(db)
            workflow_runner.register_all_workflows()
            workflow_runner.start()
            logger.info("workflow_runner_started")
        except Exception as e:
            logger.error("workflow_runner_start_error", error=str(e))

    yield

    # Shutdown: Stop workflow runner
    if workflow_runner:
        workflow_runner.stop()
        logger.info("workflow_runner_stopped")


# Initialize FastAPI app
app = FastAPI(
    title="IvyQuest Agent Service",
    version=settings.service_version,
    description="Multi-agent coaching platform for college admissions (v10.0)",
    lifespan=lifespan,
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
extracurriculars_agent = ExtracurricularsAgent()
gameplan_agent = GamePlanAgent()
awards_agent = AwardsAgent()
programs_agent = ProgramsAgent()
opportunity_agent = programs_agent  # Backward compat alias
narrative_synthesis_agent = NarrativeSynthesisAgent()


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


class NarrativeInput(BaseModel):
    profile_id: str
    assessment_contract: Optional[Dict[str, Any]] = None


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
        "agents": ["Execution", "Assessment", "GamePlan", "Awards", "Opportunity", "NarrativeSynthesis"],
        "workflows": ["silence_detector", "deadline_alerts", "weekly_scout", "daily_checkin"],
        "status": "running",
        "features": {
            "agents_enabled": settings.enable_agents,
            "execution_agent": settings.enable_execution_agent,
            "crisis_alchemy": settings.enable_crisis_alchemy,
            "cri_scoring": settings.enable_cri_scoring,
            "workflows_enabled": workflow_runner is not None and workflow_runner.scheduler.running if workflow_runner else False,
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
# Narrative Synthesis Agent Endpoints
# =====================================================

@app.post("/agents/narrative/synthesize")
async def synthesize_narrative(input: NarrativeInput):
    """
    Synthesize personalized narrative using Jenny's Formula.

    IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE

    Returns:
    - brand_statement: One powerful sentence (15-25 words)
    - narrative_dna: 2-3 paragraph personalized story
    - first_principle: The core "why" driving the student
    - themes: Key recurring themes
    - confidence: Synthesis confidence (handoff if < 0.7)
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        result = await narrative_synthesis_agent.synthesize(
            input.profile_id,
            input.assessment_contract
        )
        return result
    except Exception as e:
        logger.error("narrative_synthesis_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/narrative/{profile_id}")
async def get_narrative(profile_id: str):
    """
    Get existing narrative for a profile.

    Returns cached narrative if available, or synthesizes a new one.
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Try to get from database first
        from tools.database import get_supabase_client
        db = get_supabase_client()

        result = db.table("profiles").select(
            "narrative_brand_statement, narrative_dna, narrative_first_principle, "
            "narrative_themes, narrative_confidence, narrative_updated_at"
        ).eq("id", profile_id).single().execute()

        if result.data and result.data.get("narrative_brand_statement"):
            return {
                "success": True,
                "brand_statement": result.data.get("narrative_brand_statement"),
                "narrative_dna": result.data.get("narrative_dna"),
                "first_principle": result.data.get("narrative_first_principle"),
                "themes": result.data.get("narrative_themes", []),
                "confidence": result.data.get("narrative_confidence", 0.7),
                "updated_at": result.data.get("narrative_updated_at"),
                "cached": True
            }

        # No cached narrative, synthesize new one
        return await narrative_synthesis_agent.synthesize(profile_id)

    except Exception as e:
        logger.error("get_narrative_error", error=str(e), profile_id=profile_id)
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
    Generate comprehensive game plan with multi-agent orchestration.

    Orchestration Flow (v1.0.0):
    1. EC Agent (FIRST) → identity_synthesis (spike, archetype, pillars)
    2. Awards + Programs (PARALLEL) ← use identity_synthesis for filtering
    3. Synthesis → Unified GamePlan

    Legacy features still included:
    - Filters activities by ROI (4+ touchpoints)
    - Plants identity seeds (6-12mo ahead)
    - Applies Strategic Overwhelm (1.4x)
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Use process() to trigger orchestrated flow
        result = await gameplan_agent.process(input.profile_id)
        return result
    except Exception as e:
        logger.error("gameplan_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/gameplan/activities/{profile_id}")
async def get_gameplan_activities(profile_id: str):
    """
    Get filtered activities for a profile's game plan.

    Returns activities filtered by ROI (4+ touchpoints).
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Generate game plan which includes filtered activities
        result = await gameplan_agent.generate(profile_id)

        if result.get("success") and result.get("data"):
            activities = result["data"].get("filtered_activities", [])
            return {
                "success": True,
                "activities": activities,
                "count": len(activities),
                "profile_id": profile_id,
            }
        elif result.get("filtered_activities"):
            activities = result.get("filtered_activities", [])
            return {
                "success": True,
                "activities": activities,
                "count": len(activities),
                "profile_id": profile_id,
            }
        else:
            return {
                "success": True,
                "activities": [],
                "count": 0,
                "profile_id": profile_id,
            }
    except Exception as e:
        logger.error("gameplan_activities_error", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/gameplan/seeds/{profile_id}")
async def get_gameplan_seeds(profile_id: str):
    """
    Get identity seeds for a profile's game plan.

    Returns identity seeds planted 6-12 months ahead.
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Generate game plan which includes identity seeds
        result = await gameplan_agent.generate(profile_id)

        if result.get("success") and result.get("data"):
            seeds = result["data"].get("identity_seeds", [])
            return {
                "success": True,
                "seeds": seeds,
                "count": len(seeds),
                "profile_id": profile_id,
            }
        elif result.get("identity_seeds"):
            seeds = result.get("identity_seeds", [])
            return {
                "success": True,
                "seeds": seeds,
                "count": len(seeds),
                "profile_id": profile_id,
            }
        else:
            return {
                "success": True,
                "seeds": [],
                "count": 0,
                "profile_id": profile_id,
            }
    except Exception as e:
        logger.error("gameplan_seeds_error", error=str(e), profile_id=profile_id)
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


@app.get("/agents/awards/portfolio/{profile_id}")
async def get_awards_portfolio(profile_id: str):
    """
    Get awards portfolio for a profile.

    Returns a balanced 2-2-1 portfolio:
    - 2 Likely awards (60%+ win probability)
    - 2 Target awards (40-60% probability)
    - 1 Stretch award (20-40% probability)
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Use the awards agent match which returns portfolio data
        result = await awards_agent.match(profile_id)

        if result.get("success") and result.get("data"):
            portfolio = result["data"].get("portfolio", {})
            return {
                "success": True,
                "portfolio": portfolio,
                "profile_id": profile_id,
            }
        elif result.get("portfolio"):
            return {
                "success": True,
                "portfolio": result.get("portfolio", {}),
                "profile_id": profile_id,
            }
        else:
            # Return empty portfolio structure
            return {
                "success": True,
                "portfolio": {
                    "likely": [],
                    "target": [],
                    "stretch": [],
                    "skip": [],
                },
                "profile_id": profile_id,
            }
    except Exception as e:
        logger.error("awards_portfolio_error", error=str(e), profile_id=profile_id)
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


@app.get("/agents/opportunities/alerts/{profile_id}")
async def get_opportunity_alerts(profile_id: str):
    """
    Get opportunity alerts for a profile.

    Returns advance alerts for opportunities with deadlines 5-6 months away.
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Use the opportunity agent match which returns alerts
        result = await opportunity_agent.match(profile_id)

        if result.get("success") and result.get("data"):
            alerts = result["data"].get("advance_alerts", [])
            return {
                "success": True,
                "alerts": alerts,
                "count": len(alerts),
                "urgent_count": len([a for a in alerts if a.get("days_until", 999) < 30]),
                "profile_id": profile_id,
            }
        elif result.get("advance_alerts"):
            alerts = result.get("advance_alerts", [])
            return {
                "success": True,
                "alerts": alerts,
                "count": len(alerts),
                "urgent_count": len([a for a in alerts if a.get("days_until", 999) < 30]),
                "profile_id": profile_id,
            }
        else:
            return {
                "success": True,
                "alerts": [],
                "count": 0,
                "urgent_count": 0,
                "profile_id": profile_id,
            }
    except Exception as e:
        logger.error("opportunity_alerts_error", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# v2.0 Jenny Intelligence Module Endpoints
# =====================================================

from modules import (
    TimeAuditModule,
    AwardsProbabilityEngine,
    ProgramRedirectModule,
    NCWITStrategyModule,
    CrisisAlchemyModule,
)
from validation import JennyVoiceValidator, validate_jenny_voice

# Initialize modules
time_audit_module = TimeAuditModule()
awards_probability_engine = AwardsProbabilityEngine()
program_redirect_module = ProgramRedirectModule()
ncwit_strategy_module = NCWITStrategyModule()
crisis_alchemy_module = CrisisAlchemyModule()
jenny_voice_validator = JennyVoiceValidator()


class TimeAuditInput(BaseModel):
    sleep_hours: float = 8
    school_hours: float = 7.5
    commute_minutes: int = 30
    religious_hours: float = 0
    misc_hours: float = 3
    social_media_hours_daily: float = 4
    homework_hours_daily: float = 2


class WeeklyPlanInput(BaseModel):
    profile_id: str
    tasks: List[Dict[str, Any]]
    available_hours: float = 26


class PortfolioInput(BaseModel):
    profile_id: str
    awards: Optional[List[Dict[str, Any]]] = None


class NCWITInput(BaseModel):
    profile_id: str
    student_data: Optional[Dict[str, Any]] = None


class OpportunityRecommendInput(BaseModel):
    profile_id: str
    program: Dict[str, Any]


class CrisisAlchemyInput(BaseModel):
    profile_id: str
    crisis_description: str
    student_data: Optional[Dict[str, Any]] = None


class VoiceValidationInput(BaseModel):
    text: str
    auto_fix: bool = True


@app.post("/agents/time-audit")
async def calculate_time_audit(input: TimeAuditInput):
    """
    Calculate available passion hours using Jenny's 168-hour framework.

    Formula: 168 - fixed_commitments - social_media = passion_hours (~26/week)

    Returns:
    - Total hours breakdown
    - Social media audit with recovery potential
    - Available passion hours per day/week
    - Jenny's walkthrough script
    """
    try:
        audit = time_audit_module.calculate_available_time(
            sleep_hours=input.sleep_hours,
            school_hours=input.school_hours,
            commute_minutes=input.commute_minutes,
            religious_hours=input.religious_hours,
            misc_hours=input.misc_hours,
            social_media_hours_daily=input.social_media_hours_daily,
            homework_hours_daily=input.homework_hours_daily
        )

        return {
            "success": True,
            "audit": time_audit_module.to_dict(audit),
            "walkthrough_script": time_audit_module.generate_walkthrough_script(audit),
            "efficiency_hacks": time_audit_module.get_efficiency_hacks(),
        }
    except Exception as e:
        logger.error("time_audit_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/weekly-plan")
async def generate_weekly_plan(input: WeeklyPlanInput):
    """
    Generate P0/P1/P2 prioritized weekly plan.

    Follows Jenny's prioritization framework:
    - P0: Must complete (non-negotiable)
    - P1: Should complete (important)
    - P2: If time permits (nice to have)

    Returns balanced plan with time budgets and buffer.
    """
    try:
        plan = time_audit_module.generate_weekly_plan(
            tasks=input.tasks,
            available_hours=input.available_hours
        )

        return {
            "success": True,
            "plan": {
                "week_start": plan.week_start.isoformat(),
                "p0_must_complete": [{"name": t.name, "hours": t.estimated_hours, "priority": t.priority} for t in plan.p0_must_complete],
                "p1_should_complete": [{"name": t.name, "hours": t.estimated_hours, "priority": t.priority} for t in plan.p1_should_complete],
                "p2_if_time_permits": [{"name": t.name, "hours": t.estimated_hours, "priority": t.priority} for t in plan.p2_if_time_permits],
                "total_hours_estimated": plan.total_hours_estimated,
                "available_hours": plan.available_hours,
                "buffer_hours": plan.buffer_hours,
            },
            "formatted_plan": time_audit_module.format_weekly_plan(plan),
            "flexibility_note": plan.flexibility_note,
        }
    except Exception as e:
        logger.error("weekly_plan_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/awards/portfolio")
async def build_awards_portfolio(input: PortfolioInput):
    """
    Build a balanced 2-2-1 awards portfolio.

    Portfolio Structure:
    - 2 Likely awards (60%+ win probability)
    - 2 Target awards (40-60% probability)
    - 1 Stretch award (20-40% probability)

    Probability Formula:
    probability = fit×0.4 + (100-competition)×0.3 + quality×0.3 + bonuses
    Bonuses: +15% vulnerability storytelling, +10% identity alignment
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Get profile for scoring
        db = get_supabase_client()
        profile_result = db.table("profiles").select("*").eq("id", input.profile_id).single().execute()

        if not profile_result.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        student = profile_result.data

        # Get awards to score (from input or database)
        if input.awards:
            awards = input.awards
        else:
            awards_result = db.table("awards").select("*").limit(50).execute()
            awards = awards_result.data if awards_result.data else []

        # Build portfolio
        portfolio = awards_probability_engine.build_balanced_portfolio(student, awards)

        return {
            "success": True,
            "portfolio": awards_probability_engine.to_dict(portfolio),
            "formatted_summary": awards_probability_engine.format_portfolio_summary(portfolio),
            "profile_id": input.profile_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("portfolio_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/ncwit-strategy")
async def generate_ncwit_strategy(input: NCWITInput):
    """
    Generate personalized NCWIT Aspirations strategy.

    Implements Jenny's NCWIT coaching approach:
    - Identity Multiplication: Layer ALL identity markers
    - Vulnerability Formula: Background + Barrier + Persistence = Compelling
    - Sensory Detail: "Make them FEEL your story, not just understand it"

    Returns complete strategy with coaching script and essay structure.
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Get student data
        if input.student_data:
            student = input.student_data
        else:
            db = get_supabase_client()
            result = db.table("profiles").select("*").eq("id", input.profile_id).single().execute()
            if not result.data:
                raise HTTPException(status_code=404, detail="Profile not found")
            student = result.data

        strategy = ncwit_strategy_module.generate_strategy(student)

        return {
            "success": True,
            "strategy": ncwit_strategy_module.to_dict(strategy),
            "transformation_examples": ncwit_strategy_module.get_transformation_examples(),
            "essay_q1_structure": ncwit_strategy_module.format_essay_structure(1),
            "essay_q2_structure": ncwit_strategy_module.format_essay_structure(2),
            "profile_id": input.profile_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ncwit_strategy_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/opportunities/recommend")
async def recommend_opportunity(input: OpportunityRecommendInput):
    """
    Recommend opportunity with Jenny's redirect logic.

    If program cost >= $5000, triggers "Just Be One" redirect:
    "If you want to be an entrepreneur, just be one.
     Don't pay $8000 to learn how to have an idea."

    Returns free alternatives and self-directed options.
    """
    if not settings.enable_agents:
        raise HTTPException(status_code=503, detail="Agents are disabled")

    try:
        # Get student profile
        db = get_supabase_client()
        result = db.table("profiles").select("*").eq("id", input.profile_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        student = result.data

        # Check if redirect is needed
        redirect = program_redirect_module.generate_redirect(input.program, student)

        if redirect.should_redirect:
            # Return redirect response
            return {
                "success": True,
                "redirect_triggered": True,
                "redirect": program_redirect_module.to_dict(redirect),
                "formatted_alternatives": program_redirect_module.format_alternatives(redirect),
                "tier_recommendations": program_redirect_module.get_tier_recommendations(student),
                "profile_id": input.profile_id,
            }
        else:
            # Normal opportunity match
            return {
                "success": True,
                "redirect_triggered": False,
                "program": input.program,
                "recommendation": "Program fits within budget, proceed with application.",
                "profile_id": input.profile_id,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("opportunity_recommend_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/crisis-alchemy")
async def apply_crisis_alchemy(input: CrisisAlchemyInput):
    """
    Apply Jenny's 4-step Crisis Alchemy protocol.

    Protocol:
    1. VALIDATE (2s) - Acknowledge the pain genuinely
    2. ACT (10s) - Provide immediate micro-action
    3. REFRAME (30s) - Shift perspective on situation
    4. CREATE (2min) - Propose pivot that creates opportunity

    Core Principle: Transform every setback into a stronger application story.
    """
    if not settings.enable_crisis_alchemy:
        raise HTTPException(status_code=503, detail="Crisis Alchemy is disabled")

    try:
        # Get student data
        if input.student_data:
            student = input.student_data
        else:
            db = get_supabase_client()
            result = db.table("profiles").select("*").eq("id", input.profile_id).single().execute()
            student = result.data if result.data else {}

        # Detect crisis type
        crisis_type = crisis_alchemy_module.detect_crisis_type(input.crisis_description)

        # Generate response
        response = crisis_alchemy_module.generate_response(
            crisis_type=crisis_type,
            description=input.crisis_description,
            student=student
        )

        return {
            "success": True,
            "crisis_type": crisis_type,
            "response": crisis_alchemy_module.to_dict(response),
            "formatted_response": crisis_alchemy_module.format_crisis_response(response),
            "profile_id": input.profile_id,
        }
    except Exception as e:
        logger.error("crisis_alchemy_error", error=str(e), profile_id=input.profile_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validation/jenny-voice")
async def validate_jenny_voice_text(input: VoiceValidationInput):
    """
    Validate text matches Jenny's voice patterns.

    6-Dimension Scoring (100 points total):
    - Forbidden phrase absence: 25 points
    - Warmth-first opening: 20 points
    - Agency preservation: 20 points
    - Jenny speech patterns: 15 points
    - Exclamation calibration: 10 points
    - Check-in question: 10 points

    Pass threshold: 70/100
    Excellence: 90+/100
    """
    try:
        result = jenny_voice_validator.validate(input.text)

        response = {
            "success": True,
            "passed": result.passing,
            "score": result.score,
            "dimension_scores": result.dimension_scores,
            "forbidden_phrases_found": result.forbidden_found,
            "issues": result.issues,
            "excellence": result.excellence,
        }

        return response
    except Exception as e:
        logger.error("voice_validation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/jenny-techniques")
async def list_jenny_techniques():
    """
    List all available Jenny coaching techniques.

    Returns documentation for each technique with usage patterns.
    """
    return {
        "success": True,
        "techniques": [
            {
                "name": "168-Hour Framework",
                "endpoint": "/agents/time-audit",
                "description": "Calculate available passion hours from weekly schedule",
                "key_insight": "168 - fixed_commitments - social_media = ~26 passion hours/week",
            },
            {
                "name": "2-2-1 Portfolio",
                "endpoint": "/agents/awards/portfolio",
                "description": "Build balanced awards portfolio with probability scoring",
                "key_insight": "2 Likely + 2 Target + 1 Stretch = optimal risk balance",
            },
            {
                "name": "Crisis Alchemy",
                "endpoint": "/agents/crisis-alchemy",
                "description": "Transform setbacks into application strengths",
                "key_insight": "VALIDATE → ACT → REFRAME → CREATE",
            },
            {
                "name": "NCWIT Strategy",
                "endpoint": "/agents/ncwit-strategy",
                "description": "Identity multiplication and vulnerability storytelling",
                "key_insight": "Background + Barrier + Persistence = Compelling Story",
            },
            {
                "name": "Just Be One",
                "endpoint": "/agents/opportunities/recommend",
                "description": "Redirect from expensive programs to self-directed action",
                "key_insight": "Don't pay $8000 to learn how to have an idea",
            },
            {
                "name": "Jenny Voice",
                "endpoint": "/validation/jenny-voice",
                "description": "Validate and fix text to match Jenny's coaching voice",
                "key_insight": "Warmth-first, agency-preserving, question-ending",
            },
        ],
    }


# =====================================================
# Notification Endpoints
# =====================================================

class MarkNotificationInput(BaseModel):
    notification_id: str
    read: bool = True


@app.get("/notifications/{profile_id}")
async def get_notifications(
    profile_id: str,
    unread_only: bool = False,
    limit: int = 50
):
    """
    Get notifications for a profile.

    Args:
        profile_id: The profile UUID
        unread_only: Only return unread notifications
        limit: Max notifications to return (default 50)
    """
    try:
        db = get_supabase_client()

        query = db.table("notifications").select("*").eq(
            "profile_id", profile_id
        ).order("created_at", desc=True).limit(limit)

        if unread_only:
            query = query.eq("read", False)

        result = query.execute()

        return {
            "success": True,
            "notifications": result.data if result.data else [],
            "count": len(result.data) if result.data else 0,
            "unread_count": len([n for n in (result.data or []) if not n.get("read")]),
        }
    except Exception as e:
        logger.error("get_notifications_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notifications/mark-read")
async def mark_notification_read(input: MarkNotificationInput):
    """
    Mark a notification as read/unread.
    """
    try:
        db = get_supabase_client()

        update_data = {"read": input.read}
        if input.read:
            from datetime import datetime
            update_data["read_at"] = datetime.utcnow().isoformat()

        result = db.table("notifications").update(update_data).eq(
            "id", input.notification_id
        ).execute()

        return {
            "success": True,
            "notification_id": input.notification_id,
            "read": input.read,
        }
    except Exception as e:
        logger.error("mark_notification_error", notification_id=input.notification_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notifications/{profile_id}/mark-all-read")
async def mark_all_notifications_read(profile_id: str):
    """
    Mark all notifications for a profile as read.
    """
    try:
        db = get_supabase_client()
        from datetime import datetime

        result = db.table("notifications").update({
            "read": True,
            "read_at": datetime.utcnow().isoformat()
        }).eq("profile_id", profile_id).eq("read", False).execute()

        return {
            "success": True,
            "profile_id": profile_id,
            "marked_count": len(result.data) if result.data else 0,
        }
    except Exception as e:
        logger.error("mark_all_read_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notifications/{profile_id}/count")
async def get_notification_count(profile_id: str):
    """
    Get unread notification count for a profile.

    Lightweight endpoint for badge display.
    """
    try:
        db = get_supabase_client()

        result = db.table("notifications").select(
            "id", count="exact"
        ).eq("profile_id", profile_id).eq("read", False).execute()

        return {
            "success": True,
            "profile_id": profile_id,
            "unread_count": result.count if result.count else 0,
        }
    except Exception as e:
        logger.error("notification_count_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Workflow Endpoints (Proactive Engagement)
# =====================================================

class WorkflowRunInput(BaseModel):
    workflow_name: str


class WorkflowPauseInput(BaseModel):
    workflow_name: str


@app.get("/workflows/status")
async def get_workflow_status():
    """
    Get status of all registered workflows.

    Returns scheduler state and next run times.
    """
    if not workflow_runner:
        raise HTTPException(status_code=503, detail="Workflow runner not initialized")

    try:
        return workflow_runner.get_status()
    except Exception as e:
        logger.error("workflow_status_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflows/run")
async def run_workflow(input: WorkflowRunInput, background_tasks: BackgroundTasks):
    """
    Manually trigger a specific workflow.

    Runs immediately regardless of schedule.
    """
    if not workflow_runner:
        raise HTTPException(status_code=503, detail="Workflow runner not initialized")

    workflow_name = input.workflow_name

    if workflow_name not in workflow_runner.workflows:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_name}' not found. Available: {list(workflow_runner.workflows.keys())}"
        )

    try:
        result = await workflow_runner.run_now(workflow_name)
        return {
            "success": True,
            "workflow": workflow_name,
            "result": result.to_dict() if result else None,
        }
    except Exception as e:
        logger.error("workflow_run_error", workflow=workflow_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflows/run-all")
async def run_all_workflows():
    """
    Manually trigger all workflows.

    Useful for testing or initial population.
    """
    if not workflow_runner:
        raise HTTPException(status_code=503, detail="Workflow runner not initialized")

    try:
        results = await workflow_runner.run_all_now()
        return {
            "success": True,
            "results": {name: result.to_dict() for name, result in results.items()},
        }
    except Exception as e:
        logger.error("workflow_run_all_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflows/pause")
async def pause_workflow(input: WorkflowPauseInput):
    """
    Pause a workflow's scheduled execution.

    Workflow can still be run manually.
    """
    if not workflow_runner:
        raise HTTPException(status_code=503, detail="Workflow runner not initialized")

    try:
        success = workflow_runner.pause_workflow(input.workflow_name)
        return {"success": success, "workflow": input.workflow_name, "status": "paused"}
    except Exception as e:
        logger.error("workflow_pause_error", workflow=input.workflow_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflows/resume")
async def resume_workflow(input: WorkflowPauseInput):
    """
    Resume a paused workflow.
    """
    if not workflow_runner:
        raise HTTPException(status_code=503, detail="Workflow runner not initialized")

    try:
        success = workflow_runner.resume_workflow(input.workflow_name)
        return {"success": success, "workflow": input.workflow_name, "status": "resumed"}
    except Exception as e:
        logger.error("workflow_resume_error", workflow=input.workflow_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/runs")
async def get_workflow_runs(
    workflow_name: Optional[str] = None,
    limit: int = 20
):
    """
    Get recent workflow run history.

    Args:
        workflow_name: Optional filter by workflow
        limit: Max results (default 20)
    """
    try:
        db = get_supabase_client()

        query = db.table("workflow_runs").select("*").order(
            "run_at", desc=True
        ).limit(limit)

        if workflow_name:
            query = query.eq("workflow_name", workflow_name)

        result = query.execute()

        return {
            "success": True,
            "runs": result.data if result.data else [],
            "count": len(result.data) if result.data else 0,
        }
    except Exception as e:
        logger.error("get_workflow_runs_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/deadlines/{profile_id}")
async def get_profile_deadlines(profile_id: str, days_ahead: int = 30):
    """
    Get upcoming deadlines for a profile.

    Returns opportunities and awards with deadlines in the next N days.
    """
    try:
        from workflows.deadline_alerts import DeadlineAlertWorkflow

        db = get_supabase_client()
        workflow = DeadlineAlertWorkflow(db)

        deadlines = await workflow.get_upcoming_deadlines(profile_id, days_ahead)

        return {
            "success": True,
            "profile_id": profile_id,
            "days_ahead": days_ahead,
            "deadlines": deadlines,
            "count": len(deadlines),
        }
    except Exception as e:
        logger.error("get_deadlines_error", profile_id=profile_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Evaluation Endpoints
# =====================================================

class EvaluationRunInput(BaseModel):
    tags: Optional[str] = None
    difficulty: Optional[str] = None
    max_examples: Optional[int] = None


@app.get("/evaluation/golden")
async def list_golden_examples(
    tags: Optional[str] = None,
    difficulty: Optional[str] = None
):
    """
    List available golden examples.

    Args:
        tags: Comma-separated tags to filter by
        difficulty: Difficulty tier (easy, medium, hard)
    """
    try:
        db = get_supabase_client()
        loader = GoldenDatasetLoader(db)

        if tags:
            examples = await loader.load_by_tags(tags.split(','))
        elif difficulty:
            examples = await loader.load_by_difficulty(difficulty)
        else:
            examples = await loader.load_all()

        return {
            "success": True,
            "count": len(examples),
            "examples": [
                {
                    "id": e.id,
                    "profile_id": e.profile_id,
                    "difficulty": e.difficulty_tier,
                    "tags": e.tags
                }
                for e in examples
            ]
        }
    except Exception as e:
        logger.error("list_golden_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/golden/{golden_id}")
async def get_golden_example(golden_id: str):
    """Get a specific golden example by ID."""
    try:
        db = get_supabase_client()
        loader = GoldenDatasetLoader(db)

        example = await loader.get_by_id(golden_id)
        if not example:
            raise HTTPException(status_code=404, detail="Golden example not found")

        return {
            "success": True,
            "example": example.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_golden_error", golden_id=golden_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/golden-stats")
async def get_golden_stats():
    """Get statistics about the golden dataset."""
    try:
        db = get_supabase_client()
        loader = GoldenDatasetLoader(db)

        stats = await loader.get_stats()
        return {"success": True, **stats}
    except Exception as e:
        logger.error("golden_stats_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluation/run/{agent_name}")
async def run_evaluation(
    agent_name: str,
    input: EvaluationRunInput
):
    """
    Run evaluation for an agent against golden examples.

    Args:
        agent_name: Name of the agent to evaluate (narrative, awards, crisis)
        input: Evaluation parameters (tags, difficulty, max_examples)
    """
    try:
        db = get_supabase_client()
        pipeline = EvaluationPipeline(db, agent_version=settings.service_version)

        # Define agent callables
        async def narrative_callable(profile):
            return await narrative_synthesis_agent.synthesize_from_profile(profile)

        async def awards_callable(profile):
            # Would call AwardsAgent - placeholder for now
            return await awards_agent.match_from_profile(profile)

        agent_map = {
            "narrative": narrative_callable,
            # Add more agents as needed
        }

        if agent_name not in agent_map:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown agent: {agent_name}. Available: {list(agent_map.keys())}"
            )

        results = await pipeline.run_full_evaluation(
            agent_name=agent_name,
            agent_callable=agent_map[agent_name],
            tags=input.tags.split(',') if input.tags else None,
            difficulty=input.difficulty,
            max_examples=input.max_examples
        )

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error("run_evaluation_error", agent_name=agent_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/runs")
async def get_evaluation_runs(
    agent_version: Optional[str] = None,
    run_id: Optional[str] = None,
    limit: int = 20
):
    """
    Get recent evaluation runs.

    Args:
        agent_version: Filter by agent version
        run_id: Filter by specific run ID
        limit: Max results to return
    """
    try:
        db = get_supabase_client()

        query = db.table('evaluation_runs').select('*').order(
            'created_at', desc=True
        ).limit(limit)

        if agent_version:
            query = query.eq('agent_version', agent_version)

        if run_id:
            query = query.eq('run_id', run_id)

        result = query.execute()

        return {
            "success": True,
            "runs": result.data if result.data else [],
            "count": len(result.data) if result.data else 0,
        }
    except Exception as e:
        logger.error("get_evaluation_runs_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/runs/{run_id}")
async def get_evaluation_run_details(run_id: str):
    """Get detailed results of a specific evaluation run."""
    try:
        db = get_supabase_client()

        result = db.table('evaluation_runs').select('*').eq(
            'run_id', run_id
        ).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Run not found")

        # Calculate aggregate stats
        scores = [r['overall_score'] for r in result.data]
        passed = sum(1 for r in result.data if r.get('passed'))

        return {
            "success": True,
            "run_id": run_id,
            "examples_count": len(result.data),
            "passed": passed,
            "failed": len(result.data) - passed,
            "pass_rate": passed / len(result.data) if result.data else 0,
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "results": result.data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_run_details_error", run_id=run_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/trends")
async def get_evaluation_trends(days: int = 30):
    """
    Get evaluation score trends over time.

    Args:
        days: Number of days to look back (default 30)
    """
    try:
        db = get_supabase_client()
        pipeline = EvaluationPipeline(db)

        trends = await pipeline.get_historical_trends(days)
        return {"success": True, **trends}
    except Exception as e:
        logger.error("get_trends_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/compare")
async def compare_agent_versions(
    version_a: str,
    version_b: str
):
    """
    Compare evaluation results between two agent versions.

    Args:
        version_a: First version to compare
        version_b: Second version to compare
    """
    try:
        db = get_supabase_client()
        pipeline = EvaluationPipeline(db)

        comparison = await pipeline.compare_versions(version_a, version_b)
        return {"success": True, **comparison}
    except Exception as e:
        logger.error("compare_versions_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# v13.2 Memory & Handoff Endpoints
# =====================================================

from fastapi import APIRouter, Query, Depends

v13_router = APIRouter(prefix="/v13", tags=["v13"])

# v13.2 Memory Manager (initialized on startup)
_v13_memory_manager = None


async def get_v13_memory():
    """Dependency to get v13 memory manager."""
    global _v13_memory_manager
    if _v13_memory_manager is None:
        # Lazy init on first request
        try:
            from agents.agents.core import MemoryManager
            _v13_memory_manager = MemoryManager(
                redis_client=None,  # TODO: Initialize from settings
                supabase_client=get_supabase_client(),
                embedding_model=None,  # TODO: Add embeddings
            )
        except Exception as e:
            logger.error("v13_memory_init_error", error=str(e))
            raise HTTPException(status_code=503, detail="v13 Memory manager not available")
    return _v13_memory_manager


@v13_router.get("/health")
async def v13_health_check():
    """v15.0 Health check with quality thresholds."""
    try:
        from agents.agents.core import QualityThresholds
        return {
            "status": "healthy",
            "version": "15.0.0",
            "react_enabled": True,
            "memory_enabled": True,
            "hitl_enabled": True,
            "thresholds": {
                "min_quality": QualityThresholds.MIN_QUALITY_SCORE,
                "min_voice": QualityThresholds.MIN_VOICE_SCORE,
                "min_golden": QualityThresholds.MIN_GOLDEN_SIMILARITY,
                "max_cycles": QualityThresholds.MAX_REACT_CYCLES,
            }
        }
    except ImportError:
        # Return healthy status for basic API functionality
        # ReAct advanced features are optional
        return {
            "status": "healthy",
            "version": "15.0.0",
            "react_enabled": False,
            "memory_enabled": False,
            "hitl_enabled": False,
            "note": "Running in basic mode (ReAct features not loaded)"
        }


class V13HandoffRequest(BaseModel):
    from_agent: str
    to_agent: str
    profile_id: str
    context: Dict[str, Any]
    task: str
    reason: str
    priority: str = "normal"


@v13_router.post("/memory/handoff")
async def create_v13_handoff(request: V13HandoffRequest):
    """Create agent handoff (v13.2)."""
    memory = await get_v13_memory()

    handoff = await memory.create_handoff(
        from_agent=request.from_agent,
        to_agent=request.to_agent,
        profile_id=request.profile_id,
        context=request.context,
        task=request.task,
        reason=request.reason,
        priority=request.priority,
    )

    if not handoff:
        raise HTTPException(status_code=503, detail="Handoffs disabled - Redis not configured")

    return {
        "success": True,
        "from_agent": handoff.from_agent,
        "to_agent": handoff.to_agent,
        "profile_id": handoff.profile_id,
        "task": handoff.task,
        "timestamp": handoff.timestamp.isoformat(),
    }


@v13_router.get("/memory/handoff/{profile_id}/{to_agent}")
async def get_v13_handoff(
    profile_id: str,
    to_agent: str,
    from_agent: Optional[str] = None,
):
    """Get latest handoff to an agent (v13.2)."""
    memory = await get_v13_memory()
    handoff = await memory.get_handoff(profile_id, to_agent, from_agent)

    if not handoff:
        return {"error": "No handoff found"}

    return {
        "from_agent": handoff.from_agent,
        "to_agent": handoff.to_agent,
        "profile_id": handoff.profile_id,
        "task": handoff.task,
        "reason": handoff.reason,
        "context": handoff.context,
        "priority": handoff.priority,
        "timestamp": handoff.timestamp.isoformat(),
    }


@v13_router.get("/knowledge/search")
async def search_v13_coaching_knowledge(
    query: str,
    category: Optional[str] = None,
    archetype: Optional[str] = None,
    limit: int = Query(default=5, ge=1, le=20),
):
    """Search Jenny's coaching knowledge base (v13.2)."""
    memory = await get_v13_memory()

    results = await memory.search_coaching_knowledge(
        query=query,
        category=category,
        archetype=archetype,
        limit=limit,
    )

    return {
        "query": query,
        "category": category,
        "results": results,
        "count": len(results),
    }


@v13_router.get("/profile/{profile_id}/evolution")
async def get_v13_profile_evolution(
    profile_id: str,
    days: int = Query(default=90, ge=1, le=365),
):
    """Get profile evolution timeline (v13.2)."""
    memory = await get_v13_memory()

    if not memory.snapshots:
        return {"error": "Snapshots disabled"}

    snapshots = await memory.snapshots.get_evolution_timeline(
        profile_id=profile_id,
        limit=50,
    )

    return {
        "profile_id": profile_id,
        "days": days,
        "snapshots": [s.to_dict() for s in snapshots],
        "count": len(snapshots),
    }


@v13_router.get("/interactions/{profile_id}/recall")
async def recall_v13_interactions(
    profile_id: str,
    query: str,
    limit: int = Query(default=5, ge=1, le=20),
):
    """Semantic search for past interactions (v13.2)."""
    memory = await get_v13_memory()

    if not memory.interactions:
        return {"error": "Interaction memory disabled"}

    interactions = await memory.interactions.recall_similar_interactions(
        profile_id=profile_id,
        query=query,
        limit=limit,
    )

    return {
        "profile_id": profile_id,
        "query": query,
        "interactions": [i.to_dict() for i in interactions],
        "count": len(interactions),
    }


@v13_router.get("/interactions/{profile_id}/recent")
async def get_v13_recent_interactions(
    profile_id: str,
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get recent interactions (v13.2)."""
    memory = await get_v13_memory()

    if not memory.interactions:
        return {"error": "Interaction memory disabled"}

    interactions = await memory.interactions.get_recent_interactions(
        profile_id=profile_id,
        limit=limit,
    )

    return {
        "profile_id": profile_id,
        "interactions": [i.to_dict() for i in interactions],
        "count": len(interactions),
    }


# Register v13 router
app.include_router(v13_router)


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
