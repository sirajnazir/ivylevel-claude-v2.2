# EXECUTION AGENT AUDIT

**Generated:** 2026-01-18
**Version:** v5.3
**Status:** Production-Ready with Known Gaps

---

## Executive Summary

The Execution Agent (v5.3) is a chat-enabled coaching buddy integrated with the IvyLevel dashboard. It provides real-time streaming chat, execution tracking, and proactive nudging capabilities. The agent is fully functional but relies on tables (`projects`, `weekly_plans`) that may be sparsely populated.

---

## 1. Component Architecture

### 1.1 Frontend Components

```
ExecutionTab (components/tabs/ExecutionTab.tsx) - v5.3
├── Header
│   ├── View Toggle (Dashboard / Chat)
│   └── Refresh Button
│
├── DashboardView (Default)
│   ├── EDSCard (Execution Debt Score)
│   │   ├── Score display (0-100)
│   │   ├── Status indicator (healthy/warning/critical)
│   │   └── Stats: active, overdue, stalled projects
│   │
│   ├── QuickActionsCard (4 buttons)
│   │   ├── "Chat with Coach" → switches to chat view
│   │   ├── "Review Focus" → P0 priorities
│   │   ├── "Handle Stalls" → stalled projects
│   │   └── "Generate Plan" → weekly plan
│   │
│   ├── WeeklyFocusCard (P0 Tasks)
│   │   └── Top 3 focus items with numbered badges
│   │
│   ├── StalledProjectsCard
│   │   └── Projects with severity indicators
│   │
│   └── ActiveProjectsCard
│       └── Grid of active projects
│
└── ChatView
    ├── MessageHistory (scrollable)
    │   └── ChatBubble components
    ├── SuggestionChips (when empty)
    └── InputArea (input + send button)
```

### 1.2 Backend Components

```
ExecutionChatAgent (agents/execution_chat.py) - v5.3
├── MiddlewareIntegrationMixin (40 patterns)
│
├── Properties
│   ├── supabase (lazy-loaded)
│   └── llm (ChatOpenAI, streaming)
│
├── Chat Interface
│   ├── chat() - Async generator (streaming)
│   └── chat_sync() - Non-streaming with middleware
│
├── 13 Tools
│   ├── Weekly Planning (2)
│   ├── Execution Tracking (3)
│   ├── Stall Detection (2)
│   ├── Nudging (2)
│   └── Memory (4)
│
└── Helper Methods
    ├── _build_context()
    ├── _build_system_prompt()
    ├── _extract_and_store_insights()
    └── _parse_json_response()
```

---

## 2. API Endpoints

### 2.1 Frontend API Routes (Next.js)

| Endpoint | Method | File | Purpose |
|----------|--------|------|---------|
| `/api/agents/execution/chat/stream` | POST | `app/api/agents/execution/chat/stream/route.ts` | SSE streaming chat |

### 2.2 Backend API Routes (FastAPI)

| Endpoint | Method | Purpose | Agent Method |
|----------|--------|---------|--------------|
| `/api/execution/chat/stream` | POST | SSE streaming | `ExecutionChatAgent.chat()` |
| `/api/execution/chat` | POST | Non-streaming | `ExecutionChatAgent.chat()` |
| `/api/execution/workflow/run` | POST | Trigger workflow | `run_execution_workflow()` |
| `/api/execution/weekly-focus/{profile_id}` | GET | Get P0 items | `tool_get_weekly_focus()` |
| `/api/execution/weekly-plan/generate` | POST | Generate plan | `tool_generate_weekly_plan()` |
| `/api/execution/eds/{profile_id}` | GET | Get EDS score | `tool_calculate_eds()` |
| `/api/execution/stalls/{profile_id}` | GET | Get stalled projects | `tool_detect_stalls()` |
| `/api/execution/projects/{profile_id}` | GET | Get active projects | `tool_get_active_projects()` |
| `/api/execution/conversations/{profile_id}` | GET | Get chat history | `tool_get_conversation_history()` |

---

## 3. Database Patterns

### 3.1 Tables READ

| Table | Columns Used | Purpose |
|-------|--------------|---------|
| `profiles` | `id`, `first_name`, `last_name`, `grade`, `archetype` | Context building |
| `projects` | `id`, `profile_id`, `name`, `status`, `last_activity_at`, `target_end_date` | Execution tracking |
| `project_steps` | `id`, `project_id`, `status`, `completed_at` | Step tracking |
| `weekly_plans` | `profile_id`, `week_start`, `week_end`, `p0_tasks`, `p1_tasks`, `p2_tasks` | Weekly focus |
| `conversations` | `profile_id`, `agent_type`, `role`, `content`, `created_at` | Chat history |
| `crises` | `id`, `project_id`, `status` | Crisis context |
| `agent_memories` | `profile_id`, `content`, `observation_type` | Long-term memory |

### 3.2 Tables WRITTEN

| Table | Trigger | Columns Written |
|-------|---------|-----------------|
| `conversations` | Every chat message | `profile_id`, `agent_type`, `role`, `content`, `context_type`, `context_id`, `is_proactive`, `thread_id`, `created_at` |
| `weekly_plans` | Generate plan action | `profile_id`, `week_start`, `week_end`, `p0_tasks`, `p1_tasks`, `p2_tasks`, `generated_at`, `generated_by` |
| `notifications` | Nudge creation | `profile_id`, `type`, `title`, `message`, `metadata`, `read`, `created_at` |
| `crises` | Escalation | `profile_id`, `project_id`, `type`, `title`, `description`, `urgency`, `status`, `detected_by` |
| `projects` | Status update | `status`, `actual_end_date` |
| `project_steps` | Step completion | `status`, `completed_at` |
| `agent_memories` | Insight storage | `profile_id`, `agent_id`, `observation_type`, `content`, `confidence` |

---

## 4. Current Capabilities

### 4.1 WORKING ✅

| Capability | Status | Notes |
|------------|--------|-------|
| Dashboard rendering | ✅ Active | Loads EDS, focus, projects |
| Chat interface | ✅ Active | Real-time SSE streaming |
| Conversation persistence | ✅ Active | Stored in `conversations` table |
| EDS calculation | ✅ Active | Based on overdue + stalled projects |
| Stall detection | ✅ Active | Threshold-based (5/10/14 days) |
| Weekly plan generation | ✅ Active | LLM-powered P0/P1/P2 |
| Context-aware chat | ✅ Active | Project/crisis/plan context |
| Message history | ✅ Active | Auto-loads on mount |

### 4.2 PARTIAL ⚠️

| Capability | Status | Notes |
|------------|--------|-------|
| Proactive nudging | ⚠️ Backend only | No scheduled trigger |
| Crisis escalation | ⚠️ Backend only | Manual trigger only |
| Project updates | ⚠️ UI incomplete | API exists, no UI button |
| Weekly plan display | ⚠️ Read-only | Can view but not edit |

### 4.3 NOT IMPLEMENTED ❌

| Capability | Status | Notes |
|------------|--------|-------|
| Scheduled nudge jobs | ❌ Missing | No APScheduler job defined |
| Push notifications | ❌ Missing | No web push integration |
| Human coach handoff | ❌ Missing | HITL approval exists but not exposed |
| Voice input | ❌ Missing | Text only |
| File attachments | ❌ Missing | No upload support |

---

## 5. Entry Points

### 5.1 User-Initiated

```
1. Dashboard Tab Click
   /dashboard?tab=execution
   ↓
   ExecutionTab mounts
   ↓
   Dashboard view loads (default)
   ↓
   Parallel API calls:
   - GET /api/execution/eds/{profile_id}
   - GET /api/execution/weekly-focus/{profile_id}
   - GET /api/execution/stalls/{profile_id}
   - GET /api/execution/projects/{profile_id}

2. Chat View Toggle
   User clicks "Chat" or "Chat with Coach"
   ↓
   ChatView renders
   ↓
   useExecutionChat hook initializes
   ↓
   Loads history from `conversations` table

3. Send Message
   User types → Enter/Click Send
   ↓
   POST /api/agents/execution/chat/stream
   ↓
   SSE stream back
   ↓
   Real-time message display
   ↓
   Both messages saved to `conversations`

4. Project Click
   User clicks stalled/active project
   ↓
   Switches to Chat view
   ↓
   Auto-sends context message:
   "I want to discuss my project '{title}'"
   with context_type='project', context_id=project.id
```

### 5.2 System-Initiated (Not Yet Active)

```
1. Stall Detection Workflow (DORMANT)
   Cron job (not configured)
   ↓
   Scan projects > 5 days inactive
   ↓
   Create nudge notification
   ↓
   Store proactive message in conversations

2. EDS Threshold Alert (DORMANT)
   Cron job (not configured)
   ↓
   Calculate EDS for all profiles
   ↓
   If EDS > 25: warning nudge
   ↓
   If EDS > 50: crisis escalation
```

---

## 6. Message Flow Diagram

```
┌─────────────────┐
│   User Types    │
│    Message      │
└────────┬────────┘
         ▼
┌─────────────────────┐
│ useExecutionChat.ts │  (React Hook)
│   sendMessage()     │
└────────┬────────────┘
         ▼
┌──────────────────────────────────────┐
│ Next.js API Route                    │
│ /api/agents/execution/chat/stream    │
│ - Store user message in Supabase     │
│ - Proxy to backend                   │
└────────┬─────────────────────────────┘
         ▼
┌──────────────────────────────────────┐
│ FastAPI Backend                      │
│ /api/execution/chat/stream           │
│ - Store user message (again)         │
│ - Call ExecutionChatAgent.chat()     │
└────────┬─────────────────────────────┘
         ▼
┌──────────────────────────────────────┐
│ ExecutionChatAgent.chat()            │
│ 1. Build context (profile, projects) │
│ 2. Build system prompt               │
│ 3. Get conversation history          │
│ 4. Stream from LLM (ChatOpenAI)      │
│ 5. Yield chunks                      │
└────────┬─────────────────────────────┘
         ▼
┌─────────────────────────────────────┐
│ SSE Response (text/event-stream)    │
│ data: {"content":"Hi ",...}         │
│ data: {"content":"there!",...}      │
│ data: {"done":true,...}             │
│ data: [DONE]                        │
└────────┬────────────────────────────┘
         ▼
┌──────────────────────────────────────┐
│ Store assistant message in Supabase  │
│ conversations table                  │
└────────┬─────────────────────────────┘
         ▼
┌─────────────────────────────────────┐
│ ChatBubble renders incrementally    │
│ Real-time typing effect             │
└─────────────────────────────────────┘
```

---

## 7. System Prompt Analysis

The system prompt (built in `_build_system_prompt()`) includes:

```
1. Role Definition
   - "Execution Agent - supportive, proactive coaching buddy"
   - 2+ year relationship framing

2. Context Injection
   - Student name, grade, archetype
   - Weekly focus (P0 items)
   - EDS score and status
   - Stalled projects list

3. Interaction Guidelines
   - Priority questions → weekly focus
   - Stuck feeling → stalled projects
   - Project discussion → project details
   - Progress → celebrate

4. Tone Guidelines
   - Warm and encouraging
   - Specific and actionable
   - Brief for simple, detailed when needed
```

---

## 8. Tool Inventory (13 Tools)

### Weekly Planning
| Tool | Purpose | Tables |
|------|---------|--------|
| `tool_get_weekly_focus` | Get top 3 P0 items | `weekly_plans` |
| `tool_generate_weekly_plan` | Create new weekly plan | `weekly_plans`, `projects` |

### Execution Tracking
| Tool | Purpose | Tables |
|------|---------|--------|
| `tool_get_active_projects` | List active projects | `projects` |
| `tool_get_project_details` | Get single project | `projects` |
| `tool_update_project_status` | Update status | `projects`, `project_steps` |

### Stall Detection
| Tool | Purpose | Tables |
|------|---------|--------|
| `tool_detect_stalls` | Find stalled projects | `projects` |
| `tool_calculate_eds` | Calculate debt score | `projects` |

### Nudging & Escalation
| Tool | Purpose | Tables |
|------|---------|--------|
| `tool_create_nudge` | Create notification | `notifications`, `conversations` |
| `tool_escalate_to_crisis` | Create crisis | `crises`, `projects` |

### Memory
| Tool | Purpose | Tables |
|------|---------|--------|
| `tool_search_memory` | Search past insights | `agent_memories` |
| `tool_store_insight` | Store new insight | `agent_memories` |
| `tool_get_conversation_history` | Get chat history | `conversations` |

---

## 9. Known Gaps & Recommendations

### 9.1 Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| No scheduled nudge workflow | High | Students don't get proactive reminders |
| Projects table may be empty | High | Dashboard shows empty state |
| Duplicate message storage | Medium | Both Next.js and FastAPI write to `conversations` |
| No project creation UI | Medium | Students can't add projects from Execution tab |
| No weekly plan editing | Low | Can only generate, not modify |

### 9.2 Recommendations

1. **Add APScheduler Jobs** for execution workflow:
   ```python
   @scheduler.scheduled_job('cron', hour=9)
   async def execution_daily_check():
       # Scan all profiles
       # Detect stalls
       # Create nudges
   ```

2. **Deduplicate Message Storage**: Store only in FastAPI backend, not Next.js frontend.

3. **Add Project Creation Button**: Allow students to add projects from dashboard.

4. **Connect to GamePlan**: Auto-populate `projects` table from `game_plans.plan_data`.

5. **Enable Push Notifications**: Integrate web push for proactive nudges.

---

## 10. Testing Checklist

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| Load Execution tab | Dashboard renders with EDS card | ✅ |
| Switch to Chat view | Chat interface loads | ✅ |
| Send message | SSE streaming response | ✅ |
| View message history | Previous messages load | ✅ |
| Click stalled project | Context message sent | ✅ |
| Generate weekly plan | P0/P1/P2 created | ✅ |
| EDS calculation | Score returns | ✅ |
| Clear chat | Messages cleared | ✅ |

---

## Appendix: File Locations

| Component | Path |
|-----------|------|
| ExecutionTab Component | `/components/tabs/ExecutionTab.tsx` |
| useExecutionChat Hook | `/hooks/useExecutionChat.ts` |
| Frontend API Route | `/app/api/agents/execution/chat/stream/route.ts` |
| Backend Router | `/agents/api/routes/execution.py` |
| ExecutionChatAgent | `/agents/agents/execution_chat.py` |
| Middleware Mixin | `/agents/agents/mixins.py` |
