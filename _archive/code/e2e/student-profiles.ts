/**
 * IvyQuest v3.0 — Synthetic Bay Area Student Profiles
 *
 * Realistic test profiles from various Bay Area high schools
 * spanning grades 9-12 with diverse backgrounds and aspirations.
 */

export interface Activity {
  name: string;
  category: string;
  leadership: string;
  impact: string;
  hoursPerWeek: number;
  yearsInvolved: number;
  description: string;
  isSpike: boolean;
}

export interface StudentProfile {
  id: string;
  name: string;
  email: string;
  grade: string;
  school: string;
  city: string;
  targetSchools: string[];
  intendedMajor: string;
  gpa: string;
  gpaScale: string;
  courseRigor: string;
  testType: string;
  satScore: string;
  actScore: string;
  apCount: number;
  awards: string[];
  activities: Activity[];
  operatingStyle: string;
  psychAnswers: Record<string, string>;
  expectedTier: 'exceptional' | 'competitive' | 'average' | 'developing';
  expectedScoreRange: [number, number];
  description: string;
}

// ============================================================================
// BAY AREA STUDENT PROFILES
// ============================================================================

export const BAY_AREA_PROFILES: StudentProfile[] = [
  // -------------------------------------------------------------------------
  // PROFILE 1: Palo Alto High School - Senior - STEM Superstar
  // -------------------------------------------------------------------------
  {
    id: 'paly-senior-stem',
    name: 'Kevin Chen',
    email: 'kevin.chen@paly.edu',
    grade: '12',
    school: 'Palo Alto High School',
    city: 'Palo Alto',
    targetSchools: ['stanford', 'mit', 'caltech', 'harvard', 'princeton'],
    intendedMajor: 'Computer Science & AI',
    gpa: '4.0',
    gpaScale: '4.0',
    courseRigor: 'ap_max',
    testType: 'sat',
    satScore: '1580',
    actScore: '',
    apCount: 14,
    awards: [
      'Intel ISEF Finalist',
      'USACO Platinum Division',
      'National Merit Scholar',
      'AP Scholar with Distinction',
    ],
    activities: [
      {
        name: 'Machine Learning Research - Stanford AI Lab',
        category: 'stem',
        leadership: 'active',
        impact: 'international',
        hoursPerWeek: 15,
        yearsInvolved: 2,
        description: 'Published paper on neural network optimization at NeurIPS workshop',
        isSpike: true,
      },
      {
        name: 'Competitive Programming Club',
        category: 'academic',
        leadership: 'founder',
        impact: 'state',
        hoursPerWeek: 8,
        yearsInvolved: 3,
        description: 'Founded club, trained 50+ students for USACO competitions',
        isSpike: false,
      },
      {
        name: 'Math Olympiad Team',
        category: 'academic',
        leadership: 'leader',
        impact: 'national',
        hoursPerWeek: 6,
        yearsInvolved: 4,
        description: 'AMC 12 Perfect Score, AIME Qualifier',
        isSpike: false,
      },
      {
        name: 'Code.org Volunteer Instructor',
        category: 'community',
        leadership: 'leader',
        impact: 'local',
        hoursPerWeek: 4,
        yearsInvolved: 2,
        description: 'Teach coding to underserved middle schoolers in East Palo Alto',
        isSpike: false,
      },
    ],
    operatingStyle: 'analytical_thinker',
    psychAnswers: {
      work_approach: 'research',
      learning_style: 'doing',
      challenge_response: 'analyze',
      team_role: 'analyst',
      success_definition: 'mastery',
    },
    expectedTier: 'exceptional',
    expectedScoreRange: [88, 98],
    description: 'Elite STEM student from competitive Palo Alto school with research publications',
  },

  // -------------------------------------------------------------------------
  // PROFILE 2: Lowell High School - Junior - Humanities Focus
  // -------------------------------------------------------------------------
  {
    id: 'lowell-junior-humanities',
    name: 'Maya Rodriguez',
    email: 'maya.rodriguez@sfusd.edu',
    grade: '11',
    school: 'Lowell High School',
    city: 'San Francisco',
    targetSchools: ['yale', 'columbia', 'brown', 'uchicago', 'northwestern'],
    intendedMajor: 'Political Science & Economics',
    gpa: '3.95',
    gpaScale: '4.0',
    courseRigor: 'ap_heavy',
    testType: 'sat',
    satScore: '1520',
    actScore: '',
    apCount: 10,
    awards: [
      'National Speech & Debate Tournament Semifinalist',
      'We The People National Finalist',
      'Published in Teen Ink Magazine',
    ],
    activities: [
      {
        name: 'Model United Nations',
        category: 'academic',
        leadership: 'leader',
        impact: 'national',
        hoursPerWeek: 12,
        yearsInvolved: 3,
        description: 'Secretary General of SF Bay MUN, organized conference for 500+ delegates',
        isSpike: true,
      },
      {
        name: 'School Newspaper - The Lowell',
        category: 'arts',
        leadership: 'leader',
        impact: 'school',
        hoursPerWeek: 10,
        yearsInvolved: 3,
        description: 'Editor-in-Chief, won NSPA Pacemaker Award',
        isSpike: false,
      },
      {
        name: 'Youth City Government',
        category: 'leadership',
        leadership: 'active',
        impact: 'local',
        hoursPerWeek: 5,
        yearsInvolved: 2,
        description: 'Interned with SF Board of Supervisors on housing policy',
        isSpike: false,
      },
      {
        name: 'Tutoring at Chinatown YMCA',
        category: 'community',
        leadership: 'active',
        impact: 'local',
        hoursPerWeek: 4,
        yearsInvolved: 2,
        description: 'ESL tutoring for immigrant families',
        isSpike: false,
      },
    ],
    operatingStyle: 'dynamic_leader',
    psychAnswers: {
      work_approach: 'collaborate',
      learning_style: 'discussing',
      challenge_response: 'mobilize',
      team_role: 'leader',
      success_definition: 'impact',
    },
    expectedTier: 'competitive',
    expectedScoreRange: [78, 88],
    description: 'Debate champion and policy wonk from prestigious SF magnet school',
  },

  // -------------------------------------------------------------------------
  // PROFILE 3: Mission San Jose High - Sophomore - STEM Rising
  // -------------------------------------------------------------------------
  {
    id: 'msj-sophomore-rising',
    name: 'Arjun Patel',
    email: 'arjun.patel@fremont.k12.ca.us',
    grade: '10',
    school: 'Mission San Jose High School',
    city: 'Fremont',
    targetSchools: ['mit', 'stanford', 'berkeley', 'cmu'],
    intendedMajor: 'Electrical Engineering',
    gpa: '3.9',
    gpaScale: '4.0',
    courseRigor: 'ap_some',
    testType: 'sat',
    satScore: '1450',
    actScore: '',
    apCount: 4,
    awards: [
      'Science Olympiad State Medalist',
      'First Robotics Regional Winner',
    ],
    activities: [
      {
        name: 'FIRST Robotics Team 254',
        category: 'stem',
        leadership: 'active',
        impact: 'national',
        hoursPerWeek: 15,
        yearsInvolved: 2,
        description: 'Lead programmer on award-winning Chezy Pofs team',
        isSpike: true,
      },
      {
        name: 'Science Olympiad',
        category: 'academic',
        leadership: 'active',
        impact: 'state',
        hoursPerWeek: 8,
        yearsInvolved: 2,
        description: 'Won medals in Circuit Lab and Astronomy',
        isSpike: false,
      },
      {
        name: 'Indian Classical Music',
        category: 'arts',
        leadership: 'active',
        impact: 'local',
        hoursPerWeek: 5,
        yearsInvolved: 8,
        description: 'Tabla performer, competed at regional competitions',
        isSpike: false,
      },
    ],
    operatingStyle: 'methodical_builder',
    psychAnswers: {
      work_approach: 'plan_first',
      learning_style: 'doing',
      challenge_response: 'analyze',
      team_role: 'implementer',
      success_definition: 'mastery',
    },
    expectedTier: 'competitive',
    expectedScoreRange: [70, 82],
    description: 'Strong sophomore from top-ranked engineering feeder school',
  },

  // -------------------------------------------------------------------------
  // PROFILE 4: Gunn High School - Senior - Arts & Activism
  // -------------------------------------------------------------------------
  {
    id: 'gunn-senior-arts',
    name: 'Sofia Kim',
    email: 'sofia.kim@pausd.org',
    grade: '12',
    school: 'Gunn High School',
    city: 'Palo Alto',
    targetSchools: ['brown', 'yale', 'stanford', 'pomona', 'wesleyan'],
    intendedMajor: 'Environmental Studies & Film',
    gpa: '3.85',
    gpaScale: '4.0',
    courseRigor: 'ap_heavy',
    testType: 'act',
    satScore: '',
    actScore: '34',
    apCount: 9,
    awards: [
      'Scholastic Art & Writing Gold Key',
      'SF International Film Festival Youth Selection',
      'California State Science Fair Honorable Mention',
    ],
    activities: [
      {
        name: 'Environmental Documentary Filmmaking',
        category: 'arts',
        leadership: 'founder',
        impact: 'state',
        hoursPerWeek: 12,
        yearsInvolved: 3,
        description: 'Created documentary on Bay Area water crisis, screened at 5 festivals',
        isSpike: true,
      },
      {
        name: 'Sunrise Movement - Climate Activism',
        category: 'community',
        leadership: 'leader',
        impact: 'state',
        hoursPerWeek: 8,
        yearsInvolved: 2,
        description: 'Organized student climate strikes, testified at City Council',
        isSpike: false,
      },
      {
        name: 'School Film Club',
        category: 'arts',
        leadership: 'founder',
        impact: 'school',
        hoursPerWeek: 6,
        yearsInvolved: 3,
        description: 'Founded and grew to 40+ members, produced 12 short films',
        isSpike: false,
      },
      {
        name: 'Marine Biology Research',
        category: 'stem',
        leadership: 'active',
        impact: 'local',
        hoursPerWeek: 4,
        yearsInvolved: 2,
        description: 'Summer research at Hopkins Marine Station',
        isSpike: false,
      },
    ],
    operatingStyle: 'creative_explorer',
    psychAnswers: {
      work_approach: 'brainstorm',
      learning_style: 'observing',
      challenge_response: 'try_new',
      team_role: 'creative',
      success_definition: 'creation',
    },
    expectedTier: 'competitive',
    expectedScoreRange: [75, 85],
    description: 'Creative filmmaker and environmental activist with unique interdisciplinary profile',
  },

  // -------------------------------------------------------------------------
  // PROFILE 5: Monta Vista High - Freshman - Early Starter
  // -------------------------------------------------------------------------
  {
    id: 'mv-freshman-early',
    name: 'Emily Wang',
    email: 'emily.wang@fuhsd.org',
    grade: '9',
    school: 'Monta Vista High School',
    city: 'Cupertino',
    targetSchools: ['stanford', 'berkeley', 'ucla'],
    intendedMajor: 'Undecided (leaning Biology)',
    gpa: '4.0',
    gpaScale: '4.0',
    courseRigor: 'honors',
    testType: 'sat',
    satScore: '',
    actScore: '',
    apCount: 0,
    awards: [
      'JV Tennis League Champion',
      'Honor Roll',
    ],
    activities: [
      {
        name: 'JV Tennis Team',
        category: 'athletics',
        leadership: 'active',
        impact: 'school',
        hoursPerWeek: 12,
        yearsInvolved: 1,
        description: 'Varsity track next year, USTA ranked',
        isSpike: false,
      },
      {
        name: 'Biology Olympiad Prep',
        category: 'academic',
        leadership: 'participant',
        impact: 'school',
        hoursPerWeek: 4,
        yearsInvolved: 1,
        description: 'Preparing for USABO Open Exam',
        isSpike: false,
      },
      {
        name: 'Piano',
        category: 'arts',
        leadership: 'active',
        impact: 'local',
        hoursPerWeek: 5,
        yearsInvolved: 8,
        description: 'MTAC Certificate of Merit Level 10',
        isSpike: false,
      },
    ],
    operatingStyle: 'balanced_achiever',
    psychAnswers: {
      work_approach: 'plan_first',
      learning_style: 'reading',
      challenge_response: 'persist',
      team_role: 'supporter',
      success_definition: 'growth',
    },
    expectedTier: 'developing',
    expectedScoreRange: [45, 60],
    description: 'Promising freshman just starting high school journey',
  },

  // -------------------------------------------------------------------------
  // PROFILE 6: Lynbrook High School - Junior - Business Focus
  // -------------------------------------------------------------------------
  {
    id: 'lynbrook-junior-business',
    name: 'Jason Liu',
    email: 'jason.liu@fuhsd.org',
    grade: '11',
    school: 'Lynbrook High School',
    city: 'San Jose',
    targetSchools: ['penn', 'northwestern', 'uchicago', 'nyu', 'usc'],
    intendedMajor: 'Business & Finance',
    gpa: '3.88',
    gpaScale: '4.0',
    courseRigor: 'ap_heavy',
    testType: 'sat',
    satScore: '1490',
    actScore: '',
    apCount: 8,
    awards: [
      'DECA State Finalist',
      'Diamond Bar Economics Challenge Winner',
      'National Economics Challenge Semifinalist',
    ],
    activities: [
      {
        name: 'DECA Business Club',
        category: 'academic',
        leadership: 'leader',
        impact: 'state',
        hoursPerWeek: 10,
        yearsInvolved: 3,
        description: 'Vice President, led team to State competition in Entrepreneurship',
        isSpike: true,
      },
      {
        name: 'Student-Run Investment Fund',
        category: 'leadership',
        leadership: 'founder',
        impact: 'school',
        hoursPerWeek: 6,
        yearsInvolved: 2,
        description: 'Founded club managing $5K portfolio, 23% returns',
        isSpike: false,
      },
      {
        name: 'Varsity Golf',
        category: 'athletics',
        leadership: 'active',
        impact: 'school',
        hoursPerWeek: 10,
        yearsInvolved: 3,
        description: 'Starting player, handicap 8',
        isSpike: false,
      },
      {
        name: 'Junior Achievement Volunteer',
        category: 'community',
        leadership: 'active',
        impact: 'local',
        hoursPerWeek: 3,
        yearsInvolved: 2,
        description: 'Teach financial literacy to middle schoolers',
        isSpike: false,
      },
    ],
    operatingStyle: 'strategic_networker',
    psychAnswers: {
      work_approach: 'dive_in',
      learning_style: 'discussing',
      challenge_response: 'mobilize',
      team_role: 'leader',
      success_definition: 'recognition',
    },
    expectedTier: 'competitive',
    expectedScoreRange: [72, 82],
    description: 'Business-oriented student with entrepreneurial drive from competitive South Bay school',
  },

  // -------------------------------------------------------------------------
  // PROFILE 7: Oakland Tech - Senior - First Generation
  // -------------------------------------------------------------------------
  {
    id: 'oakland-senior-firstgen',
    name: 'Marcus Johnson',
    email: 'marcus.johnson@ousd.org',
    grade: '12',
    school: 'Oakland Technical High School',
    city: 'Oakland',
    targetSchools: ['berkeley', 'stanford', 'ucla', 'howard', 'morehouse'],
    intendedMajor: 'Computer Science & Social Justice',
    gpa: '3.75',
    gpaScale: '4.0',
    courseRigor: 'ap_some',
    testType: 'sat',
    satScore: '1380',
    actScore: '',
    apCount: 5,
    awards: [
      'QuestBridge College Prep Scholar',
      'Bank of America Student Leader',
      'East Bay Community Foundation Scholar',
    ],
    activities: [
      {
        name: 'Black Student Union',
        category: 'leadership',
        leadership: 'leader',
        impact: 'local',
        hoursPerWeek: 8,
        yearsInvolved: 3,
        description: 'President, organized community events and advocacy campaigns',
        isSpike: true,
      },
      {
        name: 'Code2040 Fellow',
        category: 'stem',
        leadership: 'active',
        impact: 'national',
        hoursPerWeek: 10,
        yearsInvolved: 1,
        description: 'Summer internship at tech startup, learned full-stack development',
        isSpike: false,
      },
      {
        name: 'Youth vs Apocalypse',
        category: 'community',
        leadership: 'active',
        impact: 'state',
        hoursPerWeek: 5,
        yearsInvolved: 2,
        description: 'Environmental justice organizing in frontline communities',
        isSpike: false,
      },
      {
        name: 'Part-Time Job - Target',
        category: 'work',
        leadership: 'active',
        impact: 'local',
        hoursPerWeek: 15,
        yearsInvolved: 2,
        description: 'Work to support family, promoted to team lead',
        isSpike: false,
      },
    ],
    operatingStyle: 'collaborative_connector',
    psychAnswers: {
      work_approach: 'collaborate',
      learning_style: 'doing',
      challenge_response: 'mobilize',
      team_role: 'mediator',
      success_definition: 'impact',
    },
    expectedTier: 'competitive',
    expectedScoreRange: [68, 78],
    description: 'First-gen student overcoming obstacles with strong leadership and community focus',
  },

  // -------------------------------------------------------------------------
  // PROFILE 8: Los Altos High - Sophomore - Well-Rounded
  // -------------------------------------------------------------------------
  {
    id: 'lahs-sophomore-rounded',
    name: 'Sarah Martinez',
    email: 'sarah.martinez@mvla.net',
    grade: '10',
    school: 'Los Altos High School',
    city: 'Los Altos',
    targetSchools: ['stanford', 'duke', 'vanderbilt', 'usc'],
    intendedMajor: 'Psychology',
    gpa: '3.7',
    gpaScale: '4.0',
    courseRigor: 'honors',
    testType: 'sat',
    satScore: '1350',
    actScore: '',
    apCount: 2,
    awards: [
      'Varsity Soccer All-League Honorable Mention',
      'Spanish Honor Society',
    ],
    activities: [
      {
        name: 'Varsity Soccer',
        category: 'athletics',
        leadership: 'active',
        impact: 'school',
        hoursPerWeek: 15,
        yearsInvolved: 2,
        description: 'Starting midfielder, team made CCS playoffs',
        isSpike: false,
      },
      {
        name: 'Peer Counseling',
        category: 'community',
        leadership: 'active',
        impact: 'school',
        hoursPerWeek: 4,
        yearsInvolved: 1,
        description: 'Trained peer counselor for mental health support',
        isSpike: false,
      },
      {
        name: 'Spanish Club',
        category: 'cultural',
        leadership: 'active',
        impact: 'school',
        hoursPerWeek: 2,
        yearsInvolved: 2,
        description: 'Help organize cultural events and tutoring',
        isSpike: false,
      },
    ],
    operatingStyle: 'balanced_achiever',
    psychAnswers: {
      work_approach: 'collaborate',
      learning_style: 'discussing',
      challenge_response: 'seek_help',
      team_role: 'supporter',
      success_definition: 'growth',
    },
    expectedTier: 'average',
    expectedScoreRange: [55, 68],
    description: 'Well-rounded sophomore with strong athletics but still developing profile',
  },

  // -------------------------------------------------------------------------
  // PROFILE 9: Saratoga High - Senior - Music Prodigy
  // -------------------------------------------------------------------------
  {
    id: 'saratoga-senior-music',
    name: 'Daniel Park',
    email: 'daniel.park@lgsuhsd.org',
    grade: '12',
    school: 'Saratoga High School',
    city: 'Saratoga',
    targetSchools: ['juilliard', 'harvard', 'yale', 'stanford', 'rice'],
    intendedMajor: 'Music Performance (Violin)',
    gpa: '3.92',
    gpaScale: '4.0',
    courseRigor: 'ap_heavy',
    testType: 'sat',
    satScore: '1510',
    actScore: '',
    apCount: 9,
    awards: [
      'YoungArts Finalist - Classical Music',
      'California All-State Orchestra Principal',
      'Menuhin Competition Semifinalist',
    ],
    activities: [
      {
        name: 'Violin Performance',
        category: 'arts',
        leadership: 'active',
        impact: 'international',
        hoursPerWeek: 25,
        yearsInvolved: 12,
        description: 'Studied at SF Conservatory pre-college, performed with symphony orchestras',
        isSpike: true,
      },
      {
        name: 'Youth Symphony',
        category: 'arts',
        leadership: 'leader',
        impact: 'state',
        hoursPerWeek: 6,
        yearsInvolved: 4,
        description: 'Concertmaster of California Youth Symphony',
        isSpike: false,
      },
      {
        name: 'Music Therapy Volunteer',
        category: 'community',
        leadership: 'founder',
        impact: 'local',
        hoursPerWeek: 3,
        yearsInvolved: 2,
        description: 'Founded program to perform at senior centers and hospitals',
        isSpike: false,
      },
      {
        name: 'School Orchestra',
        category: 'arts',
        leadership: 'leader',
        impact: 'school',
        hoursPerWeek: 4,
        yearsInvolved: 4,
        description: 'Section leader, mentor younger students',
        isSpike: false,
      },
    ],
    operatingStyle: 'disciplined_perfectionist',
    psychAnswers: {
      work_approach: 'plan_first',
      learning_style: 'doing',
      challenge_response: 'persist',
      team_role: 'specialist',
      success_definition: 'mastery',
    },
    expectedTier: 'exceptional',
    expectedScoreRange: [85, 95],
    description: 'World-class violinist with exceptional dedication and achievements',
  },

  // -------------------------------------------------------------------------
  // PROFILE 10: Carlmont High - Junior - Average Achiever
  // -------------------------------------------------------------------------
  {
    id: 'carlmont-junior-average',
    name: 'Tyler Wilson',
    email: 'tyler.wilson@seq.org',
    grade: '11',
    school: 'Carlmont High School',
    city: 'Belmont',
    targetSchools: ['berkeley', 'ucsb', 'sdsu', 'cal_poly'],
    intendedMajor: 'Business Administration',
    gpa: '3.4',
    gpaScale: '4.0',
    courseRigor: 'honors',
    testType: 'act',
    satScore: '',
    actScore: '27',
    apCount: 3,
    awards: [],
    activities: [
      {
        name: 'JV Basketball',
        category: 'athletics',
        leadership: 'active',
        impact: 'school',
        hoursPerWeek: 10,
        yearsInvolved: 2,
        description: 'Starting point guard',
        isSpike: false,
      },
      {
        name: 'Part-Time Job - Safeway',
        category: 'work',
        leadership: 'active',
        impact: 'local',
        hoursPerWeek: 12,
        yearsInvolved: 1,
        description: 'Cashier, saving for college',
        isSpike: false,
      },
    ],
    operatingStyle: 'practical_doer',
    psychAnswers: {
      work_approach: 'dive_in',
      learning_style: 'doing',
      challenge_response: 'persist',
      team_role: 'implementer',
      success_definition: 'recognition',
    },
    expectedTier: 'average',
    expectedScoreRange: [42, 55],
    description: 'Average student with limited extracurriculars but solid work ethic',
  },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export function getProfileById(id: string): StudentProfile | undefined {
  return BAY_AREA_PROFILES.find(p => p.id === id);
}

export function getProfilesByGrade(grade: string): StudentProfile[] {
  return BAY_AREA_PROFILES.filter(p => p.grade === grade);
}

export function getProfilesByTier(tier: string): StudentProfile[] {
  return BAY_AREA_PROFILES.filter(p => p.expectedTier === tier);
}
