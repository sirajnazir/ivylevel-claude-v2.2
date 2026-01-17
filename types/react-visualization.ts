/**
 * ReAct Visualization Types v5.0
 * ===============================
 *
 * TypeScript types for the ReAct cycle visualization components.
 * These types mirror the backend _react metadata structure from react_wrapper.py
 */

// Phase data types for each step of the ReAct cycle

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

export interface ToolExecution {
  name: string;
  duration_ms?: number;
  success: boolean;
}

export interface ActPhaseData {
  action: string;
  tools_executed: ToolExecution[];
  hints_applied: number;
  input_summary: Record<string, unknown>;
  output_summary: Record<string, unknown>;
  duration_ms: number;
}

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

export interface LearnPhaseData {
  reasoning: string;
  what_worked: string[];
  what_failed: string[];
  quality_delta: number;
  corrections_to_apply: string[];
  should_continue: boolean;
}

export interface CycleSummary {
  cycle: number;
  think: ThinkPhaseData;
  act: ActPhaseData;
  observe: ObservePhaseData;
  learn: LearnPhaseData;
  duration_ms: number;
  quality_score?: number;  // For backwards compatibility
}

export interface InputDataFlow {
  from_profile?: Record<string, unknown>;
  from_assessment?: Record<string, unknown>;
  from_ec_agent?: Record<string, unknown>;
  to_awards_agent?: Record<string, unknown>;
  to_programs_agent?: Record<string, unknown>;
  to_downstream_agents?: Record<string, unknown>;
}

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
}

// Phase types for UI
export type PhaseType = 'think' | 'act' | 'observe' | 'learn';

// Phase configuration for consistent styling
export interface PhaseConfig {
  key: PhaseType;
  title: string;
  icon: string; // Lucide icon name
  color: string;
  bgColor: string;
}

// Phase color configuration
export const PHASE_COLORS: Record<PhaseType, { color: string; bgColor: string }> = {
  think: { color: '#FF4A23', bgColor: 'rgba(255, 74, 35, 0.1)' },  // Orange
  act: { color: '#3B82F6', bgColor: 'rgba(59, 130, 246, 0.1)' },    // Blue
  observe: { color: '#7C3AED', bgColor: 'rgba(124, 58, 237, 0.1)' }, // Purple
  learn: { color: '#1DBF73', bgColor: 'rgba(29, 191, 115, 0.1)' },   // Green
} as const;

// Helper type for extracting phase data from cycle summary
export type PhaseData<T extends PhaseType> =
  T extends 'think' ? ThinkPhaseData :
  T extends 'act' ? ActPhaseData :
  T extends 'observe' ? ObservePhaseData :
  T extends 'learn' ? LearnPhaseData :
  never;
