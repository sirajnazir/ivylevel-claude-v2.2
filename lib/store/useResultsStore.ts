/**
 * Results Store (Zustand)
 * Caches scoring results and twin fleet data
 *
 * v1.1.0 - Added Strategic Intelligence fields
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type {
  AssessmentResults,
  IvyReadyScore,
  SchoolProbability,
  Booster,
  BoosterRecommendations,
  TwinFleet,
  DigitalTwin,
  ArchetypeID,
} from '../types/student';

// Narrative Synthesis result type
interface NarrativeSynthesis {
  brand_statement: string;
  narrative_dna: string;
  first_principle: string;
  themes: string[];
  confidence: number;
  synthesis_inputs?: {
    identity: Record<string, unknown>;
    aptitude: Record<string, unknown>;
    passion: Record<string, unknown>;
    service: Record<string, unknown>;
  };
}

// ============================================
// Strategic Intelligence Types (v1.1.0)
// ============================================

export type Archetype =
  | 'academic_powerhouse'
  | 'stem_innovator'
  | 'creative_visionary'
  | 'community_changemaker'
  | 'entrepreneurial_leader'
  | 'humanities_scholar'
  | 'athletic_scholar'
  | 'multi_hyphenate';

export interface IdentitySynthesis {
  spike: string;
  archetype: Archetype;
  archetype_confidence: number;
  pillars: string[];
  narrative_hook: string;
  differentiation_summary: string;
  portfolio_balance_score?: number;
}

export interface PortfolioAudit {
  diagnosis: 'COMPETITIVE' | 'NEEDS_VALIDATION' | 'WEAK' | 'UNDERDEVELOPED';
  score: number;
  tier_summary: {
    T1: number;
    T2: number;
    T3: number;
    T4: number;
  };
  gaps: string[];
}

export interface AwardMatch {
  award_id: string;
  name: string;
  strategic_tier: number;
  fit_score: number;
  archetype_alignment: number;
  identity_alignment: number;
  win_probability: number;
  portfolio_role: 'reach' | 'target' | 'safety';
  rationale: string;
  success_patterns: string[];
  common_mistakes: string[];
  differentiation_factor: string;
}

export interface ProgramMatch {
  program_id: string;
  name: string;
  organization: string;
  strategic_tier: number;
  fit_score: number;
  archetype_alignment: number;
  acceptance_probability: number;
  rationale: string;
  success_patterns: string[];
  hidden_value: string[];
}

export interface AwardsPortfolio {
  reach: AwardMatch[];
  target: AwardMatch[];
  safety: AwardMatch[];
}

export interface ProgramsPortfolio {
  primary: ProgramMatch[];
  alternatives: ProgramMatch[];
}

export interface PriorityAction {
  type: string;
  priority: 'high' | 'medium' | 'low';
  action: string;
  rationale: string;
}

export interface TimelineItem {
  type: 'award' | 'program';
  name: string;
  deadline_month: number;
  priority: string;
}

// GamePlan API response shape (for setGamePlanResults)
export interface GamePlanApiResponse {
  identity?: {
    synthesis?: IdentitySynthesis;
    portfolio_audit?: PortfolioAudit;
  };
  awards?: {
    portfolio?: AwardsPortfolio;
  };
  programs?: {
    portfolio?: ProgramsPortfolio;
  };
  priority_actions?: PriorityAction[];
  unified_timeline?: TimelineItem[];
}

interface ResultsStoreState {
  // Scoring results
  results: AssessmentResults | null;
  ivy_score: IvyReadyScore | null;
  school_probabilities: SchoolProbability[];
  helping_factors: string[];
  holding_back_factors: string[];
  archetype: ArchetypeID | null;
  archetype_label: string;
  narrative_tagline: string;

  // Narrative Synthesis (Jenny's Formula)
  narrative: NarrativeSynthesis | null;
  brand_statement: string;
  narrative_dna: string;
  first_principle: string;
  narrative_themes: string[];
  narrative_confidence: number;

  // Strategic Intelligence (v1.1.0)
  identity_synthesis: IdentitySynthesis | null;
  portfolio_audit: PortfolioAudit | null;
  awards_portfolio: AwardsPortfolio | null;
  programs_portfolio: ProgramsPortfolio | null;
  priority_actions: PriorityAction[];
  unified_timeline: TimelineItem[];

  // Boosters
  booster_recommendations: BoosterRecommendations | null;
  top_3_boosters: Booster[];
  all_boosters: Booster[];

  // Twin Fleet
  twin_fleet: TwinFleet | null;
  base_twin: DigitalTwin | null;
  school_twins: DigitalTwin[];

  // Meta
  scored_at: string | null;
  narrative_synthesized_at: string | null;
  is_stale: boolean;

  // Actions
  setResults: (results: AssessmentResults) => void;
  setNarrative: (narrative: NarrativeSynthesis) => void;
  setGamePlanResults: (results: GamePlanApiResponse) => void;
  setBoosters: (boosters: BoosterRecommendations) => void;
  setTwinFleet: (fleet: TwinFleet) => void;
  markStale: () => void;
  clearResults: () => void;
  getSchoolProbability: (schoolId: string) => SchoolProbability | null;
  getTopSchool: () => SchoolProbability | null;
}

export const useResultsStore = create<ResultsStoreState>()(
  devtools(
    persist(
      immer((set, get) => ({
        results: null,
        ivy_score: null,
        school_probabilities: [],
        helping_factors: [],
        holding_back_factors: [],
        archetype: null,
        archetype_label: '',
        narrative_tagline: '',
        // Narrative Synthesis (Jenny's Formula)
        narrative: null,
        brand_statement: '',
        narrative_dna: '',
        first_principle: '',
        narrative_themes: [],
        narrative_confidence: 0,
        // Strategic Intelligence (v1.1.0)
        identity_synthesis: null,
        portfolio_audit: null,
        awards_portfolio: null,
        programs_portfolio: null,
        priority_actions: [],
        unified_timeline: [],
        // Other
        booster_recommendations: null,
        top_3_boosters: [],
        all_boosters: [],
        twin_fleet: null,
        base_twin: null,
        school_twins: [],
        scored_at: null,
        narrative_synthesized_at: null,
        is_stale: false,

        setResults: (results) =>
          set((state) => {
            state.results = results;
            state.ivy_score = results.ivy_ready_score;
            state.school_probabilities = results.school_probabilities;
            state.helping_factors = results.helping_factors;
            state.holding_back_factors = results.holding_back_factors;
            state.archetype = results.archetype_detected as ArchetypeID;
            state.archetype_label = results.archetype_label;
            state.narrative_tagline = results.narrative_tagline;
            state.scored_at = new Date().toISOString();
            state.is_stale = false;
          }),

        setNarrative: (narrative) =>
          set((state) => {
            state.narrative = narrative;
            state.brand_statement = narrative.brand_statement;
            state.narrative_dna = narrative.narrative_dna;
            state.first_principle = narrative.first_principle;
            state.narrative_themes = narrative.themes;
            state.narrative_confidence = narrative.confidence;
            state.narrative_synthesized_at = new Date().toISOString();
          }),

        // Set GamePlan results with Strategic Intelligence (v1.1.0)
        setGamePlanResults: (results) =>
          set((state) => {
            // Map identity synthesis from EC Agent
            if (results.identity?.synthesis) {
              state.identity_synthesis = results.identity.synthesis as IdentitySynthesis;
            }
            // Map portfolio audit from EC Agent
            if (results.identity?.portfolio_audit) {
              state.portfolio_audit = results.identity.portfolio_audit as PortfolioAudit;
            }
            // Map awards portfolio from Awards Agent
            if (results.awards?.portfolio) {
              state.awards_portfolio = results.awards.portfolio as AwardsPortfolio;
            }
            // Map programs portfolio from Programs Agent
            if (results.programs?.portfolio) {
              state.programs_portfolio = results.programs.portfolio as ProgramsPortfolio;
            }
            // Map priority actions
            if (results.priority_actions) {
              state.priority_actions = results.priority_actions as PriorityAction[];
            }
            // Map unified timeline
            if (results.unified_timeline) {
              state.unified_timeline = results.unified_timeline as TimelineItem[];
            }
          }),

        setBoosters: (boosters) =>
          set((state) => {
            state.booster_recommendations = boosters;
            state.top_3_boosters = boosters.top_3_boosters;
            state.all_boosters = boosters.all_eligible_boosters;
          }),

        setTwinFleet: (fleet) =>
          set((state) => {
            state.twin_fleet = fleet;
            state.base_twin = fleet.base_twin;
            state.school_twins = fleet.school_twins;
          }),

        markStale: () =>
          set((state) => {
            state.is_stale = true;
          }),

        clearResults: () =>
          set((state) => {
            state.results = null;
            state.ivy_score = null;
            state.school_probabilities = [];
            state.helping_factors = [];
            state.holding_back_factors = [];
            state.archetype = null;
            state.archetype_label = '';
            state.narrative_tagline = '';
            // Clear narrative
            state.narrative = null;
            state.brand_statement = '';
            state.narrative_dna = '';
            state.first_principle = '';
            state.narrative_themes = [];
            state.narrative_confidence = 0;
            state.narrative_synthesized_at = null;
            // Clear strategic intelligence (v1.1.0)
            state.identity_synthesis = null;
            state.portfolio_audit = null;
            state.awards_portfolio = null;
            state.programs_portfolio = null;
            state.priority_actions = [];
            state.unified_timeline = [];
            // Clear others
            state.booster_recommendations = null;
            state.top_3_boosters = [];
            state.all_boosters = [];
            state.twin_fleet = null;
            state.base_twin = null;
            state.school_twins = [];
            state.scored_at = null;
            state.is_stale = false;
          }),

        getSchoolProbability: (schoolId) => {
          const state = get();
          return state.school_probabilities.find((s) => s.school_id === schoolId) || null;
        },

        getTopSchool: () => {
          const state = get();
          if (state.school_probabilities.length === 0) return null;
          return state.school_probabilities.reduce((best, current) =>
            current.p_final > best.p_final ? current : best
          );
        },
      })),
      {
        name: 'ivyquest-results',
        partialize: (state) => ({
          results: state.results,
          narrative: state.narrative,
          booster_recommendations: state.booster_recommendations,
          twin_fleet: state.twin_fleet,
          scored_at: state.scored_at,
          narrative_synthesized_at: state.narrative_synthesized_at,
        }),
      }
    ),
    { name: 'ResultsStore' }
  )
);
