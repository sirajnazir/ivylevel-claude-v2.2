# Data Discovery Report - Handover v1.0

**Document Version**: 1.0
**Date**: January 2026
**Purpose**: Comprehensive analysis of existing seed data vs v1.0 Jenny Intelligence schema requirements

---

## Executive Summary

| Dataset | Count | Schema Completeness | Jenny Intelligence | Gap Status |
|---------|-------|---------------------|-------------------|------------|
| **Awards** | 97 | 85% core fields | **0% present** | Critical |
| **Opportunities** | 58 | 90% core fields | **0% present** | Critical |

**Key Finding**: The existing seed data has excellent structural foundation but **ZERO Jenny Intelligence fields** that the v1.0 specification requires for TYPE-014/TYPE-029 intelligence-driven recommendations.

---

## Part 1: Awards Data Analysis

### 1.1 Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Awards** | 97 |
| **Categories** | 10 (STEM, Humanities, Arts, Leadership, Service, Academic, Debate, Entrepreneurship, Journalism, Research) |
| **Levels** | 5 (National: 71, State: 12, International: 8, Regional: 3, Local: 3) |

### 1.2 Category Distribution

```
Category          Count   Percentage
---------------------------------
STEM              20      20.6%
Academic          13      13.4%
Leadership        13      13.4%
Humanities        12      12.4%
Arts              12      12.4%
Entrepreneurship  10      10.3%
Service            6       6.2%
Debate             5       5.2%
Research           3       3.1%
Journalism         3       3.1%
```

### 1.3 Current Schema - Field Presence

| Field | Present | Percentage | Notes |
|-------|---------|------------|-------|
| `id` | 97 | 100% | Unique identifier |
| `name` | 97 | 100% | Award name |
| `organization` | 97 | 100% | Sponsoring organization |
| `category` | 97 | 100% | Award category |
| `level` | 97 | 100% | national/state/regional/local |
| `description` | 97 | 100% | Brief description |
| `prestige_score` | 97 | 100% | 1-10 scale |
| `historical_win_rate` | 97 | 100% | 0.0-1.0 probability |
| `effort_hours` | 97 | 100% | Hours to prepare |
| `eligibility` | 97 | 100% | Eligibility criteria object |
| `eligibility.grades` | 97 | 100% | Eligible grade levels |
| `prize_type` | 97 | 100% | scholarship/recognition/cash |
| `diversity_focus` | 97 | 100% | Boolean |
| `touchpoints` | 97 | 100% | Number of touchpoints |
| `is_active` | 97 | 100% | Boolean (auto-added) |
| `deadline_month` | 92 | 95% | Application deadline month |
| `prize_amount` | 47 | 48% | Dollar amount if applicable |
| `touchpoint_types` | 12 | 12% | Array of touchpoint types |
| `deadline_recurring` | 11 | 11% | Recurring deadline string |
| `eligibility.citizenship` | 11 | 11% | Citizenship requirements |
| `eligibility.demographics` | 9 | 9% | Demographic targeting |
| `eligibility.requirements` | 5 | 5% | Specific requirements |
| `eligibility.gender` | 3 | 3% | Gender requirements |
| `eligibility.income` | 2 | 2% | Income requirements |

### 1.4 Sample Award Record (Full Schema)

```json
{
  "id": "ncwit-aic",
  "name": "NCWIT Award for Aspirations in Computing",
  "organization": "National Center for Women & IT",
  "category": "stem",
  "level": "national",
  "description": "Honors young women at the high-school level for computing achievements.",
  "prestige_score": 8,
  "historical_win_rate": 0.1,
  "effort_hours": 15,
  "deadline_month": 11,
  "deadline_recurring": "November 1 annually",
  "eligibility": {
    "grades": [9, 10, 11, 12],
    "gender": ["female", "non-binary"],
    "requirements": ["computing_experience", "essay", "recommendation"]
  },
  "prize_amount": 500,
  "prize_type": "scholarship",
  "diversity_focus": true,
  "touchpoints": 4,
  "touchpoint_types": ["application", "essay", "recommendation", "interview"],
  "is_active": true
}
```

---

## Part 2: Opportunities (Summer Programs) Data Analysis

### 2.1 Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Programs** | 58 |
| **Types** | 3 (Summer Program: 49, Internship: 8, Research: 1) |
| **Categories** | 8 (Research, STEM, Leadership, Academic, Arts, Entrepreneurship, Humanities, Journalism) |

### 2.2 Selectivity Distribution

```
Selectivity          Count   Percentage
--------------------------------------
Highly Selective     24      41.4%
Selective            16      27.6%
Accessible            8      13.8%
Moderate              8      13.8%
Open                  2       3.4%
```

### 2.3 Current Schema - Field Presence

| Field | Present | Percentage | Notes |
|-------|---------|------------|-------|
| `id` | 58 | 100% | Unique identifier |
| `name` | 58 | 100% | Program name |
| `organization` | 58 | 100% | Sponsoring org |
| `type` | 58 | 100% | summer_program/internship/research |
| `category` | 58 | 100% | Program category |
| `description` | 58 | 100% | Brief description |
| `prestige_score` | 58 | 100% | 1-10 scale |
| `acceptance_rate` | 58 | 100% | 0.0-1.0 |
| `selectivity` | 58 | 100% | highly_selective/selective/moderate/open |
| `deadline_month` | 58 | 100% | Application deadline month |
| `duration_weeks` | 58 | 100% | Program duration |
| `cost` | 58 | 100% | Program cost ($) |
| `location` | 58 | 100% | Physical location |
| `eligibility` | 58 | 100% | Eligibility object |
| `eligibility.grades` | 58 | 100% | Eligible grades |
| `focus_area` | 58 | 100% | STEM/HUMANITIES/ARTS/etc |
| `diversity_focus` | 58 | 100% | Boolean |
| `touchpoints` | 58 | 100% | Number of touchpoints |
| `is_active` | 58 | 100% | Boolean |
| `is_residential` | 58 | 100% | Boolean |
| `is_virtual` | 58 | 100% | Boolean |
| `effort_hours` | 57 | 98% | Hours required |
| `program_start_month` | 57 | 98% | Start month |
| `financial_aid_available` | 25 | 43% | Boolean |
| `stipend` | 12 | 21% | Stipend amount |
| `deadline_recurring` | 11 | 19% | Recurring deadline |
| `eligibility.citizenship` | 8 | 14% | Citizenship requirements |
| `eligibility.gender` | 5 | 9% | Gender requirements |
| `eligibility.age_min` | 4 | 7% | Minimum age |
| `eligibility.income_requirement` | 2 | 3% | Income-based eligibility |

### 2.4 Sample Opportunity Record (Full Schema)

```json
{
  "id": "rsi",
  "name": "Research Science Institute (RSI)",
  "organization": "MIT / Center for Excellence in Education",
  "type": "summer_program",
  "category": "research",
  "description": "Six-week summer science and engineering program combining coursework with hands-on research.",
  "prestige_score": 10,
  "acceptance_rate": 0.03,
  "selectivity": "highly_selective",
  "deadline_month": 1,
  "deadline_recurring": "January 15 annually",
  "program_start_month": 6,
  "program_end_month": 8,
  "duration_weeks": 6,
  "cost": 0,
  "financial_aid_available": true,
  "location": "Cambridge, MA",
  "is_virtual": false,
  "is_residential": true,
  "effort_hours": 40,
  "eligibility": {
    "grades": [11],
    "citizenship": ["US", "international"],
    "requirements": ["essay", "recommendation", "transcript", "test_scores"]
  },
  "focus_area": "STEM",
  "touchpoints": 5,
  "diversity_focus": true,
  "is_active": true
}
```

---

## Part 3: v1.0 Jenny Intelligence Schema Requirements

### 3.1 Required Jenny Intelligence Fields for Awards

From v1.0 Handover specification, TYPE-014 Awards Agent requires:

| Field | Type | Description | Current Status |
|-------|------|-------------|----------------|
| `jenny_tier` | `int (1-4)` | Jenny's personal tier assessment | **MISSING** |
| `jenny_notes` | `string` | Jenny's expert commentary | **MISSING** |
| `success_patterns` | `string[]` | What leads to wins | **MISSING** |
| `common_mistakes` | `string[]` | What to avoid | **MISSING** |
| `archetype_fit` | `Dict[str, float]` | Which archetypes excel (0.0-1.0) | **MISSING** |
| `demographic_saturation` | `Dict[str, str]` | Regional/demographic overrepresentation | **MISSING** |
| `relationships.prerequisites` | `string[]` | Awards that should be won first | **MISSING** |
| `relationships.leads_to` | `string[]` | Awards this enables | **MISSING** |
| `win_cascade_position` | `string` | "entry" / "intermediate" / "capstone" | **MISSING** |
| `timing_windows.ideal_grade` | `int[]` | Optimal grades to apply | **MISSING** |
| `timing_windows.application_window_days` | `int` | Days before deadline to start | **MISSING** |

### 3.2 Required Jenny Intelligence Fields for Programs

From v1.0 Handover specification, TYPE-029 Summer Programs Agent requires:

| Field | Type | Description | Current Status |
|-------|------|-------------|----------------|
| `jenny_tier` | `int (1-4)` | Jenny's personal tier assessment | **MISSING** |
| `jenny_notes` | `string` | Jenny's expert commentary | **MISSING** |
| `success_patterns` | `string[]` | What leads to acceptance | **MISSING** |
| `common_mistakes` | `string[]` | Application pitfalls | **MISSING** |
| `archetype_fit` | `Dict[str, float]` | Which archetypes excel (0.0-1.0) | **MISSING** |
| `hidden_benefits` | `string[]` | Non-obvious advantages | **MISSING** |
| `red_flags` | `string[]` | Warning signs in applications | **MISSING** |
| `synergy_with` | `string[]` | Complementary programs | **MISSING** |
| `timing_windows.ideal_grade` | `int[]` | Optimal grades to apply | **MISSING** |
| `timing_windows.application_window_days` | `int` | Days before deadline to start | **MISSING** |

---

## Part 4: Schema Gap Analysis

### 4.1 Awards Schema Comparison

| v1.0 Required Field | Current Has | Mapping | Action Required |
|---------------------|-------------|---------|-----------------|
| `id` | `id` | Direct | None |
| `name` | `name` | Direct | None |
| `organization` | `organization` | Direct | None |
| `category` | `category` | Direct | None |
| `level` | `level` | Direct | None |
| `description` | `description` | Direct | None |
| `prestige_score` | `prestige_score` | Direct | None |
| `historical_win_rate` | `historical_win_rate` | Direct | None |
| `effort_hours` | `effort_hours` | Direct | None |
| `eligibility.grades` | `eligibility.grades` | Direct | None |
| `eligibility.gender` | `eligibility.gender` | Direct | None (3% coverage) |
| `eligibility.citizenship` | `eligibility.citizenship` | Direct | None (11% coverage) |
| `deadline_month` | `deadline_month` | Direct | None |
| `prize_amount` | `prize_amount` | Direct | None (48% coverage) |
| `diversity_focus` | `diversity_focus` | Direct | None |
| `touchpoints` | `touchpoints` | Direct | None |
| **`jenny_tier`** | - | **MISSING** | **ADD** |
| **`jenny_notes`** | - | **MISSING** | **ADD** |
| **`success_patterns`** | - | **MISSING** | **ADD** |
| **`common_mistakes`** | - | **MISSING** | **ADD** |
| **`archetype_fit`** | - | **MISSING** | **ADD** |
| **`demographic_saturation`** | - | **MISSING** | **ADD** |
| **`relationships.prerequisites`** | - | **MISSING** | **ADD** |
| **`relationships.leads_to`** | - | **MISSING** | **ADD** |
| **`win_cascade_position`** | - | **MISSING** | **ADD** |
| **`timing_windows`** | - | **MISSING** | **ADD** |

### 4.2 Programs Schema Comparison

| v1.0 Required Field | Current Has | Mapping | Action Required |
|---------------------|-------------|---------|-----------------|
| `id` | `id` | Direct | None |
| `name` | `name` | Direct | None |
| `organization` | `organization` | Direct | None |
| `type` | `type` | Direct | None |
| `category` | `category` | Direct | None |
| `description` | `description` | Direct | None |
| `prestige_score` | `prestige_score` | Direct | None |
| `acceptance_rate` | `acceptance_rate` | Direct | None |
| `selectivity` | `selectivity` | Direct | None |
| `deadline_month` | `deadline_month` | Direct | None |
| `duration_weeks` | `duration_weeks` | Direct | None |
| `cost` | `cost` | Direct | None |
| `financial_aid_available` | `financial_aid_available` | Direct | None (43% coverage) |
| `location` | `location` | Direct | None |
| `is_residential` | `is_residential` | Direct | None |
| `eligibility.grades` | `eligibility.grades` | Direct | None |
| `eligibility.citizenship` | `eligibility.citizenship` | Direct | None (14% coverage) |
| `diversity_focus` | `diversity_focus` | Direct | None |
| `touchpoints` | `touchpoints` | Direct | None |
| **`jenny_tier`** | - | **MISSING** | **ADD** |
| **`jenny_notes`** | - | **MISSING** | **ADD** |
| **`success_patterns`** | - | **MISSING** | **ADD** |
| **`common_mistakes`** | - | **MISSING** | **ADD** |
| **`archetype_fit`** | - | **MISSING** | **ADD** |
| **`hidden_benefits`** | - | **MISSING** | **ADD** |
| **`red_flags`** | - | **MISSING** | **ADD** |
| **`synergy_with`** | - | **MISSING** | **ADD** |
| **`timing_windows`** | - | **MISSING** | **ADD** |

---

## Part 5: Data Quality Assessment

### 5.1 Awards Data Quality

| Metric | Value | Assessment |
|--------|-------|------------|
| Total Records | 97 | Good coverage |
| Unique Categories | 10 | Good diversity |
| Records with prestige_score | 100% | Complete |
| Records with historical_win_rate | 100% | Complete |
| Records with eligibility.grades | 100% | Complete |
| Records with deadline_month | 95% | Excellent |
| Records with prize_amount | 48% | Fair |
| Records with gender restrictions | 3% | Expected (most are open) |
| Records with citizenship restrictions | 11% | Expected |

**Quality Score: 8.5/10** - Excellent structural data, missing intelligence layer.

### 5.2 Opportunities Data Quality

| Metric | Value | Assessment |
|--------|-------|------------|
| Total Records | 58 | Moderate coverage |
| Unique Types | 3 | Limited (focus on summer programs) |
| Records with acceptance_rate | 100% | Complete |
| Records with selectivity | 100% | Complete |
| Records with eligibility.grades | 100% | Complete |
| Records with financial_aid_available | 43% | Fair |
| Records with program_start_month | 98% | Excellent |
| Records with stipend | 21% | Expected (most don't offer) |

**Quality Score: 8.0/10** - Good structural data, missing intelligence layer.

### 5.3 Coverage Gaps Identified

1. **No local/school-specific awards** - All awards are national/state/regional level
2. **Limited internship coverage** - Only 8 internships vs 49 summer programs
3. **Missing international programs** - Most programs are US-based
4. **No virtual-first programs post-COVID** - Limited is_virtual coverage
5. **Missing cost ranges** - Cost is binary ($0 or fixed), no ranges

---

## Part 6: Implementation Recommendations

### 6.1 Phase 1: Jenny Intelligence Schema Addition

**Priority: CRITICAL** - Required before v1.0 agents can function as designed.

**Option A: Seed Data Enhancement (Recommended)**
- Add Jenny Intelligence fields directly to `awards_data.py` and `opportunities_data.py`
- Use LLM to generate initial values based on award/program characteristics
- Manual review by domain expert

**Option B: Separate Intelligence Layer**
- Keep existing seed data unchanged
- Create `jenny_awards_intelligence.py` and `jenny_programs_intelligence.py`
- Join at runtime via `id` field

**Option C: Database-First Approach**
- Migrate seed data to Supabase
- Add Jenny Intelligence columns
- Load via API at agent initialization

### 6.2 Phase 2: Archetype Fit Calculation

For each award/program, calculate archetype fit scores (0.0-1.0) based on:
- Category alignment (STEM awards → Academic Powerhouse archetype)
- Effort hours alignment (high hours → Grit & Grind archetype)
- Diversity focus (diversity_focus=true → Changemaker archetype)
- Prestige score (high prestige → Legacy Builder archetype)

Example archetype_fit calculation:
```python
def calculate_archetype_fit(award: dict) -> dict:
    fit = {
        "academic_powerhouse": 0.0,
        "changemaker": 0.0,
        "creative_visionary": 0.0,
        "grit_and_grind": 0.0,
        "legacy_builder": 0.0,
        "stem_specialist": 0.0,
        "community_leader": 0.0,
        "multi_hyphenate": 0.0
    }

    # Category-based scoring
    if award["category"] == "stem":
        fit["stem_specialist"] = 0.9
        fit["academic_powerhouse"] = 0.7
    elif award["category"] == "arts":
        fit["creative_visionary"] = 0.9
        fit["multi_hyphenate"] = 0.6
    elif award["category"] == "service":
        fit["changemaker"] = 0.9
        fit["community_leader"] = 0.8

    # Diversity focus boosts changemaker
    if award.get("diversity_focus"):
        fit["changemaker"] = max(fit["changemaker"], 0.7)

    # High effort boosts grit_and_grind
    if award.get("effort_hours", 0) > 30:
        fit["grit_and_grind"] = 0.8

    # High prestige boosts legacy_builder
    if award.get("prestige_score", 0) >= 9:
        fit["legacy_builder"] = 0.8

    return fit
```

### 6.3 Phase 3: Win Cascade Mapping

Create prerequisite relationships between awards:
```python
WIN_CASCADE = {
    # Entry-level awards (no prerequisites)
    "entry": [
        "scholastic-writing-regional",
        "local-science-fair",
        "school-debate-champion"
    ],

    # Intermediate awards (require entry-level wins)
    "intermediate": {
        "ncwit-aic": ["local-stem-award", "school-cs-achievement"],
        "regeneron-sts-semifinal": ["regional-science-fair", "siemens-semifinal"],
        "nsf-honorable-mention": ["state-debate-champion"]
    },

    # Capstone awards (require intermediate wins)
    "capstone": {
        "regeneron-sts-finalist": ["regeneron-sts-semifinal"],
        "presidential-scholar": ["national-merit-finalist", "ap-scholar-distinction"]
    }
}
```

### 6.4 Phase 4: Jenny Notes Generation

Use LLM to generate Jenny-style notes for each award/program:

**Prompt Template:**
```
You are Jenny, an elite college admissions consultant with 20+ years of experience.
Generate expert insider notes for this award:

Award: {name}
Category: {category}
Prestige: {prestige_score}/10
Win Rate: {historical_win_rate * 100}%
Effort: {effort_hours} hours

Generate:
1. jenny_tier (1-4, where 1=must-have, 4=nice-to-have)
2. jenny_notes (2-3 sentences of insider advice)
3. success_patterns (3-5 patterns that lead to wins)
4. common_mistakes (3-5 common pitfalls to avoid)
```

---

## Part 7: Recommended Next Steps

### Immediate Actions (Week 1)

1. **Create Jenny Intelligence TypeScript interfaces** matching v1.0 spec
2. **Add jenny_tier to top 20 awards** (highest prestige_score) manually
3. **Add jenny_tier to top 10 programs** (lowest acceptance_rate) manually
4. **Create database migration** for Jenny Intelligence columns

### Short-Term Actions (Weeks 2-4)

5. **Generate Jenny Intelligence for remaining awards** using LLM
6. **Generate Jenny Intelligence for remaining programs** using LLM
7. **Manual review and adjustment** of generated content
8. **Create archetype_fit calculation utility**
9. **Map win cascade relationships** for national awards

### Medium-Term Actions (Weeks 5-8)

10. **Validate jenny_tier distribution** (should be ~15% Tier 1, ~25% Tier 2, ~35% Tier 3, ~25% Tier 4)
11. **Test archetype matching** against known student profiles (Huda case study)
12. **Integrate Jenny Intelligence** into Awards Agent (TYPE-014)
13. **Integrate Jenny Intelligence** into Summer Programs Agent (TYPE-029)

---

## Appendix A: Complete Field Inventory

### Awards Fields (Current + Required)

```typescript
interface Award {
  // EXISTING FIELDS (✓)
  id: string;                        // ✓ 100%
  name: string;                      // ✓ 100%
  organization: string;              // ✓ 100%
  category: string;                  // ✓ 100%
  level: string;                     // ✓ 100%
  description: string;               // ✓ 100%
  prestige_score: number;            // ✓ 100%
  historical_win_rate: number;       // ✓ 100%
  effort_hours: number;              // ✓ 100%
  deadline_month: number;            // ✓ 95%
  deadline_recurring?: string;       // ✓ 11%
  prize_amount?: number;             // ✓ 48%
  prize_type: string;                // ✓ 100%
  diversity_focus: boolean;          // ✓ 100%
  touchpoints: number;               // ✓ 100%
  touchpoint_types?: string[];       // ✓ 12%
  is_active: boolean;                // ✓ 100%
  eligibility: {
    grades: number[];                // ✓ 100%
    gender?: string[];               // ✓ 3%
    citizenship?: string[];          // ✓ 11%
    demographics?: string[];         // ✓ 9%
    requirements?: string[];         // ✓ 5%
    income?: string;                 // ✓ 2%
  };

  // MISSING JENNY INTELLIGENCE FIELDS (✗)
  jenny_tier?: 1 | 2 | 3 | 4;                      // ✗ 0%
  jenny_notes?: string;                            // ✗ 0%
  success_patterns?: string[];                     // ✗ 0%
  common_mistakes?: string[];                      // ✗ 0%
  archetype_fit?: Record<string, number>;          // ✗ 0%
  demographic_saturation?: Record<string, string>; // ✗ 0%
  win_cascade_position?: 'entry' | 'intermediate' | 'capstone';  // ✗ 0%
  relationships?: {
    prerequisites?: string[];                      // ✗ 0%
    leads_to?: string[];                           // ✗ 0%
  };
  timing_windows?: {
    ideal_grade?: number[];                        // ✗ 0%
    application_window_days?: number;              // ✗ 0%
  };
}
```

### Opportunities Fields (Current + Required)

```typescript
interface Opportunity {
  // EXISTING FIELDS (✓)
  id: string;                        // ✓ 100%
  name: string;                      // ✓ 100%
  organization: string;              // ✓ 100%
  type: string;                      // ✓ 100%
  category: string;                  // ✓ 100%
  description: string;               // ✓ 100%
  prestige_score: number;            // ✓ 100%
  acceptance_rate: number;           // ✓ 100%
  selectivity: string;               // ✓ 100%
  deadline_month: number;            // ✓ 100%
  deadline_recurring?: string;       // ✓ 19%
  program_start_month?: number;      // ✓ 98%
  program_end_month?: number;        // ✓ 2%
  duration_weeks: number;            // ✓ 100%
  cost: number;                      // ✓ 100%
  financial_aid_available?: boolean; // ✓ 43%
  stipend?: number;                  // ✓ 21%
  location: string;                  // ✓ 100%
  is_virtual: boolean;               // ✓ 100%
  is_residential: boolean;           // ✓ 100%
  effort_hours?: number;             // ✓ 98%
  focus_area: string;                // ✓ 100%
  diversity_focus: boolean;          // ✓ 100%
  touchpoints: number;               // ✓ 100%
  is_active: boolean;                // ✓ 100%
  eligibility: {
    grades: number[];                // ✓ 100%
    citizenship?: string[];          // ✓ 14%
    gender?: string[];               // ✓ 9%
    age_min?: number;                // ✓ 7%
    income_requirement?: boolean;    // ✓ 3%
    requirements?: string[];         // ✓ 3%
    gpa_min?: number;                // ✓ 2%
    location?: string;               // ✓ 2%
  };

  // MISSING JENNY INTELLIGENCE FIELDS (✗)
  jenny_tier?: 1 | 2 | 3 | 4;               // ✗ 0%
  jenny_notes?: string;                      // ✗ 0%
  success_patterns?: string[];               // ✗ 0%
  common_mistakes?: string[];                // ✗ 0%
  archetype_fit?: Record<string, number>;    // ✗ 0%
  hidden_benefits?: string[];                // ✗ 0%
  red_flags?: string[];                      // ✗ 0%
  synergy_with?: string[];                   // ✗ 0%
  timing_windows?: {
    ideal_grade?: number[];                  // ✗ 0%
    application_window_days?: number;        // ✗ 0%
  };
}
```

---

## Appendix B: Sample Jenny Intelligence Enhancement

### Example: NCWIT Award Enhanced

```json
{
  "id": "ncwit-aic",
  "name": "NCWIT Award for Aspirations in Computing",

  // ... existing fields ...

  // NEW JENNY INTELLIGENCE FIELDS
  "jenny_tier": 2,
  "jenny_notes": "This is THE award for women in tech. Winners get incredible networking at the summit and it's become a strong signal for Stanford/MIT. Focus your essay on IMPACT, not just technical skills - they want to see how you've inspired others.",

  "success_patterns": [
    "Leadership in CS club or coding initiative",
    "Mentoring younger students in tech",
    "Creating apps/projects that solve real community problems",
    "Strong recommendation from CS teacher emphasizing character",
    "Demonstrable persistence through technical challenges"
  ],

  "common_mistakes": [
    "Focusing only on technical achievements, not impact",
    "Generic essay about loving coding since age 10",
    "Not highlighting collaborative projects",
    "Weak recommender who doesn't know specific projects",
    "Applying without meaningful community involvement"
  ],

  "archetype_fit": {
    "stem_specialist": 0.9,
    "changemaker": 0.8,
    "community_leader": 0.7,
    "academic_powerhouse": 0.6,
    "creative_visionary": 0.5,
    "multi_hyphenate": 0.4,
    "grit_and_grind": 0.3,
    "legacy_builder": 0.2
  },

  "demographic_saturation": {
    "california": "high",
    "texas": "moderate",
    "midwest": "low",
    "northeast": "moderate"
  },

  "win_cascade_position": "intermediate",

  "relationships": {
    "prerequisites": ["local-cs-award", "school-cs-achievement"],
    "leads_to": ["ncwit-collegiate", "grace-hopper-scholarship"]
  },

  "timing_windows": {
    "ideal_grade": [10, 11],
    "application_window_days": 45
  }
}
```

---

*Document End - Data Discovery Report v1.0*
