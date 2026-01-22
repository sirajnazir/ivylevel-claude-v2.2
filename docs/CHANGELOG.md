# IvyLevel Changelog

**Current Version:** MVP 1.0.4
**Last Updated:** January 22, 2026 @ 14:50 PST

---

## MVP 1.0.4 - Critical Assessment Data Persistence Fix (January 22, 2026 @ 14:50 PST)

**Tag:** `ivylevel-mvp-1.0.4`

### Critical Bug Fixed

**Issue:** Assessment completion was NOT saving data to Supabase database
- ❌ All assessment data remained in browser localStorage only (Zustand stores)
- ❌ No profile data persisted to database
- ❌ No scoring results saved to `assessments` table
- ❌ Assessment marked as incomplete in database
- ❌ Dashboard showed empty/placeholder data after refresh

**Root Cause:**
`handleFrame6Complete()` in `/app/assessment/page.tsx` (lines 91-97) was passing the entire `AssessmentResults` object as the `scores` parameter instead of extracting the flat scores structure that `saveAssessment()` expects.

```typescript
// BEFORE (WRONG):
const scores = results || { score_aptitude: 0, ... };
// This assigned the ENTIRE AssessmentResults object, including nested ivy_ready_score

// AFTER (CORRECT):
const scores = results?.ivy_ready_score
  ? {
      aptitude: results.ivy_ready_score.category_scores.aptitude,
      passion: results.ivy_ready_score.category_scores.passion,
      community: results.ivy_ready_score.category_scores.community,
      identity: results.ivy_ready_score.category_scores.narrative,
      overall: results.ivy_ready_score.total_score,
      ivy_ready_score: results.ivy_ready_score.total_score,
    }
  : { /* defaults */ };
```

### Files Changed

#### 1. `/app/assessment/page.tsx` (lines 91-122)
- **Fixed:** Score extraction to properly convert `AssessmentResults` → flat scores structure
- **Impact:** Assessments now save correctly to database on Frame 6 completion
- **Verification:** Toast notification shows "Assessment Complete - Your profile has been saved!"

#### 2. `/lib/hooks/useUserData.ts` (lines 118-135)
- **Added:** Defensive code to handle existing malformed data in database
- **Fix:** Type guard to detect if `ivy_ready_score` is object vs number
- **Impact:** Dashboard can load both old (malformed) and new (correct) data gracefully

#### 3. `/app/dashboard/page.tsx` (lines 397-408)
- **Removed:** Extensive debug logging from previous debugging session
- **Kept:** Defensive type guards to filter non-string values from arrays
- **Cleanup:** Simplified validation logic while maintaining safety

#### 4. `/components/tabs/AssessmentTab.tsx` (lines 70-92)
- **Removed:** Debug console.log statements
- **Kept:** Defensive validation to prevent rendering invalid data as React children
- **Cleanup:** Condensed validation logic for better readability

#### 5. `/app/logout/page.tsx` (NEW FILE)
- **Created:** Utility route for easy sign-out during testing
- **Purpose:** Clears Supabase session + localStorage, redirects to EntryPortal
- **Usage:** `localhost:3006/logout`

#### 6. `/app/reset/page.tsx` (NEW FILE)
- **Created:** Utility route for deleting all user data during testing
- **Purpose:** Calls `deleteUserData()` → signs out → redirects to EntryPortal
- **Usage:** `localhost:3006/reset` (requires authentication)
- **UI:** Red warning screen with confirmation button

#### 7. `/middleware.ts` (lines 16-23, 147-150)
- **Added:** `/assessment` to protected routes
- **Added:** `/logout` to public routes
- **Added:** `/reset` to protected routes
- **Updated:** Student route check to include `/assessment`

#### 8. `/app/page.tsx` (lines 41, 60)
- **Fixed:** Two redirects from `/quest` → `/assessment`
- **Completed:** Migration from legacy `/quest` route to new `/assessment` route
- **Impact:** Fresh assessments and incomplete assessments now route to correct page

### What Gets Saved to Database Now

When Frame 6 completes, the following data is correctly saved to `assessments` table:

**Profile Data (complete StudentProfile object):**
- Identity Pillar: name, grade, role
- Aptitude Pillar: GPA, SAT/ACT, AP count, academic awards
- Passion Pillar: spike category, leadership level, EC commitment, research level, awards
  - **NEW WHY fields:** why_passion, passion_origin, passion_reason (from Frame 3 Card 10)
- Community Pillar: service leadership, service hours, community impact
- Operating Data: first-gen status, work hours, parent occupations (from Frame 4)
- Target Schools & Major

**Scores Data (flat structure):**
```typescript
{
  aptitude: 78,          // 0-100
  passion: 65,           // 0-100
  community: 52,         // 0-100
  identity: 70,          // 0-100 (narrative)
  overall: 68,           // Total score
  ivy_ready_score: 68    // Same as overall
}
```

**Additional Fields:**
- `archetype`: Student archetype detected by scoring engine
- `completeness_score`: Profile completeness percentage (0-100)
- `completed_at`: Timestamp when assessment finished
- `session_id`: Unique session identifier

### Verification Performed

**Testing Flow:**
1. ✅ Cleared localStorage and sessionStorage
2. ✅ Deleted test user data from database using `/reset` route
3. ✅ Completed fresh assessment (all 6 frames)
4. ✅ Verified toast notification: "Assessment Complete - Your profile has been saved!"
5. ✅ Verified browser console: `[Assessment] Saved successfully: c3c5581f-94f6-425d-ab1f-d3d708b76795`
6. ✅ Verified server logs: `POST /api/score 200 in 481ms`
7. ✅ Verified server logs: `[AssessmentService] Assessment saved: c3c5581f-94f6-425d-ab1f-d3d708b76795`
8. ✅ Navigated to dashboard - no React rendering errors
9. ✅ Dashboard loaded with real scores (not objects)
10. ✅ Database query confirmed data persisted correctly

**Console Logs Confirmed:**
```
[AssessmentService] Assessment saved: c3c5581f-94f6-425d-ab1f-d3d708b76795
[Assessment] Saved successfully: c3c5581f-94f6-425d-ab1f-d3d708b76795
[useUserData] Found assessment data, loading into stores
[useUserData] Marking assessment as complete
[Dashboard] Generating game plan...
```

**No Errors:**
- ❌ No "Objects are not valid as a React child" errors
- ❌ No `totalScore` being an object errors
- ❌ No `ivy_ready_score` structure errors

### Impact

**Before Fix:**
- Students could complete assessment but data wasn't saved
- Dashboard showed empty/placeholder data
- Refreshing browser lost all progress
- Required re-taking entire assessment

**After Fix:**
- ✅ Assessment data persists to database on completion
- ✅ Dashboard loads real data from database
- ✅ Refreshing browser maintains all data
- ✅ Cross-device session continuity (if enabled)
- ✅ Assessment marked as complete in database
- ✅ Scoring results available for game plan generation

### Breaking Changes
None - backward compatible with defensive data loading

### Migration Required
None - old malformed data is handled gracefully

---

## MVP 1.0.3 - PRD Accuracy Fix (January 21, 2026 @ 20:15 PST)

**Tag:** `ivylevel-mvp-1.0.3`

### Changes
- Fixed PRD.md discrepancies found during critical analysis:
  - **Migration count**: Changed "43 SQL migrations" → "32 SQL migrations" (line 663)
  - **Frame naming**: Changed "Frame0-Frame6" → "Frame1-Frame6" (line 637)
  - **Dashboard tabs**: Updated to reflect actual component names (MissionControl, GamePlanFull, CoachConnect, etc.)
  - **Dashboard count**: Changed "Dashboard tabs" → "10 dashboard components"

### Verification Performed
All PRD claims verified against codebase:
- ✅ 8 Active Agents (all exist)
- ✅ 4 Proactive Jobs (all exist)
- ✅ 6-Frame Assessment (confirmed)
- ✅ Proactive System Architecture (confirmed)
- ✅ API Routes (confirmed)

---

## MVP 1.0.2 - Master PRD Specification (January 21, 2026 @ 19:45 PST)

**Tag:** `ivylevel-mvp-1.0.2`

### Changes
- Added `/docs/PRD.md` - Canonical Master Specification (~2000 lines)
  - Part 1: Executive Summary (Vision, North Star, Huda Validation)
  - Part 2: Product Requirements Document (Problems, Solutions, Requirements)
  - Part 3: User Journeys & Jobs-to-be-Done (6 Core Jobs)
  - Part 4: UI/UX Specification (Frames, Dashboard, Interaction Patterns)
  - Part 5: Technical Specification (Architecture, Agents, Proactive System)
  - Part 6: Architecture Diagrams (System, Agent, Data Flow)
  - Part 7: Implementation Status (What's Built vs Deferred)
  - Part 8: Appendix (Glossary, Dependencies, References)
  - Addendum A: Data-Backed Intelligence (Chetty, CDS, High School Data)
- Updated `/docs/README.md` to include PRD as Master Spec

### Purpose
Syncs business/product requirements with technical implementation. This is the single source of truth for what IvyLevel is, what's built, and what's planned.

---

## MVP 1.0.1 - Documentation Accuracy Fix (January 21, 2026 @ 19:15 PST)

**Tag:** `ivylevel-mvp-1.0.1`

### Changes
- Fixed agent file names in ARCHITECTURE.md and AGENTS.md:
  - `narrative.py` → `narrative_synthesis.py`
  - `ec_agent.py` → `extracurriculars.py`
  - Added missing `OpportunityAgent` (`opportunity.py`)
- Removed references to non-existent files (`deadline_monitor.py`, `stall_detector.py`)
- Added Version Reference table to README.md
- Standardized all docs to MVP 1.x.y versioning with timestamps

### Files Updated
- `/docs/ARCHITECTURE.md`
- `/docs/README.md`
- `/agents/docs/AGENTS.md`
- All canonical docs (version/timestamp headers)

---

## MVP 1.0.0 - Production Release (January 21, 2026)

**Tag:** `ivylevel-mvp-v1.0`

### Summary
First production-ready release with complete codebase cleanup and canonical documentation.

### Features
- **Proactive Opportunity Matching** - Automatically matches students to awards/programs
- **Deadline Monitoring** - Alerts for approaching deadlines
- **Stall Detection** - Identifies stuck projects
- **Inactivity Checks** - Re-engages inactive students

### Codebase Cleanup
- Archived 91+ old documentation files to `/_archive/docs/`
- Archived 21 old code directories to `/_archive/code/`
- Clean root directory with only essential files
- Updated `.gitignore` with proper patterns

### Documentation Restructure
- Created `/STRUCTURE.md` - Master project structure reference
- Created `/docs/` canonical documentation (ARCHITECTURE, DATABASE, API, DEPLOYMENT)
- Created `/agents/docs/` backend documentation (AGENTS, PROACTIVE)
- Created `/app/docs/` frontend documentation (COMPONENTS, FRAMES)
- Added strict documentation rules to CLAUDE.md

### Technical
- Fixed opportunity matcher schema (`application_deadline` vs `deadline`)
- Created REST API at `/proactive/*`
- Migration 043: proactive_autonomy_tables
- 6 new database tables

---

## Pre-MVP Development History

*These versions used internal numbering (v1-v10) before MVP release.*

### Internal v10 - Proactive Autonomy (January 2026)
- Proactive opportunity matching system
- APScheduler background jobs
- nudge_queue and proactive_notifications tables

### Internal v9 - Middleware Integration (January 2026)
- 50 middleware patterns implemented
- Quality scoring system
- Coaching assets (E1-E22 techniques)

### Internal v5.4 - Execution Chat Enhancement (January 2026)
- Game plan context in system prompt
- 13 execution coaching tools
- EDS (Execution Distress Score) tracking

### Internal v5 - Multi-Agent Architecture (January 2026)
- ReAct cycles for sub-agents
- LangChain/Agno integration
- Orchestrator pattern

### Internal v4 - Assessment Frames (December 2025)
- 6-frame assessment flow
- Profile scoring engine
- Archetype detection

### Internal v3 - Game Plan Generation (December 2025)
- 4-year strategic roadmaps
- Project-based planning

### Internal v2 - Dashboard MVP (December 2025)
- Multi-tab dashboard
- Profile management

### Internal v1 - Foundation (November 2025)
- Initial Next.js setup
- Supabase integration

---

## Upcoming: MVP 1.1.0

### Planned Features
- Proactive Notifications UI in dashboard
- Enhanced Memory Display
- Outcome Tracking (win/loss learning)

---

## Version Naming Convention

```
MVP X.Y.Z

X = Major release (MVP 1, MVP 2, etc.)
Y = Feature update (1.1, 1.2, etc.)
Z = Bug fix / doc update (1.0.1, 1.0.2, etc.)
```

| Version | Type | Example |
|---------|------|---------|
| MVP X.0.0 | Major release | MVP 2.0.0 - Next major |
| MVP X.Y.0 | Feature update | MVP 1.1.0 - Notifications UI |
| MVP X.Y.Z | Bug/doc fix | MVP 1.0.1 - Doc accuracy fix |

---

## Rollback Procedures

### Code Rollback
```bash
# View recent commits
git log --oneline -10

# Rollback to specific version
git checkout <tag-name>

# Example
git checkout ivylevel-mvp-1.0.1
```

### Database Rollback
- Migrations are forward-only in Supabase
- For critical rollbacks, restore from backup
