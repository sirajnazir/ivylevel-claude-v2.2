# IvyQuest Platform Architecture Specification

**Document ID:** SPEC_PLATFORM_ARCHITECTURE_20260120_1830_v1_001
**Version:** 1.0
**Date:** 2026-01-20
**Status:** Approved/Implemented
**Author:** Claude Code

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Architecture (Without Letta)](#2-current-state-architecture-without-letta)
3. [Database Schema](#3-database-schema)
4. [UI/UX Flow](#4-uiux-flow)
5. [Agent Architecture](#5-agent-architecture)
6. [Letta Integration Architecture](#6-letta-integration-architecture)
7. [Data Flow Diagrams](#7-data-flow-diagrams)
8. [Backward Compatibility Guarantees](#8-backward-compatibility-guarantees)
9. [Testing Plan](#9-testing-plan)
10. [Appendix](#10-appendix)

---

## 1. Executive Summary

### 1.1 Purpose

This specification documents the complete IvyQuest platform architecture, covering:
- Current production system (Agno-based agents + Supabase)
- UI/UX flow from Assessment through Execution
- Database schema (45 tables)
- Letta integration layer (optional, feature-flagged)
- Backward compatibility guarantees

### 1.2 Key Architectural Principles

| Principle | Implementation |
|-----------|----------------|
| **Single Source of Truth** | Supabase is THE canonical data store |
| **Additive Enhancement** | Letta supplements, never replaces |
| **Feature-Flag Safety** | All Letta features are OFF by default |
| **Graceful Degradation** | System works fully without Letta |

### 1.3 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────────┐ ┌───────────┐         │
│  │Assessment│ │Dashboard│ │Multi-Agent  │ │ Execution │         │
│  │ Frames  │ │  Tabs   │ │    Tab      │ │    Tab    │         │
│  └────┬────┘ └────┬────┘ └──────┬──────┘ └─────┬─────┘         │
└───────┼──────────┼─────────────┼───────────────┼───────────────┘
        │          │             │               │
        ▼          ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                         │
│  /api/agents/*  │  /api/execution/*  │  /api/letta/* (optional) │
└────────┬────────────────┬────────────────────┬──────────────────┘
         │                │                    │
         ▼                ▼                    ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────────────┐
│  AGNO AGENTS   │ │ EXECUTION CHAT │ │  LETTA LAYER           │
│  (Production)  │ │    AGENT       │ │  (Feature-Flagged)     │
│  ├─GamePlan    │ │                │ │  ├─Orchestrator        │
│  ├─Awards      │ │  Uses Supabase │ │  ├─GamePlan Specialist │
│  ├─Programs    │ │  + LangChain   │ │  ├─Execution Specialist│
│  ├─Assessment  │ │                │ │  ├─Awards Specialist   │
│  └─Narrative   │ │                │ │  └─Essay Specialist    │
└────────┬───────┘ └────────┬───────┘ └───────────┬────────────┘
         │                  │                      │
         └──────────────────┼──────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE (PostgreSQL)                         │
│                    SINGLE SOURCE OF TRUTH                        │
│  45 Tables: profiles, game_plans, projects, conversations...    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Current State Architecture (Without Letta)

### 2.1 Agent Framework

**Primary Framework:** Agno + LangChain/LangGraph

| Agent | Purpose | Key Tools |
|-------|---------|-----------|
| GamePlanAgent | Strategic planning, phase management | DB access, LLM reasoning |
| AwardsAgent | Award recommendations, fit scoring | Award DB, probability calc |
| ProgramsAgent | Summer program matching | Program DB, deadline tracking |
| AssessmentAgent | Profile analysis, archetype detection | Scoring engine |
| NarrativeSynthesisAgent | Brand statement, narrative DNA | LLM synthesis |
| ExecutionChatAgent | Coaching, task tracking, nudges | 13 tools, chat streaming |

### 2.2 Data Flow (Production)

```
User Input (Frames 1-6)
        │
        ▼
┌─────────────────┐
│ useStudentStore │  (Zustand - client state)
│ (localStorage)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Backend Agents │────▶│    Supabase     │
│  (Agno-based)   │◀────│   (45 tables)   │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│ useResultsStore │  (Zustand - cached results)
│ (sessionStorage)│
└────────┬────────┘
         │
         ▼
    Dashboard UI
```

### 2.3 Agent Communication Pattern

**Current Pattern:** No direct agent-to-agent communication

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  GamePlan    │     │    Awards    │     │  Execution   │
│    Agent     │     │    Agent     │     │    Agent     │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │    SUPABASE    │
                   │  (Shared Data) │
                   └────────────────┘
```

All agents read/write to the same Supabase tables, enabling implicit coordination through shared state.

---

## 3. Database Schema

### 3.1 Core Tables (45 Total)

#### Identity & Profiling (2 tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `profiles` | Student profiles with agent-derived attributes | id, assessment_id, grade, archetype_id, narrative_dna, spike, pillars, brand_statement, execution_debt |
| `archetypes` | 8 student archetype classifications | label, patterns, coaching_approach |

#### Assessment & Planning (2 tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `assessments` | Assessment results | session_id, profile_data, game_plan_data, scores, tier |
| `game_plans` | Strategic multi-year plans | plan_data, target_schools, current_phase, completion_percentage |

#### Project Execution (3 tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `projects` | Tracked projects (49+ per student) | name, status, category, deadline, last_activity_at |
| `project_steps` | Microsteps within projects | title, status, due_date, is_milestone |
| `weekly_plans` | P0/P1/P2 prioritization | p0_tasks, p1_tasks, p2_tasks, generated_at |

#### Crisis & Opportunity (5 tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `crises` | Crisis Alchemy 4-step tracking | type, urgency, status, step1-4 data |
| `awards` | 200+ awards database | name, level, prestige_score, deadline |
| `opportunities` | 500+ programs database | type, acceptance_rate, deadline |
| `student_applications` | Application tracking | status, predicted_probability |
| `nudge_queue` | Proactive engagement queue | nudge_type, priority, message_draft |

#### Conversation & Memory (7 tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `conversations` | Persistent chat history | role, content, context_type, is_proactive |
| `agent_memories` | Long-term memory with pgvector | content, embedding, importance |
| `phase3_semantic_memories` | B3 semantic memory | embedding, memory_type |
| `phase3_longterm_memories` | B4 key-value memory | memory_key, memory_value |
| `phase3_feedback` | I1 feedback learning | feedback_type, feedback_value |
| `phase3_behavior_adaptations` | I2/I3 personalization | behavior_key, behavior_value |
| `phase3_recognized_patterns` | I5 pattern recognition | pattern_type, pattern_signature |

### 3.2 Key Relationships

```
profiles
    │
    ├──▶ assessments (1:1)
    │
    ├──▶ game_plans (1:N)
    │
    ├──▶ projects (1:N)
    │       │
    │       └──▶ project_steps (1:N)
    │
    ├──▶ weekly_plans (1:N)
    │
    ├──▶ conversations (1:N)
    │
    ├──▶ crises (1:N)
    │
    └──▶ nudge_queue (1:N)
```

### 3.3 Critical Fields for Agent Context

| Field | Table | Used By |
|-------|-------|---------|
| `brand_statement` | profiles | AssessmentAgentCard, NarrativeSynthesis |
| `spike` | profiles | GamePlanAgent, StrategicIdentity |
| `pillars` | profiles | AssessmentTab, AgentCards |
| `plan_data` | game_plans | ExecutionChatAgent (v5.4), GamePlanTab |
| `p0_tasks` | weekly_plans | ExecutionTab (Weekly Focus) |
| `status` | projects | Stall detection, EDS calculation |
| `last_activity_at` | projects | Stall detection (5+ days) |

---

## 4. UI/UX Flow

### 4.1 Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    ASSESSMENT PHASE (Frames 1-6)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Frame 1: Warmup          Frame 2: Snapshot                     │
│  ├─ Role Selection        ├─ GPA (weighted/unweighted)          │
│  ├─ Name, Grade           ├─ Test Scores (SAT/ACT)              │
│  ├─ Target Schools        ├─ Course Rigor (AP/IB)               │
│  └─ Intended Major        └─ Academic Awards                    │
│                                                                  │
│  Frame 3: Context         Frame 4: Building                     │
│  ├─ Background            ├─ Passion Projects                   │
│  ├─ Constraints           ├─ Impact Stories                     │
│  └─ Resources             └─ Leadership Roles                   │
│                                                                  │
│  Frame 5: PowerUps        Frame 6: ProfileReveal                │
│  ├─ Special Skills        ├─ Narrative Synthesis                │
│  ├─ Unique Experiences    ├─ Brand Statement Generation         │
│  └─ Hidden Talents        └─ Initial Twin Fleet                 │
│                                                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DASHBOARD PHASE                             │
├────────────┬────────────┬──────────────┬───────────────────────┤
│ Assessment │  GamePlan  │ Multi-Agent  │     Execution         │
│    Tab     │    Tab     │     Tab      │        Tab            │
├────────────┴────────────┴──────────────┴───────────────────────┤
│                                                                  │
│  ASSESSMENT TAB                                                  │
│  ├─ Ivy+ Ready Score (5-ring visualization)                     │
│  ├─ Strategic Identity (archetype, spike, pillars)              │
│  ├─ Portfolio Audit (diagnosis, tier breakdown)                 │
│  ├─ Admissions Rubric (AI/EC/PQ/Recs scores)                    │
│  ├─ Dimensional Scores (4 domains)                              │
│  └─ Brand Statement                                             │
│                                                                  │
│  GAMEPLAN TAB                                                    │
│  ├─ Initial Plan View (baseline strategy)                       │
│  │   ├─ Target Profile & Narrative                              │
│  │   ├─ EC Strategy (activities, hours)                         │
│  │   ├─ Target Schools (reach/target/safety)                    │
│  │   ├─ Target Awards                                           │
│  │   └─ Target Summer Programs                                  │
│  └─ Progress View (evolution tracking)                          │
│      ├─ Current Phase Header                                    │
│      ├─ Phase Timeline (expandable)                             │
│      └─ Priority Actions (P0/P1/P2)                             │
│                                                                  │
│  MULTI-AGENT TAB                                                 │
│  ├─ Dashboard View (6 Agent Cards)                              │
│  │   ├─ AssessmentAgentCard                                     │
│  │   ├─ GamePlanAgentCard                                       │
│  │   ├─ AwardsAgentCard                                         │
│  │   ├─ OpportunityAgentCard                                    │
│  │   ├─ ExecutionAgentCard                                      │
│  │   └─ CrisisAgentCard                                         │
│  └─ Chat View (agent conversation)                              │
│      ├─ Agent Selector (sidebar)                                │
│      ├─ Message History                                         │
│      └─ Streaming Responses                                     │
│                                                                  │
│  EXECUTION TAB                                                   │
│  ├─ Dashboard View                                              │
│  │   ├─ EDS Card (Execution Debt Score)                         │
│  │   ├─ Quick Actions (4 buttons)                               │
│  │   ├─ Weekly Focus (P0 items)                                 │
│  │   ├─ Stalled Projects (0-4 items)                            │
│  │   └─ Active Projects (grid)                                  │
│  └─ Chat View                                                   │
│      ├─ Execution Coach conversation                            │
│      ├─ Context-aware (project/general)                         │
│      └─ Suggested prompts                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Sources by Component

| Component | Primary Data Source | Hook/API |
|-----------|---------------------|----------|
| AssessmentTab | Zustand + DB | useResultsStore, useProfileIdentity |
| GamePlanTab | Backend API | useGamePlan(profileId) |
| AssessmentAgentCard | DB + Store | useProfileIdentity, useNarrativeDNA |
| GamePlanAgentCard | Backend API | useGamePlan, useIdentitySeeds |
| AwardsAgentCard | Backend API | useAwardMatches |
| ExecutionAgentCard | Backend API | useExecutionDebtScore |
| ExecutionTab Dashboard | Backend API | /api/execution/* endpoints |
| ExecutionTab Chat | Backend Streaming | useExecutionChat |

### 4.3 Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/agents` | POST | Multi-agent chat |
| `/api/agents/narrative/synthesize` | POST | Generate brand statement |
| `/api/agents/game-plan/generate` | POST | Generate game plan |
| `/api/execution/eds/{profile_id}` | GET | Execution Debt Score |
| `/api/execution/weekly-focus/{profile_id}` | GET | P0 tasks |
| `/api/execution/stalls/{profile_id}` | GET | Stalled projects |
| `/api/execution/projects/{profile_id}` | GET | Active projects |
| `/api/execution/weekly-plan/generate` | POST | Generate weekly plan |
| `/api/execution/chat/stream` | POST | Streaming chat |

---

## 5. Agent Architecture

### 5.1 ExecutionChatAgent (v5.4)

**File:** `/agents/agents/execution_chat.py`

**System Prompt Context Includes:**
```
Student: {first_name} {last_name}
Grade: {grade}
Archetype: {archetype}
Spike/Focus: {spike}
Narrative Theme: {narrative_theme}

GAME PLAN - SUMMER PROGRAMS (actual names)
GAME PLAN - AWARDS TO PURSUE (actual names)
GAME PLAN - EXTRACURRICULARS (actual names)

WEEKLY FOCUS (P0 Items)
EXECUTION STATUS (EDS, Active, Overdue, Stalled)
STALLED PROJECTS
PROACTIVE TOPICS TO RAISE
```

**13 Available Tools:**
1. `tool_get_weekly_focus` - P0 items
2. `tool_generate_weekly_plan` - Create weekly plan
3. `tool_get_active_projects` - Active projects
4. `tool_get_project_details` - Project details
5. `tool_update_project_status` - Update project/step
6. `tool_detect_stalls` - Find stalled projects
7. `tool_calculate_eds` - Execution Debt Score
8. `tool_create_nudge` - Create notification
9. `tool_escalate_to_crisis` - Crisis Alchemy
10. `tool_search_memory` - Long-term memory search
11. `tool_store_insight` - Store observation
12. `tool_get_conversation_history` - Chat history
13. `tool_update_project` - Update with notes

### 5.2 Middleware Integration (50 Patterns)

All agents inherit from `MiddlewareIntegrationMixin`:

```
MiddlewareStackV9 (50 Patterns)
├── J1: Reasoning Traces
├── J3: Audit Trail
├── E4: Quality Scoring
├── H3: Retry Logic
├── G2: Approval Workflows
└── ... (45 more patterns)
```

---

## 6. Letta Integration Architecture

### 6.1 Why Letta Was Implemented

| Problem | Without Letta | With Letta |
|---------|---------------|------------|
| **Stateless Agents** | Context resets each turn | 5 persistent memory blocks |
| **No Coordination** | Agents work independently | Orchestrator coordinates specialists |
| **No Proactivity** | On-demand only | Background jobs monitor & alert |
| **Loose Techniques** | 139 techniques not embedded | Native technique search tool |

### 6.2 Letta Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     LETTA LAYER (Optional)                       │
│                                                                  │
│  Feature Flags (All OFF by default):                            │
│  ├─ LETTA_ENABLED=false                                         │
│  ├─ LETTA_ORCHESTRATOR_ENABLED=false                            │
│  ├─ LETTA_GAMEPLAN_ENABLED=false                                │
│  ├─ LETTA_EXECUTION_ENABLED=false                               │
│  ├─ LETTA_AWARDS_ENABLED=false                                  │
│  └─ LETTA_ESSAY_ENABLED=false                                   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    ORCHESTRATOR                            │  │
│  │              (Central Router/Supervisor)                   │  │
│  └────────┬─────────┬─────────┬─────────┬────────────────────┘  │
│           │         │         │         │                        │
│           ▼         ▼         ▼         ▼                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │GamePlan │ │Execution│ │ Awards  │ │  Essay  │               │
│  │Specialist│ │Specialist│ │Specialist│ │Specialist│            │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘               │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  5 MEMORY BLOCKS (Per Agent):                                   │
│  ├─ student_profile (5000 chars max)                            │
│  ├─ coaching_history (5000 chars max)                           │
│  ├─ active_gameplan (5000 chars max)                            │
│  ├─ outcome_tracker (5000 chars max)                            │
│  └─ deadline_state (5000 chars max)                             │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MEMORY SYNC (Supabase → Letta):                                │
│  ├─ On-demand: Before every chat                                │
│  ├─ Scheduled: Every 5 minutes                                  │
│  └─ Direction: ONE-WAY (Supabase is source of truth)            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Memory Sync Flow

```
SUPABASE (Source of Truth)
        │
        │ (Read-Only SELECT queries)
        ▼
┌─────────────────────────────────────┐
│     MemorySyncService               │
│     _gather_source_data()           │
├─────────────────────────────────────┤
│  profiles → student_profile block   │
│  game_plans → active_gameplan block │
│  proactive_notifications → coaching_history block │
│  (future: tasks → deadline_state)   │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│     MemoryBlock.build()             │
│     (Transform to Markdown)         │
│     (Truncate to 5000 chars)        │
└────────────────┬────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌───────────────┐  ┌─────────────────┐
│ letta_memory_ │  │ Letta Cloud API │
│ snapshots     │  │ agents.memory   │
│ (backup)      │  │ .update()       │
└───────────────┘  └─────────────────┘
```

### 6.4 When Letta is Enabled vs Disabled

| Feature | LETTA_ENABLED=false | LETTA_ENABLED=true |
|---------|---------------------|---------------------|
| /api/agents/* | Works normally (Agno) | Works normally (Agno) |
| /api/execution/* | Works normally | Works normally |
| /api/letta/* | Returns 503 gracefully | Letta agents respond |
| Memory persistence | Session-based | Cross-session |
| Agent coordination | Via Supabase | Via Orchestrator |
| Proactive monitoring | Manual | Background jobs |

### 6.5 Letta Database Tables (NEW - Isolated)

| Table | Purpose |
|-------|---------|
| `letta_agent_registry` | Agent IDs per student |
| `letta_memory_snapshots` | Memory block backups |
| `letta_approval_queue` | Pending HITL approvals |
| `letta_transition_log` | Audit trail |

**Critical Rule:** Letta tables NEVER modify existing tables. Read-only from Supabase.

---

## 7. Data Flow Diagrams

### 7.1 Assessment to Dashboard

```
Frame 1-6 (User Input)
        │
        ▼
useStudentStore (Zustand)
        │
        ├─────────────────────────────────┐
        ▼                                 │
POST /api/agents/narrative/synthesize    │
        │                                 │
        ▼                                 │
NarrativeSynthesisAgent                  │
        │                                 │
        ├─▶ brand_statement              │
        ├─▶ narrative_dna                │
        └─▶ themes                       │
                │                         │
                ▼                         │
        Supabase profiles table          │
                │                         │
                ├◀────────────────────────┘
                ▼
        useProfileIdentity hook
                │
                ▼
        AssessmentTab / AssessmentAgentCard
```

### 7.2 Execution Tab Data Flow

```
User opens Execution Tab
        │
        ├──────────────────┐
        │                  │
        ▼                  ▼
loadDashboardData()   generateWeeklyPlan()
        │                  │
        ├──────────────────┤
        │                  │
        ▼                  ▼
GET /api/execution/    POST /api/execution/
    eds/{id}               weekly-plan/generate
    weekly-focus/{id}           │
    stalls/{id}                 │
    projects/{id}               │
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
          ExecutionChatAgent
                    │
                    ├─▶ _get_game_plan() [NEW v5.4]
                    ├─▶ _get_profile()
                    ├─▶ _get_current_weekly_plan()
                    ├─▶ tool_calculate_eds()
                    └─▶ tool_detect_stalls()
                            │
                            ▼
                    System Prompt includes:
                    - Actual summer program names
                    - Actual award names
                    - Actual EC names
                    - P0/P1/P2 tasks
                    - EDS score
```

---

## 8. Backward Compatibility Guarantees

### 8.1 Design Principle: "ADDITIVE ONLY"

Letta **supplements, never replaces** existing functionality.

### 8.2 Coexistence Table

| Existing Agent | Letta Equivalent | Can Coexist | Notes |
|----------------|------------------|-------------|-------|
| AssessmentAgent | Assessment (dormant) | Yes | Letta version not active |
| ExecutionChatAgent | Execution Specialist | Yes | Different endpoints |
| GamePlanAgent | GamePlan Specialist | Yes | Different endpoints |
| AwardsAgent | Awards Specialist | Yes | Different endpoints |
| NarrativeSynthesisAgent | Essay Specialist | Yes | Different endpoints |

### 8.3 What Won't Break When Letta is Enabled

| Component | Guarantee |
|-----------|-----------|
| Assessment Frames | No changes - still use useStudentStore |
| AssessmentTab | No changes - still use useResultsStore + useProfileIdentity |
| GamePlanTab | No changes - still use useGamePlan |
| Multi-Agent Tab | No changes - still use /api/agents |
| Execution Tab | No changes - still use /api/execution/* |
| Agent Cards | No changes - same hooks, same data |
| Database tables | No modifications - Letta has separate letta_* tables |

### 8.4 Data Isolation

```
EXISTING TABLES (Untouched by Letta):
├── profiles
├── assessments
├── game_plans
├── projects
├── project_steps
├── weekly_plans
├── conversations
├── agent_memories
├── crises
├── nudge_queue
└── ... (all 45 production tables)

NEW LETTA TABLES (Isolated):
├── letta_agent_registry
├── letta_memory_snapshots
├── letta_approval_queue
└── letta_transition_log

RULE: Letta reads FROM existing tables, writes ONLY to letta_* tables
```

---

## 9. Testing Plan

### 9.1 Pre-Letta-Enable Testing

| Test | Expected Result |
|------|-----------------|
| Load Assessment Tab | Shows scores, brand statement, archetype |
| Load Multi-Agent Tab | All 6 agent cards render with data |
| Click Agent Card | Opens detail modal with correct data |
| Chat with agent | Streaming response works |
| Load Execution Tab | EDS, Weekly Focus, Projects display |
| Generate Weekly Plan | P0/P1/P2 items created |
| Chat with Execution Coach | References actual game plan data |

### 9.2 Post-Letta-Enable Testing

| Test | Expected Result |
|------|-----------------|
| All Pre-Letta tests | Still pass (backward compatible) |
| GET /api/letta/health | Returns healthy status |
| GET /api/letta/status/{id} | Shows agent registry |
| POST /api/letta/chat/{id} | Orchestrator responds |
| Memory sync | letta_memory_snapshots populated |
| Background jobs | Deadline alerts generated |

### 9.3 Rollback Test

| Test | Expected Result |
|------|-----------------|
| Set LETTA_ENABLED=false | All Letta endpoints return 503 |
| All production features | Work normally |
| No errors in logs | Clean shutdown of Letta layer |

---

## 10. Appendix

### 10.1 Environment Variables

```bash
# Production (Required)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
OPENAI_API_KEY=xxx

# Letta (Optional - All OFF by default)
LETTA_ENABLED=false
LETTA_API_KEY=xxx
LETTA_ORCHESTRATOR_ENABLED=false
LETTA_GAMEPLAN_ENABLED=false
LETTA_EXECUTION_ENABLED=false
LETTA_AWARDS_ENABLED=false
LETTA_ESSAY_ENABLED=false
```

### 10.2 Key Files

| File | Purpose |
|------|---------|
| `/agents/agents/execution_chat.py` | ExecutionChatAgent (v5.4) |
| `/agents/agents/mixins/middleware_mixin.py` | Middleware patterns |
| `/agents/letta/config.py` | Letta feature flags |
| `/agents/letta/client.py` | Letta client wrapper |
| `/agents/letta/memory/sync.py` | Memory sync service |
| `/components/tabs/ExecutionTab.tsx` | Execution Hub UI |
| `/components/agents/cards/*.tsx` | Agent cards |
| `/hooks/useProfileIdentity.ts` | DB identity hook |
| `/hooks/useAgentData.ts` | Agent data hooks |

### 10.3 Version History

| Version | Date | Changes |
|---------|------|---------|
| v5.3 | 2026-01 | ExecutionChatAgent with 13 tools |
| v5.4 | 2026-01-20 | Added game plan context to ExecutionChatAgent |
| v9.0 | 2026-01 | Middleware stack with 50 patterns |
| Letta v1 | 2026-01 | Letta layer with 6 agents (feature-flagged) |

---

**End of Specification**

*Document generated: 2026-01-20 18:30 UTC*
*Next review: 2026-02-20*
