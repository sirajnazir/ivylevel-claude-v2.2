/**
 * useUserData Hook
 *
 * Handles loading and syncing user data between Supabase and local Zustand stores.
 * - On login: Loads assessment and game plan data from Supabase into stores
 * - On assessment complete: Saves to Supabase (if feature flag enabled)
 * - Provides sync status and error handling
 */

'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useAuth } from '@/lib/auth/AuthProvider';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { useResultsStore } from '@/lib/store/useResultsStore';
import { useSessionStore } from '@/lib/store/useSessionStore';
import {
  loadLatestAssessment,
  saveAssessment,
  calculateCompleteness,
} from '@/lib/services/assessmentService';
import {
  loadActiveGamePlan,
  saveGamePlan,
} from '@/lib/services/gamePlanService';
import type { StudentProfile, AssessmentResults, IvyReadyScore } from '@/lib/types/student';

// =============================================================================
// Types
// =============================================================================

export interface UserDataState {
  isLoading: boolean;
  isLoaded: boolean;
  isSaving: boolean;
  error: string | null;
  lastSyncedAt: string | null;
  hasSupabaseData: boolean;
  // Loaded game plan from Supabase
  gamePlanData: {
    planData: Record<string, unknown> | null;
    targetTier: string | null;
    currentPhase: string | null;
    currentWeek: number;
    completionPercentage: number;
  } | null;
}

export interface UseUserDataReturn extends UserDataState {
  loadUserData: () => Promise<void>;
  saveUserData: () => Promise<boolean>;
  syncStatus: 'idle' | 'loading' | 'saving' | 'synced' | 'error';
}

// =============================================================================
// Feature Flag
// =============================================================================

// Check if Supabase persistence is enabled
const ENABLE_SUPABASE_PERSISTENCE =
  process.env.NEXT_PUBLIC_ENABLE_SUPABASE_PERSISTENCE === 'true';

// =============================================================================
// Hook Implementation
// =============================================================================

export function useUserData(): UseUserDataReturn {
  const { user, isAuthenticated, isReady } = useAuth();
  const loadProfile = useStudentStore((s) => s.loadProfile);
  const getProfile = useStudentStore((s) => s.getProfile);
  const setResults = useResultsStore((s) => s.setResults);
  const results = useResultsStore((s) => s.results);
  const sessionId = useSessionStore((s) => s.session_id);
  const setAssessmentComplete = useSessionStore((s) => s.setAssessmentComplete);

  // State
  const [state, setState] = useState<UserDataState>({
    isLoading: false,
    isLoaded: false,
    isSaving: false,
    error: null,
    lastSyncedAt: null,
    hasSupabaseData: false,
    gamePlanData: null,
  });

  // Prevent multiple loads
  const hasLoadedRef = useRef(false);
  const loadingRef = useRef(false);

  // ==========================================================================
  // Load User Data from Supabase
  // ==========================================================================

  const loadUserData = useCallback(async () => {
    if (!user?.id || loadingRef.current) {
      return;
    }

    loadingRef.current = true;
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      console.log('[useUserData] Loading data for user:', user.id);

      // Load assessment data
      const assessmentResult = await loadLatestAssessment(user.id);

      if (assessmentResult.success && assessmentResult.data) {
        console.log('[useUserData] Found assessment data, loading into stores');

        // Load profile into student store
        if (assessmentResult.data.profile) {
          loadProfile(assessmentResult.data.profile as StudentProfile);
        }

        // Load scores into results store
        if (assessmentResult.data.scores) {
          // Construct AssessmentResults from scores
          const scores = assessmentResult.data.scores;
          const ivyReadyScore: IvyReadyScore = {
            total_score: scores.overall ?? scores.ivy_ready_score ?? 0,
            category_scores: {
              aptitude: scores.aptitude ?? 0,
              passion: scores.passion ?? 0,
              community: scores.community ?? 0,
              narrative: scores.identity ?? 0,
            },
            percentile_rank: 50, // Default percentile
          };
          const assessmentResults: Partial<AssessmentResults> = {
            ivy_ready_score: ivyReadyScore,
            archetype_detected: assessmentResult.data.archetype || undefined,
            archetype_label: assessmentResult.data.archetype || '',
            school_probabilities: [],
            helping_factors: [],
            holding_back_factors: [],
            narrative_tagline: '',
          };
          setResults(assessmentResults as AssessmentResults);
        }

        // Mark assessment as complete if we have a completed_at timestamp
        if (assessmentResult.data.completedAt) {
          console.log('[useUserData] Marking assessment as complete');
          setAssessmentComplete(true);
        }

        setState((prev) => ({
          ...prev,
          hasSupabaseData: true,
          lastSyncedAt: assessmentResult.data?.completedAt || null,
        }));
      } else {
        console.log('[useUserData] No assessment data found in Supabase');
      }

      // Load game plan data
      const gamePlanResult = await loadActiveGamePlan(user.id);

      let loadedGamePlan = null;
      if (gamePlanResult.success && gamePlanResult.data) {
        console.log('[useUserData] Found game plan data:', gamePlanResult.data);
        loadedGamePlan = {
          planData: gamePlanResult.data.planData as Record<string, unknown> | null,
          targetTier: gamePlanResult.data.targetArchetype,
          currentPhase: gamePlanResult.data.currentPhase,
          currentWeek: gamePlanResult.data.currentWeek,
          completionPercentage: gamePlanResult.data.completionPercentage,
        };
      }

      setState((prev) => ({
        ...prev,
        isLoading: false,
        isLoaded: true,
        gamePlanData: loadedGamePlan,
      }));

      hasLoadedRef.current = true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load user data';
      console.error('[useUserData] Load error:', errorMessage);
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    } finally {
      loadingRef.current = false;
    }
  }, [user?.id, loadProfile, setResults]);

  // ==========================================================================
  // Save User Data to Supabase
  // ==========================================================================

  const saveUserData = useCallback(async (): Promise<boolean> => {
    if (!ENABLE_SUPABASE_PERSISTENCE) {
      console.log('[useUserData] Supabase persistence disabled, skipping save');
      return true;
    }

    if (!user?.id) {
      console.log('[useUserData] No user ID, skipping save');
      return false;
    }

    setState((prev) => ({ ...prev, isSaving: true, error: null }));

    try {
      const profile = getProfile();
      const currentResults = results;

      // Build scores object
      const scores = currentResults?.ivy_ready_score
        ? {
            aptitude: currentResults.ivy_ready_score.category_scores.aptitude,
            passion: currentResults.ivy_ready_score.category_scores.passion,
            community: currentResults.ivy_ready_score.category_scores.community,
            identity: currentResults.ivy_ready_score.category_scores.narrative,
            overall: currentResults.ivy_ready_score.total_score,
            ivy_ready_score: currentResults.ivy_ready_score.total_score,
          }
        : {
            aptitude: 0,
            passion: 0,
            community: 0,
            identity: 0,
            overall: 0,
            ivy_ready_score: 0,
          };

      const result = await saveAssessment({
        userId: user.id,
        sessionId: sessionId || profile.session_id,
        profile,
        scores,
        archetype: currentResults?.archetype_detected,
        completenessScore: calculateCompleteness(profile),
      });

      if (!result.success) {
        throw new Error(result.error || 'Failed to save assessment');
      }

      console.log('[useUserData] Assessment saved successfully');

      setState((prev) => ({
        ...prev,
        isSaving: false,
        lastSyncedAt: new Date().toISOString(),
        hasSupabaseData: true,
      }));

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save user data';
      console.error('[useUserData] Save error:', errorMessage);
      setState((prev) => ({
        ...prev,
        isSaving: false,
        error: errorMessage,
      }));
      return false;
    }
  }, [user?.id, getProfile, results, sessionId]);

  // ==========================================================================
  // Auto-load on Auth Ready
  // ==========================================================================

  useEffect(() => {
    // Only load if:
    // - Auth is ready
    // - User is authenticated
    // - Haven't loaded yet
    // - Supabase persistence is enabled
    if (isReady && isAuthenticated && user?.id && !hasLoadedRef.current && ENABLE_SUPABASE_PERSISTENCE) {
      loadUserData();
    }
  }, [isReady, isAuthenticated, user?.id, loadUserData]);

  // Reset on logout
  useEffect(() => {
    if (isReady && !isAuthenticated) {
      hasLoadedRef.current = false;
      setState({
        isLoading: false,
        isLoaded: false,
        isSaving: false,
        error: null,
        lastSyncedAt: null,
        hasSupabaseData: false,
        gamePlanData: null,
      });
    }
  }, [isReady, isAuthenticated]);

  // ==========================================================================
  // Compute Sync Status
  // ==========================================================================

  const syncStatus = (() => {
    if (state.error) return 'error';
    if (state.isLoading) return 'loading';
    if (state.isSaving) return 'saving';
    if (state.isLoaded || state.hasSupabaseData) return 'synced';
    return 'idle';
  })() as UseUserDataReturn['syncStatus'];

  return {
    ...state,
    loadUserData,
    saveUserData,
    syncStatus,
  };
}

// =============================================================================
// Convenience Hooks
// =============================================================================

/**
 * Hook to save assessment data when it completes
 */
export function useAutoSaveAssessment(isComplete: boolean): void {
  const { saveUserData } = useUserData();
  const hasSavedRef = useRef(false);

  useEffect(() => {
    if (isComplete && !hasSavedRef.current && ENABLE_SUPABASE_PERSISTENCE) {
      hasSavedRef.current = true;
      saveUserData().catch(console.error);
    }
  }, [isComplete, saveUserData]);
}

/**
 * Hook to check if user has existing data in Supabase
 */
export function useHasSupabaseData(): boolean {
  const { hasSupabaseData } = useUserData();
  return hasSupabaseData;
}
