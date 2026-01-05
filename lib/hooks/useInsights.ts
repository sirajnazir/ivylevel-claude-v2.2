/**
 * Insights Hook
 *
 * Connects UI components to the real InsightEngine via InsightsStore
 * Generates contextual insights based on profile
 */

'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { useInsightsStore } from '@/lib/store/useInsightsStore';
import type { Insight, InsightCategory, InsightSeverity } from '@/lib/insights/types';

// =============================================================================
// TYPES
// =============================================================================

interface UseInsightsReturn {
  // State
  insights: Insight[];
  isGenerating: boolean;
  error: string | null;
  lastGeneratedAt: string | null;

  // Actions
  generateInsights: (attribute?: string) => Promise<Insight[]>;
  refreshInsights: () => Promise<Insight[]>;
  clearInsights: () => void;

  // Filtered views
  criticalInsights: Insight[];
  warningInsights: Insight[];
  positiveInsights: Insight[];

  // Counts
  totalCount: number;
  criticalCount: number;
  warningCount: number;

  // Filter methods
  filterByCategory: (category: InsightCategory) => Insight[];
  filterBySeverity: (severity: InsightSeverity) => Insight[];
}

// =============================================================================
// HOOK IMPLEMENTATION
// =============================================================================

export function useInsights(): UseInsightsReturn {
  const [error, setError] = useState<string | null>(null);

  // Get profile from student store
  const profile = useStudentStore((s) => s.profile);

  // Get insights and actions from store (store handles InsightEngine internally)
  const insights = useInsightsStore((s) => s.insights);
  const isGenerating = useInsightsStore((s) => s.isGenerating);
  const lastGeneratedAt = useInsightsStore((s) => s.lastGeneratedAt);
  const storeGenerateInsights = useInsightsStore((s) => s.generateInsights);
  const clearInsights = useInsightsStore((s) => s.clearInsights);

  /**
   * Generate insights from profile using the store's generateInsights
   * (which internally uses InsightEngine with proper profile conversion)
   */
  const generateInsights = useCallback(async (attribute?: string): Promise<Insight[]> => {
    if (!profile) {
      setError('No profile available for insight generation');
      return [];
    }

    setError(null);

    try {
      // Call store's generateInsights (handles InsightEngine internally)
      storeGenerateInsights(attribute);

      // Return the insights from store after generation
      return useInsightsStore.getState().insights;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error generating insights';
      setError(message);
      console.error('[useInsights] Error:', err);
      return [];
    }
  }, [profile, storeGenerateInsights]);

  /**
   * Refresh insights (force regeneration)
   */
  const refreshInsights = useCallback(async (): Promise<Insight[]> => {
    clearInsights();
    return generateInsights();
  }, [generateInsights, clearInsights]);

  // Filtered views
  const criticalInsights = useMemo(() =>
    insights.filter(i => i.severity === 'critical'),
    [insights]
  );

  const warningInsights = useMemo(() =>
    insights.filter(i => i.severity === 'warning'),
    [insights]
  );

  const positiveInsights = useMemo(() =>
    insights.filter(i => i.severity === 'positive'),
    [insights]
  );

  // Counts
  const totalCount = insights.length;
  const criticalCount = criticalInsights.length;
  const warningCount = warningInsights.length;

  // Filter methods
  const filterByCategory = useCallback((category: InsightCategory): Insight[] => {
    return insights.filter(i => i.category === category);
  }, [insights]);

  const filterBySeverity = useCallback((severity: InsightSeverity): Insight[] => {
    return insights.filter(i => i.severity === severity);
  }, [insights]);

  return {
    insights,
    isGenerating,
    error,
    lastGeneratedAt,
    generateInsights,
    refreshInsights,
    clearInsights,
    criticalInsights,
    warningInsights,
    positiveInsights,
    totalCount,
    criticalCount,
    warningCount,
    filterByCategory,
    filterBySeverity,
  };
}

// =============================================================================
// AUTO-GENERATE ON PROFILE CHANGE
// =============================================================================

/**
 * Hook that auto-generates insights when profile changes
 */
export function useAutoInsights(debounceMs: number = 500) {
  const { generateInsights, insights } = useInsights();
  const profile = useStudentStore((s) => s.profile);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (profile) {
        generateInsights();
      }
    }, debounceMs);

    return () => clearTimeout(timeoutId);
  }, [profile, generateInsights, debounceMs]);

  return insights;
}

// =============================================================================
// TOP INSIGHTS HOOK
// =============================================================================

/**
 * Get only the top N most important insights
 */
export function useTopInsights(count: number = 5) {
  const { insights } = useInsights();

  return useMemo(() => {
    // Sort by priority descending
    const sorted = [...insights].sort((a, b) => b.priority - a.priority);
    return sorted.slice(0, count);
  }, [insights, count]);
}
