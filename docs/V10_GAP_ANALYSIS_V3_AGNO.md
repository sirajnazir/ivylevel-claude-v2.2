# IvyQuest v10.0 Gap Analysis: Current State vs Agno Multi-Agent Spec v2.0

**Generated:** 2026-01-10
**Audited By:** Claude Code
**Based On:**
- MULTI_AGENT_PLATFORM_EVALUATION.md (Agno Framework Recommendation)
- IVYQUEST_MULTIAGENT_SPEC_V2.md (Full JTBD + Agno Tech Spec)
- IVYQUEST_EVALUATION_FRAMEWORK.md (Golden Benchmarks + LLM-as-Judge)

---

## Executive Summary

### Overall Status: 🟡 SIGNIFICANT REFACTORING REQUIRED

The current IvyQuest implementation uses **LangChain/LangGraph** architecture, but the V2 specification mandates migration to **Agno Framework** for 529× performance improvement. Additionally, the spec introduces **Jobs-to-be-Done (JTBD)** framework, **Proactive Workflows**, and **Evaluation Infrastructure** not present in current code.

| Category | Current | Target (V2 Spec) | Gap Status |
|----------|---------|------------------|------------|
| **Agent Framework** | LangChain + LangGraph | Agno | 🔴 FULL MIGRATION |
| **JTBD Architecture** | Not implemented | J1-J6 Job Mapping | 🔴 NOT STARTED |
| **AssessmentContract** | Partial (in store) | Full agent coordination | 🟡 PARTIAL |
| **Proactive Workflows** | Not implemented | 4 autonomous workflows | 🔴 NOT STARTED |
| **Evaluation Framework** | Not implemented | Golden + LLM-as-Judge | 🔴 NOT STARTED |
| **Jenny Intelligence** | Partial (5 of 12) | All 12 patterns | 🟡 PARTIAL |
| **Database Schema** | Complete (85%) | +3 new tables | 🟢 MINOR UPDATES |
| **NarrativeSynthesis** | ✅ Working | Working | ✅ COMPLETE |

---

## SECTION 1: Framework Migration Gap

### 1.1 Current Framework: LangChain + LangGraph

**Current Architecture:**
```
agents/
├── agents/
│   ├── base.py        # BaseAgent (LangChain)
│   ├── assessment.py  # ChatOpenAI (LangChain)
│   ├── gameplan.py    # ChatOpenAI (LangChain)
│   ├── awards.py      # ChatOpenAI (LangChain)
│   ├── opportunity.py # ChatOpenAI (LangChain)
│   └── narrative_synthesis.py # ChatGoogleGenerativeAI (LangChain)
├── graphs/
│   └── crisis_alchemy.py # LangGraph StateGraph
├── tools/
│   ├── database.py    # Supabase client
│   └── cri.py         # CRI computation
└── main.py            # FastAPI endpoints
```

**Dependencies:**
- `langchain-openai==0.2.14`
- `langchain-google-genai==2.0.8`
- `langgraph==0.2.61`

### 1.2 Target Framework: Agno

**Required Architecture (per V2 Spec):**
```
agents/
├── team.py              # Agno Team (Coaching Team)
├── agents/
│   ├── profile_decoder.py    # Agno Agent + Memory
│   ├── strategy_architect.py # Agno Agent + Memory
│   ├── awards_specialist.py  # Agno Agent + StructuredTools
│   ├── opportunity_scout.py  # Agno Agent + StructuredTools
│   └── execution_partner.py  # Agno Agent + Memory
├── tools/
│   ├── opportunity_tool.py   # Agno StructuredTool
│   ├── award_tool.py         # Agno StructuredTool
│   └── database.py
├── workflows/
│   ├── weekly_scout.py       # Agno Workflow (proactive)
│   ├── deadline_alert.py     # Agno Workflow (proactive)
│   ├── daily_checkin.py      # Agno Workflow (proactive)
│   └── silence_detector.py   # Agno Workflow (proactive)
├── memory/
│   └── supabase_storage.py   # AgentMemory with Supabase
└── main.py                   # FastAPI + Agno playground
```

**Required Dependencies:**
```
agno>=1.0.0           # Core framework
agno[openai]          # OpenAI models
agno[google]          # Google Gemini
agno[postgres]        # Supabase memory storage
```

### 1.3 Migration Effort Matrix

| Component | Current LOC | Migration Complexity | Estimated Effort |
|-----------|-------------|---------------------|------------------|
| Assessment Agent | 559 lines | HIGH - Full rewrite | 3 days |
| GamePlan Agent | 1014 lines | HIGH - Full rewrite | 4 days |
| Awards Agent | 788 lines | MEDIUM - Tool adaptation | 2 days |
| Opportunity Agent | 650 lines | MEDIUM - Tool adaptation | 2 days |
| Execution Agent | 950 lines | HIGH - State machine | 4 days |
| NarrativeSynthesis | 450 lines | LOW - Keep LangChain | 0.5 days |
| Crisis Alchemy Graph | 391 lines | MEDIUM - Agno Workflow | 2 days |
| Base Agent | 332 lines | DELETE - Use Agno Agent | N/A |

**Total Migration Estimate:** 17.5 developer-days

---

## SECTION 2: JTBD (Jobs-to-be-Done) Architecture Gap

### 2.1 Current State: No JTBD Framework

The current implementation has agents organized by **function** (Assessment, GamePlan, Awards, etc.) rather than by **student job**.

### 2.2 Target State: J1-J6 Job Mapping

Per V2 Spec, all agents must map to student jobs:

| Job | Description | Target Agent | Current Agent | Gap |
|-----|-------------|--------------|---------------|-----|
| **J1** | "Help me understand where I stand" | ProfileDecoder | AssessmentAgent | 🟡 RENAME + ENHANCE |
| **J2** | "Build a plan that actually works" | StrategyArchitect | GamePlanAgent | 🟡 RENAME + ENHANCE |
| **J3** | "Find me awards I can win" | AwardsSpecialist | AwardsAgent | 🟡 ADD JTBD MAPPING |
| **J4** | "Match me to summer programs" | OpportunityScout | OpportunityAgent | 🟡 ADD JTBD MAPPING |
| **J5** | "Help me actually finish things" | ExecutionPartner | ExecutionAgent | 🟡 ADD PROACTIVE |
| **J6** | "Write my story compellingly" | NarrativeCoach | NarrativeSynthesis | 🟢 WORKING |

### 2.3 Required AssessmentContract Schema

**Current Schema (in `lib/store/useResultsStore.ts`):**
```typescript
interface ResultsStore {
  assessment: Assessment | null;
  scores: {
    aptitude: number;
    passion: number;
    community: number;
    narrative: number;
    overall: number;
  } | null;
  archetype: Archetype | null;
  // ... missing many fields
}
```

**Target Schema (per V2 Spec):**
```typescript
interface AssessmentContract {
  // Core Assessment
  profile_id: string;
  assessment_timestamp: string;

  // Pillar Scores (0-100)
  scores: {
    aptitude: number;      // Weighted: gpa, sat, ap_count, rigor
    passion: number;       // Weighted: spike_depth, consistency, leadership
    community: number;     // Weighted: hours, impact, leadership
    narrative: number;     // Weighted: clarity, authenticity, differentiation
    overall: number;       // Weighted average
  };

  // Dimensional Analysis
  dimensional_breakdown: DimensionalScore[];

  // Narrative Components
  narrative: {
    brand_statement: string;
    narrative_dna: string;
    first_principle: string;
    themes: string[];
  };

  // Profile Data (raw)
  profile_data: {
    identity: IdentityData;
    operating: OperatingData;
    aptitude: AptitudeData;
    passion: PassionData;
    community: CommunityData;
  };

  // Strategic Analysis
  archetype: {
    id: string;
    confidence: number;
    rationale: string;
  };

  // Gaps & Opportunities
  gaps: {
    priority: 'P1' | 'P2' | 'P3';
    pillar: string;
    description: string;
    impact: number;
    actions: string[];
  }[];

  // Hidden (internal only)
  _hidden: {
    probabilities: Record<string, number>;
    hidden_target: string;
    cri: number;
  };
}
```

**Gap:** Current schema is ~40% complete. Missing:
- `dimensional_breakdown`
- `_hidden.probabilities`, `_hidden.hidden_target`, `_hidden.cri`
- Full `gaps` array structure
- Agent coordination fields

---

## SECTION 3: Proactive Workflows Gap

### 3.1 Current State: Reactive Only

Current agents only respond to explicit API calls. No autonomous workflows exist.

### 3.2 Target State: 4 Proactive Workflows

Per V2 Spec, the system must include autonomous workflows:

| Workflow | Trigger | Frequency | Current Status |
|----------|---------|-----------|----------------|
| **Weekly Scout** | Cron: Monday 9am | Weekly | 🔴 NOT IMPLEMENTED |
| **Deadline Alerts** | Database trigger | 30/7/3 days before | 🔴 NOT IMPLEMENTED |
| **Daily Check-in** | Cron: 3pm | Daily (if active) | 🔴 NOT IMPLEMENTED |
| **Silence Detector** | Activity monitor | After 3 days | 🟡 PARTIAL (code exists, not autonomous) |

### 3.3 Required Workflow Implementations

**Weekly Scout Workflow:**
```python
# agents/workflows/weekly_scout.py
from agno.workflow import Workflow, Task

class WeeklyScoutWorkflow(Workflow):
    """Proactively discover opportunities and send personalized alerts."""

    name = "weekly_scout"
    schedule = "0 9 * * MON"  # Monday 9am

    async def run(self, profile_id: str) -> ScoutReport:
        # 1. Get new opportunities since last week
        # 2. Filter by profile fit
        # 3. Generate personalized recommendations
        # 4. Send notification (email/push)
        pass
```

**Silence Detection (currently partial):**
- Code exists in `ExecutionAgent._detect_silence()` at line 795
- Not running autonomously
- Needs to be converted to Agno Workflow

---

## SECTION 4: Evaluation Framework Gap

### 4.1 Current State: No Evaluation Infrastructure

The current codebase has **no automated evaluation** of agent outputs.

### 4.2 Target State: Golden Dataset + LLM-as-Judge

Per Evaluation Framework V1.0, three evaluation layers required:

| Layer | Description | Current Status |
|-------|-------------|----------------|
| **Golden Dataset** | 20+ student profiles with Jenny Duan outputs | 🔴 NOT IMPLEMENTED |
| **Objective Metrics** | Automated checks (brand statement 15-25 words, etc.) | 🔴 NOT IMPLEMENTED |
| **LLM-as-Judge** | GPT-4o scoring with rubrics | 🔴 NOT IMPLEMENTED |

### 4.3 Required Evaluation Infrastructure

**Golden Dataset Schema:**
```python
# agents/evaluation/golden_dataset.py
@dataclass
class GoldenExample:
    profile_id: str
    input_profile: Dict                # Student profile data
    expected_brand_statement: str      # Jenny's output
    expected_themes: List[str]         # Jenny's themes
    expected_activities: List[str]     # Jenny's recommendations
    expected_awards: List[str]         # Jenny's award picks
    quality_annotations: Dict          # Human quality ratings
```

**LLM-as-Judge Rubric:**
```python
BRAND_STATEMENT_RUBRIC = """
Score the brand statement on a 1-5 scale:

1 (Poor): Generic, could apply to anyone
2 (Below Average): Some personalization but missing key identity markers
3 (Average): Decent personalization, captures spike
4 (Good): Strong identity synthesis, memorable
5 (Excellent): Instantly memorable, threads identity through spike and service

Student Profile:
{profile}

Brand Statement:
{brand_statement}

Score (1-5):
Rationale:
"""
```

**Database Tables Required:**
```sql
-- Evaluation golden dataset
CREATE TABLE evaluation_golden (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL,
  input_profile JSONB NOT NULL,
  expected_outputs JSONB NOT NULL,
  quality_annotations JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Evaluation runs
CREATE TABLE evaluation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_version VARCHAR(50) NOT NULL,
  golden_id UUID REFERENCES evaluation_golden(id),
  actual_outputs JSONB NOT NULL,
  objective_scores JSONB NOT NULL,
  llm_judge_scores JSONB NOT NULL,
  overall_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- A/B test results
CREATE TABLE ab_test_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_name VARCHAR(100),
  variant_a_config JSONB,
  variant_b_config JSONB,
  metrics JSONB,
  winner VARCHAR(10),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## SECTION 5: Jenny Intelligence Patterns Gap

### 5.1 Pattern Implementation Status

Per V2 Spec, 12 "Jenny Intelligence" patterns must be implemented:

| Pattern | Description | Current Status | Location |
|---------|-------------|----------------|----------|
| **Probability Sequencing** | Order awards by win probability | 🟢 IMPLEMENTED | awards.py:309 |
| **Rejection Alchemy** | Turn rejections into opportunities | 🟢 IMPLEMENTED | awards.py:382 |
| **3x Buffer** | Triple time estimates | 🟢 IMPLEMENTED | execution.py:862 |
| **Celebration Calibration** | Scale celebrations to difficulty | 🟢 IMPLEMENTED | execution.py:653 |
| **Silence Detection** | Detect inactive students | 🟡 PARTIAL | execution.py:795 |
| **Constraint Reframe** | Turn limitations to strengths | 🟡 PARTIAL | assessment.py:453 |
| **Narrative Threading** | Connect activities to story | 🟡 PARTIAL | gameplan.py:691 |
| **Identity Seed Planting** | Long-term positioning | 🟡 PARTIAL | gameplan.py:456 |
| **Crisis Alchemy** | 4-step crisis protocol | 🟢 IMPLEMENTED | crisis_alchemy.py |
| **Multi-Touchpoint Filter** | Require 4+ touchpoints | 🟡 PARTIAL | gameplan.py:198 |
| **Hidden Target Optimization** | Optimize for best-fit school | 🟡 PARTIAL | assessment.py:432 |
| **CRI Boost** | Context-adjusted scoring | 🟢 IMPLEMENTED | cri.py |

**Summary:** 6 complete, 6 partial, 0 missing

---

## SECTION 6: Agent-by-Agent Gap Analysis

### 6.1 ProfileDecoder (currently: AssessmentAgent)

| Spec Requirement | Current | Gap |
|------------------|---------|-----|
| Agno Agent class | LangChain ChatOpenAI | 🔴 MIGRATE |
| Memory: Supabase | Manual DB calls | 🟡 ADD AGNO MEMORY |
| Output: AssessmentContract | Partial dict | 🟡 EXTEND SCHEMA |
| synthesize_narrative_dna() | ✅ In NarrativeSynthesis | 🟢 COMPLETE |
| detect_archetype() | ✅ Working | 🟢 COMPLETE |
| calculate_hidden_probabilities() | ✅ Working | 🟢 COMPLETE |
| compute_cri() | ✅ Working | 🟢 COMPLETE |
| constraint_reframe() | ⚠️ Basic | 🟡 ENHANCE |

**Action Items:**
1. Migrate to Agno Agent with `AgentMemory(db=PostgresStore)`
2. Extend output schema to full AssessmentContract
3. Enhance constraint_reframe with SFFA rubric mapping

### 6.2 StrategyArchitect (currently: GamePlanAgent)

| Spec Requirement | Current | Gap |
|------------------|---------|-----|
| Agno Agent class | LangChain ChatOpenAI | 🔴 MIGRATE |
| filter_activities_by_roi() | ✅ Working | 🟢 COMPLETE |
| plant_identity_seeds() | ✅ Working | 🟢 COMPLETE |
| apply_strategic_overwhelm() | ✅ Working | 🟢 COMPLETE |
| thread_narrative_dna() | ⚠️ Basic | 🟡 ENHANCE |
| Master Narrative synthesis | ✅ In NarrativeSynthesizer | 🟢 COMPLETE |
| Narrative coherence validation | ✅ Working | 🟢 COMPLETE |

**Action Items:**
1. Migrate to Agno Agent
2. Enhance thread_narrative_dna() with LLM-based connections

### 6.3 AwardsSpecialist (currently: AwardsAgent)

| Spec Requirement | Current | Gap |
|------------------|---------|-----|
| Agno Agent class | LangChain ChatOpenAI | 🔴 MIGRATE |
| StructuredTool: AwardSearchTool | None | 🔴 ADD TOOL |
| calculate_win_probability() | ✅ Working | 🟢 COMPLETE |
| balance_portfolio() | ✅ Working | 🟢 COMPLETE |
| process_rejection() | ✅ Working | 🟢 COMPLETE |
| probability_sequencing() | ✅ Working | 🟢 COMPLETE |
| 200+ awards database | ⚠️ 5 sample awards | 🟡 POPULATE |

**Action Items:**
1. Migrate to Agno Agent with AwardSearchTool
2. Populate awards table with 200+ real awards

### 6.4 OpportunityScout (currently: OpportunityAgent)

| Spec Requirement | Current | Gap |
|------------------|---------|-----|
| Agno Agent class | LangChain ChatOpenAI | 🔴 MIGRATE |
| StructuredTool: OpportunitySearchTool | None | 🔴 ADD TOOL |
| calculate_fit_score() | ✅ Working | 🟢 COMPLETE |
| send_advance_alerts() | ✅ Working | 🟢 COMPLETE |
| create_backup_cascade() | ✅ Working | 🟢 COMPLETE |
| Weekly Scout Workflow | None | 🔴 ADD WORKFLOW |
| 500+ opportunities database | ⚠️ 5 sample | 🟡 POPULATE |

**Action Items:**
1. Migrate to Agno Agent with OpportunitySearchTool
2. Create WeeklyScoutWorkflow
3. Populate opportunities table with 500+ programs

### 6.5 ExecutionPartner (currently: ExecutionAgent)

| Spec Requirement | Current | Gap |
|------------------|---------|-----|
| Agno Agent class | LangChain/LangGraph | 🔴 MIGRATE |
| scaffold_project() | ✅ Working | 🟢 COMPLETE |
| handle_crisis() | ✅ Working (LangGraph) | 🟡 MIGRATE TO AGNO |
| detect_blockers() | ✅ Working | 🟢 COMPLETE |
| compute_eds() | ✅ Working | 🟢 COMPLETE |
| silence_detection() | ⚠️ Not autonomous | 🟡 ADD WORKFLOW |
| celebration_calibration() | ✅ Working | 🟢 COMPLETE |
| 3x_buffer() | ✅ Working | 🟢 COMPLETE |
| Daily Check-in Workflow | None | 🔴 ADD WORKFLOW |

**Action Items:**
1. Migrate Crisis Alchemy from LangGraph to Agno Workflow
2. Create SilenceDetectorWorkflow
3. Create DailyCheckinWorkflow

### 6.6 NarrativeCoach (currently: NarrativeSynthesisAgent)

| Spec Requirement | Current | Gap |
|------------------|---------|-----|
| Jenny's Formula synthesis | ✅ Working (Gemini) | 🟢 COMPLETE |
| brand_statement generation | ✅ Working | 🟢 COMPLETE |
| narrative_dna extraction | ✅ Working | 🟢 COMPLETE |
| theme identification | ✅ Working | 🟢 COMPLETE |
| first_principle extraction | ✅ Working | 🟢 COMPLETE |
| Micro-Edit Mastery | None | 🔴 ADD FEATURE |
| Talk-First-Write-Second | ⚠️ UI only | 🟡 INTEGRATE |

**Action Items:**
1. Add micro_edit_patterns tool
2. Integrate VoiceInput component with essay workflow

---

## SECTION 7: Database Schema Updates Required

### 7.1 Current Schema Status

All core v10.0 tables exist. Three new tables required for V2 spec:

```sql
-- 1. Evaluation golden dataset
CREATE TABLE IF NOT EXISTS evaluation_golden (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID,
  input_profile JSONB NOT NULL,
  expected_outputs JSONB NOT NULL,
  jenny_annotations JSONB,
  difficulty_tier VARCHAR(20), -- 'easy', 'medium', 'hard'
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Evaluation runs
CREATE TABLE IF NOT EXISTS evaluation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id VARCHAR(100) NOT NULL,
  agent_version VARCHAR(50) NOT NULL,
  golden_id UUID REFERENCES evaluation_golden(id),
  actual_outputs JSONB NOT NULL,
  objective_scores JSONB,
  llm_judge_scores JSONB,
  overall_score FLOAT,
  passed BOOLEAN,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Proactive workflow state
CREATE TABLE IF NOT EXISTS workflow_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID REFERENCES profiles(id),
  workflow_name VARCHAR(100) NOT NULL,
  last_run TIMESTAMPTZ,
  next_run TIMESTAMPTZ,
  state JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(profile_id, workflow_name)
);
```

### 7.2 Profile Table Extensions

```sql
-- Add columns for proactive workflows
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMPTZ;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS preferred_contact_time TIME;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{"email": true, "push": true, "sms": false}';
```

---

## SECTION 8: Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
**Goal:** Agno framework setup + core migration

| Task | Effort | Priority |
|------|--------|----------|
| Install Agno dependencies | 0.5 days | P0 |
| Create Agno Team (CoachingTeam) | 1 day | P0 |
| Migrate ProfileDecoder | 3 days | P0 |
| Migrate StrategyArchitect | 2 days | P0 |
| Create database migration | 0.5 days | P0 |

### Phase 2: Specialist Agents (Week 3-4)
**Goal:** Complete agent migration + tools

| Task | Effort | Priority |
|------|--------|----------|
| Create AwardSearchTool | 1 day | P1 |
| Migrate AwardsSpecialist | 2 days | P1 |
| Create OpportunitySearchTool | 1 day | P1 |
| Migrate OpportunityScout | 2 days | P1 |
| Populate awards/opportunities DBs | 2 days | P1 |

### Phase 3: Execution + Workflows (Week 5)
**Goal:** ExecutionPartner + proactive workflows

| Task | Effort | Priority |
|------|--------|----------|
| Migrate ExecutionPartner | 3 days | P0 |
| Create WeeklyScoutWorkflow | 1 day | P1 |
| Create DeadlineAlertWorkflow | 0.5 days | P1 |
| Create SilenceDetectorWorkflow | 0.5 days | P2 |

### Phase 4: Evaluation Infrastructure (Week 6)
**Goal:** Golden dataset + automated testing

| Task | Effort | Priority |
|------|--------|----------|
| Create GoldenDataset schema | 1 day | P1 |
| Build 20+ golden examples | 3 days | P1 |
| Implement LLM-as-Judge | 2 days | P1 |
| Create evaluation pipeline | 1 day | P1 |

### Phase 5: Polish + Testing (Week 7)
**Goal:** Integration testing + benchmarks

| Task | Effort | Priority |
|------|--------|----------|
| End-to-end integration tests | 2 days | P0 |
| Performance benchmarks | 1 day | P2 |
| Documentation | 1 day | P2 |
| Huda benchmark validation | 1 day | P1 |

---

## SECTION 9: Code to Delete

The following code should be deleted after Agno migration:

| File | Reason | Lines |
|------|--------|-------|
| `agents/agents/base.py` | Replaced by Agno Agent | 332 |
| `agents/graphs/crisis_alchemy.py` | Migrate to Agno Workflow | 391 |

**Total lines to delete:** ~723

---

## SECTION 10: Code to Keep

The following code can be retained with minimal changes:

| File | Reason | Changes |
|------|--------|---------|
| `agents/tools/cri.py` | Pure computation, framework-agnostic | None |
| `agents/tools/database.py` | Supabase client, use for AgentMemory | Minor adapter |
| `agents/agents/narrative_synthesis.py` | Working with Gemini | Keep as fallback |
| All migration files | Database schema | Add 3 new tables |

---

## SECTION 11: Success Criteria

### Functional Requirements

| Requirement | Metric | Target |
|-------------|--------|--------|
| Assessment completion | End-to-end flow works | 100% |
| Narrative generation | Brand statement quality | 4.0/5.0 LLM-judge |
| Awards matching | Win rate (Huda benchmark) | >40% |
| Opportunity matching | Top 3 relevance | >80% fit score |
| Crisis recovery | Response time | <72 hours |
| Proactive alerts | Delivery rate | >90% |

### Performance Requirements

| Metric | Current | Target (Agno) |
|--------|---------|---------------|
| Agent response time | ~3-5s | <1s |
| Memory efficiency | N/A | 50% reduction |
| Concurrent users | ~10 | 100+ |

### Evaluation Requirements

| Metric | Target |
|--------|--------|
| Golden dataset coverage | 20+ profiles |
| Objective test pass rate | >95% |
| LLM-judge score | >4.0/5.0 average |
| Huda benchmark | Match or exceed |

---

## Conclusion

The V2 Multi-Agent specification requires **significant refactoring** of the current IvyQuest agent architecture:

1. **Framework Migration**: LangChain → Agno (~17.5 days)
2. **New Infrastructure**:
   - 4 Proactive Workflows
   - Evaluation Framework (Golden + LLM-as-Judge)
   - 3 new database tables
3. **Data Population**: 200+ awards, 500+ opportunities
4. **Feature Completion**: 6 partial Jenny Intelligence patterns

**Estimated Total Effort:** 7 weeks (1 developer)

**Recommended Approach:**
1. Retain `NarrativeSynthesisAgent` (working with Gemini)
2. Incremental migration: one agent at a time
3. Parallel track: evaluation infrastructure
4. Golden dataset from existing Jenny coaching data

**Risk Mitigation:**
- Keep LangChain as fallback during migration
- Feature flags for Agno vs LangChain
- Extensive integration testing before cutover
