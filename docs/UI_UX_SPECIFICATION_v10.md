# IvyQuest v10.0 UI/UX Integration Specification

**Version:** 1.0.0
**Date:** December 24, 2024
**Status:** Detailed Spec - Ready for Review

---

## Table of Contents

1. [Part 1: Current v2.2 UI/UX Flow](#part-1-current-v22-uiux-flow)
2. [Part 2: v10.0 UI Components & Features](#part-2-v100-ui-components--features)
3. [Part 3: Integration Plan & Code Changes](#part-3-integration-plan--code-changes)

---

# Part 1: Current v2.2 UI/UX Flow

## 1.1 File System Structure (v2.2 UI Components)

```
/Users/snazir/ivyquest-claude-v2.2/
├── app/
│   ├── quest/
│   │   └── [frameId]/
│   │       └── page.tsx              # Frame routing (1-6)
│   ├── results/
│   │   └── page.tsx                  # Results/completion page
│   └── layout.tsx                    # Root layout
│
├── components/
│   ├── frames/                       # Main frame components
│   │   ├── Frame1Warmup.tsx          # Welcome & name input
│   │   ├── Frame2Snapshot.tsx        # Quick profile capture
│   │   ├── Frame3Building.tsx        # Academic & activity details
│   │   ├── Frame4Context.tsx         # Context & demographics
│   │   ├── Frame5GamePlan.tsx        # Personalized game plan
│   │   ├── Frame6ProfileReveal.tsx   # Profile overview & scores
│   │   ├── Frame4Operating.tsx       # (Alternative) Operating mode
│   │   ├── Frame4Reveal.tsx          # (Alternative) Reveal mode
│   │   ├── Frame5Reveal.tsx          # (Alternative) Detailed reveal
│   │   ├── Frame5PowerUps.tsx        # Power-ups display
│   │   ├── Frame6PowerUps.tsx        # Additional power-ups
│   │   ├── operating/                # Operating sub-cards
│   │   │   ├── Card1Scenarios.tsx
│   │   │   ├── Card2TimeEnergy.tsx
│   │   │   └── Card3HiddenCapabilities.tsx
│   │   ├── reveal/                   # Reveal sub-cards
│   │   │   ├── Card1LaunchSequence.tsx
│   │   │   ├── Card2DualScore.tsx
│   │   │   ├── Card3SchoolCards.tsx
│   │   │   └── Card4CategoryBreakdown.tsx
│   │   └── powerups/                 # Power-up sub-cards
│   │       ├── ActionPlan.tsx
│   │       ├── BoosterCard.tsx
│   │       └── ImpactMeter.tsx
│   │
│   ├── quest/                        # Quest orchestration
│   │   ├── QuestContainer.tsx        # Main container & frame config
│   │   ├── HUD.tsx                   # Heads-up display
│   │   ├── Timeline.tsx              # Progress timeline
│   │   └── DualScoreDisplay.tsx      # Score visualization
│   │
│   ├── layout/                       # Layout components
│   │   ├── AssessmentLayout.tsx      # Assessment wrapper
│   │   └── SplitFrameLayout.tsx      # 2-column layout
│   │
│   ├── insights/                     # Insight display
│   │   ├── InsightsPanel.tsx         # Main insights panel
│   │   ├── InsightsProvider.tsx      # Context provider
│   │   ├── ContextualInsightCard.tsx # Contextual insights
│   │   ├── IvyInsightCard.tsx        # Ivy-specific insights
│   │   ├── NotificationInsightCard.tsx # Notification style
│   │   └── LoadingInsight.tsx        # Loading state
│   │
│   ├── rings/                        # Score visualization
│   │   └── CircularProgress.tsx      # Circular progress rings
│   │
│   ├── booking/                      # Coach booking
│   │   └── CoachBooking.tsx          # Calendly integration
│   │
│   ├── common/                       # Shared components
│   │   ├── DroneAssistant.tsx        # AI assistant panel
│   │   └── ClearStaleData.tsx        # Data cleanup
│   │
│   └── ui/                           # Base UI primitives
│       ├── Button.tsx
│       ├── Card.tsx
│       ├── ChipSelector.tsx
│       ├── CollegeLogo.tsx
│       ├── HighlightedText.tsx
│       ├── Input.tsx
│       ├── Modal.tsx
│       ├── Progress.tsx
│       ├── ScoreRing.tsx
│       ├── Select.tsx
│       ├── Slider.tsx
│       ├── SliderInput.tsx
│       ├── Toast.tsx
│       └── VoiceInput.tsx
```

---

## 1.2 Frame-by-Frame Flow Analysis

### Frame 1: Warmup (`Frame1Warmup.tsx`)

**Purpose:** Welcome screen with personal greeting and name capture

**UI Components:**
- Hero section with branded heading
- Name input field (required)
- Animated entry with Framer Motion
- Continue button (disabled until name entered)

**Data Captured:**
- `profile.identity.name` - Student's name

**Visual Elements:**
- Gradient background (coral/peach tones)
- DroneAssistant panel on right (desktop)
- Split layout on larger screens

**User Flow:**
```
[Landing] → Enter Name → [Continue Button] → Frame 2
```

---

### Frame 2: Snapshot (`Frame2Snapshot.tsx`)

**Purpose:** Quick profile snapshot - grade level, school type, GPA

**UI Components:**
- Grade level selector (chips: 9th, 10th, 11th, 12th)
- School type selector (Public, Private, Charter, Homeschool)
- GPA input (slider or text input)
- Test score inputs (SAT/ACT optional)
- Quick activity count

**Data Captured:**
- `profile.identity.grade` - Current grade
- `profile.identity.school_type` - Type of school
- `profile.aptitude.gpa_unweighted` - Unweighted GPA
- `profile.aptitude.gpa_weighted` - Weighted GPA (optional)
- `profile.aptitude.sat_total` - SAT score (optional)
- `profile.aptitude.act_total` - ACT score (optional)

**Visual Elements:**
- Card-based layout
- Real-time validation feedback
- Progress indicator in HUD
- InsightsPanel showing real-time analysis

**User Flow:**
```
[Grade Selection] → [School Type] → [GPA Entry] → [Test Scores] → [Continue] → Frame 3
```

---

### Frame 3: Building (`Frame3Building.tsx`)

**Purpose:** Deep dive into activities, leadership, awards

**UI Components:**
- Activity type selector (Sports, Arts, Academic, Service, etc.)
- EC commitment years slider (1-4+ years)
- Leadership level selector (Participant → Founder/President)
- Awards/honors multi-select
- AP/Honors course count
- Service hours input

**Data Captured:**
- `profile.passion.ec_types` - Array of activity types
- `profile.passion.ec_commitment_years` - Years of commitment
- `profile.passion.leadership_level` - Leadership tier
- `profile.passion.ec_awards` - Array of awards
- `profile.aptitude.ap_count` - Number of AP courses
- `profile.community.service_hours` - Volunteer hours

**Visual Elements:**
- Multi-step card progression
- Leadership tier visualization
- Real-time scoring updates
- Animated transitions between sub-sections

**User Flow:**
```
[Activity Types] → [Commitment Level] → [Leadership] → [Awards] → [Course Rigor] → [Service] → Frame 4
```

---

### Frame 4: Context (`Frame4Context.tsx`)

**Purpose:** Demographic context, constraints, operating preferences

**UI Components:**
- First-generation status toggle
- Family responsibilities selector
- Socioeconomic context indicators
- Available hours per week slider
- Favorite subject selector
- Personal strengths multi-select
- Career direction selector

**Data Captured:**
- `profile.demographics.first_gen` - First-generation status
- `profile.demographics.family_duties` - Family responsibilities
- `profile.demographics.low_ses` - Socioeconomic context
- `profile.operating.availableHoursPerWeek` - Time availability
- `profile.operating.favoriteSubject` - Academic interest
- `profile.operating.strengths` - Personal strengths array
- `profile.operating.careerDirection` - Career aspirations

**Visual Elements:**
- Sensitive topic handling (empathetic language)
- Privacy reassurance messaging
- Context-aware tips
- Drone assistant with supportive messaging

**User Flow:**
```
[Demographics] → [Context Factors] → [Time/Energy] → [Interests] → [Continue] → Frame 5
```

---

### Frame 5: Profile Reveal (`Frame6ProfileReveal.tsx`)

**Note:** Despite the filename, this is displayed as Frame 5 in the routing.

**Purpose:** Show profile overview with category scores

**UI Components:**
- Overall completeness percentage (large display)
- Circular progress rings (Aptitude, Passion, Service, Identity)
- Tier classification (Fresh Start, Emerging, Optimization)
- Archetype display
- Strengths list (green cards)
- Gaps/Priority areas list (orange cards)
- Quick wins (30-day actions)

**Data Displayed:**
- Calculated category scores (0-100 each)
- Profile completeness percentage
- Profile tier classification
- Archetype label
- Dynamic strengths/gaps based on actual data

**Visual Elements:**
- Animated score reveal
- CircularProgress component with 4 rings
- Color-coded strength/gap cards
- Motion animations for engagement

**User Flow:**
```
[Profile Overview] → [View Scores] → [Review Strengths/Gaps] → [Continue to Game Plan] → Frame 6
```

---

### Frame 6: Game Plan (`Frame5GamePlan.tsx`)

**Note:** Despite the filename, this is displayed as Frame 6 in the routing.

**Purpose:** Personalized action plan with phases and priorities

**UI Components:**
- Tier-based game plan header
- Phase selector tabs (Immediate, Short-term, Long-term)
- Action cards with priority badges (Critical, High, Medium, Low)
- Expandable action details (tips, resources)
- Quick wins section
- Time commitment display
- Coach booking integration (Calendly)
- Continue to Results button

**Data Displayed:**
- `GamePlan` object with phases and actions
- Priority-coded action items
- Time estimates per action
- Impact points per action
- Strength-based recommendations

**Visual Elements:**
- Phase navigation tabs
- Expandable/collapsible action cards
- Priority color coding
- Coach booking modal/inline
- Encouragement messaging

**User Flow:**
```
[View Game Plan] → [Explore Phases] → [Expand Actions] → [Book Coach (optional)] → [Continue to Results]
```

---

### Results Page (`/results/page.tsx`)

**Purpose:** Assessment completion and next steps

**UI Components:**
- Trophy icon (success indicator)
- Ivy+ Ready Score display (large number)
- "Review Your Results" button → Frame 5
- "View Power-Ups" button → Frame 6
- "Start New Assessment" button → Clear & restart

**Visual Elements:**
- Gradient background
- Glass-morphism card
- Celebratory styling

---

## 1.3 Current Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Input Flow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Frame 1 ──► Frame 2 ──► Frame 3 ──► Frame 4 ──► Frame 5 ──► Frame 6
│    │           │           │           │           │           │
│    ▼           ▼           ▼           ▼           ▼           ▼
│  name      academics    activities   context    scores     game plan
│            GPA/tests   leadership   demographics category   actions
│                        awards       operating    rings      phases
│                                                             │
└─────────────────────────────────────────────────────────────┼───┘
                                                              │
                                                              ▼
                                                         /results
```

**State Management:**
- `useStudentStore` - Profile data (Zustand)
- `useSessionStore` - Frame navigation state
- `useResultsStore` - Scoring results
- `useInsightsStore` - Real-time insights

---

## 1.4 Current Insights System

**InsightsPanel Component:**
- Displays real-time feedback during data entry
- Categories: HYPER_LOCAL, CONTEXT, TEMPORAL, APTITUDE, PASSION, PSYCHOMETRIC, INSTITUTIONAL
- Severity levels: critical, warning, positive, neutral
- Animated card reveals
- NEW badge for latest insights

**Insight Triggers:**
- GPA entry → Academic strength/gap insight
- Test scores → Competitive positioning insight
- Leadership → Leadership tier insight
- First-gen → CRI boost insight
- Service hours → Community engagement insight

---

# Part 2: v10.0 UI Components & Features

## 2.1 v10 Component File Structure

```
/Users/snazir/ivyquest-claude-v2.2/
├── components/
│   └── v10/                          # NEW v10 components
│       ├── index.ts                  # Export barrel
│       ├── SuperpowerUnlock.tsx      # CRI reveal pyramid
│       ├── DualView.tsx              # Student/Parent views
│       └── CrisisAlchemyCard.tsx     # 4-step crisis response
│
├── agents/                           # Python Agent Service
│   ├── main.py                       # FastAPI server
│   ├── config.py                     # Settings & feature flags
│   └── agents/
│       ├── assessment_agent.py       # Profile assessment
│       ├── execution_agent.py        # Task execution
│       ├── crisis_alchemy_agent.py   # Crisis handling
│       ├── narrative_dna_agent.py    # Story synthesis
│       └── cri_agent.py              # Context Relativity Index
│
├── app/api/agents/                   # Next.js API routes (proxy)
│   └── [agentType]/
│       └── route.ts                  # Agent API endpoints
│
└── lib/
    ├── config/
    │   └── featureFlags.ts           # v10 feature flag system
    └── events/
        └── eventBus.ts               # Event bus for agent comms
```

---

## 2.2 v10 Component Details

### 2.2.1 SuperpowerUnlock Component

**File:** `components/v10/SuperpowerUnlock.tsx`

**Purpose:** Dramatic reveal showing how constraints become superpowers

**When to Display:** After Frame 3 (Building) or Frame 4 (Context), before scores

**Props Interface:**
```typescript
interface SuperpowerUnlockProps {
  constraints: string[];       // e.g., ['first_gen', 'low_ses', 'family_duties']
  cri: number;                 // Context Relativity Index (e.g., 1.35)
  narrativeDna: string;        // Synthesized narrative statement
  narrativeThemes?: string[];  // Theme tags
  archetypeLabel?: string;     // e.g., "The Resilient Pioneer"
  onContinue: () => void;      // Navigation callback
}
```

**Visual Elements:**
1. **Pyramid Visualization (SVG):**
   - Base (maroon): Constraints/barriers
   - Middle (orange): Growth
   - Apex (green): Success with glow effect

2. **Animated Reveal Steps:**
   - Step 1 (500ms): Show pyramid base
   - Step 2 (1500ms): Show middle section
   - Step 3 (2500ms): Show apex with glow
   - Step 4 (3500ms): Reveal CRI percentage
   - Step 5 (4500ms): Show Narrative DNA
   - Step 6 (5500ms): Enable continue button

3. **CRI Display:**
   - Large percentage (+X%)
   - Status badge (exceptional/strong/baseline)
   - Archetype pill

4. **Narrative DNA:**
   - Italic quoted statement
   - Theme tags as pills

**Constraint Labels Mapping:**
```typescript
{
  family_duties: 'Family Responsibilities',
  low_ses: 'Economic Background',
  underrepresented: 'Underrepresented Community',
  first_gen: 'First Generation',
  work_hours: 'Work Commitments',
  rural: 'Rural Location',
  immigrant: 'Immigrant Background',
  neurodiverse: 'Unique Learning Style',
  health_challenges: 'Health Journey',
  single_parent: 'Single Parent Household',
  limited_resources: 'Resource Constraints',
  language_barrier: 'Multilingual Journey',
}
```

---

### 2.2.2 DualView Component

**File:** `components/v10/DualView.tsx`

**Purpose:** Same data, different framing for students vs parents (ACP-009)

**When to Display:** Throughout results and game plan sections

**Props Interface:**
```typescript
interface DualViewData {
  value: number | string;
  label: string;
  student: {
    title: string;
    description: string;
    encouragement?: string;
  };
  parent: {
    title: string;
    description: string;
    metric?: string;
  };
}

interface DualViewProps {
  data: DualViewData[];
  defaultView?: 'student' | 'parent';
  showToggle?: boolean;
  className?: string;
}
```

**Visual Elements:**
1. **Toggle Button:** Student View (orange) | Parent View (maroon)
2. **View-specific cards:**
   - Student: Heart icon, encouragement text, success colors
   - Parent: BarChart icon, metrics, analytical language

**Pre-built Components:**
- `DualViewCRI` - CRI with dual framing
- `DualViewProgress` - Task completion with dual framing
- `DualViewCrisis` - Crisis status with dual framing

**Example Usage:**
```tsx
// Student sees: "Your Superpower Boost +20%"
// Parent sees: "Context Relativity Index: CRI 1.20 - Performance relative to expected outcomes"
<DualViewCRI cri={1.2} viewMode="student" />
```

---

### 2.2.3 CrisisAlchemyCard Component

**File:** `components/v10/CrisisAlchemyCard.tsx`

**Purpose:** Display 4-step Crisis Alchemy protocol responses

**When to Display:** When crisis detected (grade drop, rejection, disengagement)

**Props Interface:**
```typescript
interface CrisisAlchemyCardProps {
  crisisId: string;
  title: string;
  description: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  status: 'detected' | 'proposed' | 'approved' | 'resolved' | 'escalated';
  step1?: { message?: string; emotion_acknowledged?: string; };
  step2?: { action?: string; duration_minutes?: number; why_it_helps?: string; };
  step3?: { opportunity_angle?: string; narrative_connection?: string; };
  step4?: { activity_name?: string; description?: string; first_step?: string; touchpoints?: string[]; };
  approvalDeadline?: string;
  onApprove?: () => void;
  onReject?: () => void;
}
```

**4-Step Protocol Tabs:**
1. **Validate (2s):** Heart icon, pink - Acknowledge emotion
2. **Act (10s):** Zap icon, amber - Micro-action for agency
3. **Reframe (30s):** RefreshCw icon, blue - Find opportunity
4. **Create (2min):** Lightbulb icon, green - Design new activity

**Visual Elements:**
- Collapsible card header
- Urgency badge (color-coded)
- Status indicator
- Approval deadline countdown
- HITL approve/reject buttons (when status=proposed)
- Step tabs with checkmarks for completed steps

---

## 2.3 v10 Backend Agents (For UI Integration)

### Agent Endpoints (via `/api/agents/[agentType]`):

| Agent | Endpoint | Purpose | UI Integration Point |
|-------|----------|---------|---------------------|
| Assessment | `/api/agents/assessment` | Profile analysis | After Frame 4 |
| CRI | `/api/agents/cri` | Context Relativity Index | SuperpowerUnlock |
| Narrative DNA | `/api/agents/narrative` | Story synthesis | SuperpowerUnlock |
| Crisis Alchemy | `/api/agents/crisis` | Crisis response | CrisisAlchemyCard |
| Execution | `/api/agents/execution` | Task management | Game Plan actions |

---

## 2.4 v10 Feature Flags

**File:** `lib/config/featureFlags.ts`

```typescript
interface FeatureFlags {
  v10Agents: boolean;           // Master switch
  assessmentAgent: boolean;     // Profile assessment
  executionAgent: boolean;      // Task execution
  crisisAlchemy: boolean;       // Crisis handling
  criComputation: boolean;      // CRI scoring
  narrativeDna: boolean;        // Story synthesis
  dualView: boolean;            // Student/Parent views
  eventBus: boolean;            // Agent communication
  stateVersioning: boolean;     // State snapshots
}
```

**Environment Variables:**
```bash
ENABLE_V10_AGENTS=true
ENABLE_ASSESSMENT_AGENT=true
ENABLE_EXECUTION_AGENT=true
ENABLE_CRISIS_ALCHEMY=true
ENABLE_CRI_SCORING=true
ENABLE_NARRATIVE_DNA=true
ENABLE_DUAL_VIEW=true
ENABLE_EVENT_BUS=true
ENABLE_STATE_VERSIONING=true
```

---

# Part 3: Integration Plan & Code Changes

## 3.1 Integration Overview

### New User Flow (v10 Integrated):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        v10.0 Enhanced User Flow                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Frame 1 ──► Frame 2 ──► Frame 3 ──► Frame 4 ──► [Superpower] ──► Frame 5   │
│  Warmup     Snapshot     Building    Context      Unlock          Reveal    │
│                                         │            ▲                       │
│                                         ▼            │                       │
│                                    [Agent APIs] ─────┘                       │
│                                    - CRI Agent                               │
│                                    - Narrative DNA                           │
│                                    - Assessment                              │
│                                                                             │
│  Frame 5 ──► Frame 6 ──► Results ──► [Optional: Chat Interface]            │
│  Reveal     Game Plan    Complete      AI Suggestions                       │
│    │           │                                                            │
│    ▼           ▼                                                            │
│  [DualView] [DualView]              [CrisisAlchemyCard if crisis detected] │
│  Toggle     Toggle                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3.2 Specific Code Changes Required

### 3.2.1 Add SuperpowerUnlock Between Frame 4 and Frame 5

**File to Modify:** `app/quest/[frameId]/page.tsx`

**Current Code (lines 31-38):**
```typescript
const FRAME_COMPONENTS: Record<number, React.ComponentType<{ onComplete: () => void }>> = {
  1: Frame1Warmup,
  2: Frame2Snapshot,
  3: Frame3Building,
  4: Frame4Context,
  5: Frame6ProfileReveal,
  6: Frame5GamePlan,
};
```

**Required Change:**
```typescript
import { SuperpowerUnlock } from '@/components/v10';
import { getFeatureFlags } from '@/lib/config/featureFlags';

// Add new frame slot for SuperpowerUnlock
const FRAME_COMPONENTS: Record<number, React.ComponentType<{ onComplete: () => void }>> = {
  1: Frame1Warmup,
  2: Frame2Snapshot,
  3: Frame3Building,
  4: Frame4Context,
  // Frame 4.5: SuperpowerUnlock (conditional, handled in component)
  5: Frame6ProfileReveal,
  6: Frame5GamePlan,
};

// In FramePage component, add logic to show SuperpowerUnlock:
function FramePage() {
  const flags = getFeatureFlags();
  const [showSuperpowerUnlock, setShowSuperpowerUnlock] = useState(false);

  // After Frame 4 completion, check if should show SuperpowerUnlock
  const handleComplete = () => {
    if (frameId === 4 && flags.criComputation && flags.narrativeDna) {
      setShowSuperpowerUnlock(true);
      return;
    }
    // ... existing navigation logic
  };

  if (showSuperpowerUnlock) {
    return (
      <SuperpowerUnlock
        constraints={getConstraintsFromProfile(profile)}
        cri={calculatedCRI}
        narrativeDna={narrativeStatement}
        onContinue={() => {
          setShowSuperpowerUnlock(false);
          router.push('/quest/5');
        }}
      />
    );
  }
  // ... rest of component
}
```

---

### 3.2.2 Add DualView Toggle to Frame 5 & Frame 6

**File to Modify:** `components/frames/Frame6ProfileReveal.tsx`

**Add at top of component:**
```typescript
import { DualView, DualViewCRI } from '@/components/v10';
import { getFeatureFlags } from '@/lib/config/featureFlags';

export function Frame6ProfileReveal({ onComplete }: Frame6ProfileRevealProps) {
  const flags = getFeatureFlags();
  const [viewMode, setViewMode] = useState<'student' | 'parent'>('student');

  // ... existing code ...

  return (
    <div>
      {/* Add DualView toggle at top */}
      {flags.dualView && (
        <div className="flex justify-center mb-6">
          <ViewModeToggle value={viewMode} onChange={setViewMode} />
        </div>
      )}

      {/* Wrap score display in DualView when enabled */}
      {flags.dualView ? (
        <DualViewCRI cri={profile.cri || 1.0} viewMode={viewMode} />
      ) : (
        // Existing score display
        <CircularProgress ... />
      )}

      {/* ... rest of component */}
    </div>
  );
}
```

**Similar change for:** `components/frames/Frame5GamePlan.tsx`

---

### 3.2.3 Add Crisis Alchemy Detection & Display

**File to Create:** `components/frames/CrisisMonitor.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { CrisisAlchemyCard } from '@/components/v10';
import { getFeatureFlags } from '@/lib/config/featureFlags';

interface Crisis {
  id: string;
  title: string;
  description: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  status: 'detected' | 'proposed' | 'approved' | 'resolved' | 'escalated';
  steps: {
    step1?: any;
    step2?: any;
    step3?: any;
    step4?: any;
  };
}

export function CrisisMonitor() {
  const flags = getFeatureFlags();
  const [crises, setCrises] = useState<Crisis[]>([]);

  useEffect(() => {
    if (!flags.crisisAlchemy) return;

    // Subscribe to crisis events
    const unsubscribe = eventBus.subscribe('crisis.detected', (crisis) => {
      setCrises(prev => [...prev, crisis]);
    });

    return unsubscribe;
  }, [flags.crisisAlchemy]);

  if (!flags.crisisAlchemy || crises.length === 0) return null;

  return (
    <div className="space-y-4">
      {crises.map(crisis => (
        <CrisisAlchemyCard
          key={crisis.id}
          crisisId={crisis.id}
          title={crisis.title}
          description={crisis.description}
          urgency={crisis.urgency}
          status={crisis.status}
          step1={crisis.steps.step1}
          step2={crisis.steps.step2}
          step3={crisis.steps.step3}
          step4={crisis.steps.step4}
          onApprove={() => handleApprove(crisis.id)}
          onReject={() => handleReject(crisis.id)}
        />
      ))}
    </div>
  );
}
```

**Add to Results page and Game Plan:**
```typescript
import { CrisisMonitor } from '@/components/frames/CrisisMonitor';

// In component JSX:
<CrisisMonitor />
```

---

### 3.2.4 Add Agent API Integration Hook

**File to Create:** `lib/hooks/useAgentAPI.ts`

```typescript
import { useState, useCallback } from 'react';
import { getFeatureFlags } from '@/lib/config/featureFlags';

interface AgentResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export function useAgentAPI<T>(agentType: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);

  const flags = getFeatureFlags();

  const invoke = useCallback(async (payload: any): Promise<AgentResponse<T>> => {
    if (!flags.v10Agents) {
      return { success: false, error: 'v10 agents not enabled' };
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/agents/${agentType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (response.ok) {
        setData(result.data);
        return { success: true, data: result.data };
      } else {
        setError(result.error);
        return { success: false, error: result.error };
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }, [agentType, flags.v10Agents]);

  return { invoke, loading, error, data };
}

// Specialized hooks
export function useCRIAgent() {
  return useAgentAPI<{ cri: number; boost_factors: string[] }>('cri');
}

export function useNarrativeAgent() {
  return useAgentAPI<{ narrative_dna: string; themes: string[]; archetype: string }>('narrative');
}

export function useCrisisAgent() {
  return useAgentAPI<{ crisis_id: string; steps: any }>('crisis');
}
```

---

### 3.2.5 Create Wrapper Component for v10 Integration

**File to Create:** `components/quest/V10EnhancedFlow.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { getFeatureFlags } from '@/lib/config/featureFlags';
import { SuperpowerUnlock } from '@/components/v10';
import { useCRIAgent, useNarrativeAgent } from '@/lib/hooks/useAgentAPI';

interface V10EnhancedFlowProps {
  children: React.ReactNode;
  currentFrame: number;
  onFrameComplete: () => void;
}

export function V10EnhancedFlow({ children, currentFrame, onFrameComplete }: V10EnhancedFlowProps) {
  const flags = getFeatureFlags();
  const { profile } = useStudentStore();
  const [showSuperpowerUnlock, setShowSuperpowerUnlock] = useState(false);
  const [criData, setCriData] = useState<{ cri: number; factors: string[] } | null>(null);
  const [narrativeData, setNarrativeData] = useState<{ dna: string; themes: string[] } | null>(null);

  const criAgent = useCRIAgent();
  const narrativeAgent = useNarrativeAgent();

  // After Frame 4, trigger agent calls
  useEffect(() => {
    if (currentFrame === 4 && flags.v10Agents) {
      const fetchAgentData = async () => {
        // Parallel agent calls
        const [criResult, narrativeResult] = await Promise.all([
          criAgent.invoke({ profile }),
          narrativeAgent.invoke({ profile }),
        ]);

        if (criResult.success && criResult.data) {
          setCriData({ cri: criResult.data.cri, factors: criResult.data.boost_factors });
        }

        if (narrativeResult.success && narrativeResult.data) {
          setNarrativeData({
            dna: narrativeResult.data.narrative_dna,
            themes: narrativeResult.data.themes
          });
        }

        // Show SuperpowerUnlock if we have data
        if (criResult.success && narrativeResult.success) {
          setShowSuperpowerUnlock(true);
        }
      };

      fetchAgentData();
    }
  }, [currentFrame, flags.v10Agents, profile]);

  // Render SuperpowerUnlock interstitial
  if (showSuperpowerUnlock && criData && narrativeData) {
    return (
      <SuperpowerUnlock
        constraints={extractConstraints(profile)}
        cri={criData.cri}
        narrativeDna={narrativeData.dna}
        narrativeThemes={narrativeData.themes}
        onContinue={() => {
          setShowSuperpowerUnlock(false);
          onFrameComplete();
        }}
      />
    );
  }

  return <>{children}</>;
}

function extractConstraints(profile: any): string[] {
  const constraints: string[] = [];

  if (profile.demographics?.first_gen) constraints.push('first_gen');
  if (profile.demographics?.low_ses) constraints.push('low_ses');
  if (profile.demographics?.family_duties) constraints.push('family_duties');
  if (profile.demographics?.underrepresented) constraints.push('underrepresented');

  return constraints;
}
```

---

### 3.2.6 Update QuestContainer for v10 Flow

**File to Modify:** `components/quest/QuestContainer.tsx`

**Add v10 wrapper:**
```typescript
import { V10EnhancedFlow } from './V10EnhancedFlow';
import { getFeatureFlags } from '@/lib/config/featureFlags';

export function QuestContainer({ children }: { children: React.ReactNode }) {
  const flags = getFeatureFlags();
  const { currentFrame } = useSessionStore();

  // Wrap in v10 enhanced flow if enabled
  if (flags.v10Agents) {
    return (
      <V10EnhancedFlow
        currentFrame={currentFrame}
        onFrameComplete={handleFrameComplete}
      >
        {children}
      </V10EnhancedFlow>
    );
  }

  return <>{children}</>;
}
```

---

## 3.3 New Interfaces to Add

### 3.3.1 AI Chat Suggestion Bubbles

**File to Create:** `components/v10/AISuggestionBubbles.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, ChevronRight } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';

interface Suggestion {
  id: string;
  text: string;
  action: () => void;
  priority: 'high' | 'medium' | 'low';
}

interface AISuggestionBubblesProps {
  suggestions: Suggestion[];
  maxVisible?: number;
  position?: 'bottom-right' | 'bottom-left' | 'top-right';
}

export function AISuggestionBubbles({
  suggestions,
  maxVisible = 3,
  position = 'bottom-right'
}: AISuggestionBubblesProps) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const visibleSuggestions = suggestions
    .filter(s => !dismissed.has(s.id))
    .slice(0, maxVisible);

  if (visibleSuggestions.length === 0) return null;

  const positionClasses = {
    'bottom-right': 'fixed bottom-6 right-6',
    'bottom-left': 'fixed bottom-6 left-6',
    'top-right': 'fixed top-20 right-6',
  };

  return (
    <div className={`${positionClasses[position]} z-50 space-y-3 max-w-sm`}>
      <AnimatePresence>
        {visibleSuggestions.map((suggestion, index) => (
          <motion.div
            key={suggestion.id}
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ delay: index * 0.1 }}
            className="rounded-xl p-4 shadow-lg cursor-pointer group"
            style={{
              backgroundColor: BRAND_COLORS.bgPrimary,
              border: `1px solid ${BRAND_COLORS.borderLight}`,
            }}
            onClick={suggestion.action}
          >
            <div className="flex items-start gap-3">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: BRAND_COLORS.primaryBg }}
              >
                <Sparkles size={16} style={{ color: BRAND_COLORS.primary }} />
              </div>
              <div className="flex-1">
                <p
                  className="text-sm"
                  style={{ color: BRAND_COLORS.textPrimary }}
                >
                  {suggestion.text}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setDismissed(prev => new Set([...prev, suggestion.id]));
                }}
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X size={16} style={{ color: BRAND_COLORS.textMuted }} />
              </button>
            </div>
            <div className="flex justify-end mt-2">
              <span
                className="text-xs flex items-center gap-1"
                style={{ color: BRAND_COLORS.primary }}
              >
                Tap to learn more <ChevronRight size={12} />
              </span>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
```

---

### 3.3.2 AI Chat Interface (Optional Enhancement)

**File to Create:** `components/v10/AIChatInterface.tsx`

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Sparkles } from 'lucide-react';
import { BRAND_COLORS } from '@/lib/constants/brand';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function AIChatInterface() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/agents/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I apologize, but I could not process that request.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center shadow-lg z-50 transition-transform hover:scale-105"
        style={{
          background: `linear-gradient(135deg, ${BRAND_COLORS.primary}, ${BRAND_COLORS.primaryLight})`,
        }}
      >
        {isOpen ? (
          <X size={24} color="white" />
        ) : (
          <MessageCircle size={24} color="white" />
        )}
      </button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 w-96 h-[500px] rounded-2xl shadow-2xl z-40 flex flex-col overflow-hidden"
            style={{
              backgroundColor: BRAND_COLORS.bgPrimary,
              border: `1px solid ${BRAND_COLORS.borderLight}`,
            }}
          >
            {/* Header */}
            <div
              className="p-4 flex items-center gap-3"
              style={{
                borderBottom: `1px solid ${BRAND_COLORS.borderLight}`,
                background: `linear-gradient(135deg, ${BRAND_COLORS.primaryBg}, white)`,
              }}
            >
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: BRAND_COLORS.primary }}
              >
                <Sparkles size={20} color="white" />
              </div>
              <div>
                <h3 className="font-semibold" style={{ color: BRAND_COLORS.textHeading }}>
                  IvyQuest Assistant
                </h3>
                <p className="text-xs" style={{ color: BRAND_COLORS.textMuted }}>
                  Powered by v10.0 Agents
                </p>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <Sparkles size={32} style={{ color: BRAND_COLORS.textMuted }} className="mx-auto mb-3" />
                  <p style={{ color: BRAND_COLORS.textMuted }}>
                    Ask me anything about your college application journey!
                  </p>
                </div>
              )}

              {messages.map(message => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className="max-w-[80%] rounded-2xl px-4 py-2"
                    style={{
                      backgroundColor: message.role === 'user'
                        ? BRAND_COLORS.primary
                        : BRAND_COLORS.bgPill,
                      color: message.role === 'user'
                        ? 'white'
                        : BRAND_COLORS.textPrimary,
                    }}
                  >
                    {message.content}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div
                    className="rounded-2xl px-4 py-3"
                    style={{ backgroundColor: BRAND_COLORS.bgPill }}
                  >
                    <div className="flex gap-1">
                      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div
              className="p-4"
              style={{ borderTop: `1px solid ${BRAND_COLORS.borderLight}` }}
            >
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-2 rounded-full outline-none"
                  style={{
                    backgroundColor: BRAND_COLORS.bgPill,
                    color: BRAND_COLORS.textPrimary,
                  }}
                />
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || isLoading}
                  className="w-10 h-10 rounded-full flex items-center justify-center disabled:opacity-50"
                  style={{ backgroundColor: BRAND_COLORS.primary }}
                >
                  <Send size={18} color="white" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
```

---

## 3.4 Integration Checklist

### Phase 1: Core Integration (Required)
- [ ] Add `V10EnhancedFlow` wrapper to quest flow
- [ ] Integrate `SuperpowerUnlock` after Frame 4
- [ ] Add `DualView` toggle to Frame 5 and Frame 6
- [ ] Create agent API hooks (`useAgentAPI.ts`)
- [ ] Wire up CRI and Narrative DNA agents

### Phase 2: Crisis Handling
- [ ] Add `CrisisMonitor` component
- [ ] Integrate `CrisisAlchemyCard` display
- [ ] Connect to Crisis Alchemy agent
- [ ] Add HITL approval flow

### Phase 3: Enhanced UX
- [ ] Add `AISuggestionBubbles` for proactive tips
- [ ] Add `AIChatInterface` for conversational AI
- [ ] Implement event bus subscriptions for real-time updates

### Phase 4: Polish
- [ ] Add loading states for agent calls
- [ ] Add error boundaries for agent failures
- [ ] Implement graceful degradation when agents unavailable
- [ ] Add analytics tracking for v10 features

---

## 3.5 Testing Strategy

### Unit Tests
- Test each v10 component in isolation
- Test agent API hooks with mocked responses
- Test feature flag conditional rendering

### Integration Tests
- Test full flow with v10 features enabled
- Test fallback to v2.2 when agents fail
- Test HITL approval workflows

### E2E Tests
- Test complete user journey with all v10 features
- Validate CRI calculations match expected values
- Test crisis detection and response flow

---

## 3.6 Rollout Plan

1. **Stage 1:** Enable feature flags in development
2. **Stage 2:** Internal testing with all features
3. **Stage 3:** Beta rollout with 10% of users
4. **Stage 4:** Gradual rollout (25% → 50% → 100%)
5. **Stage 5:** Remove feature flags, make v10 default

---

## Summary

This specification provides a complete roadmap for integrating v10.0 features into the existing v2.2 UI/UX flow. The key additions are:

1. **SuperpowerUnlock** - Dramatic CRI reveal between Frame 4 and 5
2. **DualView** - Student/Parent perspective toggle throughout
3. **CrisisAlchemyCard** - Crisis handling UI with HITL approval
4. **AI Chat & Suggestions** - Proactive AI assistance

All changes are designed to be:
- **Feature-flagged** - Can enable/disable independently
- **Backward-compatible** - Falls back to v2.2 gracefully
- **Progressively enhanced** - Works without agents, better with them
