/**
 * IvyQuest v3.0 — Frame & Score Trackers
 * 
 * Track frame navigation and score changes.
 * 
 * @version 1.0.0
 * @module trackers/FrameTracker
 */

import {
  FRAME_EVENTS,
  SCORE_EVENTS,
  FRAME_CONFIG,
  TIMING_THRESHOLDS,
} from '../constants/analytics.constants';
import { generateEventId } from '../utils/analyticsUtils';
import type {
  AnalyticsEvent,
  FrameMetrics,
  HesitationEvent,
  ScoreHistoryEntry,
  ScoreSnapshot,
} from '../types/analytics.types';

// ============================================================================
// FRAME TRACKER
// ============================================================================

export class FrameTracker {
  private sessionId: string;
  private currentFrame: number = -1;
  private frameMetrics: Map<number, FrameMetrics> = new Map();
  private eventCallback?: (event: AnalyticsEvent) => void;
  
  constructor(sessionId: string, onEvent?: (event: AnalyticsEvent) => void) {
    this.sessionId = sessionId;
    this.eventCallback = onEvent;
    
    // Initialize frame metrics
    Object.keys(FRAME_CONFIG).forEach(key => {
      const frameId = parseInt(key);
      const config = FRAME_CONFIG[frameId as keyof typeof FRAME_CONFIG];
      
      this.frameMetrics.set(frameId, {
        frameId,
        frameName: config.name,
        duration: 0,
        cardsCompleted: 0,
        cardsTotal: config.cards.length,
        completionPercentage: 0,
        interactions: 0,
        hesitations: [],
        backTracks: 0,
        isComplete: false,
        isCurrent: false,
      });
    });
  }
  
  private emitEvent(type: string, data: Record<string, unknown> = {}): void {
    const event: AnalyticsEvent = {
      id: generateEventId(),
      type: type as any,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      frameId: this.currentFrame >= 0 ? this.currentFrame : undefined,
      data,
    };
    
    this.eventCallback?.(event);
  }
  
  enterFrame(frameId: number): void {
    const previousFrame = this.currentFrame;
    
    // Exit previous frame
    if (previousFrame >= 0 && previousFrame !== frameId) {
      this.exitFrame(previousFrame);
    }
    
    // Check for backtrack
    if (previousFrame > frameId) {
      const metrics = this.frameMetrics.get(previousFrame);
      if (metrics) {
        metrics.backTracks++;
      }
    }
    
    this.currentFrame = frameId;
    const metrics = this.frameMetrics.get(frameId);
    
    if (metrics) {
      metrics.enteredAt = metrics.enteredAt || Date.now();
      metrics.isCurrent = true;
      
      // Mark other frames as not current
      this.frameMetrics.forEach((m, id) => {
        if (id !== frameId) m.isCurrent = false;
      });
    }
    
    this.emitEvent(FRAME_EVENTS.FRAME_ENTER, {
      frameId,
      frameName: FRAME_CONFIG[frameId as keyof typeof FRAME_CONFIG]?.name,
      sourceFrame: previousFrame >= 0 ? previousFrame : undefined,
    });
  }
  
  exitFrame(frameId: number): void {
    const metrics = this.frameMetrics.get(frameId);
    
    if (metrics && metrics.enteredAt) {
      metrics.exitedAt = Date.now();
      metrics.duration += metrics.exitedAt - metrics.enteredAt;
      metrics.isCurrent = false;
      
      this.emitEvent(FRAME_EVENTS.FRAME_EXIT, {
        frameId,
        frameName: metrics.frameName,
        duration: metrics.duration,
        completionPercentage: metrics.completionPercentage,
      });
    }
  }
  
  completeFrame(frameId: number): void {
    const metrics = this.frameMetrics.get(frameId);
    
    if (metrics) {
      metrics.isComplete = true;
      metrics.completedAt = Date.now();
      metrics.completionPercentage = 100;
      
      if (metrics.enteredAt) {
        metrics.duration = metrics.completedAt - metrics.enteredAt;
      }
      
      this.emitEvent(FRAME_EVENTS.FRAME_COMPLETE, {
        frameId,
        frameName: metrics.frameName,
        duration: metrics.duration,
        interactions: metrics.interactions,
      });
    }
  }
  
  recordCardComplete(frameId: number, cardId: string): void {
    const metrics = this.frameMetrics.get(frameId);
    
    if (metrics) {
      metrics.cardsCompleted++;
      metrics.completionPercentage = Math.round(
        (metrics.cardsCompleted / metrics.cardsTotal) * 100
      );
      
      this.emitEvent(FRAME_EVENTS.CARD_COMPLETE, {
        frameId,
        cardId,
        cardsCompleted: metrics.cardsCompleted,
        cardsTotal: metrics.cardsTotal,
      });
    }
  }
  
  recordInteraction(frameId: number): void {
    const metrics = this.frameMetrics.get(frameId);
    if (metrics) {
      metrics.interactions++;
    }
  }
  
  recordHesitation(frameId: number, fieldId: string, duration: number): void {
    const metrics = this.frameMetrics.get(frameId);
    
    if (metrics && duration >= TIMING_THRESHOLDS.HESITATION_THRESHOLD) {
      metrics.hesitations.push({
        fieldId,
        startTime: Date.now() - duration,
        duration,
        resolved: false,
      });
    }
  }
  
  getCurrentFrame(): number {
    return this.currentFrame;
  }
  
  getFrameMetrics(frameId?: number): FrameMetrics | FrameMetrics[] {
    if (frameId !== undefined) {
      return this.frameMetrics.get(frameId) || this.createEmptyMetrics(frameId);
    }
    return Array.from(this.frameMetrics.values());
  }
  
  private createEmptyMetrics(frameId: number): FrameMetrics {
    const config = FRAME_CONFIG[frameId as keyof typeof FRAME_CONFIG];
    return {
      frameId,
      frameName: config?.name || `Frame ${frameId}`,
      duration: 0,
      cardsCompleted: 0,
      cardsTotal: config?.cards.length || 0,
      completionPercentage: 0,
      interactions: 0,
      hesitations: [],
      backTracks: 0,
      isComplete: false,
      isCurrent: false,
    };
  }
}

// ============================================================================
// SCORE TRACKER
// ============================================================================

export class ScoreTracker {
  private sessionId: string;
  private history: ScoreHistoryEntry[] = [];
  private currentScores: ScoreSnapshot = {
    aptitude: 0,
    passion: 0,
    community: 0,
    operating: 0,
    ivyReady: 0,
  };
  private eventCallback?: (event: AnalyticsEvent) => void;
  
  constructor(sessionId: string, onEvent?: (event: AnalyticsEvent) => void) {
    this.sessionId = sessionId;
    this.eventCallback = onEvent;
  }
  
  private emitEvent(type: string, data: Record<string, unknown> = {}): void {
    const event: AnalyticsEvent = {
      id: generateEventId(),
      type: type as any,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      data,
    };
    
    this.eventCallback?.(event);
  }
  
  recordScoreUpdate(
    frameId: number,
    newScores: Partial<ScoreSnapshot>,
    trigger: string,
    cardId?: string
  ): void {
    const previousScores = { ...this.currentScores };
    
    // Update current scores
    Object.entries(newScores).forEach(([key, value]) => {
      if (value !== undefined) {
        this.currentScores[key as keyof ScoreSnapshot] = value;
      }
    });
    
    // Calculate deltas
    const delta: Partial<ScoreSnapshot> = {};
    (Object.keys(this.currentScores) as (keyof ScoreSnapshot)[]).forEach(key => {
      const diff = this.currentScores[key] - previousScores[key];
      if (diff !== 0) {
        delta[key] = diff;
      }
    });
    
    // Skip if no actual change
    if (Object.keys(delta).length === 0) return;
    
    // Record history entry
    const entry: ScoreHistoryEntry = {
      timestamp: Date.now(),
      frameId,
      cardId,
      trigger,
      scores: { ...this.currentScores },
      delta,
    };
    
    this.history.push(entry);
    
    // Emit event
    this.emitEvent(SCORE_EVENTS.SCORE_UPDATE, {
      previousScores,
      newScores: this.currentScores,
      delta,
      trigger,
    });
    
    // Check for tier change
    const prevTier = this.getTier(previousScores.ivyReady);
    const newTier = this.getTier(this.currentScores.ivyReady);
    
    if (prevTier !== newTier) {
      this.emitEvent(SCORE_EVENTS.TIER_CHANGE, {
        oldTier: prevTier,
        newTier: newTier,
        score: this.currentScores.ivyReady,
      });
    }
  }
  
  private getTier(score: number): string {
    if (score >= 85) return 'exceptional';
    if (score >= 70) return 'competitive';
    if (score >= 50) return 'average';
    return 'developing';
  }
  
  getCurrentScores(): ScoreSnapshot {
    return { ...this.currentScores };
  }
  
  getHistory(): ScoreHistoryEntry[] {
    return [...this.history];
  }
  
  getScoreAtTime(timestamp: number): ScoreSnapshot | null {
    // Find the entry closest to the timestamp
    for (let i = this.history.length - 1; i >= 0; i--) {
      if (this.history[i].timestamp <= timestamp) {
        return { ...this.history[i].scores };
      }
    }
    return null;
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default { FrameTracker, ScoreTracker };
