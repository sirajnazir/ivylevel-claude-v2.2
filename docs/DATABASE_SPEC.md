# IvyQuest v2.2 - Database Specification Document

**Single Source of Truth for All Data Models**

**Version**: 2.2.0
**Last Updated**: 2025-12-18
**Author**: Claude Code

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Core Data Models](#2-core-data-models)
3. [Type Enumerations](#3-type-enumerations)
4. [Layer 1: Core Attributes](#4-layer-1-core-attributes)
5. [Layer 2: Target Schools & Major](#5-layer-2-target-schools--major)
6. [Layer 3: Context](#6-layer-3-context)
7. [Layer 4: Assessment Intelligence](#7-layer-4-assessment-intelligence)
8. [Operating Data (Frame 4)](#8-operating-data-frame-4)
9. [Scoring Engine Outputs](#9-scoring-engine-outputs)
10. [Booster/Mod System](#10-boostermod-system)
11. [Zustand Stores](#11-zustand-stores)
12. [Constants & Defaults](#12-constants--defaults)
13. [Digital Twin System](#13-digital-twin-system)
14. [Archetype System](#14-archetype-system)
15. [API Payloads](#15-api-payloads)
16. [File Locations](#16-file-locations)

---

## 1. Executive Summary

This document serves as the **single source of truth** for all data models, types, stores, and constants in the IvyQuest application.

### Key Statistics
- **58 student attributes** across 4 layers
- **6 Zustand stores** for state management
- **12 target schools** supported
- **20+ boosters** in the recommendation engine
- **4 scoring categories** (Aptitude, Passion, Community, Narrative)

### Data Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    StudentProfile                           │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Core Attributes (70% of score)                    │
│    ├── Aptitude (35%)                                       │
│    ├── Passion (35%)                                        │
│    └── Community (25%)                                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Target Schools & Major                            │
│    ├── target_schools[]                                     │
│    ├── intended_major                                       │
│    └── major_certainty                                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Context Multipliers                               │
│    ├── high_school (saturation)                             │
│    ├── demographics (multipliers)                           │
│    └── major_context                                        │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Assessment Intelligence                           │
│    ├── psychometrics                                        │
│    ├── time_management                                      │
│    ├── hidden_capabilities                                  │
│    ├── family_context                                       │
│    └── academic_intelligence                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Core Data Models

### Complete StudentProfile Interface

```typescript
interface StudentProfile {
  // Meta
  session_id: string;                        // UUID v4
  timestamp: string;                         // ISO 8601

  // Identity
  identity: StudentIdentity;

  // Layer 2: Targets
  target_schools: string[];
  intended_major: string;
  major_certainty: MajorCertainty;

  // Layer 1: Core Attributes
  aptitude: AptitudeAttributes;
  passion: PassionAttributes;
  community: CommunityAttributes;

  // Layer 3: Context
  high_school: HighSchoolContext | null;
  demographics: DemographicContext;
  major_context: MajorContext;

  // Layer 4: Assessment Intelligence
  assessment_intelligence: AssessmentIntelligence;

  // Frame 4: Operating Data
  operating?: OperatingData;

  // Profile Analysis
  completeness?: ProfileCompleteness;
  classification?: ProfileClassification;
}
```

### StudentIdentity

```typescript
interface StudentIdentity {
  role: Role;                    // 'STUDENT' | 'PARENT'
  name: string;                  // Student name
  grade: Grade;                  // 9 | 10 | 11 | 12 | 'gap'
  student_id?: string;           // Optional unique ID
}
```

---

## 3. Type Enumerations

### Grade Levels
```typescript
type Grade = 9 | 10 | 11 | 12 | 'gap';
```

### User Roles
```typescript
type Role = 'STUDENT' | 'PARENT';
```

### Major Certainty
```typescript
type MajorCertainty = 'EXPLORING' | 'LIKELY' | 'LOCKED';
```

### School Context
```typescript
type HSType = 'PUBLIC' | 'PRIVATE' | 'MAGNET' | 'CHARTER';

type SaturationLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'ULTRA';

type Region =
  | 'BAY_AREA'
  | 'NORTHEAST'
  | 'SOUTH'
  | 'MIDWEST'
  | 'SOUTHWEST'
  | 'NORTHWEST'
  | 'INTERNATIONAL'
  | 'OTHER';
```

### Activity Classifications
```typescript
type SpikeCategory =
  | 'RESEARCH'
  | 'LEADER'
  | 'SERVICE'
  | 'CREATE'
  | 'BUSINESS'
  | 'SPORTS'
  | 'FIGURING';

type LeadershipLevel =
  | 'FOUNDER_NATIONAL'
  | 'FOUNDER_STATE'
  | 'STATE_PRES'
  | 'SCHOOL_PRES'
  | 'OFFICER'
  | 'PARTICIPANT';

type ResearchLevel =
  | 'NATIONAL'
  | 'STATE'
  | 'SCHOOL'
  | 'INDEPENDENT'
  | 'NONE';

type ServiceLeadership =
  | 'NATIONAL'
  | 'REGIONAL'
  | 'LOCAL'
  | 'PARTICIPANT';
```

### Psychometric Profiles
```typescript
type CoachabilityLevel = 'HIGH' | 'MEDIUM' | 'LOW';
type BurnoutRisk = 'LOW' | 'MEDIUM' | 'HIGH';
type EffortLevel = 'LOW' | 'MEDIUM' | 'HIGH';
```

### Demographics
```typescript
type Ethnicity =
  | 'ASIAN'
  | 'BLACK'
  | 'HISPANIC'
  | 'WHITE'
  | 'NATIVE'
  | 'PACIFIC_ISLANDER'
  | 'MULTIRACIAL'
  | 'OTHER'
  | 'PREFER_NOT_SAY';

type IncomeBand =
  | 'BELOW_75K'
  | '75K_150K'
  | '150K_300K'
  | 'ABOVE_300K'
  | 'TOP_1_PERCENT'
  | 'PREFER_NOT_SAY';

type ParentArchetype = 'HELICOPTER' | 'BALANCED' | 'HANDS_OFF';
```

### Profile Assessment
```typescript
type SchoolFit = 'BEST_FIT' | 'STRONG_FIT' | 'TOUGH' | 'WORST_FIT';
type ProfileTier = 'fresh-start' | 'emerging' | 'optimization';
type ProfilePhase = 'foundation' | 'direction-setting' | 'refinement';
type ClarityLevel = 'low' | 'medium' | 'high';
```

---

## 4. Layer 1: Core Attributes

### 4.1 Aptitude Attributes (35% of total score)

**Purpose**: Academic credentials and intellectual rigor

| Sub-category | Weight | Fields |
|-------------|--------|--------|
| GPA | 35% | `gpa_weighted`, `gpa_unweighted`, `gpa_normalized` |
| Tests | 30% | `sat_total`, `act_total`, `sat_normalized`, `test_optional` |
| Rigor | 20% | `ap_count`, `ap_avg_score`, `ib_diploma`, `rigor_normalized` |
| Awards | 15% | `academic_awards[]`, `awards_normalized` |

```typescript
interface AptitudeAttributes {
  // GPA (0.35 weight)
  gpa_weighted: number | null;          // 4.0-4.7+ scale
  gpa_normalized: number | null;        // 0.0-1.0 rubric score
  gpa_unweighted?: number | null;       // Traditional 4.0 scale

  // Tests (0.30 weight)
  sat_total: number | null;             // 1200-1600
  sat_normalized: number | null;        // 0.0-1.0 rubric score
  sat_math?: number | null;
  sat_verbal?: number | null;
  act_total: number | null;             // 24-36
  act_normalized?: number | null;
  test_optional: boolean;               // Default: false

  // Rigor (0.20 weight)
  ap_count: number | null;              // 0-15+
  ap_avg_score: number | null;          // 3.0-5.0
  rigor_normalized: number | null;      // 0.0-1.0
  ib_diploma: boolean;                  // Default: false
  dual_enrollment_credits?: number | null;

  // Academic Recognition (0.15 weight)
  academic_awards: string[];            // USAMO, ISEF, Regeneron, etc.
  awards_normalized: number | null;     // 0.0-1.0
}
```

**Default Values**:
```typescript
NORMALIZED_DEFAULTS.aptitude = {
  gpa: 0.5,           // ~3.3 GPA equivalent
  sat: 0.5,           // ~1300 SAT
  rigor: 0.4,         // 4-5 AP courses
  awards: 0.0,        // No awards
}

RAW_DEFAULTS.aptitude = {
  gpa_weighted: 3.5,
  gpa_unweighted: 3.3,
  sat_total: 1300,
  act_total: 28,
  ap_count: 5,
  ap_avg_score: 3.5,
}
```

---

### 4.2 Passion Attributes (35% of total score)

**Purpose**: Extracurricular spike and depth

| Sub-category | Weight | Fields |
|-------------|--------|--------|
| Leadership | 35% | `leadership_level`, `leadership_normalized` |
| Projects | 20% | `project_impact`, `project_normalized`, `project_description` |
| Research | 20% | `research_level`, `research_normalized` |
| EC Commitment | 15% | `ec_commitment_years`, `ec_hours_weekly`, `commitment_normalized` |
| EC Awards | 10% | `ec_awards[]`, `ec_awards_normalized` |

```typescript
interface PassionAttributes {
  // Spike Category
  spike_category: SpikeCategory | null;

  // Leadership (0.35 weight)
  leadership_level: LeadershipLevel | null;
  leadership_normalized: number | null;   // 0.0-1.0
  leadership_description?: string;

  // EC Commitment (0.15 weight)
  ec_commitment_years: number | null;     // 1-4+
  ec_hours_weekly: number | null;         // 1-20+
  commitment_normalized: number | null;

  // Projects & Impact (0.20 weight)
  project_impact: number | null;          // People affected: 0-10000+
  project_normalized: number | null;      // 0.0-1.0
  project_description?: string;

  // Research (0.20 weight)
  research_level: ResearchLevel | null;
  research_normalized: number | null;     // 0.0-1.0
  research_description?: string;

  // EC Awards (0.10 weight)
  ec_awards: string[];                    // STATE, NATIONAL, INTERNATIONAL
  ec_awards_normalized: number | null;

  // NLP Extraction
  brag_text: string | null;
  brag_nlp_extracted: Record<string, any> | null;
}
```

**Default Values**:
```typescript
NORMALIZED_DEFAULTS.passion = {
  leadership: 0.25,     // Participant level
  project: 0.2,         // ~20 people impact
  research: 0.0,        // No research
  commitment: 0.5,      // 2 years, moderate
  awards: 0.0,          // No EC awards
}

RAW_DEFAULTS.passion = {
  ec_commitment_years: 2,
  ec_hours_weekly: 8,
  project_impact: 20,
}
```

---

### 4.3 Community Attributes (25% of total score)

**Purpose**: Service leadership and social impact

| Sub-category | Weight | Fields |
|-------------|--------|--------|
| Service Leadership | 35% | `service_leadership`, `service_normalized` |
| Community Impact | 35% | `community_impact`, `impact_normalized` |
| Hours | 20% | `service_hours`, `hours_normalized` |
| Description | 10% | `service_description` |

```typescript
interface CommunityAttributes {
  // Service Leadership (0.35 weight)
  service_leadership: ServiceLeadership | null;
  service_normalized: number | null;        // 0.0-1.0

  // Hours (0.20 weight)
  service_hours: number | null;             // Total by graduation
  hours_normalized: number | null;

  // Community Impact (0.35 weight)
  community_impact: number | null;          // People affected
  impact_normalized: number | null;         // 0.0-1.0

  // Description (0.10 weight)
  service_description?: string;
}
```

**Default Values**:
```typescript
NORMALIZED_DEFAULTS.community = {
  service: 0.3,       // Participant level
  hours: 0.4,         // ~75 hours
  impact: 0.2,        // Small local impact
}

RAW_DEFAULTS.community = {
  service_hours: 75,
  community_impact: 20,
}
```

---

## 5. Layer 2: Target Schools & Major

```typescript
// Attached to StudentProfile
target_schools: string[];           // School IDs: 'HARVARD', 'MIT', etc.
intended_major: string;             // User-entered major
major_certainty: MajorCertainty;    // 'EXPLORING' | 'LIKELY' | 'LOCKED'
```

### Supported Schools

| School ID | Name | Base Acceptance Rate |
|-----------|------|---------------------|
| HARVARD | Harvard University | 3.2% |
| STANFORD | Stanford University | 3.7% |
| MIT | MIT | 3.9% |
| YALE | Yale University | 4.6% |
| PRINCETON | Princeton University | 4.0% |
| COLUMBIA | Columbia University | 3.9% |
| UPENN | University of Pennsylvania | 5.7% |
| BROWN | Brown University | 5.1% |
| DARTMOUTH | Dartmouth College | 6.2% |
| CORNELL | Cornell University | 7.3% |
| CALTECH | Caltech | 2.7% |
| DUKE | Duke University | 6.0% |

---

## 6. Layer 3: Context

### 6.1 High School Context

```typescript
interface HighSchoolContext {
  hs_name: string;                          // School name
  hs_code: string;                          // Unique identifier
  hs_type: HSType;                          // PUBLIC | PRIVATE | MAGNET | CHARTER
  region: Region;                           // Geographic region

  // Saturation (NSC historical data)
  saturation_level: SaturationLevel;        // LOW | MEDIUM | HIGH | ULTRA
  ivy_applicants_per_year: number;          // Historical count
  saturation_adjustment: number;            // -0.08 to +0.05
}
```

**Saturation Adjustments**:
| Level | Adjustment | Description |
|-------|------------|-------------|
| LOW | +0.05 | Underrepresented school, boost probability |
| MEDIUM | 0.00 | Average representation |
| HIGH | -0.05 | Many applicants, slight penalty |
| ULTRA | -0.08 | Feeder school, significant penalty |

---

### 6.2 Demographic Context

```typescript
interface DemographicContext {
  ethnicity: Ethnicity | null;
  ethnicity_multiplier: number;             // 0.85-1.15

  first_gen: boolean | null;
  first_gen_multiplier: number;             // 1.15 if true (Chetty 2023)

  legacy: boolean | null;
  legacy_schools: string[];                 // Which schools have legacy

  income_band: IncomeBand | null;
  income_top_1_percent: boolean;
  income_multiplier: number;                // 0.95-1.20

  recruited_athlete: boolean;
  athlete_multiplier: number;               // 2.5 if true (Chetty 2023)
}
```

**Multipliers (Chetty 2023 Research)**:
| Factor | Multiplier | Source |
|--------|------------|--------|
| First Generation | 1.15x | Chetty 2023 |
| Recruited Athlete | 2.5x | Chetty 2023 |
| Legacy (Harvard) | 5.0x | SFFA Trial |
| Legacy (MIT) | 1.0x (none) | MIT Policy |
| Top 1% Income | 1.20x | Chetty 2023 |

---

### 6.3 Major Context

```typescript
interface MajorContext {
  intended_major: string;                   // User's intended major
  major_certainty: MajorCertainty;
  major_multiplier: number;                 // School-specific difficulty
}
```

**Major Multipliers by School** (example):
| School | CS | Pre-Med | Business | Humanities |
|--------|-----|---------|----------|------------|
| Stanford | 0.55 | 0.70 | 0.75 | 0.90 |
| MIT | 0.65 | N/A | 0.80 | 0.95 |
| Harvard | 0.60 | 0.65 | 0.70 | 0.85 |

---

## 7. Layer 4: Assessment Intelligence

### 7.1 Psychometrics

```typescript
interface StudentPsychometrics {
  // Core Traits (0.0-1.0 scales)
  grit_resilience: number | null;
  introversion_extroversion: number | null;    // -1.0 to +1.0
  coachability: CoachabilityLevel | null;
  coachability_score: number | null;           // 0.0-1.0

  // Narrative Readiness
  vision_clarity: number | null;               // 0.0-1.0
  identity_comfort: number | null;             // 0.0-1.0
  maturity_level: number | null;               // 0.0-1.0
  articulation_ability: number | null;         // 0.0-1.0 (NLP-derived)

  // Big Five OCEAN
  openness: number | null;
  conscientiousness: number | null;
  extraversion: number | null;
  agreeableness: number | null;
  neuroticism: number | null;
}
```

---

### 7.2 Time Management Profile

```typescript
interface TimeManagementProfile {
  homework_hours_daily: number | null;        // 1-8+
  social_media_hours_daily: number | null;    // 0-6+
  ec_hours_weekly: number | null;             // From passion
  sleep_hours_daily: number | null;           // Default 8

  // Computed
  committed_hours_weekly: number | null;      // Sum of above × 7
  reclaimable_hours_weekly: number | null;    // 168 - committed
  burnout_risk: BurnoutRisk | null;           // Based on ratio
}
```

**Default Values**:
```typescript
time_management: {
  homework_hours_daily: 3,
  social_media_hours_daily: 2,
  ec_hours_weekly: 10,
  sleep_hours_daily: 7,
  committed_hours_weekly: 100,
  reclaimable_hours_weekly: 20,
  burnout_risk: 'MEDIUM',
}
```

---

### 7.3 Hidden Capabilities

```typescript
interface HiddenCapabilities {
  hidden_technical_projects: string[];       // Discord bots, mods, etc.
  hobby_passions: string[];                  // Vintage bikes, fanfic, Etsy
  unconventional_interests: string[];
  family_responsibilities?: string;
  work_experience?: string;
}
```

---

### 7.4 Family Context

```typescript
interface FamilyContext {
  parent_archetype: ParentArchetype | null;  // HELICOPTER | BALANCED | HANDS_OFF
  academic_expectations: string | null;      // IVY_ONLY, TOP_20, FLEXIBLE
  family_challenges?: string;
  parent_education_level?: string;
}
```

---

### 7.5 Academic Intelligence

```typescript
interface AcademicIntelligence {
  grade_pattern_trajectory: 'UPWARD' | 'STABLE' | 'DOWNWARD' | null;
  gpa_dip_context?: string;                  // Explanation if dip exists
  test_anxiety_indicator: number | null;     // SAT vs GPA discrepancy
  learning_differences?: string;
  academic_setbacks?: string;
}
```

---

### 7.6 Complete AssessmentIntelligence

```typescript
interface AssessmentIntelligence {
  psychometrics: StudentPsychometrics;
  time_management: TimeManagementProfile;
  hidden_capabilities: HiddenCapabilities;
  family_context: FamilyContext;
  academic_intelligence: AcademicIntelligence;
}
```

---

## 8. Operating Data (Frame 4)

```typescript
type CareerDirection = 'yes' | 'exploring' | 'no-idea';
type TransportationType = 'drive-self' | 'parent-drives' | 'public-transit' | 'limited';

interface OperatingData {
  // Interests
  favoriteSubject?: string | null;
  favoriteSubjectReason?: string | null;
  careerDirection?: CareerDirection;
  careerInterest?: string | null;
  careerExclusions?: string[];              // ['cs', 'law', 'medicine']

  // Strengths
  strengths?: string[];                      // Selected from predefined list
  strengthExample?: string | null;
  naturalTalent?: string | null;

  // Context
  parent1Occupation?: string;
  parent2Occupation?: string;
  firstGeneration?: boolean | null;
  workHours?: number;                        // Per week
  familyResponsibilities?: string | null;
  transportation?: TransportationType;

  // Time Capacity
  availableHoursPerWeek?: number;            // 0-20
  homeworkHoursPerDay?: number;              // 0-6
  burnoutRisk?: 'low' | 'moderate' | 'high';
}
```

### Available Strengths Options
```typescript
const STRENGTH_OPTIONS = [
  'memorization',
  'hands-on',
  'explaining',
  'competitive',
  'social',
  'creative',
  'analytical',
  'disciplined',
  'curious',
  'writing',
];
```

---

## 9. Scoring Engine Outputs

### 9.1 Ivy Ready Score

```typescript
interface IvyReadyScore {
  total_score: number;                       // 0-100
  category_scores: {
    aptitude: number;                        // 0-100
    passion: number;                         // 0-100
    community: number;                       // 0-100
    narrative: number;                       // 0-100
  };
  percentile_rank: number;                   // Among Ivy applicants
}
```

**Category Weights**:
```typescript
CATEGORY_WEIGHTS.overall = {
  aptitude: 0.30,
  passion: 0.35,
  community: 0.25,
  narrative: 0.10,
}
```

---

### 9.2 School Probability

```typescript
interface SchoolProbability {
  school_id: string;
  school_name: string;

  // Probability Calculation
  p_base: number;                            // Base from rubric sigmoid
  p_context: number;                         // After context multipliers
  p_final: number;                           // Capped at 95%

  // Fit Assessment
  fit_level: SchoolFit;
  fit_reasons: string[];
  warnings: string[];

  // Evidence
  rubric_score: number;                      // 1.0-6.0 (SFFA scale)
  above_base_rate: number;                   // vs school acceptance
}
```

---

### 9.3 Profile Completeness

```typescript
interface ProfileCompleteness {
  score: number;                             // 0-100
  hasAcademics: boolean;
  hasActivities: boolean;
  hasContext: boolean;
  hasOperating: boolean;
}
```

**Completeness Calculation**:
```
Total: 0-100 points

Academics (30 points):
  +10: GPA (weighted or unweighted) > 0
  +10: Test scores (SAT or ACT) > 0
  +10: AP courses count > 0

Activities (40 points):
  +20: EC commitment years > 0
  +10: Service hours > 0
  +10: Leadership level != PARTICIPANT

Context (15 points):
  +5: Parent occupation filled
  +5: Transportation method filled
  +5: First generation status answered

Operating (15 points):
  +5: Available hours per week set
  +5: Favorite subject filled
  +5: Strengths array has items
```

---

## 10. Booster/Mod System

### 10.1 Booster Categories

```typescript
type BoosterCategory =
  | 'APTITUDE'
  | 'PASSION'
  | 'COMMUNITY'
  | 'NARRATIVE'
  | 'LOOPHOLE'
  | 'NON_ACADEMIC'
  | 'STRATEGIC';
```

### 10.2 Booster Interface

```typescript
interface Booster {
  id: string;
  name: string;
  description: string;
  category: BoosterCategory;

  // Effort
  effort: EffortLevel;
  time_weeks: number;                        // 0-24
  hours_weekly_required?: number;
  total_hours?: number;

  // Impact
  expected_lift: {
    aptitude: number;
    passion: number;
    community: number;
    narrative: number;
  };
  roi_score: number;

  // Targeting
  target_school?: string | null;
  addresses_gap?: string;

  // Projection
  current_prob?: number;
  boosted_prob?: number;
  roi?: number;

  // Matching
  matched_to_archetype?: boolean;
  matched_to_ocean?: string[];
  feasibility_score?: number;                // 0.0-1.0

  // Status
  unlocked?: boolean;
  prerequisites?: string[];
  action_steps?: string[];
  success_metric?: string;
}
```

### 10.3 Sample Boosters

| ID | Name | Category | Time | Impact |
|----|------|----------|------|--------|
| academic_competition | Join Academic Competitions | APTITUDE | 12 weeks | +8 aptitude |
| research_project | Start Research Project | APTITUDE | 24 weeks | +12 aptitude |
| leadership_role | Pursue Leadership Position | PASSION | 8 weeks | +10 passion |
| passion_project | Launch Passion Project | PASSION | 16 weeks | +15 passion |
| service_initiative | Lead Service Initiative | COMMUNITY | 12 weeks | +12 community |
| narrative_clarity | Develop Personal Narrative | NARRATIVE | 4 weeks | +10 narrative |

---

## 11. Zustand Stores

### 11.1 Store Overview

| Store | Persist Key | Middleware | Purpose |
|-------|-------------|------------|---------|
| useStudentStore | `ivyquest-student-profile` | immer, persist, devtools | Student profile data |
| useSessionStore | `ivyquest-session` | immer, persist, devtools | Navigation & progress |
| useInsightsStore | - (no persist) | immer, devtools | Real-time insights |
| useFrame3Store | `ivyquest-frame3-operating` | immer, persist, devtools | Frame 3 quiz state |
| useFrame4Store | - (no persist) | immer | Score display state |
| useFrame5Store | - (no persist) | immer | Booster selection state |

---

### 11.2 useStudentStore

**File**: `lib/store/useStudentStore.ts`
**Persist Key**: `ivyquest-student-profile`

```typescript
interface StudentStoreState {
  profile: StudentProfile;
  isLoading: boolean;
  isDirty: boolean;

  // Actions
  setIdentity(identity: Partial<StudentIdentity>): void;
  setTargetSchools(schools: string[]): void;
  setAptitude(aptitude: Partial<AptitudeAttributes>): void;
  setPassion(passion: Partial<PassionAttributes>): void;
  setCommunity(community: Partial<CommunityAttributes>): void;
  setDemographics(demo: Partial<DemographicContext>): void;
  updateOperating<K extends keyof OperatingData>(field: K, value: OperatingData[K]): void;
  calculateCompleteness(): number;
  resetProfile(): void;
  loadProfile(profile: StudentProfile): void;
}
```

---

### 11.3 useSessionStore

**File**: `lib/store/useSessionStore.ts`
**Persist Key**: `ivyquest-session`

```typescript
type FrameId = 1 | 2 | 3 | 4 | 5 | 6;

interface SessionStoreState {
  session_id: string;
  user_id: string | null;
  started_at: string;

  current_frame: FrameId;
  current_card: number;
  frame_progress: Record<FrameId, FrameProgress>;

  quiz_answers: QuizAnswer[];
  quiz_streak: number;
  quiz_total_xp: number;

  total_xp: number;
  is_completed: boolean;
  completed_at: string | null;
}
```

**Frame Card Counts**:
```typescript
FRAME_CARD_COUNTS = {
  1: 4,      // Identity, Schools, Major, Certainty
  2: 5,      // GPA, Test, AP, Awards, Summary
  3: 10,     // Scenario questions
  4: 15,     // Quiz questions
  5: 6,      // Score, Schools, Factors, Archetype, Twin, Summary
  6: 4,      // Top3, Grid, ROI, Action Plan
}
```

---

### 11.4 useInsightsStore

**File**: `lib/store/useInsightsStore.ts`
**Persist**: None (calculated real-time)

```typescript
interface InsightsStoreState {
  insights: Insight[];
  isGenerating: boolean;
  lastGeneratedAt: string | null;
  lastTrigger: string | null;
  realtimeInsights: RealtimeInsight[];

  // Actions
  generateInsights(attributeTrigger?: string): void;
  clearInsights(): void;
  addRealtimeInsight(insight: RealtimeInsight): void;
  getFilteredInsights(options: InsightFilterOptions): Insight[];
}
```

---

## 12. Constants & Defaults

### 12.1 File: `lib/constants/defaults.ts`

```typescript
// Normalized Score Defaults (0.0-1.0 scale)
export const NORMALIZED_DEFAULTS = {
  aptitude: { gpa: 0.5, sat: 0.5, rigor: 0.4, awards: 0.0 },
  passion: { leadership: 0.25, project: 0.2, research: 0.0, commitment: 0.5, awards: 0.0 },
  community: { service: 0.3, hours: 0.4, impact: 0.2 },
  narrative: { vision_clarity: 0.5, identity_comfort: 0.5, articulation: 0.5, maturity: 0.5, grit: 0.5, coachability: 0.5 },
};

// Raw Value Defaults
export const RAW_DEFAULTS = {
  aptitude: { gpa_weighted: 3.5, gpa_unweighted: 3.3, sat_total: 1300, act_total: 28, ap_count: 5, ap_avg_score: 3.5 },
  passion: { ec_commitment_years: 2, ec_hours_weekly: 8, project_impact: 20 },
  community: { service_hours: 75, community_impact: 20 },
};

// Category Weights
export const CATEGORY_WEIGHTS = {
  aptitude: { gpa: 0.35, sat: 0.30, rigor: 0.20, awards: 0.15 },
  passion: { leadership: 0.35, project: 0.20, research: 0.20, commitment: 0.15, awards: 0.10 },
  community: { service: 0.35, impact: 0.35, hours: 0.20, description: 0.10 },
  narrative: { vision: 0.30, identity: 0.25, articulation: 0.25, maturity: 0.20 },
  overall: { aptitude: 0.30, passion: 0.35, community: 0.25, narrative: 0.10 },
};

// Context Defaults
export const CONTEXT_DEFAULTS = {
  demographics: { ethnicity_multiplier: 1.0, first_gen_multiplier: 1.0, income_multiplier: 1.0, athlete_multiplier: 1.0 },
  high_school: { saturation_adjustment: 0.0, saturation_level: 'MEDIUM' },
};

// Default Target Schools
export const DEFAULT_TARGET_SCHOOLS = [
  'HARVARD', 'STANFORD', 'MIT', 'YALE',
  'PRINCETON', 'CALTECH', 'CMU', 'COLUMBIA'
];

// Validation Bounds
export const VALIDATION_BOUNDS = {
  normalized: { min: 0.0, max: 1.0 },
  percentageScore: { min: 0, max: 100 },
  probability: { min: 0.0, max: 0.95 },     // IMPORTANT: Capped at 95%
  rubricRating: { min: 1, max: 6 },         // SFFA scale
  gpa: { min: 0.0, max: 5.0 },
  sat: { min: 400, max: 1600 },
  act: { min: 1, max: 36 },
};
```

---

### 12.2 File: `lib/constants/brand.ts`

```typescript
export const BRAND_COLORS = {
  // Primary
  primary: '#FF4A23',                        // Ivylevel orange
  primaryLight: '#FF7224',
  primaryDark: '#e6391a',
  primaryBg: 'rgba(255, 74, 35, 0.1)',

  // Secondary
  secondary: '#641432',                      // Ivylevel maroon
  secondaryLight: '#8a1d45',
  secondaryBg: 'rgba(100, 20, 50, 0.1)',

  // Text
  textHeading: '#020202',
  textPrimary: '#020202',
  textSecondary: '#616479',
  textMuted: '#9698A6',

  // Background
  bgPage: '#F7F8FA',
  bgPrimary: '#FFFFFF',
  bgCard: '#F5F4F3',

  // Semantic
  success: '#1DBF73',
  warning: '#EAB705',
  error: '#dc2626',
  info: '#3b82f6',

  // Border
  borderLight: '#E6EAEE',
  borderDefault: '#DFE0E4',
  borderSelected: '#FF4A23',
};
```

---

## 13. Digital Twin System

```typescript
interface TwinGear {
  head: string | null;                       // Crown, helmet, etc.
  torso: string | null;                      // Reactor, armor
  weapon: string | null;                     // Sword, mic, beaker
  shield: string | null;                     // Community shield
  accessory: string | null;                  // Backpack, belt
  aura: string | null;                       // Grit red, adaptable blue
}

interface DigitalTwin {
  twin_id: string;                           // 'BASE' or school_id
  school_id: string | null;

  // Visual State
  theme: string;                             // 'TECH', 'LEADER', etc.
  color: string;
  gear: TwinGear;
  current_form: 'GREYED' | 'PARTIAL' | 'IDEAL';

  // Stats
  completion_percent: number;                // 0-100
  probability: number;
  is_launched: boolean;
  broke_barrier: boolean;

  // Gaps
  gaps: string[];
}

interface TwinFleet {
  base_twin: DigitalTwin;
  school_twins: DigitalTwin[];
  focused_twin: string | null;
}
```

---

## 14. Archetype System

### Supported Archetypes

| ID | Label | Detection Criteria |
|----|-------|-------------------|
| SCHOLAR | Academic Excellence | High GPA, test scores, academic awards |
| RESEARCHER | Research-Focused | Research level > SCHOOL |
| LEADER | Leadership-Driven | Leadership level > OFFICER |
| ENTREPRENEUR | Founder Mentality | Business spike + project impact |
| CHANGEMAKER | Community Impact | High service hours + impact |
| CREATOR | Project-Focused | High project_impact |
| POLYMATH | Balanced Excellence | All categories > 70% |
| EXPLORER | Finding Path | MajorCertainty = EXPLORING |
| COOKIE_CUTTER_BAY_AREA_CS | Aarnav-like | Bay Area + CS + scattered ECs |
| STRUGGLING_JUNIOR_PREMED | Low GPA Recovery | Low GPA + clinical passion |

```typescript
interface StudentArchetype {
  archetype_id: ArchetypeID;
  archetype_label: string;

  detection_criteria: {
    spike_category?: SpikeCategory;
    region?: Region;
    saturation_level?: SaturationLevel;
    leadership_level_max?: LeadershipLevel;
    passion_scattered?: boolean;
    academic_recovery?: boolean;
  };

  avatar_treatment: string;
  booster_priorities: string[];
  narrative_template: string;
}
```

---

## 15. API Payloads

### 15.1 Score Request/Response

```typescript
interface ScoreRequest {
  student_profile: StudentProfile;
  school_configs: SchoolConfig[];
}

interface ScoreResponse {
  assessment_results: AssessmentResults;
  booster_recommendations: BoosterRecommendations;
  twin_fleet: TwinFleet;
}
```

### 15.2 Assessment Results

```typescript
interface AssessmentResults {
  ivy_ready_score: IvyReadyScore;
  school_probabilities: SchoolProbability[];

  helping_factors: string[];                 // Green bullets
  holding_back_factors: string[];            // Amber bullets

  archetype_detected: ArchetypeID;
  archetype_label: string;
  narrative_tagline: string;
}
```

---

## 16. File Locations

```
/Users/snazir/ivyquest-claude-v2.2/
├── lib/
│   ├── types/
│   │   ├── student.ts              # All 58 attributes + scoring types
│   │   ├── frame3.types.ts         # Frame 3 specific types
│   │   ├── frame4.types.ts         # Frame 4 specific types
│   │   └── frame5.types.ts         # Frame 5 specific types
│   │
│   ├── store/
│   │   ├── index.ts                # Export barrel
│   │   ├── useStudentStore.ts      # Main profile store
│   │   ├── useSessionStore.ts      # Navigation store
│   │   ├── useInsightsStore.ts     # Real-time insights
│   │   ├── useFrame3Store.ts       # Frame 3 quiz state
│   │   ├── useFrame4Store.ts       # Score display state
│   │   ├── useFrame5Store.ts       # Booster selection
│   │   ├── useResultsStore.ts      # Final results
│   │   ├── useUIStore.ts           # UI state
│   │   └── useTwinStore.ts         # Digital twin state
│   │
│   ├── constants/
│   │   ├── defaults.ts             # All centralized defaults
│   │   ├── brand.ts                # Brand colors & styles
│   │   ├── frame3.constants.ts     # Frame 3 scenarios
│   │   ├── frame4.constants.ts     # Score tiers & schools
│   │   ├── frame5.constants.ts     # Booster definitions
│   │   ├── droneMessages.ts        # Insight messages
│   │   └── ivylevelDesign.ts       # Design system
│   │
│   ├── gamePlan/
│   │   └── gamePlanEngine.ts       # Action plan generation
│   │
│   └── insights/
│       ├── generators/             # Insight generators
│       ├── loadingInsights.ts      # Loading state insights
│       └── realtimeInsights.ts     # Real-time insight logic
│
├── docs/
│   ├── DATABASE_SPEC.md            # This document
│   ├── TECHNICAL_REPORT_Dec18.md   # Bug fixes report
│   └── MASTER_SPEC.md              # System specification
```

---

## Appendix A: Data Research Sources

| Source | Data Used | Citation |
|--------|-----------|----------|
| Chetty 2023 | Legacy/Athlete multipliers | "Diversifying Society's Leaders" |
| SFFA v. Harvard | Rubric ratings (1-6) | Trial documents |
| Common Data Set 2025 | Acceptance rates, SAT ranges | CDS filings |
| NSC | High school saturation data | National Student Clearinghouse |

---

## Appendix B: Validation Rules

```typescript
// Required for valid profile
const REQUIRED_FIELDS = [
  'identity.role',
  'identity.grade',
];

// Validation bounds
const BOUNDS = {
  gpa_weighted: [0, 5.0],
  gpa_unweighted: [0, 4.0],
  sat_total: [400, 1600],
  act_total: [1, 36],
  ap_count: [0, 20],
  ap_avg_score: [1, 5],
  ec_commitment_years: [0, 10],
  ec_hours_weekly: [0, 40],
  service_hours: [0, 2000],
  project_impact: [0, 100000],
};

// Probability cap
const MAX_PROBABILITY = 0.95;  // Never show 100%
```

---

**Document End**

*This specification is the single source of truth for the IvyQuest data model. All implementations should reference these definitions for consistency and correctness.*
