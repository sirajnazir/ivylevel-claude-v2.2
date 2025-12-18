# IvyQuest Assessment - Complete Source Code Audit for Insight Generation

**Date:** December 17, 2025
**Purpose:** Pre-implementation analysis for Noom-style insight generation system

---

## 1. ASSESSMENT FLOW MAPPING

### CURRENT ASSESSMENT FLOW

```
Entry Point: /quest (Landing) → /quest/1 (Start Assessment)

Frame/Phase 1: Warmup (Identity & Goals)
├─ Route: /quest/1
├─ Component: /components/frames/Frame1Warmup.tsx
├─ Cards: 4 sequential
├─ Questions:
│  ├─ Q1: "Are you a student or parent?" → Selection → profile.identity.role
│  ├─ Q2: "What's your name? Grade level?" → Text + Select → profile.identity.name, .grade
│  ├─ Q3: "Pick your dream schools (min 1)" → Multi-select → profile.target_schools[]
│  └─ Q4: "What do you want to study?" → Text + Buttons → profile.intended_major, .major_certainty
├─ Data collected: role, name, grade, target_schools[], intended_major, major_certainty
├─ XP: 25 per card (100 total)
└─ Next: Frame 2

Frame/Phase 2: Snapshot (Academic Profile)
├─ Route: /quest/2
├─ Component: /components/frames/Frame2Snapshot.tsx
├─ Cards: 4 sequential
├─ Questions:
│  ├─ Q1: GPA sliders → Dual sliders (weighted 2.0-5.0, unweighted 2.0-4.0) → profile.aptitude.gpa_weighted, .gpa_unweighted
│  ├─ Q2: Test scores → Tabs (SAT/ACT/Optional) + Slider → profile.aptitude.sat_total or .act_total or .test_optional
│  ├─ Q3: Course rigor → Slider + Toggle → profile.aptitude.ap_count, .ap_avg_score, .ib_diploma
│  └─ Q4: Academic awards → Multi-checkbox (10 options) → profile.aptitude.academic_awards[]
├─ Data collected: GPA (weighted/unweighted), SAT/ACT, AP count/avg, IB diploma, academic awards
├─ Real-time viz: PillarCards (Aptitude pillar), InsightsPanel
├─ XP: 30 per card (120 total)
└─ Next: Frame 3

Frame/Phase 3: Building (Passions & Impact)
├─ Route: /quest/3
├─ Component: /components/frames/Frame3Building.tsx
├─ Cards: 9 sequential (largest frame)
├─ Questions:
│  ├─ Q1: "What defines your passion?" → Single-select buttons (7 options) → profile.passion.spike_category
│  ├─ Q2: "Highest leadership role?" → Single-select (6 levels) → profile.passion.leadership_level
│  ├─ Q3: Commitment → Dual sliders (years 1-6, hours 1-30) → profile.passion.ec_commitment_years, .ec_hours_weekly
│  ├─ Q4: Projects → Textarea + Slider (impact 0-10K) → profile.passion.project_description, .project_impact
│  ├─ Q5: "Tell us your story" → Textarea + AI Extract button → profile.passion.brag_text (triggers /api/nlp)
│  ├─ Q6: Research experience → Single-select (5 levels) → profile.passion.research_level
│  ├─ Q7: EC Awards → Multi-checkbox (5 levels) → profile.passion.ec_awards[]
│  ├─ Q8: Community service → 2 Sliders + Buttons → profile.community.service_hours, .community_impact, .service_leadership
│  └─ Q9: High school → Search autocomplete → profile.high_school (name, code, type, saturation_level)
├─ Data collected: spike, leadership, commitment, projects, brag_text, research, EC awards, service, high school
├─ Real-time viz: PillarCards (Passion & Community), InsightsPanel
├─ XP: 35 per card (315 total)
└─ Next: Frame 4

Frame/Phase 4: Operating (Psychometrics)
├─ Route: /quest/4
├─ Component: /components/frames/Frame4Operating.tsx
├─ Cards: 3 cards
├─ Questions:
│  ├─ Q1: Scenarios → Decision-based choice buttons → frame3Data.scenarioResponses
│  ├─ Q2: Time & Energy → Selections + Dropdown → frame3Data.weeklyAvailableHours, .peakProductivity, .energySource
│  └─ Q3: Hidden capabilities → Multi-checkbox → frame3Data.hiddenCapabilities[]
├─ Data output: operatingStyle, energyPattern, riskTolerance, stressResponse, hiddenStrengths
├─ Psychometrics mapped: coachability_score, introversion_extroversion, openness, conscientiousness
├─ XP: 40 per card (120 total)
└─ Next: Frame 5

Frame/Phase 5: Reveal (Scoring & Results)
├─ Route: /quest/5
├─ Component: /components/frames/Frame5Reveal.tsx
├─ Stages: 5 progressive reveals
├─ Flow:
│  ├─ Stage 1: Score → Ivy+ Ready Score (circular animated ring)
│  ├─ Stage 2: Schools → Admission probabilities per target school
│  ├─ Stage 3: Fleet → Digital Twin Fleet visualization (3D lazy-loaded)
│  ├─ Stage 4: Factors → Helping & Holding Back factors
│  └─ Stage 5: Archetype → Student archetype + narrative tagline
├─ API Call: POST /api/score with full profile → returns AssessmentResults
├─ XP: 50 per stage (250 total)
└─ Next: Frame 6

Frame/Phase 6: Power-Ups (Strategic Boosters)
├─ Route: /quest/6
├─ Component: /components/frames/Frame6PowerUps.tsx
├─ Cards: 4 cards
├─ Content:
│  ├─ Card 1: Top 3 personalized boosters (AI-recommended from 47 total)
│  ├─ Card 2: Browsable booster grid by category (APTITUDE, PASSION, COMMUNITY)
│  ├─ Card 3: ROI Calculator (time investment vs. score impact)
│  └─ Card 4: Action Plan summary with action steps
├─ XP: 50 per card (200 total)
└─ Next: /results (assessment complete)
```

### BRANCHING LOGIC

**Linear Flow (No Branching):**
All frames progress sequentially: 1 → 2 → 3 → 4 → 5 → 6 → Results

**Conditional UI Only:**
- Frame 2 Tests Card: Tabs switch between SAT/ACT/Test Optional views
- Frame 3 Brag Text: AI Extract button enabled only if text ≥50 chars
- Frame 3 High School: Autocomplete conditional on search input
- Frame 5: Progressive stage reveals (user clicks Next for each)

### PROGRESS TRACKING

- **Method:** FrameProgress component (segmented bar) + card dot indicators
- **Location:** `/components/ui/Progress.tsx`, `/components/layout/AssessmentLayout.tsx`
- **Total Steps:** 6 frames × variable cards = ~25 cards total
- **XP System:** 655 total possible XP (25-50 XP per card)

---

## 2. FILE STRUCTURE & COMPONENT INVENTORY

### FILE STRUCTURE

```
/Users/snazir/ivyquest-claude-v2.2/
├─ app/
│  ├─ page.tsx                          (Landing page)
│  ├─ assessment/page.tsx               (Legacy assessment entry)
│  ├─ dashboard/page.tsx                (User dashboard)
│  ├─ results/page.tsx                  (Results summary page)
│  ├─ quest/
│  │  ├─ page.tsx                       (Quest landing/continue)
│  │  ├─ layout.tsx                     (Quest layout wrapper)
│  │  └─ [frameId]/page.tsx             (Dynamic frame router)
│  └─ api/
│     ├─ score/route.ts                 (POST /api/score - scoring engine)
│     └─ nlp/route.ts                   (POST /api/nlp - brag text extraction)
│
├─ components/
│  ├─ frames/
│  │  ├─ Frame1Warmup.tsx               (Identity & Goals)
│  │  ├─ Frame2Snapshot.tsx             (Academic Profile)
│  │  ├─ Frame3Building.tsx             (Passions & Impact)
│  │  ├─ Frame4Operating.tsx            (Psychometrics)
│  │  ├─ Frame5Reveal.tsx               (Scoring & Results)
│  │  ├─ Frame6PowerUps.tsx             (Boosters)
│  │  ├─ Frame4Reveal.tsx               (Alternative reveal)
│  │  ├─ Frame5PowerUps.tsx             (Alternative power-ups)
│  │  ├─ reveal/
│  │  │  ├─ Card1LaunchSequence.tsx
│  │  │  ├─ Card2DualScore.tsx
│  │  │  ├─ Card3SchoolCards.tsx
│  │  │  └─ Card4CategoryBreakdown.tsx
│  │  ├─ operating/
│  │  │  ├─ Card1Scenarios.tsx
│  │  │  ├─ Card2TimeEnergy.tsx
│  │  │  └─ Card3HiddenCapabilities.tsx
│  │  └─ powerups/
│  │     ├─ BoosterCard.tsx
│  │     ├─ ActionPlan.tsx
│  │     └─ ImpactMeter.tsx
│  │
│  ├─ layout/
│  │  ├─ AssessmentLayout.tsx           (Header, XP counter, frame progress)
│  │  └─ SplitFrameLayout.tsx           (2-column layout with drone)
│  │
│  ├─ common/
│  │  └─ DroneAssistant.tsx             (Drone avatar + speech bubble)
│  │
│  ├─ insights/
│  │  ├─ InsightsPanel.tsx              (Real-time insight display)
│  │  └─ InsightsProvider.tsx           (Auto-subscription wrapper)
│  │
│  ├─ rings/
│  │  ├─ CircularProgress.tsx           (5-ring score visualization)
│  │  └─ PillarCards.tsx                (2x2 pillar score cards)
│  │
│  ├─ twin/
│  │  ├─ TwinCharacter.tsx              (Single avatar)
│  │  └─ TwinFleet.tsx                  (3D twin fleet)
│  │
│  ├─ quest/
│  │  ├─ QuestContainer.tsx             (Frame config, HUD, timeline)
│  │  ├─ HUD.tsx                        (Score badges overlay)
│  │  ├─ Timeline.tsx                   (Quest timeline)
│  │  ├─ ModCard.tsx                    (Modular card)
│  │  ├─ DroneGuide.tsx                 (Alternative drone)
│  │  └─ DualScoreDisplay.tsx           (Score comparison)
│  │
│  ├─ ui/
│  │  ├─ Button.tsx
│  │  ├─ Card.tsx
│  │  ├─ Input.tsx
│  │  ├─ Modal.tsx
│  │  ├─ Progress.tsx                   (Progress bar + FrameProgress)
│  │  ├─ Slider.tsx
│  │  ├─ SliderInput.tsx
│  │  ├─ Select.tsx
│  │  ├─ ChipSelector.tsx
│  │  ├─ ScoreRing.tsx
│  │  ├─ Toast.tsx
│  │  ├─ CollegeLogo.tsx
│  │  ├─ HighlightedText.tsx
│  │  └─ VoiceInput.tsx
│  │
│  ├─ debug/
│  │  └─ DebugOverlay.tsx
│  │
│  ├─ icons/
│  │  └─ index.tsx
│  │
│  └─ IvylevelLogo.tsx
│
├─ lib/
│  ├─ store/
│  │  ├─ index.ts                       (Central export hub)
│  │  ├─ useSessionStore.ts             (Frame navigation, XP)
│  │  ├─ useStudentStore.ts             (Profile data - 58+ attributes)
│  │  ├─ useResultsStore.ts             (Scoring results)
│  │  ├─ useInsightsStore.ts            (AI insights + auto-subscription)
│  │  ├─ useFrame3Store.ts              (Psychometrics)
│  │  ├─ useFrame4Store.ts              (Quiz/IvyScore)
│  │  ├─ useFrame5Store.ts              (Power-ups)
│  │  ├─ useTwinStore.ts                (Digital Twin Fleet)
│  │  └─ useUIStore.ts                  (Toast, modal)
│  │
│  ├─ scoring/
│  │  ├─ engine.ts                      (IvyLevel v6.0 Scoring Engine - 31.7KB)
│  │  ├─ archetypeDetector.ts           (11 archetype detection)
│  │  └─ factorAnalysis.ts              (Helping/holding back factors)
│  │
│  ├─ insights/
│  │  ├─ types.ts                       (7 insight categories)
│  │  └─ InsightEngine.ts               (Insight generation logic)
│  │
│  ├─ integration/
│  │  ├─ store/
│  │  │  ├─ questStore.master.ts        (Unified quest state machine)
│  │  │  ├─ questStore.selectors.ts     (Optimized selectors)
│  │  │  └─ questStore.persistence.ts   (localStorage, auto-save)
│  │  └─ hooks/
│  │     ├─ useQuestNavigation.ts
│  │     ├─ useQuestProgress.ts
│  │     └─ useQuestPersistence.ts
│  │
│  ├─ constants/
│  │  ├─ brand.ts                       (BRAND_COLORS - primary #FF4A23)
│  │  ├─ defaults.ts                    (Centralized scoring defaults)
│  │  ├─ droneMessages.ts               (Frame-by-frame drone messages)
│  │  ├─ frame3.constants.ts
│  │  ├─ frame4.constants.ts
│  │  ├─ frame5.constants.ts
│  │  └─ index.ts
│  │
│  ├─ data/
│  │  ├─ schools.ts                     (8 Ivy+ schools with CDS 2025 rates)
│  │  ├─ high-schools.ts                (High school database)
│  │  ├─ nsc-saturation.ts              (Saturation adjustments)
│  │  ├─ chetty-roi.ts                  (Chetty 2023 multipliers)
│  │  └─ cds-data.ts                    (College data)
│  │
│  ├─ visualization/
│  │  ├─ feedback-system/
│  │  │  ├─ types/feedback.types.ts     (Toast, achievement, milestone types)
│  │  │  ├─ constants/feedback.constants.ts
│  │  │  ├─ utils/feedbackUtils.ts
│  │  │  └─ components/ (ScoreDelta, Notifications, etc.)
│  │  └─ twin-fleet/
│  │     ├─ types/twin.types.ts
│  │     ├─ constants/twin.constants.ts
│  │     ├─ utils/twinUtils.ts
│  │     └─ components/
│  │
│  ├─ analytics/
│  │  ├─ types/analytics.types.ts
│  │  ├─ constants/analytics.constants.ts
│  │  ├─ trackers/ (Frame, Session, Score, Interaction)
│  │  └─ context/AnalyticsContext.tsx
│  │
│  ├─ validation/
│  │  └─ profile.ts                     (Profile validation layer)
│  │
│  ├─ utils/
│  │  ├─ cn.ts                          (classnames utility)
│  │  ├─ normalize.ts
│  │  └─ safeValue.ts                   (Safe number/percentage functions)
│  │
│  ├─ types/
│  │  ├─ student.ts                     (58 attributes + 39 assessment intelligence)
│  │  ├─ frame3.types.ts
│  │  ├─ frame4.types.ts
│  │  └─ frame5.types.ts
│  │
│  ├─ engines/
│  │  └─ boosterEngine.ts               (47 boosters with ROI)
│  │
│  ├─ ai/
│  │  └─ gemini.ts                      (Google Gemini integration)
│  │
│  ├─ supabase/
│  │  ├─ client.ts
│  │  └─ server.ts
│  │
│  └─ trace/ (Debugging/logging)
│
└─ types/ (Global TypeScript types)
```

### COMPONENT INVENTORY

#### Assessment Frame Components

| Component | File | Purpose | Key Props |
|-----------|------|---------|-----------|
| Frame1Warmup | `/components/frames/Frame1Warmup.tsx` | Role, identity, schools, major collection | Uses SplitFrameLayout |
| Frame2Snapshot | `/components/frames/Frame2Snapshot.tsx` | GPA, tests, AP, awards inputs | Real-time PillarCards |
| Frame3Building | `/components/frames/Frame3Building.tsx` | Leadership, projects, research, community | AI brag text extraction |
| Frame4Operating | `/components/frames/Frame4Operating.tsx` | Scenarios, time/energy, capabilities | Psychometrics mapping |
| Frame5Reveal | `/components/frames/Frame5Reveal.tsx` | Multi-stage results reveal | API scoring, animations |
| Frame6PowerUps | `/components/frames/Frame6PowerUps.tsx` | Booster recommendations, action plan | ROI calculations |

#### Layout Components

| Component | File | Purpose |
|-----------|------|---------|
| AssessmentLayout | `/components/layout/AssessmentLayout.tsx` | Header, XP counter, frame progress bar |
| SplitFrameLayout | `/components/layout/SplitFrameLayout.tsx` | 2-column grid: left (inputs) + right (drone/insights) |
| FrameWrapper | (in AssessmentLayout) | Animation wrapper with title/subtitle |
| CardNavigation | (in AssessmentLayout) | Back/Next buttons + dot indicators |

#### Visualization Components

| Component | File | Purpose |
|-----------|------|---------|
| CircularProgress | `/components/rings/CircularProgress.tsx` | 5-ring concentric SVG score visualization |
| PillarCards | `/components/rings/PillarCards.tsx` | 2x2 grid of pillar score cards with wave animations |
| ScoreRing | `/components/ui/ScoreRing.tsx` | Reusable circular progress ring |
| InsightsPanel | `/components/insights/InsightsPanel.tsx` | Real-time insight cards with severity coloring |
| DronePanel | `/components/common/DroneAssistant.tsx` | Animated drone avatar + speech bubble |

---

## 3. DATA FLOW & STATE MANAGEMENT

### STATE MANAGEMENT

**Method:** Zustand (with immer, persist, devtools middleware)

**Primary Stores:**

| Store | File | Purpose |
|-------|------|---------|
| useSessionStore | `/lib/store/useSessionStore.ts` | Frame navigation, XP tracking, quiz answers |
| useStudentStore | `/lib/store/useStudentStore.ts` | Complete student profile (58+ attributes) |
| useResultsStore | `/lib/store/useResultsStore.ts` | Scoring results, school probabilities |
| useInsightsStore | `/lib/store/useInsightsStore.ts` | AI insights with auto-subscription |
| useFrame3Store | `/lib/store/useFrame3Store.ts` | Psychometrics, operating style, aura |
| useFrame4Store | `/lib/store/useFrame4Store.ts` | Quiz responses, IvyScore breakdown |
| useFrame5Store | `/lib/store/useFrame5Store.ts` | Selected boosters, action plan |

### STATE STRUCTURE

```typescript
// useStudentStore structure
{
  profile: {
    identity: { role, name, grade },
    target_schools: string[],
    intended_major: string,
    aptitude: { gpa_weighted, gpa_unweighted, sat_total, act_total, ap_count, ap_avg_score, academic_awards[] },
    passion: { spike_category, leadership_level, ec_commitment_years, ec_hours_weekly, project_description, project_impact, brag_text, research_level, ec_awards[] },
    community: { service_hours, community_impact, service_leadership },
    high_school: { name, code, type, region, saturation_level, adjustment },
    demographics: { ethnicity, first_gen, legacy, income_bracket, recruited_athlete },
    assessment_intelligence: { psychometrics, time_management, hidden_capabilities[] },
  },
  isLoading: boolean,
  isDirty: boolean,
}

// useSessionStore structure
{
  session_id: string,
  current_frame: 1-6,
  current_card: number,
  frame_progress: Record<number, { cards_completed, xp_earned, started_at, completed_at }>,
  quiz_answers: QuizAnswer[],
  total_xp: number,
  is_completed: boolean,
}

// useInsightsStore structure
{
  insights: Insight[],
  isGenerating: boolean,
  lastGeneratedAt: number,
  lastTrigger: string,
}
```

### DATA FLOW

```
User Input (Component)
    ↓
Store Update (useStudentStore.setXXX())
    ↓
isDirty flag set to true
    ↓
InsightsStore auto-subscription detects change
    ↓
InsightEngine.generate() called
    ↓
Insights updated in store
    ↓
InsightsPanel re-renders
    ↓
AutoSaveManager (500ms debounce)
    ↓
localStorage persistence
```

### PERSISTENCE

- **Primary:** localStorage key `'ivyquest_v3_current'`
- **History:** localStorage key `'ivyquest_v3_history'` (up to 10 sessions)
- **Auto-save:** 500ms debounce on dirty changes
- **Session Timeout:** 24 hours default
- **Storage Quota:** 5MB browser limit with usage tracking

### API INTEGRATIONS

| Endpoint | Method | Purpose | Data |
|----------|--------|---------|------|
| `/api/score` | POST | Scoring engine | Sends: StudentProfile → Returns: AssessmentResults |
| `/api/nlp` | POST | Brag text extraction | Sends: {type, text} → Returns: {extraction: {...}} |

---

## 4. SCORING & CALCULATION SYSTEM

### SCORING LOCATION

**Primary Engine:** `/lib/scoring/engine.ts` (31.7 KB)
**API Endpoint:** `/app/api/score/route.ts`
**Archetype Detection:** `/lib/scoring/archetypeDetector.ts`
**Factor Analysis:** `/lib/scoring/factorAnalysis.ts`

### TYPES OF SCORES

| Score | Range | Purpose |
|-------|-------|---------|
| Ivy+ Ready Score | 0-100 | Overall competitiveness |
| Aptitude Score | 0-100 | Academic performance |
| Passion Score | 0-100 | EC engagement |
| Community Score | 0-100 | Service & impact |
| Narrative Score | 0-100 | Psychometric readiness |
| SFFA Rubric | 1-6 | Academic, EC, Athletic, Personal, Overall |
| School Probability | 0-95% | Per-school admission probability |

### KEY FORMULAS

**Category Weights (Overall):**
- Aptitude: 30%
- Passion: 35%
- Community: 25%
- Narrative: 10%

**School Probability (Sigmoid):**
```
P_base = 1 / (1 + exp(-(0.05 * S - C_j)))
Where:
- S = rubric composite (0-100)
- C_j = school threshold (Harvard: 3.1, MIT: 2.8, etc.)

P_final = min(0.95, P_base × context_multipliers)
```

**Context Multipliers (Chetty 2023):**
- Legacy: 0x to 5x (school-specific)
- First-gen: 1.15x
- Recruited athlete: 2.5x
- Income top 1%: 1.20x
- Saturation: -0.08 to +0.05

### RESULTS DISPLAY

**Visualization Libraries:**
- **Framer Motion** (^11.11.9): Animations, transitions
- **SVG-based:** CircularProgress, PillarCards (custom)
- **Three.js + React Three Fiber** (^8.17.10): 3D Digital Twin Fleet

**Components:**
- `CircularProgress`: 5-ring concentric SVG (78-162px radii)
- `PillarCards`: 2x2 grid with wave animations
- `ScoreRing`: Reusable circular progress
- School cards: Probability + fit level + reasons

---

## 5. FEEDBACK/MESSAGING SYSTEM

### CURRENT FEEDBACK SYSTEM (Updated December 2025)

**Messages Exist:** Yes - Now fully dynamic and contextual

**Two Integrated Systems:**

1. **Drone Assistant Messages** (Now Dynamic ✅)
   - Location: `/lib/constants/droneMessages.ts`
   - Component: `/components/common/DroneAssistant.tsx`
   - Trigger: Frame/card change + user input
   - Personalization: ✅ Dynamic based on profile data, grade, selections

2. **Insights System** (Fully Implemented ✅)
   - Location: `/lib/insights/realtimeInsights.ts`, `/lib/insights/generators/`
   - Store: `/lib/store/useInsightsStore.ts`
   - Component: `/components/insights/InsightsPanel.tsx`
   - Card Components:
     - `IvyInsightCard.tsx` - Primary insight display
     - `ContextualInsightCard.tsx` - Context-aware insights
     - `NotificationInsightCard.tsx` - Alert-style insights
     - `LoadingInsight.tsx` - Frame 5 loading state
   - Trigger: Profile data change (real-time)
   - Personalization: Full (profile, schools, demographics, benchmarks)

### DRONE MESSAGE EXAMPLES

```typescript
// Frame 1 Messages
FRAME1_MESSAGES = {
  role: "Hi there! I'm Ivy, your college admissions assistant...",
  identity: "Great choice! Now, tell me your name and what grade you're in...",
  schools: "Dream big! Select the schools you're interested in...",
  major: "What field excites you the most?..."
}

// Frame 5 Messages
FRAME5_MESSAGES = {
  loading: "Analyzing your profile with our AI engine...",
  score: "Here's your Ivy+ Ready Score!...",
  schools: "Now let's see how you match up with each school...",
  fleet: "Meet your Digital Twin Fleet!...",
  factors: "Understanding what's helping and holding you back...",
  archetype: "Every successful applicant has a unique story..."
}
```

### INSIGHTS SYSTEM (7 Categories)

| Category | Icon | Purpose |
|----------|------|---------|
| HYPER_LOCAL | School | High school peer benchmarking (AP utilization, SAT gaps) |
| CONTEXT | Users | Demographics, region, hooks/advantages |
| TEMPORAL | Clock | Grade-aware timing insights |
| APTITUDE | BookOpen | GPA, SAT, rigor analysis |
| PASSION | Heart | Leadership, research, impact level |
| PSYCHOMETRIC | Brain | Grit, burnout risk, time management |
| INSTITUTIONAL | Building | CDS benchmarks, school-specific comparisons |

### INSIGHT STRUCTURE

```typescript
interface Insight {
  id: string;
  category: InsightCategory;
  title: string;
  message: string;
  severity: 'critical' | 'warning' | 'positive' | 'neutral';
  priority: number; // 1-10
  dataSource: string;
  delta?: string; // e.g., "-40 pts", "+0.2 GPA"
  data?: { studentValue, benchmark, percentile, schoolId, ... };
}
```

### TEMPLATE SYSTEM

**Exists:** Partial
- Constants files for static messages
- InsightEngine generates dynamic messages
- No interpolation/templating engine (messages are computed)

### INTEGRATION STATUS (Updated December 2025)

| Feature | Location | Status |
|---------|----------|--------|
| Real-time insights | `/lib/insights/realtimeInsights.ts` | ✅ Fully integrated |
| Loading insights | `/lib/insights/loadingInsights.ts` | ✅ Frame 5 loading state |
| Benchmark data | `/lib/data/benchmarks.ts` | ✅ Percentile calculations |
| Outcome data | `/lib/data/outcomeData.ts` | ✅ Success statistics |
| Toast notifications | `/lib/visualization/feedback-system/` | Framework exists, minimal use |
| Achievement system | `/lib/visualization/feedback-system/types/` | Types defined, not triggered |
| Milestone system | `/lib/visualization/feedback-system/constants/` | 7 milestones defined, not implemented |
| Score delta animations | `/lib/visualization/feedback-system/types/` | 🔲 Phase 3 (Gamification) |
| Point burst animations | - | 🔲 Phase 3 (Gamification) |

---

## 6. UI/UX PATTERNS & TRANSITIONS

### LOADING STATES

**Between Frames:** Yes
- Component: Framer Motion `AnimatePresence`
- Duration: 0.3s transition
- Content: Fade + slide animation

**Scoring Loading:** Yes (Frame 5)
- Component: `/components/frames/Frame5Reveal.tsx`
- Duration: API call (~1-3s)
- Content: "Analyzing your profile..." + pulsing dot

### TRANSITIONS

**Animation Library:** Framer Motion (^11.11.9)

**Implemented Transitions:**
- Frame entry: `opacity: 0→1, y: 20→0` (0.3s)
- Frame exit: `opacity: 1→0, y: 0→-20` (0.3s)
- Card navigation: Dot indicator scale/color
- Ring animations: Staggered stroke-dashoffset (1.5s per ring)
- Pillar cards: Wave path animations (3s duration)
- Insight cards: `opacity: 0→1, y: 10→0`
- XP counter: Scale bounce on update

### PROGRESS INDICATORS

**Type:** Segmented bar + card dots

**Components:**
- `FrameProgress`: 6 segments (one per frame), animated fill
- `CardNavigation`: Dot indicators (current = wide, completed = orange, pending = gray)

**Location:** `/components/ui/Progress.tsx`, `/components/layout/AssessmentLayout.tsx`

**Updates:** On frame/card change via useSessionStore

### INPUT VALIDATION

| Input | Validation | Error Display |
|-------|------------|---------------|
| Name | ≥2 characters | Inline (button disabled) |
| Grade | Required selection | Inline (button disabled) |
| Schools | ≥1 selected | Inline (button disabled) |
| Major | ≥2 characters | Inline (button disabled) |
| GPA | 2.0-5.0 range | Slider constraints |
| SAT | 400-1600 range | Slider constraints |
| Brag text | ≥50 chars for AI | Button disabled state |

### ERROR/SUCCESS STATES

- **Errors:** Button disabled state + visual graying
- **Success:** Card completion → orange dot transition
- **Toast:** Framework exists but minimal use
- **Validation:** Real-time via slider/input constraints

---

## 7. INTEGRATION POINTS FOR INSIGHTS

### 1. AFTER USER INPUTS

| Location | Current Behavior | Opportunity | Readiness |
|----------|------------------|-------------|-----------|
| GPA input (Frame 2) | Slider updates store | Add contextual insight: "Your GPA is in the top X% of MIT admits" | **Easy** - InsightsPanel already exists |
| Test scores (Frame 2) | Tab selection + slider | Add percentile context: "1520 SAT = 99th percentile" | **Easy** - already showing in UI |
| Leadership (Frame 3) | Level selection | Add normalization: "Only 3% of applicants are national founders" | **Easy** - data available |
| Service hours (Frame 3) | Slider input | Add benchmark: "That's 2x the average applicant" | **Easy** - calculation exists |
| School selection (Frame 1) | Multi-select | Add acceptance rate context per school | **Easy** - CDS data available |

### 2. DURING LOADING/TRANSITIONS

| Location | Current Behavior | Opportunity | Readiness |
|----------|------------------|-------------|-----------|
| Frame 5 loading | "Analyzing..." text | Show educational facts, philosophy quotes, statistics | **Easy** - just text swap |
| Between frames | Fade transition | Add micro-insights or tips | **Medium** - needs transition integration |
| Card completion | Dot turns orange | Add celebratory micro-feedback | **Easy** - animation addition |

### 3. AT CALCULATION POINTS

| Location | Current Behavior | Opportunity | Readiness |
|----------|------------------|-------------|-----------|
| Score reveal (Frame 5) | Number display | Add percentile, comparison to similar students | **Easy** - data exists |
| School probabilities | Percentage cards | Add "You're X above/below average" | **Easy** - calculation exists |
| Factor analysis | List display | Add improvement predictions | **Medium** - needs booster linking |

### 4. IN RESULTS SECTION

| Location | Current Behavior | Opportunity | Readiness |
|----------|------------------|-------------|-----------|
| Archetype reveal | Label + tagline | Add detailed personality insights, similar successful students | **Medium** - needs content creation |
| Helping factors | Green list | Add "This alone is worth X% boost" quantification | **Easy** - data exists |
| Holding back | Orange list | Add specific improvement actions with ROI | **Easy** - booster engine exists |
| Power-ups | Booster cards | Add before/after score projections | **Easy** - calculation exists |

---

## 8. CRITICAL QUESTIONS ANSWERED

### 1. Is there an existing message/feedback system we can extend, or build from scratch?

**Answer: EXTEND existing systems**

Two systems to extend:
1. **Drone Messages** (`droneMessages.ts`): Add dynamic variant that pulls from profile
2. **Insights System** (`InsightEngine.ts`): Fully functional, just add more insight types

The feedback-system framework in `/lib/visualization/feedback-system/` has types for toasts, achievements, milestones, and score deltas - all defined but not integrated.

### 2. Where is assessment state stored? Can we easily access it for insights?

**Answer: Zustand stores, easily accessible**

```typescript
import { useStudentStore, useSessionStore, useInsights } from '@/lib/store';

// In any component:
const profile = useStudentStore((s) => s.profile);
const { gpa_weighted, sat_total } = profile.aptitude;
const insights = useInsights(); // Already auto-generated
```

### 3. Are there loading states where we can inject insights?

**Answer: Yes - multiple locations**

1. **Frame 5 loading** (scoring API call): 1-3 seconds available
2. **Frame transitions**: 0.3s animation gap
3. **Card completion**: Brief moment before next card
4. **Drone panel**: Always visible on desktop right panel

### 4. Is user data sufficient for personalization?

**Answer: Yes - 58+ attributes available**

Available data:
- Identity: name, grade, role
- Target schools: array of school IDs
- Academics: GPA, SAT/ACT, AP count/scores, awards
- Passions: spike, leadership, commitment, projects, research
- Community: service hours, impact, leadership
- Demographics: ethnicity, first-gen, legacy, income, athlete
- High school: saturation level, region, type
- Psychometrics: coachability, introversion, openness, conscientiousness

### 5. What visualization library is used? Can we add insight cards?

**Answer: Framer Motion + custom SVG**

- Framer Motion for animations
- Custom SVG for rings/waves
- InsightsPanel component already exists with severity coloring
- Adding insight cards is trivial - just add to insights array

### 6. Are there any Noom-style tactics already implemented?

**Answer: Partially**

| Tactic | Status |
|--------|--------|
| Personalized insights | Yes (InsightEngine) |
| Real-time feedback | Yes (auto-subscription) |
| Gamification (XP) | Yes (fully implemented) |
| Progress visualization | Yes (frame progress, rings) |
| Contextual messaging | Partial (drone is static) |
| Statistics/benchmarks | Partial (in insights, could expand) |
| Celebratory moments | No (framework exists, not triggered) |
| Loading state content | No (just "Analyzing...") |

### 7. What's the SIMPLEST place to add our FIRST insight as a proof-of-concept?

**Answer: Frame 5 loading state**

Location: `/components/frames/Frame5Reveal.tsx` lines ~75-124

Why:
1. User is waiting anyway (API call)
2. No UI changes needed - just text content
3. High engagement moment (anticipating results)
4. Can show 3-4 rotating facts during load
5. Already has loading indicator

**Implementation:**
```typescript
const LOADING_INSIGHTS = [
  "Did you know? MIT's middle 50% SAT range is 1510-1570.",
  "Fun fact: Harvard's acceptance rate dropped to 4.2% this year.",
  "Your GPA is in the top 15% of all applicants nationwide.",
  // personalized based on profile
];

// Show rotating insight during loading
{isLoading && <RotatingInsight messages={LOADING_INSIGHTS} />}
```

---

## SUMMARY (Updated December 2025)

### WHAT'S NOW IMPLEMENTED ✅

1. **InsightEngine + InsightsPanel**: ✅ Fully functional with real-time updates
2. **Drone messaging system**: ✅ Now dynamic with contextual messages
3. **State management**: ✅ All 58+ profile attributes accessible + useInsightsStore
4. **Scoring data**: ✅ All calculations + benchmark percentiles
5. **Visualization components**: ✅ CircularProgress, PillarCards, ScoreRing, InsightCards
6. **Animation system**: ✅ Framer Motion integrated throughout
7. **Loading state content**: ✅ Frame 5 loading insights implemented
8. **Benchmark data**: ✅ GPA, SAT, leadership percentiles
9. **Outcome data**: ✅ Success statistics by profile type
10. **Two-column layout**: ✅ Frames 1-3 with drone panel

### WHAT'S STILL MISSING (Phase 3)

1. **Point burst animations**: Floating "+15" on positive inputs
2. **Sound effects**: Web Audio API integration
3. **StrengthBadge indicators**: Category badges
4. **XP counter animations**: Header XP increment effects
5. **Achievement popups**: Celebration moments on milestones
6. **View All Insights modal**: Collected insights history

### IMPLEMENTATION PROGRESS

| Phase | Status | Commit |
|-------|--------|--------|
| Phase 1: Layout Restructuring | ✅ Complete | `5444ca4` |
| Phase 2: Dynamic Drone Messages | ✅ Complete | `5444ca4` |
| Phase 3: Gamification Engine | 🔲 Not Started | - |
| Phase 4: Insight Collection | ✅ Complete | `5444ca4` |
| Phase 5: Data-Backed Messages | ✅ Complete | `5444ca4` |

**Overall: 4/5 phases complete (80%)**

### NEXT PRIORITY: Phase 3 - Gamification Engine

| Component | Purpose | Effort |
|-----------|---------|--------|
| `PointBurst.tsx` | Animated floating points | 2-3 hours |
| `StrengthBadge.tsx` | Category indicators | 1-2 hours |
| `SoundEffects.ts` | Web Audio API sounds | 2-3 hours |
| `GamificationProvider.tsx` | Context for state | 1-2 hours |
| Integration with frames | Wire up triggers | 3-4 hours |

**Estimated remaining effort:** 10-15 hours for Phase 3

---

*Report updated by Claude Code - December 2025*
