/**
 * IvyQuest v3.0 — Feedback System Package
 * 
 * Real-time visual feedback for score changes, validation, and notifications.
 * 
 * @version 1.0.0
 * @module @ivyquest/feedback-system
 */

// ============================================================================
// CONTEXT & HOOKS
// ============================================================================

export {
  FeedbackProvider,
  FeedbackContext,
  useFeedback,
  useScoreDelta,
} from './context/FeedbackContext';

// ============================================================================
// SCORE DELTA COMPONENTS
// ============================================================================

export {
  ScoreDeltaPopup,
  ScoreDeltaTrail,
} from './components/ScoreDelta';

// ============================================================================
// VALIDATION COMPONENTS
// ============================================================================

export {
  FieldValidation,
  CardValidation,
  ValidatedInputWrapper,
} from './components/ValidationFeedback';

// ============================================================================
// NOTIFICATION COMPONENTS
// ============================================================================

export {
  Toast as ToastComponent,
  ToastContainer,
  AchievementUnlock,
} from './components/Notifications';

// ============================================================================
// PROGRESS COMPONENTS
// ============================================================================

export {
  MilestoneReached,
  FrameComplete,
  ContextualHint,
  BoosterSuggestion,
} from './components/Progress';

// ============================================================================
// CONSTANTS
// ============================================================================

export {
  SCORE_DELTA_CONFIG,
  VALIDATION_STATES,
  TOAST_CONFIG,
  ACHIEVEMENT_CONFIG,
  MILESTONES,
  HINT_CONFIG,
  CATEGORY_COLORS,
  ANIMATION_PRESETS,
  type ValidationStateId,
  type ToastTypeId,
  type AchievementRarity,
  type MilestoneId,
  type HintTypeId,
  type ScoreCategory,
  type AnimationPreset,
} from './constants/feedback.constants';

// ============================================================================
// UTILITIES
// ============================================================================

export {
  // ID
  generateFeedbackId,
  
  // Score Delta
  getDeltaMagnitude,
  getDeltaColors,
  getDeltaSize,
  getCategoryColors,
  formatDelta,
  getAnimationDuration,
  
  // Validation
  getValidationConfig,
  areAllFieldsValid,
  getInvalidFieldCount,
  getValidationSummary,
  
  // Toast
  getToastConfig,
  getToastDuration,
  shouldAutoDisiss,
  
  // Achievement
  getAchievementRarityConfig,
  getAchievementSound,
  formatUnlockTime,
  
  // Hint
  getHintConfig,
  sortHintsByPriority,
  filterExpiredHints,
  
  // Animation
  calculatePopupPosition,
  calculateTrailPath,
  staggerDelay,
  
  // Feedback
  triggerHaptic,
  playSound,
} from './utils/feedbackUtils';

// ============================================================================
// TYPES
// ============================================================================

export type {
  // Score Delta
  ScoreDelta,
  ScoreDeltaPopupProps,
  ScoreDeltaTrailProps,
  
  // Validation
  ValidationState,
  FieldValidationProps,
  CardValidationProps,
  
  // Toast
  Toast,
  ToastProps,
  ToastContainerProps,
  
  // Achievement
  Achievement,
  AchievementUnlockProps,
  
  // Milestone
  Milestone,
  MilestoneReachedProps,
  FrameCompleteProps,
  
  // Hint
  Hint,
  ContextualHintProps,
  BoosterSuggestionProps,
  
  // Context
  FeedbackContextValue,
  FeedbackProviderProps,
  FeedbackConfig,
  
  // Hook
  UseScoreDeltaReturn,
  UseScoreDeltaOptions,
  
  // Animation
  AnimationConfig,
} from './types/feedback.types';
