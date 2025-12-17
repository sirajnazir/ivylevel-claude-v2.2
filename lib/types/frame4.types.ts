/**
 * Frame 4: Reveal - Type Definitions
 * Interfaces for score calculations, school fits, and store state
 */

// Input types from previous frames
export interface Frame0Inputs {
  targetSchools: string[];
  intendedMajor: string;
  majorCertainty: 'exploring' | 'likely' | 'locked';
  gradeLevel: number;
  studentName: string;
}

export interface Frame1Inputs {
  aptitudeScore: number;
  gpaWeighted: number;
  satTotal: number | null;
  actComposite: number | null;
  apCount: number;
  saturationLevel: string;
  demographicMultipliers: {
    firstGen: boolean;
    legacy: Record<string, boolean>;
    urm: boolean;
    incomePercentile: number;
  };
}

export interface Frame2Inputs {
  passionScore: number;
  communityScore: number;
  spikeCategory: string;
  leadershipLevel: string;
  serviceHours: number;
  studentArchetype: string;
}

export interface Frame3Inputs {
  operatingStyle: string;
  timeCapacity: number;
  energyPattern: string;
  strengthProfile: string;
  readinessScore: number;
  auraColor: string;
}

// Combined inputs from all frames
export interface AllFrameInputs extends Frame0Inputs, Frame1Inputs, Frame2Inputs, Frame3Inputs {}

// Ivy+ Ready Score structure
export interface IvyReadyScore {
  total: number;
  tier: 'exceptional' | 'competitive' | 'average' | 'below';
  percentile: number;
  categoryScores: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
  };
  multipliers: {
    firstGen: number;
    urm: number;
    legacy: number;
  };
}

// Market Reality (RS Rubric) structure
export interface MarketReality {
  min: number;
  max: number;
  label: 'reach' | 'target' | 'safety';
  confidence: number;
}

// Individual school fit card data
export interface SchoolFitCard {
  schoolId: string;
  schoolName: string;
  probability: { min: number; max: number };
  fitLabel: 'reach' | 'target' | 'safety';
  fitScore: number;
  keyInsight: string;
  categoryScores: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
  };
  schoolColor: string;
  culture: string;
}

// Category breakdown item
export interface CategoryBreakdown {
  id: string;
  label: string;
  icon: string;
  score: number;
  weight: number;
  status: 'strength' | 'average' | 'improvement';
  insight: string;
}

// Launch sequence phases
export type LaunchPhase =
  | 'idle'
  | 'countdown'
  | 'launch'
  | 'flight'
  | 'landing'
  | 'reveal';

// Dual score display data
export interface DualScoreData {
  profileStrength: number;
  marketReality: MarketReality;
  schoolCount: number;
}

// Frame 4 card identifiers
export type Frame4Card =
  | 'launch'
  | 'dualScore'
  | 'schoolCards'
  | 'categoryBreakdown';

// Frame 4 store state
export interface Frame4State {
  // Current card and phase
  currentCard: Frame4Card;
  launchPhase: LaunchPhase;
  isAnimating: boolean;

  // Calculated scores
  ivyReadyScore: IvyReadyScore | null;
  schoolFits: SchoolFitCard[];
  categoryBreakdowns: CategoryBreakdown[];

  // UI state
  activeSchoolIndex: number;
  autoplayEnabled: boolean;
  hasSeenLaunch: boolean;

  // Timing
  frameStartTime: number | null;
  cardStartTimes: Record<Frame4Card, number | null>;
}

// Frame 4 store actions
export interface Frame4Actions {
  // Navigation
  setCurrentCard: (card: Frame4Card) => void;
  nextCard: () => void;
  prevCard: () => void;

  // Launch sequence
  setLaunchPhase: (phase: LaunchPhase) => void;
  startLaunchSequence: () => void;

  // Score calculation
  calculateScores: (inputs: AllFrameInputs) => void;

  // School cards
  setActiveSchoolIndex: (index: number) => void;
  nextSchool: () => void;
  prevSchool: () => void;
  toggleAutoplay: () => void;

  // Animation state
  setIsAnimating: (animating: boolean) => void;

  // Timing
  startFrame: () => void;
  recordCardStart: (card: Frame4Card) => void;

  // Reset
  reset: () => void;
}

// Combined store slice
export interface Frame4StoreSlice extends Frame4State, Frame4Actions {}

// Demographic multipliers for probability calculation
export interface DemographicInputs {
  firstGen: boolean;
  legacy: Record<string, boolean>;
  urm: boolean;
  incomePercentile: number;
}

// Trace log entry for analytics
export interface Frame4TraceEntry {
  event: string;
  timestamp: number;
  data?: Record<string, unknown>;
}

// Animation configuration
export interface AnimationConfig {
  duration: number;
  easing: readonly number[];
  delay?: number;
}

// Score ring props
export interface ScoreRingProps {
  score: number;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showLabel?: boolean;
  animated?: boolean;
  color?: string;
}

// Market reality bar props
export interface MarketRealityBarProps {
  min: number;
  max: number;
  label: string;
  animated?: boolean;
  delay?: number;
}

// Card component props
export interface Card1Props {
  onComplete: () => void;
}

export interface Card2Props {
  ivyReadyScore: IvyReadyScore;
  marketReality: MarketReality;
  schoolCount: number;
  onComplete: () => void;
}

export interface Card3Props {
  schoolFits: SchoolFitCard[];
  activeIndex: number;
  onIndexChange: (index: number) => void;
  autoplay: boolean;
  onToggleAutoplay: () => void;
  onComplete: () => void;
}

export interface Card4Props {
  categoryBreakdowns: CategoryBreakdown[];
  onComplete: () => void;
}
