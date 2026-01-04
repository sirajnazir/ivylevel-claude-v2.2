/**
 * IvyQuest v10.0 Feature Flags
 * SIMPLIFIED: 3 master flags + 3 enhancement flags
 * Testing matrix: 8 core combinations (down from 512)
 * @version 10.0
 */

export interface FeatureFlags {
  // === CORE FLAGS (3) ===
  v10Agents: boolean;      // Master switch for ALL v10.0 agents
  criScoring: boolean;     // CRI computation + boost reveal
  commandDeck: boolean;    // Post-assessment dashboard

  // === ENHANCEMENT FLAGS (3) ===
  aiChat: boolean;         // Floating AI chat interface
  suggestions: boolean;    // Proactive AI suggestion bubbles
  eventBus: boolean;       // Real-time agent events

  // === LEGACY FLAGS (for backward compatibility) ===
  assessmentAgent: boolean;
  executionAgent: boolean;
  crisisAlchemy: boolean;
  dualView: boolean;
  hitlMode: boolean;
  stateVersioning: boolean;
}

const getEnvBool = (key: string, defaultVal = false): boolean => {
  if (typeof window !== 'undefined') {
    return (window as any).__ENV__?.[key] === 'true' ||
           process.env[`NEXT_PUBLIC_${key}`] === 'true' ||
           defaultVal;
  }
  return process.env[key] === 'true' ||
         process.env[`NEXT_PUBLIC_${key}`] === 'true' ||
         defaultVal;
};

export function getFeatureFlags(): FeatureFlags {
  const v10Agents = getEnvBool('ENABLE_V10_AGENTS') || getEnvBool('ENABLE_AGENTS');

  return {
    // Core flags
    v10Agents,
    criScoring: getEnvBool('ENABLE_CRI_SCORING') || getEnvBool('ENABLE_CRI_COMPUTATION'),
    commandDeck: getEnvBool('ENABLE_COMMAND_DECK'),

    // Enhancement flags (default to true when agents enabled)
    aiChat: getEnvBool('ENABLE_AI_CHAT', false),
    suggestions: getEnvBool('ENABLE_SUGGESTIONS', v10Agents),
    eventBus: getEnvBool('ENABLE_EVENT_BUS', v10Agents),

    // Legacy flags (for backward compatibility)
    assessmentAgent: getEnvBool('ENABLE_ASSESSMENT_AGENT') || v10Agents,
    executionAgent: getEnvBool('ENABLE_EXECUTION_AGENT') || v10Agents,
    crisisAlchemy: getEnvBool('ENABLE_CRISIS_ALCHEMY') || v10Agents,
    dualView: getEnvBool('ENABLE_DUAL_VIEW') || v10Agents,
    hitlMode: getEnvBool('ENABLE_HITL_MODE'),
    stateVersioning: getEnvBool('ENABLE_STATE_VERSIONING'),
  };
}

export function useFeatureFlag(flag: keyof FeatureFlags): boolean {
  return getFeatureFlags()[flag];
}

export function getActiveAgents(): string[] {
  const flags = getFeatureFlags();
  if (!flags.v10Agents) return [];

  return ['assessment', 'execution', 'gameplan', 'awards', 'opportunity', 'crisis', 'narrative', 'cri'];
}

export function isAgentActive(name: string): boolean {
  return getActiveAgents().includes(name);
}

export function getPostAssessmentRoute(): string {
  return getFeatureFlags().commandDeck ? '/dashboard' : '/results';
}

/**
 * Check if a specific feature is enabled
 */
export function isFeatureEnabled(feature: keyof FeatureFlags): boolean {
  const flags = getFeatureFlags();

  // Master switch check for agent-related features
  if (feature !== 'v10Agents' && feature !== 'criScoring' && feature !== 'commandDeck') {
    if (!flags.v10Agents) return false;
  }

  return flags[feature];
}

/**
 * Get agent service URL
 */
export function getAgentServiceUrl(): string {
  return process.env.AGENT_SERVICE_URL || 'http://localhost:8001';
}

/**
 * Get configuration for Strategic Overwhelm
 */
export function getOverwhelmConfig(): { factor: number; targetCompletion: number } {
  return {
    factor: parseFloat(process.env.OVERWHELM_FACTOR || '1.4'),
    targetCompletion: parseFloat(process.env.TARGET_COMPLETION_RATE || '0.73'),
  };
}

/**
 * Get configuration for HITL (Human-in-the-Loop)
 */
export function getHitlConfig(): { timeoutHours: number; autoApproveLoUrgency: boolean } {
  return {
    timeoutHours: parseFloat(process.env.HITL_TIMEOUT_HOURS || '1.0'),
    autoApproveLoUrgency: getEnvBool('HITL_AUTO_APPROVE_LOW_URGENCY'),
  };
}

// Environment variable documentation
export const ENV_VARS = {
  // Core
  ENABLE_V10_AGENTS: 'Master switch for all v10.0 agents',
  ENABLE_CRI_SCORING: 'CRI computation and Frame 5 boost reveal',
  ENABLE_COMMAND_DECK: 'Post-assessment dashboard at /dashboard',
  // Enhancement
  ENABLE_AI_CHAT: 'Floating AI chat interface (default: false)',
  ENABLE_SUGGESTIONS: 'Proactive AI suggestion bubbles (default: true when agents on)',
  ENABLE_EVENT_BUS: 'Real-time agent event communication (default: true when agents on)',
} as const;

// Export types
export type FeatureFlagKey = keyof FeatureFlags;
