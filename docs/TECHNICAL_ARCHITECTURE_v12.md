# IvyQuest Technical Architecture Specification v12.0

**Version:** 12.0
**Last Updated:** January 4, 2026
**Platform:** IvyQuest - AI-Powered College Admissions Assessment Platform

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Directory Structure](#3-directory-structure)
4. [Frontend Architecture](#4-frontend-architecture)
5. [Backend & API Layer](#5-backend--api-layer)
6. [State Management](#6-state-management)
7. [Scoring Engine](#7-scoring-engine)
8. [Insights System](#8-insights-system)
9. [Game Plan Engine](#9-game-plan-engine)
10. [Multi-Agent System](#10-multi-agent-system)
11. [Data Layer & Persistence](#11-data-layer--persistence)
12. [Type System](#12-type-system)
13. [Visualization System](#13-visualization-system)
14. [Analytics & Tracing](#14-analytics--tracing)
15. [Testing Infrastructure](#15-testing-infrastructure)
16. [Deployment Configuration](#16-deployment-configuration)
17. [Appendix: File Reference](#17-appendix-file-reference)

---

## 1. Executive Summary

IvyQuest is a comprehensive AI-powered college admissions assessment platform that guides students through a gamified journey to evaluate their "Ivy+ Readiness." The platform combines:

- **Assessment Journey**: 6-frame gamified questionnaire collecting 58 Layer 1 attributes
- **Scoring Engine**: IvyLevel v6.0 algorithm with Chetty 2023 multipliers
- **Real-time Insights**: AI-generated contextual guidance during assessment
- **Multi-Agent System**: Python-based agents for strategic reasoning (Agno + LangGraph)
- **Digital Twin**: Visual avatar representing student profile completeness
- **Game Plan**: Personalized booster recommendations with ROI calculations

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14.2, React 18, TypeScript |
| State Management | Zustand + Immer |
| Styling | Tailwind CSS, Framer Motion |
| 3D Visualization | Three.js, React Three Fiber |
| Backend | Next.js API Routes |
| Database | Supabase (PostgreSQL) |
| AI/NLP | Google Generative AI (Gemini) |
| Multi-Agent | Python 3.13, Agno, LangGraph, FastAPI |
| Testing | Playwright (E2E) |

---

## 2. System Architecture Overview

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Frame 1   │→ │   Frame 2   │→ │   Frame 3   │→ │   Frame 4   │→ ...   │
│  │  (Warmup)   │  │  (Snapshot) │  │  (Building) │  │  (Context)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STATE MANAGEMENT LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ useSession  │  │ useStudent  │  │ useResults  │  │ useInsights │        │
│  │   Store     │  │   Store     │  │   Store     │  │   Store     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             API LAYER                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ /api/score  │  │  /api/nlp   │  │/api/agents/*│  │/api/handoff │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌───────────────────────┐ ┌───────────────────┐ ┌───────────────────────────┐
│    SCORING ENGINE     │ │  INSIGHTS ENGINE  │ │    MULTI-AGENT SYSTEM     │
│  ┌─────────────────┐  │ │ ┌───────────────┐ │ │  ┌─────────────────────┐  │
│  │   Normalize     │  │ │ │  7 Categories │ │ │  │  Assessment Agent   │  │
│  │   Calculate     │  │ │ │  4 Severities │ │ │  │  Execution Agent    │  │
│  │   Apply Mult.   │  │ │ │  Real-time    │ │ │  │  GamePlan Agent     │  │
│  │   Archetype     │  │ │ └───────────────┘ │ │  │  Awards Agent       │  │
│  └─────────────────┘  │ └───────────────────┘ │  │  Opportunity Agent  │  │
└───────────────────────┘                       │  └─────────────────────┘  │
                                                └───────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PERSISTENCE LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        Supabase (PostgreSQL)                         │    │
│  │   assessments | coach_sessions | archetypes | opportunities | ...    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Four-Layer Data Model

```
Layer 1: CORE ATTRIBUTES (58 attributes)
├── Aptitude: GPA, SAT, ACT, AP courses, academic awards
├── Passion: Leadership, projects, research, EC commitment
└── Community: Service hours, impact, leadership

Layer 2: TARGET SCHOOLS (8 Ivy+ schools)
├── Acceptance rates (CDS 2025)
├── Category weights per school
└── ROI multipliers (Chetty 2023)

Layer 3: CONTEXT MULTIPLIERS
├── Demographics: Ethnicity, first-gen, legacy, athlete
├── High School: Saturation (NSC), region, type
└── Major: Field-specific multipliers

Layer 4: ASSESSMENT INTELLIGENCE (39 points)
├── Psychometrics: Big Five, grit, vision clarity
├── Time Management: 168-hour framework
├── Hidden Capabilities: Hobbies, projects
└── Family Context: Parent archetype, expectations
```

---

## 3. Directory Structure

```
ivyquest-claude-v2.2/
├── app/                          # Next.js App Router
│   ├── api/                      # API routes
│   │   ├── score/               # Main scoring endpoint
│   │   ├── nlp/                 # NLP extraction
│   │   ├── agents/              # Multi-agent APIs
│   │   │   ├── assessment/      # Assessment agent
│   │   │   ├── execution/       # Execution agent + crisis
│   │   │   ├── gameplan/        # Game plan generation
│   │   │   ├── awards/          # Award matching
│   │   │   └── opportunities/   # Summer program matching
│   │   └── handoff/             # Conversation handoff
│   ├── dashboard/               # Post-assessment dashboard
│   ├── quest/                   # Assessment journey
│   │   └── [frameId]/           # Dynamic frame routing
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   └── globals.css              # Global styles
│
├── components/                   # React Components (91 files)
│   ├── frames/                  # Assessment frame components
│   │   ├── Frame1Warmup.tsx
│   │   ├── Frame2Snapshot.tsx
│   │   ├── Frame3Building.tsx
│   │   ├── Frame4Context.tsx
│   │   ├── Frame5GamePlan.tsx
│   │   ├── Frame6ProfileReveal.tsx
│   │   ├── reveal/              # Reveal card components
│   │   ├── operating/           # Operating data cards
│   │   └── powerups/            # Booster components
│   ├── insights/                # Real-time insights (7 files)
│   ├── quest/                   # Quest UI overlays (10 files)
│   ├── dashboard/               # Dashboard components (10 files)
│   ├── rings/                   # Circular progress visualizations
│   ├── tabs/                    # Tab navigation components
│   ├── ui/                      # Design system (13 files)
│   ├── layout/                  # Layout components
│   ├── shared/                  # Shared utilities
│   └── booking/                 # Calendly integration
│
├── lib/                          # Business Logic (109 files)
│   ├── store/                   # Zustand stores (10 stores)
│   │   ├── useSessionStore.ts   # Session state
│   │   ├── useStudentStore.ts   # Student profile
│   │   ├── useResultsStore.ts   # Assessment results
│   │   ├── useInsightsStore.ts  # Real-time insights
│   │   ├── useUIStore.ts        # UI state
│   │   ├── useTwinStore.ts      # Digital twin
│   │   ├── useFrame3Store.ts    # Frame 3 state
│   │   ├── useFrame4Store.ts    # Frame 4 state
│   │   └── useFrame5Store.ts    # Frame 5 state
│   ├── scoring/                 # Scoring engine
│   │   ├── engine.ts            # Main calculator (938 lines)
│   │   ├── archetypeDetector.ts # Archetype detection
│   │   └── factorAnalysis.ts    # Helping/holding factors
│   ├── insights/                # Insights system
│   │   ├── InsightEngine.ts     # Generation logic
│   │   ├── realtimeInsights.ts  # Real-time generation
│   │   └── loadingInsights.ts   # Placeholder states
│   ├── gamePlan/                # Game plan engine
│   │   └── gamePlanEngine.ts    # Booster recommendations
│   ├── types/                   # TypeScript definitions
│   │   ├── student.ts           # Complete schema (752 lines)
│   │   ├── frame4.types.ts      # Frame 4 types
│   │   └── integration.types.ts # Integration types
│   ├── constants/               # Configuration (11 files)
│   │   ├── brand.ts             # Design system colors
│   │   ├── defaults.ts          # Scoring defaults
│   │   ├── design.ts            # UI design tokens
│   │   └── frame*.constants.ts  # Frame-specific constants
│   ├── data/                    # Static data (7 files)
│   │   ├── schools.ts           # School configurations
│   │   ├── cds-data.ts          # Common Data Set
│   │   ├── high-schools.ts      # HS saturation data
│   │   └── chetty-roi.ts        # ROI multipliers
│   ├── utils/                   # Utilities (5 files)
│   │   ├── normalize.ts         # Profile normalization
│   │   ├── safeValue.ts         # Null-safe helpers
│   │   └── skipLogic.ts         # Conditional visibility
│   ├── validation/              # Input validation
│   │   └── profile.ts           # Profile validation
│   ├── integration/             # Quest orchestration
│   ├── visualization/           # Visual feedback
│   ├── analytics/               # Analytics tracking
│   ├── trace/                   # Execution tracing
│   ├── hooks/                   # Custom React hooks
│   ├── supabase/                # Database client
│   └── config/                  # Feature flags
│
├── agents/                       # Python Multi-Agent System
│   ├── main.py                  # FastAPI entry point
│   ├── agents/                  # Agent implementations
│   │   ├── assessment.py        # Assessment agent
│   │   ├── execution.py         # Execution agent
│   │   ├── gameplan.py          # GamePlan agent
│   │   ├── awards.py            # Awards agent
│   │   └── opportunity.py       # Opportunity agent
│   ├── graphs/                  # LangGraph workflows
│   │   └── crisis_alchemy.py    # Crisis handling
│   ├── tools/                   # Agent tools
│   │   ├── cri.py               # CRI calculations
│   │   └── database.py          # Supabase integration
│   └── config.py                # Agent configuration
│
├── supabase/                     # Database
│   └── migrations/              # SQL migrations (10 files)
│
├── e2e/                          # End-to-end tests
│   ├── huda-benchmark.spec.ts   # Full flow benchmark
│   ├── v10-agents.spec.ts       # Agent tests
│   └── v10-ui-flow.spec.ts      # UI flow tests
│
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
└── public/                       # Static assets
```

---

## 4. Frontend Architecture

### 4.1 Assessment Frame Components

The assessment journey consists of 6 main frames, each collecting specific data:

| Frame | Component | Purpose | Data Collected |
|-------|-----------|---------|----------------|
| 1 | `Frame1Warmup.tsx` | Icebreaker/onboarding | Name, grade, goals |
| 2 | `Frame2Snapshot.tsx` | Quick academic snapshot | GPA, test scores |
| 3 | `Frame3Building.tsx` | Layer 1 attributes | Aptitude, passion, community |
| 4 | `Frame4Context.tsx` | Context multipliers | Demographics, school type |
| 5 | `Frame5GamePlan.tsx` | Game plan creation | Booster selections |
| 6 | `Frame6ProfileReveal.tsx` | Final profile reveal | Summary, next steps |

### 4.2 Frame Component Structure

```typescript
// Standard Frame Component Pattern
interface FrameProps {
  onComplete?: () => void;
}

export function FrameN({ onComplete }: FrameProps) {
  const { profile, updateProfile } = useStudentStore();
  const { nextFrame, completeFrame } = useSessionStore();

  // Calculate scores dynamically
  const categoryScores = useMemo(() => [
    { name: 'Aptitude', score: calculateAptitudeScore(profile) },
    { name: 'Passion', score: calculatePassionScore(profile) },
    { name: 'Service', score: calculateServiceScore(profile) },
    { name: 'Identity', score: calculateIdentityScore(profile) },
  ], [profile]);

  const handleNext = useCallback(() => {
    completeFrame();
    onComplete ? onComplete() : nextFrame();
  }, [completeFrame, nextFrame, onComplete]);

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '24px 16px' }}>
      {/* Frame content */}
      <button onClick={handleNext}>Continue</button>
    </div>
  );
}
```

### 4.3 Visualization Components

#### Circular Progress (5-Ring System)

```typescript
// components/rings/CircularProgress.tsx
interface CircularProgressProps {
  aptitude: number;    // 0-100
  passion: number;     // 0-100
  community: number;   // 0-100 (displayed as "Service")
  narrative: number;   // 0-100 (displayed as "Identity")
  totalScore: number;  // 0-100
  size?: number;       // default: 400px
}

// Ring Configuration (inner to outer)
const RING_CONFIG = {
  colors: {
    total: 'url(#ivyGradient)',  // Brand gradient
    aptitude: '#FFBB6D',         // Golden
    passion: '#FF6E6D',          // Coral
    community: '#55AAAA',        // Teal
    narrative: '#979797',        // Gray
  },
  radii: {
    narrative: 78,   // Innermost
    community: 98,
    passion: 118,
    aptitude: 138,
    total: 162,      // Outermost
  },
};
```

#### Pillar Cards (2x2 Grid)

```typescript
// components/rings/PillarCards.tsx
interface PillarCardsProps {
  aptitude: number;
  passion: number;
  community: number;
  narrative: number;
}

// Each card displays:
// - Pillar name and icon
// - Score percentage
// - SVG wave animation (height based on score)
// - Color-coded background
```

### 4.4 Dashboard Architecture

```typescript
// app/dashboard/page.tsx
function DashboardContent() {
  const studentProfile = useStudentStore((s) => s.profile);
  const results = useResultsStore((s) => s.results);

  // Dynamic score calculation (same formulas as Frame6)
  const assessmentData = useMemo(() => {
    const aptitudeScore = calculateAptitudeScore(studentProfile);
    const passionScore = calculatePassionScore(studentProfile);
    const serviceScore = calculateServiceScore(studentProfile);
    const identityScore = calculateIdentityScore(studentProfile);

    const overallScore = Math.round(
      (aptitudeScore + passionScore + serviceScore + identityScore) / 4
    );

    return {
      ivyReadyScore: { overall: overallScore, tier: getTierFromScore(overallScore) },
      pillars: { aptitude: aptitudeScore, passion: passionScore, ... },
      // ... strengths, weakSpots, admissionsRubric
    };
  }, [studentProfile]);

  return (
    <div>
      <TabHeader activeTab={activeTab} onTabChange={setActiveTab} />
      <AnimatePresence mode="wait">
        {activeTab === 'assessment' && <AssessmentTab data={assessmentData} />}
        {activeTab === 'gameplan' && <GamePlanTab data={gamePlanData} />}
        {/* ... other tabs */}
      </AnimatePresence>
    </div>
  );
}
```

### 4.5 Design System

```typescript
// lib/constants/brand.ts
export const BRAND_COLORS = {
  // Primary brand colors
  primary: '#FF4A23',           // Ivylevel Orange
  primaryLight: 'rgba(255, 74, 35, 0.1)',
  secondary: '#641432',         // Ivylevel Maroon
  secondaryLight: '#8a1d45',

  // Text colors
  textHeading: '#641432',       // Maroon for headings
  textPrimary: '#374151',       // Gray-700
  textSecondary: '#6b7280',     // Gray-500
  textMuted: '#9ca3af',         // Gray-400

  // Background colors
  bgPrimary: 'rgba(255,255,255,0.95)',
  bgCard: '#ffffff',
  bgSubtle: '#f9fafb',

  // State colors
  success: '#16a34a',
  warning: '#d97706',
  error: '#dc2626',
};

// lib/constants/design.ts
export const GRADIENTS = {
  primary: 'linear-gradient(135deg, #641432 0%, #8B1E4A 100%)',
  accent: 'linear-gradient(135deg, #FF4A23 0%, #FF7224 100%)',
  brand: 'linear-gradient(135deg, #641432 0%, #8B1E4A 50%, #FF4A23 100%)',
};

export const TIER_CONFIG = {
  BRONZE: { color: '#CD7F32', label: 'Bronze', min: 0 },
  SILVER: { color: '#C0C0C0', label: 'Silver', min: 60 },
  GOLD: { color: '#FFD700', label: 'Gold', min: 75 },
  PLATINUM: { color: '#E5E4E2', label: 'Platinum', min: 85 },
  DIAMOND: { color: '#B9F2FF', label: 'Diamond', min: 95 },
};
```

---

## 5. Backend & API Layer

### 5.1 Scoring API

```typescript
// app/api/score/route.ts
export async function POST(request: NextRequest) {
  const { profile } = await request.json();

  // Step 1: Validate and complete profile at API boundary
  const { profile: completedProfile, validation } = prepareProfile(profile);

  // Step 2: Normalize all Layer 1 attributes (0.0-1.0 scale)
  const normalized_profile = normalizeStudentProfile(completedProfile);

  // Step 3: Generate complete assessment results
  const results: AssessmentResults = generateAssessmentResults(normalized_profile);

  // Step 4: Return results with school configurations
  return NextResponse.json({
    success: true,
    profile: normalized_profile,
    results,
    school_configs: getSchools(completedProfile.target_schools),
    timestamp: new Date().toISOString(),
  });
}
```

### 5.2 Agent APIs

```typescript
// app/api/agents/[agentType]/route.ts

// Assessment Agent - Synthesizes identity
POST /api/agents/assessment/enhance
Request: { profile: StudentProfile }
Response: { enhanced_profile, archetype, narrative_dna }

// Execution Agent - Strategy execution
POST /api/agents/execution/[profileId]
Request: { profile, goal, context }
Response: { action_plan, timeline, blockers }

// GamePlan Agent - Strategic planning
POST /api/agents/gameplan/generate
Request: { profile, target_schools, timeframe }
Response: { phases, milestones, boosters }

// Awards Agent - Award matching
POST /api/agents/awards/match/[profileId]
Request: { profile, interests }
Response: { recommended_awards, application_strategy }

// Opportunity Agent - Summer programs
POST /api/agents/opportunities/match/[profileId]
Request: { profile, grade, interests }
Response: { programs, fit_scores, deadlines }

// Crisis Handler
POST /api/agents/execution/crisis
Request: { profile, crisis_type, context }
Response: { resolution_plan, support_resources }
```

### 5.3 NLP API

```typescript
// app/api/nlp/route.ts
// Extracts structured data from free-text inputs

POST /api/nlp
Request: { text: string, extraction_type: 'activities' | 'awards' | 'leadership' }
Response: {
  extracted: {
    entities: string[],
    categories: string[],
    sentiment: number,
    confidence: number
  }
}
```

---

## 6. State Management

### 6.1 Store Architecture

All stores use Zustand with these middleware:
- **Immer**: Immutable state updates
- **Persist**: localStorage synchronization
- **Devtools**: Redux DevTools integration

### 6.2 Core Stores

#### Session Store
```typescript
// lib/store/useSessionStore.ts
interface SessionStoreState {
  // Session metadata
  session_id: string;
  user_type: 'student' | 'parent' | 'counselor';
  started_at: string;

  // Frame navigation
  current_frame: number;
  current_card: number;
  frame_history: number[];

  // Progress tracking
  xp: number;
  streak: number;
  is_completed: boolean;
  completed_frames: number[];

  // Quiz answers
  quiz_answers: Record<string, any>;

  // Agent data cache
  cri_score: number | null;
  narrative_dna: string | null;
  archetype: string | null;

  // Actions
  nextFrame: () => void;
  prevFrame: () => void;
  completeFrame: () => void;
  setQuizAnswer: (key: string, value: any) => void;
  addXP: (amount: number) => void;
}
```

#### Student Store
```typescript
// lib/store/useStudentStore.ts
interface StudentStoreState {
  profile: StudentProfile;

  // Actions
  updateProfile: (updates: Partial<StudentProfile>) => void;
  updateAptitude: (updates: Partial<AptitudeAttributes>) => void;
  updatePassion: (updates: Partial<PassionAttributes>) => void;
  updateCommunity: (updates: Partial<CommunityAttributes>) => void;
  updateOperating: (updates: Partial<OperatingData>) => void;
  updateDemographics: (updates: Partial<DemographicContext>) => void;
  resetProfile: () => void;
}
```

#### Results Store
```typescript
// lib/store/useResultsStore.ts
interface ResultsStoreState {
  // Scoring results
  results: AssessmentResults | null;
  ivy_score: IvyReadyScore | null;
  school_probabilities: SchoolProbability[];
  helping_factors: string[];
  holding_back_factors: string[];

  // Archetype
  archetype: ArchetypeID | null;
  archetype_label: string;
  narrative_tagline: string;

  // Boosters
  booster_recommendations: BoosterRecommendations | null;
  top_3_boosters: Booster[];
  all_boosters: Booster[];

  // Twin Fleet
  twin_fleet: TwinFleet | null;
  base_twin: DigitalTwin | null;
  school_twins: DigitalTwin[];

  // Actions
  setResults: (results: AssessmentResults) => void;
  setBoosters: (boosters: BoosterRecommendations) => void;
  setTwinFleet: (fleet: TwinFleet) => void;
  clearResults: () => void;
}
```

#### Insights Store
```typescript
// lib/store/useInsightsStore.ts
interface InsightsStoreState {
  insights: Insight[];
  is_generating: boolean;
  last_generated_at: string | null;

  // Filtering
  category_filter: InsightCategory | null;
  severity_filter: InsightSeverity | null;

  // Actions
  addInsight: (insight: Insight) => void;
  removeInsight: (id: string) => void;
  setGenerating: (status: boolean) => void;
  filterByCategory: (category: InsightCategory) => void;
  filterBySeverity: (severity: InsightSeverity) => void;
  clearInsights: () => void;
}
```

---

## 7. Scoring Engine

### 7.1 Scoring Pipeline

```
Raw Profile Data
      │
      ▼
┌─────────────────┐
│   Validation    │ → Apply defaults for missing fields
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Normalization  │ → Convert to 0.0-1.0 scale
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Category Scores │ → Weighted aggregation
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Ivy+ Score     │ → 0-100 overall readiness
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ SFFA Rubric     │ → 1-6 scale per category
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  P_base         │ → Sigmoid probability
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Multipliers     │ → Chetty + demographics
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  P_final        │ → Capped at 95%
└─────────────────┘
```

### 7.2 Scoring Formulas

#### Pillar Score Calculation

```typescript
// lib/scoring/engine.ts

// APTITUDE SCORE (0-100)
function calculateAptitudeScore(profile: StudentProfile): number {
  const apt = profile.aptitude;
  if (!apt) return 0;

  let total = 0;
  let count = 0;

  // GPA component (weighted or unweighted)
  const gpa = apt.gpa_weighted ?? apt.gpa_unweighted;
  if (gpa > 0) {
    const gpaMax = apt.gpa_weighted ? 5.0 : 4.0;
    total += (gpa / gpaMax) * 100;
    count++;
  }

  // SAT component
  if (apt.sat_total > 0) {
    total += (apt.sat_total / 1600) * 100;
    count++;
  }

  // ACT component
  if (apt.act_total > 0) {
    total += (apt.act_total / 36) * 100;
    count++;
  }

  // AP component
  if (apt.ap_count > 0) {
    total += Math.min((apt.ap_count / 12) * 100, 100);
    count++;
  }

  return count > 0 ? Math.round(total / count) : 0;
}

// PASSION SCORE (0-100)
// EC commitment: 40pts, Leadership: 30pts, Awards: 30pts
function calculatePassionScore(profile: StudentProfile): number {
  const pass = profile.passion;
  if (!pass) return 0;

  let score = 0;

  // EC Commitment (40 points max)
  if (pass.ec_commitment_years > 0) {
    score += Math.min((pass.ec_commitment_years / 4) * 40, 40);
  }

  // Leadership (30 points)
  if (pass.leadership_level && pass.leadership_level !== 'PARTICIPANT') {
    score += 30;
  }

  // Awards (30 points)
  if (pass.ec_awards?.length > 0) {
    score += 30;
  }

  return Math.round(score);
}

// SERVICE SCORE (0-100)
function calculateServiceScore(profile: StudentProfile): number {
  const hours = profile.community?.service_hours || 0;
  return Math.round(Math.min((hours / 300) * 100, 100));
}

// IDENTITY SCORE (0-100)
// 25pts each for: subject, strengths, career, first-gen
function calculateIdentityScore(profile: StudentProfile): number {
  let score = 0;

  if (profile.operating?.favoriteSubject) score += 25;
  if (profile.operating?.strengths?.length > 0) score += 25;
  if (profile.operating?.careerDirection) score += 25;
  if (profile.demographics?.first_gen) score += 25;

  return score;
}

// OVERALL SCORE
const overallScore = Math.round(
  (aptitudeScore + passionScore + serviceScore + identityScore) / 4
);
```

#### Category Weights

```typescript
// lib/constants/defaults.ts
export const CATEGORY_WEIGHTS = {
  overall: {
    aptitude: 0.30,
    passion: 0.35,
    community: 0.25,
    narrative: 0.10,
  },
  aptitude: {
    gpa: 0.35,
    sat: 0.30,
    rigor: 0.20,
    awards: 0.15,
  },
  passion: {
    leadership: 0.35,
    project: 0.20,
    research: 0.20,
    commitment: 0.15,
    awards: 0.10,
  },
  community: {
    service: 0.35,
    impact: 0.35,
    hours: 0.20,
    description: 0.10,
  },
};
```

### 7.3 Context Multipliers (Chetty 2023)

```typescript
// lib/data/chetty-roi.ts
export const CHETTY_MULTIPLIERS = {
  legacy: {
    HARVARD: 5.0,
    YALE: 4.2,
    PRINCETON: 4.5,
    MIT: 0.0,  // No legacy preference
    // ...
  },
  first_gen: 1.15,
  athlete: {
    recruited: 2.5,
    walk_on: 1.3,
  },
  income_top_1: 1.20,
  ethnicity: {
    underrepresented: 1.15,
    asian: 0.85,
    white: 1.0,
  },
  high_school_saturation: {
    // NSC data: number of admits per year from same HS
    low: 0.05,      // < 2 admits/year
    medium: 0.0,    // 2-5 admits/year
    high: -0.08,    // > 5 admits/year
  },
};
```

### 7.4 Probability Calculation

```typescript
// Sigmoid formula for P_base
function calculateBaseProbability(ivyScore: number, school: SchoolConfig): number {
  const k = 0.1;  // Steepness
  const x0 = 50;  // Midpoint
  return 1 / (1 + Math.exp(-k * (ivyScore - x0)));
}

// Final probability with multipliers
function calculateFinalProbability(
  pBase: number,
  profile: StudentProfile,
  school: SchoolConfig
): number {
  let multiplier = 1.0;

  // Apply Chetty multipliers
  if (profile.demographics?.legacy?.includes(school.id)) {
    multiplier *= CHETTY_MULTIPLIERS.legacy[school.id];
  }
  if (profile.demographics?.first_gen) {
    multiplier *= CHETTY_MULTIPLIERS.first_gen;
  }
  // ... other multipliers

  // P_final = P_base × multiplier, capped at 95%
  return Math.min(pBase * multiplier, 0.95);
}
```

### 7.5 Archetype Detection

```typescript
// lib/scoring/archetypeDetector.ts

// 11 Universal Archetypes
export const UNIVERSAL_ARCHETYPES = [
  'SCHOLAR',        // High GPA, research focus
  'RESEARCHER',     // Published work, STEM depth
  'LEADER',         // Strong leadership positions
  'ENTREPRENEUR',   // Business/startup experience
  'ATHLETE',        // Recruited athlete
  'ARTIST',         // Creative portfolio
  'ACTIVIST',       // Social impact focus
  'INNOVATOR',      // Tech/invention focus
  'HUMANITARIAN',   // Service-first approach
  'POLYMATH',       // Multi-domain excellence
  'SPECIALIST',     // Deep spike in one area
];

// 9 Legacy Archetypes (saturation warnings)
export const LEGACY_ARCHETYPES = [
  'COOKIE_CUTTER_BAY_AREA_CS',
  'GENERIC_PREMED',
  'STANDARD_BUSINESS_TRACK',
  // ...
];

function detectArchetype(profile: StudentProfile): ArchetypeResult {
  // Check spike category
  const spikeCategory = identifySpikeCategory(profile);

  // Check region
  const region = profile.high_school?.region;

  // Check saturation
  const saturation = profile.high_school?.saturation_level;

  // Check leadership
  const leadershipLevel = profile.passion?.leadership_level;

  // Match to archetype
  return matchArchetype(spikeCategory, region, saturation, leadershipLevel);
}
```

---

## 8. Insights System

### 8.1 Insight Architecture

```typescript
// lib/insights/InsightEngine.ts

// 7 Insight Categories
type InsightCategory =
  | 'HYPER_LOCAL'    // High school peer benchmarking
  | 'CONTEXT'        // Demographics, region, hooks
  | 'TEMPORAL'       // Grade-aware timing
  | 'APTITUDE'       // GPA, SAT, rigor
  | 'PASSION'        // Leadership, research, impact
  | 'PSYCHOMETRIC'   // Grit, burnout, time management
  | 'INSTITUTIONAL'; // CDS benchmarks, school-specific

// 4 Severity Levels
type InsightSeverity = 'critical' | 'warning' | 'positive' | 'neutral';

interface Insight {
  id: string;
  category: InsightCategory;
  severity: InsightSeverity;
  priority: number;  // 1-10
  title: string;
  description: string;
  action?: string;
  data_source?: string;
}
```

### 8.2 Real-time Generation

```typescript
// lib/insights/realtimeInsights.ts

export async function generateInsights(
  profile: StudentProfile,
  context: InsightContext
): Promise<Insight[]> {
  const insights: Insight[] = [];

  // Generate category-specific insights
  insights.push(...generateAptitudeInsights(profile));
  insights.push(...generatePassionInsights(profile));
  insights.push(...generateContextInsights(profile));
  insights.push(...generateTemporalInsights(profile, context.grade));
  insights.push(...generateHyperLocalInsights(profile));

  // Sort by priority
  return insights.sort((a, b) => b.priority - a.priority);
}

// Trigger on profile updates
export function setupInsightSubscription(
  store: StudentStore,
  insightsStore: InsightsStore
) {
  store.subscribe(
    (state) => state.profile,
    async (profile) => {
      insightsStore.setGenerating(true);
      const insights = await generateInsights(profile, getCurrentContext());
      insights.forEach(insight => insightsStore.addInsight(insight));
      insightsStore.setGenerating(false);
    }
  );
}
```

---

## 9. Game Plan Engine

### 9.1 Booster System

```typescript
// lib/gamePlan/gamePlanEngine.ts

// Booster Categories
type BoosterCategory =
  | 'APTITUDE'      // GPA/SAT/Rigor improvements
  | 'PASSION'       // EC intensity, research, leadership
  | 'COMMUNITY'     // Service hours, impact scaling
  | 'NARRATIVE'     // Essay quality, storytelling
  | 'LOOPHOLE'      // Uncommon paths
  | 'NON_ACADEMIC'  // Character, resilience
  | 'STRATEGIC';    // School-specific targeting

interface Booster {
  id: string;
  title: string;
  description: string;
  category: BoosterCategory;

  // Impact
  probability_boost: number;  // +0.05 to +0.15
  pillar_boost: {
    aptitude?: number;
    passion?: number;
    community?: number;
    narrative?: number;
  };

  // Feasibility
  time_commitment: number;  // hours
  effort_level: 'low' | 'medium' | 'high';
  time_window: 'weeks' | 'months' | 'years';

  // ROI
  roi_score: number;  // probability boost / time investment
}
```

### 9.2 ROI Calculation

```typescript
function calculateBoosterROI(
  booster: Booster,
  currentProbability: number,
  profile: StudentProfile
): number {
  // Projected probability after booster
  const boostedProbability = Math.min(
    currentProbability + booster.probability_boost,
    0.95
  );

  // ROI = probability gain / time investment
  const probabilityGain = boostedProbability - currentProbability;
  const roi = probabilityGain / booster.time_commitment;

  // Adjust for feasibility
  const feasibilityMultiplier = calculateFeasibility(booster, profile);

  return roi * feasibilityMultiplier;
}

function calculateFeasibility(booster: Booster, profile: StudentProfile): number {
  // Check available time (168-hour framework)
  const reclaimableHours = 168 - profile.operating?.committed_hours || 40;

  if (booster.time_commitment > reclaimableHours * 4) {
    return 0.5;  // Low feasibility
  }

  // Check burnout risk
  if (profile.psychometrics?.burnout_risk === 'high') {
    return 0.7;
  }

  return 1.0;
}
```

### 9.3 Recommendation Algorithm

```typescript
async function generateBoosterRecommendations(
  profile: StudentProfile,
  targetSchools: string[]
): Promise<BoosterRecommendations> {
  // Get all eligible boosters
  const allBoosters = getEligibleBoosters(profile);

  // Calculate ROI for each
  const scoredBoosters = allBoosters.map(booster => ({
    ...booster,
    roi: calculateBoosterROI(booster, getCurrentProbability(profile), profile),
  }));

  // Sort by ROI
  const sortedBoosters = scoredBoosters.sort((a, b) => b.roi - a.roi);

  // Select top 3 with diversity
  const top3 = selectDiverseTop3(sortedBoosters);

  return {
    top_3_boosters: top3,
    all_eligible_boosters: sortedBoosters,
    total_time_commitment: top3.reduce((sum, b) => sum + b.time_commitment, 0),
    projected_improvement: calculateProjectedImprovement(top3, profile),
    burnout_warning: assessBurnoutRisk(top3, profile),
  };
}
```

---

## 10. Multi-Agent System

### 10.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT SYSTEM                           │
│                   (Python 3.13 + Agno + LangGraph)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Assessment  │    │  Execution  │    │  GamePlan   │         │
│  │   Agent     │    │   Agent     │    │   Agent     │         │
│  │             │    │             │    │             │         │
│  │ - Identity  │    │ - Crisis    │    │ - Phases    │         │
│  │ - Archetype │    │ - Blockers  │    │ - Boosters  │         │
│  │ - Readiness │    │ - Strategy  │    │ - Timeline  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│  ┌─────────────┐    ┌─────────────┐                            │
│  │   Awards    │    │ Opportunity │                            │
│  │   Agent     │    │   Agent     │                            │
│  │             │    │             │                            │
│  │ - Matching  │    │ - Programs  │                            │
│  │ - Strategy  │    │ - Timing    │                            │
│  │ - Timeline  │    │ - Fit       │                            │
│  └─────────────┘    └─────────────┘                            │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                       SHARED TOOLS                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │    CRI      │    │  Database   │    │   Search    │         │
│  │ Calculator  │    │  (Supabase) │    │   Tools     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Agent Implementations

```python
# agents/agents/assessment.py
class AssessmentAgent(StatefulAgent):
    """
    Synthesizes student identity and computes readiness.
    """

    def __init__(self):
        super().__init__(
            name="assessment",
            model="gemini-2.0-flash",
            tools=[cri_tool, database_tool],
        )

    async def enhance_profile(self, profile: dict) -> dict:
        """
        Analyzes profile and generates:
        - Archetype classification
        - Narrative DNA
        - Readiness assessment
        - Gap identification
        """
        # Layer 4 intelligence integration
        enhanced = await self.run(
            prompt=self._build_assessment_prompt(profile),
            context={"profile": profile}
        )
        return enhanced


# agents/agents/execution.py
class ExecutionAgent(StatefulAgent):
    """
    Bridges strategy-execution gap.
    Handles crisis situations and blocker resolution.
    """

    def __init__(self):
        super().__init__(
            name="execution",
            model="gemini-2.0-flash",
            tools=[cri_tool, database_tool],
        )
        self.crisis_graph = CrisisAlchemyGraph()

    async def handle_crisis(self, crisis: dict) -> dict:
        """
        Routes crisis through LangGraph workflow.
        """
        return await self.crisis_graph.run(crisis)

    async def identify_blockers(self, profile: dict, goal: str) -> list:
        """
        Identifies execution blockers and suggests resolutions.
        """
        return await self.run(
            prompt=self._build_blocker_prompt(profile, goal),
            context={"profile": profile, "goal": goal}
        )


# agents/agents/gameplan.py
class GamePlanAgent(StatefulAgent):
    """
    Strategic activity planning and timeline optimization.
    """

    async def generate_plan(
        self,
        profile: dict,
        target_schools: list,
        timeframe: str
    ) -> dict:
        """
        Generates phased game plan with:
        - Milestone timeline
        - Booster sequencing
        - Risk assessment
        """
        return await self.run(
            prompt=self._build_gameplan_prompt(profile, target_schools),
            context={
                "profile": profile,
                "schools": target_schools,
                "timeframe": timeframe
            }
        )
```

### 10.3 LangGraph Workflows

```python
# agents/graphs/crisis_alchemy.py
from langgraph.graph import StateGraph, END

class CrisisAlchemyGraph:
    """
    Crisis handling workflow using LangGraph.
    """

    def __init__(self):
        self.graph = StateGraph(CrisisState)

        # Add nodes
        self.graph.add_node("assess", self.assess_crisis)
        self.graph.add_node("categorize", self.categorize_crisis)
        self.graph.add_node("resolve", self.generate_resolution)
        self.graph.add_node("escalate", self.escalate_to_human)

        # Add edges
        self.graph.add_edge("assess", "categorize")
        self.graph.add_conditional_edges(
            "categorize",
            self.route_crisis,
            {
                "resolvable": "resolve",
                "needs_escalation": "escalate",
            }
        )
        self.graph.add_edge("resolve", END)
        self.graph.add_edge("escalate", END)

        self.compiled = self.graph.compile()

    async def run(self, crisis: dict) -> dict:
        state = CrisisState(crisis=crisis)
        result = await self.compiled.ainvoke(state)
        return result
```

### 10.4 Agent Tools

```python
# agents/tools/cri.py
@tool
def calculate_cri(profile: dict) -> dict:
    """
    Calculate Crisis Response Initiative score.

    CRI measures student's ability to handle challenges:
    - Resilience indicators
    - Support system strength
    - Historical crisis handling
    """
    return {
        "cri_score": compute_cri_score(profile),
        "risk_factors": identify_risk_factors(profile),
        "support_recommendations": generate_support_recs(profile),
    }


# agents/tools/database.py
@tool
def query_opportunities(criteria: dict) -> list:
    """
    Query opportunity database for matching programs.
    """
    supabase = get_supabase_client()
    return supabase.table("opportunities").select("*").match(criteria).execute()

@tool
def save_agent_state(profile_id: str, agent_type: str, state: dict) -> bool:
    """
    Persist agent state for conversation continuity.
    """
    supabase = get_supabase_client()
    return supabase.table("agent_states").upsert({
        "profile_id": profile_id,
        "agent_type": agent_type,
        "state": state,
        "updated_at": datetime.now().isoformat()
    }).execute()
```

---

## 11. Data Layer & Persistence

### 11.1 Supabase Schema

```sql
-- Core assessment table
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT UNIQUE NOT NULL,
  profile_data JSONB NOT NULL,
  game_plan_data JSONB,
  scores JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Coach sessions
CREATE TABLE coach_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID REFERENCES assessments(id),
  scheduled_at TIMESTAMPTZ NOT NULL,
  calendly_event_id TEXT,
  status TEXT DEFAULT 'scheduled',
  notes TEXT
);

-- Agent state persistence
CREATE TABLE agent_states (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id TEXT NOT NULL,
  agent_type TEXT NOT NULL,
  state JSONB NOT NULL,
  version INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(profile_id, agent_type)
);

-- Row Level Security
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous access by session_id"
ON assessments FOR ALL
USING (session_id = current_setting('app.session_id', true));
```

### 11.2 Data Flow

```
┌─────────────────┐
│   User Input    │
│   (Frames)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   Zustand       │────▶│  localStorage   │
│   Stores        │     │  (persist)      │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│   API Routes    │
│  (/api/score)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Supabase      │
│   (PostgreSQL)  │
└─────────────────┘
```

### 11.3 Supabase Client

```typescript
// lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js';
import type { Database } from './database.types';

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Server-side client
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr';

export function createServerSupabase() {
  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}
```

---

## 12. Type System

### 12.1 Core Student Profile

```typescript
// lib/types/student.ts

export interface StudentProfile {
  // Identity
  identity: {
    name: string;
    email?: string;
    grade: 9 | 10 | 11 | 12;
  };

  // Layer 1: Core Attributes
  aptitude: AptitudeAttributes;
  passion: PassionAttributes;
  community: CommunityAttributes;

  // Layer 3: Context
  demographics: DemographicContext;
  high_school: HighSchoolContext;

  // Layer 4: Intelligence
  operating: OperatingData;
  psychometrics?: StudentPsychometrics;

  // Meta
  target_schools: string[];
  classification?: ProfileClassification;
  completeness?: CompletenessFlags;
}

export interface AptitudeAttributes {
  gpa_weighted?: number;      // 0.0-5.0
  gpa_unweighted?: number;    // 0.0-4.0
  sat_total?: number;         // 400-1600
  act_total?: number;         // 1-36
  ap_count?: number;          // 0-20+
  ap_subjects?: string[];
  academic_awards?: string[];
}

export interface PassionAttributes {
  leadership_level: 'PARTICIPANT' | 'MEMBER' | 'OFFICER' | 'PRESIDENT' | 'FOUNDER' | 'STATE_LEADER' | 'NATIONAL_LEADER';
  ec_commitment_years: number;  // 0-4
  ec_awards?: string[];
  research_experience?: boolean;
  publications?: number;
}

export interface CommunityAttributes {
  service_hours: number;        // 0-1000+
  service_leadership?: boolean;
  impact_description?: string;
}

export interface DemographicContext {
  ethnicity?: string;
  first_gen?: boolean;
  legacy?: string[];      // School IDs
  athlete?: {
    sport: string;
    level: 'recruited' | 'walk_on' | 'club';
  };
  income_bracket?: string;
}

export interface OperatingData {
  favoriteSubject?: string;
  strengths?: string[];
  careerDirection?: string;
  availableHoursPerWeek?: number;
  committed_hours?: number;
}
```

### 12.2 Scoring Types

```typescript
export interface IvyReadyScore {
  total_score: number;  // 0-100
  category_scores: {
    aptitude: number;   // 0-100
    passion: number;    // 0-100
    community: number;  // 0-100
    narrative: number;  // 0-100
  };
  percentile_rank: number;
}

export interface SchoolProbability {
  school_id: string;
  school_name: string;
  p_base: number;       // Base probability
  p_final: number;      // After multipliers
  fit_level: 'reach' | 'target' | 'safety';
  rubric_scores: {
    academic: number;   // 1-6 SFFA scale
    extracurricular: number;
    personal: number;
    recommendation: number;
  };
  warnings?: string[];
}

export interface AssessmentResults {
  ivy_ready_score: IvyReadyScore;
  school_probabilities: SchoolProbability[];
  helping_factors: string[];
  holding_back_factors: string[];
  archetype_detected: string;
  archetype_label: string;
  narrative_tagline: string;
}
```

### 12.3 Digital Twin Types

```typescript
export interface TwinGear {
  head: string;       // Helmet style
  torso: string;      // Armor type
  weapon: string;     // Primary tool
  shield: string;     // Defense
  accessory: string;  // Special item
  aura: string;       // Visual effect
}

export interface DigitalTwin {
  twin_id: string;
  school_id?: string;
  theme: string;
  gear: TwinGear;
  completion_percent: number;
  probability?: number;
  gaps: string[];
}

export interface TwinFleet {
  base_twin: DigitalTwin;
  school_twins: DigitalTwin[];
}
```

---

## 13. Visualization System

### 13.1 Ring Visualization

```typescript
// components/rings/CircularProgress.tsx

// 5-ring concentric visualization
// Ring order (inner to outer):
// 1. Narrative (Identity) - Gray
// 2. Community (Service) - Teal
// 3. Passion - Coral
// 4. Aptitude - Golden
// 5. Total Score - Brand Gradient

const RING_CONFIG = {
  colors: {
    total: 'url(#ivyGradient)',
    aptitude: '#FFBB6D',
    passion: '#FF6E6D',
    community: '#55AAAA',
    narrative: '#979797',
  },
  radii: {
    narrative: 78,
    community: 98,
    passion: 118,
    aptitude: 138,
    total: 162,
  },
  strokeWidth: {
    default: 12,
    total: 18,
  },
};

// SVG gradient for brand colors
<linearGradient id="ivyGradient">
  <stop offset="0%" stopColor="#641432" />
  <stop offset="30%" stopColor="#8A1D45" />
  <stop offset="50%" stopColor="#FE4A22" />
  <stop offset="70%" stopColor="#FF7224" />
  <stop offset="100%" stopColor="#FFBB6D" />
</linearGradient>
```

### 13.2 Pillar Cards

```typescript
// components/rings/PillarCards.tsx

// 2x2 grid with animated wave fills
const PILLAR_CONFIG = [
  { key: 'aptitude', label: 'Aptitude', icon: BookOpen, color: '#FFBB6D' },
  { key: 'passion', label: 'Passion', icon: Heart, color: '#FF6E6D' },
  { key: 'community', label: 'Service', icon: Users, color: '#55AAAA' },
  { key: 'narrative', label: 'Identity', icon: Sparkles, color: '#9698A6' },
];

// Wave animation using SVG path
function WaveAnimation({ score, color }) {
  const waveHeight = (100 - score) / 100;  // Inverse for fill effect
  return (
    <motion.path
      d={generateWavePath(waveHeight)}
      fill={color}
      animate={{ y: [0, -5, 0] }}
      transition={{ repeat: Infinity, duration: 2 }}
    />
  );
}
```

### 13.3 Twin Visualization

```typescript
// components/twin/TwinAvatar.tsx

// 3D avatar using Three.js + React Three Fiber
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';

function TwinAvatar({ twin, size = 300 }) {
  const { gear, completion_percent, theme } = twin;

  return (
    <Canvas style={{ width: size, height: size }}>
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} />

      {/* Base character */}
      <Character gear={gear} theme={theme} />

      {/* Completion aura */}
      <CompletionAura percent={completion_percent} />

      <OrbitControls enableZoom={false} />
    </Canvas>
  );
}
```

---

## 14. Analytics & Tracing

### 14.1 Analytics System

```typescript
// lib/analytics/SessionTracker.ts
export class SessionTracker {
  private sessionId: string;
  private events: AnalyticsEvent[] = [];

  trackFrameView(frameId: number) {
    this.events.push({
      type: 'frame_view',
      frameId,
      timestamp: Date.now(),
    });
  }

  trackInteraction(action: string, metadata?: Record<string, any>) {
    this.events.push({
      type: 'interaction',
      action,
      metadata,
      timestamp: Date.now(),
    });
  }

  trackScore(scoreType: string, value: number) {
    this.events.push({
      type: 'score',
      scoreType,
      value,
      timestamp: Date.now(),
    });
  }
}
```

### 14.2 Trace System

```typescript
// lib/trace/TraceContext.ts
export class TraceContext {
  private traceId: string;
  private spans: TraceSpan[] = [];

  startSpan(name: string, attributes?: Record<string, any>): TraceSpan {
    const span = new TraceSpan(name, this.traceId, attributes);
    this.spans.push(span);
    return span;
  }

  // Example usage:
  // const span = trace.startSpan('calculate_score');
  // const result = calculateScore(profile);
  // span.end({ result });
}

// lib/trace/loggers.ts
export const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data);
  },
  warn: (message: string, data?: any) => {
    console.warn(`[WARN] ${message}`, data);
  },
  error: (message: string, error?: Error) => {
    console.error(`[ERROR] ${message}`, error);
  },
  debug: (message: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`, data);
    }
  },
};
```

---

## 15. Testing Infrastructure

### 15.1 E2E Tests

```typescript
// e2e/huda-benchmark.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Huda Benchmark - Full Assessment Flow', () => {
  test('completes full assessment journey', async ({ page }) => {
    await page.goto('/');

    // Frame 1: Warmup
    await page.click('text=Start Assessment');
    await page.fill('[name="name"]', 'Test Student');
    await page.click('text=Continue');

    // Frame 2: Snapshot
    await page.fill('[name="gpa"]', '3.8');
    await page.fill('[name="sat"]', '1450');
    await page.click('text=Continue');

    // ... continue through all frames

    // Verify final score
    await expect(page.locator('[data-testid="ivy-score"]')).toBeVisible();
  });
});

// e2e/v10-agents.spec.ts
test.describe('Agent Integration Tests', () => {
  test('assessment agent enhances profile', async ({ request }) => {
    const response = await request.post('/api/agents/assessment/enhance', {
      data: { profile: mockProfile },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.archetype).toBeDefined();
  });
});
```

### 15.2 Test Commands

```bash
# Unit tests
npm run test:scoring

# E2E tests
npm run test:e2e

# Specific test suites
npm run test:e2e:huda      # Benchmark test
npm run test:e2e:agents    # Agent tests
npm run test:e2e:ui        # UI flow tests

# With UI (headed)
npx playwright test --headed
```

---

## 16. Deployment Configuration

### 16.1 Environment Variables

```bash
# .env.local

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# Google AI (Gemini)
GOOGLE_GENERATIVE_AI_API_KEY=xxx

# Calendly
CALENDLY_API_KEY=xxx
NEXT_PUBLIC_CALENDLY_URL=https://calendly.com/xxx

# Feature Flags
NEXT_PUBLIC_ENABLE_AGENTS=true
NEXT_PUBLIC_ENABLE_INSIGHTS=true
```

### 16.2 Vercel Configuration

```json
// vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "regions": ["iad1"],
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  }
}
```

### 16.3 Next.js Configuration

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverComponentsExternalPackages: ['@supabase/supabase-js'],
  },
  images: {
    domains: ['xxx.supabase.co'],
  },
  async rewrites() {
    return [
      {
        source: '/api/agents/:path*',
        destination: process.env.AGENTS_API_URL + '/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
```

---

## 17. Appendix: File Reference

### Key Files by Purpose

| Purpose | Files |
|---------|-------|
| **Main Entry** | `app/page.tsx`, `app/layout.tsx` |
| **Assessment Frames** | `components/frames/Frame1-6*.tsx` |
| **Dashboard** | `app/dashboard/page.tsx`, `components/tabs/*.tsx` |
| **Scoring Engine** | `lib/scoring/engine.ts`, `app/api/score/route.ts` |
| **State Management** | `lib/store/use*Store.ts` |
| **Types** | `lib/types/student.ts` |
| **Constants** | `lib/constants/defaults.ts`, `brand.ts`, `design.ts` |
| **Insights** | `lib/insights/InsightEngine.ts`, `realtimeInsights.ts` |
| **Game Plan** | `lib/gamePlan/gamePlanEngine.ts` |
| **Multi-Agent** | `agents/main.py`, `agents/agents/*.py` |
| **Database** | `supabase/migrations/*.sql`, `lib/supabase/*.ts` |
| **Visualization** | `components/rings/*.tsx`, `components/twin/*.tsx` |

### Recent Updates (v12.0)

1. **Dynamic Scoring**: Dashboard now uses same scoring functions as Frame6ProfileReveal
2. **Brand Color Alignment**: Updated GRADIENTS and COLORS to use Ivylevel brand (maroon #641432, orange #FF4A23)
3. **CircularProgress Fix**: Center circle now properly centered using flexbox
4. **Responsive Layout**: Side-by-side layout for rings and pillar cards

---

**Document Version:** 12.0
**Generated:** January 4, 2026
**Maintainer:** IvyQuest Engineering Team
