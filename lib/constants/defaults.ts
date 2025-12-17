/**
 * Centralized Default Values for IvyQuest Scoring System
 *
 * PRINCIPLE: All default values are defined here as the SINGLE SOURCE OF TRUTH.
 * These defaults represent reasonable baseline assumptions for incomplete profiles.
 *
 * Defaults are based on:
 * - Median applicant data from Chetty 2023
 * - College Board percentile distributions
 * - IvyLevel spec recommendations
 */

// =============================================================================
// NORMALIZED SCORE DEFAULTS (0.0 - 1.0 scale)
// =============================================================================

export const NORMALIZED_DEFAULTS = {
  // Aptitude category defaults
  aptitude: {
    gpa: 0.5,           // 3.3 GPA equivalent (median)
    sat: 0.5,           // ~1300 SAT equivalent
    rigor: 0.4,         // 4-5 AP courses
    awards: 0.0,        // No awards (conservative)
  },

  // Passion category defaults
  passion: {
    leadership: 0.25,    // Participant level
    project: 0.2,        // Small group impact (~20 people)
    research: 0.0,       // No research
    commitment: 0.5,     // 2 years, moderate hours
    awards: 0.0,         // No EC awards
  },

  // Community category defaults
  community: {
    service: 0.3,        // Participant level volunteer
    hours: 0.4,          // ~75 hours
    impact: 0.2,         // Small local impact
  },

  // Narrative/Psychometric defaults
  narrative: {
    vision_clarity: 0.5,
    identity_comfort: 0.5,
    articulation: 0.5,
    maturity: 0.5,
    grit: 0.5,
    coachability: 0.5,
    description_quality: 0.5,
  },
} as const;

// =============================================================================
// RAW VALUE DEFAULTS (before normalization)
// =============================================================================

export const RAW_DEFAULTS = {
  aptitude: {
    gpa_weighted: 3.5,
    gpa_unweighted: 3.3,
    sat_total: 1300,
    act_total: 28,
    ap_count: 5,
    ap_avg_score: 3.5,
  },

  passion: {
    ec_commitment_years: 2,
    ec_hours_weekly: 8,
    project_impact: 20,
  },

  community: {
    service_hours: 75,
    community_impact: 20,
  },
} as const;

// =============================================================================
// CATEGORY WEIGHTS (from IvyLevel spec)
// =============================================================================

export const CATEGORY_WEIGHTS = {
  aptitude: {
    gpa: 0.35,
    sat: 0.30,
    rigor: 0.20,
    awards: 0.15,
  },

  passion: {
    leadership: 0.35,
    project: 0.20,
    research: 0.20,
    commitment: 0.15,
    awards: 0.10,
  },

  community: {
    service: 0.35,
    impact: 0.35,
    hours: 0.20,
    description: 0.10,
  },

  narrative: {
    vision: 0.30,
    identity: 0.25,
    articulation: 0.25,
    maturity: 0.20,
  },

  // Overall Ivy+ Ready Score weights
  overall: {
    aptitude: 0.30,
    passion: 0.35,
    community: 0.25,
    narrative: 0.10,
  },
} as const;

// =============================================================================
// DEMOGRAPHIC/CONTEXT DEFAULTS
// =============================================================================

export const CONTEXT_DEFAULTS = {
  demographics: {
    ethnicity_multiplier: 1.0,
    first_gen_multiplier: 1.0,
    income_multiplier: 1.0,
    athlete_multiplier: 1.0,
  },

  high_school: {
    saturation_adjustment: 0.0,
    saturation_level: 'MEDIUM' as const,
  },
} as const;

// =============================================================================
// TARGET SCHOOLS DEFAULTS
// =============================================================================

export const DEFAULT_TARGET_SCHOOLS = [
  'HARVARD',
  'STANFORD',
  'MIT',
  'YALE',
  'PRINCETON',
  'CALTECH',
  'CMU',
  'COLUMBIA',
] as const;

// =============================================================================
// VALIDATION BOUNDS
// =============================================================================

export const VALIDATION_BOUNDS = {
  normalized: {
    min: 0.0,
    max: 1.0,
  },

  percentageScore: {
    min: 0,
    max: 100,
  },

  probability: {
    min: 0.0,
    max: 0.95,  // Capped at 95% per spec
  },

  rubricRating: {
    min: 1,
    max: 6,  // SFFA rubric scale
  },

  gpa: {
    min: 0.0,
    max: 5.0,  // Weighted GPA can exceed 4.0
  },

  sat: {
    min: 400,
    max: 1600,
  },

  act: {
    min: 1,
    max: 36,
  },
} as const;

// =============================================================================
// TYPE EXPORTS
// =============================================================================

export type NormalizedDefaults = typeof NORMALIZED_DEFAULTS;
export type RawDefaults = typeof RAW_DEFAULTS;
export type CategoryWeights = typeof CATEGORY_WEIGHTS;
export type ContextDefaults = typeof CONTEXT_DEFAULTS;
export type ValidationBounds = typeof VALIDATION_BOUNDS;
