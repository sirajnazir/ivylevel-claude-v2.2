export const EDGE_TERMS = {
  singular: 'Edge',
  plural: 'Edge',
  verb: 'Build',
  adjective: 'Competitive',
} as const;

export const EDGE_VALUES = {
  frameComplete: 50,
  assessmentComplete: 500,
  actionStart: 5,
  actionComplete: 20,
  quickWinComplete: 30,
  firstAction: 100,
  weeklyStreak: 50,
  essayDraftComplete: 75,
  coachSession: 100,
} as const;

export interface EdgeTier {
  id: string;
  name: string;
  minEdge: number;
  maxEdge: number;
  color: string;
  bgColor: string;
}

export const EDGE_TIERS: EdgeTier[] = [
  { id: 'starter', name: 'Getting Started', minEdge: 0, maxEdge: 249, color: '#6B7280', bgColor: '#F3F4F6' },
  { id: 'building', name: 'Building Momentum', minEdge: 250, maxEdge: 749, color: '#2563EB', bgColor: '#DBEAFE' },
  { id: 'advancing', name: 'Advancing', minEdge: 750, maxEdge: 1499, color: '#059669', bgColor: '#D1FAE5' },
  { id: 'competitive', name: 'Competitive', minEdge: 1500, maxEdge: 2999, color: '#D97706', bgColor: '#FEF3C7' },
  { id: 'elite', name: 'Elite', minEdge: 3000, maxEdge: Infinity, color: '#641432', bgColor: '#FFF5F2' },
];

export function getEdgeTier(edgePoints: number): EdgeTier {
  return EDGE_TIERS.find(tier => edgePoints >= tier.minEdge && edgePoints <= tier.maxEdge) || EDGE_TIERS[0];
}

export function getEdgeProgress(edgePoints: number): { current: number; nextTier: EdgeTier | null; progress: number } {
  const currentTier = getEdgeTier(edgePoints);
  const currentIndex = EDGE_TIERS.findIndex(t => t.id === currentTier.id);
  const nextTier = currentIndex < EDGE_TIERS.length - 1 ? EDGE_TIERS[currentIndex + 1] : null;
  if (!nextTier) return { current: edgePoints, nextTier: null, progress: 100 };
  const tierRange = nextTier.minEdge - currentTier.minEdge;
  const progressInTier = edgePoints - currentTier.minEdge;
  return { current: edgePoints, nextTier, progress: Math.min(100, Math.round((progressInTier / tierRange) * 100)) };
}

export function formatEdge(points: number): string {
  return points >= 1000 ? \`\${(points / 1000).toFixed(1)}K\` : points.toString();
}

export const EDGE_ANIMATION = {
  countDuration: 1500,
  popDelay: 200,
  glowDuration: 500,
} as const;
