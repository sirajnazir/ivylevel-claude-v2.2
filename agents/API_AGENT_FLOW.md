# API → AGENT → DATABASE FLOW DOCUMENTATION

**Generated:** 2026-01-18
**Backend Version:** v10.0 (IvyQuest Agent Service)
**Frontend Version:** Next.js 13+ (App Router)

---

## Executive Summary

IvyLevel uses a multi-tier architecture:
1. **Next.js Frontend** → API routes (`/app/api/...`)
2. **FastAPI Backend** → Agent service (`http://localhost:8001`)
3. **Supabase Database** → PostgreSQL with real-time subscriptions

Total Endpoints: **103** (52 in main.py + 51 in routers)

---

## 1. FRONTEND → BACKEND FLOW

### 1.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND                      │
│                                                          │
│  ┌─────────────┐    ┌─────────────────────────────────┐ │
│  │  Components  │    │       API Routes                 │ │
│  │  (React)     │───▶│  /app/api/agents/...            │ │
│  └─────────────┘    └──────────────┬──────────────────┘ │
└─────────────────────────────────────┼────────────────────┘
                                      │
                                      ▼ HTTP/SSE
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                        │
│                                                          │
│  ┌────────────┐   ┌──────────────┐   ┌───────────────┐  │
│  │   Routers   │──▶│    Agents    │──▶│  Middleware   │  │
│  │  (FastAPI)  │   │  (LangChain) │   │   v9 Stack    │  │
│  └────────────┘   └──────────────┘   └───────────────┘  │
└─────────────────────────────────────────────────────────┘
                                      │
                                      ▼ SQL
┌─────────────────────────────────────────────────────────┐
│                     SUPABASE                             │
│  PostgreSQL + Real-time + Auth + Storage                 │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Environment Variables

```bash
# Frontend (.env.local)
NEXT_PUBLIC_AGENTS_API_URL=http://localhost:8001
AGENT_SERVICE_URL=http://localhost:8001
EXECUTION_STREAMING_ENABLED=false

# Backend (.env)
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
OPENAI_API_KEY=...
```

---

## 2. FRONTEND API ROUTES

### 2.1 Assessment Agents

| Route | Method | Backend Endpoint | Purpose |
|-------|--------|------------------|---------|
| `/api/agents/assessment/archetype` | POST | `/agents/assessment/enhance` | Detect archetype |
| `/api/agents/assessment/enhance` | POST | `/agents/assessment/enhance` | Full assessment |
| `/api/agents/assessment/narrative` | POST | `/agents/narrative/synthesize` | Generate narrative |

### 2.2 Execution Agents

| Route | Method | Backend Endpoint | Purpose |
|-------|--------|------------------|---------|
| `/api/agents/execution/chat/stream` | POST | `/api/execution/chat/stream` | Streaming chat |
| `/api/agents/execution/blockers/{profileId}` | GET | `/agents/execution/blockers/{profileId}` | Get blockers |
| `/api/agents/execution/crisis` | POST | `/agents/execution/crisis` | Crisis handling |
| `/api/agents/execution/eds/{profileId}` | GET | `/api/execution/eds/{profileId}` | EDS score |
| `/api/agents/execution/scaffold` | POST | `/agents/execution/scaffold` | Scaffold project |

### 2.3 GamePlan Agents

| Route | Method | Backend Endpoint | Purpose |
|-------|--------|------------------|---------|
| `/api/agents/gameplan/generate` | POST | `/agents/gameplan/generate` | Generate plan |
| `/api/agents/gameplan/activities/{profileId}` | GET | `/agents/gameplan/activities/{profileId}` | Get activities |
| `/api/agents/gameplan/seeds/{profileId}` | GET | `/agents/gameplan/seeds/{profileId}` | Get seeds |

### 2.4 Awards Agents

| Route | Method | Backend Endpoint | Purpose |
|-------|--------|------------------|---------|
| `/api/agents/awards/match/{profileId}` | GET | `/agents/awards/match/{profileId}` | Match awards |
| `/api/agents/awards/portfolio/{profileId}` | GET | `/agents/awards/portfolio/{profileId}` | Get portfolio |
| `/api/agents/awards/timeline/{profileId}` | GET | `/agents/awards/timeline/{profileId}` | Get timeline |

### 2.5 Opportunities Agents

| Route | Method | Backend Endpoint | Purpose |
|-------|--------|------------------|---------|
| `/api/agents/opportunities/match/{profileId}` | GET | `/agents/opportunities/match/{profileId}` | Match programs |
| `/api/agents/opportunities/alerts/{profileId}` | GET | `/agents/opportunities/alerts/{profileId}` | Get alerts |
| `/api/agents/opportunities/timeline/{profileId}` | GET | `/agents/opportunities/timeline/{profileId}` | Get timeline |

---

## 3. BACKEND ROUTERS

### 3.1 Main Router (main.py)

**52 Direct Endpoints**

#### Health & Status
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/api/react/config` | GET | ReAct config |
| `/api/debug/react-status` | GET | ReAct status |

#### Assessment Agents
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/assessment/enhance` | POST | Full assessment |
| `/agents/narrative/synthesize` | POST | Narrative synthesis |
| `/agents/narrative/{profile_id}` | GET | Get narrative |

#### Execution Agents
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/execution/scaffold` | POST | Scaffold project |
| `/agents/execution/crisis` | POST | Crisis alchemy |
| `/agents/handoff/approve` | POST | HITL approval |
| `/agents/execution/blockers/{profile_id}` | GET | Detect blockers |
| `/agents/execution/eds/{profile_id}` | GET | EDS score |

#### GamePlan Agents
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/gameplan/generate` | POST | Generate plan |
| `/agents/gameplan/orchestrate/{profile_id}` | GET | Orchestrate |
| `/agents/gameplan/activities/{profile_id}` | GET | Get activities |
| `/agents/gameplan/seeds/{profile_id}` | GET | Get seeds |

#### Awards Agents
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/awards/match/{profile_id}` | GET | Match awards |
| `/agents/awards/portfolio/{profile_id}` | GET | Get portfolio |

#### Programs Agents
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/opportunities/match/{profile_id}` | GET | Match programs |
| `/agents/opportunities/alerts/{profile_id}` | GET | Alerts |
| `/agents/programs/match/{profile_id}` | GET | Match (alias) |

#### EC Agent
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/ec/analyze/{profile_id}` | GET | Analyze EC |

#### Jenny's Intelligence Modules
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/time-audit` | POST | Time audit |
| `/agents/weekly-plan` | POST | Weekly plan |
| `/agents/awards/portfolio` | POST | Awards portfolio |
| `/agents/ncwit-strategy` | POST | NCWIT strategy |
| `/agents/opportunities/recommend` | POST | Recommend programs |
| `/agents/crisis-alchemy` | POST | Crisis alchemy |
| `/validation/jenny-voice` | POST | Voice validation |

#### Notifications
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/notifications/{profile_id}` | GET | Get notifications |
| `/notifications/mark-read` | POST | Mark read |
| `/notifications/{profile_id}/mark-all-read` | POST | Mark all read |
| `/notifications/{profile_id}/count` | GET | Unread count |

#### Workflows
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/workflows/status` | GET | Workflow status |
| `/workflows/run` | POST | Run workflow |
| `/workflows/run-all` | POST | Run all |
| `/workflows/pause` | POST | Pause |
| `/workflows/resume` | POST | Resume |
| `/workflows/runs` | GET | Run history |
| `/workflows/deadlines/{profile_id}` | GET | Deadlines |

#### Evaluation
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/evaluation/golden` | GET | List golden |
| `/evaluation/golden/{golden_id}` | GET | Get golden |
| `/evaluation/golden-stats` | GET | Stats |
| `/evaluation/run/{agent_name}` | POST | Run eval |
| `/evaluation/runs` | GET | Run history |
| `/evaluation/runs/{run_id}` | GET | Run details |
| `/evaluation/trends` | GET | Trends |
| `/evaluation/compare` | GET | Compare |

### 3.2 Execution Router (`/api/execution`) - 9 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/execution/chat/stream` | POST | SSE streaming chat |
| `/api/execution/chat` | POST | Non-streaming chat |
| `/api/execution/workflow/run` | POST | Run workflow |
| `/api/execution/weekly-focus/{profile_id}` | GET | Weekly focus |
| `/api/execution/weekly-plan/generate` | POST | Generate plan |
| `/api/execution/eds/{profile_id}` | GET | EDS score |
| `/api/execution/stalls/{profile_id}` | GET | Stalled projects |
| `/api/execution/projects/{profile_id}` | GET | Active projects |
| `/api/execution/conversations/{profile_id}` | GET | Chat history |

### 3.3 Intelligence Router (`/intelligence`) - 23 Endpoints

| Category | Endpoints | Purpose |
|----------|-----------|---------|
| Reasoning | 2 | Run/event |
| Student Intelligence | 3 | Summary/adaptations/archetype |
| Learning | 1 | Learn pattern |
| Goals | 5 | CRUD + at-risk |
| Notifications | 2 | Get/mark viewed |
| Outcomes | 1 | Record outcome |
| Assets | 4 | List/get/top/health |
| Loader | 6 | Coaches/validate/seed |

### 3.4 Letta Router (`/api/letta`) - 10 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/letta/chat/{profile_id}` | POST | Multi-agent chat |
| `/api/letta/status/{profile_id}` | GET | Status |
| `/api/letta/agents/{profile_id}` | GET | List agents |
| `/api/letta/approvals/{profile_id}` | GET | Pending approvals |
| `/api/letta/approve/{approval_id}` | POST | Approve |
| `/api/letta/reject/{approval_id}` | POST | Reject |
| `/api/letta/health` | GET | Health |
| `/api/letta/config` | GET | Config |
| `/api/letta/debug/memory/{profile_id}` | GET | Debug memory |

### 3.5 V13 Memory Router (`/v13`) - 7 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v13/health` | GET | Health |
| `/v13/memory/handoff` | POST | Create handoff |
| `/v13/memory/handoff/{profile_id}/{to_agent}` | GET | Get handoff |
| `/v13/knowledge/search` | GET | Search knowledge |
| `/v13/profile/{profile_id}/evolution` | GET | Profile evolution |
| `/v13/interactions/{profile_id}/recall` | GET | Recall interactions |
| `/v13/interactions/{profile_id}/recent` | GET | Recent interactions |

---

## 4. AGENT CLASSES

### 4.1 Primary Agents

| Agent | File | Mixin | Processing |
|-------|------|-------|------------|
| AssessmentAgent | `agents/assessment.py` | MiddlewareIntegrationMixin | Direct |
| NarrativeSynthesisAgent | `agents/narrative_synthesis.py` | MiddlewareIntegrationMixin | Direct |
| GamePlanAgent | `agents/gameplan.py` | MiddlewareIntegrationMixin | ReAct optional |
| ExecutionAgent | `agents/execution.py` | BaseAgent + Mixin | Direct |
| ExecutionChatAgent | `agents/execution_chat.py` | MiddlewareIntegrationMixin | Streaming |
| AwardsAgent | `agents/awards.py` | MiddlewareIntegrationMixin | ReAct optional |
| ProgramsAgent | `agents/programs.py` | MiddlewareIntegrationMixin | ReAct optional |
| ExtracurricularsAgent | `agents/extracurriculars.py` | MiddlewareIntegrationMixin | ReAct optional |
| OpportunityAgent | `agents/opportunity.py` | Alias for ProgramsAgent | ReAct optional |

### 4.2 Letta Agents

| Agent | File | Role |
|-------|------|------|
| LettaOrchestratorAgent | `letta/agents/orchestrator.py` | Router |
| LettaExecutionAgent | `letta/agents/execution.py` | Specialist |
| LettaAssessmentAgent | `letta/agents/assessment.py` | Specialist |
| LettaAwardsAgent | `letta/agents/awards.py` | Specialist |
| LettaEssayAgent | `letta/agents/essay.py` | Specialist |
| LettaGamePlanAgent | `letta/agents/gameplan.py` | Specialist |

### 4.3 ReAct Wrapper

```python
# Optional wrapper for quality improvement
from agents.core.react_wrapper import ReActWrapper

# Enable via feature flag
if FEATURE_FLAGS.get("enable_react"):
    agent = ReActWrapper(original_agent, max_cycles=3, min_quality=0.70)
```

---

## 5. MIDDLEWARE STACK V9

### 5.1 50 Patterns Across 9 Domains

| Domain | Patterns | Purpose |
|--------|----------|---------|
| **Tools** | Registry, schema, calling, chaining, parallel | Tool orchestration |
| **Context** | System, session, engineering | Request context |
| **Memory** | Semantic, consolidation, extraction, episodic, long-term | Memory tiers |
| **Quality** | Coherence, reflection, scoring, LLM judge, producer-critic | QA |
| **Recovery** | Retry, degradation, pivot | Error handling |
| **Learning** | Feedback, strategy, adaptation, patterns, preferences | Learning |
| **Optimization** | Compression | Response optimization |
| **Shadow** | Manager | HITL shadow mode |
| **HITL** | Atomic operations | Approval workflow |
| **Observability** | Monitoring, cost, logging, traces, audit | Observability |
| **Reasoning** | Planning, self-correction | Deliberative reasoning |
| **Safety** | Moderation, guardrails, PII | Data protection |
| **Approval** | Workflow | Approval management |

### 5.2 Usage Pattern

```python
class MyAgent(MiddlewareIntegrationMixin):
    async def process(self, profile_id: str, **kwargs):
        async with self.with_middleware_context(profile_id, session_id, "my_agent") as ctx:
            # ctx.student - student profile
            # ctx.temporal - deadline info
            # ctx.session - conversation state
            # ctx.trace - reasoning trace

            result = await self._do_work(ctx)
            return self.middleware_finalize(result, output_type="my_agent")
```

---

## 6. DATABASE FLOW

### 6.1 Read Patterns by Agent

| Agent | Tables Read | Key Columns |
|-------|-------------|-------------|
| AssessmentAgent | `profiles` | `*` (all columns) |
| NarrativeSynthesisAgent | `profiles` | `narrative_*`, `archetype`, `pillars` |
| GamePlanAgent | `profiles`, `game_plans`, `activities` | Profile + plan data |
| ExecutionChatAgent | `profiles`, `projects`, `weekly_plans`, `conversations`, `crises` | Execution context |
| AwardsAgent | `profiles`, `opportunities` | Profile + awards |
| ProgramsAgent | `profiles`, `opportunities` | Profile + programs |

### 6.2 Write Patterns by Agent

| Agent | Tables Written | Trigger |
|-------|----------------|---------|
| AssessmentAgent | `profiles` | Assessment complete |
| NarrativeSynthesisAgent | `profiles` | Narrative synthesis |
| GamePlanAgent | `game_plans` | Plan generation |
| ExecutionChatAgent | `conversations`, `weekly_plans`, `notifications`, `crises`, `agent_memories` | Chat + actions |
| AwardsAgent | `agent_memories` | Insights |
| WorkflowRunner | `workflow_runs` | Workflow execution |

### 6.3 Tables Summary

| Table | Reads | Writes | Real-time |
|-------|-------|--------|-----------|
| `profiles` | All agents | Assessment, Narrative | No |
| `game_plans` | GamePlan, Execution | GamePlan | No |
| `projects` | Execution | Execution | No |
| `project_steps` | Execution | Execution | No |
| `weekly_plans` | Execution | Execution | No |
| `conversations` | Execution | Execution | Possible |
| `notifications` | All | Execution | Yes |
| `crises` | Execution | Execution | No |
| `opportunities` | Awards, Programs | None | No |
| `agent_memories` | All | All | No |
| `letta_agent_registry` | Letta | Letta | No |
| `letta_memory_snapshots` | Letta | Letta | No |
| `letta_approval_queue` | Letta | Letta | No |

---

## 7. REQUEST LIFECYCLE

```
1. FRONTEND REQUEST
   ┌─────────────────────────────────────┐
   │ User action (button click, form)    │
   │ → useExecutionChat.sendMessage()    │
   │ → fetch('/api/agents/...')          │
   └─────────────────────────────────────┘
                    │
                    ▼
2. NEXT.JS API ROUTE
   ┌─────────────────────────────────────┐
   │ Validate request                     │
   │ → Optional: store in Supabase       │
   │ → Proxy to FastAPI backend          │
   └─────────────────────────────────────┘
                    │
                    ▼
3. FASTAPI ROUTER
   ┌─────────────────────────────────────┐
   │ Parse ProfileInput/request          │
   │ → Load agent (singleton/per-request)│
   │ → Optional: ReAct wrapper           │
   └─────────────────────────────────────┘
                    │
                    ▼
4. MIDDLEWARE CONTEXT
   ┌─────────────────────────────────────┐
   │ with_middleware_context():          │
   │ → Load student profile              │
   │ → Load temporal context             │
   │ → Initialize trace                  │
   │ → Apply safety guardrails           │
   └─────────────────────────────────────┘
                    │
                    ▼
5. AGENT PROCESSING
   ┌─────────────────────────────────────┐
   │ Build context                       │
   │ → Construct system prompt           │
   │ → Query LLM (streaming)             │
   │ → Extract insights                  │
   └─────────────────────────────────────┘
                    │
                    ▼
6. FINALIZATION
   ┌─────────────────────────────────────┐
   │ middleware_finalize():              │
   │ → Quality scoring                   │
   │ → Audit trail                       │
   │ → Cost tracking                     │
   └─────────────────────────────────────┘
                    │
                    ▼
7. RESPONSE
   ┌─────────────────────────────────────┐
   │ SSE: data: {...} → data: [DONE]    │
   │ JSON: {"success": true, ...}        │
   │ → Store in Supabase (if needed)     │
   └─────────────────────────────────────┘
```

---

## 8. FEATURE FLAGS

### 8.1 ReAct Configuration

```python
FEATURE_FLAGS = {
    "enable_react": True,
    "react_max_cycles": 3,
    "react_min_confidence": 0.70,
    "react_enable_for_agents": ["EC", "GamePlan", "Awards", "Programs"],
    "react_ab_test_enabled": False,
    "react_ab_test_percentage": 0.10,
    "react_verbose_logging": False,
    "enable_guardrails": True,
    "enable_voice_validation": True,
    "enable_golden_benchmark": True,
}
```

### 8.2 Letta Configuration

```python
LETTA_CONFIG = {
    "enabled": os.getenv("LETTA_ENABLED", "false") == "true",
    "api_key": os.getenv("LETTA_API_KEY"),
    "base_url": os.getenv("LETTA_BASE_URL", "https://api.letta.com"),
}
```

---

## 9. TESTING ENDPOINTS

### Quick Health Check
```bash
curl http://localhost:8001/health
```

### Test Execution Chat
```bash
curl -X POST http://localhost:8001/api/execution/chat \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "YOUR_PROFILE_ID", "message": "What should I focus on?"}'
```

### Test EDS Score
```bash
curl http://localhost:8001/api/execution/eds/YOUR_PROFILE_ID
```

### Test Letta Chat
```bash
curl -X POST http://localhost:8001/api/letta/chat/YOUR_PROFILE_ID \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me with my activities"}'
```

---

## Appendix: File Index

| Category | Path | Description |
|----------|------|-------------|
| Main Entry | `/agents/main.py` | FastAPI app + 52 endpoints |
| Routers | `/agents/routers/` | Intelligence router |
| Routers | `/agents/api/routes/` | Execution router |
| Routers | `/agents/letta/router.py` | Letta router |
| Agents | `/agents/agents/*.py` | Primary agents |
| Agents | `/agents/letta/agents/` | Letta specialists |
| Middleware | `/agents/middleware/` | V9 stack (50 patterns) |
| Tools | `/agents/tools/` | Database, LLM tools |
| Config | `/agents/config.py` | Feature flags |
| Frontend Routes | `/app/api/agents/` | Next.js API routes |
| Frontend Hooks | `/hooks/` | useExecutionChat, etc. |
| Frontend Components | `/components/tabs/` | Tab components |
