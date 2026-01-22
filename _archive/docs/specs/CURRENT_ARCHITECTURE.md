# IvyLevel Platform - Current Architecture

## Overview

IvyLevel is a college admissions AI counseling platform that uses a multi-agent orchestration system to provide personalized guidance. The platform follows a **Diagnosis → Prescription** flow:

1. **Assessment System** (Frames 1-6) → Collects 58 Layer 1 attributes + 39 Layer 4 intelligence points
2. **IV Scoring Engine** → 5-layer scoring producing school-specific probabilities
3. **Multi-Agent System** → Generates personalized GamePlan with activities, awards, programs
4. **Execution Agent** → Converts strategy into actionable microsteps with crisis handling

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       FRONTEND (Next.js)                             │
├─────────────────────────────────────────────────────────────────────┤
│  Assessment Flow          │  Dashboard              │  Agent Chat    │
│  (Frames 1-6)             │  (IV Scores, GamePlan)  │  (SSE Stream)  │
└─────────────┬─────────────┴────────────┬────────────┴───────┬───────┘
              │                          │                    │
              ▼                          ▼                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API ROUTES (/api)                              │
├─────────────────────────────────────────────────────────────────────┤
│  /profiles     │  /assessments  │  /game-plans  │  /agents/chat     │
│  /scoring      │  /dashboard    │  /targets     │  /agents/stream   │
└─────────────┬─────────────┬─────────────┬───────────────┬───────────┘
              │             │             │               │
              ▼             ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SCORING ENGINE (lib/scoring)                      │
├─────────────────────────────────────────────────────────────────────┤
│  5-Layer Pipeline:                                                   │
│  1. Normalization (raw → 0-1)                                        │
│  2. Category Aggregation (13 categories)                             │
│  3. IV+ Ready Score (100-point scale)                                │
│  4. SFFA Rubric (Harvard-style 1-6)                                  │
│  5. School Probabilities (P = min(0.95, P_base × Πmultipliers))     │
└─────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  MULTI-AGENT SYSTEM (agents/)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  MIDDLEWARE STACK v9.0                       │    │
│  │  50 Patterns: v6.0(15) + v7.0(10) + v8.0(15) + v9.0(20)     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌───────────────────────────┼───────────────────────────────┐      │
│  │              ORCHESTRATION FLOW                            │      │
│  │                                                            │      │
│  │  ┌─────────────┐                                          │      │
│  │  │  GamePlan   │◄──── Master Orchestrator                 │      │
│  │  │   Agent     │                                          │      │
│  │  └──────┬──────┘                                          │      │
│  │         │                                                  │      │
│  │         ▼                                                  │      │
│  │  ┌─────────────┐     identity_synthesis                   │      │
│  │  │  EC Agent   │────────────────────────┐                │      │
│  │  │   (FIRST)   │                        │                │      │
│  │  └─────────────┘                        ▼                │      │
│  │                               ┌─────────────────────┐     │      │
│  │                               │   Awards + Programs │     │      │
│  │                               │     (PARALLEL)      │     │      │
│  │                               └──────────┬──────────┘     │      │
│  │                                          │                │      │
│  │                                          ▼                │      │
│  │                               ┌─────────────────────┐     │      │
│  │                               │  Narrative Synthesis │     │      │
│  │                               │   → Unified GamePlan │     │      │
│  │                               └─────────────────────┘     │      │
│  └───────────────────────────────────────────────────────────┘      │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    EXECUTION AGENT v10.0                     │    │
│  │  Project Scaffolding │ Crisis Alchemy │ EDS Tracking        │    │
│  │  Blocker Detection   │ Strategic Overwhelm (1.4x)           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE (Supabase + pgvector)                    │
├─────────────────────────────────────────────────────────────────────┤
│  Core:              │  Phase 3 (v9.0):                               │
│  - profiles         │  - phase3_semantic_memories (vector 1536)     │
│  - assessments      │  - phase3_longterm_memories                   │
│  - game_plans       │  - phase3_feedback                            │
│  - conversations    │  - phase3_behavior_adaptations                │
│  - events           │  - phase3_recognized_patterns                 │
│  - crises           │  - phase3_tool_registry                       │
│  - projects         │  - phase3_cost_records                        │
│  - project_steps    │  - phase3_memory_operations                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Assessment Flow (Frames 1-6)

### Frame Breakdown

| Frame | Name | Data Collected |
|-------|------|----------------|
| 1 | Basic Info | first_name, email, grade_level, high_school_type |
| 2 | Academic Foundation | gpa_unweighted, gpa_weighted, course_rigor, ap_courses, test_scores |
| 3 | Extracurricular Activities | activities array (name, role, years, hours, achievements) |
| 4 | Spike/Interests | primary_interests, spike_areas, passion_projects |
| 5 | Awards & Recognition | awards array (name, level, year, significance) |
| 6 | Target Schools | target_schools, early_decision_school, reach/match/safety |

### Data Collection Points

- **Layer 1**: 58 structured attributes (from assessment form fields)
- **Layer 4**: 39 intelligence points (extracted insights from narratives, activities, patterns)

## IV Scoring Engine

The scoring engine (`lib/scoring/engine.ts`, ~900 lines) implements a 5-layer calculation:

```
Layer 1: Raw → Normalized (0-1)
    ↓
Layer 2: Category Aggregation (13 categories)
    ↓
Layer 3: IV+ Ready Score (100-point scale)
    ↓
Layer 4: SFFA Rubric Mapping (Harvard-style 1-6)
    ↓
Layer 5: School Probability (P_final = min(0.95, P_base × Πmultipliers))
```

### SFFA Rubric Categories

| Category | Weight | Description |
|----------|--------|-------------|
| Academic | 0.25 | GPA, course rigor, AP count, test scores |
| Personal | 0.20 | Spike clarity, narrative strength, authenticity |
| Extracurricular | 0.25 | Leadership tier, impact, longevity |
| Athletic | 0.10 | Recruited athlete status |
| Overall | 0.20 | Holistic fit, school-specific alignment |

## Middleware Stack Architecture

### Inheritance Chain

```
MiddlewareStackBasic (v6.0) - 15 Critical Patterns
    └── MiddlewareStackV7 (v7.0) - +10 Important Patterns
            └── MiddlewareStackV8 (v8.0) - +15 Enhancement Patterns
                    └── MiddlewareStackV9 (v9.0) - +20 Final Patterns = 50 TOTAL
```

### Pattern Categories (50 Total)

| Category | Patterns | Purpose |
|----------|----------|---------|
| Context (C) | C1-C4 | Session, user, temporal, student context |
| Reasoning (A) | A1-A12 | CoT, ReAct, self-consistency, planning, metacognition |
| Memory (B) | B1-B6 | Working, cache, semantic, long-term, extraction, consolidation |
| Tools (D) | D1-D7 | Registry, calling, schema, parallel execution, chaining |
| Validation (E) | E1-E4 | Output validation, schema, confidence, quality scoring |
| Safety (F) | F1-F6 | Rate limiting, guardrails, moderation, PII detection |
| Orchestration (G) | G1-G4 | Multi-agent orchestration |
| Resilience (H) | H1-H4 | Retry, circuit breaker, fallbacks |
| Learning (I) | I1-I5 | Feedback, adaptation, pattern recognition, preferences |
| Observability (J) | J1-J5 | Traces, logging, audit, metrics, cost tracking |
| Optimization (K) | K1-K4 | Token optimization, batching, context compression |

## ReAct Framework

### Current Implementation (v13.2)

```python
ReActAgentConfig:
    quality_thresholds:
        completeness: 70    # Minimum % completeness
        confidence: 70      # Minimum % confidence
        coherence: 0.6      # Minimum 0-1 coherence score

    max_cycles: 3           # Maximum THINK→ACT→OBSERVE→LEARN cycles
    cycle_timeout: 60s      # Per-cycle timeout
```

### Cycle Flow

```
THINK: Agent reasons about current state and next action
   ↓
ACT: Execute chosen action (LLM call, tool use, data access)
   ↓
OBSERVE: Capture action results and self-assess quality
   ↓
LEARN: Extract improvements for next cycle
   ↓
[Loop if quality thresholds not met, up to max_cycles]
```

## Data Flow

### New Student Journey

```
1. Landing Page → /profiles (create profile)
2. Assessment Start → Frame 1 (basic info)
3. Frame progression → Frames 2-6 (collect Layer 1 attributes)
4. Assessment Complete → /scoring/calculate
5. IV Scoring → Generate IV+ Ready score, SFFA rubric scores
6. Dashboard View → Display scores, recommendations
7. Agent Chat → GamePlan generation via multi-agent system
8. GamePlan Display → Activities, awards, programs with roadmap
9. Execution → Microsteps via Execution Agent with EDS tracking
```

### Agent Chat Flow

```
User Message → /api/agents/chat
    ↓
Route to appropriate agent (EC, Awards, Programs, GamePlan, Execution)
    ↓
Agent processes with Middleware context
    ↓
SSE Stream → Real-time response chunks
    ↓
Persist conversation → Supabase conversations table
```

## Database Schema

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| profiles | Student profiles | id, first_name, email, grade_level, gpa, activities |
| assessments | Assessment data | profile_id, assessment_type, responses (JSONB) |
| game_plans | Generated plans | profile_id, activities, awards, programs, narrative |
| conversations | Chat history | profile_id, agent_name, messages (JSONB) |
| events | Event bus | event_type, payload, profile_id |
| crises | Crisis records | profile_id, type, status, proposed_response |
| projects | Student projects | profile_id, name, type, status, total_steps |
| project_steps | Microsteps | project_id, title, status, difficulty |

### Phase 3 Tables (v9.0)

| Table | Pattern | Purpose |
|-------|---------|---------|
| phase3_semantic_memories | B3 | Vector embeddings for similarity search |
| phase3_longterm_memories | B4 | Key-value persistent memory |
| phase3_feedback | I1 | User feedback for learning |
| phase3_behavior_adaptations | I2/I3 | Personalization settings |
| phase3_recognized_patterns | I5 | Detected user patterns |
| phase3_tool_registry | D1 | Dynamic tool management |
| phase3_cost_records | J5 | LLM cost tracking |
| phase3_memory_operations | B5/B6 | Memory extraction/consolidation logs |

## Key Integration Points

### External Services

| Service | Purpose | Integration |
|---------|---------|-------------|
| OpenAI | LLM, embeddings, moderation | gpt-4o, text-embedding-3-small |
| Supabase | Database, auth, realtime | PostgreSQL + pgvector |
| Langfuse | Observability, tracing | Trace logging, cost tracking |
| Redis | Working memory, caching | Optional (falls back to in-memory) |

### Internal Integrations

| Component | Depends On |
|-----------|-----------|
| Scoring Engine | Assessment data, profile |
| Multi-Agent System | Scoring output, profile, middleware |
| Execution Agent | GamePlan output, project data |
| Dashboard | All agent outputs, scoring, profile |

---

*Document generated: Platform Discovery Phase 1*
*Architecture Version: v10.0 Framework / Middleware v9.0*
