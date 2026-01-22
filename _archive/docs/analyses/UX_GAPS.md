# UX GAPS & RECOMMENDATIONS

**Generated:** 2026-01-18
**Audit Type:** Comprehensive UI/UX and Agent Flow Analysis
**Focus:** Execution Tab and Autonomous Agent Integration

---

## Executive Summary

After a comprehensive audit of the IvyLevel platform, we identified **23 gaps** across 5 categories:
- **Critical (P0):** 4 gaps - Block core functionality
- **High (P1):** 7 gaps - Significantly impact user experience
- **Medium (P2):** 8 gaps - Nice-to-have improvements
- **Low (P3):** 4 gaps - Minor polish items

---

## 1. CRITICAL GAPS (P0)

### 1.1 No Proactive Nudge Scheduler

**Current State:**
- ExecutionChatAgent has `tool_create_nudge()` and `tool_detect_stalls()`
- Backend APIs exist: `/api/execution/stalls/{profile_id}`
- NO scheduled job to trigger these proactively

**Impact:**
- Students don't receive automatic reminders
- Stalled projects go unnoticed until student manually checks
- 2+ year coaching relationship feels passive, not proactive

**Recommendation:**
```python
# Add to agents/scheduler_jobs.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=9, minute=0)
async def daily_execution_check():
    """Run daily stall detection and nudge creation."""
    profiles = await get_active_profiles()
    for profile in profiles:
        agent = ExecutionChatAgent()
        stalls = await agent.tool_detect_stalls(profile.id, threshold_days=5)
        for stall in stalls:
            await agent.tool_create_nudge(
                profile_id=profile.id,
                message=generate_nudge_message(stall),
                nudge_type="stall_reminder",
                project_id=stall['id'],
            )
```

**Files to Modify:**
- `agents/scheduler_jobs.py` - Add execution workflow job
- `agents/main.py` - Register scheduler job

---

### 1.2 Projects Table Often Empty

**Current State:**
- ExecutionTab fetches from `projects` table
- API: `GET /api/execution/projects/{profile_id}`
- Returns empty array for most profiles

**Impact:**
- Dashboard shows "No active projects yet"
- EDS score is always 0
- Weekly focus has nothing to prioritize

**Root Cause:**
- `projects` table not populated from `game_plans.plan_data`
- No UI to create projects manually
- GamePlan agent generates plan but doesn't create project records

**Recommendation:**
1. Auto-populate projects from game plan:
```python
# After game plan generation
async def sync_gameplan_to_projects(profile_id: str, plan_data: dict):
    activities = plan_data.get("activities", [])
    for activity in activities:
        supabase.table("projects").upsert({
            "profile_id": profile_id,
            "name": activity.get("name"),
            "type": activity.get("type"),
            "status": "active",
            "source": "gameplan",
        }, on_conflict="profile_id,name").execute()
```

2. Add "Create Project" button to Execution Tab

**Files to Modify:**
- `agents/agents/gameplan.py` - Add sync after generation
- `components/tabs/ExecutionTab.tsx` - Add create button

---

### 1.3 Duplicate Message Storage

**Current State:**
- Next.js API route stores message in `conversations`
- FastAPI backend ALSO stores same message
- Results in duplicate entries

**Code Path:**
```
1. Next.js: /api/agents/execution/chat/stream/route.ts (line 55-68)
   → INSERT into conversations (user message)
   → INSERT into conversations (assistant message) - line 152-165

2. FastAPI: /api/routes/execution.py (line 62-72)
   → INSERT into conversations (user message)
   → INSERT into conversations (assistant message) - line 88-98
```

**Impact:**
- Duplicate messages in history
- Wasted database writes
- Confusing conversation history

**Recommendation:**
Remove storage from Next.js route, keep only in FastAPI:
```typescript
// app/api/agents/execution/chat/stream/route.ts
// REMOVE lines 55-68 (user message storage)
// REMOVE lines 152-165 (assistant message storage)
// Only proxy to backend
```

**Files to Modify:**
- `app/api/agents/execution/chat/stream/route.ts` - Remove Supabase inserts

---

### 1.4 No Connection Between Letta and Execution

**Current State:**
- Letta multi-agent system exists (`/api/letta/*`)
- Execution agent exists (`/api/execution/*`)
- They operate completely independently

**Impact:**
- Students might chat with wrong agent
- Context not shared between systems
- Letta Orchestrator doesn't route to ExecutionChatAgent

**Recommendation:**
1. Add Execution as a Letta specialist:
```python
# letta/agents/execution.py
class LettaExecutionAgent:
    """Letta specialist that wraps ExecutionChatAgent."""

    async def process(self, message: str, profile_id: str):
        from agents.execution_chat import ExecutionChatAgent
        agent = ExecutionChatAgent()
        return await agent.chat_sync(profile_id, message)
```

2. Configure Orchestrator to route execution queries

**Files to Modify:**
- `letta/agents/__init__.py` - Export execution agent
- `letta/agents/orchestrator.py` - Add routing logic

---

## 2. HIGH PRIORITY GAPS (P1)

### 2.1 No Project Creation UI

**Current State:**
- Projects can be created via API
- No UI button to create projects
- Students stuck with empty state

**Recommendation:**
Add "Add Project" floating action button to ExecutionTab:
```tsx
<FloatingActionButton
  onClick={() => setShowCreateModal(true)}
  icon={<Plus />}
  label="Add Project"
/>
```

**Files to Modify:**
- `components/tabs/ExecutionTab.tsx`

---

### 2.2 Weekly Plan Not Editable

**Current State:**
- Can generate weekly plan via LLM
- Cannot manually edit P0/P1/P2 items
- No drag-and-drop prioritization

**Recommendation:**
Add edit mode to WeeklyFocusCard:
- Allow drag-and-drop between P0/P1/P2
- Add/remove tasks
- Save changes to `weekly_plans` table

**Files to Modify:**
- `components/tabs/ExecutionTab.tsx` - Add WeeklyPlanEditor

---

### 2.3 No Push Notifications

**Current State:**
- Notifications stored in database
- Only visible when user opens app
- No web push or email delivery

**Recommendation:**
1. Implement Web Push API
2. Add notification preferences to profile
3. Trigger push for high-priority nudges

**Files to Modify:**
- Add `lib/notifications/push.ts`
- Add ServiceWorker for push

---

### 2.4 Chat History Not Persistent Across Sessions

**Current State:**
- Chat loads history from `conversations` table (working)
- BUT uses temp IDs during streaming
- History sometimes shows duplicates

**Root Cause:**
- Race condition between streaming and storage
- Thread ID management inconsistent

**Recommendation:**
- Use optimistic updates with proper ID reconciliation
- Add debounce to history loading

**Files to Modify:**
- `hooks/useExecutionChat.ts`

---

### 2.5 No Crisis Escalation UI

**Current State:**
- `tool_escalate_to_crisis()` exists in backend
- No UI to trigger escalation
- "Severe" stalls (14+ days) not auto-escalated

**Recommendation:**
1. Add "Escalate" button on severe stalled projects
2. Show crisis modal with reason input
3. Auto-suggest escalation for 14+ day stalls

**Files to Modify:**
- `components/tabs/ExecutionTab.tsx` - Add escalation UI

---

### 2.6 Context Not Passed to Chat When Clicking Projects

**Current State:**
- Clicking stalled project switches to chat
- Sends message: "I want to discuss my project '{title}'"
- Context is passed BUT not clearly indicated in UI

**Recommendation:**
- Show context banner at top of chat
- "Currently discussing: [Project Name]"
- Allow clearing context

**Files to Modify:**
- `components/tabs/ExecutionTab.tsx` - Add context indicator

---

### 2.7 No Handoff to Human Coach

**Current State:**
- HITL approval exists in middleware (`/agents/handoff/approve`)
- No UI for students to request human help
- No coach dashboard to see pending requests

**Recommendation:**
1. Add "Talk to Human Coach" button
2. Create coach dashboard route
3. Implement notification to coach

**Files to Modify:**
- `components/tabs/ExecutionTab.tsx`
- Add `/coach/dashboard` route

---

## 3. MEDIUM PRIORITY GAPS (P2)

### 3.1 EDS Score Not Explained

**Current State:**
- Shows number (0-100)
- Shows status (healthy/warning/critical)
- No explanation of what affects score

**Recommendation:**
Add tooltip or expandable section explaining:
- Overdue projects add +5 each
- Stalled projects add +3 each
- Thresholds: <25 healthy, <50 warning, 50+ critical

---

### 3.2 No Visual Progress Tracking

**Current State:**
- Projects have status but no visual progress
- No completion percentage
- No burndown/burnup charts

**Recommendation:**
Add progress indicators:
- Project cards show % complete
- Weekly/monthly progress chart
- Achievement streak tracking

---

### 3.3 Archetype Not Used in Execution Context

**Current State:**
- Profile has archetype (SCHOLAR, BUILDER, etc.)
- System prompt mentions it
- No archetype-specific coaching patterns

**Recommendation:**
- Adjust nudge messaging per archetype
- SCHOLAR: data-driven suggestions
- BUILDER: action-oriented steps

---

### 3.4 No Deadline Visualization

**Current State:**
- `tool_get_weekly_focus` returns deadlines
- Not displayed prominently in UI
- No calendar view

**Recommendation:**
Add deadline section to dashboard:
- Timeline view of upcoming deadlines
- Color-coded urgency
- Link to relevant projects

---

### 3.5 Suggestion Chips Static

**Current State:**
- Chat shows 3 static suggestions
- Not personalized to current context
- Same for all students

**Recommendation:**
Generate dynamic suggestions based on:
- Current stalls
- Recent conversation
- Weekly focus items

---

### 3.6 No Onboarding for Execution Tab

**Current State:**
- Students land on tab with no guidance
- Dashboard might be empty
- No tutorial or first-time experience

**Recommendation:**
Add first-time experience:
- Explain EDS score
- Suggest first action
- Quick tour of features

---

### 3.7 Message Formatting Limited

**Current State:**
- Plain text messages
- No markdown rendering
- No action buttons in responses

**Recommendation:**
- Add markdown support
- Allow inline action buttons
- Support code blocks for technical students

---

### 3.8 No Conversation Export

**Current State:**
- Chat history viewable in app
- Cannot export for reference
- No sharing with coaches

**Recommendation:**
Add export button:
- Download as PDF
- Copy to clipboard
- Share with coach

---

## 4. LOW PRIORITY GAPS (P3)

### 4.1 No Dark Mode

**Current State:**
- Light mode only (brand requirement)
- No user preference

**Recommendation:**
Keep as is - brand consistency

---

### 4.2 No Keyboard Shortcuts

**Current State:**
- Mouse/touch only
- No Cmd+Enter to send

**Recommendation:**
Add keyboard shortcuts for power users

---

### 4.3 No Typing Indicator

**Current State:**
- Loading spinner during streaming
- No "Coach is typing..." animation

**Recommendation:**
Add typing indicator with dots animation

---

### 4.4 Refresh Button Hidden During Chat

**Current State:**
- Refresh only visible in Dashboard view
- Cannot manually refresh during chat

**Recommendation:**
Add subtle refresh option in chat header

---

## 5. DEAD CODE & CLEANUP

### 5.1 Unused Components

| Component | Location | Status |
|-----------|----------|--------|
| `sessions` tab | TABS array | Disabled but defined |
| `AIChatInterface` | `/components/v10/` | Floating widget, may conflict with ExecutionTab chat |

### 5.2 Duplicate Functionality

| Feature | Location 1 | Location 2 | Action |
|---------|------------|------------|--------|
| Chat interface | ExecutionTab | AIChatInterface | Consolidate |
| Message storage | Next.js route | FastAPI route | Remove from Next.js |

---

## 6. RECOMMENDED PRIORITY ORDER

### Phase 1: Critical Fixes (1-2 weeks)
1. Add proactive nudge scheduler (P0)
2. Sync game plan to projects table (P0)
3. Remove duplicate message storage (P0)

### Phase 2: High Priority (2-3 weeks)
4. Add project creation UI (P1)
5. Add crisis escalation UI (P1)
6. Add context indicator in chat (P1)

### Phase 3: Medium Priority (3-4 weeks)
7. Add deadline visualization (P2)
8. Dynamic suggestion chips (P2)
9. Markdown support in messages (P2)

### Phase 4: Polish (Ongoing)
10. Onboarding flow (P2)
11. Keyboard shortcuts (P3)
12. Typing indicator (P3)

---

## 7. VALIDATION CHECKLIST

After implementing fixes, validate with these tests:

| Test | Expected Result |
|------|-----------------|
| New student completes assessment | Game plan creates project records |
| Student doesn't login for 5 days | Receives proactive nudge |
| Student clicks stalled project | Chat opens with context |
| Student asks for weekly plan | Plan generated with P0/P1/P2 |
| Student marks task complete | EDS score updates |
| EDS > 50 | Crisis escalation suggested |
| 14+ day stall | Auto-escalation triggered |

---

## Appendix: Files Requiring Changes

| Priority | File | Changes |
|----------|------|---------|
| P0 | `agents/scheduler_jobs.py` | Add execution workflow job |
| P0 | `agents/agents/gameplan.py` | Add project sync after generation |
| P0 | `app/api/agents/execution/chat/stream/route.ts` | Remove duplicate storage |
| P1 | `components/tabs/ExecutionTab.tsx` | Add create project, escalation, context UI |
| P1 | `hooks/useExecutionChat.ts` | Fix ID reconciliation |
| P2 | `components/tabs/ExecutionTab.tsx` | Add deadline view, onboarding |
