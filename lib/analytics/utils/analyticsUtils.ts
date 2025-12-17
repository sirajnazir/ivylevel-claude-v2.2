/**
 * IvyQuest v3.0 — Analytics Utilities
 * 
 * Helper functions for metrics and insights.
 * 
 * @version 1.0.0
 * @module lib/utils/analyticsUtils
 */

import {
  TIMING_THRESHOLDS,
  FRAME_CONFIG,
  INSIGHT_THRESHOLDS,
  CHART_COLORS,
} from '../constants/analytics.constants';
import type {
  SessionMetrics,
  FrameMetrics,
  ScoreHistoryEntry,
  ScoreEvolution,
  SessionInsight,
  TimelineEntry,
} from '../types/analytics.types';

// ============================================================================
// ID GENERATION
// ============================================================================

export function generateEventId(): string {
  return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export function generateSessionId(): string {
  return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// ============================================================================
// TIME UTILITIES
// ============================================================================

export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours}:${(minutes % 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
  }
  return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`;
}

export function formatDurationShort(ms: number): string {
  const minutes = Math.round(ms / 60000);
  if (minutes < 1) return '<1m';
  if (minutes >= 60) return `${Math.round(minutes / 60)}h`;
  return `${minutes}m`;
}

export function getTimeCategory(duration: number, expectedDuration: number): 'fast' | 'normal' | 'slow' {
  const ratio = duration / expectedDuration;
  if (ratio < INSIGHT_THRESHOLDS.RUSHED_TIME_RATIO) return 'fast';
  if (ratio > INSIGHT_THRESHOLDS.THOROUGH_TIME_RATIO) return 'slow';
  return 'normal';
}

// ============================================================================
// DEVICE DETECTION
// ============================================================================

export function getDeviceType(): 'desktop' | 'tablet' | 'mobile' {
  if (typeof window === 'undefined') return 'desktop';
  
  const width = window.innerWidth;
  if (width < 768) return 'mobile';
  if (width < 1024) return 'tablet';
  return 'desktop';
}

export function getBrowserInfo(): string {
  if (typeof navigator === 'undefined') return 'unknown';
  
  const ua = navigator.userAgent;
  let browser = 'Unknown';
  
  if (ua.includes('Chrome')) browser = 'Chrome';
  else if (ua.includes('Firefox')) browser = 'Firefox';
  else if (ua.includes('Safari')) browser = 'Safari';
  else if (ua.includes('Edge')) browser = 'Edge';
  
  return browser;
}

// ============================================================================
// METRICS CALCULATIONS
// ============================================================================

export function calculateCompletionPercentage(
  framesCompleted: number,
  totalFrames: number = 6
): number {
  return Math.round((framesCompleted / totalFrames) * 100);
}

export function calculateFrameProgress(frameMetrics: FrameMetrics[]): number {
  const total = frameMetrics.length;
  const completed = frameMetrics.filter(f => f.isComplete).length;
  return Math.round((completed / total) * 100);
}

export function calculateActiveDuration(
  totalDuration: number,
  pauseTotalDuration: number
): number {
  return Math.max(0, totalDuration - pauseTotalDuration);
}

export function calculateAverageFrameTime(frameMetrics: FrameMetrics[]): number {
  const completedFrames = frameMetrics.filter(f => f.duration > 0);
  if (completedFrames.length === 0) return 0;
  
  const totalTime = completedFrames.reduce((sum, f) => sum + f.duration, 0);
  return Math.round(totalTime / completedFrames.length);
}

// ============================================================================
// SCORE ANALYSIS
// ============================================================================

export function analyzeScoreEvolution(history: ScoreHistoryEntry[]): ScoreEvolution {
  if (history.length === 0) {
    return {
      entries: [],
      peakScore: 0,
      peakTimestamp: 0,
      finalScore: 0,
      totalGain: 0,
    };
  }
  
  let peakScore = 0;
  let peakTimestamp = 0;
  
  history.forEach(entry => {
    if (entry.scores.ivyReady > peakScore) {
      peakScore = entry.scores.ivyReady;
      peakTimestamp = entry.timestamp;
    }
  });
  
  const firstEntry = history[0];
  const lastEntry = history[history.length - 1];
  
  return {
    entries: history,
    peakScore,
    peakTimestamp,
    finalScore: lastEntry.scores.ivyReady,
    totalGain: lastEntry.scores.ivyReady - (firstEntry.scores.ivyReady || 0),
  };
}

export function getScoreTrend(history: ScoreHistoryEntry[]): 'up' | 'down' | 'stable' {
  if (history.length < 2) return 'stable';
  
  const recent = history.slice(-5);
  const first = recent[0].scores.ivyReady;
  const last = recent[recent.length - 1].scores.ivyReady;
  
  const diff = last - first;
  if (diff > 5) return 'up';
  if (diff < -5) return 'down';
  return 'stable';
}

// ============================================================================
// INSIGHT GENERATION
// ============================================================================

export function generateInsights(
  metrics: SessionMetrics,
  frameMetrics: FrameMetrics[],
  scoreHistory: ScoreHistoryEntry[],
  finalScores: { aptitude: number; passion: number; community: number; operating: number; ivyReady: number }
): SessionInsight[] {
  const insights: SessionInsight[] = [];
  
  // Score-based insights
  if (finalScores.aptitude >= 80) {
    insights.push({
      id: 'strong_academics',
      type: 'strength',
      category: 'academic',
      title: 'Strong Academic Foundation',
      description: 'Your academic profile is highly competitive for top universities.',
      priority: 1,
    });
  }
  
  if (finalScores.passion >= 80) {
    insights.push({
      id: 'passionate_engagement',
      type: 'strength',
      category: 'activities',
      title: 'Passionate Engagement',
      description: 'Your spike and activities show genuine passion and depth.',
      priority: 1,
    });
  }
  
  if (finalScores.community < 60) {
    insights.push({
      id: 'improve_community',
      type: 'improvement',
      category: 'activities',
      title: 'Consider Leadership Opportunities',
      description: 'Adding leadership roles or community impact could strengthen your profile.',
      priority: 2,
    });
  }
  
  // Time-based insights
  const avgTime = calculateAverageFrameTime(frameMetrics);
  const expectedAvg = Object.values(FRAME_CONFIG).reduce((sum, f) => sum + f.expectedDuration, 0) / 6;
  
  if (avgTime < expectedAvg * 0.5) {
    insights.push({
      id: 'rushed_completion',
      type: 'suggestion',
      category: 'overall',
      title: 'Take Your Time',
      description: 'You completed the assessment quickly. Consider reviewing your responses.',
      priority: 3,
    });
  }
  
  // Score progress insight
  if (scoreHistory.length > 0) {
    const evolution = analyzeScoreEvolution(scoreHistory);
    if (evolution.totalGain >= 20) {
      insights.push({
        id: 'significant_progress',
        type: 'achievement',
        category: 'overall',
        title: 'Significant Progress',
        description: `Your Ivy+ Ready Score improved by ${evolution.totalGain} points during the assessment.`,
        priority: 2,
      });
    }
  }
  
  return insights.sort((a, b) => a.priority - b.priority);
}

// ============================================================================
// TIMELINE GENERATION
// ============================================================================

export function generateTimeline(
  frameMetrics: FrameMetrics[],
  scoreHistory: ScoreHistoryEntry[]
): TimelineEntry[] {
  const entries: TimelineEntry[] = [];
  
  // Add frame events
  frameMetrics.forEach(frame => {
    if (frame.enteredAt) {
      entries.push({
        timestamp: frame.enteredAt,
        type: 'frame',
        label: `Started ${frame.frameName}`,
        duration: frame.duration,
      });
    }
    
    if (frame.completedAt) {
      entries.push({
        timestamp: frame.completedAt,
        type: 'milestone',
        label: `Completed ${frame.frameName}`,
        description: `Duration: ${formatDuration(frame.duration)}`,
      });
    }
  });
  
  // Add significant score changes
  scoreHistory.forEach((entry, index) => {
    if (index === 0) return;
    
    const prevEntry = scoreHistory[index - 1];
    const delta = entry.scores.ivyReady - prevEntry.scores.ivyReady;
    
    if (Math.abs(delta) >= INSIGHT_THRESHOLDS.SIGNIFICANT_SCORE_DIFF) {
      entries.push({
        timestamp: entry.timestamp,
        type: 'score',
        label: `Score ${delta > 0 ? 'increased' : 'decreased'} by ${Math.abs(delta)}`,
        description: entry.trigger,
        data: { delta, newScore: entry.scores.ivyReady },
      });
    }
  });
  
  // Sort by timestamp
  return entries.sort((a, b) => a.timestamp - b.timestamp);
}

// ============================================================================
// CHART DATA HELPERS
// ============================================================================

export function getFrameChartData(frameMetrics: FrameMetrics[]) {
  return frameMetrics.map(frame => ({
    name: frame.frameName,
    duration: Math.round(frame.duration / 60000), // Convert to minutes
    expected: Math.round((FRAME_CONFIG[frame.frameId as keyof typeof FRAME_CONFIG]?.expectedDuration || 0) / 60000),
    completion: frame.completionPercentage,
    color: CHART_COLORS.frames[frame.frameId as keyof typeof CHART_COLORS.frames],
  }));
}

export function getScoreChartData(history: ScoreHistoryEntry[]) {
  return history.map(entry => ({
    timestamp: entry.timestamp,
    frameId: entry.frameId,
    aptitude: entry.scores.aptitude,
    passion: entry.scores.passion,
    community: entry.scores.community,
    operating: entry.scores.operating,
    ivyReady: entry.scores.ivyReady,
  }));
}

// ============================================================================
// EXPORT UTILITIES
// ============================================================================

export function exportToJSON(data: unknown): string {
  return JSON.stringify(data, null, 2);
}

export function exportToCSV(
  headers: string[],
  rows: (string | number)[][]
): string {
  const headerRow = headers.join(',');
  const dataRows = rows.map(row => row.join(','));
  return [headerRow, ...dataRows].join('\n');
}

// ============================================================================
// LOCAL STORAGE
// ============================================================================

export function saveToLocalStorage(key: string, data: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (e) {
    console.warn('Failed to save to localStorage:', e);
  }
}

export function loadFromLocalStorage<T>(key: string): T | null {
  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  } catch (e) {
    console.warn('Failed to load from localStorage:', e);
    return null;
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
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
};
