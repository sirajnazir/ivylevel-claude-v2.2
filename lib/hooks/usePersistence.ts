/**
 * Assessment Persistence Hook
 *
 * Provides functions to save and load assessment data to/from Supabase.
 * Designed to work alongside Zustand's localStorage persistence.
 */

import { useState, useCallback } from 'react';
import type { StudentProfile } from '@/lib/types/student';
import type { GamePlan } from '@/lib/gamePlan/gamePlanEngine';
import { getProfileTier } from '@/lib/utils/skipLogic';

interface PersistenceState {
  isLoading: boolean;
  isSaving: boolean;
  lastSaved: Date | null;
  error: string | null;
}

interface SaveOptions {
  email?: string;
  gamePlan?: GamePlan;
  scores?: {
    aptitude: number;
    passion: number;
    community: number;
    identity: number;
    overall: number;
  };
  completeness?: number;
  tier?: string;
  archetype?: string;
}

interface PersistenceResult {
  success: boolean;
  persisted: boolean;
  action?: 'created' | 'updated';
  id?: string;
  message?: string;
}

interface LoadResult {
  success: boolean;
  found: boolean;
  data: {
    profile: StudentProfile;
    game_plan: GamePlan | null;
    scores: SaveOptions['scores'] | null;
    completeness: number;
    tier: string | null;
    archetype: string | null;
  } | null;
}

export function usePersistence() {
  const [state, setState] = useState<PersistenceState>({
    isLoading: false,
    isSaving: false,
    lastSaved: null,
    error: null,
  });

  /**
   * Save assessment to Supabase
   */
  const saveAssessment = useCallback(
    async (profile: StudentProfile, options: SaveOptions = {}): Promise<PersistenceResult> => {
      setState((prev) => ({ ...prev, isSaving: true, error: null }));

      try {
        const response = await fetch('/api/assessment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: profile.session_id,
            email: options.email,
            profile,
            game_plan: options.gamePlan,
            scores: options.scores,
            completeness: options.completeness ?? profile.completeness?.score ?? 0,
            tier: options.tier ?? getProfileTier(profile),
            archetype: options.archetype ?? profile.classification?.archetype ?? 'Explorer',
          }),
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || 'Failed to save assessment');
        }

        setState((prev) => ({
          ...prev,
          isSaving: false,
          lastSaved: new Date(),
          error: null,
        }));

        return result;
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({
          ...prev,
          isSaving: false,
          error: message,
        }));
        return {
          success: false,
          persisted: false,
          message,
        };
      }
    },
    []
  );

  /**
   * Load assessment by session ID
   */
  const loadBySessionId = useCallback(async (sessionId: string): Promise<LoadResult> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await fetch(`/api/assessment?session_id=${encodeURIComponent(sessionId)}`);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to load assessment');
      }

      setState((prev) => ({ ...prev, isLoading: false, error: null }));

      return {
        success: true,
        found: result.found,
        data: result.found ? result.data : null,
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: message,
      }));
      return {
        success: false,
        found: false,
        data: null,
      };
    }
  }, []);

  /**
   * Load assessments by email
   */
  const loadByEmail = useCallback(
    async (
      email: string
    ): Promise<{
      success: boolean;
      found: boolean;
      count: number;
      data: LoadResult['data'][];
    }> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await fetch(`/api/assessment?email=${encodeURIComponent(email)}`);
        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || 'Failed to load assessments');
        }

        setState((prev) => ({ ...prev, isLoading: false, error: null }));

        return {
          success: true,
          found: result.found,
          count: result.count || 0,
          data: result.data || [],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: message,
        }));
        return {
          success: false,
          found: false,
          count: 0,
          data: [],
        };
      }
    },
    []
  );

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    saveAssessment,
    loadBySessionId,
    loadByEmail,
    clearError,
  };
}

export default usePersistence;
