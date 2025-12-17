/**
 * IvyQuest v3.0 — Feedback System Utilities
 * 
 * Helper functions for feedback calculations and formatting.
 * 
 * @version 1.0.0
 * @module lib/utils/feedbackUtils
 */

import {
  SCORE_DELTA_CONFIG,
  CATEGORY_COLORS,
  VALIDATION_STATES,
  TOAST_CONFIG,
  ACHIEVEMENT_CONFIG,
  HINT_CONFIG,
  type ScoreCategory,
  type ValidationStateId,
  type ToastTypeId,
  type AchievementRarity,
} from '../constants/feedback.constants';

// ============================================================================
// ID GENERATION
// ============================================================================

/**
 * Generate unique ID for feedback items
 */
export function generateFeedbackId(prefix: string = 'fb'): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// ============================================================================
// SCORE DELTA UTILITIES
// ============================================================================

/**
 * Get delta magnitude category
 */
export function getDeltaMagnitude(delta: number): 'minor' | 'moderate' | 'major' | 'exceptional' {
  const absDelta = Math.abs(delta);
  const { thresholds } = SCORE_DELTA_CONFIG;
  
  if (absDelta >= thresholds.exceptional) return 'exceptional';
  if (absDelta >= thresholds.major) return 'major';
  if (absDelta >= thresholds.moderate) return 'moderate';
  return 'minor';
}

/**
 * Get delta colors based on direction
 */
export function getDeltaColors(delta: number) {
  if (delta > 0) return SCORE_DELTA_CONFIG.colors.positive;
  if (delta < 0) return SCORE_DELTA_CONFIG.colors.negative;
  return SCORE_DELTA_CONFIG.colors.neutral;
}

/**
 * Get delta size configuration
 */
export function getDeltaSize(delta: number) {
  const magnitude = getDeltaMagnitude(delta);
  return SCORE_DELTA_CONFIG.sizes[magnitude];
}

/**
 * Get category colors
 */
export function getCategoryColors(category: ScoreCategory) {
  return CATEGORY_COLORS[category];
}

/**
 * Format delta for display
 */
export function formatDelta(delta: number): string {
  if (delta > 0) return `+${delta}`;
  return delta.toString();
}

/**
 * Calculate animation duration based on delta magnitude
 */
export function getAnimationDuration(delta: number): number {
  const magnitude = getDeltaMagnitude(delta);
  const baseDuration = SCORE_DELTA_CONFIG.durations.popup;
  
  const multipliers: Record<string, number> = {
    minor: 0.8,
    moderate: 1.0,
    major: 1.3,
    exceptional: 1.5,
  };
  
  return baseDuration * (multipliers[magnitude] || 1);
}

// ============================================================================
// VALIDATION UTILITIES
// ============================================================================

/**
 * Get validation state configuration
 */
export function getValidationConfig(state: ValidationStateId) {
  return VALIDATION_STATES[state];
}

/**
 * Check if all fields are valid
 */
export function areAllFieldsValid(
  fields: Record<string, { state: ValidationStateId }>
): boolean {
  return Object.values(fields).every(field => field.state === 'valid');
}

/**
 * Get invalid field count
 */
export function getInvalidFieldCount(
  fields: Record<string, { state: ValidationStateId }>
): number {
  return Object.values(fields).filter(field => field.state === 'invalid').length;
}

/**
 * Get validation summary
 */
export function getValidationSummary(
  fields: Record<string, { state: ValidationStateId }>
): { valid: number; invalid: number; empty: number; total: number } {
  const values = Object.values(fields);
  return {
    valid: values.filter(f => f.state === 'valid').length,
    invalid: values.filter(f => f.state === 'invalid').length,
    empty: values.filter(f => f.state === 'empty').length,
    total: values.length,
  };
}

// ============================================================================
// TOAST UTILITIES
// ============================================================================

/**
 * Get toast configuration
 */
export function getToastConfig(type: ToastTypeId) {
  return TOAST_CONFIG.types[type];
}

/**
 * Get default toast duration
 */
export function getToastDuration(type: ToastTypeId): number {
  return TOAST_CONFIG.types[type].defaultDuration;
}

/**
 * Should toast auto-dismiss
 */
export function shouldAutoDisiss(type: ToastTypeId): boolean {
  return TOAST_CONFIG.types[type].defaultDuration > 0;
}

// ============================================================================
// ACHIEVEMENT UTILITIES
// ============================================================================

/**
 * Get achievement rarity configuration
 */
export function getAchievementRarityConfig(rarity: AchievementRarity) {
  return ACHIEVEMENT_CONFIG.rarities[rarity];
}

/**
 * Get achievement sound effect
 */
export function getAchievementSound(rarity: AchievementRarity): string {
  return ACHIEVEMENT_CONFIG.sounds[rarity];
}

/**
 * Format achievement unlock time
 */
export function formatUnlockTime(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

// ============================================================================
// HINT UTILITIES
// ============================================================================

/**
 * Get hint type configuration
 */
export function getHintConfig(type: keyof typeof HINT_CONFIG.types) {
  return HINT_CONFIG.types[type];
}

/**
 * Sort hints by priority
 */
export function sortHintsByPriority(hints: Array<{ priority?: number }>): Array<{ priority?: number }> {
  return [...hints].sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0));
}

/**
 * Filter expired hints
 */
export function filterExpiredHints<T extends { expiresAt?: number }>(hints: T[]): T[] {
  const now = Date.now();
  return hints.filter(hint => !hint.expiresAt || hint.expiresAt > now);
}

// ============================================================================
// ANIMATION UTILITIES
// ============================================================================

/**
 * Calculate popup position with boundary checks
 */
export function calculatePopupPosition(
  position: { x: number; y: number },
  popupSize: { width: number; height: number },
  viewport: { width: number; height: number },
  offset: { x: number; y: number } = { x: 0, y: -20 }
): { x: number; y: number } {
  let x = position.x + offset.x;
  let y = position.y + offset.y;
  
  // Boundary checks
  if (x + popupSize.width > viewport.width) {
    x = viewport.width - popupSize.width - 10;
  }
  if (x < 10) {
    x = 10;
  }
  if (y + popupSize.height > viewport.height) {
    y = viewport.height - popupSize.height - 10;
  }
  if (y < 10) {
    y = 10;
  }
  
  return { x, y };
}

/**
 * Calculate trail path points
 */
export function calculateTrailPath(
  from: { x: number; y: number },
  to: { x: number; y: number },
  segments: number = 10
): Array<{ x: number; y: number }> {
  const points: Array<{ x: number; y: number }> = [];
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    // Add slight curve using quadratic bezier-like interpolation
    const curveOffset = Math.sin(t * Math.PI) * 30;
    points.push({
      x: from.x + dx * t + curveOffset,
      y: from.y + dy * t,
    });
  }
  
  return points;
}

/**
 * Stagger delay for multiple items
 */
export function staggerDelay(index: number, baseDelay: number = 50): number {
  return index * baseDelay;
}

// ============================================================================
// HAPTIC FEEDBACK
// ============================================================================

/**
 * Trigger haptic feedback (mobile)
 */
export function triggerHaptic(type: 'light' | 'medium' | 'heavy' = 'light'): void {
  if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
    const durations: Record<string, number> = {
      light: 10,
      medium: 25,
      heavy: 50,
    };
    navigator.vibrate(durations[type]);
  }
}

// ============================================================================
// SOUND EFFECTS
// ============================================================================

/**
 * Play sound effect
 */
export function playSound(soundId: string, volume: number = 0.5): void {
  // Sound implementation would go here
  // This is a placeholder for the actual audio system
  console.log(`[Sound] Playing: ${soundId} at volume ${volume}`);
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  // ID
  generateFeedbackId,
  
  // Score Delta
  getDeltaMagnitude,
  getDeltaColors,
  getDeltaSize,
  getCategoryColors,
  formatDelta,
  getAnimationDuration,
  
  // Validation
  getValidationConfig,
  areAllFieldsValid,
  getInvalidFieldCount,
  getValidationSummary,
  
  // Toast
  getToastConfig,
  getToastDuration,
  shouldAutoDisiss,
  
  // Achievement
  getAchievementRarityConfig,
  getAchievementSound,
  formatUnlockTime,
  
  // Hint
  getHintConfig,
  sortHintsByPriority,
  filterExpiredHints,
  
  // Animation
  calculatePopupPosition,
  calculateTrailPath,
  staggerDelay,
  
  // Feedback
  triggerHaptic,
  playSound,
};
