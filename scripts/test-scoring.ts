/**
 * Test script for scoring functions
 * Run with: npx ts-node scripts/test-scoring.ts
 */

// Copy of scoring functions from Frame6ProfileReveal.tsx for testing

function calculateAptitudeScore(profile: any): number {
  const aptitude = profile.aptitude;

  // NO DATA = 0 SCORE (not 100, not null, exactly 0)
  if (!aptitude) return 0;

  let totalScore = 0;
  let componentCount = 0;

  // Only count fields that have actual positive data
  if (aptitude.gpa_weighted != null && aptitude.gpa_weighted > 0) {
    totalScore += (aptitude.gpa_weighted / 5.0) * 100;
    componentCount++;
  } else if (aptitude.gpa_unweighted != null && aptitude.gpa_unweighted > 0) {
    totalScore += (aptitude.gpa_unweighted / 4.0) * 100;
    componentCount++;
  }

  if (aptitude.sat_total != null && aptitude.sat_total > 0) {
    totalScore += (aptitude.sat_total / 1600) * 100;
    componentCount++;
  }

  if (aptitude.act_total != null && aptitude.act_total > 0) {
    totalScore += (aptitude.act_total / 36) * 100;
    componentCount++;
  }

  if (aptitude.ap_count != null && aptitude.ap_count > 0) {
    totalScore += Math.min((aptitude.ap_count / 12) * 100, 100);
    componentCount++;
  }

  // Return 0 if no components have data (NOT average of nothing)
  return componentCount > 0 ? Math.round(totalScore / componentCount) : 0;
}

function calculatePassionScore(profile: any): number {
  const passion = profile.passion;
  if (!passion) return 0;

  let score = 0;

  // EC commitment years (only if positive number)
  const ecYears = passion.ec_commitment_years;
  if (ecYears != null && ecYears > 0) {
    score += Math.min((ecYears / 4) * 40, 40);
  }

  // Leadership (check it's meaningful, not just 'PARTICIPANT' or empty)
  if (
    passion.leadership_level &&
    passion.leadership_level !== 'PARTICIPANT' &&
    passion.leadership_level !== 'None' &&
    passion.leadership_level !== ''
  ) {
    score += 30;
  }

  // Awards (only if array exists and has items)
  const hasEcAwards = Array.isArray(passion.ec_awards) && passion.ec_awards.length > 0;
  const hasAcademicAwards =
    Array.isArray(profile.aptitude?.academic_awards) &&
    profile.aptitude.academic_awards.length > 0;

  if (hasEcAwards || hasAcademicAwards) {
    score += 30;
  }

  return Math.round(score);
}

function calculateServiceScore(profile: any): number {
  const community = profile.community;

  // NO data or 0 hours = 0 score
  if (!community) return 0;

  const hours = community.service_hours;
  if (hours == null || hours === 0) return 0;

  const score = Math.min((hours / 300) * 100, 100);
  return Math.round(score);
}

function calculateIdentityScore(profile: any): number {
  let score = 0;

  // Only add points if data actually exists and is meaningful
  if (profile.operating?.favoriteSubject && profile.operating.favoriteSubject !== '') {
    score += 25;
  }

  if (Array.isArray(profile.operating?.strengths) && profile.operating.strengths.length > 0) {
    score += 25;
  }

  if (
    profile.operating?.careerDirection &&
    profile.operating.careerDirection !== 'no-idea' &&
    profile.operating.careerDirection !== ''
  ) {
    score += 25;
  }

  // first_gen must be explicitly true (not just truthy)
  if (profile.demographics?.first_gen === true) {
    score += 25;
  }

  return score;
}

// ============================================================================
// TEST CASES
// ============================================================================

console.log('\n=== SCORING FUNCTION TESTS ===\n');

// Test 1: Completely empty profile
const emptyProfile = {};
console.log('TEST 1: Empty profile {}');
console.log('  Aptitude:', calculateAptitudeScore(emptyProfile), '(expected: 0)');
console.log('  Passion:', calculatePassionScore(emptyProfile), '(expected: 0)');
console.log('  Service:', calculateServiceScore(emptyProfile), '(expected: 0)');
console.log('  Identity:', calculateIdentityScore(emptyProfile), '(expected: 0)');

// Test 2: Profile with null values (like from server)
const nullProfile = {
  aptitude: {
    gpa_weighted: null,
    gpa_unweighted: null,
    sat_total: null,
    act_total: null,
    ap_count: null,
    academic_awards: [],
  },
  passion: {
    ec_commitment_years: null,
    leadership_level: null,
    ec_awards: [],
  },
  community: {
    service_hours: null,
  },
  operating: {
    favoriteSubject: '',
    strengths: [],
    careerDirection: 'no-idea',
  },
  demographics: {
    first_gen: false,
  },
};
console.log('\nTEST 2: Profile with null values');
console.log('  Aptitude:', calculateAptitudeScore(nullProfile), '(expected: 0)');
console.log('  Passion:', calculatePassionScore(nullProfile), '(expected: 0)');
console.log('  Service:', calculateServiceScore(nullProfile), '(expected: 0)');
console.log('  Identity:', calculateIdentityScore(nullProfile), '(expected: 0)');

// Test 3: Profile with 0 values
const zeroProfile = {
  aptitude: {
    gpa_weighted: 0,
    sat_total: 0,
    ap_count: 0,
    academic_awards: [],
  },
  passion: {
    ec_commitment_years: 0,
    leadership_level: 'None',
    ec_awards: [],
  },
  community: {
    service_hours: 0,
  },
  operating: {
    favoriteSubject: '',
    strengths: [],
    careerDirection: '',
  },
  demographics: {
    first_gen: false,
  },
};
console.log('\nTEST 3: Profile with 0 values');
console.log('  Aptitude:', calculateAptitudeScore(zeroProfile), '(expected: 0)');
console.log('  Passion:', calculatePassionScore(zeroProfile), '(expected: 0)');
console.log('  Service:', calculateServiceScore(zeroProfile), '(expected: 0)');
console.log('  Identity:', calculateIdentityScore(zeroProfile), '(expected: 0)');

// Test 4: Profile with actual data
const fullProfile = {
  aptitude: {
    gpa_weighted: 4.2,
    sat_total: 1450,
    ap_count: 6,
    academic_awards: ['Honor Roll'],
  },
  passion: {
    ec_commitment_years: 3,
    leadership_level: 'PRESIDENT',
    ec_awards: ['State Champion'],
  },
  community: {
    service_hours: 150,
  },
  operating: {
    favoriteSubject: 'Computer Science',
    strengths: ['analytical', 'creative'],
    careerDirection: 'yes',
  },
  demographics: {
    first_gen: true,
  },
};
console.log('\nTEST 4: Full profile with data');
console.log('  Aptitude:', calculateAptitudeScore(fullProfile), '(expected: ~75-85)');
console.log('  Passion:', calculatePassionScore(fullProfile), '(expected: ~90)');
console.log('  Service:', calculateServiceScore(fullProfile), '(expected: 50)');
console.log('  Identity:', calculateIdentityScore(fullProfile), '(expected: 100)');

// Test 5: Realistic "fresh start" profile from the app
const freshStartProfile = {
  session_id: '7102bd07-f7fc-46d2-b4db-6bcdd68dc024',
  timestamp: '2025-12-18T11:46:32.256Z',
  identity: { role: 'STUDENT', name: '', grade: 11 },
  target_schools: [],
  intended_major: '',
  major_certainty: 'EXPLORING',
  aptitude: {
    gpa_weighted: null,
    gpa_normalized: null,
    gpa_unweighted: null,
    sat_total: null,
    sat_normalized: null,
    act_total: null,
    act_normalized: null,
    test_optional: false,
    ap_count: null,
    ap_avg_score: null,
    rigor_normalized: null,
    ib_diploma: false,
    academic_awards: [],
    awards_normalized: null
  },
  passion: {
    spike_category: null,
    leadership_level: null,
    leadership_normalized: null,
    ec_commitment_years: null,
    ec_hours_weekly: null,
    commitment_normalized: null,
    project_impact: null,
    project_normalized: null,
    project_description: '',
    research_level: null,
    research_normalized: null,
    ec_awards: [],
    ec_awards_normalized: null,
    brag_text: '',
    brag_nlp_extracted: null
  },
  community: {
    service_leadership: null,
    service_normalized: null,
    service_hours: null,
    hours_normalized: null,
    community_impact: null,
    impact_normalized: null
  },
  operating: {},
  demographics: {
    ethnicity: 'PREFER_NOT_SAY',
    first_gen: false,
  },
  completeness: {
    score: 100,
    hasAcademics: true,
    hasActivities: true,
  },
};
console.log('\nTEST 5: Fresh start profile (from dev server logs)');
console.log('  Aptitude:', calculateAptitudeScore(freshStartProfile), '(expected: 0)');
console.log('  Passion:', calculatePassionScore(freshStartProfile), '(expected: 0)');
console.log('  Service:', calculateServiceScore(freshStartProfile), '(expected: 0)');
console.log('  Identity:', calculateIdentityScore(freshStartProfile), '(expected: 0)');

console.log('\n=== TESTS COMPLETE ===\n');
