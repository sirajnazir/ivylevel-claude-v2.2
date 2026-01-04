/**
 * Edge Points System Constants
 * Replaces XP terminology with "Edge" - implies competitive advantage
 * @version 11.0
 */

export const EDGE_TERMS = {
  singular: 'Edge',
  plural: 'Edge',
  verb: 'Build',
  adjective: 'Competitive',
} as const;

export const EDGE_VALUES = {
  // Frame progression
  frameComplete: 50,
  cardComplete: 25,
  assessmentComplete: 500,

  // Actions
  actionStart: 5,
  actionComplete: 20,
  quickWinComplete: 30,
  firstAction: 100,

  // Engagement
  weeklyStreak: 50,
  essayDraftComplete: 75,
  coachSession: 100,

  // Achievements
  milestoneReached: 100,
  tierAdvancement: 200,
} as const;

export interface EdgeTier {
  id: string;
  name: string;
  minEdge: number;
  maxEdge: number;
  color: string;
  bgColor: string;
  description: string;
}

export const EDGE_TIERS: EdgeTier[] = [
  {
    id: 'starter',
    name: 'Getting Started',
    minEdge: 0,
    maxEdge: 249,
    color: '#6B7280',
    bgColor: '#F3F4F6',
    description: 'Beginning your college prep journey'
  },
  {
    id: 'building',
    name: 'Building Momentum',
    minEdge: 250,
    maxEdge: 749,
    color: '#2563EB',
    bgColor: '#DBEAFE',
    description: 'Making consistent progress'
  },
  {
    id: 'advancing',
    name: 'Advancing',
    minEdge: 750,
    maxEdge: 1499,
    color: '#059669',
    bgColor: '#D1FAE5',
    description: 'Standing out from the crowd'
  },
  {
    id: 'competitive',
    name: 'Competitive',
    minEdge: 1500,
    maxEdge: 2999,
    color: '#D97706',
    bgColor: '#FEF3C7',
    description: 'Strong positioning for top schools'
  },
  {
    id: 'elite',
    name: 'Elite',
    minEdge: 3000,
    maxEdge: Infinity,
    color: '#641432',
    bgColor: '#FFF5F2',
    description: 'Top-tier candidate profile'
  },
];

/**
 * Get the current Edge tier based on points
 */
export function getEdgeTier(edgePoints: number): EdgeTier {
  return EDGE_TIERS.find(tier =>
    edgePoints >= tier.minEdge && edgePoints <= tier.maxEdge
  ) || EDGE_TIERS[0];
}

/**
 * Get progress toward next tier
 */
export function getEdgeProgress(edgePoints: number): {
  current: number;
  currentTier: EdgeTier;
  nextTier: EdgeTier | null;
  progress: number;
  pointsToNext: number;
} {
  const currentTier = getEdgeTier(edgePoints);
  const currentIndex = EDGE_TIERS.findIndex(t => t.id === currentTier.id);
  const nextTier = currentIndex < EDGE_TIERS.length - 1 ? EDGE_TIERS[currentIndex + 1] : null;

  if (!nextTier) {
    return {
      current: edgePoints,
      currentTier,
      nextTier: null,
      progress: 100,
      pointsToNext: 0
    };
  }

  const tierRange = nextTier.minEdge - currentTier.minEdge;
  const progressInTier = edgePoints - currentTier.minEdge;
  const progress = Math.min(100, Math.round((progressInTier / tierRange) * 100));

  return {
    current: edgePoints,
    currentTier,
    nextTier,
    progress,
    pointsToNext: nextTier.minEdge - edgePoints
  };
}

/**
 * Format Edge points for display
 */
export function formatEdge(points: number): string {
  if (points >= 10000) {
    return `${(points / 1000).toFixed(1)}K`;
  }
  if (points >= 1000) {
    return `${(points / 1000).toFixed(1)}K`;
  }
  return points.toString();
}

/**
 * Animation constants for Edge displays
 */
export const EDGE_ANIMATION = {
  countDuration: 1500,
  popDelay: 200,
  glowDuration: 500,
  progressDuration: 1000,
} as const;

export default {
  EDGE_TERMS,
  EDGE_VALUES,
  EDGE_TIERS,
  EDGE_ANIMATION,
  getEdgeTier,
  getEdgeProgress,
  formatEdge,
};
