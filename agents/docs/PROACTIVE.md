# IvyLevel Proactive System (v10.0)

**Version:** v10.0
**Last Updated:** January 21, 2026
**Location:** `/agents/proactive/`

---

## Overview

The Proactive Autonomy system enables Jenny to reach out to students without being prompted. It runs scheduled background jobs that:

1. **Match opportunities** - Find relevant awards/programs
2. **Alert on deadlines** - Warn about approaching deadlines
3. **Detect stalls** - Identify stuck projects
4. **Check inactivity** - Re-engage inactive students

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    APScheduler                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Opportunity │ │  Deadline   │ │    Stall    │   │
│  │   Matcher   │ │   Alerts    │ │  Detector   │   │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘   │
└─────────┼───────────────┼───────────────┼───────────┘
          │               │               │
          ▼               ▼               ▼
    ┌─────────────────────────────────────────┐
    │              nudge_queue                 │
    │        proactive_notifications           │
    └─────────────────────────────────────────┘
                      │
                      ▼
              [Frontend Display]
```

---

## Components

### config.py

Feature flags and scheduling configuration.

```python
PROACTIVE_ENABLED=true           # Master switch
PROACTIVE_OPPORTUNITY_MATCH=true # Hourly matching
PROACTIVE_DEADLINE_ALERTS=true   # 6-hourly checks
PROACTIVE_STALL_DETECTION=true   # Daily at 9am
PROACTIVE_INACTIVITY_CHECK=true  # Daily at noon
```

### scheduler.py

Registers APScheduler jobs on server startup.

**Jobs:**
| Job | Schedule | Function |
|-----|----------|----------|
| Opportunity Matcher | Every 1 hour | `job_opportunity_match` |
| Deadline Alerts | Every 6 hours | `_job_deadline_alerts` |
| Stall Detection | Daily 9:00 AM | `_job_stall_detection` |
| Inactivity Check | Daily 12:00 PM | `_job_inactivity_check` |

### opportunity_matcher.py

Matches students to awards and programs.

**Logic:**
1. Query all active profiles
2. For each profile, find opportunities with:
   - Deadlines in next 30 days
   - Category matching archetype
   - Eligibility matching grade
3. Score matches (0.0 - 1.0)
4. Create nudges for scores > 0.3

**Scoring Factors:**
- Base deadline score: 0.15
- Archetype match: 0.25
- Major match: 0.15
- Grade match: 0.15
- Prestige bonus: 0.15
- Category match: 0.15

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/proactive/status` | Get config and schedules |
| GET | `/proactive/matches/{profile_id}` | Get matches for profile |
| GET | `/proactive/notifications/{profile_id}` | Get notifications |
| POST | `/proactive/trigger/{job_name}` | Manual trigger |

### Example: Get Matches

```bash
curl "http://localhost:8000/proactive/matches/{profile_id}?max_matches=3"
```

**Response:**
```json
{
  "success": true,
  "matches": [
    {
      "source": "opportunity",
      "opportunity_name": "Summer Science Program",
      "match_score": 0.85,
      "deadline": "2026-02-15",
      "match_reasons": [
        "🎯 Matches your STEM Innovator profile",
        "⭐ Highly prestigious opportunity"
      ]
    }
  ]
}
```

---

## Database Tables

### nudge_queue

Pending nudges waiting for delivery.

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| profile_id | uuid | Target student |
| nudge_type | text | opportunity_match, deadline_alert, etc. |
| priority | text | high, medium, low |
| message_draft | text | Generated message |
| metadata | jsonb | Match details |
| status | text | pending, sent, dismissed |

### proactive_notifications

Notifications ready for display.

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| profile_id | uuid | Target student |
| notification_type | text | Type of notification |
| title | text | Display title |
| message | text | Display message |
| priority | text | Priority level |
| status | text | pending, sent, actioned, dismissed |

---

## Configuration

### Environment Variables

```bash
# Master switch
PROACTIVE_ENABLED=true

# Individual features
PROACTIVE_OPPORTUNITY_MATCH=true
PROACTIVE_DEADLINE_ALERTS=true
PROACTIVE_STALL_DETECTION=true
PROACTIVE_INACTIVITY_CHECK=true
PROACTIVE_OUTCOME_TRACKING=true

# Scheduling (optional - defaults shown)
PROACTIVE_OPPORTUNITY_INTERVAL=1   # Hours
PROACTIVE_DEADLINE_INTERVAL=6      # Hours
PROACTIVE_STALL_HOUR=9             # 9 AM
```

---

## Testing

### Manual Trigger

```bash
# Trigger opportunity matching
curl -X POST "http://localhost:8000/proactive/trigger/opportunity_match"

# Trigger all jobs
curl -X POST "http://localhost:8000/proactive/trigger/all"
```

### Check Logs

```bash
# In server output, look for:
# - "opportunity_match_job_started"
# - "opportunity_matching_completed"
# - "opportunity_match_job_completed"
```

---

## Troubleshooting

### Jobs Not Running

1. Check `PROACTIVE_ENABLED=true` in `.env`
2. Verify server started without errors
3. Look for "proactive_scheduler_jobs_registered" in logs

### No Matches Found

1. Verify profile has archetype, grade, target_major set
2. Check opportunities/awards have upcoming deadlines
3. Check `is_active=true` on opportunities

### Duplicate Notifications

- The system checks for existing nudges in last 24 hours
- Duplicates are skipped automatically
