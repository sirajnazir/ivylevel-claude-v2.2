/**
 * IvyQuest v6.0 - Complete Type Definitions
 * 58 StudentAttributes across 4 layers + Scoring Engine types
 */

// ============================================================================
// LAYER 1: STUDENT ATTRIBUTES (Core 58 Attributes)
// ============================================================================

export type Grade = 9 | 10 | 11 | 12 | 'gap';
export type Role = 'STUDENT' | 'PARENT';
export type MajorCertainty = 'EXPLORING' | 'LIKELY' | 'LOCKED';
export type SaturationLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'ULTRA';
export type SpikeCategory = 'RESEARCH' | 'LEADER' | 'SERVICE' | 'CREATE' | 'BUSINESS' | 'SPORTS' | 'FIGURING';
export type LeadershipLevel = 'FOUNDER_NATIONAL' | 'FOUNDER_STATE' | 'STATE_PRES' | 'SCHOOL_PRES' | 'OFFICER' | 'PARTICIPANT';
export type ResearchLevel = 'NATIONAL' | 'STATE' | 'SCHOOL' | 'INDEPENDENT' | 'NONE';
export type ServiceLeadership = 'NATIONAL' | 'REGIONAL' | 'LOCAL' | 'PARTICIPANT';
export type CoachabilityLevel = 'HIGH' | 'MEDIUM' | 'LOW';
export type BurnoutRisk = 'LOW' | 'MEDIUM' | 'HIGH';
export type EffortLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type SchoolFit = 'BEST_FIT' | 'STRONG_FIT' | 'TOUGH' | 'WORST_FIT';
export type Ethnicity = 'ASIAN' | 'BLACK' | 'HISPANIC' | 'WHITE' | 'NATIVE' | 'PACIFIC_ISLANDER' | 'MULTIRACIAL' | 'OTHER' | 'PREFER_NOT_SAY';
export type IncomeBand = 'BELOW_75K' | '75K_150K' | '150K_300K' | 'ABOVE_300K' | 'TOP_1_PERCENT' | 'PREFER_NOT_SAY';
export type HSType = 'PUBLIC' | 'PRIVATE' | 'MAGNET' | 'CHARTER';
export type Region = 'BAY_AREA' | 'NORTHEAST' | 'SOUTH' | 'MIDWEST' | 'SOUTHWEST' | 'NORTHWEST' | 'INTERNATIONAL' | 'OTHER';
export type ParentArchetype = 'HELICOPTER' | 'BALANCED' | 'HANDS_OFF';

/**
 * Student Identity
 */
export interface StudentIdentity {
  role: Role;
  name: string;
  grade: Grade;
  student_id?: string;
}

/**
 * Layer 1 Aptitude Attributes
 * Weights: GPA 35%, SAT 30%, Rigor 20%, Awards 15%
 */
export interface AptitudeAttributes {
  // GPA (0.35 weight)
  gpa_weighted: number | null;  // Raw 4.0-4.7+ scale
  gpa_normalized: number | null;  // 0.0-1.0 rubric score
  gpa_unweighted?: number | null;

  // Tests (0.30 weight)
  sat_total: number | null;  // 1200-1600
  sat_normalized: number | null;  // 0.0-1.0 rubric score
  sat_math?: number | null;
  sat_verbal?: number | null;
  act_total: number | null;  // 24-36
  act_normalized?: number | null;
  test_optional: boolean;

  // Rigor (0.20 weight)
  ap_count: number | null;  // 0-15+
  ap_avg_score: number | null;  // 3.0-5.0
  rigor_normalized: number | null;  // 0.0-1.0 rubric score
  ib_diploma: boolean;
  dual_enrollment_credits?: number | null;

  // Academic Recognition (0.15 weight)
  academic_awards: string[];  // ENUM_LIST: USAMO, ISEF, Regeneron, etc.
  awards_normalized: number | null;  // 0.0-1.0 rubric score
}

/**
 * Layer 1 Passion Attributes
 * Weights: Leadership 35%, Projects 20%, Research 20%, EC Commitment 15%, Awards 10%
 */
export interface PassionAttributes {
  // Spike Category
  spike_category: SpikeCategory | null;

  // Leadership (0.35 weight)
  leadership_level: LeadershipLevel | null;
  leadership_normalized: number | null;  // 0.0-1.0
  leadership_description?: string;

  // EC Commitment (0.15 weight)
  ec_commitment_years: number | null;  // 1-4+
  ec_hours_weekly: number | null;  // 1-20+
  commitment_normalized: number | null;

  // Projects & Impact (0.20 weight)
  project_impact: number | null;  // People affected: 0-10000+
  project_normalized: number | null;  // 0.0-1.0
  project_description?: string;

  // Research (0.20 weight)
  research_level: ResearchLevel | null;
  research_normalized: number | null;  // 0.0-1.0
  research_description?: string;

  // EC Awards (0.10 weight)
  ec_awards: string[];  // STATE, NATIONAL, INTERNATIONAL
  ec_awards_normalized: number | null;

  // NLP Extraction
  brag_text: string | null;
  brag_nlp_extracted: Record<string, any> | null;
}

/**
 * Layer 1 Community Attributes
 * Weights: Service Leadership 35%, Impact 35%, Hours 20%, Description 10%
 */
export interface CommunityAttributes {
  // Service Leadership (0.35 weight)
  service_leadership: ServiceLeadership | null;
  service_normalized: number | null;  // 0.0-1.0

  // Hours (0.20 weight)
  service_hours: number | null;  // Total by graduation
  hours_normalized: number | null;

  // Community Impact (0.35 weight)
  community_impact: number | null;  // People affected
  impact_normalized: number | null;  // 0.0-1.0

  // Description (0.10 weight)
  service_description?: string;
}

// ============================================================================
// LAYER 2: SCHOOL CONFIGURATIONS
// ============================================================================

export interface SchoolConfig {
  school_id: string;  // 'HARVARD', 'MIT', 'STANFORD', etc.
  school_name: string;

  // Base Statistics (2025 Real Data)
  base_acceptance_rate: number;  // e.g., 0.042 for Harvard (4.2%)
  base_sat_50th: number;  // 50th percentile SAT

  // Category Weights (must sum to 100%)
  weight_aptitude: number;  // e.g., 30% for MIT
  weight_passion: number;   // e.g., 40% for MIT (STEM focused)
  weight_community: number;  // e.g., 20% for MIT
  weight_narrative: number;  // e.g., 10% for MIT

  // Distinctive Emphasis
  distinctive_values: string[];  // e.g., ['TECH', 'MERITOCRACY'] for MIT

  // ROI Multipliers (Chetty 2023 data)
  legacy_roi: number;  // e.g., 5.0 for Harvard, 0.0 for MIT (merit-only)
  first_gen_roi: number;  // e.g., 1.15
  athlete_roi: number;  // e.g., 2.5

  // Major Multipliers
  major_multipliers: Record<string, number>;  // e.g., {'CS': 0.55} for Stanford

  // Theme for Digital Twin
  twin_theme: string;  // 'TECH', 'LEADER', 'GLOBAL', 'ENTREPRENEUR'
  twin_color: string;  // Hex color
}

// ============================================================================
// LAYER 3: CONTEXT MULTIPLIERS
// ============================================================================

/**
 * High School Context (NSC Data)
 */
export interface HighSchoolContext {
  hs_name: string;
  hs_code: string;  // Unique identifier
  hs_type: HSType;
  region: Region;

  // Saturation (NSC historical data)
  saturation_level: SaturationLevel;
  ivy_applicants_per_year: number;
  saturation_adjustment: number;  // -0.08 to +0.05
}

/**
 * Demographic Context (Chetty 2023 multipliers)
 */
export interface DemographicContext {
  ethnicity: Ethnicity | null;
  ethnicity_multiplier: number;  // 0.85-1.15

  first_gen: boolean | null;
  first_gen_multiplier: number;  // 1.15 if true

  legacy: boolean | null;
  legacy_schools: string[];  // Which schools have legacy

  income_band: IncomeBand | null;
  income_top_1_percent: boolean;
  income_multiplier: number;  // 0.95-1.20

  recruited_athlete: boolean;
  athlete_multiplier: number;  // 2.5 if true
}

/**
 * Major Context
 */
export interface MajorContext {
  intended_major: string;
  major_certainty: MajorCertainty;
  major_multiplier: number;  // School-specific, e.g., 0.55 for CS at Stanford
}

// ============================================================================
// LAYER 4: ASSESSMENT INTELLIGENCE (39 Points)
// ============================================================================

/**
 * Psychometrics (Big Five OCEAN + IvyLevel Custom)
 */
export interface StudentPsychometrics {
  // Core Traits (0.0-1.0 scales)
  grit_resilience: number | null;
  introversion_extroversion: number | null;  // -1.0 (intro) to +1.0 (extro)
  coachability: CoachabilityLevel | null;
  coachability_score: number | null;  // 0.0-1.0

  // Narrative Readiness (correlates to essay quality)
  vision_clarity: number | null;  // 0.0-1.0
  identity_comfort: number | null;  // 0.0-1.0
  maturity_level: number | null;  // 0.0-1.0
  articulation_ability: number | null;  // 0.0-1.0 (NLP-derived from brag)

  // Big Five OCEAN (for booster matching)
  openness: number | null;  // 0.0-1.0
  conscientiousness: number | null;
  extraversion: number | null;
  agreeableness: number | null;
  neuroticism: number | null;
}

/**
 * Time Management Profile (168-hour framework)
 */
export interface TimeManagementProfile {
  homework_hours_daily: number | null;  // 1-8+
  social_media_hours_daily: number | null;  // 0-6+
  ec_hours_weekly: number | null;  // From passion attributes
  sleep_hours_daily: number | null;  // Default 8, can adjust

  // Computed
  committed_hours_weekly: number | null;  // Sum of above × 7
  reclaimable_hours_weekly: number | null;  // 168 - committed
  burnout_risk: BurnoutRisk | null;  // Based on committed/168 ratio
}

/**
 * Hidden Capabilities (essay gold mines)
 */
export interface HiddenCapabilities {
  hidden_technical_projects: string[];  // Discord bots, mods, etc.
  hobby_passions: string[];  // Vintage bikes, fanfic, Etsy shop
  unconventional_interests: string[];
  family_responsibilities?: string;
  work_experience?: string;
}

/**
 * Family Context (Duo mode insights)
 */
export interface FamilyContext {
  parent_archetype: ParentArchetype | null;
  academic_expectations: string | null;  // IVY_ONLY, TOP_20, etc.
  family_challenges?: string;
  parent_education_level?: string;
}

/**
 * Academic Intelligence (patterns & trajectory)
 */
export interface AcademicIntelligence {
  grade_pattern_trajectory: 'UPWARD' | 'STABLE' | 'DOWNWARD' | null;
  gpa_dip_context?: string;  // Explanation if dip
  test_anxiety_indicator: number | null;  // SAT vs GPA discrepancy
  learning_differences?: string;
  academic_setbacks?: string;
}

/**
 * Complete Layer 4
 */
export interface AssessmentIntelligence {
  psychometrics: StudentPsychometrics;
  time_management: TimeManagementProfile;
  hidden_capabilities: HiddenCapabilities;
  family_context: FamilyContext;
  academic_intelligence: AcademicIntelligence;
}

// ============================================================================
// COMPLETE STUDENT PROFILE
// ============================================================================

export interface StudentProfile {
  // Meta
  session_id: string;
  timestamp: string;

  // Identity
  identity: StudentIdentity;

  // Layer 2: Targets
  target_schools: string[];  // School IDs
  intended_major: string;
  major_certainty: MajorCertainty;

  // Layer 1: Core Attributes
  aptitude: AptitudeAttributes;
  passion: PassionAttributes;
  community: CommunityAttributes;

  // Layer 3: Context
  high_school: HighSchoolContext | null;
  demographics: DemographicContext;
  major_context: MajorContext;

  // Layer 4: Assessment Intelligence
  assessment_intelligence: AssessmentIntelligence;
}

// ============================================================================
// SCORING ENGINE OUTPUTS
// ============================================================================

/**
 * Ivy+ Ready Score (0-100, controllables focus)
 */
export interface IvyReadyScore {
  total_score: number;  // 0-100
  category_scores: {
    aptitude: number;  // 0-100
    passion: number;   // 0-100
    community: number; // 0-100
    narrative: number; // 0-100 (predicted from Layer 4)
  };
  percentile_rank: number;  // Among Ivy applicants
}

/**
 * RS Rubric Probability (school-specific)
 */
export interface SchoolProbability {
  school_id: string;
  school_name: string;

  // Probability Calculation (Spec Page 8-9 formula)
  p_base: number;  // Base from rubric sigmoid
  p_context: number;  // After context multipliers
  p_final: number;  // Capped at 95%, P_base × ROI

  // Fit Assessment
  fit_level: SchoolFit;
  fit_reasons: string[];  // Why this school likes/dislikes you
  warnings: string[];  // CS penalty, saturation, etc.

  // Evidence
  rubric_score: number;  // 1.0-6.0 (SFFA scale)
  above_base_rate: number;  // How much above school's base acceptance
}

/**
 * Complete Assessment Results
 */
export interface AssessmentResults {
  ivy_ready_score: IvyReadyScore;
  school_probabilities: SchoolProbability[];

  // Diagnostics
  helping_factors: string[];  // Green bullets
  holding_back_factors: string[];  // Amber bullets

  // Archetype
  archetype_detected: string;  // e.g., 'COOKIE_CUTTER_BAY_AREA_CS'
  archetype_label: string;  // Human-readable
  narrative_tagline: string;  // Agent-crafted, e.g., "Indie Game Developer"
}

// ============================================================================
// BOOSTER / MOD SYSTEM
// ============================================================================

export type BoosterCategory = 'APTITUDE' | 'PASSION' | 'COMMUNITY' | 'NARRATIVE' | 'LOOPHOLE' | 'NON_ACADEMIC' | 'STRATEGIC';

export interface Booster {
  // Core identification (supports both template and output formats)
  booster_id?: string;  // Template format: 'AP_ADD_STEM'
  id?: string;  // Output format: 'LOOP_001', 'NON_003'

  // Name (supports both formats)
  title?: string;  // Template format
  name?: string;  // Output format

  description: string;  // 1-2 lines
  category: BoosterCategory;

  // Effort and time
  effort_level?: EffortLevel;  // Template format
  effort?: EffortLevel;  // Output format
  time_weeks: number;  // 0-24
  hours_per_week?: number;  // Template format
  hours_weekly_required?: number;  // Output format
  total_hours?: number;  // Calculated

  // Impact (template format)
  impact_attributes?: string[];
  expected_lift?: { aptitude: number; passion: number; community: number; narrative: number };
  roi_score?: number;
  prerequisites?: string[];
  action_steps?: string[];
  success_metric?: string;

  // Output format fields
  target_school?: string | null;  // Null = all schools
  addresses_gap?: string;  // Which attribute it improves
  current_prob?: number;  // Before booster
  boosted_prob?: number;  // After booster
  roi?: number;  // Multiplicative gain, e.g., 2.3x
  explanation?: string;  // Detailed reasoning
  data_source?: string;  // e.g., 'Chetty 2023', 'CDS 2025'
  matched_to_archetype?: boolean;
  matched_to_ocean?: string[];  // Which Big Five traits make it feasible
  feasibility_score?: number;  // 0.0-1.0 (based on reclaimable hours)
  unlocked?: boolean;  // False if premium-only
}

/**
 * Booster Recommendations
 */
export interface BoosterRecommendations {
  top_3_boosters: Booster[];
  all_eligible_boosters: Booster[];
  projected_improvement: {
    school_id: string;
    current: number;
    with_top_3: number;
    percentage_gain: number;
  }[];
  total_time_commitment: number;  // Hours over weeks
  burnout_check: {
    feasible: boolean;
    reclaimable_hours_sufficient: boolean;
    warning?: string;
  };
}

// ============================================================================
// REAL DATA SOURCES (Spec requirements)
// ============================================================================

/**
 * Chetty 2023 ROI Data
 */
export interface ChettyROIData {
  legacy_multipliers: Record<string, number>;  // Harvard: 5.0, MIT: 0.0
  first_gen_boost: number;  // 1.15
  athlete_boost: number;  // 2.5
  income_top_1_percent_roi: number;  // 1.20
}

/**
 * Common Data Set (CDS) 2025 Acceptance Rates
 */
export interface CDSData {
  school_id: string;
  acceptance_rate: number;  // e.g., 0.042 for Harvard
  sat_25th: number;
  sat_50th: number;
  sat_75th: number;
  total_applicants: number;
  total_accepted: number;
}

/**
 * SFFA v. Harvard Rubric (1-6 scale)
 */
export interface SFFARubric {
  academic_rating: number;  // 1-6 (6 = best)
  extracurricular_rating: number;  // 1-6
  athletic_rating: number;  // 1-6
  personal_rating: number;  // 1-6
  overall_rating: number;  // 1-6
}

/**
 * NSC Saturation Data
 */
export interface NSCSaturationData {
  hs_code: string;
  ivy_applicants_annual: number;
  saturation_level: SaturationLevel;
  adjustment_factor: number;  // -0.08 to +0.05
}

// ============================================================================
// DIGITAL TWIN SYSTEM
// ============================================================================

export interface TwinGear {
  head: string | null;  // Crown, helmet, etc.
  torso: string | null;  // Reactor, armor
  weapon: string | null;  // Sword, mic, beaker
  shield: string | null;  // Community shield
  accessory: string | null;  // Backpack, belt
  aura: string | null;  // Grit red, adaptable blue
}

export interface DigitalTwin {
  twin_id: string;  // 'BASE' or school_id
  school_id: string | null;  // Null for base twin

  // Visual State
  theme: string;  // 'TECH', 'LEADER', etc.
  color: string;  // Hex
  gear: TwinGear;
  current_form: 'GREYED' | 'PARTIAL' | 'IDEAL';  // Greyed = gaps, Ideal = with boosters

  // Stats
  completion_percent: number;  // 0-100
  probability: number;  // School acceptance prob
  is_launched: boolean;  // Post-Frame 5
  broke_barrier: boolean;  // Broke through acceptance barrier

  // Gaps (greyed items)
  gaps: string[];  // e.g., ['AWARDS', 'RESEARCH', 'COMMUNITY']
}

export interface TwinFleet {
  base_twin: DigitalTwin;
  school_twins: DigitalTwin[];
  focused_twin: string | null;  // Which twin is camera-focused
}

// ============================================================================
// ARCHETYPE SYSTEM
// ============================================================================

export interface StudentArchetype {
  archetype_id: string;  // e.g., 'COOKIE_CUTTER_BAY_AREA_CS'
  archetype_label: string;  // e.g., 'Well-Rounded Late-Starter'

  // Detection Signals
  detection_criteria: {
    spike_category?: SpikeCategory;
    region?: Region;
    saturation_level?: SaturationLevel;
    leadership_level_max?: LeadershipLevel;
    passion_scattered?: boolean;  // Multiple weak ECs
    academic_recovery?: boolean;  // GPA upward trend
    creative_synthesis?: boolean;  // Art + STEM
  };

  // Personalization
  avatar_treatment: string;  // Visual style
  booster_priorities: string[];  // Which boosters to emphasize
  narrative_template: string;  // For tagline generation
  quiz_adjustments: string[];  // Which Layer 4 questions to emphasize
}

// Archetype IDs - Universal detection system
export type ArchetypeID =
  // Universal archetypes (always detectable)
  | 'SCHOLAR'      // Academic excellence
  | 'RESEARCHER'   // Research-focused
  | 'LEADER'       // Leadership-driven
  | 'ENTREPRENEUR' // Founder mentality
  | 'CHANGEMAKER'  // Community impact
  | 'ADVOCATE'     // Social justice
  | 'CREATOR'      // Project-focused
  | 'PERFORMER'    // Arts/athletics
  | 'POLYMATH'     // Balanced excellence
  | 'EMERGING'     // Growing potential
  | 'EXPLORER'     // Finding path
  // Legacy spec archetypes (for compatibility)
  | 'COOKIE_CUTTER_BAY_AREA_CS'  // Aarnav-like
  | 'WELL_ROUNDED_LATE_STARTER'  // Anoushka-like
  | 'INTROVERTED_EXPLORER'       // Solo projects + unique hobby
  | 'PARENT_DRIVEN_SCATTERED'    // Helicopter parent + many ECs
  | 'EMERGING_SERVICE_STEM'      // Service focus + academic recovery
  | 'CREATIVE_PREMED'            // Zainab-like art + medicine
  | 'STRUGGLING_JUNIOR_PREMED'   // Low GPA + clinical passion
  | 'HIGH_ACHIEVER_PIVOT'        // Srinidhi-like bio → CS shift
  | 'FRESHMAN_EXPLORER'          // 9th grade + undecided
  | 'ULTRA_COMPETITIVE_ENV'      // Top feeder school
  | 'GENERIC';                   // Fallback (should rarely be used)

// ============================================================================
// KAHOOT QUIZ SYSTEM
// ============================================================================

export interface QuizQuestion {
  question_id: string;
  question_text: string;
  question_type: 'MCQ' | 'SCENARIO' | 'SCALE';

  // Options
  options: {
    value: string;
    label: string;
    score: number;  // Maps to Layer 4 attribute value
  }[];

  // Mapping
  maps_to_attribute: string;  // e.g., 'grit_resilience', 'openness'
  weight: number;  // Contribution to final attribute score

  // Gamification
  time_limit_seconds: number;
  points_correct: number;
  points_streak_bonus: number;
}

export interface QuizSession {
  session_id: string;
  frame_id: number;  // Which frame this quiz belongs to
  questions: QuizQuestion[];

  // Results
  answers: Record<string, string>;  // question_id → answer value
  scores: Record<string, number>;  // question_id → points earned
  total_xp: number;
  streak_count: number;

  // Derived Layer 4
  derived_attributes: Partial<AssessmentIntelligence>;
}

// ============================================================================
// DUO MODE
// ============================================================================

export interface DuoSession {
  session_id: string;
  student_socket_id: string;
  parent_socket_id: string | null;

  // Sync State
  current_frame: number;
  current_card: number;

  // Buffs
  parent_verified_gpa: boolean;  // +0.05 to score
  parent_verified_test: boolean;
  parent_buff_brag: boolean;

  // Votes
  parent_votes: Record<string, string>;  // question_id → vote

  // Split View
  student_view: 'GAME';  // Always game
  parent_view: 'DASHBOARD' | 'GAME';  // Toggle pro mode
}

// ============================================================================
// API PAYLOADS
// ============================================================================

export interface ScoreRequest {
  student_profile: StudentProfile;
  school_configs: SchoolConfig[];
}

export interface ScoreResponse {
  assessment_results: AssessmentResults;
  booster_recommendations: BoosterRecommendations;
  twin_fleet: TwinFleet;
}

export interface NLPExtractionRequest {
  text: string;
  context: 'BRAG' | 'HIDDEN_CAPABILITIES' | 'SERVICE';
}

export interface NLPExtractionResponse {
  extracted_attributes: Partial<PassionAttributes | CommunityAttributes | HiddenCapabilities>;
  confidence_scores: Record<string, number>;
  keywords_detected: string[];
}
