# STUDENT JOURNEY MAP

**Generated:** 2026-01-18
**Platform:** IvyLevel College Coaching
**Focus:** Complete student experience from signup to ongoing coaching

---

## Executive Summary

The IvyLevel student journey spans from initial assessment through 2+ years of coaching. This document maps every touchpoint, UI component, API call, and agent interaction a student experiences.

---

## 1. ROUTE INVENTORY

### 1.1 All Student-Accessible Routes

| Route | Access | Purpose | Key Components |
|-------|--------|---------|----------------|
| `/` | Public | Landing page | Hero, features, CTA |
| `/auth/login` | Public | Authentication | Login form |
| `/quest` | Authenticated | Assessment intro | QuestOrchestrator |
| `/quest/[frameId]` | Authenticated | Assessment frames | Frame components |
| `/assessment` | Authenticated | Assessment page | Assessment flow |
| `/dashboard` | Authenticated | Main hub (tabbed) | Tab navigation |
| `/dashboard?tab=assessment` | Authenticated | Assessment results | IvyScore, pillars |
| `/dashboard?tab=gameplan` | Authenticated | Strategic plan | GamePlanFull |
| `/dashboard?tab=preparation` | Authenticated | Weekly tasks | PreparationTab |
| `/dashboard?tab=growth` | Authenticated | Achievements | GrowthTab |
| `/dashboard?tab=multiagents` | Authenticated | Agent status | MultiAgentTab |
| `/dashboard?tab=execution` | Authenticated | **Execution Hub** | ExecutionTab |
| `/coach` | Authenticated | Coach interface | CoachConnect |
| `/results` | Authenticated | Assessment results | ResultsDisplay |
| `/admin` | Admin only | Admin panel | Admin controls |

### 1.2 Dashboard Tab Configuration

```typescript
// From lib/constants/design.ts
export const TABS = [
  { id: 'assessment', label: 'Assessment', enabled: true },
  { id: 'gameplan', label: 'Game Plan', enabled: true },
  { id: 'preparation', label: 'Preparation', enabled: true },
  { id: 'growth', label: 'Growth', enabled: true },
  { id: 'sessions', label: 'Sessions', enabled: false },  // DISABLED
  { id: 'multiagents', label: 'Multi-Agents', enabled: true },
  { id: 'execution', label: 'Execution', enabled: true },
];
```

---

## 2. NEW STUDENT FLOW

### 2.1 Signup → Assessment

```
┌─────────────────────────────────────────────────────────────────┐
│                        STEP 1: SIGNUP                            │
├─────────────────────────────────────────────────────────────────┤
│ Route: /auth/login (or Supabase auth)                           │
│ Component: Login form                                            │
│ Action: Create account / Sign in                                 │
│ Database: Creates row in `profiles` with:                        │
│   - id (UUID)                                                    │
│   - email                                                        │
│   - first_name, last_name                                        │
│   - onboarding_completed: false                                  │
│   - onboarding_step: 0                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     STEP 2: QUEST INTRO                          │
├─────────────────────────────────────────────────────────────────┤
│ Route: /quest                                                    │
│ Component: QuestOrchestrator                                     │
│ Display: Welcome message, "Begin Quest" button                   │
│ Action: Start assessment flow                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 3: ASSESSMENT FRAMES                       │
├─────────────────────────────────────────────────────────────────┤
│ Route: /quest/[frameId] (frames 1-6)                             │
│                                                                  │
│ FRAME 1: Basic Info                                              │
│   - Grade, school type                                           │
│   - Stored: profiles.grade, profiles.school_type                 │
│                                                                  │
│ FRAME 2: Academic Profile                                        │
│   - GPA, test scores, course rigor                               │
│   - Stored: profiles.gpa, profiles.sat_score, profiles.act_score │
│                                                                  │
│ FRAME 3: Activities & Interests                                  │
│   - Extracurriculars, passions                                   │
│   - Stored: activities table (linked to profile)                 │
│                                                                  │
│ FRAME 4: Goals & Aspirations                                     │
│   - Target schools, intended major                               │
│   - Stored: profiles.target_schools, profiles.intended_major     │
│                                                                  │
│ FRAME 5: Self-Reflection                                         │
│   - Open-ended responses about identity                          │
│   - Used for narrative DNA extraction                            │
│                                                                  │
│ FRAME 6: Complete & Submit                                       │
│   - Review all answers                                           │
│   - Trigger assessment processing                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STEP 4: ASSESSMENT PROCESSING                    │
├─────────────────────────────────────────────────────────────────┤
│ Trigger: Frame 6 submit                                          │
│ Agents Called:                                                   │
│   1. AssessmentAgent.enhance()                                   │
│      → Detect archetype (SCHOLAR, BUILDER, etc.)                 │
│      → Calculate IvyScore                                        │
│      → Calculate CRI score                                       │
│      → Generate hidden probabilities                             │
│                                                                  │
│   2. NarrativeSynthesisAgent.synthesize()                        │
│      → Generate narrative_dna                                    │
│      → Generate brand_statement                                  │
│      → Extract narrative_themes                                  │
│      → Create first_principle                                    │
│                                                                  │
│ Database Updates:                                                │
│   profiles.archetype = "SCHOLAR"                                 │
│   profiles.ivy_score = 79                                        │
│   profiles.cri_score = 85                                        │
│   profiles.narrative_dna = "Growing up as..."                    │
│   profiles.narrative_brand_statement = "A South Asian..."        │
│   profiles.narrative_themes = ["Community", "Leadership", ...]   │
│   profiles.onboarding_completed = true                           │
│   profiles.assessment_completed_at = NOW()                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STEP 5: DASHBOARD ACCESS                       │
├─────────────────────────────────────────────────────────────────┤
│ Route: /dashboard (redirected after assessment)                  │
│ Default Tab: assessment (shows results)                          │
│                                                                  │
│ Components Loaded:                                               │
│   - DashboardLayout                                              │
│   - TabHeader (navigation)                                       │
│   - AssessmentTab (default)                                      │
│     - IvyScoreCard                                               │
│     - PillarDisplay                                              │
│     - ArchetypeCard                                              │
│     - NarrativeDNA display                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 First Dashboard Experience

```
┌─────────────────────────────────────────────────────────────────┐
│                     DASHBOARD LOAD SEQUENCE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 1. Page Mount (/dashboard)                                       │
│    ├─ useSessionStore() → get profile_id from auth               │
│    ├─ useUserData() → fetch profile from Supabase                │
│    └─ useGamePlan() → fetch game_plans for profile               │
│                                                                  │
│ 2. Tab Content Render                                            │
│    ├─ Assessment Tab (default)                                   │
│    │   ├─ IvyScoreCard with score animation                      │
│    │   ├─ Pillar breakdown (4 pillars)                           │
│    │   ├─ Factor details (12+ factors)                           │
│    │   └─ Narrative DNA summary                                  │
│    │                                                             │
│    ├─ GamePlan Tab                                               │
│    │   ├─ Fetch: GET /agents/gameplan/activities/{profile_id}    │
│    │   ├─ Display: Target schools, EC recommendations            │
│    │   └─ Timeline view of phases                                │
│    │                                                             │
│    ├─ Execution Tab                                              │
│    │   ├─ Fetch (parallel):                                      │
│    │   │   ├─ GET /api/execution/eds/{profile_id}                │
│    │   │   ├─ GET /api/execution/weekly-focus/{profile_id}       │
│    │   │   ├─ GET /api/execution/stalls/{profile_id}             │
│    │   │   └─ GET /api/execution/projects/{profile_id}           │
│    │   └─ Display: Dashboard or Chat view                        │
│    │                                                             │
│    └─ Multi-Agents Tab                                           │
│        ├─ Show all agent statuses                                │
│        └─ Display orchestration flow                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. EXECUTION TAB JOURNEY

### 3.1 Dashboard View Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION TAB - DASHBOARD                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐  ┌────────────────────────────────┐   │
│  │     EDS Score        │  │         Quick Actions          │   │
│  │  ┌───────────────┐   │  │  ┌──────────┐ ┌──────────┐    │   │
│  │  │      25       │   │  │  │  Chat    │ │  Focus   │    │   │
│  │  │   WARNING     │   │  │  │  Coach   │ │  Review  │    │   │
│  │  └───────────────┘   │  │  └──────────┘ └──────────┘    │   │
│  │  Active: 5           │  │  ┌──────────┐ ┌──────────┐    │   │
│  │  Overdue: 2          │  │  │  Handle  │ │ Generate │    │   │
│  │  Stalled: 1          │  │  │  Stalls  │ │   Plan   │    │   │
│  └──────────────────────┘  │  └──────────┘ └──────────┘    │   │
│                            └────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────┐  ┌────────────────────────────────┐   │
│  │   Weekly Focus (P0)  │  │      Stalled Projects          │   │
│  │  1. Submit NCWIT app │  │  ⚫ CS Project (12 days)       │   │
│  │  2. Finish essay     │  │     Severity: SEVERE           │   │
│  │  3. Update activities│  │                                │   │
│  └──────────────────────┘  └────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Active Projects                        │   │
│  │  [CS Project] [NCWIT App] [Essay Draft] [Club Leadership]│   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Chat View Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION TAB - CHAT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │           ⚡ Execution Coach                              │   │
│  │                                                          │   │
│  │   I'm your execution buddy! Ask me about your            │   │
│  │   priorities, stalled projects, or anything you          │   │
│  │   need help getting done.                                │   │
│  │                                                          │   │
│  │   ┌─────────────────────────────────────────────────┐    │   │
│  │   │ What should I focus on this week?               │    │   │
│  │   └─────────────────────────────────────────────────┘    │   │
│  │   ┌─────────────────────────────────────────────────┐    │   │
│  │   │ Help me with a stalled project                  │    │   │
│  │   └─────────────────────────────────────────────────┘    │   │
│  │   ┌─────────────────────────────────────────────────┐    │   │
│  │   │ Generate my weekly plan                         │    │   │
│  │   └─────────────────────────────────────────────────┘    │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Ask your execution coach anything...            [Send] │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Chat Interaction Sequence

```
USER SENDS MESSAGE
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ 1. Input captured in ExecutionTab                          │
│    → setInput(message)                                     │
│    → handleSend() called                                   │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ 2. useExecutionChat.sendMessage()                          │
│    → Add user message to local state                       │
│    → Add placeholder assistant message                     │
│    → POST /api/agents/execution/chat/stream                │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ 3. Next.js API Route processes                             │
│    → Store user message in conversations table             │
│    → Proxy to FastAPI backend                              │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ 4. FastAPI /api/execution/chat/stream                      │
│    → ExecutionChatAgent.chat()                             │
│    → Build context (profile, projects, weekly_plan)        │
│    → Construct system prompt with student data             │
│    → Stream response from ChatOpenAI                       │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ 5. SSE Response streams back                               │
│    data: {"content": "Great ", "done": false}              │
│    data: {"content": "question!", "done": false}           │
│    data: {"content": " Let me...", "done": false}          │
│    ...                                                     │
│    data: {"done": true, "conversation_id": "..."}          │
│    data: [DONE]                                            │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ 6. Frontend updates in real-time                           │
│    → ChatBubble content updates with each chunk            │
│    → Typing indicator shown during streaming               │
│    → Final message rendered when done                      │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ 7. Persistence                                             │
│    → Assistant message saved to conversations table        │
│    → Thread ID tracked for conversation continuity         │
│    → Insights extracted and stored in agent_memories       │
└───────────────────────────────────────────────────────────┘
```

---

## 4. ONGOING COACHING FLOW

### 4.1 Returning Student (Day 2+)

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETURNING STUDENT FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 1. LOGIN                                                         │
│    Route: /auth/login                                            │
│    Action: Authenticate via Supabase                             │
│    Redirect: /dashboard                                          │
│                                                                  │
│ 2. DASHBOARD LOADS                                               │
│    Default Tab: Last viewed (stored in localStorage)             │
│    Data Fetched:                                                 │
│      - Profile (cached in Zustand store)                         │
│      - Notifications (badge count)                               │
│      - Active game plan                                          │
│                                                                  │
│ 3. NOTIFICATION CHECK                                            │
│    Component: NotificationBell (top nav)                         │
│    Fetch: GET /notifications/{profile_id}/count                  │
│    Display: Unread count badge                                   │
│                                                                  │
│ 4. EXECUTION TAB (if visited)                                    │
│    Loads:                                                        │
│      - Updated EDS score                                         │
│      - Any new stalled projects                                  │
│      - Updated weekly focus                                      │
│    Conversations: Loads history (last 50 messages)               │
│                                                                  │
│ 5. PROACTIVE NUDGES (if configured)                              │
│    Source: notifications table                                   │
│    Display: NotificationPanel                                    │
│    Types:                                                        │
│      - execution_nudge: Stall reminder                           │
│      - deadline_alert: Upcoming deadline                         │
│      - achievement: Progress celebration                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Proactive Agent Intervention (PLANNED)

```
┌─────────────────────────────────────────────────────────────────┐
│                PROACTIVE NUDGE FLOW (Not Yet Active)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ SCHEDULED JOB (9 AM daily) - NOT IMPLEMENTED                     │
│    │                                                             │
│    ▼                                                             │
│ ┌─────────────────────────────────────────────────────────┐     │
│ │ 1. Scan all active profiles                              │     │
│ │    - Query profiles where onboarding_completed = true    │     │
│ │    - Filter to active students                           │     │
│ └─────────────────────────────────────────────────────────┘     │
│    │                                                             │
│    ▼                                                             │
│ ┌─────────────────────────────────────────────────────────┐     │
│ │ 2. For each profile, run stall detection                 │     │
│ │    - ExecutionChatAgent.tool_detect_stalls()             │     │
│ │    - Check projects > 5 days inactive                    │     │
│ └─────────────────────────────────────────────────────────┘     │
│    │                                                             │
│    ▼                                                             │
│ ┌─────────────────────────────────────────────────────────┐     │
│ │ 3. Generate personalized nudge                           │     │
│ │    - Use LLM to craft message                            │     │
│ │    - Reference specific stalled project                  │     │
│ │    - Suggest next micro-step                             │     │
│ └─────────────────────────────────────────────────────────┘     │
│    │                                                             │
│    ▼                                                             │
│ ┌─────────────────────────────────────────────────────────┐     │
│ │ 4. Store and deliver                                     │     │
│ │    - Insert into notifications table                     │     │
│ │    - Insert into conversations (is_proactive = true)     │     │
│ │    - Optional: Send push notification                    │     │
│ └─────────────────────────────────────────────────────────┘     │
│    │                                                             │
│    ▼                                                             │
│ ┌─────────────────────────────────────────────────────────┐     │
│ │ 5. Student sees nudge on next login                      │     │
│ │    - Notification bell shows unread count                │     │
│ │    - Execution tab shows proactive message               │     │
│ └─────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. COMPONENT HIERARCHY

### 5.1 Dashboard Page

```
DashboardPage (/dashboard)
├── DashboardLayout
│   ├── TopNav
│   │   ├── Logo
│   │   ├── NotificationBell → NotificationPanel
│   │   └── UserMenu
│   │
│   ├── Sidebar (mobile: hidden)
│   │   └── TabNavigation
│   │
│   └── MainContent
│       ├── TabHeader (mobile: visible)
│       │   └── Tab buttons (horizontal scroll)
│       │
│       └── TabContent (conditional render)
│           │
│           ├── [tab=assessment] AssessmentTab
│           │   ├── IvyScoreCard
│           │   ├── PillarDisplay
│           │   ├── FactorDetails
│           │   └── NarrativeSummary
│           │
│           ├── [tab=gameplan] GamePlanTab
│           │   ├── PhaseTimeline
│           │   ├── TargetSchools
│           │   └── ActivityRecommendations
│           │
│           ├── [tab=preparation] PreparationTab
│           │   ├── WeeklyTasks
│           │   └── ProgressTracker
│           │
│           ├── [tab=growth] GrowthTab
│           │   ├── AchievementsList
│           │   └── MilestoneTracker
│           │
│           ├── [tab=multiagents] MultiAgentsTab
│           │   ├── AgentStatusCards
│           │   └── OrchestrationFlow
│           │
│           └── [tab=execution] ExecutionTab
│               ├── Header (Dashboard/Chat toggle)
│               │
│               ├── [view=dashboard] DashboardView
│               │   ├── EDSCard
│               │   ├── QuickActionsCard
│               │   ├── WeeklyFocusCard
│               │   ├── StalledProjectsCard
│               │   └── ActiveProjectsCard
│               │
│               └── [view=chat] ChatView
│                   ├── MessageHistory
│                   │   └── ChatBubble (mapped)
│                   ├── SuggestionChips (when empty)
│                   └── InputArea
```

### 5.2 Quest/Assessment Flow

```
QuestPage (/quest)
├── QuestOrchestrator
│   ├── WelcomeScreen
│   └── StartButton → /quest/1

QuestFramePage (/quest/[frameId])
├── QuestFrame
│   ├── FrameHeader (progress indicator)
│   ├── FrameContent (dynamic per frame)
│   │   ├── Frame1: BasicInfoFrame
│   │   ├── Frame2: AcademicFrame
│   │   ├── Frame3: ActivitiesFrame
│   │   ├── Frame4: GoalsFrame
│   │   ├── Frame5: ReflectionFrame
│   │   └── Frame6: ReviewFrame
│   └── NavigationButtons
│       ├── BackButton
│       └── NextButton / SubmitButton
```

---

## 6. STATE MANAGEMENT

### 6.1 Zustand Stores

| Store | Purpose | Key State |
|-------|---------|-----------|
| `useSessionStore` | Auth session | `profile_id`, `user_id`, `session_id`, `is_completed` |
| `useStudentStore` | Student data | `profile`, `gamePlan`, `loading` |
| `useResultsStore` | Assessment results | `ivyScore`, `pillars`, `archetype` |
| `useFrame3Store` | Frame 3 state | Activities input |
| `useFrame4Store` | Frame 4 state | Goals input |
| `useFrame5Store` | Frame 5 state | Reflections input |
| `useInsightsStore` | Insights | Generated insights |

### 6.2 Data Flow

```
User Action
    │
    ▼
Component (e.g., ExecutionTab)
    │
    ├─── Local State (useState)
    │    - UI state (input, view toggle)
    │    - Transient data
    │
    ├─── Zustand Store
    │    - Session data (profile_id)
    │    - Cached profile data
    │
    └─── API Call (fetch/useQuery)
         - Server data (EDS, projects)
         - Real-time updates
```

---

## 7. DATABASE TOUCHPOINTS

### 7.1 Assessment Phase

| Action | Table | Operation | Columns |
|--------|-------|-----------|---------|
| Create account | `profiles` | INSERT | `id`, `email`, `first_name`, `last_name` |
| Frame 1 submit | `profiles` | UPDATE | `grade`, `school_type` |
| Frame 2 submit | `profiles` | UPDATE | `gpa`, `sat_score`, `act_score` |
| Frame 3 submit | `activities` | INSERT | `profile_id`, `activity_data` |
| Frame 4 submit | `profiles` | UPDATE | `target_schools`, `intended_major` |
| Assessment complete | `profiles` | UPDATE | `archetype`, `narrative_*`, `ivy_score`, `assessment_completed_at` |

### 7.2 Ongoing Usage

| Action | Table | Operation | Columns |
|--------|-------|-----------|---------|
| Send chat | `conversations` | INSERT | `profile_id`, `role`, `content`, `agent_type` |
| Generate plan | `weekly_plans` | UPSERT | `profile_id`, `p0_tasks`, `p1_tasks`, `p2_tasks` |
| Update project | `projects` | UPDATE | `status`, `last_activity_at` |
| Create nudge | `notifications` | INSERT | `profile_id`, `type`, `message` |
| Store insight | `agent_memories` | INSERT | `profile_id`, `content`, `observation_type` |

---

## 8. MOBILE EXPERIENCE

### 8.1 Responsive Breakpoints

```css
/* From Tailwind config */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet portrait */
lg: 1024px  /* Tablet landscape / Desktop */
xl: 1280px  /* Large desktop */
```

### 8.2 Mobile-Specific Adaptations

| Component | Desktop | Mobile |
|-----------|---------|--------|
| Sidebar | Visible, fixed | Hidden, hamburger menu |
| TabHeader | Horizontal tabs | Horizontal scroll |
| DashboardView | 3-column grid | Single column |
| ChatView | Full height | Full height with safe areas |
| QuickActions | 2x2 grid | 2x2 grid (smaller) |

---

## Appendix: Sample Profile Data

```json
{
  "id": "4c4c94f9-a7df-4483-9dc6-7905dda36386",
  "first_name": "Huda",
  "last_name": "Sira",
  "email": "huda@ivylevel.com",
  "grade": 11,
  "gpa": 3.9,
  "sat_score": 1590,
  "archetype": "SCHOLAR",
  "ivy_score": 79,
  "intended_major": "Computer Science",
  "narrative_dna": "Growing up as a South Asian Muslim in a household enriched by the traditions and values of their immigrant parents...",
  "narrative_brand_statement": "A South Asian Muslim innovator...",
  "narrative_themes": ["Community Empowerment", "Cultural Identity", "Academic Excellence", "Leadership", "Economic Growth"],
  "onboarding_completed": true,
  "assessment_completed_at": "2026-01-15T10:30:00Z"
}
```
