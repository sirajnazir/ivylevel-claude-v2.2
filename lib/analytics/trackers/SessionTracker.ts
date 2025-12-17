/**
 * IvyQuest v3.0 — Session Tracker
 * 
 * Tracks session lifecycle and timing.
 * 
 * @version 1.0.0
 * @module trackers/SessionTracker
 */

import {
  SESSION_EVENTS,
  TIMING_THRESHOLDS,
} from '../constants/analytics.constants';
import {
  generateSessionId,
  generateEventId,
  getDeviceType,
  getBrowserInfo,
  calculateActiveDuration,
} from '../utils/analyticsUtils';
import type { AnalyticsEvent, SessionMetrics } from '../types/analytics.types';

// ============================================================================
// SESSION TRACKER CLASS
// ============================================================================

export class SessionTracker {
  private sessionId: string;
  private startedAt: number;
  private lastActiveAt: number;
  private pausedAt: number | null = null;
  private pauseCount: number = 0;
  private pauseTotalDuration: number = 0;
  private interactionCount: number = 0;
  private fieldEdits: number = 0;
  private validationErrors: number = 0;
  private framesCompleted: number = 0;
  private isActive: boolean = true;
  private completedAt: number | null = null;
  
  private eventCallback?: (event: AnalyticsEvent) => void;
  
  constructor(questId?: string, onEvent?: (event: AnalyticsEvent) => void) {
    this.sessionId = questId || generateSessionId();
    this.startedAt = Date.now();
    this.lastActiveAt = this.startedAt;
    this.eventCallback = onEvent;
    
    // Setup visibility listeners
    if (typeof document !== 'undefined') {
      document.addEventListener('visibilitychange', this.handleVisibilityChange);
      window.addEventListener('beforeunload', this.handleBeforeUnload);
    }
    
    // Emit start event
    this.emitEvent(SESSION_EVENTS.SESSION_START, {
      deviceType: getDeviceType(),
      browserInfo: getBrowserInfo(),
      screenSize: typeof window !== 'undefined' 
        ? { width: window.innerWidth, height: window.innerHeight }
        : { width: 0, height: 0 },
    });
  }
  
  // ============================================================================
  // EVENT EMISSION
  // ============================================================================
  
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
  
  // ============================================================================
  // VISIBILITY HANDLING
  // ============================================================================
  
  private handleVisibilityChange = (): void => {
    if (document.hidden) {
      this.pause();
    } else {
      this.resume();
    }
  };
  
  private handleBeforeUnload = (): void => {
    this.end('page_unload');
  };
  
  // ============================================================================
  // SESSION CONTROL
  // ============================================================================
  
  pause(): void {
    if (this.pausedAt) return;
    
    this.pausedAt = Date.now();
    this.isActive = false;
    
    this.emitEvent(SESSION_EVENTS.SESSION_PAUSE, {
      duration: this.getTotalDuration(),
      framesCompleted: this.framesCompleted,
    });
  }
  
  resume(): void {
    if (!this.pausedAt) return;
    
    const pauseDuration = Date.now() - this.pausedAt;
    
    if (pauseDuration >= TIMING_THRESHOLDS.MIN_PAUSE_DURATION) {
      this.pauseCount++;
      this.pauseTotalDuration += pauseDuration;
      
      this.emitEvent(SESSION_EVENTS.SESSION_RESUME, {
        pauseDuration,
        totalPauses: this.pauseCount,
      });
    }
    
    this.pausedAt = null;
    this.isActive = true;
    this.lastActiveAt = Date.now();
  }
  
  end(reason: string = 'completed'): void {
    if (this.completedAt) return;
    
    this.completedAt = Date.now();
    this.isActive = false;
    
    this.emitEvent(SESSION_EVENTS.SESSION_END, {
      reason,
      totalDuration: this.getTotalDuration(),
      activeDuration: this.getActiveDuration(),
      framesCompleted: this.framesCompleted,
      interactionCount: this.interactionCount,
    });
    
    // Cleanup listeners
    if (typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', this.handleVisibilityChange);
      window.removeEventListener('beforeunload', this.handleBeforeUnload);
    }
  }
  
  // ============================================================================
  // METRICS TRACKING
  // ============================================================================
  
  recordInteraction(): void {
    this.interactionCount++;
    this.lastActiveAt = Date.now();
  }
  
  recordFieldEdit(): void {
    this.fieldEdits++;
    this.recordInteraction();
  }
  
  recordValidationError(): void {
    this.validationErrors++;
  }
  
  recordFrameComplete(): void {
    this.framesCompleted++;
  }
  
  // ============================================================================
  // GETTERS
  // ============================================================================
  
  getSessionId(): string {
    return this.sessionId;
  }
  
  getTotalDuration(): number {
    const endTime = this.completedAt || Date.now();
    return endTime - this.startedAt;
  }
  
  getActiveDuration(): number {
    return calculateActiveDuration(this.getTotalDuration(), this.pauseTotalDuration);
  }
  
  getMetrics(): SessionMetrics {
    return {
      questId: this.sessionId,
      startedAt: this.startedAt,
      lastActiveAt: this.lastActiveAt,
      completedAt: this.completedAt || undefined,
      
      totalDuration: this.getTotalDuration(),
      activeDuration: this.getActiveDuration(),
      pauseCount: this.pauseCount,
      pauseTotalDuration: this.pauseTotalDuration,
      
      framesCompleted: this.framesCompleted,
      framesTotal: 6,
      completionPercentage: Math.round((this.framesCompleted / 6) * 100),
      
      interactionCount: this.interactionCount,
      fieldEdits: this.fieldEdits,
      validationErrors: this.validationErrors,
      
      deviceType: getDeviceType(),
      browserInfo: getBrowserInfo(),
    };
  }
  
  isSessionActive(): boolean {
    return this.isActive;
  }
  
  // ============================================================================
  // CLEANUP
  // ============================================================================
  
  destroy(): void {
    if (!this.completedAt) {
      this.end('destroyed');
    }
  }
}

export default SessionTracker;
