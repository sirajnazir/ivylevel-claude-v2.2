/**
 * IvyQuest v3.0 — Master Zustand Store
 *
 * Unified store combining all frame slices with navigation and persistence.
 *
 * @version 1.0.0
 * @module store/questStore.master
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { subscribeWithSelector } from 'zustand/middleware';
import type {
  QuestStore,
  FrameId,
  Frame0Data,
  Frame1Data,
  Frame2Data,
  Frame3Data,
  Frame4Data,
  Frame5Data,
  QuestScores,
  NavigationState,
  PersistenceState,
  SavedSession,
  DemographicsData,
} from '../types/integration.types';

// ============================================================================
// CONSTANTS
// ============================================================================

const QUEST_VERSION = '3.0.0';
const STORAGE_KEY = 'ivyquest_v3_current';

// Custom UUID generator (replaces uuid package)
function generateQuestId(): string {
  // Use crypto.randomUUID if available (modern browsers and Node.js 19+)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback to manual UUID v4 generation
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// ============================================================================
// INITIAL STATES
// ============================================================================

const initialFrame0: Frame0Data = {
  role: null,
  studentName: '',
  gradeLevel: null,
  targetSchools: [],
  intendedMajor: null,
  majorCertainty: 'exploring',
  twinInitialized: false,
};

const initialFrame1: Frame1Data = {
  gpa: null,
  isWeightedGPA: false,
  sat: null,
  act: null,
  apCount: 0,
  ibCount: 0,
  honorsCount: 0,
  classRank: null,
  classSize: null,
  isRanked: false,
  demographics: {
    firstGen: false,
    urm: false,
    lowIncome: false,
    legacy: null,
    recruitedAthlete: false,
    developmentCase: false,
    facultyChild: false,
  },
};

const initialFrame2: Frame2Data = {
  activities: [],
  primarySpike: null,
  spikeDepth: 'local',
  leadershipRoles: [],
  serviceHours: 0,
  impactScope: 'local',
  diversityOfInvolvement: 0,
};

const initialFrame3: Frame3Data = {
  timeBand: null,
  operatingStyle: null,
  energyPattern: null,
  productivityPeak: 'flexible',
  hiddenCapabilities: [],
  auraType: null,
};

const initialFrame4: Frame4Data = {
  hasViewedScores: false,
  hasViewedSchoolFits: false,
  revealSequenceComplete: false,
  selectedSchoolForDetail: null,
};

const initialFrame5: Frame5Data = {
  boosters: [],
  selectedBoosters: [],
  actionPlan: null,
};

const initialScores: QuestScores = {
  aptitude: null,
  passion: null,
  community: null,
  operating: null,
  ivyReady: null,
  marketReality: null,
  calculatedAt: null,
};

const initialNavigation: NavigationState = {
  currentFrame: 0,
  currentCard: 1,
  completedFrames: [],
  canNavigateTo: [0],
  history: [],
};

const createInitialPersistence = (): PersistenceState => ({
  questId: generateQuestId(),
  version: QUEST_VERSION,
  startedAt: new Date().toISOString(),
  lastUpdatedAt: new Date().toISOString(),
  autoSaveEnabled: true,
  lastSavedAt: null,
  isDirty: false,
});

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

function isFrame0Complete(data: Frame0Data): boolean {
  return (
    data.role !== null &&
    data.studentName.trim().length >= 2 &&
    data.gradeLevel !== null &&
    data.targetSchools.length >= 1 &&
    data.intendedMajor !== null
  );
}

function isFrame1Complete(data: Frame1Data): boolean {
  return data.gpa !== null && data.gpa > 0;
}

function isFrame2Complete(data: Frame2Data): boolean {
  return data.activities.length >= 1 || data.leadershipRoles.length >= 1;
}

function isFrame3Complete(data: Frame3Data): boolean {
  return data.timeBand !== null && data.operatingStyle !== null;
}

function isFrame4Complete(data: Frame4Data): boolean {
  return data.revealSequenceComplete;
}

function isFrame5Complete(data: Frame5Data): boolean {
  return data.selectedBoosters.length >= 1 && data.actionPlan !== null;
}

function calculateCanNavigateTo(completedFrames: FrameId[]): FrameId[] {
  const canNavigate: FrameId[] = [0]; // Always can go to frame 0

  // Can navigate to any completed frame
  for (const frame of completedFrames) {
    if (!canNavigate.includes(frame)) {
      canNavigate.push(frame);
    }
  }

  // Can navigate to next frame after last completed
  const maxCompleted = Math.max(...completedFrames, -1);
  const nextFrame = (maxCompleted + 1) as FrameId;
  if (nextFrame <= 5 && !canNavigate.includes(nextFrame)) {
    canNavigate.push(nextFrame);
  }

  return canNavigate.sort((a, b) => a - b);
}

// ============================================================================
// SCORING FUNCTIONS
// ============================================================================

function calculateAptitude(frame1: Frame1Data) {
  const gpa = frame1.gpa ?? 0;
  const gpaScore = (gpa / 4.0) * 100;

  let testScore = 70;
  if (frame1.sat) {
    testScore = ((frame1.sat - 400) / 1200) * 100;
  } else if (frame1.act) {
    testScore = ((frame1.act - 1) / 35) * 100;
  }

  const rigorScore = Math.min(
    100,
    (frame1.apCount * 8 + frame1.ibCount * 10 + frame1.honorsCount * 4) / 1.5
  );

  let rankScore = 70;
  if (frame1.isRanked && frame1.classRank && frame1.classSize) {
    rankScore = (1 - frame1.classRank / frame1.classSize) * 100;
  }

  const total =
    gpaScore * 0.35 + testScore * 0.35 + rigorScore * 0.2 + rankScore * 0.1;

  return {
    total: Math.round(Math.min(100, Math.max(0, total)) * 10) / 10,
    breakdown: {
      gpa: Math.round(gpaScore * 10) / 10,
      test: Math.round(testScore * 10) / 10,
      rigor: Math.round(rigorScore * 10) / 10,
      rank: Math.round(rankScore * 10) / 10,
    },
    flags: {
      testOptional: !frame1.sat && !frame1.act,
      unranked: !frame1.isRanked,
      weightedGPA: frame1.isWeightedGPA,
    },
  };
}

function calculatePassion(frame2: Frame2Data) {
  const spikeScore = frame2.primarySpike ? 60 : 30;
  const depthMultiplier =
    { international: 2, national: 1.5, state: 1.3, regional: 1.1, local: 1 }[
      frame2.spikeDepth
    ] ?? 1;
  const spikeDepthScore = Math.min(100, spikeScore * depthMultiplier);

  const awardScore = frame2.activities.reduce(
    (sum, a) => sum + (a.awards?.length ?? 0) * 15,
    0
  );
  const consistencyScore =
    Math.max(...frame2.activities.map((a) => a.yearsActive), 0) * 25;
  const uniquenessScore =
    new Set(frame2.activities.map((a) => a.category)).size * 15;

  const total =
    spikeDepthScore * 0.4 +
    Math.min(100, awardScore) * 0.3 +
    Math.min(100, consistencyScore) * 0.2 +
    Math.min(100, uniquenessScore) * 0.1;

  return {
    total: Math.round(Math.min(100, Math.max(0, total)) * 10) / 10,
    breakdown: {
      spikeDepth: Math.round(spikeDepthScore * 10) / 10,
      awards: Math.round(Math.min(100, awardScore) * 10) / 10,
      consistency: Math.round(Math.min(100, consistencyScore) * 10) / 10,
      uniqueness: Math.round(Math.min(100, uniquenessScore) * 10) / 10,
    },
    spikeCategory: frame2.primarySpike,
    topActivities: frame2.activities.slice(0, 3),
  };
}

function calculateCommunity(frame2: Frame2Data) {
  const leadershipPoints = {
    founder: 30,
    president: 25,
    captain: 20,
    vice_president: 18,
    officer: 15,
    editor: 15,
    member: 5,
  };
  const leadershipScore = Math.min(
    100,
    frame2.leadershipRoles.reduce(
      (sum, r) =>
        sum +
        (leadershipPoints[r.role as keyof typeof leadershipPoints] ?? 5),
      0
    )
  );

  const impactMultiplier =
    {
      international: 2,
      national: 1.5,
      state: 1.2,
      regional: 1.1,
      local: 1,
      school: 0.8,
    }[frame2.impactScope] ?? 1;
  const impactScore = Math.min(100, 40 * impactMultiplier);

  const serviceScore =
    frame2.serviceHours >= 200
      ? 100
      : frame2.serviceHours >= 100
        ? 70
        : frame2.serviceHours >= 50
          ? 50
          : 30;
  const diversityScore = frame2.diversityOfInvolvement * 10;

  const total =
    leadershipScore * 0.4 +
    impactScore * 0.3 +
    serviceScore * 0.2 +
    diversityScore * 0.1;

  return {
    total: Math.round(Math.min(100, Math.max(0, total)) * 10) / 10,
    breakdown: {
      leadership: Math.round(leadershipScore * 10) / 10,
      impact: Math.round(impactScore * 10) / 10,
      service: Math.round(serviceScore * 10) / 10,
      diversity: Math.round(diversityScore * 10) / 10,
    },
    topRoles: frame2.leadershipRoles.slice(0, 3),
  };
}

function calculateOperating(frame3: Frame3Data) {
  const timeScores = {
    '20+': 100,
    '15-20': 85,
    '10-15': 70,
    '5-10': 55,
    '<5': 40,
  };
  const timeScore =
    timeScores[frame3.timeBand as keyof typeof timeScores] ?? 50;

  const styleScore = frame3.operatingStyle ? 70 : 50;
  const energyScore = frame3.energyPattern === 'balanced' ? 80 : 60;
  const capabilityBonus = Math.min(15, frame3.hiddenCapabilities.length * 3);

  const total =
    timeScore * 0.4 + styleScore * 0.3 + (energyScore + capabilityBonus) * 0.3;

  return {
    total: Math.round(Math.min(100, Math.max(0, total)) * 10) / 10,
    breakdown: {
      timeCapacity: Math.round(timeScore * 10) / 10,
      styleMatch: Math.round(styleScore * 10) / 10,
      energy: Math.round((energyScore + capabilityBonus) * 10) / 10,
    },
    style: frame3.operatingStyle || 'unknown',
    matchedSchools: [],
  };
}

function calculateIvyReady(
  aptitude: ReturnType<typeof calculateAptitude>,
  passion: ReturnType<typeof calculatePassion>,
  community: ReturnType<typeof calculateCommunity>,
  operating: ReturnType<typeof calculateOperating>,
  demographics: DemographicsData
) {
  const rawScore =
    aptitude.total * 0.35 +
    passion.total * 0.3 +
    community.total * 0.2 +
    operating.total * 0.15;

  let multiplier = 1.0;
  if (demographics.firstGen) multiplier *= 1.3;
  if (demographics.urm) multiplier *= 1.4;
  if (demographics.lowIncome) multiplier *= 1.25;

  const finalScore = Math.min(100, rawScore * multiplier);

  const tier =
    finalScore >= 85
      ? ('exceptional' as const)
      : finalScore >= 70
        ? ('competitive' as const)
        : finalScore >= 50
          ? ('average' as const)
          : ('developing' as const);

  return {
    total: Math.round(finalScore * 10) / 10,
    tier,
    breakdown: {
      aptitude: aptitude.total,
      passion: passion.total,
      community: community.total,
      operating: operating.total,
    },
    weights: {
      aptitude: 0.35,
      passion: 0.3,
      community: 0.2,
      operating: 0.15,
    },
    demographicMultiplier: multiplier,
    rawScore: Math.round(rawScore * 10) / 10,
  };
}

function calculateMarketReality(
  targetSchools: string[],
  ivyReady: ReturnType<typeof calculateIvyReady>,
  demographics: DemographicsData
) {
  const schoolConfigs: Record<string, { name: string; rate: number }> = {
    harvard: { name: 'Harvard', rate: 3.2 },
    yale: { name: 'Yale', rate: 4.5 },
    princeton: { name: 'Princeton', rate: 4.0 },
    stanford: { name: 'Stanford', rate: 3.7 },
    mit: { name: 'MIT', rate: 3.9 },
    columbia: { name: 'Columbia', rate: 3.9 },
    penn: { name: 'Penn', rate: 5.9 },
    brown: { name: 'Brown', rate: 5.1 },
    duke: { name: 'Duke', rate: 6.0 },
    northwestern: { name: 'Northwestern', rate: 7.0 },
  };

  const schoolFits = targetSchools.map((schoolId) => {
    const config = schoolConfigs[schoolId.toLowerCase()] || {
      name: schoolId,
      rate: 10,
    };
    const scoreMultiplier = 0.5 + ivyReady.total / 100;
    let probability = config.rate * scoreMultiplier;

    if (demographics.legacy === schoolId) probability *= 5;
    if (demographics.recruitedAthlete) probability *= 80;

    probability = Math.min(95, Math.max(1, probability));

    const fitLabel =
      probability >= 30
        ? ('safety' as const)
        : probability >= 15
          ? ('target' as const)
          : probability >= 5
            ? ('reach' as const)
            : ('far_reach' as const);

    return {
      schoolId,
      schoolName: config.name,
      probability: Math.round(probability * 10) / 10,
      probabilityRange: {
        low: Math.round(probability * 0.7 * 10) / 10,
        high: Math.round(Math.min(95, probability * 1.3) * 10) / 10,
      },
      fitLabel,
      categoryScores: ivyReady.breakdown,
      styleMatch: 70,
      insights: {
        strengths: ['Strong academic profile'],
        improvements: ['Consider deeper spike'],
      },
    };
  });

  schoolFits.sort((a, b) => b.probability - a.probability);

  return {
    schoolFits,
    overallProbability:
      schoolFits.reduce((sum, f) => sum + f.probability, 0) /
        schoolFits.length || 0,
    bestFitSchool: schoolFits[0]?.schoolId || '',
    reachSchools: schoolFits
      .filter((f) => f.fitLabel === 'reach' || f.fitLabel === 'far_reach')
      .map((f) => f.schoolId),
    targetSchools: schoolFits
      .filter((f) => f.fitLabel === 'target')
      .map((f) => f.schoolId),
    safetySchools: schoolFits
      .filter((f) => f.fitLabel === 'safety')
      .map((f) => f.schoolId),
  };
}

// ============================================================================
// STORE CREATION
// ============================================================================

export const useQuestMasterStore = create<QuestStore>()(
  subscribeWithSelector(
    immer((set, get) => ({
      // ========================================================================
      // INITIAL STATE
      // ========================================================================

      questId: '',
      version: QUEST_VERSION,
      startedAt: '',
      lastUpdatedAt: '',

      navigation: initialNavigation,

      frame0: initialFrame0,
      frame1: initialFrame1,
      frame2: initialFrame2,
      frame3: initialFrame3,
      frame4: initialFrame4,
      frame5: initialFrame5,

      scores: initialScores,

      isComplete: false,
      completedAt: null,

      persistence: createInitialPersistence(),

      // ========================================================================
      // LIFECYCLE ACTIONS
      // ========================================================================

      initializeQuest: () => {
        const now = new Date().toISOString();
        const questId = generateQuestId();

        console.log('[QUEST.INIT]', questId);

        set((state) => {
          state.questId = questId;
          state.version = QUEST_VERSION;
          state.startedAt = now;
          state.lastUpdatedAt = now;

          state.navigation = { ...initialNavigation };

          state.frame0 = { ...initialFrame0 };
          state.frame1 = { ...initialFrame1 };
          state.frame2 = { ...initialFrame2 };
          state.frame3 = { ...initialFrame3 };
          state.frame4 = { ...initialFrame4 };
          state.frame5 = { ...initialFrame5 };

          state.scores = { ...initialScores };

          state.isComplete = false;
          state.completedAt = null;

          state.persistence = {
            ...createInitialPersistence(),
            questId,
          };
        });
      },

      resetQuest: () => {
        console.log('[QUEST.RESET]');
        get().initializeQuest();
      },

      completeQuest: () => {
        const { frame5, scores, frame0 } = get();

        if (!isFrame5Complete(frame5)) {
          console.warn('[QUEST.COMPLETE] Cannot complete - Frame 5 incomplete');
          return;
        }

        const now = new Date().toISOString();

        console.log('[QUEST.COMPLETE]', {
          studentName: frame0.studentName,
          ivyReady: scores.ivyReady?.total,
          boosters: frame5.selectedBoosters.length,
        });

        set((state) => {
          state.isComplete = true;
          state.completedAt = now;
          state.lastUpdatedAt = now;
          state.navigation.completedFrames = [0, 1, 2, 3, 4, 5];
        });

        get().saveSession();
      },

      // ========================================================================
      // NAVIGATION ACTIONS
      // ========================================================================

      navigationActions: {
        goToFrame: (frame: FrameId) => {
          const { navigation } = get();

          if (!navigation.canNavigateTo.includes(frame)) {
            console.warn('[NAV.GO_TO] Cannot navigate to frame', frame);
            return false;
          }

          console.log('[NAV.GO_TO]', {
            from: navigation.currentFrame,
            to: frame,
          });

          set((state) => {
            state.navigation.history.push({
              frame: state.navigation.currentFrame,
              timestamp: new Date().toISOString(),
            });
            state.navigation.currentFrame = frame;
            state.navigation.currentCard = 1;
            state.lastUpdatedAt = new Date().toISOString();
            state.persistence.isDirty = true;
          });

          return true;
        },

        nextFrame: () => {
          const { navigation } = get();
          const current = navigation.currentFrame;

          // Check if current frame is complete
          const state = get();
          const completionChecks: Record<FrameId, boolean> = {
            0: isFrame0Complete(state.frame0),
            1: isFrame1Complete(state.frame1),
            2: isFrame2Complete(state.frame2),
            3: isFrame3Complete(state.frame3),
            4: isFrame4Complete(state.frame4),
            5: isFrame5Complete(state.frame5),
          };

          if (!completionChecks[current]) {
            console.warn('[NAV.NEXT] Current frame not complete', current);
            return false;
          }

          if (current >= 5) {
            console.warn('[NAV.NEXT] Already at last frame');
            return false;
          }

          const nextFrame = (current + 1) as FrameId;

          console.log('[NAV.NEXT]', { from: current, to: nextFrame });

          set((s) => {
            if (!s.navigation.completedFrames.includes(current)) {
              s.navigation.completedFrames.push(current);
            }

            s.navigation.history.push({
              frame: current,
              timestamp: new Date().toISOString(),
            });
            s.navigation.currentFrame = nextFrame;
            s.navigation.currentCard = 1;
            s.navigation.canNavigateTo = calculateCanNavigateTo(
              s.navigation.completedFrames
            );

            s.lastUpdatedAt = new Date().toISOString();
            s.persistence.isDirty = true;
          });

          // Trigger score calculation when moving to Frame 4
          if (nextFrame === 4) {
            get().calculateScores();
          }

          return true;
        },

        prevFrame: () => {
          const { navigation } = get();
          const current = navigation.currentFrame;

          if (current <= 0) {
            console.warn('[NAV.PREV] Already at first frame');
            return false;
          }

          const prevFrame = (current - 1) as FrameId;

          console.log('[NAV.PREV]', { from: current, to: prevFrame });

          set((state) => {
            state.navigation.history.push({
              frame: current,
              timestamp: new Date().toISOString(),
            });
            state.navigation.currentFrame = prevFrame;
            state.navigation.currentCard = 1;
            state.lastUpdatedAt = new Date().toISOString();
          });

          return true;
        },

        setCurrentCard: (card: number) => {
          set((state) => {
            state.navigation.currentCard = card;
          });
        },

        markFrameComplete: (frame: FrameId) => {
          set((state) => {
            if (!state.navigation.completedFrames.includes(frame)) {
              state.navigation.completedFrames.push(frame);
              state.navigation.canNavigateTo = calculateCanNavigateTo(
                state.navigation.completedFrames
              );
            }
            state.lastUpdatedAt = new Date().toISOString();
            state.persistence.isDirty = true;
          });
        },
      },

      // ========================================================================
      // FRAME UPDATE ACTIONS
      // ========================================================================

      updateFrame0: (data: Partial<Frame0Data>) => {
        set((state) => {
          Object.assign(state.frame0, data);
          state.lastUpdatedAt = new Date().toISOString();
          state.persistence.isDirty = true;
        });
      },

      updateFrame1: (data: Partial<Frame1Data>) => {
        set((state) => {
          if (data.demographics) {
            Object.assign(state.frame1.demographics, data.demographics);
            const { demographics: _, ...rest } = data;
            Object.assign(state.frame1, rest);
          } else {
            Object.assign(state.frame1, data);
          }
          state.lastUpdatedAt = new Date().toISOString();
          state.persistence.isDirty = true;
        });
      },

      updateFrame2: (data: Partial<Frame2Data>) => {
        set((state) => {
          Object.assign(state.frame2, data);
          state.lastUpdatedAt = new Date().toISOString();
          state.persistence.isDirty = true;
        });
      },

      updateFrame3: (data: Partial<Frame3Data>) => {
        set((state) => {
          Object.assign(state.frame3, data);
          state.lastUpdatedAt = new Date().toISOString();
          state.persistence.isDirty = true;
        });
      },

      updateFrame4: (data: Partial<Frame4Data>) => {
        set((state) => {
          Object.assign(state.frame4, data);
          state.lastUpdatedAt = new Date().toISOString();
          state.persistence.isDirty = true;
        });
      },

      updateFrame5: (data: Partial<Frame5Data>) => {
        set((state) => {
          Object.assign(state.frame5, data);
          state.lastUpdatedAt = new Date().toISOString();
          state.persistence.isDirty = true;
        });
      },

      // ========================================================================
      // SCORE CALCULATION
      // ========================================================================

      calculateScores: () => {
        const { frame0, frame1, frame2, frame3 } = get();

        console.log('[SCORES.CALCULATE] Starting calculation');

        const aptitudeScore = calculateAptitude(frame1);
        const passionScore = calculatePassion(frame2);
        const communityScore = calculateCommunity(frame2);
        const operatingScore = calculateOperating(frame3);

        const ivyReadyScore = calculateIvyReady(
          aptitudeScore,
          passionScore,
          communityScore,
          operatingScore,
          frame1.demographics
        );

        const marketReality = calculateMarketReality(
          frame0.targetSchools,
          ivyReadyScore,
          frame1.demographics
        );

        console.log('[SCORES.CALCULATE] Complete', {
          aptitude: aptitudeScore.total,
          passion: passionScore.total,
          community: communityScore.total,
          operating: operatingScore.total,
          ivyReady: ivyReadyScore.total,
        });

        set((state) => {
          state.scores = {
            aptitude: aptitudeScore,
            passion: passionScore,
            community: communityScore,
            operating: operatingScore,
            ivyReady: ivyReadyScore,
            marketReality: marketReality,
            calculatedAt: new Date().toISOString(),
          };
          state.lastUpdatedAt = new Date().toISOString();
          state.persistence.isDirty = true;
        });
      },

      recalculateForSchool: (schoolId: string) => {
        console.log('[SCORES.RECALC_SCHOOL]', schoolId);
        get().calculateScores();
      },

      // ========================================================================
      // PERSISTENCE ACTIONS
      // ========================================================================

      saveSession: () => {
        const state = get();

        const session: SavedSession = {
          questId: state.persistence.questId,
          state: {
            questId: state.questId,
            version: state.version,
            startedAt: state.startedAt,
            lastUpdatedAt: state.lastUpdatedAt,
            navigation: state.navigation,
            frame0: state.frame0,
            frame1: state.frame1,
            frame2: state.frame2,
            frame3: state.frame3,
            frame4: state.frame4,
            frame5: state.frame5,
            scores: state.scores,
            isComplete: state.isComplete,
            completedAt: state.completedAt,
            persistence: state.persistence,
          },
          savedAt: new Date().toISOString(),
          version: QUEST_VERSION,
        };

        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

          set((s) => {
            s.persistence.lastSavedAt = session.savedAt;
            s.persistence.isDirty = false;
          });

          console.log('[PERSIST.SAVE] Session saved', session.questId);
        } catch (error) {
          console.error('[PERSIST.SAVE] Failed to save', error);
        }
      },

      loadSession: (questId?: string) => {
        try {
          const stored = localStorage.getItem(STORAGE_KEY);

          if (!stored) {
            console.log('[PERSIST.LOAD] No saved session found');
            return false;
          }

          const session: SavedSession = JSON.parse(stored);

          if (session.version !== QUEST_VERSION) {
            console.warn('[PERSIST.LOAD] Version mismatch', {
              saved: session.version,
              current: QUEST_VERSION,
            });
          }

          const savedTime = new Date(session.savedAt).getTime();
          const now = Date.now();
          const hoursOld = (now - savedTime) / (1000 * 60 * 60);

          if (hoursOld > 24) {
            console.log('[PERSIST.LOAD] Session too old', { hoursOld });
            return false;
          }

          console.log('[PERSIST.LOAD] Restoring session', session.questId);

          set((state) => {
            Object.assign(state, session.state);
            state.persistence.isDirty = false;
          });

          return true;
        } catch (error) {
          console.error('[PERSIST.LOAD] Failed to load', error);
          return false;
        }
      },

      clearSession: () => {
        try {
          localStorage.removeItem(STORAGE_KEY);
          console.log('[PERSIST.CLEAR] Session cleared');
        } catch (error) {
          console.error('[PERSIST.CLEAR] Failed to clear', error);
        }
      },

      exportSession: () => {
        const state = get();

        return {
          questId: state.persistence.questId,
          state: {
            questId: state.questId,
            version: state.version,
            startedAt: state.startedAt,
            lastUpdatedAt: state.lastUpdatedAt,
            navigation: state.navigation,
            frame0: state.frame0,
            frame1: state.frame1,
            frame2: state.frame2,
            frame3: state.frame3,
            frame4: state.frame4,
            frame5: state.frame5,
            scores: state.scores,
            isComplete: state.isComplete,
            completedAt: state.completedAt,
            persistence: state.persistence,
          },
          savedAt: new Date().toISOString(),
          version: QUEST_VERSION,
        };
      },
    }))
  )
);

// Export initial state for testing/reset purposes
export const initialState = {
  frame0: initialFrame0,
  frame1: initialFrame1,
  frame2: initialFrame2,
  frame3: initialFrame3,
  frame4: initialFrame4,
  frame5: initialFrame5,
  scores: initialScores,
  navigation: initialNavigation,
};

export default useQuestMasterStore;
