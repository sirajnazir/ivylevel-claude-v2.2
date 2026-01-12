/**
 * IvyQuest v2.0 React Query Hooks
 * Provides data fetching and mutations for v2.0 features
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import agentV2Api, {
  TimeAuditInput,
  WeeklyPlanInput,
  AwardsPortfolioInput,
  NCWITStrategyInput,
  ProgramRecommendInput,
  CrisisAlchemyInput,
} from '../api/agentV2Client';

// ============================================================
// QUERY KEYS
// ============================================================

export const agentV2Keys = {
  all: ['agentV2'] as const,
  health: () => [...agentV2Keys.all, 'health'] as const,
  techniques: () => [...agentV2Keys.all, 'techniques'] as const,
  timeAudit: (profileId?: string) => [...agentV2Keys.all, 'timeAudit', profileId] as const,
  weeklyPlan: (profileId?: string) => [...agentV2Keys.all, 'weeklyPlan', profileId] as const,
  awardsPortfolio: (profileId?: string) => [...agentV2Keys.all, 'awardsPortfolio', profileId] as const,
  ncwitStrategy: (profileId?: string) => [...agentV2Keys.all, 'ncwitStrategy', profileId] as const,
};

// ============================================================
// HEALTH & STATUS HOOKS
// ============================================================

export function useAgentV2Health() {
  return useQuery({
    queryKey: agentV2Keys.health(),
    queryFn: () => agentV2Api.checkHealth(),
    staleTime: 30 * 1000, // 30 seconds
    retry: 1,
    refetchOnWindowFocus: false,
  });
}

export function useJennyTechniques() {
  return useQuery({
    queryKey: agentV2Keys.techniques(),
    queryFn: () => agentV2Api.getJennyTechniques(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ============================================================
// TIME MANAGEMENT HOOKS
// ============================================================

export function useTimeAudit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: TimeAuditInput) => agentV2Api.runTimeAudit(input),
    onSuccess: (data) => {
      // Cache the result
      queryClient.setQueryData(agentV2Keys.timeAudit(), data);
    },
  });
}

export function useWeeklyPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: WeeklyPlanInput) => agentV2Api.generateWeeklyPlan(input),
    onSuccess: (data) => {
      queryClient.setQueryData(agentV2Keys.weeklyPlan(), data);
    },
  });
}

// ============================================================
// AWARDS HOOKS
// ============================================================

export function useAwardsPortfolio() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: AwardsPortfolioInput) => agentV2Api.buildAwardsPortfolio(input),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(agentV2Keys.awardsPortfolio(variables.profile_id), data);
    },
  });
}

// Cached query version (for when you want to persist results)
export function useAwardsPortfolioQuery(profileId: string | undefined, studentProfile: AwardsPortfolioInput['student_profile']) {
  return useQuery({
    queryKey: agentV2Keys.awardsPortfolio(profileId),
    queryFn: () => agentV2Api.buildAwardsPortfolio({
      profile_id: profileId,
      student_profile: studentProfile,
    }),
    enabled: !!profileId && !!studentProfile?.spike,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// ============================================================
// NCWIT STRATEGY HOOKS
// ============================================================

export function useNCWITStrategy() {
  return useMutation({
    mutationFn: (input: NCWITStrategyInput) => agentV2Api.getNCWITStrategy(input),
  });
}

// ============================================================
// OPPORTUNITY HOOKS
// ============================================================

export function useOpportunityRecommendations() {
  return useMutation({
    mutationFn: (input: ProgramRecommendInput) => agentV2Api.recommendOpportunities(input),
  });
}

// ============================================================
// CRISIS ALCHEMY HOOKS
// ============================================================

export function useCrisisAlchemy() {
  return useMutation({
    mutationFn: (input: CrisisAlchemyInput) => agentV2Api.handleCrisis(input),
  });
}

// ============================================================
// JENNY VOICE VALIDATION HOOKS
// ============================================================

export function useJennyVoiceValidation() {
  return useMutation({
    mutationFn: (text: string) => agentV2Api.validateVoice({ text }),
  });
}

// ============================================================
// COMBINED DASHBOARD HOOK
// ============================================================

export function useV2Dashboard(profileId: string | undefined) {
  const health = useAgentV2Health();
  const techniques = useJennyTechniques();

  return {
    isBackendHealthy: health.data?.status === 'healthy',
    backendVersion: health.data?.version,
    techniques: techniques.data?.techniques || [],
    isLoading: health.isLoading,
    error: health.error,
    profileId,
  };
}
