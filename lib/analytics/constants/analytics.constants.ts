/**
 * IvyQuest v3.0 — Session Analytics Constants
 * 
 * Event types, thresholds, and configuration.
 * 
 * @version 1.0.0
 * @module lib/constants/analytics.constants
 */

// ============================================================================
// EVENT TYPES
// ============================================================================

export const SESSION_EVENTS = {
  SESSION_START: 'session_start',
  SESSION_PAUSE: 'session_pause',
  SESSION_RESUME: 'session_resume',
  SESSION_END: 'session_end',
  SESSION_ABANDON: 'session_abandon',
} as const;

export const FRAME_EVENTS = {
  FRAME_ENTER: 'frame_enter',
  FRAME_EXIT: 'frame_exit',
  FRAME_COMPLETE: 'frame_complete',
  FRAME_SKIP_ATTEMPT: 'frame_skip_attempt',
  CARD_ENTER: 'card_enter',
  CARD_EXIT: 'card_exit',
  CARD_COMPLETE: 'card_complete',
} as const;

export const INTERACTION_EVENTS = {
  FIELD_FOCUS: 'field_focus',
  FIELD_BLUR: 'field_blur',
  FIELD_CHANGE: 'field_change',
  SELECTION_MADE: 'selection_made',
  BUTTON_CLICK: 'button_click',
  NAVIGATION_CLICK: 'navigation_click',
  VALIDATION_ERROR: 'validation_error',
  VALIDATION_SUCCESS: 'validation_success',
} as const;

export const SCORE_EVENTS = {
  SCORE_CALCULATED: 'score_calculated',
  SCORE_UPDATE: 'score_update',
  TIER_CHANGE: 'tier_change',
  SCHOOL_FIT_UPDATE: 'school_fit_update',
  BOOSTER_APPLIED: 'booster_applied',
  BOOSTER_REMOVED: 'booster_removed',
} as const;

export type SessionEventType = typeof SESSION_EVENTS[keyof typeof SESSION_EVENTS];
export type FrameEventType = typeof FRAME_EVENTS[keyof typeof FRAME_EVENTS];
export type InteractionEventType = typeof INTERACTION_EVENTS[keyof typeof INTERACTION_EVENTS];
export type ScoreEventType = typeof SCORE_EVENTS[keyof typeof SCORE_EVENTS];
export type AnalyticsEventType = SessionEventType | FrameEventType | InteractionEventType | ScoreEventType;

// ============================================================================
// TIMING THRESHOLDS
// ============================================================================

export const TIMING_THRESHOLDS = {
  /** Minimum time before considering field interaction valid (ms) */
  MIN_INTERACTION_TIME: 100,
  
  /** Time before considering user hesitating on field (ms) */
  HESITATION_THRESHOLD: 10000,
  
  /** Time before considering session idle (ms) */
  IDLE_THRESHOLD: 60000,
  
  /** Time before session considered abandoned (ms) */
  ABANDON_THRESHOLD: 1800000, // 30 minutes
  
  /** Debounce time for field change events (ms) */
  FIELD_CHANGE_DEBOUNCE: 500,
  
  /** Minimum pause duration to track (ms) */
  MIN_PAUSE_DURATION: 1000,
  
  /** Expected time per frame (ms) */
  EXPECTED_FRAME_TIMES: {
    0: 180000,  // 3 minutes
    1: 300000,  // 5 minutes
    2: 420000,  // 7 minutes
    3: 240000,  // 4 minutes
    4: 120000,  // 2 minutes
    5: 300000,  // 5 minutes
  },
} as const;

// ============================================================================
// FRAME CONFIGURATION
// ============================================================================

export const FRAME_CONFIG = {
  0: {
    id: 0,
    name: 'Warm-Up',
    cards: ['role', 'name', 'grade', 'targets'],
    expectedDuration: 180000,
  },
  1: {
    id: 1,
    name: 'Snapshot',
    cards: ['academics', 'testing', 'strengths'],
    expectedDuration: 300000,
  },
  2: {
    id: 2,
    name: 'Spike',
    cards: ['activities', 'spike', 'achievements'],
    expectedDuration: 420000,
  },
  3: {
    id: 3,
    name: 'Operating',
    cards: ['workstyle', 'preferences', 'capabilities'],
    expectedDuration: 240000,
  },
  4: {
    id: 4,
    name: 'Reveal',
    cards: ['scores', 'breakdown', 'schools'],
    expectedDuration: 120000,
  },
  5: {
    id: 5,
    name: 'Power-Ups',
    cards: ['boosters', 'plan', 'summary'],
    expectedDuration: 300000,
  },
} as const;

// ============================================================================
// ANALYTICS CONFIGURATION
// ============================================================================

export const ANALYTICS_CONFIG = {
  /** Enable event batching */
  enableBatching: true,
  
  /** Batch size before flush */
  batchSize: 10,
  
  /** Max time before batch flush (ms) */
  batchTimeout: 5000,
  
  /** Store events locally */
  enableLocalStorage: true,
  
  /** Local storage key */
  storageKey: 'ivyquest_analytics',
  
  /** Max events to store locally */
  maxLocalEvents: 1000,
  
  /** Sample rate (1 = 100%) */
  sampleRate: 1.0,
} as const;

// ============================================================================
// INSIGHT THRESHOLDS
// ============================================================================

export const INSIGHT_THRESHOLDS = {
  /** Score difference to highlight */
  SIGNIFICANT_SCORE_DIFF: 10,
  
  /** Probability threshold for "good fit" */
  GOOD_FIT_PROBABILITY: 25,
  
  /** Minimum activities for "engaged" badge */
  MIN_ACTIVITIES_ENGAGED: 3,
  
  /** Leadership roles for "leader" badge */
  MIN_LEADERSHIP_ROLES: 2,
  
  /** Awards for "accomplished" badge */
  MIN_AWARDS: 2,
  
  /** Time ratio to flag "rushed" */
  RUSHED_TIME_RATIO: 0.5,
  
  /** Time ratio to flag "thorough" */
  THOROUGH_TIME_RATIO: 1.5,
} as const;

// ============================================================================
// CHART COLORS
// ============================================================================

export const CHART_COLORS = {
  primary: '#00D4FF',
  secondary: '#3B82F6',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  
  frames: {
    0: '#06B6D4', // Cyan
    1: '#3B82F6', // Blue
    2: '#F59E0B', // Amber
    3: '#8B5CF6', // Purple
    4: '#10B981', // Emerald
    5: '#EC4899', // Pink
  },
  
  scores: {
    aptitude: '#3B82F6',
    passion: '#F59E0B',
    community: '#10B981',
    operating: '#8B5CF6',
    ivyReady: '#00D4FF',
  },
  
  tiers: {
    exceptional: '#FFD700',
    competitive: '#00D4FF',
    average: '#3B82F6',
    developing: '#6B7280',
  },
} as const;

// ============================================================================
// REPORT CONFIGURATION
// ============================================================================

export const REPORT_CONFIG = {
  /** Show timeline by default */
  defaultShowTimeline: true,
  
  /** Show score evolution by default */
  defaultShowScoreEvolution: true,
  
  /** Show insights by default */
  defaultShowInsights: true,
  
  /** Export formats */
  exportFormats: ['json', 'csv', 'pdf'] as const,
  
  /** Chart animation duration (ms) */
  chartAnimationDuration: 1000,
  
  /** Chart height (px) */
  chartHeight: 200,
} as const;

export type ExportFormat = typeof REPORT_CONFIG.exportFormats[number];

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  SESSION_EVENTS,
  FRAME_EVENTS,
  INTERACTION_EVENTS,
  SCORE_EVENTS,
  TIMING_THRESHOLDS,
  FRAME_CONFIG,
  ANALYTICS_CONFIG,
  INSIGHT_THRESHOLDS,
  CHART_COLORS,
  REPORT_CONFIG,
};
