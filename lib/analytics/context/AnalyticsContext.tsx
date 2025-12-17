/**
 * IvyQuest v3.0 — Analytics Context
 * 
 * Central state management for analytics.
 * 
 * @version 1.0.0
 * @module context/AnalyticsContext
 */

'use client';

import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useMemo,
  useCallback,
} from 'react';
import { SessionTracker } from '../trackers/SessionTracker';
import { FrameTracker, ScoreTracker } from '../trackers/FrameTracker';
import {
  generateSessionId,
  generateInsights,
  analyzeScoreEvolution,
  exportToJSON,
  exportToCSV,
} from '../utils/analyticsUtils';
import { ANALYTICS_CONFIG } from '../constants/analytics.constants';
import type {
  AnalyticsContextValue,
  AnalyticsProviderProps,
  AnalyticsConfig,
  AnalyticsEvent,
  SessionMetrics,
  FrameMetrics,
  ScoreEvolution,
  InsightAnalysis,
  ExportFormat,
} from '../types/analytics.types';

// ============================================================================
// DEFAULT CONFIG
// ============================================================================

const defaultConfig: AnalyticsConfig = {
  enableTracking: true,
  trackInteractions: true,
  trackTiming: true,
  anonymize: false,
  sampleRate: 1.0,
};

// ============================================================================
// CONTEXT
// ============================================================================

const AnalyticsContext = createContext<AnalyticsContextValue | null>(null);

// ============================================================================
// PROVIDER
// ============================================================================

export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({
  children,
  config = {},
  questId,
}) => {
  const mergedConfig = { ...defaultConfig, ...config };
  const sessionIdRef = useRef<string>(questId || generateSessionId());
  
  // Event batch
  const eventBatch = useRef<AnalyticsEvent[]>([]);
  const batchTimeout = useRef<NodeJS.Timeout | null>(null);
  
  // Event handler
  const handleEvent = useCallback((event: AnalyticsEvent) => {
    if (!mergedConfig.enableTracking) return;
    
    // Sample rate check
    if (Math.random() > (mergedConfig.sampleRate || 1)) return;
    
    // Add to batch
    eventBatch.current.push(event);
    
    // Immediate callback
    mergedConfig.onEvent?.(event);
    
    // Batch processing
    if (ANALYTICS_CONFIG.enableBatching) {
      if (eventBatch.current.length >= ANALYTICS_CONFIG.batchSize) {
        flushBatch();
      } else if (!batchTimeout.current) {
        batchTimeout.current = setTimeout(flushBatch, ANALYTICS_CONFIG.batchTimeout);
      }
    }
  }, [mergedConfig]);
  
  // Flush batch
  const flushBatch = useCallback(async () => {
    if (batchTimeout.current) {
      clearTimeout(batchTimeout.current);
      batchTimeout.current = null;
    }
    
    if (eventBatch.current.length === 0) return;
    
    const batch = [...eventBatch.current];
    eventBatch.current = [];
    
    await mergedConfig.onBatch?.(batch);
  }, [mergedConfig]);
  
  // Initialize trackers
  const sessionTracker = useRef<SessionTracker>(
    new SessionTracker(sessionIdRef.current, handleEvent)
  );
  
  const frameTracker = useRef<FrameTracker>(
    new FrameTracker(sessionIdRef.current, handleEvent)
  );
  
  const scoreTracker = useRef<ScoreTracker>(
    new ScoreTracker(sessionIdRef.current, handleEvent)
  );
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      sessionTracker.current.destroy();
      flushBatch();
    };
  }, [flushBatch]);
  
  // ============================================================================
  // TRACKING METHODS
  // ============================================================================
  
  const trackEvent = useCallback((
    type: string,
    data?: Record<string, unknown>
  ) => {
    if (!mergedConfig.enableTracking) return;
    
    handleEvent({
      id: `evt_${Date.now()}`,
      type: type as any,
      timestamp: Date.now(),
      sessionId: sessionIdRef.current,
      data: data || {},
    });
  }, [mergedConfig.enableTracking, handleEvent]);
  
  const trackFrameNavigation = useCallback((
    fromFrame: number,
    toFrame: number
  ) => {
    if (!mergedConfig.enableTracking) return;
    
    if (fromFrame >= 0) {
      frameTracker.current.exitFrame(fromFrame);
    }
    frameTracker.current.enterFrame(toFrame);
    sessionTracker.current.recordInteraction();
  }, [mergedConfig.enableTracking]);
  
  const trackFieldInteraction = useCallback((
    fieldId: string,
    action: 'focus' | 'blur' | 'change',
    value?: unknown
  ) => {
    if (!mergedConfig.enableTracking || !mergedConfig.trackInteractions) return;
    
    const currentFrame = frameTracker.current.getCurrentFrame();
    frameTracker.current.recordInteraction(currentFrame);
    
    if (action === 'change') {
      sessionTracker.current.recordFieldEdit();
    } else {
      sessionTracker.current.recordInteraction();
    }
    
    trackEvent(`field_${action}`, { fieldId, value });
  }, [mergedConfig, trackEvent]);
  
  const trackScoreChange = useCallback((
    category: string,
    oldScore: number,
    newScore: number,
    trigger: string
  ) => {
    if (!mergedConfig.enableTracking) return;
    
    const currentFrame = frameTracker.current.getCurrentFrame();
    scoreTracker.current.recordScoreUpdate(
      currentFrame,
      { [category]: newScore },
      trigger
    );
  }, [mergedConfig.enableTracking]);
  
  // ============================================================================
  // GETTERS
  // ============================================================================
  
  const getSessionMetrics = useCallback((): SessionMetrics => {
    return sessionTracker.current.getMetrics();
  }, []);
  
  const getFrameMetrics = useCallback((
    frameId?: number
  ): FrameMetrics | FrameMetrics[] => {
    return frameTracker.current.getFrameMetrics(frameId);
  }, []);
  
  const getScoreHistory = useCallback((): ScoreEvolution => {
    const history = scoreTracker.current.getHistory();
    return analyzeScoreEvolution(history);
  }, []);
  
  const getInsights = useCallback((): InsightAnalysis => {
    const metrics = sessionTracker.current.getMetrics();
    const frameMetrics = frameTracker.current.getFrameMetrics() as FrameMetrics[];
    const scoreHistory = scoreTracker.current.getHistory();
    const currentScores = scoreTracker.current.getCurrentScores();
    
    const insights = generateInsights(metrics, frameMetrics, scoreHistory, currentScores);
    
    return {
      insights,
      strengths: insights.filter(i => i.type === 'strength').map(i => i.title),
      improvements: insights.filter(i => i.type === 'improvement').map(i => i.title),
      suggestions: insights.filter(i => i.type === 'suggestion').map(i => i.title),
      achievements: insights.filter(i => i.type === 'achievement').map(i => i.title),
    };
  }, []);
  
  // ============================================================================
  // EXPORT
  // ============================================================================
  
  const exportReport = useCallback(async (
    format: ExportFormat
  ): Promise<string | Blob> => {
    const report = {
      questId: sessionIdRef.current,
      generatedAt: Date.now(),
      metrics: getSessionMetrics(),
      frameMetrics: getFrameMetrics() as FrameMetrics[],
      scoreEvolution: getScoreHistory(),
      insights: getInsights(),
    };
    
    switch (format) {
      case 'json':
        return exportToJSON(report);
      
      case 'csv': {
        const headers = ['Frame', 'Duration (min)', 'Completion %', 'Interactions'];
        const rows = (report.frameMetrics as FrameMetrics[]).map(f => [
          f.frameName,
          Math.round(f.duration / 60000),
          f.completionPercentage,
          f.interactions,
        ]);
        return exportToCSV(headers, rows);
      }
      
      case 'pdf':
        // PDF generation would require additional library
        return exportToJSON(report);
      
      default:
        return exportToJSON(report);
    }
  }, [getSessionMetrics, getFrameMetrics, getScoreHistory, getInsights]);
  
  const flush = useCallback(async () => {
    await flushBatch();
  }, [flushBatch]);
  
  // ============================================================================
  // CONTEXT VALUE
  // ============================================================================
  
  const value = useMemo<AnalyticsContextValue>(() => ({
    sessionId: sessionIdRef.current,
    isTracking: mergedConfig.enableTracking ?? true,
    trackEvent,
    trackFrameNavigation,
    trackFieldInteraction,
    trackScoreChange,
    getSessionMetrics,
    getFrameMetrics,
    getScoreHistory,
    getInsights,
    exportReport,
    flush,
  }), [
    mergedConfig.enableTracking,
    trackEvent,
    trackFrameNavigation,
    trackFieldInteraction,
    trackScoreChange,
    getSessionMetrics,
    getFrameMetrics,
    getScoreHistory,
    getInsights,
    exportReport,
    flush,
  ]);
  
  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
};

// ============================================================================
// HOOKS
// ============================================================================

export function useAnalytics(): AnalyticsContextValue {
  const context = useContext(AnalyticsContext);
  
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  
  return context;
}

export function useSessionMetrics() {
  const { getSessionMetrics, getFrameMetrics } = useAnalytics();
  const [metrics, setMetrics] = React.useState(getSessionMetrics());
  const [frameMetrics, setFrameMetrics] = React.useState(getFrameMetrics() as FrameMetrics[]);
  
  const refresh = useCallback(() => {
    setMetrics(getSessionMetrics());
    setFrameMetrics(getFrameMetrics() as FrameMetrics[]);
  }, [getSessionMetrics, getFrameMetrics]);
  
  return {
    metrics,
    frameMetrics,
    isLoading: false,
    refresh,
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export { AnalyticsContext };
export default AnalyticsProvider;
