/**
 * Domain-Specific Loggers
 * Typed wrappers around TraceContext for specific use cases
 */

import { traceContext, TraceContext } from './TraceContext';
import type {
  ScoringTraceData,
  ScoreBreakdown,
  InputTraceData,
  StateChangeTraceData,
  NavigationTraceData,
  ApiTraceData,
  TwinTraceData,
  PerformanceTraceData,
} from './types';

// ============================================
// Scoring Logger
// ============================================

class ScoringLogger {
  private ctx: TraceContext;

  constructor(ctx: TraceContext) {
    this.ctx = ctx;
  }

  /**
   * Log individual component score calculation
   */
  logComponentScore(data: ScoringTraceData): void {
    this.ctx.info('scoring', 'component:calculate', `Calculated ${data.component} score`, {
      ...data,
      formula: data.formula || 'standard_normalization',
    });
  }

  /**
   * Log full score breakdown
   */
  logScoreBreakdown(
    studentId: string,
    schoolId: string,
    breakdown: ScoreBreakdown
  ): void {
    this.ctx.info('scoring', 'breakdown:complete', `Score breakdown for ${schoolId}`, {
      studentId,
      schoolId,
      breakdown,
      timestamp: Date.now(),
    });
  }

  /**
   * Log booster application
   */
  logBoosterApplied(
    boosterType: string,
    baseScore: number,
    multiplier: number,
    newScore: number
  ): void {
    this.ctx.info('scoring', 'booster:applied', `Applied ${boosterType} booster`, {
      boosterType,
      baseScore,
      multiplier,
      newScore,
      delta: newScore - baseScore,
    });
  }

  /**
   * Log normalization step
   */
  logNormalization(
    field: string,
    rawValue: unknown,
    normalizedValue: number,
    min: number,
    max: number
  ): void {
    this.ctx.debug('scoring', 'normalize', `Normalized ${field}`, {
      field,
      rawValue,
      normalizedValue,
      range: { min, max },
    });
  }

  /**
   * Log school-specific multiplier
   */
  logSchoolMultiplier(
    schoolId: string,
    baseScore: number,
    multiplier: number,
    reason: string
  ): void {
    this.ctx.info('scoring', 'school:multiplier', `School multiplier applied`, {
      schoolId,
      baseScore,
      multiplier,
      adjustedScore: baseScore * multiplier,
      reason,
    });
  }

  /**
   * Log final probability calculation
   */
  logProbabilityCalculation(
    schoolId: string,
    profileStrength: number,
    baseAcceptance: number,
    finalProbability: number,
    factors: Record<string, number>
  ): void {
    this.ctx.info('scoring', 'probability:final', `Final probability for ${schoolId}`, {
      schoolId,
      profileStrength,
      baseAcceptance,
      finalProbability,
      factors,
    });
  }

  /**
   * Start a scoring calculation span
   */
  startCalculation(schoolId: string): string {
    return this.ctx.startSpan(`score:${schoolId}`, 'scoring', { schoolId });
  }

  /**
   * End a scoring calculation span
   */
  endCalculation(spanId: string): void {
    this.ctx.endSpan(spanId);
  }
}

// ============================================
// Input Logger
// ============================================

class InputLogger {
  private ctx: TraceContext;

  constructor(ctx: TraceContext) {
    this.ctx = ctx;
  }

  /**
   * Log input field change
   */
  logInputChange(data: InputTraceData): void {
    const level = data.isValid ? 'info' : 'warn';
    this.ctx.log(level, 'input', 'field:change', `${data.fieldId} changed`, {
      ...data,
      timestamp: Date.now(),
    });
  }

  /**
   * Log validation result
   */
  logValidation(
    fieldId: string,
    isValid: boolean,
    errors: string[] = []
  ): void {
    const level = isValid ? 'debug' : 'warn';
    this.ctx.log(level, 'validation', 'field:validate', `Validated ${fieldId}`, {
      fieldId,
      isValid,
      errors,
    });
  }

  /**
   * Log voice input transcription
   */
  logVoiceInput(
    fieldId: string,
    transcript: string,
    confidence: number,
    duration: number
  ): void {
    this.ctx.info('input', 'voice:transcribe', `Voice input for ${fieldId}`, {
      fieldId,
      transcript,
      confidence,
      durationMs: duration,
    });
  }

  /**
   * Log chip selection
   */
  logChipSelection(
    fieldId: string,
    selectedChips: string[],
    action: 'add' | 'remove',
    chip: string
  ): void {
    this.ctx.info('input', 'chip:select', `Chip ${action}: ${chip}`, {
      fieldId,
      selectedChips,
      action,
      chip,
    });
  }

  /**
   * Log slider drag
   */
  logSliderChange(
    fieldId: string,
    previousValue: number,
    newValue: number,
    min: number,
    max: number
  ): void {
    this.ctx.debug('input', 'slider:change', `Slider ${fieldId} changed`, {
      fieldId,
      previousValue,
      newValue,
      min,
      max,
      percentage: ((newValue - min) / (max - min)) * 100,
    });
  }

  /**
   * Log form submission
   */
  logFormSubmit(
    formId: string,
    frameId: number,
    cardId: string,
    isValid: boolean,
    fieldCount: number
  ): void {
    const level = isValid ? 'info' : 'warn';
    this.ctx.log(level, 'input', 'form:submit', `Form ${formId} submitted`, {
      formId,
      frameId,
      cardId,
      isValid,
      fieldCount,
    });
  }

  /**
   * Start an input interaction span
   */
  startInteraction(fieldId: string): string {
    return this.ctx.startSpan(`input:${fieldId}`, 'input', { fieldId });
  }

  /**
   * End an input interaction span
   */
  endInteraction(spanId: string): void {
    this.ctx.endSpan(spanId);
  }
}

// ============================================
// State Logger
// ============================================

class StateLogger {
  private ctx: TraceContext;

  constructor(ctx: TraceContext) {
    this.ctx = ctx;
  }

  /**
   * Log state change
   */
  logStateChange(data: StateChangeTraceData): void {
    this.ctx.info('state', 'change', `${data.storeName}.${data.action}`, {
      ...data,
      timestamp: Date.now(),
    });
  }

  /**
   * Log store initialization
   */
  logStoreInit(storeName: string, initialState: unknown): void {
    this.ctx.info('state', 'store:init', `${storeName} initialized`, {
      storeName,
      initialState,
    });
  }

  /**
   * Log store hydration from persistence
   */
  logHydration(storeName: string, hydratedState: unknown): void {
    this.ctx.info('state', 'store:hydrate', `${storeName} hydrated from storage`, {
      storeName,
      hydratedState,
    });
  }

  /**
   * Log store reset
   */
  logStoreReset(storeName: string): void {
    this.ctx.info('state', 'store:reset', `${storeName} reset to initial state`, {
      storeName,
    });
  }

  /**
   * Log selector subscription
   */
  logSelector(storeName: string, selectorPath: string, value: unknown): void {
    this.ctx.debug('state', 'selector:read', `Read ${storeName}.${selectorPath}`, {
      storeName,
      selectorPath,
      value,
    });
  }
}

// ============================================
// Navigation Logger
// ============================================

class NavigationLogger {
  private ctx: TraceContext;

  constructor(ctx: TraceContext) {
    this.ctx = ctx;
  }

  /**
   * Log frame navigation
   */
  logFrameNavigation(data: NavigationTraceData): void {
    this.ctx.info('navigation', 'frame:navigate', `Navigate Frame ${data.fromFrame} → ${data.toFrame}`, {
      ...data,
      timestamp: Date.now(),
    });
  }

  /**
   * Log card navigation within frame
   */
  logCardNavigation(
    frameId: number,
    fromCard: number,
    toCard: number,
    direction: 'next' | 'prev'
  ): void {
    this.ctx.info('navigation', 'card:navigate', `Card ${fromCard} → ${toCard}`, {
      frameId,
      fromCard,
      toCard,
      direction,
    });
  }

  /**
   * Log Edge award (formerly XP)
   */
  logEdgeAward(amount: number, reason: string, totalEdge: number): void {
    this.ctx.info('navigation', 'edge:award', `+${amount} Edge: ${reason}`, {
      amount,
      reason,
      totalEdge,
    });
  }

  // Backwards compatibility alias
  logXPAward(amount: number, reason: string, totalXP: number): void {
    this.logEdgeAward(amount, reason, totalXP);
  }

  /**
   * Log achievement unlock
   */
  logAchievement(achievementId: string, achievementName: string): void {
    this.ctx.info('navigation', 'achievement:unlock', `Achievement: ${achievementName}`, {
      achievementId,
      achievementName,
    });
  }

  /**
   * Start a navigation span
   */
  startNavigation(from: number, to: number): string {
    return this.ctx.startSpan(`nav:${from}->${to}`, 'navigation', { from, to });
  }

  /**
   * End a navigation span
   */
  endNavigation(spanId: string): void {
    this.ctx.endSpan(spanId);
  }
}

// ============================================
// API Logger
// ============================================

class ApiLogger {
  private ctx: TraceContext;

  constructor(ctx: TraceContext) {
    this.ctx = ctx;
  }

  /**
   * Log API request start
   */
  logRequest(data: Omit<ApiTraceData, 'latencyMs' | 'responseStatus' | 'responseData'>): string {
    const spanId = this.ctx.startSpan(`api:${data.method}:${data.endpoint}`, 'api', {
      endpoint: data.endpoint,
      method: data.method,
    });

    this.ctx.info('api', 'request:start', `${data.method} ${data.endpoint}`, {
      ...data,
      spanId,
    });

    return spanId;
  }

  /**
   * Log API response
   */
  logResponse(spanId: string, data: ApiTraceData): void {
    const level = data.responseStatus && data.responseStatus >= 400 ? 'error' : 'info';

    this.ctx.log(level, 'api', 'request:complete', `${data.method} ${data.endpoint} → ${data.responseStatus}`, {
      ...data,
    });

    this.ctx.endSpan(spanId, data.responseStatus && data.responseStatus >= 400 ? 'error' : 'completed');
  }

  /**
   * Log API error
   */
  logError(endpoint: string, method: string, error: unknown): void {
    this.ctx.error('api', 'request:error', `${method} ${endpoint} failed`, {
      endpoint,
      method,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
  }
}

// ============================================
// Twin Logger
// ============================================

class TwinLogger {
  private ctx: TraceContext;

  constructor(ctx: TraceContext) {
    this.ctx = ctx;
  }

  /**
   * Log gear upgrade
   */
  logGearUpgrade(data: TwinTraceData): void {
    this.ctx.info('twin', 'gear:upgrade', `${data.schoolId} ${data.gearSlot}: ${data.gearTier}`, {
      ...data,
    });
  }

  /**
   * Log twin fleet update
   */
  logFleetUpdate(schoolIds: string[], updateType: 'add' | 'remove' | 'reorder'): void {
    this.ctx.info('twin', 'fleet:update', `Fleet ${updateType}`, {
      schoolIds,
      updateType,
      fleetSize: schoolIds.length,
    });
  }

  /**
   * Log twin animation
   */
  logAnimation(schoolId: string, animationType: string, duration: number): void {
    this.ctx.debug('twin', 'animation:play', `${schoolId} animation: ${animationType}`, {
      schoolId,
      animationType,
      durationMs: duration,
    });
  }
}

// ============================================
// Performance Logger
// ============================================

class PerformanceLogger {
  private ctx: TraceContext;

  constructor(ctx: TraceContext) {
    this.ctx = ctx;
  }

  /**
   * Log render performance
   */
  logRender(componentName: string, durationMs: number): void {
    const level = durationMs > 16 ? 'warn' : 'debug';
    this.ctx.log(level, 'performance', 'render', `${componentName} rendered`, {
      componentName,
      durationMs,
      fps: Math.round(1000 / durationMs),
    });
  }

  /**
   * Log calculation performance
   */
  logCalculation(calculationType: string, durationMs: number): void {
    this.ctx.debug('performance', 'calculate', `${calculationType} completed`, {
      calculationType,
      durationMs,
    });
  }

  /**
   * Start a performance measurement
   */
  startMeasure(name: string): () => void {
    const start = performance.now();
    const spanId = this.ctx.startSpan(`perf:${name}`, 'performance', { name });

    return () => {
      const duration = performance.now() - start;
      this.ctx.info('performance', 'measure:complete', `${name} took ${duration.toFixed(2)}ms`, {
        name,
        durationMs: duration,
      });
      this.ctx.endSpan(spanId);
    };
  }

  /**
   * Log memory usage
   */
  logMemory(): void {
    if ('memory' in performance) {
      const memory = (performance as Performance & { memory?: { usedJSHeapSize: number; totalJSHeapSize: number } }).memory;
      if (memory) {
        this.ctx.debug('performance', 'memory', 'Memory snapshot', {
          usedHeap: memory.usedJSHeapSize,
          totalHeap: memory.totalJSHeapSize,
          usagePercent: ((memory.usedJSHeapSize / memory.totalJSHeapSize) * 100).toFixed(2),
        });
      }
    }
  }
}

// ============================================
// Export Singleton Instances
// ============================================

export const scoringLogger = new ScoringLogger(traceContext);
export const inputLogger = new InputLogger(traceContext);
export const stateLogger = new StateLogger(traceContext);
export const navigationLogger = new NavigationLogger(traceContext);
export const apiLogger = new ApiLogger(traceContext);
export const twinLogger = new TwinLogger(traceContext);
export const performanceLogger = new PerformanceLogger(traceContext);
