# IvyQuest Current State Specification
## Multi-Agent Architecture Documentation v1.0

**Document Type**: System Analysis
**Date**: January 2026
**Status**: Complete Current State Analysis (Phase 1)

---

## 1. Executive Summary

IvyQuest is a multi-agent college admissions coaching platform that combines:
- **6 Specialized Agents** for different aspects of college preparation
- **Enriched Knowledge Base** with 97 awards and 58 programs
- **Strategic Intelligence** features (archetypes, win cascade, portfolio strategy)
- **Orchestrated Pipeline**: EC Agent → Awards + Programs (parallel)

### Key Architecture: 3P Stack
| Component | Role |
|-----------|------|
| **Agno** | Runtime spine (stateful agents, memory, workflows, HITL) |
| **LangGraph** | Deliberative reasoning (Crisis Alchemy, planning graphs) |
| **AutoGen** | Selective debates (offline narrative experiments) |

---

## 2. Agent Architecture

### 2.1 Agent Inventory

| Agent | File | Lines | Purpose | Autonomy |
|-------|------|-------|---------|----------|
| **ExtracurricularsAgent** | `extracurriculars.py` | 631 | Identity synthesis, portfolio analysis | FULL |
| **AwardsAgent** | `awards.py` | 1069 | Award matching with strategic intelligence | FULL |
| **ProgramsAgent** | `programs.py` | 664 | Program matching with strategic intelligence | FULL |
| **GamePlanAgent** | `gameplan.py` | 1333 | Orchestration, master narrative | HIGH |
| **ExecutionAgent** | `execution.py` | 949 | Bridge strategy-execution gap | HIGH |
| **AssessmentAgent** | `assessment.py` | 546 | Identity synthesis, readiness scoring | FULL |
| **NarrativeSynthesisAgent** | `narrative_synthesis.py` | 584 | Jenny's Formula narrative generation | HIGH |

### 2.2 Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GAMEPLAN ORCHESTRATION FLOW                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   STEP 1: EC Agent (FIRST)                                             │
│   ────────────────────────                                             │
│   Input:  profile_id                                                    │
│   Output: identity_synthesis                                            │
│           ├─ spike: string                                              │
│           ├─ archetype: enum (8 types)                                  │
│           ├─ archetype_confidence: float                                │
│           ├─ archetype_scores: Dict[archetype, float]                   │
│           ├─ pillars: List[string]                                      │
│           ├─ portfolio_balance_score: float                             │
│           ├─ portfolio_gaps: List[string]                               │
│           └─ portfolio_strengths: List[string]                          │
│                                                                         │
│                           │                                             │
│                           ▼                                             │
│                                                                         │
│   STEP 2: Awards + Programs (PARALLEL)                                  │
│   ─────────────────────────────────────                                 │
│   Both receive: identity_synthesis                                      │
│                                                                         │
│   ┌─────────────────────┐    ┌─────────────────────┐                   │
│   │   Awards Agent      │    │   Programs Agent    │                   │
│   │                     │    │                     │                   │
│   │   Uses:             │    │   Uses:             │                   │
│   │   - archetype_fit   │    │   - archetype_fit   │                   │
│   │   - strategic_tier  │    │   - strategic_tier  │                   │
│   │   - win_cascade     │    │   - hidden_value    │                   │
│   │   - 2-2-1 strategy  │    │   - synergies       │                   │
│   │                     │    │                     │                   │
│   │   Output:           │    │   Output:           │                   │
│   │   - portfolio       │    │   - matches         │                   │
│   │   - timeline        │    │   - advance_alerts  │                   │
│   └─────────────────────┘    └─────────────────────┘                   │
│                                                                         │
│                           │                                             │
│                           ▼                                             │
│                                                                         │
│   STEP 3: Synthesis                                                     │
│   ─────────────────                                                     │
│   - Master Narrative synthesis                                          │
│   - Priority actions generation                                         │
│   - Unified timeline creation                                           │
│   - State versioning                                                    │
│   - Event publishing                                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent Details

### 3.1 ExtracurricularsAgent

**File**: `agents/agents/extracurriculars.py` (631 lines)

**Purpose**: Runs FIRST in orchestration to produce identity synthesis that feeds Awards and Programs agents.

**Primitives Used**:
- TYPE-013: Portfolio Optimization (balance across categories)
- TYPE-014: Narrative Synthesis (create identity from ECs)
- TYPE-015: Impact Assessment (evaluate activity impact)

**Input Schema**:
```python
profile_id: str
```

**Output Schema** (IdentitySynthesis):
```python
@dataclass
class IdentitySynthesis:
    spike: str = ""                          # Primary passion/focus area
    spike_evidence: List[str] = []           # Activities supporting spike
    archetype: str = "multi_hyphenate"       # One of 8 archetypes
    archetype_confidence: float = 0.5        # 0.0-1.0
    archetype_scores: Dict[str, float] = {}  # All 8 archetype scores
    pillars: List[str] = []                  # 3-5 key pillars
    pillar_evidence: Dict[str, List[str]] = {}
    portfolio_balance_score: float = 0.0     # 0.0-1.0
    portfolio_gaps: List[str] = []           # Missing categories
    portfolio_strengths: List[str] = []      # Strong categories
    total_impact_score: float = 0.0
    top_impact_activities: List[Dict] = []
    leadership_level: str = "member"
    leadership_evidence: List[str] = []
```

**Processing Logic**:

| Step | Type | Description |
|------|------|-------------|
| `_get_profile` | Deterministic | Fetch profile with assessment data |
| `_extract_activities` | Deterministic | Parse activities from profile_data |
| `_analyze_portfolio_balance` | Deterministic | TYPE-013 - categorize & score balance |
| `_synthesize_identity` | **LLM-Assisted** | TYPE-014 - generate spike, archetype |
| `_assess_impact` | Deterministic | TYPE-015 - score activity impacts |

**CRITICAL BUG IDENTIFIED**:
```python
# Line 152-154: Returns placeholder if no activities
activities = self._extract_activities(profile)
if not activities:
    return self._placeholder_response(profile_id,
        message="Add extracurricular activities to generate analysis")
```

**Impact**: New students with no activities get empty spike and default archetype.

**8 Archetypes**:
```python
ARCHETYPES = [
    "academic_powerhouse",
    "stem_innovator",
    "creative_visionary",
    "community_changemaker",
    "entrepreneurial_leader",
    "humanities_scholar",
    "athletic_scholar",
    "multi_hyphenate",
]
```

---

### 3.2 AwardsAgent

**File**: `agents/agents/awards.py` (1069 lines)

**Purpose**: Match students to awards using Strategic Intelligence from enriched data.

**Input Schema**:
```python
profile_id: str
identity_synthesis: Optional[Dict] = None  # From EC Agent
```

**Output Schema**:
```python
{
    "success": bool,
    "total_matches": int,
    "portfolio": {
        "reach": List[AwardMatch],   # 2 awards (Tier 1-2)
        "target": List[AwardMatch],  # 2 awards (Tier 2-3)
        "safety": List[AwardMatch],  # 1 award (Tier 3-4)
    },
    "top_recommendations": List[AwardMatch],
    "timeline": List[TimelineItem],
    "strategic_insights": List[str],
}
```

**Key Features**:
- 2-2-1 Portfolio Strategy: 2 reach, 2 target, 1 safety
- Archetype fit scoring (MIN_ARCHETYPE_FIT = 0.3)
- Win cascade positioning (entry → building → capstone)
- ROI calculation: `(probability × prestige × tier_boost) / effort`

**Enriched Data Source**: `seeds/enriched/awards_enriched.json` (97 awards, 7167 lines)

**Processing Logic**:

| Step | Type | Description |
|------|------|-------------|
| `_load_enriched_awards` | Deterministic | Load from JSON with caching |
| `_filter_by_eligibility` | Deterministic | Grade, citizenship, deadlines |
| `_filter_by_archetype` | Deterministic | Filter by archetype_fit score |
| `calculate_win_probability` | **LLM-Assisted** | ACP-001 hidden probability |
| `_build_2_2_1_portfolio` | Deterministic | Apply portfolio strategy |

---

### 3.3 ProgramsAgent

**File**: `agents/agents/programs.py` (664 lines)

**Purpose**: Match students to summer programs using Strategic Intelligence.

**Input Schema**:
```python
profile_id: str
identity_synthesis: Optional[Dict] = None  # From EC Agent
```

**Output Schema**:
```python
{
    "success": bool,
    "total_matches": int,
    "top_recommendations": List[ProgramMatch],
    "advance_alerts": List[AlertItem],
    "synergy_recommendations": List[SynergyItem],
    "timeline": List[TimelineItem],
    "strategic_insights": List[str],
}
```

**Key Features**:
- Hidden value identification
- Synergy recommendations (pairs_well_with, leads_to)
- Application intensity planning
- Advance alerts (6 months ahead)

**Enriched Data Source**: `seeds/enriched/programs_enriched.json` (58 programs, 4902 lines)

---

### 3.4 GamePlanAgent

**File**: `agents/agents/gameplan.py` (1333 lines)

**Purpose**: Orchestrates multi-agent flow and synthesizes master narrative.

**Primitives Used**:
- ACP-004: Strategic Overwhelm (1.4x capacity assignment)
- ACP-005: Multi-Touchpoint Leverage (>=4 touchpoints required)
- ACP-006: Identity Seed Architecture (6-12 month advance planting)

**Key Methods**:

| Method | Purpose |
|--------|---------|
| `process()` | Main entry - routes to orchestrated or legacy flow |
| `generate_orchestrated()` | NEW: Multi-agent orchestration |
| `generate()` | Legacy: Single-agent generation |
| `_synthesize_gameplan()` | Combine EC, Awards, Programs results |

**Orchestration Code** (lines 96-200):
```python
async def generate_orchestrated(self, profile_id: str):
    # STEP 1: EC Agent FIRST
    ec_result = await self.ec_agent.process(profile_id)
    identity_synthesis = ec_result.get("identity_synthesis", {})

    # STEP 2: Awards + Programs PARALLEL
    awards_task = self.awards_agent.process(profile_id, identity_synthesis=identity_synthesis)
    programs_task = self.programs_agent.process(profile_id, identity_synthesis=identity_synthesis)
    awards_result, programs_result = await asyncio.gather(awards_task, programs_task)

    # STEP 3: Synthesize
    unified_plan = self._synthesize_gameplan(...)
```

---

## 4. Enriched Knowledge Base

### 4.1 Awards Data Structure

**File**: `agents/seeds/enriched/awards_enriched.json`
**Count**: 97 awards
**Lines**: 7,167

**Schema per Award**:
```json
{
  "id": "presidential-scholars",
  "name": "U.S. Presidential Scholars Program",
  "organization": "U.S. Department of Education",
  "category": "academic",
  "level": "national",
  "description": "...",
  "prestige_score": 10,
  "historical_win_rate": 0.002,
  "effort_hours": 50,
  "deadline_month": 1,
  "eligibility": {
    "grades": [12],
    "citizenship": ["US"]
  },
  "strategic_tier": 1,
  "strategic_tier_rationale": "...",
  "strategic_notes": "...",
  "success_patterns": ["...", "..."],
  "common_mistakes": ["...", "..."],
  "archetype_fit": {
    "academic_powerhouse": 1.0,
    "stem_innovator": 0.8,
    "creative_visionary": 0.6,
    "community_changemaker": 0.9,
    "entrepreneurial_leader": 0.7,
    "humanities_scholar": 0.8,
    "athletic_scholar": 0.5,
    "multi_hyphenate": 0.9
  },
  "win_cascade": {
    "position": "capstone",
    "prerequisites": ["..."],
    "enables": ["..."]
  },
  "timing": {
    "ideal_grades": [12],
    "prep_weeks": 12,
    "deadline_strategy": "..."
  },
  "differentiation_factor": "...",
  "enrichment_version": "1.0.0",
  "enrichment_date": "2026-01-12T19:46:38.584578"
}
```

### 4.2 Programs Data Structure

**File**: `agents/seeds/enriched/programs_enriched.json`
**Count**: 58 programs
**Lines**: 4,902

**Schema per Program**:
```json
{
  "id": "rsi",
  "name": "Research Science Institute (RSI)",
  "organization": "MIT / Center for Excellence in Education",
  "type": "summer_program",
  "category": "research",
  "description": "...",
  "prestige_score": 10,
  "acceptance_rate": 0.03,
  "selectivity": "highly_selective",
  "deadline_month": 1,
  "duration_weeks": 6,
  "cost": 0,
  "location": "Cambridge, MA",
  "eligibility": {
    "grades": [11],
    "citizenship": ["US", "international"]
  },
  "strategic_tier": 1,
  "strategic_tier_rationale": "...",
  "strategic_notes": "...",
  "success_patterns": ["...", "..."],
  "common_mistakes": ["...", "..."],
  "archetype_fit": {
    "academic_powerhouse": 0.9,
    "stem_innovator": 1.0,
    "creative_visionary": 0.6,
    "community_changemaker": 0.4,
    "entrepreneurial_leader": 0.5,
    "humanities_scholar": 0.2,
    "athletic_scholar": 0.1,
    "multi_hyphenate": 0.7
  },
  "hidden_value": ["...", "..."],
  "synergies": {
    "pairs_well_with": ["...", "..."],
    "leads_to": ["...", "..."]
  },
  "timing": {
    "ideal_grades": [11],
    "prep_weeks": 12,
    "application_intensity": "heavy"
  },
  "differentiation_factor": "...",
  "enrichment_version": "1.0.0",
  "enrichment_date": "2026-01-12T19:49:31.211029"
}
```

---

## 5. API Endpoints

### 5.1 FastAPI Backend

**File**: `agents/main.py`
**Port**: 8001

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/agents/assessment/enhance` | POST | Full assessment enhancement |
| `/agents/narrative/synthesize` | POST | Jenny's Formula narrative |
| `/agents/narrative/{profile_id}` | GET | Get existing narrative |
| `/agents/execution/scaffold` | POST | Break project into microsteps |
| `/agents/execution/crisis` | POST | Handle crisis/blocker |
| `/agents/execution/blockers/{profile_id}` | GET | Detect blockers |
| `/agents/execution/eds/{profile_id}` | GET | Execution Debt Score |
| `/agents/gameplan/generate` | POST | **Orchestrated GamePlan** |
| `/agents/gameplan/activities/{profile_id}` | GET | Filtered activities |
| `/agents/gameplan/seeds/{profile_id}` | GET | Identity seeds |
| `/agents/awards/match/{profile_id}` | GET | Award matches |
| `/agents/awards/portfolio/{profile_id}` | GET | Award portfolio |
| `/agents/opportunities/match/{profile_id}` | GET | Program matches |
| `/agents/opportunities/alerts/{profile_id}` | GET | Deadline alerts |
| `/notifications/{profile_id}` | GET | User notifications |

---

## 6. Frontend Architecture

### 6.1 Zustand Stores

| Store | File | Purpose |
|-------|------|---------|
| `useResultsStore` | `lib/store/useResultsStore.ts` | Scoring results, Strategic Intelligence |
| `useStudentStore` | `lib/store/useStudentStore.ts` | Student profile data |
| `useInsightsStore` | `lib/store/useInsightsStore.ts` | Agent insights |
| `useSessionStore` | `lib/store/useSessionStore.ts` | Session management |
| `useTwinStore` | `lib/store/useTwinStore.ts` | Digital twin fleet |

### 6.2 Results Store (Strategic Intelligence)

**File**: `lib/store/useResultsStore.ts` (370 lines)

**Key State Fields**:
```typescript
interface ResultsStoreState {
  // Strategic Intelligence (v1.1.0)
  identity_synthesis: IdentitySynthesis | null;
  portfolio_audit: PortfolioAudit | null;
  awards_portfolio: AwardsPortfolio | null;
  programs_portfolio: ProgramsPortfolio | null;
  priority_actions: PriorityAction[];
  unified_timeline: TimelineItem[];

  // Actions
  setGamePlanResults: (results: GamePlanApiResponse) => void;
}
```

### 6.3 Agent UI Components

| Component | File | Purpose |
|-----------|------|---------|
| `AgentDashboardV13` | `AgentDashboardV13.tsx` | Dashboard layout |
| `AgentDetailModal` | `AgentDetailModal.tsx` | Detailed agent view |
| `AssessmentAgentCard` | `cards/AssessmentAgentCard.tsx` | Assessment display |
| `GamePlanAgentCard` | `cards/GamePlanAgentCard.tsx` | GamePlan display |
| `AwardsAgentCard` | `cards/AwardsAgentCard.tsx` | 2-2-1 portfolio |
| `OpportunityAgentCard` | `cards/OpportunityAgentCard.tsx` | Programs display |
| `ExecutionAgentCard` | `cards/ExecutionAgentCard.tsx` | Execution status |
| `CrisisAgentCard` | `cards/CrisisAgentCard.tsx` | Crisis alchemy |

### 6.4 New UI Components (Strategic Intelligence)

| Component | File | Purpose |
|-----------|------|---------|
| `ArchetypeBadge` | `components/ui/ArchetypeBadge.tsx` | 8 archetype badges |
| `SpikeIndicator` | `components/ui/SpikeIndicator.tsx` | Spike display |

### 6.5 Data Fetching Hooks

**File**: `hooks/useAgentData.ts` (16,829 lines of hooks)

| Hook | Purpose |
|------|---------|
| `useGamePlan(profileId)` | Fetch orchestrated GamePlan |
| `useAwardMatches(profileId)` | Fetch award matches |
| `useAwardPortfolio(profileId)` | Fetch 2-2-1 portfolio |
| `useOpportunityMatches(profileId)` | Fetch program matches |
| `useOpportunityAlerts(profileId)` | Fetch deadline alerts |
| `useNarrativeDNA(profileId)` | Fetch narrative synthesis |
| `useExecutionDebtScore(profileId)` | Fetch EDS |
| `useBlockers(profileId)` | Fetch blockers |

---

## 7. Database Schema

### 7.1 Core Tables

| Table | Purpose |
|-------|---------|
| `profiles` | User profiles (id, email, role) |
| `assessments` | Assessment data (profile_data, scores, archetype) |
| `agent_state_versions` | Agent state versioning |
| `agent_events` | Agent event log |
| `notifications` | User notifications |

### 7.2 Data Access Pattern

**File**: `agents/tools/database.py`

**Key Function**: `get_profile_with_assessment(profile_id)`
```python
async def get_profile_with_assessment(profile_id: str) -> Optional[Dict]:
    # Fetches from profiles + assessments tables
    # Merges assessment.profile_data into profile
    # Returns unified profile dict
```

### 7.3 Profile Data Structure

Profile data is stored in `assessments.profile_data` JSON field:

```json
{
  "identity": { "strengths": [], "values": [] },
  "aptitude": { "gpa": 4.0, "sat_total": 1500, "intended_major": "..." },
  "passion": { "interests": [], "dream_career": "", "causes": [] },
  "service": { "volunteer_interests": [] },
  "experience": { "activities": [], "awards": [], "programs": [] }
}
```

---

## 8. Current State Issues

### 8.1 Critical Bug: Empty Spike

**Location**: `agents/agents/extracurriculars.py:152-154`

**Issue**: EC Agent returns placeholder with empty spike when no activities exist.

**Impact**:
- All new students get `spike=""` and `archetype="multi_hyphenate"` (default)
- Awards/Programs agents cannot do meaningful archetype-based filtering
- Strategic Intelligence features are useless for new users

**Root Cause**: Agent designed as analyzer only, not generator.

### 8.2 Missing Capability: Profile-Based Inference

**Expected**: EC Agent should infer identity from profile signals when activities are empty:
- `passion.interests`
- `passion.dream_career`
- `passion.causes`
- `aptitude.intended_major`
- `identity.strengths`

**Actual**: Agent gives up immediately if `activities = []`.

---

## 9. Processing Mode Analysis

### 9.1 What is Currently Deterministic

| Component | Agent | Type |
|-----------|-------|------|
| Activity extraction | EC | Parsing |
| Portfolio balance calculation | EC | Algorithm |
| Activity tier classification | EC | Rules |
| Eligibility filtering | Awards/Programs | Rules |
| Archetype fit filtering | Awards/Programs | Score threshold |
| 2-2-1 portfolio construction | Awards | Rules |
| ROI calculation | Awards | Algorithm |
| Timeline generation | All | Math |

### 9.2 What Currently Uses LLM

| Component | Agent | Purpose |
|-----------|-------|---------|
| Spike synthesis | EC | Generate spike phrase |
| Archetype determination | EC | Determine from signals |
| Win probability | Awards | Calculate hidden probability |
| Fit score calculation | Programs | Assess program fit |
| Master narrative | GamePlan | Synthesize story |
| Crisis resolution | Execution | Generate solutions |

### 9.3 What's Missing

| Component | Needed For |
|-----------|------------|
| Profile-based spike inference | New students without activities |
| Profile-based archetype scoring | New students without activities |
| LLM routing layer | Decide BUILD/OPTIMIZE/REFRAME strategy |
| Guardrails validation | Prevent hallucination |
| Grounding checks | Ensure awards/programs exist in KB |

---

## 10. File Summary

### Backend (agents/)

| Directory | Files | Lines | Purpose |
|-----------|-------|-------|---------|
| `agents/agents/` | 11 .py | 7,249 | Agent implementations |
| `agents/tools/` | 4 .py | ~500 | Database, utilities |
| `agents/workflows/` | 6 .py | ~800 | Scheduled workflows |
| `agents/seeds/enriched/` | 3 .json | 12,094 | Knowledge base |

### Frontend (components/, lib/)

| Directory | Files | Purpose |
|-----------|-------|---------|
| `components/agents/` | 15 .tsx | Agent UI components |
| `components/agents/cards/` | 8 .tsx | Agent card components |
| `components/ui/` | 20+ .tsx | UI primitives |
| `lib/store/` | 10 .ts | Zustand stores |
| `lib/types/` | 6 .ts | TypeScript types |
| `hooks/` | 1 .ts | Data fetching hooks |

---

## 11. Next Steps (Phase 2)

1. **Gap Analysis**: Compare current state to Hybrid Architecture v4.0
2. **Database Audit**: Document exact schema from Supabase
3. **Migration Plan**: Surgical, additive implementation strategy
4. **Supabase Vector Planning**: Design pgvector strategy if needed

---

*Document Version: 1.0*
*Generated: January 2026*
*Status: Ready for Phase 2 - Gap Analysis*
