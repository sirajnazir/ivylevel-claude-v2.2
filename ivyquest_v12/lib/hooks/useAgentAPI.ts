/**
 * IvyQuest Agent API Hooks
 * Type-safe hooks for communicating with v10.0 backend agents.
 * @version 10.0
 */

import { useState, useCallback } from 'react';
import { getFeatureFlags, isAgentActive } from '@/lib/config/featureFlags';
import { emit } from '@/lib/events/eventBus';

// ============================================================================
// TYPES
// ============================================================================

export interface AgentResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp?: string;
}

export interface AgentState<T> {
  loading: boolean;
  error: string | null;
  data: T | null;
}

// CRI Agent
export interface CRIAgentResponse {
  cri: number;
  boost_percentage: number;
  boost_factors: string[];
  status: 'exceptional' | 'strong' | 'moderate' | 'baseline';
}

// Narrative Agent
export interface NarrativeAgentResponse {
  narrative_dna: string;
  themes: string[];
  archetype: string;
  archetype_description: string;
  identity_seeds: string[];
}

// Assessment Agent
export interface AssessmentAgentResponse {
  category_scores: {
    aptitude: number;
    passion: number;
    service: number;
    identity: number;
  };
  overall_score: number;
  tier: 'fresh_start' | 'emerging' | 'optimization' | 'competitive';
  strengths: string[];
  gaps: string[];
}

// Game Plan Agent
export interface GamePlanAction {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  phase: 'immediate' | 'short_term' | 'long_term';
  impact_score: number;
  time_estimate: string;
  tips?: string[];
  resources?: string[];
}

export interface GamePlanAgentResponse {
  actions: GamePlanAction[];
  quick_wins: GamePlanAction[];
  total_actions: number;
}

// Execution Agent
export interface Microstep {
  id: string;
  title: string;
  completed: boolean;
  due_date?: string;
}

export interface Blocker {
  id: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  suggested_resolution: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'blocked' | 'completed';
  progress_percentage: number;
  microsteps: Microstep[];
  eds_score: number;
  blockers: Blocker[];
}

export interface ExecutionAgentResponse {
  projects: Project[];
  overall_eds: number;
  active_blockers: number;
  next_actions: Microstep[];
}

// Crisis Agent
export interface CrisisStep {
  completed: boolean;
  message?: string;
  action?: string;
  duration_minutes?: number;
  opportunity_angle?: string;
  activity?: { name: string; description: string; first_step: string };
}

export interface CrisisAlchemyResponse {
  crisis_id: string;
  title: string;
  description: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  status: 'detected' | 'proposed' | 'approved' | 'resolved' | 'escalated';
  steps: {
    validate: CrisisStep;
    act: CrisisStep;
    reframe: CrisisStep;
    create: CrisisStep;
  };
  approval_deadline?: string;
}

// Awards Agent
export interface Award {
  id: string;
  name: string;
  category: string;
  deadline: string;
  deadline_days: number;
  amount?: number;
  win_probability: number;
  roi: 'high' | 'medium' | 'low';
  effort_hours: number;
  requirements: string[];
  match_reasons: string[];
}

export interface AwardsAgentResponse {
  matched_awards: Award[];
  total_matches: number;
  high_priority_count: number;
}

// Opportunity Agent
export interface Opportunity {
  id: string;
  name: string;
  type: 'summer_program' | 'internship' | 'research' | 'competition' | 'conference';
  organization: string;
  deadline: string;
  deadline_days: number;
  fit_score: number;
  requires_application: boolean;
  cost?: number;
  location?: string;
  description: string;
  match_reasons: string[];
}

export interface OpportunityAgentResponse {
  opportunities: Opportunity[];
  total_matches: number;
  by_type: Record<string, number>;
  upcoming_alerts: Opportunity[];
}

// Chat Agent
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface ChatAgentResponse {
  response: string;
  suggestions?: string[];
  context_used?: string[];
}

// ============================================================================
// BASE HOOK
// ============================================================================

export function useAgentAPI<TInput, TOutput>(agentType: string) {
  const [state, setState] = useState<AgentState<TOutput>>({
    loading: false,
    error: null,
    data: null,
  });

  const invoke = useCallback(async (payload: TInput): Promise<AgentResponse<TOutput>> => {
    const flags = getFeatureFlags();
    
    if (!flags.v10Agents) {
      return { success: false, error: 'v10 agents not enabled' };
    }

    if (!isAgentActive(agentType)) {
      return { success: false, error: `Agent '${agentType}' not active` };
    }

    setState(prev => ({ ...prev, loading: true, error: null }));
    emit('agent.loading', { agent: agentType }, agentType);

    try {
      const response = await fetch(`/api/agents/${agentType}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Request-ID': crypto.randomUUID(),
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setState({ loading: false, error: null, data: result.data });
        emit('agent.success', { agent: agentType, data: result.data }, agentType);
        return { success: true, data: result.data, timestamp: result.timestamp };
      } else {
        const errorMsg = result.error || `Request failed: ${response.status}`;
        setState({ loading: false, error: errorMsg, data: null });
        emit('agent.error', { agent: agentType, error: errorMsg }, agentType);
        return { success: false, error: errorMsg };
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setState({ loading: false, error: message, data: null });
      emit('agent.error', { agent: agentType, error: message }, agentType);
      return { success: false, error: message };
    }
  }, [agentType]);

  const reset = useCallback(() => {
    setState({ loading: false, error: null, data: null });
  }, []);

  return { ...state, invoke, reset };
}

// ============================================================================
// SPECIALIZED HOOKS
// ============================================================================

export function useCRIAgent() {
  return useAgentAPI<{ profile: any }, CRIAgentResponse>('cri');
}

export function useNarrativeAgent() {
  return useAgentAPI<{ profile: any }, NarrativeAgentResponse>('narrative');
}

export function useAssessmentAgent() {
  return useAgentAPI<{ profile: any }, AssessmentAgentResponse>('assessment');
}

export function useGamePlanAgent() {
  return useAgentAPI<{ profile: any; scores?: any }, GamePlanAgentResponse>('gameplan');
}

export function useExecutionAgent() {
  return useAgentAPI<{ profile: any; project_ids?: string[] }, ExecutionAgentResponse>('execution');
}

export function useCrisisAgent() {
  return useAgentAPI<{ profile: any; crisis_type?: string }, CrisisAlchemyResponse>('crisis');
}

export function useAwardsAgent() {
  return useAgentAPI<{ profile: any }, AwardsAgentResponse>('awards');
}

export function useOpportunityAgent() {
  return useAgentAPI<{ profile: any; months_ahead?: number }, OpportunityAgentResponse>('opportunity');
}

export function useChatAgent() {
  return useAgentAPI<{ message: string; history?: ChatMessage[] }, ChatAgentResponse>('chat');
}

// ============================================================================
// COMBINED HOOKS
// ============================================================================

export function useProfileRevealData() {
  const criAgent = useCRIAgent();
  const narrativeAgent = useNarrativeAgent();

  const fetchAll = useCallback(async (profile: any) => {
    const [criResult, narrativeResult] = await Promise.all([
      criAgent.invoke({ profile }),
      narrativeAgent.invoke({ profile }),
    ]);

    return {
      cri: criResult,
      narrative: narrativeResult,
      allSuccess: criResult.success && narrativeResult.success,
    };
  }, []);

  return {
    loading: criAgent.loading || narrativeAgent.loading,
    error: criAgent.error || narrativeAgent.error,
    criData: criAgent.data,
    narrativeData: narrativeAgent.data,
    fetchAll,
  };
}

export function useCommandDeckData() {
  const executionAgent = useExecutionAgent();
  const awardsAgent = useAwardsAgent();
  const opportunityAgent = useOpportunityAgent();

  const fetchAll = useCallback(async (profile: any) => {
    const [execResult, awardsResult, oppResult] = await Promise.all([
      executionAgent.invoke({ profile }),
      awardsAgent.invoke({ profile }),
      opportunityAgent.invoke({ profile, months_ahead: 6 }),
    ]);

    return {
      execution: execResult,
      awards: awardsResult,
      opportunities: oppResult,
      allSuccess: execResult.success && awardsResult.success && oppResult.success,
    };
  }, []);

  return {
    loading: executionAgent.loading || awardsAgent.loading || opportunityAgent.loading,
    executionData: executionAgent.data,
    awardsData: awardsAgent.data,
    opportunitiesData: opportunityAgent.data,
    fetchAll,
  };
}
