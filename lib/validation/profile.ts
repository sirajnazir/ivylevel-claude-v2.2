/**
 * Profile Validation and Completion Layer
 *
 * PRINCIPLE: Validate inputs at system boundaries.
 * This module ensures all profiles are complete and valid before reaching business logic.
 *
 * Usage: Call `completeProfile(profile)` at API entry points to ensure
 * the scoring engine receives well-formed data.
 */

import type {
  StudentProfile,
  AptitudeAttributes,
  PassionAttributes,
  CommunityAttributes,
  HighSchoolContext,
  DemographicContext,
  MajorContext,
  AssessmentIntelligence,
  StudentIdentity,
} from '../types/student';

import {
  NORMALIZED_DEFAULTS,
  RAW_DEFAULTS,
  CONTEXT_DEFAULTS,
  DEFAULT_TARGET_SCHOOLS,
} from '../constants/defaults';

import { safeNumber, safeString, safeArray } from '../utils/safeValue';

// =============================================================================
// PROFILE COMPLETION (Applies Defaults to Missing Fields)
// =============================================================================

/**
 * Complete a partial profile with defaults for all missing fields.
 * This is the main entry point for profile validation.
 *
 * @param profile - Partial or complete student profile
 * @returns Complete profile with all required fields populated
 */
export function completeProfile(profile: Partial<StudentProfile>): StudentProfile {
  return {
    session_id: profile.session_id ?? crypto.randomUUID(),
    timestamp: profile.timestamp ?? new Date().toISOString(),
    identity: completeIdentity(profile.identity),
    target_schools: completeTargetSchools(profile.target_schools),
    intended_major: safeString(profile.intended_major, 'Undeclared'),
    major_certainty: profile.major_certainty ?? 'EXPLORING',
    aptitude: completeAptitude(profile.aptitude),
    passion: completePassion(profile.passion),
    community: completeCommunity(profile.community),
    high_school: completeHighSchool(profile.high_school ?? undefined),
    demographics: completeDemographics(profile.demographics),
    major_context: completeMajorContext(profile.major_context, profile.intended_major),
    assessment_intelligence: completeAssessmentIntelligence(profile.assessment_intelligence),
  };
}

/**
 * Complete identity section
 */
function completeIdentity(identity?: Partial<StudentIdentity>): StudentIdentity {
  return {
    role: identity?.role ?? 'STUDENT',
    name: safeString(identity?.name, 'Student'),
    grade: identity?.grade ?? 11,
  };
}

/**
 * Complete target schools with defaults
 */
function completeTargetSchools(schools?: string[] | null): string[] {
  const result = safeArray(schools, [...DEFAULT_TARGET_SCHOOLS]);
  return result.length > 0 ? result : [...DEFAULT_TARGET_SCHOOLS];
}

/**
 * Complete aptitude attributes with defaults
 */
function completeAptitude(aptitude?: Partial<AptitudeAttributes>): AptitudeAttributes {
  const defaults = RAW_DEFAULTS.aptitude;
  const normDefaults = NORMALIZED_DEFAULTS.aptitude;

  return {
    gpa_weighted: safeNumber(aptitude?.gpa_weighted, defaults.gpa_weighted),
    gpa_unweighted: safeNumber(aptitude?.gpa_unweighted, defaults.gpa_unweighted),
    gpa_normalized: safeNumber(aptitude?.gpa_normalized, normDefaults.gpa),
    sat_total: aptitude?.sat_total ?? null, // Allow null for test-optional
    sat_normalized: safeNumber(aptitude?.sat_normalized, normDefaults.sat),
    act_total: aptitude?.act_total ?? null, // Allow null for test-optional
    act_normalized: safeNumber(aptitude?.act_normalized, normDefaults.sat),
    test_optional: aptitude?.test_optional ?? false,
    ap_count: safeNumber(aptitude?.ap_count, defaults.ap_count),
    ap_avg_score: safeNumber(aptitude?.ap_avg_score, defaults.ap_avg_score),
    rigor_normalized: safeNumber(aptitude?.rigor_normalized, normDefaults.rigor),
    ib_diploma: aptitude?.ib_diploma ?? false,
    academic_awards: safeArray(aptitude?.academic_awards, []),
    awards_normalized: safeNumber(aptitude?.awards_normalized, normDefaults.awards),
  };
}

/**
 * Complete passion attributes with defaults
 */
function completePassion(passion?: Partial<PassionAttributes>): PassionAttributes {
  const defaults = RAW_DEFAULTS.passion;
  const normDefaults = NORMALIZED_DEFAULTS.passion;

  return {
    spike_category: passion?.spike_category ?? null,
    leadership_level: passion?.leadership_level ?? 'PARTICIPANT',
    leadership_normalized: safeNumber(passion?.leadership_normalized, normDefaults.leadership),
    ec_commitment_years: safeNumber(passion?.ec_commitment_years, defaults.ec_commitment_years),
    ec_hours_weekly: safeNumber(passion?.ec_hours_weekly, defaults.ec_hours_weekly),
    commitment_normalized: safeNumber(passion?.commitment_normalized, normDefaults.commitment),
    project_impact: safeNumber(passion?.project_impact, defaults.project_impact),
    project_normalized: safeNumber(passion?.project_normalized, normDefaults.project),
    project_description: safeString(passion?.project_description, ''),
    research_level: passion?.research_level ?? 'NONE',
    research_normalized: safeNumber(passion?.research_normalized, normDefaults.research),
    ec_awards: safeArray(passion?.ec_awards, []),
    ec_awards_normalized: safeNumber(passion?.ec_awards_normalized, normDefaults.awards),
    brag_text: safeString(passion?.brag_text, ''),
    brag_nlp_extracted: passion?.brag_nlp_extracted ?? null,
  };
}

/**
 * Complete community attributes with defaults
 */
function completeCommunity(community?: Partial<CommunityAttributes>): CommunityAttributes {
  const defaults = RAW_DEFAULTS.community;
  const normDefaults = NORMALIZED_DEFAULTS.community;

  return {
    service_leadership: community?.service_leadership ?? 'PARTICIPANT',
    service_normalized: safeNumber(community?.service_normalized, normDefaults.service),
    service_hours: safeNumber(community?.service_hours, defaults.service_hours),
    hours_normalized: safeNumber(community?.hours_normalized, normDefaults.hours),
    community_impact: safeNumber(community?.community_impact, defaults.community_impact),
    impact_normalized: safeNumber(community?.impact_normalized, normDefaults.impact),
  };
}

/**
 * Complete high school context with defaults
 */
function completeHighSchool(hs?: Partial<HighSchoolContext>): HighSchoolContext {
  const defaults = CONTEXT_DEFAULTS.high_school;

  return {
    hs_name: safeString(hs?.hs_name, ''),
    hs_code: safeString(hs?.hs_code, ''),
    hs_type: hs?.hs_type ?? 'PUBLIC',
    region: hs?.region ?? 'OTHER',
    saturation_level: hs?.saturation_level ?? defaults.saturation_level,
    ivy_applicants_per_year: safeNumber(hs?.ivy_applicants_per_year, 0),
    saturation_adjustment: safeNumber(hs?.saturation_adjustment, defaults.saturation_adjustment),
  };
}

/**
 * Complete demographics with defaults
 */
function completeDemographics(demo?: Partial<DemographicContext>): DemographicContext {
  const defaults = CONTEXT_DEFAULTS.demographics;

  return {
    ethnicity: demo?.ethnicity ?? 'PREFER_NOT_SAY',
    ethnicity_multiplier: safeNumber(demo?.ethnicity_multiplier, defaults.ethnicity_multiplier),
    first_gen: demo?.first_gen ?? false,
    first_gen_multiplier: safeNumber(demo?.first_gen_multiplier, defaults.first_gen_multiplier),
    legacy: demo?.legacy ?? false,
    legacy_schools: safeArray(demo?.legacy_schools, []),
    income_band: demo?.income_band ?? 'PREFER_NOT_SAY',
    income_top_1_percent: demo?.income_top_1_percent ?? false,
    income_multiplier: safeNumber(demo?.income_multiplier, defaults.income_multiplier),
    recruited_athlete: demo?.recruited_athlete ?? false,
    athlete_multiplier: safeNumber(demo?.athlete_multiplier, defaults.athlete_multiplier),
  };
}

/**
 * Complete major context with defaults
 */
function completeMajorContext(ctx?: Partial<MajorContext>, intendedMajor?: string): MajorContext {
  return {
    intended_major: safeString(ctx?.intended_major ?? intendedMajor, 'Undeclared'),
    major_certainty: ctx?.major_certainty ?? 'EXPLORING',
    major_multiplier: safeNumber(ctx?.major_multiplier, 1.0),
  };
}

/**
 * Complete assessment intelligence (Layer 4) with defaults
 */
function completeAssessmentIntelligence(
  ai?: Partial<AssessmentIntelligence>
): AssessmentIntelligence {
  const normDefaults = NORMALIZED_DEFAULTS.narrative;

  return {
    psychometrics: {
      grit_resilience: safeNumber(ai?.psychometrics?.grit_resilience, normDefaults.grit),
      introversion_extroversion: safeNumber(ai?.psychometrics?.introversion_extroversion, 0),
      coachability: ai?.psychometrics?.coachability ?? 'MEDIUM',
      coachability_score: safeNumber(ai?.psychometrics?.coachability_score, normDefaults.coachability),
      vision_clarity: safeNumber(ai?.psychometrics?.vision_clarity, normDefaults.vision_clarity),
      identity_comfort: safeNumber(ai?.psychometrics?.identity_comfort, normDefaults.identity_comfort),
      maturity_level: safeNumber(ai?.psychometrics?.maturity_level, normDefaults.maturity),
      articulation_ability: safeNumber(ai?.psychometrics?.articulation_ability, normDefaults.articulation),
      openness: safeNumber(ai?.psychometrics?.openness, 0.5),
      conscientiousness: safeNumber(ai?.psychometrics?.conscientiousness, 0.5),
      extraversion: safeNumber(ai?.psychometrics?.extraversion, 0.5),
      agreeableness: safeNumber(ai?.psychometrics?.agreeableness, 0.5),
      neuroticism: safeNumber(ai?.psychometrics?.neuroticism, 0.5),
    },
    time_management: {
      homework_hours_daily: safeNumber(ai?.time_management?.homework_hours_daily, 3),
      social_media_hours_daily: safeNumber(ai?.time_management?.social_media_hours_daily, 2),
      ec_hours_weekly: safeNumber(ai?.time_management?.ec_hours_weekly, 10),
      sleep_hours_daily: safeNumber(ai?.time_management?.sleep_hours_daily, 7),
      committed_hours_weekly: safeNumber(ai?.time_management?.committed_hours_weekly, 100),
      reclaimable_hours_weekly: safeNumber(ai?.time_management?.reclaimable_hours_weekly, 20),
      burnout_risk: ai?.time_management?.burnout_risk ?? 'MEDIUM',
    },
    hidden_capabilities: {
      hidden_technical_projects: safeArray(ai?.hidden_capabilities?.hidden_technical_projects, []),
      hobby_passions: safeArray(ai?.hidden_capabilities?.hobby_passions, []),
      unconventional_interests: safeArray(ai?.hidden_capabilities?.unconventional_interests, []),
    },
    family_context: {
      parent_archetype: ai?.family_context?.parent_archetype ?? 'BALANCED',
      academic_expectations: ai?.family_context?.academic_expectations ?? 'FLEXIBLE',
    },
    academic_intelligence: {
      grade_pattern_trajectory: ai?.academic_intelligence?.grade_pattern_trajectory ?? 'STABLE',
      test_anxiety_indicator: safeNumber(ai?.academic_intelligence?.test_anxiety_indicator, 0.3),
    },
  };
}

// =============================================================================
// VALIDATION (Checks for Invalid Data)
// =============================================================================

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * Validate a profile and return any errors or warnings
 */
export function validateProfile(profile: StudentProfile): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Required fields
  if (!profile.session_id) {
    errors.push('Missing session_id');
  }

  if (!profile.target_schools || profile.target_schools.length === 0) {
    warnings.push('No target schools specified - using defaults');
  }

  // GPA bounds
  if (profile.aptitude.gpa_weighted !== null) {
    if (profile.aptitude.gpa_weighted < 0 || profile.aptitude.gpa_weighted > 5.0) {
      errors.push(`Invalid GPA: ${profile.aptitude.gpa_weighted} (must be 0-5.0)`);
    }
  }

  // SAT bounds
  if (profile.aptitude.sat_total !== null) {
    if (profile.aptitude.sat_total < 400 || profile.aptitude.sat_total > 1600) {
      errors.push(`Invalid SAT: ${profile.aptitude.sat_total} (must be 400-1600)`);
    }
  }

  // ACT bounds
  if (profile.aptitude.act_total !== null) {
    if (profile.aptitude.act_total < 1 || profile.aptitude.act_total > 36) {
      errors.push(`Invalid ACT: ${profile.aptitude.act_total} (must be 1-36)`);
    }
  }

  // Normalized values should be 0-1
  const normalizedFields = [
    { name: 'gpa_normalized', value: profile.aptitude.gpa_normalized },
    { name: 'sat_normalized', value: profile.aptitude.sat_normalized },
    { name: 'rigor_normalized', value: profile.aptitude.rigor_normalized },
    { name: 'leadership_normalized', value: profile.passion.leadership_normalized },
    { name: 'service_normalized', value: profile.community.service_normalized },
  ];

  for (const field of normalizedFields) {
    if (field.value !== null && (field.value < 0 || field.value > 1)) {
      warnings.push(`${field.name} out of bounds: ${field.value} (should be 0-1)`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

// =============================================================================
// CONVENIENCE FUNCTIONS
// =============================================================================

/**
 * Complete and validate a profile in one step
 * Returns the completed profile and any validation issues
 */
export function prepareProfile(
  partialProfile: Partial<StudentProfile>
): { profile: StudentProfile; validation: ValidationResult } {
  const profile = completeProfile(partialProfile);
  const validation = validateProfile(profile);

  return { profile, validation };
}
