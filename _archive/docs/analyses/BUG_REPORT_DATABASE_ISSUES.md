# IvyQuest Database Bug Report

**Date:** January 12, 2026
**Version:** v13.3 Frontend / v13.2 Backend
**Severity:** Critical - Data Loss
**Status:** Root Cause Identified, Pending Fix

---

## Executive Summary

The Multi-Agent Dashboard displays placeholder data (all zeros) because assessment data never persists to Supabase. The frontend correctly calls `saveAssessment()`, but a **SQL trigger bug** in `migration_015` causes the entire INSERT operation to silently rollback.

---

## Issue Overview

### Symptoms
1. Multi-Agent Dashboard shows "0 matches", "0 activities", "0 opportunities"
2. `assessments` table has 0 rows in Supabase
3. `profiles` table has 0 rows (agents read from here)
4. Backend agents return placeholder data due to missing profiles
5. No error messages appear in frontend console during assessment save

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CURRENT BROKEN FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Frontend   │───▶│  Supabase    │───▶│   Trigger    │                   │
│  │ Frame6 Save  │    │  assessments │    │  015_extract │                   │
│  └──────────────┘    │   INSERT     │    │   _awards    │                   │
│         │            └──────────────┘    └──────────────┘                   │
│         │                   │                   │                            │
│         │                   │                   ▼                            │
│         │                   │            ┌──────────────┐                   │
│         │                   │            │   SQL BUG    │                   │
│         │                   │            │   Variable   │                   │
│         │                   │            │   Shadows    │◀─── FAILURE POINT │
│         │                   │            │   Function   │                   │
│         │                   │            └──────────────┘                   │
│         │                   │                   │                            │
│         │                   ▼                   ▼                            │
│         │            ┌──────────────────────────────────┐                   │
│         │            │      ENTIRE INSERT ROLLED BACK   │                   │
│         │            │      (assessments = 0 rows)      │                   │
│         │            └──────────────────────────────────┘                   │
│         │                                                                   │
│         │            ┌──────────────┐    ┌──────────────┐                   │
│         │            │   profiles   │    │   Backend    │                   │
│         │            │   (0 rows)   │◀───│   Agents     │                   │
│         │            │ Never synced │    │   Query      │                   │
│         │            └──────────────┘    └──────────────┘                   │
│         │                                       │                            │
│         │                                       ▼                            │
│         │                              ┌──────────────┐                      │
│         └─────────────────────────────▶│  Dashboard   │                      │
│                                        │ Shows 0 data │                      │
│                                        └──────────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Bug #1: SQL Variable Name Shadowing (CRITICAL)

### Location
**File:** `/supabase/migrations/015_data_extraction_triggers.sql`
**Lines:** 122, 130, 132, 164, 166

### Problem
The PostgreSQL function `extract_awards_from_assessment()` declares a local variable `award_code` that shadows the loop variable with the same name. When the WHERE clause references `extract_awards_from_assessment.award_code`, PostgreSQL interprets the function name as a table reference, causing a runtime error.

### Affected Code

```sql
-- Line 122: Variable declaration
DECLARE
  award_code TEXT;  -- <-- THIS IS THE PROBLEM

-- Line 130-132: Loop and query
FOR award_code IN SELECT jsonb_array_elements_text(profile->'aptitude'->'academic_awards')
LOOP
  SELECT * INTO award_info FROM award_mappings
  WHERE award_mappings.award_code = extract_awards_from_assessment.award_code;
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                    PostgreSQL thinks this is a TABLE reference
                                    because award_code variable shadows it
```

### PostgreSQL Behavior
When `extract_awards_from_assessment.award_code` is evaluated:
1. PostgreSQL first looks for a table/view named `extract_awards_from_assessment`
2. If not found, it looks for a function with that name
3. But since `award_code` is declared as a local variable, the qualified reference fails
4. This throws an error inside the trigger
5. **The entire INSERT transaction rolls back silently**

### Why It's Silent
Supabase client doesn't surface trigger errors to the frontend. The `upsert()` call returns success, but the transaction is rolled back at the database level.

---

## Bug #2: Profile Sync Only Updates, Never Creates

### Location
**File:** `/supabase/migrations/003_profiles_v10.sql`
**Lines:** 93-131

### Problem
The function `sync_profile_from_assessment()` is designed to sync data from `assessments` to `profiles`, but:
1. It's a **callable function**, not an automatic trigger
2. It only **UPDATEs** existing profiles with matching `assessment_id`
3. For new assessments, there's no profile row to update → no sync happens

### Code Analysis

```sql
-- Line 107: Check if profile exists
SELECT id INTO v_profile_id FROM profiles WHERE assessment_id = p_assessment_id;

IF v_profile_id IS NOT NULL THEN
  -- UPDATE existing profile (lines 110-116)
  UPDATE profiles SET ...
ELSE
  -- CREATE new profile (lines 118-126)
  INSERT INTO profiles (...) VALUES (...) RETURNING id INTO v_profile_id;
END IF;
```

### The Problem
**This function is never called automatically.** There's no trigger that invokes `sync_profile_from_assessment()` after an assessment INSERT.

Even if called manually, the function only syncs minimal data (name, email, grade), not the full `profile_data`, `scores`, or `archetype`.

---

## Bug #3: Missing Automatic Trigger for Profile Sync

### Expected Behavior
When a completed assessment is inserted:
1. `assessments` table receives the row
2. A trigger should call `sync_profile_from_assessment()`
3. `profiles` table should get a corresponding row
4. Backend agents query `profiles` and find data

### Actual Behavior
1. Assessment INSERT is attempted
2. `extract_awards_from_assessment()` trigger fires and FAILS
3. Entire INSERT rolls back
4. Even if INSERT succeeded, there's no trigger to create a profile

---

## Bug #4: Same Shadowing Bug in School Extraction

### Location
**File:** `/supabase/migrations/015_data_extraction_triggers.sql`
**Lines:** 254, 269, 271

### Same Pattern

```sql
DECLARE
  school_id TEXT;  -- <-- Local variable shadows loop variable

FOR school_id IN SELECT jsonb_array_elements_text(profile->'target_schools')
LOOP
  SELECT * INTO school_info FROM school_metadata
  WHERE school_metadata.school_id = extract_target_schools_from_assessment.school_id;
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                    Same shadowing bug
```

---

## Data Architecture Gap

### Current State

| Table | Purpose | Row Count | Problem |
|-------|---------|-----------|---------|
| `assessments` | Frontend saves here | 0 | Trigger rollback |
| `profiles` | Backend reads here | 0 | Never synced |
| `student_items` | Award/school data | 0 | Dependent on assessments |

### Required State

| Table | Purpose | Expected Behavior |
|-------|---------|-------------------|
| `assessments` | Raw assessment data | INSERT should succeed |
| `profiles` | Agent-optimized view | Auto-created on assessment completion |
| `student_items` | Universal ledger | Populated by working triggers |

---

## Fix Options

### Option A: Quick Fix (Disable Broken Trigger)

**Pros:** Immediate fix, low risk
**Cons:** Loses automatic award/school extraction

```sql
-- Run in Supabase SQL Editor
DROP TRIGGER IF EXISTS extract_awards_on_assessment ON assessments;
DROP TRIGGER IF EXISTS extract_schools_on_assessment ON assessments;
```

### Option B: Comprehensive Migration Fix

**Pros:** Complete fix, proper architecture
**Cons:** Requires new migration, testing

```sql
-- 1. Fix variable shadowing in extract_awards_from_assessment()
CREATE OR REPLACE FUNCTION extract_awards_from_assessment()
RETURNS TRIGGER AS $$
DECLARE
  v_award_code TEXT;  -- Renamed with v_ prefix
  award_info RECORD;
  profile JSONB;
BEGIN
  profile := NEW.profile_data;

  IF profile->'aptitude'->'academic_awards' IS NOT NULL THEN
    FOR v_award_code IN SELECT jsonb_array_elements_text(profile->'aptitude'->'academic_awards')
    LOOP
      SELECT * INTO award_info FROM award_mappings WHERE award_code = v_award_code;
      -- Rest of logic using v_award_code
    END LOOP;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Fix variable shadowing in extract_target_schools_from_assessment()
-- (Similar pattern with v_school_id)

-- 3. Create automatic profile sync trigger
CREATE OR REPLACE FUNCTION auto_sync_profile_from_assessment()
RETURNS TRIGGER AS $$
DECLARE
  v_profile_id UUID;
BEGIN
  -- Check if profile exists for this user
  SELECT id INTO v_profile_id FROM profiles
  WHERE user_id = NEW.user_id;

  IF v_profile_id IS NOT NULL THEN
    -- Update existing profile
    UPDATE profiles SET
      assessment_id = NEW.id,
      name = NEW.profile_data->>'name',
      email = NEW.email,
      grade = (NEW.profile_data->>'grade')::INTEGER,
      archetype_id = (SELECT id FROM archetypes WHERE code = NEW.archetype),
      updated_at = NOW()
    WHERE id = v_profile_id;
  ELSE
    -- Create new profile
    INSERT INTO profiles (
      user_id, assessment_id, name, email, grade
    ) VALUES (
      NEW.user_id,
      NEW.id,
      NEW.profile_data->>'name',
      NEW.email,
      (NEW.profile_data->>'grade')::INTEGER
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. Create the trigger
DROP TRIGGER IF EXISTS sync_profile_on_assessment ON assessments;
CREATE TRIGGER sync_profile_on_assessment
  AFTER INSERT OR UPDATE ON assessments
  FOR EACH ROW
  WHEN (NEW.completed_at IS NOT NULL)
  EXECUTE FUNCTION auto_sync_profile_from_assessment();
```

---

## Impact Assessment

### Affected Features
- Multi-Agent Dashboard (6 cards show zeros)
- Award Agent matching
- Opportunity Agent alerts
- GamePlan Agent activities
- Narrative Synthesis Agent
- All backend agent queries

### Data Loss
- All assessments completed since v13.2 deployment have been lost
- Users will need to re-complete assessments after fix

### User Experience
- Users see "Complete Your Assessment" or zeros after completing assessment
- No error messages to indicate problem
- Confusion about platform functionality

---

## Recommended Fix Sequence

1. **Immediate:** Disable broken triggers (Option A)
2. **Short-term:** Apply Option B migration
3. **Verify:** Test full assessment → agent dashboard flow
4. **Backfill:** Re-run any test assessments

---

## Verification Steps Post-Fix

```sql
-- 1. Verify assessments table accepts INSERTs
SELECT COUNT(*) FROM assessments;

-- 2. Verify profiles sync
SELECT COUNT(*) FROM profiles;

-- 3. Verify student_items extraction
SELECT item_type, COUNT(*) FROM student_items GROUP BY item_type;

-- 4. Test from frontend
-- Complete assessment flow → check all tables
```

---

## Files Referenced

| File | Lines | Issue |
|------|-------|-------|
| `supabase/migrations/015_data_extraction_triggers.sql` | 122, 130-132, 164-166, 254, 269-271 | Variable shadowing bug |
| `supabase/migrations/003_profiles_v10.sql` | 93-131 | No automatic sync trigger |
| `lib/services/assessmentService.ts` | 118-124 | Works correctly, not the problem |
| `agents/agents/*.py` | Various | Now handle missing profiles gracefully |

---

## Appendix: Full Error Trace (Reconstructed)

```
1. Frontend: Frame6PowerUps calls assessmentService.saveAssessment()
2. AssessmentService: Calls supabase.from('assessments').upsert(...)
3. Supabase: Attempts INSERT into assessments table
4. PostgreSQL: Fires AFTER INSERT trigger extract_awards_on_assessment
5. Trigger: Enters extract_awards_from_assessment() function
6. Function: FOR award_code IN SELECT... loop begins
7. Function: SELECT * FROM award_mappings WHERE award_mappings.award_code = extract_awards_from_assessment.award_code
8. PostgreSQL: ERROR - cannot resolve extract_awards_from_assessment.award_code (variable shadowing)
9. PostgreSQL: ROLLBACK entire transaction
10. Supabase: Returns to client (error may be swallowed)
11. Frontend: Receives apparent success (no error surfaced)
12. assessments table: 0 rows (INSERT was rolled back)
13. profiles table: 0 rows (never synced)
14. Backend agents: Query profiles, find nothing, return placeholders
15. Dashboard: Shows all zeros
```

---

**Report Generated:** January 12, 2026
**Next Action:** Apply database fix migration
