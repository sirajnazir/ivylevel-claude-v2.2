/**
 * IvyQuest v3.0 — Feedback System Types
 * 
 * TypeScript interfaces for feedback components.
 * 
 * @version 1.0.0
 * @module lib/types/feedback.types
 */

import type {
  ValidationStateId,
  ToastTypeId,
  AchievementRarity,
  MilestoneId,
  HintTypeId,
  ScoreCategory,
  AnimationPreset,
} from '../constants/feedback.constants';

// ============================================================================
// SCORE DELTA TYPES
// ============================================================================

export interface ScoreDelta {
  id: string;
  delta: number;
  category: ScoreCategory;
  position: { x: number; y: number };
  timestamp: number;
}

export interface ScoreDeltaPopupProps {
  /** Point change (positive or negative) */
  delta: number;
  
  /** Score category affected */
  category: ScoreCategory;
  
  /** Screen position for popup */
  position: { x: number; y: number };
  
  /** Animation complete callback */
  onComplete?: () => void;
  
  /** Custom duration override (ms) */
  duration?: number;
  
  /** Show particle trail */
  showTrail?: boolean;
}

export interface ScoreDeltaTrailProps {
  /** Start position */
  from: { x: number; y: number };
  
  /** End position (score display) */
  to: { x: number; y: number };
  
  /** Trail color */
  color: string;
  
  /** Animation complete callback */
  onComplete?: () => void;
}

// ============================================================================
// VALIDATION TYPES
// ============================================================================

export interface ValidationState {
  state: ValidationStateId;
  message?: string;
  details?: string;
}

export interface FieldValidationProps {
  /** Validation state */
  state: ValidationStateId;
  
  /** Feedback message */
  message?: string;
  
  /** Show state icon */
  showIcon?: boolean;
  
  /** Animate state changes */
  animate?: boolean;
  
  /** Additional class name */
  className?: string;
}

export interface CardValidationProps {
  /** Card identifier */
  cardId: string;
  
  /** Field validation states */
  fields: Record<string, ValidationState>;
  
  /** Overall card validity */
  isValid: boolean;
  
  /** Show summary */
  showSummary?: boolean;
  
  /** Required fields */
  requiredFields?: string[];
}

// ============================================================================
// TOAST TYPES
// ============================================================================

export interface Toast {
  id: string;
  type: ToastTypeId;
  title: string;
  message?: string;
  duration?: number;
  dismissible?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  createdAt: number;
}

export interface ToastProps {
  /** Toast type */
  type: ToastTypeId;
  
  /** Toast title */
  title: string;
  
  /** Optional message */
  message?: string;
  
  /** Duration in ms (0 = manual dismiss) */
  duration?: number;
  
  /** Show dismiss button */
  dismissible?: boolean;
  
  /** Optional action button */
  action?: {
    label: string;
    onClick: () => void;
  };
  
  /** Close callback */
  onClose?: () => void;
}

export interface ToastContainerProps {
  /** Maximum visible toasts */
  maxVisible?: number;
  
  /** Container position */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

// ============================================================================
// ACHIEVEMENT TYPES
// ============================================================================

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  rarity: AchievementRarity;
  unlockedAt?: number;
}

export interface AchievementUnlockProps {
  /** Achievement data */
  achievement: Achievement;
  
  /** Dismiss callback */
  onDismiss?: () => void;
  
  /** Play sound */
  playSound?: boolean;
  
  /** Auto dismiss after duration */
  autoDismiss?: boolean;
}

// ============================================================================
// MILESTONE TYPES
// ============================================================================

export interface Milestone {
  id: MilestoneId;
  title: string;
  description: string;
  icon: string;
  frame: number;
  animation: string;
  completedAt?: number;
}

export interface MilestoneReachedProps {
  /** Milestone identifier */
  milestoneId: MilestoneId;
  
  /** Completion callback */
  onComplete?: () => void;
  
  /** Skip animation */
  skipAnimation?: boolean;
}

export interface FrameCompleteProps {
  /** Completed frame number */
  frameNumber: number;
  
  /** Frame name */
  frameName: string;
  
  /** Next frame preview */
  nextFrame?: {
    number: number;
    name: string;
    description: string;
  };
  
  /** Continue callback */
  onContinue?: () => void;
}

// ============================================================================
// HINT TYPES
// ============================================================================

export interface Hint {
  id: string;
  type: HintTypeId;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  dismissible?: boolean;
  priority?: number;
  expiresAt?: number;
}

export interface ContextualHintProps {
  /** Hint type */
  type: HintTypeId;
  
  /** Hint message */
  message: string;
  
  /** Optional action */
  action?: {
    label: string;
    onClick: () => void;
  };
  
  /** Allow dismissal */
  dismissible?: boolean;
  
  /** Dismiss callback */
  onDismiss?: () => void;
}

export interface BoosterSuggestionProps {
  /** Suggested booster */
  booster: {
    id: string;
    name: string;
    description: string;
    impact: number;
    category: ScoreCategory;
  };
  
  /** Apply callback */
  onApply?: () => void;
  
  /** Dismiss callback */
  onDismiss?: () => void;
}

// ============================================================================
// HOOK TYPES
// ============================================================================

export interface FeedbackContextValue {
  /** Active toasts */
  toasts: Toast[];
  
  /** Active hints */
  hints: Hint[];
  
  /** Active deltas */
  deltas: ScoreDelta[];
  
  /** Unlocked achievements */
  achievements: Achievement[];
  
  /** Completed milestones */
  completedMilestones: MilestoneId[];
  
  /** Show score delta */
  showDelta: (delta: number, category: ScoreCategory, position: { x: number; y: number }) => void;
  
  /** Show toast */
  showToast: (type: ToastTypeId, title: string, message?: string, options?: Partial<Toast>) => void;
  
  /** Show achievement */
  showAchievement: (achievement: Achievement) => void;
  
  /** Show milestone */
  showMilestone: (milestoneId: MilestoneId) => void;
  
  /** Show hint */
  showHint: (hint: Omit<Hint, 'id'>) => void;
  
  /** Dismiss toast */
  dismissToast: (id: string) => void;
  
  /** Dismiss hint */
  dismissHint: (id: string) => void;
  
  /** Clear all */
  clearAll: () => void;
}

export interface FeedbackProviderProps {
  children: React.ReactNode;
  config?: FeedbackConfig;
}

export interface FeedbackConfig {
  /** Maximum simultaneous toasts */
  maxToasts?: number;
  
  /** Default toast duration (ms) */
  defaultDuration?: number;
  
  /** Enable sound effects */
  enableSounds?: boolean;
  
  /** Enable haptic feedback */
  enableHaptics?: boolean;
  
  /** Auto-show milestones */
  autoShowMilestones?: boolean;
}

// ============================================================================
// SCORE DELTA HOOK TYPES
// ============================================================================

export interface UseScoreDeltaReturn {
  /** Current score value */
  currentScore: number;
  
  /** Previous score value */
  previousScore: number;
  
  /** Current delta */
  delta: number;
  
  /** Score category */
  category: ScoreCategory;
  
  /** Is animating */
  isAnimating: boolean;
  
  /** Track a score change */
  trackChange: (newScore: number) => void;
  
  /** Reset tracking */
  reset: () => void;
}

export interface UseScoreDeltaOptions {
  /** Initial score */
  initialScore?: number;
  
  /** Animation duration (ms) */
  animationDuration?: number;
  
  /** Minimum delta to animate */
  minDelta?: number;
  
  /** Change callback */
  onChange?: (delta: number, category: ScoreCategory) => void;
}

// ============================================================================
// ANIMATION TYPES
// ============================================================================

export interface AnimationConfig {
  preset?: AnimationPreset;
  duration?: number;
  delay?: number;
  custom?: {
    initial?: object;
    animate?: object;
    exit?: object;
    transition?: object;
  };
}

// ============================================================================
// RE-EXPORTS FROM CONSTANTS
// ============================================================================

export type {
  ValidationStateId,
  ToastTypeId,
  AchievementRarity,
  MilestoneId,
  HintTypeId,
  ScoreCategory,
  AnimationPreset,
} from '../constants/feedback.constants';

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  // Types are exported individually
};
