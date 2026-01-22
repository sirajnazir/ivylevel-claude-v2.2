# IvyLevel Changelog

**Current Version:** MVP 1.0.3
**Last Updated:** January 21, 2026 @ 20:15 PST

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
