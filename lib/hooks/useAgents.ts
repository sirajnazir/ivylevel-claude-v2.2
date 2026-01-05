/**
 * Multi-Agent System Hooks
 *
 * Connects UI components to the Python agent service
 * Handles Assessment, GamePlan, Awards, and Opportunity agents
 */

'use client';

import { useState, useCallback } from 'react';
import { useSessionStore } from '@/lib/store/useSessionStore';

// =============================================================================
// TYPES
// =============================================================================

interface AgentResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

interface AssessmentEnhanceResult {
  narrative_dna: string;
  narrative_themes: string[];
  archetype: {
    id: string;
    label: string;
    confidence: number;
    rationale: string;
  };
  cri: {
    score: number;
    boost_percentage: number;
    factors: string[];
  };
  hidden_probabilities: Record<string, number>;
}

interface GamePlanResult {
  phases: Array<{
    id: string;
    title: string;
    timeframe: string;
    milestones: Array<{
      id: string;
      title: string;
      status: string;
      deadline: string;
    }>;
  }>;
  strategic_overwhelm_factor: number;
  identity_seeds: string[];
}

interface AwardMatch {
  award_id: string;
  name: string;
  fit_score: number;
  deadline: string;
  category: 'likely' | 'stretch' | 'skip';
  rationale: string;
}

interface OpportunityMatch {
  program_id: string;
  name: string;
  fit_score: number;
  deadline: string;
  category: string;
  advance_alert: string;
}

// =============================================================================
// BASE AGENT HOOK
// =============================================================================

function useAgentBase<T>(endpoint: string) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);

  const sessionId = useSessionStore((s) => s.session_id);
  const setAgentDataLoading = useSessionStore((s) => s.setAgentDataLoading);
  const setAgentDataError = useSessionStore((s) => s.setAgentDataError);

  const callAgent = useCallback(async (body: Record<string, any> = {}): Promise<T | null> => {
    setIsLoading(true);
    setAgentDataLoading(true);
    setError(null);
    setAgentDataError(null);

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          profile_id: sessionId,
          ...body,
        }),
      });

      const result: AgentResponse<T> = await response.json();

      if (!response.ok || !result.success) {
        const errorMsg = result.error || `Agent error: ${response.status}`;
        setError(errorMsg);
        setAgentDataError(errorMsg);
        return null;
      }

      setData(result.data ?? result as any);
      return result.data ?? result as any;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Agent service unavailable';
      setError(message);
      setAgentDataError(message);
      console.error(`[Agent ${endpoint}] Error:`, err);
      return null;
    } finally {
      setIsLoading(false);
      setAgentDataLoading(false);
    }
  }, [endpoint, sessionId, setAgentDataLoading, setAgentDataError]);

  const clearError = useCallback(() => {
    setError(null);
    setAgentDataError(null);
  }, [setAgentDataError]);

  return {
    isLoading,
    error,
    data,
    callAgent,
    clearError,
  };
}

// =============================================================================
// ASSESSMENT AGENT HOOK
// =============================================================================

export function useAssessmentAgent() {
  const { isLoading, error, data, callAgent, clearError } =
    useAgentBase<AssessmentEnhanceResult>('/api/agents/assessment/enhance');

  const setAgentDataCache = useSessionStore((s) => s.setAgentDataCache);

  const enhance = useCallback(async (profileData?: Record<string, any>) => {
    const result = await callAgent({ data: profileData });

    if (result) {
      // Cache in session store
      setAgentDataCache({
        narrativeDna: result.narrative_dna,
        narrativeThemes: result.narrative_themes,
        archetype: result.archetype.id,
        assessmentTier: result.archetype.label,
        cri: result.cri.score,
        criBoostPercentage: result.cri.boost_percentage,
        criFactors: result.cri.factors,
      });
    }

    return result;
  }, [callAgent, setAgentDataCache]);

  return {
    isLoading,
    error,
    result: data,
    enhance,
    clearError,
    // Computed from result
    narrativeDna: data?.narrative_dna ?? null,
    archetype: data?.archetype ?? null,
    cri: data?.cri ?? null,
  };
}

// =============================================================================
// GAMEPLAN AGENT HOOK
// =============================================================================

export function useGamePlanAgent() {
  const { isLoading, error, data, callAgent, clearError } =
    useAgentBase<GamePlanResult>('/api/agents/gameplan/generate');

  const generate = useCallback(async () => {
    return callAgent();
  }, [callAgent]);

  return {
    isLoading,
    error,
    result: data,
    generate,
    clearError,
    phases: data?.phases ?? [],
    strategicOverwhelmFactor: data?.strategic_overwhelm_factor ?? 1.0,
    identitySeeds: data?.identity_seeds ?? [],
  };
}

// =============================================================================
// AWARDS AGENT HOOK
// =============================================================================

export function useAwardsAgent() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [awards, setAwards] = useState<AwardMatch[]>([]);

  const sessionId = useSessionStore((s) => s.session_id);

  const matchAwards = useCallback(async (): Promise<AwardMatch[]> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/agents/awards/match/${sessionId}`);
      const result = await response.json();

      if (!response.ok || !result.success) {
        setError(result.error || 'Failed to match awards');
        return [];
      }

      setAwards(result.awards ?? []);
      return result.awards ?? [];
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Awards agent unavailable';
      setError(message);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  return {
    isLoading,
    error,
    awards,
    matchAwards,
    likelyAwards: awards.filter(a => a.category === 'likely'),
    stretchAwards: awards.filter(a => a.category === 'stretch'),
  };
}

// =============================================================================
// OPPORTUNITIES AGENT HOOK
// =============================================================================

export function useOpportunitiesAgent() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [opportunities, setOpportunities] = useState<OpportunityMatch[]>([]);

  const sessionId = useSessionStore((s) => s.session_id);

  const matchOpportunities = useCallback(async (): Promise<OpportunityMatch[]> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/agents/opportunities/match/${sessionId}`);
      const result = await response.json();

      if (!response.ok || !result.success) {
        setError(result.error || 'Failed to match opportunities');
        return [];
      }

      setOpportunities(result.opportunities ?? []);
      return result.opportunities ?? [];
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Opportunities agent unavailable';
      setError(message);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  return {
    isLoading,
    error,
    opportunities,
    matchOpportunities,
    summerPrograms: opportunities.filter(o => o.category === 'summer'),
    researchPrograms: opportunities.filter(o => o.category === 'research'),
  };
}

// =============================================================================
// EXECUTION AGENT HOOK (for crisis handling)
// =============================================================================

export function useExecutionAgent() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sessionId = useSessionStore((s) => s.session_id);

  const handleCrisis = useCallback(async (
    crisisType: string,
    description: string,
    urgency: number = 3
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/agents/execution/crisis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_id: sessionId,
          crisis_type: crisisType,
          description,
          urgency,
        }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        setError(result.error || 'Crisis handling failed');
        return null;
      }

      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Execution agent unavailable';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const detectBlockers = useCallback(async () => {
    try {
      const response = await fetch(`/api/agents/execution/blockers/${sessionId}`);
      const result = await response.json();
      return result.blockers ?? [];
    } catch {
      return [];
    }
  }, [sessionId]);

  const getEDS = useCallback(async () => {
    try {
      const response = await fetch(`/api/agents/execution/eds/${sessionId}`);
      const result = await response.json();
      return result;
    } catch {
      return { eds: 0, status: 'unknown' };
    }
  }, [sessionId]);

  return {
    isLoading,
    error,
    handleCrisis,
    detectBlockers,
    getEDS,
  };
}

// =============================================================================
// COMBINED AGENT HOOK (for MultiAgentsTab)
// =============================================================================

export type AgentType = 'strategist' | 'academic' | 'awards' | 'narrative' | 'opportunity';

interface AgentMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agentType?: AgentType;
  timestamp: string;
}

export function useMultiAgentChat() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [activeAgent, setActiveAgent] = useState<AgentType>('strategist');
  const [isProcessing, setIsProcessing] = useState(false);

  const assessmentAgent = useAssessmentAgent();
  const gamePlanAgent = useGamePlanAgent();
  const awardsAgent = useAwardsAgent();
  const opportunitiesAgent = useOpportunitiesAgent();

  const sendMessage = useCallback(async (content: string): Promise<void> => {
    // Add user message
    const userMessage: AgentMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      let response: string;

      // Route to appropriate agent based on activeAgent
      switch (activeAgent) {
        case 'strategist':
          await gamePlanAgent.generate();
          response = gamePlanAgent.result
            ? `I've analyzed your profile and created a strategic plan with ${gamePlanAgent.phases.length} phases. Let me walk you through the key milestones...`
            : 'Let me analyze your profile to create a strategic plan.';
          break;

        case 'academic':
          await assessmentAgent.enhance();
          response = assessmentAgent.result
            ? `Based on your profile, I see you as a "${assessmentAgent.archetype?.label}". Your CRI score is ${assessmentAgent.cri?.score}%.`
            : 'Let me assess your academic profile.';
          break;

        case 'awards':
          await awardsAgent.matchAwards();
          response = awardsAgent.awards.length > 0
            ? `I've found ${awardsAgent.awards.length} awards that match your profile. ${awardsAgent.likelyAwards.length} are likely wins.`
            : 'Let me find awards that match your profile.';
          break;

        case 'opportunity':
          await opportunitiesAgent.matchOpportunities();
          response = opportunitiesAgent.opportunities.length > 0
            ? `I've identified ${opportunitiesAgent.opportunities.length} programs that fit your profile.`
            : 'Let me find opportunities for you.';
          break;

        case 'narrative':
          await assessmentAgent.enhance();
          response = assessmentAgent.narrativeDna
            ? `Your Narrative DNA: "${assessmentAgent.narrativeDna}". This captures your unique story arc.`
            : 'Let me help you develop your personal narrative.';
          break;

        default:
          response = 'How can I help you today?';
      }

      // Add assistant message
      const assistantMessage: AgentMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response,
        agentType: activeAgent,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch {
      const errorMessage: AgentMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'I encountered an error. Please try again.',
        agentType: activeAgent,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  }, [activeAgent, assessmentAgent, gamePlanAgent, awardsAgent, opportunitiesAgent]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    activeAgent,
    setActiveAgent,
    isProcessing,
    sendMessage,
    clearMessages,
  };
}
