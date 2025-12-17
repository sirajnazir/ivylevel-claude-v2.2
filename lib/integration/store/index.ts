/**
 * IvyQuest v3.0 — Integration Store
 *
 * Re-exports all store components.
 *
 * @version 1.0.0
 * @module store
 */

export { useQuestMasterStore, initialState } from './questStore.master';

export {
  // Navigation selectors
  selectCurrentFrame,
  selectCurrentCard,
  selectCompletedFrames,
  selectCanNavigateTo,
  selectNavigationHistory,
  selectCanGoNext,
  selectCanGoPrev,

  // Frame data selectors
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

  // Score selectors
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

  // Progress selectors
  selectIsComplete,
  selectQuestProgress,

  // Persistence selectors
  selectQuestId,
  selectStartedAt,
  selectLastUpdatedAt,
  selectIsDirty,
  selectLastSavedAt,
  selectSessionDuration,

  // Computed selectors
  selectYearsToApplication,
  selectHasNationalRecognition,
  selectHasAwards,
  selectLeadershipRoleCount,
  selectFrame5Inputs,
} from './questStore.selectors';

export {
  // Storage helpers
  isStorageAvailable,
  getStorageSize,
  saveToStorage,
  loadFromStorage,
  removeFromStorage,

  // Session management
  getSessionHistory,
  addToHistory,
  clearHistory,
  isSessionExpired,
  isSessionValid,
  attemptRestore,

  // Auto-save
  AutoSaveManager,
  DEFAULT_CONFIG,
  debounce,

  // Types
  type RestoreResult,
} from './questStore.persistence';
