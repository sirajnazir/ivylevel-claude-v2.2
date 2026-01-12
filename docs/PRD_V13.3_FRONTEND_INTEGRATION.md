# IvyQuest PRD v13.3 - Frontend UI/UX Integration
## Complete Frontend Integration with v13.2 Multi-Agent Backend

**Version:** 13.3.0
**Date:** January 11, 2026
**Status:** Implementation Ready
**Previous Version:** v13.2 (Backend Complete)
**This Version:** v13.3 (Full-Stack Integration)

---

## Executive Summary

v13.3 completes the IvyQuest platform by integrating the v13.2 multi-agent backend with a comprehensive frontend UI/UX system. This document specifies:

- **Profile ID Infrastructure**: Session management and profile persistence
- **Multi-Agent Dashboard**: 6-agent card grid with real-time data
- **Crisis Alchemy UI**: Modal workflow for crisis response and HITL approval
- **Notification System**: Bell component with proactive alerts
- **Tab Integration**: Enhancement of existing dashboard tabs
- **Testing Guide**: Comprehensive manual test scenarios

---

## PART 1: ARCHITECTURE OVERVIEW

### 1.1 Technology Stack

```
Frontend Stack:
├── Framework: Next.js 14+ (App Router)
├── State Management: Zustand + React Query
├── Styling: Tailwind CSS + BRAND_COLORS
├── Real-time: WebSocket/SSE for notifications
├── HTTP: Custom agentV13Client.ts
└── Types: TypeScript with lib/types/agents.ts

Backend Integration:
├── Agent Service: FastAPI (Port 8001)
├── v13 Endpoints: /v13/* routes
├── Memory: Redis (short-term) + Supabase (long-term)
└── Authentication: Supabase Auth
```

### 1.2 Data Flow Architecture

```
User Input → Zustand Stores → API Client → Python Agent Service
                  ↓                              ↓
              React Query ←——————————————— JSON Response
                  ↓
              UI Components → User Feedback
```

### 1.3 Component Hierarchy

```
app/dashboard/page.tsx
├── DashboardSidebar
├── DashboardHeader
│   └── NotificationBell (NEW in v13.3)
└── Tab Content
    ├── AssessmentTab (Enhanced)
    ├── GamePlanTab (Enhanced)
    ├── PreparationTab (Enhanced)
    ├── GrowthTab (Enhanced)
    └── MultiAgentTab (NEW in v13.3)
        ├── AgentDashboard
        │   ├── AssessmentAgentCard
        │   ├── GamePlanAgentCard
        │   ├── ExecutionAgentCard
        │   ├── AwardsAgentCard
        │   ├── OpportunityAgentCard
        │   └── CrisisAgentCard
        ├── ChatView
        └── NotificationsPreview
```

---

## PART 2: PROFILE ID INFRASTRUCTURE

### 2.1 Problem Statement

The v13.2 backend requires a `profile_id` to fetch agent data. Currently:
- Assessment creates profile data in Zustand stores (in-memory)
- No persistent profile record is created in Supabase
- MultiAgentTab cannot fetch personalized agent recommendations

### 2.2 Solution: Profile Persistence Flow

```typescript
// Flow: Assessment Complete → Profile Created → profileId Available

Assessment Complete
       ↓
Frame6ProfileReveal.handleComplete()
       ↓
Supabase.profiles.upsert({
  user_id: auth.user.id,
  profile_data: studentProfile,
  assessment_completed_at: new Date()
})
       ↓
useSessionStore.setProfileId(result.id)
       ↓
router.push('/dashboard')
       ↓
Dashboard reads profileId from session
       ↓
MultiAgentTab receives profileId prop
       ↓
Agent API calls include profileId
```

### 2.3 Implementation: Session Store Update

**File**: `lib/store/useSessionStore.ts`

```typescript
interface SessionState {
  // Existing fields...
  current_frame: number;
  frames_completed: number[];

  // NEW: Profile ID for agent integration
  profile_id: string | null;
  setProfileId: (id: string | null) => void;

  // NEW: Profile data status
  profile_status: 'none' | 'creating' | 'ready' | 'error';
  setProfileStatus: (status: 'none' | 'creating' | 'ready' | 'error') => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      // Existing...
      current_frame: 1,
      frames_completed: [],

      // NEW
      profile_id: null,
      setProfileId: (id) => set({ profile_id: id }),
      profile_status: 'none',
      setProfileStatus: (status) => set({ profile_status: status }),
    }),
    {
      name: 'ivyquest-session',
      partialize: (state) => ({
        current_frame: state.current_frame,
        frames_completed: state.frames_completed,
        profile_id: state.profile_id,
        profile_status: state.profile_status,
      }),
    }
  )
);
```

### 2.4 Implementation: Profile Creation on Assessment Complete

**File**: `components/frames/Frame6ProfileReveal.tsx`

```typescript
import { useSessionStore } from '@/lib/store/useSessionStore';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { createClient } from '@/lib/supabase/client';

async function handleAssessmentComplete() {
  const supabase = createClient();
  const { user } = await supabase.auth.getUser();
  const profile = useStudentStore.getState().profile;
  const results = useResultsStore.getState();

  const setProfileId = useSessionStore.getState().setProfileId;
  const setProfileStatus = useSessionStore.getState().setProfileStatus;

  setProfileStatus('creating');

  try {
    // Create or update profile record
    const { data: profileRecord, error } = await supabase
      .from('profiles')
      .upsert({
        user_id: user?.id,
        profile_data: profile,
        assessment_results: {
          ivy_score: results.ivy_score,
          archetype: results.archetype,
          school_probabilities: results.school_probabilities,
          narrative_dna: results.narrative_dna,
          brand_statement: results.brand_statement,
        },
        assessment_completed_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }, {
        onConflict: 'user_id',
      })
      .select()
      .single();

    if (error) throw error;

    setProfileId(profileRecord.id);
    setProfileStatus('ready');

    // Navigate to dashboard
    router.push('/dashboard');

  } catch (error) {
    console.error('Failed to create profile:', error);
    setProfileStatus('error');
    // Still navigate, but agent features will be limited
    router.push('/dashboard');
  }
}
```

### 2.5 Implementation: Dashboard Profile Retrieval

**File**: `app/dashboard/page.tsx`

```typescript
'use client';

import { useEffect } from 'react';
import { useSessionStore } from '@/lib/store/useSessionStore';
import { useAuth } from '@/lib/hooks/useAuth';
import { createClient } from '@/lib/supabase/client';

function DashboardContent() {
  const { user } = useAuth();
  const profileId = useSessionStore((s) => s.profile_id);
  const setProfileId = useSessionStore((s) => s.setProfileId);
  const profileStatus = useSessionStore((s) => s.profile_status);
  const setProfileStatus = useSessionStore((s) => s.setProfileStatus);

  // Fallback: Fetch profileId from Supabase if not in session
  useEffect(() => {
    async function fetchProfileId() {
      if (profileId || !user?.id || profileStatus === 'creating') return;

      const supabase = createClient();
      const { data, error } = await supabase
        .from('profiles')
        .select('id')
        .eq('user_id', user.id)
        .single();

      if (data?.id) {
        setProfileId(data.id);
        setProfileStatus('ready');
      } else {
        setProfileStatus('none');
      }
    }

    fetchProfileId();
  }, [profileId, user?.id, profileStatus]);

  // Tab rendering with profileId
  const renderTabContent = () => {
    switch (activeTab) {
      case 'assessment':
        return <AssessmentTab profileId={profileId} />;
      case 'gameplan':
        return <GamePlanTab profileId={profileId} />;
      case 'preparation':
        return <PreparationTab profileId={profileId} />;
      case 'growth':
        return <GrowthTab profileId={profileId} />;
      case 'multiagents':
        return <MultiAgentTab profileId={profileId} />;
      default:
        return <AssessmentTab profileId={profileId} />;
    }
  };

  return (
    <DashboardLayout>
      <DashboardHeader profileId={profileId}>
        <NotificationBell profileId={profileId} />
      </DashboardHeader>
      <DashboardSidebar />
      <main>{renderTabContent()}</main>
    </DashboardLayout>
  );
}
```

---

## PART 3: MULTI-AGENT DASHBOARD

### 3.1 Overview

The Multi-Agent Dashboard displays 6 agent cards in a responsive grid, each showing real-time data from the v13.2 backend.

### 3.2 Layout Specification

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

### 3.3 Implementation: AgentDashboard Component

**File**: `components/agents/AgentDashboard.tsx`

```typescript
'use client';

import { useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import {
  useAgentHealth,
  useDashboardData,
} from '@/hooks/useAgentData';
import { AssessmentAgentCard } from './cards/AssessmentAgentCard';
import { GamePlanAgentCard } from './cards/GamePlanAgentCard';
import { ExecutionAgentCard } from './cards/ExecutionAgentCard';
import { AwardsAgentCard } from './cards/AwardsAgentCard';
import { OpportunityAgentCard } from './cards/OpportunityAgentCard';
import { CrisisAgentCard } from './cards/CrisisAgentCard';
import { NotificationsPreview } from './NotificationsPreview';
import { ChatView } from './ChatView';

interface AgentDashboardProps {
  profileId: string | null;
}

type AgentType = 'narrative' | 'strategist' | 'academic' | 'awards' | 'opportunity';

export function AgentDashboard({ profileId }: AgentDashboardProps) {
  const [view, setView] = useState<'dashboard' | 'chat'>('dashboard');
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('narrative');

  const { data: health, isLoading: healthLoading } = useAgentHealth();
  const { refetchAll, isLoading } = useDashboardData(profileId);

  const handleAgentChat = (agent: AgentType) => {
    setSelectedAgent(agent);
    setView('chat');
  };

  if (view === 'chat') {
    return (
      <ChatView
        profileId={profileId}
        agent={selectedAgent}
        onBack={() => setView('dashboard')}
      />
    );
  }

  // No profileId - show limited state
  if (!profileId) {
    return (
      <div className="p-8" style={{ backgroundColor: BRAND_COLORS.bgPrimary }}>
        <div className="text-center py-12">
          <h2 style={{ color: BRAND_COLORS.textHeading }} className="text-xl font-semibold mb-2">
            Complete Your Assessment
          </h2>
          <p style={{ color: BRAND_COLORS.textMuted }}>
            Finish the IvyQuest assessment to unlock your personalized multi-agent coaching team.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6" style={{ backgroundColor: BRAND_COLORS.bgPrimary }}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ color: BRAND_COLORS.textHeading }}
          >
            Multi-Agent Dashboard
          </h1>
          <p style={{ color: BRAND_COLORS.textMuted }}>
            Your 6-agent coaching team working in parallel
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Health indicator */}
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                health?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              }`}
            />
            <span style={{ color: BRAND_COLORS.textMuted }} className="text-sm">
              {health?.status === 'healthy' ? 'Backend healthy' : 'Backend unavailable'}
            </span>
          </div>

          {/* Refresh all button */}
          <button
            onClick={() => refetchAll()}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
            style={{
              backgroundColor: BRAND_COLORS.primaryBg,
              color: BRAND_COLORS.primary,
              border: `1px solid ${BRAND_COLORS.primary}`,
            }}
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            Refresh All
          </button>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AssessmentAgentCard
          profileId={profileId}
          onChat={() => handleAgentChat('narrative')}
        />
        <GamePlanAgentCard
          profileId={profileId}
          onChat={() => handleAgentChat('strategist')}
        />
        <ExecutionAgentCard
          profileId={profileId}
          onChat={() => handleAgentChat('strategist')}
        />
        <AwardsAgentCard
          profileId={profileId}
          onChat={() => handleAgentChat('awards')}
        />
        <OpportunityAgentCard
          profileId={profileId}
          onChat={() => handleAgentChat('opportunity')}
        />
        <CrisisAgentCard profileId={profileId} />
      </div>

      {/* Notifications Preview */}
      <NotificationsPreview profileId={profileId} />
    </div>
  );
}
```

### 3.4 Implementation: Agent Card Template

**File**: `components/agents/cards/AgentCardBase.tsx`

```typescript
'use client';

import { ReactNode } from 'react';
import { RefreshCw, MessageSquare } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';

interface AgentCardBaseProps {
  title: string;
  icon: ReactNode;
  isLoading: boolean;
  isError: boolean;
  errorMessage?: string;
  onRefresh: () => void;
  onChat?: () => void;
  children: ReactNode;
  actions?: ReactNode;
}

export function AgentCardBase({
  title,
  icon,
  isLoading,
  isError,
  errorMessage,
  onRefresh,
  onChat,
  children,
  actions,
}: AgentCardBaseProps) {
  return (
    <div
      className="rounded-xl p-5 shadow-sm"
      style={{
        backgroundColor: '#ffffff',
        border: `1px solid ${BRAND_COLORS.borderLight}`,
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className="p-2 rounded-lg"
            style={{ backgroundColor: BRAND_COLORS.primaryBg }}
          >
            {icon}
          </div>
          <h3
            className="font-semibold"
            style={{ color: BRAND_COLORS.textHeading }}
          >
            {title}
          </h3>
        </div>

        {isLoading && (
          <RefreshCw
            size={16}
            className="animate-spin"
            style={{ color: BRAND_COLORS.textMuted }}
          />
        )}
      </div>

      {/* Content */}
      <div className="min-h-[120px]">
        {isError ? (
          <div className="text-center py-4">
            <p style={{ color: BRAND_COLORS.error }} className="text-sm">
              {errorMessage || 'Failed to load data'}
            </p>
            <button
              onClick={onRefresh}
              className="mt-2 text-sm underline"
              style={{ color: BRAND_COLORS.primary }}
            >
              Retry
            </button>
          </div>
        ) : (
          children
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 mt-4 pt-4 border-t" style={{ borderColor: BRAND_COLORS.borderLight }}>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors"
          style={{
            backgroundColor: BRAND_COLORS.bgSecondary,
            color: BRAND_COLORS.textPrimary,
          }}
        >
          <RefreshCw size={14} />
          Refresh
        </button>

        {onChat && (
          <button
            onClick={onChat}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors"
            style={{
              backgroundColor: BRAND_COLORS.primaryBg,
              color: BRAND_COLORS.primary,
            }}
          >
            <MessageSquare size={14} />
            Chat
          </button>
        )}

        {actions}
      </div>
    </div>
  );
}
```

### 3.5 Implementation: Assessment Agent Card

**File**: `components/agents/cards/AssessmentAgentCard.tsx`

```typescript
'use client';

import { Brain } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useNarrativeDNA } from '@/hooks/useAgentData';
import { AgentCardBase } from './AgentCardBase';

interface AssessmentAgentCardProps {
  profileId: string;
  onChat: () => void;
}

export function AssessmentAgentCard({ profileId, onChat }: AssessmentAgentCardProps) {
  const { data, isLoading, isError, refetch } = useNarrativeDNA(profileId);

  return (
    <AgentCardBase
      title="Assessment Agent"
      icon={<Brain size={20} style={{ color: BRAND_COLORS.primary }} />}
      isLoading={isLoading}
      isError={isError}
      onRefresh={() => refetch()}
      onChat={onChat}
    >
      {data && (
        <div className="space-y-3">
          <div>
            <p style={{ color: BRAND_COLORS.textMuted }} className="text-xs uppercase tracking-wide mb-1">
              Narrative DNA
            </p>
            <p style={{ color: BRAND_COLORS.textPrimary }} className="text-sm italic line-clamp-2">
              "{data.narrative_dna?.dna || 'Generating...'}"
            </p>
          </div>

          <div className="flex items-center justify-between">
            <span style={{ color: BRAND_COLORS.textMuted }} className="text-sm">
              Archetype
            </span>
            <span style={{ color: BRAND_COLORS.textHeading }} className="font-medium">
              {data.archetype?.label || 'Unknown'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span style={{ color: BRAND_COLORS.textMuted }} className="text-sm">
              Confidence
            </span>
            <div className="flex items-center gap-2">
              <div className="w-24 h-2 rounded-full bg-gray-200">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${(data.archetype?.confidence || 0) * 100}%`,
                    backgroundColor: BRAND_COLORS.success,
                  }}
                />
              </div>
              <span style={{ color: BRAND_COLORS.textPrimary }} className="text-sm">
                {Math.round((data.archetype?.confidence || 0) * 100)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </AgentCardBase>
  );
}
```

### 3.6 Additional Agent Cards (Summary)

| Card | Data Source | Key Metrics |
|------|-------------|-------------|
| **GamePlanAgentCard** | `useGamePlan(profileId)` | Activities count, Seeds count, Phases |
| **ExecutionAgentCard** | `useExecutionDebtScore(profileId)` | EDS score, Status, Blockers |
| **AwardsAgentCard** | `useAwardMatches(profileId)` | Likely/Target/Stretch, Expected Wins |
| **OpportunityAgentCard** | `useOpportunityAlerts(profileId)` | Matches, Urgent Alerts, Deadlines |
| **CrisisAgentCard** | Internal state | Report Crisis button, Active crises |

---

## PART 4: CRISIS ALCHEMY UI

### 4.1 Overview

Crisis Alchemy is the HITL (Human-in-the-Loop) workflow for handling student crises. The UI provides:
1. Crisis report modal for students to report issues
2. Crisis response display showing the 4-step VARC process
3. HITL approval flow for coach review

### 4.2 Crisis Types

```typescript
const CRISIS_TYPES = [
  {
    id: 'blocker',
    label: 'Project Blocked',
    description: "Can't make progress on something",
    icon: XCircle,
  },
  {
    id: 'rejection',
    label: 'Rejection/Setback',
    description: 'Award, program, or application rejection',
    icon: ThumbsDown,
  },
  {
    id: 'overwhelm',
    label: 'Feeling Overwhelmed',
    description: 'Too much to do, losing motivation',
    icon: AlertTriangle,
  },
  {
    id: 'deadline',
    label: 'Deadline Panic',
    description: 'Important deadline approaching fast',
    icon: Clock,
  },
  {
    id: 'doubt',
    label: 'Self-Doubt',
    description: 'Questioning direction or capabilities',
    icon: HelpCircle,
  },
];
```

### 4.3 Implementation: Crisis Report Modal

**File**: `components/agents/CrisisReportModal.tsx`

```typescript
'use client';

import { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useCrisisHandler } from '@/hooks/useAgentData';
import { CrisisResponseDisplay } from './CrisisResponseDisplay';

interface CrisisReportModalProps {
  profileId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function CrisisReportModal({ profileId, isOpen, onClose }: CrisisReportModalProps) {
  const [crisisType, setCrisisType] = useState<string>('');
  const [description, setDescription] = useState('');
  const [urgency, setUrgency] = useState(3);
  const [step, setStep] = useState<'report' | 'response'>('report');

  const { mutate: handleCrisis, data: crisisResponse, isPending } = useCrisisHandler();

  const handleSubmit = async () => {
    handleCrisis({
      profile_id: profileId,
      crisis_type: crisisType,
      description,
      urgency,
    }, {
      onSuccess: () => setStep('response'),
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className="relative w-full max-w-lg mx-4 rounded-xl shadow-xl max-h-[90vh] overflow-y-auto"
        style={{ backgroundColor: '#ffffff' }}
      >
        {/* Header */}
        <div
          className="sticky top-0 flex items-center justify-between p-4 border-b"
          style={{
            backgroundColor: '#ffffff',
            borderColor: BRAND_COLORS.borderLight,
          }}
        >
          <div className="flex items-center gap-2">
            <AlertTriangle size={20} style={{ color: BRAND_COLORS.warning }} />
            <h2 style={{ color: BRAND_COLORS.textHeading }} className="font-semibold">
              {step === 'report' ? 'Report a Crisis' : 'Crisis Response'}
            </h2>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-gray-100">
            <X size={20} style={{ color: BRAND_COLORS.textMuted }} />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          {step === 'report' ? (
            <CrisisReportForm
              crisisType={crisisType}
              setCrisisType={setCrisisType}
              description={description}
              setDescription={setDescription}
              urgency={urgency}
              setUrgency={setUrgency}
              onSubmit={handleSubmit}
              isLoading={isPending}
            />
          ) : (
            <CrisisResponseDisplay
              response={crisisResponse}
              onClose={onClose}
            />
          )}
        </div>
      </div>
    </div>
  );
}
```

### 4.4 Implementation: Crisis Response Display

**File**: `components/agents/CrisisResponseDisplay.tsx`

```typescript
'use client';

import { CheckCircle, Clock, Lightbulb, Sparkles } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { CrisisResponse } from '@/lib/types/agents';

interface CrisisResponseDisplayProps {
  response: CrisisResponse;
  onClose: () => void;
}

export function CrisisResponseDisplay({ response, onClose }: CrisisResponseDisplayProps) {
  if (!response?.success) {
    return (
      <div className="text-center py-8">
        <p style={{ color: BRAND_COLORS.error }}>
          Failed to generate crisis response. Please try again.
        </p>
      </div>
    );
  }

  const steps = [
    {
      key: 'validate',
      title: 'Validate (2s)',
      icon: CheckCircle,
      color: BRAND_COLORS.success,
      content: response.steps.validate.message,
    },
    {
      key: 'act',
      title: 'Act (10s)',
      icon: Clock,
      color: BRAND_COLORS.primary,
      content: `${response.steps.act.action} (${response.steps.act.time_required})`,
    },
    {
      key: 'reframe',
      title: 'Reframe (30s)',
      icon: Lightbulb,
      color: BRAND_COLORS.warning,
      content: response.steps.reframe.opportunity,
    },
    {
      key: 'create',
      title: 'Create (2min)',
      icon: Sparkles,
      color: BRAND_COLORS.secondary,
      content: response.steps.create.new_activity,
    },
  ];

  return (
    <div className="space-y-4">
      {/* VARC Steps */}
      {steps.map((step, index) => (
        <div
          key={step.key}
          className="p-4 rounded-lg"
          style={{ backgroundColor: BRAND_COLORS.bgSecondary }}
        >
          <div className="flex items-center gap-2 mb-2">
            <step.icon size={18} style={{ color: step.color }} />
            <span className="font-medium" style={{ color: BRAND_COLORS.textHeading }}>
              {step.title}
            </span>
          </div>
          <p style={{ color: BRAND_COLORS.textPrimary }} className="text-sm">
            {step.content}
          </p>
        </div>
      ))}

      {/* HITL Notice */}
      {response.requires_handoff && (
        <div
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: BRAND_COLORS.warningBg,
            borderColor: BRAND_COLORS.warning,
          }}
        >
          <p style={{ color: BRAND_COLORS.textHeading }} className="font-medium text-sm">
            Pending Coach Review
          </p>
          <p style={{ color: BRAND_COLORS.textMuted }} className="text-sm mt-1">
            {response.handoff_reason || 'This response requires approval from your coach before taking action.'}
          </p>
        </div>
      )}

      {/* Close Button */}
      <button
        onClick={onClose}
        className="w-full py-3 rounded-lg font-medium"
        style={{
          backgroundColor: BRAND_COLORS.primary,
          color: '#ffffff',
        }}
      >
        Got It
      </button>
    </div>
  );
}
```

---

## PART 5: NOTIFICATION SYSTEM

### 5.1 Notification Types

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

### 5.2 Implementation: Notification Bell

**File**: `components/shared/NotificationBell.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Bell } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useNotifications, useNotificationCount } from '@/hooks/useAgentData';
import { NotificationPanel } from './NotificationPanel';

interface NotificationBellProps {
  profileId: string | null;
}

export function NotificationBell({ profileId }: NotificationBellProps) {
  const [isOpen, setIsOpen] = useState(false);

  const { data: countData } = useNotificationCount(profileId);
  const { data: notifications, refetch } = useNotifications(profileId);

  const unreadCount = countData?.unread_count || 0;

  if (!profileId) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <Bell size={20} style={{ color: BRAND_COLORS.textPrimary }} />

        {unreadCount > 0 && (
          <span
            className="absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center text-xs font-medium rounded-full"
            style={{
              backgroundColor: BRAND_COLORS.error,
              color: '#ffffff',
            }}
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      <NotificationPanel
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        notifications={notifications || []}
        onRefresh={refetch}
        profileId={profileId}
      />
    </div>
  );
}
```

### 5.3 Implementation: Notification Panel

**File**: `components/shared/NotificationPanel.tsx`

```typescript
'use client';

import { useRef, useEffect } from 'react';
import { X, Clock, Award, AlertTriangle, CheckCircle } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';
import { useMarkNotificationRead } from '@/hooks/useAgentData';

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: Notification[];
  onRefresh: () => void;
  profileId: string;
}

export function NotificationPanel({
  isOpen,
  onClose,
  notifications,
  onRefresh,
  profileId,
}: NotificationPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const { mutate: markRead } = useMarkNotificationRead();

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'deadline_high':
      case 'urgent':
        return <AlertTriangle size={16} style={{ color: BRAND_COLORS.error }} />;
      case 'deadline_medium':
      case 'deadline_low':
        return <Clock size={16} style={{ color: BRAND_COLORS.warning }} />;
      case 'award_match':
      case 'opportunity_match':
        return <Award size={16} style={{ color: BRAND_COLORS.success }} />;
      case 'milestone_complete':
        return <CheckCircle size={16} style={{ color: BRAND_COLORS.success }} />;
      default:
        return <Clock size={16} style={{ color: BRAND_COLORS.textMuted }} />;
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markRead({ profileId, notificationId: notification.id });
    }
  };

  return (
    <div
      ref={panelRef}
      className="absolute right-0 top-full mt-2 w-80 rounded-xl shadow-lg z-50"
      style={{
        backgroundColor: '#ffffff',
        border: `1px solid ${BRAND_COLORS.borderLight}`,
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between p-3 border-b"
        style={{ borderColor: BRAND_COLORS.borderLight }}
      >
        <h3 style={{ color: BRAND_COLORS.textHeading }} className="font-semibold">
          Notifications
        </h3>
        <button onClick={onClose} className="p-1 rounded hover:bg-gray-100">
          <X size={16} style={{ color: BRAND_COLORS.textMuted }} />
        </button>
      </div>

      {/* Notifications List */}
      <div className="max-h-96 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="p-6 text-center">
            <p style={{ color: BRAND_COLORS.textMuted }} className="text-sm">
              No notifications yet
            </p>
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              onClick={() => handleNotificationClick(notification)}
              className="p-3 border-b cursor-pointer hover:bg-gray-50 transition-colors"
              style={{
                borderColor: BRAND_COLORS.borderLight,
                backgroundColor: notification.read ? 'transparent' : BRAND_COLORS.primaryBg,
              }}
            >
              <div className="flex gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getNotificationIcon(notification.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p
                    className="font-medium text-sm"
                    style={{ color: BRAND_COLORS.textHeading }}
                  >
                    {notification.title}
                  </p>
                  <p
                    className="text-sm mt-0.5 line-clamp-2"
                    style={{ color: BRAND_COLORS.textMuted }}
                  >
                    {notification.message}
                  </p>
                  <p
                    className="text-xs mt-1"
                    style={{ color: BRAND_COLORS.textMuted }}
                  >
                    {formatRelativeTime(notification.created_at)}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}
```

---

## PART 6: API CLIENT INTEGRATION

### 6.1 v13 Agent Client

**File**: `lib/api/agentV13Client.ts`

```typescript
// IvyQuest v13.3 Agent API Client
// Connects frontend to v13.2 Python backend

const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8001';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${AGENT_API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: errorData.detail || `HTTP ${response.status}`,
      };
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

export const agentV13Api = {
  // ============ HEALTH ============
  async checkHealth() {
    return fetchApi<{
      status: string;
      version: string;
      react_enabled: boolean;
      memory_enabled: boolean;
      thresholds: {
        min_quality: number;
        min_voice: number;
        min_golden: number;
        max_cycles: number;
      };
    }>('/v13/health');
  },

  // ============ ASSESSMENT ============
  async getNarrativeDNA(profileId: string) {
    return fetchApi<{
      narrative_dna: { dna: string; themes: string[]; confidence: number };
      archetype: { id: string; label: string; confidence: number };
    }>(`/agents/narrative/${profileId}`);
  },

  async synthesizeNarrative(profileId: string, force = false) {
    return fetchApi(`/agents/narrative/synthesize`, {
      method: 'POST',
      body: JSON.stringify({ profile_id: profileId, force_refresh: force }),
    });
  },

  // ============ GAMEPLAN ============
  async getGamePlan(profileId: string) {
    return fetchApi(`/agents/gameplan/generate`, {
      method: 'POST',
      body: JSON.stringify({ profile_id: profileId }),
    });
  },

  async getFilteredActivities(profileId: string) {
    return fetchApi(`/agents/gameplan/activities/${profileId}`);
  },

  async getIdentitySeeds(profileId: string) {
    return fetchApi(`/agents/gameplan/seeds/${profileId}`);
  },

  // ============ EXECUTION ============
  async getExecutionDebtScore(profileId: string) {
    return fetchApi<{
      profile_id: string;
      execution_debt_score: number;
      status: 'healthy' | 'at_risk' | 'critical';
      contributing_factors: string[];
    }>(`/agents/execution/eds/${profileId}`);
  },

  async handleCrisis(input: {
    profile_id: string;
    crisis_type: string;
    description: string;
    urgency: number;
  }) {
    return fetchApi(`/agents/execution/crisis`, {
      method: 'POST',
      body: JSON.stringify(input),
    });
  },

  async approveHandoff(crisisId: string, approved: boolean, rationale?: string) {
    return fetchApi(`/agents/handoff/approve`, {
      method: 'POST',
      body: JSON.stringify({ crisis_id: crisisId, approved, rationale }),
    });
  },

  // ============ AWARDS ============
  async getAwardMatches(profileId: string) {
    return fetchApi(`/agents/awards/match/${profileId}`);
  },

  async getAwardPortfolio(profileId: string) {
    return fetchApi(`/agents/awards/portfolio/${profileId}`);
  },

  async getAwardTimeline(profileId: string) {
    return fetchApi(`/agents/awards/timeline/${profileId}`);
  },

  // ============ OPPORTUNITIES ============
  async getOpportunityMatches(profileId: string) {
    return fetchApi(`/agents/opportunities/match/${profileId}`);
  },

  async getOpportunityAlerts(profileId: string) {
    return fetchApi<{
      alerts: Array<{
        alert_id: string;
        type: string;
        opportunity_name: string;
        deadline: string;
        urgency: string;
      }>;
      count: number;
      urgent_count: number;
    }>(`/agents/opportunities/alerts/${profileId}`);
  },

  async getOpportunityTimeline(profileId: string) {
    return fetchApi(`/agents/opportunities/timeline/${profileId}`);
  },

  // ============ MEMORY (v13.2) ============
  async getHandoff(profileId: string, toAgent: string) {
    return fetchApi(`/v13/memory/handoff/${profileId}/${toAgent}`);
  },

  async searchKnowledge(query: string, limit = 5) {
    return fetchApi(`/v13/knowledge/search?query=${encodeURIComponent(query)}&limit=${limit}`);
  },

  async getProfileEvolution(profileId: string, days = 90) {
    return fetchApi(`/v13/profile/${profileId}/evolution?days=${days}`);
  },

  async recallInteractions(profileId: string, query: string, limit = 5) {
    return fetchApi(
      `/v13/interactions/${profileId}/recall?query=${encodeURIComponent(query)}&limit=${limit}`
    );
  },

  async getRecentInteractions(profileId: string, limit = 10) {
    return fetchApi(`/v13/interactions/${profileId}/recent?limit=${limit}`);
  },

  // ============ NOTIFICATIONS ============
  async getNotifications(profileId: string) {
    return fetchApi(`/notifications/${profileId}`);
  },

  async getNotificationCount(profileId: string) {
    return fetchApi<{ unread_count: number }>(`/notifications/${profileId}/count`);
  },

  async markNotificationRead(profileId: string, notificationId: string) {
    return fetchApi(`/notifications/mark-read`, {
      method: 'POST',
      body: JSON.stringify({ profile_id: profileId, notification_id: notificationId }),
    });
  },
};
```

### 6.2 React Query Hooks

**File**: `hooks/useAgentData.ts` (Enhanced for v13.3)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentV13Api } from '@/lib/api/agentV13Client';

// ============ HEALTH ============
export function useAgentHealth() {
  return useQuery({
    queryKey: ['agent-health'],
    queryFn: async () => {
      const result = await agentV13Api.checkHealth();
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    staleTime: 30_000, // 30 seconds
    refetchInterval: 60_000, // 1 minute
  });
}

// ============ ASSESSMENT ============
export function useNarrativeDNA(profileId: string | null) {
  return useQuery({
    queryKey: ['narrative-dna', profileId],
    queryFn: async () => {
      if (!profileId) throw new Error('No profile ID');
      const result = await agentV13Api.getNarrativeDNA(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    enabled: !!profileId,
    staleTime: 5 * 60_000, // 5 minutes
  });
}

// ============ GAMEPLAN ============
export function useGamePlan(profileId: string | null) {
  return useQuery({
    queryKey: ['game-plan', profileId],
    queryFn: async () => {
      if (!profileId) throw new Error('No profile ID');
      const result = await agentV13Api.getGamePlan(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    enabled: !!profileId,
    staleTime: 10 * 60_000, // 10 minutes
  });
}

// ============ EXECUTION ============
export function useExecutionDebtScore(profileId: string | null) {
  return useQuery({
    queryKey: ['eds', profileId],
    queryFn: async () => {
      if (!profileId) throw new Error('No profile ID');
      const result = await agentV13Api.getExecutionDebtScore(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    enabled: !!profileId,
    staleTime: 5 * 60_000,
  });
}

export function useCrisisHandler() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: {
      profile_id: string;
      crisis_type: string;
      description: string;
      urgency: number;
    }) => {
      const result = await agentV13Api.handleCrisis(input);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['eds', variables.profile_id] });
      queryClient.invalidateQueries({ queryKey: ['notifications', variables.profile_id] });
    },
  });
}

// ============ AWARDS ============
export function useAwardMatches(profileId: string | null) {
  return useQuery({
    queryKey: ['award-matches', profileId],
    queryFn: async () => {
      if (!profileId) throw new Error('No profile ID');
      const [matches, portfolio, timeline] = await Promise.all([
        agentV13Api.getAwardMatches(profileId),
        agentV13Api.getAwardPortfolio(profileId),
        agentV13Api.getAwardTimeline(profileId),
      ]);
      return {
        matches: matches.data,
        portfolio: portfolio.data,
        timeline: timeline.data,
      };
    },
    enabled: !!profileId,
    staleTime: 15 * 60_000, // 15 minutes
  });
}

// ============ OPPORTUNITIES ============
export function useOpportunityAlerts(profileId: string | null) {
  return useQuery({
    queryKey: ['opportunity-alerts', profileId],
    queryFn: async () => {
      if (!profileId) throw new Error('No profile ID');
      const result = await agentV13Api.getOpportunityAlerts(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    enabled: !!profileId,
    staleTime: 5 * 60_000,
  });
}

// ============ NOTIFICATIONS ============
export function useNotifications(profileId: string | null) {
  return useQuery({
    queryKey: ['notifications', profileId],
    queryFn: async () => {
      if (!profileId) throw new Error('No profile ID');
      const result = await agentV13Api.getNotifications(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    enabled: !!profileId,
    staleTime: 30_000, // 30 seconds
    refetchInterval: 60_000, // 1 minute
  });
}

export function useNotificationCount(profileId: string | null) {
  return useQuery({
    queryKey: ['notification-count', profileId],
    queryFn: async () => {
      if (!profileId) throw new Error('No profile ID');
      const result = await agentV13Api.getNotificationCount(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    enabled: !!profileId,
    staleTime: 30_000,
    refetchInterval: 30_000, // More frequent for count
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ profileId, notificationId }: { profileId: string; notificationId: string }) => {
      const result = await agentV13Api.markNotificationRead(profileId, notificationId);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['notifications', variables.profileId] });
      queryClient.invalidateQueries({ queryKey: ['notification-count', variables.profileId] });
    },
  });
}

// ============ DASHBOARD DATA (Combined) ============
export function useDashboardData(profileId: string | null) {
  const queryClient = useQueryClient();

  const narrativeDNA = useNarrativeDNA(profileId);
  const gamePlan = useGamePlan(profileId);
  const eds = useExecutionDebtScore(profileId);
  const awards = useAwardMatches(profileId);
  const opportunities = useOpportunityAlerts(profileId);

  const isLoading =
    narrativeDNA.isLoading ||
    gamePlan.isLoading ||
    eds.isLoading ||
    awards.isLoading ||
    opportunities.isLoading;

  const refetchAll = () => {
    if (!profileId) return;

    queryClient.invalidateQueries({ queryKey: ['narrative-dna', profileId] });
    queryClient.invalidateQueries({ queryKey: ['game-plan', profileId] });
    queryClient.invalidateQueries({ queryKey: ['eds', profileId] });
    queryClient.invalidateQueries({ queryKey: ['award-matches', profileId] });
    queryClient.invalidateQueries({ queryKey: ['opportunity-alerts', profileId] });
  };

  return {
    narrativeDNA,
    gamePlan,
    eds,
    awards,
    opportunities,
    isLoading,
    refetchAll,
  };
}
```

---

## PART 7: TESTING GUIDE

### 7.1 Test Environment Setup

```bash
# Prerequisites
# 1. Python agent service running on port 8001
# 2. Next.js app running on port 3000
# 3. Supabase database with v13.2 migrations applied
# 4. Redis running for short-term memory

# Environment Variables (.env.local)
NEXT_PUBLIC_AGENT_API_URL=http://localhost:8001
NEXT_PUBLIC_SUPABASE_URL=<your-url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-key>

# Start Services
cd agents && python main.py  # Terminal 1
npm run dev                  # Terminal 2
```

### 7.2 Test Suite: Profile ID Infrastructure

| TC# | Test Case | Steps | Expected Result |
|-----|-----------|-------|-----------------|
| TC-001 | Profile creation on assessment complete | 1. Complete Frames 1-6<br>2. Click "View Dashboard" | Profile record created in Supabase with user_id |
| TC-002 | ProfileId stored in session | 1. Complete assessment<br>2. Check localStorage | `ivyquest-session` contains `profile_id` |
| TC-003 | ProfileId retrieval on dashboard load | 1. Navigate directly to /dashboard<br>2. Wait for load | ProfileId fetched from Supabase |
| TC-004 | ProfileId passed to MultiAgentTab | 1. Open Dashboard<br>2. Click Multi-Agents tab | Agent cards load with data |

### 7.3 Test Suite: Multi-Agent Dashboard

| TC# | Test Case | Steps | Expected Result |
|-----|-----------|-------|-----------------|
| TC-010 | Dashboard header health indicator | 1. Navigate to Multi-Agents tab | Green "Backend healthy" indicator visible |
| TC-011 | Refresh All button | 1. Click "Refresh All"<br>2. Wait for completion | All 6 cards refresh simultaneously |
| TC-012 | Assessment Agent card data | 1. View Assessment Agent card | Narrative DNA, Archetype, Confidence displayed |
| TC-013 | GamePlan Agent card data | 1. View GamePlan Agent card | Activities count, Seeds count, Phases visible |
| TC-014 | Execution Agent card data | 1. View Execution Agent card | EDS score, Status indicator visible |
| TC-015 | Awards Agent card data | 1. View Awards Agent card | Likely/Target/Stretch counts, Expected Wins |
| TC-016 | Opportunity Agent card data | 1. View Opportunity Agent card | Matches count, Urgent Alerts count |
| TC-017 | Agent card refresh | 1. Click "Refresh" on any card | Card data updates |
| TC-018 | Agent card chat | 1. Click "Chat" on any card | Chat view opens with agent selected |

### 7.4 Test Suite: Crisis Alchemy

| TC# | Test Case | Steps | Expected Result |
|-----|-----------|-------|-----------------|
| TC-030 | Crisis report modal open | 1. Click "Report Crisis" on Crisis card | Modal opens |
| TC-031 | Crisis type selection | 1. Open modal<br>2. Select "Rejection/Setback" | Type highlighted, description shown |
| TC-032 | Crisis description input | 1. Enter description text | Text appears in input |
| TC-033 | Urgency slider | 1. Move urgency slider | Value updates (1-5) |
| TC-034 | Crisis submission | 1. Fill form<br>2. Click Submit | Loading state, then response displayed |
| TC-035 | VARC response display | 1. Submit crisis | 4 steps shown: Validate, Act, Reframe, Create |
| TC-036 | HITL notice | 1. Submit high-urgency crisis | "Pending Coach Review" notice visible |

### 7.5 Test Suite: Notifications

| TC# | Test Case | Steps | Expected Result |
|-----|-----------|-------|-----------------|
| TC-050 | Notification bell visible | 1. Navigate to dashboard | Bell icon in header |
| TC-051 | Unread count badge | 1. Check bell icon | Badge shows unread count (or hidden if 0) |
| TC-052 | Notification panel open | 1. Click bell icon | Panel slides open |
| TC-053 | Notification list | 1. Open panel | List of notifications with icons |
| TC-054 | Mark as read | 1. Click notification | Notification marked read, count updates |
| TC-055 | Empty state | 1. Open panel with no notifications | "No notifications yet" message |

### 7.6 Test Suite: Error Handling

| TC# | Test Case | Steps | Expected Result |
|-----|-----------|-------|-----------------|
| TC-070 | Agent service down | 1. Stop agent service<br>2. Navigate to Multi-Agents | "Backend unavailable" indicator |
| TC-071 | Network timeout | 1. Throttle network<br>2. Refresh card | Loading spinner, then error with retry |
| TC-072 | Invalid profile ID | 1. Clear session storage<br>2. Navigate to dashboard | Graceful fallback, no crash |
| TC-073 | API error response | 1. Trigger 500 error | Error message displayed, retry available |

### 7.7 Performance Benchmarks

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Dashboard initial load | < 2s | Time to first paint |
| All agent cards populated | < 5s | Time until all cards show data |
| Full refresh | < 8s | Time for Refresh All to complete |
| Notification count fetch | < 500ms | API response time |
| Crisis submission | < 3s | Time to show response |

---

## PART 8: FILE MANIFEST

### 8.1 Files to CREATE (New in v13.3)

| File Path | Description |
|-----------|-------------|
| `components/agents/AgentDashboard.tsx` | Main dashboard component |
| `components/agents/cards/AgentCardBase.tsx` | Base card template |
| `components/agents/cards/AssessmentAgentCard.tsx` | Assessment agent card |
| `components/agents/cards/GamePlanAgentCard.tsx` | GamePlan agent card |
| `components/agents/cards/ExecutionAgentCard.tsx` | Execution agent card |
| `components/agents/cards/AwardsAgentCard.tsx` | Awards agent card |
| `components/agents/cards/OpportunityAgentCard.tsx` | Opportunity agent card |
| `components/agents/cards/CrisisAgentCard.tsx` | Crisis agent card |
| `components/agents/CrisisReportModal.tsx` | Crisis report modal |
| `components/agents/CrisisResponseDisplay.tsx` | VARC response display |
| `components/agents/ChatView.tsx` | Agent chat interface |
| `components/agents/NotificationsPreview.tsx` | Dashboard notifications section |
| `components/shared/NotificationBell.tsx` | Header notification bell |
| `components/shared/NotificationPanel.tsx` | Notification dropdown panel |
| `lib/api/agentV13Client.ts` | v13 API client |

### 8.2 Files to UPDATE (Enhanced in v13.3)

| File Path | Changes |
|-----------|---------|
| `lib/store/useSessionStore.ts` | Add profile_id, profile_status |
| `components/frames/Frame6ProfileReveal.tsx` | Add profile creation on complete |
| `app/dashboard/page.tsx` | Add profileId retrieval, pass to tabs |
| `components/tabs/MultiAgentsTab.tsx` | Wire to AgentDashboard |
| `hooks/useAgentData.ts` | Add v13 hooks |
| `lib/types/agents.ts` | Add Notification type |

### 8.3 Component Dependencies

```
AgentDashboard
├── AgentCardBase
│   ├── AssessmentAgentCard → useNarrativeDNA
│   ├── GamePlanAgentCard → useGamePlan
│   ├── ExecutionAgentCard → useExecutionDebtScore
│   ├── AwardsAgentCard → useAwardMatches
│   ├── OpportunityAgentCard → useOpportunityAlerts
│   └── CrisisAgentCard → useCrisisHandler
├── ChatView
├── NotificationsPreview → useNotifications
└── CrisisReportModal → CrisisResponseDisplay
```

---

## PART 9: IMPLEMENTATION CHECKLIST

### Phase 1: Infrastructure (P0)
- [ ] Add `profile_id` to `useSessionStore`
- [ ] Create profile record on assessment complete
- [ ] Retrieve profileId on dashboard mount
- [ ] Pass profileId to all dashboard tabs

### Phase 2: Multi-Agent Dashboard (P0)
- [ ] Create AgentCardBase component
- [ ] Implement all 6 agent cards
- [ ] Create AgentDashboard layout
- [ ] Wire MultiAgentsTab to AgentDashboard
- [ ] Implement Refresh All functionality

### Phase 3: Crisis Alchemy (P1)
- [ ] Create CrisisReportModal
- [ ] Implement crisis type selection
- [ ] Create CrisisResponseDisplay
- [ ] Add HITL notice for high-stakes responses

### Phase 4: Notifications (P1)
- [ ] Create NotificationBell component
- [ ] Create NotificationPanel component
- [ ] Add to dashboard header
- [ ] Implement mark as read

### Phase 5: API Client (P0)
- [ ] Create agentV13Client.ts
- [ ] Add all v13 endpoints
- [ ] Create React Query hooks
- [ ] Implement error handling

### Phase 6: Testing (P2)
- [ ] Test profile ID flow
- [ ] Test all agent cards
- [ ] Test crisis workflow
- [ ] Test notifications
- [ ] Test error states

---

## APPENDIX A: Version Comparison

| Feature | v13.2 | v13.3 |
|---------|-------|-------|
| Backend: ReAct Framework | Complete | Complete |
| Backend: Memory System | Complete | Complete |
| Backend: HITL Workflow | Complete | Complete |
| Frontend: Profile Infrastructure | Partial | Complete |
| Frontend: Multi-Agent Dashboard | Placeholder | Complete |
| Frontend: Crisis Alchemy UI | None | Complete |
| Frontend: Notification System | None | Complete |
| Frontend: API Integration | Partial | Complete |
| Full-Stack Integration | Incomplete | Complete |

---

## APPENDIX B: Brand Colors Reference

```typescript
// lib/constants/brand.ts
export const BRAND_COLORS = {
  // Primary
  primary: '#FF4A23',        // Ivylevel orange
  primaryBg: 'rgba(255, 74, 35, 0.1)',

  // Secondary
  secondary: '#641432',      // Ivylevel maroon

  // Text
  textHeading: '#641432',    // Maroon
  textPrimary: '#374151',    // Gray-700
  textMuted: '#9ca3af',      // Gray-400

  // Background
  bgPrimary: 'rgba(255, 255, 255, 0.95)',
  bgSecondary: '#f9fafb',    // Gray-50

  // Status
  success: '#16a34a',        // Green-600
  warning: '#d97706',        // Amber-600
  error: '#dc2626',          // Red-600

  // Borders
  borderLight: '#e5e7eb',    // Gray-200
  borderDefault: '#d1d5db',  // Gray-300
};
```

---

*PRD v13.3 - Frontend UI/UX Integration*
*Full-Stack Integration Complete*
*Date: January 11, 2026*
