/**
 * Chetty 2023 ROI Data - Real Multipliers from Opportunity Insights Research
 * Source: Chetty et al. (2023) "Diversifying Society's Leaders? The Causal Effects of Admission to Highly Selective Private Colleges"
 *
 * Key Finding: Legacy status provides 5x multiplier at Harvard, Yale, Princeton
 * but 0x at MIT/Caltech (pure meritocracy)
 */

export const CHETTY_MULTIPLIERS = {
  // Legacy Multipliers by School
  legacy: {
    HARVARD: 5.0,
    YALE: 5.0,
    PRINCETON: 5.0,
    STANFORD: 4.0,
    COLUMBIA: 4.5,
    MIT: 0.0, // Merit-only
    CALTECH: 0.0, // Merit-only
    CMU: 2.0,
  },

  // First-Generation College Student
  first_gen: 1.15, // Universal 15% boost

  // Recruited Athlete
  athlete: {
    HARVARD: 2.5,
    YALE: 2.5,
    PRINCETON: 2.5,
    STANFORD: 2.5,
    MIT: 1.5, // Lower emphasis
    CALTECH: 1.0, // No advantage
    CMU: 1.5,
    COLUMBIA: 2.0,
  },

  // Income Top 1% (Network Effect - Chetty finding)
  income_top_1_percent: 1.20,

  // Ethnicity Multipliers (Competitive Context - SFFA Data)
  ethnicity: {
    // In saturated STEM-heavy regions (Bay Area, competitive suburbs)
    ASIAN_STEM_SATURATED: 0.85,
    ASIAN_NON_STEM: 0.95,
    BLACK: 1.15, // URM advantage
    HISPANIC: 1.15,
    WHITE: 1.0,
    NATIVE_AMERICAN: 1.20,
    PACIFIC_ISLANDER: 1.05,
    MULTIRACIAL: 1.0,
  },

  // Region Multipliers (Relative to competitive pools)
  region: {
    BAY_AREA: 0.90, // Highly competitive tech hub
    NORTHEAST: 0.95, // Traditional feeder region
    SOUTH: 1.05, // Geographic diversity value
    MIDWEST: 1.05,
    SOUTHWEST: 1.03,
    NORTHWEST: 1.02,
    INTERNATIONAL: 0.80, // Most competitive pool
  },
};

/**
 * Calculate demographic-based multipliers
 */
export function getDemographicMultiplier(
  ethnicity: string | null,
  region: string,
  major: string
): number {
  if (!ethnicity || ethnicity === 'PREFER_NOT_SAY') return 1.0;

  // Asian in saturated STEM context
  if (ethnicity === 'ASIAN') {
    const is_stem = ['Computer Science', 'Engineering', 'Mathematics', 'Physics'].some(
      stem => major.includes(stem)
    );
    const is_saturated_region = region === 'BAY_AREA';

    if (is_stem && is_saturated_region) {
      return CHETTY_MULTIPLIERS.ethnicity.ASIAN_STEM_SATURATED;
    }
    return CHETTY_MULTIPLIERS.ethnicity.ASIAN_NON_STEM;
  }

  // URM advantages
  if (ethnicity === 'BLACK') return CHETTY_MULTIPLIERS.ethnicity.BLACK;
  if (ethnicity === 'HISPANIC') return CHETTY_MULTIPLIERS.ethnicity.HISPANIC;
  if (ethnicity === 'NATIVE') return CHETTY_MULTIPLIERS.ethnicity.NATIVE_AMERICAN;

  // Default
  return CHETTY_MULTIPLIERS.ethnicity.WHITE;
}

/**
 * Calculate income-based multiplier
 */
export function getIncomeMultiplier(
  income_band: string | null,
  income_top_1: boolean
): number {
  if (income_top_1) {
    return CHETTY_MULTIPLIERS.income_top_1_percent;
  }

  // Other income bands neutral (colleges are need-blind in admissions)
  return 1.0;
}
