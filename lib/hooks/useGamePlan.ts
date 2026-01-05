/**
 * Game Plan Hook
 *
 * Connects UI components to the real GamePlanEngine
 * Generates personalized action plans based on profile
 */

'use client';

import { useState, useCallback, useMemo } from 'react';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { generateGamePlan, getStrengthBasedRecommendations } from '@/lib/gamePlan/gamePlanEngine';
import type { GamePlan, GamePlanAction, GamePlanPhase } from '@/lib/gamePlan/gamePlanEngine';

// =============================================================================
// TYPES
// =============================================================================

interface UseGamePlanReturn {
  // State
  gamePlan: GamePlan | null;
  isGenerating: boolean;
  error: string | null;

  // Actions
  generatePlan: () => Promise<GamePlan | null>;
  regeneratePlan: () => Promise<GamePlan | null>;

  // Computed data
  totalActions: number;
  criticalActions: GamePlanAction[];
  quickWins: GamePlanAction[];
  phases: GamePlanPhase[];
  weeklyCommitment: number;
  strengthRecommendations: { activity: string; rationale: string }[];
}

// =============================================================================
// HOOK IMPLEMENTATION
// =============================================================================

export function useGamePlan(): UseGamePlanReturn {
  const [gamePlan, setGamePlan] = useState<GamePlan | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get profile from student store
  const profile = useStudentStore((s) => s.profile);

  /**
   * Generate game plan from profile
   */
  const generatePlan = useCallback(async (): Promise<GamePlan | null> => {
    if (!profile) {
      setError('No profile available for game plan generation');
      return null;
    }

    setIsGenerating(true);
    setError(null);

    try {
      // Generate plan using the real engine
      const plan = generateGamePlan(profile);
      setGamePlan(plan);
      return plan;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error generating game plan';
      setError(message);
      console.error('[useGamePlan] Error:', err);
      return null;
    } finally {
      setIsGenerating(false);
    }
  }, [profile]);

  /**
   * Regenerate plan (force refresh)
   */
  const regeneratePlan = useCallback(async (): Promise<GamePlan | null> => {
    setGamePlan(null);
    return generatePlan();
  }, [generatePlan]);

  // Computed values
  const totalActions = useMemo(() => {
    if (!gamePlan) return 0;
    return gamePlan.phases.reduce((sum, phase) => sum + phase.actions.length, 0);
  }, [gamePlan]);

  const criticalActions = useMemo(() => {
    if (!gamePlan) return [];
    return gamePlan.phases
      .flatMap(p => p.actions)
      .filter(a => a.priority === 'critical');
  }, [gamePlan]);

  const quickWins = useMemo(() => {
    return gamePlan?.quickWins ?? [];
  }, [gamePlan]);

  const phases = useMemo(() => {
    return gamePlan?.phases ?? [];
  }, [gamePlan]);

  const weeklyCommitment = useMemo(() => {
    return gamePlan?.weeklyCommitment ?? 0;
  }, [gamePlan]);

  const strengthRecommendations = useMemo(() => {
    if (!profile?.operating?.strengths) return [];
    return getStrengthBasedRecommendations(profile.operating.strengths);
  }, [profile]);

  return {
    gamePlan,
    isGenerating,
    error,
    generatePlan,
    regeneratePlan,
    totalActions,
    criticalActions,
    quickWins,
    phases,
    weeklyCommitment,
    strengthRecommendations,
  };
}

// =============================================================================
// PHASE-SPECIFIC HOOK
// =============================================================================

export function useGamePlanPhase(phaseId: string) {
  const { gamePlan } = useGamePlan();

  const phase = useMemo(() => {
    return gamePlan?.phases.find(p => p.id === phaseId) ?? null;
  }, [gamePlan, phaseId]);

  const completedActions = useMemo(() => {
    // In a real implementation, this would track completion status
    // For now, return empty since we don't have completion tracking
    return 0;
  }, []);

  const progress = useMemo(() => {
    if (!phase) return 0;
    return Math.round((completedActions / phase.actions.length) * 100);
  }, [phase, completedActions]);

  return {
    phase,
    actions: phase?.actions ?? [],
    totalActions: phase?.actions.length ?? 0,
    completedActions,
    progress,
  };
}

// =============================================================================
// PREPARATION DATA TRANSFORMER
// =============================================================================

/**
 * Transform game plan into preparation tab format
 */
export function usePreparationData() {
  const { gamePlan, phases } = useGamePlan();

  // Transform phases into week-based structure for PreparationTab
  const weeklyTasks = useMemo(() => {
    if (!gamePlan) return [];

    // Group actions by estimated week
    const weeks: Array<{
      weekNumber: number;
      weekRange: string;
      focus: string;
      tasks: Array<{
        id: string;
        title: string;
        status: 'pending' | 'in_progress' | 'completed';
        category: string;
        priority: string;
        timeCommitment: string;
      }>;
      progress: number;
    }> = [];

    let weekNumber = 1;

    for (const phase of phases) {
      // Each phase maps to approximately 4 weeks
      const tasksPerWeek = Math.ceil(phase.actions.length / 4);

      for (let i = 0; i < phase.actions.length; i += tasksPerWeek) {
        const weekActions = phase.actions.slice(i, i + tasksPerWeek);

        if (weekActions.length > 0) {
          weeks.push({
            weekNumber,
            weekRange: `Week ${weekNumber}`,
            focus: phase.title,
            tasks: weekActions.map(action => ({
              id: action.id,
              title: action.title,
              status: 'pending' as const,
              category: action.category,
              priority: action.priority,
              timeCommitment: action.timeCommitment,
            })),
            progress: 0,
          });
          weekNumber++;
        }
      }
    }

    return weeks;
  }, [gamePlan, phases]);

  return {
    weeklyTasks,
    totalWeeks: weeklyTasks.length,
    hasData: weeklyTasks.length > 0,
  };
}
