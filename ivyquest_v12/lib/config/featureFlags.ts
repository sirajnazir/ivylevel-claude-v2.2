/**
 * Feature Flags - v12.0
 * Includes tabbed dashboard flag
 */

export interface FeatureFlags {
  // Core v10 flags
  v10Agents: boolean;
  criScoring: boolean;
  commandDeck: boolean;
  // Enhancement flags
  aiChat: boolean;
  suggestions: boolean;
  eventBus: boolean;
  // v11 flags
  edgePoints: boolean;
  svgIcons: boolean;
  // v12 flags
  tabbedDashboard: boolean;
}

const defaultFlags: FeatureFlags = {
  v10Agents: true,
  criScoring: true,
  commandDeck: true,
  aiChat: false,
  suggestions: true,
  eventBus: true,
  edgePoints: true,
  svgIcons: true,
  tabbedDashboard: true,
};

export function getFeatureFlags(): FeatureFlags {
  if (typeof window === 'undefined') return defaultFlags;
  
  return {
    v10Agents: process.env.NEXT_PUBLIC_ENABLE_V10_AGENTS !== 'false',
    criScoring: process.env.NEXT_PUBLIC_ENABLE_CRI_SCORING !== 'false',
    commandDeck: process.env.NEXT_PUBLIC_ENABLE_COMMAND_DECK !== 'false',
    aiChat: process.env.NEXT_PUBLIC_ENABLE_AI_CHAT === 'true',
    suggestions: process.env.NEXT_PUBLIC_ENABLE_SUGGESTIONS !== 'false',
    eventBus: process.env.NEXT_PUBLIC_ENABLE_EVENT_BUS !== 'false',
    edgePoints: process.env.NEXT_PUBLIC_ENABLE_EDGE_POINTS !== 'false',
    svgIcons: process.env.NEXT_PUBLIC_ENABLE_SVG_ICONS !== 'false',
    tabbedDashboard: process.env.NEXT_PUBLIC_ENABLE_TABBED_DASHBOARD !== 'false',
  };
}

export function isFeatureEnabled(flag: keyof FeatureFlags): boolean {
  return getFeatureFlags()[flag];
}
