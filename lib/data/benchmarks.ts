/**
 * Benchmark data for insight generation
 * Sources: Harvard SFFA dataset, College Board, Common Data Sets
 */

export const BENCHMARKS = {
  // === GPA DATA ===
  gpa: {
    // Percentile rankings among Ivy+ applicants
    percentiles: {
      4.7: 98,
      4.5: 90,
      4.3: 80,
      4.0: 70,
      3.9: 65,
      3.7: 60,
      3.5: 50,
      3.3: 40,
      3.0: 30,
    },

    // Average GPAs by category
    averages: {
      ivyPlus: 4.18,
      top20: 4.05,
      top50: 3.85,
      national: 3.38,
      workingStudents: 3.1,
      firstGen: 3.6,
      lowIncome: 3.5,
    },

    // Context boosts (added to raw GPA for contextualized score)
    contextBoosts: {
      work15Plus: 0.4,
      work20Plus: 0.6,
      work25Plus: 0.8,
      familyCare: 0.5,
      firstGen: 0.3,
      lowIncome: 0.4,
      highSaturation: -0.2, // negative boost for competitive regions
    },

    // GPA ranges for outcome lookup
    ranges: {
      '4.5+': { min: 4.5, max: 5.0 },
      '4.0-4.5': { min: 4.0, max: 4.49 },
      '3.7-4.0': { min: 3.7, max: 3.99 },
      '3.5-3.7': { min: 3.5, max: 3.69 },
      '3.0-3.5': { min: 3.0, max: 3.49 },
    },
  },

  // === SAT/ACT DATA ===
  sat: {
    // Percentile rankings nationally
    percentiles: {
      1600: 99.9,
      1570: 99,
      1550: 98,
      1520: 98,
      1500: 96,
      1480: 95,
      1450: 90,
      1400: 85,
      1350: 75,
      1300: 65,
      1250: 55,
      1200: 45,
      1150: 35,
      1100: 25,
    },

    // School middle 50% ranges (p25-p75)
    schoolRanges: {
      harvard: { p25: 1480, p50: 1520, p75: 1580 },
      stanford: { p25: 1470, p50: 1515, p75: 1570 },
      mit: { p25: 1510, p50: 1545, p75: 1580 },
      yale: { p25: 1470, p50: 1515, p75: 1570 },
      princeton: { p25: 1470, p50: 1520, p75: 1570 },
      caltech: { p25: 1530, p50: 1560, p75: 1590 },
      columbia: { p25: 1470, p50: 1520, p75: 1570 },
      penn: { p25: 1460, p50: 1510, p75: 1560 },
      brown: { p25: 1440, p50: 1500, p75: 1560 },
      duke: { p25: 1470, p50: 1520, p75: 1570 },
    },
  },

  // === LEADERSHIP DATA ===
  leadership: {
    // Distribution (what % of applicants at each level)
    distribution: {
      international: 0.02,    // 2% - Olympic, UN, etc.
      national: 0.08,         // 8% - National competitions, major nonprofits
      regional: 0.15,         // 15% - Multi-school, state level
      schoolWide: 0.30,       // 30% - Student body president, major clubs
      clubOfficer: 0.50,      // 50% - Club president, team captain
      member: 0.70,           // 70% - Active participant
    },

    // Admit rates by leadership level
    admitRates: {
      international: 0.45,
      national: 0.32,
      regional: 0.22,
      schoolWide: 0.15,
      clubOfficer: 0.12,
      member: 0.08,
    },
  },

  // === SERVICE DATA ===
  service: {
    // Average hours by applicant type
    averages: {
      allApplicants: 80,
      ivyPlusApplicants: 150,
      admittedStudents: 220,
    },

    // Multipliers vs average (80 hrs baseline)
    multipliers: {
      300: 3.75,
      250: 3.1,
      200: 2.5,
      150: 1.9,
      100: 1.25,
      50: 0.6,
    },
  },

  // === COURSE RIGOR DATA ===
  rigor: {
    // AP count benchmarks
    apCounts: {
      exceptional: 12,
      strong: 8,
      competitive: 5,
      modest: 3,
    },

    // Average for admitted students
    averages: {
      ivyPlus: 10,
      top20: 8,
      top50: 6,
    },
  },

  // === RESEARCH DATA ===
  research: {
    distribution: {
      nationalPublication: 0.02,
      regionalRecognition: 0.08,
      schoolResearch: 0.25,
      selfDirected: 0.40,
    },
  },

  // === DEMOGRAPHICS DATA ===
  demographics: {
    firstGen: {
      admitBoostMultiplier: 1.15, // 15% boost
      classComposition: 0.16, // 16% of Ivy classes
    },

    recruited: {
      admitRate: 0.75, // 75% admit rate for recruited athletes
    },

    legacy: {
      admitBoostMultiplier: 1.30, // 30% boost
    },
  },

  // === REGIONAL DATA ===
  regions: {
    highSaturation: [
      'Bay Area',
      'Palo Alto',
      'Cupertino',
      'Los Altos',
      'Manhattan',
      'Brooklyn',
      'Stuyvesant',
      'Boston',
      'Newton',
    ],
  },
} as const;

export type BenchmarkData = typeof BENCHMARKS;
