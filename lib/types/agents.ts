// IvyQuest Agent Type Definitions
// File: lib/types/agents.ts

export interface NarrativeDNA {
  dna: string;
  themes: string[];
  confidence: number;
  rationale: string;
  identity_markers?: string[];
}

export interface Archetype {
  id: string;
  label: string;
  confidence: number;
  rationale: string;
  secondary_archetype?: string;
}

export interface ConstraintReframe {
  constraint: string;
  reframed_as: string;
  narrative_angle: string;
  rubric_score: number;
}

export interface AssessmentResult {
  success: boolean;
  narrative_dna: NarrativeDNA;
  archetype: Archetype;
  cri: number;
  hidden_probabilities: Record<string, number>;
  hidden_target: string | null;
  constraint_reframes: ConstraintReframe[];
  requires_handoff: boolean;
}

export interface Activity {
  name: string;
  description: string;
  category: string;
  touchpoints: string[];
  touchpoint_count: number;
  prestige_score: number;
  hours_required: number;
  roi: number;
  narrative_alignment: number;
  narrative_thread?: string;
  recommended: boolean;
  rationale: string;
  is_stretch?: boolean;
}

export interface SeedAction {
  action: string;
  timeframe: string;
  completion_criteria: string;
  narrative_connection: string;
}

export interface IdentitySeed {
  id: string;
  target: string;
  target_type: string;
  plant_date: string;
  bloom_date: string;
  months_until_bloom: number;
  actions: SeedAction[];
  status: 'planned' | 'active' | 'completed';
  narrative_connection: string;
}

export interface Phase {
  name: string;
  duration: string;
  focus: string;
  activities: Activity[];
  activity_count: number;
}

export interface GamePlanResult {
  success: boolean;
  game_plan: {
    profile_id: string;
    narrative_dna: string;
    hidden_target: string | null;
    activities: Activity[];
    identity_seeds: IdentitySeed[];
    phases: Phase[];
    summary: {
      total_activities: number;
      total_touchpoints: number;
      average_roi: number;
      expected_completion_rate: number;
    };
    created_at: string;
  };
  requires_handoff: boolean;
}

export interface Microstep {
  id: string;
  title: string;
  description: string;
  estimated_minutes: number;
  dependencies: string[];
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  due_date?: string;
}

export interface CrisisResponse {
  success: boolean;
  crisis_id: string;
  steps: {
    validate: { message: string; emotion_acknowledged: boolean };
    act: { action: string; time_required: string };
    reframe: { opportunity: string; new_perspective: string };
    create: { new_activity: string; connection_to_narrative: string };
  };
  requires_handoff: boolean;
  handoff_reason?: string;
}

export interface ExecutionDebtScore {
  profile_id: string;
  execution_debt_score: number;
  status: 'healthy' | 'at_risk' | 'critical';
  threshold: number;
  contributing_factors?: string[];
}

export interface AwardMatch {
  award_id: string;
  name: string;
  category: string;
  level: string;
  deadline: string;
  win_probability: number;
  roi: number;
  effort_hours: number;
  prestige_score: number;
  fit_reasons: string[];
  months_until_deadline: number;
}

export interface AwardPortfolio {
  likely: AwardMatch[];
  target: AwardMatch[];
  stretch: AwardMatch[];
  total_recommended: number;
  expected_wins: number;
  total_effort_hours: number;
  strategy_notes: string[];
}

export interface OpportunityMatch {
  opportunity_id: string;
  name: string;
  type: string;
  organization: string;
  deadline: string;
  fit_score: number;
  prestige_score: number;
  selectivity: number;
  fit_reasons: string[];
  months_until_deadline: number;
  touchpoints: number;
}

export interface OpportunityAlert {
  alert_id: string;
  type: 'OPPORTUNITY_ALERT' | 'URGENT_DEADLINE';
  opportunity_id: string;
  opportunity_name: string;
  organization?: string;
  deadline: string;
  months_remaining: number;
  fit_score?: number;
  urgency: 'PREPARE_NOW' | 'URGENT';
  recommended_actions: string[];
  prep_start_date?: string;
  created_at: string;
}

export interface BackupCascade {
  primary: { id: string; name: string; fit_score: number; deadline: string };
  backups: Array<{ id: string; name: string; fit_score: number; deadline: string; priority: number }>;
  auto_failover: boolean;
  failover_strategy: string;
  notes: string[];
}

export interface OpportunityTimelineItem {
  opportunity_name: string;
  organization: string;
  type: string;
  deadline: string;
  months_until: number;
  prep_start_date: string;
  fit_score: number;
  status: 'future' | 'prepare_now' | 'approaching' | 'imminent' | 'urgent' | 'passed';
}

export interface MicroEditChange {
  original: string;
  replacement: string;
  category: string;
  explanation: string;
  position?: number;
}

export interface MicroEditResult {
  original: string;
  edited: string;
  change_count: number;
  categories_affected: string[];
  changes?: MicroEditChange[];
}

export interface EssayAnalysis {
  word_count: number;
  total_issues: number;
  issues_by_category: Record<string, number>;
  language_score: number;
  recommendations: string[];
  can_improve: boolean;
  sample_changes?: MicroEditChange[];
}

export interface AgentHealthResponse {
  status: string;
  version: string;
  agents_enabled: boolean;
}
