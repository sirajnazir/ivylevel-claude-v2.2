/**
 * IvyQuest v3.0 — Score Tracker
 * 
 * Tracks score changes, tier transitions, and score evolution over time.
 * 
 * @version 1.0.0
 * @module trackers/ScoreTracker
 */

import {
  SCORE_EVENTS,
  INSIGHT_THRESHOLDS,
} from '../constants/analytics.constants';
import {
  generateEventId,
  analyzeScoreEvolution,
} from '../utils/analyticsUtils';
import type {
  AnalyticsEvent,
  ScoreSnapshot,
  ScoreHistoryEntry,
  ScoreEvolution,
} from '../types/analytics.types';

// ============================================================================
// TIER DEFINITIONS
// ============================================================================

const SCORE_TIERS = {
  exceptional: { min: 85, max: 100, label: 'Exceptional' },
  competitive: { min: 70, max: 84, label: 'Competitive' },
  average: { min: 50, max: 69, label: 'Average' },
  developing: { min: 0, max: 49, label: 'Developing' },
} as const;

function getTierFromScore(score: number): keyof typeof SCORE_TIERS {
  if (score >= SCORE_TIERS.exceptional.min) return 'exceptional';
  if (score >= SCORE_TIERS.competitive.min) return 'competitive';
  if (score >= SCORE_TIERS.average.min) return 'average';
  return 'developing';
}

// ============================================================================
// SCORE TRACKER CLASS
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
  private currentTier: keyof typeof SCORE_TIERS = 'developing';
  private eventCallback?: (event: AnalyticsEvent) => void;
  
  constructor(
    sessionId: string,
    onEvent?: (event: AnalyticsEvent) => void
  ) {
    this.sessionId = sessionId;
    this.eventCallback = onEvent;
    
    // Record initial state
    this.recordSnapshot(0, 'initial', 'Session started');
  }
  
  // ==========================================================================
  // EVENT EMISSION
  // ==========================================================================
  
  private emitEvent(
    type: string,
    data: Record<string, unknown> = {}
  ): void {
    const event: AnalyticsEvent = {
      id: generateEventId(),
      type: type as any,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      data,
    };
    
    this.eventCallback?.(event);
  }
  
  // ==========================================================================
  // SCORE UPDATES
  // ==========================================================================
  
  updateScore(
    category: keyof ScoreSnapshot,
    newScore: number,
    frameId: number,
    trigger: string,
    cardId?: string
  ): void {
    const oldScore = this.currentScores[category];
    const delta = newScore - oldScore;
    
    // Skip if no change
    if (delta === 0) return;
    
    // Update current scores
    this.currentScores[category] = newScore;
    
    // Check for tier change on ivyReady
    if (category === 'ivyReady') {
      this.checkTierChange(newScore);
    }
    
    // Record to history if significant
    if (Math.abs(delta) >= 1) {
      this.recordSnapshot(frameId, cardId || category, trigger);
    }
    
    // Emit event
    this.emitEvent(SCORE_EVENTS.SCORE_UPDATE, {
      category,
      oldScore,
      newScore,
      delta,
      frameId,
      trigger,
    });
  }
  
  updateAllScores(
    scores: Partial<ScoreSnapshot>,
    frameId: number,
    trigger: string,
    cardId?: string
  ): void {
    const oldScores = { ...this.currentScores };
    const deltas: Partial<ScoreSnapshot> = {};
    let hasSignificantChange = false;
    
    // Calculate deltas
    Object.entries(scores).forEach(([key, value]) => {
      const category = key as keyof ScoreSnapshot;
      if (value !== undefined) {
        const delta = value - this.currentScores[category];
        deltas[category] = delta;
        this.currentScores[category] = value;
        
        if (Math.abs(delta) >= INSIGHT_THRESHOLDS.SIGNIFICANT_SCORE_DIFF) {
          hasSignificantChange = true;
        }
      }
    });
    
    // Check tier change
    if (scores.ivyReady !== undefined) {
      this.checkTierChange(scores.ivyReady);
    }
    
    // Record snapshot
    this.recordSnapshot(frameId, cardId || 'bulk_update', trigger);
    
    // Emit event
    this.emitEvent(SCORE_EVENTS.SCORE_CALCULATED, {
      scores: this.currentScores,
      deltas,
      frameId,
      trigger,
      hasSignificantChange,
    });
  }
  
  // ==========================================================================
  // TIER TRACKING
  // ==========================================================================
  
  private checkTierChange(newIvyReadyScore: number): void {
    const newTier = getTierFromScore(newIvyReadyScore);
    
    if (newTier !== this.currentTier) {
      const oldTier = this.currentTier;
      this.currentTier = newTier;
      
      this.emitEvent(SCORE_EVENTS.TIER_CHANGE, {
        oldTier,
        newTier,
        score: newIvyReadyScore,
        improved: this.isTierBetter(newTier, oldTier),
      });
    }
  }
  
  private isTierBetter(
    newTier: keyof typeof SCORE_TIERS,
    oldTier: keyof typeof SCORE_TIERS
  ): boolean {
    const tierOrder = ['developing', 'average', 'competitive', 'exceptional'];
    return tierOrder.indexOf(newTier) > tierOrder.indexOf(oldTier);
  }
  
  // ==========================================================================
  // SCHOOL FIT TRACKING
  // ==========================================================================
  
  updateSchoolFit(
    schoolId: string,
    probability: number,
    previousProbability?: number
  ): void {
    const delta = previousProbability !== undefined 
      ? probability - previousProbability 
      : 0;
    
    this.emitEvent(SCORE_EVENTS.SCHOOL_FIT_UPDATE, {
      schoolId,
      probability,
      previousProbability,
      delta,
      isGoodFit: probability >= INSIGHT_THRESHOLDS.GOOD_FIT_PROBABILITY,
    });
  }
  
  // ==========================================================================
  // BOOSTER TRACKING
  // ==========================================================================
  
  trackBoosterApplied(
    boosterId: string,
    category: keyof ScoreSnapshot,
    impact: number
  ): void {
    this.emitEvent(SCORE_EVENTS.BOOSTER_APPLIED, {
      boosterId,
      category,
      impact,
      scoreAfter: this.currentScores[category],
    });
  }
  
  trackBoosterRemoved(
    boosterId: string,
    category: keyof ScoreSnapshot,
    impact: number
  ): void {
    this.emitEvent(SCORE_EVENTS.BOOSTER_REMOVED, {
      boosterId,
      category,
      impact,
      scoreAfter: this.currentScores[category],
    });
  }
  
  // ==========================================================================
  // HISTORY MANAGEMENT
  // ==========================================================================
  
  private recordSnapshot(
    frameId: number,
    cardId: string,
    trigger: string
  ): void {
    const previousEntry = this.history[this.history.length - 1];
    
    const delta: Partial<ScoreSnapshot> = {};
    if (previousEntry) {
      (Object.keys(this.currentScores) as Array<keyof ScoreSnapshot>).forEach(key => {
        delta[key] = this.currentScores[key] - previousEntry.scores[key];
      });
    }
    
    this.history.push({
      timestamp: Date.now(),
      frameId,
      cardId,
      trigger,
      scores: { ...this.currentScores },
      delta,
    });
  }
  
  // ==========================================================================
  // GETTERS
  // ==========================================================================
  
  getCurrentScores(): ScoreSnapshot {
    return { ...this.currentScores };
  }
  
  getCurrentTier(): string {
    return this.currentTier;
  }
  
  getHistory(): ScoreHistoryEntry[] {
    return [...this.history];
  }
  
  getEvolution(): ScoreEvolution {
    return analyzeScoreEvolution(this.history);
  }
  
  getScoreAtFrame(frameId: number): ScoreSnapshot | undefined {
    // Find the last entry for this frame
    const frameEntries = this.history.filter(e => e.frameId === frameId);
    if (frameEntries.length === 0) return undefined;
    return frameEntries[frameEntries.length - 1].scores;
  }
  
  getScoreChangesInFrame(frameId: number): Partial<ScoreSnapshot> {
    const frameEntries = this.history.filter(e => e.frameId === frameId);
    if (frameEntries.length === 0) return {};
    
    const delta: Partial<ScoreSnapshot> = {
      aptitude: 0,
      passion: 0,
      community: 0,
      operating: 0,
      ivyReady: 0,
    };
    
    frameEntries.forEach(entry => {
      (Object.keys(delta) as Array<keyof ScoreSnapshot>).forEach(key => {
        delta[key]! += entry.delta[key] || 0;
      });
    });
    
    return delta;
  }
  
  getBiggestGains(): Array<{ category: keyof ScoreSnapshot; gain: number; frameId: number }> {
    const gains: Array<{ category: keyof ScoreSnapshot; gain: number; frameId: number }> = [];
    
    this.history.forEach(entry => {
      (Object.keys(entry.delta) as Array<keyof ScoreSnapshot>).forEach(category => {
        const delta = entry.delta[category];
        if (delta && delta >= INSIGHT_THRESHOLDS.SIGNIFICANT_SCORE_DIFF) {
          gains.push({
            category,
            gain: delta,
            frameId: entry.frameId,
          });
        }
      });
    });
    
    return gains.sort((a, b) => b.gain - a.gain);
  }
  
  // ==========================================================================
  // CLEANUP
  // ==========================================================================
  
  destroy(): void {
    // History is preserved for final report
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default ScoreTracker;
