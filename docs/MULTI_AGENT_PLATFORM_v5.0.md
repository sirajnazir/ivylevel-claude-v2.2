# IvyLevel Multi-Agent Platform v5.0

> **Complete Technical Specification**
>
> Version: 5.0 (Agentic)
> Last Updated: January 2026
> Status: Production Ready

---

## Table of Contents

1. [Product Requirements Document (PRD)](#1-product-requirements-document-prd)
2. [Jobs To Be Done (JTBD)](#2-jobs-to-be-done-jtbd)
3. [UI/UX Specification](#3-uiux-specification)
4. [Technical Specification](#4-technical-specification)
5. [Database Schema](#5-database-schema)
6. [Data Flow Architecture](#6-data-flow-architecture)
7. [API Reference](#7-api-reference)
8. [Appendices](#8-appendices)

---

## 1. Product Requirements Document (PRD)

### 1.1 Executive Summary

The IvyLevel Multi-Agent Platform is an AI-powered college admissions coaching system that orchestrates multiple specialized agents to provide personalized strategic guidance. The platform implements a sophisticated 6-agent architecture with self-correcting ReAct cycles, enabling autonomous decision-making with human-in-the-loop oversight for critical decisions.

### 1.2 Vision Statement

**"Every student deserves a Jenny"** - Democratize elite college admissions coaching by encoding expert methodology into an intelligent multi-agent system that provides personalized, strategic guidance at scale.

### 1.3 Core Value Propositions

| Value Prop | Description | Target Metric |
|------------|-------------|---------------|
| **Personalization** | Hyper-personalized activity recommendations using 4 Pillars + 10 Dimensions framework | 94%+ specificity score |
| **Strategic Intelligence** | Hidden probability analysis and strategic positioning | >80% archetype match accuracy |
| **Self-Correction** | ReAct cycles that improve output quality automatically | 70+ quality threshold |
| **Execution Support** | Bridge strategy-execution gap with scaffolding | >80% project completion |

### 1.4 Target Users

#### Primary Personas

1. **High-Achieving Student (Primary)**
   - Grade: 9-12
   - Goal: Top-tier university admission
   - Pain: Overwhelmed by options, lacks strategic direction

2. **First-Generation Student**
   - Limited access to guidance
   - Needs more hand-holding
   - Benefits from hidden opportunity identification

3. **Parent/Guardian**
   - Wants visibility into student progress
   - Needs reassurance and strategic overview

### 1.5 Success Metrics (KPIs)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Quality Score | ≥70% | Guardrails validation |
| Archetype Match | ≥80% | Identity synthesis confidence |
| Activity Completion | ≥80% | Execution tracking |
| User Engagement | Daily active | Dashboard visits |
| Crisis Recovery | <72 hours | Time to resolution |

### 1.6 Feature Requirements

#### P0 - Critical (Must Have)

| Feature | Description | Agent |
|---------|-------------|-------|
| Identity Synthesis | Extract spike, archetype, pillars from profile | EC Agent |
| Activity Generation | Generate personalized EC activities | EC Generation Engine |
| Award Matching | Match to relevant awards with strategic tiers | Awards Agent |
| Program Matching | Match to summer programs with fit scoring | Programs Agent |
| Strategic Roadmap | Unified game plan with phases | GamePlan Agent |
| ReAct Self-Correction | Quality improvement through iteration | ReAct Wrapper |

#### P1 - High Priority

| Feature | Description | Agent |
|---------|-------------|-------|
| Project Scaffolding | Break projects into microsteps | Execution Agent |
| Crisis Handling | Transform crises into opportunities | Execution Agent |
| Narrative Synthesis | Generate brand statement and narrative DNA | Narrative Agent |
| Timeline Alerts | Deadline tracking and notifications | Programs Agent |

#### P2 - Medium Priority

| Feature | Description | Agent |
|---------|-------------|-------|
| Essay Analysis | AI-powered essay feedback | Tools |
| Voice Validation | Jenny's coaching voice compliance | Guardrails |
| Golden Benchmarking | Compare to successful profiles | ReAct |

### 1.7 Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Response Time | <120s for full game plan generation |
| Availability | 99.9% uptime |
| Scalability | Support 10,000 concurrent users |
| Security | SOC 2 compliant, data encryption |
| Privacy | FERPA/COPPA compliant |

---

## 2. Jobs To Be Done (JTBD)

### 2.1 Primary Jobs

#### Job 1: Strategic Identity Discovery

> **When** I'm starting my college journey
> **I want to** understand my unique identity and positioning
> **So that** I can differentiate myself in applications

**Functional Requirements:**
- Extract identity signals from profile data
- Classify into one of 8 archetypes
- Generate a compelling "spike" narrative
- Identify 3-5 pillars of differentiation

**Emotional Requirements:**
- Feel confident in my unique story
- Understand what makes me different
- Have a clear direction

**Success Criteria:**
- Archetype confidence ≥70%
- Spike specificity ≥85%
- User validates identity resonance

---

#### Job 2: Personalized Activity Planning

> **When** I need to build my extracurricular portfolio
> **I want to** receive activity recommendations tailored to my identity
> **So that** my activities reinforce my narrative

**Functional Requirements:**
- Generate activities using 4 Pillars framework
- Apply 10 Dimensions of hyper-personalization
- Pass "Only They" uniqueness test
- Categorize by gap addressed (Signature Project, Leadership, Research, etc.)

**Emotional Requirements:**
- Feel excited about activities (not generic)
- See myself in the recommendations
- Believe activities are achievable

**Success Criteria:**
- 3+ activities generated per profile
- "Only They" test pass rate ≥80%
- Activity implementation rate ≥60%

---

#### Job 3: Strategic Award/Program Matching

> **When** I'm looking for awards and programs
> **I want to** find opportunities that match my profile and goals
> **So that** I can build credentials efficiently

**Functional Requirements:**
- Match based on archetype fit
- Apply strategic tier filtering (Tier 1-4)
- Create 2-2-1 portfolio (reach/target/safety)
- Identify hidden value opportunities

**Emotional Requirements:**
- Feel I have a realistic chance
- Understand strategic positioning
- See clear application path

**Success Criteria:**
- ≥50 award matches per profile
- ≥20 program matches per profile
- Fit score accuracy ≥75%

---

#### Job 4: Unified Strategic Roadmap

> **When** I have multiple recommendations
> **I want to** see everything organized into a coherent plan
> **So that** I know what to do and when

**Functional Requirements:**
- Synthesize EC, Awards, Programs into unified view
- Organize into strategic phases (Foundation, Momentum, Capstone)
- Generate identity seeds for long-term planting
- Provide master narrative connecting everything

**Emotional Requirements:**
- Feel organized and in control
- See the bigger picture
- Trust the strategic logic

**Success Criteria:**
- 3 strategic phases defined
- 6+ identity seeds planted
- Narrative coherence score ≥80%

---

#### Job 5: Execution Support

> **When** I'm implementing my plan
> **I want to** have support to actually complete activities
> **So that** strategy becomes reality

**Functional Requirements:**
- Break projects into 20+ microsteps
- Detect blockers (>5 days inactivity)
- Track Execution Debt Score
- Handle crises with opportunity transformation

**Emotional Requirements:**
- Feel supported, not alone
- Have accountability
- See progress clearly

**Success Criteria:**
- Project completion ≥80%
- EDS <50
- Crisis recovery <72 hours

---

### 2.2 Job Map

```
DISCOVERY          PLANNING           EXECUTION          SUCCESS
    │                  │                  │                 │
    ▼                  ▼                  ▼                 │
┌─────────┐     ┌───────────┐     ┌───────────┐            │
│ EC Agent│────▶│ GamePlan  │────▶│ Execution │─────────────▶
│(Identity)│    │ Agent     │     │ Agent     │
└─────────┘     └───────────┘     └───────────┘
    │                  │
    ▼                  ▼
┌─────────┐     ┌───────────┐
│ Awards  │     │ Programs  │
│ Agent   │     │ Agent     │
└─────────┘     └───────────┘
```

---

## 3. UI/UX Specification

### 3.1 Design Principles

1. **Clarity Over Complexity** - Complex AI processes presented simply
2. **Progressive Disclosure** - Show summary, expand for details
3. **Trust Through Transparency** - Show reasoning, not just results
4. **Action-Oriented** - Every view leads to clear next steps
5. **Celebratory Progress** - Acknowledge achievements visually

### 3.2 Component Architecture

#### 3.2.1 Agent Cards (Summary View)

```
┌─────────────────────────────────────────┐
│ [Icon] Agent Name                    ↻  │
├─────────────────────────────────────────┤
│                                         │
│   ┌─────┐  ┌─────┐  ┌─────┐            │
│   │  3  │  │  6  │  │  4  │            │
│   │Acts │  │Seeds│  │Opps │            │
│   └─────┘  └─────┘  └─────┘            │
│                                         │
│   Category 1              ████████ 3   │
│   Category 2              ██████   2   │
│   Category 3              ████     1   │
│                                         │
│   [Preview Items...]                    │
│                                         │
│   ─────────────────────────────────────│
│   Refresh  │  Chat  │  Click for details│
└─────────────────────────────────────────┘
```

**Card Types:**

| Card | Key Metrics | Preview Content |
|------|-------------|-----------------|
| EC Agent | Activities, Seeds, Categories | Top activities |
| Awards Agent | Reach/Target/Safety counts | Top recommendations |
| Programs Agent | Matches, Alerts, Synergies | Top programs |
| GamePlan Agent | Activities, Seeds, Phases | Current phase |
| Execution Agent | EDS, Blockers, Projects | Active tasks |

#### 3.2.2 Agent Detail Modal (Expanded View)

```
┌────────────────────────────────────────────────────────┐
│ [X]                    Agent Name - Detail View        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ▼ Section 1 (Expandable)                    [Count]  │
│  ┌────────────────────────────────────────────────┐   │
│  │ Content for section 1...                       │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  ▶ Section 2 (Collapsed)                     [Count]  │
│                                                        │
│  ▶ Section 3 (Collapsed)                     [Count]  │
│                                                        │
│  ═══════════════════════════════════════════════════  │
│  Agent Reasoning Process                               │
│  ─────────────────────────────────────────────────────│
│  │ Passed │ Cycles: 3/3 │ Final: 76 │ +56 │ 1m 51s │  │
│  │                                                    │
│  │  Trajectory: ●────●────●                          │
│  │              20   68   76                         │
│  │                                                    │
│  │  ▼ Cycle 1 of 3                           [20]    │
│  │  ┌──────────────────────────────────────────────┐ │
│  │  │ 🧠 THINK                              154ms   │ │
│  │  │ "EC Agent analyzing 0 activities..."         │ │
│  │  │                                              │ │
│  │  │ ⚡ ACT                                186ms   │ │
│  │  │ Executing process() with 5 hints             │ │
│  │  │                                              │ │
│  │  │ 👁 OBSERVE                            20%    │ │
│  │  │ Quality: 20% | Voice: 80% | Golden: 65%      │ │
│  │  │                                              │ │
│  │  │ 📚 LEARN                             +20 pts │ │
│  │  │ "Spike too generic, archetype unclear"       │ │
│  │  └──────────────────────────────────────────────┘ │
│  │                                                    │
│  │  ▶ Cycle 2 of 3                           [68]    │
│  │  ▶ Cycle 3 of 3 (Latest)                  [76]    │
│  └────────────────────────────────────────────────────┘
└────────────────────────────────────────────────────────┘
```

#### 3.2.3 ReAct Visualization Component

**Header:**
```
┌─────────────────────────────────────────────────────────┐
│  🧠 Agent Reasoning Process              v5.0 Agentic  │
├─────────────────────────────────────────────────────────┤
│  [Passed] Cycles: 3/3 │ Final: 76 │ +56 │ Duration: 1m │
│                                                         │
│  Trajectory: ●───────●───────●                         │
│              20      68      76                         │
│           Cycle 1  Cycle 2  Cycle 3                    │
└─────────────────────────────────────────────────────────┘
```

**Cycle Card (Expanded):**
```
┌─────────────────────────────────────────────────────────┐
│  Cycle 2 of 3                            Score: 68 (+48)│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ▼ 🧠 THINK                                     154ms  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ "EC Agent correction cycle 2. Refining identity  │  │
│  │  synthesis across 1 pillars. Applying 5 targeted │  │
│  │  hints to strengthen narrative coherence."       │  │
│  │                                                   │  │
│  │ Focus: [Spike Specificity] [Archetype Confidence]│  │
│  │                                                   │  │
│  │ Tools: archetype_classifier • spike_generator •  │  │
│  │        theme_extractor • golden_benchmark        │  │
│  │                                                   │  │
│  │ Gap Analysis:                                    │  │
│  │   🔴 CRITICAL: Spike too generic (30% vs 94%)    │  │
│  │   🟡 MEDIUM: Archetype unclear (0% confidence)   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ▶ ⚡ ACT                                        186ms  │
│                                                         │
│  ▶ 👁 OBSERVE                              Quality: 68% │
│                                                         │
│  ▶ 📚 LEARN                                   +48 pts  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Color System

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Primary | Orange | `#FF4A23` | Accent, buttons, selected |
| Secondary | Maroon | `#641432` | Headings, important text |
| Success | Green | `#16A34A` | Passed, positive, EC activities |
| Warning | Amber | `#D97706` | Caution, awards |
| Error | Red | `#DC2626` | Failed, negative |
| Info | Blue | `#3B82F6` | Programs, information |
| THINK | Orange | `#FF4A23` | Reasoning phase |
| ACT | Blue | `#3B82F6` | Action phase |
| OBSERVE | Purple | `#8B5CF6` | Observation phase |
| LEARN | Green | `#10B981` | Learning phase |

### 3.4 Responsive Design

| Breakpoint | Layout | Card Columns |
|------------|--------|--------------|
| Mobile (<640px) | Stack | 1 |
| Tablet (640-1024px) | Grid | 2 |
| Desktop (>1024px) | Grid | 3-4 |

### 3.5 Interaction Patterns

1. **Card Click** → Opens Detail Modal
2. **Section Header Click** → Expands/Collapses Section
3. **Cycle Header Click** → Expands/Collapses Cycle Details
4. **Refresh Button** → Regenerates Agent Data
5. **Chat Button** → Opens Agent-Specific Chat

---

## 4. Technical Specification

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 14)                    │
├─────────────────────────────────────────────────────────────────┤
│  React Components    │    Hooks (React Query)    │    Stores   │
│  - AgentCards        │    - useGamePlan          │   - Zustand │
│  - AgentDetailModal  │    - useAgentData         │   - Results │
│  - ReActVisualization│    - useNotifications     │   - Student │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (Next.js Routes)                │
├─────────────────────────────────────────────────────────────────┤
│  /api/agents/gameplan/generate    │  /api/agents/awards/match  │
│  /api/agents/assessment/enhance   │  /api/agents/opportunities/│
│  /api/agents/execution/scaffold   │  /api/agents/tools/        │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AGENT SERVICE (Python/FastAPI)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────────────────────────────┐   │
│  │   Router    │────▶│        ORCHESTRATION LAYER          │   │
│  │ (main.py)   │     │                                     │   │
│  └─────────────┘     │  ┌─────────────────────────────┐    │   │
│                      │  │      GamePlanAgent          │    │   │
│                      │  │  (Master Orchestrator)      │    │   │
│                      │  └─────────────────────────────┘    │   │
│                      │              │                      │   │
│                      │    ┌─────────┴─────────┐            │   │
│                      │    ▼                   ▼            │   │
│                      │  ┌───────┐  ┌────────────────────┐  │   │
│                      │  │  EC   │  │ Awards │ Programs  │  │   │
│                      │  │ Agent │  │ Agent  │ Agent     │  │   │
│                      │  │(FIRST)│  │   (PARALLEL)       │  │   │
│                      │  └───────┘  └────────────────────┘  │   │
│                      └─────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   INTELLIGENCE LAYER                    │   │
│  │                                                         │   │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐ │   │
│  │  │  ReAct Wrapper  │  │   EC Generation Engine       │ │   │
│  │  │  (Self-Correct) │  │   (4 Pillars + 10 Dims)      │ │   │
│  │  └─────────────────┘  └──────────────────────────────┘ │   │
│  │                                                         │   │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐ │   │
│  │  │   Guardrails    │  │    Narrative Synthesis       │ │   │
│  │  │  (Validation)   │  │    (Jenny's Formula)         │ │   │
│  │  └─────────────────┘  └──────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     DATA LAYER                          │   │
│  │                                                         │   │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐ │   │
│  │  │  Supabase DB    │  │   Enriched Data Files        │ │   │
│  │  │  (Profiles)     │  │   (Awards, Programs JSON)    │ │   │
│  │  └─────────────────┘  └──────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Agent Specifications

#### 4.2.1 EC Agent (Extracurriculars)

**Purpose:** Identity synthesis and activity generation

**File:** `/agents/agents/extracurriculars.py`

**Input:**
```python
{
  "profile_id": "uuid",
  "react_hints": ["hint1", "hint2"],  # Optional
  "_react_feedback": {                 # Optional
    "hints": [],
    "focus_areas": [],
    "gap_analysis": {},
    "cycle": 1
  }
}
```

**Output:**
```python
{
  "success": True,
  "profile_id": "uuid",
  "identity_synthesis": {
    "spike": "...",
    "spike_confidence": 0.85,
    "archetype": "community_changemaker",
    "archetype_confidence": 0.80,
    "pillars": ["IDENTITY", "SERVICE", "PASSION"],
    "portfolio_balance_score": 0.75,
    "portfolio_gaps": ["leadership", "research"],
    "total_impact_score": 8.5
  },
  "portfolio_analysis": {
    "category_counts": {},
    "balance_score": 0.75,
    "gaps": [],
    "strengths": []
  },
  "ec_generation": {
    "four_pillars": {...},
    "master_narrative": "...",
    "recommended_activities": [
      {
        "title": "...",
        "activity_type": "signature_project",
        "description": "...",
        "gap_addressed": "signature_project",
        "implementation_steps": [],
        "validation_criteria": {
          "only_they_test": "...",
          "success_metrics": []
        }
      }
    ]
  }
}
```

**Primitives Used:**
- TYPE-013: Portfolio Optimization
- TYPE-014: Narrative Synthesis
- TYPE-015: Impact Assessment

**Dependencies:** EC Generation Engine, Guardrails

---

#### 4.2.2 Awards Agent

**Purpose:** Strategic award matching

**File:** `/agents/agents/awards.py`

**Input:**
```python
{
  "profile_id": "uuid",
  "identity_synthesis": {...},  # From EC Agent
  "constraints": {...}
}
```

**Output:**
```python
{
  "success": True,
  "profile_id": "uuid",
  "total_matches": 64,
  "portfolio": {
    "reach": [...],   # 2 awards
    "target": [...],  # 2 awards
    "safety": [...]   # 1 award
  },
  "top_recommendations": [...],
  "timeline": [...],
  "strategic_insights": [...]
}
```

**Data Source:** `/agents/seeds/enriched/awards_enriched.json`

---

#### 4.2.3 Programs Agent

**Purpose:** Summer program matching

**File:** `/agents/agents/programs.py`

**Input:**
```python
{
  "profile_id": "uuid",
  "identity_synthesis": {...},  # From EC Agent
  "constraints": {...}
}
```

**Output:**
```python
{
  "success": True,
  "profile_id": "uuid",
  "total_matches": 29,
  "top_recommendations": [...],
  "advance_alerts": [...],
  "synergy_recommendations": [...],
  "timeline": [...],
  "strategic_insights": [...]
}
```

**Data Source:** `/agents/seeds/enriched/programs_enriched.json`

---

#### 4.2.4 GamePlan Agent (Orchestrator)

**Purpose:** Orchestrate all agents and synthesize unified roadmap

**File:** `/agents/agents/gameplan.py`

**Orchestration Flow:**
```python
async def process(profile_id):
    # Step 1: EC Agent FIRST
    ec_result = await ec_agent.process(profile_id)
    identity_synthesis = ec_result["identity_synthesis"]

    # Step 2: Awards + Programs PARALLEL
    awards_result, programs_result = await asyncio.gather(
        awards_agent.process(profile_id, identity_synthesis=identity_synthesis),
        programs_agent.process(profile_id, identity_synthesis=identity_synthesis)
    )

    # Step 3: Synthesis
    return synthesize_gameplan(ec_result, awards_result, programs_result)
```

**Output:**
```python
{
  "success": True,
  "game_plan": {
    "profile_id": "uuid",
    "identity_synthesis": {...},
    "archetype": "community_changemaker",
    "spike": "...",
    "pillars": [...],
    "narrative_dna": "...",
    "ec_generation": {...},
    "awards": {...},
    "programs": {...},
    "activities": [...],
    "identity_seeds": [...],
    "phases": [...],
    "summary": {...},
    "_react": {...}  # ReAct metadata
  },
  "_react_by_agent": {
    "ec": {...},
    "awards": {...},
    "programs": {...}
  }
}
```

---

### 4.3 EC Generation Engine

**File:** `/agents/agents/core/ec_generation_engine.py`

#### 4.3.1 Four Pillars Framework

```python
class FourPillars:
    """
    IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE
    """

    identity: IdentityPillar  # Demographics, culture, personality
    aptitude: AptitudePillar  # Skills, academic strengths
    passion: PassionPillar    # Interests, hobbies, energy
    service: ServicePillar    # Volunteering, causes, values

    def get_specificity_score(self) -> float:
        """Calculate overall specificity (0-1)"""

    def get_pillar_count(self) -> int:
        """Count pillars with data"""
```

#### 4.3.2 Ten Dimensions of Hyper-Personalization

| # | Dimension | Description |
|---|-----------|-------------|
| 1 | Geographic Context | Local relevance, partners, community |
| 2 | Identity-Informed WHY | Specific identity connection |
| 3 | Field Gap Analysis | Statistics about gap being filled |
| 4 | Personal Catalyst | Origin story, emotional connection |
| 5 | Target Audience | Specific demographics served |
| 6 | Unique Contribution | What intersection makes them unique |
| 7 | Representation | Who appears in their work |
| 8 | Cultural Depth | How values are integrated |
| 9 | Temporal Relevance | Why now, current context |
| 10 | Problem Specificity | Exact problem, measurable goal |

#### 4.3.3 Gap Types

```python
class GapType(Enum):
    ACTIVITY_COUNT = "activity_count"
    SIGNATURE_PROJECT = "signature_project"
    LEADERSHIP = "leadership"
    RESEARCH = "research"
    COMMUNITY_SERVICE = "community_service"
    NARRATIVE_COHERENCE = "narrative_coherence"
```

#### 4.3.4 "Only They" Test

```python
def validate_only_they(activity: GeneratedActivity) -> bool:
    """
    Validates that the activity passes the "Only They" test:
    - Could another student with different identity do this? NO
    - Is this generic/template-like? NO
    - Does it reflect specific pillars? YES
    """
```

---

### 4.4 ReAct Framework

**File:** `/agents/agents/core/react_wrapper.py`

#### 4.4.1 Cycle Structure

```python
@dataclass
class ReActCycle:
    cycle_number: int
    think: str                    # Reasoning
    action: str                   # What was executed
    observation: Dict[str, Any]   # Validation results
    learning: Optional[str]       # Improvement insights
    quality_score: float          # 0-100
    voice_score: Optional[float]  # 0-100
    golden_similarity: Optional[float]  # 0-1
    duration_ms: int
    passed: bool
```

#### 4.4.2 Quality Thresholds

| Threshold | Value | Description |
|-----------|-------|-------------|
| MIN_QUALITY_SCORE | 70 | Guardrails confidence × 100 |
| MIN_VOICE_SCORE | 70 | Jenny voice compliance |
| MIN_GOLDEN_SIMILARITY | 0.6 | Golden benchmark match |
| MAX_REACT_CYCLES | 3 | Maximum iterations |

#### 4.4.3 Phase Details

**THINK Phase:**
- LLM-powered reasoning about profile
- Tool selection (archetype_classifier, spike_generator, etc.)
- Gap analysis with severity categorization
- Specific hint generation

**ACT Phase:**
- Execute agent's process() method
- Pass improvement hints as _react_feedback
- Track execution time

**OBSERVE Phase:**
- Validate output with guardrails
- Calculate quality score
- Compare to golden benchmark
- Check voice compliance

**LEARN Phase:**
- Analyze what worked/failed
- Generate specific corrections
- Decide whether to continue

---

### 4.5 Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Next.js | 14.x |
| UI Components | React | 18.x |
| Styling | Tailwind CSS | 3.x |
| State Management | Zustand | 4.x |
| Data Fetching | React Query | 5.x |
| Backend | Python/FastAPI | 3.11+ |
| LLM | OpenAI GPT-4o | Latest |
| Database | Supabase/PostgreSQL | 15.x |
| Authentication | Supabase Auth | Latest |

---

## 5. Database Schema

### 5.1 Core Tables

#### profiles
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),

  -- Assessment Link
  assessment_id UUID,

  -- Identity
  archetype_id UUID REFERENCES archetypes(id),
  archetype_confidence FLOAT CHECK (archetype_confidence BETWEEN 0 AND 1),
  archetype_rationale TEXT,
  narrative_dna TEXT,
  narrative_themes JSONB,

  -- Execution
  execution_debt FLOAT DEFAULT 0,

  -- Strategic Intelligence
  hidden_target TEXT,
  hidden_probabilities JSONB,
  hidden_strategy_notes TEXT,

  -- Identity Seeds
  identity_seeds JSONB,

  -- Constraints
  constraints JSONB,

  -- Agent Tracking
  last_agent_interaction TIMESTAMPTZ,
  agent_notes JSONB,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_profiles_user ON profiles(user_id);
CREATE INDEX idx_profiles_archetype ON profiles(archetype_id);
```

#### agent_state_versions
```sql
CREATE TABLE agent_state_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID REFERENCES profiles(id) NOT NULL,

  -- Agent Info
  agent TEXT NOT NULL CHECK (agent IN (
    'Assessment', 'Execution', 'GamePlan',
    'Awards', 'Opportunity', 'EC'
  )),
  version INTEGER NOT NULL,

  -- State Data
  state JSONB NOT NULL,
  state_diff JSONB,

  -- Event Info
  event_type TEXT NOT NULL,
  event_payload JSONB,

  -- Audit
  created_by TEXT CHECK (created_by IN ('agent', 'human', 'system')),
  is_human_override BOOLEAN DEFAULT FALSE,
  override_approved_by TEXT,

  -- Rollback
  is_rolled_back BOOLEAN DEFAULT FALSE,
  rolled_back_to_version INTEGER,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now(),

  -- Constraints
  UNIQUE(profile_id, agent, version)
);

-- Indexes
CREATE INDEX idx_state_versions_profile ON agent_state_versions(profile_id);
CREATE INDEX idx_state_versions_agent ON agent_state_versions(agent);
CREATE INDEX idx_state_versions_human ON agent_state_versions(is_human_override);
```

#### game_plans
```sql
CREATE TABLE game_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  profile_id UUID REFERENCES profiles(id),

  -- Plan Data
  plan_data JSONB NOT NULL,
  target_archetype TEXT,

  -- Progress
  current_phase TEXT,
  current_week INTEGER DEFAULT 1,
  completion_percentage FLOAT DEFAULT 0,

  -- Status
  is_active BOOLEAN DEFAULT TRUE,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- View for active game plan
CREATE VIEW v_active_game_plan AS
SELECT * FROM game_plans WHERE is_active = TRUE;
```

#### archetypes
```sql
CREATE TABLE archetypes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  description TEXT,
  characteristics JSONB,
  signals JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Seed data
INSERT INTO archetypes (name, display_name) VALUES
  ('academic_powerhouse', 'Academic Powerhouse'),
  ('stem_innovator', 'STEM Innovator'),
  ('creative_visionary', 'Creative Visionary'),
  ('community_changemaker', 'Community Changemaker'),
  ('entrepreneurial_leader', 'Entrepreneurial Leader'),
  ('humanities_scholar', 'Humanities Scholar'),
  ('athletic_scholar', 'Athletic Scholar'),
  ('multi_hyphenate', 'Multi-Hyphenate');
```

### 5.2 Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────────────┐
│   users     │     │     archetypes      │
├─────────────┤     ├─────────────────────┤
│ id (PK)     │     │ id (PK)             │
│ email       │     │ name                │
│ ...         │     │ display_name        │
└──────┬──────┘     │ characteristics     │
       │            └──────────┬──────────┘
       │                       │
       ▼                       │
┌─────────────────────────────────────────┐
│               profiles                   │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ user_id (FK) ────────────────────────────┤
│ archetype_id (FK) ───────────────────────┤
│ assessment_id                            │
│ narrative_dna                            │
│ hidden_target                            │
│ identity_seeds (JSONB)                   │
│ constraints (JSONB)                      │
└──────┬──────────────────────────────────┘
       │
       ├───────────────────────┐
       │                       │
       ▼                       ▼
┌─────────────────┐   ┌─────────────────────┐
│  game_plans     │   │ agent_state_versions│
├─────────────────┤   ├─────────────────────┤
│ id (PK)         │   │ id (PK)             │
│ user_id (FK)    │   │ profile_id (FK)     │
│ profile_id (FK) │   │ agent               │
│ plan_data       │   │ version             │
│ current_phase   │   │ state (JSONB)       │
│ is_active       │   │ event_type          │
└─────────────────┘   │ is_human_override   │
                      └─────────────────────┘
```

---

## 6. Data Flow Architecture

### 6.1 Complete Request Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                            │
│   User clicks "Generate Game Plan" on Dashboard                │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                              │
│                                                                │
│   1. useGamePlan hook triggered                                │
│   2. React Query makes POST /api/agents/gameplan/generate      │
│   3. Loading state shown to user                               │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (Next.js)                       │
│                                                                │
│   Route: /app/api/agents/gameplan/generate/route.ts            │
│   1. Validate request                                          │
│   2. Forward to Python agent service                           │
│   3. POST http://localhost:8001/agents/gameplan/generate       │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    AGENT SERVICE (Python)                      │
│                                                                │
│   Router: /agents/main.py                                      │
│   1. Parse profile_id from request                             │
│   2. Load profile from Supabase                                │
│   3. Initialize orchestrator                                   │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION                               │
│                                                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ STEP 1: EC Agent (FIRST)                                │  │
│   │                                                         │  │
│   │   ┌───────────────────────────────────────────────────┐ │  │
│   │   │ ReAct Wrapper                                     │ │  │
│   │   │                                                   │ │  │
│   │   │   CYCLE 1:                                        │ │  │
│   │   │   ├─ THINK: Analyze profile, identify gaps        │ │  │
│   │   │   ├─ ACT: Run EC Engine (4 Pillars)               │ │  │
│   │   │   ├─ OBSERVE: Quality=20%, Voice=80%              │ │  │
│   │   │   └─ LEARN: "Spike too generic, retry"            │ │  │
│   │   │                                                   │ │  │
│   │   │   CYCLE 2:                                        │ │  │
│   │   │   ├─ THINK: Apply hints, focus on specificity     │ │  │
│   │   │   ├─ ACT: Regenerate with corrections             │ │  │
│   │   │   ├─ OBSERVE: Quality=68%, Voice=80%              │ │  │
│   │   │   └─ LEARN: "Improving, continue"                 │ │  │
│   │   │                                                   │ │  │
│   │   │   CYCLE 3:                                        │ │  │
│   │   │   ├─ THINK: Final refinements                     │ │  │
│   │   │   ├─ ACT: Generate final output                   │ │  │
│   │   │   ├─ OBSERVE: Quality=76%, PASSED!                │ │  │
│   │   │   └─ LEARN: "Quality achieved"                    │ │  │
│   │   └───────────────────────────────────────────────────┘ │  │
│   │                                                         │  │
│   │   OUTPUT: identity_synthesis, ec_generation             │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                 │
│                              ▼                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ STEP 2: Awards + Programs (PARALLEL)                    │  │
│   │                                                         │  │
│   │   ┌─────────────────┐    ┌─────────────────┐            │  │
│   │   │  Awards Agent   │    │ Programs Agent  │            │  │
│   │   │                 │    │                 │            │  │
│   │   │ INPUT:          │    │ INPUT:          │            │  │
│   │   │ - profile_id    │    │ - profile_id    │            │  │
│   │   │ - identity_     │    │ - identity_     │            │  │
│   │   │   synthesis     │    │   synthesis     │            │  │
│   │   │                 │    │                 │            │  │
│   │   │ OUTPUT:         │    │ OUTPUT:         │            │  │
│   │   │ - 64 matches    │    │ - 29 matches    │            │  │
│   │   │ - 2-2-1 portfolio│   │ - synergies     │            │  │
│   │   │ - timeline      │    │ - alerts        │            │  │
│   │   └─────────────────┘    └─────────────────┘            │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                 │
│                              ▼                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ STEP 3: Synthesis                                       │  │
│   │                                                         │  │
│   │   - Combine EC activities + Awards + Programs           │  │
│   │   - Generate phases (Foundation, Momentum, Capstone)    │  │
│   │   - Create identity seeds                               │  │
│   │   - Build master narrative                              │  │
│   │   - Attach _react metadata                              │  │
│   └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    RESPONSE PATH                               │
│                                                                │
│   1. Agent service returns JSON response                       │
│   2. Next.js gateway forwards to frontend                      │
│   3. React Query caches result                                 │
│   4. Components re-render with new data                        │
│   5. User sees populated dashboard                             │
└────────────────────────────────────────────────────────────────┘
```

### 6.2 Data Transformations

#### Profile → EC Agent Input
```javascript
// Frontend extracts profile_id
const profileId = user.profile?.id;

// API call
POST /api/agents/gameplan/generate
Body: { profile_id: profileId }
```

#### EC Agent → Downstream Agents
```python
# EC Agent produces identity_synthesis
identity_synthesis = {
    "spike": "Tech Explorer developing inclusive platforms...",
    "spike_confidence": 0.85,
    "archetype": "community_changemaker",
    "archetype_confidence": 0.80,
    "pillars": ["IDENTITY", "SERVICE", "PASSION"]
}

# Passed to Awards/Programs agents
awards_result = await awards_agent.process(
    profile_id,
    identity_synthesis=identity_synthesis
)
```

#### Backend → Frontend Response
```python
# Backend returns
{
    "success": True,
    "game_plan": {...},
    "_react_by_agent": {...}
}

# Frontend hook transforms
{
    success: true,
    game_plan: {
        profile_id,
        narrative_dna,
        activities,        # EC activities + phase activities
        ec_generation,     # EC Engine specific data
        awards,
        programs,
        phases,
        _react             # Orchestrator ReAct
    },
    _react_by_agent        # Per-agent ReAct
}
```

### 6.3 State Management

```
┌─────────────────────────────────────────────────────────────┐
│                    STATE FLOW                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐                                           │
│   │ React Query │  ← Primary cache for agent data           │
│   │   Cache     │                                           │
│   └──────┬──────┘                                           │
│          │                                                  │
│          ▼                                                  │
│   ┌─────────────┐                                           │
│   │  Zustand    │  ← UI state (modals, selections)          │
│   │   Stores    │                                           │
│   │             │                                           │
│   │ - results   │  ← Computed/derived state                 │
│   │ - student   │  ← Profile data                           │
│   │ - ui        │  ← UI state                               │
│   └──────┬──────┘                                           │
│          │                                                  │
│          ▼                                                  │
│   ┌─────────────┐                                           │
│   │ Components  │  ← Consume via hooks                      │
│   │             │                                           │
│   │ - Cards     │  ← Summary views                          │
│   │ - Modals    │  ← Detail views                           │
│   │ - ReAct     │  ← Cycle visualization                    │
│   └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. API Reference

### 7.1 GamePlan Endpoints

#### POST /agents/gameplan/generate
Generate complete game plan with orchestration.

**Request:**
```json
{
  "profile_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "game_plan": {
    "profile_id": "uuid",
    "identity_synthesis": {...},
    "archetype": "community_changemaker",
    "spike": "...",
    "pillars": ["IDENTITY", "SERVICE"],
    "narrative_dna": "...",
    "ec_generation": {
      "four_pillars": {...},
      "recommended_activities": [...]
    },
    "awards": {
      "portfolio": {...},
      "top_recommendations": [...]
    },
    "programs": {
      "top_recommendations": [...]
    },
    "activities": [...],
    "identity_seeds": [...],
    "phases": [...],
    "_react": {...}
  },
  "_react_by_agent": {
    "ec": {...},
    "awards": {...},
    "programs": {...}
  }
}
```

#### GET /agents/gameplan/activities/{profile_id}
Get filtered activities for profile.

#### GET /agents/gameplan/seeds/{profile_id}
Get identity seeds for profile.

### 7.2 Assessment Endpoints

#### POST /agents/assessment/enhance
Enhance assessment with AI analysis.

#### POST /agents/narrative/synthesize
Generate narrative DNA.

### 7.3 Awards Endpoints

#### POST /agents/awards/match
Match profile to awards.

### 7.4 Programs Endpoints

#### POST /agents/opportunities/match
Match profile to programs.

#### GET /agents/opportunities/alerts/{profile_id}
Get deadline alerts.

### 7.5 Execution Endpoints

#### POST /agents/execution/scaffold
Create project scaffold.

#### POST /agents/execution/crisis
Handle crisis situation.

#### GET /agents/execution/eds/{profile_id}
Get Execution Debt Score.

#### GET /agents/execution/blockers/{profile_id}
Get active blockers.

---

## 8. Appendices

### 8.1 Glossary

| Term | Definition |
|------|------------|
| **Spike** | A student's unique differentiator - their "point of the spear" |
| **Archetype** | One of 8 student profiles (e.g., STEM Innovator, Community Changemaker) |
| **Pillar** | One of 4 identity dimensions (Identity, Aptitude, Passion, Service) |
| **ReAct** | Reasoning + Acting framework for self-correcting agents |
| **EDS** | Execution Debt Score - measure of incomplete tasks |
| **HITL** | Human-in-the-Loop - human approval for critical decisions |
| **Golden Benchmark** | Reference successful profiles for comparison |
| **Identity Seed** | Strategic activity planted months in advance |

### 8.2 Archetype Reference

| Archetype | Description | Key Signals |
|-----------|-------------|-------------|
| academic_powerhouse | Excellence in academics | High GPA, Olympiads, research |
| stem_innovator | Technology and science focus | Coding, robotics, research |
| creative_visionary | Arts and creative expression | Portfolio, performances |
| community_changemaker | Social impact focus | Service hours, nonprofits |
| entrepreneurial_leader | Business and leadership | Startups, clubs founded |
| humanities_scholar | Liberal arts focus | Writing, debate, languages |
| athletic_scholar | Sports excellence | Varsity, recruitment |
| multi_hyphenate | Multiple strong areas | Cross-domain achievements |

### 8.3 Quality Score Breakdown

```
Quality Score = weighted_average(
    guardrails_confidence × 0.4,
    voice_score × 0.3,
    golden_similarity × 0.3
)

Thresholds:
- PASS: ≥70
- WARN: 50-69
- FAIL: <50
```

### 8.4 Frontend Component Implementation

#### 8.4.1 ReAct Visualization Components

The ReAct visualization is implemented as a set of React components that display the THINK → ACT → OBSERVE → LEARN cycle phases with expand/collapse functionality similar to Claude AI's thinking accordion.

**Component Directory Structure:**
```
/components/agents/react/
├── index.ts                    # Barrel exports
├── ReActVisualization.tsx      # Main container component
├── CycleCard.tsx               # Individual cycle with all 4 phases
└── PhaseAccordion.tsx          # Expandable phase wrapper
```

**Component Details:**

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `ReActVisualization` | Main container that renders header, trajectory, and cycles | Improvement trajectory chart, summary stats, cycle list |
| `CycleCard` | Displays a single ReAct cycle | Cycle header with score/delta, 4 phase accordions |
| `PhaseAccordion` | Expandable wrapper for each phase | Smooth animation, color-coded by phase |

**Phase-Specific Rendering (inline in CycleCard):**

| Phase | Icon | Color | Content Displayed |
|-------|------|-------|------------------|
| THINK | Brain | `#FF4A23` (orange) | Reasoning text, focus areas, tools selected, gap analysis |
| ACT | Zap | `#3B82F6` (blue) | Action description, tools executed with timing, input/output summary |
| OBSERVE | Eye | `#8B5CF6` (purple) | Quality/voice/golden scores with gauges, issues/strengths found |
| LEARN | BookOpen | `#10B981` (green) | Learning reasoning, what worked/failed, corrections for next cycle |

#### 8.4.2 TypeScript Type Definitions

**File:** `/lib/types/react-visualization.ts`

```typescript
// Core phase data types
export interface ThinkPhaseData {
  reasoning: string;
  planned_actions: string[];
  focus_areas: string[];
  gap_analysis: { critical: string[]; medium: string[]; low: string[] };
  tools_selected: string[];
  benchmark_targets: Record<string, number>;
  confidence: number;
}

export interface ActPhaseData {
  action: string;
  tools_executed: ToolExecution[];
  hints_applied: number;
  input_summary: Record<string, unknown>;
  output_summary: Record<string, unknown>;
  duration_ms: number;
}

export interface ObservePhaseData {
  quality_score: number;
  voice_score: number;
  golden_similarity: number;
  combined_score: number;
  passed: boolean;
  failing_dimensions: string[];
  issues_found: string[];
  strengths_found: string[];
}

export interface LearnPhaseData {
  reasoning: string;
  what_worked: string[];
  what_failed: string[];
  quality_delta: number;
  corrections_to_apply: string[];
  should_continue: boolean;
}

// Complete cycle and metadata
export interface CycleSummary {
  cycle: number;
  think: ThinkPhaseData;
  act: ActPhaseData;
  observe: ObservePhaseData;
  learn: LearnPhaseData;
  duration_ms: number;
}

export interface ReactMetadata {
  success: boolean;
  cycles_executed: number;
  max_cycles: number;
  final_confidence: number;
  passed_quality: boolean;
  improvement_trajectory: number[];
  total_duration_ms: number;
  cycle_summary: CycleSummary[];
  agentic_enabled: boolean;
  version: string;
}
```

#### 8.4.3 EC Generation Engine Components

**Component Directory Structure:**
```
/components/agents/ec-engine/
├── FourPillarsGrid.tsx         # 4 Pillars visual grid
├── TenDimensionsAccordion.tsx  # 10 Dimensions expandable list
└── ActivityOutputCard.tsx      # Generated activity with full context
```

**Component Details:**

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `FourPillarsGrid` | Displays the 4 Pillars (Identity, Aptitude, Passion, Service) | Color-coded cards, strength indicators, evidence display |
| `TenDimensionsAccordion` | Shows 10 Dimensions of hyper-personalization | Expandable items, priority indicators, gap recommendations |
| `ActivityOutputCard` | Shows a generated activity with full EC Engine context | Pillar mapping, dimension evidence, Only-They test result |

#### 8.4.4 Integration Points

**AgentDetailModal Integration:**

The `AgentDetailModal` component (`/components/agents/AgentDetailModal.tsx`) integrates the ReAct visualization:

```typescript
import { ReActVisualization } from './react';

// Helper function extracts per-agent ReAct data
function getReactDataForAgent(data, agentType) {
  // Returns appropriate _react data based on agent type
  // Handles _react_by_agent structure from orchestrator
}

// In render:
{hasReactData && (
  <ReActVisualization
    agentName={getAgentDisplayName(agentType)}
    reactData={reactData}
  />
)}
```

**Data Flow:**

```
GamePlan API Response
    │
    ├── game_plan._react           → Orchestrator's own ReAct cycles
    │
    └── _react_by_agent
        ├── ec._react              → EC Agent ReAct cycles
        ├── awards._react          → Awards Agent ReAct cycles
        └── programs._react        → Programs Agent ReAct cycles
    │
    ▼
AgentDetailModal
    │
    └── getReactDataForAgent(data, agentType)
        │
        └── Returns appropriate ReactMetadata
            │
            ▼
        ReActVisualization Component
```

### 8.5 Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2024-06 | Initial multi-agent architecture |
| v2.0 | 2024-08 | Added strategic intelligence |
| v3.0 | 2024-10 | Added ReAct self-correction |
| v4.0 | 2024-12 | Hybrid architecture with EC Engine |
| v5.0 | 2025-01 | Agentic ReAct with visualization |
| v5.1 | 2025-01 | ReAct visualization components, EC Engine UI, TypeScript types |

---

## Document Information

- **Authors:** IvyLevel Engineering Team
- **Last Updated:** January 2026
- **Status:** Production
- **Classification:** Internal Technical Documentation
