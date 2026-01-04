# IvyQuest v2.2 - Complete Technical Specification

> **Version**: 2.2.0
> **Generated**: 2025-12-21
> **Status**: AUTHORITATIVE REFERENCE

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [UI/UX Architecture](#4-uiux-architecture)
5. [State Management](#5-state-management)
6. [Data Models & Types](#6-data-models--types)
7. [Scoring Engine](#7-scoring-engine)
8. [Database & Persistence](#8-database--persistence)
9. [API Layer](#9-api-layer)
10. [External Integrations](#10-external-integrations)
11. [End-to-End Data Flow](#11-end-to-end-data-flow)
12. [File Structure](#12-file-structure)
13. [Constants & Configuration](#13-constants--configuration)
14. [Known Issues & Roadmap](#14-known-issues--roadmap)

---

## 1. Executive Summary

### 1.1 Purpose

IvyQuest is an AI-powered college admissions assessment platform that guides students through a comprehensive evaluation, providing personalized insights, probability calculations, and actionable recommendations for elite university admissions.

### 1.2 Core User Journey

```
Landing (/) → Quest (/quest) → Frames 1-6 → Results (/results)
```

### 1.3 Key Statistics

| Metric | Value |
|--------|-------|
| **Student Attributes** | 58 across 4 layers |
| **Assessment Intelligence Points** | 39 |
| **Zustand Stores** | 10 |
| **Target Schools Supported** | 12 elite universities |
| **Boosters in Engine** | 20+ |
| **Frame Components** | 6 main + variants |
| **API Endpoints** | 3 |

---

## 2. Technology Stack

### 2.1 Core Technologies

| Layer | Technology | Version |
|-------|------------|---------|
| **Framework** | Next.js (App Router) | 14.2.x |
| **Language** | TypeScript | 5.x |
| **State** | Zustand + Immer | 4.5.x |
| **Database** | Supabase | 2.87.x |
| **Styling** | Tailwind CSS | 3.4.x |
| **Animation** | Framer Motion | 11.x |
| **PDF** | @react-pdf/renderer | 4.3.x |
| **Validation** | Zod | 3.23.x |
| **AI/NLP** | Google Generative AI | 0.24.x |
| **Forms** | React Hook Form | 7.53.x |

### 2.2 Development Dependencies

| Tool | Purpose |
|------|---------|
| Playwright | E2E Testing |
| ESLint | Code Quality |
| TypeScript | Type Safety |

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Frame     │  │   Layout    │  │     UI      │              │
│  │ Components  │  │ Components  │  │ Components  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┴────────────────┘                      │
│                          │                                       │
│  ┌───────────────────────┴───────────────────────┐              │
│  │              ZUSTAND STORES (10)               │              │
│  │  Student | Session | Results | Insights | UI   │              │
│  │  Frame3 | Frame4 | Frame5 | Twin | Trace      │              │
│  └───────────────────────┬───────────────────────┘              │
│                          │                                       │
│  ┌───────────────────────┴───────────────────────┐              │
│  │           CONTEXT PROVIDERS (3)                │              │
│  │    Analytics | Feedback | Insights             │              │
│  └───────────────────────────────────────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                        API LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ /api/score   │  │/api/assessment│ │   /api/nlp   │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                    │
├─────────┴─────────────────┴─────────────────┴────────────────────┤
│                     EXTERNAL SERVICES                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Supabase │  │  Gemini  │  │ Calendly │  │  Sentry  │         │
│  │    DB    │  │    AI    │  │ Booking  │  │ Logging  │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow Direction

```
Supabase (Truth) → API Layer → Zustand (Cache) → Components (Display)
                                    ↑
                    User Input → Validation → API → Supabase
```

---

## 4. UI/UX Architecture

### 4.1 Frame Components

| Frame | File | Purpose | Cards |
|-------|------|---------|-------|
| **1** | `Frame1Warmup.tsx` | Identity, Schools, Major | 4 |
| **2** | `Frame2Snapshot.tsx` | GPA, Tests, Rigor, Awards | 5 |
| **3** | `Frame3Building.tsx` | Passion, Leadership, Projects | 10 |
| **4** | `Frame4Context.tsx` | Demographics, High School, Operating | 15 |
| **5** | `Frame5GamePlan.tsx` | Action phases, Recommendations | 6 |
| **6** | `Frame6ProfileReveal.tsx` | Scores, Probabilities, Analysis | 4 |

### 4.2 Layout System

```
app/
├── layout.tsx                    # Root layout with providers
├── globals.css                   # Design system CSS
├── quest/
│   ├── layout.tsx               # Quest layout with debug overlay
│   ├── page.tsx                 # Quest entry/navigation
│   └── [frameId]/page.tsx       # Dynamic frame renderer
└── results/page.tsx             # Final results display
```

### 4.3 Component Hierarchy

```
components/
├── frames/                      # 6 Frame components + variants
│   ├── Frame1Warmup.tsx
│   ├── Frame2Snapshot.tsx
│   ├── Frame3Building.tsx
│   ├── Frame4Context.tsx
│   ├── Frame5GamePlan.tsx
│   ├── Frame6ProfileReveal.tsx
│   ├── operating/               # Frame 4 sub-cards
│   ├── powerups/                # Booster components
│   └── reveal/                  # Score reveal animations
├── layout/
│   ├── AssessmentLayout.tsx     # Global assessment wrapper
│   └── SplitFrameLayout.tsx     # 2-column input layout
├── ui/                          # 14 base components
│   ├── Card.tsx                 # Glassmorphism card
│   ├── Input.tsx                # Form input
│   ├── Button.tsx               # 6 variants, 4 sizes
│   ├── Slider.tsx               # Range input
│   ├── ChipSelector.tsx         # Multi-select chips
│   └── ScoreRing.tsx            # Circular progress
├── insights/                    # Real-time feedback
├── quest/                       # Game-like components
├── rings/                       # Circular progress rings
├── twin/                        # Digital twin visualization
└── booking/                     # Coach scheduling
```

### 4.4 Brand Color System

**CRITICAL**: Never use dark-mode Tailwind classes in Frame components.

```typescript
// lib/constants/brand.ts
BRAND_COLORS = {
  // Primary Brand
  primary: '#FF4A23',              // Ivylevel orange (main CTA)
  secondary: '#641432',            // Ivylevel maroon (headings)

  // Text Colors
  textHeading: '#020202',          // Near-black
  textPrimary: '#020202',
  textSecondary: '#616479',        // Gray
  textMuted: '#9698A6',            // Light gray

  // Backgrounds
  bgPrimary: '#FFFFFF',            // White cards
  bgPage: '#F7F8FA',               // Page background
  bgCard: '#F5F4F3',               // Warm gray

  // Semantic
  success: '#1DBF73',              // Green
  warning: '#EAB705',              // Yellow
  error: '#dc2626',                // Red
}
```

### 4.5 Animation Patterns

- **Framer Motion** for all component animations
- **Entry animations**: `initial={{ opacity: 0, y: 20 }}` → `animate={{ opacity: 1, y: 0 }}`
- **Floating effects**: `animate={{ y: [0, -8, 0] }}` with `repeat: Infinity`
- **AnimatePresence** for mount/unmount transitions

---

## 5. State Management

### 5.1 Zustand Store Architecture

| Store | Persist Key | Purpose |
|-------|-------------|---------|
| `useStudentStore` | `ivyquest-student-profile` | Student profile (58 attributes) |
| `useSessionStore` | `ivyquest-session` | Session & navigation state |
| `useResultsStore` | `ivyquest-results` | Assessment results cache |
| `useInsightsStore` | — | Real-time insight generation |
| `useFrame3Store` | `ivyquest-frame3-operating` | Frame 3 scenarios & signals |
| `useFrame4Store` | — | Score reveal state |
| `useFrame5Store` | — | Booster selection state |
| `useUIStore` | — | UI state (modals, toasts) |
| `useTwinStore` | `ivyquest-twin-fleet` | Digital twin fleet |
| `useTraceStore` | — | Debug tracing (dev only) |

### 5.2 Middleware Stack

```typescript
create<StoreState>()(
  devtools(                        // Redux DevTools
    persist(                       // localStorage persistence
      immer((set, get) => ({...})),// Immutable updates
      { name: 'storage-key' }
    ),
    { name: 'StoreName' }
  )
)
```

### 5.3 Context Providers

| Provider | Purpose |
|----------|---------|
| `InsightsProvider` | Auto-subscription to profile changes |
| `AnalyticsProvider` | Session/frame tracking |
| `FeedbackProvider` | Toast/hint/achievement notifications |

### 5.4 Auto-Subscription Pattern

```typescript
// Insights auto-regenerate when StudentStore changes
useStudentStore.subscribe((state) => {
  if (state.profile !== previousProfile) {
    useInsightsStore.getState().generateInsights();
  }
});
```

---

## 6. Data Models & Types

### 6.1 Core Student Profile

```typescript
interface StudentProfile {
  session_id: string;
  timestamp: string;

  // Identity
  identity: StudentIdentity;

  // Layer 2: Targets
  target_schools: string[];
  intended_major: string;
  major_certainty: MajorCertainty;

  // Layer 1: Core Attributes (58 total)
  aptitude: AptitudeAttributes;      // GPA, SAT, Rigor, Awards
  passion: PassionAttributes;        // Leadership, Projects, Research
  community: CommunityAttributes;    // Service, Impact, Hours

  // Layer 3: Context Multipliers
  high_school: HighSchoolContext | null;
  demographics: DemographicContext;
  major_context: MajorContext;

  // Layer 4: Assessment Intelligence (39 points)
  assessment_intelligence: AssessmentIntelligence;

  // Operating Data (Frame 4)
  operating?: OperatingData;

  // Classification
  completeness?: ProfileCompleteness;
  classification?: ProfileClassification;
}
```

### 6.2 Layer 1: Core Attributes

#### Aptitude (35% of Ivy+ Score)
| Attribute | Weight | Type |
|-----------|--------|------|
| GPA | 35% | `number \| null` (0-5.0 weighted) |
| SAT/ACT | 30% | `number \| null` (400-1600 / 1-36) |
| AP Rigor | 20% | `number \| null` (count + avg score) |
| Academic Awards | 15% | `string[]` |

#### Passion (35% of Ivy+ Score)
| Attribute | Weight | Type |
|-----------|--------|------|
| Leadership | 35% | `LeadershipLevel` |
| Projects | 20% | `number` (people impacted) |
| Research | 20% | `ResearchLevel` |
| EC Commitment | 15% | `number` (years + hours/week) |
| EC Awards | 10% | `string[]` |

#### Community (25% of Ivy+ Score)
| Attribute | Weight | Type |
|-----------|--------|------|
| Service Leadership | 35% | `ServiceLeadership` |
| Community Impact | 35% | `number` (people affected) |
| Service Hours | 20% | `number` (total hours) |
| Description | 10% | `string` |

### 6.3 Layer 3: Context Multipliers (Chetty 2023)

| Factor | Multiplier | Source |
|--------|------------|--------|
| Legacy (Harvard) | 5.0x | SFFA Trial |
| Legacy (MIT) | 0.0x | Merit-only policy |
| First Generation | 1.15x | Chetty 2023 |
| Recruited Athlete | 2.5x | Chetty 2023 |
| Top 1% Income | 1.20x | Chetty 2023 |
| High Saturation HS | -8% to +5% | NSC Data |

### 6.4 Type Enumerations

```typescript
type Grade = 9 | 10 | 11 | 12 | 'gap';
type Role = 'STUDENT' | 'PARENT';
type MajorCertainty = 'EXPLORING' | 'LIKELY' | 'LOCKED';

type SpikeCategory = 'RESEARCH' | 'LEADER' | 'SERVICE' | 'CREATE' |
                     'BUSINESS' | 'SPORTS' | 'FIGURING';

type LeadershipLevel = 'FOUNDER_NATIONAL' | 'FOUNDER_STATE' |
                       'STATE_PRES' | 'SCHOOL_PRES' |
                       'OFFICER' | 'PARTICIPANT';

type ResearchLevel = 'NATIONAL' | 'STATE' | 'SCHOOL' |
                     'INDEPENDENT' | 'NONE';

type ProfileTier = 'fresh-start' | 'emerging' | 'optimization';

type SchoolFit = 'BEST_FIT' | 'STRONG_FIT' | 'TOUGH' | 'WORST_FIT';
```

---

## 7. Scoring Engine

### 7.1 Location & Architecture

**File**: `lib/scoring/engine.ts` (939 lines)

```
lib/scoring/
├── engine.ts              # Main scoring calculations
├── archetypeDetector.ts   # Student archetype detection
└── factorAnalysis.ts      # Helping/holding factors
```

### 7.2 Normalization Functions (Layer 1 → 0.0-1.0)

#### GPA Normalization
```typescript
// SFFA Rubric Mapping
4.0+ → 1.0       (Summa, top 1%)
3.85-3.99 → 0.80-1.0  (Magna, top 5%)
3.7-3.84 → 0.60-0.80  (Cum Laude, top 10%)
3.5-3.69 → 0.40-0.60  (Good, top 25%)
3.0-3.49 → 0.20-0.40  (Average, top 50%)
<3.0 → 0.0-0.20       (Below)
```

#### SAT Normalization
```typescript
// CollegeBoard 2025 Percentile Mapping
1600 → 1.0       (99.9th percentile)
1500-1590 → 0.85-0.95  (99th)
1400-1490 → 0.70-0.85  (95th)
1300-1390 → 0.55-0.70  (87th)
1200-1290 → 0.40-0.55  (76th)
<1200 → <0.40
```

#### Leadership Normalization
```typescript
FOUNDER_NATIONAL → 1.0
FOUNDER_STATE → 0.85
STATE_PRES → 0.75
SCHOOL_PRES → 0.70
OFFICER → 0.50
PARTICIPANT → 0.25
```

### 7.3 Ivy+ Ready Score Calculation

**Formula**: Weighted sum of category scores (0-100)

```typescript
CATEGORY_WEIGHTS = {
  aptitude: 0.30,    // 30%
  passion: 0.35,     // 35%
  community: 0.25,   // 25%
  narrative: 0.10,   // 10%
}

IvyReadyScore = (
  aptitude_score × 0.30 +
  passion_score × 0.35 +
  community_score × 0.25 +
  narrative_score × 0.10
)
```

### 7.4 School Probability Calculation

**Sigmoid Formula** (Spec Page 8-9):

```
P_base = 1 / (1 + exp(-(0.05 × S - C_j)))
P_context = P_base × Π(Multipliers)
P_final = min(0.95, P_context)   // Capped at 95%
```

**School Threshold Constants (C_j)**:
| School | C_j | Base Rate |
|--------|-----|-----------|
| Harvard | 3.1 | 4.2% |
| Stanford | 3.2 | 3.9% |
| Yale | 2.95 | 5.1% |
| MIT | 2.8 | 5.7% |
| Princeton | 2.75 | 5.8% |
| Caltech | 2.6 | 6.4% |
| CMU | 2.2 | 11% |

### 7.5 SFFA Rubric (1-6 Scale)

Used by Harvard and similar schools in holistic review:

```typescript
interface SFFARubric {
  academic_rating: number;        // 1-6
  extracurricular_rating: number; // 1-6
  athletic_rating: number;        // 1-6
  personal_rating: number;        // 1-6
  overall_rating: number;         // 1-6
}
```

### 7.6 Archetype Detection

**Universal Archetypes** (10 types):
1. **SCHOLAR** - Academic excellence (High aptitude, GPA 0.80+)
2. **RESEARCHER** - Research-focused (National research, STEM)
3. **LEADER** - Leadership-driven (High leadership level)
4. **ENTREPRENEUR** - Founder mentality (Impact + startup energy)
5. **CHANGEMAKER** - Community impact (Service leadership)
6. **ADVOCATE** - Social justice focus
7. **CREATOR** - Project-focused (Makers, artists)
8. **PERFORMER** - Arts/Athletics
9. **POLYMATH** - Balanced excellence (All categories >70%)
10. **EMERGING** - Growing potential

---

## 8. Database & Persistence

### 8.1 Supabase Configuration

**Files**:
- `lib/supabase/client.ts` - Browser client
- `lib/supabase/server.ts` - Server client
- `lib/supabase/database.types.ts` - TypeScript types

**Environment Variables**:
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIs...
ENABLE_SUPABASE_PERSISTENCE=true
```

### 8.2 Database Schema

#### assessments Table
```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT UNIQUE NOT NULL,
  email TEXT,
  profile_data JSONB NOT NULL,
  game_plan_data JSONB,
  scores JSONB,
  completeness NUMERIC,
  tier TEXT,
  archetype TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### coach_sessions Table
```sql
CREATE TABLE coach_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID REFERENCES assessments,
  email TEXT NOT NULL,
  scheduled_at TIMESTAMP,
  calendly_event_id TEXT,
  coach_notes TEXT,
  status TEXT CHECK (status IN ('pending', 'scheduled', 'completed', 'cancelled')),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 8.3 localStorage Persistence

| Key | Store | Purpose |
|-----|-------|---------|
| `ivyquest-student-profile` | useStudentStore | Full profile |
| `ivyquest-session` | useSessionStore | Navigation state |
| `ivyquest-results` | useResultsStore | Cached results |
| `ivyquest-twin-fleet` | useTwinStore | Twin state |
| `ivyquest-frame3-operating` | useFrame3Store | Frame 3 data |

### 8.4 Version Management

**Current Version**: 2.1.0

```typescript
// lib/hooks/useClearStaleData.ts
const VERSION_KEY = 'ivyquest-version';
const CURRENT_VERSION = '2.1.0';

// Clears localStorage on version change
if (storedVersion !== CURRENT_VERSION) {
  clearAllIvyQuestData();
}
```

---

## 9. API Layer

### 9.1 POST /api/assessment - Persistence

**Request**:
```typescript
{
  session_id: string;           // Required
  email?: string;               // Optional
  profile: StudentProfile;      // Required
  game_plan?: object;           // Optional
  scores?: CategoryScores;      // Optional
  completeness?: number;        // 0-100
  tier?: string;                // fresh-start | emerging | optimization
  archetype?: string;           // Detected archetype
}
```

**Response**:
```typescript
{
  success: true,
  persisted: true,
  action: 'created' | 'updated',
  id: string
}
```

### 9.2 GET /api/assessment - Retrieval

**Query Parameters**:
- `session_id` - Fetch single assessment
- `email` - Fetch all assessments by email

### 9.3 POST /api/score - Scoring Engine

**Request**:
```typescript
{
  profile: Partial<StudentProfile>
}
```

**Response**:
```typescript
{
  success: true,
  profile: StudentProfile,          // Normalized
  results: AssessmentResults,       // Full scoring
  school_configs: SchoolConfig[],   // Target schools
  timestamp: string
}
```

**Processing Pipeline**:
1. `prepareProfile()` - Complete with defaults
2. `normalizeStudentProfile()` - Normalize to 0-1
3. `generateAssessmentResults()` - Calculate scores
4. Return complete results

### 9.4 POST /api/nlp - Text Extraction

**Request**:
```typescript
{
  type: 'brag_text' | 'project' | 'tagline' | 'essay';
  text: string;
  context?: { spike, major, achievement }  // For tagline
}
```

**Response varies by type** - extracts structured data using Gemini AI.

---

## 10. External Integrations

### 10.1 Google Gemini AI

**Configuration**:
```typescript
// lib/ai/gemini.ts
const model = generativeAI.getGenerativeModel({
  model: 'gemini-2.0-flash-exp'
});
```

**Functions**:
- `extractFromBragText(text)` - Parse achievement descriptions
- `extractFromProjectDescription(text)` - Analyze technical projects
- `generateNarrativeTagline(spike, major, achievement)` - Create taglines
- `analyzeEssayDraft(essayText)` - Essay critique

### 10.2 Calendly Integration

**Configuration**:
```typescript
// lib/utils/calendly.ts
const CALENDLY_URL = process.env.NEXT_PUBLIC_CALENDLY_URL;
```

**Functions**:
- `generateCalendlyURL(baseURL, context)` - Pre-fill student data
- `openCalendlyPopup(url)` - Open centered popup (700×800px)

### 10.3 PDF Generation

**Package**: `@react-pdf/renderer` (v4.3.x)

**File**: `lib/pdf/GamePlanPDF.tsx`

Converts GamePlan to professional PDF with:
- Header with branding
- Phase breakdowns
- Action steps
- Quick wins
- Generation timestamp

### 10.4 Monitoring

| Service | Purpose |
|---------|---------|
| **LangChain** | AI tracing |
| **Sentry** | Error tracking |
| **Local Trace** | Debug logging |

---

## 11. End-to-End Data Flow

### 11.1 Complete Flow Diagram

```
USER INPUT (Quiz/Form)
    ↓
Frame 0: Target Schools & Major Selection
    ↓
Frame 1: Academic Data (GPA, SAT, AP, Awards)
    → normalizeGPA(), normalizeSAT(), normalizeRigor()
    → AptitudeAttributes (Layer 1)
    ↓
Frame 2: Activities & Leadership
    → normalizeLeadership(), normalizeProjectImpact()
    → PassionAttributes + CommunityAttributes (Layer 1)
    ↓
Frame 3: Operating Profile (Scenarios, Time, Hidden Capabilities)
    → OperatingStyle, TimeCapacity, HiddenStrengthsSignal
    ↓
Frame 4: Assessment Intelligence (Psychometrics Quiz)
    → StudentPsychometrics, TimeManagementProfile
    → AssessmentIntelligence (Layer 4)
    ↓
POST /api/score
    ↓
  1. prepareProfile() → Complete + Validate
  2. normalizeStudentProfile() → All normalized (0.0-1.0)
  3. generateAssessmentResults()
     - Calculate category scores
     - Calculate Ivy+ Ready Score (0-100)
     - For each target school:
       * Calculate P_base (sigmoid)
       * Apply Chetty multipliers
       * Calculate P_final (capped 95%)
       * Determine SchoolFit level
     - Detect archetype
     - Analyze helping/holding factors
  4. Return AssessmentResults
    ↓
FRONTEND DISPLAY
  - Ivy+ Ready Score card
  - School probabilities
  - Category breakdown
  - Digital Twin visualization
  - Booster recommendations
```

### 11.2 State Change Lifecycle

```
User updates GPA in Form
    ↓
setGPA() action in useStudentStore
    ↓
Immer creates new state (immutable)
    ↓
isDirty flag set to true
    ↓
Zustand persist saves to localStorage
    ↓
Component re-renders (subscribers notified)
    ↓
InsightsProvider detects profile change
    ↓
generateInsights() triggered
    ↓
InsightEngine processes profile
    ↓
useInsightsStore updates insights[]
    ↓
UI displays new insights
```

---

## 12. File Structure

```
ivyquest-claude-v2.2/
├── app/
│   ├── layout.tsx                 # Root layout + providers
│   ├── page.tsx                   # Landing → redirect to /quest
│   ├── globals.css                # Design system CSS
│   ├── quest/
│   │   ├── layout.tsx             # Quest layout
│   │   ├── page.tsx               # Quest entry
│   │   └── [frameId]/page.tsx     # Dynamic frame router
│   ├── results/page.tsx           # Results display
│   └── api/
│       ├── score/route.ts         # Scoring API
│       ├── assessment/route.ts    # Persistence API
│       └── nlp/route.ts           # NLP extraction API
│
├── components/
│   ├── frames/                    # 6 Frame components
│   ├── layout/                    # Layout system
│   ├── ui/                        # 14 base components
│   ├── insights/                  # Real-time insights
│   ├── quest/                     # Game components
│   ├── rings/                     # Circular progress
│   ├── twin/                      # Digital twin
│   └── booking/                   # Coach scheduling
│
├── lib/
│   ├── types/
│   │   ├── student.ts             # 752 lines - all types
│   │   ├── frame3.types.ts
│   │   ├── frame4.types.ts
│   │   └── frame5.types.ts
│   │
│   ├── store/                     # 10 Zustand stores
│   │   ├── useStudentStore.ts
│   │   ├── useSessionStore.ts
│   │   ├── useResultsStore.ts
│   │   ├── useInsightsStore.ts
│   │   ├── useFrame3Store.ts
│   │   ├── useFrame4Store.ts
│   │   ├── useFrame5Store.ts
│   │   ├── useUIStore.ts
│   │   ├── useTwinStore.ts
│   │   └── index.ts
│   │
│   ├── scoring/
│   │   ├── engine.ts              # 939 lines - scoring logic
│   │   ├── archetypeDetector.ts   # Archetype detection
│   │   └── factorAnalysis.ts      # Factor analysis
│   │
│   ├── constants/
│   │   ├── defaults.ts            # Centralized defaults
│   │   ├── brand.ts               # Brand colors
│   │   ├── frame3.constants.ts
│   │   ├── frame4.constants.ts
│   │   └── frame5.constants.ts
│   │
│   ├── data/
│   │   ├── schools.ts             # 8 elite school configs
│   │   ├── cds-data.ts            # CDS 2025 data
│   │   ├── chetty-roi.ts          # Chetty multipliers
│   │   ├── nsc-saturation.ts      # NSC saturation data
│   │   └── high-schools.ts
│   │
│   ├── supabase/
│   │   ├── client.ts              # Browser client
│   │   ├── server.ts              # Server client
│   │   └── database.types.ts
│   │
│   ├── validation/
│   │   └── profile.ts             # Profile validation
│   │
│   ├── utils/
│   │   ├── safeValue.ts           # Null-safe utilities
│   │   ├── normalize.ts           # Normalization utils
│   │   ├── skipLogic.ts           # Profile tier logic
│   │   └── calendly.ts            # Calendly utils
│   │
│   ├── hooks/
│   │   ├── usePersistence.ts      # Supabase persistence
│   │   ├── useClearStaleData.ts   # Version management
│   │   └── useInsightNotifications.ts
│   │
│   ├── ai/
│   │   └── gemini.ts              # Gemini AI integration
│   │
│   ├── gamePlan/
│   │   └── gamePlanEngine.ts      # Action plan generation
│   │
│   ├── insights/
│   │   ├── InsightEngine.ts
│   │   ├── types.ts
│   │   └── realtimeInsights.ts
│   │
│   └── trace/                     # Debug tracing
│
├── docs/
│   ├── MASTER_SPEC.md
│   ├── DATABASE_SPEC.md
│   └── TECHNICAL_SPECIFICATION.md  # This file
│
└── supabase/
    └── migrations/
        └── 001_create_assessments.sql
```

---

## 13. Constants & Configuration

### 13.1 Normalized Defaults (0.0-1.0)

```typescript
// lib/constants/defaults.ts
NORMALIZED_DEFAULTS = {
  aptitude: {
    gpa: 0.5,        // ~3.3 GPA equivalent
    sat: 0.5,        // ~1300 SAT
    rigor: 0.4,      // 4-5 AP courses
    awards: 0.0,     // No awards (conservative)
  },
  passion: {
    leadership: 0.25,     // Participant level
    project: 0.2,         // ~20 people impact
    research: 0.0,        // No research
    commitment: 0.5,      // 2 years, moderate
    awards: 0.0,
  },
  community: {
    service: 0.3,         // Participant level
    hours: 0.4,           // ~75 hours
    impact: 0.2,          // Small local
  },
  narrative: {
    vision_clarity: 0.5,
    identity_comfort: 0.5,
    articulation: 0.5,
    maturity: 0.5,
  },
}
```

### 13.2 Validation Bounds

```typescript
VALIDATION_BOUNDS = {
  normalized: { min: 0.0, max: 1.0 },
  percentageScore: { min: 0, max: 100 },
  probability: { min: 0.0, max: 0.95 },  // Capped per spec
  rubricRating: { min: 1, max: 6 },      // SFFA scale
  gpa: { min: 0.0, max: 5.0 },           // Weighted can exceed 4.0
  sat: { min: 400, max: 1600 },
  act: { min: 1, max: 36 },
}
```

### 13.3 Category Weights

```typescript
CATEGORY_WEIGHTS = {
  aptitude: { gpa: 0.35, sat: 0.30, rigor: 0.20, awards: 0.15 },
  passion: { leadership: 0.35, project: 0.20, research: 0.20, commitment: 0.15, awards: 0.10 },
  community: { service: 0.35, impact: 0.35, hours: 0.20, description: 0.10 },
  narrative: { vision: 0.30, identity: 0.25, articulation: 0.25, maturity: 0.20 },
  overall: { aptitude: 0.30, passion: 0.35, community: 0.25, narrative: 0.10 },
}
```

---

## 14. Known Issues & Roadmap

### 14.1 Critical Issues (Open)

| ID | Description | Status |
|----|-------------|--------|
| KI-001 | Dynamic import crash in Frame5GamePlan | OPEN |
| KI-002 | Inflated scores (100%+) on empty profile | OPEN |
| KI-003 | Missing CircularProgress rings in reveal | OPEN |

### 14.2 Design Principles

1. **Single Source of Truth**: Constants in `/lib/constants/`
2. **Validation at Boundaries**: All API inputs validated with Zod
3. **Centralized Defaults**: No magic numbers
4. **Safe Value Utilities**: Universal null/undefined handling
5. **Type Safety**: Complete TypeScript coverage
6. **Immutable Updates**: Immer middleware on all stores

### 14.3 Future Enhancements

- [ ] Email verification before persistence
- [ ] Authentication layer
- [ ] Real-time collaboration (Duo mode)
- [ ] Essay analysis integration
- [ ] Mobile app wrapper

---

## Appendix A: Safe Value Utilities

```typescript
// lib/utils/safeValue.ts

// Safe number with bounds
safeNumber(value: number | null | undefined, fallback: number, bounds?: {min?, max?}): number

// Safe normalized score (0.0-1.0)
safeNormalized(value: number | null | undefined, fallback: number): number

// Safe percentage (0-100)
safePercentage(value: number | null | undefined, fallback: number): number

// Safe probability (0.0-0.95, per spec cap)
safeProbability(value: number | null | undefined, fallback: number): number

// Safe array mutation (sort, reverse)
safeSort<T>(array: T[] | readonly T[] | null | undefined, compareFn?): T[]

// Weighted sum computation
weightedSum(items: Array<{value, weight, fallback}>): number
```

---

## Appendix B: Quick Reference

### Scoring Formula Summary

```
1. Normalize raw values → 0.0-1.0
2. Calculate category scores (weighted sums)
3. Ivy+ Ready Score = Σ(category × weight) × 100
4. P_base = sigmoid(0.05 × rubric_composite - C_j)
5. P_final = min(0.95, P_base × Π(multipliers))
```

### Store Usage Pattern

```typescript
// Read state
const profile = useStudentStore((s) => s.profile);

// Update state
const setGPA = useStudentStore((s) => s.setGPA);
setGPA(3.9);

// Selector hook
const ivyScore = useFrame4IvyScore();
```

### API Error Handling Pattern

```typescript
try {
  // API logic
} catch (error: unknown) {
  console.error('[Service Name] Operation:', error);
  return NextResponse.json(
    { error: 'User-friendly message', details: (error as Error).message },
    { status: 500 }
  );
}
```

---

*This specification is the authoritative technical reference for IvyQuest v2.2. All implementations must conform to these patterns and structures.*
