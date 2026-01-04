# IvyQuest Original Frontend - UI/UX Specification

> Comprehensive analysis of the original unified frontend at `./original-unified-frontend/apps/`

---

## 1. APPLICATION STRUCTURE OVERVIEW

### 1.1 Project Organization

**Location:** `/original-unified-frontend/apps/unified-app/`

**Directory Structure:**
```
src/
├── components/           # All React components organized by feature
│   ├── student/         # Student dashboard components (MAIN)
│   ├── coach/           # Coach dashboard components
│   ├── admin/           # Admin console components
│   ├── auth/            # Authentication-related components
│   ├── shared/          # Shared/reusable components
│   ├── v10/             # v10 feature components (preparation, projects, timeline)
│   ├── v3.2/            # v3.2 evidence tracking components
│   └── v26/             # v26 multi-agent tab components
├── hooks/               # Custom React hooks
├── services/            # API clients and services
├── contexts/            # React Context providers
├── utils/               # Utility functions
├── config/              # Configuration files
├── types/               # TypeScript interfaces
└── styles/              # Global and component styles
```

**Tech Stack:**
- React 18.3.1
- TypeScript 5.2.2
- Styled-components 6.1.8
- React Router v6.22.0
- Vite 5.1.4
- TanStack React Query 5.20.5
- Lucide React (icons)

---

## 2. TABBED INTERFACE ARCHITECTURE

### 2.1 Main Tabs (StudentDashboard)

The primary user interface is a tabbed system defined in **StudentDashboard.tsx**:

| Tab ID | Label | Description | Status |
|--------|-------|-------------|--------|
| `assessment` | Assessment | Main assessment results and scoring | Active |
| `gameplan` | Game Plan | Multi-year strategic roadmap | Active |
| `preparation` | Preparation | Weekly vitals, tasks, and action planning | Active |
| `growth_transformations` | Growth | Timeline of growth events | Active |
| `sessions` | Sessions | Video/session library player | Active |
| `multiagents` | Multi-Agents | Multi-agent chat interface (v26) | Active |
| `application` | Application | College application tracking | Hidden |
| `evidence` | Evidence | Evidence panel and HGTI scoring | Hidden |
| `aichat` | AI Chat | AI chat interface | Hidden |

**Location:** `src/components/student/StudentDashboard.tsx`

### 2.2 Tab Navigation Header

**File:** `Header.tsx`

**Layout:**
- Fixed/sticky header at top with 64px height
- White background with 1px bottom border (#EAEAEA)
- Left section: Logo (flame icon) + navigation items
- Right section: Search bar, notifications, profile pic, logout button

**Tab Styling:**
```css
/* Active Tab */
color: #FF5733;
background: rgba(255, 87, 51, 0.1);

/* Inactive Tab */
color: #666;
background: transparent;

/* Hover */
background: #F5F5F5;

/* Common */
padding: 8px 16px;
border-radius: 24px;
font-size: 14px;
font-weight: 500;
```

---

## 3. TAB CONTENT SPECIFICATIONS

### 3.1 ASSESSMENT TAB

**File:** `StudentDashboard.tsx` (lines 524-694)

**Layout:** Two-column grid (2fr 1fr)

**Components:**

| Component | Purpose | File |
|-----------|---------|------|
| `CircularProgress` | Central score visualization with pillar rings | `CircularProgress.tsx` |
| `IvyScoreCard` | Overall Ivy+ readiness score display | `IvyScoreCard.tsx` |
| `AptitudeCard` | Academic performance pillar | `AptitudeCard.tsx` |
| `PassionCard` | Extracurricular engagement pillar | `PassionCard.tsx` |
| `ServiceCard` | Community service pillar | `ServiceCard.tsx` |
| `IdentityCard` | Personal narrative pillar | `IdentityCard.tsx` |

**Sections:**

1. **Dimensional Scores Grid** - Shows all 8 dimensions with score and tier badge
2. **Strengths Section** - "Standout Strengths" with ROI scores and impact labels
3. **Weak Spots Section** - "Focus Areas" with priority badges (P0/P1/P2)
4. **Admissions Rubric Correlation** - Purple gradient card showing:
   - Academic Index
   - Extracurricular Rating
   - Personal Qualities
   - Recommendation Strength
   - Overall Admit Probability
   - Target Schools list

**Data Interface:**
```typescript
interface AssessmentData {
  ivyReadyScore: {
    overall: number;
    tier: 'BRONZE' | 'SILVER' | 'GOLD' | 'PLATINUM' | 'DIAMOND';
    changeVs180Days: number;
  };
  pillars: {
    aptitude: { score: number; evidence: Evidence[] };
    passion: { score: number; evidence: Evidence[] };
    service: { score: number; evidence: Evidence[] };
    identity: { score: number; evidence: Evidence[] };
  };
  dimensionalScores: DimensionCard[];
  strengths: StrengthItem[];
  weakSpots: WeakSpotItem[];
  admissionsRubric: RubricData;
}
```

---

### 3.2 GAMEPLAN TAB

**File:** `GamePlanView.tsx` (1004 lines)

**Title:** "Your Precision Roadmap"

#### Section A: Initial Game Plan (Baseline)

| Card | Content |
|------|---------|
| Target Profile & Narrative | Profile name, unique narrative story |
| Planned EC Strategy | ECs with title, category, role, hours/week, impact, years |
| Target Schools | School name, tier badge (Reach/Target/Safety) |
| Target Awards & Honors | Award title and description |
| Target Summer Programs | Program title and description |
| Multi-Year Timeline | All phases with dates |

#### Section B: Progress & Evolution

| Card | Content |
|------|---------|
| Current Phase Header | Phase name, week range, goal, completion % |
| Phase Milestones | Status badges, target dates, progress icons |
| Opportunities Status | Category badges, priority colors, deadlines |
| Timeline Progress Summary | Progress bars per phase |
| EC Evolution Summary | Top 4 activities with status |

**Phase Header Styling:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Status Colors:**
```css
completed: #28a745 (green)
in_progress: #ffc107 (yellow)
pending: #6c757d (gray)
```

---

### 3.3 PREPARATION TAB

**File:** `WeeklyVitals.tsx`

**Layout:** Auto-fill grid with 350px minimum card width

**Components:**
- `WeeklyVitals` - Primary container
- `WeeklyActionPlanCard` - Detailed action items per week

**Week Card Styling:**
```css
/* Base */
background: white;
border: 1px solid #e9ecef;
border-radius: 12px;

/* Top Border Gradient (inactive) */
border-top: 3px solid;
border-image: linear-gradient(90deg, #FF5733, #FFC300) 1;

/* Top Border Gradient (expanded) */
border-image: linear-gradient(90deg, #667eea, #764ba2) 1;

/* Hover */
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
transform: translateY(-2px);

/* Transition */
transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
```

---

### 3.4 SESSIONS TAB

**File:** `SessionsViewOptimal.tsx` (70,477 bytes)

**Features:**
- Video search & filtering
- Light/Dark theme toggle (glassmorphism UI)
- Metadata caching for performance
- Smart video prefetch service
- Enhanced media player with controls
- Multiple session types and categories

**Glassmorphism CSS Variables:**
```css
--ivy-bg-gradient
--theme-text-primary
--theme-bg-glass
--ivy-glass-blur
--theme-shadow-glass
```

**Layout:**
- Sticky header with title and video count
- Responsive grid for video cards
- Search functionality
- Cache freshness indicators

---

### 3.5 GROWTH_TRANSFORMATIONS TAB

**File:** `v10/GrowthTransformationsTab.tsx`

**Purpose:** Timeline visualization of student growth events

**Components:**
- `TimelineView` - Main timeline display
- Growth event cards with dates and descriptions

---

### 3.6 MULTIAGENTS TAB (v26)

**File:** `v26/MultiAgentsTabRedesigned.tsx`

**Purpose:** Multi-agent conversational AI interface

**Features:**
- Agent chat bubbles with responses
- Multiple agent interactions
- Full-width layout (no content padding)
- Response streaming support

---

## 4. COMPONENT HIERARCHY

```
App (Router + Auth + Theme Provider)
├── AppRoutes
│   ├── Public Routes
│   │   ├── EntryPortal
│   │   ├── Login
│   │   └── Register
│   │
│   └── Authenticated Routes
│       ├── StudentDashboard (MAIN)
│       │   ├── Header (Tab Navigation)
│       │   │   ├── NavItem (each tab)
│       │   │   ├── SearchBar
│       │   │   ├── NotificationBadge
│       │   │   └── LogoutButton
│       │   │
│       │   └── MainContent
│       │       ├── Assessment Tab
│       │       │   ├── CircularProgress
│       │       │   ├── IvyScoreCard
│       │       │   ├── PillarCards (4x)
│       │       │   ├── DimensionalGrid
│       │       │   ├── StrengthsGrid
│       │       │   ├── WeakSpotsGrid
│       │       │   └── AdmissionsRubricCard
│       │       │
│       │       ├── GamePlan Tab
│       │       │   └── GamePlanView
│       │       │
│       │       ├── Preparation Tab
│       │       │   └── WeeklyVitals
│       │       │
│       │       ├── Sessions Tab
│       │       │   └── SessionsViewOptimal
│       │       │
│       │       ├── Growth Tab
│       │       │   └── GrowthTransformationsTab
│       │       │
│       │       └── MultiAgents Tab
│       │           └── MultiAgentsTabRedesigned
│       │
│       ├── CoachDashboard
│       └── AdminDashboard
```

---

## 5. DESIGN SYSTEM

### 5.1 Color Palette

**Brand Colors:**
```css
/* Primary */
--color-primary: #FF5733;           /* Ivylevel orange */
--color-primary-light: rgba(255, 87, 51, 0.1);
--color-primary-fade: #FFC300;

/* Secondary (Purple Gradient) */
--color-secondary: #667eea;
--color-secondary-accent: #764ba2;
--gradient-purple: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Text Colors:**
```css
--color-text-heading: #333;
--color-text-primary: #333;
--color-text-secondary: #666;
--color-text-muted: #999;
```

**Background Colors:**
```css
--color-bg-page: #FAFAFA;
--color-bg-card: #FFFFFF;
--color-bg-subtle: #F5F5F5;
```

**State Colors:**
```css
--color-success: #28a745;    /* or #16a34a */
--color-warning: #ffc107;    /* or #d97706 */
--color-error: #dc3545;      /* or #dc2626 */
--color-info: #17a2b8;
```

**Border Colors:**
```css
--color-border-default: #e9ecef;
--color-border-subtle: #e5e7eb;
--color-border-header: #EAEAEA;
```

### 5.2 Typography

```css
/* Headings */
h1 { font-size: 32px; font-weight: 600; }
h2 { font-size: 24-28px; font-weight: 600-700; }
h3 { font-size: 20px; font-weight: 600; }

/* Body */
body { font-size: 14-16px; font-weight: 400-500; }
small { font-size: 12-13px; font-weight: 400-500; }
tiny { font-size: 11px; font-weight: 500; }
```

### 5.3 Spacing

```css
/* Header */
header { padding: 0 32px; height: 64px; }

/* Main Container */
main { max-width: 1400px; padding: 40px; }

/* Cards */
.card { padding: 24px; }

/* Grid Gaps */
.grid { gap: 24px; }
```

### 5.4 Border Radius

```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-pill: 24px;
--radius-circle: 50%;
```

### 5.5 Shadows

```css
--shadow-card: 0 2px 8px rgba(0, 0, 0, 0.08);
--shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.12);
--shadow-modal: 0 8px 32px rgba(0, 0, 0, 0.15);
```

### 5.6 Transitions

```css
--transition-fast: 0.2s ease;
--transition-standard: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
```

---

## 6. API SERVICES

### 6.1 v10 API Service

**File:** `utils/v10ApiService.ts`

**Base URL:** `http://localhost:8787`

**Endpoints:**
```typescript
// Assessment
getAssessment(studentId): AssessmentData

// Game Plan
getGamePlan(studentId): GamePlanData
getOpportunities(studentId): OpportunitiesResponse
getMilestones(studentId, options): MilestonesResponse

// Preparation
getWeeklyVitals(studentId): WeeklyVitals[]
getTasks(studentId): Task[]

// Timeline
getTimeline(studentId): TimelineEvent[]
getProjects(studentId): Project[]
```

### 6.2 API Configuration

**File:** `config/api.ts`

```typescript
API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:4101'

// Student Endpoints
/api/students/{studentId}/profile
/api/student/gameplan
/api/student/sessions
/api/student/sessions/urls
/api/stream/{sessionId}

// Assessment Endpoints
/api/assessments/{studentId}/profile

// Mobility Endpoints
/api/mobility/{studentId}/data
```

---

## 7. COMPLETE FILE LISTING

### 7.1 Core Application Files

```
src/
├── App.tsx                     # Main routing
├── AppDebugLatest.tsx          # Active app version
├── main.tsx                    # Entry point
├── index.css                   # Global styles
└── vite-env.d.ts               # Vite types
```

### 7.2 Student Components (Primary)

```
src/components/student/
├── StudentDashboard.tsx        # MAIN (1017 lines)
├── Header.tsx                  # Tab navigation
├── GamePlanView.tsx            # GamePlan tab (1004 lines)
├── SessionsViewOptimal.tsx     # Sessions tab (70KB)
├── CircularProgress.tsx        # Score visualization
├── IvyScoreCard.tsx            # Overall score card
├── AptitudeCard.tsx            # Pillar component
├── PassionCard.tsx             # Pillar component
├── ServiceCard.tsx             # Pillar component
├── IdentityCard.tsx            # Pillar component
├── ProgressTracker.tsx         # Progress tracking
├── VideoPlayer.tsx             # Video playback
├── AIChat.tsx                  # AI chat component
├── Frame.tsx                   # Frame container
└── ui/
    └── card.tsx                # Card primitive
```

### 7.3 v10 Components

```
src/components/v10/
├── WeeklyVitals.tsx            # Preparation tab
├── WeeklyActionPlanCard.tsx    # Weekly actions
├── TaskManager.tsx             # Task management
├── ProjectsView.tsx            # Projects display
├── TimelineView.tsx            # Timeline display
└── GrowthTransformationsTab.tsx # Growth tab
```

### 7.4 v26 Components

```
src/components/v26/
├── MultiAgentsTabRedesigned.tsx # MultiAgents tab
└── ResponseBubbles.tsx          # Agent responses
```

### 7.5 Shared Components

```
src/components/shared/
├── UnifiedHeader.tsx           # Unified header
├── EntryPortal.tsx             # Entry page
├── RoleBasedDashboard.tsx      # Role routing
├── LogoutButton.tsx            # Logout action
├── EnhancedMediaPlayer.tsx     # Media player
├── NonVideoPlayer.tsx          # Audio player
└── Icons.tsx                   # Icon components
```

### 7.6 Services

```
src/services/
├── DashboardDataService.ts     # Dashboard data
├── apiService.ts               # API client
├── agentClient.ts              # Agent API
├── agentFrameworkAuth.ts       # Agent auth
├── firebase.ts                 # Firebase config
├── metadataCacheService.ts     # Metadata caching
├── videoPrefetchService.ts     # Video prefetch
├── videoPreloadService.ts      # Video preload
├── v152Client.ts               # v152 API
├── v3.2ApiService.ts           # v3.2 API
└── auth/
    ├── cognitoAuthService.ts   # Cognito auth
    └── simpleAuthService.ts    # Simple auth
```

### 7.7 Configuration & Utils

```
src/
├── hooks/
│   ├── useAuth.tsx             # Auth hook
│   ├── useStudentData.tsx      # Student data hook
│   ├── useDashboardData.ts     # Dashboard hook
│   └── useAgentChat.ts         # Agent chat hook
│
├── contexts/
│   ├── AuthContext.tsx         # Auth context
│   └── ThemeContext.tsx        # Theme context
│
├── utils/
│   ├── v10ApiService.ts        # v10 API client
│   ├── featureFlags.ts         # Feature flags
│   └── utils.ts                # Utilities
│
├── config/
│   └── api.ts                  # API config
│
├── types/
│   └── dashboard.ts            # TypeScript types
│
└── styles/
    ├── global.css              # Global styles
    └── design-system.css       # Design tokens
```

---

## 8. DESIGN PATTERNS

### 8.1 Tab Content Rendering

```typescript
const [activeTab, setActiveTab] = useState('assessment');

const renderTabContent = () => {
  switch(activeTab) {
    case 'assessment':
      return <AssessmentContent />;
    case 'gameplan':
      return <GamePlanView studentId={studentId} />;
    case 'preparation':
      return <WeeklyVitals studentId={studentId} />;
    case 'sessions':
      return <SessionsViewOptimal />;
    case 'growth_transformations':
      return <GrowthTransformationsTab studentId={studentId} />;
    case 'multiagents':
      return <MultiAgentsTabRedesigned />;
    default:
      return null;
  }
};
```

### 8.2 Card Component Pattern

```typescript
const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
`;
```

### 8.3 Status Badge Pattern

```typescript
const StatusBadge = styled.span<{ status: string }>`
  padding: 4px 12px;
  border-radius: 24px;
  font-size: 12px;
  font-weight: 500;

  ${({ status }) => {
    switch(status) {
      case 'completed':
        return `background: #d1fae5; color: #059669;`;
      case 'in_progress':
        return `background: #fef3c7; color: #d97706;`;
      case 'pending':
        return `background: #f3f4f6; color: #6b7280;`;
    }
  }}
`;
```

### 8.4 Data Fetching Pattern

```typescript
useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await v10Api.getAssessment(studentId);
      setData(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };
  fetchData();
}, [studentId]);
```

---

## 9. RESPONSIVE BREAKPOINTS

```css
/* Mobile */
@media (max-width: 767px) {
  /* Single column layouts */
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1199px) {
  /* Adjusted grids */
}

/* Desktop */
@media (min-width: 1200px) and (max-width: 1599px) {
  /* Standard layouts */
}

/* Large Desktop */
@media (min-width: 1600px) {
  /* Extended layouts */
}
```

---

## 10. ACTIVE vs LEGACY CODE

### Active (In Use)
- `StudentDashboard.tsx` - Primary student interface
- `GamePlanView.tsx` - Full gameplan implementation
- `WeeklyVitals.tsx` - v10 preparation tab
- `SessionsViewOptimal.tsx` - Sessions tab
- `MultiAgentsTabRedesigned.tsx` - v26 agents interface
- All pillar cards (Aptitude, Passion, Service, Identity)

### Legacy (Unused)
- `GamePlan.js` - Old JS implementation
- `Execution.js` - Old JS implementation
- `Profile.js` - Old JS implementation
- Multiple App variations (AppDebug, AppSimpleTest, AppMinimal)
- Hidden tabs (application, evidence, aichat)

---

## 11. SUMMARY

The IvyQuest Original Frontend implements a comprehensive student success platform with:

1. **6 Primary Tabs** - Assessment, GamePlan, Preparation, Sessions, Growth, MultiAgents
2. **Multi-Column Layouts** - Responsive grid-based designs
3. **Consistent Visual Language** - Orange (#FF5733) and purple (#667eea) gradient theme
4. **Component-Driven Architecture** - Styled-components for styling
5. **Real-Time Data** - v10 API service with caching strategies
6. **Role-Based UI** - Student, Coach, and Admin dashboards
7. **Professional Design System** - Typography, spacing, colors, and interactions

This specification serves as the reference for reimplementing the frontend with modern best practices.
