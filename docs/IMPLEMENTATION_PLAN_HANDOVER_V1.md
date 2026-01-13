# Incremental Implementation Plan
## Handover Package v1.0 on Existing Architecture

**Version:** 1.0
**Date:** January 2026
**Approach:** Incremental enhancement of autonomous ReAct agents
**Principle:** NO breaking changes, continuous evolution

---

# TABLE OF CONTENTS

1. [Implementation Philosophy](#1-implementation-philosophy)
2. [Architecture Preservation Strategy](#2-architecture-preservation-strategy)
3. [Phase 1: Foundation & Contracts](#3-phase-1-foundation--contracts)
4. [Phase 2: EC Agent Implementation](#4-phase-2-ec-agent-implementation)
5. [Phase 3: Awards Agent Enhancement](#5-phase-3-awards-agent-enhancement)
6. [Phase 4: Summer Programs Enhancement](#6-phase-4-summer-programs-enhancement)
7. [Phase 5: Orchestration Integration](#7-phase-5-orchestration-integration)
8. [Phase 6: Testing & Validation](#8-phase-6-testing--validation)
9. [Third-Party Integration Points](#9-third-party-integration-points)
10. [Risk Mitigation & Rollback](#10-risk-mitigation--rollback)
11. [Success Criteria](#11-success-criteria)

---

# 1. IMPLEMENTATION PHILOSOPHY

## 1.1 Core Principles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION PRINCIPLES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. PRESERVE existing ReAct framework - DO NOT replace                       │
│     └── All new agents extend BaseAgent with ReAct cycle                    │
│     └── Quality gates (70/70/0.6) remain enforced                           │
│     └── 3-tier memory architecture unchanged                                │
│                                                                              │
│  2. ENHANCE autonomous agent capabilities - DO NOT hardcode                  │
│     └── Agents make decisions based on data, not if/else trees              │
│     └── Intelligence types are configurable, not baked in                   │
│     └── All thresholds from config, not magic numbers                       │
│                                                                              │
│  3. INCREMENTAL delivery - DO NOT big-bang                                   │
│     └── Each phase is independently deployable                              │
│     └── Backward compatibility at each step                                 │
│     └── Feature flags for gradual rollout                                   │
│                                                                              │
│  4. DATA-DRIVEN decisions - DO NOT assume                                    │
│     └── Databases seeded with real Jenny intelligence                       │
│     └── Probability calculations based on historical data                   │
│     └── Validation against Huda golden reference                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 1.2 What We PRESERVE

| Component | Current State | Preservation Strategy |
|-----------|---------------|----------------------|
| ReAct Framework | `BaseAgent` with reason/act/observe | All new agents extend BaseAgent |
| Quality Gates | 70/70/0.6 thresholds | Reuse `QualityGate` class |
| 3-Tier Memory | Working/Redis/Supabase | Use existing `MemoryManager` |
| HITL Workflow | Crisis approval pattern | Extend to new agent outputs |
| Event Publishing | `publish_event()` pattern | Add new event types |
| State Versioning | Audit trail with `created_by` | Apply to all new agents |
| Execution Agent | 950 lines, fully implemented | Keep unchanged |
| Narrative Synthesis | `gameplan_narrative.py` | Enhance, don't replace |

## 1.3 What We ENHANCE

| Component | Current State | Enhancement Strategy |
|-----------|---------------|---------------------|
| Game Plan Agent | Partial orchestrator | Add specialist invocation |
| Awards Agent | Stub implementation | Full implementation + database |
| Opportunity Agent | Basic fit scoring | Rename + TYPE-028/029/030 |
| Narrative Module | FirstPrinciplePassion | Add cookie-cutter + authenticity |

## 1.4 What We CREATE

| Component | Purpose | Approach |
|-----------|---------|----------|
| EC Agent | Portfolio + narrative + impact | New agent extending BaseAgent |
| Intelligence Types | TYPE-013 through TYPE-030 | New `/intelligence/` directory |
| Matching Engine | Awards + programs scoring | New `/matching/` directory |
| Databases | 200 awards + 150 programs | JSON seeds + Supabase tables |
| Handoff Contracts | Type-safe agent communication | New `/models/contracts.py` |

---

# 2. ARCHITECTURE PRESERVATION STRATEGY

## 2.1 BaseAgent Extension Pattern

All new agents MUST extend the existing `BaseAgent` class:

```python
# /agents/agents/extracurriculars_agent.py
from .base_agent import BaseAgent
from ..config import settings

class ExtracurricularsAgent(BaseAgent):
    """
    EC Agent - Extends BaseAgent with ReAct framework.

    PRESERVES:
    - ReAct cycle (reason → act → observe)
    - Quality gates (70/70/0.6)
    - 3-tier memory
    - State versioning
    - Event publishing

    ADDS:
    - TYPE-013: Portfolio Optimization
    - TYPE-014: Narrative Synthesis (enhanced)
    - TYPE-015: Impact Engineering
    """

    def __init__(self):
        super().__init__(agent_name="ec_agent")
        self.portfolio_optimizer = PortfolioOptimizer()
        self.narrative_synthesizer = NarrativeSynthesizer()  # Enhanced
        self.impact_assessor = ImpactAssessor()

    async def analyze(
        self,
        student_profile: Dict,
        existing_activities: List[Dict],
        four_pillars: Dict,
        weak_spots: List[Dict]
    ) -> ECAgentOutput:
        """
        Main entry point - uses ReAct framework from BaseAgent.
        """
        return await self.execute_react_cycle(
            task="analyze_extracurriculars",
            context={
                "profile": student_profile,
                "activities": existing_activities,
                "four_pillars": four_pillars,
                "weak_spots": weak_spots,
            }
        )

    async def reason(self, task: str, context: Dict) -> Thought:
        """ReAct REASON step - analyze what needs to be done."""
        # ... reasoning logic
        pass

    async def act(self, action: Action) -> ActionResult:
        """ReAct ACT step - execute intelligence types."""
        if action.type == "portfolio_optimization":
            return await self.portfolio_optimizer.optimize(action.params)
        elif action.type == "narrative_synthesis":
            return await self.narrative_synthesizer.synthesize(action.params)
        elif action.type == "impact_assessment":
            return await self.impact_assessor.assess(action.params)

    async def observe(self, result: ActionResult) -> Observation:
        """ReAct OBSERVE step - process results."""
        # ... observation logic
        pass
```

## 2.2 Configuration-Driven Intelligence

All thresholds, weights, and constants MUST come from configuration:

```python
# /agents/config/intelligence_config.py
from pydantic import BaseSettings

class IntelligenceConfig(BaseSettings):
    """
    Centralized configuration for all intelligence types.
    NO HARDCODED VALUES - all configurable.
    """

    # TYPE-013: Portfolio Optimization
    tier_classification: dict = {
        "T1": {"min_scope": "national", "keywords": ["founder", "ISEF", "RSI"]},
        "T2": {"min_scope": "regional", "roles": ["president", "captain"]},
        "T3": {"min_scope": "school", "min_engagement": "moderate"},
        "T4": {"min_scope": "local", "min_engagement": "basic"},
    }

    slot_strategy: dict = {
        "flagship": {"count": (2, 3), "min_hours": 8, "tiers": ["T1", "T2"]},
        "supporting": {"count": (3, 4), "min_hours": 4, "tiers": ["T2", "T3"]},
        "validation": {"count": (2, 3), "min_hours": 0, "tiers": ["T2", "T3"]},
        "service": {"count": 2, "min_hours": 2, "tiers": ["T3", "T4"]},
    }

    # TYPE-014: Narrative Synthesis
    cookie_cutter_patterns: dict = {
        "asian_male_stem": {"triggers": ["asian", "male", "cs", "debate"], "severity": 0.40},
        "generic_stem_nhs": {"triggers": ["stem_club", "nhs", "hospital"], "severity": 0.25},
        "zero_self_initiated": {"triggers": ["no_self_started"], "severity": 0.40},
        "generic_memberships": {"triggers": ["3+_clubs_no_leadership"], "severity": 0.25},
    }

    cookie_cutter_thresholds: dict = {
        "COOKIE_CUTTER": 0.6,
        "GENERIC": 0.4,
        "DIFFERENTIATED": 0.2,
        "UNIQUE": 0.0,
    }

    # TYPE-015: Impact Engineering
    evidence_ladder: dict = {
        "M0": {"name": "Built", "evidence": "project_exists"},
        "M1": {"name": "Used", "evidence": "user_count > 0"},
        "M2": {"name": "Measured", "evidence": "quantified_outcomes"},
        "M3": {"name": "Dollars", "evidence": "amount >= 1000"},
        "M4": {"name": "Media", "evidence": "external_validation"},
    }

    portfolio_health_weights: dict = {
        "baseline": 50,
        "M0_penalty": -10,
        "M2_plus_bonus": 15,
        "M4_bonus": 25,
    }

    # Awards Agent
    demographic_multipliers: dict = {
        "female_in_stem": 1.3,
        "male_in_nursing": 1.4,
        "underrepresented_minority": 1.2,
        "first_generation": 1.15,
        "rural_student": 1.3,
        "small_town": 1.2,
        "urban_saturated": 0.85,
        "immigrant_story": 1.15,
        "financial_hardship": 1.1,
    }

    portfolio_strategy: dict = {
        "north_star_count": 2,
        "building_block_count": 2,
        "context_leverage_count": 1,
        "bombardment_multiplier": 3.0,
        "expected_win_rate": 0.35,
    }

    # Summer Programs Agent
    program_scoring_weights: dict = {
        "alignment": 0.40,
        "selectivity_fit": 0.30,
        "impact": 0.30,
        "feasibility": 0.20,
    }

    reach_match_safety_ratio: dict = {
        "reach": 2,
        "match": 3,
        "safety": 2,
    }

    class Config:
        env_prefix = "IVYQUEST_INTELLIGENCE_"

# Singleton instance
intelligence_config = IntelligenceConfig()
```

## 2.3 Database Abstraction Layer

Database access MUST go through an abstraction layer for flexibility:

```python
# /agents/db/awards_repository.py
from typing import List, Optional
from .base_repository import BaseRepository

class AwardsRepository(BaseRepository):
    """
    Awards database abstraction.

    Supports:
    - Local JSON (development)
    - Supabase (production)
    - Future: External APIs

    NEVER hardcode awards data in agents.
    """

    def __init__(self, source: str = "supabase"):
        self.source = source
        if source == "json":
            self._load_json()
        elif source == "supabase":
            self._connect_supabase()

    async def get_all_awards(self) -> List[Award]:
        """Get all awards from database."""
        pass

    async def get_eligible_awards(
        self,
        profile: StudentProfile
    ) -> List[Award]:
        """
        Get awards the student is eligible for.
        Applies hard eligibility filters.
        """
        all_awards = await self.get_all_awards()
        return [
            award for award in all_awards
            if self._check_eligibility(profile, award)
        ]

    async def get_awards_by_category(
        self,
        category: str
    ) -> List[Award]:
        """Get awards by category (Research, STEM, Arts, etc.)"""
        pass

    async def get_awards_by_tier(
        self,
        tier: str  # "North_Star", "Building_Block", "Quick_Win"
    ) -> List[Award]:
        """Get awards by Jenny's tier classification."""
        pass

    def _check_eligibility(
        self,
        profile: StudentProfile,
        award: Award
    ) -> bool:
        """
        Check hard eligibility requirements.
        Returns False if ANY hard requirement fails.
        """
        # Grade check
        if profile.grade < award.eligibility.grade_range.min:
            return False
        if profile.grade > award.eligibility.grade_range.max:
            return False

        # Gender check
        if award.eligibility.demographic.gender != "any":
            if profile.gender not in award.eligibility.demographic.gender:
                return False

        # Citizenship check
        if award.eligibility.citizenship:
            if profile.citizenship not in award.eligibility.citizenship:
                return False

        # Geographic check
        if award.eligibility.geographic.states:
            if profile.state not in award.eligibility.geographic.states:
                return False

        return True
```

---

# 3. PHASE 1: FOUNDATION & CONTRACTS

## 3.1 Overview

| Duration | Deliverables | Dependencies |
|----------|--------------|--------------|
| Week 1 | Contracts, schemas, config, initial seeding | None |

## 3.2 Task Breakdown

### Task 1.1: Create Handoff Contracts

**File:** `/agents/models/contracts.py`

```python
"""
Type-safe handoff contracts between agents.

These contracts define the EXACT shape of data
passed between agents. Any change requires
version bump and migration.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# === ENUMS ===

class Tier(str, Enum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"

class JennyTier(str, Enum):
    NORTH_STAR = "North_Star"
    BUILDING_BLOCK = "Building_Block"
    QUICK_WIN = "Quick_Win"
    PARTICIPATION = "Participation"

class SlotType(str, Enum):
    FLAGSHIP = "flagship"
    SUPPORTING = "supporting"
    VALIDATION = "validation"
    SERVICE = "service"

class EvidenceLevel(str, Enum):
    M0 = "M0"  # Built
    M1 = "M1"  # Used
    M2 = "M2"  # Measured
    M3 = "M3"  # Dollars
    M4 = "M4"  # Media

class CookieCutterDiagnosis(str, Enum):
    UNIQUE = "UNIQUE"
    DIFFERENTIATED = "DIFFERENTIATED"
    GENERIC = "GENERIC"
    COOKIE_CUTTER = "COOKIE_CUTTER"


# === EC AGENT CONTRACTS ===

class ClassifiedActivity(BaseModel):
    """Activity with tier classification."""
    activity_id: str
    name: str
    tier: Tier
    slot_type: SlotType
    hours_per_week: float
    evidence_level: EvidenceLevel
    identity_alignment: float  # 0-1


class PortfolioOptimizationOutput(BaseModel):
    """TYPE-013 output."""
    classified_activities: List[ClassifiedActivity]
    slot_optimization: Dict[SlotType, List[ClassifiedActivity]]
    tier_summary: Dict[str, Any]
    gaps: List[Dict[str, Any]]
    overcommitment: Optional[Dict[str, Any]]


class IdentitySynthesis(BaseModel):
    """Core identity output - passed to Awards + Programs."""
    label: str  # "Muslim Game Developer for AI Education"
    confidence: float  # 0-1
    themes: List[str]
    first_principle: str  # "BUILDER", "STORYTELLER", etc.
    supporting_activities: List[str]
    orphaned_activities: List[str]


class NarrativeSynthesisOutput(BaseModel):
    """TYPE-014 output."""
    identity: IdentitySynthesis
    web: Dict[str, Any]
    cookie_cutter: Dict[str, Any]
    authenticity: Dict[str, Any]


class ImpactAssessmentOutput(BaseModel):
    """TYPE-015 output."""
    activities_by_level: Dict[EvidenceLevel, List[Dict]]
    flagship_progress: List[Dict]
    portfolio_health: Dict[str, Any]
    recommendations: List[str]


class ECAgentInput(BaseModel):
    """Input contract for EC Agent."""
    student_id: str
    student_profile: Dict[str, Any]
    demographic_data: Dict[str, Any]
    existing_activities: List[Dict[str, Any]]
    four_pillars: Dict[str, Any]
    weak_spots: List[Dict[str, Any]]
    target_schools: List[Dict[str, Any]]
    available_hours_weekly: float = 20.0


class ECAgentOutput(BaseModel):
    """Output contract for EC Agent."""
    student_id: str
    portfolio_audit: PortfolioOptimizationOutput
    narrative_synthesis: NarrativeSynthesisOutput
    impact_assessment: ImpactAssessmentOutput
    priority_actions: List[Dict[str, Any]]
    processing_time_ms: int


# === AWARDS AGENT CONTRACTS ===

class AwardRecommendation(BaseModel):
    """Single award recommendation."""
    award_id: str
    name: str
    jenny_tier: JennyTier
    probability: float  # 0-1
    narrative_alignment: float  # 0-1
    eligibility_status: str
    application_hours: int
    deadline: Optional[datetime]
    rationale: str


class AwardsPortfolio(BaseModel):
    """2-2-1 portfolio structure."""
    north_star_awards: List[AwardRecommendation]
    building_block_awards: List[AwardRecommendation]
    context_leverage_awards: List[AwardRecommendation]
    quick_win_awards: List[AwardRecommendation]


class AwardsAgentInput(BaseModel):
    """Input contract for Awards Agent."""
    student_id: str
    student_profile: Dict[str, Any]
    identity_synthesis: IdentitySynthesis  # FROM EC AGENT
    existing_awards: List[str]
    weak_spots: List[Dict[str, Any]]
    target_schools: List[Dict[str, Any]]
    cri_score: float
    archetype: str
    max_awards_to_apply: int = 15


class AwardsAgentOutput(BaseModel):
    """Output contract for Awards Agent."""
    student_id: str
    portfolio: AwardsPortfolio
    portfolio_summary: Dict[str, Any]
    bombardment_plan: Dict[str, Any]
    ineligible_awards: List[Dict[str, Any]]
    timeline: Dict[str, List[AwardRecommendation]]
    processing_time_ms: int


# === SUMMER PROGRAMS AGENT CONTRACTS ===

class ProgramRecommendation(BaseModel):
    """Single program recommendation."""
    program_id: str
    name: str
    institution: str
    tier: Tier
    fit_score: float
    roi_score: float
    alignment_reason: str
    total_cost: int
    estimated_cost_with_aid: int
    deadline: Optional[datetime]


class SummerProgramsAgentInput(BaseModel):
    """Input contract for Summer Programs Agent."""
    student_id: str
    student_profile: Dict[str, Any]
    identity_synthesis: IdentitySynthesis  # FROM EC AGENT
    four_pillars: Dict[str, Any]
    interests: List[str]
    available_summer_weeks: int = 10
    budget_constraint: Optional[int]
    residential_ok: bool = True
    existing_essays: Optional[Dict[str, str]]


class SummerProgramsAgentOutput(BaseModel):
    """Output contract for Summer Programs Agent."""
    student_id: str
    program_recommendations: Dict[str, Any]
    application_strategy: Dict[str, Any]
    cost_benefit: Dict[str, Any]
    priority_programs: Dict[str, List[str]]
    processing_time_ms: int


# === GAME PLAN OUTPUT CONTRACT ===

class GamePlanOutput(BaseModel):
    """Final Game Plan output."""
    game_plan_id: str
    student_id: str
    version: int

    # Target Profile
    target_activities: List[ClassifiedActivity]
    target_awards: List[AwardRecommendation]
    target_programs: List[ProgramRecommendation]

    # Narrative
    narrative: Dict[str, Any]
    four_pillars: Dict[str, Any]

    # Roadmap
    phases: List[Dict[str, Any]]
    priority_actions: List[Dict[str, Any]]

    # Metadata
    confidence_score: float
    created_at: datetime
    next_review_date: datetime
```

### Task 1.2: Create Intelligence Configuration

**File:** `/agents/config/intelligence_config.py`

(See Section 2.2 above)

### Task 1.3: Create Database Schemas

**File:** `/agents/db/schemas/awards_schema.py`

```python
"""
Awards database schema - Supabase table definition.
"""

AWARDS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS awards (
    -- Identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    award_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    short_name TEXT,
    aliases TEXT[],

    -- Categorization
    category TEXT NOT NULL,
    subcategory TEXT,
    tags TEXT[],

    -- Award Structure
    award_type TEXT NOT NULL,  -- 'competition', 'application', 'nomination'
    levels JSONB,
    tiers JSONB,
    team_vs_individual TEXT,
    team_size JSONB,

    -- Eligibility (CRITICAL)
    eligibility JSONB NOT NULL,
    -- Structure: {
    --   grade_range: {min, max},
    --   citizenship: [],
    --   geographic: {scope, states},
    --   demographic: {gender, underrepresented, first_gen, low_income},
    --   prerequisites: {prior_awards, courses, skills}
    -- }

    -- Logistics
    logistics JSONB,
    -- Structure: {website, fee, format, recommendation_letters}

    -- Timeline
    timeline JSONB,
    -- Structure: {frequency, registration, competition_rounds, results}

    -- Selectivity
    selectivity JSONB,
    -- Structure: {participants, winners, acceptance_rate, difficulty}

    -- Preparation
    preparation JSONB,
    -- Structure: {prep_months, start_grade, skills, resources}

    -- Jenny Classification (CRITICAL)
    jenny_tier TEXT NOT NULL,  -- 'North_Star', 'Building_Block', 'Quick_Win'
    jenny_rationale TEXT,
    archetype_fit JSONB,  -- {archetype: fit_score}
    demographic_saturation JSONB,  -- {demo_key: saturation_level}
    college_impact JSONB,
    jenny_notes TEXT,
    success_patterns TEXT[],
    common_mistakes TEXT[],

    -- Relationships
    relationships JSONB,
    -- Structure: {prerequisites, feeds_into, alternatives, complements}
    win_cascade_position JSONB,

    -- Matching
    matching_weights JSONB,
    addresses_weak_spots TEXT[],

    -- Metadata
    source TEXT[],
    last_verified TIMESTAMPTZ,
    confidence_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_awards_category ON awards(category);
CREATE INDEX idx_awards_jenny_tier ON awards(jenny_tier);
CREATE INDEX idx_awards_eligibility ON awards USING GIN(eligibility);
"""
```

### Task 1.4: Seed Core Awards (50)

**File:** `/agents/databases/seeds/awards_core.json`

```json
{
  "metadata": {
    "version": "1.0",
    "count": 50,
    "categories": ["Research", "STEM_Academic", "Technical", "Leadership_Service"],
    "last_updated": "2026-01-12"
  },
  "awards": [
    {
      "award_id": "regeneron-isef",
      "name": "Regeneron International Science and Engineering Fair",
      "short_name": "ISEF",
      "aliases": ["Intel ISEF", "Science Fair"],
      "category": "Research",
      "subcategory": "Science",
      "tags": ["research", "STEM", "prestigious", "international"],

      "award_type": "competition",
      "levels": [
        {"level_id": "regional", "level_name": "Regional Fair", "level_order": 1},
        {"level_id": "state", "level_name": "State Fair", "level_order": 2},
        {"level_id": "national", "level_name": "ISEF Finals", "level_order": 3}
      ],
      "tiers": [
        {"tier_name": "Grand Award", "winner_count": 20},
        {"tier_name": "Category Award", "winner_count": 100}
      ],
      "team_vs_individual": "both",
      "team_size": {"min": 1, "max": 3},

      "eligibility": {
        "grade_range": {"min": 9, "max": 12},
        "citizenship": ["any"],
        "geographic": {"scope": "international"},
        "demographic": {"gender": "any"},
        "prerequisites": {"prior_awards": [], "courses": [], "skills": ["research"]}
      },

      "selectivity": {
        "annual_participants": 70000,
        "annual_winners": 1800,
        "acceptance_rate": 0.026,
        "difficulty_rating": "very_high"
      },

      "jenny_tier": "North_Star",
      "jenny_rationale": "Pinnacle research award - signals genuine scientific inquiry",
      "archetype_fit": {
        "Young_Explorer": 0.6,
        "Freshman_Founder": 0.5,
        "Sophomore_Specialist": 0.8,
        "Junior_Executor": 0.9,
        "Cookie_Cutter_Risk": 0.3,
        "Introverted_Builder": 0.9,
        "Dual_Passion_Bridge": 0.7
      },
      "demographic_saturation": {
        "indian_male_cs_bay_area": "very_high",
        "asian_female_stem": "high",
        "underrepresented_stem": "low",
        "first_generation": "low"
      },
      "college_impact": {
        "recognition_level": "exceptional",
        "admissions_boost": "+20-40%",
        "schools_that_value": ["MIT", "Caltech", "Stanford", "Harvard"]
      },
      "jenny_notes": "Plant as North Star in 8th-9th grade. Regional qualifier is the real challenge.",
      "success_patterns": [
        "Multi-year research commitment",
        "Mentor relationship with university professor",
        "Iterative project refinement"
      ],
      "common_mistakes": [
        "Starting too late (junior year)",
        "Choosing overly common topics",
        "Weak experimental design"
      ],

      "relationships": {
        "prerequisites": [],
        "feeds_into": ["siemens-competition", "regeneron-sts"],
        "alternatives": ["broadcom-masters"],
        "complements": ["science-olympiad"]
      },
      "win_cascade_position": {
        "is_entry_point": false,
        "is_capstone": true,
        "typical_sequence_position": 5
      },

      "matching_weights": {
        "academic_strength": 0.25,
        "subject_expertise": 0.35,
        "prior_awards": 0.10,
        "project_quality": 0.30
      },
      "addresses_weak_spots": ["Research_Gap", "Awards_Gap"]
    }
    // ... 49 more awards
  ]
}
```

### Task 1.5: Seed Core Programs (50)

**File:** `/agents/databases/seeds/programs_core.json`

(Similar structure to awards, with program-specific fields)

## 3.3 Deliverables Checklist

| Deliverable | File Path | Status |
|-------------|-----------|--------|
| Handoff contracts | `/agents/models/contracts.py` | To create |
| Intelligence config | `/agents/config/intelligence_config.py` | To create |
| Awards schema | `/agents/db/schemas/awards_schema.py` | To create |
| Programs schema | `/agents/db/schemas/programs_schema.py` | To create |
| 50 core awards seed | `/agents/databases/seeds/awards_core.json` | To create |
| 50 core programs seed | `/agents/databases/seeds/programs_core.json` | To create |
| Migration script | `/agents/db/migrations/001_create_awards_programs.py` | To create |
| Huda golden reference | `/agents/tests/golden/huda_reference.json` | To create |

---

# 4. PHASE 2: EC AGENT IMPLEMENTATION

## 4.1 Overview

| Duration | Deliverables | Dependencies |
|----------|--------------|--------------|
| Week 2-3 | EC Agent + TYPE-013/014/015 | Phase 1 contracts |

## 4.2 Task Breakdown

### Task 2.1: Create EC Agent Base

**File:** `/agents/agents/extracurriculars_agent.py`

```python
"""
EC Agent - Extracurriculars Specialist

EXTENDS: BaseAgent (preserves ReAct framework)
IMPLEMENTS: TYPE-013, TYPE-014, TYPE-015
OUTPUTS: identity_synthesis (used by Awards + Programs)
"""

from typing import Dict, List, Any, Optional
import structlog

from .base_agent import BaseAgent
from ..intelligence.TYPE_013_EC_Portfolio import PortfolioOptimizer
from ..intelligence.TYPE_014_Narrative import NarrativeSynthesizer
from ..intelligence.TYPE_015_Impact import ImpactAssessor
from ..models.contracts import (
    ECAgentInput,
    ECAgentOutput,
    PortfolioOptimizationOutput,
    NarrativeSynthesisOutput,
    ImpactAssessmentOutput,
)
from ..config import intelligence_config


class ExtracurricularsAgent(BaseAgent):
    """
    EC Agent - Portfolio optimization, narrative synthesis, impact assessment.

    This agent is the FIRST specialist invoked by GamePlan.
    It produces identity_synthesis that other agents consume.

    ReAct Framework Integration:
    - reason(): Analyze student activities and identify gaps
    - act(): Run TYPE-013/014/015 intelligence
    - observe(): Validate outputs against quality gates
    """

    def __init__(self):
        super().__init__(agent_name="ec_agent")
        self.logger = structlog.get_logger(__name__)

        # Intelligence modules (configurable, not hardcoded)
        self.portfolio_optimizer = PortfolioOptimizer(
            config=intelligence_config.tier_classification,
            slot_config=intelligence_config.slot_strategy,
        )
        self.narrative_synthesizer = NarrativeSynthesizer(
            cookie_cutter_config=intelligence_config.cookie_cutter_patterns,
            thresholds=intelligence_config.cookie_cutter_thresholds,
        )
        self.impact_assessor = ImpactAssessor(
            evidence_ladder=intelligence_config.evidence_ladder,
            health_weights=intelligence_config.portfolio_health_weights,
        )

    async def analyze(self, input_data: ECAgentInput) -> ECAgentOutput:
        """
        Main entry point - analyze student's extracurricular profile.

        Execution Order:
        1. TYPE-013: Portfolio Optimization (tier classification, 10-slot strategy)
        2. TYPE-014: Narrative Synthesis (identity, cookie-cutter, authenticity)
        3. TYPE-015: Impact Engineering (evidence ladder, portfolio health)
        4. Generate priority actions from gaps

        Returns:
        - portfolio_audit: Classified activities with gaps
        - narrative_synthesis: Identity label + cookie-cutter analysis
        - impact_assessment: Evidence ladder positioning
        - priority_actions: Recommended next steps
        """
        self._log_start("analyze", student_id=input_data.student_id)

        # Execute via ReAct framework
        result = await self.execute_react_cycle(
            task="analyze_extracurriculars",
            context={
                "input": input_data.dict(),
            },
            max_iterations=3,
        )

        if not result.success:
            self.logger.error("ec_analysis_failed", error=result.error)
            raise Exception(f"EC Agent analysis failed: {result.error}")

        return result.output

    async def reason(self, task: str, context: Dict) -> "Thought":
        """
        ReAct REASON step.

        Analyze what intelligence types need to run and in what order.
        """
        input_data = context.get("input", {})
        activities = input_data.get("existing_activities", [])

        # Determine what analysis is needed
        needs_portfolio = len(activities) > 0
        needs_narrative = True  # Always synthesize narrative
        needs_impact = len(activities) > 0

        thought = Thought(
            reasoning=f"Student has {len(activities)} activities. Need portfolio={needs_portfolio}, narrative={needs_narrative}, impact={needs_impact}",
            selected_action=Action(
                type="full_analysis",
                params={
                    "run_portfolio": needs_portfolio,
                    "run_narrative": needs_narrative,
                    "run_impact": needs_impact,
                }
            )
        )

        return thought

    async def act(self, action: "Action") -> "ActionResult":
        """
        ReAct ACT step.

        Execute the intelligence types based on reasoning.
        """
        params = action.params
        input_data = self._current_context.get("input", {})

        results = {}

        # TYPE-013: Portfolio Optimization
        if params.get("run_portfolio"):
            results["portfolio"] = await self.portfolio_optimizer.optimize(
                activities=input_data.get("existing_activities", []),
                profile=input_data.get("student_profile", {}),
                available_hours=input_data.get("available_hours_weekly", 20),
            )

        # TYPE-014: Narrative Synthesis
        if params.get("run_narrative"):
            results["narrative"] = await self.narrative_synthesizer.synthesize(
                activities=input_data.get("existing_activities", []),
                four_pillars=input_data.get("four_pillars", {}),
                demographics=input_data.get("demographic_data", {}),
            )

        # TYPE-015: Impact Assessment
        if params.get("run_impact"):
            results["impact"] = await self.impact_assessor.assess(
                activities=input_data.get("existing_activities", []),
                portfolio_audit=results.get("portfolio"),
            )

        # Generate priority actions
        results["priority_actions"] = self._generate_priority_actions(
            portfolio=results.get("portfolio"),
            narrative=results.get("narrative"),
            impact=results.get("impact"),
            weak_spots=input_data.get("weak_spots", []),
        )

        return ActionResult(
            success=True,
            data=results,
        )

    async def observe(self, result: "ActionResult") -> "Observation":
        """
        ReAct OBSERVE step.

        Validate results against quality gates.
        """
        data = result.data

        # Build output
        output = ECAgentOutput(
            student_id=self._current_context["input"]["student_id"],
            portfolio_audit=data.get("portfolio"),
            narrative_synthesis=data.get("narrative"),
            impact_assessment=data.get("impact"),
            priority_actions=data.get("priority_actions", []),
            processing_time_ms=self._get_processing_time(),
        )

        # Calculate quality scores
        confidence = self._calculate_confidence(output)
        completeness = self._calculate_completeness(output)
        coherence = self._calculate_coherence(output)

        return Observation(
            data=output,
            confidence=confidence,
            completeness=completeness,
            coherence=coherence,
        )

    def _generate_priority_actions(
        self,
        portfolio: Optional[PortfolioOptimizationOutput],
        narrative: Optional[NarrativeSynthesisOutput],
        impact: Optional[ImpactAssessmentOutput],
        weak_spots: List[Dict],
    ) -> List[Dict]:
        """Generate priority actions based on all analysis."""
        actions = []

        # Gap-based actions
        if portfolio and portfolio.gaps:
            for gap in portfolio.gaps:
                actions.append({
                    "priority": gap.get("priority", "medium"),
                    "source": "portfolio_gap",
                    "action": f"Address {gap.get('category')} gap",
                    "suggested_activities": gap.get("suggested_activities", []),
                })

        # Cookie-cutter differentiation actions
        if narrative and narrative.cookie_cutter.get("score", 0) >= 0.4:
            for plan in narrative.cookie_cutter.get("differentiation_plan", []):
                actions.append({
                    "priority": plan.get("priority", "high"),
                    "source": "differentiation",
                    "action": plan.get("action"),
                    "timeline": plan.get("timeline"),
                })

        # Impact elevation actions
        if impact and impact.portfolio_health.get("stuck_at_M0", 0) > 0:
            actions.append({
                "priority": "high",
                "source": "impact_stagnation",
                "action": "Elevate M0 activities to M1+ evidence level",
                "recommendations": impact.recommendations,
            })

        # Weak spot mapping
        for ws in weak_spots:
            actions.append({
                "priority": ws.get("severity", "medium"),
                "source": "weak_spot",
                "action": f"Address weak spot: {ws.get('area')}",
                "suggested_fix": ws.get("suggested_fix"),
            })

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda x: priority_order.get(x["priority"], 2))

        return actions


# Singleton instance
ec_agent = ExtracurricularsAgent()
```

### Task 2.2: Implement TYPE-013 Portfolio Optimization

**File:** `/agents/intelligence/TYPE_013_EC_Portfolio.py`

```python
"""
TYPE-013: EC Portfolio Optimization

Classifies activities into T1-T4 tiers and assigns 10-slot Common App roles.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re

from ..models.contracts import (
    ClassifiedActivity,
    PortfolioOptimizationOutput,
    Tier,
    SlotType,
)


@dataclass
class PortfolioOptimizerConfig:
    """Configuration for portfolio optimization."""
    tier_classification: Dict[str, Any]
    slot_strategy: Dict[str, Any]


class PortfolioOptimizer:
    """
    TYPE-013 Implementation.

    Responsibilities:
    1. Classify activities into T1-T4 tiers
    2. Assign 10-slot Common App roles
    3. Detect gaps in portfolio
    4. Check for overcommitment
    """

    # T1 Keywords (national/international recognition)
    T1_KEYWORDS = [
        'founder', 'national champion', 'international', 'patent',
        'published research', 'nonprofit 501(c)(3)', 'national finalist',
        'isef finalist', 'rsi', 'tasp', 'presidential scholar',
        'national merit finalist', 'imo', 'usamo', 'usaco platinum'
    ]

    # T2 Keywords (regional/state recognition)
    T2_KEYWORDS = [
        'president', 'captain', 'regional', 'state champion',
        'editor-in-chief', 'founder local', 'varsity', 'principal',
        'usaco gold', 'aime qualifier'
    ]

    def __init__(self, config: Dict, slot_config: Dict):
        self.config = config
        self.slot_config = slot_config

    async def optimize(
        self,
        activities: List[Dict],
        profile: Dict,
        available_hours: float
    ) -> PortfolioOptimizationOutput:
        """
        Main optimization function.

        Steps:
        1. Classify each activity into T1-T4
        2. Assign to 10-slot strategy
        3. Identify gaps
        4. Check overcommitment
        """
        # Step 1: Classify activities
        classified = []
        for activity in activities:
            tier = self._classify_tier(activity)
            classified.append(ClassifiedActivity(
                activity_id=activity.get("id", ""),
                name=activity.get("name", ""),
                tier=tier,
                slot_type=SlotType.SUPPORTING,  # Default, will be optimized
                hours_per_week=activity.get("hours_per_week", 0),
                evidence_level=self._get_evidence_level(activity),
                identity_alignment=0.0,  # Will be set by TYPE-014
            ))

        # Step 2: Optimize slot assignment
        slot_optimization = self._optimize_slots(classified)

        # Update slot types in classified activities
        for slot_type, slot_activities in slot_optimization.items():
            for activity in slot_activities:
                activity.slot_type = slot_type

        # Step 3: Identify gaps
        gaps = self._identify_gaps(classified, slot_optimization)

        # Step 4: Check overcommitment
        overcommitment = self._check_overcommitment(classified, available_hours)

        # Step 5: Generate tier summary
        tier_summary = self._generate_tier_summary(classified)

        return PortfolioOptimizationOutput(
            classified_activities=classified,
            slot_optimization=slot_optimization,
            tier_summary=tier_summary,
            gaps=gaps,
            overcommitment=overcommitment,
        )

    def _classify_tier(self, activity: Dict) -> Tier:
        """Classify activity into T1-T4 tier."""
        name = activity.get("name", "").lower()
        description = activity.get("description", "").lower()
        role = activity.get("role", "").lower()
        scope = activity.get("scope", "").lower()
        all_text = f"{name} {description} {role} {scope}"

        # T1: National/International with T1 keywords
        for keyword in self.T1_KEYWORDS:
            if keyword in all_text:
                return Tier.T1

        # Check for founder + national scope
        if "founder" in role and scope in ["national", "international"]:
            return Tier.T1

        # T2: Regional/State or leadership roles
        for keyword in self.T2_KEYWORDS:
            if keyword in all_text:
                return Tier.T2

        # Check for president/captain + significant impact
        if any(r in role for r in ["president", "captain", "lead"]):
            if scope in ["regional", "state"] or activity.get("hours_per_week", 0) >= 5:
                return Tier.T2

        # T3: School/Local with moderate engagement
        if scope in ["school", "local"] and activity.get("hours_per_week", 0) >= 2:
            return Tier.T3

        # T4: Basic participation
        return Tier.T4

    def _optimize_slots(
        self,
        activities: List[ClassifiedActivity]
    ) -> Dict[SlotType, List[ClassifiedActivity]]:
        """Assign activities to optimal 10-slot positions."""
        slots = {
            SlotType.FLAGSHIP: [],
            SlotType.SUPPORTING: [],
            SlotType.VALIDATION: [],
            SlotType.SERVICE: [],
        }

        # Sort by tier (T1 first) then hours
        sorted_activities = sorted(
            activities,
            key=lambda x: (x.tier.value, -x.hours_per_week)
        )

        # Assign flagship (2-3 T1/T2 activities with highest hours)
        flagship_config = self.slot_config.get("flagship", {})
        min_flagship, max_flagship = flagship_config.get("count", (2, 3))
        min_hours = flagship_config.get("min_hours", 8)
        flagship_tiers = flagship_config.get("tiers", ["T1", "T2"])

        for activity in sorted_activities:
            if len(slots[SlotType.FLAGSHIP]) >= max_flagship:
                break
            if (activity.tier.value in flagship_tiers and
                activity.hours_per_week >= min_hours):
                slots[SlotType.FLAGSHIP].append(activity)

        # Assign supporting (3-4 T2/T3 activities)
        supporting_config = self.slot_config.get("supporting", {})
        min_supporting, max_supporting = supporting_config.get("count", (3, 4))

        for activity in sorted_activities:
            if activity in slots[SlotType.FLAGSHIP]:
                continue
            if len(slots[SlotType.SUPPORTING]) >= max_supporting:
                break
            if activity.tier.value in ["T2", "T3"]:
                slots[SlotType.SUPPORTING].append(activity)

        # Assign validation (2-3 selective programs/recognition)
        validation_config = self.slot_config.get("validation", {})
        min_validation, max_validation = validation_config.get("count", (2, 3))

        for activity in sorted_activities:
            if activity in slots[SlotType.FLAGSHIP] or activity in slots[SlotType.SUPPORTING]:
                continue
            if len(slots[SlotType.VALIDATION]) >= max_validation:
                break
            # Validation typically low hours, high recognition
            if activity.hours_per_week <= 4 and activity.tier.value in ["T2", "T3"]:
                slots[SlotType.VALIDATION].append(activity)

        # Assign service (2 community activities)
        service_config = self.slot_config.get("service", {})
        service_count = service_config.get("count", 2)

        for activity in sorted_activities:
            if activity in slots[SlotType.FLAGSHIP] or \
               activity in slots[SlotType.SUPPORTING] or \
               activity in slots[SlotType.VALIDATION]:
                continue
            if len(slots[SlotType.SERVICE]) >= service_count:
                break
            # Service activities
            name_lower = activity.name.lower()
            if any(kw in name_lower for kw in ["volunteer", "service", "community", "teach"]):
                slots[SlotType.SERVICE].append(activity)

        return slots

    def _identify_gaps(
        self,
        activities: List[ClassifiedActivity],
        slots: Dict[SlotType, List[ClassifiedActivity]]
    ) -> List[Dict]:
        """Identify gaps in the portfolio."""
        gaps = []

        # Check flagship gaps
        flagship_config = self.slot_config.get("flagship", {})
        min_flagship = flagship_config.get("count", (2, 3))[0]
        if len(slots[SlotType.FLAGSHIP]) < min_flagship:
            gaps.append({
                "category": "flagship",
                "count": min_flagship - len(slots[SlotType.FLAGSHIP]),
                "priority": "critical",
                "suggested_activities": [
                    "Start a nonprofit or significant project",
                    "Pursue national competition",
                    "Create initiative with measurable impact"
                ]
            })

        # Check tier distribution
        tier_counts = {t: 0 for t in Tier}
        for a in activities:
            tier_counts[a.tier] += 1

        if tier_counts[Tier.T1] == 0:
            gaps.append({
                "category": "T1_missing",
                "count": 1,
                "priority": "high",
                "suggested_activities": [
                    "Pursue ISEF-qualifying research",
                    "Apply to RSI/TASP",
                    "Start nonprofit with national reach"
                ]
            })

        # Check service gap
        if len(slots[SlotType.SERVICE]) < 2:
            gaps.append({
                "category": "service",
                "count": 2 - len(slots[SlotType.SERVICE]),
                "priority": "medium",
                "suggested_activities": [
                    "Tutoring or mentoring",
                    "Community service project",
                    "Volunteer at local organization"
                ]
            })

        return gaps

    def _check_overcommitment(
        self,
        activities: List[ClassifiedActivity],
        available_hours: float
    ) -> Optional[Dict]:
        """Check if student is overcommitted."""
        total_hours = sum(a.hours_per_week for a in activities)

        if total_hours > available_hours:
            return {
                "detected": True,
                "total_hours_per_week": total_hours,
                "available_hours": available_hours,
                "over_by": total_hours - available_hours,
                "recommendation": f"Consider reducing commitments by {total_hours - available_hours:.1f} hours/week"
            }

        return None

    def _generate_tier_summary(
        self,
        activities: List[ClassifiedActivity]
    ) -> Dict[str, Any]:
        """Generate tier distribution summary."""
        tier_counts = {t.value: 0 for t in Tier}
        for a in activities:
            tier_counts[a.tier.value] += 1

        # Determine diagnosis
        if tier_counts["T1"] >= 2 and tier_counts["T2"] >= 3:
            diagnosis = "COMPETITIVE"
        elif tier_counts["T1"] >= 1 or tier_counts["T2"] >= 4:
            diagnosis = "NEEDS_VALIDATION"
        else:
            diagnosis = "WEAK"

        return {
            "T1_count": tier_counts["T1"],
            "T2_count": tier_counts["T2"],
            "T3_count": tier_counts["T3"],
            "T4_count": tier_counts["T4"],
            "diagnosis": diagnosis,
        }

    def _get_evidence_level(self, activity: Dict) -> str:
        """Determine evidence level for activity."""
        # This will be enhanced by TYPE-015
        impact = activity.get("impact", {})

        if impact.get("media_coverage") or impact.get("awards"):
            return "M4"
        if impact.get("revenue") and impact.get("revenue") >= 1000:
            return "M3"
        if impact.get("measured_outcomes"):
            return "M2"
        if impact.get("user_count") and impact.get("user_count") > 0:
            return "M1"
        return "M0"
```

### Task 2.3: Enhance TYPE-014 Narrative Synthesis

**File:** `/agents/intelligence/TYPE_014_Narrative.py`

(Enhance existing `gameplan_narrative.py` with cookie-cutter detection and authenticity test)

### Task 2.4: Implement TYPE-015 Impact Engineering

**File:** `/agents/intelligence/TYPE_015_Impact.py`

```python
"""
TYPE-015: Impact Engineering

Assesses evidence ladder level (M0-M4) and portfolio health.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..models.contracts import (
    ImpactAssessmentOutput,
    EvidenceLevel,
)


class ImpactAssessor:
    """
    TYPE-015 Implementation.

    Evidence Ladder:
    - M0: Built (project exists)
    - M1: Used (real users adopted)
    - M2: Measured (quantified outcomes)
    - M3: Dollars ($1,000+ raised/earned)
    - M4: Media (external validation)
    """

    def __init__(self, evidence_ladder: Dict, health_weights: Dict):
        self.evidence_ladder = evidence_ladder
        self.health_weights = health_weights

    async def assess(
        self,
        activities: List[Dict],
        portfolio_audit: Optional[Any] = None
    ) -> ImpactAssessmentOutput:
        """
        Assess impact evidence for all activities.

        Steps:
        1. Classify each activity by evidence level
        2. Track flagship progress
        3. Calculate portfolio health score
        4. Generate recommendations
        """
        # Step 1: Classify by evidence level
        activities_by_level = {level: [] for level in EvidenceLevel}

        for activity in activities:
            level = self._determine_evidence_level(activity)
            diagnosis = {
                "activity_id": activity.get("id"),
                "name": activity.get("name"),
                "current_level": level.value,
                "evidence": self._extract_evidence(activity, level),
                "next_level_requirements": self._get_next_level_requirements(level),
            }
            activities_by_level[level].append(diagnosis)

        # Step 2: Track flagship progress
        flagship_progress = []
        if portfolio_audit:
            for flagship in portfolio_audit.slot_optimization.get("flagship", []):
                level = self._determine_evidence_level_from_classified(flagship)
                flagship_progress.append({
                    "flagship_name": flagship.name,
                    "current_level": level.value,
                    "target_level": "M3",  # Flagships should reach M3+
                    "on_track": level.value >= "M2",
                })

        # Step 3: Calculate portfolio health
        portfolio_health = self._calculate_portfolio_health(activities_by_level)

        # Step 4: Generate recommendations
        recommendations = self._generate_recommendations(
            activities_by_level,
            flagship_progress,
            portfolio_health,
        )

        return ImpactAssessmentOutput(
            activities_by_level={k.value: v for k, v in activities_by_level.items()},
            flagship_progress=flagship_progress,
            portfolio_health=portfolio_health,
            recommendations=recommendations,
        )

    def _determine_evidence_level(self, activity: Dict) -> EvidenceLevel:
        """Determine evidence level for an activity."""
        impact = activity.get("impact", {})

        # M4: Media/External Validation
        if impact.get("media_coverage") or \
           impact.get("press_mentions") or \
           impact.get("awards_won"):
            return EvidenceLevel.M4

        # M3: Dollars ($1,000+)
        revenue = impact.get("revenue", 0) or 0
        raised = impact.get("funds_raised", 0) or 0
        if revenue >= 1000 or raised >= 1000:
            return EvidenceLevel.M3

        # M2: Measured Outcomes
        if impact.get("survey_results") or \
           impact.get("pre_post_assessment") or \
           impact.get("quantified_outcomes"):
            return EvidenceLevel.M2

        # M1: Users
        users = impact.get("user_count", 0) or impact.get("participants", 0) or 0
        if users > 0:
            return EvidenceLevel.M1

        # M0: Built (default - project exists)
        return EvidenceLevel.M0

    def _calculate_portfolio_health(
        self,
        activities_by_level: Dict[EvidenceLevel, List]
    ) -> Dict[str, Any]:
        """Calculate overall portfolio health score."""
        baseline = self.health_weights.get("baseline", 50)
        m0_penalty = self.health_weights.get("M0_penalty", -10)
        m2_bonus = self.health_weights.get("M2_plus_bonus", 15)
        m4_bonus = self.health_weights.get("M4_bonus", 25)

        score = baseline

        # Penalties for M0 stagnation
        stuck_at_m0 = len([
            a for a in activities_by_level[EvidenceLevel.M0]
            if self._is_stagnated(a)
        ])
        score += stuck_at_m0 * m0_penalty

        # Bonuses for M2+ and M4
        m2_plus_count = sum(
            len(activities_by_level[level])
            for level in [EvidenceLevel.M2, EvidenceLevel.M3, EvidenceLevel.M4]
        )
        m4_count = len(activities_by_level[EvidenceLevel.M4])

        score += m2_plus_count * m2_bonus
        score += m4_count * m4_bonus

        # Clamp to 0-100
        score = max(0, min(100, score))

        return {
            "stuck_at_M0": stuck_at_m0,
            "reached_M2_plus": m2_plus_count,
            "reached_M4": m4_count,
            "overall_score": score,
        }

    def _is_stagnated(self, activity_diagnosis: Dict) -> bool:
        """Check if activity is stagnated at M0."""
        # Stagnation: M0 level with significant time investment
        total_hours = activity_diagnosis.get("total_hours", 0)
        return activity_diagnosis.get("current_level") == "M0" and total_hours > 50

    def _generate_recommendations(
        self,
        activities_by_level: Dict,
        flagship_progress: List,
        portfolio_health: Dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # M0 elevation recommendations
        if portfolio_health["stuck_at_M0"] > 0:
            recommendations.append(
                "Prioritize getting real users for M0 activities - even 10 users moves you to M1"
            )

        # Flagship recommendations
        for fp in flagship_progress:
            if not fp["on_track"]:
                recommendations.append(
                    f"Flagship '{fp['flagship_name']}' needs evidence elevation - "
                    f"currently at {fp['current_level']}, target {fp['target_level']}"
                )

        # M4 recommendations
        if portfolio_health["reached_M4"] == 0:
            recommendations.append(
                "Consider pursuing awards, press coverage, or publications "
                "to achieve M4 evidence level"
            )

        # General health recommendations
        if portfolio_health["overall_score"] < 50:
            recommendations.append(
                "Portfolio health is below target (50). Focus on elevating "
                "existing activities rather than starting new ones."
            )

        return recommendations

    def _extract_evidence(self, activity: Dict, level: EvidenceLevel) -> Dict:
        """Extract evidence for the determined level."""
        impact = activity.get("impact", {})

        evidence_map = {
            EvidenceLevel.M4: {
                "type": "media",
                "details": impact.get("media_coverage") or impact.get("awards_won"),
            },
            EvidenceLevel.M3: {
                "type": "dollars",
                "amount": impact.get("revenue", 0) + impact.get("funds_raised", 0),
            },
            EvidenceLevel.M2: {
                "type": "measured",
                "details": impact.get("quantified_outcomes"),
            },
            EvidenceLevel.M1: {
                "type": "users",
                "count": impact.get("user_count", 0),
            },
            EvidenceLevel.M0: {
                "type": "built",
                "details": "Project exists",
            },
        }

        return evidence_map.get(level, {"type": "unknown"})

    def _get_next_level_requirements(self, current: EvidenceLevel) -> str:
        """Get requirements to reach the next evidence level."""
        requirements = {
            EvidenceLevel.M0: "Get at least 1 real user to reach M1",
            EvidenceLevel.M1: "Collect measurable outcome data (surveys, assessments) to reach M2",
            EvidenceLevel.M2: "Generate $1,000+ in revenue or fundraising to reach M3",
            EvidenceLevel.M3: "Achieve media coverage, press, or award recognition to reach M4",
            EvidenceLevel.M4: "Already at maximum evidence level",
        }
        return requirements.get(current, "Unknown")
```

## 4.3 Deliverables Checklist

| Deliverable | File Path | Status |
|-------------|-----------|--------|
| EC Agent base | `/agents/agents/extracurriculars_agent.py` | To create |
| TYPE-013 Portfolio | `/agents/intelligence/TYPE_013_EC_Portfolio.py` | To create |
| TYPE-014 Narrative (enhanced) | `/agents/intelligence/TYPE_014_Narrative.py` | To create |
| TYPE-015 Impact | `/agents/intelligence/TYPE_015_Impact.py` | To create |
| EC Agent unit tests | `/agents/tests/test_ec_agent.py` | To create |
| Huda validation test | `/agents/tests/test_huda_ec.py` | To create |

---

# 5. PHASE 3: AWARDS AGENT ENHANCEMENT

## 5.1 Overview

| Duration | Deliverables | Dependencies |
|----------|--------------|--------------|
| Week 3-4 | Enhanced Awards Agent + 100 awards | Phase 2 EC Agent |

## 5.2 Key Enhancements

1. **Rename** `awards.py` → keep but enhance
2. **Add** Jenny's tier system (North Star/Building Block/Quick Win)
3. **Add** Full eligibility validation
4. **Add** 2-2-1 portfolio strategy
5. **Add** Win cascade sequencing
6. **Add** Identity synthesis integration
7. **Seed** 100 awards database

## 5.3 Integration Point: Identity Synthesis

```python
# In enhanced awards_agent.py
async def match(
    self,
    input_data: AwardsAgentInput
) -> AwardsAgentOutput:
    """
    Match awards using identity from EC Agent.

    CRITICAL: identity_synthesis comes from EC Agent output.
    This enables narrative-aligned award selection.
    """
    identity = input_data.identity_synthesis

    # Use identity themes for filtering
    aligned_awards = await self.awards_repo.get_awards_aligned_with_themes(
        themes=identity.themes,
        first_principle=identity.first_principle,
    )

    # Calculate probability with identity boost
    for award in aligned_awards:
        award.probability = self._calculate_probability_with_identity(
            award=award,
            profile=input_data.student_profile,
            identity=identity,  # NEW: identity factors into probability
        )
```

---

# 6. PHASE 4: SUMMER PROGRAMS ENHANCEMENT

## 6.1 Overview

| Duration | Deliverables | Dependencies |
|----------|--------------|--------------|
| Week 4-5 | Enhanced Programs Agent + TYPE-028/029/030 | Phase 2 EC Agent |

## 6.2 Key Enhancements

1. **Rename** `opportunity.py` → `summer_programs_agent.py`
2. **Add** TYPE-028 Program Selection Matrix
3. **Add** TYPE-029 Application Strategy
4. **Add** TYPE-030 Cost-Benefit Intelligence
5. **Add** Identity synthesis integration
6. **Seed** 100 programs database

---

# 7. PHASE 5: ORCHESTRATION INTEGRATION

## 7.1 Overview

| Duration | Deliverables | Dependencies |
|----------|--------------|--------------|
| Week 5-6 | Enhanced GamePlan orchestration | Phases 2-4 |

## 7.2 GamePlan Enhancement

```python
# Enhanced gameplan.py
class GamePlanAgent:
    """
    Enhanced Game Plan Orchestrator.

    CHANGES FROM CURRENT:
    1. Invokes EC Agent FIRST
    2. Passes identity_synthesis to Awards + Programs
    3. Executes Awards + Programs IN PARALLEL
    4. Synthesizes all outputs
    5. Generates phase-based roadmap
    """

    def __init__(self):
        self.narrative_synthesizer = NarrativeSynthesizer()  # KEEP
        self.narrative_filter = None  # KEEP

        # NEW: Specialist agent references
        self.ec_agent = ExtracurricularsAgent()
        self.awards_agent = AwardsAgent()
        self.programs_agent = SummerProgramsAgent()

    async def generate_gameplan(
        self,
        profile_id: str,
        assessment_output: Dict[str, Any]
    ) -> GamePlanOutput:
        """
        Enhanced orchestration flow.
        """
        self._log_start("generate_gameplan", profile_id=profile_id)

        # STEP 1: EC Agent FIRST (generates identity)
        ec_output = await self.ec_agent.analyze(
            ECAgentInput(
                student_id=profile_id,
                student_profile=assessment_output.get("student_profile"),
                demographic_data=assessment_output.get("demographics"),
                existing_activities=assessment_output.get("activities", []),
                four_pillars=assessment_output.get("four_pillars"),
                weak_spots=assessment_output.get("weak_spots", []),
                target_schools=assessment_output.get("target_schools", []),
            )
        )

        # Extract identity for other agents
        identity_synthesis = ec_output.narrative_synthesis.identity

        # STEP 2: Awards + Programs IN PARALLEL
        awards_task = self.awards_agent.match(
            AwardsAgentInput(
                student_id=profile_id,
                student_profile=assessment_output.get("student_profile"),
                identity_synthesis=identity_synthesis,  # FROM EC AGENT
                existing_awards=assessment_output.get("existing_awards", []),
                weak_spots=assessment_output.get("weak_spots", []),
                target_schools=assessment_output.get("target_schools", []),
                cri_score=assessment_output.get("cri_score", 50),
                archetype=assessment_output.get("archetype", ""),
            )
        )

        programs_task = self.programs_agent.recommend(
            SummerProgramsAgentInput(
                student_id=profile_id,
                student_profile=assessment_output.get("student_profile"),
                identity_synthesis=identity_synthesis,  # FROM EC AGENT
                four_pillars=assessment_output.get("four_pillars"),
                interests=assessment_output.get("interests", []),
            )
        )

        # Execute in parallel
        awards_output, programs_output = await asyncio.gather(
            awards_task, programs_task
        )

        # STEP 3: Synthesize all outputs
        game_plan = await self._synthesize(
            assessment=assessment_output,
            ec_output=ec_output,
            awards_output=awards_output,
            programs_output=programs_output,
        )

        # STEP 4: Validate coherence (NOW WITH REAL DATA)
        self.narrative_filter = NarrativeFilter(
            ec_output.narrative_synthesis.to_master_narrative()
        )

        coherence = self.narrative_filter.validate_gameplan_coherence(
            activities=ec_output.portfolio_audit.classified_activities,
            awards=awards_output.portfolio.all_awards,  # NOW POPULATED
            programs=programs_output.program_recommendations.programs,  # NOW POPULATED
        )

        game_plan.narrative["coherence_score"] = coherence["coherence_score"]

        # Save to database
        result = await create_gameplan(game_plan.dict())

        return game_plan
```

## 7.3 Remove Hardcoded Arrays

```python
# BEFORE (current code):
narrative_coherence = self.narrative_filter.validate_gameplan_coherence(
    activities=threaded_plan,
    awards=[],      # ❌ HARDCODED
    programs=[],    # ❌ HARDCODED
)

# AFTER (enhanced code):
narrative_coherence = self.narrative_filter.validate_gameplan_coherence(
    activities=ec_output.portfolio_audit.classified_activities,
    awards=awards_output.portfolio.all_awards,        # ✅ REAL DATA
    programs=programs_output.program_recommendations.programs,  # ✅ REAL DATA
)
```

---

# 8. PHASE 6: TESTING & VALIDATION

## 8.1 Overview

| Duration | Deliverables | Dependencies |
|----------|--------------|--------------|
| Week 6-7 | Full test suite + Huda validation | Phases 1-5 |

## 8.2 Test Categories

### Unit Tests
- TYPE-013 tier classification
- TYPE-014 cookie-cutter detection
- TYPE-015 evidence ladder
- Awards probability calculation
- Programs ROI calculation

### Integration Tests
- EC Agent → Awards Agent handoff
- EC Agent → Programs Agent handoff
- Full GamePlan orchestration
- Parallel execution timing

### Golden Reference Tests
```python
# /agents/tests/test_huda_golden.py
async def test_huda_ec_agent_output():
    """Validate EC Agent produces expected Huda output."""
    input_data = load_huda_input()
    ec_output = await ec_agent.analyze(input_data)

    # Validate identity label
    assert "Muslim" in ec_output.narrative_synthesis.identity.label
    assert "Game" in ec_output.narrative_synthesis.identity.label
    assert "AI" in ec_output.narrative_synthesis.identity.label

    # Validate tier distribution
    assert ec_output.portfolio_audit.tier_summary["T1_count"] >= 2
    assert ec_output.portfolio_audit.tier_summary["diagnosis"] == "COMPETITIVE"

    # Validate authenticity
    assert ec_output.narrative_synthesis.authenticity["passed"] == True

async def test_huda_awards_output():
    """Validate Awards Agent produces expected Huda awards."""
    ec_output = load_huda_ec_output()
    input_data = AwardsAgentInput(
        student_id="huda-001",
        identity_synthesis=ec_output.narrative_synthesis.identity,
        # ...
    )
    awards_output = await awards_agent.match(input_data)

    # Validate portfolio structure
    assert len(awards_output.portfolio.north_star_awards) >= 2
    assert len(awards_output.portfolio.building_block_awards) >= 2

    # Validate specific awards
    award_names = [a.name for a in awards_output.portfolio.all_awards]
    assert "NCWIT" in " ".join(award_names)
    assert "Games for Change" in " ".join(award_names)
```

---

# 9. THIRD-PARTY INTEGRATION POINTS

## 9.1 Current Third-Party Stack

| Service | Purpose | Integration Status |
|---------|---------|-------------------|
| **Supabase** | Database + Auth | ✅ Integrated |
| **Redis** | Session cache | ✅ Integrated |
| **OpenAI GPT-4o** | LLM reasoning | ✅ Integrated |
| **LangGraph** | Crisis workflow | ✅ Integrated |
| **Vercel** | Frontend hosting | ✅ Integrated |

## 9.2 New Integration Points

| Service | Purpose | Implementation |
|---------|---------|----------------|
| **Awards Database** | 200 awards storage | Supabase table |
| **Programs Database** | 150 programs storage | Supabase table |
| **Essay Similarity** | TYPE-029 essay reuse | OpenAI embeddings |

## 9.3 Supabase Schema Extensions

```sql
-- New tables for Handover v1.0
CREATE TABLE awards (
    -- Schema from Phase 1
);

CREATE TABLE summer_programs (
    -- Schema from Phase 1
);

CREATE TABLE award_recommendations (
    id UUID PRIMARY KEY,
    profile_id UUID REFERENCES profiles,
    game_plan_id UUID REFERENCES game_plans,
    award_id UUID REFERENCES awards,
    probability FLOAT,
    narrative_alignment FLOAT,
    status TEXT,  -- 'recommended', 'applied', 'won', 'rejected'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE program_recommendations (
    id UUID PRIMARY KEY,
    profile_id UUID REFERENCES profiles,
    game_plan_id UUID REFERENCES game_plans,
    program_id UUID REFERENCES summer_programs,
    fit_score FLOAT,
    roi_score FLOAT,
    status TEXT,  -- 'recommended', 'applied', 'accepted', 'rejected'
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

# 10. RISK MITIGATION & ROLLBACK

## 10.1 Feature Flags

```python
# /agents/config/feature_flags.py
class FeatureFlags:
    """Feature flags for gradual rollout."""

    # Phase 2: EC Agent
    EC_AGENT_ENABLED = True
    TYPE_013_ENABLED = True
    TYPE_014_COOKIE_CUTTER_ENABLED = True
    TYPE_015_ENABLED = True

    # Phase 3: Awards Agent
    AWARDS_DATABASE_ENABLED = True
    AWARDS_IDENTITY_INTEGRATION_ENABLED = True
    AWARDS_WIN_CASCADE_ENABLED = True

    # Phase 4: Programs Agent
    PROGRAMS_DATABASE_ENABLED = True
    PROGRAMS_TYPE_028_ENABLED = True
    PROGRAMS_TYPE_029_ENABLED = True
    PROGRAMS_TYPE_030_ENABLED = True

    # Phase 5: Orchestration
    PARALLEL_SPECIALIST_EXECUTION_ENABLED = True
    PHASE_ROADMAP_ENABLED = True

# Usage in code
if FeatureFlags.EC_AGENT_ENABLED:
    ec_output = await self.ec_agent.analyze(...)
else:
    ec_output = self._legacy_narrative_synthesis(...)  # Fallback
```

## 10.2 Rollback Strategy

| Phase | Rollback Trigger | Rollback Action |
|-------|------------------|-----------------|
| Phase 2 | EC Agent errors > 5% | Disable EC_AGENT_ENABLED flag |
| Phase 3 | Awards probability calibration off > 30% | Disable AWARDS_IDENTITY_INTEGRATION_ENABLED |
| Phase 4 | Programs ROI calculation errors | Disable TYPE_030_ENABLED |
| Phase 5 | Parallel execution timeouts | Disable PARALLEL_SPECIALIST_EXECUTION_ENABLED |

## 10.3 Backward Compatibility

```python
# Maintain backward compatibility with legacy code
async def generate_gameplan(self, profile_id: str, assessment_output: Dict) -> Dict:
    """
    Enhanced orchestration with backward compatibility.
    """
    if FeatureFlags.EC_AGENT_ENABLED:
        # New flow
        ec_output = await self.ec_agent.analyze(...)
        identity = ec_output.narrative_synthesis.identity
    else:
        # Legacy flow (existing code)
        raw_extraction = self._extract_raw_components(assessment_output)
        master_narrative = self.narrative_synthesizer.synthesize(raw_extraction)
        identity = None

    if FeatureFlags.AWARDS_DATABASE_ENABLED and identity:
        # New awards flow
        awards_output = await self.awards_agent.match(
            identity_synthesis=identity, ...
        )
    else:
        # Legacy: empty awards
        awards_output = {"portfolio": {"all_awards": []}}

    # ... continue with backward-compatible synthesis
```

---

# 11. SUCCESS CRITERIA

## 11.1 Phase Success Metrics

| Phase | Metric | Target | Measurement |
|-------|--------|--------|-------------|
| Phase 1 | Contracts defined | 8 contracts | Code review |
| Phase 1 | Awards seeded | 50 core | Database count |
| Phase 2 | EC Agent accuracy | Match Huda identity | Golden test |
| Phase 2 | TYPE-013 classification | 95% accuracy | Manual review |
| Phase 3 | Awards eligibility | 100% accuracy | No false positives |
| Phase 3 | Portfolio structure | 2-2-1 achieved | Output validation |
| Phase 4 | Programs alignment | 70%+ identity match | Score validation |
| Phase 5 | Orchestration | All specialists called | Log validation |
| Phase 6 | Huda end-to-end | 100% structure match | Golden test |

## 11.2 Quality Gates

| Gate | Threshold | Enforcement |
|------|-----------|-------------|
| Confidence | ≥70% | Block output if below |
| Completeness | ≥70% | Block output if below |
| Coherence | ≥0.6 | Block output if below |
| Test coverage | ≥80% | Block merge if below |
| Huda validation | 100% pass | Block release if failing |

## 11.3 Definition of Done

- [ ] All contracts implemented and type-safe
- [ ] EC Agent produces identity matching Huda reference
- [ ] Awards Agent produces 2-2-1 portfolio
- [ ] Programs Agent produces 8-12 aligned recommendations
- [ ] GamePlan orchestration invokes all specialists
- [ ] `awards=[]` and `programs=[]` replaced with real data
- [ ] All quality gates passing
- [ ] 80%+ test coverage
- [ ] Huda golden reference validation passing
- [ ] Documentation updated
- [ ] Feature flags in place for rollback

---

*Incremental Implementation Plan v1.0*
*Handover Package v1.0 on Existing Architecture*
*Duration: 6-7 weeks*
*Approach: Preserve ReAct, Enhance Autonomy, No Breaking Changes*
