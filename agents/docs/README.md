# IvyLevel Backend (Agents)

**Version:** MVP 1.0.1
**Last Updated:** January 21, 2026 @ 19:15 PST
**Framework:** FastAPI + Agno + LangChain

---

## Overview

The `/agents/` directory contains the AI backend powering IvyLevel:
- Multi-agent orchestration
- Proactive coaching system
- Execution tracking
- Memory management

---

## Quick Start

```bash
cd agents

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with credentials

# Run
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [AGENTS.md](./AGENTS.md) | Agent catalog and details |
| [PROACTIVE.md](./PROACTIVE.md) | Proactive system guide |

---

## Directory Structure

```
/agents/
├── agents/              # Agent implementations
│   ├── execution_chat.py
│   ├── gameplan.py
│   ├── awards.py
│   └── ...
├── proactive/           # v10.0 Proactive system
│   ├── config.py
│   ├── scheduler.py
│   └── opportunity_matcher.py
├── api/routes/          # API routers
├── tools/               # Agent tools
├── letta/               # Future: Letta integration
├── docs/                # ← YOU ARE HERE
├── specs/               # Design specs (planning)
└── main.py              # FastAPI entry point
```

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, router registration |
| `agents/execution_chat.py` | Execution coaching agent |
| `agents/gameplan.py` | Game plan generation |
| `proactive/scheduler.py` | Background job scheduling |
| `tools/database.py` | Supabase client |

---

## Environment Variables

See `.env.example` for full list. Key variables:

```bash
# Required
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
OPENAI_API_KEY=
GOOGLE_GENERATIVE_AI_API_KEY=

# Feature Flags
PROACTIVE_ENABLED=true
LETTA_ENABLED=false
```

---

## Testing

```bash
# Run tests
pytest

# Specific test
pytest tests/test_agents.py

# With coverage
pytest --cov=agents
```

---

## Specs Directory

The `/agents/specs/` folder contains:
- **Design specs** for new features (prefixed with `SPEC_`)
- **Current state** documentation

When a spec is implemented, move it to `/_archive/docs/specs/`.
