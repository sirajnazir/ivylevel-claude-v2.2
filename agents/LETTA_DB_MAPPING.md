# LETTA DATABASE INTEGRATION AUDIT

**Generated:** 2026-01-18
**Audit Type:** Ground Truth Analysis (Live Database + Codebase Inspection)

---

## Executive Summary

Critical mismatches found between Letta integration code and actual database schema:

| Category | Count | Severity |
|----------|-------|----------|
| Missing Tables | 6 | P0 (Critical) |
| Table Name Mismatches | 1 | P0 (Critical) |
| Missing Columns | 4 | P1 (High) |
| Column Name Mismatches | 3 | P1 (High) |
| Type/Structure Mismatches | 2 | P2 (Medium) |

---

## Phase 1: Ground Truth Discovery

### 1.1 Actual Database Tables

**Tables that EXIST in Supabase:**
```
✓ profiles                 (49 columns, has data)
✓ game_plans               (22 columns, has data)
✓ assessments              (18 columns, has data)
✓ opportunities            (35 columns, has data)
✓ activities               (empty)
✓ proactive_notifications  (empty)
✓ letta_agent_registry     (8 columns, has data)
✓ letta_memory_snapshots   (empty)
✓ letta_approval_queue     (empty)
✓ letta_transition_log     (empty)
```

**Tables that DO NOT EXIST (but Letta code queries):**
```
✗ assessment_narratives    - Referenced in sync.py:135
✗ student_intelligence     - Referenced in sync.py:182
✗ execution_logs           - Referenced in sync.py:200
✗ gameplans               - Should be "game_plans" (naming mismatch)
✗ tasks                    - Referenced in sync.py:249, database.py:230
✗ outcome_driven_goals     - Referenced in sync.py:275, database.py:407
```

### 1.2 Profiles Table - Actual Schema (49 columns)

```sql
-- Actual columns with data types (extracted from live database)
id                          UUID PRIMARY KEY
email                       TEXT
role                        TEXT
first_name                  TEXT
last_name                   TEXT
grade                       INTEGER
graduation_year             INTEGER (NULL)
high_school                 TEXT
target_major                TEXT
organization                TEXT (NULL)
gpa                         FLOAT
sat_score                   INTEGER
act_score                   INTEGER (NULL)
archetype                   TEXT
archetype_confidence        INTEGER (NULL)
ivy_score                   INTEGER
cri_score                   INTEGER (NULL)
eds_score                   INTEGER (NULL)
spike                       TEXT (NULL)
spike_score                 INTEGER (NULL)
spike_confidence            INTEGER
pillars                     JSONB (list)
brand_statement             TEXT (NULL)
narrative_brand_statement   TEXT
narrative_dna               TEXT
narrative_themes            JSONB (list)
narrative_first_principle   TEXT
narrative_confidence        FLOAT
narrative_updated_at        TIMESTAMPTZ
identity_synthesis          JSONB
target_schools              JSONB (NULL)
intended_major              TEXT
school_type                 TEXT (NULL)
school_name                 TEXT (NULL)
preferences                 JSONB
notification_preferences    JSONB
preferred_contact_time      TIME
onboarding_completed        BOOLEAN
onboarding_step             INTEGER
is_active                   BOOLEAN
is_verified                 BOOLEAN
assessment_completed_at     TIMESTAMPTZ
last_activity_at            TIMESTAMPTZ
last_login_at               TIMESTAMPTZ (NULL)
last_synthesized_at         TIMESTAMPTZ (NULL)
last_synthesized_by         TEXT (NULL)
avatar_url                  TEXT (NULL)
created_at                  TIMESTAMPTZ
updated_at                  TIMESTAMPTZ
```

### 1.3 Game_Plans Table - Actual Schema (22 columns)

```sql
id                      UUID PRIMARY KEY
user_id                 UUID
profile_id              UUID (NULL - NOTE: often NULL!)
assessment_id           UUID (NULL)
plan_data               JSONB
plan_status             TEXT (not "status")
plan_version            INTEGER
current_phase           TEXT (not "phase")
current_week            INTEGER
completion_percentage   INTEGER
generation_version      TEXT
ec_generation           JSONB (NULL)
programs_data           JSONB (NULL)
awards_data             JSONB (NULL)
target_schools          JSONB (NULL)
target_tier             TEXT (NULL)
target_archetype        TEXT (NULL)
react_metadata          JSONB (NULL)
activated_at            TIMESTAMPTZ (NULL)
completed_at            TIMESTAMPTZ (NULL)
created_at              TIMESTAMPTZ
updated_at              TIMESTAMPTZ
```

---

## Phase 2: Gap Analysis

### 2.1 Table-Level Mapping

| Letta Code Queries | Actual Table | Status | Fix Required |
|-------------------|--------------|--------|--------------|
| `profiles` | `profiles` | ✓ Match | None |
| `assessment_narratives` | - | ✗ Missing | Data exists in `profiles.narrative_*` columns |
| `student_intelligence` | - | ✗ Missing | Need to create or map to existing |
| `execution_logs` | - | ✗ Missing | Need to create |
| `gameplans` | `game_plans` | ✗ Wrong Name | Change to `game_plans` |
| `tasks` | - | ✗ Missing | Need to create |
| `outcome_driven_goals` | - | ✗ Missing | Need to create or map |
| `proactive_notifications` | `proactive_notifications` | ✓ Match | None |

### 2.2 Profiles Table - Field Mapping

| Letta Expects | Type Expected | Actual Column | Actual Type | Match | Fix |
|---------------|---------------|---------------|-------------|-------|-----|
| `name` | string | - | - | ✗ | Use `f"{first_name} {last_name}"` |
| `grade` | int | `grade` | INTEGER | ✓ | None |
| `school_type` | string | `school_type` | TEXT (NULL) | ✓ | Handle NULL |
| `gpa` | float | `gpa` | FLOAT | ✓ | None |
| `test_scores` | dict | - | - | ✗ | Build from `sat_score`, `act_score` |
| `course_rigor` | string | - | - | ✗ | Not tracked - use default |
| `target_schools` | list | `target_schools` | JSONB (NULL) | ✓ | Handle NULL |
| `intended_major` | string | `intended_major` | TEXT | ✓ | None |
| `assessment_data` | dict | - | - | ✗ | Build from profile columns |
| `archetype` | string | `archetype` | TEXT | ✓ | None |
| `cri_score` | int | `cri_score` | INTEGER (NULL) | ✓ | Handle NULL |
| `narrative_dna` | string | `narrative_dna` | TEXT | ✓ | None |

### 2.3 Game_Plans Table - Field Mapping

| Letta Expects | Actual Column | Match | Fix |
|---------------|---------------|-------|-----|
| `status` | `plan_status` | ✗ | Change query to `plan_status` |
| `phase` | `current_phase` | ✗ | Change query to `current_phase` |
| `strategic_focus` | - | ✗ | Extract from `plan_data` JSON |
| `milestones` | - | ✗ | Extract from `plan_data` JSON |
| `profile_id` | `profile_id` | ✓ | Note: Often NULL, may need to use `user_id` |

### 2.4 Tool-to-Table Audit

| Tool Name | Tables Queried | Status | Issues |
|-----------|----------------|--------|--------|
| `get_student_profile` | `profiles`, `assessment_narratives`, `student_intelligence` | ⚠️ Partial | 2 tables don't exist |
| `get_active_gameplan` | `gameplans`, `tasks` | ✗ Broken | Wrong table name, tasks missing |
| `get_recent_interactions` | `proactive_notifications`, `execution_logs` | ⚠️ Partial | execution_logs doesn't exist |
| `get_goal_progress` | `outcome_driven_goals` | ✗ Broken | Table doesn't exist |

---

## Phase 3: Prioritized Fix List

### P0 - Critical (Breaks Core Functionality)

| # | File | Line | Current Code | Should Be | Why |
|---|------|------|--------------|-----------|-----|
| 1 | `letta/memory/sync.py` | 232 | `supabase.table("gameplans")` | `supabase.table("game_plans")` | Table name mismatch |
| 2 | `letta/tools/database.py` | 208 | `supabase.table("gameplans")` | `supabase.table("game_plans")` | Table name mismatch |
| 3 | `letta/memory/sync.py` | 235 | `.eq("status", "active")` | `.eq("plan_status", "active")` | Column name mismatch |
| 4 | `letta/tools/database.py` | 211 | `.eq("status", "active")` | `.eq("plan_status", "active")` | Column name mismatch |

### P1 - High (Data Not Loading)

| # | File | Line | Current Code | Should Be | Why |
|---|------|------|--------------|-----------|-----|
| 5 | `letta/memory/blocks.py` | 68 | `profile.get('name', 'Unknown')` | `f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or 'Unknown'` | Column doesn't exist |
| 6 | `letta/memory/blocks.py` | 74 | `profile.get('test_scores', {})` | Build dict from `sat_score`, `act_score` | Column doesn't exist |
| 7 | `letta/memory/sync.py` | 148 | `profile.get("assessment_data", profile)` | Just use `profile` directly | Column doesn't exist |
| 8 | `letta/tools/database.py` | 117 | `profile.get("assessment_data", {})` | Build from profile columns | Column doesn't exist |

### P2 - Medium (Missing Tables - Needs Graceful Handling)

| # | File | Table Missing | Current Behavior | Recommendation |
|---|------|---------------|------------------|----------------|
| 9 | `sync.py:135` | `assessment_narratives` | Error silently caught | Use `profiles.narrative_*` columns instead |
| 10 | `sync.py:182` | `student_intelligence` | Error silently caught | Skip or create table |
| 11 | `sync.py:200` | `execution_logs` | Error silently caught | Skip or create table |
| 12 | `sync.py:249` | `tasks` | Error silently caught | Skip or create table |
| 13 | `sync.py:275` | `outcome_driven_goals` | Error silently caught | Skip or create table |

---

## Phase 4: Recommended Code Fixes

### Fix 1: Update sync.py - Student Profile Builder

```python
# letta/memory/sync.py - _fetch_student_profile method

async def _fetch_student_profile(self, profile_id: str) -> Dict[str, Any]:
    """Fetch student profile data from profiles table."""
    try:
        profile_result = self.supabase.table("profiles") \
            .select("*") \
            .eq("id", profile_id) \
            .single() \
            .execute()

        profile = profile_result.data or {}

        # Build name from first_name and last_name
        name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Unknown"

        # Build test_scores from individual columns
        test_scores = {}
        if profile.get('sat_score'):
            test_scores['sat'] = profile['sat_score']
        if profile.get('act_score'):
            test_scores['act'] = profile['act_score']

        # Build assessment-like structure from profile columns
        profile_data = {
            "name": name,
            "grade": profile.get('grade'),
            "school_type": profile.get('school_type'),
            "gpa": profile.get('gpa'),
            "test_scores": test_scores,
            "target_schools": profile.get('target_schools') or [],
            "intended_major": profile.get('intended_major') or profile.get('target_major'),
        }

        # Assessment data from profile columns (no separate table)
        assessment_data = {
            "archetype": profile.get('archetype'),
            "cri_score": profile.get('cri_score'),
            "narrative_dna": profile.get('narrative_dna'),
            "narrative_brand_statement": profile.get('narrative_brand_statement'),
            "strengths": profile.get('narrative_themes') or [],
        }

        return {
            "profile": profile_data,
            "assessment": assessment_data,
        }

    except Exception as e:
        logger.error("fetch_student_profile_error", profile_id=profile_id, error=str(e))
        return {}
```

### Fix 2: Update sync.py - Gameplan Queries

```python
# letta/memory/sync.py - _fetch_active_gameplan method

async def _fetch_active_gameplan(self, profile_id: str) -> Dict[str, Any]:
    """Fetch active gameplan and tasks."""
    try:
        gameplan = {}
        try:
            # FIX: Use correct table name and column names
            result = self.supabase.table("game_plans") \
                .select("*") \
                .eq("profile_id", profile_id) \
                .eq("plan_status", "active") \  # FIX: was "status"
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()

            if result.data:
                gp = result.data[0]
                # Extract fields with correct column names
                gameplan = {
                    "id": gp.get("id"),
                    "phase": gp.get("current_phase"),  # FIX: was "phase"
                    "status": gp.get("plan_status"),   # FIX: was "status"
                    "created_at": gp.get("created_at"),
                    "strategic_focus": gp.get("plan_data", {}).get("strategic_focus", ""),
                    "milestones": gp.get("plan_data", {}).get("milestones", []),
                }
        except Exception:
            pass

        # NOTE: tasks table doesn't exist - return empty
        tasks = []

        return {
            "gameplan": gameplan,
            "tasks": tasks,
        }

    except Exception as e:
        logger.error("fetch_active_gameplan_error", profile_id=profile_id, error=str(e))
        return {}
```

### Fix 3: Update blocks.py - Student Profile Block

```python
# letta/memory/blocks.py - StudentProfileBlock.build method

def build(self, data: Dict[str, Any]) -> str:
    """Build student profile block from profile data."""
    profile = data.get("profile", {})
    assessment = data.get("assessment", {})

    # FIX: Handle name construction
    name = profile.get('name', 'Unknown')

    # FIX: Build test scores string from dict or handle missing
    test_scores = profile.get('test_scores', {})
    test_scores_str = self._format_test_scores(test_scores)

    lines = [
        "# Student Profile",
        "",
        f"**Name:** {name}",
        f"**Grade:** {profile.get('grade', 'N/A')}",
        f"**School Type:** {profile.get('school_type') or 'N/A'}",
        "",
        "## Academic Profile",
        f"- GPA: {profile.get('gpa') or 'N/A'}",
        f"- Test Scores: {test_scores_str}",
        f"- Course Rigor: N/A",  # Not tracked in DB
        "",
        # ... rest unchanged
    ]
```

---

## Summary of Required Changes

### Immediate (P0) - 4 changes
1. `sync.py:232` - Fix table name `gameplans` → `game_plans`
2. `database.py:208` - Fix table name `gameplans` → `game_plans`
3. `sync.py:235` - Fix column name `status` → `plan_status`
4. `database.py:211` - Fix column name `status` → `plan_status`

### High Priority (P1) - 4 changes
5. `blocks.py:68` - Construct name from first_name + last_name
6. `blocks.py:74` - Build test_scores dict from sat_score/act_score
7. `sync.py:148` - Don't look for assessment_data column
8. `database.py:117` - Build assessment data from profile columns

### Medium Priority (P2) - 5 missing tables
- Either create tables or update code to gracefully skip

---

## Appendix: Sample Profile Data

```json
{
  "id": "4c4c94f9-a7df-4483-9dc6-7905dda36386",
  "first_name": "Huda",
  "last_name": "Sira",
  "email": "huda@ivylevel.com",
  "grade": 11,
  "gpa": 3.9,
  "sat_score": 1590,
  "act_score": null,
  "archetype": "SCHOLAR",
  "ivy_score": 79,
  "target_major": "Computer Science",
  "intended_major": "Computer Science",
  "narrative_dna": "Growing up as a South Asian Muslim...",
  "narrative_brand_statement": "A South Asian Muslim innovator...",
  "target_schools": null,
  "school_type": null
}
```
