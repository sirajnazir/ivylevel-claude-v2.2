# IvyQuest v2.2 - Limitation Analysis Report

**Date**: January 5, 2026
**Version**: 2.2.0
**Author**: Claude Code
**Status**: Critical Review Required

---

## Executive Summary

This report provides a comprehensive analysis of the current data persistence architecture, identifying gaps between the documented database schema, actual Supabase implementation, code usage, and user experience requirements.

### Critical Finding

**Assessment data is NOT linked to user accounts**. Currently:
- Assessment data persists in **browser localStorage** (via Zustand)
- Supabase persistence is **disabled by default** (`ENABLE_SUPABASE_PERSISTENCE=false`)
- The `profiles` table exists in migrations but is **NOT the auth profiles table**
- User authentication (Auth profiles) and assessment data are **completely separate**

This means:
- Users lose assessment data when switching browsers/devices
- Coaches cannot access student assessments
- Multi-device experience is broken

---

## 1. Current Data Storage Architecture

### 1.1 Zustand Stores (localStorage)

| Store | Persist Key | Data Stored | Persists Across |
|-------|-------------|-------------|-----------------|
| `useStudentStore` | `ivyquest-student-profile` | Full 58-attribute student profile | Same browser only |
| `useSessionStore` | `ivyquest-session-v10` | Session ID, frame progress, quiz answers, XP | Same browser only |
| `useResultsStore` | `ivyquest-results` | Assessment results, booster recommendations | Same browser only |
| `useFrame3Store` | `ivyquest-frame3-operating` | Frame 3 quiz responses | Same browser only |
| `useTwinStore` | `ivyquest-twin-fleet` | Digital twin configuration | Same browser only |
| `useInsightsStore` | *No persist* | Real-time insights | Not persisted |
| `useFrame4Store` | *No persist* | Score display state | Not persisted |
| `useFrame5Store` | *No persist* | Booster selection state | Not persisted |
| `useUIStore` | *No persist* | UI state (modals, loading) | Not persisted |

**Total localStorage data**: ~50-100KB per user session

### 1.2 Supabase Tables (Actual vs Documented)

#### Tables Defined in Code (`database.types.ts`)

| Table | Defined | Used in Code | Notes |
|-------|---------|--------------|-------|
| `assessments` | Yes | Yes (API route) | Disabled by default |
| `coach_sessions` | Yes | Unknown | Schema defined but usage unclear |

#### Tables Defined in Migrations (May Not Be Deployed)

| Migration | Table | Purpose | Deployed? |
|-----------|-------|---------|-----------|
| `001_create_assessments.sql` | `assessments` | Store completed assessments | Unknown |
| `002_archetypes.sql` | `archetypes` | Pre-defined student archetypes | Unknown |
| `003_profiles_v10.sql` | `profiles` | Enhanced agent-derived profiles | Unknown |
| `004_crises.sql` | `crises` | Crisis/blocker tracking | Unknown |
| `005_chetty_baselines.sql` | `chetty_baselines` | Research-based multipliers | Unknown |
| `006_agent_state_versions.sql` | `agent_state_versions` | Agent state tracking | Unknown |
| `007_opportunities_awards.sql` | `opportunities`, `awards` | Summer programs, awards DB | Unknown |
| `008_projects.sql` | `projects` | Student project tracking | Unknown |
| `009_migrations_tracker.sql` | `migrations_tracker` | Migration history | Unknown |

#### Auth Profiles Table (Created by Beta Auth)

| Table | Purpose | Fields |
|-------|---------|--------|
| `profiles` (auth) | User authentication | id, email, role, first_name, last_name, is_active |

**CONFLICT**: There are TWO different `profiles` tables:
1. Auth profiles (created by our beta auth system) - for user authentication
2. Agent profiles (from migration 003) - for v10.0 agent data

These serve different purposes and have different schemas!

---

## 2. Data Flow Analysis

### 2.1 Current Flow (Broken)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CURRENT STATE (BROKEN)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  User A (Browser 1)              User A (Browser 2/Device 2)            │
│  ┌─────────────────┐             ┌─────────────────┐                    │
│  │ localStorage:   │             │ localStorage:   │                    │
│  │ - profile ✓     │             │ - (empty)       │                    │
│  │ - session ✓     │    ╳        │ - NO DATA       │                    │
│  │ - results ✓     │  ─────────► │                 │                    │
│  └─────────────────┘   BROKEN    └─────────────────┘                    │
│                                                                          │
│  Supabase Auth                   Supabase Data                          │
│  ┌─────────────────┐             ┌─────────────────┐                    │
│  │ profiles (auth) │      ╳      │ assessments     │                    │
│  │ - user_id       │  ─────────► │ - NO user_id    │                    │
│  │ - email         │  NOT LINKED │ - session_id    │                    │
│  │ - role          │             │ - email (opt)   │                    │
│  └─────────────────┘             └─────────────────┘                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Expected Flow (After Fix)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXPECTED STATE (FIXED)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  User Login → Auth Session → Fetch User's Assessments from Supabase     │
│                                                                          │
│  Supabase Auth                   Supabase Data                          │
│  ┌─────────────────┐             ┌─────────────────┐                    │
│  │ profiles (auth) │  ────────►  │ assessments     │                    │
│  │ - user_id ◄─────┼─────────────┼─► user_id       │                    │
│  │ - email         │   LINKED    │ - session_id    │                    │
│  │ - role          │             │ - profile_data  │                    │
│  └─────────────────┘             └─────────────────┘                    │
│                                         │                               │
│                                         ▼                               │
│                              ┌─────────────────┐                        │
│                              │ Load into       │                        │
│                              │ Zustand stores  │                        │
│                              │ on login        │                        │
│                              └─────────────────┘                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Gap Analysis

### 3.1 Authentication vs Assessment Data Link

| Aspect | Current State | Required State | Gap |
|--------|--------------|----------------|-----|
| User identification | `session_id` (random UUID) | `user_id` (auth.users.id) | **Critical** |
| Assessment ownership | Optional `email` field | Required `user_id` FK | **Critical** |
| Multi-device access | Not supported | Required for beta | **Critical** |
| Data on login | Not loaded | Auto-load from Supabase | **Critical** |

### 3.2 Persistence Feature Flags

| Flag | Current Value | Effect |
|------|---------------|--------|
| `ENABLE_SUPABASE_PERSISTENCE` | `false` (default) | Assessments NOT saved to DB |

**Location**: `/app/api/assessment/route.ts:13`

```typescript
const ENABLE_PERSISTENCE = process.env.ENABLE_SUPABASE_PERSISTENCE === 'true';
```

### 3.3 Missing Database Schema Updates

The `assessments` table needs these additions:

```sql
-- REQUIRED: Add user_id column to link to auth users
ALTER TABLE assessments ADD COLUMN user_id UUID REFERENCES auth.users(id);

-- REQUIRED: Index for user lookups
CREATE INDEX idx_assessments_user_id ON assessments(user_id);

-- RECOMMENDED: RLS policy for user-owned data
CREATE POLICY "Users can access own assessments" ON assessments
  FOR ALL
  USING (auth.uid() = user_id);
```

### 3.4 Missing Application Code

| Component | Current | Required | Priority |
|-----------|---------|----------|----------|
| Save assessment on completion | localStorage only | Supabase + localStorage | P0 |
| Load assessment on login | Not implemented | Fetch from Supabase | P0 |
| Link session to user | No link | Set `user_id` on save | P0 |
| Sync localStorage ↔ Supabase | Not implemented | Bi-directional sync | P1 |
| Offline support | Works (localStorage) | Sync when online | P2 |

---

## 4. Detailed Schema Analysis

### 4.1 assessments Table (Current)

```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY,
  session_id TEXT NOT NULL,      -- Random UUID, NOT linked to auth
  email TEXT,                     -- Optional, user-provided
  profile_data JSONB NOT NULL,    -- Full StudentProfile JSON
  game_plan_data JSONB,           -- Game plan if completed
  scores JSONB,                   -- {aptitude, passion, community, identity, overall}
  completeness INTEGER DEFAULT 0,
  tier TEXT,
  archetype TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

### 4.2 assessments Table (Required Changes)

```sql
-- Add user_id for auth linkage
ALTER TABLE assessments ADD COLUMN user_id UUID REFERENCES auth.users(id);

-- Make session_id unique per user (optional)
ALTER TABLE assessments ADD CONSTRAINT unique_user_session
  UNIQUE (user_id, session_id);

-- Index for fast user lookups
CREATE INDEX idx_assessments_user ON assessments(user_id);

-- RLS: Users can only access their own assessments
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "assessment_owner_access" ON assessments
  FOR ALL
  USING (auth.uid() = user_id OR user_id IS NULL);
```

### 4.3 profiles Table Conflict Resolution

**Problem**: Two tables named `profiles` with different purposes.

| profiles (auth) | profiles (v10 agent) |
|-----------------|---------------------|
| User authentication | Agent-derived data |
| Simple schema | Complex schema (CRI, narrative DNA) |
| Created by trigger | Created by agent system |
| Required for login | Optional enhancement |

**Recommendation**: Rename agent profiles table to `student_profiles` or `agent_profiles`.

---

## 5. Code Changes Required

### 5.1 Enable Supabase Persistence (Immediate)

```bash
# .env.local
ENABLE_SUPABASE_PERSISTENCE=true
```

### 5.2 Update Assessment API to Include user_id

```typescript
// app/api/assessment/route.ts

export async function POST(request: NextRequest) {
  // ... existing code ...

  // Get authenticated user
  const { data: { user } } = await supabase.auth.getUser();

  const insertData: AssessmentInsert = {
    session_id,
    user_id: user?.id || null,  // NEW: Link to auth user
    email: email || user?.email || null,
    // ... rest of fields
  };
}
```

### 5.3 Load Assessment on Login (New Hook)

```typescript
// lib/hooks/useLoadUserAssessment.ts

export function useLoadUserAssessment() {
  const { user, isAuthenticated } = useAuth();
  const loadProfile = useStudentStore((s) => s.loadProfile);
  const setResults = useResultsStore((s) => s.setResults);

  useEffect(() => {
    if (!isAuthenticated || !user) return;

    async function loadUserData() {
      const response = await fetch(`/api/assessment?user_id=${user.id}`);
      const { data } = await response.json();

      if (data?.profile_data) {
        loadProfile(data.profile_data);
      }
      if (data?.scores) {
        setResults({ scores: data.scores });
      }
    }

    loadUserData();
  }, [isAuthenticated, user]);
}
```

### 5.4 Save Assessment with User Link

```typescript
// lib/session/sessionManager.ts (or new file)

export async function saveAssessmentToSupabase(
  profile: StudentProfile,
  scores: AssessmentScores,
  userId: string
) {
  const response = await fetch('/api/assessment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: profile.session_id,
      user_id: userId,  // Link to authenticated user
      profile,
      scores,
      completeness: calculateCompleteness(profile),
    }),
  });

  return response.json();
}
```

---

## 6. Migration Plan

### Phase 1: Enable Persistence (Immediate)

1. Set `ENABLE_SUPABASE_PERSISTENCE=true` in `.env.local`
2. Add `user_id` column to `assessments` table
3. Update API to save `user_id` on authenticated requests
4. Test: Complete assessment while logged in → verify saved to Supabase

### Phase 2: Load on Login (This Week)

1. Create `useLoadUserAssessment` hook
2. Call hook in dashboard layout
3. Implement "merge" logic if localStorage has newer data
4. Test: Logout → Login → verify data loads from Supabase

### Phase 3: Full Sync (Future)

1. Implement bi-directional sync
2. Handle offline scenarios
3. Add conflict resolution
4. Coach access to student assessments

---

## 7. Verification Checklist

### Immediate Verification

- [ ] `ENABLE_SUPABASE_PERSISTENCE` is set to `true`
- [ ] `assessments` table has `user_id` column
- [ ] RLS policies allow user access to own data
- [ ] Assessment saves include `user_id` when authenticated

### Post-Fix Verification

- [ ] Complete assessment while logged in → data in Supabase
- [ ] Logout → Login → same data appears
- [ ] Different browser, same login → same data appears
- [ ] Coach can view student assessments (if applicable)

---

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data loss during migration | Low | High | Backup localStorage before sync |
| RLS policy blocks access | Medium | High | Test policies thoroughly |
| Merge conflicts | Medium | Medium | Latest-write-wins strategy |
| Performance impact | Low | Low | Index on user_id |

---

## Appendix A: Environment Variables

```bash
# Required for persistence
ENABLE_SUPABASE_PERSISTENCE=true

# Supabase connection (already configured)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx  # For admin operations
```

## Appendix B: Database Types Update

```typescript
// lib/supabase/database.types.ts - Add user_id

interface Assessment {
  Row: {
    id: string;
    session_id: string;
    user_id: string | null;  // NEW
    email: string | null;
    profile_data: Json;
    // ... rest
  };
  Insert: {
    user_id?: string | null;  // NEW
    // ... rest
  };
  Update: {
    user_id?: string | null;  // NEW
    // ... rest
  };
}
```

## Appendix C: Zustand Store Data Sizes

| Store | Typical Size | Max Observed |
|-------|--------------|--------------|
| StudentProfile | ~15KB | ~25KB |
| SessionStore | ~5KB | ~10KB |
| ResultsStore | ~8KB | ~15KB |
| Frame3Store | ~3KB | ~5KB |
| TwinStore | ~4KB | ~8KB |
| **Total** | **~35KB** | **~63KB** |

localStorage limit: ~5MB per origin. Current usage is well within limits.

---

## Appendix D: Related Files

| File | Purpose |
|------|---------|
| `lib/store/useStudentStore.ts` | Main profile store |
| `lib/store/useSessionStore.ts` | Session state |
| `lib/store/useResultsStore.ts` | Assessment results |
| `app/api/assessment/route.ts` | Persistence API |
| `lib/supabase/database.types.ts` | TypeScript schema |
| `supabase/migrations/*.sql` | Database migrations |
| `lib/auth/AuthProvider.tsx` | Authentication context |

---

**Report End**

*This analysis should be reviewed with the development team before implementing changes. Priority should be given to Phase 1 (Enable Persistence) to prevent further data loss.*
