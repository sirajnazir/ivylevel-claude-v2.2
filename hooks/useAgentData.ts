// IvyQuest Agent Data Hooks
// File: hooks/useAgentData.ts

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentApi } from '@/lib/api/agentClient';
import type {
  NarrativeDNA,
  AssessmentResult,
  GamePlanResult,
  FilteredActivitiesData,
  IdentitySeedsData,
  AwardPortfolio,
  AwardMatch,
  OpportunityMatch,
  OpportunityAlert,
  BackupCascade,
  ExecutionDebtScore,
  BlockersData,
  MicroEditResult,
  EssayAnalysis,
  AgentHealthResponse,
} from '@/lib/types/agents';

// Assessment Hooks
export function useAssessmentEnhancement(profileId: string | null) {
  return useQuery({
    queryKey: ['assessment', 'enhance', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.enhanceAssessment(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as AssessmentResult;
    },
    enabled: !!profileId,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}

export function useNarrativeDNA(profileId: string | null) {
  return useQuery({
    queryKey: ['assessment', 'narrative', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.synthesizeNarrativeDNA(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as NarrativeDNA;
    },
    enabled: !!profileId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useEnhanceAssessmentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ profileId, data }: { profileId: string; data?: Record<string, unknown> }) => {
      const result = await agentApi.enhanceAssessment(profileId, data);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['assessment', 'enhance', variables.profileId], data);
    },
  });
}

// Game Plan Hooks
export function useGamePlan(profileId: string | null) {
  return useQuery({
    queryKey: ['gameplan', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.generateGamePlan(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as GamePlanResult;
    },
    enabled: !!profileId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFilteredActivities(profileId: string | null) {
  return useQuery({
    queryKey: ['gameplan', 'activities', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.getFilteredActivities(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as FilteredActivitiesData;
    },
    enabled: !!profileId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useIdentitySeeds(profileId: string | null) {
  return useQuery({
    queryKey: ['gameplan', 'seeds', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.getIdentitySeeds(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as IdentitySeedsData;
    },
    enabled: !!profileId,
    staleTime: 5 * 60 * 1000,
  });
}

// Execution Hooks
export function useExecutionDebtScore(profileId: string | null) {
  return useQuery({
    queryKey: ['execution', 'eds', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.getExecutionDebtScore(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as ExecutionDebtScore;
    },
    enabled: !!profileId,
    staleTime: 2 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  });
}

export function useBlockers(profileId: string | null) {
  return useQuery({
    queryKey: ['execution', 'blockers', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.getBlockers(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as BlockersData;
    },
    enabled: !!profileId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useHandleCrisisMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: { profile_id: string; crisis_type: string; description: string; urgency?: number }) => {
      const result = await agentApi.handleCrisis(input);
      if (!result.success) throw new Error(result.error);
      return result.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['execution', variables.profile_id] });
    },
  });
}

// Awards Hooks
export function useAwardMatches(profileId: string | null) {
  return useQuery({
    queryKey: ['awards', 'match', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.matchAwards(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as { matches: AwardMatch[]; portfolio: AwardPortfolio; timeline: any[]; summary: any };
    },
    enabled: !!profileId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useAwardPortfolio(profileId: string | null) {
  return useQuery({
    queryKey: ['awards', 'portfolio', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.getAwardPortfolio(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as { portfolio: AwardPortfolio };
    },
    enabled: !!profileId,
    staleTime: 10 * 60 * 1000,
  });
}

// Opportunities Hooks
export function useOpportunityMatches(profileId: string | null) {
  return useQuery({
    queryKey: ['opportunities', 'match', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.matchOpportunities(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as { matches: OpportunityMatch[]; alerts: OpportunityAlert[]; backup_cascades: BackupCascade[]; timeline: any[] };
    },
    enabled: !!profileId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useOpportunityAlerts(profileId: string | null) {
  return useQuery({
    queryKey: ['opportunities', 'alerts', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.getOpportunityAlerts(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as { alerts: OpportunityAlert[]; count: number; urgent_count: number };
    },
    enabled: !!profileId,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 10 * 60 * 1000,
  });
}

export function useBackupCascades(profileId: string | null) {
  return useQuery({
    queryKey: ['opportunities', 'cascades', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      const result = await agentApi.getBackupCascades(profileId);
      if (!result.success) throw new Error(result.error);
      return result.data as { cascades: BackupCascade[] };
    },
    enabled: !!profileId,
    staleTime: 10 * 60 * 1000,
  });
}

// Tools Hooks
export function useMicroEdits() {
  return useMutation({
    mutationFn: async ({ text, essayType = 'common_app' }: { text: string; essayType?: string }) => {
      const result = await agentApi.applyMicroEdits(text, essayType);
      if (!result.success) throw new Error(result.error);
      return result.data as MicroEditResult;
    },
  });
}

export function useEssayAnalysis() {
  return useMutation({
    mutationFn: async ({ text, essayType = 'common_app' }: { text: string; essayType?: string }) => {
      const result = await agentApi.analyzeEssay(text, essayType);
      if (!result.success) throw new Error(result.error);
      return result.data as EssayAnalysis;
    },
  });
}

export function useDebouncedEssayAnalysis(text: string, delay: number = 1000) {
  const [analysis, setAnalysis] = useState<EssayAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    if (!text || text.length < 50) {
      setAnalysis(null);
      return;
    }
    setIsAnalyzing(true);
    const timer = setTimeout(async () => {
      try {
        const result = await agentApi.analyzeEssay(text);
        if (result.success && result.data) {
          setAnalysis(result.data as EssayAnalysis);
        }
      } catch (error) {
        console.error('Essay analysis error:', error);
      } finally {
        setIsAnalyzing(false);
      }
    }, delay);
    return () => clearTimeout(timer);
  }, [text, delay]);

  return { analysis, isAnalyzing };
}

// Health Check
export function useAgentHealth() {
  return useQuery({
    queryKey: ['agent', 'health'],
    queryFn: async () => {
      const result = await agentApi.checkAgentHealth();
      if (!result.success) throw new Error(result.error);
      return result.data as AgentHealthResponse;
    },
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
    retry: 3,
  });
}

// Combined Dashboard Hook
export function useDashboardData(profileId: string | null) {
  const assessment = useAssessmentEnhancement(profileId);
  const gamePlan = useGamePlan(profileId);
  const awards = useAwardMatches(profileId);
  const opportunities = useOpportunityMatches(profileId);
  const eds = useExecutionDebtScore(profileId);
  const alerts = useOpportunityAlerts(profileId);

  return {
    assessment: assessment.data,
    gamePlan: gamePlan.data,
    awards: awards.data,
    opportunities: opportunities.data,
    eds: eds.data,
    alerts: alerts.data,
    isLoading: assessment.isLoading || gamePlan.isLoading || awards.isLoading || opportunities.isLoading,
    hasError: assessment.isError || gamePlan.isError || awards.isError || opportunities.isError,
    refetchAll: () => {
      assessment.refetch();
      gamePlan.refetch();
      awards.refetch();
      opportunities.refetch();
      eds.refetch();
      alerts.refetch();
    },
  };
}

// ============================================================
// v13.3 NOTIFICATION HOOKS
// ============================================================

import { agentV13Api } from '@/lib/api/agentV13Client';

export function useNotifications(profileId: string | null, limit: number = 20) {
  return useQuery({
    queryKey: ['notifications', profileId, limit],
    queryFn: async () => {
      if (!profileId) return null;
      return await agentV13Api.getNotifications(profileId, limit);
    },
    enabled: !!profileId,
    staleTime: 30 * 1000,      // 30 seconds
    refetchInterval: 60 * 1000, // 1 minute
  });
}

export function useNotificationCount(profileId: string | null) {
  return useQuery({
    queryKey: ['notification-count', profileId],
    queryFn: async () => {
      if (!profileId) return null;
      return await agentV13Api.getNotificationCount(profileId);
    },
    enabled: !!profileId,
    staleTime: 30 * 1000,      // 30 seconds
    refetchInterval: 30 * 1000, // 30 seconds (more frequent for count)
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ profileId, notificationId }: { profileId: string; notificationId: string }) => {
      return await agentV13Api.markNotificationRead(profileId, notificationId);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['notifications', variables.profileId] });
      queryClient.invalidateQueries({ queryKey: ['notification-count', variables.profileId] });
    },
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (profileId: string) => {
      return await agentV13Api.markAllNotificationsRead(profileId);
    },
    onSuccess: (_, profileId) => {
      queryClient.invalidateQueries({ queryKey: ['notifications', profileId] });
      queryClient.invalidateQueries({ queryKey: ['notification-count', profileId] });
    },
  });
}

// ============================================================
// v13.3 HEALTH HOOK
// ============================================================

export function useAgentV13Health() {
  return useQuery({
    queryKey: ['agent-v13-health'],
    queryFn: async () => {
      return await agentV13Api.checkHealth();
    },
    staleTime: 30 * 1000,      // 30 seconds
    refetchInterval: 60 * 1000, // 1 minute
    retry: 3,
  });
}

// ============================================================
// v13.3 PROFILE EVOLUTION HOOK
// ============================================================

export function useProfileEvolution(profileId: string | null, days: number = 90) {
  return useQuery({
    queryKey: ['profile-evolution', profileId, days],
    queryFn: async () => {
      if (!profileId) return null;
      return await agentV13Api.getProfileEvolution(profileId, days);
    },
    enabled: !!profileId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ============================================================
// v13.3 COMBINED DASHBOARD V13 HOOK
// ============================================================

export function useDashboardV13Data(profileId: string | null) {
  const queryClient = useQueryClient();

  const narrativeDna = useNarrativeDNA(profileId);
  const gamePlan = useGamePlan(profileId);
  const eds = useExecutionDebtScore(profileId);
  const awards = useAwardMatches(profileId);
  const opportunities = useOpportunityAlerts(profileId);
  const notifications = useNotificationCount(profileId);

  const isLoading =
    narrativeDna.isLoading ||
    gamePlan.isLoading ||
    eds.isLoading ||
    awards.isLoading ||
    opportunities.isLoading;

  const refetchAll = useCallback(() => {
    if (!profileId) return;
    queryClient.invalidateQueries({ queryKey: ['assessment', 'narrative', profileId] });
    queryClient.invalidateQueries({ queryKey: ['gameplan', profileId] });
    queryClient.invalidateQueries({ queryKey: ['execution', 'eds', profileId] });
    queryClient.invalidateQueries({ queryKey: ['awards', 'match', profileId] });
    queryClient.invalidateQueries({ queryKey: ['opportunities', 'alerts', profileId] });
    queryClient.invalidateQueries({ queryKey: ['notification-count', profileId] });
  }, [profileId, queryClient]);

  return {
    narrativeDna,
    gamePlan,
    eds,
    awards,
    opportunities,
    notifications,
    isLoading,
    refetchAll,
  };
}
