/**
 * Results Store (Zustand)
 * Caches scoring results and twin fleet data
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
