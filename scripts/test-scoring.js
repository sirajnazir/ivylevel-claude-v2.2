/**
 * Test script for scoring functions
 * Run with: node scripts/test-scoring.js
 */

// Copy of scoring functions from Frame6ProfileReveal.tsx for testing

function calculateAptitudeScore(profile) {
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

function calculatePassionScore(profile) {
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

function calculateServiceScore(profile) {
  const community = profile.community;

  // NO data or 0 hours = 0 score
  if (!community) return 0;

  const hours = community.service_hours;
  if (hours == null || hours === 0) return 0;

  const score = Math.min((hours / 300) * 100, 100);
  return Math.round(score);
}

function calculateIdentityScore(profile) {
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

// ============================================================================
// V10.0 HUDA BENCHMARK TESTS
// ============================================================================

console.log('\n=== V10.0 HUDA BENCHMARK TESTS ===\n');

// CRI Computation Function (v10.0)
function computeCRI(profile) {
  const constraints = profile.constraints || [];
  let cri = 1.0;

  // Apply constraint multipliers per Chetty 2023
  if (constraints.includes('first_gen')) cri *= 1.15;
  if (constraints.includes('low_ses') || constraints.includes('low_income')) cri *= 1.10;
  if (constraints.includes('immigrant')) cri *= 1.05;
  if (constraints.includes('single_parent')) cri *= 1.05;
  if (constraints.includes('work_hours')) cri *= 1.03;
  if (constraints.includes('rural')) cri *= 1.08;
  if (constraints.includes('underrepresented')) cri *= 1.07;

  // Performance boost for exceeding expectations
  const gpa = profile.aptitude?.gpa_weighted || 3.5;
  const expectedGpa = 3.3; // Median for constrained students
  if (gpa > expectedGpa && constraints.length > 0) {
    cri *= 1.0 + (gpa - expectedGpa) * 0.2;
  }

  return Math.round(cri * 100) / 100;
}

// Huda Profile - Canonical First-Gen Low-Income Student
const hudaProfile = {
  aptitude: {
    gpa_weighted: 4.2,
    sat_total: 1520,
    ap_count: 8,
    ap_avg_score: 4.5,
    academic_awards: ['QuestBridge Finalist'],
  },
  passion: {
    ec_commitment_years: 3,
    leadership_level: 'FOUNDER_STATE',
    ec_awards: ['Bank of America Student Leader'],
  },
  community: {
    service_hours: 300,
  },
  demographics: {
    first_gen: true,
    low_income: true,
  },
  constraints: ['first_gen', 'low_ses', 'immigrant', 'single_parent', 'work_hours'],
};

// Test CRI > 1.2
const hudaCRI = computeCRI(hudaProfile);
console.log('HUDA BENCHMARK - CRI Computation:');
console.log('  CRI:', hudaCRI);
console.log('  Expected: > 1.2');
console.log('  Result:', hudaCRI > 1.2 ? 'PASS' : 'FAIL');

// Test CRI increases with constraints
console.log('\nCRI SCALING TEST:');
const cri1 = computeCRI({ constraints: ['first_gen'] });
const cri2 = computeCRI({ constraints: ['first_gen', 'low_ses'] });
const cri3 = computeCRI({ constraints: ['first_gen', 'low_ses', 'immigrant'] });
console.log('  1 constraint:', cri1);
console.log('  2 constraints:', cri2);
console.log('  3 constraints:', cri3);
console.log('  Scaling:', cri3 > cri2 && cri2 > cri1 ? 'PASS' : 'FAIL');

// Test category weights sum to 1.0
const CATEGORY_WEIGHTS = {
  aptitude: { gpa: 0.35, sat: 0.30, rigor: 0.20, awards: 0.15 },
  passion: { leadership: 0.35, project: 0.20, research: 0.20, commitment: 0.15, awards: 0.10 },
  community: { service: 0.35, impact: 0.35, hours: 0.20, description: 0.10 },
  overall: { aptitude: 0.30, passion: 0.35, community: 0.25, narrative: 0.10 },
};

console.log('\nCATEGORY WEIGHTS VALIDATION:');
Object.entries(CATEGORY_WEIGHTS).forEach(([category, weights]) => {
  const sum = Object.values(weights).reduce((a, b) => a + b, 0);
  console.log(`  ${category}: ${sum.toFixed(2)} (${Math.abs(sum - 1.0) < 0.001 ? 'PASS' : 'FAIL'})`);
});

// SSR Test - All profiles must compute without error
console.log('\nSSR (SCORING SUCCESS RATE) TEST:');
const testProfiles = [
  { name: 'Empty', profile: {} },
  { name: 'Null values', profile: nullProfile },
  { name: 'Zero values', profile: zeroProfile },
  { name: 'Full data', profile: fullProfile },
  { name: 'Huda', profile: hudaProfile },
  { name: 'Fresh start', profile: freshStartProfile },
];

let ssrPassed = 0;
testProfiles.forEach(({ name, profile }) => {
  try {
    const aptitude = calculateAptitudeScore(profile);
    const passion = calculatePassionScore(profile);
    const service = calculateServiceScore(profile);
    const identity = calculateIdentityScore(profile);

    if (aptitude >= 0 && aptitude <= 100 &&
        passion >= 0 && passion <= 100 &&
        service >= 0 && service <= 100 &&
        identity >= 0 && identity <= 100) {
      ssrPassed++;
      console.log(`  ${name}: PASS`);
    } else {
      console.log(`  ${name}: FAIL (score out of bounds)`);
    }
  } catch (e) {
    console.log(`  ${name}: FAIL (${e.message})`);
  }
});

const ssr = (ssrPassed / testProfiles.length) * 100;
console.log(`\nSSR: ${ssr.toFixed(1)}% (${ssrPassed}/${testProfiles.length})`);
console.log('SSR Target: 100%');
console.log('SSR Result:', ssr === 100 ? 'PASS' : 'FAIL');

console.log('\n=== V10.0 BENCHMARK TESTS COMPLETE ===\n');

// Exit with proper code
process.exit(ssr === 100 && hudaCRI > 1.2 ? 0 : 1);
