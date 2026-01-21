# IvyQuest Proactive Autonomy Specification v10.0

**Document ID:** SPEC_PROACTIVE_AUTONOMY_v10.0_20260120
**Version:** 10.0
**Date:** 2026-01-20
**Status:** Implemented (Feature-Flagged OFF)
**Author:** Claude Code

---

## 1. Executive Summary

This specification documents the v10.0 Proactive Autonomy implementation, which adds autonomous coaching capabilities to the existing agent system without modifying any working functionality.

### Key Principle: Additive Only

All v10.0 changes follow the **ADDITIVE ONLY** principle:
- NO modifications to existing agent files
- NO modifications to existing scheduler jobs
- NO modifications to existing database tables
- ALL new features are feature-flagged OFF by default

### What v10.0 Adds

| Component | Description | Status |
|-----------|-------------|--------|
| `/agents/proactive/` module | New module for proactive capabilities | ✅ Implemented |
| Migration 043 | 6 new tables for proactive autonomy | ✅ Created |
| Opportunity Matcher | Hourly job matching students to opportunities | ✅ Implemented |
| Feature Flags | PROACTIVE_ENABLED and granular flags | ✅ Implemented |
| main.py registration | Proactive jobs registered (additive) | ✅ Implemented |

---

## 2. Architecture Overview

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXISTING SYSTEM (UNCHANGED)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ExecutionChatAgent (v5.4)  ←→  Supabase (45 existing tables)               │
│  GamePlanAgent                                                               │
│  AwardsAgent                                                                 │
│  Other agents...                                                             │
│                                                                              │
│  APScheduler (execution_jobs.py, execution_scheduler.py)                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
                           [ADDITIVE LAYER v10.0]
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          v10.0 PROACTIVE AUTONOMY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /agents/proactive/                                                          │
│  ├── __init__.py           # Module exports                                 │
│  ├── config.py             # Feature flags (PROACTIVE_ENABLED, etc.)        │
│  ├── opportunity_matcher.py # Hourly opportunity matching job               │
│  └── scheduler.py          # Job registration                               │
│                                                                              │
│  New Tables (Migration 043):                                                │
│  ├── nudge_queue           # Proactive nudges                               │
│  ├── proactive_notifications # Autonomous notifications                     │
│  ├── student_outcomes      # Track wins/losses                              │
│  ├── autonomous_reasoning_cycles # Reasoning logs                           │
│  ├── coaching_assets       # Jenny's techniques                             │
│  └── technique_effectiveness # What works per archetype                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Feature Flag Architecture

```
PROACTIVE_ENABLED (master switch)
         │
         ├── PROACTIVE_OPPORTUNITY_MATCH
         ├── PROACTIVE_DEADLINE_ALERTS
         ├── PROACTIVE_STALL_DETECTION
         ├── PROACTIVE_INACTIVITY_CHECK
         └── PROACTIVE_OUTCOME_TRACKING
```

**All flags default to FALSE** for safe rollout.

---

## 3. New Database Tables

### 3.1 Migration 043: proactive_autonomy_tables.sql

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `nudge_queue` | Proactive nudges from scheduler | profile_id, nudge_type, priority, message_draft, status |
| `proactive_notifications` | Autonomous notifications | profile_id, notification_type, title, message, urgency |
| `student_outcomes` | Track real outcomes (wins/losses) | profile_id, outcome_type, outcome_data, contributing_factors |
| `autonomous_reasoning_cycles` | Log reasoning cycles | profile_id, trigger_event, predictions, decisions, actions_taken |
| `coaching_assets` | Jenny's techniques library | name, category, content, effectiveness_score |
| `technique_effectiveness` | Per-archetype effectiveness | asset_id, archetype, times_used, success_count, effectiveness_rate |

### 3.2 Helper Functions

| Function | Purpose |
|----------|---------|
| `get_pending_nudges(profile_id, limit)` | Get pending nudges sorted by priority |
| `update_asset_effectiveness(asset_id, archetype, situation, was_successful)` | Update technique effectiveness after outcome |

---

## 4. Proactive Module Implementation

### 4.1 config.py

```python
# Environment Variables (all default to false)
PROACTIVE_ENABLED=false          # Master switch
PROACTIVE_OPPORTUNITY_MATCH=false # Hourly opportunity matching
PROACTIVE_DEADLINE_ALERTS=false   # Deadline proximity alerts
PROACTIVE_STALL_DETECTION=false   # Project stall detection
PROACTIVE_INACTIVITY_CHECK=false  # Student inactivity check-ins
PROACTIVE_OUTCOME_TRACKING=false  # Track wins/losses for learning

# Intervals (configurable)
PROACTIVE_OPPORTUNITY_INTERVAL=1  # Hours between opportunity matches
PROACTIVE_DEADLINE_INTERVAL=6     # Hours between deadline checks
PROACTIVE_STALL_HOUR=9            # Hour (24h) for daily stall check
```

### 4.2 opportunity_matcher.py

The opportunity matcher:
1. Runs hourly (when enabled)
2. Gets all active student profiles
3. Matches each profile to opportunities based on:
   - Archetype alignment
   - Major/interest alignment
   - Grade eligibility
   - Deadline proximity
   - Prestige level
4. Creates nudges in `nudge_queue` for delivery
5. Avoids duplicate nudges within 24 hours

### 4.3 scheduler.py

Registers 4 proactive jobs with APScheduler:
1. **opportunity_match**: Hourly (IntervalTrigger)
2. **deadline_alerts**: Every N hours (IntervalTrigger)
3. **stall_detection**: Daily at configured hour (CronTrigger)
4. **inactivity_check**: Daily at noon (CronTrigger)

All jobs:
- Check their feature flag before running
- Return `{"skipped": true}` when disabled
- Log their execution for debugging

---

## 5. main.py Integration

### 5.1 Additive Registration

```python
# v10.0: Register Proactive Autonomy scheduler jobs
# ADDITIVE: Opportunity matching, deadline alerts, stall detection, inactivity checks
# All jobs respect PROACTIVE_ENABLED flag (default: false)
try:
    from proactive import register_proactive_jobs
    register_proactive_jobs(workflow_runner.scheduler, db)
    logger.info("proactive_scheduler_jobs_registered")
except Exception as e:
    logger.warning("proactive_jobs_registration_skipped", error=str(e))
```

### 5.2 Fail-Safe Design

- Uses try/catch to prevent failures from affecting startup
- Gracefully skips when module not available
- Logs warnings for debugging

---

## 6. Activation Checklist

To enable proactive features in production:

### Step 1: Run Migration
```bash
# Run migration 043 in Supabase
psql -d your_database -f supabase/migrations/043_proactive_autonomy_tables.sql
```

### Step 2: Enable Features
```env
# Add to .env
PROACTIVE_ENABLED=true

# Enable specific features
PROACTIVE_OPPORTUNITY_MATCH=true
PROACTIVE_DEADLINE_ALERTS=true
PROACTIVE_STALL_DETECTION=true
PROACTIVE_INACTIVITY_CHECK=true
```

### Step 3: Verify
```python
# Check logs for registration
# Should see: "proactive_scheduler_jobs_registered"
# Should see: "proactive_job_registered" for each enabled job
```

### Step 4: Monitor
```sql
-- Check nudge_queue for new entries
SELECT * FROM nudge_queue WHERE status = 'pending' ORDER BY created_at DESC LIMIT 10;

-- Check proactive_notifications
SELECT * FROM proactive_notifications WHERE status = 'pending' LIMIT 10;
```

---

## 7. Backward Compatibility Guarantees

### 7.1 Zero Breaking Changes

| Aspect | Guarantee |
|--------|-----------|
| Existing Agents | NOT MODIFIED - ExecutionChatAgent, GamePlanAgent, etc. unchanged |
| Existing Scheduler | NOT MODIFIED - execution_jobs.py, execution_scheduler.py unchanged |
| Existing Tables | NOT MODIFIED - all 45+ existing tables unchanged |
| Existing API Routes | NOT MODIFIED - all /api/* routes unchanged |
| Default Behavior | UNCHANGED - with PROACTIVE_ENABLED=false, system behaves exactly as v9.0 |

### 7.2 Rollback Procedure

```bash
# Instant rollback - just disable features
PROACTIVE_ENABLED=false

# No code changes needed
# No migration rollback needed (tables are harmless when unused)
```

---

## 8. Files Added/Modified

### 8.1 New Files

| File | Purpose |
|------|---------|
| `/agents/proactive/__init__.py` | Module exports |
| `/agents/proactive/config.py` | Feature flags and configuration |
| `/agents/proactive/opportunity_matcher.py` | Hourly opportunity matching job |
| `/agents/proactive/scheduler.py` | Job registration |
| `/supabase/migrations/043_proactive_autonomy_tables.sql` | Database migration |
| `/agents/specs/SPEC_PROACTIVE_AUTONOMY_v10.0_20260120.md` | This specification |

### 8.2 Modified Files

| File | Change |
|------|--------|
| `/agents/main.py` | ADDITIVE: Added proactive jobs registration block (lines 120-128) |

---

## 9. Testing Plan

### 9.1 Existing Functionality Tests (MUST PASS)

| Test | Command | Expected |
|------|---------|----------|
| Agent imports | `python -c "from agents.execution_chat import ExecutionChatAgent"` | No errors |
| API startup | `uvicorn main:app --port 8000` | Server starts, no errors |
| Execution chat | POST /api/agents/execution/chat/stream | 200 response |
| Weekly plan | Tool: generate_weekly_plan | Plan generated |

### 9.2 Proactive Feature Tests (When Enabled)

| Test | Command | Expected |
|------|---------|----------|
| Config loads | `python -c "from proactive import PROACTIVE_CONFIG; print(PROACTIVE_CONFIG.to_dict())"` | Config dict printed |
| Jobs register | Start server with PROACTIVE_ENABLED=true | "proactive_scheduler_jobs_registered" in logs |
| Opportunity match | Trigger job manually | Nudges created in nudge_queue |

---

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| v10.0 | 2026-01-20 | Initial proactive autonomy implementation |

---

## 11. Next Steps (v10.1+)

### Phase 2: Memory Enhancement
- Post-conversation fact extraction
- Pre-conversation memory injection
- Personal calendar awareness (birthdays, holidays)

### Phase 3: Outcome Tracking
- Track actual wins/losses
- Update technique effectiveness
- Learn what works per archetype

### Phase 4: Letta Evaluation
- Evaluate if Letta still needed
- Potential activation if pragmatic autonomy insufficient

---

*Document generated by Claude Code - v10.0 Proactive Autonomy Implementation*
