/**
 * IvyQuest v3.0 — Progress Hook
 *
 * Provides quest progress tracking and analytics.
 *
 * @version 1.0.0
 * @module hooks/useQuestProgress
 */

import { useMemo } from 'react';
import { useQuestMasterStore } from '../store/questStore.master';
import {
  selectQuestProgress,
  selectIsComplete,
  selectSessionDuration,
  selectStartedAt,
  selectLastUpdatedAt,
} from '../store/questStore.selectors';
import type { FrameId, QuestProgress } from '../types/integration.types';
import { FRAME_META } from '../types/integration.types';

// ============================================================================
// TYPES
// ============================================================================

export interface UseQuestProgressReturn {
  // Progress data
  progress: QuestProgress;

  // Completion status
  isComplete: boolean;
  isStarted: boolean;

  // Timing
  sessionDuration: number; // minutes
  startedAt: string | null;
  lastUpdatedAt: string;
  estimatedTimeRemaining: number; // minutes

  // Progress helpers
  overallPercent: number;
  framesCompleted: number;
  totalFrames: number;

  // Frame-specific progress
  getFrameProgress: (frame: FrameId) => {
    isComplete: boolean;
    percentComplete: number;
    cardsCompleted: number;
    totalCards: number;
    name: string;
    icon: string;
  };

  // Progress bar data
  progressBarData: Array<{
    frameId: FrameId;
    name: string;
    icon: string;
    percent: number;
    isComplete: boolean;
    isCurrent: boolean;
  }>;
}

// ============================================================================
// HOOK
// ============================================================================

export function useQuestProgress(): UseQuestProgressReturn {
  // Subscribe to progress state
  const progress = useQuestMasterStore(selectQuestProgress);
  const isComplete = useQuestMasterStore(selectIsComplete);
  const sessionDuration = useQuestMasterStore(selectSessionDuration);
  const startedAt = useQuestMasterStore(selectStartedAt);
  const lastUpdatedAt = useQuestMasterStore(selectLastUpdatedAt);

  // Computed values
  const isStarted = !!startedAt;
  const overallPercent = progress.percentComplete;
  const framesCompleted = progress.completedFrames.length;
  const totalFrames = 6;
  const estimatedTimeRemaining = progress.estimatedTimeRemaining;

  // Get progress for a specific frame
  const getFrameProgress = useMemo(() => {
    return (frame: FrameId) => {
      const frameProgress = progress.frameProgress[frame];
      const meta = FRAME_META[frame];

      return {
        isComplete: frameProgress.isComplete,
        percentComplete: frameProgress.percentComplete,
        cardsCompleted: frameProgress.cardsCompleted,
        totalCards: frameProgress.totalCards,
        name: meta.name,
        icon: meta.icon,
      };
    };
  }, [progress.frameProgress]);

  // Progress bar visualization data
  const progressBarData = useMemo(() => {
    const allFrames: FrameId[] = [0, 1, 2, 3, 4, 5];

    return allFrames.map((frameId) => {
      const frameProgress = progress.frameProgress[frameId];
      const meta = FRAME_META[frameId];

      return {
        frameId,
        name: meta.name,
        icon: meta.icon,
        percent: frameProgress.percentComplete,
        isComplete: frameProgress.isComplete,
        isCurrent: progress.currentFrame === frameId,
      };
    });
  }, [progress.frameProgress, progress.currentFrame]);

  return {
    // Progress data
    progress,

    // Completion status
    isComplete,
    isStarted,

    // Timing
    sessionDuration,
    startedAt,
    lastUpdatedAt,
    estimatedTimeRemaining,

    // Progress helpers
    overallPercent,
    framesCompleted,
    totalFrames,

    // Frame-specific progress
    getFrameProgress,

    // Progress bar data
    progressBarData,
  };
}

// ============================================================================
// PROGRESS INDICATOR HOOK
// ============================================================================

/**
 * Simplified hook for progress indicators/badges
 */
export function useProgressIndicator() {
  const progress = useQuestMasterStore(selectQuestProgress);
  const isComplete = useQuestMasterStore(selectIsComplete);

  const label = useMemo(() => {
    if (isComplete) return 'Complete';
    if (progress.percentComplete === 0) return 'Not Started';
    return `${progress.percentComplete}%`;
  }, [isComplete, progress.percentComplete]);

  const color = useMemo(() => {
    if (isComplete) return 'green';
    if (progress.percentComplete >= 75) return 'emerald';
    if (progress.percentComplete >= 50) return 'yellow';
    if (progress.percentComplete >= 25) return 'orange';
    return 'gray';
  }, [isComplete, progress.percentComplete]);

  return {
    percent: progress.percentComplete,
    label,
    color,
    isComplete,
  };
}

// ============================================================================
// FRAME PROGRESS HOOK
// ============================================================================

/**
 * Hook for individual frame progress tracking
 */
export function useFrameProgress(frameId: FrameId) {
  const progress = useQuestMasterStore(selectQuestProgress);

  const frameProgress = useMemo(
    () => progress.frameProgress[frameId],
    [progress.frameProgress, frameId]
  );

  const meta = FRAME_META[frameId];

  return {
    ...frameProgress,
    frameId,
    name: meta.name,
    description: meta.description,
    icon: meta.icon,
    color: meta.color,
    targetDuration: meta.targetDuration,
    isCurrent: progress.currentFrame === frameId,
    isPast: progress.completedFrames.includes(frameId),
    isFuture:
      !progress.completedFrames.includes(frameId) &&
      progress.currentFrame !== frameId,
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default useQuestProgress;
