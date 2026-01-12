# IvyQuest Multi-Agent System Specification v15.0
## Comprehensive UI/UX, Data Flow, Message Sequences & Agent Design

**Version:** 15.0.0
**Date:** January 12, 2026
**Status:** Implemented & Tested
**Architecture:** 6-Agent Parallel Processing with ReAct Framework

---

## Table of Contents

1. [System Overview](#part-1-system-overview)
2. [Agent Architecture](#part-2-agent-architecture)
3. [UI/UX Design](#part-3-uiux-design)
4. [Data Flow Architecture](#part-4-data-flow-architecture)
5. [Message Sequence Diagrams](#part-5-message-sequence-diagrams)
6. [Individual Agent Specifications](#part-6-individual-agent-specifications)
7. [Inter-Agent Communication](#part-7-inter-agent-communication)
8. [Frontend Component Specifications](#part-8-frontend-component-specifications)
9. [API Reference](#part-9-api-reference)
10. [Testing & Validation](#part-10-testing--validation)

---

## PART 1: SYSTEM OVERVIEW

### 1.1 Multi-Agent Architecture

IvyQuest v15.0 implements a **6-agent parallel processing architecture** designed to provide comprehensive college admissions coaching. Each agent operates with defined autonomy levels while maintaining narrative coherence across the student's journey.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     IvyQuest Multi-Agent Intelligence                       │
│                              v15.0 Architecture                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                        │
│  │ ASSESSMENT  │  │  GAME PLAN  │  │  EXECUTION  │                        │
│  │   AGENT     │  │    AGENT    │  │    AGENT    │                        │
│  │ ─────────── │  │ ─────────── │  │ ─────────── │                        │
│  │ Narrative   │  │ Strategic   │  │ Project     │                        │
│  │ Synthesis   │──▶│ Roadmap    │──▶│ Scaffolding │                        │
│  │ & Identity  │  │ Generation  │  │ & Crisis    │                        │
│  │             │  │             │  │ Management  │                        │
│  │ Autonomy:   │  │ Autonomy:   │  │ Autonomy:   │                        │
│  │ HIGH        │  │ HIGH        │  │ MEDIUM/LOW  │                        │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘                        │
│         │                │                                                  │
│         │                │         ┌─────────────┐                        │
│         │                │         │   CRISIS    │                        │
│         │                │         │    AGENT    │                        │
│         │                │         │ ─────────── │                        │
│         │                └────────▶│ VARC        │                        │
│         │                          │ Framework   │                        │
│         │                          │ Autonomy:   │                        │
│         │                          │ LOW (HITL)  │                        │
│         │                          └─────────────┘                        │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────┐  ┌─────────────┐                                         │
│  │   AWARDS    │  │ OPPORTUNITY │                                         │
│  │   AGENT     │  │    AGENT    │                                         │
│  │ ─────────── │  │ ─────────── │                                         │
│  │ Portfolio   │  │ Program     │                                         │
│  │ Matching &  │  │ Matching &  │                                         │
│  │ ROI Analysis│  │ Alerts      │                                         │
│  │             │  │             │                                         │
│  │ Autonomy:   │  │ Autonomy:   │                                         │
│  │ FULL        │  │ FULL        │                                         │
│  └─────────────┘  └─────────────┘                                         │
│                                                                             │
├────────────────────────────────────────────────────────────────────────────┤
│                          SHARED INFRASTRUCTURE                              │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐                 │
│  │  3-Tier Memory │ │  Quality Gates │ │  HITL Workflow │                 │
│  │  Working/Redis │ │  70/70/0.6     │ │  Approval Flow │                 │
│  │  /Supabase     │ │  Max 3 Cycles  │ │  7-day Timeout │                 │
│  └────────────────┘ └────────────────┘ └────────────────┘                 │
└────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Agent Roster

| Agent | Purpose | Autonomy | LLM Usage | Output Type |
|-------|---------|----------|-----------|-------------|
| **Assessment** | Narrative DNA synthesis | HIGH | Gemini/GPT-4 | Generative |
| **Game Plan** | Strategic roadmap | HIGH | Gemini/GPT-4 | Generative |
| **Execution** | Project scaffolding | MEDIUM | Gemini/GPT-4 | Generative |
| **Awards** | Portfolio matching | FULL | Gemini/GPT-4 | Deterministic |
| **Opportunity** | Program matching | FULL | Gemini/GPT-4 | Deterministic |
| **Crisis** | VARC transformation | LOW | Gemini/GPT-4 | Generative + HITL |

### 1.3 Core Design Principles

1. **Jenny's Formula**: `IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE`
2. **Quality Gates**: All outputs must meet 70/70/0.6 thresholds
3. **Narrative Coherence**: All agents align with student's narrative DNA
4. **Strategic Overwhelm**: 1.4x capacity assignment (73% completion target)
5. **Multi-Touchpoint**: Activities must have ≥4 touchpoints
6. **HITL Safety**: Human review for high-stakes decisions

---

## PART 2: AGENT ARCHITECTURE

### 2.1 ReAct Framework Implementation

Each agent follows the **ReAct (Reasoning + Acting)** pattern:

```
┌────────────────────────────────────────────────────────────────────┐
│                    ReAct Agent Execution Loop                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│   │  THINK  │───▶│ ACTION  │───▶│ OBSERVE │───▶│  LEARN  │        │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘        │
│        │                                              │             │
│        │         ┌─────────────────────────────┐     │             │
│        │         │     QUALITY GATES CHECK      │     │             │
│        │         │                              │     │             │
│        │         │  Quality Score ≥ 70?        │     │             │
│        │         │  Voice Score ≥ 70?          │     │             │
│        │         │  Golden Similarity ≥ 0.6?   │     │             │
│        │         │                              │     │             │
│        │         │  YES ──▶ RETURN RESULT      │     │             │
│        │         │  NO  ──▶ INJECT LEARNINGS   │◀────┘             │
│        │         └─────────────────────────────┘                   │
│        │                        │                                   │
│        │◀───────────────────────┘ (Max 3 Cycles)                   │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 Autonomy Levels

```python
class AutonomyLevel(Enum):
    FULL = "full"       # No human review (deterministic calculations)
    HIGH = "high"       # Auto-approve if confidence > 70%
    MEDIUM = "medium"   # Optional human review
    LOW = "low"         # Always requires human review
```

### 2.3 Quality Thresholds

```python
class QualityThresholds:
    MIN_QUALITY_SCORE = 70      # Content quality (0-100)
    MIN_VOICE_SCORE = 70        # Jenny voice compliance (0-100)
    MIN_GOLDEN_SIMILARITY = 0.6 # Golden example match (0-1)
    MAX_REACT_CYCLES = 3        # Self-correction attempts
    MAX_THINK_TIME_MS = 5000    # Think phase timeout
    MAX_ACTION_TIME_MS = 10000  # Action phase timeout
```

### 2.4 LLM Provider Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                  LLM Provider Selection                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────┐                                     │
│  │  Google Gemini     │◀─────── PRIMARY (More Stable)       │
│  │  gemini-2.0-flash  │                                     │
│  └─────────┬──────────┘                                     │
│            │                                                 │
│            │ If unavailable                                  │
│            ▼                                                 │
│  ┌────────────────────┐                                     │
│  │  OpenAI GPT-4      │◀─────── FALLBACK                    │
│  │  gpt-4-turbo       │                                     │
│  └────────────────────┘                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## PART 3: UI/UX DESIGN

### 3.1 Multi-Agent Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  IvyQuest Command Deck                                     [Bell] [User]│
├────────┬────────────────────────────────────────────────────────────────┤
│        │                                                                 │
│  NAV   │  Multi-Agent Dashboard                                         │
│        │  Your 6-agent coaching team working in parallel                │
│ ────── │                                                                 │
│ Assess │  ● Backend healthy                        [Refresh All]        │
│ Game   │  v15.0.0 • ReAct: On • Memory: On • HITL: On                   │
│ Prep   │                                                                 │
│ Growth │  ┌───────────────────┐ ┌───────────────────┐ ┌────────────────┐│
│ Multi  │  │ ASSESSMENT AGENT  │ │ GAME PLAN AGENT   │ │EXECUTION AGENT ││
│        │  │ ───────────────── │ │ ───────────────── │ │────────────────││
│        │  │ Narrative DNA:    │ │ 12 Activities     │ │ EDS: 24        ││
│        │  │ "A South Asian..."│ │ 6 Identity Seeds  │ │ Status: Healthy││
│        │  │                   │ │ 3 Phases          │ │ Blockers: 0    ││
│        │  │ Themes: [Culture] │ │                   │ │                ││
│        │  │ [Leadership]      │ │ Current Phase:    │ │ ████████░░     ││
│        │  │                   │ │ "Foundation"      │ │ 24/100         ││
│        │  │ Confidence: 95%   │ │                   │ │                ││
│        │  │ ███████████████░  │ │ Touchpoints: 48   │ │ Contributing:  ││
│        │  │                   │ │ Avg ROI: 2.3      │ │ - On track     ││
│        │  │ [Refresh] [Chat]  │ │ [Refresh] [Chat]  │ │[Refresh] [Chat]││
│        │  │ Click for details │ │ Click for details │ │Click for detail││
│        │  └───────────────────┘ └───────────────────┘ └────────────────┘│
│        │                                                                 │
│        │  ┌───────────────────┐ ┌───────────────────┐ ┌────────────────┐│
│        │  │ AWARDS AGENT      │ │ OPPORTUNITY AGENT │ │ CRISIS RESPONSE││
│        │  │ ───────────────── │ │ ───────────────── │ │────────────────││
│        │  │ ┌─────┬─────┬────┐│ │ ┌──────┬─────────┐│ │                ││
│        │  │ │  0  │  4  │  2 ││ │ │  8   │    2    ││ │ ✓ No Active   ││
│        │  │ │Likly│Targt│Strch│ │ │Match │ Urgent  ││ │   Crises      ││
│        │  │ └─────┴─────┴────┘│ │ └──────┴─────────┘│ │                ││
│        │  │                   │ │                   │ │ Everything is  ││
│        │  │ Expected Wins: 2.4│ │ Upcoming:         │ │ on track       ││
│        │  │                   │ │ • RSI (14 days)   │ │                ││
│        │  │ Strategy Tip:     │ │ • TASP (2 months) │ │ [Report Crisis]││
│        │  │ "Focus on local"  │ │                   │ │                ││
│        │  │                   │ │                   │ │ VARC Framework ││
│        │  │ [Refresh] [Chat]  │ │ [Refresh] [Chat]  │ │ V A R C        ││
│        │  │ Click for details │ │ Click for details │ │                ││
│        │  └───────────────────┘ └───────────────────┘ └────────────────┘│
│        │                                                                 │
└────────┴────────────────────────────────────────────────────────────────┘
```

### 3.2 Agent Card Component Design

Each agent card follows a consistent structure:

```
┌──────────────────────────────────────┐
│ [Icon] AGENT NAME                    │ ← Header with icon
│ ──────────────────────────────────── │
│                                      │
│  ┌────────────────────────────────┐  │
│  │                                │  │
│  │     PRIMARY METRIC             │  │ ← Key value display
│  │     (Large, prominent)         │  │
│  │                                │  │
│  └────────────────────────────────┘  │
│                                      │
│  Secondary Info                      │ ← Supporting details
│  • Detail 1                          │
│  • Detail 2                          │
│                                      │
│ ──────────────────────────────────── │
│ [Refresh] [Chat]  Click for details  │ ← Actions footer
└──────────────────────────────────────┘
```

### 3.3 Agent Detail Modal Design

When a card is clicked, a detail modal opens:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENT NAME - Detailed View                                        [X] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        SECTION 1                                 │   │
│  │  Primary data visualization / content                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        SECTION 2                                 │   │
│  │  Secondary data / breakdown                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        SECTION 3                                 │   │
│  │  Additional details / action items                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Color System (Brand Colors)

```typescript
export const BRAND_COLORS = {
  // Primary accent
  primary: '#FF4A23',              // Ivylevel orange
  primaryBg: 'rgba(255, 74, 35, 0.1)',

  // Secondary
  secondary: '#641432',            // Ivylevel maroon (headings)

  // Status colors
  success: '#16a34a',              // Green - healthy, likely
  warning: '#d97706',              // Amber - target, caution
  error: '#dc2626',                // Red - stretch, urgent

  // EDS Status (Execution Debt Score)
  edsHealthy: '#16a34a',           // Green (0-30)
  edsAtRisk: '#d97706',            // Orange (30-60)
  edsCritical: '#dc2626',          // Red (60+)
};
```

### 3.5 Responsive Grid Layout

```css
/* Desktop: 3 columns */
@media (min-width: 1024px) {
  .agent-grid { grid-template-columns: repeat(3, 1fr); }
}

/* Tablet: 2 columns */
@media (min-width: 768px) and (max-width: 1023px) {
  .agent-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Mobile: 1 column */
@media (max-width: 767px) {
  .agent-grid { grid-template-columns: 1fr; }
}
```

---

## PART 4: DATA FLOW ARCHITECTURE

### 4.1 High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       END-TO-END DATA FLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  USER PROFILE DATA                                                       │
│  (from Assessment Frames)                                                │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                    SUPABASE DATABASE                          │       │
│  │  profiles table ──▶ profile_id                               │       │
│  │                     profile_data (JSON)                       │       │
│  │                     assessment_results                        │       │
│  └──────────────────────────────────────────────────────────────┘       │
│         │                                                                │
│         │ profile_id                                                     │
│         ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                  PYTHON AGENT SERVICE                         │       │
│  │                     (FastAPI @ :8001)                         │       │
│  │                                                               │       │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │       │
│  │  │Assessment  │  │ Game Plan  │  │ Execution  │             │       │
│  │  │  Agent     │  │   Agent    │  │   Agent    │             │       │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │       │
│  │        │               │               │                     │       │
│  │  ┌─────┴──────┐  ┌─────┴──────┐  ┌─────┴──────┐             │       │
│  │  │ Awards     │  │Opportunity │  │  Crisis    │             │       │
│  │  │   Agent    │  │   Agent    │  │   Agent    │             │       │
│  │  └────────────┘  └────────────┘  └────────────┘             │       │
│  │                                                               │       │
│  └──────────────────────────────────────────────────────────────┘       │
│         │                                                                │
│         │ JSON Responses                                                 │
│         ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                  NEXT.JS FRONTEND                             │       │
│  │                                                               │       │
│  │  React Query ──▶ useAgentData hooks ──▶ Agent Cards          │       │
│  │       │                                                       │       │
│  │       └──▶ Cache (staleTime, gcTime)                         │       │
│  │                                                               │       │
│  └──────────────────────────────────────────────────────────────┘       │
│         │                                                                │
│         ▼                                                                │
│     USER INTERFACE                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Assessment Agent Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  ASSESSMENT AGENT DATA FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  INPUT: Profile Data                                                     │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ {                                                             │       │
│  │   profile_id: "uuid",                                        │       │
│  │   identity: { ethnicity, first_gen, geographic_location },   │       │
│  │   aptitude: { gpa, sat, skills, achievements },              │       │
│  │   passion: { spike, essay_keywords },                        │       │
│  │   service: { volunteer_hours, leadership, communities }      │       │
│  │ }                                                             │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                            │                                             │
│                            ▼                                             │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │              JENNY'S FORMULA SYNTHESIS                        │       │
│  │                                                               │       │
│  │  IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE  │       │
│  │                                                               │       │
│  │  1. Extract four pillars from profile data                   │       │
│  │  2. Apply Jenny's Formula via LLM                            │       │
│  │  3. Generate brand statement (1 sentence)                    │       │
│  │  4. Generate narrative DNA (2-3 paragraphs)                  │       │
│  │  5. Extract themes and first principle                       │       │
│  │  6. Calculate confidence score                               │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                            │                                             │
│                            ▼                                             │
│  OUTPUT: Narrative DNA                                                   │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ {                                                             │       │
│  │   success: true,                                              │       │
│  │   brand_statement: "One powerful sentence",                  │       │
│  │   narrative_dna: "2-3 paragraph story",                      │       │
│  │   first_principle: "Core driving why",                       │       │
│  │   themes: ["theme1", "theme2", "theme3"],                    │       │
│  │   identity_markers: ["marker1", "marker2"],                  │       │
│  │   confidence: 0.85,                                           │       │
│  │   requires_handoff: false                                     │       │
│  │ }                                                             │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Game Plan Agent Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   GAME PLAN AGENT DATA FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  INPUT: Profile + Narrative DNA                                          │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ {                                                             │       │
│  │   profile_id: "uuid",                                        │       │
│  │   narrative_dna: "...",    // From Assessment Agent          │       │
│  │   hidden_target: "STANFORD", // Computed hidden target       │       │
│  │   archetype: "DOUBLE_DOWN"                                   │       │
│  │ }                                                             │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                            │                                             │
│                            ▼                                             │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │              ACTIVITY FILTERING PIPELINE                      │       │
│  │                                                               │       │
│  │  1. Get all possible activities from database                │       │
│  │  2. Filter through narrative lens (not just ROI)             │       │
│  │  3. Require ≥4 touchpoints per activity (ACP-005)           │       │
│  │  4. Apply Strategic Overwhelm (1.4x capacity) (ACP-004)     │       │
│  │  5. Calculate ROI: (probability × prestige) / effort        │       │
│  │  6. Generate identity seeds (6-12 months ahead)             │       │
│  │  7. Create phased roadmap                                     │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                            │                                             │
│                            ▼                                             │
│  OUTPUT: Strategic Roadmap                                               │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ {                                                             │       │
│  │   game_plan: {                                                │       │
│  │     activities: Activity[],         // Filtered list          │       │
│  │     identity_seeds: IdentitySeed[], // 6-12 month plants     │       │
│  │     phases: Phase[],                // Phased rollout         │       │
│  │     summary: {                                                │       │
│  │       total_activities: 12,                                   │       │
│  │       total_touchpoints: 48,                                  │       │
│  │       average_roi: 2.3,                                       │       │
│  │       expected_completion_rate: 0.73  // 73% target          │       │
│  │     }                                                         │       │
│  │   }                                                           │       │
│  │ }                                                             │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.4 Awards Agent Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AWARDS AGENT DATA FLOW                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  INPUT: Profile Data                                                     │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ {                                                             │       │
│  │   profile_id: "uuid",                                        │       │
│  │   academic: { gpa, sat, ap_count },                          │       │
│  │   activities: [...],                                          │       │
│  │   awards_won: [...],                                          │       │
│  │   narrative_dna: "..."                                        │       │
│  │ }                                                             │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                            │                                             │
│                            ▼                                             │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │              AWARD MATCHING PIPELINE                          │       │
│  │                                                               │       │
│  │  1. Get all active awards from database                      │       │
│  │  2. Filter by eligibility criteria                           │       │
│  │  3. Calculate win probability via LLM                        │       │
│  │  4. Calculate ROI: (prob × prestige) / effort               │       │
│  │  5. Categorize into tiers:                                   │       │
│  │     - Likely: 60%+ win probability                           │       │
│  │     - Target: 40-60% probability                             │       │
│  │     - Stretch: 20-40% probability                            │       │
│  │  6. Compute expected wins (sum of probabilities)             │       │
│  │  7. Generate strategy notes                                   │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                            │                                             │
│                            ▼                                             │
│  OUTPUT: Award Portfolio                                                 │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ {                                                             │       │
│  │   matches: AwardMatch[],                                      │       │
│  │   portfolio: {                                                │       │
│  │     likely: AwardMatch[],      // 60%+ probability           │       │
│  │     target: AwardMatch[],      // 40-60% probability         │       │
│  │     stretch: AwardMatch[],     // 20-40% probability         │       │
│  │     total_recommended: 6,                                     │       │
│  │     expected_wins: 2.4,        // Sum of probabilities       │       │
│  │     total_effort_hours: 120,                                  │       │
│  │     strategy_notes: ["Focus on...", "Consider..."]          │       │
│  │   }                                                           │       │
│  │ }                                                             │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## PART 5: MESSAGE SEQUENCE DIAGRAMS

### 5.1 Dashboard Initialization Sequence

```
┌──────┐    ┌────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────┐
│ User │    │  Frontend  │    │ React Query │    │ Agent Service│    │ Supabase │
└──┬───┘    └─────┬──────┘    └──────┬──────┘    └──────┬───────┘    └────┬─────┘
   │              │                   │                  │                 │
   │ Navigate to  │                   │                  │                 │
   │ /dashboard   │                   │                  │                 │
   │─────────────▶│                   │                  │                 │
   │              │                   │                  │                 │
   │              │ Check profileId   │                  │                 │
   │              │ in sessionStore   │                  │                 │
   │              │──────────────────▶│                  │                 │
   │              │                   │                  │                 │
   │              │ If null, fetch    │                  │                 │
   │              │ from Supabase     │                  │                 │
   │              │───────────────────────────────────────────────────────▶│
   │              │                   │                  │                 │
   │              │◀──────────────────────────────────── profile_id ───────│
   │              │                   │                  │                 │
   │              │ useDashboardV13Data(profileId)       │                 │
   │              │──────────────────▶│                  │                 │
   │              │                   │                  │                 │
   │              │                   │ Parallel queries │                 │
   │              │                   │──────────────────▶                 │
   │              │                   │ GET /agents/narrative/{id}        │
   │              │                   │ POST /agents/gameplan/generate    │
   │              │                   │ GET /agents/execution/eds/{id}    │
   │              │                   │ GET /agents/awards/match/{id}     │
   │              │                   │ GET /agents/opportunities/alerts  │
   │              │                   │ GET /v13/health                   │
   │              │                   │                  │                 │
   │              │                   │◀───── JSON responses ─────────────│
   │              │                   │                  │                 │
   │              │◀── Cached data ───│                  │                 │
   │              │                   │                  │                 │
   │◀─ Render ────│                   │                  │                 │
   │  Dashboard   │                   │                  │                 │
   │              │                   │                  │                 │
```

### 5.2 Assessment Agent Narrative Synthesis Sequence

```
┌──────┐    ┌────────────┐    ┌─────────────────┐    ┌──────────┐    ┌─────────┐
│ User │    │  Frontend  │    │ Assessment Agent│    │   LLM    │    │Supabase │
└──┬───┘    └─────┬──────┘    └────────┬────────┘    └────┬─────┘    └────┬────┘
   │              │                     │                  │               │
   │ Click Refresh│                     │                  │               │
   │ on Assessment│                     │                  │               │
   │──────────────▶                     │                  │               │
   │              │                     │                  │               │
   │              │ POST /agents/narrative/synthesize     │               │
   │              │ { profile_id }      │                  │               │
   │              │────────────────────▶│                  │               │
   │              │                     │                  │               │
   │              │                     │ Get profile data │               │
   │              │                     │──────────────────────────────────▶
   │              │                     │◀─── profile_data ────────────────│
   │              │                     │                  │               │
   │              │                     │ Extract 4 Pillars│               │
   │              │                     │ Identity         │               │
   │              │                     │ Aptitude         │               │
   │              │                     │ Passion          │               │
   │              │                     │ Service          │               │
   │              │                     │                  │               │
   │              │                     │ Build prompt     │               │
   │              │                     │ (Jenny's Formula)│               │
   │              │                     │                  │               │
   │              │                     │ LLM invoke      │               │
   │              │                     │─────────────────▶│               │
   │              │                     │                  │               │
   │              │                     │◀─ Narrative DNA ─│               │
   │              │                     │  + themes        │               │
   │              │                     │  + confidence    │               │
   │              │                     │                  │               │
   │              │                     │ Store narrative  │               │
   │              │                     │──────────────────────────────────▶
   │              │                     │                  │               │
   │              │◀────────────────────│                  │               │
   │              │ { narrative_dna, themes, confidence }  │               │
   │              │                     │                  │               │
   │◀─ Update UI ─│                     │                  │               │
   │              │                     │                  │               │
```

### 5.3 Crisis Alchemy HITL Sequence

```
┌──────┐    ┌────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────┐
│ User │    │  Frontend  │    │ Crisis Agent │    │ HITL Manager │    │ Coach │
└──┬───┘    └─────┬──────┘    └──────┬───────┘    └──────┬───────┘    └───┬───┘
   │              │                   │                   │                │
   │ Click "Report│                   │                   │                │
   │ Crisis"      │                   │                   │                │
   │──────────────▶                   │                   │                │
   │              │                   │                   │                │
   │              │ Open Crisis Modal │                   │                │
   │◀─────────────│                   │                   │                │
   │              │                   │                   │                │
   │ Fill form:   │                   │                   │                │
   │ type,desc,   │                   │                   │                │
   │ urgency      │                   │                   │                │
   │──────────────▶                   │                   │                │
   │              │                   │                   │                │
   │              │ POST /agents/crisis-alchemy           │                │
   │              │ { crisis_type, description, urgency } │                │
   │              │───────────────────▶                   │                │
   │              │                   │                   │                │
   │              │                   │ Generate VARC     │                │
   │              │                   │ Response          │                │
   │              │                   │                   │                │
   │              │                   │ Check confidence  │                │
   │              │                   │ confidence < 70%? │                │
   │              │                   │        │          │                │
   │              │                   │        ▼ YES      │                │
   │              │                   │ Create HITL Request                │
   │              │                   │───────────────────▶                │
   │              │                   │                   │                │
   │              │                   │                   │ Notify Coach   │
   │              │                   │                   │───────────────▶│
   │              │                   │                   │                │
   │              │◀──────────────────│                   │                │
   │              │ { steps: VARC,    │                   │                │
   │              │   requires_handoff: true,             │                │
   │              │   handoff_reason: "..." }             │                │
   │              │                   │                   │                │
   │◀─ Show VARC ─│                   │                   │                │
   │  + Pending   │                   │                   │                │
   │  Review badge│                   │                   │                │
   │              │                   │                   │                │
   │              │                   │                   │   Review &     │
   │              │                   │                   │◀── Approve ────│
   │              │                   │                   │                │
   │              │                   │                   │ POST /handoff/ │
   │              │                   │◀──────────────────│ approve        │
   │              │                   │                   │                │
   │              │◀── Update status ─│                   │                │
   │◀─ Approved ──│                   │                   │                │
   │              │                   │                   │                │
```

### 5.4 Opportunity Alert Generation Sequence

```
┌──────────────┐    ┌───────────────────┐    ┌──────────────┐    ┌──────────┐
│   Scheduler  │    │ Opportunity Agent │    │   Database   │    │ Frontend │
└──────┬───────┘    └─────────┬─────────┘    └──────┬───────┘    └────┬─────┘
       │                      │                     │                  │
       │ Cron: Daily at 6AM   │                     │                  │
       │─────────────────────▶│                     │                  │
       │                      │                     │                  │
       │                      │ Get all profiles    │                  │
       │                      │ with active         │                  │
       │                      │ assessments         │                  │
       │                      │────────────────────▶│                  │
       │                      │◀───── profiles ─────│                  │
       │                      │                     │                  │
       │                      │ For each profile:   │                  │
       │                      │                     │                  │
       │                      │ Get matched         │                  │
       │                      │ opportunities       │                  │
       │                      │────────────────────▶│                  │
       │                      │◀── opportunities ───│                  │
       │                      │                     │                  │
       │                      │ Check deadlines:    │                  │
       │                      │ 6 months = PREPARE  │                  │
       │                      │ 3 months = URGENT   │                  │
       │                      │ 1 month = IMMINENT  │                  │
       │                      │                     │                  │
       │                      │ Create alerts       │                  │
       │                      │────────────────────▶│                  │
       │                      │                     │                  │
       │                      │ Create notification │                  │
       │                      │────────────────────▶│                  │
       │                      │                     │                  │
       │                      │                     │                  │
       │                      │                     │   Poll every     │
       │                      │                     │◀── 30 seconds ───│
       │                      │                     │                  │
       │                      │                     │── alerts ───────▶│
       │                      │                     │                  │
       │                      │                     │    Show badge    │
       │                      │                     │    + alert list  │
       │                      │                     │                  │
```

---

## PART 6: INDIVIDUAL AGENT SPECIFICATIONS

### 6.1 Assessment Agent

#### 6.1.1 Purpose
Diagnoses student state and synthesizes personalized narrative using Jenny's Formula.

#### 6.1.2 Input Schema
```typescript
interface AssessmentInput {
  profile_id: string;
  data?: {
    raw_identity: {
      ethnicity?: string;
      first_gen?: boolean;
      geographic_location?: string;
      cultural_background?: string[];
      immigration_status?: string;
      religion?: string;
    };
    raw_aptitude: {
      gpa_weighted?: number;
      sat_total?: number;
      ap_count?: number;
      awards?: string[];
      skills?: string[];
    };
    raw_passion: {
      spike?: string;
      essay_keywords?: string[];
      intended_major?: string;
    };
    raw_service: {
      volunteer_hours?: number;
      leadership_roles?: string[];
      communities_served?: string[];
    };
  };
}
```

#### 6.1.3 Output Schema
```typescript
interface AssessmentOutput {
  success: boolean;
  brand_statement: string;          // 1 powerful sentence
  narrative_dna: string;            // 2-3 paragraphs
  first_principle: string;          // Core "why"
  themes: string[];                 // 3 recurring themes
  identity_markers?: string[];      // Key identity points
  confidence: number;               // 0-1
  requires_handoff: boolean;
  synthesis_inputs?: {
    identity: object;
    aptitude: object;
    passion: object;
    service: object;
  };
}
```

#### 6.1.4 Processing Steps
1. Extract four pillars from profile data
2. Build synthesis prompt with Jenny's Formula
3. Invoke LLM (Gemini primary, GPT-4 fallback)
4. Parse structured response
5. Validate confidence (cap at 0.95)
6. Store in database
7. Flag for handoff if confidence < 0.7

#### 6.1.5 API Endpoints
| Endpoint | Method | Description | Timeout |
|----------|--------|-------------|---------|
| `/agents/narrative/{profile_id}` | GET | Get existing narrative | 60s |
| `/agents/narrative/synthesize` | POST | Generate new narrative | 120s |

#### 6.1.6 Frontend Component
```typescript
// AssessmentAgentCard.tsx
interface Props {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}
```

**Displays:**
- Narrative DNA quote (line-clamp-4)
- Themes as badges (max 3)
- Confidence progress bar
- Identity markers (in detail modal)

---

### 6.2 Game Plan Agent

#### 6.2.1 Purpose
Generates strategic roadmap optimized for hidden target with narrative-aligned activities.

#### 6.2.2 Input Schema
```typescript
interface GamePlanInput {
  profile_id: string;
  assessment_data?: {
    narrative_dna?: string;
    hidden_target?: string;
    archetype?: string;
  };
}
```

#### 6.2.3 Output Schema
```typescript
interface GamePlanOutput {
  success: boolean;
  game_plan: {
    profile_id: string;
    narrative_dna: string;
    hidden_target: string | null;
    activities: Activity[];
    identity_seeds: IdentitySeed[];
    phases: Phase[];
    summary: {
      total_activities: number;
      total_touchpoints: number;
      average_roi: number;
      expected_completion_rate: number;
    };
    created_at: string;
  };
  requires_handoff: boolean;
}

interface Activity {
  name: string;
  description: string;
  category: string;
  touchpoints: string[];           // ≥4 required
  touchpoint_count: number;
  prestige_score: number;
  hours_required: number;
  roi: number;                     // (prob × prestige) / effort
  narrative_alignment: number;     // 0-1
  narrative_thread?: string;
  recommended: boolean;
  rationale: string;
}

interface IdentitySeed {
  id: string;
  target: string;
  target_type: string;
  plant_date: string;
  bloom_date: string;
  months_until_bloom: number;
  actions: SeedAction[];
  status: 'planned' | 'active' | 'completed';
  narrative_connection: string;
}

interface Phase {
  name: string;
  start_date: string;
  end_date: string;
  focus_areas: string[];
  key_milestones: string[];
}
```

#### 6.2.4 Processing Steps (ACP Primitives)
1. **ACP-004 Strategic Overwhelm**: Assign 1.4x capacity
2. **ACP-005 Multi-Touchpoint**: Require ≥4 touchpoints per activity
3. **ACP-006 Identity Seeds**: Plant 6-12 months ahead
4. Filter activities through narrative lens
5. Calculate ROI for each activity
6. Generate phased roadmap
7. Create summary statistics

#### 6.2.5 API Endpoints
| Endpoint | Method | Description | Timeout |
|----------|--------|-------------|---------|
| `/agents/gameplan/generate` | POST | Generate full game plan | **120s** |
| `/agents/gameplan/activities/{id}` | GET | Get filtered activities | 60s |
| `/agents/gameplan/seeds/{id}` | GET | Get identity seeds | 60s |

#### 6.2.6 Frontend Component
```typescript
// GamePlanAgentCard.tsx
interface Props {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}
```

**Displays:**
- 3-column stats: Activities, Seeds, Phases
- Current phase name
- Total touchpoints
- Average ROI

---

### 6.3 Execution Agent

#### 6.3.1 Purpose
Bridges strategy-execution gap through project scaffolding, EDS tracking, and crisis management.

#### 6.3.2 EDS (Execution Debt Score) Schema
```typescript
interface ExecutionDebtScore {
  profile_id: string;
  execution_debt_score: number;    // 0-100 (lower = better)
  status: 'healthy' | 'at_risk' | 'critical';
  threshold: number;
  contributing_factors?: string[];
}

// Status thresholds:
// healthy: 0-30
// at_risk: 30-60
// critical: 60+
```

#### 6.3.3 Blocker Schema
```typescript
interface Blocker {
  id: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category?: string;
  created_at?: string;
  resolution_steps?: string[];
}
```

#### 6.3.4 Crisis Response Schema (VARC)
```typescript
interface CrisisResponse {
  success: boolean;
  crisis_id: string;
  steps: {
    validate: {
      message: string;
      emotion_acknowledged: boolean;
    };
    act: {
      action: string;
      time_required: string;    // e.g., "30 minutes"
    };
    reframe: {
      opportunity: string;
      new_perspective: string;
    };
    create: {
      new_activity: string;
      connection_to_narrative: string;
    };
  };
  requires_handoff: boolean;
  handoff_reason?: string;
}
```

#### 6.3.5 API Endpoints
| Endpoint | Method | Description | Timeout |
|----------|--------|-------------|---------|
| `/agents/execution/eds/{id}` | GET | Get EDS score | 60s |
| `/agents/execution/blockers/{id}` | GET | Get blockers | 60s |
| `/agents/execution/scaffold` | POST | Scaffold project | 120s |
| `/agents/execution/crisis` | POST | Handle crisis | **120s** |

#### 6.3.6 Frontend Component
```typescript
// ExecutionAgentCard.tsx
interface Props {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}
```

**Displays:**
- EDS score (large, color-coded)
- Status badge (healthy/at_risk/critical)
- Progress bar (0-100)
- Active blockers count
- Contributing factors (max 2)

**EDS Interpretation:**
| Score | Label | Color |
|-------|-------|-------|
| 0-20 | Excellent execution | Green |
| 21-40 | Good progress | Green |
| 41-60 | Needs attention | Orange |
| 61-80 | At risk | Orange |
| 81-100 | Critical | Red |

---

### 6.4 Awards Agent

#### 6.4.1 Purpose
Matches students to awards with ROI optimization. Target: >40% win rate.

#### 6.4.2 Award Match Schema
```typescript
interface AwardMatch {
  award_id: string;
  name: string;
  category: string;
  level: string;
  deadline: string;
  win_probability: number;    // 0-1, LLM-calculated
  roi: number;                // (prob × prestige × 100) / effort
  effort_hours: number;
  prestige_score: number;     // 1-10
  fit_reasons: string[];
  months_until_deadline: number;
}
```

#### 6.4.3 Portfolio Schema
```typescript
interface AwardPortfolio {
  likely: AwardMatch[];       // 60%+ probability
  target: AwardMatch[];       // 40-60% probability
  stretch: AwardMatch[];      // 20-40% probability
  total_recommended: number;
  expected_wins: number;      // Sum of probabilities
  total_effort_hours: number;
  strategy_notes: string[];
}
```

#### 6.4.4 Portfolio Strategy (Huda Model)
Balanced 2-2-1 portfolio:
- **2 Likely** (60%+ win): High confidence, foundation
- **2 Target** (40-60%): Competitive, achievable stretch
- **1 Stretch** (20-40%): High prestige, narrative-boosting

#### 6.4.5 API Endpoints
| Endpoint | Method | Description | Timeout |
|----------|--------|-------------|---------|
| `/agents/awards/match/{id}` | GET | Get award matches | 60s |
| `/agents/awards/portfolio/{id}` | GET | Get portfolio | 60s |

#### 6.4.6 Frontend Component
```typescript
// AwardsAgentCard.tsx
interface Props {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}
```

**Displays:**
- 3-tier grid: Likely (green), Target (amber), Stretch (orange)
- Expected wins count
- Strategy tip (first note)
- Total hours + total recommended

**Detail Modal Shows:**
- Full portfolio breakdown by tier
- Each award with:
  - Name, category, level
  - Win probability badge
  - Fit reasons
  - Deadline + effort hours + ROI
- Strategy notes list

---

### 6.5 Opportunity Agent

#### 6.5.1 Purpose
Matches students to summer programs with 6-month advance alerts and backup cascades.

#### 6.5.2 Opportunity Match Schema
```typescript
interface OpportunityMatch {
  opportunity_id: string;
  name: string;
  type: string;                     // summer_program, internship, etc.
  organization: string;
  fit_score: number;                // 0-1
  acceptance_probability: number;
  prestige_score: number;           // 1-10
  selectivity: number;              // 1-10
  fit_reasons: string[];
  deadline: string;
  duration: string;
  cost: string;
  touchpoints: number;
  months_until_deadline: number;
  recommendation: string;
}
```

#### 6.5.3 Alert Schema
```typescript
interface OpportunityAlert {
  alert_id: string;
  type: 'OPPORTUNITY_ALERT' | 'URGENT_DEADLINE';
  opportunity_id: string;
  opportunity_name: string;
  organization?: string;
  deadline: string;
  months_remaining: number;
  fit_score?: number;
  urgency: 'PREPARE_NOW' | 'URGENT';
  recommended_actions: string[];
  prep_start_date?: string;
  created_at: string;
}
```

#### 6.5.4 Alert Urgency Levels
| Months Out | Urgency | Color |
|------------|---------|-------|
| 6+ months | PREPARE_NOW | Orange |
| 3 months | URGENT | Red |
| 1 month | IMMINENT | Red (pulsing) |

#### 6.5.5 API Endpoints
| Endpoint | Method | Description | Timeout |
|----------|--------|-------------|---------|
| `/agents/opportunities/match/{id}` | GET | Get matches | 60s |
| `/agents/opportunities/alerts/{id}` | GET | Get alerts | 60s |

#### 6.5.6 Frontend Component
```typescript
// OpportunityAgentCard.tsx
interface Props {
  profileId: string;
  onChat?: () => void;
  onViewDetails?: (data: Record<string, unknown>) => void;
}
```

**Displays:**
- 2-column grid: Matches, Deadlines
- Urgent badge (if urgent_count > 0)
- Upcoming deadlines list (max 2)
- Top match preview with fit score

---

### 6.6 Crisis Agent

#### 6.6.1 Purpose
Transforms crises into opportunities using the VARC framework.

#### 6.6.2 VARC Framework
| Step | Duration | Purpose |
|------|----------|---------|
| **V**alidate | 2 seconds | Acknowledge emotion, normalize struggle |
| **A**ct | 10 seconds | Immediate actionable step (24-48 hours) |
| **R**eframe | 30 seconds | Narrative lens - advance identity |
| **C**reate | 2 minutes | New activity connected to narrative |

#### 6.6.3 Crisis Types
```typescript
const CRISIS_TYPES = [
  { id: 'blocker', label: 'Project Blocked' },
  { id: 'rejection', label: 'Rejection/Setback' },
  { id: 'overwhelm', label: 'Feeling Overwhelmed' },
  { id: 'deadline', label: 'Deadline Panic' },
  { id: 'doubt', label: 'Self-Doubt' },
];
```

#### 6.6.4 Input Schema
```typescript
interface CrisisInput {
  profile_id: string;
  crisis_type: string;
  description: string;
  urgency?: number;    // 1-5 scale
}
```

#### 6.6.5 API Endpoints
| Endpoint | Method | Description | Timeout |
|----------|--------|-------------|---------|
| `/agents/crisis-alchemy` | POST | Handle crisis | 120s |
| `/agents/handoff/approve` | POST | HITL approval | 60s |

#### 6.6.6 Frontend Components
```typescript
// CrisisAgentCard.tsx - Status display
// CrisisAlchemyModal.tsx - Crisis input + VARC response
```

**Card Displays:**
- Active crisis count OR "No Active Crises"
- VARC framework grid (V-A-R-C letters)
- "Report Crisis" button (red)

**Modal Flow:**
1. Crisis type selection
2. Description textarea
3. Urgency slider (1-5)
4. Submit → Show VARC response
5. If handoff required, show "Pending Review" badge

---

## PART 7: INTER-AGENT COMMUNICATION

### 7.1 Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT DEPENDENCY GRAPH                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                      ┌──────────────────┐                               │
│                      │   USER PROFILE   │                               │
│                      │   (Input Data)   │                               │
│                      └────────┬─────────┘                               │
│                               │                                          │
│                               ▼                                          │
│                      ┌──────────────────┐                               │
│                      │   ASSESSMENT     │                               │
│                      │     AGENT        │                               │
│                      │                  │                               │
│                      │ Output:          │                               │
│                      │ • narrative_dna  │                               │
│                      │ • hidden_target  │                               │
│                      │ • archetype      │                               │
│                      │ • themes         │                               │
│                      └────────┬─────────┘                               │
│                               │                                          │
│          ┌────────────────────┼────────────────────┐                    │
│          │                    │                    │                    │
│          ▼                    ▼                    ▼                    │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐             │
│  │  GAME PLAN    │   │    AWARDS     │   │ OPPORTUNITY   │             │
│  │    AGENT      │   │    AGENT      │   │    AGENT      │             │
│  │               │   │               │   │               │             │
│  │ Uses:         │   │ Uses:         │   │ Uses:         │             │
│  │ • narrative   │   │ • profile     │   │ • profile     │             │
│  │ • hidden_tgt  │   │ • narrative   │   │ • narrative   │             │
│  │               │   │               │   │               │             │
│  │ Output:       │   │ Output:       │   │ Output:       │             │
│  │ • activities  │   │ • portfolio   │   │ • matches     │             │
│  │ • seeds       │   │ • expected_   │   │ • alerts      │             │
│  │ • phases      │   │   wins        │   │ • cascades    │             │
│  └───────┬───────┘   └───────────────┘   └───────┬───────┘             │
│          │                                        │                     │
│          │                                        │                     │
│          ▼                                        ▼                     │
│  ┌───────────────┐                       ┌───────────────┐             │
│  │  EXECUTION    │                       │    CRISIS     │             │
│  │    AGENT      │◀─────────────────────▶│    AGENT      │             │
│  │               │                       │               │             │
│  │ Uses:         │                       │ Uses:         │             │
│  │ • activities  │                       │ • narrative   │             │
│  │               │                       │               │             │
│  │ Output:       │                       │ Output:       │             │
│  │ • projects    │      Crisis can       │ • VARC steps  │             │
│  │ • EDS         │◀──── trigger new ────▶│ • new_activity│             │
│  │ • blockers    │      activities       │ • handoff     │             │
│  └───────────────┘                       └───────────────┘             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Data Handoff Contracts

#### Assessment → Game Plan
```typescript
interface AssessmentToGamePlan {
  narrative_dna: string;
  hidden_target: string | null;
  archetype: string;
  themes: string[];
}
```

#### Game Plan → Execution
```typescript
interface GamePlanToExecution {
  activities: Activity[];
  identity_seeds: IdentitySeed[];
  target_completion_rate: number;  // 0.73 (73%)
}
```

#### Crisis → Game Plan
```typescript
interface CrisisToGamePlan {
  new_activity: {
    name: string;
    description: string;
    narrative_connection: string;
  };
  priority: 'high';
}
```

### 7.3 Event-Driven Communication

```typescript
// Event types for cross-agent communication
type AgentEvent =
  | 'assessment_complete'      // Assessment finished → trigger Game Plan
  | 'narrative_synthesized'    // Narrative ready → update Awards/Opportunity
  | 'gameplan_generated'       // Game Plan ready → update Execution
  | 'crisis_detected'          // Crisis reported → trigger Crisis Agent
  | 'handoff_requested'        // Agent needs human review
  | 'blocker_detected'         // Execution detected blocker
  | 'deadline_approaching'     // Opportunity alert triggered
  ;
```

---

## PART 8: FRONTEND COMPONENT SPECIFICATIONS

### 8.1 Component Hierarchy

```
app/dashboard/page.tsx
├── DashboardLayout
│   ├── DashboardSidebar
│   │   └── Navigation tabs
│   └── DashboardHeader
│       └── NotificationBell
│           └── NotificationPanel
├── Tab Content
│   └── MultiAgentTab
│       └── AgentDashboardV13
│           ├── Header (title, health, version, refresh)
│           ├── Agent Grid (2x3)
│           │   ├── AssessmentAgentCard
│           │   │   └── onClick → AgentDetailModal (assessment)
│           │   ├── GamePlanAgentCard
│           │   │   └── onClick → AgentDetailModal (gameplan)
│           │   ├── ExecutionAgentCard
│           │   │   └── onClick → AgentDetailModal (execution)
│           │   ├── AwardsAgentCard
│           │   │   └── onClick → AgentDetailModal (awards)
│           │   ├── OpportunityAgentCard
│           │   │   └── onClick → AgentDetailModal (opportunity)
│           │   └── CrisisAgentCard
│           │       ├── onClick → AgentDetailModal (crisis)
│           │       └── Report Crisis → CrisisAlchemyModal
│           └── AgentDetailModal
│               ├── AssessmentDetail
│               ├── GamePlanDetail
│               ├── ExecutionDetail
│               ├── AwardsDetail
│               ├── OpportunityDetail
│               └── CrisisDetail
└── CrisisAlchemyModal
    ├── CrisisTypeSelector
    ├── CrisisDescriptionInput
    ├── UrgencySlider
    └── CrisisResponseDisplay (VARC)
```

### 8.2 React Query Hook Configuration

```typescript
// hooks/useAgentData.ts

// Polling intervals
const STALE_TIMES = {
  health: 30_000,           // 30 seconds
  narrativeDna: 10 * 60_000, // 10 minutes
  gamePlan: 10 * 60_000,     // 10 minutes
  eds: 5 * 60_000,           // 5 minutes
  awards: 10 * 60_000,       // 10 minutes
  opportunities: 5 * 60_000, // 5 minutes
  alerts: 30_000,            // 30 seconds
  notifications: 30_000,     // 30 seconds
};

// Cache retention
const GC_TIMES = {
  gamePlan: 30 * 60_000,     // 30 minutes (expensive to regenerate)
  default: 10 * 60_000,      // 10 minutes
};

// Query options for slow endpoints
const SLOW_QUERY_OPTIONS = {
  retry: false,              // Don't retry on failure
  refetchOnWindowFocus: false,
  refetchOnMount: 'always',
};
```

### 8.3 State Management

```typescript
// Zustand stores used
import { useSessionStore } from '@/lib/store/useSessionStore';
// - profile_id: string | null
// - profile_status: 'none' | 'creating' | 'ready' | 'error'

import { useStudentStore } from '@/lib/store/useStudentStore';
// - profile: StudentProfile
// - assessment data

import { useResultsStore } from '@/lib/store/useResultsStore';
// - ivy_score
// - archetype
// - school_probabilities
```

---

## PART 9: API REFERENCE

### 9.1 Base Configuration

```typescript
const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8001';

// Timeout configuration
const API_TIMEOUT = 60000;        // Standard: 60 seconds
const API_TIMEOUT_LONG = 120000;  // LLM operations: 120 seconds
```

### 9.2 Complete Endpoint Reference

| Endpoint | Method | Timeout | Description |
|----------|--------|---------|-------------|
| **Health** |
| `/v13/health` | GET | 60s | Health check with version |
| **Assessment** |
| `/agents/narrative/{profile_id}` | GET | 60s | Get narrative DNA |
| `/agents/narrative/synthesize` | POST | 120s | Generate narrative |
| `/agents/assessment/enhance` | POST | 120s | Full assessment |
| **Game Plan** |
| `/agents/gameplan/generate` | POST | 120s | Generate game plan |
| `/agents/gameplan/activities/{id}` | GET | 60s | Get activities |
| `/agents/gameplan/seeds/{id}` | GET | 60s | Get identity seeds |
| **Execution** |
| `/agents/execution/eds/{id}` | GET | 60s | Get EDS score |
| `/agents/execution/blockers/{id}` | GET | 60s | Get blockers |
| `/agents/execution/scaffold` | POST | 120s | Scaffold project |
| `/agents/execution/crisis` | POST | 120s | Handle crisis |
| **Awards** |
| `/agents/awards/match/{id}` | GET | 60s | Get award matches |
| `/agents/awards/portfolio/{id}` | GET | 60s | Get portfolio |
| **Opportunity** |
| `/agents/opportunities/match/{id}` | GET | 60s | Get matches |
| `/agents/opportunities/alerts/{id}` | GET | 60s | Get alerts |
| **Crisis** |
| `/agents/crisis-alchemy` | POST | 120s | Handle crisis |
| `/agents/handoff/approve` | POST | 60s | HITL approval |
| **Notifications** |
| `/notifications/{id}` | GET | 60s | Get notifications |
| `/notifications/{id}/count` | GET | 60s | Get unread count |
| `/notifications/mark-read` | POST | 60s | Mark as read |

---

## PART 10: TESTING & VALIDATION

### 10.1 Agent Test Matrix

| Agent | Unit Tests | Integration Tests | E2E Tests | Status |
|-------|------------|-------------------|-----------|--------|
| Assessment | 15+ | 5 | 2 | ✅ Tested |
| Game Plan | 12+ | 5 | 2 | ✅ Tested |
| Execution | 10+ | 4 | 2 | ✅ Tested |
| Awards | 8+ | 3 | 1 | ✅ Tested |
| Opportunity | 8+ | 3 | 1 | ✅ Tested |
| Crisis | 10+ | 5 | 2 | ✅ Tested |

### 10.2 Quality Gate Validation

```python
# tests/test_quality_gates.py

def test_threshold_values():
    assert QualityThresholds.MIN_QUALITY_SCORE == 70
    assert QualityThresholds.MIN_VOICE_SCORE == 70
    assert QualityThresholds.MIN_GOLDEN_SIMILARITY == 0.6

def test_observation_passes_thresholds():
    obs = Observation(quality_score=75, voice_score=75, golden_similarity=0.65)
    assert obs.passes_thresholds is True

    obs_fail = Observation(quality_score=69, voice_score=70, golden_similarity=0.6)
    assert obs_fail.passes_thresholds is False
```

### 10.3 Huda Benchmarks

| Metric | Target | Huda Actual | Status |
|--------|--------|-------------|--------|
| Project Completion | >80% | 100% | ✅ |
| Crisis Recovery | <72 hours | <2 hours | ✅ |
| Task Completion | >70% | 73% | ✅ |
| EDS Score | <50 | 12 | ✅ |
| Award Win Rate | >40% | 62.5% (5/8) | ✅ |

### 10.4 Frontend Component Tests

| Component | Tests | Coverage |
|-----------|-------|----------|
| AgentCardBase | Click handler, loading state, error state | ✅ |
| AgentDetailModal | Open/close, escape key, content switch | ✅ |
| AwardsDetail | Tier rendering, award items, strategy notes | ✅ |
| CrisisAlchemyModal | Form submission, VARC display, HITL badge | ✅ |

### 10.5 API Integration Tests

```bash
# Run smoke tests
cd agents && pytest tests/test_smoke.py -v

# Expected results:
# - test_health_endpoint: PASS (v15.0.0)
# - test_health_thresholds: PASS (70/70/0.6)
# - test_version_string: PASS (15.0.0)
```

---

## APPENDIX A: File Inventory

### Agent Backend Files
| File | Lines | Description |
|------|-------|-------------|
| `agents/agents/assessment.py` | ~600 | Assessment agent |
| `agents/agents/narrative_synthesis.py` | ~450 | Narrative synthesis |
| `agents/agents/gameplan.py` | ~1000 | Game plan generation |
| `agents/agents/execution.py` | ~500 | Execution + crisis |
| `agents/agents/awards.py` | ~800 | Awards matching |
| `agents/agents/opportunity.py` | ~650 | Opportunity matching |

### Frontend Components
| File | Lines | Description |
|------|-------|-------------|
| `components/agents/AgentDashboardV13.tsx` | ~230 | Main dashboard |
| `components/agents/AgentDetailModal.tsx` | ~550 | Detail modal |
| `components/agents/cards/AgentCardBase.tsx` | ~120 | Base card |
| `components/agents/cards/*.tsx` | ~150 each | Individual cards |
| `components/agents/CrisisAlchemyModal.tsx` | ~400 | Crisis UI |

### Hooks & API
| File | Lines | Description |
|------|-------|-------------|
| `hooks/useAgentData.ts` | ~500 | React Query hooks |
| `lib/api/agentClient.ts` | ~200 | API client |

---

*IvyQuest Multi-Agent System Specification v15.0*
*Complete UI/UX, Data Flow, Message Sequences & Agent Design*
*Date: January 12, 2026*
