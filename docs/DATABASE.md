# IvyLevel Database Specification

**Version:** MVP 1.0.1
**Last Updated:** January 21, 2026 @ 19:15 PST
**Database:** Supabase (PostgreSQL + pgvector)

---

## Overview

IvyLevel uses Supabase as the primary database with:
- **PostgreSQL** for relational data
- **pgvector** for embeddings (semantic search)
- **Row Level Security (RLS)** for access control

---

## Core Tables

### User & Profile

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `profiles` | Student profiles | id, user_id, first_name, grade, archetype, target_major, spike |
| `assessments` | Assessment responses | id, profile_id, frame_number, responses, scores |
| `user_preferences` | User settings | id, profile_id, preferences |

### Planning & Execution

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `game_plans` | 4-year strategic plans | id, profile_id, plan_data, version |
| `projects` | Individual projects | id, profile_id, name, status, category, deadline |
| `weekly_plans` | Weekly execution plans | id, profile_id, week_start, tasks, status |
| `eds_data` | Execution Distress Score | id, profile_id, score, factors, calculated_at |

### Conversations & Memory

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `conversations` | Chat history | id, profile_id, agent_type, messages |
| `memory_entries` | Agent memory | id, profile_id, agent_id, content, embedding |

### Resources

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `awards` | Scholarships & awards | id, name, deadline, eligibility, prestige_score |
| `opportunities` | Summer programs | id, name, application_deadline, category, tier |
| `ecs` | Extracurricular activities | id, name, category, impact_score |
| `coaching_assets` | Jenny's techniques | id, code, name, category, content |

### Proactive System (v10.0)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `nudge_queue` | Pending nudges | id, profile_id, nudge_type, priority, status |
| `proactive_notifications` | Autonomous notifications | id, profile_id, notification_type, message |
| `student_outcomes` | Win/loss tracking | id, profile_id, outcome_type, result |
| `autonomous_reasoning_cycles` | Agent reasoning logs | id, profile_id, agent_id, reasoning |
| `technique_effectiveness` | Learning from outcomes | id, technique_id, archetype, effectiveness |

---

## Key Relationships

```
profiles
├── assessments (1:many)
├── game_plans (1:many)
├── projects (1:many)
├── weekly_plans (1:many)
├── conversations (1:many)
├── nudge_queue (1:many)
└── proactive_notifications (1:many)

awards/opportunities
└── matched via proactive_notifications.metadata
```

---

## Migrations

**Location:** `/supabase/migrations/`

### Recent Migrations

| Number | Name | Description |
|--------|------|-------------|
| 043 | `proactive_autonomy_tables` | v10.0 proactive system tables |
| 042 | `coaching_assets` | Jenny's execution techniques |
| 041 | `eds_enhancements` | EDS calculation improvements |

### Running Migrations

```bash
# Apply migrations
supabase db push

# Check migration status
supabase migration list

# Create new migration
supabase migration new <name>
```

---

## Column Reference

### profiles

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| user_id | uuid | Auth user reference |
| first_name | text | Student's first name |
| last_name | text | Student's last name |
| grade | integer | Current grade (9-12) |
| archetype | text | Student archetype (stem_innovator, etc.) |
| target_major | text | Intended college major |
| spike | text | Unique strength/passion area |
| pillars | jsonb | Supporting interest areas |
| target_schools | text[] | Target colleges |
| is_active | boolean | Account active status |
| created_at | timestamp | Creation timestamp |

### awards

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| name | text | Award name |
| organization | text | Sponsoring organization |
| deadline | date | Application deadline |
| eligibility | jsonb | Eligibility criteria |
| prestige_score | integer | 1-10 prestige rating |
| category | text | Award category |
| is_active | boolean | Currently available |

### opportunities

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| name | text | Program name |
| organization | text | Host organization |
| application_deadline | date | Deadline (note: NOT "deadline") |
| type | text | Program type |
| category | text | Program category |
| tier | text | Selectivity tier |
| prestige_score | integer | 1-10 prestige rating |
| is_active | boolean | Currently available |

---

## Indexes

Key indexes for performance:

```sql
-- Profile lookups
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_profiles_archetype ON profiles(archetype);

-- Deadline queries
CREATE INDEX idx_awards_deadline ON awards(deadline);
CREATE INDEX idx_opportunities_deadline ON opportunities(application_deadline);

-- Conversation history
CREATE INDEX idx_conversations_profile ON conversations(profile_id, created_at);

-- Proactive queries
CREATE INDEX idx_nudge_queue_status ON nudge_queue(status, priority);
CREATE INDEX idx_notifications_profile ON proactive_notifications(profile_id, status);
```

---

## Supabase Connection

### Environment Variables

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...    # Server-side only
```

### Client Usage

```typescript
// Frontend (anon key)
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(url, anonKey)

// Backend (service role)
const supabase = createClient(url, serviceRoleKey)
```
