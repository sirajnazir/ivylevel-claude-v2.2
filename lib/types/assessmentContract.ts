/**
 * IvyQuest V2.0 - AssessmentContract
 *
 * The AssessmentContract is the core coordination structure passed between agents.
 * It follows the V2 Multi-Agent Spec with four pillar structure and delegation contracts.
 *
 * Agent Flow:
 * ProfileDecoder → AssessmentContract → StrategyArchitect
 *                                     → AwardsSpecialist (via AwardsDelegation)
 *                                     → OpportunityScout (via OpportunityDelegation)
 *                                     → ExecutionPartner
 *                                     → NarrativeCoach
 */

import {
  ArchetypeID,
  SpikeCategory,
  LeadershipLevel,
  ServiceLeadership,
  Gender,
  Ethnicity,
  ImmigrationStatus,
  IncomeBand,
  Region,
  FirstPrinciplePassion,
} from './student';

// =============================================================================
// FIRST PRINCIPLE TYPES (Jenny's Core Extraction)
// =============================================================================

export type FirstPrinciple =
  | 'BUILDER'       // Creates things, makes stuff work
  | 'STORYTELLER'   // Communicates, shares narratives
  | 'DISCOVERER'    // Researches, finds new knowledge
  | 'ADVOCATE'      // Fights for causes, speaks up
  | 'CONNECTOR'     // Brings people together
  | 'HEALER'        // Helps, cares for others
  | 'LEADER';       // Organizes, directs, inspires

// =============================================================================
// GAP AND FACTOR TYPES
// =============================================================================

export interface GapItem {
  /** Unique identifier */
  id: string;

  /** Which pillar this gap affects */
  pillar: 'identity' | 'aptitude' | 'passion' | 'service';

  /** Gap title */
  title: string;

  /** Detailed description */
  description: string;

  /** Current score in this area (0-100) */
  currentScore: number;

  /** Target score to close gap (0-100) */
  targetScore: number;

  /** Impact if gap is closed (0.0-1.0) */
  impact: number;

  /** Suggested actions to close gap */
  suggestedActions: string[];

  /** Estimated effort to close (weeks) */
  effortWeeks?: number;
}

export interface Factor {
  /** Factor description */
  factor: string;

  /** Impact magnitude (0.0-1.0) */
  impact: number;

  /** Which pillar this affects */
  pillar: 'identity' | 'aptitude' | 'passion' | 'service' | 'demographic';

  /** Additional context */
  context?: string;

  /** Data source for this factor */
  dataSource?: string;
}

// =============================================================================
// PILLAR STRUCTURES
// =============================================================================

export interface IdentityPillar {
  /** Identity score (0-100) */
  identityScore: number;

  /** Raw identity data */
  data: {
    firstName?: string;
    lastName?: string;
    grade: 9 | 10 | 11 | 12 | 'gap';
    graduationYear?: number;
    gender?: Gender;
    culturalBackground?: Ethnicity[];
    religion?: string;
    immigrationStatus?: ImmigrationStatus;
    firstGeneration?: boolean;
    region?: Region;
  };

  /** Identity markers extracted */
  markers: string[];

  /** Constraint reframes (turning limitations to strengths) */
  constraintReframes?: {
    constraint: string;
    reframedAs: string;
    narrativeAngle: string;
  }[];
}

export interface AptitudePillar {
  /** Aptitude score (0-100) */
  aptitudeScore: number;

  /** Dimensional breakdown */
  dimensions: {
    gpa: { score: number; weight: number; value?: number };
    testScores: { score: number; weight: number; sat?: number; act?: number };
    rigor: { score: number; weight: number; apCount?: number; ibDiploma?: boolean };
    academicAwards: { score: number; weight: number; awards: string[] };
  };

  /** Raw aptitude data */
  data: {
    gpaWeighted?: number;
    gpaUnweighted?: number;
    satTotal?: number;
    satMath?: number;
    satVerbal?: number;
    actTotal?: number;
    apCount?: number;
    apAvgScore?: number;
    ibDiploma?: boolean;
    academicAwards?: string[];
    testOptional?: boolean;
  };
}

export interface PassionPillar {
  /** Passion score (0-100) */
  passionScore: number;

  /** Spike category */
  spike: SpikeCategory | null;

  /** Spike depth (0-100) */
  spikeDepth: number;

  /** Dimensional breakdown */
  dimensions: {
    leadership: { score: number; weight: number; level?: LeadershipLevel };
    projects: { score: number; weight: number; impactCount?: number };
    research: { score: number; weight: number; level?: string };
    commitment: { score: number; weight: number; years?: number; hoursWeekly?: number };
    ecAwards: { score: number; weight: number; awards: string[] };
  };

  /** Raw passion data */
  data: {
    spikeCategory?: SpikeCategory;
    spikeDescription?: string;
    bragText?: string;
    leadershipLevel?: LeadershipLevel;
    leadershipDescription?: string;
    ecCommitmentYears?: number;
    ecHoursWeekly?: number;
    projectImpact?: number;
    projectDescription?: string;
    researchLevel?: string;
    researchDescription?: string;
    ecAwards?: string[];
    activities?: ActivityData[];
    projects?: ProjectData[];
  };
}

export interface ServicePillar {
  /** Service score (0-100) */
  serviceScore: number;

  /** Dimensional breakdown */
  dimensions: {
    leadership: { score: number; weight: number; level?: ServiceLeadership };
    hours: { score: number; weight: number; total?: number };
    impact: { score: number; weight: number; peopleServed?: number };
    consistency: { score: number; weight: number; yearsActive?: number };
  };

  /** Raw service data */
  data: {
    serviceHours?: number;
    serviceLeadership?: ServiceLeadership;
    serviceDescription?: string;
    serviceCause?: string;
    communityImpact?: number;
    communitiesServed?: string[];
  };
}

// =============================================================================
// SYNTHESIS OUTPUT (from NarrativeSynthesisAgent)
// =============================================================================

export interface SynthesisOutput {
  /**
   * Narrative DNA - Extended story (2-3 paragraphs)
   */
  narrativeDna: string;

  /**
   * Brand statement - One sentence (15-25 words)
   */
  brandStatement: string;

  /**
   * First principle passion (Jenny's core extraction)
   */
  firstPrinciple: FirstPrinciple;

  /**
   * Evidence supporting the first principle
   */
  firstPrincipleEvidence: string[];

  /**
   * Key themes (3-5 themes)
   */
  themes: string[];

  /**
   * Detected archetype
   */
  archetype: {
    id: ArchetypeID;
    label: string;
    confidence: number;
    rationale: string;
  };

  /**
   * Context Relativity Index
   * Adjusts achievements relative to constraints
   */
  cri: number;

  /**
   * Synthesis confidence (0.0-1.0)
   * < 0.7 triggers human handoff
   */
  confidence: number;
}

// =============================================================================
// ANALYSIS OUTPUT
// =============================================================================

export interface AnalysisOutput {
  /** P0 Gaps - Critical, must address */
  p0Gaps: GapItem[];

  /** P1 Gaps - High priority */
  p1Gaps: GapItem[];

  /** P2 Gaps - Nice to have */
  p2Gaps: GapItem[];

  /** Helping factors (green bullets) */
  helpingFactors: Factor[];

  /** Holding factors (amber bullets) */
  holdingFactors: Factor[];
}

// =============================================================================
// DELEGATION CONTRACTS
// =============================================================================

export interface AwardsDelegation {
  /**
   * Profile fit criteria for award matching
   */
  fitCriteria: {
    spikeCategory: SpikeCategory | null;
    academicLevel: 'exceptional' | 'strong' | 'average';
    leadershipLevel: LeadershipLevel | null;
    demographics: {
      firstGen?: boolean;
      underrepresented?: boolean;
      gender?: Gender;
    };
    availableHoursWeekly: number;
  };

  /**
   * Target award categories based on profile
   */
  targetCategories: string[];

  /**
   * CRI-adjusted probability multiplier
   */
  probabilityMultiplier: number;

  /**
   * Constraints for award selection
   */
  constraints: {
    maxEffortHours: number;
    minPrestigeScore: number;
    excludeCategories?: string[];
  };
}

export interface OpportunityDelegation {
  /**
   * Profile fit criteria for opportunity matching
   */
  fitCriteria: {
    grade: number;
    spikeCategory: SpikeCategory | null;
    academicLevel: 'exceptional' | 'strong' | 'average';
    targetMajor?: string;
    demographics: {
      firstGen?: boolean;
      underrepresented?: boolean;
      gender?: Gender;
    };
  };

  /**
   * Target opportunity types based on profile
   */
  targetTypes: string[];

  /**
   * Selectivity preference */
  selectivityPreference: 'highly_selective' | 'selective' | 'moderate' | 'open';

  /**
   * Budget constraints */
  budgetConstraints: {
    maxCost: number;
    needFinancialAid: boolean;
  };

  /**
   * Timeline constraints */
  timeline: {
    earliestStartMonth: number;
    latestEndMonth: number;
    preferResidential: boolean;
  };
}

// =============================================================================
// HIDDEN CALCULATIONS (Internal Use Only)
// =============================================================================

export interface HiddenCalculations {
  /**
   * Hidden probability matrix (ACP-001)
   * School ID → acceptance probability
   */
  probabilities: Record<string, number>;

  /**
   * Hidden target school
   * Best fit based on probability + fit analysis
   */
  hiddenTarget: string;

  /**
   * Chetty baseline for this demographic
   */
  chettyBaseline: number;

  /**
   * Constraint multipliers applied
   */
  constraintMultipliers: Record<string, number>;

  /**
   * Internal school fit scores
   */
  schoolFits?: Record<string, {
    fitScore: number;
    probability: number;
    reasons: string[];
  }>;
}

// =============================================================================
// AGENT METADATA
// =============================================================================

export interface AgentMetadata {
  /** Which agent last processed this contract */
  processingAgent: string;

  /** Processing time in milliseconds */
  processingTimeMs: number;

  /** Whether human handoff is required */
  requiresHandoff: boolean;

  /** Reason for handoff if required */
  handoffReason?: string;

  /** Agent version */
  agentVersion?: string;

  /** Processing history */
  history?: {
    agent: string;
    action: string;
    timestamp: string;
    durationMs: number;
    success: boolean;
  }[];
}

// =============================================================================
// CORE ASSESSMENT CONTRACT (V2.0)
// =============================================================================

/**
 * AssessmentContract V2.0 - The canonical data structure for agent coordination
 *
 * All agents receive this contract and can read/extend specific sections.
 * Hidden fields (_hidden) are NEVER exposed to the UI.
 */
export interface AssessmentContract {
  // =========================================================================
  // METADATA
  // =========================================================================

  /** Contract version */
  version: '2.0';

  /** Unique profile identifier (matches Supabase profiles.id) */
  profileId: string;

  /** ISO timestamp when assessment was generated */
  generatedAt: string;

  /** Session ID for tracking */
  sessionId?: string;

  // =========================================================================
  // FOUR PILLARS
  // =========================================================================

  /** Identity pillar (who the student IS) */
  identity: IdentityPillar;

  /** Aptitude pillar (academic strength) */
  aptitude: AptitudePillar;

  /** Passion pillar (spike and depth) */
  passion: PassionPillar;

  /** Service pillar (community impact) */
  service: ServicePillar;

  // =========================================================================
  // SYNTHESIS (from NarrativeSynthesisAgent)
  // =========================================================================

  /** Synthesized narrative outputs */
  synthesis: SynthesisOutput;

  // =========================================================================
  // ANALYSIS
  // =========================================================================

  /** Gap and factor analysis */
  analysis: AnalysisOutput;

  // =========================================================================
  // DELEGATION CONTRACTS
  // =========================================================================

  /** Delegation contract for AwardsSpecialist */
  awardsDelegation: AwardsDelegation;

  /** Delegation contract for OpportunityScout */
  opportunityDelegation: OpportunityDelegation;

  // =========================================================================
  // HIDDEN FIELDS (internal agent use only)
  // =========================================================================

  /** Hidden calculations - NEVER expose to UI */
  _hidden: HiddenCalculations;

  /** Agent coordination metadata */
  _agentMetadata: AgentMetadata;
}

// =============================================================================
// ACTIVITY AND PROJECT DATA
// =============================================================================

export interface ActivityData {
  name: string;
  category: string;
  yearsCommitted: number;
  hoursWeekly?: number;
  leadershipRole?: string;
  description?: string;
  impact?: number;
}

export interface ProjectData {
  name: string;
  description: string;
  impactCount?: number;
  url?: string;
  technologies?: string[];
}

// =============================================================================
// EVALUATION TYPES
// =============================================================================

/**
 * Golden example for evaluation
 */
export interface GoldenExample {
  /** Profile identifier */
  profileId: string;

  /** Input profile data */
  inputProfile: {
    identity: Partial<IdentityPillar['data']>;
    aptitude: Partial<AptitudePillar['data']>;
    passion: Partial<PassionPillar['data']>;
    service: Partial<ServicePillar['data']>;
  };

  /** Expected outputs */
  expectedOutputs: {
    brandStatement: string;
    themes: string[];
    firstPrinciple: FirstPrinciple;
    narrativeDna?: string;
    archetype?: string;
  };

  /** Jenny's quality annotations */
  jennyAnnotations: {
    brandStatementQuality: number; // 1-5
    themeCoherence: number; // 1-5
    activityAlignment: number; // 1-5
    awardFit: number; // 1-5
    notes?: string;
  };

  /** Difficulty tier */
  difficultyTier: 'easy' | 'medium' | 'hard';

  /** Tags for filtering */
  tags: string[];
}

/**
 * Evaluation run result
 */
export interface EvaluationResult {
  /** Run identifier */
  runId: string;

  /** Agent version tested */
  agentVersion: string;

  /** Golden example ID */
  goldenId: string;

  /** Actual outputs from agent */
  actualOutputs: {
    brandStatement: string;
    themes: string[];
    firstPrinciple?: FirstPrinciple;
    confidence: number;
  };

  /** Objective metric scores */
  objectiveScores: {
    brandStatementLength: { score: number; passed: boolean };
    themeCount: { score: number; passed: boolean };
    confidenceThreshold: { score: number; passed: boolean };
  };

  /** LLM-as-Judge scores */
  llmJudgeScores: {
    brandStatement: { score: number; maxScore: number; evaluation: string };
    themes: { score: number; maxScore: number; overlap: number };
  };

  /** Overall score (0-100) */
  overallScore: number;

  /** Pass/fail status */
  passed: boolean;

  /** Processing time */
  durationMs: number;
}

// =============================================================================
// WORKFLOW TYPES
// =============================================================================

/**
 * Workflow state for a profile
 */
export interface WorkflowState {
  /** Profile ID */
  profileId: string;

  /** Workflow name */
  workflowName: string;

  /** Last execution time */
  lastRun?: string;

  /** Next scheduled run */
  nextRun?: string;

  /** Run count */
  runCount: number;

  /** Workflow-specific state */
  state: Record<string, unknown>;

  /** Whether workflow is enabled */
  enabled: boolean;
}

/**
 * Notification for a student
 */
export interface Notification {
  /** Notification ID */
  id: string;

  /** Profile ID */
  profileId: string;

  /** Title */
  title: string;

  /** Message body */
  message: string;

  /** Notification type */
  type:
    | 'info'
    | 'success'
    | 'warning'
    | 'urgent'
    | 'deadline_30d'
    | 'deadline_7d'
    | 'deadline_3d'
    | 'silence_alert'
    | 'opportunity'
    | 'award'
    | 'celebration';

  /** Delivery channel */
  channel: 'in_app' | 'email' | 'push' | 'sms';

  /** Read status */
  read: boolean;

  /** Sent timestamp */
  sentAt?: string;

  /** Action URL (optional) */
  actionUrl?: string;

  /** Source */
  source: 'workflow' | 'agent' | 'coach' | 'system';

  /** Created timestamp */
  createdAt: string;
}

// =============================================================================
// HELPER FUNCTION TYPES
// =============================================================================

/**
 * Create a minimal contract for testing
 */
export function createMinimalContract(
  profileId: string,
  grade: number,
  spike: SpikeCategory | null
): Partial<AssessmentContract> {
  return {
    version: '2.0',
    profileId,
    generatedAt: new Date().toISOString(),
    identity: {
      identityScore: 50,
      data: { grade: grade as 9 | 10 | 11 | 12 },
      markers: [],
    },
    aptitude: {
      aptitudeScore: 50,
      dimensions: {
        gpa: { score: 50, weight: 0.35 },
        testScores: { score: 50, weight: 0.30 },
        rigor: { score: 50, weight: 0.20 },
        academicAwards: { score: 50, weight: 0.15, awards: [] },
      },
      data: {},
    },
    passion: {
      passionScore: 50,
      spike,
      spikeDepth: 50,
      dimensions: {
        leadership: { score: 50, weight: 0.35 },
        projects: { score: 50, weight: 0.20 },
        research: { score: 50, weight: 0.20 },
        commitment: { score: 50, weight: 0.15 },
        ecAwards: { score: 50, weight: 0.10, awards: [] },
      },
      data: { spikeCategory: spike || undefined },
    },
    service: {
      serviceScore: 50,
      dimensions: {
        leadership: { score: 50, weight: 0.35 },
        hours: { score: 50, weight: 0.20 },
        impact: { score: 50, weight: 0.35 },
        consistency: { score: 50, weight: 0.10 },
      },
      data: {},
    },
  };
}

// =============================================================================
// EXPORTS
// =============================================================================
// Note: All types are already exported inline with their declarations
