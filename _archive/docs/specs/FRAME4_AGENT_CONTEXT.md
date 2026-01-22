# CLAUDE AGENT CONTEXT — Frame 4: Reveal

> **CRITICAL**: Read this ENTIRE document before writing ANY code.
> This file contains mandatory guardrails for AI coding agents.

---

## 🚨 ABSOLUTE PROHIBITIONS

These rules are NON-NEGOTIABLE. Violation = immediate rollback.

| # | Rule | Consequence |
|---|------|-------------|
| 1 | **NEVER modify Frame 0-3 code** | Breaks upstream dependencies |
| 2 | **NEVER hardcode score calculations** | Use scoring engine |
| 3 | **NEVER show scores without animation** | Ruins the reveal moment |
| 4 | **NEVER display raw probabilities without context** | Creates anxiety |
| 5 | **NEVER skip the launch sequence** | Destroys emotional payoff |
| 6 | **NEVER show negative/discouraging language** | Harms student wellbeing |
| 7 | **NEVER reveal all schools simultaneously** | Overwhelms user |
| 8 | **NEVER bypass store for state** | Creates race conditions |
| 9 | **NEVER ignore TypeScript errors** | Masks runtime failures |
| 10 | **NEVER skip trace logging** | Breaks analytics pipeline |

---

## 📋 FRAME 4 SCOPE

### What Frame 4 Does
- Receives all signals from Frames 0-3
- Calculates final Ivy+ Ready Score
- Computes RS Rubric probabilities per school
- Animates the "big reveal" moment
- Shows school-by-school fit analysis
- Displays category breakdown
- Prepares data for Frame 5 boosters

### What Frame 4 Does NOT Do
- Modify any upstream data
- Recommend specific boosters (Frame 5)
- Allow editing of scores
- Store payment or PII

---

## 🔄 INPUT DEPENDENCIES

### From Frame 0 (Warm-Up)
```typescript
interface Frame0Inputs {
  targetSchools: string[];
  intendedMajor: string;
  majorCertainty: 'exploring' | 'likely' | 'locked';
  gradeLevel: number;
  studentName: string;
}
```

### From Frame 1 (Snapshot)
```typescript
interface Frame1Inputs {
  aptitudeScore: number;      // 0-100
  gpaWeighted: number;
  satTotal: number | null;
  actComposite: number | null;
  apCount: number;
  saturationLevel: string;
  demographicMultipliers: {
    firstGen: boolean;
    legacy: Record<string, boolean>;
    urm: boolean;
    incomePercentile: number;
  };
}
```

### From Frame 2 (Building)
```typescript
interface Frame2Inputs {
  passionScore: number;       // 0-100
  communityScore: number;     // 0-100
  spikeCategory: string;
  leadershipLevel: string;
  serviceHours: number;
  studentArchetype: string;
}
```

### From Frame 3 (Operating)
```typescript
interface Frame3Inputs {
  operatingStyle: string;
  timeCapacity: number;
  energyPattern: string;
  strengthProfile: string;
  readinessScore: number;     // 0-100
  auraColor: string;
}
```

---

## 🃏 CARD-BY-CARD REQUIREMENTS

### Card 1: Launch Sequence

**Purpose**: Create emotional buildup before reveal

**Required Phases**:
1. **Countdown** (3-2-1) with engine warmup visual
2. **Launch** — Twin fleet lifts off
3. **Flight** — Brief transition animation
4. **Landing** — Screen shake, dramatic pause
5. **Reveal** — Transition to score display

**Animation Durations**:
```typescript
const LAUNCH_TIMINGS = {
  countdown: 3000,      // 3 seconds
  launch: 1200,         // 1.2 seconds
  flight: 800,          // 0.8 seconds
  landing: 600,         // 0.6 seconds
  revealDelay: 400,     // 0.4 seconds
};
```

**Visual Requirements**:
- Engine glow particles during countdown
- Vertical movement during launch
- Motion blur during flight
- Screen shake on landing
- Dramatic fade to score display

---

### Card 2: Dual Score Display

**Purpose**: Show both Profile Strength AND Market Reality

**Required Elements**:
1. **Profile Strength Ring** — Animated 0 → actual score
2. **Market Reality Bar** — Probability range with context
3. **Score Labels** — Clear explanation of each metric
4. **Benchmarks** — 50 Average / 70 Competitive / 85+ Exceptional

**Animation Sequence**:
```typescript
// Profile Strength animates first (1.5s)
// Market Reality animates second (1.2s, delayed 300ms)
// Labels fade in after animations complete
```

**Data Contract**:
```typescript
interface DualScoreData {
  profileStrength: number;     // 0-100
  marketReality: {
    min: number;               // Lower bound %
    max: number;               // Upper bound %
    label: string;             // "Reach" | "Target" | "Safety"
  };
  schoolCount: number;
}
```

---

### Card 3: School Fit Cards

**Purpose**: Per-school breakdown with swipe navigation

**Required Elements**:
- Swipeable card carousel
- School logo/name header
- Probability range display
- Fit indicators (Reach/Target/Safety)
- Key insight per school
- Navigation dots

**Card Content**:
```typescript
interface SchoolFitCard {
  schoolId: string;
  schoolName: string;
  probability: { min: number; max: number };
  fitLabel: 'reach' | 'target' | 'safety';
  fitScore: number;            // 0-100
  keyInsight: string;          // "Your research spike aligns with MIT's maker culture"
  categoryScores: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
  };
}
```

**Swipe Behavior**:
- Horizontal swipe to change schools
- Dots indicate current position
- Auto-play option (2.5s per card)
- Tap to pause auto-play

---

### Card 4: Category Breakdown

**Purpose**: Show where student is strong vs needs work

**Required Elements**:
- 4 category bars (Aptitude, Passion, Community, Operating)
- Visual indicators for each bar
- Strength/weakness labels
- Actionable insight per category

**Category Config**:
```typescript
const CATEGORIES = [
  { id: 'aptitude', label: 'Aptitude', icon: '📚', weight: 0.35 },
  { id: 'passion', label: 'Passion', icon: '🔥', weight: 0.30 },
  { id: 'community', label: 'Community', icon: '🤝', weight: 0.20 },
  { id: 'operating', label: 'Operating', icon: '⚙️', weight: 0.15 },
];
```

**Visual Treatment**:
- Green bar for scores 70+
- Yellow bar for scores 50-69
- Orange bar for scores below 50
- Pulsing highlight on strongest category

---

## 📊 SCORE CALCULATIONS

### Ivy+ Ready Score (Profile Strength)
```typescript
function calculateIvyReadyScore(inputs: AllFrameInputs): number {
  const baseScore = (
    inputs.aptitudeScore * 0.35 +
    inputs.passionScore * 0.30 +
    inputs.communityScore * 0.20 +
    (inputs.readinessScore * 0.15)
  );

  // Apply multipliers
  let multiplier = 1.0;
  if (inputs.firstGen) multiplier *= 1.08;
  if (inputs.urm) multiplier *= 1.05;

  return Math.min(100, Math.round(baseScore * multiplier));
}
```

### Market Reality (RS Rubric)
```typescript
function calculateMarketReality(
  schoolId: string,
  ivyReadyScore: number,
  demographics: DemographicInputs
): { min: number; max: number; label: string } {
  const baseRate = SCHOOL_ACCEPTANCE_RATES[schoolId];

  // Apply demographic adjustments
  let adjustedRate = baseRate;
  if (demographics.legacy[schoolId]) adjustedRate *= 2.5;
  if (demographics.firstGen) adjustedRate *= 1.3;
  if (demographics.urm) adjustedRate *= 1.4;

  // Apply score-based adjustment
  const scoreMultiplier = 0.5 + (ivyReadyScore / 100);
  adjustedRate *= scoreMultiplier;

  // Create range
  const variance = adjustedRate * 0.3;
  return {
    min: Math.max(1, Math.round(adjustedRate - variance)),
    max: Math.min(100, Math.round(adjustedRate + variance)),
    label: getFitLabel(adjustedRate, baseRate),
  };
}
```

---

## 🎨 VISUAL REQUIREMENTS

### Color Scheme
```typescript
const REVEAL_COLORS = {
  exceptional: '#10B981',    // Green (85+)
  competitive: '#3B82F6',    // Blue (70-84)
  average: '#F59E0B',        // Amber (50-69)
  below: '#EF4444',          // Red (<50)

  reach: '#EF4444',          // Red
  target: '#F59E0B',         // Amber
  safety: '#10B981',         // Green
};
```

### Animation Easing
```typescript
const EASING = {
  scoreReveal: [0.4, 0, 0.2, 1],   // cubic-bezier
  cardSwipe: [0.25, 0.1, 0.25, 1],
  bounce: [0.68, -0.55, 0.265, 1.55],
};
```

---

## 🔍 TRACE LOGGING REQUIREMENTS

```typescript
// Launch sequence phases
trace.log('FRAME4.LAUNCH', `Phase: ${phase}`);

// Score reveal
trace.log('FRAME4.SCORE', `IvyReady: ${score}, Schools: ${schools.length}`);

// School card views
trace.log('FRAME4.SCHOOL', `Viewed: ${schoolId}, Probability: ${min}-${max}%`);

// Frame completion
trace.log('FRAME4.COMPLETE', `Duration: ${duration}ms`);
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Before Starting
- [ ] Verify all Frame 0-3 signals are accessible
- [ ] Confirm scoring engine functions exist
- [ ] Check animation library is installed

### Per-Card Checklist
- [ ] Component renders without errors
- [ ] Animations play smoothly (60fps)
- [ ] Score calculations are accurate
- [ ] Mobile responsive
- [ ] Trace logging implemented

### Before Marking Frame Complete
- [ ] All 4 cards functional
- [ ] Card transitions smooth
- [ ] Scores match scoring engine
- [ ] No console errors
- [ ] Analytics tracking working

---

## 🚫 COMMON MISTAKES TO AVOID

1. **Don't show raw numbers without animation** — Ruins the reveal
2. **Don't use negative language** — "Only 5%" → "5-8% range, similar to peers"
3. **Don't skip the countdown** — Students expect the dramatic moment
4. **Don't overwhelm with data** — Progressive disclosure
5. **Don't forget accessibility** — Screen reader announcements for scores

---

## 💬 TONE GUIDELINES

**DO SAY**:
- "Your Profile Strength: 72 — Competitive range!"
- "At Harvard, students like you have a 6-10% probability"
- "Your Passion score is your strongest asset"

**DON'T SAY**:
- "Your score is only 72"
- "You have low chances at Harvard"
- "Your Community score is weak"

---

**Remember**: Frame 4 is THE moment students have been waiting for.
Make it dramatic, make it clear, make it actionable.
