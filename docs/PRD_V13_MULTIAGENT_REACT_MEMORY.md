# IvyQuest v13.0 Product Requirements Document
## Multi-Agent + ReAct + Memory Platform

**Version:** 13.0.0
**Date:** January 11, 2026
**Status:** Implementation Specification
**Author:** Claude Code

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Platform Baseline](#2-current-platform-baseline)
3. [Jobs To Be Done (JTBD)](#3-jobs-to-be-done-jtbd)
4. [UI/UX Specifications](#4-uiux-specifications)
5. [Technical Specifications](#5-technical-specifications)
6. [Migration Roadmap](#6-migration-roadmap)
7. [Success Metrics](#7-success-metrics)

---

## 1. Executive Summary

### 1.1 Vision Statement

IvyQuest v13.0 represents a paradigm shift from reactive endpoint-based agents to **autonomous, memory-enabled AI agents** that think, learn, and adapt. This platform combines:

- **ReAct Framework**: Think → Action → Observe → Learn → Self-Correct
- **3-Tier Memory Architecture**: Working buffer, Short-term (Redis), Long-term (Supabase/pgvector)
- **Agno Runtime Spine**: Stateful agent management with cross-agent communication
- **Jenny Voice Integration**: Consistent, warm, agency-preserving communication style

### 1.2 Key Differentiators

| Feature | v2.0 (Current) | v13.0 (Target) |
|---------|---------------|----------------|
| Agent Architecture | Stateless endpoints | Stateful ReAct agents |
| Memory | None | 3-tier persistent memory |
| Learning | None | Observation-based adaptation |
| Cross-Agent Communication | None | Event-driven messaging |
| Human-in-the-Loop | None | Full HITL workflow |
| Voice Consistency | Manual validation | Embedded Jenny Voice layer |

### 1.3 Success Criteria

- **Agent Autonomy**: 80% of tasks completed without human intervention
- **Memory Recall**: 95% accuracy on student context retrieval
- **Jenny Voice Score**: ≥8.0/10 across all agent outputs
- **Response Time**: <2s for cached memory, <5s for cold start
- **User Satisfaction**: 4.5/5 on agent helpfulness rating

---

## 2. Current Platform Baseline

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT v2.0 ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Next.js    │    │   FastAPI    │    │   Supabase   │       │
│  │   Frontend   │───▶│   Backend    │───▶│   Database   │       │
│  │   (React)    │    │   (Python)   │    │  (Postgres)  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                                    │
│         ▼                   ▼                                    │
│  ┌──────────────┐    ┌──────────────┐                           │
│  │   Zustand    │    │   Agno       │                           │
│  │   State      │    │   Agents     │                           │
│  │   Store      │    │   (Basic)    │                           │
│  └──────────────┘    └──────────────┘                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Implemented Components

#### 2.2.1 Backend Agents (100% Complete)

| Agent | Endpoint | Status | Description |
|-------|----------|--------|-------------|
| TimeAudit | `/agents/time-audit` | ✅ | 168-hour framework analysis |
| WeeklyPlan | `/agents/weekly-plan` | ✅ | P0/P1/P2 prioritized planning |
| AwardsPortfolio | `/agents/awards/portfolio` | ✅ | 2-2-1 portfolio builder |
| NCWITStrategy | `/agents/ncwit-strategy` | ✅ | Essay strategy generator |
| ProgramRecommend | `/agents/opportunities/recommend` | ✅ | Opportunity matching |
| CrisisAlchemy | `/agents/crisis-alchemy` | ✅ | Crisis response system |
| JennyVoice | `/validation/jenny-voice` | ✅ | 6-dimension voice validator |
| NarrativeSynthesis | `/agents/narrative/synthesize` | ✅ | Brand statement generator |
| HealthCheck | `/health` | ✅ | Service health monitor |

#### 2.2.2 Frontend Components (25% Complete)

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| TimeAuditCardV2 | `components/agents/TimeAuditCardV2.tsx` | ✅ | Fully functional |
| AwardsPortfolioCardV2 | `components/agents/AwardsPortfolioCardV2.tsx` | ✅ | Fully functional |
| CrisisAlchemyModal | `components/agents/CrisisAlchemyModal.tsx` | ✅ | Fully functional |
| MultiAgentsTab | `components/tabs/MultiAgentsTab.tsx` | ⚠️ | Dashboard/Chat hybrid |
| V2TestPanel | `components/debug/V2TestPanel.tsx` | ✅ | 9/9 tests passing |
| WeeklyPlanCard | - | ❌ | Not implemented |
| NCWITStrategyCard | - | ❌ | Not implemented |
| OpportunitiesCard | - | ❌ | Not implemented |
| NarrativeSynthesisCard | - | ❌ | Not implemented |

#### 2.2.3 Data Flow Architecture

```
Current Data Flow:
─────────────────
User Input → Assessment Form → Supabase (profiles) → Dashboard
                                      ↓
                              agentV2Client.ts → FastAPI Endpoints
                                      ↓
                              Component Cards (limited)
```

### 2.3 Known Limitations

1. **No Memory Persistence**: Agents forget context between calls
2. **No Cross-Agent Communication**: Agents operate in isolation
3. **No Learning Loop**: No observation-based improvement
4. **Limited HITL**: No workflow for human review/override
5. **Inconsistent Profile Flow**: profile_id not reliably passed
6. **Missing Agent Cards**: 6 of 9 agent features not surfaced in UI

---

## 3. Jobs To Be Done (JTBD)

### 3.1 JTBD Framework Overview

The JTBD framework identifies the core "jobs" students hire IvyQuest to accomplish. Each job maps to specific agent capabilities and UI surfaces.

### 3.2 Primary Jobs

#### Job 1: "Help me understand my unique value proposition"

**Context**: High-achieving students struggle to articulate what makes them distinctive in a sea of similar applicants.

**Functional Requirements**:
- Synthesize activities, experiences, and identity into a coherent narrative
- Identify 2-3 differentiating "spikes" from raw data
- Generate a brand statement that resonates emotionally
- Provide archetype classification with confidence scores

**Emotional Requirements**:
- Feel understood and validated
- Gain clarity without feeling boxed in
- Experience "aha" moment of self-discovery

**Agent Mapping**:
| Agent | Role | Output |
|-------|------|--------|
| NarrativeSynthesis | Primary | Brand statement, themes, archetype |
| Assessment | Supporting | Raw factor analysis, identity extraction |

**UI Surface**: `NarrativeSynthesisCard` → Dashboard prominent placement

**Success Metric**: User can recite their brand statement from memory within 24 hours

---

#### Job 2: "Help me build a winning awards portfolio"

**Context**: Students don't know which awards to pursue or how to balance risk across likely/target/stretch categories.

**Functional Requirements**:
- Analyze profile fit against 50+ award opportunities
- Calculate probability scores with competition factors
- Build 2-2-1 portfolio (2 likely, 2 target, 1 stretch)
- Provide deadline-aware timeline
- Track application progress

**Emotional Requirements**:
- Feel strategic rather than overwhelmed
- Confidence in portfolio balance
- Excitement about achievable wins

**Agent Mapping**:
| Agent | Role | Output |
|-------|------|--------|
| AwardsPortfolio | Primary | Tiered portfolio, probability scores |
| Opportunity | Supporting | Alternative recommendations |

**UI Surface**: `AwardsPortfolioCardV2` → Multi-Agents Dashboard

**Success Metric**: Expected wins ≥2.5 per portfolio, balance score ≥7.5/10

---

#### Job 3: "Help me manage my time effectively"

**Context**: Students are overwhelmed with commitments and don't know how to fit passion projects into their schedule.

**Functional Requirements**:
- Audit 168-hour weekly budget
- Identify recoverable time (social media, inefficiencies)
- Calculate passion hours available
- Generate efficiency hacks with Jenny voice
- Create weekly P0/P1/P2 prioritized plans

**Emotional Requirements**:
- Relief from overwhelm
- Agency over schedule
- Optimism about what's possible

**Agent Mapping**:
| Agent | Role | Output |
|-------|------|--------|
| TimeAudit | Primary | Hour breakdown, efficiency hacks |
| WeeklyPlan | Supporting | Prioritized task plan |

**UI Surface**: `TimeAuditCardV2` + `WeeklyPlanCard` → Multi-Agents Dashboard

**Success Metric**: ≥10 passion hours identified per week

---

#### Job 4: "Help me navigate crises and setbacks"

**Context**: Students experience rejection, failure, and anxiety that derails their progress.

**Functional Requirements**:
- Classify crisis type (rejection, burnout, impostor syndrome, etc.)
- Provide immediate validation and micro-action
- Reframe crisis into growth narrative
- Suggest pivot activities aligned with spike

**Emotional Requirements**:
- Feel heard and validated
- Move from paralysis to action
- See crisis as opportunity

**Agent Mapping**:
| Agent | Role | Output |
|-------|------|--------|
| CrisisAlchemy | Primary | Crisis response, pivot activity |
| Narrative | Supporting | Reframe in context of brand |

**UI Surface**: `CrisisAlchemyModal` → Floating action button access

**Success Metric**: 80% of students take suggested micro-action within 24 hours

---

#### Job 5: "Help me win specific competitions"

**Context**: Students need targeted strategies for high-value competitions like NCWIT, Regeneron, Google Science Fair.

**Functional Requirements**:
- Analyze competition rubric and past winners
- Map student profile to competition criteria
- Generate essay/application strategy
- Identify vulnerability and identity multipliers
- Provide sensory detail suggestions

**Emotional Requirements**:
- Feel prepared and strategic
- Confidence in unique angle
- Excitement about competitive edge

**Agent Mapping**:
| Agent | Role | Output |
|-------|------|--------|
| NCWITStrategy | Primary | Essay structure, vulnerability formula |
| Narrative | Supporting | Identity layer integration |

**UI Surface**: `NCWITStrategyCard` → Competition-specific view

**Success Metric**: 40% improvement in competition advancement rate

---

#### Job 6: "Help me find the right opportunities"

**Context**: Students waste time and money on programs that don't align with their goals or spike.

**Functional Requirements**:
- Match profile to 4-tier opportunity hierarchy
- Detect and redirect from paid programs to free alternatives
- Provide self-directed options for every recommendation
- Track opportunity pipeline

**Emotional Requirements**:
- Trust in recommendations
- Financial relief (avoiding costly programs)
- Excitement about aligned opportunities

**Agent Mapping**:
| Agent | Role | Output |
|-------|------|--------|
| Opportunity | Primary | Tiered recommendations, redirect logic |
| Awards | Supporting | Competition opportunities |

**UI Surface**: `OpportunitiesCard` → Multi-Agents Dashboard

**Success Metric**: 70% of students pursue recommended free programs

---

### 3.3 JTBD → Agent → UI Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JTBD → AGENT → UI MATRIX                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Job 1: Value Proposition                                                    │
│  ├── NarrativeSynthesis Agent ──▶ NarrativeSynthesisCard                    │
│  └── Assessment Agent ──────────▶ AssessmentTab (existing)                  │
│                                                                              │
│  Job 2: Awards Portfolio                                                     │
│  ├── AwardsPortfolio Agent ─────▶ AwardsPortfolioCardV2 ✅                  │
│  └── Opportunity Agent ─────────▶ Related opportunities section             │
│                                                                              │
│  Job 3: Time Management                                                      │
│  ├── TimeAudit Agent ───────────▶ TimeAuditCardV2 ✅                        │
│  └── WeeklyPlan Agent ──────────▶ WeeklyPlanCard (NEW)                      │
│                                                                              │
│  Job 4: Crisis Navigation                                                    │
│  ├── CrisisAlchemy Agent ───────▶ CrisisAlchemyModal ✅                     │
│  └── Narrative Agent ───────────▶ Reframe integration                       │
│                                                                              │
│  Job 5: Competition Strategy                                                 │
│  ├── NCWITStrategy Agent ───────▶ NCWITStrategyCard (NEW)                   │
│  └── Narrative Agent ───────────▶ Identity layer overlay                    │
│                                                                              │
│  Job 6: Opportunity Discovery                                                │
│  ├── Opportunity Agent ─────────▶ OpportunitiesCard (NEW)                   │
│  └── Awards Agent ──────────────▶ Competition section                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. UI/UX Specifications

### 4.1 Design System Integration

#### 4.1.1 Brand Colors (from CLAUDE.md)

```typescript
// lib/constants/brand.ts
export const BRAND_COLORS = {
  // Primary palette
  primary: '#FF4A23',        // Ivylevel orange - main accent
  secondary: '#641432',      // Ivylevel maroon - headings

  // Text hierarchy
  textHeading: '#641432',    // Maroon for headings
  textPrimary: '#374151',    // Gray-700 for body
  textMuted: '#9ca3af',      // Gray-400 for captions

  // Backgrounds
  bgPrimary: 'rgba(255, 255, 255, 0.95)',
  primaryBg: 'rgba(255, 74, 35, 0.1)',  // Light orange
  bgSuccess: 'rgba(22, 163, 74, 0.1)',  // Light green
  bgWarning: 'rgba(217, 119, 6, 0.1)',  // Light amber
  bgError: 'rgba(220, 38, 38, 0.1)',    // Light red

  // Borders
  borderLight: '#e5e7eb',    // Gray-200
  borderDefault: '#d1d5db',  // Gray-300
};
```

#### 4.1.2 Card Component Standard

All agent cards follow this structure:

```tsx
interface AgentCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;              // Agent accent color
  isLoading?: boolean;
  error?: string;
  children: React.ReactNode;  // Card body content
  actions?: React.ReactNode;  // Footer actions
  badge?: {                   // Status badge
    label: string;
    variant: 'success' | 'warning' | 'error' | 'info';
  };
}
```

### 4.2 Agent Card Specifications

#### 4.2.1 NarrativeSynthesisCard (NEW)

**Purpose**: Display synthesized brand statement and narrative DNA

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│ 📖 Your Story DNA                              [Regenerate] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ARCHETYPE                                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🎭 The Technical Humanist                    85% conf  │ │
│  │ You blend deep technical skills with genuine          │ │
│  │ empathy for human impact...                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  BRAND STATEMENT                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ "I'm the kid who debugs code with the same care I     │ │
│  │  use to debug people's problems..."                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  THEMES                                                      │
│  ┌──────────┐ ┌──────────────┐ ┌─────────────────┐         │
│  │ Impact   │ │ Innovation   │ │ Community       │         │
│  └──────────┘ └──────────────┘ └─────────────────┘         │
│                                                              │
│  IDENTITY SEEDS                                              │
│  • First-generation technologist                             │
│  • Bilingual bridge-builder                                  │
│  • Crisis responder                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Data Contract**:
```typescript
interface NarrativeSynthesisData {
  brand_statement: string;
  narrative_dna: string;
  first_principle: string;
  themes: string[];
  identity_seeds: string[];
  archetype: string;
  archetype_description: string;
  confidence: number;
}
```

---

#### 4.2.2 WeeklyPlanCard (NEW)

**Purpose**: Display prioritized weekly tasks with P0/P1/P2 breakdown

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│ 📅 This Week's Plan                              [Refresh]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Week of Jan 13, 2026                                        │
│                                                              │
│  ⏱️ Available: 24 hrs  │  📊 Planned: 18 hrs  │  Buffer: 6h │
│                                                              │
│  P0 - MUST COMPLETE                              🔴 8 hrs   │
│  ├─ NCWIT Essay Draft                           3 hrs       │
│  ├─ Science Fair Poster                         4 hrs       │
│  └─ College App Review                          1 hr        │
│                                                              │
│  P1 - SHOULD COMPLETE                            🟡 7 hrs   │
│  ├─ Research Paper Outline                      2 hrs       │
│  ├─ Club Meeting Prep                           1.5 hrs     │
│  └─ SAT Practice                                3.5 hrs     │
│                                                              │
│  P2 - IF TIME PERMITS                            🟢 3 hrs   │
│  ├─ Read 2 chapters                             1.5 hrs     │
│  └─ Portfolio updates                           1.5 hrs     │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│  💡 "You've got this! Focus on P0 first, and don't         │
│     stress about P2 - those are bonus wins!"               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Data Contract**:
```typescript
interface WeeklyPlanData {
  week_start: string;
  p0_must_complete: TaskItem[];
  p1_should_complete: TaskItem[];
  p2_if_time_permits: TaskItem[];
  total_hours_estimated: number;
  available_hours: number;
  buffer_hours: number;
  flexibility_note: string;  // Jenny-voiced encouragement
}

interface TaskItem {
  name: string;
  estimated_hours: number;
  deadline?: string;
  category?: string;
}
```

---

#### 4.2.3 NCWITStrategyCard (NEW)

**Purpose**: Display NCWIT-specific essay strategy and coaching

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│ 🏆 NCWIT Strategy                                [Refresh]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  YOUR IDENTITY MULTIPLIERS                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🎯 First-gen + STEM pioneer = 2.5x multiplier        │   │
│  │                                                       │   │
│  │ Identity Layers:                                      │   │
│  │ • First-generation college student                    │   │
│  │ • Only girl in robotics club                          │   │
│  │ • Immigrant background                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  VULNERABILITY ANGLES                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ✨ "The moment I realized I was different..."         │   │
│  │ ✨ "When my code broke and so did I..."               │   │
│  │ ✨ "The failure that became my fuel..."               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ESSAY 1 STRUCTURE (400 words)                               │
│  1. Opening hook: Sensory detail moment                      │
│  2. Identity revelation: First-gen perspective               │
│  3. Technical challenge: Project struggle                    │
│  4. Transformation: What you learned                         │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│  🎤 Jenny's Coaching:                                        │
│  "Your story isn't about proving you belong—it's about      │
│   showing them what they're missing without you!"           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

#### 4.2.4 OpportunitiesCard (NEW)

**Purpose**: Display tiered opportunity recommendations with redirect logic

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│ 💡 Opportunities For You                         [Refresh]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🥇 TIER 1: SELECTIVE FREE                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ MIT PRIMES                                    ⭐ 92%  │   │
│  │ Research program for high schoolers                  │   │
│  │ Fit: Your math olympiad + research interest         │   │
│  │ [Learn More]                                         │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Google CSSI                                   ⭐ 88%  │   │
│  │ Summer CS intensive                                  │   │
│  │ Fit: Your coding projects + first-gen status        │   │
│  │ [Learn More]                                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  🥈 TIER 2: GOVERNMENT PROGRAMS                              │
│  • NSLC Medical - 85% fit                                   │
│  • NASA High School Internship - 82% fit                    │
│                                                              │
│  ⚠️ REDIRECT ALERT                                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🚫 [Expensive Summer Camp] - $5,000                  │   │
│  │ Instead, try: MIT OpenCourseWare (FREE) or           │   │
│  │ Start your own research project!                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 4.3 Multi-Agents Dashboard Layout

#### 4.3.1 Desktop Layout (≥1024px)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Multi-Agent Intelligence                    v2.0: healthy   [Crisis Help]  │
│                                                          [Dashboard] [Chat] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐           │
│  │                             │  │                             │           │
│  │   NarrativeSynthesisCard    │  │   AwardsPortfolioCardV2     │           │
│  │   (Your Story DNA)          │  │   (2-2-1 Portfolio)         │           │
│  │                             │  │                             │           │
│  └─────────────────────────────┘  └─────────────────────────────┘           │
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐           │
│  │                             │  │                             │           │
│  │   TimeAuditCardV2           │  │   WeeklyPlanCard            │           │
│  │   (168-Hour Framework)      │  │   (P0/P1/P2 Tasks)          │           │
│  │                             │  │                             │           │
│  └─────────────────────────────┘  └─────────────────────────────┘           │
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐           │
│  │                             │  │                             │           │
│  │   NCWITStrategyCard         │  │   OpportunitiesCard         │           │
│  │   (Competition Strategy)    │  │   (Tiered Recommendations)  │           │
│  │                             │  │                             │           │
│  └─────────────────────────────┘  └─────────────────────────────┘           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.3.2 Mobile Layout (<768px)

Single column with collapsible cards, prioritized by JTBD importance:
1. NarrativeSynthesisCard (Job 1)
2. AwardsPortfolioCard (Job 2)
3. TimeAuditCard (Job 3)
4. Crisis Help floating button (Job 4)
5. Remaining cards in expandable accordion

### 4.4 Memory Integration UI

#### 4.4.1 Memory Status Indicator

```
┌─────────────────────────────────────────────────────────────┐
│ 🧠 Agent Memory                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Working Memory     ████████░░ 80%   12 items               │
│  Short-term (Redis) ████░░░░░░ 40%   45 items (24h cache)   │
│  Long-term (DB)     ██████████ 100%  234 items              │
│                                                              │
│  Last sync: 2 minutes ago                   [Sync Now]      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 4.4.2 Memory Recall Display

When an agent uses memory, show inline indicator:

```
┌─────────────────────────────────────────────────────────────┐
│ 💭 Jenny remembers:                                          │
│ • You mentioned feeling overwhelmed last Tuesday            │
│ • Your NCWIT essay is due in 12 days                        │
│ • You prefer morning study sessions                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Specifications

### 5.1 Architecture Overview (v13.0)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         v13.0 ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           FRONTEND (Next.js)                            ││
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           ││
│  │  │ Dashboard  │ │ Agent Cards│ │ Chat UI    │ │ Memory UI  │           ││
│  │  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘           ││
│  │        │              │              │              │                   ││
│  │        └──────────────┴──────────────┴──────────────┘                   ││
│  │                              │                                          ││
│  │                    ┌─────────▼─────────┐                                ││
│  │                    │   agentV2Client   │                                ││
│  │                    │   (TypeScript)    │                                ││
│  │                    └─────────┬─────────┘                                ││
│  └──────────────────────────────┼──────────────────────────────────────────┘│
│                                 │                                            │
│                                 │ HTTP/WebSocket                             │
│                                 │                                            │
│  ┌──────────────────────────────▼──────────────────────────────────────────┐│
│  │                           BACKEND (FastAPI)                             ││
│  │                                                                         ││
│  │  ┌─────────────────────────────────────────────────────────────────┐   ││
│  │  │                      AGNO RUNTIME SPINE                         │   ││
│  │  │                                                                  │   ││
│  │  │  ┌──────────────────────────────────────────────────────────┐   │   ││
│  │  │  │                   ReAct Base Agent                       │   │   ││
│  │  │  │  ┌───────┐ ┌───────┐ ┌─────────┐ ┌───────┐ ┌──────────┐ │   │   ││
│  │  │  │  │ Think │→│ Action│→│ Observe │→│ Learn │→│ Self-Corr│ │   │   ││
│  │  │  │  └───────┘ └───────┘ └─────────┘ └───────┘ └──────────┘ │   │   ││
│  │  │  └──────────────────────────────────────────────────────────┘   │   ││
│  │  │                              │                                   │   ││
│  │  │  ┌───────────┬───────────┬──┴────────┬───────────┬───────────┐ │   ││
│  │  │  │ Narrative │ Awards    │ Time      │ Crisis    │ Opportunity│ │   ││
│  │  │  │ Agent     │ Agent     │ Agent     │ Agent     │ Agent      │ │   ││
│  │  │  └───────────┴───────────┴───────────┴───────────┴───────────┘ │   ││
│  │  │                                                                  │   ││
│  │  └─────────────────────────────────────────────────────────────────┘   ││
│  │                              │                                          ││
│  │  ┌───────────────────────────▼───────────────────────────────────────┐ ││
│  │  │                      3-TIER MEMORY SYSTEM                         │ ││
│  │  │                                                                    │ ││
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │ ││
│  │  │  │   Working    │  │  Short-term  │  │      Long-term           │ │ ││
│  │  │  │   Buffer     │──│   (Redis)    │──│    (Supabase/pgvector)   │ │ ││
│  │  │  │   (In-mem)   │  │   24h TTL    │  │    Semantic search       │ │ ││
│  │  │  └──────────────┘  └──────────────┘  └──────────────────────────┘ │ ││
│  │  └────────────────────────────────────────────────────────────────────┘ ││
│  │                                                                         ││
│  │  ┌─────────────────────────────────────────────────────────────────┐   ││
│  │  │                    JENNY VOICE LAYER                            │   ││
│  │  │  All agent outputs pass through 6-dimension voice validation   │   ││
│  │  └─────────────────────────────────────────────────────────────────┘   ││
│  │                                                                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 ReAct Agent Framework

#### 5.2.1 Base Agent Class

```python
# agents/core/react_base.py

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from pydantic import BaseModel
from agno import Agent, RunContext
from .memory import MemoryManager
from .voice import JennyVoiceValidator

T = TypeVar('T', bound=BaseModel)

class ReActAgent(Agent, Generic[T], ABC):
    """
    Base class for all ReAct-enabled agents.
    Implements: Think → Action → Observe → Learn → Self-Correct
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        memory: MemoryManager,
        voice_validator: JennyVoiceValidator,
    ):
        super().__init__(name=name, description=description)
        self.agent_id = agent_id
        self.memory = memory
        self.voice = voice_validator
        self.max_iterations = 5
        self.thought_log: list[str] = []

    async def run(self, context: RunContext, input_data: T) -> dict:
        """
        Main ReAct loop execution.
        """
        iteration = 0
        observation = None

        while iteration < self.max_iterations:
            # THINK: Analyze current state and plan
            thought = await self._think(context, input_data, observation)
            self.thought_log.append(thought)

            # ACTION: Execute planned action
            action_result = await self._action(context, input_data, thought)

            # OBSERVE: Analyze action results
            observation = await self._observe(context, action_result)

            # Check if task is complete
            if self._is_complete(observation):
                break

            # LEARN: Update memory with insights
            await self._learn(context, observation)

            # SELF-CORRECT: Adjust strategy if needed
            if self._needs_correction(observation):
                await self._self_correct(context, observation)

            iteration += 1

        # Generate final output with Jenny voice
        output = await self._generate_output(context, input_data)
        validated_output = await self.voice.validate_and_transform(output)

        return validated_output

    @abstractmethod
    async def _think(
        self,
        context: RunContext,
        input_data: T,
        last_observation: dict | None
    ) -> str:
        """Generate reasoning about current state and next action."""
        pass

    @abstractmethod
    async def _action(
        self,
        context: RunContext,
        input_data: T,
        thought: str
    ) -> dict:
        """Execute the planned action."""
        pass

    @abstractmethod
    async def _observe(
        self,
        context: RunContext,
        action_result: dict
    ) -> dict:
        """Analyze action results and extract insights."""
        pass

    async def _learn(self, context: RunContext, observation: dict) -> None:
        """Store insights in memory for future use."""
        await self.memory.store_observation(
            agent_id=self.agent_id,
            profile_id=context.profile_id,
            observation=observation
        )

    async def _self_correct(self, context: RunContext, observation: dict) -> None:
        """Adjust strategy based on failed or suboptimal outcomes."""
        correction = await self._generate_correction(observation)
        self.thought_log.append(f"[CORRECTION] {correction}")

    @abstractmethod
    def _is_complete(self, observation: dict) -> bool:
        """Check if the task is complete."""
        pass

    @abstractmethod
    def _needs_correction(self, observation: dict) -> bool:
        """Determine if self-correction is needed."""
        pass

    @abstractmethod
    async def _generate_output(
        self,
        context: RunContext,
        input_data: T
    ) -> dict:
        """Generate final output after ReAct loop."""
        pass
```

#### 5.2.2 Agent Implementation Example

```python
# agents/agents/narrative_react.py

from .core.react_base import ReActAgent
from pydantic import BaseModel

class NarrativeInput(BaseModel):
    profile_id: str
    assessment_contract: dict | None = None

class NarrativeReActAgent(ReActAgent[NarrativeInput]):
    """
    ReAct-enabled Narrative Synthesis Agent.
    Synthesizes brand statement, themes, and archetype from profile data.
    """

    def __init__(self, memory: MemoryManager, voice: JennyVoiceValidator):
        super().__init__(
            agent_id="narrative",
            name="Narrative Synthesis Agent",
            description="Synthesizes compelling personal narratives from student profiles",
            memory=memory,
            voice_validator=voice,
        )

    async def _think(
        self,
        context: RunContext,
        input_data: NarrativeInput,
        last_observation: dict | None
    ) -> str:
        # Retrieve relevant memories
        memories = await self.memory.recall(
            profile_id=input_data.profile_id,
            query="narrative synthesis themes identity",
            limit=5
        )

        # Generate thought based on context
        thought = f"""
        Analyzing profile {input_data.profile_id}:
        - Previous insights: {len(memories)} relevant memories
        - Assessment data available: {input_data.assessment_contract is not None}
        - Last observation: {last_observation}

        Plan: Extract identity layers, identify themes, synthesize brand statement
        """
        return thought

    async def _action(
        self,
        context: RunContext,
        input_data: NarrativeInput,
        thought: str
    ) -> dict:
        # Load profile data
        profile = await self._load_profile(input_data.profile_id)

        # Extract identity layers
        identity = await self._extract_identity_layers(profile)

        # Identify themes
        themes = await self._identify_themes(profile, identity)

        # Generate brand statement
        brand_statement = await self._synthesize_brand(
            profile, identity, themes
        )

        return {
            "identity_layers": identity,
            "themes": themes,
            "brand_statement": brand_statement,
            "confidence": self._calculate_confidence(profile)
        }

    async def _observe(
        self,
        context: RunContext,
        action_result: dict
    ) -> dict:
        return {
            "success": len(action_result["themes"]) >= 2,
            "confidence": action_result["confidence"],
            "needs_more_data": action_result["confidence"] < 0.7,
            "action_result": action_result
        }

    def _is_complete(self, observation: dict) -> bool:
        return observation["success"] and observation["confidence"] >= 0.7

    def _needs_correction(self, observation: dict) -> bool:
        return not observation["success"] or observation["needs_more_data"]

    async def _generate_output(
        self,
        context: RunContext,
        input_data: NarrativeInput
    ) -> dict:
        # Get final action result from thought log
        final_result = self.thought_log[-1] if self.thought_log else {}

        return {
            "success": True,
            "brand_statement": final_result.get("brand_statement", ""),
            "narrative_dna": self._generate_dna(final_result),
            "first_principle": self._extract_first_principle(final_result),
            "themes": final_result.get("themes", []),
            "identity_seeds": final_result.get("identity_layers", []),
            "archetype": self._classify_archetype(final_result),
            "archetype_description": self._describe_archetype(final_result),
            "confidence": final_result.get("confidence", 0.8)
        }
```

### 5.3 Memory System Architecture

#### 5.3.1 Memory Manager

```python
# agents/core/memory.py

from typing import Optional
from datetime import datetime, timedelta
import json
import redis.asyncio as redis
from supabase import Client as SupabaseClient
import numpy as np

class MemoryManager:
    """
    3-tier memory system:
    - Working: In-memory buffer for current session
    - Short-term: Redis with 24h TTL
    - Long-term: Supabase with pgvector for semantic search
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        supabase_client: SupabaseClient,
        embedding_model: EmbeddingModel,
    ):
        self.redis = redis_client
        self.supabase = supabase_client
        self.embeddings = embedding_model
        self.working_memory: dict[str, list] = {}
        self.short_term_ttl = timedelta(hours=24)

    async def store_observation(
        self,
        agent_id: str,
        profile_id: str,
        observation: dict,
        importance: float = 0.5,
    ) -> str:
        """
        Store an observation in all three memory tiers.
        Returns memory_id for reference.
        """
        memory_id = f"{agent_id}:{profile_id}:{datetime.utcnow().timestamp()}"

        # Serialize observation
        content = json.dumps(observation)
        embedding = await self.embeddings.encode(content)

        # Tier 1: Working memory (current session)
        if profile_id not in self.working_memory:
            self.working_memory[profile_id] = []
        self.working_memory[profile_id].append({
            "id": memory_id,
            "agent_id": agent_id,
            "content": observation,
            "importance": importance,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Tier 2: Short-term (Redis, 24h TTL)
        await self.redis.setex(
            f"memory:{memory_id}",
            self.short_term_ttl,
            json.dumps({
                "content": observation,
                "embedding": embedding.tolist(),
                "importance": importance,
            })
        )

        # Tier 3: Long-term (Supabase, persistent)
        await self.supabase.table("agent_memories").insert({
            "id": memory_id,
            "agent_id": agent_id,
            "profile_id": profile_id,
            "content": observation,
            "embedding": embedding.tolist(),
            "importance": importance,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

        return memory_id

    async def recall(
        self,
        profile_id: str,
        query: str,
        limit: int = 10,
        min_importance: float = 0.0,
        time_weight: float = 0.3,
    ) -> list[dict]:
        """
        Retrieve relevant memories using semantic search.
        Combines recency, importance, and semantic similarity.
        """
        # Generate query embedding
        query_embedding = await self.embeddings.encode(query)

        # Search working memory first (fastest)
        working_results = self._search_working_memory(
            profile_id, query_embedding, limit
        )

        # Search Redis short-term memory
        redis_results = await self._search_redis(
            profile_id, query_embedding, limit
        )

        # Search Supabase long-term memory (semantic)
        supabase_results = await self._search_supabase(
            profile_id, query_embedding, limit, min_importance
        )

        # Merge and rank results
        all_results = self._merge_and_rank(
            working_results, redis_results, supabase_results,
            time_weight=time_weight
        )

        return all_results[:limit]

    async def _search_supabase(
        self,
        profile_id: str,
        query_embedding: np.ndarray,
        limit: int,
        min_importance: float,
    ) -> list[dict]:
        """Semantic search using pgvector."""
        result = await self.supabase.rpc(
            "match_memories",
            {
                "query_embedding": query_embedding.tolist(),
                "match_threshold": 0.7,
                "match_count": limit,
                "filter_profile_id": profile_id,
                "min_importance": min_importance,
            }
        ).execute()

        return result.data or []

    async def consolidate_memories(
        self,
        profile_id: str,
        consolidation_threshold: int = 100,
    ) -> None:
        """
        Consolidate old memories by summarizing and archiving.
        Runs when memory count exceeds threshold.
        """
        # Count memories for profile
        count = await self.supabase.table("agent_memories")\
            .select("id", count="exact")\
            .eq("profile_id", profile_id)\
            .execute()

        if count.count > consolidation_threshold:
            # Get oldest memories
            old_memories = await self.supabase.table("agent_memories")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .order("created_at", desc=False)\
                .limit(50)\
                .execute()

            # Summarize and create consolidated memory
            summary = await self._summarize_memories(old_memories.data)
            await self.store_observation(
                agent_id="memory_consolidator",
                profile_id=profile_id,
                observation={"type": "consolidated", "summary": summary},
                importance=0.9,
            )

            # Archive old memories
            old_ids = [m["id"] for m in old_memories.data]
            await self.supabase.table("agent_memories")\
                .update({"archived": True})\
                .in_("id", old_ids)\
                .execute()
```

#### 5.3.2 Database Schema (Supabase)

```sql
-- migrations/030_agent_memory_system.sql

-- Agent memories table with pgvector for semantic search
CREATE TABLE IF NOT EXISTS agent_memories (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    content JSONB NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002 dimensions
    importance FLOAT DEFAULT 0.5,
    archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast profile lookups
CREATE INDEX idx_agent_memories_profile
ON agent_memories(profile_id, created_at DESC);

-- Index for semantic search
CREATE INDEX idx_agent_memories_embedding
ON agent_memories USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Function for semantic memory search
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(1536),
    match_threshold FLOAT,
    match_count INT,
    filter_profile_id UUID,
    min_importance FLOAT DEFAULT 0.0
)
RETURNS TABLE (
    id TEXT,
    agent_id TEXT,
    content JSONB,
    importance FLOAT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        am.id,
        am.agent_id,
        am.content,
        am.importance,
        1 - (am.embedding <=> query_embedding) AS similarity,
        am.created_at
    FROM agent_memories am
    WHERE am.profile_id = filter_profile_id
        AND am.archived = FALSE
        AND am.importance >= min_importance
        AND 1 - (am.embedding <=> query_embedding) > match_threshold
    ORDER BY am.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Trigger to update updated_at
CREATE TRIGGER update_agent_memories_timestamp
    BEFORE UPDATE ON agent_memories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 5.4 Jenny Voice Layer

#### 5.4.1 Voice Validator

```python
# agents/core/voice.py

from pydantic import BaseModel
from typing import Literal

class VoiceScore(BaseModel):
    forbidden_absence: float      # No forbidden phrases
    warmth_first: float           # Warmth before advice
    agency_preservation: float    # Preserves student agency
    checkin_question: float       # Includes check-in
    speech_patterns: float        # Uses Jenny patterns
    exclamation_calibration: float # Appropriate enthusiasm

class JennyVoiceValidator:
    """
    Validates and transforms agent outputs to match Jenny's voice.
    Based on 6-dimension scoring rubric.
    """

    FORBIDDEN_PHRASES = [
        "you should", "you need to", "you must", "you have to",
        "I recommend", "I suggest", "the best approach",
        "actually", "obviously", "clearly", "simply",
        "as an AI", "I cannot", "I don't have"
    ]

    JENNY_PATTERNS = [
        "What if we...", "Have you thought about...",
        "I'm curious...", "That's so interesting because...",
        "Here's a thought...", "You know what might be fun?",
        "I love that you...", "This reminds me of...",
    ]

    WARMTH_STARTERS = [
        "I hear you", "That makes total sense",
        "I get it", "Totally understandable",
        "First off, you're doing great",
    ]

    def __init__(self, llm_client):
        self.llm = llm_client
        self.passing_threshold = 8.0
        self.excellence_threshold = 9.5

    async def validate(self, text: str) -> tuple[bool, VoiceScore, list[str]]:
        """
        Validate text against Jenny voice criteria.
        Returns (passed, scores, issues).
        """
        scores = VoiceScore(
            forbidden_absence=self._score_forbidden_absence(text),
            warmth_first=self._score_warmth_first(text),
            agency_preservation=self._score_agency(text),
            checkin_question=self._score_checkin(text),
            speech_patterns=self._score_patterns(text),
            exclamation_calibration=self._score_exclamations(text),
        )

        total = self._calculate_total(scores)
        issues = self._identify_issues(text, scores)
        passed = total >= self.passing_threshold

        return passed, scores, issues

    async def validate_and_transform(self, output: dict) -> dict:
        """
        Validate output and transform if needed.
        Applies Jenny voice to all text fields.
        """
        transformed = {}

        for key, value in output.items():
            if isinstance(value, str) and len(value) > 20:
                passed, scores, issues = await self.validate(value)

                if not passed:
                    # Transform to Jenny voice using LLM
                    value = await self._transform_to_jenny(value, issues)

                transformed[key] = value
            else:
                transformed[key] = value

        return transformed

    async def _transform_to_jenny(
        self,
        text: str,
        issues: list[str]
    ) -> str:
        """Use LLM to transform text to Jenny's voice."""
        prompt = f"""
        Transform this text to match Jenny's voice characteristics:

        Original text: {text}

        Issues to fix: {issues}

        Jenny's voice rules:
        1. Never use: {self.FORBIDDEN_PHRASES[:5]}
        2. Start with warmth: {self.WARMTH_STARTERS[:3]}
        3. Use patterns like: {self.JENNY_PATTERNS[:3]}
        4. Preserve student agency - suggest, don't command
        5. End with a check-in question

        Return ONLY the transformed text.
        """

        response = await self.llm.generate(prompt)
        return response.text

    def _score_forbidden_absence(self, text: str) -> float:
        """Score based on absence of forbidden phrases."""
        text_lower = text.lower()
        found = [p for p in self.FORBIDDEN_PHRASES if p in text_lower]
        if not found:
            return 10.0
        return max(0.0, 10.0 - len(found) * 2.0)

    def _score_warmth_first(self, text: str) -> float:
        """Score based on warmth in opening."""
        first_sentence = text.split('.')[0].lower() if text else ""
        for starter in self.WARMTH_STARTERS:
            if starter.lower() in first_sentence:
                return 10.0
        # Check for emotional acknowledgment
        warmth_words = ["hear", "understand", "get", "feel", "sense"]
        if any(w in first_sentence for w in warmth_words):
            return 8.0
        return 5.0

    def _score_agency(self, text: str) -> float:
        """Score based on agency preservation."""
        text_lower = text.lower()
        commands = ["you should", "you need", "you must", "do this"]
        suggestions = ["what if", "might", "could", "consider", "explore"]

        command_count = sum(1 for c in commands if c in text_lower)
        suggestion_count = sum(1 for s in suggestions if s in text_lower)

        if command_count == 0 and suggestion_count > 0:
            return 10.0
        if command_count > suggestion_count:
            return max(0.0, 5.0 - command_count)
        return 7.0

    def _score_checkin(self, text: str) -> float:
        """Score based on presence of check-in question."""
        if "?" in text[-100:]:  # Question in last 100 chars
            checkin_phrases = ["does that", "what do you think", "how does that",
                             "make sense", "sound good", "feel about"]
            if any(p in text.lower()[-100:] for p in checkin_phrases):
                return 10.0
            return 7.0  # Has question but not check-in style
        return 3.0

    def _score_patterns(self, text: str) -> float:
        """Score based on use of Jenny speech patterns."""
        text_lower = text.lower()
        matches = sum(1 for p in self.JENNY_PATTERNS
                     if p.lower() in text_lower)
        return min(10.0, 5.0 + matches * 2.0)

    def _score_exclamations(self, text: str) -> float:
        """Score based on appropriate exclamation use."""
        exclamation_count = text.count('!')
        word_count = len(text.split())
        ratio = exclamation_count / max(1, word_count / 50)

        if 0.5 <= ratio <= 2.0:  # Sweet spot
            return 10.0
        if ratio == 0:
            return 6.0  # Too flat
        if ratio > 3.0:
            return 4.0  # Too enthusiastic
        return 7.0

    def _calculate_total(self, scores: VoiceScore) -> float:
        """Calculate weighted total score."""
        weights = {
            "forbidden_absence": 2.0,
            "warmth_first": 1.5,
            "agency_preservation": 1.5,
            "checkin_question": 1.0,
            "speech_patterns": 1.0,
            "exclamation_calibration": 1.0,
        }
        total_weight = sum(weights.values())
        weighted_sum = sum(
            getattr(scores, k) * v for k, v in weights.items()
        )
        return weighted_sum / total_weight
```

### 5.5 Cross-Agent Communication

#### 5.5.1 Event Bus

```python
# agents/core/events.py

from typing import Callable, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class AgentEvent:
    source_agent: str
    event_type: str
    payload: dict
    profile_id: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class EventBus:
    """
    Event-driven communication between agents.
    Supports pub/sub pattern for cross-agent coordination.
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}
        self._event_history: list[AgentEvent] = []
        self._max_history = 1000

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[AgentEvent], Any]
    ) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event: AgentEvent) -> list[Any]:
        """Publish an event to all subscribers."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        handlers = self._subscribers.get(event.event_type, [])
        results = await asyncio.gather(
            *[handler(event) for handler in handlers],
            return_exceptions=True
        )
        return results

    def get_events(
        self,
        profile_id: str,
        event_types: list[str] = None,
        limit: int = 100
    ) -> list[AgentEvent]:
        """Retrieve event history for a profile."""
        filtered = [
            e for e in self._event_history
            if e.profile_id == profile_id
            and (event_types is None or e.event_type in event_types)
        ]
        return filtered[-limit:]

# Event types
class EventTypes:
    NARRATIVE_SYNTHESIZED = "narrative.synthesized"
    AWARDS_PORTFOLIO_BUILT = "awards.portfolio_built"
    TIME_AUDIT_COMPLETE = "time.audit_complete"
    CRISIS_DETECTED = "crisis.detected"
    CRISIS_RESOLVED = "crisis.resolved"
    OPPORTUNITY_MATCHED = "opportunity.matched"
    MEMORY_CONSOLIDATED = "memory.consolidated"
```

### 5.6 HITL (Human-in-the-Loop) Workflow

#### 5.6.1 Workflow Manager

```python
# agents/core/hitl.py

from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"

class HITLRequest(BaseModel):
    id: str
    agent_id: str
    profile_id: str
    action_type: str
    proposed_action: dict
    confidence: float
    reasoning: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    reviewer_id: Optional[str] = None
    review_notes: Optional[str] = None
    created_at: datetime = None
    reviewed_at: Optional[datetime] = None

class HITLWorkflowManager:
    """
    Human-in-the-Loop workflow for high-stakes agent decisions.
    """

    REVIEW_THRESHOLDS = {
        "narrative.brand_statement": 0.85,
        "awards.portfolio_change": 0.80,
        "crisis.major_pivot": 0.70,
        "opportunity.expensive_program": 0.90,
    }

    def __init__(self, supabase_client, notification_service):
        self.supabase = supabase_client
        self.notifications = notification_service

    async def request_review(
        self,
        agent_id: str,
        profile_id: str,
        action_type: str,
        proposed_action: dict,
        confidence: float,
        reasoning: str,
    ) -> HITLRequest:
        """
        Create a HITL review request.
        """
        threshold = self.REVIEW_THRESHOLDS.get(action_type, 0.85)

        # Auto-approve if confidence exceeds threshold
        if confidence >= threshold:
            return HITLRequest(
                id=f"hitl_{datetime.utcnow().timestamp()}",
                agent_id=agent_id,
                profile_id=profile_id,
                action_type=action_type,
                proposed_action=proposed_action,
                confidence=confidence,
                reasoning=reasoning,
                status=WorkflowStatus.APPROVED,
                review_notes="Auto-approved: high confidence",
            )

        # Create review request
        request = HITLRequest(
            id=f"hitl_{datetime.utcnow().timestamp()}",
            agent_id=agent_id,
            profile_id=profile_id,
            action_type=action_type,
            proposed_action=proposed_action,
            confidence=confidence,
            reasoning=reasoning,
            created_at=datetime.utcnow(),
        )

        # Store in database
        await self.supabase.table("hitl_requests").insert(
            request.model_dump()
        ).execute()

        # Send notification
        await self.notifications.send(
            type="hitl_review_needed",
            profile_id=profile_id,
            data={"request_id": request.id, "action_type": action_type}
        )

        return request

    async def submit_review(
        self,
        request_id: str,
        reviewer_id: str,
        decision: WorkflowStatus,
        notes: str = None,
        modified_action: dict = None,
    ) -> HITLRequest:
        """
        Submit human review decision.
        """
        update_data = {
            "status": decision.value,
            "reviewer_id": reviewer_id,
            "review_notes": notes,
            "reviewed_at": datetime.utcnow().isoformat(),
        }

        if decision == WorkflowStatus.MODIFIED and modified_action:
            update_data["proposed_action"] = modified_action

        await self.supabase.table("hitl_requests")\
            .update(update_data)\
            .eq("id", request_id)\
            .execute()

        # Retrieve updated request
        result = await self.supabase.table("hitl_requests")\
            .select("*")\
            .eq("id", request_id)\
            .single()\
            .execute()

        return HITLRequest(**result.data)
```

### 5.7 API Endpoints (v13.0)

#### 5.7.1 New Endpoints

```python
# agents/main.py (additions)

from fastapi import APIRouter
from .core.memory import MemoryManager
from .core.events import EventBus
from .core.hitl import HITLWorkflowManager

v13_router = APIRouter(prefix="/v13", tags=["v13-agents"])

@v13_router.post("/agents/{agent_id}/run")
async def run_agent(
    agent_id: str,
    request: AgentRunRequest,
    memory: MemoryManager = Depends(get_memory),
    events: EventBus = Depends(get_event_bus),
):
    """
    Run a ReAct agent with full memory and event support.
    """
    agent = get_agent(agent_id, memory)
    result = await agent.run(request.context, request.input)

    # Publish completion event
    await events.publish(AgentEvent(
        source_agent=agent_id,
        event_type=f"{agent_id}.completed",
        payload=result,
        profile_id=request.context.profile_id,
    ))

    return result

@v13_router.get("/memory/{profile_id}/recall")
async def recall_memories(
    profile_id: str,
    query: str,
    limit: int = 10,
    memory: MemoryManager = Depends(get_memory),
):
    """
    Semantic search across agent memories.
    """
    memories = await memory.recall(
        profile_id=profile_id,
        query=query,
        limit=limit,
    )
    return {"memories": memories}

@v13_router.get("/hitl/pending")
async def get_pending_reviews(
    profile_id: str = None,
    hitl: HITLWorkflowManager = Depends(get_hitl),
):
    """
    Get pending HITL review requests.
    """
    requests = await hitl.get_pending(profile_id=profile_id)
    return {"requests": requests}

@v13_router.post("/hitl/{request_id}/review")
async def submit_review(
    request_id: str,
    decision: ReviewDecision,
    hitl: HITLWorkflowManager = Depends(get_hitl),
):
    """
    Submit human review decision.
    """
    result = await hitl.submit_review(
        request_id=request_id,
        reviewer_id=decision.reviewer_id,
        decision=decision.status,
        notes=decision.notes,
        modified_action=decision.modified_action,
    )
    return result
```

### 5.8 Frontend Integration (v13.0)

#### 5.8.1 Updated agentV2Client.ts

```typescript
// lib/api/agentV13Client.ts

const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8000';

// Memory types
export interface MemoryItem {
  id: string;
  agent_id: string;
  content: Record<string, unknown>;
  importance: number;
  similarity: number;
  created_at: string;
}

export interface MemoryRecallResult {
  memories: MemoryItem[];
}

// HITL types
export interface HITLRequest {
  id: string;
  agent_id: string;
  profile_id: string;
  action_type: string;
  proposed_action: Record<string, unknown>;
  confidence: number;
  reasoning: string;
  status: 'pending' | 'in_review' | 'approved' | 'rejected' | 'modified';
  reviewer_id?: string;
  review_notes?: string;
  created_at: string;
  reviewed_at?: string;
}

class AgentV13Client {
  private baseUrl: string;

  constructor(baseUrl: string = AGENT_API_URL) {
    this.baseUrl = baseUrl;
  }

  // Run any agent with ReAct framework
  async runAgent<T>(
    agentId: string,
    input: Record<string, unknown>,
    context: { profile_id: string }
  ): Promise<T> {
    return this.request('POST', `/v13/agents/${agentId}/run`, {
      input,
      context,
    });
  }

  // Memory operations
  async recallMemories(
    profileId: string,
    query: string,
    limit: number = 10
  ): Promise<MemoryRecallResult> {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
    });
    return this.request(
      'GET',
      `/v13/memory/${profileId}/recall?${params}`
    );
  }

  // HITL operations
  async getPendingReviews(
    profileId?: string
  ): Promise<{ requests: HITLRequest[] }> {
    const params = profileId
      ? `?profile_id=${profileId}`
      : '';
    return this.request('GET', `/v13/hitl/pending${params}`);
  }

  async submitReview(
    requestId: string,
    decision: {
      reviewer_id: string;
      status: HITLRequest['status'];
      notes?: string;
      modified_action?: Record<string, unknown>;
    }
  ): Promise<HITLRequest> {
    return this.request('POST', `/v13/hitl/${requestId}/review`, decision);
  }

  private async request<T>(
    method: 'GET' | 'POST',
    path: string,
    data?: Record<string, unknown>
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const options: RequestInit = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };

    if (data && method === 'POST') {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    return response.json();
  }
}

export const agentV13Api = new AgentV13Client();
export default agentV13Api;
```

---

## 6. Migration Roadmap

### 6.1 Phase 1: Foundation (Week 1-2)

| Task | Priority | Status | Owner |
|------|----------|--------|-------|
| ReAct base class implementation | P0 | Pending | Backend |
| Memory manager core | P0 | Pending | Backend |
| Redis integration | P0 | Pending | Backend |
| Supabase pgvector setup | P0 | Pending | Backend |
| Jenny voice validator | P0 | Pending | Backend |

### 6.2 Phase 2: Agent Migration (Week 3-4)

| Task | Priority | Status | Owner |
|------|----------|--------|-------|
| NarrativeSynthesis → ReAct | P0 | Pending | Backend |
| AwardsPortfolio → ReAct | P0 | Pending | Backend |
| TimeAudit → ReAct | P1 | Pending | Backend |
| CrisisAlchemy → ReAct | P1 | Pending | Backend |
| Opportunity → ReAct | P2 | Pending | Backend |

### 6.3 Phase 3: Frontend Cards (Week 5-6)

| Task | Priority | Status | Owner |
|------|----------|--------|-------|
| NarrativeSynthesisCard | P0 | Pending | Frontend |
| WeeklyPlanCard | P1 | Pending | Frontend |
| NCWITStrategyCard | P1 | Pending | Frontend |
| OpportunitiesCard | P2 | Pending | Frontend |
| MemoryStatusIndicator | P2 | Pending | Frontend |

### 6.4 Phase 4: Advanced Features (Week 7-8)

| Task | Priority | Status | Owner |
|------|----------|--------|-------|
| Cross-agent event bus | P1 | Pending | Backend |
| HITL workflow manager | P1 | Pending | Backend |
| Memory consolidation | P2 | Pending | Backend |
| HITL review UI | P2 | Pending | Frontend |

---

## 7. Success Metrics

### 7.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| ReAct iteration efficiency | <3 avg iterations | Agent telemetry |
| Memory recall accuracy | >95% | Semantic similarity scores |
| Jenny voice pass rate | >90% | Voice validator scores |
| API response time (cached) | <2s | P95 latency |
| API response time (cold) | <5s | P95 latency |
| Memory consolidation rate | 100 → 20 items | Compression ratio |

### 7.2 Product Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Agent task completion | >80% autonomous | HITL request rate |
| User satisfaction | 4.5/5 | In-app rating |
| Feature adoption | >60% use 3+ agents | Analytics |
| Time to value | <5 min first insight | Session tracking |
| Brand statement recall | >70% remember | User survey |

### 7.3 Quality Gates

Before production release:
- [ ] All ReAct agents pass 50+ golden test cases
- [ ] Memory system handles 10K+ entries per profile
- [ ] Jenny voice score ≥8.0 on 100% of outputs
- [ ] HITL workflow tested with 3+ human reviewers
- [ ] Load test: 100 concurrent users, <5s response
- [ ] Security audit: No PII leakage in memory system

---

## 8. Appendices

### A. File Structure

```
agents/
├── core/
│   ├── react_base.py      # ReAct framework base class
│   ├── memory.py          # 3-tier memory manager
│   ├── voice.py           # Jenny voice validator
│   ├── events.py          # Cross-agent event bus
│   └── hitl.py            # HITL workflow manager
├── agents/
│   ├── narrative_react.py # Narrative synthesis agent
│   ├── awards_react.py    # Awards portfolio agent
│   ├── time_react.py      # Time audit agent
│   ├── crisis_react.py    # Crisis alchemy agent
│   └── opportunity_react.py # Opportunity agent
├── main.py                # FastAPI app with v13 routes
└── requirements.txt       # Dependencies

lib/
├── api/
│   └── agentV13Client.ts  # v13 API client
├── hooks/
│   ├── useMemory.ts       # Memory hooks
│   └── useHITL.ts         # HITL hooks
└── types/
    └── agentsV13.ts       # v13 type definitions

components/
├── agents/
│   ├── NarrativeSynthesisCard.tsx
│   ├── WeeklyPlanCard.tsx
│   ├── NCWITStrategyCard.tsx
│   ├── OpportunitiesCard.tsx
│   └── MemoryStatusIndicator.tsx
└── hitl/
    └── ReviewPanel.tsx
```

### B. Environment Variables

```env
# .env.local additions for v13

# Memory system
REDIS_URL=redis://localhost:6379
EMBEDDING_MODEL=text-embedding-ada-002

# HITL
HITL_NOTIFICATION_WEBHOOK=https://...
HITL_AUTO_APPROVE_THRESHOLD=0.90

# Feature flags
ENABLE_REACT_AGENTS=true
ENABLE_MEMORY_SYSTEM=true
ENABLE_HITL_WORKFLOW=true
```

### C. API Compatibility

v13.0 maintains backwards compatibility with v2.0 endpoints:

| v2.0 Endpoint | v13.0 Equivalent | Notes |
|---------------|------------------|-------|
| `/agents/narrative/synthesize` | `/v13/agents/narrative/run` | Add memory context |
| `/agents/awards/portfolio` | `/v13/agents/awards/run` | Add memory context |
| `/agents/time-audit` | `/v13/agents/time/run` | Add memory context |
| `/agents/crisis-alchemy` | `/v13/agents/crisis/run` | Add memory context |

---

*Document Version: 13.0.0*
*Last Updated: January 11, 2026*
