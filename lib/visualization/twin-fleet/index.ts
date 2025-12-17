/**
 * IvyQuest v3.0 — Twin Fleet Package
 * 
 * 3D avatar visualization system with school-specific twins.
 * 
 * @version 1.0.0
 * @module @ivyquest/twin-fleet
 */

// ============================================================================
// AVATAR COMPONENTS
// ============================================================================

export {
  BaseTwin,
  TwinAura,
  TwinParticles,
} from './components/TwinAvatar';

// ============================================================================
// FLEET COMPONENTS
// ============================================================================

export {
  SchoolTwin,
  FleetDisplay,
} from './components/TwinFleet';

// ============================================================================
// COMMAND DECK
// ============================================================================

export {
  default as CommandDeck,
  DeckBackground,
  DeckHUD,
} from './components/CommandDeck';

// ============================================================================
// ANIMATIONS
// ============================================================================

export {
  MaterializeSequence,
  ScoreReveal,
  LaunchSequence,
} from './components/animations';

// ============================================================================
// CONSTANTS
// ============================================================================

export {
  SCORE_TIERS,
  SCHOOL_COLORS,
  OPERATING_STYLE_VISUALS,
  TWIN_SIZES,
  ANIMATION_TIMINGS,
  PARTICLE_CONFIG,
  AURA_CONFIG,
  FLEET_LAYOUTS,
  HUD_CONFIG,
  COMMAND_DECK_THEMES,
  type ScoreTierId,
  type SchoolId,
  type OperatingStyleId,
  type TwinSize,
  type FleetLayoutId,
} from './constants/twin.constants';

// ============================================================================
// UTILITIES
// ============================================================================

export {
  // Color utilities
  hexToRgb,
  rgbToHex,
  lerpColor,
  adjustBrightness,
  withAlpha,
  createGradient,
  
  // Tier utilities
  getTierFromScore,
  getTierConfig,
  getTierColors,
  getSchoolColors,
  blendTierAndSchoolColors,
  
  // Animation utilities
  lerp,
  clamp,
  easings,
  createAnimationCounter,
  staggerDelay,
  getAnimationPhase,
  
  // Position utilities
  calculateArcPositions,
  calculateGridPositions,
  calculateOrbitalPositions,
  
  // Particle utilities
  createParticle,
  updateParticle,
  
  // Probability utilities
  getProbabilityColor,
  getProbabilityLabel,
  formatProbability,
} from './utils/twinUtils';

// ============================================================================
// TYPES
// ============================================================================

export type {
  // Score types
  CategoryScores,
  TwinScoreState,
  
  // Avatar props
  BaseTwinProps,
  SchoolTwinProps,
  TwinAuraProps,
  TwinParticlesProps,
  
  // Fleet props
  SchoolTwinData,
  FleetDisplayProps,
  
  // Command deck props
  CommandDeckProps,
  DeckHUDProps,
  
  // Animation props
  MaterializeSequenceProps,
  ScoreRevealProps,
  LaunchSequenceProps,
  
  // Utility types
  ColorSet,
  Position,
  Size,
  AnimationConfig,
  Particle,
  
  // Hook return types
  UseTwinAnimationReturn,
  UseTwinColorsReturn,
} from './types/twin.types';
