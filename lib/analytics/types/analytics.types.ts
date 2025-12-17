/**
 * IvyQuest v3.0 — Session Analytics Types
 * 
 * TypeScript interfaces for analytics tracking.
 * 
 * @version 1.0.0
 * @module lib/types/analytics.types
 */

import type {
  AnalyticsEventType,
  ExportFormat,
} from '../constants/analytics.constants';

// ============================================================================
// EVENT TYPES
// ============================================================================

export interface AnalyticsEvent {
  id: string;
  type: AnalyticsEventType;
  timestamp: number;
  sessionId: string;
  frameId?: number;
  cardId?: string;
  data: Record<string, unknown>;
}

export interface SessionStartEvent extends AnalyticsEvent {
  type: 'session_start';
  data: {
    deviceType: 'desktop' | 'tablet' | 'mobile';
    browserInfo: string;
    screenSize: { width: number; height: number };
    source?: string;
    referrer?: string;
  };
}

export interface FrameEvent extends AnalyticsEvent {
  type: 'frame_enter' | 'frame_exit' | 'frame_complete';
  data: {
    frameId: number;
    frameName: string;
    duration?: number;
    completionPercentage?: number;
    sourceFrame?: number;
  };
}

export interface InteractionEvent extends AnalyticsEvent {
  type: 'field_focus' | 'field_blur' | 'field_change' | 'selection_made';
  data: {
    fieldId: string;
    fieldType: string;
    value?: unknown;
    previousValue?: unknown;
    duration?: number;
  };
}

export interface ScoreEvent extends AnalyticsEvent {
  type: 'score_calculated' | 'score_update' | 'tier_change';
  data: {
    category?: string;
    oldScore?: number;
    newScore?: number;
    oldTier?: string;
    newTier?: string;
    trigger?: string;
  };
}

// ============================================================================
// METRICS TYPES
// ============================================================================

export interface SessionMetrics {
  questId: string;
  startedAt: number;
  lastActiveAt: number;
  completedAt?: number;
  
  totalDuration: number;
  activeDuration: number;
  pauseCount: number;
  pauseTotalDuration: number;
  
  framesCompleted: number;
  framesTotal: number;
  completionPercentage: number;
  
  interactionCount: number;
  fieldEdits: number;
  validationErrors: number;
  
  deviceType: 'desktop' | 'tablet' | 'mobile';
  browserInfo: string;
}

export interface FrameMetrics {
  frameId: number;
  frameName: string;
  
  enteredAt?: number;
  exitedAt?: number;
  completedAt?: number;
  duration: number;
  
  cardsCompleted: number;
  cardsTotal: number;
  completionPercentage: number;
  
  interactions: number;
  hesitations: HesitationEvent[];
  backTracks: number;
  
  isComplete: boolean;
  isCurrent: boolean;
}

export interface HesitationEvent {
  fieldId: string;
  startTime: number;
  duration: number;
  resolved: boolean;
}

export interface CardMetrics {
  cardId: string;
  frameId: number;
  
  enteredAt?: number;
  completedAt?: number;
  duration: number;
  
  fieldsCompleted: number;
  fieldsTotal: number;
  
  interactions: number;
  validationErrors: number;
}

// ============================================================================
// SCORE HISTORY TYPES
// ============================================================================

export interface ScoreSnapshot {
  aptitude: number;
  passion: number;
  community: number;
  operating: number;
  ivyReady: number;
}

export interface ScoreHistoryEntry {
  timestamp: number;
  frameId: number;
  cardId?: string;
  trigger: string;
  scores: ScoreSnapshot;
  delta: Partial<ScoreSnapshot>;
}

export interface ScoreEvolution {
  entries: ScoreHistoryEntry[];
  peakScore: number;
  peakTimestamp: number;
  finalScore: number;
  totalGain: number;
}

// ============================================================================
// INSIGHT TYPES
// ============================================================================

export interface SessionInsight {
  id: string;
  type: 'strength' | 'improvement' | 'suggestion' | 'achievement';
  category: 'academic' | 'activities' | 'operating' | 'overall';
  title: string;
  description: string;
  priority: number;
  data?: Record<string, unknown>;
}

export interface InsightAnalysis {
  insights: SessionInsight[];
  strengths: string[];
  improvements: string[];
  suggestions: string[];
  achievements: string[];
}

// ============================================================================
// REPORT TYPES
// ============================================================================

export interface SessionReport {
  questId: string;
  generatedAt: number;
  
  metrics: SessionMetrics;
  frameMetrics: FrameMetrics[];
  scoreEvolution: ScoreEvolution;
  insights: InsightAnalysis;
  
  timeline: TimelineEntry[];
}

export interface TimelineEntry {
  timestamp: number;
  type: 'frame' | 'milestone' | 'score' | 'interaction';
  label: string;
  description?: string;
  duration?: number;
  data?: Record<string, unknown>;
}

// ============================================================================
// CONTEXT TYPES
// ============================================================================

export interface AnalyticsConfig {
  /** Enable tracking */
  enableTracking?: boolean;
  
  /** Track field interactions */
  trackInteractions?: boolean;
  
  /** Track timing */
  trackTiming?: boolean;
  
  /** Anonymize data */
  anonymize?: boolean;
  
  /** Sample rate (0-1) */
  sampleRate?: number;
  
  /** Event callback */
  onEvent?: (event: AnalyticsEvent) => void | Promise<void>;
  
  /** Batch callback */
  onBatch?: (events: AnalyticsEvent[]) => void | Promise<void>;
}

export interface AnalyticsContextValue {
  /** Current session ID */
  sessionId: string;
  
  /** Is tracking enabled */
  isTracking: boolean;
  
  /** Track custom event */
  trackEvent: (type: AnalyticsEventType, data?: Record<string, unknown>) => void;
  
  /** Track frame navigation */
  trackFrameNavigation: (fromFrame: number, toFrame: number) => void;
  
  /** Track field interaction */
  trackFieldInteraction: (fieldId: string, action: 'focus' | 'blur' | 'change', value?: unknown) => void;
  
  /** Track score change */
  trackScoreChange: (category: string, oldScore: number, newScore: number, trigger: string) => void;
  
  /** Get session metrics */
  getSessionMetrics: () => SessionMetrics;
  
  /** Get frame metrics */
  getFrameMetrics: (frameId?: number) => FrameMetrics | FrameMetrics[];
  
  /** Get score history */
  getScoreHistory: () => ScoreEvolution;
  
  /** Get insights */
  getInsights: () => InsightAnalysis;
  
  /** Export report */
  exportReport: (format: ExportFormat) => Promise<string | Blob>;
  
  /** Flush pending events */
  flush: () => Promise<void>;
}

export interface AnalyticsProviderProps {
  children: React.ReactNode;
  config?: AnalyticsConfig;
  questId?: string;
}

// ============================================================================
// HOOK TYPES
// ============================================================================

export interface UseAnalyticsReturn extends AnalyticsContextValue {}

export interface UseSessionMetricsReturn {
  metrics: SessionMetrics;
  frameMetrics: FrameMetrics[];
  isLoading: boolean;
  refresh: () => void;
}

// ============================================================================
// COMPONENT PROPS
// ============================================================================

export interface SessionReportProps {
  questId?: string;
  showTimeline?: boolean;
  showScoreEvolution?: boolean;
  showInsights?: boolean;
  showFrameBreakdown?: boolean;
  onExport?: (format: ExportFormat) => void;
}

export interface ProgressChartProps {
  data: FrameMetrics[];
  type?: 'timeline' | 'bar' | 'pie';
  showLabels?: boolean;
  interactive?: boolean;
  height?: number;
  onFrameClick?: (frameId: number) => void;
}

export interface TimeBreakdownProps {
  frameMetrics: FrameMetrics[];
  showExpected?: boolean;
  showComparison?: boolean;
}

export interface InsightsPanelProps {
  insights: InsightAnalysis;
  showStrengths?: boolean;
  showImprovements?: boolean;
  showSuggestions?: boolean;
  maxItems?: number;
}

// ============================================================================
// RE-EXPORTS FROM CONSTANTS
// ============================================================================

export type {
  AnalyticsEventType,
  ExportFormat,
} from '../constants/analytics.constants';

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  // Types are exported individually
};
