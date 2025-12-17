/**
 * IvyQuest v3.0 — Store Selectors
 *
 * Derived state selectors for efficient subscriptions.
 *
 * @version 1.0.0
 * @module store/questStore.selectors
 */

import type { QuestStore, QuestProgress, FrameId } from '../types/integration.types';

// ============================================================================
// NAVIGATION SELECTORS
// ============================================================================

export const selectCurrentFrame = (state: QuestStore) =>
  state.navigation.currentFrame;

export const selectCurrentCard = (state: QuestStore) =>
  state.navigation.currentCard;

export const selectCompletedFrames = (state: QuestStore) =>
  state.navigation.completedFrames;

export const selectCanNavigateTo = (state: QuestStore) =>
  state.navigation.canNavigateTo;

export const selectNavigationHistory = (state: QuestStore) =>
  state.navigation.history;

export const selectCanGoNext = (state: QuestStore) => {
  const current = state.navigation.currentFrame;
  return (
    current < 5 &&
    state.navigation.canNavigateTo.includes((current + 1) as FrameId)
  );
};

export const selectCanGoPrev = (state: QuestStore) => {
  return state.navigation.currentFrame > 0;
};

// ============================================================================
// FRAME DATA SELECTORS
// ============================================================================

export const selectFrame0 = (state: QuestStore) => state.frame0;
export const selectFrame1 = (state: QuestStore) => state.frame1;
export const selectFrame2 = (state: QuestStore) => state.frame2;
export const selectFrame3 = (state: QuestStore) => state.frame3;
export const selectFrame4 = (state: QuestStore) => state.frame4;
export const selectFrame5 = (state: QuestStore) => state.frame5;

export const selectStudentName = (state: QuestStore) => state.frame0.studentName;
export const selectTargetSchools = (state: QuestStore) =>
  state.frame0.targetSchools;
export const selectGradeLevel = (state: QuestStore) => state.frame0.gradeLevel;

export const selectDemographics = (state: QuestStore) =>
  state.frame1.demographics;

export const selectActivities = (state: QuestStore) => state.frame2.activities;
export const selectPrimarySpike = (state: QuestStore) =>
  state.frame2.primarySpike;

export const selectOperatingStyle = (state: QuestStore) =>
  state.frame3.operatingStyle;
export const selectHiddenCapabilities = (state: QuestStore) =>
  state.frame3.hiddenCapabilities;

export const selectSelectedBoosters = (state: QuestStore) =>
  state.frame5.selectedBoosters;
export const selectActionPlan = (state: QuestStore) => state.frame5.actionPlan;

// ============================================================================
// SCORE SELECTORS
// ============================================================================

export const selectScores = (state: QuestStore) => state.scores;

export const selectAptitudeScore = (state: QuestStore) => state.scores.aptitude;
export const selectPassionScore = (state: QuestStore) => state.scores.passion;
export const selectCommunityScore = (state: QuestStore) => state.scores.community;
export const selectOperatingScore = (state: QuestStore) => state.scores.operating;
export const selectIvyReadyScore = (state: QuestStore) => state.scores.ivyReady;
export const selectMarketReality = (state: QuestStore) =>
  state.scores.marketReality;

export const selectScoreBreakdown = (state: QuestStore) => {
  const { ivyReady } = state.scores;
  if (!ivyReady) return null;

  return {
    total: ivyReady.total,
    tier: ivyReady.tier,
    aptitude: ivyReady.breakdown.aptitude,
    passion: ivyReady.breakdown.passion,
    community: ivyReady.breakdown.community,
    operating: ivyReady.breakdown.operating,
  };
};

export const selectSchoolFits = (state: QuestStore) =>
  state.scores.marketReality?.schoolFits ?? [];

export const selectBestFitSchool = (state: QuestStore) => {
  const fits = state.scores.marketReality?.schoolFits ?? [];
  return fits.length > 0 ? fits[0] : null;
};

// ============================================================================
// PROGRESS SELECTORS
// ============================================================================

export const selectIsComplete = (state: QuestStore) => state.isComplete;

function getFrameCardCount(frameId: FrameId): number {
  const cardCounts: Record<FrameId, number> = {
    0: 4,
    1: 4,
    2: 6,
    3: 5,
    4: 3,
    5: 4,
  };
  return cardCounts[frameId];
}

export const selectQuestProgress = (state: QuestStore): QuestProgress => {
  const completedFrames = state.navigation.completedFrames;
  const currentFrame = state.navigation.currentFrame;
  const allFrames: FrameId[] = [0, 1, 2, 3, 4, 5];

  const remainingFrames = allFrames.filter((f) => !completedFrames.includes(f));

  // Calculate frame-level progress
  const frameProgress: QuestProgress['frameProgress'] =
    {} as QuestProgress['frameProgress'];

  for (const frameId of allFrames) {
    const isComplete = completedFrames.includes(frameId);
    const isCurrent = currentFrame === frameId;

    let percentComplete = 0;
    if (isComplete) {
      percentComplete = 100;
    } else if (isCurrent) {
      const cardCount = getFrameCardCount(frameId);
      percentComplete = ((state.navigation.currentCard - 1) / cardCount) * 100;
    }

    frameProgress[frameId] = {
      isComplete,
      percentComplete,
      cardsCompleted: isComplete
        ? getFrameCardCount(frameId)
        : isCurrent
          ? state.navigation.currentCard - 1
          : 0,
      totalCards: getFrameCardCount(frameId),
    };
  }

  // Overall progress
  const totalCards = allFrames.reduce<number>((sum, f) => sum + getFrameCardCount(f), 0);
  const completedCards = Object.values(frameProgress).reduce(
    (sum, fp) => sum + fp.cardsCompleted,
    0
  );
  const percentComplete = Math.round((completedCards / totalCards) * 100);

  // Estimated time remaining (assuming 30 seconds per card)
  const remainingCards = totalCards - completedCards;
  const estimatedTimeRemaining = Math.round(remainingCards * 0.5);

  return {
    percentComplete,
    currentFrame,
    completedFrames,
    remainingFrames,
    estimatedTimeRemaining,
    frameProgress,
  };
};

// ============================================================================
// PERSISTENCE SELECTORS
// ============================================================================

export const selectQuestId = (state: QuestStore) => state.questId;
export const selectStartedAt = (state: QuestStore) => state.startedAt;
export const selectLastUpdatedAt = (state: QuestStore) => state.lastUpdatedAt;
export const selectIsDirty = (state: QuestStore) => state.persistence.isDirty;
export const selectLastSavedAt = (state: QuestStore) =>
  state.persistence.lastSavedAt;

export const selectSessionDuration = (state: QuestStore) => {
  if (!state.startedAt) return 0;

  const start = new Date(state.startedAt).getTime();
  const end = state.completedAt
    ? new Date(state.completedAt).getTime()
    : Date.now();

  return Math.round((end - start) / 60000);
};

// ============================================================================
// COMPUTED SELECTORS
// ============================================================================

export const selectYearsToApplication = (state: QuestStore) => {
  const gradeLevel = state.frame0.gradeLevel;
  if (!gradeLevel) return 0;

  const yearsMap: Record<string, number> = {
    '9': 4,
    '10': 3,
    '11': 2,
    '12': 1,
    gap: 1,
  };

  return yearsMap[gradeLevel] ?? 2;
};

export const selectHasNationalRecognition = (state: QuestStore) => {
  const { activities } = state.frame2;
  return activities.some(
    (a) => a.depthLevel === 'national' || a.depthLevel === 'international'
  );
};

export const selectHasAwards = (state: QuestStore) => {
  const { activities } = state.frame2;
  return activities.some((a) => a.awards && a.awards.length > 0);
};

export const selectLeadershipRoleCount = (state: QuestStore) => {
  return state.frame2.leadershipRoles.length;
};

export const selectFrame5Inputs = (state: QuestStore) => {
  const { frame0, frame1, frame2, frame3, scores } = state;

  return {
    currentScores: {
      aptitude: scores.aptitude?.total ?? 50,
      passion: scores.passion?.total ?? 50,
      community: scores.community?.total ?? 50,
      operating: scores.operating?.total ?? 50,
      ivyReady: scores.ivyReady?.total ?? 50,
    },
    targetSchools: frame0.targetSchools,
    yearsToApp: selectYearsToApplication(state),
    gradeLevel: frame0.gradeLevel ?? '11',
    hiddenCapabilities: frame3.hiddenCapabilities,
    operatingStyle: frame3.operatingStyle ?? '',
    hasNationalRecognition: selectHasNationalRecognition(state),
    leadershipRoleCount: frame2.leadershipRoles.length,
    serviceHours: frame2.serviceHours,
    apCourseCount: frame1.apCount,
    hasAwards: selectHasAwards(state),
  };
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  selectCurrentFrame,
  selectCurrentCard,
  selectCompletedFrames,
  selectCanNavigateTo,
  selectCanGoNext,
  selectCanGoPrev,
  selectFrame0,
  selectFrame1,
  selectFrame2,
  selectFrame3,
  selectFrame4,
  selectFrame5,
  selectStudentName,
  selectTargetSchools,
  selectScores,
  selectIvyReadyScore,
  selectMarketReality,
  selectScoreBreakdown,
  selectSchoolFits,
  selectIsComplete,
  selectQuestProgress,
  selectYearsToApplication,
  selectFrame5Inputs,
};
