# IvyQuest Scoring Engine Specification

> **Version**: 1.0.0
> **Last Updated**: 2025-12-22
> **Status**: AUTHORITATIVE

---

## Table of Contents

1. [Overview](#1-overview)
2. [Data Structures](#2-data-structures)
3. [Normalization Functions](#3-normalization-functions)
4. [Category Score Calculations](#4-category-score-calculations)
5. [Ivy+ Ready Score](#5-ivy-ready-score)
6. [SFFA Rubric System](#6-sffa-rubric-system)
7. [Probability Calculations](#7-probability-calculations)
8. [Chetty 2023 Context Multipliers](#8-chetty-2023-context-multipliers)
9. [School Configuration Database](#9-school-configuration-database)
10. [Archetype Detection System](#10-archetype-detection-system)
11. [Factor Analysis System](#11-factor-analysis-system)
12. [Sample Calculations](#12-sample-calculations)
13. [Constants & Defaults Reference](#13-constants--defaults-reference)

---

## 1. Overview

### 1.1 Scoring Philosophy

The IvyQuest scoring engine implements a multi-layered assessment system based on:

1. **Chetty et al. (2023)**: "Diversifying Society's Leaders?" - Opportunity Insights research on elite college admissions
2. **SFFA v. Harvard**: 1-6 rubric scale used in holistic review
3. **CDS 2025**: Common Data Set admission statistics
4. **NSC Data**: National Student Clearinghouse saturation data

### 1.2 Scoring Layers

```
Layer 1: Attribute Normalization (0.0-1.0)
    ↓
Layer 2: Category Scores (0-100%)
    ↓
Layer 3: Ivy+ Ready Score (0-100)
    ↓
Layer 4: SFFA Rubric (1-6 scale)
    ↓
Layer 5: Base Probability (Sigmoid)
    ↓
Layer 6: Context Multipliers (Chetty)
    ↓
Layer 7: Final Probability (Capped 95%)
```

### 1.3 Key Formulas

| Formula | Expression |
|---------|------------|
| Base Probability | `P_base = 1 / (1 + exp(-(0.05 * S - C_j)))` |
| Final Probability | `P_final = min(0.95, P_base × Π Multipliers)` |
| Ivy+ Ready Score | `Σ(Category_Score × Weight)` |

---

## 2. Data Structures

### 2.1 StudentProfile

```typescript
interface StudentProfile {
  // Identity
  identity: {
    grade: string;           // "9" | "10" | "11" | "12"
    first_name?: string;
    school_type?: string;    // "PUBLIC" | "PRIVATE" | "CHARTER" | "MAGNET"
  };

  // Aptitude Attributes
  aptitude: AptitudeAttributes;

  // Passion/EC Attributes
  passion: PassionAttributes;

  // Community/Service Attributes
  community: CommunityAttributes;

  // Demographics
  demographics: {
    ethnicity: string | null;
    ethnicity_multiplier: number;    // 0.85 - 1.20
    first_gen: boolean;
    first_gen_multiplier: number;    // 1.0 or 1.15
    legacy: boolean;
    legacy_schools: string[];
    recruited_athlete: boolean;
    income_top_1_percent: boolean;
    income_multiplier: number;       // 1.0 or 1.20
  };

  // High School Context
  high_school?: {
    saturation_level: "LOW" | "MEDIUM" | "HIGH";
    saturation_adjustment: number;    // -0.08 to +0.05
    ivy_applicants_per_year: number;
  };

  // Major Selection
  intended_major: string;
  major_certainty?: "CERTAIN" | "LIKELY" | "EXPLORING";
  target_schools: string[];

  // Assessment Intelligence (Psychometrics)
  assessment_intelligence: {
    psychometrics: {
      vision_clarity?: number;       // 0.0-1.0
      identity_comfort?: number;
      articulation_ability?: number;
      maturity_level?: number;
      grit_resilience?: number;
      coachability_score?: number;
    };
  };
}
```

### 2.2 AptitudeAttributes

```typescript
interface AptitudeAttributes {
  // Raw Values
  gpa_weighted: number | null;       // 0.0-5.0
  gpa_unweighted?: number | null;    // 0.0-4.0
  sat_total: number | null;          // 400-1600
  act_total?: number | null;         // 1-36
  ap_count: number | null;           // 0-20+
  ap_avg_score: number | null;       // 1.0-5.0
  academic_awards: string[];         // Award names

  // Normalized Values (0.0-1.0)
  gpa_normalized?: number;
  sat_normalized?: number;
  rigor_normalized?: number;
  awards_normalized?: number;
}
```

### 2.3 PassionAttributes

```typescript
interface PassionAttributes {
  // Raw Values
  leadership_level: string | null;   // FOUNDER_NATIONAL, FOUNDER_STATE, STATE_PRES, SCHOOL_PRES, OFFICER, PARTICIPANT
  project_impact: number | null;     // People affected
  research_level: string | null;     // NATIONAL, STATE, SCHOOL, INDEPENDENT, NONE
  ec_commitment_years: number | null; // 1-4+
  ec_hours_weekly: number | null;    // 1-20+
  ec_awards: string[];

  // Normalized Values (0.0-1.0)
  leadership_normalized?: number;
  project_normalized?: number;
  research_normalized?: number;
  commitment_normalized?: number;
  ec_awards_normalized?: number;
}
```

### 2.4 CommunityAttributes

```typescript
interface CommunityAttributes {
  // Raw Values
  service_leadership: string | null;  // NATIONAL, REGIONAL, LOCAL, PARTICIPANT
  service_hours: number | null;       // Total by graduation
  community_impact: number | null;    // People affected

  // Normalized Values (0.0-1.0)
  service_normalized?: number;
  hours_normalized?: number;
  impact_normalized?: number;
}
```

---

## 3. Normalization Functions

All normalization functions convert raw values to a 0.0-1.0 scale for consistent scoring.

### 3.1 normalizeGPA()

**Input**: `gpa_weighted: number | null` (0.0-5.0)
**Output**: `number` (0.0-1.0)

**SFFA Rubric Mapping**:

| GPA Range | Normalized | SFFA Rating | Percentile |
|-----------|------------|-------------|------------|
| 4.0+ | 1.00 | 6 (Summa) | Top 1% |
| 3.85-3.99 | 0.80-0.99 | 5 (Magna) | Top 5% |
| 3.70-3.84 | 0.60-0.79 | 4 (Cum Laude) | Top 10% |
| 3.50-3.69 | 0.40-0.59 | 3 (Good) | Top 25% |
| 3.00-3.49 | 0.20-0.39 | 2 (Average) | Top 50% |
| <3.00 | 0.00-0.19 | 1 (Below) | Bottom 50% |

**Formula (Piecewise Linear)**:
```typescript
if (gpa >= 4.0) return 1.0;
if (gpa >= 3.85) return 0.80 + (gpa - 3.85) / 0.15 * 0.20;
if (gpa >= 3.70) return 0.60 + (gpa - 3.70) / 0.15 * 0.20;
if (gpa >= 3.50) return 0.40 + (gpa - 3.50) / 0.20 * 0.20;
if (gpa >= 3.00) return 0.20 + (gpa - 3.00) / 0.50 * 0.20;
return Math.max(0, (gpa - 2.0) / 1.0 * 0.20);
```

### 3.2 normalizeSAT()

**Input**: `sat_total: number | null` (400-1600)
**Output**: `number` (0.0-1.0)

**CollegeBoard 2025 Percentile Mapping**:

| SAT Range | Normalized | Percentile |
|-----------|------------|------------|
| 1600 | 1.00 | 99.9th |
| 1500-1599 | 0.85-0.99 | 99th |
| 1400-1499 | 0.70-0.84 | 95th |
| 1300-1399 | 0.55-0.69 | 87th |
| 1200-1299 | 0.40-0.54 | 76th |
| <1200 | 0.00-0.39 | <76th |

**Formula**:
```typescript
if (sat >= 1600) return 1.0;
if (sat >= 1500) return 0.85 + (sat - 1500) / 100 * 0.15;
if (sat >= 1400) return 0.70 + (sat - 1400) / 100 * 0.15;
if (sat >= 1300) return 0.55 + (sat - 1300) / 100 * 0.15;
if (sat >= 1200) return 0.40 + (sat - 1200) / 100 * 0.15;
return Math.max(0, (sat - 800) / 400 * 0.40);
```

### 3.3 normalizeRigor()

**Input**: `ap_count: number | null`, `ap_avg_score: number | null`
**Output**: `number` (0.0-1.0)

**Composition**: 60% AP Count + 40% AP Average Score

**AP Count Component**:

| AP Courses | Component Score |
|------------|-----------------|
| 11+ | 1.00 |
| 8-10 | 0.80 |
| 4-7 | 0.60 |
| 0-3 | 0.20 |

**AP Average Component**:

| Avg Score | Component Score |
|-----------|-----------------|
| 5.0 | 1.00 |
| 4.5-4.9 | 0.85 |
| 4.0-4.4 | 0.70 |
| <4.0 | 0.40 |
| (unknown) | 0.70 (default) |

**Formula**:
```typescript
const count_score = ap_count >= 11 ? 1.0 : ap_count >= 8 ? 0.80 : ap_count >= 4 ? 0.60 : 0.20;
const avg_score = ap_avg >= 5.0 ? 1.0 : ap_avg >= 4.5 ? 0.85 : ap_avg >= 4.0 ? 0.70 : 0.40;
return count_score * 0.60 + avg_score * 0.40;
```

### 3.4 normalizeLeadership()

**Input**: `level: string | null`
**Output**: `number` (0.0-1.0)

| Leadership Level | Normalized Score |
|------------------|------------------|
| FOUNDER_NATIONAL | 1.00 |
| FOUNDER_STATE | 0.85 |
| STATE_PRES | 0.75 |
| SCHOOL_PRES | 0.70 |
| OFFICER | 0.50 |
| PARTICIPANT | 0.25 |
| (null/empty) | 0.00 |

### 3.5 normalizeProjectImpact()

**Input**: `impact: number | null` (people affected)
**Output**: `number` (0.0-1.0)

| People Affected | Normalized Score | Category |
|-----------------|------------------|----------|
| 10,000+ | 1.00 | Viral impact |
| 1,000-9,999 | 0.85-0.99 | Significant reach |
| 200-999 | 0.60-0.84 | School-wide |
| 50-199 | 0.40-0.59 | Class-level |
| 10-49 | 0.20-0.39 | Small group |
| <10 | 0.00-0.19 | Minimal |

### 3.6 normalizeResearch()

**Input**: `level: string | null`
**Output**: `number` (0.0-1.0)

| Research Level | Normalized Score | Examples |
|----------------|------------------|----------|
| NATIONAL | 1.00 | Intel/Regeneron finalist, published paper |
| STATE | 0.75 | State science fair recognition |
| SCHOOL | 0.50 | School research program (e.g., COSMOS) |
| INDEPENDENT | 0.30 | Self-directed without recognition |
| NONE | 0.00 | No research experience |

### 3.7 normalizeECCommitment()

**Input**: `years: number | null`, `hours_weekly: number | null`
**Output**: `number` (0.0-1.0)

**Composition**: 60% Years + 40% Hours

| Years | Component | | Hours/Week | Component |
|-------|-----------||-|------------|-----------|
| 4+ | 1.00 | | 15+ | 1.00 |
| 3 | 0.75 | | 10-14 | 0.80 |
| 2 | 0.50 | | 5-9 | 0.60 |
| 1 | 0.25 | | 1-4 | 0.30 |

### 3.8 normalizeServiceLeadership()

**Input**: `level: string | null`
**Output**: `number` (0.0-1.0)

| Service Leadership | Normalized Score |
|--------------------|------------------|
| NATIONAL | 1.00 |
| REGIONAL | 0.75 |
| LOCAL | 0.60 |
| PARTICIPANT | 0.30 |

### 3.9 normalizeServiceHours()

**Input**: `hours: number | null` (total by graduation)
**Output**: `number` (0.0-1.0)

| Total Hours | Normalized Score |
|-------------|------------------|
| 500+ | 1.00 |
| 250-499 | 0.80-0.99 |
| 100-249 | 0.60-0.79 |
| 50-99 | 0.40-0.59 |
| <50 | 0.00-0.39 |

### 3.10 normalizeAcademicAwards()

**Input**: `awards: string[]`
**Output**: `number` (0.0-1.0) - Maximum of all awards

| Award Level | Normalized Score | Examples |
|-------------|------------------|----------|
| INTERNATIONAL | 1.00 | ISEF, IPhO, IMO, IOI |
| NATIONAL | 0.85 | USAMO, Regeneron, Intel finalist |
| STATE | 0.60 | State Science Olympiad |
| SCHOOL | 0.30 | AP Scholar, Honor Roll |
| Generic | 0.20 | Other awards |

---

## 4. Category Score Calculations

### 4.1 Aptitude Score (0-100)

**Weights**:
- GPA: 35%
- SAT: 30%
- Rigor: 20%
- Awards: 15%

**Formula**:
```typescript
aptitude_score = (
  gpa_normalized * 0.35 +
  sat_normalized * 0.30 +
  rigor_normalized * 0.20 +
  awards_normalized * 0.15
) * 100
```

**Defaults** (for missing data):
```typescript
NORMALIZED_DEFAULTS.aptitude = {
  gpa: 0.5,      // 3.3 GPA equivalent
  sat: 0.5,      // ~1300 SAT
  rigor: 0.4,    // 4-5 AP courses
  awards: 0.0,   // No awards (conservative)
}
```

### 4.2 Passion Score (0-100)

**Weights**:
- Leadership: 35%
- Projects: 20%
- Research: 20%
- EC Commitment: 15%
- Awards: 10%

**Formula**:
```typescript
passion_score = (
  leadership_normalized * 0.35 +
  project_normalized * 0.20 +
  research_normalized * 0.20 +
  commitment_normalized * 0.15 +
  ec_awards_normalized * 0.10
) * 100
```

**Defaults**:
```typescript
NORMALIZED_DEFAULTS.passion = {
  leadership: 0.25,    // Participant level
  project: 0.2,        // ~20 people impact
  research: 0.0,       // No research
  commitment: 0.5,     // 2 years, moderate hours
  awards: 0.0,
}
```

### 4.3 Community Score (0-100)

**Weights**:
- Service Leadership: 35%
- Impact: 35%
- Hours: 20%
- Description Quality: 10%

**Formula**:
```typescript
community_score = (
  service_normalized * 0.35 +
  impact_normalized * 0.35 +
  hours_normalized * 0.20 +
  description_quality * 0.10
) * 100
```

**Defaults**:
```typescript
NORMALIZED_DEFAULTS.community = {
  service: 0.3,      // Participant level
  hours: 0.4,        // ~75 hours
  impact: 0.2,       // Small local impact
}
```

### 4.4 Narrative Score (0-100) - Predicted

**Weights** (Psychometric Markers):
- Vision Clarity: 30%
- Identity Comfort: 25%
- Articulation: 25%
- Maturity: 20%

**Formula**:
```typescript
narrative_score = (
  vision_clarity * 0.30 +
  identity_comfort * 0.25 +
  articulation_ability * 0.25 +
  maturity_level * 0.20
) * 100
```

**Defaults**:
```typescript
NORMALIZED_DEFAULTS.narrative = {
  vision_clarity: 0.5,
  identity_comfort: 0.5,
  articulation: 0.5,
  maturity: 0.5,
}
```

---

## 5. Ivy+ Ready Score

### 5.1 Definition

The **Ivy+ Ready Score** is a school-agnostic metric (0-100) representing overall strength for elite college admissions. It focuses on **controllable factors** (not demographics).

### 5.2 Weights

| Category | Weight | Rationale |
|----------|--------|-----------|
| Aptitude | 30% | Academic foundation |
| Passion | 35% | Spike activities, leadership |
| Community | 25% | Service, social impact |
| Narrative | 10% | Essay/interview readiness |

### 5.3 Formula

```typescript
ivy_ready_score = (
  aptitude_score * 0.30 +
  passion_score * 0.35 +
  community_score * 0.25 +
  narrative_score * 0.10
)
```

### 5.4 Percentile Estimation

Based on Chetty 2023 applicant pool data:
- Median Ivy applicant: ~55
- Median admit: ~75

```typescript
percentile_rank = min(99, max(1,
  (total_score - 40) / (90 - 40) * 90 + 5
))
```

---

## 6. SFFA Rubric System

### 6.1 Overview

The SFFA (Students for Fair Admissions v. Harvard) rubric uses a **1-6 scale** across five dimensions:

| Rating | Meaning | Percentile |
|--------|---------|------------|
| 6 | Exceptional (Summa) | Top 1% |
| 5 | Very Strong (Magna) | Top 5% |
| 4 | Strong (Cum Laude) | Top 10% |
| 3 | Good | Top 25% |
| 2 | Average | Top 50% |
| 1 | Below Average | Bottom 50% |

### 6.2 Rating Calculations

**Academic Rating**:
```typescript
academic_rating = ceil(aptitude_score / 100 * 6)  // 1-6
```

**Extracurricular Rating**:
```typescript
extracurricular_rating = ceil(passion_score / 100 * 6)  // 1-6
```

**Athletic Rating**:
```typescript
athletic_rating = recruited_athlete ? 5 : 3  // Default 3
```

**Personal Rating**:
```typescript
personal_composite = community_score * 0.60 + coachability * 100 * 0.40
personal_rating = ceil(personal_composite / 100 * 6)  // 1-6
```

**Overall Rating**:
```typescript
overall_composite = (
  academic_rating * 0.30 +
  extracurricular_rating * 0.35 +
  athletic_rating * 0.10 +
  personal_rating * 0.25
)
overall_rating = round(overall_composite)  // 1-6
```

### 6.3 Rubric to Composite Score

Converts 1-6 rubric to 0-100 for probability calculations:

```typescript
rubric_composite = ((overall_rating - 1) / 5) * 100
```

| Overall Rating | Composite Score |
|----------------|-----------------|
| 6 | 100 |
| 5 | 80 |
| 4 | 60 |
| 3 | 40 |
| 2 | 20 |
| 1 | 0 |

---

## 7. Probability Calculations

### 7.1 Sigmoid Base Probability

**Formula**:
```
P_base = 1 / (1 + exp(-(0.05 * S - C_j)))
```

Where:
- `S` = Rubric composite score (0-100)
- `C_j` = School-specific threshold constant

### 7.2 School Threshold Constants (C_j)

Calibrated to CDS 2025 base acceptance rates:

| School | Base Rate | C_j Threshold |
|--------|-----------|---------------|
| Stanford | 3.9% | 3.2 |
| Harvard | 4.2% | 3.1 |
| Columbia | 4.8% | 3.0 |
| Yale | 5.1% | 2.95 |
| MIT | 5.7% | 2.8 |
| Princeton | 5.8% | 2.75 |
| Caltech | 6.4% | 2.6 |
| CMU | 11.0% | 2.2 |

### 7.3 Final Probability

**Formula**:
```
P_final = min(0.95, P_base × Π Multipliers)
```

**Cap at 95%**: No certainty in admissions (per specification).

---

## 8. Chetty 2023 Context Multipliers

### 8.1 Source

Chetty et al. (2023): "Diversifying Society's Leaders? The Causal Effects of Admission to Highly Selective Private Colleges" - Opportunity Insights Research

### 8.2 Legacy Multipliers (School-Specific)

| School | Legacy Multiplier | Note |
|--------|-------------------|------|
| Harvard | 5.0x | Chetty finding: legacy = 5x odds |
| Yale | 5.0x | Same as Harvard |
| Princeton | 5.0x | Same as Harvard |
| Columbia | 4.5x | Slightly lower |
| Stanford | 4.0x | Lower than Ivies |
| CMU | 2.0x | Moderate |
| MIT | 0.0x | **Pure meritocracy** - no legacy advantage |
| Caltech | 0.0x | **Pure meritocracy** - no legacy advantage |

### 8.3 Universal Multipliers

| Factor | Multiplier | Condition |
|--------|------------|-----------|
| First-Gen | 1.15x | First generation college student |
| Income Top 1% | 1.20x | Family in top 1% income (network effect) |

### 8.4 Recruited Athlete Multipliers

| School | Athlete Multiplier |
|--------|-------------------|
| Harvard, Yale, Princeton, Stanford | 2.5x |
| Columbia | 2.0x |
| MIT, CMU | 1.5x |
| Caltech | 1.0x (no advantage) |

### 8.5 Ethnicity Multipliers (SFFA Context)

| Ethnicity Context | Multiplier | Notes |
|-------------------|------------|-------|
| Asian (STEM + Saturated Region) | 0.85x | Bay Area + CS/Engineering |
| Asian (Non-STEM) | 0.95x | Humanities, Social Sciences |
| Black (URM) | 1.15x | Underrepresented |
| Hispanic (URM) | 1.15x | Underrepresented |
| Native American | 1.20x | Most underrepresented |
| Pacific Islander | 1.05x | |
| White | 1.00x | Baseline |
| Multiracial | 1.00x | Baseline |

### 8.6 Region Multipliers

| Region | Multiplier | Notes |
|--------|------------|-------|
| Bay Area | 0.90x | Most competitive tech hub |
| Northeast | 0.95x | Traditional feeder region |
| Midwest | 1.05x | Geographic diversity value |
| South | 1.05x | Geographic diversity value |
| Southwest | 1.03x | |
| Northwest | 1.02x | |
| International | 0.80x | Most competitive pool |

### 8.7 High School Saturation

Based on NSC (National Student Clearinghouse) data:

| Saturation Level | Adjustment | Ivy Apps/Year |
|------------------|------------|---------------|
| LOW | +0.05 | <10 |
| MEDIUM | 0.00 | 10-50 |
| HIGH | -0.08 | 50+ |

### 8.8 Major Multipliers (School-Specific)

**Stanford CS Example**:

| Major | Multiplier | Strategy |
|-------|------------|----------|
| Computer Science | 0.55x | Most competitive |
| Engineering | 0.65x | Very competitive |
| Symbolic Systems | 1.20x | Strategic alternative |
| Product Design | 1.10x | Strategic alternative |

**CMU SCS Example**:

| Major | Multiplier |
|-------|------------|
| Computer Science (SCS) | 0.50x |
| Engineering | 0.70x |
| Drama | 1.30x |

### 8.9 Multiplier Application

```typescript
function calculateContextMultipliers(profile, school_config): number {
  let multiplier = 1.0;

  // Legacy (school-specific)
  if (profile.demographics.legacy &&
      profile.demographics.legacy_schools.includes(school_config.school_id)) {
    multiplier *= school_config.legacy_roi;
  }

  // First-Gen (universal)
  if (profile.demographics.first_gen) {
    multiplier *= 1.15;
  }

  // Recruited Athlete
  if (profile.demographics.recruited_athlete) {
    multiplier *= school_config.athlete_roi;
  }

  // Ethnicity
  multiplier *= profile.demographics.ethnicity_multiplier;

  // Income Top 1%
  if (profile.demographics.income_top_1_percent) {
    multiplier *= 1.20;
  }

  // High School Saturation
  if (profile.high_school) {
    multiplier *= (1 + profile.high_school.saturation_adjustment);
  }

  // Major
  const major_mult = school_config.major_multipliers[profile.intended_major] ?? 1.0;
  multiplier *= major_mult;

  return multiplier;
}
```

---

## 9. School Configuration Database

### 9.1 Harvard University

```typescript
{
  school_id: 'HARVARD',
  school_name: 'Harvard University',
  base_acceptance_rate: 0.042,       // 4.2%
  base_sat_50th: 1520,
  weight_aptitude: 30,
  weight_passion: 35,
  weight_community: 25,
  weight_narrative: 10,
  distinctive_values: ['LEADERSHIP', 'GLOBAL_IMPACT', 'EXCELLENCE'],
  legacy_roi: 5.0,
  first_gen_roi: 1.15,
  athlete_roi: 2.5,
  major_multipliers: {
    'Computer Science': 0.70,
    'Economics': 0.75,
    'Government': 1.0,
    'Biology': 0.80,
    'Mathematics': 0.85,
  },
}
```

### 9.2 Stanford University

```typescript
{
  school_id: 'STANFORD',
  base_acceptance_rate: 0.039,       // 3.9% (lowest)
  base_sat_50th: 1510,
  weight_aptitude: 25,
  weight_passion: 45,               // Highest passion weight
  weight_community: 20,
  weight_narrative: 10,
  distinctive_values: ['ENTREPRENEURSHIP', 'INNOVATION', 'INTELLECTUAL_VITALITY'],
  legacy_roi: 4.0,
  athlete_roi: 2.5,
  major_multipliers: {
    'Computer Science': 0.55,       // Most competitive
    'Symbolic Systems': 1.20,       // Strategic alternative
    'Engineering': 0.65,
    'Product Design': 1.10,
  },
}
```

### 9.3 MIT

```typescript
{
  school_id: 'MIT',
  base_acceptance_rate: 0.057,       // 5.7%
  base_sat_50th: 1540,
  weight_aptitude: 40,               // Highest aptitude
  weight_passion: 40,                // Maker culture
  weight_community: 10,              // Lowest community
  weight_narrative: 10,
  distinctive_values: ['TECH_MERITOCRACY', 'MAKER_CULTURE', 'STEM_EXCELLENCE'],
  legacy_roi: 0.0,                   // PURE MERITOCRACY
  athlete_roi: 1.5,
  major_multipliers: {
    'Computer Science': 0.70,
    'Engineering': 0.75,
    'Physics': 0.90,
  },
}
```

### 9.4 Yale University

```typescript
{
  school_id: 'YALE',
  base_acceptance_rate: 0.051,       // 5.1%
  base_sat_50th: 1515,
  weight_aptitude: 28,
  weight_passion: 32,
  weight_community: 30,              // Highest community weight
  weight_narrative: 10,
  distinctive_values: ['COMMUNITY', 'LIBERAL_ARTS', 'SERVICE_LEADERSHIP'],
  legacy_roi: 5.0,
  major_multipliers: {
    'Political Science': 1.10,
    'English': 1.05,
    'Computer Science': 0.75,
  },
}
```

### 9.5 Princeton University

```typescript
{
  school_id: 'PRINCETON',
  base_acceptance_rate: 0.058,       // 5.8%
  base_sat_50th: 1530,
  weight_aptitude: 35,
  weight_passion: 35,
  weight_community: 20,
  weight_narrative: 10,
  distinctive_values: ['ACADEMIC_EXCELLENCE', 'RESEARCH', 'UNDERGRADUATE_FOCUS'],
  legacy_roi: 5.0,
  major_multipliers: {
    'Physics': 1.05,
    'Computer Science': 0.70,
    'Economics': 0.80,
  },
}
```

### 9.6 Caltech

```typescript
{
  school_id: 'CALTECH',
  base_acceptance_rate: 0.064,       // 6.4%
  base_sat_50th: 1560,               // Highest median SAT
  weight_aptitude: 50,               // Highest aptitude emphasis
  weight_passion: 35,
  weight_community: 5,               // Lowest community
  weight_narrative: 10,
  distinctive_values: ['RESEARCH_EXCELLENCE', 'PURE_STEM', 'ACADEMIC_RIGOR'],
  legacy_roi: 0.0,                   // PURE MERITOCRACY
  athlete_roi: 1.0,                  // No athletic advantage
  major_multipliers: {
    'Physics': 1.0,
    'Mathematics': 1.0,
    'Computer Science': 0.80,
  },
}
```

### 9.7 CMU

```typescript
{
  school_id: 'CMU',
  base_acceptance_rate: 0.110,       // 11%
  base_sat_50th: 1500,
  weight_aptitude: 35,
  weight_passion: 40,
  weight_community: 15,
  weight_narrative: 10,
  distinctive_values: ['CS_EXCELLENCE', 'INTERDISCIPLINARY', 'MAKER_CULTURE'],
  legacy_roi: 2.0,
  major_multipliers: {
    'Computer Science': 0.50,        // SCS most competitive
    'Drama': 1.30,                   // Less competitive school
    'Design': 1.00,
  },
}
```

### 9.8 Columbia University

```typescript
{
  school_id: 'COLUMBIA',
  base_acceptance_rate: 0.048,       // 4.8%
  base_sat_50th: 1510,
  weight_aptitude: 32,
  weight_passion: 33,
  weight_community: 25,
  weight_narrative: 10,
  distinctive_values: ['URBAN', 'CORE_CURRICULUM', 'GLOBAL'],
  legacy_roi: 4.5,
  major_multipliers: {
    'Computer Science': 0.68,
    'Economics': 0.75,
    'Political Science': 1.0,
  },
}
```

---

## 10. Archetype Detection System

### 10.1 Archetype Definitions

| Archetype ID | Label | Tagline |
|--------------|-------|---------|
| SCHOLAR | The Scholar | Excellence through intellectual mastery |
| RESEARCHER | The Researcher | Driven by curiosity and discovery |
| LEADER | The Leader | Inspiring others to achieve together |
| ENTREPRENEUR | The Entrepreneur | Creating solutions that matter |
| CHANGEMAKER | The Changemaker | Transforming communities through action |
| ADVOCATE | The Advocate | Voice for those who need one |
| CREATOR | The Creator | Building what others only imagine |
| PERFORMER | The Performer | Excellence on every stage |
| POLYMATH | The Polymath | Excellence without boundaries |
| EMERGING | The Emerging Talent | Potential waiting to be unlocked |
| EXPLORER | The Explorer | Finding your unique path |

### 10.2 Detection Algorithm

Each archetype has a `matchScore()` function that returns 0-100 based on profile characteristics:

**SCHOLAR Detection**:
```typescript
matchScore: (p, scores) => {
  let score = 0;
  if (scores.aptitude >= 70) score += 40;
  else if (scores.aptitude >= 50) score += 20;
  if ((p.aptitude.gpa_normalized ?? 0) >= 0.80) score += 20;
  if ((p.aptitude.rigor_normalized ?? 0) >= 0.70) score += 20;
  if (p.passion.research_level !== 'NONE') score += 15;
  if (scores.aptitude > scores.passion && scores.aptitude > scores.community) score += 10;
  return score;
}
```

**ENTREPRENEUR Detection**:
```typescript
matchScore: (p, scores) => {
  let score = 0;
  if (p.passion.leadership_level?.includes('FOUNDER')) score += 45;
  if ((p.passion.project_impact ?? 0) >= 500) score += 25;
  else if ((p.passion.project_impact ?? 0) >= 100) score += 15;
  const bizMajors = ['Business', 'Economics', 'Computer Science', 'Engineering'];
  if (bizMajors.includes(p.intended_major ?? '')) score += 15;
  if (scores.passion > scores.aptitude) score += 10;
  return score;
}
```

**POLYMATH Detection** (Balanced Excellence):
```typescript
matchScore: (_, scores) => {
  let score = 0;
  const allAbove50 = scores.aptitude >= 50 && scores.passion >= 50 && scores.community >= 50;
  if (allAbove50) score += 40;
  const max = Math.max(scores.aptitude, scores.passion, scores.community);
  const min = Math.min(scores.aptitude, scores.passion, scores.community);
  if (max - min <= 20) score += 25;  // Balanced
  const avg = (scores.aptitude + scores.passion + scores.community) / 3;
  if (avg >= 55) score += 20;
  return score;
}
```

### 10.3 Result Structure

```typescript
interface ArchetypeResult {
  id: ArchetypeID;           // Primary archetype
  label: string;
  tagline: string;
  confidence: number;         // 0-100
  alternates: Array<{         // Top 2 alternatives
    id: ArchetypeID;
    label: string;
    confidence: number;
  }>;
}
```

---

## 11. Factor Analysis System

### 11.1 Helping Factors (Strengths)

**Tier 1 - Exceptional (Priority 90-100)**:

| Factor ID | Threshold | Example Message |
|-----------|-----------|-----------------|
| perfect_gpa | gpa_normalized >= 0.95 | "Perfect GPA (4.0) — top 1%" |
| elite_sat | sat_normalized >= 0.90 | "Elite SAT (1580) — 99th percentile" |
| national_research | research_level == 'NATIONAL' | "National-level research — Regeneron caliber" |
| founder_leadership | leadership includes 'FOUNDER' | "Founded organization — entrepreneurial spike" |

**Tier 2 - Strong (Priority 40-70)**:

| Factor ID | Threshold | Example Message |
|-----------|-----------|-----------------|
| strong_gpa | gpa_normalized >= 0.65 | "Strong GPA (3.85) — competitive" |
| strong_sat | sat_normalized >= 0.65 | "Strong SAT (1450) — above Ivy median" |
| strong_rigor | rigor_normalized >= 0.60 | "Solid AP rigor (8 courses)" |
| leadership_role | leadership_normalized >= 0.50 | "Leadership experience (OFFICER)" |
| long_commitment | ec_commitment_years >= 3 | "3+ years EC commitment — depth" |
| high_grit | grit_resilience >= 0.60 | "High resilience score" |

**Tier 3 - Baseline (Priority 1-20)**:

| Factor ID | Threshold | Example Message |
|-----------|-----------|-----------------|
| has_gpa | gpa_normalized > 0.3 | "Maintaining 3.2 GPA — foundation" |
| has_ecs | ec_commitment_years >= 1 | "Active in extracurriculars" |
| taking_assessment | always true | "Taking initiative — growth mindset" |

### 11.2 Holding Back Factors (Gaps)

**Critical (Priority 60-80)**:

| Factor ID | Threshold | Example Message |
|-----------|-----------|-----------------|
| no_awards | awards_normalized < 0.10 | "No academic awards — 15% weight unfilled" |
| low_project_impact | project_normalized < 0.30 | "Low project impact (20 people) — aim for 200+" |
| weak_community | community_score < 40 | "Community score 35% — leadership gap" |
| no_research | research_level == 'NONE' | "No research — consider summer programs" |
| low_leadership | leadership == 'PARTICIPANT' | "Participant-level only — seek officer roles" |

**Competitive Context (Priority 45-55)**:

| Factor ID | Threshold | Example Message |
|-----------|-----------|-----------------|
| cs_penalty | major in [CS, Engineering] | "CS is highly competitive (0.55-0.70x)" |
| high_saturation | saturation_level == 'HIGH' | "Competitive high school — need differentiation" |

**Moderate (Priority 35-40)**:

| Factor ID | Threshold | Example Message |
|-----------|-----------|-----------------|
| moderate_gpa | gpa_normalized < 0.40 | "GPA below Ivy median — focus on upward trend" |
| short_commitment | ec_commitment_years < 2 | "Short EC history — depth matters" |

### 11.3 Factor Thresholds

```typescript
FACTOR_THRESHOLDS = {
  strong: {
    gpa_normalized: 0.65,       // Top 35%
    sat_normalized: 0.65,
    rigor_normalized: 0.60,
    leadership_normalized: 0.50,
    project_normalized: 0.40,
    research_normalized: 0.50,
    commitment_normalized: 0.60,
    service_normalized: 0.50,
    hours_normalized: 0.50,
    grit: 0.60,
    category_score: 50,
  },
  weak: {
    gpa_normalized: 0.40,       // Bottom 40%
    sat_normalized: 0.40,
    rigor_normalized: 0.35,
    awards_normalized: 0.10,
    project_normalized: 0.30,
    service_normalized: 0.25,
    category_score: 40,
  },
}
```

---

## 12. Sample Calculations

### 12.1 Sample Profile: "High-Achieving STEM Student"

**Raw Data**:
```typescript
{
  aptitude: {
    gpa_weighted: 4.2,
    sat_total: 1540,
    ap_count: 10,
    ap_avg_score: 4.5,
    academic_awards: ['STATE Science Olympiad'],
  },
  passion: {
    leadership_level: 'OFFICER',
    project_impact: 150,
    research_level: 'SCHOOL',
    ec_commitment_years: 3,
    ec_hours_weekly: 12,
  },
  community: {
    service_leadership: 'LOCAL',
    service_hours: 120,
    community_impact: 50,
  },
  demographics: {
    first_gen: false,
    legacy: false,
    recruited_athlete: false,
  },
  intended_major: 'Computer Science',
}
```

**Step 1: Normalization**

| Attribute | Raw Value | Formula | Normalized |
|-----------|-----------|---------|------------|
| GPA | 4.2 | gpa >= 4.0 → 1.0 | **1.00** |
| SAT | 1540 | 0.85 + (40/100) * 0.15 | **0.91** |
| Rigor | 10 APs, 4.5 avg | 0.80 * 0.60 + 0.85 * 0.40 | **0.82** |
| Awards | STATE | max([0.60]) | **0.60** |
| Leadership | OFFICER | mapping | **0.50** |
| Project | 150 people | 0.40 + (100/150) * 0.20 | **0.53** |
| Research | SCHOOL | mapping | **0.50** |
| Commitment | 3 yr, 12 hr | 0.75 * 0.60 + 0.80 * 0.40 | **0.77** |
| Service | LOCAL | mapping | **0.60** |
| Hours | 120 | 0.60 + (20/150) * 0.20 | **0.63** |
| Impact | 50 | 0.40 + 0 | **0.40** |

**Step 2: Category Scores**

**Aptitude**:
```
= (1.00 * 0.35) + (0.91 * 0.30) + (0.82 * 0.20) + (0.60 * 0.15)
= 0.35 + 0.273 + 0.164 + 0.09
= 0.877 → 88%
```

**Passion**:
```
= (0.50 * 0.35) + (0.53 * 0.20) + (0.50 * 0.20) + (0.77 * 0.15) + (0 * 0.10)
= 0.175 + 0.106 + 0.10 + 0.116 + 0
= 0.497 → 50%
```

**Community**:
```
= (0.60 * 0.35) + (0.40 * 0.35) + (0.63 * 0.20) + (0.50 * 0.10)
= 0.21 + 0.14 + 0.126 + 0.05
= 0.526 → 53%
```

**Narrative** (using defaults):
```
= (0.50 * 0.30) + (0.50 * 0.25) + (0.50 * 0.25) + (0.50 * 0.20)
= 0.50 → 50%
```

**Step 3: Ivy+ Ready Score**

```
= (88 * 0.30) + (50 * 0.35) + (53 * 0.25) + (50 * 0.10)
= 26.4 + 17.5 + 13.25 + 5.0
= 62.15 → 62
```

**Step 4: SFFA Rubric**

| Dimension | Score | Rating (ceil/6) |
|-----------|-------|-----------------|
| Academic | 88 | 6 |
| Extracurricular | 50 | 3 |
| Athletic | - | 3 (default) |
| Personal | 53 | 4 |
| **Overall** | - | **4** (weighted avg) |

**Rubric Composite**: `(4 - 1) / 5 * 100 = 60`

**Step 5: Probability (Stanford Example)**

```
P_base = 1 / (1 + exp(-(0.05 * 60 - 3.2)))
       = 1 / (1 + exp(-(3.0 - 3.2)))
       = 1 / (1 + exp(0.2))
       = 1 / (1 + 1.22)
       = 0.45 (45%)

Multiplier (CS penalty) = 0.55

P_final = min(0.95, 0.45 * 0.55)
        = 0.248 → 24.8%
```

**Step 6: Results**

| School | Base Rate | P_final | Fit Level |
|--------|-----------|---------|-----------|
| Stanford | 3.9% | 24.8% | BEST_FIT |
| Harvard | 4.2% | 31.0% | BEST_FIT |
| MIT | 5.7% | 28.7% | BEST_FIT |

**Archetype**: SCHOLAR (aptitude dominant)
**Helping Factors**: Perfect GPA, Elite SAT, Strong rigor
**Holding Back**: Low project impact, No research recognition, CS penalty

---

### 12.2 Sample Profile: "Community-Focused Leader"

**Raw Data**:
```typescript
{
  aptitude: {
    gpa_weighted: 3.7,
    sat_total: 1380,
    ap_count: 6,
    ap_avg_score: 4.0,
    academic_awards: [],
  },
  passion: {
    leadership_level: 'FOUNDER_STATE',
    project_impact: 800,
    research_level: 'NONE',
    ec_commitment_years: 4,
    ec_hours_weekly: 20,
  },
  community: {
    service_leadership: 'REGIONAL',
    service_hours: 300,
    community_impact: 500,
  },
  demographics: {
    first_gen: true,
    legacy: false,
    recruited_athlete: false,
  },
  intended_major: 'Political Science',
}
```

**Normalized Values**:

| Attribute | Normalized |
|-----------|------------|
| GPA | 0.60 |
| SAT | 0.61 |
| Rigor | 0.64 |
| Awards | 0.00 |
| Leadership | 0.85 |
| Project | 0.69 |
| Research | 0.00 |
| Commitment | 1.00 |
| Service | 0.75 |
| Hours | 0.84 |
| Impact | 0.69 |

**Category Scores**:

| Category | Score |
|----------|-------|
| Aptitude | 51% |
| Passion | 60% |
| Community | 76% |
| Narrative | 50% |

**Ivy+ Ready Score**: 59

**SFFA Rubric**:
- Academic: 4
- Extracurricular: 4
- Personal: 5
- **Overall: 4**

**Probability (Yale - emphasizes community)**:

```
Rubric Composite = 60
P_base = 1 / (1 + exp(-(0.05 * 60 - 2.95))) = 0.51

Multipliers:
- First-gen: 1.15
- Political Science at Yale: 1.10
- Total: 1.265

P_final = min(0.95, 0.51 * 1.265) = 0.645 → 64.5%
```

**Archetype**: CHANGEMAKER (community dominant, high service leadership)

---

## 13. Constants & Defaults Reference

### 13.1 Normalized Defaults

```typescript
NORMALIZED_DEFAULTS = {
  aptitude: {
    gpa: 0.5,      // 3.3 GPA
    sat: 0.5,      // ~1300 SAT
    rigor: 0.4,    // 4-5 APs
    awards: 0.0,
  },
  passion: {
    leadership: 0.25,
    project: 0.2,
    research: 0.0,
    commitment: 0.5,
    awards: 0.0,
  },
  community: {
    service: 0.3,
    hours: 0.4,
    impact: 0.2,
  },
  narrative: {
    vision_clarity: 0.5,
    identity_comfort: 0.5,
    articulation: 0.5,
    maturity: 0.5,
    grit: 0.5,
    coachability: 0.5,
    description_quality: 0.5,
  },
}
```

### 13.2 Category Weights

```typescript
CATEGORY_WEIGHTS = {
  aptitude: { gpa: 0.35, sat: 0.30, rigor: 0.20, awards: 0.15 },
  passion: { leadership: 0.35, project: 0.20, research: 0.20, commitment: 0.15, awards: 0.10 },
  community: { service: 0.35, impact: 0.35, hours: 0.20, description: 0.10 },
  narrative: { vision: 0.30, identity: 0.25, articulation: 0.25, maturity: 0.20 },
  overall: { aptitude: 0.30, passion: 0.35, community: 0.25, narrative: 0.10 },
}
```

### 13.3 Validation Bounds

```typescript
VALIDATION_BOUNDS = {
  normalized: { min: 0.0, max: 1.0 },
  percentageScore: { min: 0, max: 100 },
  probability: { min: 0.0, max: 0.95 },  // Capped at 95%
  rubricRating: { min: 1, max: 6 },
  gpa: { min: 0.0, max: 5.0 },
  sat: { min: 400, max: 1600 },
  act: { min: 1, max: 36 },
}
```

### 13.4 Default Target Schools

```typescript
DEFAULT_TARGET_SCHOOLS = [
  'HARVARD', 'STANFORD', 'MIT', 'YALE',
  'PRINCETON', 'CALTECH', 'CMU', 'COLUMBIA'
]
```

---

## Appendix A: File Reference

| File | Purpose |
|------|---------|
| `lib/scoring/engine.ts` | Core scoring calculations |
| `lib/scoring/archetypeDetector.ts` | Archetype detection system |
| `lib/scoring/factorAnalysis.ts` | Helping/holding back analysis |
| `lib/data/schools.ts` | School configurations |
| `lib/data/chetty-roi.ts` | Chetty research multipliers |
| `lib/constants/defaults.ts` | Centralized defaults |
| `lib/utils/safeValue.ts` | Safe value utilities |
| `lib/types/student.ts` | TypeScript interfaces |

---

*This specification is authoritative for all scoring-related implementations. Updates require documentation review.*
