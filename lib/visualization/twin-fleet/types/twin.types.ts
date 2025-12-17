/**
 * IvyQuest v3.0 — Twin Fleet Types
 * 
 * TypeScript interfaces for avatar components.
 * 
 * @version 1.0.0
 * @module lib/types/twin.types
 */

import type {
  ScoreTierId,
  SchoolId,
  OperatingStyleId,
  TwinSize,
  FleetLayoutId,
} from '../constants/twin.constants';

// ============================================================================
// SCORE TYPES
// ============================================================================

export interface CategoryScores {
  aptitude: number;
  passion: number;
  community: number;
  operating: number;
}

export interface TwinScoreState {
  ivyReadyScore: number;
  tier: ScoreTierId;
  categoryScores: CategoryScores;
  demographicMultiplier?: number;
}

// ============================================================================
// AVATAR PROPS
// ============================================================================

export interface BaseTwinProps {
  /** Ivy+ Ready Score (0-100) */
  score: number;
  
  /** Score tier */
  tier: ScoreTierId;
  
  /** Operating style for visual patterns */
  style?: OperatingStyleId;
  
  /** Avatar size */
  size?: TwinSize;
  
  /** Is avatar currently active/focused */
  isActive?: boolean;
  
  /** Show particle effects */
  showParticles?: boolean;
  
  /** Show aura glow */
  showAura?: boolean;
  
  /** Custom class name */
  className?: string;
  
  /** Click handler */
  onClick?: () => void;
  
  /** Animation state */
  animationState?: 'idle' | 'active' | 'celebrating' | 'transitioning';
}

export interface SchoolTwinProps extends Omit<BaseTwinProps, 'tier' | 'score'> {
  /** School identifier */
  schoolId: SchoolId;

  /** Overall score (optional, calculated from categoryScores if not provided) */
  score?: number;
  
  /** Admission probability (0-100) */
  probability: number;
  
  /** Category scores for this school */
  categoryScores: CategoryScores;
  
  /** Operating style match percentage (0-1) */
  styleMatch?: number;
  
  /** Whether this school is currently selected/focused */
  isSelected?: boolean;
  
  /** Show fit ring indicator */
  showFitRing?: boolean;
  
  /** Custom label override */
  label?: string;
}

// ============================================================================
// AURA PROPS
// ============================================================================

export interface TwinAuraProps {
  /** Primary glow color */
  primaryColor: string;
  
  /** Secondary glow color */
  secondaryColor?: string;
  
  /** Glow intensity (0-1) */
  intensity: number;
  
  /** Aura blur radius */
  blur?: number;
  
  /** Breathing animation enabled */
  breathing?: boolean;
  
  /** Animation speed multiplier */
  speedMultiplier?: number;
  
  /** Size of the aura */
  size: { width: number; height: number };
}

// ============================================================================
// PARTICLE PROPS
// ============================================================================

export interface Particle {
  id: string;
  x: number;
  y: number;
  size: number;
  opacity: number;
  color: string;
  velocity: { x: number; y: number };
  lifespan: number;
  age: number;
}

export interface TwinParticlesProps {
  /** Particle color (inherits from tier) */
  color: string;
  
  /** Secondary particle color */
  secondaryColor?: string;
  
  /** Particle density multiplier */
  density?: number;
  
  /** Pattern type */
  pattern?: 'default' | 'structured' | 'flowing' | 'expansive' | 'orbital';
  
  /** Animation speed multiplier */
  speedMultiplier?: number;
  
  /** Container bounds */
  bounds: { width: number; height: number };
  
  /** Is particle system active */
  isActive?: boolean;
}

// ============================================================================
// FLEET PROPS
// ============================================================================

export interface SchoolTwinData {
  schoolId: SchoolId;
  probability: number;
  categoryScores: CategoryScores;
  styleMatch?: number;
  insights?: {
    strengths: string[];
    improvements: string[];
  };
}

export interface FleetDisplayProps {
  /** Base twin configuration */
  baseTwin: {
    score: number;
    tier: ScoreTierId;
    style?: OperatingStyleId;
  };
  
  /** School-specific twins */
  schoolTwins: SchoolTwinData[];
  
  /** Fleet layout style */
  layout?: FleetLayoutId;
  
  /** Currently selected school */
  selectedSchool?: SchoolId | null;
  
  /** School selection handler */
  onTwinSelect?: (schoolId: SchoolId) => void;
  
  /** Show all twins or only selected */
  showAll?: boolean;
  
  /** Maximum twins to display */
  maxDisplay?: number;
}

// ============================================================================
// COMMAND DECK PROPS
// ============================================================================

export interface CommandDeckProps {
  /** Student name for display */
  studentName: string;
  
  /** Ivy+ Ready Score */
  ivyReadyScore: number;
  
  /** Score tier */
  tier: ScoreTierId;
  
  /** Category scores */
  categoryScores?: CategoryScores;
  
  /** Target school IDs */
  targetSchools: SchoolId[];
  
  /** Currently active/themed school */
  activeSchool?: SchoolId | null;
  
  /** Show HUD overlay */
  showHUD?: boolean;
  
  /** Show score bars */
  showScoreBars?: boolean;
  
  /** Children (twin fleet) */
  children?: React.ReactNode;
  
  /** Theme override */
  theme?: 'default' | SchoolId;
}

export interface DeckHUDProps {
  /** Ivy+ Ready Score */
  ivyReadyScore: number;
  
  /** Score tier */
  tier: ScoreTierId;
  
  /** Category scores */
  categoryScores: CategoryScores;
  
  /** Currently selected school */
  selectedSchool?: SchoolId | null;
  
  /** School fit probability */
  schoolProbability?: number;
  
  /** Style match percentage */
  styleMatch?: number;
  
  /** Position */
  position?: 'top' | 'bottom' | 'left' | 'right';
}

// ============================================================================
// ANIMATION PROPS
// ============================================================================

export interface MaterializeSequenceProps {
  /** Duration override (ms) */
  duration?: number;
  
  /** Final score to reveal */
  targetScore?: number;
  
  /** Tier to materialize into */
  tier?: ScoreTierId;
  
  /** Operating style for pattern */
  style?: OperatingStyleId;
  
  /** Completion callback */
  onComplete?: () => void;
  
  /** Progress callback */
  onProgress?: (progress: number) => void;
  
  /** Auto-start animation */
  autoPlay?: boolean;
}

export interface ScoreRevealProps {
  /** Starting score (usually 0) */
  fromScore?: number;
  
  /** Final score */
  toScore: number;
  
  /** Score tier */
  tier: ScoreTierId;
  
  /** Duration override (ms) */
  duration?: number;
  
  /** Show tier badge animation */
  showTierBadge?: boolean;
  
  /** Completion callback */
  onComplete?: () => void;
  
  /** Easing function */
  easing?: 'linear' | 'easeOut' | 'easeInOut' | 'bounce';
}

export interface LaunchSequenceProps {
  /** From frame */
  fromFrame: number;
  
  /** To frame */
  toFrame: number;
  
  /** Duration override (ms) */
  duration?: number;
  
  /** Completion callback */
  onComplete?: () => void;
  
  /** Skip animation */
  skip?: boolean;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface ColorSet {
  primary: string;
  secondary: string;
  glow: string;
}

export interface Position {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface AnimationConfig {
  duration: number;
  delay?: number;
  easing?: string;
  repeat?: number | 'infinity';
}

// ============================================================================
// HOOK RETURN TYPES
// ============================================================================

export interface UseTwinAnimationReturn {
  isAnimating: boolean;
  progress: number;
  currentPhase: string;
  play: () => void;
  pause: () => void;
  reset: () => void;
}

export interface UseTwinColorsReturn {
  tierColors: ColorSet;
  schoolColors: {
    primary: string;
    secondary: string;
    accent: string;
    gradient: string;
  } | null;
  blendedColors: ColorSet;
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  // Types are exported individually
};
