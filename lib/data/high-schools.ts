/**
 * High School Database
 *
 * 16 Bay Area high school profiles for hyper-local benchmarking
 * Source: Ported from Gemini Phoenix v2.2 InsightLogic system
 *
 * This data enables:
 * - Peer benchmarking (compare to school's Stanford/Harvard admits)
 * - Rigor context (AP utilization rates)
 * - Strategic recommendations (dual enrollment opportunities)
 */

// ============================================================================
// TYPES
// ============================================================================

export type CompetitivenessLevel = 'EXTREME' | 'HIGH' | 'MODERATE';
export type StrategicValue = 'HIGH' | 'MEDIUM' | 'LOW';

export interface DualEnrollmentInfo {
  available: boolean;
  partnerCollege?: string;
  strategicValue: StrategicValue;
}

export interface MatriculationData {
  target: string;
  admitsPerYear: number;
  avgAdmitSat: number;
  commonSpikes: string[];
}

export interface HighSchoolProfile {
  id: string;
  name: string;
  city: string;

  // Competitive context
  competitiveness: CompetitivenessLevel;

  // GPA & Rigor context
  avgGpa: number;           // Unweighted Median
  top10PercentGpa: number;  // Weighted Threshold for Top 10%

  // Course menu
  apOfferings: number;      // Total APs in catalog
  apCapPolicy: string | null; // e.g. "No APs in 9th"

  // Dual enrollment strategy
  dualEnrollment: DualEnrollmentInfo;

  // Outcomes (Stanford as proxy for Ivy+)
  matriculation: MatriculationData[];
}

// ============================================================================
// HIGH SCHOOL DATABASE
// ============================================================================

export const HIGH_SCHOOLS: Record<string, HighSchoolProfile> = {
  // =========================================================================
  // TRI-VALLEY COHORT
  // =========================================================================

  'MOUNTAIN_HOUSE': {
    id: 'MOUNTAIN_HOUSE',
    name: 'Mountain House High',
    city: 'Mountain House',
    competitiveness: 'MODERATE',
    avgGpa: 3.75,
    top10PercentGpa: 4.30,
    apOfferings: 19,
    apCapPolicy: 'Limited access for 9th/10th',
    dualEnrollment: {
      available: true,
      partnerCollege: 'Delta College',
      strategicValue: 'HIGH',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 1,
        avgAdmitSat: 1540,
        commonSpikes: ['Dual Enrollment', 'Community Founder'],
      },
    ],
  },

  'DUBLIN_HIGH': {
    id: 'DUBLIN_HIGH',
    name: 'Dublin High School',
    city: 'Dublin',
    competitiveness: 'HIGH',
    avgGpa: 3.82,
    top10PercentGpa: 4.45,
    apOfferings: 23,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      partnerCollege: 'Las Positas',
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 4,
        avgAdmitSat: 1550,
        commonSpikes: ['Engineering', 'Biomed'],
      },
    ],
  },

  'AMADOR_VALLEY': {
    id: 'AMADOR_VALLEY',
    name: 'Amador Valley High',
    city: 'Pleasanton',
    competitiveness: 'HIGH',
    avgGpa: 3.85,
    top10PercentGpa: 4.50,
    apOfferings: 24,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 6,
        avgAdmitSat: 1560,
        commonSpikes: ['Robotics', 'Debate'],
      },
    ],
  },

  'FOOTHILL': {
    id: 'FOOTHILL',
    name: 'Foothill High School',
    city: 'Pleasanton',
    competitiveness: 'HIGH',
    avgGpa: 3.84,
    top10PercentGpa: 4.48,
    apOfferings: 22,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 5,
        avgAdmitSat: 1550,
        commonSpikes: ['Math Competition', 'Research'],
      },
    ],
  },

  'TRACY_HIGH': {
    id: 'TRACY_HIGH',
    name: 'Tracy High School',
    city: 'Tracy',
    competitiveness: 'MODERATE',
    avgGpa: 3.60,
    top10PercentGpa: 4.20,
    apOfferings: 14,
    apCapPolicy: 'IB Program Focus',
    dualEnrollment: {
      available: true,
      partnerCollege: 'Delta College',
      strategicValue: 'HIGH',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 0.5,
        avgAdmitSat: 1510,
        commonSpikes: ['IB Diploma', 'AgSci'],
      },
    ],
  },

  'LIVERMORE': {
    id: 'LIVERMORE',
    name: 'Livermore High School',
    city: 'Livermore',
    competitiveness: 'MODERATE',
    avgGpa: 3.55,
    top10PercentGpa: 4.15,
    apOfferings: 16,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'HIGH',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 0.5,
        avgAdmitSat: 1500,
        commonSpikes: ['Athletics', 'STEM'],
      },
    ],
  },

  // =========================================================================
  // SILICON VALLEY CORE (EXTREME SATURATION)
  // =========================================================================

  'MONTA_VISTA': {
    id: 'MONTA_VISTA',
    name: 'Monta Vista High',
    city: 'Cupertino',
    competitiveness: 'EXTREME',
    avgGpa: 3.92,
    top10PercentGpa: 4.65,
    apOfferings: 26,
    apCapPolicy: 'Open but rigorous',
    dualEnrollment: {
      available: true,
      partnerCollege: 'De Anza',
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 14,
        avgAdmitSat: 1570,
        commonSpikes: ['USAMO', 'Research Published', 'Startup'],
      },
    ],
  },

  'CUPERTINO_HIGH': {
    id: 'CUPERTINO_HIGH',
    name: 'Cupertino High School',
    city: 'Cupertino',
    competitiveness: 'EXTREME',
    avgGpa: 3.88,
    top10PercentGpa: 4.55,
    apOfferings: 24,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 8,
        avgAdmitSat: 1560,
        commonSpikes: ['Coding', 'Music'],
      },
    ],
  },

  'LYNBROOK': {
    id: 'LYNBROOK',
    name: 'Lynbrook High School',
    city: 'San Jose',
    competitiveness: 'EXTREME',
    avgGpa: 3.94,
    top10PercentGpa: 4.70,
    apOfferings: 22,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 12,
        avgAdmitSat: 1580,
        commonSpikes: ['USACO Platinum', 'AIME'],
      },
    ],
  },

  'GUNN_HIGH': {
    id: 'GUNN_HIGH',
    name: 'Henry M. Gunn High',
    city: 'Palo Alto',
    competitiveness: 'EXTREME',
    avgGpa: 3.90,
    top10PercentGpa: 4.60,
    apOfferings: 28,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 18,
        avgAdmitSat: 1570,
        commonSpikes: ['Research', 'Journalism', 'Robotics'],
      },
    ],
  },

  'PALO_ALTO_HIGH': {
    id: 'PALO_ALTO_HIGH',
    name: 'Palo Alto High',
    city: 'Palo Alto',
    competitiveness: 'EXTREME',
    avgGpa: 3.88,
    top10PercentGpa: 4.50,
    apOfferings: 30,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 16,
        avgAdmitSat: 1560,
        commonSpikes: ['Media', 'Social Justice'],
      },
    ],
  },

  'FREMONT_HIGH': {
    id: 'FREMONT_HIGH',
    name: 'Fremont High (Sunnyvale)',
    city: 'Sunnyvale',
    competitiveness: 'HIGH',
    avgGpa: 3.75,
    top10PercentGpa: 4.40,
    apOfferings: 21,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 3,
        avgAdmitSat: 1540,
        commonSpikes: ['AVID Leadership', 'Engineering'],
      },
    ],
  },

  'IRVINGTON': {
    id: 'IRVINGTON',
    name: 'Irvington High School',
    city: 'Fremont',
    competitiveness: 'HIGH',
    avgGpa: 3.85,
    top10PercentGpa: 4.50,
    apOfferings: 23,
    apCapPolicy: 'Benchmark Project Required',
    dualEnrollment: {
      available: true,
      strategicValue: 'MEDIUM',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 7,
        avgAdmitSat: 1560,
        commonSpikes: ['Arts Magnet', 'Civic Engagement'],
      },
    ],
  },

  // =========================================================================
  // PRIVATE SCHOOLS (THE BENCHMARK)
  // =========================================================================

  'BASIS_SV': {
    id: 'BASIS_SV',
    name: 'Basis Independent SV',
    city: 'San Jose',
    competitiveness: 'EXTREME',
    avgGpa: 3.95,
    top10PercentGpa: 4.90,
    apOfferings: 32,
    apCapPolicy: 'Mandatory APs from 9th',
    dualEnrollment: {
      available: false,
      strategicValue: 'LOW',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 12,
        avgAdmitSat: 1580,
        commonSpikes: ['Capstone Research', 'National Awards'],
      },
    ],
  },

  'VALLEY_CHRISTIAN': {
    id: 'VALLEY_CHRISTIAN',
    name: 'Valley Christian',
    city: 'San Jose',
    competitiveness: 'HIGH',
    avgGpa: 3.80,
    top10PercentGpa: 4.45,
    apOfferings: 26,
    apCapPolicy: null,
    dualEnrollment: {
      available: true,
      strategicValue: 'LOW',
    },
    matriculation: [
      {
        target: 'STANFORD',
        admitsPerYear: 5,
        avgAdmitSat: 1540,
        commonSpikes: ['AMSE Institute', 'Conservatory'],
      },
    ],
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get high school data by ID
 */
export function getHighSchool(schoolId: string): HighSchoolProfile | null {
  return HIGH_SCHOOLS[schoolId] || null;
}

/**
 * Search high schools by name, city
 */
export function searchHighSchools(query: string): HighSchoolProfile[] {
  const lowerQuery = query.toLowerCase();
  return Object.values(HIGH_SCHOOLS).filter(
    (school) =>
      school.name.toLowerCase().includes(lowerQuery) ||
      school.city.toLowerCase().includes(lowerQuery)
  );
}

/**
 * Get all high schools by competitiveness level
 */
export function getHighSchoolsByCompetitiveness(
  level: CompetitivenessLevel
): HighSchoolProfile[] {
  return Object.values(HIGH_SCHOOLS).filter(
    (school) => school.competitiveness === level
  );
}

/**
 * Get all high school IDs
 */
export function getAllHighSchoolIds(): string[] {
  return Object.keys(HIGH_SCHOOLS);
}

/**
 * Get total count of high schools
 */
export function getHighSchoolCount(): number {
  return Object.keys(HIGH_SCHOOLS).length;
}

/**
 * Get readable competitiveness label
 */
export function getCompetitivenessLabel(level: CompetitivenessLevel): string {
  const labels: Record<CompetitivenessLevel, string> = {
    EXTREME: 'Extremely Competitive (Top 1%)',
    HIGH: 'Highly Competitive (Top 10%)',
    MODERATE: 'Moderately Competitive',
  };
  return labels[level];
}

/**
 * Calculate AP utilization rate for a student
 */
export function calculateAPUtilization(
  schoolId: string,
  studentAPCount: number
): number {
  const school = getHighSchool(schoolId);
  if (!school || school.apOfferings === 0) return 0;
  return studentAPCount / school.apOfferings;
}

/**
 * Get Stanford admit data for a high school
 */
export function getStanfordMatriculation(
  schoolId: string
): MatriculationData | null {
  const school = getHighSchool(schoolId);
  if (!school) return null;
  return school.matriculation.find((m) => m.target === 'STANFORD') || null;
}

/**
 * Check if school has high-value dual enrollment
 */
export function hasHighValueDualEnrollment(schoolId: string): boolean {
  const school = getHighSchool(schoolId);
  if (!school) return false;
  return (
    school.dualEnrollment.available &&
    school.dualEnrollment.strategicValue === 'HIGH'
  );
}

/**
 * Get schools with dual enrollment at a specific partner college
 */
export function getSchoolsByPartnerCollege(
  partnerCollege: string
): HighSchoolProfile[] {
  return Object.values(HIGH_SCHOOLS).filter(
    (school) =>
      school.dualEnrollment.available &&
      school.dualEnrollment.partnerCollege?.toLowerCase() ===
        partnerCollege.toLowerCase()
  );
}

export default HIGH_SCHOOLS;
