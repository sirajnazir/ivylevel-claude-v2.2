# IvyLevel Project Structure

**Version:** MVP 1.0.1
**Last Updated:** January 21, 2026 @ 19:15 PST

---

## Quick Reference

```
ivyquest-claude-v2.2/
│
├── 📁 FRONTEND (Next.js)
│   ├── app/                 # Next.js App Router (pages, layouts)
│   ├── components/          # React components
│   ├── hooks/               # React hooks
│   ├── lib/                 # Utilities, stores, constants
│   ├── types/               # TypeScript type definitions
│   └── public/              # Static assets
│
├── 📁 BACKEND (Python/FastAPI)
│   └── agents/              # Python backend (FastAPI + AI agents)
│       ├── agents/          # Agent implementations
│       ├── api/             # API routes
│       ├── proactive/       # Proactive system (v10.0)
│       └── main.py          # Entry point
│
├── 📁 DATABASE
│   └── supabase/            # Supabase config & migrations
│       └── migrations/      # SQL migrations
│
├── 📁 DOCUMENTATION
│   ├── docs/                # Master documentation
│   ├── agents/docs/         # Backend docs
│   └── app/docs/            # Frontend docs
│
├── 📁 INFRASTRUCTURE
│   ├── scripts/             # Utility scripts
│   ├── tests/               # Test suites
│   └── tools/               # Dev tools
│
└── 📁 ARCHIVE
    ├── _archive/            # Old code & docs
    └── _future/             # Planned features
```

---

## Detailed Structure

### Frontend (Next.js 14)

All frontend code uses Next.js App Router pattern.

```
/app/                        # Next.js App Router
├── (auth)/                  # Auth route group
│   └── login/page.tsx
├── (dashboard)/             # Dashboard route group
│   ├── assessment/          # Assessment frames
│   ├── dashboard/           # Main dashboard
│   └── execution/           # Execution hub
├── api/                     # Next.js API routes
│   ├── auth/
│   └── profile/
├── layout.tsx               # Root layout
├── page.tsx                 # Home page
└── docs/                    # Frontend documentation
    ├── README.md
    ├── COMPONENTS.md
    └── FRAMES.md

/components/                 # React Components
├── frames/                  # Assessment frame components
│   ├── Frame0.tsx → Frame6.tsx
├── dashboard/               # Dashboard tab components
│   ├── OverviewTab.tsx
│   ├── ExecutionTab.tsx
│   └── MultiAgentTab.tsx
├── ui/                      # shadcn/ui primitives
│   ├── button.tsx
│   ├── card.tsx
│   └── ...
└── shared/                  # Shared components
    ├── Header.tsx
    └── AgentChat.tsx

/hooks/                      # React Hooks
├── useProfile.ts
├── useAssessment.ts
└── useExecution.ts

/lib/                        # Utilities & State
├── store/                   # Zustand stores
│   ├── profile.ts
│   └── assessment.ts
├── constants/               # Constants
│   └── brand.ts             # Brand colors
├── api/                     # API clients
│   └── agents.ts
└── utils/                   # Helper functions

/types/                      # TypeScript Types
├── profile.ts
├── assessment.ts
└── api.ts

/public/                     # Static Assets
├── images/
└── icons/
```

### Backend (Python FastAPI)

The `/agents/` folder is the Python backend (named "agents" because it's an AI agent system).

```
/agents/                     # Python Backend Root
├── main.py                  # FastAPI entry point
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container build
├── .env                     # Environment variables
│
├── agents/                  # Agent Implementations ⚠️
│   ├── __init__.py
│   ├── base.py              # Base agent class
│   ├── execution_chat.py    # Execution coaching (v5.4)
│   ├── gameplan.py          # Game plan generation
│   ├── awards.py            # Awards matching
│   ├── assessment.py        # Assessment processing
│   └── ...
│
├── api/                     # API Layer
│   └── routes/
│       ├── execution.py     # /api/execution/*
│       └── proactive.py     # /proactive/*
│
├── proactive/               # Proactive System (v10.0)
│   ├── config.py            # Feature flags
│   ├── scheduler.py         # APScheduler jobs
│   └── opportunity_matcher.py
│
├── tools/                   # Agent Tools
│   ├── database.py          # Supabase client
│   └── ...
│
├── memory/                  # Memory management
├── middleware/              # Request middleware
├── letta/                   # Future: Letta integration
│
├── docs/                    # Backend Documentation
│   ├── README.md
│   ├── AGENTS.md
│   └── PROACTIVE.md
│
└── specs/                   # Planning specs only
    └── README.md
```

**Note on `/agents/agents/`:** This nested structure exists because:
- Outer `agents/` = the entire Python backend
- Inner `agents/` = the actual AI agent implementations

This naming is historical. The inner folder contains the agent classes.

### Database (Supabase)

```
/supabase/                   # Supabase Configuration
├── config.toml              # Supabase config
└── migrations/              # SQL Migrations
    ├── 001_initial.sql
    ├── ...
    └── 043_proactive_autonomy_tables.sql  # Latest
```

### Documentation

```
/docs/                       # Master Documentation
├── README.md                # Doc index (START HERE)
├── ARCHITECTURE.md          # System architecture
├── DATABASE.md              # Database schema
├── API.md                   # API reference
├── DEPLOYMENT.md            # Deployment guide
└── CHANGELOG.md             # Version history

/agents/docs/                # Backend-specific
├── README.md
├── AGENTS.md                # Agent catalog
└── PROACTIVE.md             # Proactive system

/app/docs/                   # Frontend-specific
├── README.md
├── COMPONENTS.md            # Component guide
└── FRAMES.md                # Assessment frames
```

### Infrastructure & Tools

```
/scripts/                    # Utility Scripts
├── seed-data.js
└── ...

/tests/                      # Test Suites
└── ...

/tools/                      # Development Tools
└── ...
```

### Archive & Future

```
/_archive/                   # Archived Code & Docs
├── code/                    # Old code
├── docs/                    # Old documentation
│   ├── specs/
│   ├── analyses/
│   └── iterations/
└── experiments/             # Experimental code

/_future/                    # Planned Features
├── letta/
├── features/
└── enhancements/
```

---

## Configuration Files (Root)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | AI agent instructions |
| `STRUCTURE.md` | This file |
| `package.json` | Node.js dependencies |
| `tsconfig.json` | TypeScript config |
| `tailwind.config.ts` | Tailwind CSS config |
| `next.config.js` | Next.js config |
| `middleware.ts` | Next.js middleware |
| `playwright.config.ts` | E2E test config |
| `postcss.config.js` | PostCSS config |
| `vercel.json` | Vercel deployment |
| `.env.local` | Frontend env vars |
| `.gitignore` | Git ignore rules |

---

## Key Entry Points

| What | Location | Command |
|------|----------|---------|
| Frontend dev | Root | `npm run dev` |
| Backend dev | /agents | `uvicorn main:app --reload` |
| Frontend build | Root | `npm run build` |
| Backend container | /agents | `docker build .` |
| Migrations | /supabase | `supabase db push` |

---

## Import Patterns

### Frontend (TypeScript)

```typescript
// Components
import { Button } from '@/components/ui/button'

// Hooks
import { useProfile } from '@/hooks/useProfile'

// Store
import { useProfileStore } from '@/lib/store/profile'

// Constants
import { BRAND_COLORS } from '@/lib/constants/brand'

// Types
import type { Profile } from '@/types/profile'
```

### Backend (Python)

```python
# From main.py
from agents.execution_chat import ExecutionChatAgent
from proactive.scheduler import register_proactive_jobs
from tools.database import get_supabase_client
from api.routes.proactive import router as proactive_router
```

---

## Why This Structure?

### Frontend at Root
Next.js expects `app/`, `components/`, `lib/` at root level. This is the standard Next.js convention.

### Backend in /agents/
The Python backend is isolated in `/agents/` with its own:
- Virtual environment (`venv/`)
- Dependencies (`requirements.txt`)
- Entry point (`main.py`)

### Nested agents/agents/
Historical naming. The outer `agents/` is the backend, inner `agents/` contains agent classes. Renaming would break imports.

---

## Adding New Code

### New Frontend Component
```
/components/<category>/<ComponentName>.tsx
```

### New Backend Agent
```
/agents/agents/<agent_name>.py
```

### New API Route (Backend)
```
/agents/api/routes/<route_name>.py
→ Register in main.py
```

### New API Route (Frontend)
```
/app/api/<route>/route.ts
```

### New Migration
```
/supabase/migrations/<number>_<name>.sql
→ Run: supabase db push
```

---

## Quick Navigation

| I want to... | Go to... |
|--------------|----------|
| Edit a React component | `/components/` |
| Edit an AI agent | `/agents/agents/` |
| Add an API endpoint | `/agents/api/routes/` |
| Change database schema | `/supabase/migrations/` |
| Read documentation | `/docs/README.md` |
| Find old code | `/_archive/code/` |
