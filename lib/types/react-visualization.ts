/**
 * ReAct Cycle Visualization Types
 * IvyQuest v5.1 Multi-Agent Dashboard
 *
 * Provides complete type definitions for:
 * - ReAct THINK/REASON/ACT/VALIDATE cycle visualization (v5.1 standard)
 * - EC Generation Engine 4 Pillars + 10 Dimensions
 * - Activity output cards with quality metrics
 * - Multi-agent orchestration view
 * - Quality Score with "Only They" test integration
 *
 * NOTE: v5.1 changes ReAct phases from (think/act/observe/learn)
 *       to (think/reason/act/validate) for better clarity.
 */

// ============================================================================
// REACT CYCLE PHASE TYPES (v5.1 Standard)
// ============================================================================

/**
 * v5.1 ReAct Phase Names
 * - think: Analyze inputs, extract information, identify gaps
 * - reason: Apply logic, make decisions, plan actions
 * - act: Execute actions, call tools, generate outputs
 * - validate: Check quality, compare benchmarks (replaces observe+learn)
 */
export type ReActPhase = 'think' | 'reason' | 'act' | 'validate';

/**
 * Legacy phase type for backwards compatibility
 * @deprecated Use ReActPhase instead
 */
export type LegacyPhaseType = 'think' | 'act' | 'observe' | 'learn';

/**
 * Phase type that supports both old and new phase names
 */
export type PhaseType = ReActPhase | LegacyPhaseType;

/**
 * THINK phase data - Agent's reasoning and analysis
 */
export interface ThinkPhaseData {
  reasoning: string;
  planned_actions: string[];
  focus_areas: string[];
  gap_analysis: {
    critical: string[];
    medium: string[];
    low: string[];
  };
  tools_selected: string[];
  benchmark_targets: Record<string, number>;
  confidence: number;
}

/**
 * REASON phase data - Logic application and decision making (v5.1 NEW)
 */
export interface ReasonPhaseData {
  reasoning: string;
  decisions_made: string[];
  logic_applied: string[];
  constraints_considered: string[];
  approach_selected: string;
  confidence: number;
}

/**
 * ACT phase data - Tool execution and actions taken
 */
export interface ActPhaseData {
  action: string;
  tools_executed: ToolExecution[];
  hints_applied: number;
  input_summary: Record<string, unknown>;
  output_summary: Record<string, unknown>;
  duration_ms: number;
}

/**
 * Tool execution record
 */
export interface ToolExecution {
  name: string;
  duration_ms: number;
  success: boolean;
  error?: string;
}

/**
 * VALIDATE phase data - Quality validation and scoring (v5.1 replaces observe+learn)
 */
export interface ValidatePhaseData {
  quality_score: QualityScore;
  passed: boolean;
  failing_dimensions: string[];
  issues_found: string[];
  strengths_found: string[];
  what_worked: string[];
  what_failed: string[];
  corrections_to_apply: string[];
  should_continue: boolean;
  quality_delta?: number;
}

/**
 * Legacy OBSERVE phase data - Quality validation and scoring
 * @deprecated Use ValidatePhaseData instead
 */
export interface ObservePhaseData {
  quality_score: number;
  voice_score: number;
  golden_similarity: number;
  combined_score: number;
  passed: boolean;
  failing_dimensions: string[];
  issues_found: string[];
  strengths_found: string[];
}

/**
 * Legacy LEARN phase data - Self-correction and improvement
 * @deprecated Use ValidatePhaseData instead
 */
export interface LearnPhaseData {
  reasoning: string;
  what_worked: string[];
  what_failed: string[];
  quality_delta: number;
  corrections_to_apply: string[];
  should_continue: boolean;
}

// ============================================================================
// QUALITY SCORE TYPES (v5.1 with Only They test)
// ============================================================================

/**
 * Quality score weights
 * v5.1: Updated weights with only_they at 30%
 */
export interface QualityWeights {
  guardrails: number;  // 0.25
  voice: number;       // 0.20
  golden: number;      // 0.25
  only_they: number;   // 0.30
}

/**
 * Quality status
 */
export type QualityStatus = 'passed' | 'warning' | 'failed';

/**
 * Quality tier for activities
 */
export type QualityTier = 'standout' | 'good' | 'needs_work';

/**
 * Complete Quality Score with v5.1 only_they integration
 */
export interface QualityScore {
  guardrails_score: number;
  voice_score: number;
  golden_similarity: number;
  only_they_score: number;  // v5.1 NEW
  total: number;
  status: QualityStatus;
  weights: QualityWeights;
}

/**
 * Default quality weights (v5.1 standard)
 */
export const DEFAULT_QUALITY_WEIGHTS: QualityWeights = {
  guardrails: 0.25,
  voice: 0.20,
  golden: 0.25,
  only_they: 0.30,
} as const;

// ============================================================================
// REACT CYCLE STRUCTURE (v5.1)
// ============================================================================

/**
 * v5.1 ReAct Cycle with new phase structure
 */
export interface ReActCycle {
  cycle_number: number;
  phases: {
    think: ThinkPhaseData;
    reason: ReasonPhaseData;
    act: ActPhaseData;
    validate: ValidatePhaseData;
  };
  quality_score: QualityScore;
  quality_delta: number;
  passed: boolean;
  learning: string;
  hints_for_next: string[];
  total_duration_ms: number;
}

/**
 * Legacy cycle summary with all 4 phases (backwards compatibility)
 * @deprecated Use ReActCycle instead
 */
export interface CycleSummary {
  cycle: number;
  think: ThinkPhaseData;
  act: ActPhaseData;
  observe: ObservePhaseData;
  learn: LearnPhaseData;
  duration_ms: number;
  // Backwards compatibility - quality_score at top level
  quality_score?: number;
  // v5.1 additions for new phase support
  reason?: ReasonPhaseData;
  validate?: ValidatePhaseData;
}

// ============================================================================
// INPUT/OUTPUT DATA FLOW TYPES
// ============================================================================

/**
 * Data flow between agents in orchestration
 */
export interface InputDataFlow {
  from_assessment?: {
    narrative_dna?: string;
    archetype?: string;
    confidence?: number;
  };
  from_ec_agent?: {
    spike?: string;
    pillars?: string[];
    portfolio_balance_score?: number;
  };
  to_awards_agent?: {
    archetype?: string;
    spike_keywords?: string[];
  };
  to_programs_agent?: {
    archetype?: string;
    constraints?: Record<string, unknown>;
  };
  // Backwards compatibility - alternative property names
  from_profile?: Record<string, unknown>;
  to_downstream_agents?: Record<string, unknown>;
}

/**
 * Complete ReAct metadata structure
 */
export interface ReactMetadata {
  success: boolean;
  cycles_executed: number;
  max_cycles: number;
  final_confidence: number;
  passed_quality: boolean;
  improvement_trajectory: number[];
  total_duration_ms: number;
  cycle_summary: CycleSummary[];
  input_data_flow?: InputDataFlow;
  agentic_enabled: boolean;
  version: string;
  // Optional agent name for display
  agent_name?: string;
  // v5.1 additions
  final_quality_score?: QualityScore;
  react_cycles?: ReActCycle[];
}

// ============================================================================
// EC GENERATION ENGINE TYPES (4 Pillars + 10 Dimensions)
// ============================================================================

/**
 * The 4 Pillars of compelling ECs
 * Formula: IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE
 */
export type PillarType = 'IDENTITY' | 'APTITUDE' | 'PASSION' | 'SERVICE';

/**
 * Individual pillar evidence and analysis
 */
export interface PillarData {
  pillar_type: PillarType;
  type?: PillarType;  // Backwards compatibility
  label: string;
  elements: string[];
  evidence: string[];
  strength: number;  // 0-100
  strength_score?: number;  // Alias
  confidence: number;
  missing: string[];
  color: string;
  icon: string;
}

/**
 * Complete 4 Pillars analysis
 */
export interface FourPillarsData {
  identity: PillarData;
  aptitude: PillarData;
  passion: PillarData;
  service: PillarData;
  overall_balance: number;
  dominant_pillar: PillarType;
  weakest_pillar: PillarType;
  narrative_thread: string;
  master_narrative?: string;
  narrative_confidence?: number;
  // Computed fields
  _pillar_count?: number;
  _overall_confidence?: number;
  _specificity_score?: number;
  _active_pillars?: PillarType[];
}

/**
 * Alias for FourPillarsData
 */
export type FourPillars = FourPillarsData;

/**
 * The 10 Dimensions of Hyper-Personalization
 * v5.1: Supports both UPPERCASE and lowercase dimension types
 */
export type DimensionType =
  | 'GEOGRAPHIC' | 'geographic'
  | 'IDENTITY_WHY' | 'identity_why'
  | 'FIELD_GAP' | 'field_gap'
  | 'CATALYST' | 'catalyst'
  | 'TARGET_AUDIENCE' | 'target_audience'
  | 'UNIQUE_CONTRIBUTION' | 'unique' | 'unique_contribution'
  | 'REPRESENTATION' | 'representation'
  | 'CULTURAL_DEPTH' | 'cultural_depth'
  | 'TEMPORAL' | 'temporal'
  | 'PROBLEM_SPECIFICITY' | 'specificity' | 'problem_specificity';

/**
 * Individual dimension analysis
 */
export interface DimensionData {
  id?: number;
  type: DimensionType;
  name?: string;
  label: string;
  description: string;
  applied?: boolean;
  value?: string;
  details?: string;
  score: number;  // 0-100
  evidence: string[];
  gap_identified?: string;
  recommendation?: string;
  recommendations?: string[];
  priority: 'critical' | 'high' | 'medium' | 'low';
}

/**
 * Complete 10 Dimensions analysis
 */
export interface TenDimensionsData {
  dimensions: DimensionData[];
  dimensions_met: number;
  total_dimensions: number;
  hyper_personalization_score: number;
  critical_gaps: string[];
  recommended_focus: DimensionType[];
  // Computed fields
  _applied_count?: number;
  _coverage_score?: number;
  _passes_minimum?: boolean;
}

/**
 * Alias for TenDimensionsData
 */
export type TenDimensions = TenDimensionsData;

// ============================================================================
// IDENTITY SYNTHESIS TYPES (v5.1 NEW)
// ============================================================================

/**
 * Reframe data for Despite → Because transformation
 */
export interface ReframeData {
  original: string;
  reframed: string;
  transformation: string;
  applied: boolean;
}

/**
 * Complete Identity Synthesis output
 */
export interface IdentitySynthesis {
  // Core identifiers
  spike: string;
  spike_confidence: number;
  archetype: string;
  archetype_confidence: number;

  // Four Pillars
  four_pillars: FourPillarsData;
  pillars: PillarType[];  // Convenience field

  // Narrative
  master_narrative: string;
  reframe: ReframeData;

  // Portfolio
  portfolio_balance_score: number;
  portfolio_gaps: string[];
  portfolio_strengths: string[];

  // Quality
  total_impact_score: number;
  specificity_score: number;
}

// ============================================================================
// GENERATED ACTIVITY TYPES
// ============================================================================

/**
 * Activity type classification
 */
export type ActivityType =
  | 'signature_project'
  | 'passion_project'
  | 'leadership'
  | 'research'
  | 'community_service'
  | 'club_founding'
  | 'certification'
  | 'competition'
  | 'content_creation'
  | 'advocacy'
  | 'professional_exploration';

/**
 * Activity source
 */
export type ActivitySource = 'ec_engine' | 'legacy' | 'manual' | 'coach';

/**
 * EC Generation gap type
 */
export type GapType = 'MISSING' | 'WEAK' | 'ENHANCEMENT';

/**
 * Only They test result
 */
export interface OnlyTheyResult {
  passed: boolean;
  score: number;
  unique_identifiers: string[];
  generic_elements: string[];
  reasoning: string;
}

/**
 * Generated activity with full context
 */
export interface GeneratedActivity {
  id?: string;
  name: string;
  title?: string;  // Alias for name
  description: string;
  synthesized_description?: string;
  category: string;
  activity_type?: ActivityType;
  source?: ActivitySource;

  // 4 Pillars mapping
  pillars: PillarType[];
  pillars_used?: PillarType[];  // Alias
  pillar_evidence: Record<string, string>;
  pillar_integration?: Record<string, string>;

  // 10 Dimensions mapping
  dimensions_addressed: DimensionType[];
  dimensions_applied?: number;
  dimension_evidence: Record<string, string>;
  dimension_details?: Record<string, string>;

  // Gap filling
  gap_type: GapType;
  gap_filled: string;
  gap_addressed?: string;  // Alias

  // Quality metrics
  only_they_score: number;
  only_they_passed: boolean;
  only_they_result?: OnlyTheyResult;  // v5.1 detailed result
  specificity_score: number;
  narrative_alignment: number;

  // Execution details
  touchpoints: string[];
  components?: string[];
  implementation_steps?: string[];
  timeline?: Record<string, string>;
  measurable_outcomes?: string[];
  hours_required: number;
  prestige_score: number;
  roi: number;

  // Status
  status?: 'planned' | 'in_progress' | 'completed' | 'abandoned';
  priority?: number;

  // Reframe (Despite → Because)
  despite_because?: {
    constraint: string;
    reframe: string;
    narrative_angle: string;
  };

  // Computed fields
  _is_signature_project?: boolean;
  _quality_tier?: QualityTier;
}

// ============================================================================
// EC CONTEXT TYPES (v5.1 NEW - for downstream agent flow)
// ============================================================================

/**
 * EC Context passed to downstream agents (Awards, Programs)
 */
export interface ECContext {
  four_pillars: FourPillarsData;
  master_narrative: string;
  reframe: ReframeData;
  gap_analysis: Record<string, unknown>;
  archetype: string;
  spike: string;
}

/**
 * EC Generation Engine output
 */
export interface ECGenerationResult {
  success: boolean;

  // Identity synthesis
  identity_synthesis?: IdentitySynthesis;
  spike: string;
  spike_confidence: number;
  archetype: string;
  archetype_confidence: number;

  // Analysis
  four_pillars: FourPillarsData;
  ten_dimensions: TenDimensionsData;

  // Generated activities
  activities: GeneratedActivity[];
  recommended_activities?: GeneratedActivity[];  // Alias

  // Quality validation
  only_they_passed: boolean;
  quality_score: number;

  // EC Context for downstream
  ec_context?: ECContext;
  validation?: Record<string, unknown>;

  // Degradation handling
  degraded?: boolean;
  degradation_reason?: string;
  error?: string;

  // Metadata
  coach_augmentation_applied?: string;
  version: string;

  // Computed fields
  _activity_count?: number;
  _passing_count?: number;
  _signature_count?: number;
}

// ============================================================================
// GAME PLAN RESULT TYPES (v5.1 NEW)
// ============================================================================

/**
 * Complete GamePlan orchestration result
 */
export interface GamePlanResult {
  success: boolean;
  profile_id: string;

  // Identity
  identity_synthesis: IdentitySynthesis;
  archetype: string;
  spike: string;
  pillars: PillarType[];
  narrative_dna: string;

  // EC Generation
  ec_generation?: ECGenerationResult;

  // Activities (canonical list)
  activities: GeneratedActivity[];

  // Awards & Programs
  awards: Record<string, unknown>;
  programs: Record<string, unknown>;

  // Strategy
  identity_seeds: unknown[];
  phases: unknown[];
  summary: Record<string, unknown>;

  // ReAct
  _react?: ReactMetadata;
  _react_by_agent: Record<string, ReactMetadata>;
}

// ============================================================================
// MULTI-AGENT ORCHESTRATION TYPES
// ============================================================================

/**
 * Agent execution status in orchestration
 */
export type AgentStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

/**
 * Individual agent in orchestration
 */
export interface OrchestratedAgent {
  name: string;
  type: 'EC' | 'Awards' | 'Programs' | 'GamePlan';
  status: AgentStatus;
  execution_order: 'sequential' | 'parallel';
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
  react_metadata?: ReactMetadata;
  output_summary?: Record<string, unknown>;
  error?: string;
}

/**
 * Complete orchestration view
 */
export interface OrchestrationView {
  orchestrator: string;
  strategy: string;  // "EC → Awards || Programs" pattern
  agents: OrchestratedAgent[];
  data_flow: InputDataFlow;
  total_duration_ms: number;
  overall_success: boolean;
}

// ============================================================================
// UI COMPONENT PROPS TYPES
// ============================================================================

/**
 * Phase accordion component props
 * v5.1: Supports both old and new phase names
 */
export interface PhaseAccordionProps {
  phase: PhaseType;
  data: ThinkPhaseData | ReasonPhaseData | ActPhaseData | ValidatePhaseData | ObservePhaseData | LearnPhaseData;
  icon: React.ReactNode;
  title: string;
  color: string;
  defaultExpanded?: boolean;
  badge?: string | number;
}

/**
 * Cycle card component props
 */
export interface CycleCardProps {
  cycle: CycleSummary;
  cycleNumber: number;
  totalCycles: number;
  isLatest: boolean;
}

/**
 * Main ReAct visualization props
 */
export interface ReActVisualizationProps {
  agentName: string;
  reactData: ReactMetadata | null;
  isLoading?: boolean;
}

/**
 * Pillar card component props
 */
export interface PillarCardProps {
  pillar: PillarData;
  isHighlighted?: boolean;
  onClick?: () => void;
}

/**
 * Dimension accordion item props
 */
export interface DimensionAccordionItemProps {
  dimension: DimensionData;
  isExpanded: boolean;
  onToggle: () => void;
}

/**
 * Activity output card props
 */
export interface ActivityOutputCardProps {
  activity: GeneratedActivity;
  index?: number;
  showPillars?: boolean;
  showDimensions?: boolean;
  showReframe?: boolean;
  showMetrics?: boolean;
}

// ============================================================================
// VISUALIZATION CONSTANTS (v5.1)
// ============================================================================

/**
 * Phase color configuration with main color and background
 */
export interface PhaseColorConfig {
  color: string;
  bgColor: string;
}

/**
 * v5.1 Phase colors - supports both old and new phase names
 */
export const PHASE_COLORS: Record<string, PhaseColorConfig> = {
  // v5.1 New phases
  think: {
    color: '#3B82F6',      // Blue - analysis
    bgColor: 'rgba(59, 130, 246, 0.1)',
  },
  reason: {
    color: '#8B5CF6',      // Purple - reasoning (NEW)
    bgColor: 'rgba(139, 92, 246, 0.1)',
  },
  act: {
    color: '#10B981',      // Green - action
    bgColor: 'rgba(16, 185, 129, 0.1)',
  },
  validate: {
    color: '#F59E0B',      // Orange - validation (NEW)
    bgColor: 'rgba(245, 158, 11, 0.1)',
  },
  // Legacy phases (backwards compatibility)
  observe: {
    color: '#8B5CF6',      // Purple - maps to reason
    bgColor: 'rgba(139, 92, 246, 0.1)',
  },
  learn: {
    color: '#10B981',      // Green - maps to part of validate
    bgColor: 'rgba(16, 185, 129, 0.1)',
  },
} as const;

/**
 * Pillar colors (v5.1 updated)
 */
export const PILLAR_COLORS: Record<PillarType, string> = {
  IDENTITY: '#14B8A6',   // Teal
  APTITUDE: '#F59E0B',   // Orange/Amber
  PASSION: '#EF4444',    // Red
  SERVICE: '#22C55E',    // Green
} as const;

/**
 * Pillar icons mapping
 */
export const PILLAR_ICONS: Record<PillarType, string> = {
  IDENTITY: 'Fingerprint',
  APTITUDE: 'Brain',
  PASSION: 'Heart',
  SERVICE: 'Users',
} as const;

/**
 * Quality tier colors
 */
export const QUALITY_TIER_COLORS: Record<QualityTier, string> = {
  standout: '#16A34A',   // Green
  good: '#D97706',       // Amber
  needs_work: '#DC2626', // Red
} as const;

/**
 * Dimension priority colors
 */
export const DIMENSION_PRIORITY_COLORS: Record<string, string> = {
  critical: '#DC2626',   // Red
  high: '#F97316',       // Orange
  medium: '#EAB308',     // Yellow
  low: '#22C55E',        // Green
} as const;

/**
 * v5.1 Phase display configuration
 */
export const PHASE_CONFIG: Record<string, { icon: string; label: string; description: string; color: PhaseColorConfig }> = {
  // New phases
  think: {
    icon: 'Brain',
    label: 'THINK',
    description: 'Analyze inputs, extract information, identify gaps',
    color: PHASE_COLORS.think,
  },
  reason: {
    icon: 'Lightbulb',
    label: 'REASON',
    description: 'Apply logic, make decisions, plan actions',
    color: PHASE_COLORS.reason,
  },
  act: {
    icon: 'Zap',
    label: 'ACT',
    description: 'Execute actions, call tools, generate outputs',
    color: PHASE_COLORS.act,
  },
  validate: {
    icon: 'CheckCircle',
    label: 'VALIDATE',
    description: 'Check quality, compare benchmarks, learn',
    color: PHASE_COLORS.validate,
  },
  // Legacy phases
  observe: {
    icon: 'Eye',
    label: 'OBSERVE',
    description: 'Quality validation and scoring',
    color: PHASE_COLORS.observe,
  },
  learn: {
    icon: 'BookOpen',
    label: 'LEARN',
    description: 'Self-correction and improvement',
    color: PHASE_COLORS.learn,
  },
} as const;

/**
 * Dimension labels and descriptions
 */
export const DIMENSION_CONFIG: Record<string, { label: string; description: string }> = {
  GEOGRAPHIC: {
    label: 'Geographic',
    description: 'Where are they from? Local community context.',
  },
  geographic: {
    label: 'Geographic',
    description: 'Where are they from? Local community context.',
  },
  IDENTITY_WHY: {
    label: 'Identity WHY',
    description: 'What personal experience drives this interest?',
  },
  identity_why: {
    label: 'Identity WHY',
    description: 'What personal experience drives this interest?',
  },
  FIELD_GAP: {
    label: 'Field Gap',
    description: 'What gap in the field are they addressing?',
  },
  field_gap: {
    label: 'Field Gap',
    description: 'What gap in the field are they addressing?',
  },
  CATALYST: {
    label: 'Catalyst',
    description: 'What specific moment sparked this journey?',
  },
  catalyst: {
    label: 'Catalyst',
    description: 'What specific moment sparked this journey?',
  },
  TARGET_AUDIENCE: {
    label: 'Target Audience',
    description: 'Who specifically are they helping?',
  },
  target_audience: {
    label: 'Target Audience',
    description: 'Who specifically are they helping?',
  },
  UNIQUE_CONTRIBUTION: {
    label: 'Unique Contribution',
    description: 'What can only THEY contribute?',
  },
  unique: {
    label: 'Unique Contribution',
    description: 'What can only THEY contribute?',
  },
  unique_contribution: {
    label: 'Unique Contribution',
    description: 'What can only THEY contribute?',
  },
  REPRESENTATION: {
    label: 'Representation',
    description: 'How do they represent underserved perspectives?',
  },
  representation: {
    label: 'Representation',
    description: 'How do they represent underserved perspectives?',
  },
  CULTURAL_DEPTH: {
    label: 'Cultural Depth',
    description: 'How does heritage shape their approach?',
  },
  cultural_depth: {
    label: 'Cultural Depth',
    description: 'How does heritage shape their approach?',
  },
  TEMPORAL: {
    label: 'Temporal',
    description: 'Why is this the right time for this work?',
  },
  temporal: {
    label: 'Temporal',
    description: 'Why is this the right time for this work?',
  },
  PROBLEM_SPECIFICITY: {
    label: 'Problem Specificity',
    description: 'How precisely is the problem defined?',
  },
  specificity: {
    label: 'Problem Specificity',
    description: 'How precisely is the problem defined?',
  },
  problem_specificity: {
    label: 'Problem Specificity',
    description: 'How precisely is the problem defined?',
  },
} as const;
