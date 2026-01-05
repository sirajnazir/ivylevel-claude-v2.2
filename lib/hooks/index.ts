/**
 * Hooks Index
 *
 * Re-exports all custom hooks for easy importing
 */

// Scoring hooks
export {
  useScoring,
  useIvyScore,
  useSchoolProbabilities,
  useArchetype,
  useFactors,
} from './useScoring';

// Game Plan hooks
export {
  useGamePlan,
  useGamePlanPhase,
  usePreparationData,
} from './useGamePlan';

// Insights hooks
export {
  useInsights,
  useAutoInsights,
  useTopInsights,
} from './useInsights';

// Agent hooks
export {
  useAssessmentAgent,
  useGamePlanAgent,
  useAwardsAgent,
  useOpportunitiesAgent,
  useExecutionAgent,
  useMultiAgentChat,
} from './useAgents';

export type { AgentType } from './useAgents';

// Existing hooks
export { useNotificationStore } from './useInsightNotifications';
export { usePersistence } from './usePersistence';
export { useClearStaleData } from './useClearStaleData';
export { useAgentAPI } from './useAgentAPI';

// User data sync hooks (Supabase integration)
export {
  useUserData,
  useAutoSaveAssessment,
  useHasSupabaseData,
} from './useUserData';
export type { UserDataState, UseUserDataReturn } from './useUserData';
