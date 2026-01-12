# IvyQuest v10.0 Implementation Prompt
## Complete Context Restoration for Coding Agent

**Date:** January 2026
**Status:** Horizontal Complete → Vertical Depth Required
**Priority:** Replace stubs with real intelligence

---

## CONTEXT RESTORATION

### What is IvyQuest?

IvyQuest is a multi-agent AI coaching platform for college admissions that replicates the methodology of elite human coaches. The platform guides students through assessment, game plan generation, and execution tracking.

### Business Context

| Property | Value |
|----------|-------|
| **North Star Metric** | SSR (Student Success Rate) >85% |
| **Validation Case** | Huda: 5 national awards, $23K raised, 6,400 students impacted, 100% SSR |
| **Human Baseline** | Jenny's coaching: 122KB methodology data |
| **Target Users** | 10-20 beta students initially, scaling to 500+ |

### 6 Jobs-to-be-Done (Customer Problems We Solve)

| JTBD | Customer Pain | Jenny's Solution | Target Metric |
|------|---------------|------------------|---------------|
| 1. Build Distinctive Profile | Generic activities, no spike | 7 touchpoints/activity | 85% achieve 4+ touchpoints |
| 2. Win Prestigious Awards | 5% win rate, wrong competitions | 62.5% win rate | >40% win rate |
| 3. Execute to Completion | 80% project abandonment | 100% completion | >80% completion |
| 4. Craft Compelling Narrative | Generic essays, 60+ revisions | <10 revisions, coherent DNA | Coherence >80% |
| 5. Secure Opportunities | Hear about RSI too late | 6-month advance prep | 40% accept rate |
| 6. Navigate Crises | Rejections derail for weeks | <2hr recovery | <72hr recovery |

---

## CURRENT IMPLEMENTATION STATUS

### What's Working ✅

| Component | Status | Location |
|-----------|--------|----------|
| 6-Frame Assessment UI | ✅ Complete | `components/frames/Frame*.tsx` |
| 27-Layer Scoring Engine | ✅ Complete | `lib/scoring/` |
| Dashboard UI | ✅ Complete | `components/dashboard/` |
| Auth System | ✅ Complete | Supabase Auth + RLS |
| Data Persistence | ✅ Complete | `assessments`, `game_plans`, `student_items` |
| Profile Sync Triggers | ✅ Complete | Auto-extract awards, schools, goals |
| Database Schema | ✅ 85% Complete | All v10.0 tables exist |
| Event Bus | ✅ Complete | `lib/events/eventBus.ts` (14 event types) |
| CRI Computation | ✅ Complete | `agents/tools/cri.py` |
| Execution Agent | ✅ 90% Complete | Crisis Alchemy works via LangGraph |
| Voice Input | ✅ Complete | `components/ui/VoiceInput.tsx` |

### What's STUBBED (Returns Hardcoded Data) ❌

| Component | File | Current State | Fix Required |
|-----------|------|---------------|--------------|
| `synthesize_narrative_dna()` | `agents/agents/assessment.py:114` | Returns placeholder string | LLM synthesis |
| `filter_activities_by_roi()` | `agents/agents/gameplan.py:89` | Returns hardcoded list | Real filtering |
| `plant_identity_seeds()` | `agents/agents/gameplan.py:115` | Returns hardcoded list | Deadline scheduling |
| `calculate_win_probability()` | `agents/agents/awards.py` | Basic implementation | Historical model |
| `send_advance_alerts()` | `agents/agents/opportunity.py` | Not implemented | Alert system |
| `balance_portfolio()` | `agents/agents/awards.py` | Not implemented | Risk distribution |
| `create_backup_cascade()` | `agents/agents/opportunity.py` | Not implemented | Failover logic |

### What May Need Deployment Verification ⚠️

| Component | Issue | Check |
|-----------|-------|-------|
| Python Backend | May not be deployed | `curl $AGENT_API_URL/health` |
| API Connectivity | Next.js → Python | Test `/api/agents/assessment/enhance` |

---

## TECH STACK

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State:** Zustand + React Query
- **Auth:** Supabase Auth

### Backend
- **Database:** Supabase (PostgreSQL + RLS)
- **Agent Runtime:** Python/FastAPI with Agno
- **LLM:** OpenAI GPT-4o
- **Workflow:** LangGraph for Crisis Alchemy
- **Hosting:** Vercel (frontend), TBD (Python backend)

### Key Files Structure
```
/app
  /api/agents/          # Next.js API routes (proxy to Python)
    /assessment/
    /gameplan/
    /execution/
    /awards/
    /opportunities/

/agents                 # Python backend
  /agents/
    assessment.py       # ← NEEDS: synthesize_narrative_dna
    gameplan.py         # ← NEEDS: filter_activities_by_roi, plant_identity_seeds
    execution.py        # ✅ Working
    awards.py           # ← NEEDS: calculate_win_probability, balance_portfolio
    opportunity.py      # ← NEEDS: send_advance_alerts, create_backup_cascade
  /graphs/
    crisis_alchemy.py   # ✅ Working (LangGraph)
  /tools/
    cri.py              # ✅ Working
    database.py         # ✅ Working

/lib
  /events/
    eventBus.ts         # ✅ Working
    contracts.ts        # ✅ Working
  /scoring/             # ✅ Working
  /store/               # ✅ Working

/components
  /frames/              # ✅ Working (6 assessment frames)
  /dashboard/           # ✅ Working
  /ui/
    VoiceInput.tsx      # ✅ Working

/supabase/migrations/   # ✅ All tables exist
```

---

## 10 ATOMIC COACHING PRIMITIVES

These are the core methodologies extracted from Jenny's coaching that agents must implement:

### ACP-001: Hidden Probability Matrix ✅ IMPLEMENTED
```
probability = base_rate × profile_strength × demographic_factor × major_competitiveness
- Precomputed from Chetty baselines (NOT runtime API)
- NEVER shown to user
- Location: agents/tools/cri.py, agents/agents/assessment.py:168
```

### ACP-002: Identity Synthesis Framework ❌ STUB
```
- "12-second moment" where scattered interests crystallize
- Output: Single narrative DNA sentence + confidence + rationale
- Current: Returns placeholder in assessment.py:114
- FIX: Implement LLM synthesis with structured output
```

### ACP-003: Crisis Alchemy Protocol ✅ IMPLEMENTED
```
4-step sequence via LangGraph:
1. Validate (2s) - Acknowledge emotion
2. Act (10s) - One micro-action
3. Reframe (30s) - Find opportunity
4. Create (2min) - Design new activity
- Location: agents/graphs/crisis_alchemy.py
```

### ACP-004: Strategic Overwhelm ✅ IMPLEMENTED
```
Assign 10 tasks → complete 7 > assign 7 → complete 5
- 1.4x capacity assignment
- Target 73% completion
- Location: agents/agents/execution.py:283, agents/config.py
```

### ACP-005: Multi-Touchpoint Leverage ❌ STUB
```
Every activity MUST serve ≥4 application touchpoints or filtered out
ROI = (touchpoints × prestige) / hours
Touchpoints: club, workshop, research, award, essay, internship, rec_letter
- Current: Returns hardcoded list in gameplan.py:89
- FIX: Implement touchpoint counting + filtering
```

### ACP-006: Identity Seed Architecture ❌ STUB
```
Plant identity seeds 6-12 months before bloom
Backward-schedule from target deadlines
- Current: Returns hardcoded list in gameplan.py:115
- FIX: Implement deadline-based scheduling
```

### ACP-007: Talk-First-Write-Second ✅ IMPLEMENTED
```
5min verbal → transcribe → edit vs 3hr forced writing
- Location: components/ui/VoiceInput.tsx (451 lines)
- TODO: Wire to essay drafting workflow
```

### ACP-008: Micro-Edit Mastery ❌ NOT IMPLEMENTED
```
Language pattern replacements:
- "avoid" → "prioritize"
- "can't afford" → "family investment priorities"
- FIX: Create pattern library + replacement function
```

### ACP-009: Dual-Layer Messaging ❌ PARTIAL
```
All outputs need:
- agent_output.student (empathetic)
- agent_output.parent (quantitative)
- Current: Types exist, implementation missing
```

### ACP-010: Constraint Forge ❌ PARTIAL
```
Multi-agent debate to reframe barriers
Maps to SFFA rubric (barriers 4/5 > talent 3/5)
- Current: Only reframe step in Crisis Alchemy
```

---

## DATABASE SCHEMA (All Tables Exist)

### Core Tables
```sql
-- profiles: Extended user data
profiles (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES auth.users,
  email, first_name, last_name, grade, high_school,
  archetype_id UUID REFERENCES archetypes,
  archetype_confidence FLOAT,
  cri FLOAT,
  narrative_dna TEXT,
  execution_debt FLOAT,
  hidden_target TEXT,
  hidden_probabilities JSONB,
  identity_seeds JSONB
)

-- assessments: Full assessment snapshots
assessments (
  id UUID PRIMARY KEY,
  user_id UUID,
  profile_data JSONB,  -- Complete 58-attribute profile
  scores JSONB,        -- ivy_ready_score, dimension scores
  archetype TEXT,
  completeness_score INTEGER
)

-- game_plans: Strategic plans
game_plans (
  id UUID PRIMARY KEY,
  user_id UUID,
  plan_data JSONB,     -- phases, boosters, quick_wins
  current_phase TEXT,
  current_week INTEGER,
  completion_percentage INTEGER
)

-- student_items: Universal ledger (awards, ECs, goals, applications)
student_items (
  id UUID PRIMARY KEY,
  user_id UUID,
  item_type TEXT,      -- award, extracurricular, application, goal
  tier1_state TEXT,    -- planned, in_progress, submitted, outcome
  title, description,
  recognition_level, prestige_tier, selectivity,
  school_id, admission_probability, target_tier
)

-- crises: Crisis tracking for Execution Agent
crises (
  id UUID PRIMARY KEY,
  profile_id UUID,
  type TEXT,           -- blocker, rejection, conflict
  urgency INTEGER,
  status TEXT,         -- detected, proposed, approved, resolved
  proposed_response JSONB,
  reframed_opportunity TEXT
)

-- awards: 200+ awards database
awards (
  id UUID PRIMARY KEY,
  name, category, level, organization,
  historical_win_rate FLOAT,
  prestige_score INTEGER,
  effort_hours INTEGER,
  eligibility JSONB
)

-- opportunities: 500+ opportunities database
opportunities (
  id UUID PRIMARY KEY,
  name, type, organization,
  deadline DATE,
  prestige_score INTEGER,
  eligibility JSONB,
  fit_criteria JSONB
)

-- chetty_baselines: Precomputed mobility data
chetty_baselines (
  id UUID PRIMARY KEY,
  zip TEXT,
  school_id TEXT,
  expected_performance FLOAT,
  multiplier FLOAT
)

-- agent_state_versions: State versioning for rollback
agent_state_versions (
  id UUID PRIMARY KEY,
  profile_id UUID,
  agent TEXT,
  state JSONB,
  version INTEGER,
  created_by TEXT  -- 'agent' or 'human'
)
```

### Key Views
```sql
v_agent_student_profile    -- Complete student profile for agents
v_student_awards_detailed  -- Awards with prestige tiers
v_student_target_schools   -- Schools with probabilities
v_student_goals            -- Goals from game plan
```

---

## EVENT BUS CONTRACT

```typescript
// lib/events/contracts.ts
type IvyEvent =
  | { type: 'ASSESSMENT_COMPLETED'; payload: { profileId, narrativeDna, cri } }
  | { type: 'GAMEPLAN_GENERATED'; payload: { profileId, activities, seeds } }
  | { type: 'PROJECT_STALLED'; payload: { profileId, days, debt } }
  | { type: 'CRISIS_DETECTED'; payload: { profileId, severity, rationale } }
  | { type: 'CRISIS_RESOLVED'; payload: { profileId, outcome } }
  | { type: 'HUMAN_OVERRIDE'; payload: { agent, override, rationale } }
  | { type: 'SUCCESS_ACHIEVED'; payload: { profileId, impact, vectorData } }
  | { type: 'AWARD_MATCHED'; payload: { profileId, awardId, probability } }
  | { type: 'OPPORTUNITY_ALERT'; payload: { profileId, opportunityId, deadline } }
  | { type: 'BLOCKER_DETECTED'; payload: { profileId, projectId, days } }
  | { type: 'IDENTITY_SEED_PLANTED'; payload: { profileId, seed, bloomDate } }
  | { type: 'NARRATIVE_DNA_SYNTHESIZED'; payload: { profileId, dna, confidence } }
```

---

## YOUR TASK

You are implementing the **vertical depth** - replacing stubs with real intelligence.

### Implementation Order (By Priority)

#### Phase 1: Verify Connectivity (Day 1)
1. Check if Python backend is deployed and reachable
2. Test all API endpoints end-to-end
3. Fix any connectivity issues

#### Phase 2: Narrative DNA (Days 2-3) - HIGHEST PRIORITY
File: `agents/agents/assessment.py`
- Replace stub `synthesize_narrative_dna()` with LLM implementation
- Must produce: `{dna: string, themes: string[], confidence: number, rationale: string}`
- Must use profile data: spike_category, activities, constraints, strengths, brag_text

#### Phase 3: Activity Filtering (Days 4-5)
File: `agents/agents/gameplan.py`
- Replace stub `filter_activities_by_roi()` with real implementation
- Must count touchpoints (7 types)
- Must filter activities with <4 touchpoints
- Must calculate ROI = (touchpoints × prestige) / hours

#### Phase 4: Identity Seeds (Days 6-7)
File: `agents/agents/gameplan.py`
- Replace stub `plant_identity_seeds()` with deadline-based scheduling
- Must backward-schedule 6-8 months from target deadlines
- Must generate seed actions using LLM

#### Phase 5: Awards Intelligence (Days 8-10)
File: `agents/agents/awards.py`
- Implement `calculate_win_probability()` with historical model
- Implement `balance_portfolio()` with risk distribution (likely/target/stretch)

#### Phase 6: Opportunity Alerts (Days 11-12)
File: `agents/agents/opportunity.py`
- Implement `send_advance_alerts()` for 6-month window
- Implement `create_backup_cascade()` with 3+ alternatives

---

## CODE PATTERNS TO FOLLOW

### State Versioning (Required for all agent state changes)
```python
async def _version_state(self, profile_id: str, event: str, state: Dict, created_by: str = 'agent'):
    version = await self.db.rpc('get_next_version', {
        'p_profile_id': profile_id,
        'p_agent': self.name
    }).execute()
    
    await self.db.table('agent_state_versions').insert({
        'profile_id': profile_id,
        'agent': self.name,
        'state': state,
        'version': version.data,
        'event_type': event,
        'created_by': created_by
    }).execute()
```

### Event Publishing (Required after significant actions)
```python
async def _publish_event(self, event_type: str, payload: Dict):
    # Via Supabase Realtime or internal event bus
    await self.db.table('events').insert({
        'type': event_type,
        'payload': payload,
        'created_at': datetime.now().isoformat()
    }).execute()
```

### LLM Calls (Use structured output)
```python
async def _llm_call(self, prompt: str, response_format: Dict) -> Dict:
    response = await self.llm.ainvoke(
        prompt,
        response_format={"type": "json_object"}
    )
    return json.loads(response.content)
```

---

## VALIDATION CRITERIA

Every implementation must pass:

### 1. Huda Benchmark
- Profile: Grade 10, CS major, "competitive" + "hands-on" strengths
- Target Schools: Stanford, MIT, Columbia, Yale
- Awards: AP Scholar, USABO Qualifier, International EC recognition
- Expected: Narrative DNA coherence >80%, Activity ROI filtering works

### 2. Unit Tests
```python
def test_narrative_dna_not_placeholder():
    result = await assessment_agent.synthesize_narrative_dna(huda_profile)
    assert result['dna'] != "Student narrative DNA placeholder"
    assert result['confidence'] > 0.5
    assert len(result['themes']) >= 2

def test_activity_filtering():
    result = await gameplan_agent.filter_activities_by_roi(huda_profile)
    for activity in result:
        assert activity['touchpoint_count'] >= 4
        assert activity['roi'] > 0

def test_identity_seeds_scheduled():
    deadlines = [{'name': 'Early Action', 'date': '2025-11-01'}]
    result = await gameplan_agent.plant_identity_seeds(huda_profile, deadlines)
    for seed in result:
        assert seed['plant_date'] < seed['bloom_date']
```

### 3. Integration Test
```bash
# Full flow test
curl -X POST /api/agents/assessment/enhance \
  -d '{"profile_id": "test-huda-id"}' \
  | jq '.narrative_dna.dna' # Should NOT be "placeholder"
```

---

## START IMPLEMENTATION

Begin with Phase 1 (connectivity verification), then proceed to Phase 2 (Narrative DNA).

After each implementation:
1. Run unit tests
2. Test against Huda profile
3. Version state changes
4. Publish relevant events
5. Commit with descriptive message

Report progress after each phase:
- Files modified
- Tests passing
- Any blockers or deviations

End with "Implementation Complete: [Component] Ready" after each phase.
