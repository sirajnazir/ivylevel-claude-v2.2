# Multi-Agent Frontend Integration Specification

## Document Information

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Date | January 2026 |
| Status | Implementation Spec |
| Scope | Frontend Integration + Manual Testing |

---

# Part 1: Current State Analysis

## 1.1 Assessment Flow (IMPLEMENTED - REAL)

### Component Hierarchy
```
/quest/[frameId]/page.tsx
├── Frame1Warmup.tsx     → Identity & Target Schools
├── Frame2Snapshot.tsx   → Aptitude (GPA, SAT, AP)
├── Frame3Building.tsx   → Passion & Community (10 cards)
├── Frame4Context.tsx    → Operating Data & Quiz (15 cards)
├── Frame5GamePlan.tsx   → Score Reveal & Twin Fleet
└── Frame6ProfileReveal.tsx → Profile Summary & Boosters
```

### Data Flow
```
User Input → useStudentStore (profile) → Frame Completion
                    ↓
              useSessionStore (progress)
                    ↓
              Assessment Complete → Dashboard Redirect
```

### Real Backend Integration
- **API**: `POST /api/score` with full `StudentProfile`
- **Response**: `AssessmentResults` + `SchoolProbability[]` + `BoosterRecommendations`
- **Storage**: `useResultsStore` (ivy_score, probabilities, helping_factors, etc.)

---

## 1.2 Scoring System (IMPLEMENTED - REAL)

### Hooks Architecture
```typescript
// lib/hooks/useScoring.ts
useScoring()          → calculateScore(), results, isLoading, error
useIvyScore()         → totalScore, categoryScores (aptitude, passion, community, narrative)
useSchoolProbabilities() → probabilities[], topSchool
useArchetype()        → archetype, label, tagline
useFactors()          → helping[], holdingBack[]
```

### Real API Integration
```
Dashboard Mount → useScoring.calculateScore()
                      ↓
               POST /api/score { profile }
                      ↓
               ScoringEngine.compute()
                      ↓
               useResultsStore.setResults()
```

### Store Structure (`useResultsStore`)
```typescript
{
  results: AssessmentResults,
  ivy_score: IvyReadyScore,           // { overall, aptitude, passion, community, narrative }
  school_probabilities: SchoolProbability[],
  helping_factors: string[],
  holding_back_factors: string[],
  archetype: ArchetypeID,
  // Narrative synthesis
  brand_statement: string,
  narrative_dna: string,
  first_principle: string,
  narrative_themes: string[],
  // Boosters
  booster_recommendations: BoosterRecommendations,
  twin_fleet: TwinFleet,
}
```

---

## 1.3 Insight Generation (IMPLEMENTED - REAL)

### InsightEngine Location
```
lib/insights/InsightEngine.ts
```

### 7 Insight Categories
1. **HyperLocal** - High school peer benchmarking (saturation, college placements)
2. **Context** - Demographics, region, hooks (first-gen, legacy)
3. **Temporal** - Grade-aware timing insights
4. **Aptitude** - GPA, SAT, AP rigor benchmarking
5. **Passion** - Leadership, research, project impact
6. **Psychometric** - Grit, burnout risk, time management
7. **Identity** - Narrative clarity, articulation ability

### Hook Integration
```typescript
// lib/hooks/useInsights.ts
const {
  insights,
  generateInsights,
  criticalInsights,
  warningInsights,
  positiveInsights,
  isGenerating
} = useInsights();
```

---

## 1.4 Narrative Synthesis (PARTIAL - HYBRID)

### Current State
- **Frame 6** displays brand_statement, narrative_themes from `useResultsStore`
- **AssessmentTab** shows narrative data if available
- **MultiAgentTab** has NarrativeDNA component

### Agent Integration Points
```
Frontend: useResultsStore.brand_statement, narrative_dna, narrative_themes
Backend:  POST /agents/narrative/synthesize → NarrativeSynthesisAgent
```

### Missing Integration
- [ ] Automatic narrative synthesis on assessment complete
- [ ] Narrative regeneration trigger from dashboard
- [ ] Narrative confidence display and HITL handoff

---

## 1.5 GamePlan (IMPLEMENTED - HYBRID)

### Real Engine
```
lib/gamePlan/gamePlanEngine.ts
├── generateGamePlan(profile) → GamePlan
├── phases: Phase[]
├── quickWins: Action[]
└── weeklyCommitment: number
```

### Supabase Persistence
```typescript
// lib/hooks/useUserData.ts
const { gamePlanData } = useUserData();
// Loads from: profiles.game_plan_data (JSONB)
```

### Agent Enhancement (PENDING)
```
Backend: POST /agents/gameplan/generate → GamePlanAgent
Response: { activities, identity_seeds, phases, summary }
```

---

## 1.6 Dashboard Tabs (CURRENT STATE)

| Tab | Status | Data Source |
|-----|--------|-------------|
| **Assessment** | REAL | useScoring hooks → /api/score |
| **GamePlan** | HYBRID | useGamePlan engine + Supabase |
| **Preparation** | MOCK | mockPreparationData (hardcoded) |
| **Growth** | HYBRID | useInsights + mock events |
| **MultiAgents** | PLACEHOLDER | Chat UI exists, backend calls need wiring |

---

## 1.7 Multi-Agent Tab (CURRENT PLACEHOLDER)

### Existing Components
```
components/tabs/MultiAgentsTab.tsx    → Chat interface
components/dashboard/MultiAgentTab.tsx → Agent cards dashboard
components/agents/
├── NarrativeDNACard.tsx
├── AwardPortfolioCard.tsx
├── MicroEditPanel.tsx
└── OpportunityTimeline.tsx
```

### Current Agent Definitions
```typescript
const AGENTS = [
  { id: 'strategist', name: 'Strategist', specialty: 'Long-term planning' },
  { id: 'academic', name: 'Academic Advisor', specialty: 'Course selection' },
  { id: 'awards', name: 'Awards Scout', specialty: 'Scholarships & competitions' },
  { id: 'narrative', name: 'Story Coach', specialty: 'Personal narrative' },
  { id: 'opportunity', name: 'Innovation Guide', specialty: 'Unique opportunities' },
];
```

### Missing: Actual Backend Integration
- `useMultiAgentChat` hook exists but needs real API implementation
- `components/dashboard/MultiAgentTab.tsx` uses `useAgentData` hooks but these need profile_id

---

# Part 2: Multi-Agent Integration Architecture

## 2.1 Backend Agents (Python - IMPLEMENTED)

### Agent Service Endpoints
```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT SERVICE (Port 8001)                    │
├─────────────────────────────────────────────────────────────────┤
│ Assessment Agent                                                 │
│ ├── POST /agents/assessment/enhance     → Full enhancement       │
│ ├── POST /agents/assessment/narrative   → Narrative DNA          │
│ └── POST /agents/assessment/archetype   → Archetype detection    │
├─────────────────────────────────────────────────────────────────┤
│ Narrative Synthesis Agent                                        │
│ ├── POST /agents/narrative/synthesize   → Jenny's Formula        │
│ └── GET  /agents/narrative/{profile_id} → Cached narrative       │
├─────────────────────────────────────────────────────────────────┤
│ GamePlan Agent                                                   │
│ ├── POST /agents/gameplan/generate      → Full game plan         │
│ ├── GET  /agents/gameplan/activities/{id} → Filtered activities  │
│ └── GET  /agents/gameplan/seeds/{id}    → Identity seeds         │
├─────────────────────────────────────────────────────────────────┤
│ Execution Agent (P0 CRITICAL)                                    │
│ ├── POST /agents/execution/scaffold     → Project microsteps     │
│ ├── POST /agents/execution/crisis       → Crisis Alchemy         │
│ ├── POST /agents/handoff/approve        → HITL approval          │
│ ├── GET  /agents/execution/blockers/{id}→ Blocker detection      │
│ └── GET  /agents/execution/eds/{id}     → Execution Debt Score   │
├─────────────────────────────────────────────────────────────────┤
│ Awards Agent                                                     │
│ ├── GET  /agents/awards/match/{id}      → Award matching         │
│ ├── GET  /agents/awards/portfolio/{id}  → Portfolio optimization │
│ └── GET  /agents/awards/timeline/{id}   → Award timeline         │
├─────────────────────────────────────────────────────────────────┤
│ Opportunity Agent                                                │
│ ├── GET  /agents/opportunities/match/{id}   → Opportunity match  │
│ ├── GET  /agents/opportunities/alerts/{id}  → Deadline alerts    │
│ ├── GET  /agents/opportunities/cascades/{id}→ Backup cascades    │
│ └── GET  /agents/opportunities/timeline/{id}→ Timeline view      │
├─────────────────────────────────────────────────────────────────┤
│ Tools                                                            │
│ ├── POST /tools/micro-edits             → Essay micro-editing    │
│ └── POST /tools/analyze-essay           → Essay analysis         │
├─────────────────────────────────────────────────────────────────┤
│ Proactive Workflows                                              │
│ ├── GET  /workflows/status              → All workflow status    │
│ ├── POST /workflows/run                 → Manual trigger         │
│ ├── GET  /workflows/runs                → Run history            │
│ └── GET  /workflows/deadlines/{id}      → Profile deadlines      │
├─────────────────────────────────────────────────────────────────┤
│ Notifications                                                    │
│ ├── GET  /notifications/{id}            → List notifications     │
│ ├── POST /notifications/mark-read       → Mark as read           │
│ └── GET  /notifications/{id}/count      → Unread count           │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 Frontend API Client (IMPLEMENTED)

### Location
```
lib/api/agentClient.ts
hooks/useAgentData.ts
```

### Client Functions
```typescript
agentApi = {
  // Assessment
  enhanceAssessment(profileId, data),
  synthesizeNarrativeDNA(profileId),
  detectArchetype(profileId),

  // GamePlan
  generateGamePlan(profileId, assessmentData),
  getFilteredActivities(profileId),
  getIdentitySeeds(profileId),

  // Execution
  scaffoldProject(input),
  handleCrisis(input),
  getBlockers(profileId),
  getExecutionDebtScore(profileId),
  approveHandoff(crisisId, approved, rationale),

  // Awards
  matchAwards(profileId),
  getAwardPortfolio(profileId),
  getAwardTimeline(profileId),

  // Opportunities
  matchOpportunities(profileId),
  getOpportunityAlerts(profileId),
  getBackupCascades(profileId),
  getOpportunityTimeline(profileId),

  // Tools
  applyMicroEdits(text, essayType),
  analyzeEssay(text, essayType),

  // Health
  checkAgentHealth(),
}
```

### React Query Hooks
```typescript
// hooks/useAgentData.ts
useAssessmentEnhancement(profileId)   → AssessmentResult
useNarrativeDNA(profileId)            → NarrativeDNA
useGamePlan(profileId)                → GamePlanResult
useExecutionDebtScore(profileId)      → ExecutionDebtScore
useAwardMatches(profileId)            → { matches, portfolio, timeline }
useOpportunityMatches(profileId)      → { matches, alerts, cascades }
useOpportunityAlerts(profileId)       → { alerts, count, urgent_count }
useMicroEdits()                       → mutation
useEssayAnalysis()                    → mutation
useAgentHealth()                      → health status
useDashboardData(profileId)           → combined data + refetchAll
```

---

## 2.3 Integration Gap Analysis

### CRITICAL GAPS

| Gap | Impact | Priority |
|-----|--------|----------|
| **profileId not passed to MultiAgentTab** | Agents can't fetch data | P0 |
| **No profile persistence after assessment** | No profileId to use | P0 |
| **Chat messages not saved** | Context lost on refresh | P1 |
| **Crisis workflow UI missing** | HITL approval blocked | P1 |
| **Notification bell missing** | Proactive alerts invisible | P1 |

### INTEGRATION GAPS

| Component | Current State | Required |
|-----------|---------------|----------|
| Dashboard → MultiAgentTab | No profileId prop | Pass profileId from session/auth |
| MultiAgentTab (tabs/) | Chat-only UI | Add agent cards dashboard view |
| AssessmentTab | Shows narrative if exists | Trigger synthesis on mount |
| GamePlanTab | Uses local engine | Integrate agent game plan |
| PreparationTab | All mock data | Wire to agent activities |
| GrowthTab | Partial mock | Wire to notifications + milestones |

---

# Part 3: Detailed Implementation Plan

## 3.1 Phase 1: Profile ID Infrastructure (P0)

### 3.1.1 Profile Creation on Assessment Complete

**File**: `components/frames/Frame6ProfileReveal.tsx` (or assessment completion handler)

```typescript
// On assessment complete:
async function handleAssessmentComplete() {
  const profile = useStudentStore.getState().profile;
  const user = useAuth().user;

  // Create or update profile in Supabase
  const { data: profileRecord, error } = await supabase
    .from('profiles')
    .upsert({
      user_id: user?.id,
      profile_data: profile,
      assessment_completed_at: new Date().toISOString(),
    })
    .select()
    .single();

  // Store profile_id in session
  useSessionStore.getState().setProfileId(profileRecord.id);

  // Navigate to dashboard
  router.push('/dashboard');
}
```

### 3.1.2 Session Store Update

**File**: `lib/store/useSessionStore.ts`

```typescript
// Add to store state:
profile_id: string | null,
setProfileId: (id: string) => void,

// Add to store:
setProfileId: (id) => set({ profile_id: id }),
```

### 3.1.3 Dashboard Profile ID Retrieval

**File**: `app/dashboard/page.tsx`

```typescript
// In DashboardContent:
const profileId = useSessionStore((s) => s.profile_id);
const { user } = useAuth();

// Fallback: fetch profile_id from Supabase by user_id
useEffect(() => {
  if (!profileId && user?.id) {
    fetchProfileId(user.id);
  }
}, [profileId, user]);

// Pass to MultiAgentTab:
case 'multiagents':
  return <MultiAgentTab profileId={profileId} />;
```

---

## 3.2 Phase 2: Multi-Agent Dashboard View (P0)

### 3.2.1 Unified MultiAgentTab Component

**Replace**: `components/tabs/MultiAgentsTab.tsx`

```typescript
// New unified component structure:
export function MultiAgentTab({ profileId }: { profileId: string | null }) {
  const [view, setView] = useState<'dashboard' | 'chat'>('dashboard');
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('strategist');

  if (view === 'chat') {
    return (
      <ChatView
        profileId={profileId}
        agent={selectedAgent}
        onBack={() => setView('dashboard')}
      />
    );
  }

  return (
    <AgentDashboard
      profileId={profileId}
      onAgentChat={(agent) => {
        setSelectedAgent(agent);
        setView('chat');
      }}
    />
  );
}
```

### 3.2.2 Agent Dashboard View

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Multi-Agent Dashboard                           [Refresh All]  │
│ Your 6-agent coaching team working in parallel                  │
├─────────────────────────────────────────────────────────────────┤
│ ┌───────────────────┐ ┌───────────────────┐ ┌─────────────────┐ │
│ │ Assessment Agent  │ │ Game Plan Agent   │ │ Execution Agent │ │
│ │ ──────────────── │ │ ───────────────── │ │ ─────────────── │ │
│ │ Narrative DNA:    │ │ Activities: 12    │ │ EDS: 24 (Good)  │ │
│ │ "Builder who..."  │ │ Seeds: 5          │ │ Status: Healthy │ │
│ │ Archetype: 85%    │ │ Phases: 3         │ │ Blockers: 0     │ │
│ │                   │ │                   │ │                 │ │
│ │ [Refresh] [Chat]  │ │ [Refresh] [Chat]  │ │ [Refresh] [Chat]│ │
│ └───────────────────┘ └───────────────────┘ └─────────────────┘ │
│ ┌───────────────────┐ ┌───────────────────┐ ┌─────────────────┐ │
│ │ Awards Agent      │ │ Opportunity Agent │ │ Crisis Response │ │
│ │ ────────────────  │ │ ───────────────── │ │ ─────────────── │ │
│ │ Likely: 5         │ │ Matches: 8        │ │ No active       │ │
│ │ Target: 3         │ │ Urgent Alerts: 2  │ │ crises          │ │
│ │ Stretch: 2        │ │ Deadlines: 4      │ │                 │ │
│ │ Expected Wins: 4.2│ │                   │ │ [Report Crisis] │ │
│ │ [Refresh] [Chat]  │ │ [Refresh] [Chat]  │ │                 │ │
│ └───────────────────┘ └───────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Recent Notifications                              [View All]    │
│ • Deadline Alert: RSI Application due in 14 days               │
│ • Award Match: You qualify for Siemens Competition             │
│ • Weekly Scout: 3 new opportunities match your profile         │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2.3 Agent Card Components

**New Component**: `components/agents/AgentDashboard.tsx`

```typescript
interface AgentDashboardProps {
  profileId: string | null;
  onAgentChat: (agent: AgentType) => void;
}

export function AgentDashboard({ profileId, onAgentChat }: AgentDashboardProps) {
  const health = useAgentHealth();
  const { refetchAll, isLoading } = useDashboardData(profileId);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <DashboardHeader
        health={health.data}
        onRefreshAll={refetchAll}
        isLoading={isLoading}
      />

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AssessmentAgentCard profileId={profileId} onChat={() => onAgentChat('narrative')} />
        <GamePlanAgentCard profileId={profileId} onChat={() => onAgentChat('strategist')} />
        <ExecutionAgentCard profileId={profileId} onChat={() => onAgentChat('strategist')} />
        <AwardsAgentCard profileId={profileId} onChat={() => onAgentChat('awards')} />
        <OpportunityAgentCard profileId={profileId} onChat={() => onAgentChat('opportunity')} />
        <CrisisAgentCard profileId={profileId} />
      </div>

      {/* Notifications Section */}
      <NotificationsPreview profileId={profileId} />
    </div>
  );
}
```

---

## 3.3 Phase 3: Crisis Alchemy UI (P1)

### 3.3.1 Crisis Report Modal

**File**: `components/agents/CrisisReportModal.tsx`

```typescript
interface CrisisReportProps {
  profileId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function CrisisReportModal({ profileId, isOpen, onClose }: CrisisReportProps) {
  const [crisisType, setCrisisType] = useState<string>('');
  const [description, setDescription] = useState('');
  const [urgency, setUrgency] = useState(3);
  const mutation = useHandleCrisisMutation();

  const crisisTypes = [
    { id: 'blocker', label: 'Project Blocked', description: "Can't make progress on something" },
    { id: 'rejection', label: 'Rejection/Setback', description: 'Award, program, or application rejection' },
    { id: 'overwhelm', label: 'Feeling Overwhelmed', description: 'Too much to do, losing motivation' },
    { id: 'deadline', label: 'Deadline Panic', description: 'Important deadline approaching fast' },
    { id: 'doubt', label: 'Self-Doubt', description: 'Questioning direction or capabilities' },
  ];

  const handleSubmit = async () => {
    const result = await mutation.mutateAsync({
      profile_id: profileId,
      crisis_type: crisisType,
      description,
      urgency,
    });

    // Show Crisis Alchemy response
    // result contains: validate, act, reframe, create steps
  };

  // ... render form
}
```

### 3.3.2 Crisis Response Display

**File**: `components/agents/CrisisResponseCard.tsx`

```typescript
// Display the 4-step Crisis Alchemy response:
// 1. Validate (2s) - Acknowledge emotion
// 2. Act (10s) - Micro-action
// 3. Reframe (30s) - Opportunity angle
// 4. Create (2min) - Design pivot activity

interface CrisisResponseCardProps {
  response: CrisisResponse;
  onApprove: () => void;
  onReject: (reason: string) => void;
}
```

---

## 3.4 Phase 4: Notifications System (P1)

### 3.4.1 Notification Bell Component

**File**: `components/shared/NotificationBell.tsx`

```typescript
export function NotificationBell({ profileId }: { profileId: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const { data: notifications, refetch } = useNotifications(profileId);
  const { data: countData } = useNotificationCount(profileId);

  return (
    <>
      <button onClick={() => setIsOpen(true)} className="relative">
        <Bell size={20} />
        {countData?.unread_count > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {countData.unread_count}
          </span>
        )}
      </button>

      <NotificationPanel
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        notifications={notifications}
        onMarkRead={handleMarkRead}
      />
    </>
  );
}
```

### 3.4.2 Notification Types

```typescript
type NotificationType =
  | 'silence_nudge'      // From SilenceDetector workflow
  | 'deadline_low'       // 30 days out
  | 'deadline_medium'    // 7 days out
  | 'deadline_high'      // 3 days out
  | 'urgent'             // 1 day out
  | 'opportunity_match'  // From WeeklyScout
  | 'checkin_reminder'   // From DailyCheckin
  | 'crisis_pending'     // HITL approval needed
  | 'award_match'        // New award matched
  | 'milestone_complete' // Progress milestone
```

---

## 3.5 Phase 5: Integration with Existing Tabs (P2)

### 3.5.1 AssessmentTab Enhancement

```typescript
// Add narrative synthesis trigger:
useEffect(() => {
  if (profileId && !narrativeDna) {
    // Auto-fetch narrative from agent if not cached
    synthesizeNarrative(profileId);
  }
}, [profileId, narrativeDna]);

// Add "Regenerate Narrative" button
<button onClick={() => synthesizeNarrative(profileId, { force: true })}>
  <RefreshCw /> Regenerate Narrative
</button>
```

### 3.5.2 GamePlanTab Enhancement

```typescript
// Replace mock with agent data:
const { data: agentGamePlan, isLoading } = useGamePlan(profileId);

// Merge with local engine output
const gameplanData = useMemo(() => {
  if (agentGamePlan?.game_plan) {
    return transformAgentGamePlan(agentGamePlan.game_plan);
  }
  return localGamePlan;
}, [agentGamePlan, localGamePlan]);
```

### 3.5.3 PreparationTab Enhancement

```typescript
// Wire to filtered activities:
const { data: activities } = useFilteredActivities(profileId);

// Transform to weekly view
const weeklyTasks = useMemo(() => {
  if (activities) {
    return groupActivitiesByWeek(activities);
  }
  return mockWeeklyTasks;
}, [activities]);
```

---

# Part 4: Manual Test Plan

## 4.1 Test Environment Setup

### Prerequisites
1. Python agent service running on port 8001
2. Next.js app running on port 3000
3. Supabase database with migrations applied
4. Test user account created

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_AGENT_API_URL=http://localhost:8001
NEXT_PUBLIC_SUPABASE_URL=<your-url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-key>
```

### Start Services
```bash
# Terminal 1: Start agent service
cd agents && python main.py

# Terminal 2: Start Next.js
npm run dev
```

---

## 4.2 Test Suite: Agent Health & Connectivity

### TC-001: Agent Service Health Check
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open browser to `http://localhost:8001/health` | JSON response with `status: "healthy"` |
| 2 | Check `agents_enabled: true` | Agents are enabled |
| 3 | Open `http://localhost:8001/` | Service info with all agents listed |

### TC-002: Frontend Agent Health Check
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to dashboard | Dashboard loads |
| 2 | Switch to "Multi-Agents" tab | Tab renders without errors |
| 3 | Check for "Backend healthy" indicator | Green status badge visible |

---

## 4.3 Test Suite: Assessment Agent Integration

### TC-010: Assessment Enhancement
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete full assessment (Frames 1-6) | Navigate to dashboard |
| 2 | Click "Multi-Agents" tab | Multi-agent dashboard visible |
| 3 | Locate "Assessment Agent" card | Card shows loading or data |
| 4 | Verify Narrative DNA displayed | DNA quote visible |
| 5 | Verify Archetype shown | Archetype label + confidence % |
| 6 | Click "Refresh" on Assessment Agent | Loading spinner, then new data |

### TC-011: Narrative Synthesis
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | On Assessment Agent card, click "Chat" | Chat view opens |
| 2 | Type: "Tell me about my narrative" | Response from Story Coach agent |
| 3 | Return to dashboard view | Previous data preserved |

---

## 4.4 Test Suite: GamePlan Agent Integration

### TC-020: Game Plan Generation
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete assessment | Dashboard visible |
| 2 | Switch to "Multi-Agents" tab | Dashboard loads |
| 3 | Locate "Game Plan Agent" card | Card shows data |
| 4 | Verify Activities count | Number > 0 |
| 5 | Verify Seeds count | Number > 0 |
| 6 | Verify Phases listed | 3 phases visible |

### TC-021: Game Plan Chat
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Chat" on Game Plan Agent | Chat view opens |
| 2 | Type: "What activities should I focus on?" | Strategist responds with activity suggestions |
| 3 | Type: "Why these activities?" | Detailed rationale provided |

---

## 4.5 Test Suite: Execution Agent Integration

### TC-030: Execution Debt Score
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Multi-Agents tab | Dashboard loads |
| 2 | Locate "Execution Agent" card | Card shows EDS |
| 3 | Verify EDS score displayed | Number 0-100 |
| 4 | Verify status indicator | "healthy", "at_risk", or "critical" |

### TC-031: Project Scaffolding
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Chat" on Execution Agent | Chat view opens |
| 2 | Type: "Help me scaffold my RSI application" | Microsteps generated |
| 3 | Verify microsteps include time estimates | Each step has duration |

### TC-032: Crisis Alchemy
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Find "Crisis Response" card | Card visible |
| 2 | Click "Report Crisis" | Modal opens |
| 3 | Select crisis type: "Rejection/Setback" | Type selected |
| 4 | Enter description: "Got rejected from summer program" | Text entered |
| 5 | Set urgency: 4 | Urgency slider updated |
| 6 | Click "Submit" | Crisis Alchemy response displayed |
| 7 | Verify 4 steps shown | Validate, Act, Reframe, Create |
| 8 | Verify "Pending Coach Approval" | HITL indicator visible |

---

## 4.6 Test Suite: Awards Agent Integration

### TC-040: Award Matching
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Multi-Agents tab | Dashboard loads |
| 2 | Locate "Awards Agent" card | Card shows data |
| 3 | Verify Likely/Target/Stretch counts | Numbers visible |
| 4 | Verify "Expected Wins" | Decimal number shown |
| 5 | Click "Refresh" | Data updates |

### TC-041: Award Portfolio Details
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Chat" on Awards Agent | Chat opens |
| 2 | Type: "What awards should I apply for?" | Personalized recommendations |
| 3 | Type: "Why these awards?" | ROI explanation provided |

---

## 4.7 Test Suite: Opportunity Agent Integration

### TC-050: Opportunity Matching
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Multi-Agents tab | Dashboard loads |
| 2 | Locate "Opportunity Agent" card | Card shows data |
| 3 | Verify Matches count | Number visible |
| 4 | Verify Urgent Alerts count | Number (may be 0) |

### TC-051: Deadline Alerts
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | If urgent alerts > 0 | Alert cards visible |
| 2 | Click on alert | Details expand |
| 3 | Verify deadline date | Date shown |
| 4 | Verify recommended actions | Action items listed |

---

## 4.8 Test Suite: Chat Interface

### TC-060: Agent Selection
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter chat view | Agent selector visible |
| 2 | Click "Strategist" | Strategist highlighted |
| 3 | Click "Academic Advisor" | Academic Advisor highlighted |
| 4 | Send message | Response from selected agent |

### TC-061: Message Persistence
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Send several messages | Messages visible |
| 2 | Switch to dashboard view | View changes |
| 3 | Return to chat view | Previous messages preserved |
| 4 | Click "Clear Chat" | Messages cleared |

### TC-062: Agent Context
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Select "Awards Scout" | Agent selected |
| 2 | Type: "What awards fit my profile?" | Personalized response |
| 3 | Type: "Tell me more about the first one" | Context-aware follow-up |

---

## 4.9 Test Suite: Notifications

### TC-070: Notification Bell
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Locate notification bell in header | Bell icon visible |
| 2 | Check for unread count badge | Badge shows count (or 0) |
| 3 | Click bell | Notification panel opens |

### TC-071: Notification Actions
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open notification panel | List visible |
| 2 | Click on notification | Details expand or navigate |
| 3 | Click "Mark as Read" | Notification marked |
| 4 | Verify count decreases | Badge updates |

---

## 4.10 Test Suite: Error Handling

### TC-080: Agent Service Down
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Stop agent service (Ctrl+C) | Service stopped |
| 2 | Navigate to Multi-Agents tab | Tab loads |
| 3 | Verify error state | "Backend unavailable" message |
| 4 | Click "Refresh All" | Error persists gracefully |
| 5 | Restart agent service | Service running |
| 6 | Click "Refresh All" | Data loads successfully |

### TC-081: Network Timeout
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Simulate slow network (DevTools) | Network throttled |
| 2 | Trigger agent call | Loading spinner visible |
| 3 | Wait for timeout (60s) | Error message displayed |
| 4 | Verify retry option | "Retry" button available |

### TC-082: Invalid Profile ID
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Clear session storage | Session cleared |
| 2 | Navigate directly to /dashboard | Redirect or error |
| 3 | Verify graceful handling | No crash, clear message |

---

## 4.11 Test Suite: Data Flow Validation

### TC-090: Assessment → Agent Data Flow
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete new assessment | Dashboard loads |
| 2 | Note scores (GPA, SAT, etc.) | Values recorded |
| 3 | Switch to Multi-Agents | Tab loads |
| 4 | Check Assessment Agent data | Reflects profile |
| 5 | Check Awards matches | Appropriate for profile |
| 6 | Check Opportunities | Relevant matches |

### TC-091: Score Change → Agent Update
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Retake assessment with higher scores | New scores saved |
| 2 | Navigate to Multi-Agents | Tab loads |
| 3 | Click "Refresh All" | All agents update |
| 4 | Verify Award matches changed | Better matches appear |

---

## 4.12 Performance Test Cases

### TC-100: Initial Load Time
| Metric | Target | Pass Criteria |
|--------|--------|---------------|
| Dashboard load | < 2s | Time to interactive |
| Agent card data | < 5s | All 6 cards populated |
| Full refresh | < 8s | All data refreshed |

### TC-101: Concurrent Requests
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Refresh All" | 6 parallel requests |
| 2 | Verify no errors | All succeed |
| 3 | Verify UI responsive | No blocking |

---

## 4.13 Regression Test Matrix

| Feature | Frames | Dashboard | Multi-Agent | Notes |
|---------|--------|-----------|-------------|-------|
| Assessment completion | Must work | Must redirect | Must have data | Critical path |
| Score calculation | - | Must show | Must inform agents | Core feature |
| Narrative display | Frame 6 | Assessment tab | Agent card | Multiple views |
| Game plan | Frame 5 | GamePlan tab | Agent card | Multiple views |
| Chat interface | - | - | Must work | Agent chat |
| Crisis response | - | - | Must work | HITL flow |
| Notifications | - | Header bell | Preview section | Cross-cutting |

---

# Part 5: Implementation Checklist

## 5.1 P0 - Critical (Week 1)

- [ ] Add `profile_id` to `useSessionStore`
- [ ] Create profile record on assessment complete
- [ ] Pass `profileId` to `MultiAgentTab`
- [ ] Wire `MultiAgentTab` to use `components/dashboard/MultiAgentTab`
- [ ] Verify agent health check works
- [ ] Test all 6 agent card data loads

## 5.2 P1 - High Priority (Week 2)

- [ ] Implement Crisis Report Modal
- [ ] Implement Crisis Response Display
- [ ] Add HITL approval flow
- [ ] Implement Notification Bell
- [ ] Implement Notification Panel
- [ ] Add notification badges

## 5.3 P2 - Medium Priority (Week 3)

- [ ] Enhance AssessmentTab with agent narrative
- [ ] Enhance GamePlanTab with agent activities
- [ ] Enhance PreparationTab with filtered activities
- [ ] Enhance GrowthTab with notifications

## 5.4 P3 - Future Enhancements

- [ ] Chat message persistence (localStorage or Supabase)
- [ ] Agent conversation history
- [ ] Multi-agent collaboration view
- [ ] Essay micro-edit integration
- [ ] Workflow status dashboard

---

# Appendix A: Type Definitions

## A.1 Agent Types (Current)
```typescript
// lib/types/agents.ts - already implemented
export interface NarrativeDNA { ... }
export interface Archetype { ... }
export interface AssessmentResult { ... }
export interface GamePlanResult { ... }
export interface ExecutionDebtScore { ... }
export interface AwardMatch { ... }
export interface AwardPortfolio { ... }
export interface OpportunityMatch { ... }
export interface OpportunityAlert { ... }
export interface CrisisResponse { ... }
```

## A.2 New Types Needed
```typescript
// Add to lib/types/agents.ts
export interface Notification {
  id: string;
  profile_id: string;
  type: NotificationType;
  title: string;
  message: string;
  data?: Record<string, any>;
  read: boolean;
  read_at?: string;
  created_at: string;
}

export type NotificationType =
  | 'silence_nudge'
  | 'deadline_low'
  | 'deadline_medium'
  | 'deadline_high'
  | 'urgent'
  | 'opportunity_match'
  | 'checkin_reminder'
  | 'crisis_pending'
  | 'award_match'
  | 'milestone_complete';
```

---

# Appendix B: API Route Mapping

## B.1 Next.js → Python Agent Service

| Next.js Route | Python Endpoint | Method |
|---------------|-----------------|--------|
| `/api/agents/assessment/enhance` | `/agents/assessment/enhance` | POST |
| `/api/agents/narrative/synthesize` | `/agents/narrative/synthesize` | POST |
| `/api/agents/gameplan/generate` | `/agents/gameplan/generate` | POST |
| `/api/agents/execution/crisis` | `/agents/execution/crisis` | POST |
| `/api/agents/execution/eds/[id]` | `/agents/execution/eds/{id}` | GET |
| `/api/agents/awards/match/[id]` | `/agents/awards/match/{id}` | GET |
| `/api/agents/opportunities/match/[id]` | `/agents/opportunities/match/{id}` | GET |
| `/api/agents/opportunities/alerts/[id]` | `/agents/opportunities/alerts/{id}` | GET |

## B.2 Direct Client Calls (agentClient.ts)

The `agentClient.ts` calls the Python service directly at `AGENT_API_URL` (default: `http://localhost:8001`).

For production, configure via `NEXT_PUBLIC_AGENT_API_URL` environment variable.

---

# Appendix C: Test Data Fixtures

## C.1 Test Profile (Huda Benchmark)
```json
{
  "identity": {
    "name": "Huda Test",
    "grade": 11,
    "target_schools": ["Harvard", "MIT", "Stanford"]
  },
  "aptitude": {
    "unweighted_gpa": 3.95,
    "sat_composite": 1550,
    "ap_courses": ["AP Chemistry", "AP Biology", "AP Calc BC"],
    "ap_scores": {"chemistry": 5, "biology": 5, "calculus_bc": 5}
  },
  "passion": {
    "leadership_level": "regional",
    "ec_commitment": "high",
    "research_level": "published"
  },
  "community": {
    "service_hours": 250,
    "service_leadership": true
  },
  "demographics": {
    "first_gen": true,
    "legacy": false
  }
}
```

## C.2 Test Scenarios

| Scenario | Profile Characteristics | Expected Outcomes |
|----------|------------------------|-------------------|
| High Achiever | 4.0 GPA, 1550+ SAT, national awards | High EDS, many stretch awards |
| Emerging | 3.5 GPA, 1400 SAT, local activities | Medium EDS, likely + target awards |
| Fresh Start | 3.0 GPA, no SAT, few activities | Low EDS, foundation building |
| Crisis Test | Any profile + crisis trigger | Crisis Alchemy response |

---

*Document End - Version 1.0.0*
