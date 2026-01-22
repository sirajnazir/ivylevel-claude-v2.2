/**
 * IvyQuest v3.0 — Frame 3: Operating Store
 *
 * Zustand store for Frame 3 state management.
 * Uses immer for immutable updates.
 *
 * @version 1.0.0
 * @module lib/store/useFrame3Store
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type {
  Frame3Data,
  Frame3Signals,
  Frame3Validation,
  ScenarioResponses,
  HiddenStrengthsSignal,
  AuraState,
  Card1Validation,
  Card2Validation,
  Card3Validation,
} from '../types/frame3.types';
import {
  SCENARIO_IDS,
  TIME_BANDS,
  ENERGY_PATTERN_THRESHOLDS,
  HIDDEN_CAPABILITIES,
  AURA_CONFIG,
  VALIDATION_RULES,
  READINESS_WEIGHTS,
} from '../constants/frame3.constants';
import type {
  ScenarioId,
  OperatingStyle,
  EnergyPattern,
  HiddenCapability,
  StrengthProfile,
  TimeBandId,
  ProductivityId,
} from '../constants/frame3.constants';

// ============================================================================
// TRACE LOGGING UTILITY
// ============================================================================

const trace = {
  log: (category: string, message: string) => {
    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
      console.log(`[${category}] ${message}`);
    }
  },
};

// ============================================================================
// INITIAL STATE
// ============================================================================

const initialFrame3Data: Frame3Data = {
  scenarioResponses: {
    deadline_crunch: null,
    free_saturday: null,
    new_opportunity: null,
  },
  weeklyAvailableHours: null,
  peakProductivity: null,
  energySource: 0.5, // Default to center
  hiddenCapabilities: [],
};

const initialAuraState: AuraState = {
  color: '#06B6D4', // Cyan (balanced)
  intensity: 0,
  pulseSpeed: 'medium',
  glowRadius: 0,
  isCalibrated: false,
};

const initialFrame3Signals: Frame3Signals = {
  operatingStyle: 'balanced_operator',
  stressResponse: null,
  socialEnergy: null,
  riskTolerance: null,
  timeCapacity: 0,
  productivityPattern: null,
  energyPattern: 'balanced',
  hiddenStrengths: {
    capabilities: [],
    boosterAffinities: [],
    strengthProfile: 'versatile_generalist',
  },
  strengthProfile: 'versatile_generalist',
  boosterAffinities: [],
  aura: initialAuraState,
  readinessScore: 0,
  isComplete: false,
  completedAt: null,
};

const initialFrame3Validation: Frame3Validation = {
  card1: {
    isValid: false,
    scenariosAnswered: 0,
    minRequired: VALIDATION_RULES.card1.minScenariosAnswered,
    missingScenarios: [...SCENARIO_IDS],
  },
  card2: {
    isValid: false,
    missingFields: [...VALIDATION_RULES.card2.requiredFields],
  },
  card3: {
    isValid: false,
    capabilitiesSelected: 0,
    minRequired: VALIDATION_RULES.card3.minCapabilities,
    maxAllowed: VALIDATION_RULES.card3.maxCapabilities,
  },
  isFrameComplete: false,
};

// ============================================================================
// DERIVATION FUNCTIONS
// ============================================================================

/**
 * Derive operating style from scenario responses
 */
function deriveOperatingStyle(responses: ScenarioResponses): OperatingStyle {
  const { deadline_crunch, free_saturday, new_opportunity } = responses;

  // Count traits
  const isSystematic = deadline_crunch === 'systematic';
  const isAdaptive = deadline_crunch === 'adaptive';
  const isSocial = free_saturday === 'social';
  const isSolo = free_saturday === 'solo';
  const isCautious = new_opportunity === 'cautious';
  const isBold = new_opportunity === 'bold';

  // Determine dominant style
  if (isSystematic && isSolo && isCautious) {
    return 'methodical_builder';
  }
  if (isAdaptive && isSocial && isBold) {
    return 'dynamic_leader';
  }
  if (isSystematic && isSocial) {
    return 'organized_collaborator';
  }
  if (isAdaptive && isSolo) {
    return 'creative_innovator';
  }

  return 'balanced_operator';
}

/**
 * Calculate time capacity from band selection
 */
function calculateTimeCapacity(hours: TimeBandId | null): number {
  if (!hours) return 0;
  return TIME_BANDS[hours]?.score ?? 0;
}

/**
 * Derive energy pattern from spectrum value
 */
function deriveEnergyPattern(energy: number): EnergyPattern {
  for (const [pattern, [min, max]] of Object.entries(ENERGY_PATTERN_THRESHOLDS)) {
    if (energy >= min && energy <= max) {
      return pattern as EnergyPattern;
    }
  }
  return 'balanced';
}

/**
 * Determine strength profile from capabilities
 */
function determineStrengthProfile(capabilities: HiddenCapability[]): StrengthProfile {
  const technical = capabilities.filter((c) =>
    ['technical_build', 'data_analysis'].includes(c)
  ).length;
  const creative = capabilities.filter((c) =>
    ['creative_design', 'writing', 'idea_generation'].includes(c)
  ).length;
  const interpersonal = capabilities.filter((c) =>
    ['public_speaking', 'networking'].includes(c)
  ).length;

  if (technical >= 2) return 'technical_specialist';
  if (creative >= 2) return 'creative_innovator';
  if (interpersonal >= 2) return 'social_leader';
  return 'versatile_generalist';
}

/**
 * Derive hidden strengths signal
 */
function deriveHiddenStrengths(capabilities: HiddenCapability[]): HiddenStrengthsSignal {
  const affinities = capabilities.flatMap((cap) => {
    return HIDDEN_CAPABILITIES[cap]?.boosterAffinity ?? [];
  });

  const uniqueAffinities = Array.from(new Set(affinities));
  const strengthProfile = determineStrengthProfile(capabilities);

  return {
    capabilities,
    boosterAffinities: uniqueAffinities,
    strengthProfile,
  };
}

/**
 * Calculate aura state from signals
 */
function calculateAura(
  operatingStyle: OperatingStyle,
  energyPattern: EnergyPattern,
  card1Complete: boolean,
  card2Complete: boolean,
  card3Complete: boolean
): AuraState {
  const color = AURA_CONFIG.colors[operatingStyle];

  // Calculate intensity based on card completion
  let intensity = 0;
  if (card3Complete) {
    intensity = AURA_CONFIG.intensityStages.card3Complete[1];
  } else if (card2Complete) {
    intensity = AURA_CONFIG.intensityStages.card2Complete[1];
  } else if (card1Complete) {
    intensity = AURA_CONFIG.intensityStages.card1Complete[1];
  }

  const pulseSpeed = AURA_CONFIG.pulseSpeed[energyPattern];

  // Find appropriate glow radius
  const radiusKeys = Object.keys(AURA_CONFIG.glowRadius)
    .map(Number)
    .sort((a, b) => a - b);
  const radiusKey = radiusKeys.reduce(
    (prev, curr) => (intensity >= curr ? curr : prev),
    radiusKeys[0]
  );
  const glowRadius = AURA_CONFIG.glowRadius[radiusKey];

  return {
    color,
    intensity,
    pulseSpeed,
    glowRadius,
    isCalibrated: card3Complete,
  };
}

/**
 * Calculate readiness score
 */
function calculateReadinessScore(
  timeCapacity: number,
  operatingStyle: OperatingStyle,
  capabilitiesCount: number
): number {
  const timeScore = timeCapacity * READINESS_WEIGHTS.timeCapacity;

  const operatingClarity =
    operatingStyle !== 'balanced_operator'
      ? READINESS_WEIGHTS.operatingClarity.defined
      : READINESS_WEIGHTS.operatingClarity.balanced;

  const strengthScore =
    Math.min(capabilitiesCount, 3) * READINESS_WEIGHTS.strengthsPerCapability;

  return Math.round(timeScore + operatingClarity + strengthScore);
}

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

function validateCard1(responses: ScenarioResponses): Card1Validation {
  const answered = SCENARIO_IDS.filter((id) => responses[id] !== null);
  const missing = SCENARIO_IDS.filter((id) => responses[id] === null);

  return {
    isValid: answered.length >= VALIDATION_RULES.card1.minScenariosAnswered,
    scenariosAnswered: answered.length,
    minRequired: VALIDATION_RULES.card1.minScenariosAnswered,
    missingScenarios: missing,
  };
}

function validateCard2(data: Frame3Data): Card2Validation {
  const missingFields: string[] = [];

  if (!data.weeklyAvailableHours) missingFields.push('weeklyAvailableHours');
  if (!data.peakProductivity) missingFields.push('peakProductivity');
  // energySource has default, so always valid

  return {
    isValid: missingFields.length === 0,
    missingFields,
  };
}

function validateCard3(capabilities: HiddenCapability[]): Card3Validation {
  return {
    isValid: capabilities.length >= VALIDATION_RULES.card3.minCapabilities,
    capabilitiesSelected: capabilities.length,
    minRequired: VALIDATION_RULES.card3.minCapabilities,
    maxAllowed: VALIDATION_RULES.card3.maxCapabilities,
  };
}

// ============================================================================
// STORE TYPE
// ============================================================================

interface Frame3StoreState {
  // State
  frame3Data: Frame3Data;
  frame3Signals: Frame3Signals;
  frame3Validation: Frame3Validation;
  frame3CurrentCard: number;

  // Card 1 Actions
  setScenarioResponse: (scenarioId: ScenarioId, response: string) => void;
  clearScenarioResponse: (scenarioId: ScenarioId) => void;

  // Card 2 Actions
  setWeeklyHours: (hours: TimeBandId) => void;
  setPeakProductivity: (productivity: ProductivityId) => void;
  setEnergySource: (value: number) => void;

  // Card 3 Actions
  toggleHiddenCapability: (capability: HiddenCapability) => void;
  setHiddenCapabilities: (capabilities: HiddenCapability[]) => void;
  clearHiddenCapabilities: () => void;

  // Navigation
  setFrame3Card: (card: number) => void;
  nextFrame3Card: () => void;
  prevFrame3Card: () => void;

  // Calculations
  recalculateFrame3Signals: () => void;
  validateFrame3: () => Frame3Validation;

  // Lifecycle
  completeFrame3: () => void;
  resetFrame3: () => void;
}

// ============================================================================
// STORE CREATION
// ============================================================================

export const useFrame3Store = create<Frame3StoreState>()(
  devtools(
    persist(
      immer((set, get) => ({
        // State
        frame3Data: initialFrame3Data,
        frame3Signals: initialFrame3Signals,
        frame3Validation: initialFrame3Validation,
        frame3CurrentCard: 1,

        // Card 1 Actions
        setScenarioResponse: (scenarioId: ScenarioId, response: string) => {
          set((state) => {
            (state.frame3Data.scenarioResponses as Record<ScenarioId, string | null>)[
              scenarioId
            ] = response;
            trace.log('FRAME3.CARD1', `Scenario: ${scenarioId}, Response: ${response}`);
          });
          get().recalculateFrame3Signals();
        },

        clearScenarioResponse: (scenarioId: ScenarioId) => {
          set((state) => {
            (state.frame3Data.scenarioResponses as Record<ScenarioId, string | null>)[
              scenarioId
            ] = null;
          });
          get().recalculateFrame3Signals();
        },

        // Card 2 Actions
        setWeeklyHours: (hours: TimeBandId) => {
          set((state) => {
            state.frame3Data.weeklyAvailableHours = hours;
          });
          get().recalculateFrame3Signals();
        },

        setPeakProductivity: (productivity: ProductivityId) => {
          set((state) => {
            state.frame3Data.peakProductivity = productivity;
          });
          get().recalculateFrame3Signals();
        },

        setEnergySource: (value: number) => {
          const clampedValue = Math.max(0, Math.min(1, value));
          set((state) => {
            state.frame3Data.energySource = clampedValue;
          });
          get().recalculateFrame3Signals();
        },

        // Card 3 Actions
        toggleHiddenCapability: (capability: HiddenCapability) => {
          set((state) => {
            const index = state.frame3Data.hiddenCapabilities.indexOf(capability);
            if (index > -1) {
              // Remove
              state.frame3Data.hiddenCapabilities.splice(index, 1);
            } else if (
              state.frame3Data.hiddenCapabilities.length <
              VALIDATION_RULES.card3.maxCapabilities
            ) {
              // Add (if under max)
              state.frame3Data.hiddenCapabilities.push(capability);
            }
            trace.log(
              'FRAME3.CARD3',
              `Capabilities: ${state.frame3Data.hiddenCapabilities.join(', ')}`
            );
          });
          get().recalculateFrame3Signals();
        },

        setHiddenCapabilities: (capabilities: HiddenCapability[]) => {
          const limited = capabilities.slice(0, VALIDATION_RULES.card3.maxCapabilities);
          set((state) => {
            state.frame3Data.hiddenCapabilities = limited;
          });
          get().recalculateFrame3Signals();
        },

        clearHiddenCapabilities: () => {
          set((state) => {
            state.frame3Data.hiddenCapabilities = [];
          });
          get().recalculateFrame3Signals();
        },

        // Navigation
        setFrame3Card: (card: number) => {
          const clampedCard = Math.max(1, Math.min(6, card));
          set((state) => {
            state.frame3CurrentCard = clampedCard;
          });
        },

        nextFrame3Card: () => {
          const current = get().frame3CurrentCard;
          if (current < 6) {
            get().setFrame3Card(current + 1);
          }
        },

        prevFrame3Card: () => {
          const current = get().frame3CurrentCard;
          if (current > 1) {
            get().setFrame3Card(current - 1);
          }
        },

        // Calculations
        recalculateFrame3Signals: () => {
          const data = get().frame3Data;

          // Validate all cards
          const card1Validation = validateCard1(data.scenarioResponses);
          const card2Validation = validateCard2(data);
          const card3Validation = validateCard3(data.hiddenCapabilities);

          // Derive signals
          const operatingStyle = deriveOperatingStyle(data.scenarioResponses);
          const timeCapacity = calculateTimeCapacity(data.weeklyAvailableHours);
          const energyPattern = deriveEnergyPattern(data.energySource);
          const hiddenStrengths = deriveHiddenStrengths(data.hiddenCapabilities);

          // Calculate aura
          const aura = calculateAura(
            operatingStyle,
            energyPattern,
            card1Validation.isValid,
            card2Validation.isValid,
            card3Validation.isValid
          );

          // Calculate readiness score
          const readinessScore = calculateReadinessScore(
            timeCapacity,
            operatingStyle,
            data.hiddenCapabilities.length
          );

          const isComplete =
            card1Validation.isValid &&
            card2Validation.isValid &&
            card3Validation.isValid;

          set((state) => {
            state.frame3Signals = {
              operatingStyle,
              stressResponse: data.scenarioResponses.deadline_crunch,
              socialEnergy: data.scenarioResponses.free_saturday,
              riskTolerance: data.scenarioResponses.new_opportunity,
              timeCapacity,
              productivityPattern: data.peakProductivity,
              energyPattern,
              hiddenStrengths,
              strengthProfile: hiddenStrengths.strengthProfile,
              boosterAffinities: hiddenStrengths.boosterAffinities,
              aura,
              readinessScore,
              isComplete,
              completedAt:
                isComplete && !state.frame3Signals.completedAt
                  ? new Date().toISOString()
                  : state.frame3Signals.completedAt,
            };

            state.frame3Validation = {
              card1: card1Validation,
              card2: card2Validation,
              card3: card3Validation,
              isFrameComplete: isComplete,
            };
          });

          trace.log(
            'FRAME3.CARD2',
            `Time: ${data.weeklyAvailableHours}, Productivity: ${data.peakProductivity}, Energy: ${data.energySource}`
          );
        },

        validateFrame3: () => {
          const data = get().frame3Data;
          return {
            card1: validateCard1(data.scenarioResponses),
            card2: validateCard2(data),
            card3: validateCard3(data.hiddenCapabilities),
            isFrameComplete: get().frame3Signals.isComplete,
          };
        },

        // Lifecycle
        completeFrame3: () => {
          const signals = get().frame3Signals;
          if (signals.isComplete) {
            trace.log('FRAME3.COMPLETE', `Signals: ${JSON.stringify(signals)}`);
          }
        },

        resetFrame3: () => {
          set((state) => {
            state.frame3Data = initialFrame3Data;
            state.frame3Signals = initialFrame3Signals;
            state.frame3Validation = initialFrame3Validation;
            state.frame3CurrentCard = 1;
          });
        },
      })),
      {
        name: 'ivyquest-frame3-operating',
        partialize: (state) => ({
          frame3Data: state.frame3Data,
          frame3Signals: state.frame3Signals,
          frame3CurrentCard: state.frame3CurrentCard,
        }),
      }
    ),
    { name: 'Frame3Store' }
  )
);

// ============================================================================
// EXPORTS
// ============================================================================

export { initialFrame3Data, initialFrame3Signals, initialFrame3Validation };

export default useFrame3Store;
