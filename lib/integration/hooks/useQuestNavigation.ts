/**
 * IvyQuest v3.0 — Navigation Hook
 *
 * Provides navigation helpers and state for quest flow control.
 *
 * @version 1.0.0
 * @module hooks/useQuestNavigation
 */

import { useCallback, useMemo } from 'react';
import { useQuestMasterStore } from '../store/questStore.master';
import {
  selectCurrentFrame,
  selectCurrentCard,
  selectCompletedFrames,
  selectCanNavigateTo,
  selectCanGoNext,
  selectCanGoPrev,
  selectNavigationHistory,
} from '../store/questStore.selectors';
import type { FrameId } from '../types/integration.types';
import { FRAME_META } from '../types/integration.types';

// ============================================================================
// TYPES
// ============================================================================

export interface UseQuestNavigationReturn {
  // Current state
  currentFrame: FrameId;
  currentCard: number;
  completedFrames: FrameId[];
  canNavigateTo: FrameId[];
  history: Array<{ frame: FrameId; timestamp: string }>;

  // Navigation flags
  canGoNext: boolean;
  canGoPrev: boolean;
  isFirstFrame: boolean;
  isLastFrame: boolean;

  // Frame metadata
  currentFrameMeta: (typeof FRAME_META)[FrameId];
  nextFrameMeta: (typeof FRAME_META)[FrameId] | null;
  prevFrameMeta: (typeof FRAME_META)[FrameId] | null;

  // Navigation actions
  goToFrame: (frame: FrameId) => boolean;
  nextFrame: () => boolean;
  prevFrame: () => boolean;
  setCurrentCard: (card: number) => void;
  markFrameComplete: (frame: FrameId) => void;

  // Helpers
  isFrameComplete: (frame: FrameId) => boolean;
  isFrameAccessible: (frame: FrameId) => boolean;
  getFrameProgress: (frame: FrameId) => number;
}

// ============================================================================
// HOOK
// ============================================================================

export function useQuestNavigation(): UseQuestNavigationReturn {
  // Subscribe to navigation state
  const currentFrame = useQuestMasterStore(selectCurrentFrame);
  const currentCard = useQuestMasterStore(selectCurrentCard);
  const completedFrames = useQuestMasterStore(selectCompletedFrames);
  const canNavigateTo = useQuestMasterStore(selectCanNavigateTo);
  const canGoNext = useQuestMasterStore(selectCanGoNext);
  const canGoPrev = useQuestMasterStore(selectCanGoPrev);
  const history = useQuestMasterStore(selectNavigationHistory);

  // Get actions from store
  const goToFrame = useQuestMasterStore((state) => state.navigationActions.goToFrame);
  const nextFrame = useQuestMasterStore((state) => state.navigationActions.nextFrame);
  const prevFrame = useQuestMasterStore((state) => state.navigationActions.prevFrame);
  const setCurrentCard = useQuestMasterStore(
    (state) => state.navigationActions.setCurrentCard
  );
  const markFrameComplete = useQuestMasterStore(
    (state) => state.navigationActions.markFrameComplete
  );

  // Computed values
  const isFirstFrame = currentFrame === 0;
  const isLastFrame = currentFrame === 5;

  const currentFrameMeta = useMemo(() => FRAME_META[currentFrame], [currentFrame]);

  const nextFrameMeta = useMemo(() => {
    const nextId = (currentFrame + 1) as FrameId;
    return nextId <= 5 ? FRAME_META[nextId] : null;
  }, [currentFrame]);

  const prevFrameMeta = useMemo(() => {
    const prevId = (currentFrame - 1) as FrameId;
    return prevId >= 0 ? FRAME_META[prevId] : null;
  }, [currentFrame]);

  // Helper functions
  const isFrameComplete = useCallback(
    (frame: FrameId) => completedFrames.includes(frame),
    [completedFrames]
  );

  const isFrameAccessible = useCallback(
    (frame: FrameId) => canNavigateTo.includes(frame),
    [canNavigateTo]
  );

  const getFrameProgress = useCallback(
    (frame: FrameId) => {
      if (completedFrames.includes(frame)) {
        return 100;
      }
      if (frame === currentFrame) {
        const totalCards = FRAME_META[frame].cardCount;
        return Math.round(((currentCard - 1) / totalCards) * 100);
      }
      return 0;
    },
    [completedFrames, currentFrame, currentCard]
  );

  return {
    // Current state
    currentFrame,
    currentCard,
    completedFrames,
    canNavigateTo,
    history,

    // Navigation flags
    canGoNext,
    canGoPrev,
    isFirstFrame,
    isLastFrame,

    // Frame metadata
    currentFrameMeta,
    nextFrameMeta,
    prevFrameMeta,

    // Navigation actions
    goToFrame,
    nextFrame,
    prevFrame,
    setCurrentCard,
    markFrameComplete,

    // Helpers
    isFrameComplete,
    isFrameAccessible,
    getFrameProgress,
  };
}

// ============================================================================
// FRAME NAVIGATION HOOK
// ============================================================================

/**
 * Hook for navigating within a specific frame's cards
 */
export function useFrameCardNavigation(totalCards: number) {
  const currentCard = useQuestMasterStore(selectCurrentCard);
  const setCurrentCard = useQuestMasterStore(
    (state) => state.navigationActions.setCurrentCard
  );

  const canGoNextCard = currentCard < totalCards;
  const canGoPrevCard = currentCard > 1;
  const isFirstCard = currentCard === 1;
  const isLastCard = currentCard === totalCards;
  const progress = Math.round(((currentCard - 1) / totalCards) * 100);

  const nextCard = useCallback(() => {
    if (canGoNextCard) {
      setCurrentCard(currentCard + 1);
      return true;
    }
    return false;
  }, [canGoNextCard, currentCard, setCurrentCard]);

  const prevCard = useCallback(() => {
    if (canGoPrevCard) {
      setCurrentCard(currentCard - 1);
      return true;
    }
    return false;
  }, [canGoPrevCard, currentCard, setCurrentCard]);

  const goToCard = useCallback(
    (card: number) => {
      if (card >= 1 && card <= totalCards) {
        setCurrentCard(card);
        return true;
      }
      return false;
    },
    [totalCards, setCurrentCard]
  );

  return {
    currentCard,
    totalCards,
    canGoNextCard,
    canGoPrevCard,
    isFirstCard,
    isLastCard,
    progress,
    nextCard,
    prevCard,
    goToCard,
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default useQuestNavigation;
