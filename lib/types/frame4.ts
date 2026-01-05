/**
 * IvyQuest Frame 4 Data Types
 *
 * These interfaces define what Frame 4 SHOULD be computing and populating.
 * Currently, most of these fields exist in the schema but have default values.
 *
 * THE FIX: Frame 4 frontend must actually compute these from scenario responses
 * and UI inputs, then sync to StudentStore before assessment is saved.
 */

// =============================================================================
// PSYCHOMETRICS (assessment_intelligence.psychometrics)
// =============================================================================

/**
 * Psychometric dimensions derived from Frame 4 scenario responses.
 *
 * CURRENT STATE: All values are 0.5 (defaults)
 * SHOULD BE: Computed from user's scenario choices (0.0 - 1.0)
 */
export interface Psychometrics {
  // Big Five Personality Dimensions
  openness: number;           // 0.0 (closed) to 1.0 (open to experience)
  conscientiousness: number;  // 0.0 (spontaneous) to 1.0 (organized)
  extraversion: number;       // 0.0 (introverted) to 1.0 (extraverted)
  agreeableness: number;      // 0.0 (competitive) to 1.0 (cooperative)
  neuroticism: number;        // 0.0 (stable) to 1.0 (anxious)

  // Derived introversion/extraversion scale
  introversion_extroversion: number;  // -1.0 (intro) to +1.0 (extro)

  // Coaching-specific dimensions
  coachability: 'LOW' | 'MEDIUM' | 'HIGH';  // Categorical
  coachability_score: number;               // 0.0 - 1.0

  // Growth indicators
  grit_resilience: number;     // 0.0 - 1.0
  maturity_level: number;      // 0.0 - 1.0
  vision_clarity: number;      // 0.0 - 1.0
  identity_comfort: number;    // 0.0 - 1.0
  articulation_ability: number; // 0.0 - 1.0
}

/**
 * Scenario response to psychometric mapping.
 *
 * Each scenario question maps to one or more psychometric dimensions.
 * The frontend should aggregate responses to compute final scores.
 */
export interface ScenarioMapping {
  scenario_id: string;
  question: string;
  options: {
    value: string;
    psychometric_impact: Partial<{
      openness: number;
      conscientiousness: number;
      extraversion: number;
      agreeableness: number;
      neuroticism: number;
      grit_resilience: number;
      coachability_score: number;
    }>;
  }[];
}

// Example scenario mapping
export const SCENARIO_MAPPINGS: ScenarioMapping[] = [
  {
    scenario_id: 'deadline_pressure',
    question: 'When facing a tight deadline, you typically...',
    options: [
      {
        value: 'plan_early',
        psychometric_impact: { conscientiousness: 0.2, neuroticism: -0.1 }
      },
      {
        value: 'work_under_pressure',
        psychometric_impact: { conscientiousness: 0.1, grit_resilience: 0.15 }
      },
      {
        value: 'seek_extension',
        psychometric_impact: { agreeableness: 0.1, conscientiousness: -0.1 }
      }
    ]
  },
  {
    scenario_id: 'group_project',
    question: 'In a group project, you prefer to...',
    options: [
      {
        value: 'lead',
        psychometric_impact: { extraversion: 0.2, openness: 0.1 }
      },
      {
        value: 'collaborate',
        psychometric_impact: { agreeableness: 0.2, extraversion: 0.1 }
      },
      {
        value: 'work_independently',
        psychometric_impact: { extraversion: -0.1, conscientiousness: 0.15 }
      }
    ]
  },
  {
    scenario_id: 'feedback_response',
    question: 'When receiving critical feedback, you...',
    options: [
      {
        value: 'embrace_growth',
        psychometric_impact: { coachability_score: 0.3, openness: 0.15 }
      },
      {
        value: 'defend_position',
        psychometric_impact: { coachability_score: -0.1, grit_resilience: 0.1 }
      },
      {
        value: 'reflect_deeply',
        psychometric_impact: { coachability_score: 0.2 }
      }
    ]
  }
];

// =============================================================================
// OPERATING STYLE (profile_data.operating)
// =============================================================================

/**
 * Operating style and preferences.
 *
 * CURRENT STATE: Some fields stored, some missing
 * SHOULD BE: All fields computed from Frame 4 UI
 */
export interface OperatingProfile {
  // Time & Energy (CURRENTLY STORED)
  availableHoursPerWeek: number;    // 0-40
  homeworkHoursPerDay: number;      // 0-8

  // Personal Strengths (CURRENTLY STORED)
  strengths: string[];              // ["competitive", "hands-on", ...]

  // Family Context (CURRENTLY STORED)
  firstGeneration: boolean;
  parent1Occupation: string;
  parent2Occupation: string;

  // Career Direction (CURRENTLY STORED)
  careerDirection: 'yes' | 'no' | 'exploring';
  careerExclusions: string[];
  favoriteSubject: string;

  // === MISSING FIELDS - Need to add ===

  // Peak Performance (NEEDS TO BE ADDED)
  peak_productivity: 'morning' | 'afternoon' | 'evening' | 'night';
  energy_source: 'solo_work' | 'collaboration' | 'structured' | 'flexible';

  // Operating Style Classification (COMPUTED from scenarios)
  operating_style: 'organized_collaborator' | 'dynamic_leader' | 'independent_thinker' | 'adaptive_learner';
  risk_tolerance: 'bold' | 'balanced' | 'cautious';
  stress_response: 'systematic' | 'adaptive' | 'reactive';

  // Raw Responses (FOR RE-COMPUTATION)
  scenario_responses: Record<string, string>;
}

// =============================================================================
// HIDDEN CAPABILITIES (assessment_intelligence.hidden_capabilities)
// =============================================================================

/**
 * Hidden capabilities for essay gold mines.
 *
 * CURRENT STATE: Empty arrays
 * SHOULD BE: Populated from Frame 4 UI prompts
 */
export interface HiddenCapabilities {
  // Technical skills outside academic context
  hidden_technical_projects: string[];
  // Examples: ["built discord bot", "created game mod", "automated homework with Python"]

  // Creative endeavors
  creative_pursuits: string[];
  // Examples: ["graphic design", "video editing", "music production"]

  // Unconventional interests
  unconventional_interests: string[];
  // Examples: ["beekeeping", "vintage car restoration", "urban farming"]

  // Hobbies with depth
  hobby_passions: string[];
  // Examples: ["competitive chess", "origami", "astronomy"]

  // Family/life responsibilities
  family_responsibilities: string | null;
  // Examples: "Care for younger siblings 10 hrs/week", "Help in family business"

  // Work experience
  work_experience: string | null;
  // Examples: "Part-time barista 15 hrs/week", "Summer internship at startup"
}

// =============================================================================
// TIME MANAGEMENT (assessment_intelligence.time_management)
// =============================================================================

/**
 * Time management analysis.
 *
 * CURRENT STATE: Some values stored
 * SHOULD BE: Computed from operating data
 */
export interface TimeManagement {
  // Weekly time budget
  ec_hours_weekly: number;
  homework_hours_daily: number;
  sleep_hours_daily: number;
  social_media_hours_daily: number;
  committed_hours_weekly: number;

  // Computed analysis
  reclaimable_hours_weekly: number;
  burnout_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  time_scarcity: 'ABUNDANT' | 'MODERATE' | 'SCARCE' | 'CRITICAL';
}

// =============================================================================
// ACADEMIC INTELLIGENCE (assessment_intelligence.academic_intelligence)
// =============================================================================

/**
 * Academic patterns and signals.
 */
export interface AcademicIntelligence {
  grade_pattern_trajectory: 'IMPROVING' | 'STABLE' | 'DECLINING';
  test_anxiety_indicator: number;  // 0.0 - 1.0
  study_style: 'visual' | 'auditory' | 'kinesthetic' | 'reading';
}

// =============================================================================
// FAMILY CONTEXT (assessment_intelligence.family_context)
// =============================================================================

/**
 * Family context for coaching approach.
 */
export interface FamilyContext {
  parent_archetype: 'TIGER' | 'HELICOPTER' | 'SUPPORTIVE' | 'HANDS_OFF' | 'BALANCED';
  academic_expectations: 'INTENSE' | 'HIGH' | 'MODERATE' | 'FLEXIBLE';
  college_knowledge_level: 'EXPERT' | 'INFORMED' | 'BASIC' | 'MINIMAL';
  financial_discussion_openness: 'OPEN' | 'CAUTIOUS' | 'PRIVATE';
}

// =============================================================================
// COMPLETE ASSESSMENT INTELLIGENCE STRUCTURE
// =============================================================================

/**
 * The complete assessment_intelligence object that should be in profile_data.
 */
export interface AssessmentIntelligence {
  psychometrics: Psychometrics;
  hidden_capabilities: HiddenCapabilities;
  time_management: TimeManagement;
  academic_intelligence: AcademicIntelligence;
  family_context: FamilyContext;
}

// =============================================================================
// FRAME 4 COMPUTATION FUNCTIONS
// =============================================================================

/**
 * Compute psychometrics from scenario responses.
 *
 * This is what Frame 4 frontend SHOULD be doing.
 */
export function computePsychometrics(
  responses: Record<string, string>
): Psychometrics {
  // Initialize with neutral values
  const scores = {
    openness: 0.5,
    conscientiousness: 0.5,
    extraversion: 0.5,
    agreeableness: 0.5,
    neuroticism: 0.5,
    grit_resilience: 0.5,
    coachability_score: 0.5,
    maturity_level: 0.5,
    vision_clarity: 0.5,
    identity_comfort: 0.5,
    articulation_ability: 0.5,
  };

  // Apply impacts from each scenario response
  for (const [scenarioId, responseValue] of Object.entries(responses)) {
    const mapping = SCENARIO_MAPPINGS.find(m => m.scenario_id === scenarioId);
    if (!mapping) continue;

    const option = mapping.options.find(o => o.value === responseValue);
    if (!option) continue;

    // Add impacts (clamped to 0-1)
    for (const [dimension, impact] of Object.entries(option.psychometric_impact)) {
      if (dimension in scores) {
        scores[dimension as keyof typeof scores] = Math.max(0, Math.min(1,
          scores[dimension as keyof typeof scores] + (impact || 0)
        ));
      }
    }
  }

  // Derive categorical coachability
  const coachability: 'LOW' | 'MEDIUM' | 'HIGH' =
    scores.coachability_score >= 0.7 ? 'HIGH' :
    scores.coachability_score >= 0.4 ? 'MEDIUM' : 'LOW';

  // Derive introversion/extraversion scale
  const introversion_extroversion = (scores.extraversion - 0.5) * 2;  // -1 to +1

  return {
    ...scores,
    coachability,
    introversion_extroversion,
  };
}

/**
 * Compute time management from operating data.
 */
export function computeTimeManagement(
  operating: Partial<OperatingProfile>
): TimeManagement {
  const ecHours = operating.availableHoursPerWeek || 10;
  const homeworkDaily = operating.homeworkHoursPerDay || 2;
  const sleepDaily = 7.5;  // Assumed
  const socialMediaDaily = 2;  // Assumed

  // Calculate committed hours
  const weeklyCommitted = (homeworkDaily * 7) + ecHours + (8 * 5) + (sleepDaily * 7);
  const hoursInWeek = 168;
  const freeHours = hoursInWeek - weeklyCommitted;

  // Determine burnout risk
  let burnoutRisk: 'LOW' | 'MEDIUM' | 'HIGH';
  if (freeHours < 10) burnoutRisk = 'HIGH';
  else if (freeHours < 25) burnoutRisk = 'MEDIUM';
  else burnoutRisk = 'LOW';

  // Determine time scarcity
  let timeScarcity: 'ABUNDANT' | 'MODERATE' | 'SCARCE' | 'CRITICAL';
  if (freeHours >= 35) timeScarcity = 'ABUNDANT';
  else if (freeHours >= 20) timeScarcity = 'MODERATE';
  else if (freeHours >= 10) timeScarcity = 'SCARCE';
  else timeScarcity = 'CRITICAL';

  // Estimate reclaimable hours
  const reclaimable = Math.min(socialMediaDaily * 7, freeHours * 0.3);

  return {
    ec_hours_weekly: ecHours,
    homework_hours_daily: homeworkDaily,
    sleep_hours_daily: sleepDaily,
    social_media_hours_daily: socialMediaDaily,
    committed_hours_weekly: weeklyCommitted,
    reclaimable_hours_weekly: Math.round(reclaimable),
    burnout_risk: burnoutRisk,
    time_scarcity: timeScarcity,
  };
}

/**
 * Derive operating style from psychometrics + responses.
 */
export function deriveOperatingStyle(
  psychometrics: Psychometrics,
  _responses: Record<string, string>
): Pick<OperatingProfile, 'operating_style' | 'risk_tolerance' | 'stress_response'> {
  // Operating style based on conscientiousness + extraversion
  let operating_style: OperatingProfile['operating_style'];
  if (psychometrics.conscientiousness > 0.6 && psychometrics.extraversion > 0.5) {
    operating_style = 'organized_collaborator';
  } else if (psychometrics.extraversion > 0.7) {
    operating_style = 'dynamic_leader';
  } else if (psychometrics.conscientiousness > 0.6) {
    operating_style = 'independent_thinker';
  } else {
    operating_style = 'adaptive_learner';
  }

  // Risk tolerance based on openness + neuroticism
  let risk_tolerance: OperatingProfile['risk_tolerance'];
  if (psychometrics.openness > 0.7 && psychometrics.neuroticism < 0.4) {
    risk_tolerance = 'bold';
  } else if (psychometrics.neuroticism > 0.6) {
    risk_tolerance = 'cautious';
  } else {
    risk_tolerance = 'balanced';
  }

  // Stress response
  let stress_response: OperatingProfile['stress_response'];
  if (psychometrics.conscientiousness > 0.6) {
    stress_response = 'systematic';
  } else if (psychometrics.openness > 0.6) {
    stress_response = 'adaptive';
  } else {
    stress_response = 'reactive';
  }

  return { operating_style, risk_tolerance, stress_response };
}

// =============================================================================
// WHAT FRAME 4 SHOULD DO ON COMPLETION
// =============================================================================

/**
 * This is what Frame 4 should call before proceeding to Frame 5.
 */
export function processFrame4Completion(
  scenarioResponses: Record<string, string>,
  hiddenCapabilities: HiddenCapabilities,
  operatingInputs: Partial<OperatingProfile>
): { assessment_intelligence: Partial<AssessmentIntelligence>; operating: Partial<OperatingProfile> } {
  // 1. Compute psychometrics from scenarios
  const psychometrics = computePsychometrics(scenarioResponses);

  // 2. Compute time management from operating inputs
  const time_management = computeTimeManagement(operatingInputs);

  // 3. Derive operating style
  const operatingStyle = deriveOperatingStyle(psychometrics, scenarioResponses);

  // 4. Build complete operating profile
  const operating: Partial<OperatingProfile> = {
    ...operatingInputs,
    ...operatingStyle,
    scenario_responses: scenarioResponses,
  };

  return {
    assessment_intelligence: {
      psychometrics,
      hidden_capabilities: hiddenCapabilities,
      time_management,
    },
    operating,
  };
}
