# IvyQuest v2.0 - Complete UI/UX Implementation Plan

## Overview

Build the complete IvyQuest platform with 6 frames, Digital Twin Fleet visualization, and gamified assessment flow per the Figma wireframes and UI/UX specifications.

---

## Version History

### v2.0.0 (December 2025) - Design System Update

#### New Features
- **College Logo System**: Real black & white college logos from original Ivylevel design system
  - Logos stored in `/public/logos/` (harvard.svg, stanford.svg, mit.svg, yale.svg, princeton.svg, cmu.svg, columbia.svg)
  - `CollegeLogo` component with size normalization via scale factors
  - Used in quest landing page and Frame 1 school selection

- **Results Completion Page**: New `/results` page showing assessment completion
  - Displays final Ivy+ Score
  - Links to review results (Frame 5), view power-ups (Frame 6), or start new assessment
  - Replaces previous redirect-based approach that caused navigation loops

- **3D Twin Fleet Improvements**:
  - Added `CanvasErrorBoundary` for graceful Three.js error handling
  - Enhanced WebGL detection with detailed diagnostics
  - Improved 2D fallback with proper styling
  - Added `FORCE_3D_RENDERING` flag for debugging

#### Bug Fixes
- **Frame 5 Navigation Loop**: Fixed duplicate `completeFrame()` call that caused assessment to restart instead of progressing to Frame 6
- **Results 404**: Created results page that was missing, causing 404 errors
- **Dark Mode CSS in Frames**: Replaced dark-mode Tailwind classes with BRAND_COLORS constants throughout Frame components
- **TwinFleet CSS**: Fixed loader, legend, and fallback components to use proper colors for dark 3D background

#### UI/UX Improvements
- Updated quest landing page with real college logos instead of letter placeholders
- Normalized logo sizes using scale factors for consistent visual appearance
- Updated Fleet stage description to match 2D interaction model
- Improved loading states and error messages

#### Files Changed
- `/components/ui/CollegeLogo.tsx` - NEW: College logo component with normalization
- `/public/logos/*.svg` - NEW: BW college logo assets
- `/app/results/page.tsx` - NEW: Assessment completion page
- `/app/quest/page.tsx` - Updated with CollegeLogo component
- `/components/frames/Frame1Warmup.tsx` - Updated with CollegeLogo component
- `/components/frames/Frame5Reveal.tsx` - Fixed navigation, updated Fleet description
- `/components/twin/TwinFleet.tsx` - Added error boundary, WebGL diagnostics, fixed CSS

---

## Stack & Services

| Service | Provider | Purpose |
|---------|----------|---------|
| Database | Supabase (PostgreSQL) | User profiles, sessions, results |
| Auth | JWT + Supabase Auth | Login, registration, sessions |
| AI/LLM | Google Gemini (gemini-2.0-flash) | NLP extraction, psychometric analysis |
| Voice | ElevenLabs | Optional voice narration |
| Monitoring | Sentry + LangChain | Error tracking, LLM tracing |
| 3D Graphics | React Three Fiber + Three.js | Digital Twin Fleet visualization |

---

## Architecture

```
/app
├── (auth)/
│   ├── login/page.tsx           # Login page
│   ├── register/page.tsx        # Registration page
│   └── layout.tsx               # Auth layout (no nav)
├── (main)/
│   ├── layout.tsx               # Main layout with navigation
│   ├── dashboard/page.tsx       # Home dashboard
│   ├── assessment/
│   │   ├── page.tsx             # Assessment hub/start
│   │   ├── frame-1/page.tsx     # Warmup
│   │   ├── frame-2/page.tsx     # Snapshot
│   │   ├── frame-3/page.tsx     # Building
│   │   ├── frame-4/page.tsx     # Operating (Quiz)
│   │   ├── frame-5/page.tsx     # Reveal
│   │   └── frame-6/page.tsx     # Power-Ups
│   ├── results/page.tsx         # Full results view
│   ├── boosters/page.tsx        # 47 booster templates
│   └── profile/page.tsx         # Edit profile
├── api/
│   ├── auth/
│   │   ├── login/route.ts       # JWT login
│   │   ├── register/route.ts    # User registration
│   │   └── refresh/route.ts     # Token refresh
│   ├── score/route.ts           # Scoring engine (exists)
│   ├── nlp/route.ts             # Gemini NLP extraction
│   └── session/route.ts         # Save/load sessions
└── layout.tsx                   # Root layout

/components
├── ui/                          # Reusable primitives
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Input.tsx
│   ├── Select.tsx
│   ├── Slider.tsx
│   ├── Modal.tsx
│   ├── Progress.tsx
│   ├── ScoreRing.tsx
│   └── Toast.tsx
├── frames/                      # Frame-specific components
│   ├── WarmupFrame.tsx          # Frame 1
│   ├── SnapshotFrame.tsx        # Frame 2
│   ├── BuildingFrame.tsx        # Frame 3
│   ├── OperatingFrame.tsx       # Frame 4 (Quiz)
│   ├── RevealFrame.tsx          # Frame 5
│   └── PowerUpsFrame.tsx        # Frame 6
├── forms/                       # Data input forms
│   ├── IdentityForm.tsx
│   ├── AptitudeForm.tsx
│   ├── PassionForm.tsx
│   ├── CommunityForm.tsx
│   ├── DemographicsForm.tsx
│   └── HighSchoolForm.tsx
├── quiz/                        # Kahoot quiz system
│   ├── QuizContainer.tsx
│   ├── QuizQuestion.tsx
│   ├── QuizTimer.tsx
│   ├── QuizScoreboard.tsx
│   └── QuizResults.tsx
├── twin/                        # Digital Twin Fleet
│   ├── TwinFleetCanvas.tsx      # R3F Canvas wrapper
│   ├── TwinCharacter.tsx        # 3D character model
│   ├── TwinGear.tsx             # Gear accessories
│   ├── SchoolOrb.tsx            # School orbs/portals
│   └── FleetFormation.tsx       # Fleet arrangement
├── results/                     # Results visualization
│   ├── IvyScoreCard.tsx
│   ├── SchoolProbabilityCard.tsx
│   ├── FactorsList.tsx
│   ├── ArchetypeReveal.tsx
│   └── ComparisonChart.tsx
├── boosters/                    # Booster system
│   ├── BoosterCard.tsx
│   ├── BoosterGrid.tsx
│   ├── ROIProjection.tsx
│   └── ActionPlan.tsx
└── layout/                      # Navigation & layout
    ├── Header.tsx
    ├── Sidebar.tsx
    ├── FrameProgress.tsx
    └── MobileNav.tsx

/lib
├── store/                       # Zustand stores
│   ├── useStudentStore.ts       # Student profile state
│   ├── useSessionStore.ts       # Assessment session state
│   ├── useResultsStore.ts       # Scoring results cache
│   └── useUIStore.ts            # UI state (modals, etc.)
├── supabase/                    # Supabase integration
│   ├── client.ts                # Browser client
│   ├── server.ts                # Server client
│   └── middleware.ts            # Auth middleware
├── ai/                          # Gemini integration
│   ├── client.ts                # Gemini client
│   ├── prompts.ts               # NLP prompts
│   └── extractors.ts            # Attribute extraction
├── hooks/                       # Custom React hooks
│   ├── useScoring.ts            # Score calculation hook
│   ├── useProfile.ts            # Profile management
│   └── useQuiz.ts               # Quiz state management
└── validators/                  # Zod schemas
    ├── profile.ts               # Profile validation
    └── auth.ts                  # Auth validation
```

---

## Frame-by-Frame Implementation

### Frame 1: Warmup (Onboarding)
**Purpose**: Set context, capture identity, select target schools

**Components**:
- Welcome animation with floating twin preview
- Role selection (Student/Parent)
- Name and grade input
- Target school selector (7 schools with logos/colors)
- Intended major selector with certainty slider
- Progress indicator (1/6)

**Data Captured**:
- `identity.role`, `identity.name`, `identity.grade`
- `target_schools[]`
- `intended_major`, `major_certainty`

**Transitions**:
- Twin character begins forming in background
- School orbs appear as selections are made

---

### Frame 2: Snapshot (Quick Wins)
**Purpose**: Capture high-impact academic metrics fast

**Components**:
- GPA input with visual scale (0.0 - 4.7+)
- SAT/ACT toggle with score input
- AP course counter with average score
- Test optional toggle
- Academic awards multi-select
- Real-time normalization feedback ("Top 5% of applicants")

**Data Captured**:
- `aptitude.gpa_weighted`, `gpa_unweighted`
- `aptitude.sat_total` OR `act_total`
- `aptitude.ap_count`, `ap_avg_score`
- `aptitude.academic_awards[]`

**Gamification**:
- XP awarded for each complete section
- Twin's "crown" gear piece appears for high GPA
- Score preview updates in real-time

---

### Frame 3: Building (Deep Assessment)
**Purpose**: Capture passion, leadership, projects, community

**Sub-sections** (card-based progression):
1. **Spike Category** - Visual selector for 7 spike types
2. **Leadership** - Level selector with role description
3. **EC Commitment** - Years and hours sliders
4. **Projects** - Impact scale + description (NLP extraction)
5. **Research** - Level selector with description
6. **Awards** - Multi-select (State/National/International)
7. **Community Service** - Leadership level + hours + impact
8. **High School** - School selector with saturation lookup
9. **Demographics** - Optional sensitive fields

**Data Captured**:
- All `passion.*` attributes
- All `community.*` attributes
- `high_school.*` (auto-fills saturation from NSC database)
- `demographics.*`

**AI Integration**:
- Gemini extracts attributes from `project_description`
- Gemini extracts hidden capabilities from `brag_text`

---

### Frame 4: Operating (Psychometrics Quiz)
**Purpose**: Layer 4 assessment intelligence via Kahoot-style quiz

**Quiz Structure**:
- 15-20 questions across categories:
  - Grit/Resilience (3 questions)
  - Coachability (2 questions)
  - Vision Clarity (2 questions)
  - Big Five OCEAN (5 questions)
  - Time Management (3 questions)
  - Academic Intelligence (2 questions)

**Question Types**:
- MCQ (4 options, 10 second timer)
- Scenario-based (situation + response)
- Scale (1-5 slider)

**Gamification**:
- Point streak bonuses
- Timer pressure
- Sound effects & animations
- XP counter
- Leaderboard position (vs. average)

**Data Captured**:
- All `assessment_intelligence.psychometrics.*`
- All `assessment_intelligence.time_management.*`
- `burnout_risk` calculated

---

### Frame 5: Reveal (Results)
**Purpose**: Dramatic reveal of scoring results

**Sequence**:
1. **Suspense Build** - Twin completes formation
2. **Ivy+ Score Reveal** - Large number animation (0→score)
3. **Category Breakdown** - Aptitude, Passion, Community, Narrative
4. **School Probabilities** - Each school card flips to reveal %
5. **Fit Analysis** - Best fit, strong fit, tough, warnings
6. **Archetype Reveal** - "You are a Cookie Cutter Bay Area CS"
7. **Factors Display** - Helping vs holding back

**3D Visualization**:
- Twin Fleet forms in formation
- School orbs orbit around base twin
- Colors pulse based on probability
- Gaps shown as greyed-out gear pieces

**Components**:
- `TwinFleetCanvas` - Full 3D scene
- `IvyScoreCard` - Main score display
- `SchoolProbabilityCard` - Per-school results
- `ArchetypeReveal` - Animated archetype badge

---

### Frame 6: Power-Ups (Boosters)
**Purpose**: Actionable recommendations with ROI projections

**Layout**:
- Top 3 boosters prominently displayed
- Full booster grid (47 templates)
- ROI projection chart showing probability gains
- Action plan timeline
- Burnout feasibility check

**Booster Card Content**:
- Title + description
- Time commitment (hours/weeks)
- Impact category (which attribute improves)
- Probability gain per school
- Priority ranking

**47 Booster Categories**:
1. Academic (AP additions, test retakes)
2. Research (lab placements, publications)
3. Leadership (founding orgs, scaling impact)
4. Projects (hackathons, startups, portfolios)
5. Community (service leadership, hours)
6. Awards (competitions, applications)
7. Narrative (essay angles, spike refinement)

---

## Database Schema (Supabase)

```sql
-- Users table
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT DEFAULT 'student',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ
);

-- Student profiles (full Layer 1-4 data)
CREATE TABLE student_profiles (
  profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(user_id),
  profile_data JSONB NOT NULL,  -- Full StudentProfile
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Assessment sessions
CREATE TABLE assessment_sessions (
  session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(user_id),
  current_frame INTEGER DEFAULT 1,
  frame_progress JSONB DEFAULT '{}',
  profile_snapshot JSONB,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Scoring results
CREATE TABLE scoring_results (
  result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES assessment_sessions(session_id),
  results_data JSONB NOT NULL,  -- Full AssessmentResults
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz responses
CREATE TABLE quiz_responses (
  response_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES assessment_sessions(session_id),
  question_id TEXT NOT NULL,
  answer_value TEXT NOT NULL,
  points_earned INTEGER,
  response_time_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Implementation Order

### Phase 1: Foundation (Tasks 1-4)
1. Environment setup (.env.local with credentials)
2. Supabase client + auth integration
3. Zustand stores (student, session, results, UI)
4. Reusable UI components (Button, Card, Input, etc.)

### Phase 2: Assessment Flow (Tasks 5-10)
5. Frame 1: Warmup (identity, schools, major)
6. Frame 2: Snapshot (aptitude)
7. Frame 3: Building (passion, community, demographics)
8. Frame 4: Operating (quiz system)
9. Frame 5: Reveal (results display)
10. Frame 6: Power-Ups (boosters)

### Phase 3: Polish (Tasks 11-14)
11. Gemini NLP integration
12. Digital Twin 3D visualization
13. Dashboard and navigation
14. End-to-end testing

---

## Key Design Patterns

### Dark Theme (from globals.css)
- Background: `#0A0E14` (primary), `#141B24` (secondary)
- Text: `#F8FAFC` (primary), `#94A3B8` (secondary)
- Accent: `#4A90D9` (blue), `#34D399` (green)

### Component Styling
```tsx
// Example component pattern
<Card className="bg-background-elevated border-border-subtle rounded-2xl p-6">
  <h3 className="text-xl font-display text-text-primary">Title</h3>
  <p className="text-text-secondary">Description</p>
</Card>
```

### State Flow
```
User Input → Zustand Store → API Call → Supabase → Response → Update Store → Re-render
```

### Scoring Integration
```tsx
// After Frame 4 completes
const profile = useStudentStore(s => s.profile);
const { data: results } = await fetch('/api/score', {
  method: 'POST',
  body: JSON.stringify({ profile })
});
useResultsStore.setState({ results });
```

---

## Ready to Implement

This plan covers the complete IvyQuest v2.2 platform with:
- 6 interactive frames
- Real scoring engine integration
- Supabase persistence
- Gemini AI for NLP
- 3D Digital Twin Fleet
- 47 booster recommendations
- Kahoot-style quiz system
- Full dark theme UI

All credentials provided. No stubs or fake data.
