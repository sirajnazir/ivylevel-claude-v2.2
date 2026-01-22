# Multi-Agent Architecture Specification v5.0

> **Document Version**: 5.0
> **Last Updated**: 2026-01-16
> **Status**: Production Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Agent Roles & Responsibilities](#3-agent-roles--responsibilities)
4. [Multi-Agent Orchestration Flow](#4-multi-agent-orchestration-flow)
5. [ReAct Framework Implementation](#5-react-framework-implementation)
6. [Data Flow Specification](#6-data-flow-specification)
7. [Tool Registry & Execution](#7-tool-registry--execution)
8. [Quality Validation System](#8-quality-validation-system)
9. [Jenny's 4 Pillars Framework](#9-jennys-4-pillars-framework)
10. [Frontend Visualization Integration](#10-frontend-visualization-integration)
11. [API Contracts](#11-api-contracts)
12. [Error Handling & Fallbacks](#12-error-handling--fallbacks)
13. [Configuration Reference](#13-configuration-reference)

---

## 1. Executive Summary

### 1.1 System Purpose

IvyQuest's Multi-Agent System is a sophisticated AI orchestration platform that generates personalized college admissions strategies. The system employs multiple specialized agents that collaborate through a hierarchical orchestration pattern to produce comprehensive, narrative-driven recommendations.

### 1.2 Key Architectural Principles

| Principle | Description |
|-----------|-------------|
| **Sequential-First, Then Parallel** | EC Agent runs FIRST (creates identity), then Awards+Programs run in PARALLEL |
| **Data Dependency Enforcement** | Awards/Programs RECEIVE archetype from EC, never generate their own |
| **ReAct Self-Correction** | Each agent runs THINK→ACT→OBSERVE→LEARN cycles for quality improvement |
| **Jenny's 4 Pillars** | All identity synthesis follows Identity+Aptitude+Passion+Service formula |
| **Quality Gates** | 70/70/0.6 thresholds (quality/voice/golden) before output acceptance |

### 1.3 Agent Inventory

| Agent | Role | Runs Own ReAct? | Input Source |
|-------|------|-----------------|--------------|
| **GamePlan Orchestrator** | Coordinates all agents, synthesizes final output | Yes (outer loop) | Profile from database |
| **EC Agent** | Creates identity synthesis (archetype, spike, pillars) | Yes (inner loop) | Profile activities |
| **Awards Agent** | Matches awards to archetype | Yes (inner loop) | Identity from EC |
| **Programs Agent** | Matches programs to archetype | Yes (inner loop) | Identity from EC |

---

## 2. Architecture Overview

### 2.1 System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ ECAgentCard │  │AwardsAgent  │  │ Programs    │  │ GamePlan    │        │
│  │             │  │    Card     │  │  AgentCard  │  │  AgentCard  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┴────────────────┴────────────────┘               │
│                                   │                                        │
│                    ┌──────────────┴──────────────┐                         │
│                    │    useGamePlan() Hook       │                         │
│                    │  (Returns _react_by_agent)  │                         │
│                    └──────────────┬──────────────┘                         │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │ API: /api/agents/gameplan/generate
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    GamePlan Orchestrator                            │   │
│  │                  (ReAct Outer Loop: 1-3 cycles)                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                     ORCHESTRATION FLOW                       │   │   │
│  │  │                                                              │   │   │
│  │  │   Step 1: Load Profile from Supabase                        │   │   │
│  │  │                     │                                        │   │   │
│  │  │                     ▼                                        │   │   │
│  │  │   Step 2: EC Agent (SEQUENTIAL - runs FIRST)                │   │   │
│  │  │           ┌─────────────────────────────┐                   │   │   │
│  │  │           │  ReAct Loop (1-3 cycles)    │                   │   │   │
│  │  │           │  THINK → ACT → OBSERVE →    │                   │   │   │
│  │  │           │  LEARN → (repeat if needed) │                   │   │   │
│  │  │           └─────────────┬───────────────┘                   │   │   │
│  │  │                         │                                    │   │   │
│  │  │           Output: identity_synthesis                        │   │   │
│  │  │           {archetype, spike, pillars, confidence}           │   │   │
│  │  │                         │                                    │   │   │
│  │  │                         ▼                                    │   │   │
│  │  │   Step 3: Awards + Programs (PARALLEL)                      │   │   │
│  │  │           ┌───────────────────┬───────────────────┐         │   │   │
│  │  │           │                   │                   │         │   │   │
│  │  │           ▼                   ▼                   │         │   │   │
│  │  │   ┌───────────────┐   ┌───────────────┐          │         │   │   │
│  │  │   │ Awards Agent  │   │Programs Agent │          │         │   │   │
│  │  │   │ ReAct 1-3     │   │ ReAct 1-3     │          │         │   │   │
│  │  │   │ cycles        │   │ cycles        │          │         │   │   │
│  │  │   └───────┬───────┘   └───────┬───────┘          │         │   │   │
│  │  │           │                   │                   │         │   │   │
│  │  │           ▼                   ▼                   │         │   │   │
│  │  │   portfolio:          top_recommendations:        │         │   │   │
│  │  │   reach/target/safety programs, alerts           │         │   │   │
│  │  │           │                   │                   │         │   │   │
│  │  │           └─────────┬─────────┘                   │         │   │   │
│  │  │                     │                              │         │   │   │
│  │  │                     ▼                              │         │   │   │
│  │  │   Step 4: Narrative Synthesis                     │         │   │   │
│  │  │           Weaves all outputs into master story    │         │   │   │
│  │  │                                                    │         │   │   │
│  │  └────────────────────────────────────────────────────┘         │   │
│  │                                                                  │   │
│  │  Output: GamePlanResult with _react_by_agent                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `/agents/agents/gameplan.py` | GamePlan Orchestrator - coordinates all agents |
| `/agents/agents/extracurriculars.py` | EC Agent - identity synthesis |
| `/agents/agents/awards.py` | Awards Agent - award matching |
| `/agents/agents/programs.py` | Programs Agent - program matching |
| `/agents/agents/core/react_wrapper.py` | ReAct framework implementation |
| `/agents/agents/core/agentic_reasoner.py` | THINK/LEARN phase logic |
| `/agents/agents/core/agentic_tools.py` | Tool registry and execution |
| `/agents/agents/narrative_synthesis.py` | Jenny's Formula narrative generation |

---

## 3. Agent Roles & Responsibilities

### 3.1 EC Agent (Extracurriculars)

**Role**: DIAGNOSTIC + GENERATIVE

**Responsibilities**:
1. Analyze student activities to classify archetype
2. Generate unique spike (differentiator)
3. Extract thematic pillars (3-5 main areas)
4. Create identity synthesis using Jenny's 4 Pillars

**Tools Used**:
- `archetype_classifier` - Classifies into 8 archetypes
- `spike_generator` - Generates specific spike candidates
- `theme_extractor` - Extracts dominant themes and pillars

**Output Schema**:
```typescript
interface IdentitySynthesis {
  archetype: string;              // e.g., "stem_innovator"
  archetype_confidence: number;   // 0.0 - 1.0
  spike: string;                  // Specific differentiator
  spike_confidence: number;       // 0.0 - 1.0
  pillars: string[];             // 3-5 thematic areas
  portfolio_balance_score: number;
}
```

**ReAct Cycle Message Example**:
```
"EC Agent analyzing 8 activities using Jenny's 4 Pillars framework.
Detected signals in 3/4 pillars (Identity, Aptitude, Passion, Service).
Running diagnostic tools: classify archetype, generate spike, extract thematic pillars.
Classified archetype: stem_innovator (78% confidence).
Generated spike: 'Building AI-powered coding education for underserved K-12...' (82% specificity).
Extracted pillars: STEM, Education, Social Impact."
```

### 3.2 Awards Agent

**Role**: MATCHING ONLY

**Responsibilities**:
1. RECEIVE archetype and spike from EC Agent (never generate own)
2. Search awards database for archetype-aligned matches
3. Build reach/target/safety portfolio (2-2-1 balance)
4. Generate strategic insights

**Tools Used**:
- `awards_db_search` - Search awards database
- `golden_benchmark` - Compare portfolio quality

**Input Requirements**:
- `archetype` - FROM EC Agent
- `spike` - FROM EC Agent
- `pillars` - FROM EC Agent

**Output Schema**:
```typescript
interface AwardsOutput {
  portfolio: {
    reach: AwardMatch[];   // 2 high-selectivity awards
    target: AwardMatch[];  // 2 medium-selectivity awards
    safety: AwardMatch[];  // 1 accessible award
  };
  top_recommendations: AwardMatch[];
  strategic_insights: string[];
}
```

**ReAct Cycle Message Example**:
```
"Awards Agent received archetype 'stem_innovator' from EC Agent.
Searching award database for matches aligned with spike: 'Building AI-powered coding...'.
Building reach/target/safety portfolio.
Found 12 potential award matches.
Portfolio quality score: 85%."
```

### 3.3 Programs Agent

**Role**: MATCHING ONLY

**Responsibilities**:
1. RECEIVE archetype and spike from EC Agent (never generate own)
2. Search programs database for archetype-aligned matches
3. Apply student constraints (budget, location, duration)
4. Generate timeline and synergy recommendations

**Tools Used**:
- `programs_db_search` - Search programs database
- `golden_benchmark` - Compare recommendations quality

**Input Requirements**:
- `archetype` - FROM EC Agent
- `spike` - FROM EC Agent
- `grade` - Student grade level
- `constraints` - Budget, location, duration preferences

**Output Schema**:
```typescript
interface ProgramsOutput {
  top_recommendations: ProgramMatch[];
  advance_alerts: ProgramAlert[];
  synergy_recommendations: SynergyRec[];
  strategic_insights: string[];
  timeline: TimelineItem[];
}
```

**ReAct Cycle Message Example**:
```
"Programs Agent received archetype 'stem_innovator' from EC Agent.
Searching program database for grade 11 student.
Matching summer programs, internships, and research opportunities.
Applying constraints: ['budget', 'location'].
Found 8 potential program matches.
Portfolio quality score: 82%."
```

### 3.4 GamePlan Orchestrator

**Role**: COORDINATION + SYNTHESIS

**Responsibilities**:
1. Load profile from database
2. Orchestrate sub-agents in correct order (EC first, then parallel)
3. Collect and merge all agent outputs
4. Synthesize unified narrative
5. Build final GamePlanResult with `_react_by_agent` metadata

**Output Schema**:
```typescript
interface GamePlanResult {
  success: boolean;
  game_plan: {
    profile_id: string;
    narrative_dna: string;
    identity_synthesis: IdentitySynthesis;
    activities: Activity[];
    awards: AwardsOutput;
    programs: ProgramsOutput;
    phases: Phase[];
    summary: Summary;
    strategic_insights: string[];
    _react?: ReactMetadata;
  };
  _react_by_agent?: {
    ec?: ReactMetadata;
    awards?: ReactMetadata;
    programs?: ReactMetadata;
  };
}
```

**ReAct Cycle Message Example**:
```
"GamePlan Orchestrator synthesizing outputs from all agents.
Weaving EC identity, Awards portfolio, and Programs recommendations
into unified strategic narrative.
Overall synthesis quality: 78%."
```

---

## 4. Multi-Agent Orchestration Flow

### 4.1 Execution Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│                    GAMEPLAN ORCHESTRATION                       │
│                                                                 │
│  Time ──────────────────────────────────────────────────────►  │
│                                                                 │
│  T0        T1           T2                 T3          T4      │
│  │         │            │                  │           │       │
│  │ Load    │ EC Agent   │ Awards Agent ────┤           │       │
│  │ Profile │ (FIRST)    │ (PARALLEL)       │           │       │
│  │         │            │                  │           │       │
│  ▼         ▼            │ Programs Agent ──┤           ▼       │
│  ┌───┐    ┌───────┐     │ (PARALLEL)       │        ┌───────┐  │
│  │DB │────│EC     │────►│                  │───────►│Synth  │  │
│  │   │    │Agent  │     │                  │        │esize  │  │
│  └───┘    └───────┘     └──────────────────┘        └───────┘  │
│                                                                 │
│  Duration:  ~200ms      ~1-3s each                   ~500ms    │
│             (db)        (with ReAct)                 (merge)   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Dependencies

```
Profile (Supabase)
    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│                      EC AGENT                                 │
│                                                               │
│  Input:                      Output:                          │
│  - activities[]              - archetype                      │
│  - interests[]               - archetype_confidence           │
│  - academics{}               - spike                          │
│  - passion                   - spike_confidence               │
│  - background                - pillars[]                      │
│                              - portfolio_balance_score        │
└───────────────────────────────┬───────────────────────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
┌────────────────────────────┐  ┌────────────────────────────┐
│       AWARDS AGENT         │  │      PROGRAMS AGENT        │
│                            │  │                            │
│  Input:                    │  │  Input:                    │
│  - archetype (FROM EC)     │  │  - archetype (FROM EC)     │
│  - spike (FROM EC)         │  │  - spike (FROM EC)         │
│  - pillars (FROM EC)       │  │  - pillars (FROM EC)       │
│                            │  │  - grade                   │
│  Output:                   │  │  - constraints             │
│  - portfolio               │  │                            │
│  - top_recommendations     │  │  Output:                   │
│  - strategic_insights      │  │  - top_recommendations     │
│                            │  │  - advance_alerts          │
└────────────────────────────┘  └────────────────────────────┘
```

### 4.3 Orchestration Code Flow

```python
# In gameplan.py (simplified)

async def process(self, profile_id: str) -> GamePlanResult:
    # Step 1: Load profile
    profile = await get_profile_with_assessment(profile_id)

    # Step 2: Run EC Agent FIRST (sequential, blocking)
    ec_result = await self.ec_agent.process(profile_id, profile_data=profile)
    identity_synthesis = ec_result.get("identity_synthesis", {})

    # Step 3: Inject EC outputs into profile for downstream agents
    enriched_profile = {
        **profile,
        "archetype": identity_synthesis.get("archetype"),
        "spike": identity_synthesis.get("spike"),
        "pillars": identity_synthesis.get("pillars", []),
    }

    # Step 4: Run Awards + Programs in PARALLEL (they don't depend on each other)
    awards_task = self.awards_agent.process(profile_id, profile_data=enriched_profile)
    programs_task = self.programs_agent.process(profile_id, profile_data=enriched_profile)

    awards_result, programs_result = await asyncio.gather(awards_task, programs_task)

    # Step 5: Synthesize and return
    return self._build_game_plan(
        profile=profile,
        identity_synthesis=identity_synthesis,
        awards=awards_result,
        programs=programs_result,
    )
```

---

## 5. ReAct Framework Implementation

### 5.1 ReAct Cycle Overview

Each agent wrapped with ReAct executes a self-correction loop:

```
┌─────────────────────────────────────────────────────────────────┐
│                       ReAct LOOP                                │
│                                                                 │
│                    ┌──────────────┐                            │
│                    │    START     │                            │
│                    └──────┬───────┘                            │
│                           │                                    │
│                           ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    CYCLE N                               │  │
│  │                                                          │  │
│  │   ┌────────┐      ┌────────┐      ┌─────────┐          │  │
│  │   │ THINK  │ ───► │  ACT   │ ───► │ OBSERVE │          │  │
│  │   │        │      │        │      │         │          │  │
│  │   │ Analyze│      │Execute │      │Validate │          │  │
│  │   │ profile│      │agent   │      │ output  │          │  │
│  │   │ gaps   │      │process │      │ quality │          │  │
│  │   └────────┘      └────────┘      └────┬────┘          │  │
│  │                                        │               │  │
│  │                          ┌─────────────┴─────────────┐ │  │
│  │                          │                           │ │  │
│  │                          ▼                           ▼ │  │
│  │                    ┌──────────┐               ┌────────┐│  │
│  │                    │  LEARN   │               │ PASSED │││  │
│  │                    │          │               │        │││  │
│  │                    │Generate  │               │Return  │││  │
│  │                    │ hints    │               │ output │││  │
│  │                    └────┬─────┘               └────────┘│  │
│  │                         │                               │  │
│  └─────────────────────────┼───────────────────────────────┘  │
│                            │                                   │
│                            │ (if quality < threshold          │
│                            │  AND cycle < max_cycles)         │
│                            │                                   │
│                            ▼                                   │
│                    ┌──────────────┐                            │
│                    │ NEXT CYCLE   │                            │
│                    └──────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Phase Details

#### THINK Phase

**Purpose**: Analyze profile, identify gaps, plan actions

**File**: `/agents/agents/core/agentic_reasoner.py`

**Agent-Specific Behavior**:

| Agent | THINK Focus | Tools Selected |
|-------|-------------|----------------|
| EC Agent | Analyze activities, detect 4 Pillars | archetype_classifier, spike_generator, theme_extractor |
| Awards Agent | Review archetype fit, check portfolio balance | awards_db_search, golden_benchmark |
| Programs Agent | Review archetype fit, check constraints | programs_db_search, golden_benchmark |
| GamePlan | Validate synthesis coherence | golden_benchmark |

**Output Structure**:
```typescript
interface ThinkPhaseData {
  reasoning: string;           // Human-readable reasoning text
  planned_actions: string[];   // Tools to execute
  focus_areas: string[];       // Priority areas
  gap_analysis: {
    critical: string[];        // Must-fix issues
    moderate: string[];        // Should-fix issues
    minor: string[];           // Nice-to-fix issues
  };
  tools_selected: string[];    // Actual tools to run
  benchmark_targets: Record<string, number>;
  confidence: number;          // 0.0 - 1.0
}
```

#### ACT Phase

**Purpose**: Execute agent's process() method with hints

**File**: `/agents/agents/core/react_wrapper.py`

**Behavior**:
1. Inject `_react_feedback` into kwargs with hints from THINK
2. Call `agent.process(profile_id, **kwargs)`
3. Track execution duration
4. Capture output

**Output Structure**:
```typescript
interface ActPhaseData {
  action: string;              // "Executing {AgentName}.process()"
  tools_executed: Array<{
    name: string;
    duration_ms: number;
    success: boolean;
  }>;
  hints_applied: number;
  input_summary: Record<string, unknown>;
  output_summary: Record<string, unknown>;
  duration_ms: number;
}
```

#### OBSERVE Phase

**Purpose**: Validate output quality against thresholds

**Quality Dimensions**:

| Dimension | Threshold | Weight | Source |
|-----------|-----------|--------|--------|
| Quality Score | 70 | 40% | Content completeness calculation |
| Voice Score | 70 | 30% | Jenny voice validator |
| Golden Similarity | 0.6 | 30% | Golden benchmark comparison |

**Calculation**:
```python
combined_score = (quality_score * 0.4) + (voice_score * 0.3) + (golden_similarity * 100 * 0.3)
passed = (quality_score >= 70) and (voice_score >= 70) and (golden_similarity >= 0.6)
```

**Output Structure**:
```typescript
interface ObservePhaseData {
  quality_score: number;       // 0-100
  voice_score: number;         // 0-100
  golden_similarity: number;   // 0.0-1.0
  combined_score: number;      // Weighted average
  passed: boolean;
  failing_dimensions: string[];
  issues_found: string[];      // Human-readable issue descriptions
  strengths_found: string[];   // What's working well
}
```

#### LEARN Phase

**Purpose**: Analyze results, generate hints for next cycle

**Behavior**:
1. Compare current quality to previous quality
2. Identify what worked and what failed
3. Generate specific hints for next cycle
4. Decide whether to continue cycling

**Output Structure**:
```typescript
interface LearnPhaseData {
  reasoning: string;
  what_worked: string[];
  what_failed: string[];
  quality_delta: number;       // Current - Previous quality
  corrections_to_apply: string[];
  should_continue: boolean;
}
```

### 5.3 Cycle Progression Example

```
Cycle 1: 53%
├── THINK: "EC Agent analyzing 8 activities using Jenny's 4 Pillars..."
├── ACT: Executing Extracurriculars.process() [186ms]
├── OBSERVE: Quality 53% < 70% threshold. Issues: Spike too generic (50% specificity)
└── LEARN: "Quality below threshold. Hint: Narrow spike to specific domain + population"

Cycle 2: 61% (+8)
├── THINK: "EC Agent correction cycle 2. Applying 3 improvement hints..."
├── ACT: Executing Extracurriculars.process() with 3 hints [201ms]
├── OBSERVE: Quality 61% < 70%. Issues: Archetype confidence low (53%)
└── LEARN: "Improved +8 points but still below threshold. Focus on archetype clarity"

Cycle 3: 69% (+8)
├── THINK: "EC Agent correction cycle 3. Applying 2 improvement hints..."
├── ACT: Executing Extracurriculars.process() with 2 hints [195ms]
├── OBSERVE: Quality 69% < 70%. Max cycles reached.
└── LEARN: "Max cycles reached. Returning best result: 69%"

Final: 69% (Below threshold but max cycles reached)
Trajectory: 53 → 61 → 69
```

---

## 6. Data Flow Specification

### 6.1 Agent-Specific Data Flow

Each agent type has unique input/output data flow tracked for visualization:

#### EC Agent Data Flow

```json
{
  "from_profile": {
    "activities_count": 8,
    "has_passion": true,
    "grade": "11",
    "target_schools_count": 5
  },
  "analyzed": {
    "total_activities": 8,
    "activity_categories": ["STEM", "Service", "Leadership"]
  },
  "generated": {
    "archetype": "stem_innovator",
    "archetype_confidence": 0.78,
    "spike": "Building AI-powered coding education for underserved K-12...",
    "spike_confidence": 0.82,
    "pillars_count": 3,
    "pillars": ["STEM", "Education", "Social Impact"]
  },
  "to_downstream_agents": {
    "archetype": "stem_innovator",
    "spike": "Building AI-powered coding education...",
    "pillars": ["STEM", "Education", "Social Impact"]
  }
}
```

#### Awards Agent Data Flow

```json
{
  "from_ec_agent": {
    "archetype": "stem_innovator",
    "spike": "Building AI-powered coding education...",
    "pillars": ["STEM", "Education", "Social Impact"]
  },
  "searched": {
    "database": "awards_database",
    "matching_criteria": ["archetype_fit", "deadline", "selectivity"]
  },
  "matched": {
    "reach_count": 2,
    "target_count": 2,
    "safety_count": 1,
    "total_awards": 5
  },
  "output": {
    "portfolio_balance": "reach/target/safety",
    "has_strategic_insights": true
  }
}
```

#### Programs Agent Data Flow

```json
{
  "from_ec_agent": {
    "archetype": "stem_innovator",
    "spike": "Building AI-powered coding education...",
    "constraints": ["budget", "location"]
  },
  "searched": {
    "database": "programs_database",
    "matching_criteria": ["archetype_fit", "grade_eligibility", "constraints"],
    "student_grade": "11"
  },
  "matched": {
    "total_programs": 8,
    "program_types": ["research", "academic", "internship"]
  },
  "output": {
    "has_advance_alerts": true,
    "has_synergy_recommendations": true,
    "has_strategic_insights": true
  }
}
```

#### GamePlan Data Flow

```json
{
  "from_ec_agent": {
    "archetype": "stem_innovator",
    "spike": "Building AI-powered coding education...",
    "pillars_count": 3
  },
  "from_awards_agent": {
    "awards_count": 5,
    "has_portfolio": true
  },
  "from_programs_agent": {
    "programs_count": 8,
    "has_recommendations": true
  },
  "synthesized": {
    "phases_count": 3,
    "activities_count": 12,
    "has_narrative": true,
    "has_strategic_insights": true
  }
}
```

---

## 7. Tool Registry & Execution

### 7.1 Available Tools

| Tool Name | Description | Used By |
|-----------|-------------|---------|
| `archetype_classifier` | Classifies profile into 8 archetypes | EC Agent |
| `spike_generator` | Generates specific spike candidates | EC Agent |
| `theme_extractor` | Extracts dominant themes and pillars | EC Agent |
| `golden_benchmark` | Compares against successful profiles | All Agents |
| `awards_db_search` | Searches awards database | Awards Agent |
| `programs_db_search` | Searches programs database | Programs Agent |
| `profile_inferencer` | Infers missing profile data | EC Agent |

### 7.2 Agent-Specific Tool Selection

```python
# From agentic_reasoner.py:_select_tools()

TOOL_SELECTION = {
    # EC Agent: Full diagnostic suite - it CREATES the identity
    "Extracurriculars": [
        "archetype_classifier",
        "spike_generator",
        "theme_extractor"
    ],

    # Awards: Matching tools only - receives archetype from EC
    "Awards": [
        "awards_db_search",    # NOT archetype_classifier!
        "golden_benchmark"
    ],

    # Programs: Matching tools only - receives archetype from EC
    "Programs": [
        "programs_db_search",  # NOT archetype_classifier!
        "golden_benchmark"
    ],

    # GamePlan: Synthesis quality validation
    "GamePlan": [
        "golden_benchmark"
    ]
}
```

### 7.3 Tool Result Schema

```typescript
interface ToolResult {
  tool_name: string;
  success: boolean;
  data: Record<string, unknown>;
  confidence: number;
  reasoning: string;
  suggestions: string[];
  error?: string;
}
```

---

## 8. Quality Validation System

### 8.1 Quality Score Calculation

```python
def _calculate_quality_from_content(result, cycle_num):
    score = 40.0  # Base score

    # EC Agent factors
    identity = result.get("identity_synthesis", {})
    if identity:
        if identity.get("archetype"):
            score += 10
            if identity.get("archetype_confidence", 0) >= 0.8:
                score += 10
            elif identity.get("archetype_confidence", 0) >= 0.6:
                score += 5

        if identity.get("spike"):
            score += 10
            if identity.get("spike_confidence", 0) >= 0.85:
                score += 15
            elif identity.get("spike_confidence", 0) >= 0.7:
                score += 10

        pillars = identity.get("pillars", [])
        if len(pillars) >= 3:
            score += 10
        elif len(pillars) >= 2:
            score += 5

    # Awards Agent factors
    portfolio = result.get("portfolio", {})
    if portfolio:
        if len(portfolio.get("reach", [])) >= 2:
            score += 8
        if len(portfolio.get("target", [])) >= 2:
            score += 8
        if len(portfolio.get("safety", [])) >= 1:
            score += 4
        # Portfolio balance bonus (2-2-1 is ideal)
        if all conditions met:
            score += 10

    # Cycle bonuses (reward improvement)
    if cycle_num > 1:
        cycle_bonus = min(8 * (cycle_num - 1), 16)
        score += cycle_bonus

    return min(score, 100.0)
```

### 8.2 Quality Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| `MIN_QUALITY_SCORE` | 70 | Guardrails confidence (0-100) |
| `MIN_VOICE_SCORE` | 70 | Jenny voice compliance (0-100) |
| `MIN_GOLDEN_SIMILARITY` | 0.6 | Golden benchmark comparison (0-1) |
| `MAX_REACT_CYCLES` | 3 | Maximum correction cycles |

### 8.3 Pass/Fail Determination

```python
passed = (
    quality_score >= MIN_QUALITY_SCORE and
    (voice_score is None or voice_score >= MIN_VOICE_SCORE) and
    (golden_similarity is None or golden_similarity >= MIN_GOLDEN_SIMILARITY)
)
```

---

## 9. Jenny's 4 Pillars Framework

### 9.1 The Formula

```
IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE
```

### 9.2 Pillar Definitions

| Pillar | Color | Description | Data Sources |
|--------|-------|-------------|--------------|
| **Identity** | Purple (#8B5CF6) | Personal narrative & authentic story | gender, ethnicity, religion, immigration, first_gen |
| **Aptitude** | Blue (#3B82F6) | Academic performance & capability | GPA, test_scores, rigor, academic_awards |
| **Passion** | Orange (#F59E0B) | Extracurricular depth & engagement | activities, projects, research, leadership |
| **Service** | Green (#10B981) | Community impact & initiative | service_hours, community_impact, service_leadership |

### 9.3 Pillar Dimensions

#### Identity Pillar
- Personal identity markers
- Constraint reframes (limitations → strengths)
- Cultural background

#### Aptitude Pillar (4 Dimensions)
1. GPA (weighted & unweighted)
2. Test Scores (SAT/ACT)
3. Rigor (AP courses, IB)
4. Academic Awards

#### Passion Pillar (5 Dimensions)
1. Leadership (level, scope)
2. Projects (impact, count)
3. Research (involvement, level)
4. Commitment (years, hours)
5. EC Awards

#### Service Pillar (4 Dimensions)
1. Service Leadership
2. Hours
3. Impact (people served)
4. Consistency (years active)

### 9.4 EC Agent Integration

```python
# From agentic_reasoner.py:_build_ec_reasoning()

# Extract pillar signals from profile
has_identity = bool(profile.get("background") or profile.get("constraints"))
has_aptitude = bool(profile.get("gpa") or profile.get("test_scores"))
has_passion = activity_count > 0
has_service = any(
    "service" in str(a.get("category", "")).lower() or
    "volunteer" in str(a.get("description", "")).lower()
    for a in activities
)
pillars_detected = sum([has_identity, has_aptitude, has_passion, has_service])

# Reasoning message
f"EC Agent analyzing {activity_count} activities using Jenny's 4 Pillars framework. "
f"Detected signals in {pillars_detected}/4 pillars (Identity, Aptitude, Passion, Service)."
```

---

## 10. Frontend Visualization Integration

### 10.1 Component Structure

```
/components/agents/
├── cards/
│   ├── ECAgentCard.tsx          # Extracts _react_by_agent.ec
│   ├── AwardsAgentCard.tsx      # Extracts _react_by_agent.awards
│   ├── OpportunityAgentCard.tsx # Extracts _react_by_agent.programs
│   └── GamePlanAgentCard.tsx    # Extracts _react (orchestrator)
├── react/
│   ├── ReActVisualization.tsx   # Main visualization container
│   ├── CycleTimeline.tsx        # Horizontal cycle dots
│   ├── CycleCard.tsx            # Individual cycle card
│   └── phases/
│       ├── ThinkPhase.tsx       # THINK phase display
│       ├── ActPhase.tsx         # ACT phase display
│       ├── ObservePhase.tsx     # OBSERVE phase display
│       └── LearnPhase.tsx       # LEARN phase display
└── AgentDetailModal.tsx         # Modal with ReAct visualization
```

### 10.2 Data Extraction Pattern

```typescript
// In each AgentCard (ECAgentCard.tsx example)
const { data: gamePlan } = useGamePlan(profileId);

// Extract agent-specific ReAct data
const ecReact =
  (gamePlan as Record<string, unknown>)?._react_by_agent?.ec ||
  gamePlan?.game_plan?.identity_synthesis?._react ||
  gamePlan?.game_plan?._react;

// Pass to detail modal
onViewDetails({
  activities,
  identity_seeds: seeds,
  _react: ecReact,  // Agent-specific ReAct data
});
```

### 10.3 ReAct Metadata Structure

```typescript
interface ReactMetadata {
  success: boolean;
  cycles_executed: number;       // 1-3
  max_cycles: number;            // 3
  final_confidence: number;      // 0.0-1.0
  passed_quality: boolean;
  improvement_trajectory: number[];  // e.g., [53, 61, 69]
  ab_test_group: string;         // "treatment" or "control"
  total_duration_ms: number;
  cycle_summary: CycleSummary[];
  agentic_enabled: boolean;
  version: string;               // "5.0"
  input_data_flow: InputDataFlow;
  agent_name: string;
}
```

---

## 11. API Contracts

### 11.1 Generate GamePlan

**Endpoint**: `POST /api/agents/gameplan/generate`

**Request**:
```json
{
  "profile_id": "uuid-string"
}
```

**Response**:
```json
{
  "success": true,
  "game_plan": {
    "profile_id": "uuid-string",
    "narrative_dna": "...",
    "identity_synthesis": { ... },
    "activities": [ ... ],
    "awards": {
      "portfolio": { "reach": [], "target": [], "safety": [] },
      "top_recommendations": [],
      "strategic_insights": []
    },
    "programs": {
      "top_recommendations": [],
      "advance_alerts": [],
      "strategic_insights": []
    },
    "phases": [ ... ],
    "summary": {
      "total_activities": 12,
      "total_awards_matched": 5,
      "total_programs_matched": 8
    },
    "_react": { ... }  // GamePlan orchestrator ReAct
  },
  "_react_by_agent": {
    "ec": { ... },      // EC Agent ReAct
    "awards": { ... },  // Awards Agent ReAct
    "programs": { ... } // Programs Agent ReAct
  }
}
```

### 11.2 Get GamePlan (Cached)

**Endpoint**: `GET /api/agents/gameplan/{profile_id}`

**Response**: Same as generate, but returns cached result if available.

---

## 12. Error Handling & Fallbacks

### 12.1 Agent Failure Handling

```python
try:
    result = await agent.process(profile_id, **kwargs)
except Exception as e:
    logger.error(f"Agent {agent.name} failed: {e}")
    result = {
        "success": False,
        "error": str(e),
        "_react": {
            "success": False,
            "cycles_executed": 0,
            "error": str(e),
        }
    }
```

### 12.2 Quality Gate Failures

When quality threshold not met after max cycles:
1. Return best result achieved (highest quality score)
2. Mark `passed_quality: false` in ReAct metadata
3. Log warning for monitoring

### 12.3 Database Connection Failures

```python
try:
    profile = await get_profile_with_assessment(profile_id)
except Exception as e:
    # Fallback to minimal profile from kwargs
    profile = {
        "profile_id": profile_id,
        "activities": kwargs.get("activities", []),
        # ... other fallback fields
    }
```

---

## 13. Configuration Reference

### 13.1 Feature Flags

```python
# In config.py
FEATURE_FLAGS = {
    "enable_react": True,                    # Enable ReAct framework
    "react_max_cycles": 3,                   # Max correction cycles
    "react_min_confidence": 0.70,            # Quality threshold
    "react_verbose_logging": False,          # Detailed cycle logging
    "react_ab_test_enabled": False,          # A/B testing
    "react_ab_test_percentage": 0.10,        # Treatment group %
    "enable_voice_validation": True,         # Jenny voice check
    "enable_golden_benchmark": True,         # Golden comparison
    "react_wrap_sub_agents": True,           # Wrap EC/Awards/Programs
    "react_enable_for_agents": [             # Which agents get ReAct
        "Extracurriculars",
        "Awards",
        "Programs",
        "GamePlan"
    ],
}
```

### 13.2 Quality Thresholds

```python
# In react_wrapper.py
MIN_QUALITY_SCORE = 70      # Content quality (0-100)
MIN_VOICE_SCORE = 70        # Jenny voice (0-100)
MIN_GOLDEN_SIMILARITY = 0.6 # Benchmark similarity (0-1)
MAX_REACT_CYCLES = 3        # Max cycles per agent
```

### 13.3 Brand Colors

```typescript
// In lib/constants/brand.ts
BRAND_COLORS = {
  primary: '#FF4A23',      // IvyQuest orange
  secondary: '#641432',    // IvyQuest maroon
  success: '#16a34a',      // Green-600
  warning: '#d97706',      // Amber-600
  error: '#dc2626',        // Red-600
  // Phase colors
  thinkColor: '#FF4A23',   // Orange (THINK)
  actColor: '#3B82F6',     // Blue (ACT)
  observeColor: '#8B5CF6', // Purple (OBSERVE)
  learnColor: '#10B981',   // Green (LEARN)
}
```

---

## Appendix A: Archetype Definitions

| Archetype | Description | Keywords |
|-----------|-------------|----------|
| `stem_innovator` | Builds technical solutions to real problems | coding, AI, robotics, research, hackathon |
| `community_changemaker` | Drives measurable social impact | community, volunteer, nonprofit, advocacy |
| `creative_visionary` | Combines creativity with execution | design, art, media, innovation, startup |
| `policy_advocate` | Influences systems and policy | policy, debate, model UN, law, civic |
| `entrepreneurial_leader` | Builds organizations and leads teams | business, founder, startup, venture |
| `research_scholar` | Pursues deep academic inquiry | research, publication, PhD, analysis |
| `global_citizen` | Bridges cultures and perspectives | international, cultural, exchange, ambassador |
| `artistic_virtuoso` | Achieves excellence in performing/visual arts | music, theater, dance, performance |

---

## Appendix B: Version History

| Version | Date | Changes |
|---------|------|---------|
| 5.0 | 2026-01-16 | Agent-specific ReAct data flow, 4 Pillars integration, issue formatting |
| 4.2 | 2026-01-10 | Agentic reasoner with LLM-based THINK phase |
| 4.0 | 2026-01-05 | Hybrid architecture with sub-agent ReAct wrapping |
| 3.0 | 2025-12-20 | Basic ReAct framework implementation |

---

*End of Specification*
