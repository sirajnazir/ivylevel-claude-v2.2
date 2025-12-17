/**
 * IvyQuest v3.0 — Frame 3: Operating Types
 *
 * TypeScript type definitions for Frame 3.
 * Defines data structures, signals, and component props.
 *
 * @version 1.0.0
 * @module lib/types/frame3.types
 */

import type {
  ScenarioId,
  ScenarioResponse,
  OperatingStyle,
  TimeBandId,
  ProductivityId,
  EnergyPattern,
  HiddenCapability,
  StrengthProfile,
} from '../constants/frame3.constants';

// ============================================================================
// SCENARIO RESPONSES
// ============================================================================

export interface ScenarioResponses {
  deadline_crunch: 'systematic' | 'adaptive' | null;
  free_saturday: 'social' | 'solo' | null;
  new_opportunity: 'cautious' | 'bold' | null;
}

// ============================================================================
// CORE DATA INTERFACES
// ============================================================================

/**
 * Raw user input data from Frame 3
 */
export interface Frame3Data {
  // Card 1: Scenarios
  scenarioResponses: ScenarioResponses;

  // Card 2: Time & Energy
  weeklyAvailableHours: TimeBandId | null;
  peakProductivity: ProductivityId | null;
  energySource: number; // 0-1 scale (0 = people, 1 = ideas)

  // Card 3: Hidden Capabilities
  hiddenCapabilities: HiddenCapability[];
}

// ============================================================================
// HIDDEN STRENGTHS SIGNAL
// ============================================================================

export interface HiddenStrengthsSignal {
  capabilities: HiddenCapability[];
  boosterAffinities: string[];
  strengthProfile: StrengthProfile;
}

// ============================================================================
// AURA STATE
// ============================================================================

export interface AuraState {
  color: string;
  intensity: number;
  pulseSpeed: 'slow' | 'medium' | 'fast' | 'brilliant';
  glowRadius: number;
  isCalibrated: boolean;
}

// ============================================================================
// DERIVED SIGNALS
// ============================================================================

/**
 * Calculated signals derived from Frame 3 data
 */
export interface Frame3Signals {
  // Operating Style (from Card 1)
  operatingStyle: OperatingStyle;
  stressResponse: 'systematic' | 'adaptive' | null;
  socialEnergy: 'social' | 'solo' | null;
  riskTolerance: 'cautious' | 'bold' | null;

  // Time & Energy (from Card 2)
  timeCapacity: number; // 0-1
  productivityPattern: ProductivityId | null;
  energyPattern: EnergyPattern;

  // Hidden Capabilities (from Card 3)
  hiddenStrengths: HiddenStrengthsSignal;
  strengthProfile: StrengthProfile;
  boosterAffinities: string[];

  // Aura
  aura: AuraState;

  // Composite
  readinessScore: number; // 0-100

  // Metadata
  isComplete: boolean;
  completedAt: string | null;
}

// ============================================================================
// VALIDATION TYPES
// ============================================================================

export interface Card1Validation {
  isValid: boolean;
  scenariosAnswered: number;
  minRequired: number;
  missingScenarios: ScenarioId[];
}

export interface Card2Validation {
  isValid: boolean;
  missingFields: string[];
}

export interface Card3Validation {
  isValid: boolean;
  capabilitiesSelected: number;
  minRequired: number;
  maxAllowed: number;
}

export interface Frame3Validation {
  card1: Card1Validation;
  card2: Card2Validation;
  card3: Card3Validation;
  isFrameComplete: boolean;
}

// ============================================================================
// STORE SLICE
// ============================================================================

export interface Frame3StoreSlice {
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
// COMPONENT PROPS
// ============================================================================

export interface Frame3Props {
  onComplete: () => void;
  onBack?: () => void;
  targetSchools?: string[];
  aptitudeScore?: number;
  passionScore?: number;
  communityScore?: number;
}

export interface Card1Props {
  scenarioResponses: ScenarioResponses;
  onScenarioSelect: (scenarioId: ScenarioId, response: string) => void;
  onContinue: () => void;
  onBack: () => void;
  validation: Card1Validation;
}

export interface Card2Props {
  weeklyHours: TimeBandId | null;
  peakProductivity: ProductivityId | null;
  energySource: number;
  onWeeklyHoursSelect: (hours: TimeBandId) => void;
  onProductivitySelect: (productivity: ProductivityId) => void;
  onEnergyChange: (value: number) => void;
  onContinue: () => void;
  onBack: () => void;
  validation: Card2Validation;
}

export interface Card3Props {
  hiddenCapabilities: HiddenCapability[];
  onCapabilityToggle: (capability: HiddenCapability) => void;
  onComplete: () => void;
  onBack: () => void;
  validation: Card3Validation;
}

// ============================================================================
// HUD PROPS
// ============================================================================

export interface Frame3HUDProps {
  aptitudeScore: number;
  passionScore: number;
  communityScore: number;
  aura: AuraState;
  currentCard: number;
  totalCards: number;
}

// ============================================================================
// PROGRESS TYPES
// ============================================================================

export interface Frame3Progress {
  card1Complete: boolean;
  card2Complete: boolean;
  card3Complete: boolean;
  overallProgress: number; // 0-100
}

// ============================================================================
// ANIMATION TYPES
// ============================================================================

export interface AnimationState {
  isTransitioning: boolean;
  direction: 'forward' | 'backward';
  currentCard: number;
  targetCard: number;
}

export interface AuraAnimationConfig {
  color: string;
  intensity: number;
  pulseSpeed: 'slow' | 'medium' | 'fast' | 'brilliant';
  glowRadius: number;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type Frame3Field = keyof Frame3Data;
export type Frame3Signal = keyof Frame3Signals;

// ============================================================================
// RE-EXPORTS
// ============================================================================

export type {
  ScenarioId,
  ScenarioResponse,
  OperatingStyle,
  TimeBandId,
  ProductivityId,
  EnergyPattern,
  HiddenCapability,
  StrengthProfile,
};
