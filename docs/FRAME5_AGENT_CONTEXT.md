# CLAUDE AGENT CONTEXT — Frame 5: Power-Ups

## ⚠️ ABSOLUTE PROHIBITIONS

1. **NEVER** modify booster definitions without explicit approval
2. **NEVER** bypass priority calculation logic
3. **NEVER** show projected scores without selecting boosters first
4. **NEVER** allow action plan generation without booster selection
5. **NEVER** hardcode impact values outside booster definitions
6. **NEVER** skip trigger matching when generating recommendations
7. **NEVER** remove trace logging calls
8. **NEVER** modify priority weights without review
9. **NEVER** show boosters that don't match triggers
10. **NEVER** allow more than 10 boosters selected at once

---

## 📋 Card-by-Card Workflow

### Card 1: Overview
```
INPUTS → calculateCurrentScores → displayProfileSummary
                                         ↓
                              showTopOpportunities (3 boosters)
                                         ↓
                                    Continue →
```

**Display:**
- Current Ivy+ Ready Score
- Layer breakdown (aptitude, passion, community, operating)
- Top 3 recommended boosters with match reasons
- Years to application reminder

### Card 2: Booster Selection
```
ALL_BOOSTERS → filterByCategory → sortBy → displayGrid
                                              ↓
                                     User selects boosters
                                              ↓
                                    validateSelection (≥1)
                                              ↓
                                         Continue →
```

**Features:**
- Category filter tabs
- Sort options (priority, impact, time, difficulty)
- Expandable booster cards
- Real-time selection count

**Required for advancement:**
- At least 1 booster selected

### Card 3: Impact Preview
```
SELECTED_BOOSTERS → calculateProjectedScores → displayImpactSummary
                                                      ↓
                                               Show before/after
                                                      ↓
                                                 Continue →
```

**Display:**
- Current vs. projected Ivy+ Ready Score
- Layer-by-layer impact breakdown
- Selected boosters summary with individual impacts
- Confidence indicators

### Card 4: Action Plan
```
SELECTED_BOOSTERS → generateActionPlan → displayChecklist
                                               ↓
                                      Group by booster
                                               ↓
                                      Show timeline estimate
                                               ↓
                                      Complete Quest →
```

**Features:**
- Action items grouped by booster
- Checkboxes for completion tracking
- Notes field per item
- Progress percentage
- Estimated weeks to complete

---

## 🎯 Booster Priority Algorithm

```typescript
priority = (
  gapScore × 0.40 +       // Distance from target (85)
  improvability × 0.30 +  // How achievable
  urgency × 0.30          // Time pressure
)
```

### Gap Score (0-100)
```typescript
gapScore = min(100, ((85 - currentScore) / 50) × 100)
```

### Improvability (0-100)
```typescript
Base = 50

// Academic bonuses
if grade 9-10: +30
if grade 11: +15
if grade 12: -10

// Passion bonuses
if no national recognition: +20
if no awards: +15

// Community bonuses
if leadership < 2: +25
if service < 100hrs: +15

// Operating always gets: +20

// Difficulty penalties
easy: 0, medium: -5, hard: -15, expert: -25
```

### Urgency (fixed values)
```typescript
yearsToApp ≤ 1: 100 (critical)
yearsToApp = 2: 75 (high)
yearsToApp ≥ 3: 50 (moderate)
```

---

## 🔒 Trigger Matching Rules

Each booster has trigger conditions that must be checked:

```typescript
triggers: {
  minScore?: number;      // Skip if current score below
  maxScore?: number;      // Skip if current score above
  gradeLevel?: string[];  // Only show for these grades
  capabilities?: string[]; // Show if user has these capabilities
  missingElements?: string[]; // Show if user missing these
}
```

### Missing Element Detection
```typescript
'ap_depth' → apCourseCount < 8
'national_recognition' → hasNationalRecognition === false
'leadership' → leadershipRoleCount < 2
'service_hours' → serviceHours < 100
'awards' → hasAwards === false
'diversity' → leadershipRoleCount < 3
```

---

## 📊 Impact Calculation

```typescript
// Base impact from booster definition
impact = booster.baseImpact

// Difficulty multiplier
impact × difficultyMultiplier (easy:0.8, medium:1.0, hard:1.2, expert:1.5)

// Diminishing returns at high scores
if currentScore > 80: impact × 0.7
if currentScore > 90: impact × 0.5

// Time pressure reduction
if yearsToApp ≤ 1: impact × 0.8
```

### Projected Score Calculation
```typescript
// For each layer
projectedScore = min(100, currentScore + layerImpact)

// With diminishing returns for multiple boosters in same layer
if existingImpact > 0: impact × 0.7

// Recalculate Ivy+ Ready
projectedIvyReady =
  aptitude × 0.35 +
  passion × 0.30 +
  community × 0.20 +
  operating × 0.15
```

---

## 🧪 Test Scenarios

### Happy Path
1. Enter Frame 5 with ivyReady = 72
2. See 3 top recommended boosters
3. Continue to selection
4. Select "Take More AP Courses" and "Start Initiative"
5. View impact: +8 aptitude, +15 passion
6. Generate action plan with 8 steps
7. Complete quest

### Edge Cases
- All scores above 85 → Show operating boosters only
- Grade 12 → Reduce academic booster visibility
- Already has national recognition → Skip deepen_spike trigger
- Select 10 boosters → Prevent additional selections

---

## 📝 Trace Log Format

```
[BOOSTER_ENGINE] Starting booster generation { yearsToApp: 2, gradeLevel: '11' }
[BOOSTER_ENGINE] Generated boosters { total: 15, returned: 10 }

[FRAME5.INIT] Initializing with inputs { ivyReady: 72, yearsToApp: 2 }
[FRAME5.INIT] Generated boosters { count: 10 }

[FRAME5.SELECT] more_ap_courses { totalSelected: 1 }
[FRAME5.SELECT] start_initiative { totalSelected: 2 }

[FRAME5.ACTION_PLAN] Generated { steps: 8, weeks: 18 }
[FRAME5.COMPLETE] { selectedBoosters: ['more_ap_courses', 'start_initiative'], actionSteps: 8 }
```

---

## 🔄 State Dependencies

```
Frame 0 → targetSchools, yearsToApp, gradeLevel
Frame 1 → aptitudeScore, demographics
Frame 2 → passionScore, communityScore, activities
Frame 3 → operatingScore, hiddenCapabilities, operatingStyle
Frame 4 → ivyReadyScore (final)
     ↓
Frame 5 → Uses ALL of above for booster matching
```

---

## ✅ Pre-Deployment Checklist

- [ ] All 18 boosters defined correctly
- [ ] Trigger matching works for all conditions
- [ ] Priority calculation produces sensible rankings
- [ ] Impact calculation includes all modifiers
- [ ] Projected scores never exceed 100
- [ ] Action plan groups items by booster
- [ ] UI responsive on mobile
- [ ] Progress persists across card navigation
- [ ] Selection state survives filter/sort changes
- [ ] Trace logging captures all actions
