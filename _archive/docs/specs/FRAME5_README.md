# IvyQuest v3.0 — Frame 5: Power-Ups

## Package Contents

```
frame5-package/
├── README.md
├── package.json
├── docs/
│   └── CLAUDE_AGENT_CONTEXT.md
└── src/
    ├── components/
    │   └── frames/
    │       └── Frame5PowerUps/
    │           ├── index.tsx           # Frame orchestrator
    │           ├── BoosterCard.tsx     # Individual booster display
    │           ├── BoosterGrid.tsx     # Grid of all boosters
    │           ├── ImpactMeter.tsx     # Impact visualization
    │           └── ActionPlan.tsx      # Actionable next steps
    ├── lib/
    │   ├── constants/
    │   │   └── frame5.constants.ts
    │   ├── types/
    │   │   └── frame5.types.ts
    │   ├── store/
    │   │   └── questStore.frame5.ts
    │   ├── engines/
    │   │   └── boosterEngine.ts        # Recommendation logic
    │   └── utils/
    │       └── cn.ts
    └── index.ts
```

## Purpose

Frame 5 is the **action-oriented finale** of IvyQuest. After seeing their scores in Frame 4 (Reveal), students receive personalized "Power-Ups" — concrete recommendations to boost their profile.

## User Journey

1. **Enter Frame 5** → See summary of current profile strength
2. **View Boosters** → Prioritized list of recommendations
3. **Explore Impact** → See projected score improvement per booster
4. **Action Plan** → Specific steps and timeline

## Booster Categories

### 1. Academic Boosters
- Take more AP/IB courses
- Improve SAT/ACT scores
- Pursue independent research
- Enroll in dual enrollment

### 2. Passion Boosters
- Deepen spike activity
- Compete at higher levels
- Start a project/initiative
- Seek mentorship

### 3. Community Boosters
- Take leadership roles
- Increase service hours
- Expand impact scope
- Diversify involvement

### 4. Operating Boosters
- Optimize time allocation
- Develop hidden capabilities
- Adjust operating style
- Build energy management

## Booster Priority Scoring

Each booster is scored based on:

```typescript
priority = (
  gapSize × 0.40 +       // How far below target
  improvability × 0.30 + // How achievable
  urgency × 0.30         // Time to application
)
```

### Gap Size Calculation
```typescript
gapSize = targetScore - currentScore
// Higher gap = higher priority
```

### Improvability Factors
```typescript
improvability = {
  academic: gradeLevel < 12 ? high : low,  // Harder to change senior year
  passion: depthLevel < 'national' ? high : medium,
  community: leadershipRoles < 3 ? high : medium,
  operating: always improvable
}
```

### Urgency Calculation
```typescript
urgency = {
  yearsToApp <= 1: 'critical',
  yearsToApp == 2: 'high',
  yearsToApp >= 3: 'moderate'
}
```

## Impact Projections

Each booster shows estimated score improvement:

```typescript
// Example booster impact
{
  booster: 'Take 2 more AP courses',
  category: 'academic',
  currentScore: 78,
  projectedScore: 84,
  impact: +6,
  confidence: 'high',
  timeToComplete: '1 semester'
}
```

## Data Flow

```
Frame 0-4 Data → Booster Engine → Prioritized Recommendations
                      ↓
              Impact Calculations
                      ↓
              Action Plan Generation
```

## Integration with Hidden Capabilities

Frame 3's hidden capabilities inform Frame 5's recommendations:

```typescript
// If hidden capability detected but unused
if (capabilities.includes('visual_thinking') && !activities.includes('design')) {
  recommend({
    booster: 'Start a design project',
    rationale: 'Your visual thinking strength is untapped',
    impact: +8
  })
}
```

## UI Components

### BoosterCard
- Icon for category
- Title and description
- Impact meter (+X points)
- Difficulty indicator
- Time estimate
- "Add to Plan" button

### BoosterGrid
- Filterable by category
- Sortable by impact/priority
- Toggle completed boosters

### ImpactMeter
- Visual bar showing current vs. projected
- Animated fill on selection
- Category breakdown

### ActionPlan
- Checklist format
- Weekly/monthly timeline
- Progress tracking

## State Management

```typescript
interface Frame5State {
  // Inputs
  currentScores: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
    ivyReady: number;
  };
  targetSchools: string[];
  yearsToApp: number;
  hiddenCapabilities: string[];

  // Generated
  boosters: Booster[];
  selectedBoosters: string[];
  actionPlan: ActionItem[];

  // UI
  currentCard: number;
  categoryFilter: string | null;
  sortBy: 'priority' | 'impact' | 'time';
}
```

## Card Flow

1. **Card 1: Overview** — "Here's your current profile and top opportunities"
2. **Card 2: Boosters** — Browse and select power-ups
3. **Card 3: Impact** — See cumulative effect of selections
4. **Card 4: Action Plan** — Get specific next steps

---

**Version**: 1.0.0
**Last Updated**: December 2025
