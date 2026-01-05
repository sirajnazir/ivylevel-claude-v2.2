/**
 * Scoring API Hook
 *
 * Connects UI components to the real scoring engine via /api/score
 * Manages loading states, errors, and result caching
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { useResultsStore } from '@/lib/store/useResultsStore';
import { useSessionStore } from '@/lib/store/useSessionStore';
import type { StudentProfile, AssessmentResults, SchoolConfig } from '@/lib/types/student';

// =============================================================================
// TYPES
// =============================================================================

interface ScoreResponse {
  success: boolean;
  profile: StudentProfile;
  results: AssessmentResults;
  school_configs: SchoolConfig[];
  timestamp: string;
  error?: string;
}

interface UseScoringReturn {
  // State
  isLoading: boolean;
  error: string | null;
  lastScoredAt: string | null;

  // Actions
  calculateScore: () => Promise<AssessmentResults | null>;
  refreshScore: () => Promise<AssessmentResults | null>;
  clearError: () => void;

  // Results (from store)
  results: AssessmentResults | null;
  schoolConfigs: SchoolConfig[];
}

// =============================================================================
// HOOK IMPLEMENTATION
// =============================================================================

export function useScoring(): UseScoringReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastScoredAt, setLastScoredAt] = useState<string | null>(null);
  const [schoolConfigs, setSchoolConfigs] = useState<SchoolConfig[]>([]);

  // Get profile from student store
  const profile = useStudentStore((s) => s.profile);

  // Get results from results store
  const results = useResultsStore((s) => s.results);
  const setResults = useResultsStore((s) => s.setResults);
  const isStale = useResultsStore((s) => s.is_stale);

  // Session actions
  const completeAssessment = useSessionStore((s) => s.completeAssessment);

  /**
   * Call the scoring API
   */
  const calculateScore = useCallback(async (): Promise<AssessmentResults | null> => {
    if (!profile) {
      setError('No profile available for scoring');
      return null;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ profile }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Scoring failed: ${response.status}`);
      }

      const data: ScoreResponse = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Scoring returned unsuccessful');
      }

      // Store results
      setResults(data.results);
      setSchoolConfigs(data.school_configs);
      setLastScoredAt(data.timestamp);

      // Mark assessment as complete
      completeAssessment();

      return data.results;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error during scoring';
      setError(message);
      console.error('[useScoring] Error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [profile, setResults, completeAssessment]);

  /**
   * Force refresh score (clear cache and recalculate)
   */
  const refreshScore = useCallback(async (): Promise<AssessmentResults | null> => {
    const markStale = useResultsStore.getState().markStale;
    markStale();
    return calculateScore();
  }, [calculateScore]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Auto-refresh if results are stale
  useEffect(() => {
    if (isStale && !isLoading && profile) {
      calculateScore();
    }
  }, [isStale, isLoading, profile, calculateScore]);

  return {
    isLoading,
    error,
    lastScoredAt,
    calculateScore,
    refreshScore,
    clearError,
    results,
    schoolConfigs,
  };
}

// =============================================================================
// SIMPLIFIED SCORE HOOK (for components that just need the score)
// =============================================================================

export function useIvyScore() {
  const results = useResultsStore((s) => s.results);

  return {
    totalScore: results?.ivy_ready_score?.total_score ?? 0,
    categoryScores: results?.ivy_ready_score?.category_scores ?? {
      aptitude: 0,
      passion: 0,
      community: 0,
      narrative: 0,
    },
    percentileRank: results?.ivy_ready_score?.percentile_rank ?? 0,
    hasResults: results !== null,
  };
}

// =============================================================================
// SCHOOL PROBABILITIES HOOK
// =============================================================================

export function useSchoolProbabilities() {
  const schoolProbabilities = useResultsStore((s) => s.school_probabilities);

  return {
    probabilities: schoolProbabilities,
    topSchool: schoolProbabilities.length > 0
      ? schoolProbabilities.reduce((best, curr) =>
          curr.p_final > best.p_final ? curr : best
        )
      : null,
    averageProbability: schoolProbabilities.length > 0
      ? schoolProbabilities.reduce((sum, p) => sum + p.p_final, 0) / schoolProbabilities.length
      : 0,
  };
}

// =============================================================================
// ARCHETYPE HOOK
// =============================================================================

export function useArchetype() {
  const archetype = useResultsStore((s) => s.archetype);
  const archetypeLabel = useResultsStore((s) => s.archetype_label);
  const narrativeTagline = useResultsStore((s) => s.narrative_tagline);

  return {
    archetype,
    label: archetypeLabel,
    tagline: narrativeTagline,
    hasArchetype: archetype !== null,
  };
}

// =============================================================================
// FACTORS HOOK
// =============================================================================

export function useFactors() {
  const helpingFactors = useResultsStore((s) => s.helping_factors);
  const holdingBackFactors = useResultsStore((s) => s.holding_back_factors);

  return {
    helping: helpingFactors,
    holdingBack: holdingBackFactors,
    hasFactors: helpingFactors.length > 0 || holdingBackFactors.length > 0,
  };
}
