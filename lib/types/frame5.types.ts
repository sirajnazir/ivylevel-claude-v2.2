/**
 * IvyQuest v3.0 — Frame 5: Power-Ups Types
 *
 * TypeScript interfaces for booster recommendations.
 *
 * @version 1.0.0
 * @module types/frame5.types
 */

import type {
  BoosterCategoryId,
  DifficultyId,
  TimeEstimateId,
  BoosterDefinition,
} from '../constants/frame5.constants';

// ============================================================================
// INPUT TYPES
// ============================================================================

export interface Frame5Inputs {
  // From previous frames
  currentScores: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
    ivyReady: number;
  };
  targetSchools: string[];
  yearsToApp: number;
  gradeLevel: string;
  hiddenCapabilities: string[];
  operatingStyle: string;

  // Activity context
  hasNationalRecognition: boolean;
  leadershipRoleCount: number;
  serviceHours: number;
  apCourseCount: number;
  hasAwards: boolean;
}

// ============================================================================
// BOOSTER TYPES
// ============================================================================

export interface Booster {
  // From definition
  id: string;
  category: BoosterCategoryId;
  title: string;
  description: string;
  fullDescription: string;
  icon: string;
  difficulty: DifficultyId;
  timeEstimate: TimeEstimateId;
  targetLayer: 'aptitude' | 'passion' | 'community' | 'operating';
  actionSteps: string[];

  // Calculated
  priority: number;           // 0-100 priority score
  impact: number;             // Projected score improvement
  projectedScore: number;     // Score after applying booster
  currentScore: number;       // Current score in target layer

  // Matching
  matchReason: string;        // Why this was recommended
  confidence: 'high' | 'medium' | 'low';

  // Status
  isSelected: boolean;
  isCompleted: boolean;
}

export interface BoosterImpact {
  boosterId: string;
  category: BoosterCategoryId;
  targetLayer: string;
  currentScore: number;
  projectedScore: number;
  improvement: number;
  confidence: 'high' | 'medium' | 'low';
}

// ============================================================================
// ACTION PLAN TYPES
// ============================================================================

export interface ActionItem {
  id: string;
  boosterId: string;
  step: string;
  order: number;
  isCompleted: boolean;
  dueDate?: string;
  notes?: string;
}

export interface ActionPlan {
  items: ActionItem[];
  totalSteps: number;
  completedSteps: number;
  estimatedWeeks: number;
  projectedIvyReadyScore: number;
}

// ============================================================================
// FRAME STATE
// ============================================================================

export interface Frame5Data {
  // Inputs
  inputs: Frame5Inputs | null;

  // Generated boosters
  boosters: Booster[];
  selectedBoosters: string[];

  // Action plan
  actionPlan: ActionPlan | null;

  // Projections
  projectedScores: {
    aptitude: number;
    passion: number;
    community: number;
    operating: number;
    ivyReady: number;
  } | null;

  // Frame completion
  isComplete: boolean;
  completedAt: string | null;
}

export interface Frame5UIState {
  currentCard: number;
  categoryFilter: BoosterCategoryId | null;
  sortBy: 'priority' | 'impact' | 'time' | 'difficulty';
  expandedBoosterId: string | null;
  showCompletedBoosters: boolean;
}

// ============================================================================
// VALIDATION TYPES
// ============================================================================

export interface Frame5CardValidation {
  isValid: boolean;
  errors?: string[];
}

export interface Frame5Validation {
  card1: Frame5CardValidation;
  card2: Frame5CardValidation;
  card3: Frame5CardValidation;
  card4: Frame5CardValidation;
  isFrameComplete: boolean;
}

// ============================================================================
// COMPONENT PROPS
// ============================================================================

export interface Frame5Props {
  inputs: Frame5Inputs;
  onComplete: () => void;
  onBack?: () => void;
}

export interface BoosterCardProps {
  booster: Booster;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onToggleSelect: () => void;
  onMarkComplete?: () => void;
}

export interface BoosterGridProps {
  boosters: Booster[];
  selectedIds: string[];
  categoryFilter: BoosterCategoryId | null;
  sortBy: 'priority' | 'impact' | 'time' | 'difficulty';
  onToggleSelect: (boosterId: string) => void;
  onToggleExpand: (boosterId: string) => void;
  expandedId: string | null;
}

export interface ImpactMeterProps {
  label: string;
  currentScore: number;
  projectedScore: number;
  maxScore?: number;
  color?: string;
}

export interface ActionPlanProps {
  plan: ActionPlan;
  onToggleStep: (itemId: string) => void;
  onUpdateNotes: (itemId: string, notes: string) => void;
}

export interface OverviewCardProps {
  currentScores: Frame5Inputs['currentScores'];
  targetSchools: string[];
  yearsToApp: number;
  topBoosters: Booster[];
  onContinue: () => void;
}

// ============================================================================
// STORE SLICE
// ============================================================================

export interface Frame5StoreSlice {
  // State
  frame5Data: Frame5Data;
  frame5UI: Frame5UIState;
  frame5Validation: Frame5Validation;

  // Actions - Data
  initializeFrame5: (inputs: Frame5Inputs) => void;
  selectBooster: (boosterId: string) => void;
  deselectBooster: (boosterId: string) => void;
  toggleBoosterComplete: (boosterId: string) => void;
  generateActionPlan: () => void;
  updateProjectedScores: () => void;

  // Actions - UI
  setFrame5Card: (card: number) => void;
  nextFrame5Card: () => void;
  prevFrame5Card: () => void;
  setCategoryFilter: (category: BoosterCategoryId | null) => void;
  setSortBy: (sortBy: Frame5UIState['sortBy']) => void;
  setExpandedBooster: (boosterId: string | null) => void;
  toggleShowCompleted: () => void;

  // Actions - Action Plan
  toggleActionStep: (itemId: string) => void;
  updateActionNotes: (itemId: string, notes: string) => void;

  // Actions - Lifecycle
  completeFrame5: () => void;
  resetFrame5: () => void;
}

// ============================================================================
// ENGINE TYPES
// ============================================================================

export interface BoosterEngineConfig {
  maxBoosters?: number;
  priorityThreshold?: number;
  includeCompleted?: boolean;
}

export interface BoosterEngineResult {
  boosters: Booster[];
  projectedScores: Frame5Data['projectedScores'];
  topRecommendations: string[];
}

// ============================================================================
// RE-EXPORTS
// ============================================================================

export type {
  BoosterCategoryId,
  DifficultyId,
  TimeEstimateId,
  BoosterDefinition,
};
