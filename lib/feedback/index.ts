/**
 * IvyQuest v3.0 — Feedback System Alias
 *
 * Re-exports from visualization/feedback-system for convenient imports.
 *
 * @version 1.0.0
 * @module lib/feedback
 */

'use client';

import React from 'react';
import {
  ToastContainer as BaseToastContainer,
  useFeedback as useBaseFeedback,
} from '../visualization/feedback-system';

// Re-export everything except ToastContainer (we provide a wrapped version)
export {
  FeedbackProvider,
  FeedbackContext,
  useFeedback,
  useScoreDelta,
  ScoreDeltaPopup,
  ScoreDeltaTrail,
  FieldValidation,
  CardValidation,
  ValidatedInputWrapper,
  ToastComponent,
  AchievementUnlock,
  MilestoneReached,
  FrameComplete,
  ContextualHint,
  BoosterSuggestion,
} from '../visualization/feedback-system';

// Wrapped ToastContainer that uses context internally
export function ToastContainer({
  maxVisible,
  position
}: {
  maxVisible?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
} = {}) {
  const { toasts, dismissToast } = useBaseFeedback();

  return React.createElement(BaseToastContainer, {
    toasts,
    onDismiss: dismissToast,
    maxVisible,
    position,
  });
}

export type {
  ScoreDelta,
  ScoreDeltaPopupProps,
  ScoreDeltaTrailProps,
  ValidationState,
  FieldValidationProps,
  CardValidationProps,
  Toast,
  ToastProps,
  ToastContainerProps,
  Achievement,
  AchievementUnlockProps,
  Milestone,
  MilestoneReachedProps,
  FrameCompleteProps,
  Hint,
  ContextualHintProps,
  BoosterSuggestionProps,
  FeedbackContextValue,
  FeedbackProviderProps,
  FeedbackConfig,
  UseScoreDeltaReturn,
  UseScoreDeltaOptions,
} from '../visualization/feedback-system';
