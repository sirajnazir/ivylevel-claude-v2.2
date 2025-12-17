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
  // Weak = below these values
  weak: {
    gpa_normalized: 0.40,      // Bottom 40% = needs work
    sat_normalized: 0.40,
    rigor_normalized: 0.35,
    awards_normalized: 0.10,   // No awards
    project_normalized: 0.30,
    service_normalized: 0.25,
    category_score: 40,        // Below 40% = gap
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
