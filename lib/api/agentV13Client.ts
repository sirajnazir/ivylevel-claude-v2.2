/**
 * IvyQuest v13.0 Agent API Client
 * Multi-Agent + ReAct + Memory Platform
 *
 * Extends v2.0 client with:
 * - Memory recall/store operations
 * - HITL workflow management
 * - ReAct agent execution
 * - Event streaming
 */

const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8000';

// ============================================================
// MEMORY TYPES
// ============================================================

export interface MemoryItem {
  id: string;
  agent_id: string;
  profile_id: string;
  content: Record<string, unknown>;
  importance: number;
  tier: 'working' | 'short_term' | 'long_term';
  similarity?: number;
  created_at: string;
  accessed_at?: string;
}

export interface MemoryRecallParams {
  profile_id: string;
  query: string;
  limit?: number;
  min_importance?: number;
  time_weight?: number;
}

export interface MemoryRecallResult {
  memories: MemoryItem[];
  total_count: number;
}

export interface MemoryStoreParams {
  agent_id: string;
  profile_id: string;
  content: Record<string, unknown>;
  importance?: number;
}

export interface MemoryStoreResult {
  memory_id: string;
  stored_at: string;
}

export interface MemoryStats {
  working: {
    count: number;
    limit: number;
    utilization: number;
  };
  short_term: {
    count: number;
    ttl_hours: number;
  };
  long_term: {
    count: number;
    oldest: string;
    newest: string;
  };
}

// ============================================================
// HITL TYPES
// ============================================================

export type WorkflowStatus = 'pending' | 'in_review' | 'approved' | 'rejected' | 'modified' | 'expired';

export interface HITLRequest {
  id: string;
  agent_id: string;
  profile_id: string;
  action_type: string;
  proposed_action: Record<string, unknown>;
  confidence: number;
  reasoning: string;
  status: WorkflowStatus;
  reviewer_id?: string;
  review_notes?: string;
  modified_action?: Record<string, unknown>;
  created_at: string;
  reviewed_at?: string;
}

export interface HITLReviewDecision {
  reviewer_id: string;
  status: WorkflowStatus;
  notes?: string;
  modified_action?: Record<string, unknown>;
}

export interface HITLStats {
  total: number;
  approved: number;
  rejected: number;
  modified: number;
  pending: number;
  auto_approved: number;
  approval_rate: number;
}

// ============================================================
// REACT AGENT TYPES
// ============================================================

export interface AgentRunContext {
  profile_id: string;
  session_id?: string;
  user_id?: string;
  metadata?: Record<string, unknown>;
}

export interface AgentRunResult<T = Record<string, unknown>> {
  success: boolean;
  data: T;
  _metadata: {
    agent_id: string;
    iterations: number;
    final_state: string;
    thought_count: number;
  };
  error?: string;
}

export interface ThoughtLogEntry {
  iteration: number;
  state: string;
  thought: string;
  action_taken?: string;
  observation?: Record<string, unknown>;
  correction?: string;
  timestamp: string;
}

// ============================================================
// EVENT TYPES
// ============================================================

export interface AgentEvent {
  source_agent: string;
  event_type: string;
  payload: Record<string, unknown>;
  profile_id: string;
  timestamp: string;
  correlation_id?: string;
}

// ============================================================
// API CLIENT CLASS
// ============================================================

class AgentV13Client {
  private baseUrl: string;

  constructor(baseUrl: string = AGENT_API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    path: string,
    data?: Record<string, unknown>
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;

    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (data && (method === 'POST' || method === 'PUT')) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to agent service. Is the backend running?');
      }
      throw error;
    }
  }

  // ============================================================
  // REACT AGENT OPERATIONS
  // ============================================================

  /**
   * Run a ReAct agent with full memory and event support.
   */
  async runAgent<T = Record<string, unknown>>(
    agentId: string,
    input: Record<string, unknown>,
    context: AgentRunContext
  ): Promise<AgentRunResult<T>> {
    return this.request('POST', `/v13/agents/${agentId}/run`, {
      input,
      context,
    });
  }

  /**
   * Get the thought log from the most recent agent run.
   */
  async getThoughtLog(
    agentId: string,
    profileId: string
  ): Promise<{ thoughts: ThoughtLogEntry[] }> {
    return this.request(
      'GET',
      `/v13/agents/${agentId}/thoughts?profile_id=${profileId}`
    );
  }

  // ============================================================
  // MEMORY OPERATIONS
  // ============================================================

  /**
   * Semantic search across agent memories.
   */
  async recallMemories(params: MemoryRecallParams): Promise<MemoryRecallResult> {
    const queryParams = new URLSearchParams({
      query: params.query,
      limit: (params.limit || 10).toString(),
    });

    if (params.min_importance !== undefined) {
      queryParams.set('min_importance', params.min_importance.toString());
    }
    if (params.time_weight !== undefined) {
      queryParams.set('time_weight', params.time_weight.toString());
    }

    return this.request(
      'GET',
      `/v13/memory/${params.profile_id}/recall?${queryParams}`
    );
  }

  /**
   * Store a new memory.
   */
  async storeMemory(params: MemoryStoreParams): Promise<MemoryStoreResult> {
    return this.request('POST', '/v13/memory/store', params as unknown as Record<string, unknown>);
  }

  /**
   * Get memory statistics for a profile.
   */
  async getMemoryStats(profileId: string): Promise<MemoryStats> {
    return this.request('GET', `/v13/memory/${profileId}/stats`);
  }

  /**
   * Clear working memory for a profile.
   */
  async clearWorkingMemory(profileId: string): Promise<{ cleared: number }> {
    return this.request('DELETE', `/v13/memory/${profileId}/working`);
  }

  /**
   * Trigger memory consolidation.
   */
  async consolidateMemories(profileId: string): Promise<{ consolidated: number }> {
    return this.request('POST', `/v13/memory/${profileId}/consolidate`, {});
  }

  // ============================================================
  // HITL OPERATIONS
  // ============================================================

  /**
   * Get pending HITL review requests.
   */
  async getPendingReviews(
    profileId?: string,
    agentId?: string
  ): Promise<{ requests: HITLRequest[] }> {
    const params = new URLSearchParams();
    if (profileId) params.set('profile_id', profileId);
    if (agentId) params.set('agent_id', agentId);

    const queryString = params.toString();
    return this.request(
      'GET',
      `/v13/hitl/pending${queryString ? `?${queryString}` : ''}`
    );
  }

  /**
   * Get a specific HITL request by ID.
   */
  async getHITLRequest(requestId: string): Promise<HITLRequest> {
    return this.request('GET', `/v13/hitl/${requestId}`);
  }

  /**
   * Submit a human review decision.
   */
  async submitReview(
    requestId: string,
    decision: HITLReviewDecision
  ): Promise<HITLRequest> {
    return this.request('POST', `/v13/hitl/${requestId}/review`, decision as unknown as Record<string, unknown>);
  }

  /**
   * Mark a request as being actively reviewed.
   */
  async markInReview(
    requestId: string,
    reviewerId: string
  ): Promise<HITLRequest> {
    return this.request('POST', `/v13/hitl/${requestId}/claim`, {
      reviewer_id: reviewerId,
    });
  }

  /**
   * Get HITL request history for a profile.
   */
  async getHITLHistory(
    profileId: string,
    limit: number = 50
  ): Promise<{ requests: HITLRequest[] }> {
    return this.request(
      'GET',
      `/v13/hitl/history/${profileId}?limit=${limit}`
    );
  }

  /**
   * Get HITL statistics.
   */
  async getHITLStats(agentId?: string): Promise<HITLStats> {
    const params = agentId ? `?agent_id=${agentId}` : '';
    return this.request('GET', `/v13/hitl/stats${params}`);
  }

  // ============================================================
  // EVENT OPERATIONS
  // ============================================================

  /**
   * Get event history for a profile.
   */
  async getEventHistory(
    profileId: string,
    eventTypes?: string[],
    limit: number = 100
  ): Promise<{ events: AgentEvent[] }> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (eventTypes?.length) {
      params.set('event_types', eventTypes.join(','));
    }
    return this.request(
      'GET',
      `/v13/events/${profileId}?${params}`
    );
  }

  /**
   * Get correlated events.
   */
  async getCorrelatedEvents(
    correlationId: string
  ): Promise<{ events: AgentEvent[] }> {
    return this.request('GET', `/v13/events/correlation/${correlationId}`);
  }

  // ============================================================
  // HEALTH & STATUS
  // ============================================================

  /**
   * Check v13 service health.
   */
  async checkHealth(): Promise<{
    status: string;
    version: string;
    memory_enabled: boolean;
    hitl_enabled: boolean;
    react_enabled: boolean;
    thresholds?: {
      min_quality: number;
      min_voice: number;
      min_golden: number;
      max_cycles: number;
    };
  }> {
    return this.request('GET', '/v13/health');
  }

  // ============================================================
  // v13.3 NOTIFICATION OPERATIONS
  // ============================================================

  /**
   * Get notifications for a profile.
   * Note: Backend uses /notifications/* not /v13/notifications/*
   */
  async getNotifications(
    profileId: string,
    limit: number = 20,
    unreadOnly: boolean = false
  ): Promise<{
    notifications: Array<{
      id: string;
      type: string;
      title: string;
      message: string;
      read: boolean;
      created_at: string;
      priority?: string;
      source_agent?: string;
    }>;
    total: number;
    unread: number;
  }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      unread_only: unreadOnly.toString(),
    });
    return this.request('GET', `/notifications/${profileId}?${params}`);
  }

  /**
   * Get notification count for a profile.
   * Note: Backend uses /notifications/* not /v13/notifications/*
   */
  async getNotificationCount(profileId: string): Promise<{
    unread_count: number;
    total_count: number;
  }> {
    return this.request('GET', `/notifications/${profileId}/count`);
  }

  /**
   * Mark a notification as read.
   * Note: Backend uses /notifications/* not /v13/notifications/*
   */
  async markNotificationRead(
    profileId: string,
    notificationId: string
  ): Promise<{ success: boolean }> {
    return this.request('POST', `/notifications/mark-read`, {
      profile_id: profileId,
      notification_id: notificationId,
    });
  }

  /**
   * Mark all notifications as read for a profile.
   * Note: Backend uses /notifications/* not /v13/notifications/*
   */
  async markAllNotificationsRead(profileId: string): Promise<{
    success: boolean;
    marked_count: number;
  }> {
    return this.request('POST', `/notifications/${profileId}/mark-all-read`, {});
  }

  // ============================================================
  // v13.3 PROFILE EVOLUTION
  // ============================================================

  /**
   * Get profile evolution history (snapshots over time).
   */
  async getProfileEvolution(
    profileId: string,
    days: number = 90
  ): Promise<{
    snapshots: Array<{
      snapshot_id: string;
      created_at: string;
      ivy_score: number;
      pillar_scores: Record<string, number>;
      milestone?: string;
    }>;
    evolution_summary: {
      score_trend: 'improving' | 'stable' | 'declining';
      biggest_improvement: string;
      focus_area: string;
    };
  }> {
    return this.request('GET', `/v13/profile/${profileId}/evolution?days=${days}`);
  }

  /**
   * Get interaction history for a profile.
   */
  async getInteractionHistory(
    profileId: string,
    limit: number = 20
  ): Promise<{
    interactions: Array<{
      id: string;
      agent_id: string;
      interaction_type: string;
      summary: string;
      created_at: string;
    }>;
  }> {
    return this.request('GET', `/v13/interactions/${profileId}/recent?limit=${limit}`);
  }

  /**
   * Recall interactions by semantic query.
   */
  async recallInteractions(
    profileId: string,
    query: string,
    limit: number = 5
  ): Promise<{
    interactions: Array<{
      id: string;
      agent_id: string;
      summary: string;
      relevance: number;
      created_at: string;
    }>;
  }> {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
    });
    return this.request('GET', `/v13/interactions/${profileId}/recall?${params}`);
  }

  // ============================================================
  // v13.3 AGENT HANDOFF
  // ============================================================

  /**
   * Get handoff context for agent-to-agent communication.
   */
  async getHandoffContext(
    profileId: string,
    toAgent: string
  ): Promise<{
    context: Record<string, unknown>;
    from_agent: string;
    to_agent: string;
    created_at: string;
    ttl_remaining: number;
  }> {
    return this.request('GET', `/v13/memory/handoff/${profileId}/${toAgent}`);
  }

  /**
   * Search knowledge base semantically.
   */
  async searchKnowledge(
    query: string,
    limit: number = 5
  ): Promise<{
    results: Array<{
      id: string;
      content: string;
      relevance: number;
      source: string;
    }>;
  }> {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
    });
    return this.request('GET', `/v13/knowledge/search?${params}`);
  }
}

// ============================================================
// SINGLETON EXPORT
// ============================================================

export const agentV13Api = new AgentV13Client();
export default agentV13Api;

// ============================================================
// REACT HOOKS (for convenience)
// ============================================================

import { useState, useCallback } from 'react';

/**
 * Hook for memory operations.
 */
export function useMemory(profileId: string) {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const recall = useCallback(async (query: string, limit?: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await agentV13Api.recallMemories({
        profile_id: profileId,
        query,
        limit,
      });
      setMemories(result.memories);
      return result.memories;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to recall memories');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [profileId]);

  const store = useCallback(async (
    agentId: string,
    content: Record<string, unknown>,
    importance?: number
  ) => {
    try {
      return await agentV13Api.storeMemory({
        agent_id: agentId,
        profile_id: profileId,
        content,
        importance,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to store memory');
      return null;
    }
  }, [profileId]);

  return { memories, recall, store, isLoading, error };
}

/**
 * Hook for HITL operations.
 */
export function useHITL(profileId?: string) {
  const [requests, setRequests] = useState<HITLRequest[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPending = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await agentV13Api.getPendingReviews(profileId);
      setRequests(result.requests);
      return result.requests;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch HITL requests');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [profileId]);

  const submitReview = useCallback(async (
    requestId: string,
    decision: HITLReviewDecision
  ) => {
    try {
      const result = await agentV13Api.submitReview(requestId, decision);
      setRequests(prev => prev.filter(r => r.id !== requestId));
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit review');
      return null;
    }
  }, []);

  return { requests, fetchPending, submitReview, isLoading, error };
}
