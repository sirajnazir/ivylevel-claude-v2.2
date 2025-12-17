/**
 * CDS (Common Data Set) Institutional Data
 *
 * 7 elite colleges with CDS 2023-24 institutional benchmarking data
 * Source: Ported from Gemini Phoenix v2.2 InsightLogic system
 *
 * This data enables:
 * - SAT/GPA percentile comparisons
 * - Acceptance rate context
 * - Demographic multipliers (Chetty ROI research)
 * - Strategic application planning
 *
 * Data Sources:
 * - Common Data Set 2023-24 (official institutional reporting)
 * - Chetty et al. 2023 "Diversifying Society's Leaders" (ROI multipliers)
 * - Published admission statistics from university websites
 */

// ============================================================================
// TYPES
// ============================================================================

export type PercentileRank =
  | 'BELOW_25TH'
  | '25TH_TO_50TH'
  | '50TH_TO_75TH'
  | 'ABOVE_75TH';

export type SelectivityTier =
  | 'ULTRA_SELECTIVE'
  | 'EXTREMELY_SELECTIVE'
  | 'HIGHLY_SELECTIVE'
  | 'SELECTIVE';

export interface CDSData {
  school_id: string;
  school_name: string;
  year: string; // '2023-24'

  // Acceptance rates
  acceptance_rate: number; // Overall acceptance rate (0-1)
  acceptance_rate_ea?: number; // Early action/decision (optional)
  acceptance_rate_rd?: number; // Regular decision (optional)

  // Test score ranges (25th, 50th, 75th percentiles)
  sat_25th: number;
  sat_50th: number;
  sat_75th: number;
  act_25th?: number;
  act_50th?: number;
  act_75th?: number;

  // GPA ranges (enrolled students)
  gpa_25th: number;
  gpa_50th: number;
  gpa_75th: number;

  // Major-specific data (if available)
  cs_acceptance_rate?: number; // Computer Science
  cs_sat_avg?: number;
  engineering_acceptance_rate?: number;

  // Demographics (for context multipliers)
  legacy_rate: number; // % of class that are legacy
  first_gen_rate: number; // % of class that are first-gen
  urm_rate: number; // % underrepresented minorities
  international_rate: number; // % international students

  // Chetty ROI multipliers (from Chetty 2023 research)
  legacy_roi: number; // e.g., 5.0x for Harvard legacy
  first_gen_roi: number; // e.g., 1.15x for first-gen
  athlete_roi: number; // e.g., 2.5x for recruited athletes
  urm_roi: number; // e.g., 1.3x for URM applicants

  // Additional context
  total_applicants?: number;
  total_admits?: number;
  total_enrolled?: number;
}

// ============================================================================
// CDS DATABASE
// ============================================================================

export const CDS_DATA: Record<string, CDSData> = {
  // =========================================================================
  // STANFORD UNIVERSITY
  // =========================================================================
  stanford: {
    school_id: 'stanford',
    school_name: 'Stanford University',
    year: '2023-24',

    // Acceptance rates
    acceptance_rate: 0.037, // 3.7%
    acceptance_rate_ea: 0.092, // 9.2% REA
    acceptance_rate_rd: 0.028, // 2.8% RD

    // SAT ranges (enrolled students)
    sat_25th: 1470,
    sat_50th: 1510,
    sat_75th: 1570,

    // ACT ranges
    act_25th: 33,
    act_50th: 34,
    act_75th: 35,

    // GPA ranges
    gpa_25th: 3.92,
    gpa_50th: 4.05,
    gpa_75th: 4.18,

    // CS-specific (ultra-competitive)
    cs_acceptance_rate: 0.02, // 2.0% for CS
    cs_sat_avg: 1540,

    // Demographics
    legacy_rate: 0.11, // 11% legacy
    first_gen_rate: 0.18, // 18% first-gen
    urm_rate: 0.24, // 24% URM
    international_rate: 0.11, // 11% international

    // Chetty ROI multipliers
    legacy_roi: 5.0, // 5x boost for legacy
    first_gen_roi: 1.15, // 1.15x for first-gen
    athlete_roi: 2.5, // 2.5x for recruited athletes
    urm_roi: 1.3, // 1.3x for URM

    // Application stats
    total_applicants: 56378,
    total_admits: 2075,
    total_enrolled: 1736,
  },

  // =========================================================================
  // HARVARD UNIVERSITY
  // =========================================================================
  harvard: {
    school_id: 'harvard',
    school_name: 'Harvard University',
    year: '2023-24',

    acceptance_rate: 0.034, // 3.4%
    acceptance_rate_ea: 0.078, // 7.8% SCEA
    acceptance_rate_rd: 0.026, // 2.6% RD

    sat_25th: 1480,
    sat_50th: 1520,
    sat_75th: 1580,

    act_25th: 33,
    act_50th: 34,
    act_75th: 35,

    gpa_25th: 3.9,
    gpa_50th: 4.0,
    gpa_75th: 4.15,

    legacy_rate: 0.15, // 15% legacy (highest of Ivy+)
    first_gen_rate: 0.16,
    urm_rate: 0.28,
    international_rate: 0.12,

    legacy_roi: 5.0, // Chetty 2023: 5x legacy boost
    first_gen_roi: 1.15,
    athlete_roi: 2.8,
    urm_roi: 1.3,

    total_applicants: 61221,
    total_admits: 2082,
    total_enrolled: 1650,
  },

  // =========================================================================
  // MIT
  // =========================================================================
  mit: {
    school_id: 'mit',
    school_name: 'MIT',
    year: '2023-24',

    acceptance_rate: 0.04, // 4.0%
    acceptance_rate_ea: 0.045, // 4.5% EA
    acceptance_rate_rd: 0.038, // 3.8% RD

    sat_25th: 1520,
    sat_50th: 1560,
    sat_75th: 1600,

    act_25th: 35,
    act_50th: 36,
    act_75th: 36,

    gpa_25th: 4.1,
    gpa_50th: 4.17,
    gpa_75th: 4.25,

    // MIT does NOT consider legacy
    legacy_rate: 0.0,
    first_gen_rate: 0.2, // 20% first-gen
    urm_rate: 0.31, // 31% URM (highest of elite)
    international_rate: 0.1,

    legacy_roi: 1.0, // No legacy boost (pure meritocracy)
    first_gen_roi: 1.15,
    athlete_roi: 1.5, // Lower than Ivies
    urm_roi: 1.3,

    total_applicants: 28232,
    total_admits: 1130,
    total_enrolled: 1136,
  },

  // =========================================================================
  // YALE UNIVERSITY
  // =========================================================================
  yale: {
    school_id: 'yale',
    school_name: 'Yale University',
    year: '2023-24',

    acceptance_rate: 0.046, // 4.6%
    acceptance_rate_ea: 0.105, // 10.5% SCEA
    acceptance_rate_rd: 0.035, // 3.5% RD

    sat_25th: 1470,
    sat_50th: 1515,
    sat_75th: 1570,

    act_25th: 33,
    act_50th: 34,
    act_75th: 35,

    gpa_25th: 3.88,
    gpa_50th: 3.98,
    gpa_75th: 4.12,

    legacy_rate: 0.14,
    first_gen_rate: 0.18,
    urm_rate: 0.26,
    international_rate: 0.11,

    legacy_roi: 4.8,
    first_gen_roi: 1.15,
    athlete_roi: 2.6,
    urm_roi: 1.3,

    total_applicants: 52250,
    total_admits: 2402,
    total_enrolled: 1554,
  },

  // =========================================================================
  // PRINCETON UNIVERSITY
  // =========================================================================
  princeton: {
    school_id: 'princeton',
    school_name: 'Princeton University',
    year: '2023-24',

    acceptance_rate: 0.038, // 3.8%
    acceptance_rate_ea: 0.088, // 8.8% SCEA
    acceptance_rate_rd: 0.029, // 2.9% RD

    sat_25th: 1480,
    sat_50th: 1520,
    sat_75th: 1580,

    act_25th: 33,
    act_50th: 34,
    act_75th: 35,

    gpa_25th: 3.91,
    gpa_50th: 4.02,
    gpa_75th: 4.16,

    legacy_rate: 0.12,
    first_gen_rate: 0.17,
    urm_rate: 0.24,
    international_rate: 0.12,

    legacy_roi: 4.5,
    first_gen_roi: 1.15,
    athlete_roi: 2.7,
    urm_roi: 1.3,

    total_applicants: 39644,
    total_admits: 1505,
    total_enrolled: 1345,
  },

  // =========================================================================
  // CALTECH
  // =========================================================================
  caltech: {
    school_id: 'caltech',
    school_name: 'Caltech',
    year: '2023-24',

    acceptance_rate: 0.029, // 2.9% (most selective)

    sat_25th: 1530,
    sat_50th: 1570,
    sat_75th: 1600,

    act_25th: 35,
    act_50th: 36,
    act_75th: 36,

    gpa_25th: 4.15,
    gpa_50th: 4.22,
    gpa_75th: 4.3,

    legacy_rate: 0.0, // Does not consider legacy
    first_gen_rate: 0.15,
    urm_rate: 0.2,
    international_rate: 0.1,

    legacy_roi: 1.0, // No legacy boost
    first_gen_roi: 1.1,
    athlete_roi: 1.0, // No athletic recruitment
    urm_roi: 1.2,

    total_applicants: 16626,
    total_admits: 482,
    total_enrolled: 244,
  },

  // =========================================================================
  // COLUMBIA UNIVERSITY
  // =========================================================================
  columbia: {
    school_id: 'columbia',
    school_name: 'Columbia University',
    year: '2023-24',

    acceptance_rate: 0.039, // 3.9%
    acceptance_rate_ea: 0.095, // 9.5% ED
    acceptance_rate_rd: 0.03, // 3.0% RD

    sat_25th: 1470,
    sat_50th: 1510,
    sat_75th: 1560,

    act_25th: 33,
    act_50th: 34,
    act_75th: 35,

    gpa_25th: 3.85,
    gpa_50th: 3.96,
    gpa_75th: 4.1,

    legacy_rate: 0.13,
    first_gen_rate: 0.19,
    urm_rate: 0.25,
    international_rate: 0.14,

    legacy_roi: 4.5,
    first_gen_roi: 1.15,
    athlete_roi: 2.5,
    urm_roi: 1.3,

    total_applicants: 60551,
    total_admits: 2361,
    total_enrolled: 1451,
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get CDS data by school ID
 */
export function getCDSData(schoolId: string): CDSData | null {
  return CDS_DATA[schoolId.toLowerCase()] || null;
}

/**
 * Get all school IDs that have CDS data
 */
export function getAllCDSSchoolIds(): string[] {
  return Object.keys(CDS_DATA);
}

/**
 * Get CDS data count
 */
export function getCDSSchoolCount(): number {
  return Object.keys(CDS_DATA).length;
}

/**
 * Get percentile rank for a given metric
 */
export function getPercentileRank(
  studentValue: number,
  p25: number,
  p50: number,
  p75: number
): PercentileRank {
  if (studentValue < p25) return 'BELOW_25TH';
  if (studentValue < p50) return '25TH_TO_50TH';
  if (studentValue < p75) return '50TH_TO_75TH';
  return 'ABOVE_75TH';
}

/**
 * Get percentile label for display
 */
export function getPercentileLabel(rank: PercentileRank): string {
  const labels: Record<PercentileRank, string> = {
    BELOW_25TH: 'Below 25th Percentile',
    '25TH_TO_50TH': '25th-50th Percentile',
    '50TH_TO_75TH': '50th-75th Percentile (Middle 50%)',
    ABOVE_75TH: 'Above 75th Percentile (Top 25%)',
  };
  return labels[rank];
}

/**
 * Get school selectivity tier
 */
export function getSelectivityTier(acceptanceRate: number): SelectivityTier {
  if (acceptanceRate < 0.04) return 'ULTRA_SELECTIVE'; // <4%
  if (acceptanceRate < 0.08) return 'EXTREMELY_SELECTIVE'; // 4-8%
  if (acceptanceRate < 0.15) return 'HIGHLY_SELECTIVE'; // 8-15%
  return 'SELECTIVE'; // 15%+
}

/**
 * Get selectivity tier label for display
 */
export function getSelectivityLabel(tier: SelectivityTier): string {
  const labels: Record<SelectivityTier, string> = {
    ULTRA_SELECTIVE: 'Ultra Selective (<4% acceptance)',
    EXTREMELY_SELECTIVE: 'Extremely Selective (4-8% acceptance)',
    HIGHLY_SELECTIVE: 'Highly Selective (8-15% acceptance)',
    SELECTIVE: 'Selective (15%+ acceptance)',
  };
  return labels[tier];
}

/**
 * Calculate probability multiplier based on demographics
 */
export function calculateDemographicMultiplier(
  schoolId: string,
  demographics: {
    legacy?: boolean;
    first_gen?: boolean;
    athlete?: boolean;
    urm?: boolean;
  }
): number {
  const cds = getCDSData(schoolId);
  if (!cds) return 1.0;

  let multiplier = 1.0;

  if (demographics.legacy) multiplier *= cds.legacy_roi;
  if (demographics.first_gen) multiplier *= cds.first_gen_roi;
  if (demographics.athlete) multiplier *= cds.athlete_roi;
  if (demographics.urm) multiplier *= cds.urm_roi;

  return multiplier;
}

/**
 * Compare student SAT to school percentiles
 */
export function compareSATToSchool(
  studentSAT: number,
  schoolId: string
): {
  rank: PercentileRank;
  label: string;
  isCompetitive: boolean;
  gap25th: number;
  gap75th: number;
} {
  const cds = getCDSData(schoolId);
  if (!cds) {
    return {
      rank: 'BELOW_25TH',
      label: 'No data available',
      isCompetitive: false,
      gap25th: 0,
      gap75th: 0,
    };
  }

  const rank = getPercentileRank(
    studentSAT,
    cds.sat_25th,
    cds.sat_50th,
    cds.sat_75th
  );

  return {
    rank,
    label: getPercentileLabel(rank),
    isCompetitive: rank === '50TH_TO_75TH' || rank === 'ABOVE_75TH',
    gap25th: studentSAT - cds.sat_25th,
    gap75th: studentSAT - cds.sat_75th,
  };
}

/**
 * Compare student GPA to school percentiles
 */
export function compareGPAToSchool(
  studentGPA: number,
  schoolId: string
): {
  rank: PercentileRank;
  label: string;
  isCompetitive: boolean;
  gap25th: number;
  gap75th: number;
} {
  const cds = getCDSData(schoolId);
  if (!cds) {
    return {
      rank: 'BELOW_25TH',
      label: 'No data available',
      isCompetitive: false,
      gap25th: 0,
      gap75th: 0,
    };
  }

  const rank = getPercentileRank(
    studentGPA,
    cds.gpa_25th,
    cds.gpa_50th,
    cds.gpa_75th
  );

  return {
    rank,
    label: getPercentileLabel(rank),
    isCompetitive: rank === '50TH_TO_75TH' || rank === 'ABOVE_75TH',
    gap25th: Number((studentGPA - cds.gpa_25th).toFixed(2)),
    gap75th: Number((studentGPA - cds.gpa_75th).toFixed(2)),
  };
}

/**
 * Check if school considers legacy in admissions
 */
export function considersLegacy(schoolId: string): boolean {
  const cds = getCDSData(schoolId);
  if (!cds) return false;
  return cds.legacy_roi > 1.0;
}

/**
 * Get schools sorted by acceptance rate (most selective first)
 */
export function getSchoolsBySelectivity(): CDSData[] {
  return Object.values(CDS_DATA).sort(
    (a, b) => a.acceptance_rate - b.acceptance_rate
  );
}

/**
 * Get schools where student SAT is competitive (>=25th percentile)
 */
export function getCompetitiveSchoolsForSAT(studentSAT: number): CDSData[] {
  return Object.values(CDS_DATA).filter(
    (school) => studentSAT >= school.sat_25th
  );
}

/**
 * Get schools where student GPA is competitive (>=25th percentile)
 */
export function getCompetitiveSchoolsForGPA(studentGPA: number): CDSData[] {
  return Object.values(CDS_DATA).filter(
    (school) => studentGPA >= school.gpa_25th
  );
}

/**
 * Calculate estimated probability boost from early application
 */
export function getEarlyApplicationBoost(schoolId: string): number | null {
  const cds = getCDSData(schoolId);
  if (!cds || !cds.acceptance_rate_ea || !cds.acceptance_rate_rd) return null;

  // Calculate the ratio of EA to RD acceptance rates
  return Number((cds.acceptance_rate_ea / cds.acceptance_rate_rd).toFixed(2));
}

export default CDS_DATA;
