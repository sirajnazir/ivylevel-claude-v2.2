# Awards Agent Pre-Integration Discovery Report
## Comprehensive Analysis for Enhancement Integration

**Version:** 1.0
**Date:** January 12, 2026
**Status:** Discovery Complete
**Purpose:** Analyze current Awards Agent implementation before integrating new specifications

---

## EXECUTIVE SUMMARY

### Key Findings

The **Awards Agent** is a **production-ready, well-architected component** within the IvyQuest multi-agent system. It features:

1. **Mature Architecture**: Built on the Agno agent framework with LangChain integration
2. **Comprehensive Matching**: Multi-factor probability calculation with ROI optimization
3. **Portfolio Strategy**: Implements 2-2-1 balanced portfolio (Likely/Target/Stretch)
4. **Database Support**: Full PostgreSQL schema with 200+ awards in seed data
5. **Frontend Integration**: React Query hooks with detail modal views
6. **Test Coverage**: Unit tests and E2E tests for probability and portfolio logic

### Integration Readiness: **HIGH**

The current implementation provides solid foundations for enhancement:
- **Schema Extensibility**: JSONB fields allow additional attributes without migrations
- **Modular Design**: Separate probability engine module enables algorithm enhancement
- **Clean Interfaces**: Well-defined API contracts for inter-agent communication
- **Evaluation Framework**: Rubric-based evaluation ready for benchmarking

### Key Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Probability formula changes may affect existing portfolios | Medium | Version outputs, A/B test |
| New schema fields require migration | Low | Use existing JSONB flexibility |
| Win cascade logic adds complexity | Medium | Implement as separate module |
| Archetype-based scoring needs Assessment data | Low | Dependency already exists |

---

## SECTION 1: CODEBASE DISCOVERY

### 1.1 Repository Structure

```
/agents/
├── agents/
│   ├── awards.py              # Main AwardsAgent class (791 lines)
│   └── __init__.py            # Exports AwardsAgent, awards_agent
├── modules/
│   └── awards_probability.py  # AwardsProbabilityEngine (408 lines)
├── seeds/
│   └── awards_data.py         # 200+ awards database
├── evaluation/
│   └── rubrics/
│       └── awards.py          # 5-dimension evaluation rubric
└── tests/
    ├── test_v2_modules.py     # Unit tests for probability engine
    └── test_mile_deep_e2e.py  # E2E tests for awards agent

/supabase/migrations/
├── 007_opportunities_awards.sql  # Core awards schema
└── 025_awards_probability.sql    # Probability tracking fields

/components/agents/
├── AgentDetailModal.tsx          # AwardsDetail component (lines 396-540)
└── AwardsAgentCard.tsx           # Dashboard card component

/lib/api/
└── agentV13Client.ts             # API client with awards endpoints
```

### 1.2 Entry Points

| Entry Point | Type | Location |
|-------------|------|----------|
| `AwardsAgent.match()` | Main method | `agents/awards.py:35` |
| `AwardsAgent.process()` | Standard entry | `agents/awards.py:31` |
| `GET /agents/awards/match/{profile_id}` | REST API | `agents/main.py:502` |
| `GET /agents/awards/portfolio/{profile_id}` | REST API | `agents/main.py:521` |
| `POST /agents/awards/portfolio` | REST API | `agents/main.py:771` |
| `awards_agent` singleton | Python export | `agents/agents/__init__.py` |

### 1.3 Dependencies

**Python Dependencies:**
```python
# Core
langchain_openai     # ChatOpenAI for LLM calls
datetime             # Timeline calculations
json                 # Data serialization

# Internal
tools.database       # get_supabase_client, get_profile_with_assessment
modules.awards_probability  # AwardsProbabilityEngine
```

**External Services:**
- OpenAI GPT-4o (temperature=0.3)
- Supabase PostgreSQL
- (No Redis usage currently)

**Frontend Dependencies:**
- `@tanstack/react-query` - Data fetching
- `lucide-react` - Icons
- `@/lib/constants/brand` - Brand colors

---

## SECTION 2: AGENT ARCHITECTURE

### 2.1 Agent Framework

| Aspect | Details |
|--------|---------|
| **Framework** | Agno + LangChain |
| **Agent Type** | Autonomous (FULL autonomy level) |
| **Execution Model** | Single-shot matching (no iterative reasoning) |
| **Memory** | None (stateless per request) |
| **Tools** | Database access only |

### 2.2 Agent Definition

```python
class AwardsAgent:
    """
    Awards Agent: Matches students to awards with ROI optimization

    Primitives Used:
    - ACP-001: Hidden Probability Matrix (win probability calculation)

    Autonomy: FULL (deterministic matching)
    Huda Benchmark: >40% win rate (Huda actual: 62.5% = 5/8)
    """

    def __init__(self):
        self.name = "Awards"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.db = get_supabase_client()
```

**LLM Configuration:**
- Model: `gpt-4o`
- Temperature: `0.3` (low for consistency)
- Note: LLM currently NOT used for matching (deterministic calculations only)

### 2.3 Multi-Agent Interaction

```
Assessment Agent ────────────────────────────┐
     │                                        │
     │ profile_data, narrative_dna,          │
     │ cri_score, archetype                  │
     ▼                                        │
┌─────────────────────────────────────────────┘
│
│  ┌──────────────────┐
└─▶│   Awards Agent   │
   │                  │
   │  Input:          │
   │  - profile_id    │
   │  - profile_data  │
   │    (from DB)     │
   │                  │
   │  Output:         │
   │  - portfolio     │
   │  - timeline      │
   │  - top_recs      │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  Game Plan Agent │  (receives portfolio for integration)
   └──────────────────┘
```

**Data Flow:**
1. Awards Agent fetches profile via `get_profile_with_assessment(profile_id)`
2. Retrieves all active awards from `awards` table
3. Filters by eligibility
4. Calculates probability for each
5. Builds balanced portfolio
6. Stores state version and publishes event
7. Returns portfolio to caller

### 2.4 Agent Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AWARDS AGENT FLOW                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Input: profile_id                                                      │
│       │                                                                  │
│       ▼                                                                  │
│   ┌───────────────────────┐                                             │
│   │  Get Profile + Assess │  ──▶ get_profile_with_assessment()          │
│   └───────────┬───────────┘                                             │
│               │                                                          │
│               ▼ (profile not found?)                                     │
│   ┌───────────────────────┐                                             │
│   │  Return Placeholder   │  ──▶ {success: true, placeholder: true}     │
│   └───────────────────────┘                                             │
│               │                                                          │
│               ▼                                                          │
│   ┌───────────────────────┐                                             │
│   │    Get All Awards     │  ──▶ db.table("awards").select("*")         │
│   └───────────┬───────────┘                                             │
│               │                                                          │
│               ▼                                                          │
│   ┌───────────────────────┐                                             │
│   │ Filter by Eligibility │  ──▶ _filter_by_eligibility()               │
│   │   - Grade             │                                              │
│   │   - GPA minimum       │                                              │
│   └───────────┬───────────┘                                             │
│               │                                                          │
│               ▼                                                          │
│   ┌───────────────────────┐                                             │
│   │  For Each Award:      │                                              │
│   │  Calculate Probability│  ──▶ calculate_win_probability()            │
│   │    - base_rate        │      Multi-factor formula                    │
│   │    - strength_factor  │                                              │
│   │    - spike_alignment  │                                              │
│   │    - leadership       │                                              │
│   │    - demographic      │                                              │
│   │    - cri_boost        │                                              │
│   │                       │                                              │
│   │  Calculate ROI:       │                                              │
│   │  (prob × prestige)    │                                              │
│   │       / effort        │                                              │
│   └───────────┬───────────┘                                             │
│               │                                                          │
│               ▼                                                          │
│   ┌───────────────────────┐                                             │
│   │   Sort by ROI         │                                              │
│   └───────────┬───────────┘                                             │
│               │                                                          │
│               ▼                                                          │
│   ┌───────────────────────┐                                             │
│   │  Balance Portfolio    │  ──▶ balance_portfolio()                    │
│   │   - Likely (>50%): 3  │                                              │
│   │   - Target (25-50%):4 │                                              │
│   │   - Stretch (<25%): 2 │                                              │
│   │                       │                                              │
│   │  Sequence Applications│  ──▶ _sequence_applications()               │
│   │   - Urgent first      │                                              │
│   │   - Likely for conf.  │                                              │
│   └───────────┬───────────┘                                             │
│               │                                                          │
│               ▼                                                          │
│   ┌───────────────────────┐                                             │
│   │  Version State        │  ──▶ agent_state_versions table             │
│   │  Publish Event        │  ──▶ AWARD_MATCHED event                    │
│   └───────────┬───────────┘                                             │
│               │                                                          │
│               ▼                                                          │
│   Output: {                                                              │
│     success: true,                                                       │
│     total_matches: N,                                                    │
│     portfolio: {...},                                                    │
│     top_recommendations: [...],                                          │
│     timeline: [...]                                                      │
│   }                                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SECTION 3: DATA LAYER

### 3.1 Database Schema

**Primary Table: `awards`**

```sql
CREATE TABLE awards (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  organization TEXT,
  description TEXT,
  website_url TEXT,

  -- Classification
  category award_category,  -- ENUM: stem, humanities, arts, leadership,
                            --       service, academic, entrepreneurship,
                            --       athletics, journalism, debate, research
  level award_level,        -- ENUM: school, local, regional, state,
                            --       national, international

  -- Timing
  deadline DATE,
  deadline_recurring TEXT,  -- e.g., 'January 15 annually'
  notification_date DATE,
  award_month INTEGER,

  -- Metrics for ROI
  prestige_score INTEGER CHECK (1-10),
  historical_win_rate FLOAT CHECK (0-1),
  effort_hours INTEGER,
  total_applicants INTEGER,
  total_winners INTEGER,

  -- Flexible criteria (JSONB)
  eligibility JSONB,        -- {grades, gpa_minimum, citizenship, demographics, interests}
  requirements JSONB,       -- ['essay', 'recommendation', 'portfolio', ...]

  -- Prize details
  prize_amount DECIMAL,
  prize_type TEXT,          -- cash, scholarship, recognition, internship
  recognition_details TEXT,

  -- Multi-touchpoint
  touchpoints INTEGER CHECK (1-7),
  touchpoint_types JSONB,

  -- Status
  is_active BOOLEAN DEFAULT true,
  last_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

**Supporting Table: `student_applications`**

```sql
CREATE TABLE student_applications (
  id UUID PRIMARY KEY,
  profile_id UUID REFERENCES profiles(id),
  award_id UUID REFERENCES awards(id),

  status application_status,  -- ENUM: interested, planning, in_progress,
                              --       submitted, waitlisted, accepted,
                              --       rejected, withdrawn
  status_history JSONB,

  -- Agent predictions (Hidden Probability Matrix - ACP-001)
  predicted_probability FLOAT,
  probability_factors JSONB,
  agent_recommendation TEXT,   -- 'apply', 'skip', 'backup'
  recommendation_rationale TEXT,

  -- Additional v13.1 fields
  calculated_probability DECIMAL(5,2),
  fit_score DECIMAL(5,2),
  competition_factor DECIMAL(5,2),
  submission_quality_score DECIMAL(5,2),
  vulnerability_bonus BOOLEAN,
  identity_alignment_bonus BOOLEAN,
  portfolio_tier VARCHAR(20)  -- 'likely', 'target', 'stretch'
);
```

### 3.2 Data Models (Python)

**AwardProbability (from modules/awards_probability.py)**

```python
@dataclass
class AwardProbability:
    award_id: str
    award_name: str
    probability: float         # 0-100
    tier: str                  # 'likely', 'target', 'stretch'
    fit_score: float
    competition_factor: float
    submission_quality_score: float
    vulnerability_bonus: bool
    identity_bonus: bool
    reasoning: str

@dataclass
class Portfolio:
    likely: List[AwardProbability]
    target: List[AwardProbability]
    stretch: List[AwardProbability]
    balance_score: float
    total_expected_wins: float
    recommendations: List[str]
```

### 3.3 Data Sources

| Source | Description | Record Count |
|--------|-------------|--------------|
| `awards` table | Primary awards database | 200+ seeded |
| `seeds/awards_data.py` | Python seed data | 200+ awards |
| Sample awards fallback | In-code fallback | 5 awards |

**Award Categories Coverage:**
- STEM: 30+ awards
- Humanities: 20+ awards
- Arts: 15+ awards
- Leadership: 10+ awards
- Service: 5+ awards
- Academic: 10+ awards
- Debate: 5+ awards
- Entrepreneurship: 10+ awards
- Journalism: 5+ awards
- Identity-Specific: 15+ awards
- Local/Regional: 15+ awards

### 3.4 Vector Store

**Currently: NOT IN USE for Awards Agent**

The `success_vectors` table exists for RLHF but is not integrated:

```sql
CREATE TABLE success_vectors (
  id UUID PRIMARY KEY,
  profile_id UUID,
  application_id UUID REFERENCES student_applications(id),
  vector vector(1536),  -- OpenAI embeddings
  metadata JSONB,
  event_type TEXT,      -- Only 'SUCCESS_ACHIEVED' events
  created_at TIMESTAMPTZ
);
```

---

## SECTION 4: CURRENT FUNCTIONALITY

### 4.1 Core Features

| Feature | Description | Code Location | Input | Output |
|---------|-------------|---------------|-------|--------|
| **Award Matching** | Match profile to eligible awards | `awards.py:35` | profile_id | portfolio, timeline, top_recs |
| **Win Probability** | Multi-factor probability calculation | `awards.py:120` | profile, award | float (0-0.85) |
| **Portfolio Balancing** | 2-2-1 or 3-4-2 optimal distribution | `awards.py:286` | matched awards | balanced portfolio |
| **Application Sequencing** | Optimal application order | `awards.py:322` | portfolio | sequenced list |
| **Rejection Alchemy** | Transform rejection into improvements | `awards.py:395` | profile_id, award_id, feedback | gap analysis, alternatives |
| **Timeline Generation** | Deadline-sorted timeline | `awards.py:642` | awards | timeline with urgency |

### 4.2 Matching Logic (Probability Formula)

**Main Formula:**
```python
probability = (
    base_rate ×           # Historical win rate (0.01-0.30)
    strength_factor ×     # Academic/achievement strength (0.5-1.5)
    spike_alignment ×     # How spike matches category (0.5-1.5)
    leadership_factor ×   # Leadership level (0.8-1.4)
    demographic_factor ×  # Diversity boost if applicable (0.9-1.3)
    cri_factor            # CRI multiplier (1.0 + (cri-1)*0.2)
)

# Cap: min(0.85, max(0.01, probability))
```

**Factor Calculations:**

1. **Strength Factor (0.5-1.5):**
   - Base: 0.8
   - GPA ≥4.5: +0.3, ≥4.0: +0.2, ≥3.7: +0.1
   - SAT ≥1550: +0.2, ≥1500: +0.15, ≥1450: +0.1
   - AP ≥10: +0.2, ≥7: +0.1, ≥5: +0.05

2. **Spike Alignment (0.5-1.5):**
   - Perfect match: 1.4
   - Related category: 1.2
   - General award: 1.0
   - Weak alignment: 0.7

3. **Leadership Factor (0.8-1.4):**
   - FOUNDER_NATIONAL: 1.4
   - FOUNDER_STATE: 1.3
   - NATIONAL_PRES: 1.25
   - STATE_PRES: 1.2
   - SCHOOL_PRES: 1.15
   - OFFICER: 1.1
   - MEMBER: 1.0

4. **Demographic Factor (0.9-1.3):**
   - First-gen: +0.1
   - Underrepresented: +0.15
   - Female in STEM: +0.1

**Alternative Formula (AwardsProbabilityEngine):**
```python
probability = (
    fit_score × 0.4 +           # 0-100 scale
    (100 - selectivity) × 0.3 + # Competition factor
    quality_score × 0.3         # Submission quality estimate
)

# Bonuses:
if vulnerability_bonus: +15
if identity_bonus: +10

# Cap at 95%
```

### 4.3 Recommendation Output

**Portfolio Structure:**
```json
{
  "success": true,
  "total_matches": 45,
  "portfolio": {
    "likely": [
      {
        "award_id": "uuid",
        "name": "NCWIT Aspirations",
        "category": "STEM",
        "level": "national",
        "win_probability": 0.62,
        "effort_hours": 15,
        "prestige_score": 8,
        "roi": 3.31,
        "deadline": "2024-11-01",
        "recommendation": "likely"
      }
    ],
    "target": [...],
    "stretch": [...],
    "summary": {
      "total_awards": 9,
      "expected_wins": 3.2,
      "total_effort_hours": 180,
      "risk_distribution": {
        "likely_count": 3,
        "target_count": 4,
        "stretch_count": 2
      }
    },
    "application_sequence": [
      {
        "sequence": 1,
        "award_id": "...",
        "name": "...",
        "win_probability": 0.62,
        "effort_hours": 15,
        "rationale": "Start with high-probability win to build momentum"
      }
    ]
  },
  "top_recommendations": [...],  // Top 10 by ROI
  "timeline": [...]              // Sorted by deadline
}
```

### 4.4 Student Profile Handling

**Expected Profile Fields:**

```python
profile = {
  "id": "uuid",
  "grade": 11,
  "profile_data": {
    "identity": {"grade": 11, ...},
    "aptitude": {
      "gpa_weighted": 4.2,
      "sat_total": 1520,
      "ap_courses": 8
    },
    "passion": {
      "spike_category": "STEM",
      "leadership_level": "OFFICER"
    },
    "demographics": {
      "first_gen": True,
      "ethnicity": "HISPANIC",
      "gender": "FEMALE",
      "underrepresented": True
    },
    "operating": {"firstGeneration": True}
  },
  "cri": 1.15,
  "narrative_dna": "..."
}
```

**Profile Retrieval:**
```python
profile = await get_profile_with_assessment(profile_id)
```

---

## SECTION 5: INTEGRATION POINTS

### 5.1 Assessment Agent Integration

**Data Received:**
- `profile_data` (identity, aptitude, passion, operating, demographics)
- `cri` score
- `narrative_dna`
- `archetype` (if available)

**Integration Method:**
- Database: `get_profile_with_assessment()` function
- Location: `tools/database.py`

### 5.2 Game Plan Agent Integration

**Data Sent:**
- Portfolio with Likely/Target/Stretch awards
- Timeline with deadlines
- Expected wins estimate

**Event Published:**
```python
await self._publish_event("AWARD_MATCHED", {
    "profileId": profile_id,
    "awardId": matched_awards[0]["award_id"],
    "probability": matched_awards[0]["win_probability"]
})
```

### 5.3 Orchestrator Integration

**API Endpoints:**

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/agents/awards/match/{profile_id}` | GET | profile_id | Full match result |
| `/agents/awards/portfolio/{profile_id}` | GET | profile_id | Portfolio only |
| `/agents/awards/portfolio` | POST | {profile_id, student?, awards?} | Built portfolio |

### 5.4 External Services

| Service | Usage | Configuration |
|---------|-------|---------------|
| OpenAI GPT-4o | Initialized but NOT actively used | model="gpt-4o", temp=0.3 |
| Supabase | Database operations | get_supabase_client() |

---

## SECTION 6: CONFIGURATION & ENVIRONMENT

### 6.1 Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI authentication | Required |
| `SUPABASE_URL` | Database connection | Required |
| `SUPABASE_SERVICE_KEY` | Database auth | Required |

### 6.2 Configuration Constants

**From `agents/config.py`:**
```python
# Autonomy levels
FULL = "full"        # Awards Agent uses FULL

# Huda benchmarks
AWARD_WIN_RATE = 0.40       # Target: >40%
HUDA_AWARD_WIN_RATE = 0.625 # Actual: 62.5%
```

**From `modules/awards_probability.py`:**
```python
LIKELY_THRESHOLD = 60
TARGET_THRESHOLD = 40
FIT_WEIGHT = 0.4
COMPETITION_WEIGHT = 0.3
QUALITY_WEIGHT = 0.3
VULNERABILITY_BONUS = 15
IDENTITY_BONUS = 10
MAX_PROBABILITY = 95
```

**From `agents/awards.py`:**
```python
# Portfolio structure
likely: [:3]   # Top 3 likely wins
target: [:4]   # Top 4 targets
stretch: [:2]  # Top 2 stretch
```

---

## SECTION 7: ERROR HANDLING & LOGGING

### 7.1 Error Handling

**Pattern:**
```python
async def match(self, profile_id: str) -> Dict[str, Any]:
    try:
        # Main logic
        return {"success": True, ...}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Graceful Degradation:**
- Missing profile: Returns placeholder with `placeholder: true`
- Database failure: Falls back to sample awards (`_get_sample_awards()`)
- State versioning failure: Warning printed, continues
- Event publishing failure: Warning printed, continues

### 7.2 Logging

**Framework:** structlog

```python
import structlog
logger = structlog.get_logger()

logger.error("awards_error", error=str(e), profile_id=profile_id)
logger.error("awards_portfolio_error", error=str(e), profile_id=profile_id)
```

---

## SECTION 8: TESTING

### 8.1 Test Coverage

| Test File | Test Type | Coverage |
|-----------|-----------|----------|
| `test_v2_modules.py` | Unit | AwardsProbabilityEngine |
| `test_mile_deep_e2e.py` | E2E | Full awards agent |
| `test_agents.py` | Integration | Cross-agent |

### 8.2 Test Cases

**Unit Tests (test_v2_modules.py):**
- `test_probability_calculation` - Single award probability
- `test_vulnerability_bonus` - +15% bonus verification
- `test_identity_bonus` - +10% bonus verification
- `test_tier_classification` - Likely/Target/Stretch thresholds
- `test_portfolio_building` - 2-2-1 structure
- `test_portfolio_recommendations` - Recommendation generation
- `test_format_summary` - Output formatting
- `test_awards_portfolio_with_ncwit` - NCWIT strategy integration

**E2E Tests (test_mile_deep_e2e.py):**
- Win probability multi-factor model
- Portfolio balancing
- Boost verification (vulnerability, identity)
- Sample award testing (NCWIT, Congressional App, Coca-Cola, Regeneron)

### 8.3 Test Data

**Sample Student:**
```python
sample_student = {
    "spike": "computer science",
    "identity": ["woman", "first-generation"],
    "brand_statement": "Making tech accessible",
    "activities": [],
    "has_overcome_barrier": True,
    "is_underrepresented": True,
}
```

**Sample Awards:**
```python
sample_awards = [
    {"id": "ncwit", "name": "NCWIT Aspirations", "focus_area": "women in computing", "selectivity_percentile": 75},
    {"id": "google", "name": "Google CSSI", "focus_area": "computer science", "selectivity_percentile": 85},
    {"id": "coke", "name": "Coca-Cola Scholars", "focus_area": "leadership", "selectivity_percentile": 98}
]
```

---

## SECTION 9: KNOWN ISSUES & TECHNICAL DEBT

### 9.1 Known Issues

| Issue | Severity | Workaround |
|-------|----------|------------|
| LLM initialized but not used | Low | Remove or integrate for reasoning |
| Two probability formulas exist | Medium | Consolidate into one |
| Sample awards fallback is limited | Low | Ensure DB seeded |

### 9.2 Technical Debt

1. **Dual Probability Engines**: `AwardsAgent` has its own formula; `AwardsProbabilityEngine` has another
2. **No Caching**: Awards fetched from DB on every request
3. **Limited Error Types**: Generic exception handling
4. **Hardcoded Portfolio Sizes**: 3-4-2 structure hardcoded

### 9.3 TODOs in Code

```python
# agents/awards.py - Line 690 (implied)
# TODO: Integrate rejection history into probability adjustments

# agents/main.py - Line 1454
# Would call AwardsAgent - placeholder for now
```

---

## SECTION 10: ENHANCEMENT READINESS ASSESSMENT

### 10.1 Schema Compatibility

| New Specification | Current Support | Migration Needed |
|-------------------|-----------------|------------------|
| Jenny coaching intelligence | JSONB eligibility field | No |
| Archetype-based scoring | Archetype from Assessment | No - already received |
| Win cascade sequencing | New field needed | Add to portfolio output |
| 125 frameworks | Database records | Seed data update |
| Summer Programs | Separate table exists | Already `opportunities` table |

**JSONB Flexibility:**
The current `eligibility` and `requirements` JSONB fields can accommodate:
- Additional matching criteria
- Jenny's framework tags
- Archetype associations
- Win cascade metadata

### 10.2 Architecture Compatibility

| Enhancement | Compatibility | Approach |
|-------------|---------------|----------|
| Jenny coaching integration | HIGH | Add to probability factors |
| Archetype-based scoring | HIGH | Already receives archetype |
| Win cascade sequencing | MEDIUM | New module, integrate in `_sequence_applications()` |
| Enhanced matching algorithm | HIGH | Extend `calculate_win_probability()` |

### 10.3 Integration Points Compatibility

**Input Contracts:**
- Profile structure: ✅ Compatible
- Assessment data: ✅ Already integrated
- Archetype: ✅ Available via assessment

**Output Contracts:**
- Portfolio structure: ✅ Can extend
- Timeline: ✅ Can add cascade info
- Recommendations: ✅ Can enhance reasoning

**Downstream Impact:**
- Game Plan Agent: May need to handle new cascade logic
- Frontend: AwardsDetail component may need updates for new fields

### 10.4 Recommended Integration Approach

**Phase 1: Data Enhancement (Low Risk)**
1. Update `seeds/awards_data.py` with Jenny's 125 frameworks
2. Add archetype associations to existing awards
3. No code changes needed

**Phase 2: Algorithm Enhancement (Medium Risk)**
1. Consolidate probability formulas into single `AwardsProbabilityEngine`
2. Add archetype factor to probability calculation
3. Integrate Jenny's coaching intelligence into fit scoring
4. Add unit tests for new factors

**Phase 3: Win Cascade Logic (Medium Risk)**
1. Create new `WinCascadeModule` in `agents/modules/`
2. Integrate into `_sequence_applications()` method
3. Update portfolio output to include cascade metadata
4. Update frontend to display cascade strategy

**Phase 4: Summer Programs (Low Risk)**
1. Leverage existing `opportunities` table
2. Create parallel `SummerProgramsModule`
3. Integrate into Awards Agent or create separate agent

### 10.5 Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Probability formula changes break existing behavior | Medium | High | Version outputs, A/B test, golden dataset comparison |
| Win cascade adds complexity | Medium | Medium | Separate module, feature flag |
| Frontend breaks with new fields | Low | Medium | Backward-compatible field additions |
| Performance degradation | Low | Medium | Add caching layer |
| Archetype mismatch | Low | Low | Validation and fallback |

---

## APPENDIX A: FILE INVENTORY

| File | Lines | Purpose |
|------|-------|---------|
| `agents/agents/awards.py` | 791 | Main AwardsAgent class |
| `agents/modules/awards_probability.py` | 408 | Probability engine |
| `agents/seeds/awards_data.py` | ~2000 | Awards database seed |
| `agents/evaluation/rubrics/awards.py` | 298 | Evaluation rubric |
| `agents/tests/test_v2_modules.py` | ~400 | Unit tests |
| `agents/tests/test_mile_deep_e2e.py` | ~600 | E2E tests |
| `supabase/migrations/007_opportunities_awards.sql` | 394 | Database schema |
| `supabase/migrations/025_awards_probability.sql` | ~50 | Probability fields |
| `components/agents/AgentDetailModal.tsx` | ~600 | Frontend detail modal |

---

## APPENDIX B: API REFERENCE

### Match Awards
```
GET /agents/awards/match/{profile_id}

Response:
{
  "success": boolean,
  "total_matches": number,
  "portfolio": Portfolio,
  "top_recommendations": Award[],
  "timeline": TimelineEntry[]
}
```

### Get Portfolio
```
GET /agents/awards/portfolio/{profile_id}

Response:
{
  "success": boolean,
  "portfolio": Portfolio,
  "expected_wins": number
}
```

### Build Portfolio
```
POST /agents/awards/portfolio

Request:
{
  "profile_id": string,
  "student": object (optional),
  "awards": Award[] (optional)
}

Response:
{
  "success": boolean,
  "portfolio": Portfolio,
  "formatted_summary": string,
  "recommendations": string[]
}
```

---

## APPENDIX C: EVALUATION RUBRIC SUMMARY

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Relevance | 25% | Alignment with spike and narrative |
| Strategic Fit | 25% | Would winning strengthen application? |
| Achievability | 20% | Realistic Likely/Target/Stretch balance |
| Comprehensiveness | 15% | Are important awards missing? |
| Rationale Quality | 15% | Compelling "why" explanations |

**Scoring:** 1-5 scale per dimension, weighted average for total

---

**Document End**

*This discovery report was generated as part of the Awards Agent enhancement integration project. No changes were made to the codebase during discovery.*
