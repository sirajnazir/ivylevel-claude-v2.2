/**
 * InsightLogic Types
 *
 * TypeScript interfaces for the real-time insight generation system
 * Source: Ported from Gemini Phoenix v2.2 InsightLogic system
 */

// ============================================================================
// ENUMS
// ============================================================================

/**
 * 7 Categories of Insights
 */
export type InsightCategory =
  | 'HYPER_LOCAL'      // High school peer benchmarking
  | 'CONTEXT'          // Demographics, region, hooks
  | 'TEMPORAL'         // Grade-aware timing insights
  | 'APTITUDE'         // GPA, SAT, rigor
  | 'PASSION'          // Leadership, research, impact
  | 'PSYCHOMETRIC'     // Grit, burnout, time management
  | 'INSTITUTIONAL';   // CDS benchmarks, school-specific

/**
 * Insight severity/priority levels
 */
export type InsightSeverity =
  | 'critical'    // Red - urgent issue that needs attention
  | 'warning'     // Orange - concern that should be addressed
  | 'positive'    // Green - validation of strength
  | 'neutral';    // Blue - informational/strategic

/**
 * Grade level enum for temporal insights
 */
export type GradeLevel = '8' | '9' | '10' | '11' | '12';

// ============================================================================
// CORE INTERFACES
// ============================================================================

/**
 * Individual insight card
 */
export interface Insight {
  id: string;
  category: InsightCategory;
  title: string;
  message: string;
  severity: InsightSeverity;
  priority: number; // 1-10, higher = more important
  dataSource: string;

  // Optional fields
  delta?: string;           // e.g., "-40 pts", "+0.2 GPA"
  data?: {
    studentValue?: number | string;
    benchmark?: number | string;
    percentile?: number;
    schoolId?: string;
    [key: string]: unknown;
  };
}

/**
 * Student profile for insight generation
 */
export interface StudentProfile {
  // Core academics
  grade: GradeLevel;
  gpa_weighted?: number;
  gpa_unweighted?: number;
  sat_total?: number;
  act_composite?: number;
  ap_count?: number;
  ap_avg_score?: number;

  // Context
  high_school_id?: string;
  target_schools?: string[];
  intended_major?: string;

  // Demographics
  region?: 'BAY_AREA' | 'SOCAL' | 'NORTHEAST' | 'MIDWEST' | 'SOUTH' | 'WEST' | 'RURAL' | 'INTERNATIONAL';
  ethnicity?: 'ASIAN' | 'URM' | 'WHITE' | 'OTHER';
  legacy?: boolean;
  first_gen?: boolean;
  income_top_1?: boolean;
  recruited_athlete?: boolean;

  // Passion layer
  leadership_level?: 'NATL_FOUNDER' | 'STATE_PRES' | 'SCHOOL_PRES' | 'OFFICER' | 'MEMBER';
  project_impact?: number;
  research_level?: 'PEER_REVIEWED' | 'RSI_SIMR' | 'UNIV_LAB' | 'SCHOOL_LAB' | 'NONE';
  ec_awards?: string[];
  ec_commitment_years?: number;

  // Academic awards
  academic_awards?: string[];

  // Psychometric (derived)
  grit_resilience?: number;    // 0-1 scale
  burnout_risk?: 'HIGH' | 'MEDIUM' | 'LOW';
  reclaimable_hours?: number;
}

/**
 * Context for insight generation (called on each attribute update)
 */
export interface InsightGenerationContext {
  profile: StudentProfile;
  attribute?: string;         // Which attribute just changed (e.g., 'gpa_weighted')
  value?: unknown;            // New value of that attribute
  previousValue?: unknown;    // Previous value (for delta calculation)
}

/**
 * Insight generation result
 */
export interface InsightResult {
  insights: Insight[];
  generatedAt: string;
  attributeTrigger?: string;
}

// ============================================================================
// HELPER TYPES
// ============================================================================

/**
 * High school matriculation data (matches high-schools.ts)
 */
export interface MatriculationData {
  target: string;
  admitsPerYear: number;
  avgAdmitSat: number;
  commonSpikes: string[];
}

/**
 * Insight filter options
 */
export interface InsightFilterOptions {
  categories?: InsightCategory[];
  severities?: InsightSeverity[];
  minPriority?: number;
  maxResults?: number;
}

/**
 * Insight statistics (for analytics)
 */
export interface InsightStats {
  total: number;
  byCategory: Record<InsightCategory, number>;
  bySeverity: Record<InsightSeverity, number>;
  averagePriority: number;
}
