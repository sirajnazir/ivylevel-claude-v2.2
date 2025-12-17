/**
 * IvyQuest v3.0 — Integration Layer Types
 *
 * TypeScript interfaces for the master store and orchestration.
 *
 * @version 1.0.0
 * @module types/integration.types
 */

// ============================================================================
// FRAME DATA TYPES
// ============================================================================

// Frame 0
export interface Frame0Data {
  role: string | null;
  studentName: string;
  gradeLevel: string | null;
  targetSchools: string[];
  intendedMajor: string | null;
  majorCertainty: string;
  twinInitialized: boolean;
}

// Frame 1
export interface Frame1Data {
  gpa: number | null;
  isWeightedGPA: boolean;
  sat: number | null;
  act: number | null;
  apCount: number;
  ibCount: number;
  honorsCount: number;
  classRank: number | null;
  classSize: number | null;
  isRanked: boolean;
  demographics: DemographicsData;
}

export interface DemographicsData {
  firstGen: boolean;
  urm: boolean;
  lowIncome: boolean;
  legacy: string | null;
  recruitedAthlete: boolean;
  developmentCase: boolean;
  facultyChild: boolean;
}

// Frame 2
export interface Activity {
  id: string;
  name: string;
  category: string;
  depthLevel: string;
  yearsActive: number;
  hoursPerWeek: number;
  awards: Award[];
  description?: string;
}

export interface Award {
  id: string;
  name: string;
  level: string;
  year: number;
}

export interface LeadershipRole {
  id: string;
  organization: string;
  role: string;
  scope: string;
  yearsHeld: number;
  description?: string;
}

export interface Frame2Data {
  activities: Activity[];
  primarySpike: string | null;
  spikeDepth: string;
  leadershipRoles: LeadershipRole[];
  serviceHours: number;
  impactScope: string;
  diversityOfInvolvement: number;
}

// Frame 3
export interface Frame3Data {
  timeBand: string | null;
  operatingStyle: string | null;
  energyPattern: string | null;
  productivityPeak: string;
  hiddenCapabilities: string[];
  auraType: string | null;
}

// Frame 4
export interface Frame4Data {
  hasViewedScores: boolean;
  hasViewedSchoolFits: boolean;
  revealSequenceComplete: boolean;
  selectedSchoolForDetail: string | null;
}

// Frame 5
export interface IntegrationBooster {
  id: string;
  category: string;
  title: string;
  description: string;
  impact: number;
  isSelected: boolean;
  isCompleted: boolean;
}

export interface IntegrationActionItem {
  id: string;
  boosterId: string;
  step: string;
  order: number;
  isCompleted: boolean;
  notes?: string;
}

export interface Frame5Data {
  boosters: IntegrationBooster[];
  selectedBoosters: string[];
  actionPlan: {
    items: IntegrationActionItem[];
    totalSteps: number;
    completedSteps: number;
  } | null;
}

// ============================================================================
// SCORE TYPES
// ============================================================================

export interface LayerScore {
  total: number;
  breakdown: Record<string, number>;
}

export interface AptitudeScore extends LayerScore {
  flags: {
    testOptional: boolean;
    unranked: boolean;
    weightedGPA: boolean;
  };
}

export interface PassionScore extends LayerScore {
  spikeCategory: string | null;
  topActivities: Activity[];
}

export interface CommunityScore extends LayerScore {
  topRoles: LeadershipRole[];
}

export interface OperatingScore extends LayerScore {
  style: string;
  matchedSchools: string[];
}

export interface IvyReadyScore {
  total: number;
  tier: 'exceptional' | 'competitive' | 'average' | 'developing';
  breakdown: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
  };
  weights: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
  };
  demographicMultiplier: number;
  rawScore: number;
}

export interface SchoolFit {
  schoolId: string;
  schoolName: string;
  probability: number;
  probabilityRange: { low: number; high: number };
  fitLabel: 'safety' | 'target' | 'reach' | 'far_reach';
  categoryScores: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
  };
  styleMatch: number;
  insights: {
    strengths: string[];
    improvements: string[];
  };
}

export interface MarketReality {
  schoolFits: SchoolFit[];
  overallProbability: number;
  bestFitSchool: string;
  reachSchools: string[];
  targetSchools: string[];
  safetySchools: string[];
}

export interface QuestScores {
  aptitude: AptitudeScore | null;
  passion: PassionScore | null;
  community: CommunityScore | null;
  operating: OperatingScore | null;
  ivyReady: IvyReadyScore | null;
  marketReality: MarketReality | null;
  calculatedAt: string | null;
}

// ============================================================================
// NAVIGATION TYPES
// ============================================================================

export type FrameId = 0 | 1 | 2 | 3 | 4 | 5;

export interface NavigationState {
  currentFrame: FrameId;
  currentCard: number;
  completedFrames: FrameId[];
  canNavigateTo: FrameId[];
  history: Array<{ frame: FrameId; timestamp: string }>;
}

export interface NavigationActions {
  goToFrame: (frame: FrameId) => boolean;
  nextFrame: () => boolean;
  prevFrame: () => boolean;
  setCurrentCard: (card: number) => void;
  markFrameComplete: (frame: FrameId) => void;
}

// ============================================================================
// PERSISTENCE TYPES
// ============================================================================

export interface PersistenceState {
  questId: string;
  version: string;
  startedAt: string;
  lastUpdatedAt: string;
  autoSaveEnabled: boolean;
  lastSavedAt: string | null;
  isDirty: boolean;
}

export interface PersistenceConfig {
  storageKey: string;
  debounceMs: number;
  maxHistoryItems: number;
  sessionTimeoutHours: number;
}

export interface SavedSession {
  questId: string;
  state: QuestMasterState;
  savedAt: string;
  version: string;
}

// ============================================================================
// MASTER STATE
// ============================================================================

export interface QuestMasterState {
  // Meta
  questId: string;
  version: string;
  startedAt: string;
  lastUpdatedAt: string;

  // Navigation
  navigation: NavigationState;

  // Frame Data
  frame0: Frame0Data;
  frame1: Frame1Data;
  frame2: Frame2Data;
  frame3: Frame3Data;
  frame4: Frame4Data;
  frame5: Frame5Data;

  // Computed Scores
  scores: QuestScores;

  // Session Status
  isComplete: boolean;
  completedAt: string | null;

  // Persistence
  persistence: PersistenceState;
}

// ============================================================================
// MASTER ACTIONS
// ============================================================================

export interface QuestMasterActions {
  // Lifecycle
  initializeQuest: () => void;
  resetQuest: () => void;
  completeQuest: () => void;

  // Navigation
  navigationActions: NavigationActions;

  // Frame Updates
  updateFrame0: (data: Partial<Frame0Data>) => void;
  updateFrame1: (data: Partial<Frame1Data>) => void;
  updateFrame2: (data: Partial<Frame2Data>) => void;
  updateFrame3: (data: Partial<Frame3Data>) => void;
  updateFrame4: (data: Partial<Frame4Data>) => void;
  updateFrame5: (data: Partial<Frame5Data>) => void;

  // Score Calculation
  calculateScores: () => void;
  recalculateForSchool: (schoolId: string) => void;

  // Persistence
  saveSession: () => void;
  loadSession: (questId?: string) => boolean;
  clearSession: () => void;
  exportSession: () => SavedSession;
}

// ============================================================================
// STORE TYPE
// ============================================================================

export type QuestStore = QuestMasterState & QuestMasterActions;

// ============================================================================
// ORCHESTRATOR PROPS
// ============================================================================

export interface QuestOrchestratorProps {
  onComplete?: (result: QuestCompletionResult) => void;
  onFrameChange?: (from: FrameId, to: FrameId) => void;
  onScoreCalculated?: (scores: QuestScores) => void;
  initialState?: Partial<QuestMasterState>;
  autoRestore?: boolean;
  showDebug?: boolean;
}

export interface QuestCompletionResult {
  questId: string;
  studentName: string;
  targetSchools: string[];
  scores: QuestScores;
  selectedBoosters: string[];
  actionPlan: Frame5Data['actionPlan'];
  completedAt: string;
  duration: number; // minutes
}

// ============================================================================
// PROGRESS TYPES
// ============================================================================

export interface QuestProgress {
  percentComplete: number;
  currentFrame: FrameId;
  completedFrames: FrameId[];
  remainingFrames: FrameId[];
  estimatedTimeRemaining: number; // minutes
  frameProgress: Record<
    FrameId,
    {
      isComplete: boolean;
      percentComplete: number;
      cardsCompleted: number;
      totalCards: number;
    }
  >;
}

// ============================================================================
// FRAME METADATA
// ============================================================================

export interface FrameMeta {
  id: FrameId;
  name: string;
  description: string;
  icon: string;
  color: string;
  targetDuration: number; // seconds
  cardCount: number;
}

export const FRAME_META: Record<FrameId, FrameMeta> = {
  0: {
    id: 0,
    name: 'Warm-Up',
    description: 'Identity & Target Setup',
    icon: '👋',
    color: '#06B6D4',
    targetDuration: 60,
    cardCount: 4,
  },
  1: {
    id: 1,
    name: 'Snapshot',
    description: 'Academic Profile',
    icon: '📊',
    color: '#3B82F6',
    targetDuration: 90,
    cardCount: 4,
  },
  2: {
    id: 2,
    name: 'Spike',
    description: 'Passion & Community',
    icon: '🔥',
    color: '#F59E0B',
    targetDuration: 120,
    cardCount: 6,
  },
  3: {
    id: 3,
    name: 'Operating',
    description: 'Style & Capabilities',
    icon: '⚡',
    color: '#8B5CF6',
    targetDuration: 90,
    cardCount: 5,
  },
  4: {
    id: 4,
    name: 'Reveal',
    description: 'Score Discovery',
    icon: '🎯',
    color: '#10B981',
    targetDuration: 60,
    cardCount: 3,
  },
  5: {
    id: 5,
    name: 'Power-Ups',
    description: 'Booster Recommendations',
    icon: '🚀',
    color: '#EC4899',
    targetDuration: 120,
    cardCount: 4,
  },
};
