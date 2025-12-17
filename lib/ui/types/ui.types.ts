/**
 * IvyQuest v3.0 — UI Types
 * 
 * TypeScript interfaces for UI components.
 * 
 * @version 1.0.0
 * @module lib/types/ui.types
 */

import type { ReactNode, MouseEvent, ChangeEvent, KeyboardEvent } from 'react';

// ============================================================================
// BASE TYPES
// ============================================================================

export type Size = 'sm' | 'md' | 'lg';
export type ExtendedSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface BaseComponentProps {
  className?: string;
  id?: string;
  'data-testid'?: string;
}

// ============================================================================
// BUTTON TYPES
// ============================================================================

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';

export interface ButtonProps extends BaseComponentProps {
  variant?: ButtonVariant;
  size?: Size;
  disabled?: boolean;
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: (e: MouseEvent<HTMLButtonElement>) => void;
  children: ReactNode;
}

// ============================================================================
// CARD TYPES
// ============================================================================

export type CardVariant = 'default' | 'elevated' | 'outlined' | 'glass';
export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends BaseComponentProps {
  variant?: CardVariant;
  padding?: CardPadding;
  interactive?: boolean;
  selected?: boolean;
  onClick?: (e: MouseEvent<HTMLDivElement>) => void;
  children: ReactNode;
}

export interface CardHeaderProps extends BaseComponentProps {
  children: ReactNode;
  action?: ReactNode;
}

export interface CardBodyProps extends BaseComponentProps {
  children: ReactNode;
}

export interface CardFooterProps extends BaseComponentProps {
  children: ReactNode;
  align?: 'left' | 'center' | 'right' | 'between';
}

// ============================================================================
// INPUT TYPES
// ============================================================================

export type InputType = 'text' | 'number' | 'email' | 'password' | 'tel' | 'url';

export interface InputProps extends BaseComponentProps {
  type?: InputType;
  label?: string;
  placeholder?: string;
  value: string | number;
  onChange: (value: string) => void;
  onBlur?: () => void;
  onFocus?: () => void;
  onKeyDown?: (e: KeyboardEvent<HTMLInputElement>) => void;
  error?: string;
  hint?: string;
  disabled?: boolean;
  required?: boolean;
  readOnly?: boolean;
  size?: Size;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  min?: number;
  max?: number;
  step?: number;
  autoFocus?: boolean;
  autoComplete?: string;
}

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends BaseComponentProps {
  label?: string;
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
  hint?: string;
  disabled?: boolean;
  required?: boolean;
  size?: Size;
}

export interface TextAreaProps extends BaseComponentProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  error?: string;
  hint?: string;
  disabled?: boolean;
  required?: boolean;
  rows?: number;
  maxLength?: number;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

// ============================================================================
// BADGE TYPES
// ============================================================================

export type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral';

export interface BadgeProps extends BaseComponentProps {
  variant?: BadgeVariant;
  size?: Size;
  dot?: boolean;
  icon?: ReactNode;
  children: ReactNode;
}

// ============================================================================
// PROGRESS TYPES
// ============================================================================

export type ProgressVariant = 'bar' | 'ring' | 'steps';
export type ProgressColor = 'primary' | 'success' | 'warning' | 'error' | 'tier';

export interface ProgressBarProps extends BaseComponentProps {
  value: number;
  max?: number;
  color?: ProgressColor;
  size?: Size;
  showLabel?: boolean;
  animated?: boolean;
  label?: string;
  tierColor?: string;
}

export interface ProgressRingProps extends BaseComponentProps {
  value: number;
  max?: number;
  size?: ExtendedSize;
  strokeWidth?: number;
  color?: ProgressColor;
  showLabel?: boolean;
  label?: string;
  tierColor?: string;
}

export interface ProgressStepsProps extends BaseComponentProps {
  current: number;
  total: number;
  labels?: string[];
  clickable?: boolean;
  onStepClick?: (step: number) => void;
}

// ============================================================================
// SLIDER TYPES
// ============================================================================

export interface SliderProps extends BaseComponentProps {
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
  step?: number;
  marks?: number[] | boolean;
  label?: string;
  showValue?: boolean;
  formatValue?: (value: number) => string;
  disabled?: boolean;
}

// ============================================================================
// TOGGLE TYPES
// ============================================================================

export interface ToggleProps extends BaseComponentProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  size?: Size;
}

// ============================================================================
// TOOLTIP TYPES
// ============================================================================

export type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';

export interface TooltipProps extends BaseComponentProps {
  content: ReactNode;
  position?: TooltipPosition;
  delay?: number;
  disabled?: boolean;
  children: ReactNode;
}

// ============================================================================
// MODAL TYPES
// ============================================================================

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: ModalSize;
  closeOnOverlay?: boolean;
  showCloseButton?: boolean;
  children: ReactNode;
}

export interface ModalBodyProps extends BaseComponentProps {
  children: ReactNode;
}

export interface ModalFooterProps extends BaseComponentProps {
  children: ReactNode;
}

// ============================================================================
// SCORE DISPLAY TYPES
// ============================================================================

export type ScoreTier = 'exceptional' | 'competitive' | 'average' | 'developing';

export interface ScoreBreakdown {
  aptitude?: number;
  passion?: number;
  community?: number;
  operating?: number;
}

export interface ScoreDisplayProps extends BaseComponentProps {
  score: number;
  tier: ScoreTier;
  label?: string;
  size?: ExtendedSize;
  animated?: boolean;
  showTierBadge?: boolean;
  breakdown?: ScoreBreakdown;
  compact?: boolean;
}

// ============================================================================
// SCHOOL BADGE TYPES
// ============================================================================

export type SchoolBadgeVariant = 'full' | 'compact' | 'icon';

export interface SchoolBadgeProps extends BaseComponentProps {
  schoolId: string;
  probability?: number;
  showProbability?: boolean;
  size?: Size;
  variant?: SchoolBadgeVariant;
  onClick?: () => void;
}

// ============================================================================
// FRAME CONTAINER TYPES
// ============================================================================

export interface FrameContainerProps extends BaseComponentProps {
  frameNumber: number;
  title: string;
  subtitle?: string;
  icon?: string;
  progress?: number;
  onBack?: () => void;
  onNext?: () => void;
  backLabel?: string;
  nextLabel?: string;
  backDisabled?: boolean;
  nextDisabled?: boolean;
  showProgress?: boolean;
  children: ReactNode;
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  // Types are exported individually
};
