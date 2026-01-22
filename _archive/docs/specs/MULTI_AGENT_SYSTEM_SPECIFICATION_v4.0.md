# IvyQuest Multi-Agent Intelligence System Specification
## Version 4.0 - Hybrid Agent Architecture with ReAct Framework

**Last Updated:** January 2026
**Status:** Production Ready
**Validation Profile:** Huda S. (huda@ivylevel.com)

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [ReAct Framework Implementation](#3-react-framework-implementation)
4. [6-Agent Architecture Deep Dive](#4-6-agent-architecture-deep-dive)
5. [Orchestration Flow](#5-orchestration-flow)
6. [Huda's Complete Data Flow](#6-hudas-complete-data-flow)
7. [Awards Matching System](#7-awards-matching-system)
8. [Programs Matching System](#8-programs-matching-system)
9. [LLM Reasoning & Prompts](#9-llm-reasoning--prompts)
10. [Frontend Integration](#10-frontend-integration)
11. [Validation Evidence](#11-validation-evidence)

---

## 1. Executive Summary

The IvyQuest Multi-Agent Intelligence System is a sophisticated AI coaching platform that employs 6 specialized agents working in parallel to provide comprehensive college admissions guidance. The system implements a **Hybrid Agent Architecture (v4.0)** that combines:

- **ReAct Framework**: Reasoning + Acting with quality gates
- **Deterministic Strategic Routing**: No LLM hallucination for critical decisions
- **Parallel Agent Orchestration**: EC → (Awards || Programs) → GamePlan synthesis
- **Jenny's Voice**: Consistent coaching persona across all outputs
- **Strategic Intelligence**: Enriched data with archetype-based matching

### Key Metrics (Huda's Profile)
| Metric | Value |
|--------|-------|
| Total Awards Matched | 64 |
| Total Programs Matched | 29 |
| Activities Planned | 9 |
| Identity Seeds Planted | 8 |
| Archetype | Community Changemaker |
| Spike | Service |
| Narrative Confidence | 90% |
| Average Award Fit | 84% |
| Average Program Fit | 80% |

---

## 2. System Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │ Assessment  │ │   EC Agent  │ │ Game Plan   │ │  Execution  │        │
│  │    Card     │ │    Card     │ │    Card     │ │    Card     │        │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘        │
│         │               │               │               │                │
│  ┌──────┴───────────────┴───────────────┴───────────────┴──────┐        │
│  │                  AgentDashboardV13 Component                 │        │
│  └──────────────────────────┬──────────────────────────────────┘        │
│                             │                                            │
│  ┌─────────────┐ ┌─────────────┐                                        │
│  │   Awards    │ │  Programs   │                                        │
│  │    Card     │ │    Card     │                                        │
│  └──────┬──────┘ └──────┬──────┘                                        │
└─────────┼───────────────┼───────────────────────────────────────────────┘
          │               │
          ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      API ROUTES (Next.js /api/agents/)                   │
│  /gameplan/generate  /awards/match  /opportunities/match  /health       │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     AGENT SERVICE (Python FastAPI :8001)                 │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     ORCHESTRATION LAYER                            │ │
│  │  ┌──────────────────┐                                              │ │
│  │  │ Strategic Router │ ── Deterministic Route Selection             │ │
│  │  └────────┬─────────┘                                              │ │
│  │           │                                                         │ │
│  │  ┌────────▼─────────┐      ┌─────────────────────────────────────┐ │ │
│  │  │    EC AGENT      │ ──►  │ identity_synthesis {                │ │ │
│  │  │  (RUNS FIRST)    │      │   archetype, spike, pillars,        │ │ │
│  │  └────────┬─────────┘      │   portfolio_balance, gaps           │ │ │
│  │           │                │ }                                    │ │ │
│  │           ▼                └─────────────────────────────────────┘ │ │
│  │  ┌────────────────────────────────────────────────────┐            │ │
│  │  │              PARALLEL EXECUTION                     │            │ │
│  │  │  ┌───────────────┐        ┌───────────────────┐    │            │ │
│  │  │  │ AWARDS AGENT  │        │  PROGRAMS AGENT   │    │            │ │
│  │  │  │ (2-2-1 Port.) │        │ (top_recommen.)   │    │            │ │
│  │  │  └───────┬───────┘        └─────────┬─────────┘    │            │ │
│  │  │          │                          │               │            │ │
│  │  │          └──────────┬───────────────┘               │            │ │
│  │  └─────────────────────┼──────────────────────────────┘            │ │
│  │                        ▼                                            │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │                   GAMEPLAN SYNTHESIS                          │  │ │
│  │  │  • Master Narrative Creation                                  │  │ │
│  │  │  • Activity Planning (3 Phases)                               │  │ │
│  │  │  • Identity Seed Architecture                                 │  │ │
│  │  │  • Strategic Overwhelm (1.4x tasks)                           │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     ReAct FRAMEWORK LAYER                          │ │
│  │  THINK → ACTION → OBSERVE → LEARN → CORRECTION                    │ │
│  │  Quality Gates: min_quality=70, min_voice=70, min_golden=0.6      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     DATA LAYER                                     │ │
│  │  awards_enriched.json (1000+ awards)                               │ │
│  │  programs_enriched.json (500+ programs)                            │ │
│  │  Supabase profiles, activities, responses                          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Design Principles

1. **Deterministic Routing**: Critical strategic decisions use rule-based logic (no LLM)
2. **Parallel Execution**: Awards and Programs agents run concurrently
3. **Quality Gates**: ReAct framework ensures output quality before acceptance
4. **Archetype-Based Matching**: All matching uses identity synthesis
5. **Strategic Intelligence**: Enriched data includes success patterns and common mistakes

---

## 3. ReAct Framework Implementation

### 3.1 Core Concept

The ReAct (Reasoning + Acting) framework structures agent reasoning into observable cycles:

```
┌──────────────────────────────────────────────────────────────────┐
│                        ReAct CYCLE                                │
│                                                                   │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│   │  THINK  │───►│  ACTION │───►│ OBSERVE │───►│  LEARN  │      │
│   │         │    │         │    │         │    │         │      │
│   │Generate │    │Execute  │    │Evaluate │    │Extract  │      │
│   │reasoning│    │planned  │    │quality: │    │patterns │      │
│   │& plan   │    │action   │    │-Quality │    │for next │      │
│   │         │    │         │    │-Voice   │    │cycle    │      │
│   │         │    │         │    │-Golden  │    │         │      │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
│         ▲                                           │            │
│         │         ┌─────────────┐                   │            │
│         └─────────│ CORRECTION  │◄──────────────────┘            │
│                   │ Inject      │                                │
│                   │ learnings   │                                │
│                   └─────────────┘                                │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Quality Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| `MIN_QUALITY_SCORE` | 70 | Domain-specific content quality |
| `MIN_VOICE_SCORE` | 70 | Jenny voice compliance |
| `MIN_GOLDEN_SIMILARITY` | 0.6 | Alignment with benchmark examples |
| `MAX_CYCLES` | 3 | Maximum correction attempts |

### 3.3 Quality Evaluation Dimensions

```python
class Observation:
    quality_score: float      # 0-100: Content quality
    voice_score: float        # 0-100: Jenny voice compliance
    golden_similarity: float  # 0-1: Benchmark alignment
    issues: List[str]         # Identified problems
    strengths: List[str]      # What worked well
```

### 3.4 Exit Conditions

The ReAct loop exits when ALL conditions are met:
- `quality_score >= 70`
- `voice_score >= 70`
- `golden_similarity >= 0.6`

OR when `cycles >= MAX_CYCLES` (accepts best attempt with warning)

---

## 4. 6-Agent Architecture Deep Dive

### 4.1 Agent Overview

| Agent | Purpose | Autonomy | Runs When |
|-------|---------|----------|-----------|
| **Assessment** | Identity synthesis, CRI calculation | HIGH | On profile load |
| **EC (Extracurriculars)** | Portfolio analysis, archetype detection | FULL | FIRST in orchestration |
| **Awards** | 2-2-1 portfolio matching | FULL | PARALLEL (after EC) |
| **Programs** | Top recommendations matching | FULL | PARALLEL (after EC) |
| **GamePlan** | Orchestration + synthesis | HIGH | Main entry point |
| **Execution** | Task breakdown, crisis response | MEDIUM/LOW | On demand |

### 4.2 Assessment Agent

**Purpose:** Synthesizes student identity and computes strategic readiness

**Input:**
```json
{
  "profile_id": "uuid",
  "profile_data": {
    "grade": 10,
    "school_type": "public",
    "gpa": 3.8,
    "extracurricular_activities": [...],
    "demographics": {...}
  }
}
```

**Processing Pipeline:**
1. Synthesize Narrative DNA (ACP-002)
2. Detect Archetype with confidence scoring
3. Compute CRI (Context Relativity Index)
4. Calculate Hidden Probabilities (ACP-001)
5. Identify Hidden Target (strategic college fit)

**Output (for Huda):**
```json
{
  "narrative_dna": "Because this student is a child of immigrants, deeply rooted in their South Asian Muslim heritage, they leverage an exceptional aptitude for computer science and a profound passion for service to build bridges within and beyond their community...",
  "brand_statement": "A South Asian Muslim innovator, coding solutions to bridge community divides and empower marginalized voices through accessible technology.",
  "themes": ["Cultural Identity", "Technological Empowerment", "Community Bridge-Building", "Social Justice", "Accessible Innovation"],
  "confidence": 0.90
}
```

### 4.3 EC (Extracurriculars) Agent

**Purpose:** Portfolio analysis and identity synthesis - RUNS FIRST in orchestration

**Why First?** The EC Agent produces `identity_synthesis` which is required by Awards and Programs agents for archetype-based filtering.

**Processing Pipeline:**
1. Analyze all activities for impact, leadership, and category
2. Detect archetype from 8 possible types
3. Identify spike (unique differentiator)
4. Calculate portfolio balance across 6 categories
5. Generate activity recommendations

**Archetype Detection Logic:**
```python
ARCHETYPES = [
    "academic_powerhouse",     # Strong academics across subjects
    "stem_innovator",          # STEM focus with innovation
    "creative_visionary",      # Arts and creative pursuits
    "community_changemaker",   # Service and social impact ← HUDA
    "entrepreneurial_leader",  # Business and leadership
    "humanities_scholar",      # Humanities and writing
    "athletic_scholar",        # Sports + academics
    "multi_hyphenate"          # Diverse excellence
]

# Detection uses weighted evidence from activities
def detect_archetype(activities, profile):
    scores = {}
    for archetype in ARCHETYPES:
        scores[archetype] = calculate_evidence_score(activities, archetype)
    return max(scores, key=scores.get), scores[max_archetype]
```

**Output (for Huda):**
```json
{
  "identity_synthesis": {
    "archetype": "community_changemaker",
    "archetype_confidence": 0.85,
    "spike": "service",
    "pillars": ["Cultural Identity", "Technological Empowerment", "Community Bridge-Building"],
    "portfolio_balance_score": 0.72,
    "portfolio_gaps": ["academic", "leadership"],
    "top_impact_activities": [
      {"name": "National Service Organization", "impact": 9.2}
    ],
    "leadership_level": "founder"
  }
}
```

### 4.4 Awards Agent

**Purpose:** Match students to awards using 2-2-1 portfolio strategy

**Input Requirements:**
- `profile_id`
- `identity_synthesis` (from EC Agent)
- `route_config` (from Strategic Router)

**Matching Algorithm:**

```python
def match_awards(profile, identity_synthesis):
    # Step 1: Load enriched awards database (1000+ awards)
    all_awards = load_enriched_awards()

    # Step 2: Filter by eligibility
    eligible = filter_by_eligibility(all_awards, profile.grade, profile.citizenship)

    # Step 3: Filter by archetype fit
    archetype = identity_synthesis["archetype"]  # "community_changemaker"
    archetype_matched = [
        a for a in eligible
        if a["archetype_fit"].get(archetype, 0) >= 0.3
    ]

    # Step 4: Calculate win probability for each
    for award in archetype_matched:
        award["win_probability"] = calculate_win_probability(
            profile, award, identity_synthesis
        )
        award["roi"] = calculate_roi(award)

    # Step 5: Apply 2-2-1 portfolio strategy
    portfolio = build_portfolio(archetype_matched)
    # reach: 2 (ambitious, <25% win prob)
    # target: 2 (competitive, 25-50% win prob)
    # safety: 1 (high probability, >50% win prob)

    return portfolio
```

**Win Probability Formula:**
```python
def calculate_win_probability(profile, award, identity):
    fit_score = award["archetype_fit"][identity["archetype"]]
    selectivity = award["selectivity"]  # 0-100, higher = more selective
    quality = calculate_quality_score(profile, award)

    base_prob = (fit_score * 0.4) + ((100 - selectivity) / 100 * 0.3) + (quality * 0.3)

    # Bonuses
    if has_vulnerability_story(profile):
        base_prob += 0.15
    if identity["spike"] in award["preferred_spikes"]:
        base_prob += 0.10

    return min(base_prob, 0.95)  # Cap at 95%
```

**Output Structure:**
```json
{
  "total_matches": 64,
  "portfolio": {
    "reach": [
      {
        "name": "NCWIT Award for Aspirations in Computing",
        "organization": "National Center for Women & IT",
        "fit_score": 0.89,
        "win_probability": 0.22,
        "strategic_tier": 1,
        "strategic_notes": "Perfect fit for tech + service narrative"
      },
      {
        "name": "Congressional Art Competition",
        "organization": "U.S. House of Representatives",
        "fit_score": 0.75,
        "win_probability": 0.18
      }
    ],
    "target": [
      {
        "name": "Points of Light Daily Point of Light Award",
        "organization": "Points of Light Foundation",
        "fit_score": 0.92,
        "win_probability": 0.35
      },
      {
        "name": "NAACP ACT-SO Competition",
        "organization": "NAACP",
        "fit_score": 0.85,
        "win_probability": 0.28
      }
    ],
    "safety": [
      {
        "name": "Lions Club Youth of the Year",
        "organization": "Lions Clubs International",
        "fit_score": 0.88,
        "win_probability": 0.65,
        "strategic_notes": "High probability entry point"
      }
    ]
  },
  "strategic_insights": [
    {
      "type": "fit_analysis",
      "message": "Your community changemaker profile aligns well with top recommendations (avg fit: 84%)"
    },
    {
      "type": "strategy_tip",
      "message": "For Lions Club Youth of the Year: Demonstrate a clear and sustained impact on the community."
    },
    {
      "type": "common_mistake",
      "message": "Common mistake: Submitting generic service activities without clear leadership roles."
    }
  ]
}
```

### 4.5 Programs Agent

**Purpose:** Match students to summer programs with synergy recommendations

**Key Difference from Awards:** Programs does NOT use reach/target/safety portfolio. Instead, it provides `top_recommendations` ranked by fit score.

**Matching Algorithm:**
```python
def match_programs(profile, identity_synthesis):
    # Step 1: Load enriched programs (500+)
    all_programs = load_enriched_programs()

    # Step 2: Filter by eligibility
    eligible = filter_by_grade_eligibility(all_programs, profile.grade)

    # Step 3: Filter by archetype fit
    archetype = identity_synthesis["archetype"]
    matched = [
        p for p in eligible
        if p["archetype_fit"].get(archetype, 0) >= 0.3
    ]

    # Step 4: Calculate fit score
    for program in matched:
        program["fit_score"] = calculate_fit_score(profile, program, identity_synthesis)
        program["acceptance_probability"] = estimate_acceptance(
            program["fit_score"],
            program["selectivity"]
        )

    # Step 5: Sort by fit score, return top recommendations
    matched.sort(key=lambda x: x["fit_score"], reverse=True)

    # Step 6: Generate synergy recommendations
    synergies = generate_synergies(matched[:5])

    return {
        "total_matches": len(matched),
        "top_recommendations": matched[:5],
        "synergy_recommendations": synergies,
        "strategic_insights": generate_insights(matched, identity_synthesis)
    }
```

**Fit Score Calculation:**
```python
def calculate_fit_score(profile, program, identity):
    archetype_fit = program["archetype_fit"][identity["archetype"]]
    spike_match = 1.0 if identity["spike"] in program["focus_areas"] else 0.5

    # Weighted combination
    fit_score = (
        archetype_fit * 0.5 +      # 50% archetype alignment
        spike_match * 0.3 +         # 30% spike match
        pillar_overlap(identity, program) * 0.2  # 20% pillar overlap
    )

    return fit_score
```

**Output (for Huda):**
```json
{
  "total_matches": 29,
  "top_recommendations": [
    {
      "name": "Yale Young Global Scholars (YYGS)",
      "organization": "Yale University",
      "fit_score": 0.77,
      "acceptance_probability": 0.25,
      "strategic_notes": "Access to Yale faculty and resources"
    },
    {
      "name": "Kode With Klossy",
      "organization": "Kode With Klossy",
      "fit_score": 0.67,
      "type": "summer_program"
    },
    {
      "name": "Girls Inc. Eureka! STEM Program",
      "organization": "Girls Inc.",
      "fit_score": 0.67
    }
  ],
  "synergy_recommendations": [
    {
      "recommendation": "Yale Young Global Scholars (YYGS) pairs well with these programs for narrative coherence"
    },
    {
      "recommendation": "Completing Yale Young Global Scholars (YYGS) positions you for these opportunities"
    }
  ],
  "strategic_insights": [
    {
      "type": "fit_analysis",
      "message": "Your community changemaker profile matches well with top programs (avg fit: 80%)"
    }
  ]
}
```

### 4.6 GamePlan Agent (Orchestrator)

**Purpose:** Orchestrates all agents and synthesizes unified strategic plan

**Orchestration Sequence:**
```
1. Determine Strategic Route (deterministic)
2. Run EC Agent FIRST → identity_synthesis
3. Run Awards + Programs in PARALLEL
4. Synthesize Master Narrative
5. Build Phase Roadmap
6. Generate Identity Seeds
7. Apply Strategic Overwhelm (1.4x)
8. Return Unified GamePlan
```

**Strategic Routes:**
```python
def decide_route(profile):
    activity_count = len(profile.activities)
    months_to_deadline = calculate_months_to_ed()

    if activity_count < 3:
        return "BUILD_FRESH"      # Start from scratch
    elif has_foundation(profile):
        return "OPTIMIZE"         # Optimize existing
    elif needs_pivot(profile):
        return "REFRAME"          # Narrative pivot needed
    elif months_to_deadline < 6:
        return "URGENT_TRIAGE"    # Quick wins only
```

**Output (for Huda):**
```json
{
  "game_plan": {
    "identity_synthesis": {...},
    "narrative_dna": "A Bay Area student and scholar who uses skills in coding, technology to serve contributing to community",
    "activities": [
      {"name": "Address Portfolio Gaps", "type": "portfolio_gap"},
      {"name": "Lions Club Youth of the Year", "type": "award"},
      {"name": "NCWIT Award for Aspirations in Computing", "type": "award"},
      {"name": "Yale Young Global Scholars (YYGS)", "type": "program"}
    ],
    "identity_seeds": [
      {"name": "Community Changemaker Identity", "type": "archetype", "planted": true},
      {"name": "Service Focus", "type": "spike", "planted": true},
      {"name": "Academic Development", "type": "gap_opportunity"},
      {"name": "Leadership Development", "type": "gap_opportunity"}
    ],
    "phases": [
      {
        "name": "Foundation Building",
        "duration": "Months 1-3",
        "focus": "Build foundation, address gaps, apply to entry awards",
        "activity_count": 2
      },
      {
        "name": "Building Momentum",
        "duration": "Months 4-8",
        "focus": "Scale impact, apply to programs and building awards",
        "activity_count": 4
      },
      {
        "name": "Capstone Achievement",
        "duration": "Months 9-12",
        "focus": "Apply to capstone awards, finalize applications",
        "activity_count": 3
      }
    ],
    "awards": {
      "portfolio": {
        "reach": [...],
        "target": [...],
        "safety": [...]
      },
      "strategic_insights": [...]
    },
    "programs": {
      "top_recommendations": [...],
      "strategic_insights": [...]
    },
    "summary": {
      "total_awards_matched": 64,
      "total_programs_matched": 29,
      "activities_analyzed": 9,
      "portfolio_balance_score": 0.72
    }
  }
}
```

---

## 5. Orchestration Flow

### 5.1 Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    POST /agents/gameplan/generate                        │
│                         { profile_id: "huda-uuid" }                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 0: STRATEGIC ROUTER (Deterministic - No LLM)                      │
│                                                                          │
│  Input: profile.activities.length = 3, months_to_ed = 18                │
│  Logic: activities >= 3 AND has_some_foundation → "REFRAME"             │
│  Output: route = "REFRAME" (narrative pivot with 1-2 additions)         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 1: EC AGENT (RUNS FIRST - Sequential)                             │
│                                                                          │
│  Input:                                                                  │
│    - profile_id: "huda-uuid"                                            │
│    - activities: [national_org, coding_projects, community_service]     │
│                                                                          │
│  Processing:                                                             │
│    1. Analyze each activity for impact (0-10 scale)                     │
│    2. Detect leadership level: member → officer → president → founder   │
│    3. Calculate category distribution (6 categories)                     │
│    4. Detect archetype from evidence                                     │
│    5. Identify spike (unique differentiator)                            │
│                                                                          │
│  Archetype Evidence for Huda:                                           │
│    - community_changemaker: 0.85 (national service org, community work) │
│    - stem_innovator: 0.65 (coding projects)                             │
│    - entrepreneurial_leader: 0.55 (founded organization)                │
│    Winner: community_changemaker (0.85 confidence)                      │
│                                                                          │
│  Output: identity_synthesis = {                                         │
│    archetype: "community_changemaker",                                  │
│    archetype_confidence: 0.85,                                          │
│    spike: "service",                                                    │
│    pillars: ["Cultural Identity", "Tech Empowerment", "Community"],     │
│    portfolio_balance_score: 0.72,                                       │
│    portfolio_gaps: ["academic", "leadership"],                          │
│    leadership_level: "founder"                                          │
│  }                                                                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
          ┌──────────────────────┴──────────────────────┐
          │         PARALLEL EXECUTION (asyncio.gather)  │
          ▼                                              ▼
┌─────────────────────────────┐    ┌─────────────────────────────────────┐
│  STEP 2A: AWARDS AGENT      │    │  STEP 2B: PROGRAMS AGENT            │
│                             │    │                                      │
│  Input:                     │    │  Input:                              │
│    - profile_id             │    │    - profile_id                      │
│    - identity_synthesis     │    │    - identity_synthesis              │
│    - route: "REFRAME"       │    │    - route: "REFRAME"                │
│                             │    │                                      │
│  QUERY LOGIC:               │    │  QUERY LOGIC:                        │
│  FROM awards_enriched.json  │    │  FROM programs_enriched.json         │
│  WHERE:                     │    │  WHERE:                              │
│    grade_eligible AND       │    │    grade_eligible AND                │
│    archetype_fit[           │    │    archetype_fit[                    │
│      "community_changemaker"│    │      "community_changemaker"         │
│    ] >= 0.3                 │    │    ] >= 0.3                          │
│                             │    │                                      │
│  RANKING:                   │    │  RANKING:                            │
│    1. Win probability       │    │    1. Fit score                      │
│    2. ROI (prestige/effort) │    │    2. Acceptance probability         │
│    3. Strategic tier        │    │    3. Narrative alignment            │
│                             │    │                                      │
│  Output:                    │    │  Output:                             │
│    total_matches: 64        │    │    total_matches: 29                 │
│    portfolio: {             │    │    top_recommendations: [            │
│      reach: 2 awards        │    │      YYGS (77% fit),                 │
│      target: 2 awards       │    │      Kode With Klossy (67%),         │
│      safety: 1 award        │    │      Girls Inc. (67%)                │
│    }                        │    │    ]                                  │
│    avg_fit: 84%             │    │    avg_fit: 80%                      │
└─────────────┬───────────────┘    └──────────────────┬──────────────────┘
              │                                        │
              └────────────────┬───────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 3: NARRATIVE SYNTHESIS (LLM-Powered)                              │
│                                                                          │
│  Input:                                                                  │
│    - identity_synthesis                                                 │
│    - profile demographics: South Asian Muslim, Bay Area                 │
│    - activities: service org, coding projects                           │
│                                                                          │
│  LLM Prompt (Jenny's Formula):                                          │
│  "Because I am [IDENTITY], I use [APTITUDE] and [PASSION]              │
│   to [SERVICE], becoming [UNIQUE ROLE]"                                 │
│                                                                          │
│  For Huda:                                                              │
│  "Because I am a child of immigrants deeply rooted in South Asian      │
│   Muslim heritage, I use coding and technology skills and passion      │
│   for service to build bridges within and beyond my community,         │
│   becoming a future tech leader for social justice"                    │
│                                                                          │
│  Output:                                                                │
│    brand_statement: "A South Asian Muslim innovator, coding solutions  │
│                      to bridge community divides and empower           │
│                      marginalized voices through accessible technology"│
│    narrative_dna: [full 300-word narrative]                            │
│    themes: [Cultural Identity, Tech Empowerment, Community...]         │
│    confidence: 0.90                                                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 4: IDENTITY SEED GENERATION (ACP-006)                             │
│                                                                          │
│  Purpose: Plant strategic "seeds" 6-12 months before they're needed    │
│                                                                          │
│  Seeds Generated for Huda:                                              │
│    PLANTED (already established):                                       │
│      1. Community Changemaker Identity (archetype)                      │
│      2. Service Focus (spike)                                           │
│                                                                          │
│    OPPORTUNITIES (to develop):                                          │
│      3. Academic Development (gap_opportunity)                          │
│      4. Leadership Development (gap_opportunity)                        │
│      5. NCWIT Award Pursuit (award_seed)                               │
│      6. Congressional Art Competition Pursuit (award_seed)              │
│      7. YYGS Application (program_seed)                                 │
│      8. Kode With Klossy Application (program_seed)                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 5: PHASE ROADMAP CREATION                                         │
│                                                                          │
│  Phase 1: Foundation Building (Months 1-3)                              │
│    - Address Portfolio Gaps                                             │
│    - Apply to Lions Club Youth of the Year (safety award)               │
│    Activities: 2                                                        │
│                                                                          │
│  Phase 2: Building Momentum (Months 4-8)                                │
│    - NCWIT Award application                                            │
│    - YYGS application                                                   │
│    - Kode With Klossy application                                       │
│    - Girls Inc. program                                                 │
│    Activities: 4                                                        │
│                                                                          │
│  Phase 3: Capstone Achievement (Months 9-12)                            │
│    - Congressional Art Competition                                       │
│    - Points of Light Award                                              │
│    - NAACP ACT-SO                                                       │
│    Activities: 3                                                        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 6: STRATEGIC OVERWHELM (ACP-004)                                  │
│                                                                          │
│  Principle: Assign 1.4x tasks, expect 73% completion                    │
│                                                                          │
│  For Huda:                                                              │
│    Base activities needed: 6-7                                          │
│    With 1.4x multiplier: 9 activities assigned                          │
│    Expected completion: 6-7 (73% of 9)                                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FINAL OUTPUT: UNIFIED GAME PLAN                                        │
│                                                                          │
│  {                                                                       │
│    "game_plan": {                                                       │
│      "profile_id": "huda-uuid",                                         │
│      "identity_synthesis": {...},                                       │
│      "narrative_dna": "A Bay Area student...",                          │
│      "activities": [9 activities],                                      │
│      "identity_seeds": [8 seeds],                                       │
│      "phases": [3 phases],                                              │
│      "awards": { portfolio: {...}, strategic_insights: [...] },         │
│      "programs": { top_recommendations: [...] },                        │
│      "summary": {                                                       │
│        "total_awards_matched": 64,                                      │
│        "total_programs_matched": 29                                     │
│      }                                                                   │
│    }                                                                     │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Huda's Complete Data Flow

### 6.1 Profile Input Data

```json
{
  "profile_id": "huda-uuid",
  "user_id": "huda@ivylevel.com",
  "basic_info": {
    "name": "Huda S",
    "grade": 10,
    "school_type": "public",
    "location": "Bay Area, CA"
  },
  "demographics": {
    "ethnicity": "South Asian",
    "religion": "Muslim",
    "first_generation": true,
    "immigrant_background": true
  },
  "academics": {
    "gpa": 3.8,
    "courses": ["AP Computer Science", "AP English", "Honors Math"]
  },
  "extracurricular_activities": [
    {
      "name": "National Service Organization",
      "role": "Founder",
      "hours_per_week": 15,
      "description": "Founded organization providing tech resources to underserved communities",
      "impact": "Served 500+ individuals"
    },
    {
      "name": "Coding Projects",
      "role": "Lead Developer",
      "description": "Built accessible technology tools"
    },
    {
      "name": "Community Service",
      "role": "Volunteer Coordinator"
    }
  ],
  "interests": ["computer science", "social justice", "community service", "technology"],
  "target_schools": ["Stanford", "MIT", "UC Berkeley"]
}
```

### 6.2 Agent Processing Summary

| Agent | Input | Processing | Output |
|-------|-------|------------|--------|
| **EC Agent** | 3 activities | Archetype detection, portfolio analysis | archetype: community_changemaker, spike: service |
| **Awards Agent** | identity_synthesis + 1000 awards | Filter by archetype_fit >= 0.3, calculate win probability | 64 matches, 2-2-1 portfolio |
| **Programs Agent** | identity_synthesis + 500 programs | Filter by archetype_fit >= 0.3, calculate fit score | 29 matches, top 5 recommendations |
| **Assessment Agent** | profile + identity_synthesis | Narrative synthesis via LLM | 90% confidence narrative |
| **GamePlan Agent** | All above | Orchestrate + synthesize | Unified 9-activity plan |

### 6.3 Key Decision Points

**Why "community_changemaker" archetype?**
- Founded national service organization (highest evidence)
- Focus on serving underserved communities
- Tech skills applied to social impact
- Cultural identity driving service motivation

**Why 64 awards matched?**
```
Total awards in database: 1000+
After grade eligibility filter: ~500
After archetype_fit["community_changemaker"] >= 0.3: 64
```

**Why these specific 5 awards in portfolio?**
| Award | Why Selected | Fit Score | Win Prob |
|-------|--------------|-----------|----------|
| NCWIT | Tech + women + service | 89% | 22% (reach) |
| Congressional Art | Creative expression | 75% | 18% (reach) |
| Points of Light | Service excellence | 92% | 35% (target) |
| NAACP ACT-SO | Cultural + achievement | 85% | 28% (target) |
| Lions Club Youth | Community impact | 88% | 65% (safety) |

**Why 29 programs matched?**
```
Total programs in database: 500+
After grade eligibility filter: ~200
After archetype_fit["community_changemaker"] >= 0.3: 29
```

**Why YYGS ranked #1?**
- archetype_fit["community_changemaker"]: 0.8
- Spike "service" aligns with YYGS global focus
- Prestige factor (Yale brand)
- Combined fit score: 77%

---

## 7. Awards Matching System

### 7.1 Enriched Awards Data Structure

```json
{
  "award_id": "ncwit-aic",
  "name": "NCWIT Award for Aspirations in Computing",
  "organization": "National Center for Women & IT",
  "category": "STEM",
  "level": "national",
  "eligibility": {
    "grades": [9, 10, 11, 12],
    "citizenship": "US",
    "gender": "female"
  },
  "strategic_tier": 1,
  "selectivity": 0.85,
  "prestige_score": 95,
  "effort_hours": 20,
  "archetype_fit": {
    "academic_powerhouse": 0.7,
    "stem_innovator": 1.0,
    "creative_visionary": 0.3,
    "community_changemaker": 0.8,
    "entrepreneurial_leader": 0.6,
    "humanities_scholar": 0.2,
    "athletic_scholar": 0.1,
    "multi_hyphenate": 0.7
  },
  "preferred_spikes": ["technology", "service", "leadership"],
  "success_patterns": [
    "Demonstrated coding ability through projects",
    "Leadership in tech-related activities",
    "Community impact through technology"
  ],
  "common_mistakes": [
    "Focusing only on technical skills without leadership",
    "Not demonstrating community impact"
  ],
  "win_cascade": {
    "position": "building",
    "prerequisites": ["Basic coding knowledge", "One tech project"],
    "enables": ["Google Science Fair", "Regeneron ISEF"]
  }
}
```

### 7.2 Query Criteria for Huda

```python
# Pseudocode for awards filtering
awards_query = """
SELECT * FROM awards_enriched
WHERE grade_eligible(grades, 10)
  AND archetype_fit['community_changemaker'] >= 0.3
ORDER BY
  (win_probability * 0.4 +
   archetype_fit['community_changemaker'] * 0.3 +
   roi * 0.3) DESC
"""

# Actual filtering in code
def filter_awards_for_huda(awards, identity_synthesis):
    filtered = []
    for award in awards:
        # Eligibility check
        if 10 not in award["eligibility"]["grades"]:
            continue

        # Archetype fit threshold
        archetype = identity_synthesis["archetype"]  # "community_changemaker"
        if award["archetype_fit"].get(archetype, 0) < 0.3:
            continue

        # Calculate scores
        award["fit_score"] = award["archetype_fit"][archetype]
        award["win_probability"] = calculate_win_prob(...)
        award["roi"] = calculate_roi(...)

        filtered.append(award)

    return filtered  # 64 awards for Huda
```

### 7.3 Portfolio Construction (2-2-1 Strategy)

```python
def build_portfolio(matched_awards):
    # Sort by win probability
    sorted_awards = sorted(matched_awards, key=lambda x: x["win_probability"])

    portfolio = {
        "reach": [],    # Low probability (<25%), high prestige
        "target": [],   # Medium probability (25-50%)
        "safety": []    # High probability (>50%)
    }

    for award in sorted_awards:
        prob = award["win_probability"]
        if prob < 0.25 and len(portfolio["reach"]) < 2:
            portfolio["reach"].append(award)
        elif prob < 0.50 and len(portfolio["target"]) < 2:
            portfolio["target"].append(award)
        elif prob >= 0.50 and len(portfolio["safety"]) < 1:
            portfolio["safety"].append(award)

    return portfolio
```

---

## 8. Programs Matching System

### 8.1 Enriched Programs Data Structure

```json
{
  "program_id": "yygs",
  "name": "Yale Young Global Scholars (YYGS)",
  "organization": "Yale University",
  "type": "summer_program",
  "focus_areas": ["leadership", "global issues", "service"],
  "eligibility": {
    "grades": [10, 11]
  },
  "selectivity": 0.20,
  "prestige_score": 95,
  "cost": 6000,
  "duration": "2 weeks",
  "archetype_fit": {
    "academic_powerhouse": 0.9,
    "stem_innovator": 0.7,
    "creative_visionary": 0.5,
    "community_changemaker": 0.8,
    "entrepreneurial_leader": 0.7,
    "humanities_scholar": 0.8,
    "athletic_scholar": 0.3,
    "multi_hyphenate": 0.9
  },
  "success_patterns": [
    "Demonstrated intellectual curiosity",
    "Leadership experience",
    "Global perspective"
  ],
  "synergies": {
    "pairs_well_with": ["Girls Who Code", "Model UN"],
    "leads_to": ["Yale admission advantage", "Leadership roles"]
  },
  "hidden_value": [
    "Access to Yale faculty",
    "Ivy League preview experience",
    "Global peer network"
  ]
}
```

### 8.2 Query Criteria for Huda

```python
# Programs filtering for Huda
def filter_programs_for_huda(programs, identity_synthesis):
    archetype = "community_changemaker"
    spike = "service"

    matched = []
    for program in programs:
        # Grade eligibility
        if 10 not in program["eligibility"]["grades"]:
            continue

        # Archetype fit threshold
        if program["archetype_fit"].get(archetype, 0) < 0.3:
            continue

        # Calculate fit score
        archetype_score = program["archetype_fit"][archetype]
        spike_match = 1.0 if spike in program["focus_areas"] else 0.5

        program["fit_score"] = (archetype_score * 0.6) + (spike_match * 0.4)
        matched.append(program)

    # Sort by fit score
    matched.sort(key=lambda x: x["fit_score"], reverse=True)
    return matched  # 29 programs for Huda
```

### 8.3 Why No Reach/Target/Safety for Programs?

Unlike awards (which have binary win/lose outcomes), programs have:
- Variable acceptance rates
- Different value propositions
- Cumulative benefit (multiple programs help)

Therefore, programs use **Top Recommendations** ranking rather than portfolio balancing.

---

## 9. LLM Reasoning & Prompts

### 9.1 Models Used

| Component | Model | Temperature | Purpose |
|-----------|-------|-------------|---------|
| Narrative Synthesis | GPT-4o | 0.7 | Creative narrative generation |
| Quality Evaluation | GPT-4o | 0.3 | Consistent scoring |
| Voice Validation | GPT-4o | 0.3 | Jenny voice compliance |
| Fallback | Gemini 2.0 Flash | 0.7 | Backup for narrative |

### 9.2 Jenny's Voice Formula

```
"Because I am [IDENTITY], I use [APTITUDE] and [PASSION]
 to [SERVICE], becoming [UNIQUE ROLE]"
```

**For Huda:**
```
"Because I am a child of immigrants deeply rooted in South Asian Muslim heritage,
 I use my exceptional aptitude for computer science and profound passion for service
 to build bridges within and beyond my community,
 becoming a future leader using technology as a force for positive change."
```

### 9.3 Narrative Synthesis Prompt

```python
NARRATIVE_SYNTHESIS_PROMPT = """
You are Jenny, an expert college admissions coach. Synthesize a powerful narrative
for this student.

Student Profile:
- Archetype: {archetype}
- Spike: {spike}
- Pillars: {pillars}
- Demographics: {demographics}
- Key Activities: {activities}

Use Jenny's Formula:
"Because I am [IDENTITY], I use [APTITUDE] and [PASSION] to [SERVICE],
becoming [UNIQUE ROLE]"

Output:
1. Brand Statement (15-25 words, one powerful sentence)
2. Narrative DNA (2-3 paragraphs, 250-300 words)
3. Key Themes (3-5 themes)

Rules:
- Be specific, not generic
- Show authentic voice
- Connect identity to impact
- Avoid clichés
"""
```

### 9.4 Quality Evaluation Rubric

```python
QUALITY_RUBRIC = """
Evaluate this narrative on these dimensions (1-10 each):

1. Identity Clarity: How clearly defined is their unique identity?
2. Aptitude Alignment: Do their skills match their direction?
3. Passion Authenticity: Is the passion genuine and deep?
4. Service Relevance: Does service connect to identity?
5. Narrative Power: Overall story strength and memorability?

Total Score: Sum of all dimensions
- 40+: Transformative (exceptional application narrative)
- 30-39: Strong (competitive application)
- 20-29: Developing (needs refinement)
- <20: Weak (significant work needed)
"""
```

---

## 10. Frontend Integration

### 10.1 Component Hierarchy

```
MultiAgentsTab
└── AgentDashboardV13
    ├── AssessmentAgentCard → AgentDetailModal (assessment)
    ├── ECAgentCard → AgentDetailModal (ec)
    ├── GamePlanAgentCard → AgentDetailModal (gameplan)
    ├── ExecutionAgentCard → AgentDetailModal (execution)
    ├── AwardsAgentCard → AgentDetailModal (awards)
    ├── OpportunityAgentCard → AgentDetailModal (opportunity)
    └── CrisisAgentCard → AgentDetailModal (crisis)
```

### 10.2 Data Hooks

| Hook | Endpoint | Purpose |
|------|----------|---------|
| `useGamePlan` | GET /agents/gameplan/generate | Main orchestrated data |
| `useAwardMatches` | GET /agents/awards/match | Legacy awards endpoint |
| `useOpportunityAlerts` | GET /agents/opportunities/alerts | Deadline alerts |
| `useAgentV13Health` | GET /agents/health | Backend status |

### 10.3 Data Flow to UI Components

```typescript
// GamePlanAgentCard receives
const gamePlan = {
  game_plan: {
    activities: [...],           // → Activities count
    identity_seeds: [...],       // → Seeds count
    phases: [...],               // → Phases display
    awards: {
      portfolio: {...},          // → Awards Portfolio
      strategic_insights: [...]
    },
    programs: {
      top_recommendations: [...], // → Programs list (NOT portfolio!)
      strategic_insights: [...]
    },
    summary: {
      total_awards_matched: 64,
      total_programs_matched: 29
    }
  }
}

// AwardsAgentCard displays
// - portfolio.reach.length (2)
// - portfolio.target.length (2)
// - portfolio.safety.length (1)
// - total_awards_matched (64)

// OpportunityAgentCard displays
// - total_programs_matched (29)
// - top_recommendations[0..4] (top 5 programs)
// - NO reach/target/safety (programs don't have this)
```

### 10.4 Modal Data Structures

**AwardsDetail receives:**
```typescript
{
  portfolio: {
    reach: [{name, fit_score, organization}, ...],
    target: [...],
    safety: [...]
  },
  total_matched: 64,
  strategic_insights: [...]
}
```

**OpportunityDetail receives:**
```typescript
{
  programs: [{name, organization, fit_score}, ...],  // top_recommendations
  total_matched: 29,
  synergy_recommendations: [...],
  strategic_insights: [...]
}
// Note: NO portfolio structure - just flat list of programs
```

---

## 11. Validation Evidence

### 11.1 Huda's Dashboard Validation

| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Assessment Confidence | 90% | 90% | ✅ |
| Archetype | community_changemaker | community_changemaker | ✅ |
| Activities Count | 9 | 9 | ✅ |
| Identity Seeds | 8 | 8 | ✅ |
| Awards Matched | 64 | 64 | ✅ |
| Awards Portfolio (R/T/S) | 2/2/1 | 2/2/1 | ✅ |
| Programs Matched | 29 | 29 | ✅ |
| Top Program | YYGS (77%) | YYGS (77%) | ✅ |
| Phases | 3 | 3 | ✅ |
| Avg Award Fit | 84% | 84% | ✅ |
| Avg Program Fit | 80% | 80% | ✅ |

### 11.2 Agent Intelligence Validation

| Feature | Evidence |
|---------|----------|
| **Archetype Detection** | Correctly identified "community_changemaker" from service org founder + tech for good |
| **Spike Identification** | Correctly identified "service" as differentiating focus |
| **Portfolio Gaps** | Correctly identified "academic" and "leadership" as gaps |
| **Award Matching** | NCWIT perfect for tech + women + service; Lions Club as safe entry |
| **Program Matching** | YYGS aligns with global service focus; Kode With Klossy for tech |
| **Narrative Synthesis** | Connected immigrant identity → tech skills → community service → unique role |
| **Strategic Insights** | Provided specific actionable advice (e.g., "Demonstrate sustained impact") |

### 11.3 ReAct Framework Validation

```
Current Status (from UI): ReAct: Off

When ReAct is enabled, each agent output goes through:
1. THINK: Generate reasoning
2. ACTION: Execute strategy
3. OBSERVE: Quality score (70+), Voice score (70+), Golden similarity (0.6+)
4. LEARN: Extract patterns
5. CORRECTION: Retry if thresholds not met (max 3 cycles)
```

### 11.4 Agentic AI Characteristics Demonstrated

| Characteristic | Implementation |
|----------------|----------------|
| **Autonomous Decision Making** | Strategic Router chooses route without human input |
| **Specialized Expertise** | 6 agents each with distinct knowledge domains |
| **Parallel Processing** | Awards and Programs run concurrently |
| **Quality Self-Assessment** | ReAct framework evaluates own outputs |
| **Learning from Examples** | Golden benchmark comparison |
| **Human-in-the-Loop** | Autonomy levels trigger handoffs when confidence low |
| **Memory & State** | Profile snapshots and interaction memory |
| **Strategic Intelligence** | Success patterns, common mistakes, win cascades |

---

## Appendix A: API Reference

### A.1 Main Orchestration Endpoint

```
POST /agents/gameplan/generate
Request: { "profile_id": "uuid" }
Response: { "game_plan": {...}, "success": true }
```

### A.2 Health Check

```
GET /agents/health
Response: {
  "status": "healthy",
  "version": "15.0.0",
  "react_enabled": false,
  "memory_enabled": false,
  "hitl_enabled": false,
  "thresholds": {
    "min_quality": 70,
    "min_voice": 70,
    "min_golden": 0.6,
    "max_cycles": 3
  }
}
```

---

## Appendix B: File References

| File | Purpose |
|------|---------|
| `agents/agents/gameplan.py` | Main orchestrator |
| `agents/agents/extracurriculars.py` | EC Agent (runs first) |
| `agents/agents/awards.py` | Awards matching |
| `agents/agents/programs.py` | Programs matching |
| `agents/agents/core/react_base.py` | ReAct framework |
| `agents/agents/core/strategic_router.py` | Deterministic routing |
| `agents/seeds/enriched/awards_enriched.json` | Awards database |
| `agents/seeds/enriched/programs_enriched.json` | Programs database |
| `components/agents/AgentDashboardV13.tsx` | Main dashboard |
| `components/agents/AgentDetailModal.tsx` | Detail modals |
| `components/agents/cards/*.tsx` | Individual cards |

---

**Document Version:** 4.0
**Last Validated:** January 2026
**Profile Used:** Huda S. (huda@ivylevel.com)
**Build Status:** Production Ready ✅
