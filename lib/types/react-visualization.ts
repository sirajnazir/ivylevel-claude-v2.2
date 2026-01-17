/**
 * ReAct Cycle Visualization Types
 * IvyQuest v5.0 Multi-Agent Dashboard
 *
 * Provides complete type definitions for:
 * - ReAct THINK/ACT/OBSERVE/LEARN cycle visualization
 * - EC Generation Engine 4 Pillars + 10 Dimensions
 * - Activity output cards with quality metrics
 * - Multi-agent orchestration view
 */

// ============================================================================
// REACT CYCLE PHASE TYPES
// ============================================================================

/**
 * THINK phase data - Agent's reasoning and planning
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
 * OBSERVE phase data - Quality validation and scoring
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
 * LEARN phase data - Self-correction and improvement
 */
export interface LearnPhaseData {
  reasoning: string;
  what_worked: string[];
  what_failed: string[];
  quality_delta: number;
  corrections_to_apply: string[];
  should_continue: boolean;
}

/**
 * Complete cycle summary with all 4 phases
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
  type: PillarType;
  label: string;
  evidence: string[];
  strength: number; // 0-100
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
}

/**
 * The 10 Dimensions of Hyper-Personalization
 */
export type DimensionType =
  | 'GEOGRAPHIC'
  | 'IDENTITY_WHY'
  | 'FIELD_GAP'
  | 'CATALYST'
  | 'TARGET_AUDIENCE'
  | 'UNIQUE_CONTRIBUTION'
  | 'REPRESENTATION'
  | 'CULTURAL_DEPTH'
  | 'TEMPORAL'
  | 'PROBLEM_SPECIFICITY';

/**
 * Individual dimension analysis
 */
export interface DimensionData {
  type: DimensionType;
  label: string;
  description: string;
  score: number; // 0-100
  evidence: string[];
  gap_identified?: string;
  recommendation?: string;
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
}

// ============================================================================
// GENERATED ACTIVITY TYPES
// ============================================================================

/**
 * EC Generation gap type
 */
export type GapType = 'MISSING' | 'WEAK' | 'ENHANCEMENT';

/**
 * Generated activity with full context
 */
export interface GeneratedActivity {
  name: string;
  description: string;
  category: string;

  // 4 Pillars mapping
  pillars: PillarType[];
  pillar_evidence: Record<PillarType, string>;

  // 10 Dimensions mapping
  dimensions_addressed: DimensionType[];
  dimension_evidence: Record<DimensionType, string>;

  // Gap filling
  gap_type: GapType;
  gap_filled: string;

  // Quality metrics
  only_they_score: number;
  only_they_passed: boolean;
  specificity_score: number;
  narrative_alignment: number;

  // Execution details
  touchpoints: string[];
  hours_required: number;
  prestige_score: number;
  roi: number;

  // Reframe (Despite → Because)
  despite_because?: {
    constraint: string;
    reframe: string;
    narrative_angle: string;
  };
}

/**
 * EC Generation Engine output
 */
export interface ECGenerationResult {
  success: boolean;

  // Identity synthesis
  spike: string;
  spike_confidence: number;
  archetype: string;
  archetype_confidence: number;

  // Analysis
  four_pillars: FourPillarsData;
  ten_dimensions: TenDimensionsData;

  // Generated activities
  activities: GeneratedActivity[];

  // Quality validation
  only_they_passed: boolean;
  quality_score: number;

  // Metadata
  coach_augmentation_applied?: string;
  version: string;
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
  strategy: string; // "EC → Awards || Programs" pattern
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
  phase: 'think' | 'act' | 'observe' | 'learn';
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
  showPillars?: boolean;
  showDimensions?: boolean;
  showReframe?: boolean;
}

// ============================================================================
// VISUALIZATION CONSTANTS
// ============================================================================

/**
 * Phase type for ReAct cycles
 */
export type PhaseType = 'think' | 'act' | 'observe' | 'learn';

/**
 * Phase color configuration with main color and background
 */
export interface PhaseColorConfig {
  color: string;
  bgColor: string;
}

/**
 * Phase colors (from brand.ts compatible)
 */
export const PHASE_COLORS: Record<PhaseType, PhaseColorConfig> = {
  think: {
    color: '#FF4A23',     // Orange - Ivylevel primary
    bgColor: 'rgba(255, 74, 35, 0.1)',
  },
  act: {
    color: '#3B82F6',     // Blue - action
    bgColor: 'rgba(59, 130, 246, 0.1)',
  },
  observe: {
    color: '#8B5CF6',     // Purple - observation
    bgColor: 'rgba(139, 92, 246, 0.1)',
  },
  learn: {
    color: '#10B981',     // Green - learning
    bgColor: 'rgba(16, 185, 129, 0.1)',
  },
} as const;

/**
 * Pillar colors (from brand.ts)
 */
export const PILLAR_COLORS = {
  IDENTITY: '#7C3AED',  // Purple
  APTITUDE: '#2563EB', // Blue
  PASSION: '#F97316',  // Orange
  SERVICE: '#059669',  // Green
} as const;

/**
 * Pillar icons mapping
 */
export const PILLAR_ICONS = {
  IDENTITY: 'Fingerprint',
  APTITUDE: 'Brain',
  PASSION: 'Heart',
  SERVICE: 'Users',
} as const;

/**
 * Dimension priority colors
 */
export const DIMENSION_PRIORITY_COLORS = {
  critical: '#DC2626', // Red
  high: '#F97316',     // Orange
  medium: '#EAB308',   // Yellow
  low: '#22C55E',      // Green
} as const;

/**
 * Phase display configuration
 */
export const PHASE_CONFIG = {
  think: {
    icon: 'Brain',
    label: 'THINK',
    description: 'Agent reasoning and planning',
    color: PHASE_COLORS.think,
  },
  act: {
    icon: 'Zap',
    label: 'ACT',
    description: 'Tool execution and actions',
    color: PHASE_COLORS.act,
  },
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
export const DIMENSION_CONFIG: Record<DimensionType, { label: string; description: string }> = {
  GEOGRAPHIC: {
    label: 'Geographic',
    description: 'Where are they from? Local community context.',
  },
  IDENTITY_WHY: {
    label: 'Identity WHY',
    description: 'What personal experience drives this interest?',
  },
  FIELD_GAP: {
    label: 'Field Gap',
    description: 'What gap in the field are they addressing?',
  },
  CATALYST: {
    label: 'Catalyst',
    description: 'What specific moment sparked this journey?',
  },
  TARGET_AUDIENCE: {
    label: 'Target Audience',
    description: 'Who specifically are they helping?',
  },
  UNIQUE_CONTRIBUTION: {
    label: 'Unique Contribution',
    description: 'What can only THEY contribute?',
  },
  REPRESENTATION: {
    label: 'Representation',
    description: 'How do they represent underserved perspectives?',
  },
  CULTURAL_DEPTH: {
    label: 'Cultural Depth',
    description: 'How does heritage shape their approach?',
  },
  TEMPORAL: {
    label: 'Temporal',
    description: 'Why is this the right time for this work?',
  },
  PROBLEM_SPECIFICITY: {
    label: 'Problem Specificity',
    description: 'How precisely is the problem defined?',
  },
} as const;
