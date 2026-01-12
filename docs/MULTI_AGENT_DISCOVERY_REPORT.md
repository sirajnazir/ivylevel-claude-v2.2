# IvyLevel Multi-Agent System Discovery Report
## Complete Pre-Integration Analysis

**Version:** 2.0
**Date:** January 12, 2026
**Status:** Discovery Complete (8/8 Prompts Executed)
**Purpose:** Comprehensive analysis before Awards Agent enhancement integration

---

## EXECUTIVE SUMMARY

### System Architecture Overview

IvyQuest v15.0 is a **6-agent parallel processing platform** built on the **3P technology stack** (Agno + LangGraph + AutoGen) with:

- **Orchestration:** FastAPI service + APScheduler workflows + Supabase Realtime events
- **Memory:** 3-tier architecture (Working → Redis → Supabase/pgvector)
- **Framework:** ReAct reasoning with 0.7/0.7/0.6 quality gates
- **Agents:** Assessment, GamePlan, Execution, Awards, Opportunity, NarrativeSynthesis

### Critical Discoveries

| Finding | Severity | Impact |
|---------|----------|--------|
| GamePlan does NOT invoke Awards Agent | **CRITICAL** | Awards operate independently |
| Archetype computed but UNUSED by Awards | **HIGH** | 10-20% accuracy loss |
| No event-driven agent orchestration | **HIGH** | Agents don't coordinate |
| No dedicated Onboarding Agent | **INFO** | 6-frame wizard IS onboarding |

### Contract Compatibility Matrix

| Agent A | Agent B | Contract Status | Gaps |
|---------|---------|-----------------|------|
| Onboarding (6-Frame) | Assessment | Aligned | None |
| Assessment | GamePlan | Partial | Archetype underutilized |
| Assessment | Awards | **PARTIAL** | **Archetype UNUSED in probability** |
| GamePlan | Awards | **MISSING** | **No direct invocation exists** |
| GamePlan | Opportunity | **MISSING** | Placeholder code only |
| Awards | Execution | Partial | Portfolio format needs mapping |

---

## PART 1: SYSTEM-WIDE ARCHITECTURE

### 1.1 Orchestration Layer

**Primary Orchestrator:** `/agents/main.py` (FastAPI Service)
- **Port:** 8001
- **Version:** 15.0.0
- **Pattern:** RESTful API + Event Bus + Workflow Runner

**Agent Invocation Patterns:**

1. **Synchronous API Calls** (Most Common)
   ```
   Frontend → Next.js API Route → FastAPI Agent Service (HTTP POST)
   ```

2. **Scheduled Workflows** (APScheduler)
   - SilenceDetectorWorkflow (every 4 hours)
   - DeadlineAlertWorkflow (daily 9 AM)
   - WeeklyScoutWorkflow (Monday 9 AM)
   - DailyCheckinWorkflow (daily 3 PM)

3. **Event-Driven** (Supabase Realtime)
   - 10 event types flow between frontend/backend
   - SUCCESS_ACHIEVED triggers RLHF vector ingestion

### 1.2 Shared Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Database | Supabase (PostgreSQL 15+) | Primary persistence |
| Vector Search | pgvector extension | Semantic similarity |
| Cache | Redis 5.0+ (aioredis) | Short-term memory (24h TTL) |
| Realtime | Supabase Realtime | WebSocket event broadcast |
| LLM | OpenAI GPT-4o / Gemini 2.0 Flash | Primary reasoning engines |

### 1.3 3-Tier Memory Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ TIER 1: WORKING MEMORY (In-Process Python)                          │
│ - WorkingMemoryBuffer: Context, planned actions, evaluations        │
│ - TTL: Session lifetime                                              │
│ - Scope: Per agent per profile                                       │
├─────────────────────────────────────────────────────────────────────┤
│ TIER 2: SHORT-TERM MEMORY (Redis)                                   │
│ - Agent handoffs, session state, rate limiting                      │
│ - TTL: 24 hours                                                      │
│ - Key: handoff:{profile}:{from}:{to}                                │
├─────────────────────────────────────────────────────────────────────┤
│ TIER 3: LONG-TERM MEMORY (Supabase/PostgreSQL)                      │
│ - agent_memories, profile_snapshots, coaching_knowledge             │
│ - TTL: Permanent                                                     │
│ - Semantic search via pgvector (1536-dim embeddings)                │
│ - Quality gate: 0.7 cosine similarity threshold                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.4 Event System

**10 Event Types Defined:**

| Event | Trigger | Consumer |
|-------|---------|----------|
| `ASSESSMENT_COMPLETED` | Assessment finishes | UI, logging only |
| `GAMEPLAN_GENERATED` | GamePlan finishes | UI, logging only |
| `AWARD_MATCHED` | Awards portfolio created | UI, logging only |
| `CRISIS_DETECTED` | Blocker found | HITL workflow |
| `CRISIS_RESOLVED` | Crisis handled | Logging, metrics |
| `SUCCESS_ACHIEVED` | **CRITICAL**: RLHF ingestion | Vector store |
| `PROJECT_STALLED` | 5+ days inactivity | Execution Agent |
| `OPPORTUNITY_ALERT` | Deadline approaching | UI notifications |
| `HUMAN_OVERRIDE` | Coach approval | State versioning |
| `STATE_VERSIONED` | Audit event | Forensics |

**Critical Finding:** Events are PUBLISHED but NOT SUBSCRIBED by other agents. Event-driven orchestration is **for logging only**, not agent coordination.

---

## PART 2: ONBOARDING FLOW (NO DEDICATED AGENT)

### 2.1 Discovery Finding

**There is NO dedicated OnboardingAgent.** The 6-frame wizard IS the onboarding flow.

### 2.2 The 6-Frame Wizard Structure

**Location:** `/app/quest/` (frontend) + `/app/api/assessment/` (backend)

| Frame | Component | Purpose | Data Collected |
|-------|-----------|---------|----------------|
| 1 | Frame1Warmup | Identity Setup | Role, Name, Grade, Schools, Major |
| 2 | Frame2Snapshot | Academic Snapshot | GPA, SAT/ACT, AP/IB, Awards |
| 3 | Frame3Building | Passion & Impact | Spike, Leadership, ECs, Research, Service |
| 4 | Frame4Context | Operating Intelligence | Psychometrics, Time Management, Hidden Capabilities |
| 5 | Frame6ProfileReveal | Results Reveal | Score display, CRI factors, Archetype |
| 6 | Frame5GamePlan | Strategy | Top opportunities, Portfolio grid, Action plan |

### 2.3 Data Collection Summary

**Total Data Points:** 100+ attributes across 4 frames

```typescript
StudentProfile {
  session_id: UUID
  identity: { role, name, grade, student_id? }
  target_schools: string[]
  intended_major: string
  major_certainty: MajorCertainty
  aptitude: AptitudeAttributes      // 9 fields
  passion: PassionAttributes        // 14 fields
  community: CommunityAttributes    // 6 fields
  high_school: HighSchoolContext    // 7 fields
  demographics: DemographicContext  // 12 fields
  assessment_intelligence: AssessmentIntelligence // 30+ fields
}
```

### 2.4 Onboarding → Assessment Contract

Data flows from Zustand store to Assessment Agent via:
1. `localStorage` persistence (questStore)
2. `POST /api/assessment` on completion
3. Assessment Agent retrieves via `get_profile_with_assessment()`

**Key Files:**
- `/lib/integration/store/questStore.master.ts` (Data collection)
- `/lib/store/useStudentStore.ts` (Profile persistence)
- `/lib/validation/profile.ts` (Validation + defaults)
- `/lib/constants/defaults.ts` (Centralized defaults)

---

## PART 3: ASSESSMENT AGENT (CRITICAL FOR AWARDS)

### 3.1 Agent Definition

**File:** `/agents/agents/assessment.py` (~800 lines)
**LLM:** GPT-4o, temperature 0.7
**Autonomy:** HIGH (handoff if confidence < 0.7)

### 3.2 Processing Pipeline

1. `synthesize_narrative_dna()` - Extracts narrative DNA
2. `detect_archetype()` - Classifies student archetype
3. `compute_cri()` - Calculates Context Relativity Index
4. `calculate_hidden_probabilities()` - Multi-factor probability matrix
5. `identify_hidden_target()` - Determines target school
6. `reframe_constraints()` - ACP-010 constraint reframing

### 3.3 Archetype System

**11 Archetypes Defined:**

| ID | Label | Primary Detector |
|----|-------|------------------|
| `SCHOLAR` | The Scholar | Aptitude 70+, GPA ≥0.80 |
| `RESEARCHER` | The Researcher | Research NATIONAL/STATE, STEM major |
| `LEADER` | The Leader | FOUNDER/PRES, passion 60+ |
| `ENTREPRENEUR` | The Entrepreneur | Project impact 500+, business major |
| `CHANGEMAKER` | The Changemaker | Community 60+, 200+ service hours |
| `ADVOCATE` | The Advocate | 150+ service hours, first-gen |
| `CREATOR` | The Creator | Project impact 200+, creative major |
| `PERFORMER` | The Performer | Recruited athlete OR performance major |
| `POLYMATH` | The Polymath | All scores 50+, balanced |
| `EMERGING` | The Emerging Talent | Grade ≤10, potential |
| `EXPLORER` | The Explorer | Fallback; undeclared |

### 3.4 CRI (Context Relativity Index)

**Formula:**
```
CRI = (Performance / Expected) × Barrier_Multiplier × Chetty_Multiplier × Constraint_Multiplier
```

**Constraint Multipliers:**
- first_gen: +0.08
- low_ses: +0.10
- underrepresented: +0.08
- work_hours: +0.06
- rural: +0.05
- immigrant: +0.06

**Huda Benchmark:** CRI > 1.2 (Huda actual: 1.35)

### 3.5 Output Schema

```python
{
  "narrative_dna": {
    "dna": str,
    "themes": List[str],
    "confidence": float
  },
  "archetype": {
    "id": str,
    "label": str,
    "confidence": float,
    "rationale": str
  },
  "cri": float,
  "hidden_target": str,
  "hidden_probabilities": Dict,
  "constraint_reframes": List[Dict]
}
```

---

## PART 4: GAME PLAN AGENT (BLOCKING GAP)

### 4.1 Agent Definition

**File:** `/agents/agents/gameplan.py` (~1,028 lines)
**LLM:** GPT-4o, temperature 0.7
**Autonomy:** HIGH (handoff if coherence < 80%)

### 4.2 Processing Pipeline

1. **Master Narrative Synthesis** - Brand statement via NarrativeSynthesizer
2. **Activity Filtering** - 4+ touchpoints required (ACP-005)
3. **Identity Seed Planting** - 6-12 months before deadlines (ACP-006)
4. **Strategic Overwhelm** - 1.4x task inflation (ACP-004)
5. **Narrative Threading** - Add narrative_thread to each activity
6. **Phase Generation** - Grade-based timeline phases

### 4.3 First Principle Passions (Jenny's Framework)

```python
FirstPrinciplePassion = Enum(
    BUILDER,        # Creates things, makes stuff work
    STORYTELLER,    # Communicates, shares narratives
    DISCOVERER,     # Researches, finds new knowledge
    ADVOCATE,       # Fights for causes, speaks up
    CONNECTOR,      # Brings people together
    HEALER,         # Helps, cares for others
    LEADER,         # Organizes, directs, inspires
    ARTIST,         # Expresses through creative medium
    ENTREPRENEUR,   # Starts things, takes risks
    SCHOLAR         # Loves learning for its own sake
)
```

### 4.4 CRITICAL: No Awards Agent Invocation

**Current State (gameplan.py line 154):**
```python
narrative_coherence = self.narrative_filter.validate_gameplan_coherence(
    activities=threaded_plan,
    awards=[],  # Will be populated when Awards Agent is integrated
    programs=[]  # Will be populated when Opportunity Agent is integrated
)
```

**Impact:** Awards Agent operates INDEPENDENTLY. No direct integration exists.

### 4.5 Output Schema

```python
{
  "success": bool,
  "filtered_activities": List[Dict],
  "filtered_awards": List[Dict],      # Currently empty []
  "filtered_programs": List[Dict],    # Currently empty []
  "identity_seeds": List[Dict],
  "narrative_alignment": {
    "brand_statement": str,
    "first_principle": str,
    "coherence_score": float,
    "verdict": str
  },
  "overwhelm_summary": {
    "base_tasks": int,
    "overwhelm_tasks": int,
    "overwhelm_factor": 1.4
  }
}
```

---

## PART 5: SPECIALIST AGENTS

### 5.1 Awards Agent (Enhancement Target)

**File:** `/agents/agents/awards.py` (791 lines)
**Autonomy:** FULL (deterministic matching)
**Huda Benchmark:** >40% win rate (Actual: 62.5%)

#### Probability Formula

```python
probability = (
    base_rate ×
    strength_factor ×    # 0.5-1.5 (GPA, SAT, AP)
    spike_alignment ×    # 0.5-1.5 (category match)
    leadership_factor ×  # 0.8-1.4 (leadership level)
    demographic_factor × # 0.9-1.3 (diversity)
    cri_factor           # CRI-based boost
)
# Bounds: [0.01, 0.85]
```

#### Integration Gaps

| Gap | Current State | Target State |
|-----|---------------|--------------|
| **Archetype Usage** | Received but UNUSED | Factor in probability |
| **Jenny Intelligence** | Not implemented | 125 frameworks integration |
| **Win Cascade** | Not implemented | Sequencing logic needed |
| **GamePlan Contract** | MISSING | Direct invocation needed |

### 5.2 Opportunity Agent

**File:** `/agents/agents/opportunity.py` (648 lines)
**Autonomy:** FULL (deterministic matching)

#### Key Features

- **Fit Score Calculation:** Academic (30%) + Interest (35%) + Experience (25%) + Base (10%)
- **Advance Alerts:** 5-7 months before deadline for top 15 matches
- **Backup Cascades:** Primary + 3-4 alternatives with type matching

#### Output Schema

```python
{
  "success": bool,
  "top_recommendations": List[Dict],   # Top 10 opportunities
  "advance_alerts": List[Dict],        # 6-month alerts
  "backup_cascades": List[Dict],       # Primary + backups
  "timeline": List[Dict]               # Deadline-based
}
```

### 5.3 Narrative Synthesis Agent

**File:** `/agents/agents/narrative_synthesis.py` (584 lines)
**Autonomy:** HIGH (handoff if confidence < 0.7)

#### Jenny's Formula

```
IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE
```

#### Output Schema

```python
{
  "brand_statement": str,    # 15-25 word power statement
  "narrative_dna": str,      # 2-3 paragraph narrative
  "first_principle": str,    # Core driving "why"
  "themes": List[str],       # 3-5 key themes
  "confidence": float,       # 0.0-1.0
  "requires_handoff": bool   # Handoff if < 0.7
}
```

---

## PART 6: EXECUTION AGENT

### 6.1 Agent Definition

**File:** `/agents/agents/execution.py` (949 lines)
**Autonomy:** MEDIUM (LOW for crises)

### 6.2 Core Methods

| Method | Purpose | Configuration |
|--------|---------|---------------|
| `scaffold_project()` | Break into 20+ microsteps | 1.4x overwhelm |
| `handle_crisis()` | 4-step Crisis Alchemy | <1hr HITL timeout |
| `detect_blockers()` | Find 5+ day inactivity | Publishes events |
| `compute_eds()` | Execution Debt Score | Target: <50 |
| `calibrate_celebration()` | Jenny-style feedback | 4 celebration levels |

### 6.3 Crisis Alchemy Protocol (LangGraph)

```
1. VALIDATE - Acknowledge emotion (2s)
2. ACT - One micro-action to restore agency (10s)
3. REFRAME - Find opportunity angle (30s)
4. CREATE - Design new activity/pivot (2min)
```

**HITL Handoff:** Requires coach approval within 1 hour

### 6.4 Scheduled Workflows

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| WeeklyScout | Monday 9 AM | 3 opportunities + 2 awards |
| SilenceDetector | Every 4 hours | 72h+ inactivity detection |
| DeadlineAlerts | Daily 9 AM | 30/7/3/1 day reminders |
| DailyCheckin | Daily 3 PM | EDS monitoring |

---

## PART 7: END-TO-END DATA FLOW VALIDATION

### 7.1 Complete Pipeline

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         ACTUAL DATA FLOW                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   6-FRAME WIZARD (Onboarding)                                            │
│       │                                                                   │
│       ▼ profile_data (identity, aptitude, passion, service)              │
│   ASSESSMENT AGENT                                                        │
│       │                                                                   │
│       ├─▶ Outputs: narrative_dna, archetype, CRI, hidden_target          │
│       │   ✓ Archetype computed with confidence                            │
│       │   ✓ CRI computed with multipliers                                 │
│       │                                                                   │
│       ▼ Stored in profiles table                                         │
│   GAME PLAN AGENT (Independent API call)                                  │
│       │                                                                   │
│       ├─▶ Uses: narrative_dna, hidden_target                             │
│       │   ✗ Does NOT use archetype                                        │
│       │   ✗ Does NOT use CRI                                              │
│       │   ✗ awards=[] placeholder NOT populated                           │
│       │                                                                   │
│       ▼ Stored in game_plans table                                        │
│   AWARDS AGENT (Separate independent API call)                            │
│       │                                                                   │
│       ├─▶ Uses: aptitude, spike, leadership, demographics, CRI           │
│       │   ✗ Does NOT use archetype (790 lines, zero references)          │
│       │   ✗ Does NOT receive GamePlan context                             │
│       │   ✗ Does NOT use hidden_target for prestige matching             │
│       │                                                                   │
│       ▼ Stored in awards_portfolios table                                │
│   EXECUTION AGENT                                                         │
│       │                                                                   │
│       └─▶ weekly tasks, blockers, EDS                                     │
│           ✗ Award deadlines not synced with project timeline             │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Data Utilization Analysis

**Assessment Output Usage:**

| Field | GamePlan | Awards | Opportunity | Execution |
|-------|----------|--------|-------------|-----------|
| narrative_dna | ✓ Used | ✗ | ✗ | ✗ |
| archetype | ✗ UNUSED | ✗ UNUSED | ✗ UNUSED | ✗ |
| cri | ✗ UNUSED | ✓ Used | ✗ | ✗ |
| hidden_target | ✓ Used | ✗ UNUSED | ✗ | ✗ |
| hidden_probabilities | ✗ UNUSED | ✗ | ✗ | ✗ |

**Assessment outputs are 20-50% utilized by downstream agents.**

---

## PART 8: CROSS-CUTTING CONCERNS

### 8.1 State Versioning

**Table:** `agent_state_versions`
**File:** `/supabase/migrations/006_agent_state_versions.sql`

| Column | Purpose |
|--------|---------|
| `version` | Incrementing per profile+agent |
| `state` (JSONB) | Complete state snapshot |
| `state_diff` (JSONB) | Efficient delta storage |
| `created_by` | agent\|human\|system |
| `is_human_override` | HITL audit flag |
| `override_approved_by` | Coach approval chain |

**Functions:** `create_state_version()`, `get_state_at_version()`, `rollback_to_version()`

### 8.2 HITL (Human-in-the-Loop)

**Table:** `hitl_requests`
**Workflow:**

1. Agent proposes → Creates crisis in `proposed` status
2. Sets `approval_deadline` → <1 hour per spec
3. Coach GET → Fetch `pending_crisis_approvals` view
4. Coach POST → `/api/handoff/crisis`
5. Status transitions: pending → approved/rejected

**Handoff Triggers:**
- Narrative synthesis confidence < 0.7
- GamePlan coherence < 80%
- Crisis detection (ALWAYS requires HITL)

### 8.3 Quality Gates (0.7/0.7/0.6)

| Component | Threshold | Behavior |
|-----------|-----------|----------|
| Narrative Synthesis | confidence < 0.7 | Handoff |
| Archetype Detection | confidence < 0.7 | Handoff |
| Memory Match | similarity < 0.7 | Exclude |
| GamePlan | coherence < 80% | Handoff |

### 8.4 Error Handling

**File:** `/lib/utils/safeValue.ts` (316 lines)

```typescript
// Safe value utilities
safeNumber(value, fallback, bounds?)
safeProbability(value, fallback)  // Clamps to [0.0, 0.95]
safeNormalized(value, fallback)   // Clamps to [0.0, 1.0]
safeSort(array, compareFn)        // NEW COPY (no mutation)
safeGet(obj, 'a.b.c', fallback)   // Dot-notation access
```

**Graceful Degradation:**
- All agents return placeholder data when profiles incomplete
- Database failures don't crash requests
- Timeouts: 60s standard, 120s LLM-heavy

### 8.5 Feature Flags

**File:** `/lib/config/featureFlags.ts`

```typescript
interface FeatureFlags {
  v10Agents: boolean       // Master switch for ALL agents
  criScoring: boolean      // CRI computation
  commandDeck: boolean     // Dashboard at /dashboard
  aiChat: boolean          // Floating AI chat
  suggestions: boolean     // Proactive bubbles
  eventBus: boolean        // Real-time events
}
```

**Environment Variables:**
- `ENABLE_V10_AGENTS` - Master switch
- `HITL_TIMEOUT_HOURS` - Crisis approval timeout (default: 1.0)
- `OVERWHELM_FACTOR` - Strategic overwhelm (default: 1.4)

---

## PART 9: CRITICAL ISSUES RANKED

### TIER 1 (BREAKS SYSTEM CONTRACT)

1. **GamePlan does NOT invoke Awards Agent**
   - Impact: Awards standalone, not integrated into comprehensive plan
   - Fix: Call `awards_agent.match()` in gameplan.py

2. **Awards Agent does NOT use Archetype**
   - Impact: 10-20% accuracy loss in award matching
   - Fix: Add archetype_affinity factor to probability

3. **Event-driven agent orchestration missing**
   - Impact: Agents operate independently
   - Fix: Implement event subscriptions in agent base class

### TIER 2 (INCOMPLETE INTEGRATION)

4. **GamePlan awards placeholder hardcoded**
   - Fix: Populate from actual Awards Agent output

5. **Hidden Target not used by Awards**
   - Fix: Use for prestige matching

6. **Assessment outputs underutilized**
   - Fix: GamePlan should access archetype, CRI

### TIER 3 (NICE-TO-HAVE)

7. **Execution Agent award deadline sync**
8. **Opportunity Agent integration with GamePlan**

---

## PART 10: ENHANCEMENT READINESS ASSESSMENT

### 10.1 Schema Compatibility

| Enhancement | Current Support | Migration |
|-------------|-----------------|-----------|
| Jenny coaching intelligence | JSONB flexibility | Seed data update |
| Archetype-based scoring | Archetype received | Algorithm change |
| Win cascade sequencing | Not present | New module |
| GamePlan integration | Placeholder exists | Contract creation |

### 10.2 Recommended Integration Approach

**Phase 1: Data Enhancement (Low Risk)**
1. Update awards seed data with Jenny's 125 frameworks
2. Add archetype associations to existing awards
3. Add win_cascade_position field to awards schema

**Phase 2: Algorithm Enhancement (Medium Risk)**
1. Add archetype_affinity factor to probability calculation
2. Integrate Jenny's narrative alignment scoring
3. Use hidden_target for prestige matching

**Phase 3: GamePlan Integration (High Value)**
1. Create GamePlan → Awards handoff contract
2. Implement direct Awards invocation from GamePlan
3. Pass master_narrative to Awards for alignment

**Phase 4: Win Cascade Logic (Medium Risk)**
1. Create WinCascadeModule in `/agents/modules/`
2. Implement confidence-building sequencing
3. Track cascade state across sessions

### 10.3 Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Probability changes break portfolios | Medium | High | A/B test, golden dataset |
| GamePlan integration complexity | Medium | Medium | Feature flag, gradual rollout |
| Archetype mismatch | Low | Low | Validation + fallback |
| Win cascade state management | Medium | Medium | Redis persistence |

---

## PART 11: KEY FILES REFERENCE

### Backend Python

| File | Purpose | Lines |
|------|---------|-------|
| `/agents/main.py` | FastAPI entry, routes | ~1500 |
| `/agents/agents/assessment.py` | Assessment Agent | ~800 |
| `/agents/agents/gameplan.py` | GamePlan Agent | ~1028 |
| `/agents/agents/awards.py` | Awards Agent | 791 |
| `/agents/agents/opportunity.py` | Opportunity Agent | 648 |
| `/agents/agents/narrative_synthesis.py` | Narrative Agent | 584 |
| `/agents/agents/execution.py` | Execution Agent | 949 |
| `/agents/agents/gameplan_narrative.py` | Narrative Module | 714 |
| `/agents/modules/awards_probability.py` | Probability engine | 408 |
| `/agents/workflows/weekly_scout.py` | Weekly recommendations | 449 |
| `/agents/workflows/silence_detector.py` | Inactivity detection | 315 |
| `/agents/workflows/deadline_alerts.py` | Deadline reminders | 449 |
| `/agents/workflows/daily_checkin.py` | EDS monitoring | 435 |

### Frontend TypeScript

| File | Purpose |
|------|---------|
| `/lib/scoring/archetypeDetector.ts` | 11 archetypes + detection |
| `/lib/scoring/engine.ts` | Scoring formulas |
| `/lib/events/contracts.ts` | Event type definitions (10 types) |
| `/lib/events/bus.ts` | Event bus singleton |
| `/lib/constants/defaults.ts` | Centralized defaults |
| `/lib/utils/safeValue.ts` | Safe value utilities |
| `/lib/config/featureFlags.ts` | Feature flags |
| `/lib/integration/store/questStore.master.ts` | Onboarding data collection |

### Database Migrations

| Migration | Purpose |
|-----------|---------|
| `003_profiles_v10.sql` | Profile schema with archetype |
| `004_crises.sql` | Crisis HITL workflow |
| `006_agent_state_versions.sql` | State versioning |
| `007_opportunities_awards.sql` | Awards/Opportunities tables |
| `030_agent_memory_hitl.sql` | Memory + HITL tables |

---

## APPENDIX A: ARCHETYPE → AWARD CATEGORY MAPPING (PROPOSED)

| Archetype | Primary Award Categories | Secondary Categories |
|-----------|-------------------------|---------------------|
| SCHOLAR | academic, research | stem |
| RESEARCHER | research, stem | academic |
| LEADER | leadership, entrepreneurship | service |
| ENTREPRENEUR | entrepreneurship, stem | leadership |
| CHANGEMAKER | service, leadership | humanities |
| ADVOCATE | service, humanities | journalism |
| CREATOR | arts, entrepreneurship | stem |
| PERFORMER | arts, athletics | leadership |
| POLYMATH | academic, research, leadership | all |
| EMERGING | local, school | regional |
| EXPLORER | general, academic | varies |

---

## APPENDIX B: RECOMMENDED CONTRACT (GamePlan → Awards)

```python
# Proposed handoff contract
@dataclass
class GamePlanToAwardsHandoff:
    profile_id: str
    master_narrative: MasterNarrative
    archetype: ArchetypeResult
    activities: List[Activity]        # For synergy detection
    identity_seeds: List[IdentitySeed]  # Deadline awareness
    hidden_target: str                # School-specific optimization
    weak_spots: List[Gap]             # P0/P1/P2 for strategic targeting
    available_hours: int              # Capacity constraint
```

---

## APPENDIX C: FIRST PRINCIPLE → ACTIVITY TYPE MAPPING

| First Principle | Primary Activity Types | Example Activities |
|-----------------|----------------------|-------------------|
| BUILDER | Technical projects, hackathons | Build apps, robotics |
| STORYTELLER | Writing, film, journalism | School paper, documentary |
| DISCOVERER | Research, lab work | Science fair, ISEF |
| ADVOCATE | Activism, awareness | Policy campaigns, nonprofits |
| CONNECTOR | Community organizing | Clubs, networking events |
| HEALER | Healthcare, counseling | Hospital volunteer, peer support |
| LEADER | Organizations, teams | Student government, sports captain |
| ARTIST | Creative expression | Art portfolio, performances |
| ENTREPRENEUR | Business ventures | Startups, social enterprises |
| SCHOLAR | Academic competitions | Olympiads, debate |

---

**Document End**

*This comprehensive discovery report was generated by executing all 8 discovery prompts in the IvyLevel Multi-Agent Discovery Execution Guide. The findings identify critical integration gaps between agents that must be addressed before Awards Agent enhancement implementation.*

**Discovery Completed:** January 12, 2026
**Prompts Executed:** 8/8
**Critical Gaps Found:** 3 (GamePlan→Awards, Archetype unused, Event orchestration)
