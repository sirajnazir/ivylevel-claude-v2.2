/**
 * IvyQuest v3.0 — Integration Layer
 *
 * Central nervous system connecting all 6 frames.
 * Unified store, navigation, persistence, and orchestration.
 *
 * @version 1.0.0
 * @module integration
 */

// ============================================================================
// TYPES
// ============================================================================

export type {
  // Frame data types
  Frame0Data,
  Frame1Data,
  Frame2Data,
  Frame3Data,
  Frame4Data,
  Frame5Data,
  DemographicsData,
  Activity,
  Award,
  LeadershipRole,
  IntegrationBooster,
  IntegrationActionItem,

  // Score types
  LayerScore,
  AptitudeScore,
  PassionScore,
  CommunityScore,
  OperatingScore,
  IvyReadyScore,
  SchoolFit,
  MarketReality,
  QuestScores,

  // Navigation types
  FrameId,
  NavigationState,
  NavigationActions,

  // Persistence types
  PersistenceState,
  PersistenceConfig,
  SavedSession,

  // Master state types
  QuestMasterState,
  QuestMasterActions,
  QuestStore,

  // Component types
  QuestOrchestratorProps,
  QuestCompletionResult,

  // Progress types
  QuestProgress,
  FrameMeta,
} from './types/integration.types';

export { FRAME_META } from './types/integration.types';

// ============================================================================
// STORE
// ============================================================================

export {
  // Store
  useQuestMasterStore,
  useQuestMasterStore as useQuestStore, // Alias for final assembly compatibility
  initialState,

  // Selectors - Navigation
  selectCurrentFrame,
  selectCurrentCard,
  selectCompletedFrames,
  selectCanNavigateTo,
  selectNavigationHistory,
  selectCanGoNext,
  selectCanGoPrev,

  // Selectors - Frame data
  selectFrame0,
  selectFrame1,
  selectFrame2,
  selectFrame3,
  selectFrame4,
  selectFrame5,
  selectStudentName,
  selectTargetSchools,
  selectGradeLevel,
  selectDemographics,
  selectActivities,
  selectPrimarySpike,
  selectOperatingStyle,
  selectHiddenCapabilities,
  selectSelectedBoosters,
  selectActionPlan,

  // Selectors - Scores
  selectScores,
  selectAptitudeScore,
  selectPassionScore,
  selectCommunityScore,
  selectOperatingScore,
  selectIvyReadyScore,
  selectMarketReality,
  selectScoreBreakdown,
  selectSchoolFits,
  selectBestFitSchool,

  // Selectors - Progress
  selectIsComplete,
  selectQuestProgress,

  // Selectors - Persistence
  selectQuestId,
  selectStartedAt,
  selectLastUpdatedAt,
  selectIsDirty,
  selectLastSavedAt,
  selectSessionDuration,

  // Selectors - Computed
  selectYearsToApplication,
  selectHasNationalRecognition,
  selectHasAwards,
  selectLeadershipRoleCount,
  selectFrame5Inputs,

  // Persistence utilities
  isStorageAvailable,
  getStorageSize,
  saveToStorage,
  loadFromStorage,
  removeFromStorage,
  getSessionHistory,
  addToHistory,
  clearHistory,
  isSessionExpired,
  isSessionValid,
  attemptRestore,
  AutoSaveManager,
  DEFAULT_CONFIG,
  debounce,
  type RestoreResult,
} from './store';

// ============================================================================
// HOOKS
// ============================================================================

export {
  // Navigation hook
  useQuestNavigation,
  useFrameCardNavigation,
  type UseQuestNavigationReturn,

  // Progress hook
  useQuestProgress,
  useProgressIndicator,
  useFrameProgress,
  type UseQuestProgressReturn,

  // Persistence hook
  useQuestPersistence,
  useAutoRestore,
  type UseQuestPersistenceReturn,
  type UseAutoRestoreOptions,
} from './hooks';

// ============================================================================
// COMPONENTS
// ============================================================================

export { QuestOrchestrator } from './controllers';

// ============================================================================
// DEFAULT EXPORT
// ============================================================================

export default {
  // Re-export key items for convenience
  QuestOrchestrator: () =>
    import('./controllers/QuestOrchestrator').then((m) => m.QuestOrchestrator),
};
