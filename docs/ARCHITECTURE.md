# IvyLevel Architecture

**Version:** MVP 1.0.1
**Last Updated:** January 21, 2026 @ 19:15 PST
**Status:** Production

---

## Overview

IvyLevel is an AI-powered college coaching platform featuring:
- **Assessment Engine** - 6 interactive frames for student profiling
- **Game Plan Generation** - Personalized 4-year strategic roadmaps
- **Execution Coaching** - Weekly plans, EDS tracking, Jenny voice
- **Opportunity Matching** - Proactive awards, programs, EC recommendations

---

## Tech Stack

### Backend (FastAPI)
| Component | Technology | Location |
|-----------|------------|----------|
| Framework | FastAPI + Agno + LangChain | `/agents/` |
| Database | Supabase (PostgreSQL + pgvector) | `/supabase/` |
| Scheduler | APScheduler | `/agents/proactive/scheduler.py` |
| Version | v15.0.0 | |

### Frontend (Next.js)
| Component | Technology | Location |
|-----------|------------|----------|
| Framework | Next.js 14 + React | `/` (root) |
| State | Zustand | `/lib/store/` |
| Styling | Tailwind + shadcn/ui | `/components/ui/` |
| Frames | Frame-based SDK | `/components/frames/` |

---

## Key Components

### Active Agents (`/agents/agents/`)

| Agent | File | Purpose | Status |
|-------|------|---------|--------|
| ExecutionChatAgent | `execution_chat.py` | Weekly coaching conversations | ✅ Active (v5.4) |
| GamePlanAgent | `gameplan.py` | Strategic roadmap generation | ✅ Active |
| AwardsAgent | `awards.py` | Award/scholarship matching | ✅ Active |
| AssessmentAgent | `assessment.py` | Profile assessment processing | ✅ Active |
| NarrativeSynthesis | `narrative_synthesis.py` | Spike narrative generation | ✅ Active |
| ProgramsAgent | `programs.py` | Summer program recommendations | ✅ Active |
| ExtracurricularsAgent | `extracurriculars.py` | Extracurricular coaching | ✅ Active |
| OpportunityAgent | `opportunity.py` | Opportunity recommendations | ✅ Active |

### Proactive System (`/agents/proactive/`)

| Component | File | Purpose | Status |
|-----------|------|---------|--------|
| Config | `config.py` | Feature flags (PROACTIVE_ENABLED) | ✅ Active |
| Scheduler | `scheduler.py` | APScheduler job registration, all background jobs | ✅ Active |
| Opportunity Matcher | `opportunity_matcher.py` | Award/program matching | ✅ Active |

**Note:** Deadline alerts, stall detection, and inactivity checks are implemented as jobs within `scheduler.py`, not as separate files.

### API Routes (`/agents/api/routes/`)

| Router | Prefix | Purpose |
|--------|--------|---------|
| execution.py | `/api/execution/` | Execution hub endpoints |
| proactive.py | `/proactive/` | Opportunity matching API |
| main.py routes | `/api/agents/` | Multi-agent orchestration |

---

## Database (Supabase)

### Key Tables

| Category | Tables |
|----------|--------|
| **Core** | `profiles`, `assessments`, `game_plans`, `projects` |
| **Execution** | `weekly_plans`, `conversations`, `eds_data` |
| **Proactive** | `nudge_queue`, `proactive_notifications`, `student_outcomes` |
| **Resources** | `awards`, `opportunities`, `ecs`, `coaching_assets` |

### Migration Status
- Total migrations: 43
- Latest: `043_proactive_autonomy_tables.sql`

---

## Feature Flags

### Environment Variables (`.env`)

```bash
# Core
PROACTIVE_ENABLED=true          # Master switch for proactive system

# Proactive Features
PROACTIVE_OPPORTUNITY_MATCH=true
PROACTIVE_DEADLINE_ALERTS=true
PROACTIVE_STALL_DETECTION=true
PROACTIVE_INACTIVITY_CHECK=true

# Dormant (not in MVP)
LETTA_ENABLED=false             # Letta integration
```

---

## Dormant/Future Code

### Letta Integration (`/agents/letta/`)
- **Status:** Code complete, feature-flagged OFF
- **Purpose:** Advanced memory + A2A communication
- **Enable when:** Post-MVP evaluation if needed
- **Note:** Isolated with try/catch in main.py

---

## API Endpoints

### Active Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/api/agents/game-plan/generate` | Generate game plan |
| POST | `/api/agents/execution/chat` | Execution chat |
| GET | `/api/execution/eds/{profile_id}` | Get EDS data |
| GET | `/api/execution/weekly-plan/{profile_id}` | Get weekly plan |
| GET | `/proactive/matches/{profile_id}` | Get opportunity matches |
| GET | `/proactive/status` | Get proactive config |

### Dormant Endpoints
- `/api/letta/*` - Returns 503 when `LETTA_ENABLED=false`

---

## Directory Structure

**See [/STRUCTURE.md](/STRUCTURE.md) for complete project structure.**

```
/ivyquest-claude-v2.2/
│
├── FRONTEND (Next.js at root)
│   ├── app/                  # Next.js App Router
│   ├── components/           # React components
│   ├── hooks/                # React hooks
│   ├── lib/                  # Utilities, stores
│   └── types/                # TypeScript types
│
├── BACKEND (Python FastAPI)
│   └── agents/               # Backend root
│       ├── agents/           # Agent implementations (yes, nested)
│       ├── api/routes/       # API routers
│       ├── proactive/        # Proactive system (v10.0)
│       └── main.py           # Entry point
│
├── DATABASE
│   └── supabase/migrations/  # SQL migrations
│
├── DOCUMENTATION
│   ├── docs/                 # Master docs
│   ├── agents/docs/          # Backend docs
│   └── app/docs/             # Frontend docs
│
└── ARCHIVE
    └── _archive/             # Old code & docs
```

**Note on `/agents/agents/`:** The outer `agents/` is the Python backend folder. The inner `agents/` contains the actual AI agent class implementations. This naming is historical - see STRUCTURE.md for details.

---

## Deployment

### Development
```bash
# Backend
cd agents && source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
npm run dev
```

### Production
- Backend: Deployed via container
- Frontend: Vercel
- Database: Supabase Cloud

---

## Monitoring

### Observability Stack
- **LangSmith:** Agent tracing (LANGCHAIN_TRACING_V2=true)
- **Langfuse:** (Optional) Metrics collection
- **Structured Logging:** structlog with JSON output

### Health Checks
- `/health` - Basic health
- `/proactive/status` - Proactive system status
