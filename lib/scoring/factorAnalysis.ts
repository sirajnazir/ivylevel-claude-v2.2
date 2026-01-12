/**
 * Universal Factor Analysis System
 *
 * PRINCIPLE: Every profile has strengths and weaknesses.
 * This system identifies them using RELATIVE thresholds
 * (what's strong/weak FOR THIS STUDENT) not absolute ones.
 */

import type { StudentProfile, IvyReadyScore } from '../types/student';

// =============================================================================
// FACTOR THRESHOLDS (Configurable)
// =============================================================================

/**
 * Thresholds define what qualifies as "strong" or "weak"
 * These use percentile-based logic relative to applicant pool
 */
export const FACTOR_THRESHOLDS = {
  // Strong = above these values
  strong: {
    gpa_normalized: 0.65,      // Top 35% = "strong"
    sat_normalized: 0.65,
    rigor_normalized: 0.60,
    leadership_normalized: 0.50,
    project_normalized: 0.40,
    research_normalized: 0.50,
    commitment_normalized: 0.60,
    service_normalized: 0.50,
    hours_normalized: 0.50,
    grit: 0.60,
    category_score: 50,        // Above 50% = above average
  },
  // Weak = below these values (aligned with P2 threshold of 75%)
  weak: {
    gpa_normalized: 0.40,      // Bottom 40% = needs work
    sat_normalized: 0.40,
    rigor_normalized: 0.35,
    awards_normalized: 0.10,   // No awards
    project_normalized: 0.30,
    service_normalized: 0.25,
    category_score: 60,        // Below 60% = needs improvement (P1/P2 range)
  },
} as const;

// =============================================================================
// FACTOR DEFINITIONS
// =============================================================================

interface FactorDefinition {
  id: string;
  check: (profile: StudentProfile, scores: IvyReadyScore['category_scores']) => boolean;
  getMessage: (profile: StudentProfile, scores?: IvyReadyScore['category_scores']) => string;
  priority: number;  // Higher = more important
}

/**
 * Helping factors - ordered by priority
 * Uses RELATIVE logic: What's good about THIS profile?
 */
export const HELPING_FACTOR_DEFINITIONS: FactorDefinition[] = [
  // Tier 1: Exceptional (truly standout)
  {
    id: 'perfect_gpa',
    check: (p) => (p.aptitude.gpa_normalized ?? 0) >= 0.95,
    getMessage: (p) => `Perfect GPA (${p.aptitude.gpa_weighted?.toFixed(2)}) — top 1%`,
    priority: 100,
  },
  {
    id: 'elite_sat',
    check: (p) => (p.aptitude.sat_normalized ?? 0) >= 0.90,
    getMessage: (p) => `Elite SAT (${p.aptitude.sat_total}) — 99th percentile`,
    priority: 95,
  },
  {
    id: 'national_research',
    check: (p) => p.passion.research_level === 'NATIONAL',
    getMessage: () => `National-level research — Regeneron/Intel caliber`,
    priority: 90,
  },
  {
    id: 'founder_leadership',
    check: (p) => p.passion.leadership_level?.includes('FOUNDER') ?? false,
    getMessage: (p) => `Founded organization (${p.passion.leadership_level}) — entrepreneurial spike`,
    priority: 90,
  },

  // Tier 2: Strong (clearly above average)
  {
    id: 'strong_gpa',
    check: (p) => (p.aptitude.gpa_normalized ?? 0) >= FACTOR_THRESHOLDS.strong.gpa_normalized,
    getMessage: (p) => `Strong GPA (${p.aptitude.gpa_weighted?.toFixed(2)}) — competitive for top schools`,
    priority: 70,
  },
  {
    id: 'strong_sat',
    check: (p) => (p.aptitude.sat_normalized ?? 0) >= FACTOR_THRESHOLDS.strong.sat_normalized,
    getMessage: (p) => `Strong SAT (${p.aptitude.sat_total}) — above median for Ivy applicants`,
    priority: 65,
  },
  {
    id: 'strong_rigor',
    check: (p) => (p.aptitude.rigor_normalized ?? 0) >= FACTOR_THRESHOLDS.strong.rigor_normalized,
    getMessage: (p) => `Solid AP rigor (${p.aptitude.ap_count} courses) — shows academic ambition`,
    priority: 60,
  },
  {
    id: 'leadership_role',
    check: (p) => (p.passion.leadership_normalized ?? 0) >= FACTOR_THRESHOLDS.strong.leadership_normalized,
    getMessage: (p) => `Leadership experience (${p.passion.leadership_level}) — demonstrates initiative`,
    priority: 55,
  },
  {
    id: 'long_commitment',
    check: (p) => (p.passion.ec_commitment_years ?? 0) >= 3,
    getMessage: (p) => `${p.passion.ec_commitment_years}+ years EC commitment — depth over breadth`,
    priority: 50,
  },
  {
    id: 'research_experience',
    check: (p) => (p.passion.research_normalized ?? 0) >= FACTOR_THRESHOLDS.strong.research_normalized,
    getMessage: (p) => `Research experience (${p.passion.research_level}) — intellectual curiosity`,
    priority: 50,
  },
  {
    id: 'service_commitment',
    check: (p) => (p.community.hours_normalized ?? 0) >= FACTOR_THRESHOLDS.strong.hours_normalized,
    getMessage: (p) => `${p.community.service_hours}+ service hours — community engagement`,
    priority: 45,
  },
  {
    id: 'high_grit',
    check: (p) => (p.assessment_intelligence?.psychometrics?.grit_resilience ?? 0) >= FACTOR_THRESHOLDS.strong.grit,
    getMessage: (p) => `High resilience score — admissions officers value persistence`,
    priority: 40,
  },

  // Tier 3: Baseline positives (everyone should have SOMETHING)
  {
    id: 'has_gpa',
    check: (p) => (p.aptitude.gpa_normalized ?? 0) > 0.3,
    getMessage: (p) => `Maintaining ${p.aptitude.gpa_weighted?.toFixed(2)} GPA — foundation for growth`,
    priority: 20,
  },
  {
    id: 'has_ecs',
    check: (p) => (p.passion.ec_commitment_years ?? 0) >= 1,
    getMessage: () => `Active in extracurriculars — shows engagement`,
    priority: 15,
  },
  {
    id: 'has_community',
    check: (p) => (p.community.service_hours ?? 0) > 0,
    getMessage: (p) => `Community service experience (${p.community.service_hours} hours)`,
    priority: 10,
  },
  {
    id: 'taking_assessment',
    check: () => true,  // Always true - fallback
    getMessage: () => `Taking initiative to assess and improve — growth mindset`,
    priority: 1,
  },
];

/**
 * Holding back factors - ordered by priority
 */
export const HOLDING_BACK_DEFINITIONS: FactorDefinition[] = [
  // Critical gaps
  {
    id: 'no_awards',
    check: (p) => (p.aptitude.awards_normalized ?? 0) < FACTOR_THRESHOLDS.weak.awards_normalized,
    getMessage: () => `No academic awards — 15% of aptitude weight unfilled`,
    priority: 80,
  },
  {
    id: 'low_project_impact',
    check: (p) => (p.passion.project_normalized ?? 0) < FACTOR_THRESHOLDS.weak.project_normalized,
    getMessage: (p) => `Low project impact (${p.passion.project_impact ?? 0} people) — aim for 200+`,
    priority: 75,
  },
  {
    id: 'weak_community',
    check: (_, scores) => scores.community < FACTOR_THRESHOLDS.weak.category_score,
    getMessage: (_p, scores) => `Community score ${scores?.community ?? 0}% — volunteer leadership gap`,
    priority: 70,
  },
  {
    id: 'no_research',
    check: (p) => p.passion.research_level === 'NONE' || !p.passion.research_level,
    getMessage: () => `No research experience — consider summer programs`,
    priority: 65,
  },
  {
    id: 'low_leadership',
    check: (p) => p.passion.leadership_level === 'PARTICIPANT' || !p.passion.leadership_level,
    getMessage: () => `Participant-level ECs only — seek officer/founder roles`,
    priority: 60,
  },

  // Competitive context
  {
    id: 'cs_penalty',
    check: (p) => ['Computer Science', 'CS', 'Engineering'].includes(p.intended_major ?? ''),
    getMessage: (p) => `${p.intended_major} is highly competitive (0.55-0.70x at top schools)`,
    priority: 50,
  },
  {
    id: 'high_saturation',
    check: (p) => p.high_school?.saturation_level === 'HIGH',
    getMessage: (p) => `Competitive high school — need differentiation from peers`,
    priority: 45,
  },

  // Moderate gaps
  {
    id: 'moderate_gpa',
    check: (p) => (p.aptitude.gpa_normalized ?? 0) < FACTOR_THRESHOLDS.weak.gpa_normalized,
    getMessage: () => `GPA below Ivy median — focus on upward trend`,
    priority: 40,
  },
  {
    id: 'short_commitment',
    check: (p) => (p.passion.ec_commitment_years ?? 0) < 2,
    getMessage: () => `Short EC history — depth matters more than breadth`,
    priority: 35,
  },
];

// =============================================================================
// JENNY INTELLIGENCE: WEAKNESS TRANSFORMATION
// =============================================================================

/**
 * Jenny Intelligence: Weakness Transformation Pattern
 * Converts raw weaknesses into narrative opportunities with actionable reframes
 */
export interface WeaknessTransformation {
  originalWeakness: string;
  narrativeReframe: string;
  actionableStep: string;
  confidenceBoost: number;  // 0-1 scale: how much this reframe helps
  timeToAddress: string;    // e.g., "3 months", "1 semester"
  exampleNarrative?: string;
}

/**
 * Weakness transformation mappings
 * Each weakness ID maps to a transformation strategy
 */
const WEAKNESS_TRANSFORMATIONS: Record<string, Omit<WeaknessTransformation, 'originalWeakness'>> = {
  no_awards: {
    narrativeReframe: 'You are a builder, not a collector. Focus your narrative on CREATING impact rather than collecting accolades.',
    actionableStep: 'Enter 2-3 competitions aligned with your spike this semester. Document your process regardless of outcome.',
    confidenceBoost: 0.7,
    timeToAddress: '6 months',
    exampleNarrative: '"I haven\'t won major awards because I\'ve been focused on building [project] that has reached [X] people..."',
  },
  low_project_impact: {
    narrativeReframe: 'Quality depth often beats quantity. Your focused effort signals genuine commitment.',
    actionableStep: 'Scale one existing project by 3x. Document measurable outcomes (users, hours, dollars raised).',
    confidenceBoost: 0.75,
    timeToAddress: '4 months',
    exampleNarrative: '"Rather than spreading thin, I went deep on [activity], transforming it from [before] to [after]..."',
  },
  weak_community: {
    narrativeReframe: 'This is your most improvable dimension. Service with authenticity creates compelling stories.',
    actionableStep: 'Find ONE cause that intersects with your interests. Commit to 4 hrs/week for 6 months.',
    confidenceBoost: 0.8,
    timeToAddress: '6 months',
    exampleNarrative: '"I discovered my passion for [cause] through [experience], which led me to..."',
  },
  no_research: {
    narrativeReframe: 'Formal research is one path. Independent investigation and project-based learning count equally.',
    actionableStep: 'Cold-email 5 professors at local universities about shadowing opportunities. Start a research blog.',
    confidenceBoost: 0.65,
    timeToAddress: '3 months to start, 1 year for results',
    exampleNarrative: '"While I haven\'t done formal lab research, my independent project on [topic] involved..."',
  },
  low_leadership: {
    narrativeReframe: 'Titles are proxies. Impact is the real signal. Create leadership through initiative.',
    actionableStep: 'Launch one new initiative within an existing activity. Document before/after metrics.',
    confidenceBoost: 0.7,
    timeToAddress: '3-6 months',
    exampleNarrative: '"Without holding a formal title, I led the effort to [achievement] which resulted in..."',
  },
  cs_penalty: {
    narrativeReframe: 'Reframe your narrative around the APPLICATION of CS rather than CS itself.',
    actionableStep: 'Identify how your CS skills solve problems in underrepresented domains (healthcare, education, arts).',
    confidenceBoost: 0.6,
    timeToAddress: 'Immediate (narrative adjustment)',
    exampleNarrative: '"I use computer science as a tool to address [problem in domain X]..."',
  },
  high_saturation: {
    narrativeReframe: 'Competition breeds excellence. Your environment has sharpened you.',
    actionableStep: 'Identify and emphasize unique aspects that differentiate you from local peers.',
    confidenceBoost: 0.5,
    timeToAddress: 'Immediate (narrative adjustment)',
    exampleNarrative: '"Growing up in [competitive area] taught me to [unique lesson/approach]..."',
  },
  moderate_gpa: {
    narrativeReframe: 'Show upward trend. Admissions officers love growth stories.',
    actionableStep: 'Focus on getting A\'s in remaining courses. Highlight any semester-over-semester improvement.',
    confidenceBoost: 0.6,
    timeToAddress: '1 semester for visible trend',
    exampleNarrative: '"After struggling in [subject], I developed [strategy] that improved my grades by [X]..."',
  },
  short_commitment: {
    narrativeReframe: 'Recent but intense engagement can be compelling. Show rapid growth and deep commitment.',
    actionableStep: 'Document your accelerated growth trajectory. Highlight meaningful moments of transformation.',
    confidenceBoost: 0.55,
    timeToAddress: 'Immediate (narrative framing)',
    exampleNarrative: '"In just [X months], I went from [beginner state] to [achievement] because..."',
  },
};

/**
 * Transform a weakness into a narrative opportunity
 */
export function transformWeakness(weaknessId: string, originalMessage: string): WeaknessTransformation | null {
  const transformation = WEAKNESS_TRANSFORMATIONS[weaknessId];
  if (!transformation) return null;

  return {
    originalWeakness: originalMessage,
    ...transformation,
  };
}

/**
 * Generate transformed weakness narratives for a profile
 * Returns both the raw weaknesses AND their transformations
 */
export function analyzeWeaknessesWithTransformations(
  profile: StudentProfile,
  categoryScores: IvyReadyScore['category_scores']
): Array<{
  id: string;
  message: string;
  transformation: WeaknessTransformation | null;
}> {
  const results: Array<{
    id: string;
    message: string;
    transformation: WeaknessTransformation | null;
  }> = [];

  for (const def of HOLDING_BACK_DEFINITIONS) {
    try {
      if (def.check(profile, categoryScores)) {
        const message = def.getMessage(profile, categoryScores);
        results.push({
          id: def.id,
          message,
          transformation: transformWeakness(def.id, message),
        });
      }
    } catch {
      // Skip factors that can't be evaluated
    }
  }

  // Sort by priority and return top 5 with transformations
  results.sort((a, b) => {
    const defA = HOLDING_BACK_DEFINITIONS.find(d => d.id === a.id);
    const defB = HOLDING_BACK_DEFINITIONS.find(d => d.id === b.id);
    return (defB?.priority ?? 0) - (defA?.priority ?? 0);
  });

  return results.slice(0, 5);
}

// =============================================================================
// FACTOR ANALYSIS FUNCTIONS
// =============================================================================

/**
 * Generate helping factors for a profile
 * UNIVERSAL: Always returns at least 1-2 factors, even for weak profiles
 */
export function analyzeHelpingFactors(
  profile: StudentProfile,
  categoryScores: IvyReadyScore['category_scores']
): string[] {
  const matched: Array<{ message: string; priority: number }> = [];

  for (const def of HELPING_FACTOR_DEFINITIONS) {
    try {
      if (def.check(profile, categoryScores)) {
        matched.push({
          message: def.getMessage(profile, categoryScores),
          priority: def.priority,
        });
      }
    } catch {
      // Skip factors that can't be evaluated
    }
  }

  // Sort by priority (highest first) and take top 5
  matched.sort((a, b) => b.priority - a.priority);

  // Ensure at least 1 factor (the fallback should always match)
  const factors = matched.slice(0, 5).map(f => f.message);

  return factors.length > 0 ? factors : ['Building your profile — every improvement counts'];
}

/**
 * Generate holding back factors for a profile
 * UNIVERSAL: Only shows factors that are actually gaps, max 5
 */
export function analyzeHoldingBackFactors(
  profile: StudentProfile,
  categoryScores: IvyReadyScore['category_scores']
): string[] {
  const matched: Array<{ message: string; priority: number }> = [];

  for (const def of HOLDING_BACK_DEFINITIONS) {
    try {
      if (def.check(profile, categoryScores)) {
        matched.push({
          message: def.getMessage(profile, categoryScores),
          priority: def.priority,
        });
      }
    } catch {
      // Skip factors that can't be evaluated
    }
  }

  // Sort by priority (highest first) and take top 5
  matched.sort((a, b) => b.priority - a.priority);

  return matched.slice(0, 5).map(f => f.message);
}
