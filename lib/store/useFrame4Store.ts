/**
 * Frame 4: Reveal - Zustand Store
 * State management for reveal sequence, scores, and school fits
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import {
  SCHOOL_CONFIGS,
  CATEGORIES,
  SCORE_TIERS,
  FIT_LABELS,
} from '@/lib/constants/frame4.constants';
import type {
  Frame4State,
  Frame4Actions,
  Frame4StoreSlice,
  Frame4Card,
  LaunchPhase,
  AllFrameInputs,
  IvyReadyScore,
  SchoolFitCard,
  CategoryBreakdown,
  DemographicInputs,
} from '@/lib/types/frame4.types';

// Card order for navigation
const CARD_ORDER: Frame4Card[] = ['launch', 'dualScore', 'schoolCards', 'categoryBreakdown'];

// Initial state
export const initialFrame4State: Frame4State = {
  currentCard: 'launch',
  launchPhase: 'idle',
  isAnimating: false,
  ivyReadyScore: null,
  schoolFits: [],
  categoryBreakdowns: [],
  activeSchoolIndex: 0,
  autoplayEnabled: true,
  hasSeenLaunch: false,
  frameStartTime: null,
  cardStartTimes: {
    launch: null,
    dualScore: null,
    schoolCards: null,
    categoryBreakdown: null,
  },
};

/**
 * Calculate Ivy+ Ready Score from all frame inputs
 */
function calculateIvyReadyScore(inputs: AllFrameInputs): IvyReadyScore {
  const { aptitudeScore, passionScore, communityScore, readinessScore, demographicMultipliers } = inputs;

  // Base score from category weights
  const baseScore =
    aptitudeScore * 0.35 +
    passionScore * 0.30 +
    communityScore * 0.20 +
    readinessScore * 0.15;

  // Calculate multipliers
  const firstGenMultiplier = demographicMultipliers.firstGen ? 1.08 : 1.0;
  const urmMultiplier = demographicMultipliers.urm ? 1.05 : 1.0;
  const legacyMultiplier = Object.values(demographicMultipliers.legacy).some(Boolean) ? 1.03 : 1.0;

  // Apply multipliers
  const totalMultiplier = firstGenMultiplier * urmMultiplier * legacyMultiplier;
  const totalScore = Math.min(100, Math.round(baseScore * totalMultiplier));

  // Determine tier
  let tier: IvyReadyScore['tier'] = 'below';
  if (totalScore >= SCORE_TIERS.exceptional.min) tier = 'exceptional';
  else if (totalScore >= SCORE_TIERS.competitive.min) tier = 'competitive';
  else if (totalScore >= SCORE_TIERS.average.min) tier = 'average';

  // Calculate percentile (simplified)
  const percentile = Math.min(99, Math.round(totalScore * 0.95));

  return {
    total: totalScore,
    tier,
    percentile,
    categoryScores: {
      aptitude: Math.round(aptitudeScore),
      passion: Math.round(passionScore),
      community: Math.round(communityScore),
      operating: Math.round(readinessScore),
    },
    multipliers: {
      firstGen: firstGenMultiplier,
      urm: urmMultiplier,
      legacy: legacyMultiplier,
    },
  };
}

/**
 * Calculate market reality (probability) for a school
 */
function calculateMarketReality(
  schoolId: string,
  ivyReadyScore: number,
  demographics: DemographicInputs
): { min: number; max: number; label: 'reach' | 'target' | 'safety' } {
  const school = SCHOOL_CONFIGS[schoolId];
  if (!school) {
    return { min: 1, max: 5, label: 'reach' };
  }

  const baseRate = school.acceptanceRate * 100; // Convert to percentage

  // Apply demographic adjustments
  let adjustedRate = baseRate;
  if (demographics.legacy[schoolId]) adjustedRate *= 2.5;
  if (demographics.firstGen) adjustedRate *= 1.3;
  if (demographics.urm) adjustedRate *= 1.4;

  // Apply score-based adjustment
  const scoreMultiplier = 0.5 + (ivyReadyScore / 100);
  adjustedRate *= scoreMultiplier;

  // Create range with variance
  const variance = adjustedRate * 0.3;
  const min = Math.max(1, Math.round(adjustedRate - variance));
  const max = Math.min(100, Math.round(adjustedRate + variance));

  // Determine fit label
  let label: 'reach' | 'target' | 'safety' = 'reach';
  const avgRate = (min + max) / 2;
  if (avgRate >= FIT_LABELS.safety.min) label = 'safety';
  else if (avgRate >= FIT_LABELS.target.min) label = 'target';

  return { min, max, label };
}

/**
 * Generate key insight for a school based on student profile
 */
function generateSchoolInsight(
  schoolId: string,
  inputs: AllFrameInputs
): string {
  const school = SCHOOL_CONFIGS[schoolId];
  if (!school) return 'Your profile shows promise for this institution.';

  const { spikeCategory, studentArchetype, operatingStyle } = inputs;

  // Match spike to school strengths
  if (school.strengths.includes('research') && spikeCategory === 'research') {
    return `Your research focus aligns with ${school.name.split(' ')[0]}'s emphasis on discovery.`;
  }
  if (school.strengths.includes('entrepreneurship') && spikeCategory === 'business') {
    return `Your entrepreneurial spirit fits ${school.name.split(' ')[0]}'s innovation culture.`;
  }
  if (school.strengths.includes('arts') && spikeCategory === 'arts') {
    return `Your creative pursuits resonate with ${school.name.split(' ')[0]}'s artistic community.`;
  }
  if (school.strengths.includes('stem') && spikeCategory === 'stem') {
    return `Your STEM focus aligns well with ${school.name.split(' ')[0]}'s technical excellence.`;
  }
  if (school.strengths.includes('community') && studentArchetype === 'Community Builder') {
    return `Your community focus matches ${school.name.split(' ')[0]}'s collaborative culture.`;
  }

  return `${school.culture}`;
}

/**
 * Calculate school fit cards for all target schools
 */
function calculateSchoolFits(
  inputs: AllFrameInputs,
  ivyReadyScore: IvyReadyScore
): SchoolFitCard[] {
  const { targetSchools, demographicMultipliers } = inputs;

  return targetSchools.map((schoolId) => {
    const school = SCHOOL_CONFIGS[schoolId];
    const probability = calculateMarketReality(
      schoolId,
      ivyReadyScore.total,
      demographicMultipliers
    );

    // Calculate school-specific category adjustments
    const categoryScores = {
      aptitude: ivyReadyScore.categoryScores.aptitude,
      passion: ivyReadyScore.categoryScores.passion,
      community: ivyReadyScore.categoryScores.community,
      operating: ivyReadyScore.categoryScores.operating,
    };

    // Calculate overall fit score
    const fitScore = Math.round(
      (categoryScores.aptitude + categoryScores.passion + categoryScores.community + categoryScores.operating) / 4
    );

    return {
      schoolId,
      schoolName: school?.name || schoolId,
      probability,
      fitLabel: probability.label,
      fitScore,
      keyInsight: generateSchoolInsight(schoolId, inputs),
      categoryScores,
      schoolColor: school?.color || '#4A90D9',
      culture: school?.culture || '',
    };
  });
}

/**
 * Generate category breakdown with insights
 */
function generateCategoryBreakdowns(ivyReadyScore: IvyReadyScore): CategoryBreakdown[] {
  return CATEGORIES.map((cat) => {
    const score = ivyReadyScore.categoryScores[cat.id as keyof typeof ivyReadyScore.categoryScores];

    // Determine status
    let status: CategoryBreakdown['status'] = 'average';
    if (score >= 70) status = 'strength';
    else if (score < 50) status = 'improvement';

    // Generate insight
    let insight = '';
    if (status === 'strength') {
      insight = `Your ${cat.label.toLowerCase()} is a standout asset in your profile.`;
    } else if (status === 'improvement') {
      insight = `Focus on boosting your ${cat.label.toLowerCase()} for stronger applications.`;
    } else {
      insight = `Your ${cat.label.toLowerCase()} is solid but has room to grow.`;
    }

    return {
      id: cat.id,
      label: cat.label,
      icon: cat.icon,
      score,
      weight: cat.weight,
      status,
      insight,
    };
  });
}

/**
 * Frame 4 Zustand store
 */
export const useFrame4Store = create<Frame4StoreSlice>()(
  immer((set, get) => ({
    ...initialFrame4State,

    // Navigation
    setCurrentCard: (card) => {
      set((state) => {
        state.currentCard = card;
        if (!state.cardStartTimes[card]) {
          state.cardStartTimes[card] = Date.now();
        }
      });
      // Trace logging
      console.log('FRAME4.CARD', `Navigated to: ${card}`);
    },

    nextCard: () => {
      const { currentCard } = get();
      const currentIndex = CARD_ORDER.indexOf(currentCard);
      if (currentIndex < CARD_ORDER.length - 1) {
        const nextCard = CARD_ORDER[currentIndex + 1];
        get().setCurrentCard(nextCard);
      }
    },

    prevCard: () => {
      const { currentCard } = get();
      const currentIndex = CARD_ORDER.indexOf(currentCard);
      if (currentIndex > 0) {
        const prevCard = CARD_ORDER[currentIndex - 1];
        get().setCurrentCard(prevCard);
      }
    },

    // Launch sequence
    setLaunchPhase: (phase) => {
      set((state) => {
        state.launchPhase = phase;
      });
      console.log('FRAME4.LAUNCH', `Phase: ${phase}`);
    },

    startLaunchSequence: () => {
      set((state) => {
        state.launchPhase = 'countdown';
        state.isAnimating = true;
      });
    },

    // Score calculation
    calculateScores: (inputs) => {
      const ivyReadyScore = calculateIvyReadyScore(inputs);
      const schoolFits = calculateSchoolFits(inputs, ivyReadyScore);
      const categoryBreakdowns = generateCategoryBreakdowns(ivyReadyScore);

      set((state) => {
        state.ivyReadyScore = ivyReadyScore;
        state.schoolFits = schoolFits;
        state.categoryBreakdowns = categoryBreakdowns;
      });

      console.log('FRAME4.SCORE', `IvyReady: ${ivyReadyScore.total}, Schools: ${schoolFits.length}`);
    },

    // School cards
    setActiveSchoolIndex: (index) => {
      const { schoolFits } = get();
      if (index >= 0 && index < schoolFits.length) {
        set((state) => {
          state.activeSchoolIndex = index;
        });
        const school = schoolFits[index];
        console.log('FRAME4.SCHOOL', `Viewed: ${school.schoolId}, Probability: ${school.probability.min}-${school.probability.max}%`);
      }
    },

    nextSchool: () => {
      const { activeSchoolIndex, schoolFits } = get();
      const nextIndex = (activeSchoolIndex + 1) % schoolFits.length;
      get().setActiveSchoolIndex(nextIndex);
    },

    prevSchool: () => {
      const { activeSchoolIndex, schoolFits } = get();
      const prevIndex = activeSchoolIndex === 0 ? schoolFits.length - 1 : activeSchoolIndex - 1;
      get().setActiveSchoolIndex(prevIndex);
    },

    toggleAutoplay: () => {
      set((state) => {
        state.autoplayEnabled = !state.autoplayEnabled;
      });
    },

    // Animation state
    setIsAnimating: (animating) => {
      set((state) => {
        state.isAnimating = animating;
      });
    },

    // Timing
    startFrame: () => {
      set((state) => {
        state.frameStartTime = Date.now();
        state.cardStartTimes.launch = Date.now();
      });
    },

    recordCardStart: (card) => {
      set((state) => {
        state.cardStartTimes[card] = Date.now();
      });
    },

    // Reset
    reset: () => {
      set(() => ({ ...initialFrame4State }));
    },
  }))
);

// Selector hooks for common state slices
export const useFrame4Card = () => useFrame4Store((s) => s.currentCard);
export const useFrame4LaunchPhase = () => useFrame4Store((s) => s.launchPhase);
export const useFrame4IvyScore = () => useFrame4Store((s) => s.ivyReadyScore);
export const useFrame4SchoolFits = () => useFrame4Store((s) => s.schoolFits);
export const useFrame4Categories = () => useFrame4Store((s) => s.categoryBreakdowns);
export const useFrame4ActiveSchool = () => {
  const index = useFrame4Store((s) => s.activeSchoolIndex);
  const fits = useFrame4Store((s) => s.schoolFits);
  return fits[index] || null;
};
