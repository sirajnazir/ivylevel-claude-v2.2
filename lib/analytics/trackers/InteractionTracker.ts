/**
 * IvyQuest v3.0 — Interaction Tracker
 * 
 * Tracks field-level interactions, hesitations, and user behavior patterns.
 * 
 * @version 1.0.0
 * @module trackers/InteractionTracker
 */

import {
  INTERACTION_EVENTS,
  TIMING_THRESHOLDS,
} from '../constants/analytics.constants';
import { generateEventId } from '../utils/analyticsUtils';
import type {
  AnalyticsEvent,
  InteractionEvent,
  HesitationEvent,
} from '../types/analytics.types';

// ============================================================================
// FIELD STATE
// ============================================================================

interface FieldState {
  fieldId: string;
  frameId: number;
  cardId?: string;
  focusedAt?: number;
  blurredAt?: number;
  changeCount: number;
  totalFocusTime: number;
  hesitations: HesitationEvent[];
  lastValue?: unknown;
}

// ============================================================================
// INTERACTION TRACKER CLASS
// ============================================================================

export class InteractionTracker {
  private sessionId: string;
  private fields: Map<string, FieldState> = new Map();
  private currentField: string | null = null;
  private hesitationTimeout?: NodeJS.Timeout;
  private eventCallback?: (event: AnalyticsEvent) => void;
  
  constructor(
    sessionId: string,
    onEvent?: (event: AnalyticsEvent) => void
  ) {
    this.sessionId = sessionId;
    this.eventCallback = onEvent;
  }
  
  // ==========================================================================
  // EVENT EMISSION
  // ==========================================================================
  
  private emitEvent(
    type: string,
    fieldId: string,
    data: Record<string, unknown> = {}
  ): void {
    const fieldState = this.fields.get(fieldId);
    
    const event: AnalyticsEvent = {
      id: generateEventId(),
      type: type as any,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      frameId: fieldState?.frameId,
      cardId: fieldState?.cardId,
      data: {
        fieldId,
        ...data,
      },
    };
    
    this.eventCallback?.(event);
  }
  
  // ==========================================================================
  // FIELD REGISTRATION
  // ==========================================================================
  
  registerField(
    fieldId: string,
    frameId: number,
    cardId?: string
  ): void {
    if (!this.fields.has(fieldId)) {
      this.fields.set(fieldId, {
        fieldId,
        frameId,
        cardId,
        changeCount: 0,
        totalFocusTime: 0,
        hesitations: [],
      });
    }
  }
  
  // ==========================================================================
  // FOCUS TRACKING
  // ==========================================================================
  
  trackFocus(fieldId: string, frameId?: number, cardId?: string): void {
    // Register if not already
    if (!this.fields.has(fieldId) && frameId !== undefined) {
      this.registerField(fieldId, frameId, cardId);
    }
    
    const state = this.fields.get(fieldId);
    if (!state) return;
    
    // Update current field
    this.currentField = fieldId;
    state.focusedAt = Date.now();
    
    // Start hesitation detection
    this.startHesitationDetection(fieldId);
    
    this.emitEvent(INTERACTION_EVENTS.FIELD_FOCUS, fieldId, {
      frameId: state.frameId,
      cardId: state.cardId,
    });
  }
  
  trackBlur(fieldId: string): void {
    const state = this.fields.get(fieldId);
    if (!state || !state.focusedAt) return;
    
    const duration = Date.now() - state.focusedAt;
    state.totalFocusTime += duration;
    state.blurredAt = Date.now();
    
    // Clear current field
    if (this.currentField === fieldId) {
      this.currentField = null;
    }
    
    // Stop hesitation detection
    this.stopHesitationDetection();
    
    this.emitEvent(INTERACTION_EVENTS.FIELD_BLUR, fieldId, {
      duration,
      totalFocusTime: state.totalFocusTime,
      changeCount: state.changeCount,
    });
    
    state.focusedAt = undefined;
  }
  
  // ==========================================================================
  // CHANGE TRACKING
  // ==========================================================================
  
  trackChange(
    fieldId: string,
    newValue: unknown,
    previousValue?: unknown
  ): void {
    const state = this.fields.get(fieldId);
    if (!state) return;
    
    state.changeCount++;
    state.lastValue = newValue;
    
    // Reset hesitation timer on change
    this.startHesitationDetection(fieldId);
    
    this.emitEvent(INTERACTION_EVENTS.FIELD_CHANGE, fieldId, {
      hasValue: newValue !== undefined && newValue !== null && newValue !== '',
      changeCount: state.changeCount,
      // Don't log actual values for privacy
    });
  }
  
  trackSelection(
    fieldId: string,
    optionId: string,
    category?: string
  ): void {
    const state = this.fields.get(fieldId);
    
    this.emitEvent(INTERACTION_EVENTS.SELECTION_MADE, fieldId, {
      optionId,
      category,
      frameId: state?.frameId,
    });
  }
  
  // ==========================================================================
  // VALIDATION TRACKING
  // ==========================================================================
  
  trackValidationError(
    fieldId: string,
    errorType: string,
    message?: string
  ): void {
    this.emitEvent(INTERACTION_EVENTS.VALIDATION_ERROR, fieldId, {
      errorType,
      message,
    });
  }
  
  trackValidationSuccess(fieldId: string): void {
    this.emitEvent(INTERACTION_EVENTS.VALIDATION_SUCCESS, fieldId, {});
  }
  
  // ==========================================================================
  // HESITATION DETECTION
  // ==========================================================================
  
  private startHesitationDetection(fieldId: string): void {
    this.stopHesitationDetection();
    
    this.hesitationTimeout = setTimeout(() => {
      const state = this.fields.get(fieldId);
      if (!state || !state.focusedAt) return;
      
      const hesitationStart = state.focusedAt;
      const hesitation: HesitationEvent = {
        fieldId,
        startTime: hesitationStart,
        duration: Date.now() - hesitationStart,
        resolved: false,
      };
      
      state.hesitations.push(hesitation);
      
      // Emit hesitation event (useful for real-time coaching)
      this.emitEvent('field_hesitation', fieldId, {
        duration: hesitation.duration,
        hesitationCount: state.hesitations.length,
      });
    }, TIMING_THRESHOLDS.HESITATION_THRESHOLD);
  }
  
  private stopHesitationDetection(): void {
    if (this.hesitationTimeout) {
      clearTimeout(this.hesitationTimeout);
      this.hesitationTimeout = undefined;
    }
  }
  
  // ==========================================================================
  // METRICS
  // ==========================================================================
  
  getFieldMetrics(fieldId: string): FieldState | undefined {
    return this.fields.get(fieldId);
  }
  
  getAllHesitations(): HesitationEvent[] {
    const hesitations: HesitationEvent[] = [];
    
    this.fields.forEach(state => {
      hesitations.push(...state.hesitations);
    });
    
    return hesitations.sort((a, b) => b.duration - a.duration);
  }
  
  getFieldsWithHesitations(): string[] {
    const fields: string[] = [];
    
    this.fields.forEach((state, fieldId) => {
      if (state.hesitations.length > 0) {
        fields.push(fieldId);
      }
    });
    
    return fields;
  }
  
  getTotalInteractions(): number {
    let total = 0;
    this.fields.forEach(state => {
      total += state.changeCount;
    });
    return total;
  }
  
  getAverageFocusTime(): number {
    let totalTime = 0;
    let fieldCount = 0;
    
    this.fields.forEach(state => {
      if (state.totalFocusTime > 0) {
        totalTime += state.totalFocusTime;
        fieldCount++;
      }
    });
    
    return fieldCount > 0 ? Math.round(totalTime / fieldCount) : 0;
  }
  
  // ==========================================================================
  // CLEANUP
  // ==========================================================================
  
  destroy(): void {
    this.stopHesitationDetection();
    this.fields.clear();
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default InteractionTracker;
