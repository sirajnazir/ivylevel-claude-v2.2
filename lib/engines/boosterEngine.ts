/**
 * IvyQuest v3.0 — Booster Recommendation Engine
 *
 * Generates personalized booster recommendations based on student profile.
 *
 * Priority = gap × 0.40 + improvability × 0.30 + urgency × 0.30
 *
 * @version 1.0.0
 * @module engines/boosterEngine
 */

import {
  BOOSTERS,
  BOOSTERS_BY_ID,
  PRIORITY_WEIGHTS,
  URGENCY_SCORES,
  DIFFICULTY_LEVELS,
  TIME_ESTIMATES,
  type BoosterDefinition,
  type DifficultyId,
} from '../constants/frame5.constants';
import type {
  Frame5Inputs,
  Booster,
  ActionItem,
  ActionPlan,
  BoosterEngineConfig,
  BoosterEngineResult,
} from '../types/frame5.types';

// ============================================================================
// CONSTANTS
// ============================================================================

const DEFAULT_CONFIG: Required<BoosterEngineConfig> = {
  maxBoosters: 10,
  priorityThreshold: 20,
  includeCompleted: false,
};

const TARGET_SCORE = 85; // Target Ivy+ Ready Score

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Check if student is missing a specific element
 */
function isMissingElement(element: string, inputs: Frame5Inputs): boolean {
  switch (element) {
    case 'ap_depth':
      return inputs.apCourseCount < 8;
    case 'national_recognition':
      return !inputs.hasNationalRecognition;
    case 'leadership':
      return inputs.leadershipRoleCount < 2;
    case 'service_hours':
      return inputs.serviceHours < 100;
    case 'awards':
      return !inputs.hasAwards;
    case 'diversity':
      return inputs.leadershipRoleCount < 3;
    default:
      return false;
  }
}

/**
 * Check if booster triggers are satisfied
 */
function checkTriggers(booster: BoosterDefinition, inputs: Frame5Inputs): boolean {
  const { triggers } = booster;
  const currentScore = inputs.currentScores[booster.targetLayer];

  // Check score bounds
  if (triggers.minScore !== undefined && currentScore < triggers.minScore) {
    return false;
  }
  if (triggers.maxScore !== undefined && currentScore > triggers.maxScore) {
    return false;
  }

  // Check grade level
  if (triggers.gradeLevel && triggers.gradeLevel.length > 0) {
    if (!triggers.gradeLevel.includes(inputs.gradeLevel)) {
      return false;
    }
  }

  // Check capabilities
  if (triggers.capabilities && triggers.capabilities.length > 0) {
    const hasCapability = triggers.capabilities.some(cap =>
      inputs.hiddenCapabilities.includes(cap)
    );
    if (!hasCapability) {
      return false;
    }
  }

  // Check missing elements
  if (triggers.missingElements && triggers.missingElements.length > 0) {
    const isMissing = triggers.missingElements.some(elem =>
      isMissingElement(elem, inputs)
    );
    if (!isMissing) {
      return false;
    }
  }

  return true;
}

/**
 * Calculate gap score (0-100)
 * Higher gap = higher priority
 */
function calculateGapScore(currentScore: number): number {
  const gap = TARGET_SCORE - currentScore;
  return Math.min(100, Math.max(0, (gap / 50) * 100));
}

/**
 * Calculate improvability score (0-100)
 */
function calculateImprovability(
  booster: BoosterDefinition,
  inputs: Frame5Inputs
): number {
  let score = 50; // Base score

  // Grade level bonuses (academic layer)
  if (booster.targetLayer === 'aptitude') {
    const gradeNum = parseInt(inputs.gradeLevel, 10);
    if (gradeNum <= 10) {
      score += 30;
    } else if (gradeNum === 11) {
      score += 15;
    } else {
      score -= 10;
    }
  }

  // Passion layer bonuses
  if (booster.targetLayer === 'passion') {
    if (!inputs.hasNationalRecognition) {
      score += 20;
    }
    if (!inputs.hasAwards) {
      score += 15;
    }
  }

  // Community layer bonuses
  if (booster.targetLayer === 'community') {
    if (inputs.leadershipRoleCount < 2) {
      score += 25;
    }
    if (inputs.serviceHours < 100) {
      score += 15;
    }
  }

  // Operating layer always gets bonus
  if (booster.targetLayer === 'operating') {
    score += 20;
  }

  // Difficulty penalties
  const difficultyPenalties: Record<DifficultyId, number> = {
    easy: 0,
    medium: -5,
    hard: -15,
    expert: -25,
  };
  score += difficultyPenalties[booster.difficulty];

  return Math.min(100, Math.max(0, score));
}

/**
 * Calculate urgency score based on years to application
 */
function calculateUrgency(yearsToApp: number): number {
  if (yearsToApp <= 1) return URGENCY_SCORES.critical;
  if (yearsToApp === 2) return URGENCY_SCORES.high;
  return URGENCY_SCORES.moderate;
}

/**
 * Calculate impact for a booster
 */
function calculateImpact(
  booster: BoosterDefinition,
  inputs: Frame5Inputs,
  existingLayerImpact: number = 0
): number {
  let impact = booster.baseImpact;
  const currentScore = inputs.currentScores[booster.targetLayer];

  // Apply difficulty multiplier
  impact *= DIFFICULTY_LEVELS[booster.difficulty].multiplier;

  // Diminishing returns at high scores
  if (currentScore > 90) {
    impact *= 0.5;
  } else if (currentScore > 80) {
    impact *= 0.7;
  }

  // Time pressure reduction
  if (inputs.yearsToApp <= 1) {
    impact *= 0.8;
  }

  // Diminishing returns for multiple boosters in same layer
  if (existingLayerImpact > 0) {
    impact *= 0.7;
  }

  return Math.round(impact * 10) / 10;
}

/**
 * Determine match reason for a booster
 */
function getMatchReason(booster: BoosterDefinition, inputs: Frame5Inputs): string {
  const currentScore = inputs.currentScores[booster.targetLayer];
  const gap = TARGET_SCORE - currentScore;

  if (gap > 20) {
    return `Your ${booster.targetLayer} score has significant room for growth`;
  }

  if (booster.triggers.capabilities?.length) {
    const matchedCap = booster.triggers.capabilities.find(cap =>
      inputs.hiddenCapabilities.includes(cap)
    );
    if (matchedCap) {
      return `Matches your ${matchedCap.replace(/_/g, ' ')} capability`;
    }
  }

  if (booster.triggers.missingElements?.length) {
    const missingElem = booster.triggers.missingElements.find(elem =>
      isMissingElement(elem, inputs)
    );
    if (missingElem) {
      return `Addresses your missing ${missingElem.replace(/_/g, ' ')}`;
    }
  }

  return 'Recommended based on your profile';
}

/**
 * Determine confidence level
 */
function getConfidence(priority: number, impact: number): 'high' | 'medium' | 'low' {
  if (priority > 70 && impact > 8) return 'high';
  if (priority > 50 && impact > 5) return 'medium';
  return 'low';
}

// ============================================================================
// MAIN ENGINE FUNCTIONS
// ============================================================================

/**
 * Generate personalized booster recommendations
 */
export function generateBoosters(
  inputs: Frame5Inputs,
  config: BoosterEngineConfig = {}
): BoosterEngineResult {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  console.log('[BOOSTER_ENGINE] Starting booster generation', {
    yearsToApp: inputs.yearsToApp,
    gradeLevel: inputs.gradeLevel,
  });

  // Filter boosters by triggers
  const eligibleBoosters = BOOSTERS.filter(booster =>
    checkTriggers(booster, inputs)
  );

  // Calculate priority and impact for each
  const scoredBoosters: Booster[] = eligibleBoosters.map(definition => {
    const currentScore = inputs.currentScores[definition.targetLayer];
    const gapScore = calculateGapScore(currentScore);
    const improvability = calculateImprovability(definition, inputs);
    const urgency = calculateUrgency(inputs.yearsToApp);

    const priority = Math.round(
      gapScore * PRIORITY_WEIGHTS.gap +
      improvability * PRIORITY_WEIGHTS.improvability +
      urgency * PRIORITY_WEIGHTS.urgency
    );

    const impact = calculateImpact(definition, inputs);
    const projectedScore = Math.min(100, currentScore + impact);

    return {
      ...definition,
      priority,
      impact,
      projectedScore,
      currentScore,
      matchReason: getMatchReason(definition, inputs),
      confidence: getConfidence(priority, impact),
      isSelected: false,
      isCompleted: false,
    };
  });

  // Sort by priority (descending)
  scoredBoosters.sort((a, b) => b.priority - a.priority);

  // Filter by threshold and limit
  const filteredBoosters = scoredBoosters
    .filter(b => b.priority >= mergedConfig.priorityThreshold)
    .slice(0, mergedConfig.maxBoosters);

  console.log('[BOOSTER_ENGINE] Generated boosters', {
    total: eligibleBoosters.length,
    returned: filteredBoosters.length,
  });

  // Get top 3 recommendations
  const topRecommendations = filteredBoosters.slice(0, 3).map(b => b.id);

  return {
    boosters: filteredBoosters,
    projectedScores: null, // Calculated when boosters are selected
    topRecommendations,
  };
}

/**
 * Calculate projected scores based on selected boosters
 */
export function calculateProjectedScores(
  inputs: Frame5Inputs,
  selectedBoosters: Booster[]
): Frame5Inputs['currentScores'] {
  const projectedScores = { ...inputs.currentScores };

  // Track impact per layer for diminishing returns
  const layerImpact: Record<string, number> = {
    aptitude: 0,
    passion: 0,
    community: 0,
    operating: 0,
  };

  // Sort by impact (descending) to apply highest impact first
  const sortedBoosters = [...selectedBoosters].sort((a, b) => b.impact - a.impact);

  for (const booster of sortedBoosters) {
    const layer = booster.targetLayer;
    const definition = BOOSTERS_BY_ID[booster.id];

    if (!definition) continue;

    // Calculate impact with existing layer impact
    const impact = calculateImpact(definition, inputs, layerImpact[layer]);

    // Apply impact
    projectedScores[layer] = Math.min(100, projectedScores[layer] + impact);
    layerImpact[layer] += impact;
  }

  // Recalculate ivyReady score
  projectedScores.ivyReady = Math.round(
    projectedScores.aptitude * 0.35 +
    projectedScores.passion * 0.30 +
    projectedScores.community * 0.20 +
    projectedScores.operating * 0.15
  );

  return projectedScores;
}

/**
 * Generate action plan from selected boosters
 */
export function generateActionPlan(
  selectedBoosters: Booster[],
  inputs: Frame5Inputs
): ActionPlan {
  const items: ActionItem[] = [];
  let totalWeeks = 0;

  // Sort boosters by priority
  const sortedBoosters = [...selectedBoosters].sort((a, b) => b.priority - a.priority);

  for (const booster of sortedBoosters) {
    const definition = BOOSTERS_BY_ID[booster.id];
    if (!definition) continue;

    // Add action steps for this booster
    definition.actionSteps.forEach((step, index) => {
      items.push({
        id: `${booster.id}-step-${index + 1}`,
        boosterId: booster.id,
        step,
        order: index + 1,
        isCompleted: false,
      });
    });

    // Add to total time estimate
    totalWeeks += TIME_ESTIMATES[definition.timeEstimate].weeks;
  }

  // Calculate projected score with all selected boosters
  const projectedScores = calculateProjectedScores(inputs, selectedBoosters);

  console.log('[FRAME5.ACTION_PLAN] Generated', {
    steps: items.length,
    weeks: totalWeeks,
  });

  return {
    items,
    totalSteps: items.length,
    completedSteps: 0,
    estimatedWeeks: totalWeeks,
    projectedIvyReadyScore: projectedScores.ivyReady,
  };
}

/**
 * Get boosters by category
 */
export function getBoostersByCategory(
  boosters: Booster[],
  category: string | null
): Booster[] {
  if (!category) return boosters;
  return boosters.filter(b => b.category === category);
}

/**
 * Sort boosters by specified criteria
 */
export function sortBoosters(
  boosters: Booster[],
  sortBy: 'priority' | 'impact' | 'time' | 'difficulty'
): Booster[] {
  const sorted = [...boosters];

  switch (sortBy) {
    case 'priority':
      sorted.sort((a, b) => b.priority - a.priority);
      break;
    case 'impact':
      sorted.sort((a, b) => b.impact - a.impact);
      break;
    case 'time':
      sorted.sort((a, b) => {
        const timeA = TIME_ESTIMATES[a.timeEstimate].weeks;
        const timeB = TIME_ESTIMATES[b.timeEstimate].weeks;
        return timeA - timeB;
      });
      break;
    case 'difficulty':
      const difficultyOrder: Record<DifficultyId, number> = {
        easy: 1,
        medium: 2,
        hard: 3,
        expert: 4,
      };
      sorted.sort(
        (a, b) => difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty]
      );
      break;
  }

  return sorted;
}

export default {
  generateBoosters,
  calculateProjectedScores,
  generateActionPlan,
  getBoostersByCategory,
  sortBoosters,
};
