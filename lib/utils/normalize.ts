/**
 * Normalization Utility Functions
 * Wraps the scoring engine normalization functions for easy use
 */

import {
  normalizeGPA,
  normalizeSAT,
  normalizeRigor,
  normalizeAcademicAwards,
  normalizeLeadership,
  normalizeProjectImpact,
  normalizeResearch,
  normalizeECCommitment,
  normalizeECAwards,
  normalizeServiceLeadership,
  normalizeServiceHours,
  normalizeCommunityImpact,
} from '../scoring/engine';

import type {
  StudentProfile,
  AptitudeAttributes,
  PassionAttributes,
  CommunityAttributes,
} from '../types/student';

/**
 * Normalize all aptitude attributes in place
 */
export function normalizeAptitudeAttributes(aptitude: AptitudeAttributes): AptitudeAttributes {
  return {
    ...aptitude,
    gpa_normalized: normalizeGPA(aptitude.gpa_weighted),
    sat_normalized: normalizeSAT(aptitude.sat_total),
    rigor_normalized: normalizeRigor(aptitude.ap_count, aptitude.ap_avg_score),
    awards_normalized: normalizeAcademicAwards(aptitude.academic_awards),
  };
}

/**
 * Normalize all passion attributes in place
 */
export function normalizePassionAttributes(passion: PassionAttributes): PassionAttributes {
  return {
    ...passion,
    leadership_normalized: normalizeLeadership(passion.leadership_level),
    project_normalized: normalizeProjectImpact(passion.project_impact),
    research_normalized: normalizeResearch(passion.research_level),
    commitment_normalized: normalizeECCommitment(passion.ec_commitment_years, passion.ec_hours_weekly),
    ec_awards_normalized: normalizeECAwards(passion.ec_awards),
  };
}

/**
 * Normalize all community attributes in place
 */
export function normalizeCommunityAttributes(community: CommunityAttributes): CommunityAttributes {
  return {
    ...community,
    service_normalized: normalizeServiceLeadership(community.service_leadership),
    hours_normalized: normalizeServiceHours(community.service_hours),
    impact_normalized: normalizeCommunityImpact(community.community_impact),
  };
}

/**
 * Normalize all Layer 1 attributes in a student profile
 */
export function normalizeStudentProfile(profile: StudentProfile): StudentProfile {
  return {
    ...profile,
    aptitude: normalizeAptitudeAttributes(profile.aptitude),
    passion: normalizePassionAttributes(profile.passion),
    community: normalizeCommunityAttributes(profile.community),
  };
}
