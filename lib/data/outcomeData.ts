/**
 * Outcome data for admit rate projections
 * Sources: Harvard SFFA dataset, school Common Data Sets
 */

export const OUTCOMES = {
  // === BY GPA RANGE ===
  byGPA: {
    '4.5+': {
      mitAdmitRate: 0.18,
      stanfordAdmitRate: 0.15,
      harvardAdmitRate: 0.12,
      avgTop10: 0.16,
      vsOverallMultiplier: 3.6,
    },
    '4.0-4.5': {
      mitAdmitRate: 0.12,
      stanfordAdmitRate: 0.10,
      harvardAdmitRate: 0.08,
      avgTop10: 0.11,
      vsOverallMultiplier: 2.5,
    },
    '3.7-4.0': {
      mitAdmitRate: 0.06,
      stanfordAdmitRate: 0.05,
      harvardAdmitRate: 0.04,
      avgTop10: 0.06,
      vsOverallMultiplier: 1.5,
    },
    '3.5-3.7': {
      mitAdmitRate: 0.03,
      stanfordAdmitRate: 0.02,
      harvardAdmitRate: 0.02,
      avgTop10: 0.03,
      vsOverallMultiplier: 0.8,
    },
  },

  // === BY LEADERSHIP LEVEL ===
  byLeadership: {
    international: {
      avgAdmitRate: 0.45,
      topSchoolRate: 0.50,
      vsAverageMultiplier: 9.0,
    },
    national: {
      avgAdmitRate: 0.32,
      topSchoolRate: 0.40,
      vsAverageMultiplier: 7.0,
    },
    regional: {
      avgAdmitRate: 0.22,
      topSchoolRate: 0.28,
      vsAverageMultiplier: 4.8,
    },
    schoolWide: {
      avgAdmitRate: 0.15,
      topSchoolRate: 0.18,
      vsAverageMultiplier: 3.0,
    },
  },

  // === BY SERVICE HOURS ===
  byService: {
    '300+': {
      serviceScore: 90,
      admitBoost: 0.08,
    },
    '200-299': {
      serviceScore: 82,
      admitBoost: 0.06,
    },
    '150-199': {
      serviceScore: 75,
      admitBoost: 0.04,
    },
    '100-149': {
      serviceScore: 65,
      admitBoost: 0.02,
    },
  },

  // === TEST OPTIONAL ===
  testOptional: {
    admitRate: 0.045, // 4.5% for test-optional at top schools
    recommended: {
      satThreshold: 1450,
      actThreshold: 33,
    },
  },
} as const;

export type OutcomeData = typeof OUTCOMES;
