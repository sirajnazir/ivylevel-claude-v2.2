/**
 * IvyQuest v3.0 — Feedback System Constants
 * 
 * Configuration for feedback types, animations, and thresholds.
 * 
 * @version 1.0.0
 * @module lib/constants/feedback.constants
 */

// ============================================================================
// SCORE DELTA CONFIGURATION
// ============================================================================

export const SCORE_DELTA_CONFIG = {
  // Thresholds
  thresholds: {
    minor: 3,      // 1-3 points
    moderate: 7,   // 4-7 points
    major: 10,     // 8-10 points
    exceptional: 15, // 11+ points
  },
  
  // Animation durations (ms)
  durations: {
    popup: 1500,
    trail: 800,
    fadeOut: 300,
  },
  
  // Size scaling
  sizes: {
    minor: { scale: 0.8, fontSize: 14 },
    moderate: { scale: 1.0, fontSize: 16 },
    major: { scale: 1.2, fontSize: 20 },
    exceptional: { scale: 1.5, fontSize: 24 },
  },
  
  // Colors by direction
  colors: {
    positive: {
      primary: '#10B981',    // Green
      secondary: '#34D399',
      glow: '#6EE7B7',
    },
    negative: {
      primary: '#EF4444',    // Red
      secondary: '#F87171',
      glow: '#FCA5A5',
    },
    neutral: {
      primary: '#6B7280',    // Gray
      secondary: '#9CA3AF',
      glow: '#D1D5DB',
    },
  },
} as const;

// ============================================================================
// VALIDATION STATES
// ============================================================================

export const VALIDATION_STATES = {
  empty: {
    id: 'empty',
    icon: null,
    borderColor: '#374151',
    backgroundColor: 'transparent',
    textColor: '#9CA3AF',
  },
  valid: {
    id: 'valid',
    icon: '✓',
    borderColor: '#10B981',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    textColor: '#10B981',
  },
  invalid: {
    id: 'invalid',
    icon: '✕',
    borderColor: '#EF4444',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    textColor: '#EF4444',
  },
  warning: {
    id: 'warning',
    icon: '⚠',
    borderColor: '#F59E0B',
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    textColor: '#F59E0B',
  },
  pending: {
    id: 'pending',
    icon: '⟳',
    borderColor: '#3B82F6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    textColor: '#3B82F6',
  },
} as const;

export type ValidationStateId = keyof typeof VALIDATION_STATES;

// ============================================================================
// TOAST CONFIGURATION
// ============================================================================

export const TOAST_CONFIG = {
  types: {
    info: {
      id: 'info',
      icon: 'ℹ️',
      backgroundColor: '#1E3A5F',
      borderColor: '#3B82F6',
      textColor: '#FFFFFF',
      defaultDuration: 3000,
    },
    success: {
      id: 'success',
      icon: '✅',
      backgroundColor: '#064E3B',
      borderColor: '#10B981',
      textColor: '#FFFFFF',
      defaultDuration: 4000,
    },
    warning: {
      id: 'warning',
      icon: '⚠️',
      backgroundColor: '#78350F',
      borderColor: '#F59E0B',
      textColor: '#FFFFFF',
      defaultDuration: 5000,
    },
    error: {
      id: 'error',
      icon: '❌',
      backgroundColor: '#7F1D1D',
      borderColor: '#EF4444',
      textColor: '#FFFFFF',
      defaultDuration: 0, // Manual dismiss
    },
  },
  
  // Position
  position: {
    top: 20,
    right: 20,
    gap: 12,
  },
  
  // Animation
  animation: {
    enter: 300,
    exit: 200,
    stagger: 50,
  },
  
  // Limits
  maxVisible: 5,
  maxQueue: 10,
} as const;

export type ToastTypeId = keyof typeof TOAST_CONFIG.types;

// ============================================================================
// ACHIEVEMENT CONFIGURATION
// ============================================================================

export const ACHIEVEMENT_CONFIG = {
  rarities: {
    common: {
      id: 'common',
      label: 'Common',
      borderColor: '#6B7280',
      glowColor: 'rgba(107, 114, 128, 0.3)',
      backgroundColor: '#1F2937',
    },
    uncommon: {
      id: 'uncommon',
      label: 'Uncommon',
      borderColor: '#10B981',
      glowColor: 'rgba(16, 185, 129, 0.3)',
      backgroundColor: '#064E3B',
    },
    rare: {
      id: 'rare',
      label: 'Rare',
      borderColor: '#3B82F6',
      glowColor: 'rgba(59, 130, 246, 0.3)',
      backgroundColor: '#1E3A5F',
    },
    epic: {
      id: 'epic',
      label: 'Epic',
      borderColor: '#8B5CF6',
      glowColor: 'rgba(139, 92, 246, 0.4)',
      backgroundColor: '#4C1D95',
    },
    legendary: {
      id: 'legendary',
      label: 'Legendary',
      borderColor: '#FFD700',
      glowColor: 'rgba(255, 215, 0, 0.5)',
      backgroundColor: '#78350F',
    },
  },
  
  // Animation
  animation: {
    entrance: 500,
    hold: 4000,
    exit: 300,
  },
  
  // Sounds
  sounds: {
    common: 'achievement_common',
    uncommon: 'achievement_uncommon',
    rare: 'achievement_rare',
    epic: 'achievement_epic',
    legendary: 'achievement_legendary',
  },
} as const;

export type AchievementRarity = keyof typeof ACHIEVEMENT_CONFIG.rarities;

// ============================================================================
// MILESTONE DEFINITIONS
// ============================================================================

export const MILESTONES = {
  identity_complete: {
    id: 'identity_complete',
    title: 'Identity Locked In!',
    description: 'You\'ve established your basic profile.',
    icon: '🎯',
    frame: 0,
    animation: 'confetti',
  },
  academic_profile: {
    id: 'academic_profile',
    title: 'Academic Snapshot Captured!',
    description: 'Your academic profile is complete.',
    icon: '📊',
    frame: 1,
    animation: 'glow',
  },
  activities_logged: {
    id: 'activities_logged',
    title: 'Your Story Takes Shape!',
    description: 'Activities and involvement recorded.',
    icon: '✨',
    frame: 2,
    animation: 'stars',
  },
  spike_identified: {
    id: 'spike_identified',
    title: 'Spike Detected!',
    description: 'Your unique strength has been identified.',
    icon: '🔥',
    frame: 2,
    animation: 'fire',
  },
  operating_mapped: {
    id: 'operating_mapped',
    title: 'Operating Style Mapped!',
    description: 'We understand how you work.',
    icon: '⚡',
    frame: 3,
    animation: 'pulse',
  },
  scores_revealed: {
    id: 'scores_revealed',
    title: 'The Verdict Is In!',
    description: 'Your Ivy+ Ready Score has been calculated.',
    icon: '🎉',
    frame: 4,
    animation: 'reveal',
  },
  quest_complete: {
    id: 'quest_complete',
    title: 'Ready to Launch!',
    description: 'You\'ve completed the IvyQuest assessment.',
    icon: '🚀',
    frame: 5,
    animation: 'celebration',
  },
} as const;

export type MilestoneId = keyof typeof MILESTONES;

// ============================================================================
// HINT CONFIGURATION
// ============================================================================

export const HINT_CONFIG = {
  types: {
    tip: {
      id: 'tip',
      icon: '💡',
      backgroundColor: '#1E3A5F',
      borderColor: '#3B82F6',
      accentColor: '#60A5FA',
    },
    suggestion: {
      id: 'suggestion',
      icon: '✨',
      backgroundColor: '#064E3B',
      borderColor: '#10B981',
      accentColor: '#34D399',
    },
    warning: {
      id: 'warning',
      icon: '⚠️',
      backgroundColor: '#78350F',
      borderColor: '#F59E0B',
      accentColor: '#FBBF24',
    },
    boost: {
      id: 'boost',
      icon: '🚀',
      backgroundColor: '#4C1D95',
      borderColor: '#8B5CF6',
      accentColor: '#A78BFA',
    },
  },
  
  // Display settings
  display: {
    maxVisible: 2,
    defaultDuration: 8000,
    dismissDelay: 500,
  },
  
  // Position
  position: {
    bottom: 100,
    left: 20,
    maxWidth: 320,
  },
} as const;

export type HintTypeId = keyof typeof HINT_CONFIG.types;

// ============================================================================
// CATEGORY COLORS
// ============================================================================

export const CATEGORY_COLORS = {
  aptitude: {
    primary: '#3B82F6',    // Blue
    secondary: '#60A5FA',
    glow: '#93C5FD',
  },
  passion: {
    primary: '#F59E0B',    // Amber
    secondary: '#FBBF24',
    glow: '#FCD34D',
  },
  community: {
    primary: '#10B981',    // Emerald
    secondary: '#34D399',
    glow: '#6EE7B7',
  },
  operating: {
    primary: '#8B5CF6',    // Purple
    secondary: '#A78BFA',
    glow: '#C4B5FD',
  },
  ivyReady: {
    primary: '#00D4FF',    // Cyan
    secondary: '#22D3EE',
    glow: '#67E8F9',
  },
} as const;

export type ScoreCategory = keyof typeof CATEGORY_COLORS;

// ============================================================================
// ANIMATION PRESETS
// ============================================================================

export const ANIMATION_PRESETS = {
  bounce: {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0, opacity: 0 },
    transition: { type: 'spring', stiffness: 400, damping: 15 },
  },
  slide: {
    initial: { x: 50, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: -50, opacity: 0 },
    transition: { duration: 0.3 },
  },
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 },
  },
  pop: {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.8, opacity: 0 },
    transition: { type: 'spring', stiffness: 500, damping: 20 },
  },
  float: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 },
    transition: { duration: 0.4 },
  },
} as const;

export type AnimationPreset = keyof typeof ANIMATION_PRESETS;

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  SCORE_DELTA_CONFIG,
  VALIDATION_STATES,
  TOAST_CONFIG,
  ACHIEVEMENT_CONFIG,
  MILESTONES,
  HINT_CONFIG,
  CATEGORY_COLORS,
  ANIMATION_PRESETS,
};
