/**
 * Insights Store (Zustand)
 * Manages real-time insight generation based on student profile changes
 *
 * Architecture:
 * - Separate store for clean separation of concerns
 * - Auto-subscribes to useStudentStore for automatic insight regeneration
 * - Uses InsightEngine for all insight generation logic
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { InsightEngine } from '../insights/InsightEngine';
import type {
  Insight,
  InsightCategory,
  InsightSeverity,
  InsightFilterOptions,
  InsightStats,
  StudentProfile as InsightStudentProfile,
  GradeLevel,
} from '../insights/types';
import type { RealtimeInsight } from '../insights/realtimeInsights';
import { useStudentStore } from './useStudentStore';
import type { StudentProfile } from '../types/student';

// ============================================================================
// TYPE CONVERSIONS
// ============================================================================

/**
 * Convert the app's StudentProfile to InsightEngine's StudentProfile format
 * This bridges the gap between the two type systems
 */
function convertToInsightProfile(profile: StudentProfile): InsightStudentProfile {
  // Safe access for nullable nested objects
  const highSchool = profile.high_school;
  const demographics = profile.demographics;
  const aptitude = profile.aptitude;
  const passion = profile.passion;
  const assessmentIntelligence = profile.assessment_intelligence;

  return {
    // Core academics
    grade: String(profile.identity.grade) as GradeLevel,
    gpa_weighted: aptitude?.gpa_weighted ?? undefined,
    gpa_unweighted: aptitude?.gpa_unweighted ?? undefined,
    sat_total: aptitude?.sat_total ?? undefined,
    act_composite: aptitude?.act_total ?? undefined,
    ap_count: aptitude?.ap_count ?? undefined,
    ap_avg_score: aptitude?.ap_avg_score ?? undefined,

    // Context
    high_school_id: highSchool?.hs_code || undefined,
    target_schools: profile.target_schools?.length > 0 ? profile.target_schools : undefined,
    intended_major: profile.intended_major || undefined,

    // Demographics - map to InsightEngine's format
    region: highSchool ? mapRegion(highSchool.region) : undefined,
    ethnicity: demographics ? mapEthnicity(demographics.ethnicity) : undefined,
    legacy: demographics?.legacy ?? undefined,
    first_gen: demographics?.first_gen ?? undefined,
    income_top_1: demographics?.income_top_1_percent ?? undefined,
    recruited_athlete: demographics?.recruited_athlete ?? undefined,

    // Passion layer
    leadership_level: passion ? mapLeadershipLevel(passion.leadership_level) : undefined,
    project_impact: passion?.project_impact ?? undefined,
    research_level: passion ? mapResearchLevel(passion.research_level) : undefined,
    ec_awards: passion?.ec_awards?.length > 0 ? passion.ec_awards : undefined,
    ec_commitment_years: passion?.ec_commitment_years ?? undefined,

    // Academic awards
    academic_awards: aptitude?.academic_awards?.length > 0
      ? aptitude.academic_awards
      : undefined,

    // Psychometric
    grit_resilience: assessmentIntelligence?.psychometrics?.grit_resilience ?? undefined,
    burnout_risk: assessmentIntelligence?.time_management?.burnout_risk ?? undefined,
    reclaimable_hours: assessmentIntelligence?.time_management?.reclaimable_hours_weekly ?? undefined,
  };
}

/**
 * Map app region to InsightEngine region format
 */
function mapRegion(
  region: string
): InsightStudentProfile['region'] {
  const regionMap: Record<string, InsightStudentProfile['region']> = {
    BAY_AREA: 'BAY_AREA',
    SOCAL: 'SOCAL',
    NORTHEAST: 'NORTHEAST',
    MIDWEST: 'MIDWEST',
    SOUTH: 'SOUTH',
    WEST: 'WEST',
    RURAL: 'RURAL',
    INTERNATIONAL: 'INTERNATIONAL',
  };
  return regionMap[region];
}

/**
 * Map app ethnicity to InsightEngine ethnicity format
 */
function mapEthnicity(
  ethnicity: string | null | undefined
): InsightStudentProfile['ethnicity'] {
  if (!ethnicity) return undefined;
  const ethnicityMap: Record<string, InsightStudentProfile['ethnicity']> = {
    ASIAN: 'ASIAN',
    BLACK: 'URM',
    HISPANIC: 'URM',
    NATIVE_AMERICAN: 'URM',
    WHITE: 'WHITE',
    MULTIRACIAL: 'OTHER',
    PREFER_NOT_SAY: undefined,
    OTHER: 'OTHER',
  };
  return ethnicityMap[ethnicity];
}

/**
 * Map app leadership level to InsightEngine format
 */
function mapLeadershipLevel(
  level: string | null
): InsightStudentProfile['leadership_level'] {
  if (!level) return undefined;
  const levelMap: Record<string, InsightStudentProfile['leadership_level']> = {
    NATL_FOUNDER: 'NATL_FOUNDER',
    STATE_PRES: 'STATE_PRES',
    SCHOOL_PRES: 'SCHOOL_PRES',
    OFFICER: 'OFFICER',
    MEMBER: 'MEMBER',
  };
  return levelMap[level];
}

/**
 * Map app research level to InsightEngine format
 */
function mapResearchLevel(
  level: string | null
): InsightStudentProfile['research_level'] {
  if (!level) return undefined;
  const levelMap: Record<string, InsightStudentProfile['research_level']> = {
    PEER_REVIEWED: 'PEER_REVIEWED',
    RSI_SIMR: 'RSI_SIMR',
    UNIV_LAB: 'UNIV_LAB',
    SCHOOL_LAB: 'SCHOOL_LAB',
    NONE: 'NONE',
  };
  return levelMap[level];
}

// ============================================================================
// STORE INTERFACE
// ============================================================================

interface InsightsStoreState {
  // State
  insights: Insight[];
  isGenerating: boolean;
  lastGeneratedAt: string | null;
  lastTrigger: string | null;

  // Real-time insights state
  realtimeInsights: RealtimeInsight[];

  // Actions
  generateInsights: (attributeTrigger?: string) => void;
  clearInsights: () => void;

  // Real-time insight actions
  addRealtimeInsight: (insight: RealtimeInsight) => void;
  clearRealtimeInsights: () => void;
  removeRealtimeInsight: (id: string) => void;

  // Filtering & Utilities
  getFilteredInsights: (options: InsightFilterOptions) => Insight[];
  getInsightsByCategory: (category: InsightCategory) => Insight[];
  getInsightsBySeverity: (severity: InsightSeverity) => Insight[];
  getTopInsights: (count?: number) => Insight[];
  getStats: () => InsightStats;
}

// ============================================================================
// STORE IMPLEMENTATION
// ============================================================================

export const useInsightsStore = create<InsightsStoreState>()(
  devtools(
    immer((set, get) => ({
      // Initial state
      insights: [],
      isGenerating: false,
      lastGeneratedAt: null,
      lastTrigger: null,

      // Real-time insights initial state
      realtimeInsights: [],

      // Generate insights from current student profile
      generateInsights: (attributeTrigger?: string) => {
        set((state) => {
          state.isGenerating = true;
        });

        // Get current student profile
        const studentProfile = useStudentStore.getState().profile;

        // Convert to InsightEngine format
        const insightProfile = convertToInsightProfile(studentProfile);

        // Generate insights
        const result = InsightEngine.generate({
          profile: insightProfile,
          attribute: attributeTrigger,
        });

        set((state) => {
          state.insights = result.insights;
          state.isGenerating = false;
          state.lastGeneratedAt = result.generatedAt;
          state.lastTrigger = attributeTrigger ?? null;
        });
      },

      // Clear all insights
      clearInsights: () =>
        set((state) => {
          state.insights = [];
          state.lastGeneratedAt = null;
          state.lastTrigger = null;
        }),

      // Add a real-time insight (deduplicates by metricType to prevent stacking)
      addRealtimeInsight: (insight: RealtimeInsight) =>
        set((state) => {
          // Remove any existing insight with the same metricType (update instead of stack)
          const filtered = state.realtimeInsights.filter(
            (i) => i.metricType !== insight.metricType
          );
          // Add new insight at the front and keep only the last 15
          state.realtimeInsights = [insight, ...filtered].slice(0, 15);
        }),

      // Clear all real-time insights
      clearRealtimeInsights: () =>
        set((state) => {
          state.realtimeInsights = [];
        }),

      // Remove a specific real-time insight
      removeRealtimeInsight: (id: string) =>
        set((state) => {
          state.realtimeInsights = state.realtimeInsights.filter((i) => i.id !== id);
        }),

      // Get filtered insights
      getFilteredInsights: (options: InsightFilterOptions) => {
        const { insights } = get();
        return InsightEngine.filterInsights(insights, options);
      },

      // Get insights by category
      getInsightsByCategory: (category: InsightCategory) => {
        const { insights } = get();
        return insights.filter((i) => i.category === category);
      },

      // Get insights by severity
      getInsightsBySeverity: (severity: InsightSeverity) => {
        const { insights } = get();
        return insights.filter((i) => i.severity === severity);
      },

      // Get top N insights by priority
      getTopInsights: (count = 5) => {
        const { insights } = get();
        // Create a safe copy before sorting to avoid mutating store state
        return [...insights]
          .sort((a, b) => b.priority - a.priority)
          .slice(0, count);
      },

      // Get insight statistics
      getStats: () => {
        const { insights } = get();
        return InsightEngine.getStats(insights);
      },
    })),
    { name: 'InsightsStore' }
  )
);

// ============================================================================
// AUTO-SUBSCRIPTION TO STUDENT STORE
// ============================================================================

/**
 * Subscribe to student profile changes and auto-regenerate insights
 * This runs once when the module is imported
 */
let unsubscribe: (() => void) | null = null;
let previousProfile: StudentProfile | null = null;

export function initializeInsightSubscription(): void {
  // Avoid duplicate subscriptions
  if (unsubscribe) return;

  // Store the initial profile reference
  previousProfile = useStudentStore.getState().profile;

  // Subscribe to all store changes, then check if profile changed
  unsubscribe = useStudentStore.subscribe((state) => {
    // Only regenerate if the profile reference has changed
    if (state.profile !== previousProfile) {
      previousProfile = state.profile;
      // Regenerate insights when profile changes
      useInsightsStore.getState().generateInsights();
    }
  });
}

/**
 * Clean up subscription (useful for testing)
 */
export function cleanupInsightSubscription(): void {
  if (unsubscribe) {
    unsubscribe();
    unsubscribe = null;
    previousProfile = null;
  }
}

// ============================================================================
// SELECTOR HOOKS (for optimized component rendering)
// ============================================================================

/**
 * Hook to get all insights
 */
export function useInsights(): Insight[] {
  return useInsightsStore((state) => state.insights);
}

/**
 * Hook to get insights by category
 */
export function useInsightsByCategory(category: InsightCategory): Insight[] {
  return useInsightsStore((state) =>
    state.insights.filter((i) => i.category === category)
  );
}

/**
 * Hook to get critical insights
 */
export function useCriticalInsights(): Insight[] {
  return useInsightsStore((state) =>
    state.insights.filter((i) => i.severity === 'critical')
  );
}

/**
 * Hook to get positive insights
 */
export function usePositiveInsights(): Insight[] {
  return useInsightsStore((state) =>
    state.insights.filter((i) => i.severity === 'positive')
  );
}

/**
 * Hook to check if generating
 */
export function useIsGeneratingInsights(): boolean {
  return useInsightsStore((state) => state.isGenerating);
}

/**
 * Hook to get insight count by severity
 */
export function useInsightCounts(): Record<InsightSeverity, number> {
  return useInsightsStore((state) => ({
    critical: state.insights.filter((i) => i.severity === 'critical').length,
    warning: state.insights.filter((i) => i.severity === 'warning').length,
    positive: state.insights.filter((i) => i.severity === 'positive').length,
    neutral: state.insights.filter((i) => i.severity === 'neutral').length,
  }));
}

// ============================================================================
// REAL-TIME INSIGHT HOOKS
// ============================================================================

/**
 * Hook to get all real-time insights
 */
export function useRealtimeInsights(): RealtimeInsight[] {
  return useInsightsStore((state) => state.realtimeInsights);
}

/**
 * Hook to get the addRealtimeInsight action
 */
export function useAddRealtimeInsight(): (insight: RealtimeInsight) => void {
  return useInsightsStore((state) => state.addRealtimeInsight);
}
