/**
 * IvyQuest v3.0 — Visualization Layer
 *
 * Twin Fleet and Feedback System components.
 *
 * @version 1.0.0
 * @module visualization
 */

// ============================================================================
// TWIN FLEET
// ============================================================================

export * from './twin-fleet';

// ============================================================================
// FEEDBACK SYSTEM
// ============================================================================

// Re-export feedback-system with renamed conflicting exports
export {
  // Context & Hooks
  FeedbackProvider,
  FeedbackContext,
  useFeedback,
  useScoreDelta,

  // Score Delta Components
  ScoreDeltaPopup,
  ScoreDeltaTrail,

  // Validation Components
  FieldValidation,
  CardValidation,
  ValidatedInputWrapper,

  // Notification Components
  ToastComponent,
  ToastContainer,
  AchievementUnlock,

  // Progress Components
  MilestoneReached,
  FrameComplete,
  ContextualHint,
  BoosterSuggestion,

  // Constants
  SCORE_DELTA_CONFIG,
  VALIDATION_STATES,
  TOAST_CONFIG,
  ACHIEVEMENT_CONFIG,
  MILESTONES,
  HINT_CONFIG,
  CATEGORY_COLORS,
  ANIMATION_PRESETS,

  // Utilities
  generateFeedbackId,
  getDeltaMagnitude,
  getDeltaColors,
  getDeltaSize,
  getCategoryColors,
  formatDelta,
  getAnimationDuration,
  getValidationConfig,
  areAllFieldsValid,
  getInvalidFieldCount,
  getValidationSummary,
  getToastConfig,
  getToastDuration,
  shouldAutoDisiss,
  getAchievementRarityConfig,
  getAchievementSound,
  formatUnlockTime,
  getHintConfig,
  sortHintsByPriority,
  filterExpiredHints,
  calculatePopupPosition,
  calculateTrailPath,
  triggerHaptic,
  playSound,

  // Renamed to avoid conflict with twin-fleet
  staggerDelay as feedbackStaggerDelay,
} from './feedback-system';

// Re-export feedback-system types
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
  AnimationConfig as FeedbackAnimationConfig,
  ValidationStateId,
  ToastTypeId,
  AchievementRarity,
  MilestoneId,
  HintTypeId,
  ScoreCategory,
  AnimationPreset,
} from './feedback-system';
