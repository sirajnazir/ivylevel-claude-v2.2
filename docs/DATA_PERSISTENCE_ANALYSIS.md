# IvyQuest Data Persistence: Critical Analysis & Implementation Guide

## Executive Summary

**The original backend proposal had a fundamental misdiagnosis.** The schema already supports all the data claimed to be missing - the issue is that Frame 4 isn't computing/populating the values correctly.

| Original Claim | Reality |
|----------------|---------|
| "Frame 4 data not persisted" | Schema exists, values are defaults (0.5) |
| "Need new tables for ECs/Awards" | `student_items` already handles this |
| "Schema doesn't support psychometrics" | `assessment_intelligence.psychometrics` exists |

---

## Evidence: What's Actually in the Database

From the Supabase data dump, `profile_data` contains:

```json
{
  "operating": {
    "strengths": ["competitive", "hands-on"],
    "availableHoursPerWeek": 15,
    "homeworkHoursPerDay": 3.5,
    "firstGeneration": false
  },
  "demographics": {
    "first_gen": false,
    "ethnicity": "PREFER_NOT_SAY"
  },
  "assessment_intelligence": {
    "psychometrics": {
      "openness": 0.5,
      "conscientiousness": 0.5,
      "coachability": "MEDIUM",
      "coachability_score": 0.5
    },
    "time_management": {
      "burnout_risk": "MEDIUM",
      "reclaimable_hours_weekly": 20
    },
    "hidden_capabilities": {
      "hobby_passions": [],
      "unconventional_interests": [],
      "hidden_technical_projects": []
    }
  }
}
```

### The Real Issue

All psychometric values are **0.5** (the default midpoint). All hidden_capabilities arrays are **empty**.

**This means the frontend is NOT computing these values from Frame 4 responses** - it's just passing default values to the database.

---

## Correct Diagnosis

### What's Actually Missing

| Field | In Schema | In Database | Issue |
|-------|-----------|-------------|-------|
| `psychometrics.openness` | Yes | 0.5 (default) | Not computed from scenario responses |
| `psychometrics.conscientiousness` | Yes | 0.5 (default) | Not computed from scenario responses |
| `psychometrics.extraversion` | Yes | 0.5 (default) | Not computed from scenario responses |
| `psychometrics.coachability_score` | Yes | 0.5 (default) | Not computed from scenario responses |
| `hidden_capabilities.hobby_passions` | Yes | [] (empty) | Not populated from Frame 4 UI |
| `hidden_capabilities.unconventional_interests` | Yes | [] (empty) | Not populated from Frame 4 UI |
| `operating.peak_productivity` | No | Missing | Field not in schema (minor) |
| `operating.operating_style` | No | Missing | Field not in schema (minor) |
| `operating.risk_tolerance` | No | Missing | Field not in schema (minor) |

### Root Causes

1. **Frame 4 scenario responses** are captured but the **computation logic** to derive psychometric scores isn't running

2. **Hidden capabilities UI** exists but the data isn't being **synced to StudentStore**

3. **Some computed fields** (`operating_style`, `risk_tolerance`) are missing from the schema (minor issue)

---

## Why NOT to Create Separate Tables

The original proposal suggested creating:
- `student_extracurriculars`
- `student_awards`
- `student_target_schools`

**This violates the Universal Ledger pattern** from the legacy IvyLevel schema that tracked a real student (Huda) through 3+ years of coaching.

### The Universal Ledger Pattern (student_items)

```sql
-- IvyQuest: One table for EVERYTHING
student_items (
  item_type: 'award' | 'extracurricular' | 'program' | 'application' | 'goal' | ...
  tier1_state: 'planned' | 'in_progress' | 'submitted' | 'outcome' | 'archived'
)
```

### Benefits of Universal Ledger

| Benefit | Description |
|---------|-------------|
| **Single source of truth** | All student items in one table |
| **Consistent state machine** | Same lifecycle for all item types |
| **Simple queries** | `WHERE item_type = 'award'` |
| **Built-in views** | `v_awards`, `v_extracurriculars` already exist |
| **Timeline integration** | All items can create timeline events |
| **Flexible schema** | `extended_data` JSONB for type-specific fields |

### What the Original Proposal Got Wrong

| Proposal | Reality |
|----------|---------|
| Create `student_extracurriculars` | Already have `student_items WHERE item_type = 'extracurricular'` |
| Create `student_awards` | Already have `student_items WHERE item_type = 'award'` |
| Create `student_target_schools` | Already have `student_items WHERE item_type = 'application'` |
| 3 new tables = 3x the code | Universal ledger = 1 table, 1 API |

---

## Correct Implementation Plan

### Phase 1: Frontend Fix (CRITICAL)

Fix Frame 4 to properly compute and populate psychometrics:

#### 1.1 Psychometric Computation

See `lib/types/frame4.ts` for the computation functions:

```typescript
import { computePsychometrics, processFrame4Completion } from '@/lib/types/frame4';

// Frame 4 should call this before proceeding to Frame 5
const result = processFrame4Completion(
  scenarioResponses,    // User's choices
  hiddenCapabilities,   // Collected from UI
  operatingInputs       // Available hours, etc.
);

// Sync to StudentStore
useStudentStore.setState({
  profileData: {
    ...profileData,
    operating: result.operating,
    assessment_intelligence: result.assessment_intelligence
  }
});
```

#### 1.2 Files to Modify

| File | Change |
|------|--------|
| `components/frames/Frame4Context.tsx` | Add psychometric computation |
| `lib/store/useStudentStore.ts` | Ensure Frame4 data syncs to profile |
| `lib/hooks/useUserData.ts` | Verify saveUserData includes all fields |

### Phase 2: Run Data Extraction Triggers

Run the migration to set up automatic extraction:

```bash
# In Supabase SQL Editor
\i supabase/migrations/015_data_extraction_triggers.sql
```

This migration:
1. Adds needed columns to `student_items` (recognition_level, prestige_tier, etc.)
2. Creates `award_mappings` lookup table
3. Creates `school_metadata` lookup table
4. Creates triggers for automatic extraction on assessment/game plan completion
5. Creates enhanced views for agents
6. Backfills existing data

### Phase 3: Verification

Query the new views to verify data:

```sql
-- Check student profile
SELECT * FROM v_agent_student_profile WHERE email = 'huda@ivylevel.com';

-- Check awards
SELECT * FROM v_student_awards_detailed WHERE user_id = '...';

-- Check target schools
SELECT * FROM v_student_target_schools WHERE user_id = '...';

-- Check goals
SELECT * FROM v_student_goals WHERE user_id = '...';
```

---

## Agent Data Requirements

### Game Plan Agent

| Data Needed | Source | Location |
|-------------|--------|----------|
| Available hours | `v_agent_student_profile` | `profile_data.operating.availableHoursPerWeek` |
| Spike category | `v_agent_student_profile` | `profile_data.passion.spike_category` |
| Current grade | `v_agent_student_profile` | `grade` |
| Target schools | `v_student_target_schools` | Full view |
| Current awards | `v_student_awards_detailed` | Full view |
| Burnout risk | `v_agent_student_profile` | `intelligence.time_management.burnout_risk` |
| Coachability | `v_agent_student_profile` | `intelligence.psychometrics.coachability` |

### Awards Agent

| Data Needed | Source | Location |
|-------------|--------|----------|
| Current awards | `v_student_awards_detailed` | Full view |
| Academic stats | `v_agent_student_profile` | `aptitude` |
| Spike category | `v_agent_student_profile` | `profile_data.passion.spike_category` |
| Research level | `v_agent_student_profile` | `profile_data.passion.research_level` |
| Grade | `v_agent_student_profile` | `grade` |

### Opportunities/EC Agent

| Data Needed | Source | Location |
|-------------|--------|----------|
| Grade | `v_agent_student_profile` | `grade` |
| Spike | `v_agent_student_profile` | `profile_data.passion.spike_category` |
| Available hours | `v_agent_student_profile` | `operating.availableHoursPerWeek` |
| Region | `v_agent_student_profile` | `high_school.region` |
| Demographics | `v_agent_student_profile` | `demographics` |
| Current goals | `v_student_goals` | Full view |

---

## Implementation Checklist

### Phase 1: Frontend Fix (Do First)

- [ ] Frame 4: Add psychometric computation from scenario responses
- [ ] Frame 4: Populate hidden_capabilities from UI inputs
- [ ] Frame 4: Sync all data to StudentStore (not just Frame3Store)
- [ ] useUserData: Verify saveUserData includes operating and assessment_intelligence
- [ ] Test: Complete assessment, verify psychometrics are NOT 0.5

### Phase 2: Database Migration

- [ ] Run migration `015_data_extraction_triggers.sql`
- [ ] Verify `award_mappings` table populated
- [ ] Verify `school_metadata` table populated
- [ ] Test: Complete assessment, verify `student_items` populated

### Phase 3: Verification

- [ ] Query `v_agent_student_profile` - should show complete data
- [ ] Query `v_student_awards_detailed` - should show extracted awards
- [ ] Query `v_student_target_schools` - should show target schools with probabilities
- [ ] Query `v_student_goals` - should show extracted goals

### Phase 4: Agent Integration (Post-Beta)

- [ ] Update Game Plan agent to use `v_agent_student_profile`
- [ ] Update Awards agent to use `v_student_awards_detailed`
- [ ] Update EC agent to use relevant views
- [ ] Test end-to-end with real assessment -> game plan flow

---

## Summary: What to Actually Do

### DON'T DO (Original Proposal Recommendations)

1. Don't create `student_extracurriculars` table
2. Don't create `student_awards` table
3. Don't create `student_target_schools` table
4. Don't assume the schema is broken

### DO (Correct Approach)

1. **Fix Frame 4 frontend** to compute and populate psychometric values
2. **Fix Frame 4 frontend** to capture and sync hidden capabilities
3. **Run extraction triggers** to populate student_items from existing data
4. **Use existing views** (`v_awards`, `v_extracurriculars`, etc.) for agents
5. **Test with real assessment** to verify non-default values are stored

---

## Files Provided

| File | Purpose |
|------|---------|
| `supabase/migrations/015_data_extraction_triggers.sql` | Creates extraction logic + backfills data |
| `lib/types/frame4.ts` | TypeScript types + computation functions |
| `docs/DATA_PERSISTENCE_ANALYSIS.md` | This analysis document |

---

## Agent Data Access Examples

```typescript
// Game Plan Agent - Single query for complete profile
const { data } = await supabase
  .from('v_agent_student_profile')
  .select('*')
  .eq('user_id', userId)
  .single();

// Access psychometrics (will have REAL values after frontend fix)
const coachability = data.intelligence.psychometrics.coachability;
const burnoutRisk = data.intelligence.time_management.burnout_risk;
const availableHours = data.operating.availableHoursPerWeek;

// Awards Agent
const { data: awards } = await supabase
  .from('v_student_awards_detailed')
  .select('*')
  .eq('user_id', userId);

// Target Schools
const { data: schools } = await supabase
  .from('v_student_target_schools')
  .select('*')
  .eq('user_id', userId);

// Goals
const { data: goals } = await supabase
  .from('v_student_goals')
  .select('*')
  .eq('user_id', userId);
```
