# IvyLevel Database Specification v5.2

> **Version**: 5.2.0 (Data Unification)
> **Last Updated**: 2026-01-17
> **Status**: PRODUCTION

---

## Executive Summary

This document reflects the **current production database schema** after Data Unification v5.2 implementation. The key architectural decision is:

| Data Category | Storage | Access Pattern |
|---------------|---------|----------------|
| **Identity Data** (brand_statement, spike, pillars) | Supabase `profiles` table | `useProfileIdentity()` hook → React Query |
| **Scoring Data** (ivy_score, results) | localStorage | `useResultsStore` Zustand |
| **Agent Outputs** (game plans, awards, programs) | Supabase `game_plans` table | React Query |
| **ReAct Cycles** (debugging/analytics) | Supabase `react_cycles` table | API only |
| **UI State** (tabs, modals) | Zustand (no persist) | Direct state |

---

## 1. Core Tables

### 1.1 `profiles` Table (Identity & Assessment)

**Primary Key**: `id` (UUID)
**Purpose**: Student identity, assessment data, and agent-derived identity synthesis

```sql
-- Actual production schema (verified 2026-01-17)
CREATE TABLE profiles (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Identity
  email TEXT,
  first_name TEXT,
  last_name TEXT,
  grade INTEGER,
  graduation_year INTEGER,
  high_school TEXT,

  -- Academic Profile
  target_major TEXT,
  intended_major TEXT,
  school_name TEXT,
  school_type TEXT,
  gpa FLOAT,
  sat_score INTEGER,
  act_score INTEGER,
  target_schools JSONB DEFAULT '[]',

  -- Archetype (Agent-Derived)
  archetype TEXT,                            -- e.g., 'academic_powerhouse'
  archetype_confidence FLOAT DEFAULT 0,

  -- Narrative Synthesis (v5.2 Data Unification - PRIMARY SOURCE)
  narrative_brand_statement TEXT,            -- "An inquisitive scholar..."
  narrative_dna TEXT,                        -- Core narrative DNA
  narrative_first_principle TEXT,            -- First principle
  narrative_themes JSONB DEFAULT '[]',       -- ["theme1", "theme2"]
  narrative_confidence FLOAT DEFAULT 0,
  narrative_updated_at TIMESTAMPTZ,
  brand_statement TEXT,                      -- Legacy column (fallback)

  -- Identity Synthesis (EC Agent Output - v5.2)
  spike TEXT,                                -- Unique differentiator
  spike_confidence FLOAT DEFAULT 0,
  pillars JSONB DEFAULT '[]',                -- 4 pillars: IDENTITY, APTITUDE, PASSION, SERVICE
  identity_synthesis JSONB DEFAULT '{}',     -- Full EC Agent output
  last_synthesized_at TIMESTAMPTZ,
  last_synthesized_by TEXT,                  -- 'narrative_synthesize' | 'gameplan_generate'

  -- Scoring
  ivy_score FLOAT,
  cri_score FLOAT,                           -- Context Relativity Index
  eds_score FLOAT,                           -- Execution Debt Score
  spike_score FLOAT,
  assessment_completed_at TIMESTAMPTZ,

  -- User State
  role TEXT,                                 -- 'student' | 'parent' | 'counselor'
  organization TEXT,
  onboarding_completed BOOLEAN DEFAULT false,
  onboarding_step INTEGER DEFAULT 0,
  preferences JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  avatar_url TEXT,

  -- Notification & Contact
  preferred_contact_time TEXT,
  notification_preferences JSONB DEFAULT '{}',
  last_activity_at TIMESTAMPTZ,
  last_login_at TIMESTAMPTZ,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_archetype ON profiles(archetype);
CREATE INDEX idx_profiles_brand_statement ON profiles(id) WHERE narrative_brand_statement IS NOT NULL;
```

### 1.2 `game_plans` Table (Agent Outputs)

**Primary Key**: `id` (UUID)
**Purpose**: Stores all agent-generated game plans, awards, programs data

```sql
CREATE TABLE game_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  profile_id UUID REFERENCES profiles(id),

  -- Core Plan Data
  plan_data JSONB DEFAULT '{}',
  plan_status TEXT DEFAULT 'active',

  -- Agent Outputs (v5.2)
  ec_generation JSONB,                       -- EC Generation Engine output
  awards_data JSONB,                         -- Awards Agent portfolio
  programs_data JSONB,                       -- Programs Agent portfolio

  -- ReAct Metadata
  react_metadata JSONB,                      -- Cycle visualization data

  -- Version Tracking
  generation_version TEXT DEFAULT '5.2',

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast profile lookups
CREATE INDEX idx_game_plans_profile_updated ON game_plans(profile_id, updated_at DESC);
```

### 1.3 `assessments` Table (Raw Assessment Data)

**Primary Key**: `id` (UUID)
**Purpose**: Stores raw assessment frame answers

```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),

  -- Assessment Data
  assessment_data JSONB NOT NULL,            -- Full assessment contract
  frame_data JSONB DEFAULT '{}',             -- Per-frame answers

  -- Status
  status TEXT DEFAULT 'in_progress',         -- 'in_progress' | 'completed'
  is_completed BOOLEAN DEFAULT false,
  completed_at TIMESTAMPTZ,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 1.4 `react_cycles` Table (ReAct Analytics)

**Primary Key**: `id` (UUID)
**Purpose**: Stores individual ReAct cycle data for debugging and analytics

```sql
-- From migration 032_v5.1_react_cycles_table.sql
CREATE TABLE react_cycles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Session Reference
  session_id UUID NOT NULL,
  profile_id UUID REFERENCES profiles(id),
  agent_type TEXT NOT NULL,                  -- 'ec' | 'awards' | 'programs' | 'gameplan'

  -- Cycle Data
  cycle_number INTEGER NOT NULL,

  -- Phase Data (JSONB for flexibility)
  think_phase JSONB DEFAULT '{}',
  act_phase JSONB DEFAULT '{}',
  observe_phase JSONB DEFAULT '{}',
  learn_phase JSONB DEFAULT '{}',

  -- Quality Metrics
  quality_score FLOAT,
  voice_score FLOAT,
  golden_similarity FLOAT,
  combined_score FLOAT,
  passed BOOLEAN DEFAULT false,

  -- Timing
  duration_ms INTEGER,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,

  -- Metadata
  version TEXT DEFAULT '5.1',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX idx_react_cycles_session ON react_cycles(session_id);
CREATE INDEX idx_react_cycles_agent ON react_cycles(agent_type, created_at DESC);
CREATE INDEX idx_react_cycles_profile ON react_cycles(profile_id);
```

### 1.5 `agent_memories` Table (Long-term Memory)

**Primary Key**: `id` (UUID)
**Purpose**: Vector-based memory storage for agent learning

```sql
-- From migration 030_agent_memory_hitl.sql
CREATE TABLE agent_memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Context
  agent_type TEXT NOT NULL,
  profile_id UUID REFERENCES profiles(id),

  -- Memory Content
  observation_type TEXT NOT NULL,            -- 'success' | 'failure' | 'insight'
  content TEXT NOT NULL,

  -- Vector Embedding (pgvector)
  embedding vector(1536),                    -- OpenAI embedding dimension

  -- Metadata
  confidence FLOAT DEFAULT 0.5,
  relevance_score FLOAT,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

-- Vector similarity index
CREATE INDEX idx_agent_memories_embedding ON agent_memories
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 2. Database Functions (v5.2)

### 2.1 `get_profile_identity(p_profile_id UUID)`

**Purpose**: Fetch identity data with null-safe defaults

```sql
CREATE OR REPLACE FUNCTION get_profile_identity(p_profile_id UUID)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    name TEXT,
    email TEXT,
    grade INTEGER,
    archetype_id UUID,
    archetype_name TEXT,
    archetype_confidence FLOAT,
    brand_statement TEXT,
    narrative_dna TEXT,
    narrative_themes JSONB,
    first_principle TEXT,
    spike TEXT,
    spike_confidence FLOAT,
    pillars JSONB,
    identity_synthesis JSONB,
    narrative_confidence FLOAT,
    last_synthesized_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        NULL::UUID as user_id,
        COALESCE(p.first_name || ' ' || p.last_name, p.first_name, p.last_name, '')::TEXT as name,
        p.email,
        p.grade,
        NULL::UUID as archetype_id,
        COALESCE(p.archetype, (p.identity_synthesis->>'archetype'))::TEXT as archetype_name,
        COALESCE(p.archetype_confidence, 0.0)::FLOAT as archetype_confidence,
        COALESCE(p.narrative_brand_statement, p.brand_statement, '')::TEXT as brand_statement,
        COALESCE(p.narrative_dna, '')::TEXT as narrative_dna,
        COALESCE(p.narrative_themes, '[]'::jsonb) as narrative_themes,
        COALESCE(p.narrative_first_principle, '')::TEXT as first_principle,
        COALESCE(p.spike, '')::TEXT as spike,
        COALESCE(p.spike_confidence, 0.0)::FLOAT as spike_confidence,
        COALESCE(p.pillars, '[]'::jsonb) as pillars,
        COALESCE(p.identity_synthesis, '{}'::jsonb) as identity_synthesis,
        COALESCE(p.narrative_confidence, 0.0)::FLOAT as narrative_confidence,
        COALESCE(p.last_synthesized_at, p.narrative_updated_at) as last_synthesized_at
    FROM profiles p
    WHERE p.id = p_profile_id;
END;
$$ LANGUAGE plpgsql STABLE;
```

### 2.2 `update_profile_identity(...)`

**Purpose**: Update identity columns, preserves existing values with COALESCE

```sql
CREATE OR REPLACE FUNCTION update_profile_identity(
    p_profile_id UUID,
    p_brand_statement TEXT DEFAULT NULL,
    p_narrative_dna TEXT DEFAULT NULL,
    p_narrative_themes JSONB DEFAULT NULL,
    p_first_principle TEXT DEFAULT NULL,
    p_spike TEXT DEFAULT NULL,
    p_spike_confidence FLOAT DEFAULT NULL,
    p_pillars JSONB DEFAULT NULL,
    p_identity_synthesis JSONB DEFAULT NULL,
    p_narrative_confidence FLOAT DEFAULT NULL,
    p_source TEXT DEFAULT 'api'
)
RETURNS VOID AS $$
BEGIN
    UPDATE profiles SET
        narrative_brand_statement = COALESCE(p_brand_statement, narrative_brand_statement),
        narrative_dna = COALESCE(p_narrative_dna, narrative_dna),
        narrative_themes = COALESCE(p_narrative_themes, narrative_themes),
        narrative_first_principle = COALESCE(p_first_principle, narrative_first_principle),
        narrative_confidence = COALESCE(p_narrative_confidence, narrative_confidence),
        spike = COALESCE(p_spike, spike),
        spike_confidence = COALESCE(p_spike_confidence, spike_confidence),
        pillars = COALESCE(p_pillars, pillars),
        identity_synthesis = COALESCE(p_identity_synthesis, identity_synthesis),
        last_synthesized_at = NOW(),
        last_synthesized_by = p_source,
        narrative_updated_at = NOW(),
        updated_at = NOW()
    WHERE id = p_profile_id;
END;
$$ LANGUAGE plpgsql;
```

### 2.3 `upsert_game_plan(...)`

**Purpose**: Create or update game plan with agent outputs

```sql
CREATE OR REPLACE FUNCTION upsert_game_plan(
    p_profile_id UUID,
    p_user_id UUID,
    p_plan_data JSONB DEFAULT NULL,
    p_ec_generation JSONB DEFAULT NULL,
    p_awards_data JSONB DEFAULT NULL,
    p_programs_data JSONB DEFAULT NULL,
    p_react_metadata JSONB DEFAULT NULL,
    p_generation_version TEXT DEFAULT '5.2'
)
RETURNS UUID AS $$
DECLARE
    v_game_plan_id UUID;
BEGIN
    SELECT id INTO v_game_plan_id
    FROM game_plans
    WHERE profile_id = p_profile_id
    ORDER BY updated_at DESC
    LIMIT 1;

    IF v_game_plan_id IS NULL THEN
        INSERT INTO game_plans (
            user_id, profile_id, plan_data, ec_generation,
            awards_data, programs_data, react_metadata,
            generation_version, plan_status, created_at, updated_at
        ) VALUES (
            p_user_id, p_profile_id, COALESCE(p_plan_data, '{}'::jsonb),
            p_ec_generation, p_awards_data, p_programs_data,
            p_react_metadata, p_generation_version, 'active', NOW(), NOW()
        )
        RETURNING id INTO v_game_plan_id;
    ELSE
        UPDATE game_plans SET
            plan_data = COALESCE(p_plan_data, plan_data),
            ec_generation = COALESCE(p_ec_generation, ec_generation),
            awards_data = COALESCE(p_awards_data, awards_data),
            programs_data = COALESCE(p_programs_data, programs_data),
            react_metadata = COALESCE(p_react_metadata, react_metadata),
            generation_version = p_generation_version,
            updated_at = NOW()
        WHERE id = v_game_plan_id;
    END IF;

    RETURN v_game_plan_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 3. Frontend Data Access Patterns

### 3.1 Identity Data (Database → useProfileIdentity)

```typescript
// hooks/useProfileIdentity.ts
import { useQuery } from '@tanstack/react-query';

export function useProfileIdentity(profileId: string | null) {
  return useQuery({
    queryKey: ['profile', 'identity', profileId],
    queryFn: async () => {
      const { data, error } = await supabase
        .rpc('get_profile_identity', { p_profile_id: profileId });
      if (error) return null;
      return transformDbRow(data[0]);
    },
    enabled: !!profileId,
    staleTime: 30 * 1000,  // 30 seconds
  });
}

// Usage in components
const { data: identity } = useProfileIdentity(profileId);
const brandStatement = identity?.brandStatement;
```

### 3.2 Scoring Data (localStorage → useResultsStore)

```typescript
// lib/store/useResultsStore.ts
export const useResultsStore = create<ResultsStoreState>()(
  persist(
    immer((set, get) => ({
      results: null,
      ivy_score: null,
      school_probabilities: [],
      // ... scoring fields

      setResults: (results) => set((state) => {
        state.results = results;
        state.ivy_score = results.ivy_ready_score;
        // ...
      }),
    })),
    {
      name: 'ivyquest-results',
      partialize: (state) => ({
        // ONLY scoring data persisted (not identity)
        results: state.results,
        scored_at: state.scored_at,
        booster_recommendations: state.booster_recommendations,
        twin_fleet: state.twin_fleet,
      }),
    }
  )
);
```

### 3.3 ProfileId Resolution

```typescript
// Dashboard page.tsx
const { user } = useAuth();
const storeProfileId = useSessionStore((s) => s.profile_id);
const storeUserId = useSessionStore((s) => s.user_id);

// Priority: auth user ID > store profile_id > store user_id
const profileId = user?.id || storeProfileId || storeUserId;
```

---

## 4. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW (v5.2 Unified)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌────────────────┐         ┌────────────────┐                         │
│   │ Assessment     │         │ Multi-Agent    │                         │
│   │ Agent          │         │ Orchestrator   │                         │
│   └───────┬────────┘         └───────┬────────┘                         │
│           │                          │                                   │
│           ▼                          ▼                                   │
│   ┌────────────────────────────────────────────────────┐                │
│   │              API Layer (Next.js Routes)            │                │
│   │  /api/agents/narrative/synthesize                  │                │
│   │  /api/agents/gameplan/generate                     │                │
│   └────────────────────────┬───────────────────────────┘                │
│                            │                                             │
│                            ▼                                             │
│   ┌────────────────────────────────────────────────────┐                │
│   │              SUPABASE (PostgreSQL)                 │                │
│   │  ┌──────────────┐  ┌──────────────┐               │                │
│   │  │   profiles   │  │  game_plans  │               │                │
│   │  │──────────────│  │──────────────│               │                │
│   │  │brand_statement│ │ ec_generation│               │                │
│   │  │narrative_dna │  │ awards_data  │               │                │
│   │  │spike         │  │ programs_data│               │                │
│   │  │pillars       │  │ react_meta   │               │                │
│   │  └──────────────┘  └──────────────┘               │                │
│   └────────────────────────┬───────────────────────────┘                │
│                            │                                             │
│                            ▼                                             │
│   ┌────────────────────────────────────────────────────┐                │
│   │              React Query Cache                      │                │
│   │  ['profile', 'identity', profileId]                │                │
│   │  ['gameplan', profileId]                           │                │
│   │  staleTime: 30s                                    │                │
│   └────────────────────────┬───────────────────────────┘                │
│                            │                                             │
│           ┌────────────────┴────────────────┐                           │
│           ▼                                 ▼                            │
│   ┌──────────────────┐            ┌──────────────────┐                  │
│   │  AssessmentTab   │            │ AssessmentAgent  │                  │
│   │  (same data!)    │  ═══════   │     Card         │                  │
│   │  "Inquisitive    │            │  "Inquisitive    │                  │
│   │   scholar..."    │            │   scholar..."    │                  │
│   └──────────────────┘            └──────────────────┘                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────────────┐
   │                    SCORING DATA (Separate Path)                      │
   │                                                                      │
   │   /api/score → useResultsStore → localStorage → Frames 4/5/6       │
   │                                                                      │
   └─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Migration History

| Migration | Version | Purpose |
|-----------|---------|---------|
| `003_profiles_v10.sql` | 10.0 | Initial profiles table |
| `010_beta_complete_schema.sql` | 10.0 | Beta schema |
| `020_evaluation_and_workflows.sql` | 13.0 | Workflows |
| `030_agent_memory_hitl.sql` | 13.1 | Agent memory + HITL |
| `031_v13.1_complete_schema.sql` | 13.1 | Complete schema |
| `032_v5.1_react_cycles_table.sql` | 5.1 | ReAct cycle tracking |
| `033_data_unification_v5.2.sql` | 5.2 | **Data Unification** - identity columns + helper functions |

---

## 6. Key Constraints

### 6.1 Data Integrity

- **Profiles**: `id` is the primary key used for all lookups
- **Auth user ID** = **Profile ID** in most cases (Supabase auth links)
- **Graceful fallback**: All DB functions use COALESCE for null safety

### 6.2 Performance

- **Stale time**: 30 seconds for identity data (balance between freshness and performance)
- **Indexes**: On `email`, `archetype`, and `brand_statement` for fast lookups
- **Vector index**: IVFFlat on agent_memories for similarity search

### 6.3 Security

- **RLS enabled** on all tables
- **User can only access own data**: `auth.uid() = user_id` policies
- **Service role** required for cross-user operations

---

## Appendix: Column Reference

### Profiles Table Columns (Complete List)

| Column | Type | Purpose |
|--------|------|---------|
| `id` | UUID | Primary key |
| `email` | TEXT | User email |
| `first_name` | TEXT | First name |
| `last_name` | TEXT | Last name |
| `grade` | INTEGER | Current grade (9-12) |
| `graduation_year` | INTEGER | Expected graduation |
| `high_school` | TEXT | School name |
| `target_major` | TEXT | Intended major |
| `school_name` | TEXT | School name (alt) |
| `school_type` | TEXT | public/private/magnet |
| `gpa` | FLOAT | GPA |
| `sat_score` | INTEGER | SAT score |
| `act_score` | INTEGER | ACT score |
| `target_schools` | JSONB | Target school list |
| `intended_major` | TEXT | Major (alt) |
| `archetype` | TEXT | Agent-derived archetype |
| `archetype_confidence` | FLOAT | Archetype confidence |
| `narrative_brand_statement` | TEXT | **PRIMARY** brand statement |
| `narrative_dna` | TEXT | Narrative DNA |
| `narrative_first_principle` | TEXT | First principle |
| `narrative_themes` | JSONB | Narrative themes array |
| `narrative_confidence` | FLOAT | Narrative confidence |
| `narrative_updated_at` | TIMESTAMPTZ | Last narrative update |
| `brand_statement` | TEXT | **LEGACY** brand statement (fallback) |
| `spike` | TEXT | **v5.2** Unique spike |
| `spike_confidence` | FLOAT | **v5.2** Spike confidence |
| `pillars` | JSONB | **v5.2** Four pillars |
| `identity_synthesis` | JSONB | **v5.2** Full EC Agent output |
| `last_synthesized_at` | TIMESTAMPTZ | **v5.2** Last synthesis time |
| `last_synthesized_by` | TEXT | **v5.2** Source of synthesis |
| `ivy_score` | FLOAT | Ivy Ready Score |
| `cri_score` | FLOAT | Context Relativity Index |
| `eds_score` | FLOAT | Execution Debt Score |
| `spike_score` | FLOAT | Spike score |
| `assessment_completed_at` | TIMESTAMPTZ | Assessment completion |
| `role` | TEXT | User role |
| `organization` | TEXT | Organization |
| `onboarding_completed` | BOOLEAN | Onboarding status |
| `onboarding_step` | INTEGER | Current step |
| `preferences` | JSONB | User preferences |
| `is_active` | BOOLEAN | Active status |
| `is_verified` | BOOLEAN | Verified status |
| `avatar_url` | TEXT | Avatar URL |
| `preferred_contact_time` | TEXT | Contact preference |
| `notification_preferences` | JSONB | Notification prefs |
| `last_activity_at` | TIMESTAMPTZ | Last activity |
| `last_login_at` | TIMESTAMPTZ | Last login |
| `created_at` | TIMESTAMPTZ | Created timestamp |
| `updated_at` | TIMESTAMPTZ | Updated timestamp |

---

*This specification reflects the production database schema as of 2026-01-17 with Data Unification v5.2.*
