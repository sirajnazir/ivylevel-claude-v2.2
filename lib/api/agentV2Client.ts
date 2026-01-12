/**
 * IvyQuest v2.0 Agent API Client
 * Connects to the v2.0 backend endpoints
 */

const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8000';

// ============================================================
// TYPE DEFINITIONS
// ============================================================

export interface TimeAuditInput {
  sleep_hours?: number;
  school_hours?: number;
  commute_minutes?: number;
  religious_hours?: number;
  misc_hours?: number;
  social_media_hours?: number;
  fixed_commitments?: number;
}

export interface TimeAuditResult {
  success: boolean;
  audit: {
    total_hours: number;
    fixed_allocations: {
      sleep: number;
      school: number;
      transport: number;
      misc: number;
      religious: number;
      total: number;
    };
    social_media: {
      current_weekly: number;
      target_weekly: number;
      hours_recovered: number;
    };
    passion_hours_available: number;
    daily_passion_hours: number;
    homework_hours: number;
  };
  walkthrough_script: string;
  efficiency_hacks: Array<{
    hack: string;
    description: string;
    benefit?: string;
    jenny_quote?: string;
  }>;
}

export interface WeeklyPlanInput {
  profile_id: string;
  tasks: Array<{
    id: string;
    name: string;
    priority: 'P0' | 'P1' | 'P2';
    estimated_hours: number;
    deadline?: string;
    category: string;
  }>;
  available_hours?: number;
}

export interface WeeklyPlanResult {
  success: boolean;
  plan: {
    week_start: string;
    p0_must_complete: Array<{ name: string; estimated_hours: number }>;
    p1_should_complete: Array<{ name: string; estimated_hours: number }>;
    p2_if_time_permits: Array<{ name: string; estimated_hours: number }>;
    total_hours_estimated: number;
    available_hours: number;
    buffer_hours: number;
    flexibility_note: string;
  };
  formatted_plan: string;
}

export interface AwardProbability {
  award_id: string;
  award_name: string;
  probability: number;
  tier: 'likely' | 'target' | 'stretch';
  fit_score: number;
  competition_factor: number;
  vulnerability_bonus: boolean;
  identity_bonus: boolean;
  reasoning: string;
}

export interface AwardsPortfolioInput {
  profile_id: string;
  awards?: Array<Record<string, unknown>>;
}

export interface AwardsPortfolioResult {
  success: boolean;
  portfolio: {
    likely: AwardProbability[];
    target: AwardProbability[];
    stretch: AwardProbability[];
  };
  expected_wins: number;
  balance_score: number;
  recommendations: string[];
  formatted_summary: string;
}

export interface NCWITStrategyInput {
  profile_id: string;
  student_data?: {
    identity?: string[];
    experiences?: string[];
    spike?: string;
    is_first_gen?: boolean;
    is_new_to_school?: boolean;
  };
}

export interface NCWITStrategyResult {
  success: boolean;
  strategy: {
    identity_layers: string[];
    identity_multiplier_text: string;
    vulnerability_angles: string[];
    sensory_detail_suggestions: string[];
    jenny_coaching_script: string;
    essay_structure: {
      question_1: {
        prompt: string;
        word_limit: number;
        strategy: string;
        structure: string[];
      };
      question_2: {
        prompt: string;
        word_limit: number;
        strategy: string;
      };
    };
  };
  vulnerability_formula: string;
}

export interface ProgramRecommendInput {
  student_profile: {
    spike?: string;
    primary_project?: string;
  };
  program?: {
    name: string;
    cost_numeric: number;
    category?: string;
    duration?: string;
  };
}

export interface ProgramRecommendResult {
  success: boolean;
  redirect: boolean;
  redirect_response?: {
    should_redirect: boolean;
    program_name: string;
    program_cost: number;
    redirect_text: string;
    free_alternatives: string[];
    self_directed_option: string;
    jenny_quote: string;
  };
  recommendations?: {
    tier_1_selective_free: Array<{ name: string; fit: string; jenny_note?: string }>;
    tier_2_government: Array<{ name: string; fit: string; jenny_note?: string }>;
    tier_3_technical: Array<{ name: string; fit: string; jenny_note?: string }>;
    tier_4_redirect: Array<{ name: string; fit: string; jenny_note?: string }>;
  };
}

export interface CrisisAlchemyInput {
  profile_id: string;
  crisis_description: string;
  student_data?: {
    spike?: string;
    primary_project?: string;
  };
}

// Narrative Synthesis
export interface NarrativeSynthesisInput {
  profile_id: string;
  assessment_contract?: Record<string, unknown>;
}

export interface NarrativeSynthesisResult {
  success: boolean;
  brand_statement: string;
  narrative_dna: string;
  first_principle: string;
  themes: string[];
  identity_seeds: string[];
  archetype: string;
  archetype_description: string;
  confidence: number;
}

export interface CrisisAlchemyResult {
  success: boolean;
  crisis_type: string;
  response: {
    validation: string;
    micro_action: string;
    reframe: string;
    pivot_activity: {
      name: string;
      description: string;
      steps: string[];
      impact: string;
    };
  };
  transformation: {
    from: string;
    to: string;
  };
  full_response: string;
}

export interface JennyVoiceInput {
  text: string;
}

export interface JennyVoiceResult {
  success: boolean;
  passed: boolean;
  score: number;
  excellence: boolean;
  dimension_scores: {
    forbidden_absence: number;
    warmth_first: number;
    agency_preservation: number;
    checkin_question: number;
    speech_patterns: number;
    exclamation_calibration: number;
  };
  issues: string[];
  forbidden_phrases_found: string[];
}

export interface HealthCheckResult {
  status: string;
  version: string;
  agents_enabled: boolean;
}

// ============================================================
// API CLIENT CLASS
// ============================================================

class AgentV2Client {
  private baseUrl: string;

  constructor(baseUrl: string = AGENT_API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    method: 'GET' | 'POST',
    path: string,
    data?: Record<string, unknown>
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;

    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (data && method === 'POST') {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to agent service. Is the backend running?');
      }
      throw error;
    }
  }

  // ============================================================
  // HEALTH & STATUS
  // ============================================================

  async checkHealth(): Promise<HealthCheckResult> {
    return this.request('GET', '/health');
  }

  async getJennyTechniques(): Promise<{ techniques: Array<{ name: string; description: string }> }> {
    return this.request('GET', '/agents/jenny-techniques');
  }

  // ============================================================
  // TIME MANAGEMENT (168-Hour Framework)
  // ============================================================

  async runTimeAudit(input: TimeAuditInput): Promise<TimeAuditResult> {
    return this.request('POST', '/agents/time-audit', input as Record<string, unknown>);
  }

  async generateWeeklyPlan(input: WeeklyPlanInput): Promise<WeeklyPlanResult> {
    return this.request('POST', '/agents/weekly-plan', input as Record<string, unknown>);
  }

  // ============================================================
  // AWARDS (2-2-1 Portfolio)
  // ============================================================

  async buildAwardsPortfolio(input: AwardsPortfolioInput): Promise<AwardsPortfolioResult> {
    return this.request('POST', '/agents/awards/portfolio', input as Record<string, unknown>);
  }

  // ============================================================
  // NCWIT STRATEGY
  // ============================================================

  async getNCWITStrategy(input: NCWITStrategyInput): Promise<NCWITStrategyResult> {
    return this.request('POST', '/agents/ncwit-strategy', input as Record<string, unknown>);
  }

  // ============================================================
  // OPPORTUNITY RECOMMENDATIONS
  // ============================================================

  async recommendOpportunities(input: ProgramRecommendInput): Promise<ProgramRecommendResult> {
    return this.request('POST', '/agents/opportunities/recommend', input as Record<string, unknown>);
  }

  // ============================================================
  // CRISIS ALCHEMY
  // ============================================================

  async handleCrisis(input: CrisisAlchemyInput): Promise<CrisisAlchemyResult> {
    return this.request('POST', '/agents/crisis-alchemy', input as Record<string, unknown>);
  }

  // ============================================================
  // JENNY VOICE VALIDATION
  // ============================================================

  async validateVoice(input: JennyVoiceInput): Promise<JennyVoiceResult> {
    return this.request('POST', '/validation/jenny-voice', input as Record<string, unknown>);
  }

  // ============================================================
  // NARRATIVE SYNTHESIS
  // ============================================================

  async synthesizeNarrative(input: NarrativeSynthesisInput): Promise<NarrativeSynthesisResult> {
    return this.request('POST', '/agents/narrative/synthesize', input as Record<string, unknown>);
  }
}

// ============================================================
// SINGLETON EXPORT
// ============================================================

export const agentV2Api = new AgentV2Client();
export default agentV2Api;
