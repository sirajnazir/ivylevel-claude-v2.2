# IvyQuest Data Architecture Audit

> **Version**: 1.0.0
> **Date**: 2026-01-17
> **Status**: CRITICAL - Data Fragmentation Identified

---

## Executive Summary

This audit reveals **critical data fragmentation** across the IvyQuest platform where the same data exists in multiple locations without synchronization. The most visible symptom is the brand statement mismatch between the Dashboard Assessment Tab and the Multi-Agent Assessment Card.

**Root Cause**: No single source of truth. Data flows through multiple paths (localStorage, React Query cache, Zustand stores) without database persistence or synchronization.

---

## 1. Database Schema Audit

### 1.1 Tables Inventory

| Table | Primary Key | Key Columns | Purpose |
|-------|-------------|-------------|---------|
| `profiles` | id (UUID) | narrative_dna, narrative_themes, archetype_id | Student identity |
| `assessments` | id (UUID) | assessment_data, frame_data | Assessment answers |
| `game_plans` | id (UUID) | plan_data | Agent-generated plans |
| `archetypes` | id (UUID) | name, description | Archetype reference |
| `react_cycles` | id (UUID) | cycle data | ReAct cycle analytics |
| `react_sessions` | id (UUID) | session data | Session aggregates |
| `agent_memories` | id (UUID) | observation_type, embedding | Memory store |

### 1.2 Profiles Table Schema

```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY,
  assessment_id UUID REFERENCES assessments(id),
  user_id UUID,
  name TEXT,
  email TEXT,
  grade INTEGER,

  -- Archetype (agent-derived)
  archetype_id UUID REFERENCES archetypes(id),
  archetype_confidence FLOAT,
  archetype_rationale TEXT,

  -- Narrative DNA (Identity Synthesis)
  narrative_dna TEXT,              -- ✅ EXISTS
  narrative_themes JSONB DEFAULT '[]', -- ✅ EXISTS
  narrative_confidence FLOAT,

  -- MISSING: brand_statement      -- ❌ NOT IN SCHEMA
  -- MISSING: first_principle      -- ❌ NOT IN SCHEMA
  -- MISSING: spike               -- ❌ NOT IN SCHEMA
  -- MISSING: pillars             -- ❌ NOT IN SCHEMA

  -- Other fields...
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

### 1.3 Critical Schema Gaps

| Field | Expected Location | Actual Status | Impact |
|-------|-------------------|---------------|--------|
| `brand_statement` | profiles | ❌ Missing | Cannot persist brand statement to DB |
| `first_principle` | profiles | ❌ Missing | Lost on browser clear |
| `spike` | profiles | ❌ Missing | EC Agent spike not persisted |
| `pillars` | profiles | ❌ Missing | 4-pillar analysis not persisted |

---

## 2. Frontend State Management Audit

### 2.1 Zustand Stores

| Store | File | Key State Fields | Persisted? | Storage Key |
|-------|------|------------------|------------|-------------|
| `useResultsStore` | `/lib/store/useResultsStore.ts` | brand_statement, narrative_dna, themes | ✅ localStorage | `ivyquest-results` |
| `useStudentStore` | `/lib/store/useStudentStore.ts` | profile | ✅ localStorage | `ivyquest-student-profile` |
| `useSessionStore` | `/lib/store/useSessionStore.ts` | session_id, profile_id | ✅ localStorage | `ivyquest-session` |

### 2.2 useResultsStore Details (CRITICAL)

**File**: `/lib/store/useResultsStore.ts`

```typescript
interface ResultsStoreState {
  // Narrative Synthesis (Jenny's Formula)
  narrative: NarrativeSynthesis | null;
  brand_statement: string;        // ⚠️ localStorage only
  narrative_dna: string;          // ⚠️ localStorage only
  first_principle: string;        // ⚠️ localStorage only
  narrative_themes: string[];     // ⚠️ localStorage only
  narrative_confidence: number;

  // Strategic Intelligence (v1.1.0)
  identity_synthesis: IdentitySynthesis | null;  // ⚠️ localStorage only
  portfolio_audit: PortfolioAudit | null;
  awards_portfolio: AwardsPortfolio | null;
  programs_portfolio: ProgramsPortfolio | null;

  // Actions
  setNarrative: (narrative: NarrativeSynthesis) => void;
  setGamePlanResults: (results: GamePlanApiResponse) => void;
}
```

**Persistence Configuration**:
```typescript
persist(
  immer(...),
  {
    name: 'ivyquest-results',
    partialize: (state) => ({
      results: state.results,
      narrative: state.narrative,     // ← Only this is persisted
      booster_recommendations: state.booster_recommendations,
      twin_fleet: state.twin_fleet,
      scored_at: state.scored_at,
      narrative_synthesized_at: state.narrative_synthesized_at,
    }),
  }
)
```

### 2.3 React Query Hooks

| Hook | File | Endpoint | Query Key | Stale Time | Used By |
|------|------|----------|-----------|------------|---------|
| `useNarrativeDNA` | `/hooks/useAgentData.ts` | `/api/agents/narrative/{profileId}` | `['assessment', 'narrative', profileId]` | 10 min | AssessmentAgentCard |
| `useGamePlan` | `/hooks/useAgentData.ts` | `/api/agents/gameplan/generate` | `['gameplan', profileId]` | 5 min | GamePlanTab, MultiAgentsTab |
| `useAwardMatches` | `/hooks/useAgentData.ts` | `/api/agents/awards/match/{profileId}` | `['awards', 'match', profileId]` | 10 min | AwardsAgentCard |

### 2.4 useNarrativeDNA Hook (CRITICAL)

**File**: `/hooks/useAgentData.ts:43-63`

```typescript
export function useNarrativeDNA(profileId: string | null) {
  return useQuery({
    queryKey: ['assessment', 'narrative', profileId],
    queryFn: async () => {
      const result = await agentApi.synthesizeNarrativeDNA(profileId);
      // Transform backend response
      return {
        dna: rawData.narrative_dna || rawData.dna || '',
        themes: rawData.themes || [],
        confidence: rawData.confidence || 0,
        rationale: rawData.brand_statement || rawData.rationale || '',
      } as NarrativeDNA;
      // ⚠️ NO SYNC TO useResultsStore
      // ⚠️ NO PERSISTENCE TO DATABASE
    },
    staleTime: 10 * 60 * 1000,  // 10 minutes
  });
}
```

---

## 3. API Endpoints Audit

### 3.1 Narrative-Related Endpoints

| Endpoint | Method | Input | Output | Persists to DB? |
|----------|--------|-------|--------|-----------------|
| `/api/agents/narrative/synthesize` | POST | `{profile_id, assessment_contract}` | `{brand_statement, narrative_dna, themes}` | ❌ No |
| `/api/agents/narrative/{profileId}` | GET | `profileId` | `{narrative_dna, themes, confidence}` | ❌ No |
| `/api/agents/gameplan/generate` | POST | `{profile_id}` | `{game_plan, _react}` | ⚠️ Partial (agent_memories only) |

### 3.2 Data Flow Through APIs

```
┌────────────────────────────────────────────────────────────────────────┐
│                        API DATA FLOW                                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Dashboard Load:                                                        │
│  ────────────────                                                       │
│  1. agentV2Api.synthesizeNarrative() → response                         │
│  2. setNarrative(response) → useResultsStore (localStorage)             │
│  3. ❌ NO DATABASE WRITE                                                │
│                                                                         │
│  AssessmentAgentCard Load:                                              │
│  ─────────────────────────                                              │
│  1. useNarrativeDNA(profileId) → agentApi.synthesizeNarrativeDNA()      │
│  2. Result stored in React Query cache only                             │
│  3. ❌ NO SYNC TO useResultsStore                                       │
│  4. ❌ NO DATABASE WRITE                                                │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Component → Data Source Mapping

### 4.1 Critical Data: Brand Statement

| Component | File:Line | Data Source | Value Example |
|-----------|-----------|-------------|---------------|
| AssessmentTab | AssessmentTab.tsx:73 | `useResultsStore.brand_statement` | "A versatile scholar..." |
| AssessmentAgentCard | AssessmentAgentCard.tsx:21 | `useNarrativeDNA().rationale` | "A South Asian Muslim..." |
| Frame6ProfileReveal | Frame6ProfileReveal.tsx:238 | `useResultsStore.brand_statement` | "A versatile scholar..." |
| AgentDetailModal | AgentDetailModal.tsx:248 | `data.brand_statement` (from hook) | "A South Asian Muslim..." |

### 4.2 Data Source Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CURRENT DATA FLOW (FRAGMENTED)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│         Dashboard Load                    Multi-Agent Tab                │
│              │                                  │                        │
│              ▼                                  ▼                        │
│    ┌─────────────────┐               ┌─────────────────┐                │
│    │agentV2Api       │               │useNarrativeDNA  │                │
│    │.synthesize      │               │(different API)  │                │
│    │Narrative()      │               │                 │                │
│    └────────┬────────┘               └────────┬────────┘                │
│             │                                 │                          │
│             ▼                                 ▼                          │
│    ┌─────────────────┐               ┌─────────────────┐                │
│    │useResultsStore  │               │React Query      │                │
│    │(localStorage)   │               │(memory cache)   │                │
│    └────────┬────────┘               └────────┬────────┘                │
│             │                                 │                          │
│             ▼                                 ▼                          │
│    ┌─────────────────┐               ┌─────────────────┐                │
│    │AssessmentTab    │               │AssessmentAgent  │                │
│    │"Generic brand"  │ ← MISMATCH! → │Card "Rich brand"│                │
│    └─────────────────┘               └─────────────────┘                │
│                                                                          │
│    ❌ DATABASE NOT USED AS SOURCE OF TRUTH                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Components by Data Source

**Components using `useResultsStore`:**
- `AssessmentTab.tsx` - reads brand_statement, narrativeThemes
- `Frame6ProfileReveal.tsx` - reads/writes brand_statement
- `Frame5Reveal.tsx` - reads results
- `Frame4Reveal.tsx` - reads results
- `Frame5GamePlan.tsx` - reads results
- `GamePlanAgentCard.tsx` - reads identity_synthesis

**Components using `useNarrativeDNA` hook:**
- `AssessmentAgentCard.tsx` - reads dna, themes, rationale
- `useDashboardV13Data` hook - combines with other data

**Components using BOTH (potential conflicts):**
- `AssessmentAgentCard.tsx` - uses BOTH useNarrativeDNA AND useResultsStore

---

## 5. Gap Analysis

### 5.1 Synchronization Gaps

| # | Gap | Location A | Location B | Impact | Severity |
|---|-----|------------|------------|--------|----------|
| 1 | Brand statement mismatch | useResultsStore | useNarrativeDNA | User sees different brand statements | 🔴 Critical |
| 2 | Narrative DNA mismatch | useResultsStore | useNarrativeDNA | Inconsistent display | 🔴 Critical |
| 3 | Agent outputs not persisted | React Query | Database | Data lost on logout | 🔴 Critical |
| 4 | Strategic Intelligence local-only | useResultsStore | - | EC Agent data lost | 🟡 High |
| 5 | No DB column for brand_statement | - | Database schema | Cannot persist | 🔴 Critical |

### 5.2 Data Not Persisted to Database

| Data | Generated By | Current Storage | Should Be In |
|------|--------------|-----------------|--------------|
| brand_statement | Assessment Agent | localStorage only | profiles.brand_statement |
| narrative_dna | Assessment Agent | localStorage only | profiles.narrative_dna ✅ (exists) |
| first_principle | Assessment Agent | localStorage only | profiles.first_principle |
| spike | EC Agent | localStorage only | profiles.spike |
| pillars | EC Agent | localStorage only | profiles.pillars |
| identity_synthesis | EC Agent | localStorage only | game_plans.identity_synthesis |
| awards_portfolio | Awards Agent | React Query only | game_plans.awards_data |
| programs_portfolio | Programs Agent | React Query only | game_plans.programs_data |

### 5.3 Root Cause Summary

The fundamental problem is: **No single source of truth**

1. **Original dashboard** was built with localStorage persistence (useResultsStore)
2. **Multi-agent system** was built separately with API-only data (React Query hooks)
3. **Neither writes to database** consistently
4. **No synchronization mechanism** exists between the two
5. **Database schema** is missing key columns (brand_statement, spike, pillars)

---

## 6. Solution Options Analysis

### Option A: Sync Agent Output to Existing Stores (Quick Fix)

**Implementation:**
```typescript
// After useNarrativeDNA returns, sync to Zustand
const { data } = useNarrativeDNA(profileId);
useEffect(() => {
  if (data) {
    useResultsStore.getState().setNarrative({
      brand_statement: data.rationale,
      narrative_dna: data.dna,
      themes: data.themes,
      // ...
    });
  }
}, [data]);
```

| Pros | Cons |
|------|------|
| Quick to implement (2-4 hours) | localStorage still only source |
| Minimal code changes | No multi-device sync |
| Immediate fix for visible issue | Band-aid, not fix |

**Verdict:** ⚠️ Quick fix but technical debt

---

### Option B: Unified Frontend Store

**Implementation:**
- Create single `useStudentDataStore`
- All components read from this store
- Store populated by whichever API responds first

| Pros | Cons |
|------|------|
| Single frontend source | Still no database persistence |
| Consistent across components | Complex store management |
| No more conflicts | Race conditions possible |

**Verdict:** ⚠️ Better but incomplete

---

### Option C: Database as Single Source of Truth

**Implementation:**
1. Add missing columns to `profiles` table
2. Agent endpoints persist to DB on success
3. All reads go through React Query → DB
4. Zustand only for UI state

| Pros | Cons |
|------|------|
| TRUE single source of truth | Larger implementation effort |
| Data persists across sessions | Need DB migration |
| Clean architecture | Need to update all components |
| Scalable | More API calls |

**Verdict:** ✅ Production-grade solution

---

### Option D: Hybrid Approach (RECOMMENDED)

**Implementation:**
- **Critical Data** (identity, profile) → Database ONLY
- **Expensive Data** (game plans) → Database + React Query cache
- **Ephemeral Data** (ReAct cycles in progress) → React Query only
- **UI State** (tabs, modals) → Zustand only (no persist)
- **Preferences** (theme) → localStorage only

**Data Classification:**

| Category | Examples | Storage |
|----------|----------|---------|
| Critical | brand_statement, narrative_dna, archetype, spike | DB + React Query |
| Expensive | game_plan, ec_generation | DB + React Query |
| Transient | in-progress ReAct cycles | React Query only |
| UI State | currentTab, selectedAgent | Zustand (no persist) |
| Preferences | theme, notifications | localStorage |

| Pros | Cons |
|------|------|
| Best of all worlds | Need to classify all data |
| Optimal performance | More complex architecture |
| Clear data ownership | Training for team |
| Minimal unnecessary DB writes | |

**Verdict:** ✅ Best long-term solution

---

## 7. Recommended Architecture

### 7.1 Recommendation: Option D (Hybrid) with Database as Foundation

**Architecture Diagram:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SUPABASE DATABASE                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │  profiles   │ │ game_plans  │ │react_cycles │ │agent_memories│       │
│  │─────────────│ │─────────────│ │─────────────│ │─────────────│       │
│  │brand_stmt ★ │ │ec_generation│ │cycle_data   │ │observations │       │
│  │narrative_dna│ │awards_data  │ │scores       │ │learnings    │       │
│  │archetype    │ │programs_data│ │             │ │             │       │
│  │spike ★      │ │             │ │             │ │             │       │
│  │pillars ★    │ │             │ │             │ │             │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
│  ★ = NEW COLUMNS REQUIRED                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↑
                                    │ Writes
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
    ┌────┴─────┐             ┌──────┴──────┐            ┌──────┴──────┐
    │ Synth    │             │ Agent       │            │ Manual      │
    │ API      │             │ Service     │            │ Edit        │
    └──────────┘             └─────────────┘            └─────────────┘
                                    │
                                    ↓ Reads
                          ┌─────────────────────┐
                          │    REACT QUERY      │
                          │  ─────────────────  │
                          │  useProfile()       │
                          │  useGamePlan()      │
                          │  Stale time: 30s    │
                          └──────────┬──────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
        ┌─────┴─────┐          ┌─────┴─────┐          ┌─────┴─────┐
        │Assessment │          │Multi-Agent│          │ Other     │
        │Tab        │          │Tab        │          │ Tabs      │
        └───────────┘          └───────────┘          └───────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │
                          ┌──────────┴──────────┐
                          │   ZUSTAND STORE     │
                          │  (UI State Only)    │
                          │  ─────────────────  │
                          │  currentTab         │
                          │  expandedSections   │
                          │  selectedAgentId    │
                          │  modalOpen          │
                          └─────────────────────┘
```

### 7.2 Schema Changes Required

```sql
-- Migration: Add missing columns to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS brand_statement TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS first_principle TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS spike TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS pillars JSONB DEFAULT '[]';

-- Ensure game_plans stores all agent outputs
ALTER TABLE game_plans
ADD COLUMN IF NOT EXISTS ec_generation JSONB,
ADD COLUMN IF NOT EXISTS awards_data JSONB,
ADD COLUMN IF NOT EXISTS programs_data JSONB,
ADD COLUMN IF NOT EXISTS identity_synthesis JSONB;

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
```

### 7.3 Code Changes Required

| File | Change | Priority |
|------|--------|----------|
| `/supabase/migrations/033_*.sql` | Add brand_statement, spike, pillars to profiles | P0 |
| `/hooks/useProfile.ts` | Create unified profile hook reading from DB | P0 |
| `/app/api/agents/narrative/synthesize/route.ts` | Persist output to profiles table | P0 |
| `/app/api/agents/narrative/[profileId]/route.ts` | Persist output to profiles table | P0 |
| `/components/tabs/AssessmentTab.tsx` | Use useProfile instead of useResultsStore | P0 |
| `/components/agents/cards/AssessmentAgentCard.tsx` | Use useProfile instead of useNarrativeDNA | P0 |
| `/lib/store/useResultsStore.ts` | Remove data fields, keep UI fields only | P1 |
| Agent Service endpoints | Persist to DB on completion | P1 |
| All other components using old stores | Migrate to new hooks | P2 |

### 7.4 Migration Steps

**Phase 1: Schema (Day 1)**
1. Add missing columns to profiles table
2. Add missing columns to game_plans table
3. Verify migrations apply cleanly

**Phase 2: Hooks (Day 1-2)**
1. Create `useProfile()` unified hook that reads from Supabase
2. Create `useGamePlanData()` unified hook
3. Both read via React Query with 30-second stale time

**Phase 3: Persistence (Day 2-3)**
1. Update `/api/agents/narrative/synthesize` to persist brand_statement to profiles
2. Update `/api/agents/narrative/{profileId}` to read from profiles first
3. Update agent service to persist to DB on completion

**Phase 4: Component Migration (Day 3-4)**
1. Update AssessmentTab to use useProfile
2. Update AssessmentAgentCard to use useProfile
3. Update all other components using old stores

**Phase 5: Cleanup (Day 4-5)**
1. Remove data fields from Zustand stores (keep UI state only)
2. Remove localStorage data persistence
3. Remove old hooks
4. Test all flows

---

## 8. Immediate Fix (Quick Win)

For an immediate fix while the full migration is planned:

**Sync useNarrativeDNA to useResultsStore:**

```typescript
// In AssessmentAgentCard.tsx or a parent component
import { useEffect } from 'react';
import { useNarrativeDNA } from '@/hooks/useAgentData';
import { useResultsStore } from '@/lib/store/useResultsStore';

export function SyncNarrativeToStore({ profileId }: { profileId: string }) {
  const { data } = useNarrativeDNA(profileId);
  const setNarrative = useResultsStore((s) => s.setNarrative);

  useEffect(() => {
    if (data?.dna && data.dna !== '') {
      setNarrative({
        brand_statement: data.rationale || '',
        narrative_dna: data.dna || '',
        first_principle: '',  // Not available from this hook
        themes: data.themes || [],
        confidence: data.confidence || 0,
      });
    }
  }, [data, setNarrative]);

  return null;
}
```

This ensures the most recent Assessment Agent output is synced to the store that AssessmentTab reads from.

---

## Appendix A: localStorage Keys

| Key | Data Type | Written By | Critical? |
|-----|-----------|------------|-----------|
| `ivyquest-results` | ResultsStoreState | useResultsStore | ✅ Yes |
| `ivyquest-student-profile` | StudentProfile | useStudentStore | ✅ Yes |
| `ivyquest-session` | SessionState | useSessionStore | ✅ Yes |

---

## Appendix B: Files Audited

```
/lib/store/useResultsStore.ts    - Zustand store (critical)
/lib/store/useStudentStore.ts    - Zustand store
/lib/store/useSessionStore.ts    - Zustand store
/hooks/useAgentData.ts           - React Query hooks (critical)
/app/dashboard/page.tsx          - Dashboard data flow
/components/tabs/AssessmentTab.tsx - Brand statement display
/components/agents/cards/AssessmentAgentCard.tsx - Agent card (critical)
/supabase/migrations/003_profiles_v10.sql - DB schema
```

---

*This audit was generated on 2026-01-17. Implementation should begin with Phase 1 (Schema) immediately.*
