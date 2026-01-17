/**
 * ReAct Cycle Visualization Types
 * IvyQuest v5.1 Multi-Agent Dashboard
 *
 * Provides complete type definitions for:
 * - ReAct THINK → ACT → OBSERVE → LEARN cycle visualization
 * - EC Generation Engine 4 Pillars + 10 Dimensions
 * - Activity output cards with quality metrics
 * - Multi-agent orchestration view
 * - Quality Score with "Only They" test integration
 *
 * SEMANTIC NOTE (v5.1.1):
 * The ReAct framework uses OBSERVE and LEARN phases for self-correction:
 * - OBSERVE: See results, check quality metrics
 * - LEARN: Generate insights and hints for next cycle
 * This is the heart of the iterative improvement loop.
 */

// ============================================================================
// REACT CYCLE PHASE TYPES
// ============================================================================

/**
 * ReAct Phase Names (Semantically Correct)
 *
 * The ReAct framework follows this loop:
 * THINK → ACT → OBSERVE → LEARN → (back to THINK with hints)
 *
 * - think: Analyze inputs, extract information, identify gaps, select tools
 * - act: Execute agent's process(), call tools, generate outputs
 * - observe: See results, check quality metrics, identify issues
 * - learn: Generate insights, create hints for next cycle (SELF-CORRECTION)
 */
export type ReActPhase = 'think' | 'act' | 'observe' | 'learn';

/**
 * Phase type alias for component props
 */
export type PhaseType = ReActPhase;

/**
 * v5.1: Tool status enum
 */
export type ToolStatus = 'planned' | 'executing' | 'completed' | 'failed' | 'skipped';

/**
 * v5.1: Tool selection in THINK phase
 */
export interface ToolSelection {
  tool_id: string;
  tool_name: string;
  purpose: string;
  priority: number;
  estimated_duration_ms?: number;
}

/**
 * THINK phase data - Agent's reasoning and planning
 * v5.1: Enhanced with structured tool selection
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
  tools_selected: ToolSelection[];  // v5.1: Now structured objects
  benchmark_targets: Record<string, number>;
  confidence: number;
  duration_ms?: number;
}

/**
 * ACT phase data - Tool execution and actions taken
 * v5.1: Enhanced with structured tool execution and hints array
 */
export interface ActPhaseData {
  action: string;
  tools_executed: ToolExecution[];
  hints_applied: string[];  // v5.1: Now array of hint strings
  input_summary: Record<string, unknown>;
  output_summary: Record<string, unknown>;
  duration_ms: number;
}

/**
 * Tool execution record
 * v5.1: Enhanced with tool_id, status, and purpose
 */
export interface ToolExecution {
  tool_id: string;
  tool_name: string;
  name?: string;  // Backwards compat alias for tool_name
  status: ToolStatus;
  duration_ms: number;
  success: boolean;
  purpose?: string;
  input_summary?: Record<string, unknown>;
  output_summary?: Record<string, unknown>;
  error?: string;
}

/**
 * OBSERVE phase data - Quality validation and scoring
 *
 * This is where we SEE the results of the action:
 * - Quality scores (guardrails, voice, golden, only_they)
 * - Pass/fail status
 * - Issues found
 * - Strengths identified
 */
export interface ObservePhaseData {
  quality_score: number;
  voice_score: number;
  golden_similarity: number;
  only_they_score?: number;  // v5.1 - if computed
  combined_score: number;
  passed: boolean;
  failing_dimensions: string[];
  issues_found: string[];
  strengths_found: string[];
}

/**
 * LEARN phase data - Self-correction and improvement
 *
 * This is the HEART of self-correction:
 * - What worked in this cycle
 * - What failed and needs improvement
 * - Specific corrections to apply in next cycle
 * - Quality delta showing improvement/regression
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
  only_they_score: number;  // v5.1
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
// REACT CYCLE STRUCTURE
// ============================================================================

/**
 * Complete cycle summary with all 4 phases
 *
 * The self-correction loop:
 * 1. THINK - Analyze and plan
 * 2. ACT - Execute with hints from previous cycle
 * 3. OBSERVE - See results and quality scores
 * 4. LEARN - Generate hints for next cycle
 * 5. (Loop back to THINK if quality < 70)
 */
export interface CycleSummary {
  cycle: number;
  think: ThinkPhaseData;
  act: ActPhaseData;
  observe: ObservePhaseData;
  learn: LearnPhaseData;
  duration_ms: number;
  // Quality score at top level for easy access
  quality_score?: number;
}

// ============================================================================
// INPUT/OUTPUT DATA FLOW TYPES (v5.1 Enhanced)
// ============================================================================

/**
 * v5.1: Data flow node in visualization graph
 */
export interface DataFlowNode {
  node_id: string;
  node_type: 'agent' | 'data' | 'external';
  label: string;
  data_summary: Record<string, unknown>;
}

/**
 * v5.1: Data flow edge in visualization graph
 */
export interface DataFlowEdge {
  from_node: string;
  to_node: string;
  data_type: string;
  fields_passed: string[];
}

/**
 * Data flow between agents in orchestration
 * v5.1: Enhanced with graph structure (nodes/edges) for visualization
 */
export interface InputDataFlow {
  // v5.1: Graph structure for visualization
  agent_id?: string;
  nodes?: DataFlowNode[];
  edges?: DataFlowEdge[];

  // Original agent-to-agent flow (kept for backwards compat)
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
  from_profile?: Record<string, unknown>;
  from_upstream_agent?: Record<string, unknown>;
  to_downstream_agents?: Record<string, Record<string, unknown>>;
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
  agent_name?: string;
  final_quality_score?: QualityScore;
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
  type?: PillarType;  // Alias
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
 * Supports both UPPERCASE and lowercase types
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
// IDENTITY SYNTHESIS TYPES
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
  only_they_result?: OnlyTheyResult;
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
// EC CONTEXT TYPES (for downstream agent flow)
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
// GAME PLAN RESULT TYPES
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
 */
export interface PhaseAccordionProps {
  phase: PhaseType;
  data: ThinkPhaseData | ActPhaseData | ObservePhaseData | LearnPhaseData;
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
// VISUALIZATION CONSTANTS
// ============================================================================

/**
 * Phase color configuration with main color and background
 */
export interface PhaseColorConfig {
  color: string;
  bgColor: string;
}

/**
 * Phase colors - semantically correct THINK/ACT/OBSERVE/LEARN
 */
export const PHASE_COLORS: Record<ReActPhase, PhaseColorConfig> = {
  think: {
    color: '#FF4A23',      // Orange (Ivylevel primary) - reasoning
    bgColor: 'rgba(255, 74, 35, 0.1)',
  },
  act: {
    color: '#3B82F6',      // Blue - action/execution
    bgColor: 'rgba(59, 130, 246, 0.1)',
  },
  observe: {
    color: '#8B5CF6',      // Purple - observation/quality check
    bgColor: 'rgba(139, 92, 246, 0.1)',
  },
  learn: {
    color: '#10B981',      // Green - learning/self-correction
    bgColor: 'rgba(16, 185, 129, 0.1)',
  },
} as const;

/**
 * Pillar colors
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
 * Phase display configuration
 */
export const PHASE_CONFIG: Record<ReActPhase, { icon: string; label: string; description: string; color: PhaseColorConfig }> = {
  think: {
    icon: 'Brain',
    label: 'THINK',
    description: 'Analyze inputs, identify gaps, select tools',
    color: PHASE_COLORS.think,
  },
  act: {
    icon: 'Zap',
    label: 'ACT',
    description: 'Execute agent process, call tools',
    color: PHASE_COLORS.act,
  },
  observe: {
    icon: 'Eye',
    label: 'OBSERVE',
    description: 'See results, check quality metrics',
    color: PHASE_COLORS.observe,
  },
  learn: {
    icon: 'BookOpen',
    label: 'LEARN',
    description: 'Generate hints for self-correction',
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
