/**
 * IvyQuest v3.0 — Session Analytics Package
 * 
 * Tracking, metrics, and reporting for IvyQuest sessions.
 * 
 * @version 1.0.0
 * @module @ivyquest/session-analytics
 */

// ============================================================================
// CONTEXT & HOOKS
// ============================================================================

export {
  AnalyticsProvider,
  AnalyticsContext,
  useAnalytics,
  useSessionMetrics,
} from './context/AnalyticsContext';

// ============================================================================
// TRACKERS
// ============================================================================

export { SessionTracker } from './trackers/SessionTracker';
export { FrameTracker, ScoreTracker } from './trackers/FrameTracker';
export { InteractionTracker } from './trackers/InteractionTracker';

// ============================================================================
// REPORTER COMPONENTS
// ============================================================================

export {
  SessionReport,
  ProgressChart,
  TimeBreakdown,
  InsightsPanel,
} from './reporters/SessionReport';

// ============================================================================
// CONSTANTS
// ============================================================================

export {
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
  type SessionEventType,
  type FrameEventType,
  type InteractionEventType,
  type ScoreEventType,
  type AnalyticsEventType,
  type ExportFormat,
} from './constants/analytics.constants';

// ============================================================================
// UTILITIES
// ============================================================================

export {
  // ID
  generateEventId,
  generateSessionId,
  
  // Time
  formatDuration,
  formatDurationShort,
  getTimeCategory,
  
  // Device
  getDeviceType,
  getBrowserInfo,
  
  // Metrics
  calculateCompletionPercentage,
  calculateFrameProgress,
  calculateActiveDuration,
  calculateAverageFrameTime,
  
  // Score
  analyzeScoreEvolution,
  getScoreTrend,
  
  // Insights
  generateInsights,
  generateTimeline,
  
  // Chart
  getFrameChartData,
  getScoreChartData,
  
  // Export
  exportToJSON,
  exportToCSV,
  
  // Storage
  saveToLocalStorage,
  loadFromLocalStorage,
} from './utils/analyticsUtils';

// ============================================================================
// TYPES
// ============================================================================

export type {
  // Events
  AnalyticsEvent,
  SessionStartEvent,
  FrameEvent,
  InteractionEvent,
  ScoreEvent,
  
  // Metrics
  SessionMetrics,
  FrameMetrics,
  CardMetrics,
  HesitationEvent,
  
  // Score
  ScoreSnapshot,
  ScoreHistoryEntry,
  ScoreEvolution,
  
  // Insights
  SessionInsight,
  InsightAnalysis,
  
  // Report
  SessionReport as SessionReportType,
  TimelineEntry,
  
  // Context
  AnalyticsConfig,
  AnalyticsContextValue,
  AnalyticsProviderProps,
  
  // Hooks
  UseAnalyticsReturn,
  UseSessionMetricsReturn,
  
  // Components
  SessionReportProps,
  ProgressChartProps,
  TimeBreakdownProps,
  InsightsPanelProps,
} from './types/analytics.types';
