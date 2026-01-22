/**
 * IvyQuest v3.0 — Scoring Engine Validation Script
 *
 * Run this in browser console or as a test file to validate
 * the scoring engine calculations.
 *
 * Usage (browser console):
 *   1. Navigate to http://localhost:3000/quest
 *   2. Paste this entire script
 *   3. Call: runAllValidations()
 */

// ============================================================================
// TEST DATA FIXTURES
// ============================================================================

const TEST_FIXTURES = {
  // High achiever - should score 85+ (Exceptional)
  highAchiever: {
    frame0: {
      studentName: 'High Achiever',
      email: 'high@test.com',
      grade: '12',
      targetSchools: ['harvard', 'mit', 'stanford', 'yale', 'princeton'],
    },
    frame1: {
      gpa: '4.0',
      gpaScale: '4.0',
      courseRigor: 'ap_max',
      testType: 'sat',
      satScore: '1580',
      actScore: '',
      apCount: 12,
      awards: ['Intel ISEF Finalist', 'USAMO Qualifier', 'National Merit Scholar'],
    },
    frame2: {
      activities: [
        {
          id: 'act_1',
          name: 'AI Research Lab',
          category: 'stem',
          leadership: 'founder',
          impact: 'international',
          hoursPerWeek: 20,
          yearsInvolved: 3,
          description: 'Published peer-reviewed paper',
          isSpike: true,
        },
        {
          id: 'act_2',
          name: 'Science Olympiad',
          category: 'academic',
          leadership: 'leader',
          impact: 'national',
          hoursPerWeek: 10,
          yearsInvolved: 4,
          description: 'National champion',
          isSpike: false,
        },
        {
          id: 'act_3',
          name: 'Tutoring Nonprofit',
          category: 'community',
          leadership: 'founder',
          impact: 'state',
          hoursPerWeek: 8,
          yearsInvolved: 2,
          description: 'Serves 200+ students',
          isSpike: false,
        },
      ],
    },
    frame3: {
      answers: {
        work_approach: 'research',
        learning_style: 'doing',
        challenge_response: 'analyze',
        team_role: 'analyst',
        success_definition: 'mastery',
      },
      operatingStyle: 'analytical_thinker',
    },
    expectedScores: {
      ivyReadyMin: 85,
      ivyReadyMax: 100,
      tier: 'exceptional',
      aptitudeMin: 90,
      passionMin: 85,
    },
  },

  // Average student - should score 45-65 (Average/Developing)
  averageStudent: {
    frame0: {
      studentName: 'Average Student',
      email: 'avg@test.com',
      grade: '11',
      targetSchools: ['cornell', 'duke'],
    },
    frame1: {
      gpa: '3.3',
      gpaScale: '4.0',
      courseRigor: 'honors',
      testType: 'sat',
      satScore: '1180',
      actScore: '',
      apCount: 2,
      awards: [],
    },
    frame2: {
      activities: [
        {
          id: 'act_1',
          name: 'Soccer Team',
          category: 'athletics',
          leadership: 'participant',
          impact: 'school',
          hoursPerWeek: 8,
          yearsInvolved: 2,
          description: 'JV player',
          isSpike: false,
        },
      ],
    },
    frame3: {
      answers: {
        work_approach: 'dive_in',
        learning_style: 'discussing',
        challenge_response: 'seek_help',
        team_role: 'mediator',
        success_definition: 'impact',
      },
      operatingStyle: 'collaborative_connector',
    },
    expectedScores: {
      ivyReadyMin: 35,
      ivyReadyMax: 60,
      tier: 'average',
      aptitudeMin: 40,
      passionMin: 30,
    },
  },

  // Spike-focused student - strong passion, moderate academics
  spikeStudent: {
    frame0: {
      studentName: 'Spike Student',
      email: 'spike@test.com',
      grade: '11',
      targetSchools: ['stanford', 'mit', 'caltech'],
    },
    frame1: {
      gpa: '3.7',
      gpaScale: '4.0',
      courseRigor: 'ap_some',
      testType: 'sat',
      satScore: '1420',
      actScore: '',
      apCount: 6,
      awards: ['State Science Fair 1st Place'],
    },
    frame2: {
      activities: [
        {
          id: 'act_1',
          name: 'Robotics Competition Team',
          category: 'stem',
          leadership: 'leader',
          impact: 'international',
          hoursPerWeek: 25,
          yearsInvolved: 4,
          description: 'World championship qualifier, designed award-winning robot',
          isSpike: true,
        },
      ],
    },
    frame3: {
      answers: {
        work_approach: 'brainstorm',
        learning_style: 'doing',
        challenge_response: 'try_new',
        team_role: 'creative',
        success_definition: 'creation',
      },
      operatingStyle: 'creative_explorer',
    },
    expectedScores: {
      ivyReadyMin: 65,
      ivyReadyMax: 82,
      tier: 'competitive',
      aptitudeMin: 70,
      passionMin: 80, // Should be high due to spike
    },
  },
};

// ============================================================================
// SCORING CALCULATION (Mirror of actual engine)
// ============================================================================

function calculateAptitudeScore(frame1) {
  let score = 0;

  // GPA component (0-35 points)
  const gpa = parseFloat(frame1.gpa) || 0;
  const scale = parseFloat(frame1.gpaScale) || 4.0;
  const normalizedGPA = (gpa / scale) * 4.0;
  score += Math.min(35, normalizedGPA * 8.75);

  // Course rigor (0-20 points)
  const rigorScores = {
    'regular': 5,
    'honors': 10,
    'ap_some': 14,
    'ap_heavy': 17,
    'ap_max': 20,
  };
  score += rigorScores[frame1.courseRigor] || 5;

  // Test scores (0-25 points)
  if (frame1.satScore) {
    const sat = parseInt(frame1.satScore) || 0;
    score += Math.min(25, ((sat - 400) / 1200) * 25);
  } else if (frame1.actScore) {
    const act = parseInt(frame1.actScore) || 0;
    score += Math.min(25, ((act - 1) / 35) * 25);
  }

  // AP count (0-10 points)
  const apCount = frame1.apCount || 0;
  score += Math.min(10, apCount * 0.8);

  // Awards (0-10 points)
  const awards = frame1.awards || [];
  score += Math.min(10, awards.length * 3);

  return Math.round(Math.min(100, score));
}

function calculatePassionScore(frame2) {
  const activities = frame2.activities || [];
  if (activities.length === 0) return 0;

  let score = 0;
  let spikeBonus = 0;

  activities.forEach(activity => {
    let activityScore = 0;

    // Leadership (0-10)
    const leadershipScores = {
      'participant': 3,
      'active': 5,
      'leader': 8,
      'founder': 10,
    };
    activityScore += leadershipScores[activity.leadership] || 3;

    // Impact (0-15)
    const impactScores = {
      'school': 3,
      'local': 6,
      'state': 9,
      'national': 12,
      'international': 15,
    };
    activityScore += impactScores[activity.impact] || 3;

    // Commitment (hours * years) / 40, capped at 10
    const commitment = (activity.hoursPerWeek * activity.yearsInvolved) / 40;
    activityScore += Math.min(10, commitment * 10);

    // Spike bonus
    if (activity.isSpike) {
      spikeBonus = Math.max(spikeBonus, activityScore * 0.5);
    }

    score += activityScore;
  });

  // Normalize based on activity count
  const avgScore = score / activities.length;
  const baseScore = avgScore * 2.5;

  return Math.round(Math.min(100, baseScore + spikeBonus));
}

function calculateCommunityScore(frame2) {
  const activities = frame2.activities || [];
  let score = 0;

  activities.forEach(activity => {
    // Leadership bonus
    if (activity.leadership === 'founder' || activity.leadership === 'leader') {
      score += 15;
    } else if (activity.leadership === 'active') {
      score += 8;
    }

    // Community-focused categories
    if (activity.category === 'community' || activity.category === 'leadership') {
      score += 12;
    }

    // Impact multiplier
    const impactMult = {
      'school': 1,
      'local': 1.2,
      'state': 1.5,
      'national': 2,
      'international': 2.5,
    };
    score *= impactMult[activity.impact] || 1;
  });

  return Math.round(Math.min(100, score));
}

function calculateOperatingScore(frame3) {
  // Base score from having a defined style
  let score = 50;

  // Consistency bonus - if answers align with style
  const answers = frame3.answers || {};
  const answerCount = Object.keys(answers).length;
  score += answerCount * 8;

  // Style fit bonus
  if (frame3.operatingStyle) {
    score += 10;
  }

  return Math.round(Math.min(100, score));
}

function calculateIvyReadyScore(aptitude, passion, community, operating) {
  // Weighted average: 30% aptitude, 30% passion, 20% community, 20% operating
  const ivyReady = (
    aptitude * 0.30 +
    passion * 0.30 +
    community * 0.20 +
    operating * 0.20
  );

  return Math.round(ivyReady);
}

function getTier(score) {
  if (score >= 85) return 'exceptional';
  if (score >= 70) return 'competitive';
  if (score >= 50) return 'average';
  return 'developing';
}

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

function validateScores(fixture, fixtureName) {
  console.group(`Validating: ${fixtureName}`);

  const aptitude = calculateAptitudeScore(fixture.frame1);
  const passion = calculatePassionScore(fixture.frame2);
  const community = calculateCommunityScore(fixture.frame2);
  const operating = calculateOperatingScore(fixture.frame3);
  const ivyReady = calculateIvyReadyScore(aptitude, passion, community, operating);
  const tier = getTier(ivyReady);

  console.log('Calculated Scores:');
  console.log(`  Aptitude: ${aptitude}`);
  console.log(`  Passion: ${passion}`);
  console.log(`  Community: ${community}`);
  console.log(`  Operating: ${operating}`);
  console.log(`  Ivy+ Ready: ${ivyReady} (${tier})`);

  const expected = fixture.expectedScores;
  const results = [];

  // Validate Ivy+ Ready range
  if (ivyReady >= expected.ivyReadyMin && ivyReady <= expected.ivyReadyMax) {
    results.push({ test: 'Ivy+ Ready in range', pass: true });
    console.log(`PASS: Ivy+ Ready ${ivyReady} is within expected range [${expected.ivyReadyMin}-${expected.ivyReadyMax}]`);
  } else {
    results.push({ test: 'Ivy+ Ready in range', pass: false });
    console.error(`FAIL: Ivy+ Ready ${ivyReady} outside expected range [${expected.ivyReadyMin}-${expected.ivyReadyMax}]`);
  }

  // Validate tier
  if (tier === expected.tier) {
    results.push({ test: 'Tier correct', pass: true });
    console.log(`PASS: Tier "${tier}" matches expected`);
  } else {
    results.push({ test: 'Tier correct', pass: false });
    console.error(`FAIL: Tier "${tier}" doesn't match expected "${expected.tier}"`);
  }

  // Validate aptitude minimum
  if (aptitude >= expected.aptitudeMin) {
    results.push({ test: 'Aptitude meets minimum', pass: true });
    console.log(`PASS: Aptitude ${aptitude} >= ${expected.aptitudeMin}`);
  } else {
    results.push({ test: 'Aptitude meets minimum', pass: false });
    console.error(`FAIL: Aptitude ${aptitude} < ${expected.aptitudeMin}`);
  }

  // Validate passion minimum
  if (passion >= expected.passionMin) {
    results.push({ test: 'Passion meets minimum', pass: true });
    console.log(`PASS: Passion ${passion} >= ${expected.passionMin}`);
  } else {
    results.push({ test: 'Passion meets minimum', pass: false });
    console.error(`FAIL: Passion ${passion} < ${expected.passionMin}`);
  }

  console.groupEnd();

  return {
    fixtureName,
    scores: { aptitude, passion, community, operating, ivyReady, tier },
    results,
    allPassed: results.every(r => r.pass),
  };
}

function validateLocalStorageStructure() {
  console.group('Validating LocalStorage Structure');

  const stored = localStorage.getItem('ivyquest-storage');
  if (!stored) {
    console.warn('No ivyquest-storage found in localStorage');
    console.groupEnd();
    return { valid: false, reason: 'No data' };
  }

  try {
    const parsed = JSON.parse(stored);
    const state = parsed.state;

    const requiredKeys = ['frame0', 'frame1', 'frame2', 'frame3', 'currentFrame', 'progress'];
    const missingKeys = requiredKeys.filter(k => !(k in state));

    if (missingKeys.length > 0) {
      console.error(`Missing keys: ${missingKeys.join(', ')}`);
      console.groupEnd();
      return { valid: false, reason: `Missing keys: ${missingKeys.join(', ')}` };
    }

    console.log('All required keys present');
    console.log('Current frame:', state.currentFrame);
    console.log('Progress:', state.progress + '%');
    console.log('Frame 0 data:', state.frame0 ? 'Present' : 'Empty');
    console.log('Frame 1 data:', state.frame1 ? 'Present' : 'Empty');
    console.log('Frame 2 data:', state.frame2 ? 'Present' : 'Empty');
    console.log('Frame 3 data:', state.frame3 ? 'Present' : 'Empty');
    console.log('Scores:', state.scores ? 'Present' : 'Not calculated yet');

    console.groupEnd();
    return { valid: true, state };

  } catch (e) {
    console.error('Failed to parse localStorage:', e);
    console.groupEnd();
    return { valid: false, reason: 'Parse error' };
  }
}

// ============================================================================
// MAIN VALIDATION RUNNER
// ============================================================================

function runAllValidations() {
  console.clear();
  console.log('===================================================================');
  console.log('   IvyQuest v3.0 — End-to-End Validation Suite');
  console.log('===================================================================');
  console.log('');

  const results = [];

  // Scoring engine validations
  console.log('PHASE 1: Scoring Engine Validation');
  console.log('-----------------------------------');

  results.push(validateScores(TEST_FIXTURES.highAchiever, 'High Achiever'));
  results.push(validateScores(TEST_FIXTURES.averageStudent, 'Average Student'));
  results.push(validateScores(TEST_FIXTURES.spikeStudent, 'Spike Student'));

  console.log('');
  console.log('PHASE 2: Data Persistence Validation');
  console.log('-----------------------------------');

  const storageResult = validateLocalStorageStructure();

  // Summary
  console.log('');
  console.log('===================================================================');
  console.log('   VALIDATION SUMMARY');
  console.log('===================================================================');

  const totalTests = results.reduce((sum, r) => sum + r.results.length, 0);
  const passedTests = results.reduce((sum, r) => sum + r.results.filter(t => t.pass).length, 0);

  console.log(`Total fixtures tested: ${results.length}`);
  console.log(`Total test cases: ${totalTests}`);
  console.log(`Passed: ${passedTests}`);
  console.log(`Failed: ${totalTests - passedTests}`);
  console.log(`Storage valid: ${storageResult.valid}`);

  if (passedTests === totalTests) {
    console.log('');
    console.log('ALL SCORING VALIDATIONS PASSED!');
  } else {
    console.log('');
    console.warn('Some validations failed. Review above for details.');
  }

  return { results, storageResult };
}

// ============================================================================
// HELPER: Inject Test Data
// ============================================================================

function injectTestData(fixtureName = 'highAchiever') {
  const fixture = TEST_FIXTURES[fixtureName];
  if (!fixture) {
    console.error(`Unknown fixture: ${fixtureName}`);
    return;
  }

  const state = {
    frame0: fixture.frame0,
    frame1: fixture.frame1,
    frame2: fixture.frame2,
    frame3: fixture.frame3,
    currentFrame: 4,
    progress: 100,
    scores: null,
  };

  localStorage.setItem('ivyquest-storage', JSON.stringify({ state, version: 0 }));
  console.log(`Injected "${fixtureName}" test data. Refresh the page to see changes.`);
}

// ============================================================================
// EXPORTS
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    TEST_FIXTURES,
    calculateAptitudeScore,
    calculatePassionScore,
    calculateCommunityScore,
    calculateOperatingScore,
    calculateIvyReadyScore,
    getTier,
    validateScores,
    runAllValidations,
    injectTestData,
  };
}

console.log('IvyQuest E2E Validation Script Loaded');
console.log('------------------------------------');
console.log('Available commands:');
console.log('  runAllValidations()     - Run full validation suite');
console.log('  injectTestData("highAchiever")  - Inject high achiever data');
console.log('  injectTestData("averageStudent") - Inject average student data');
console.log('  injectTestData("spikeStudent")   - Inject spike-focused data');
console.log('');
