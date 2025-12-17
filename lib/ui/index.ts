/**
 * IvyQuest v3.0 — UI Components Library
 *
 * Shared design system components.
 *
 * @version 1.0.0
 * @module @ivyquest/ui-components
 */

// ============================================================================
// PRIMITIVES
// ============================================================================

export { Button } from './components/Button';
export { Input } from './components/Input';
export { Select, type SelectProps, type SelectOption } from './components/Select';
export {
  Checkbox,
  Radio,
  RadioGroup,
  type CheckboxProps,
  type RadioProps,
  type RadioGroupProps,
} from './components/Checkbox';
export { Slider } from './components/Slider';
export { Toggle } from './components/Toggle';

// ============================================================================
// LAYOUT
// ============================================================================

export { Card } from './components/Card';

// ============================================================================
// FEEDBACK
// ============================================================================

export { Badge } from './components/Badge';
export {
  Progress,
  ProgressBar,
  ProgressRing,
  ProgressSteps,
} from './components/Progress';
export {
  Spinner,
  Skeleton,
  SkeletonText,
  SkeletonCard,
  LoadingOverlay,
  type SpinnerProps,
  type SkeletonProps,
  type SkeletonTextProps,
  type LoadingOverlayProps,
} from './components/Loading';
export { Tooltip } from './components/Tooltip';

// ============================================================================
// OVERLAY
// ============================================================================

export { Modal } from './components/Modal';

// ============================================================================
// NAVIGATION
// ============================================================================

export { Tabs, type TabsProps, type TabListProps, type TabTriggerProps, type TabContentProps } from './components/Tabs';
export { Stepper, type StepperProps, type Step } from './components/Stepper';

// ============================================================================
// DATA DISPLAY
// ============================================================================

export { ScoreDisplay, type ScoreDisplayProps, type ScoreTier } from './components/ScoreDisplay';
export {
  StatCard,
  Avatar,
  AvatarGroup,
  Tag,
  type StatCardProps,
  type AvatarProps,
  type AvatarGroupProps,
  type TagProps,
} from './components/DataDisplay';

// ============================================================================
// UTILITIES
// ============================================================================

export { cn, cva } from './utils/cn';

// ============================================================================
// THEME & CONSTANTS
// ============================================================================

export {
  colors,
  tierColors,
  spacing,
  spacingTokens,
  fontFamily,
  fontSize,
  fontWeight,
  typography,
  borderRadius,
  borderWidth,
  shadows,
  transitions,
  zIndex,
  breakpoints,
  componentSizes,
} from './constants/theme.constants';

export type { TierColorKey } from './constants/theme.constants';

// ============================================================================
// TYPES (from central types file)
// ============================================================================

export type {
  Size,
  ExtendedSize,
  BaseComponentProps,
  ButtonVariant,
  ButtonProps,
  CardVariant,
  CardPadding,
  CardProps,
  CardHeaderProps,
  CardBodyProps,
  CardFooterProps,
  InputType,
  InputProps,
  TextAreaProps,
  BadgeVariant,
  BadgeProps,
  ProgressVariant,
  ProgressColor,
  ProgressBarProps,
  ProgressRingProps,
  ProgressStepsProps,
  SliderProps,
  ToggleProps,
  TooltipPosition,
  TooltipProps,
  ModalSize,
  ModalProps,
  ModalBodyProps,
  ModalFooterProps,
  ScoreBreakdown,
  SchoolBadgeVariant,
  SchoolBadgeProps,
  FrameContainerProps,
} from './types/ui.types';
