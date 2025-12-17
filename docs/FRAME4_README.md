# IvyQuest v3.0 — Frame 4: Reveal

## Package Contents

```
frame4-package/
├── README.md
├── package.json
├── docs/
│   ├── CLAUDE_AGENT_CONTEXT.md     # Agent guardrails
│   └── FRAME4_IMPLEMENTATION.md    # Full specification
└── src/
    ├── components/frames/Frame4Reveal/
    │   ├── index.tsx               # Frame orchestrator
    │   ├── Card1LaunchSequence.tsx # Countdown + launch animation
    │   ├── Card2DualScore.tsx      # Profile Strength + Market Reality
    │   ├── Card3SchoolCards.tsx    # Swipeable school fit cards
    │   └── Card4CategoryBreakdown.tsx # Score breakdown by category
    └── lib/
        ├── constants/
        │   ├── frame4.constants.ts # Score tiers, school configs
        │   └── index.ts
        ├── types/
        │   ├── frame4.types.ts     # Frame4Data, Frame4Signals
        │   └── index.ts
        ├── store/
        │   └── questStore.frame4.ts # Zustand slice
        ├── utils/
        │   ├── cn.ts
        │   └── index.ts
        └── index.ts
```

## Frame 4 Purpose

**THE PAYOFF** — Show the student their comprehensive assessment results

| Card | Purpose | Student Gets |
|------|---------|--------------|
| Card 1 | Launch sequence animation | "The big reveal moment!" |
| Card 2 | Dual score display | "My profile strength AND actual chances" |
| Card 3 | School-specific breakdown | "How I fit at each school" |
| Card 4 | Category breakdown | "Where I'm strong vs need improvement" |

## Key Features

### Dual Score System
1. **Profile Strength (Ivy+ Ready Score)** — What you control (0-100)
   - 50 = Average applicant
   - 70 = Competitive
   - 85+ = Exceptional

2. **Market Reality (RS Rubric)** — Your actual odds (%)
   - Based on school acceptance rates
   - Adjusted by demographics, legacy, hooks
   - Research-backed (Chetty data)

### Launch Sequence Animation
- 3-2-1 countdown
- Twin fleet takeoff
- Dramatic score reveal
- Screen shake on impact

### School Fit Cards
- Swipeable card interface
- Per-school probability range
- Fit score with category breakdown
- Insights on what each school values

### Category Breakdown
- Aptitude (academics)
- Passion (activities/spike)
- Community (service/impact)
- Operating (psychometrics)

## Data Flow

```
Frame 0 → Target Schools
Frame 1 → Aptitude Score (GPA, SAT, Rigor)
Frame 2 → Passion + Community Scores
Frame 3 → Operating Style + Readiness
    ↓
Frame 4 → REVEAL
    ↓
Frame 5 → Boosters (how to improve)
```

## Score Calculation

```typescript
// Ivy+ Ready Score (Profile Strength)
ivyReadyScore = (
  aptitudeScore * 0.35 +      // 35% academics
  passionScore * 0.30 +       // 30% spike/passion
  communityScore * 0.20 +     // 20% service/community
  operatingScore * 0.15       // 15% psychometrics
) * multipliers

// Market Reality (RS Rubric Probability)
marketReality = baseAcceptanceRate * demographicMultiplier * schoolFitMultiplier
```

---

**Target Duration**: 30-45 seconds
**Cards**: 4
**Previous Frame**: Frame 3 (Operating)
**Next Frame**: Frame 5 (Power-Ups)
