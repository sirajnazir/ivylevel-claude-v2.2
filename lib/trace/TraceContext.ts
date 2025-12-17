/**
 * TraceContext - Core Trace Management
 * Handles span lifecycle and event collection
 */

import type {
  TraceSpan,
  TraceEvent,
  TraceLevel,
  TraceDomain,
  TraceConfig,
  TRACE_LEVEL_PRIORITY,
} from './types';
import { DEFAULT_TRACE_CONFIG } from './types';

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export class TraceContext {
  private spans: Map<string, TraceSpan> = new Map();
  private events: TraceEvent[] = [];
  private config: TraceConfig;
  private activeSpanId: string | null = null;
  private listeners: Set<(event: TraceEvent) => void> = new Set();
  private spanListeners: Set<(span: TraceSpan) => void> = new Set();

  constructor(config: Partial<TraceConfig> = {}) {
    this.config = { ...DEFAULT_TRACE_CONFIG, ...config };
  }

  // ============================================
  // Configuration
  // ============================================

  updateConfig(config: Partial<TraceConfig>): void {
    this.config = { ...this.config, ...config };
  }

  getConfig(): TraceConfig {
    return { ...this.config };
  }

  isEnabled(): boolean {
    return this.config.enabled;
  }

  // ============================================
  // Span Management
  // ============================================

  startSpan(
    name: string,
    domain: TraceDomain,
    metadata?: Record<string, unknown>
  ): string {
    if (!this.isEnabled()) return '';
    if (!this.shouldSample()) return '';

    const spanId = generateId();
    const span: TraceSpan = {
      id: spanId,
      name,
      domain,
      startTime: performance.now(),
      status: 'running',
      events: [],
      metadata,
      parentSpanId: this.activeSpanId || undefined,
      childSpanIds: [],
    };

    // Link to parent span
    if (this.activeSpanId) {
      const parentSpan = this.spans.get(this.activeSpanId);
      if (parentSpan) {
        parentSpan.childSpanIds.push(spanId);
      }
    }

    this.spans.set(spanId, span);
    this.activeSpanId = spanId;

    this.log('debug', domain, `span:start`, `Started span: ${name}`, { spanId });

    return spanId;
  }

  endSpan(spanId: string, status: 'completed' | 'error' = 'completed'): TraceSpan | null {
    if (!this.isEnabled() || !spanId) return null;

    const span = this.spans.get(spanId);
    if (!span) return null;

    span.endTime = performance.now();
    span.duration = span.endTime - span.startTime;
    span.status = status;

    // Reset active span to parent
    if (this.activeSpanId === spanId) {
      this.activeSpanId = span.parentSpanId || null;
    }

    this.log('debug', span.domain, `span:end`, `Ended span: ${span.name}`, {
      spanId,
      duration: span.duration,
      status,
    });

    // Notify span listeners
    this.spanListeners.forEach((listener) => listener(span));

    // Clean up old spans if over limit
    this.pruneSpans();

    return span;
  }

  getSpan(spanId: string): TraceSpan | undefined {
    return this.spans.get(spanId);
  }

  getActiveSpanId(): string | null {
    return this.activeSpanId;
  }

  getAllSpans(): TraceSpan[] {
    return Array.from(this.spans.values());
  }

  // ============================================
  // Event Logging
  // ============================================

  log(
    level: TraceLevel,
    domain: TraceDomain,
    action: string,
    message: string,
    data?: Record<string, unknown>
  ): void {
    if (!this.isEnabled()) return;
    if (!this.shouldLog(level, domain)) return;
    if (!this.shouldSample()) return;

    const event: TraceEvent = {
      id: generateId(),
      timestamp: performance.now(),
      level,
      domain,
      action,
      message,
      data,
      parentSpanId: this.activeSpanId || undefined,
    };

    this.events.push(event);

    // Add to active span if exists
    if (this.activeSpanId) {
      const span = this.spans.get(this.activeSpanId);
      if (span) {
        span.events.push(event);
      }
    }

    // Console output
    if (this.config.consoleOutput) {
      this.outputToConsole(event);
    }

    // Notify listeners
    this.listeners.forEach((listener) => listener(event));

    // Prune old events
    this.pruneEvents();
  }

  debug(domain: TraceDomain, action: string, message: string, data?: Record<string, unknown>): void {
    this.log('debug', domain, action, message, data);
  }

  info(domain: TraceDomain, action: string, message: string, data?: Record<string, unknown>): void {
    this.log('info', domain, action, message, data);
  }

  warn(domain: TraceDomain, action: string, message: string, data?: Record<string, unknown>): void {
    this.log('warn', domain, action, message, data);
  }

  error(domain: TraceDomain, action: string, message: string, data?: Record<string, unknown>): void {
    this.log('error', domain, action, message, data);
  }

  // ============================================
  // Event Retrieval
  // ============================================

  getEvents(filter?: {
    levels?: TraceLevel[];
    domains?: TraceDomain[];
    limit?: number;
    since?: number;
  }): TraceEvent[] {
    let result = [...this.events];

    if (filter?.levels?.length) {
      result = result.filter((e) => filter.levels!.includes(e.level));
    }

    if (filter?.domains?.length) {
      result = result.filter((e) => filter.domains!.includes(e.domain));
    }

    if (filter?.since) {
      result = result.filter((e) => e.timestamp >= filter.since!);
    }

    if (filter?.limit) {
      result = result.slice(-filter.limit);
    }

    return result;
  }

  getLatestEvents(count: number): TraceEvent[] {
    return this.events.slice(-count);
  }

  // ============================================
  // Listeners
  // ============================================

  addListener(callback: (event: TraceEvent) => void): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  addSpanListener(callback: (span: TraceSpan) => void): () => void {
    this.spanListeners.add(callback);
    return () => this.spanListeners.delete(callback);
  }

  // ============================================
  // Utilities
  // ============================================

  clear(): void {
    this.spans.clear();
    this.events = [];
    this.activeSpanId = null;
  }

  exportToJSON(): string {
    return JSON.stringify({
      spans: Array.from(this.spans.values()),
      events: this.events,
      config: this.config,
      exportedAt: new Date().toISOString(),
    }, null, 2);
  }

  // ============================================
  // Private Helpers
  // ============================================

  private shouldLog(level: TraceLevel, domain: TraceDomain): boolean {
    const levelPriority: Record<TraceLevel, number> = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3,
    };

    // Check level
    if (levelPriority[level] < levelPriority[this.config.minLevel]) {
      return false;
    }

    // Check domain
    if (!this.config.enabledDomains.includes(domain)) {
      return false;
    }

    return true;
  }

  private shouldSample(): boolean {
    return Math.random() < this.config.samplingRate;
  }

  private pruneEvents(): void {
    if (this.events.length > this.config.maxStoredEvents) {
      this.events = this.events.slice(-this.config.maxStoredEvents);
    }
  }

  private pruneSpans(): void {
    const completedSpans = Array.from(this.spans.entries())
      .filter(([_, span]) => span.status !== 'running')
      .sort((a, b) => (a[1].startTime || 0) - (b[1].startTime || 0));

    while (completedSpans.length > this.config.maxStoredSpans) {
      const [oldestId] = completedSpans.shift()!;
      this.spans.delete(oldestId);
    }
  }

  private outputToConsole(event: TraceEvent): void {
    const prefix = `[${event.domain.toUpperCase()}]`;
    const timestamp = new Date().toISOString().split('T')[1].slice(0, -1);

    const styles: Record<TraceLevel, string> = {
      debug: 'color: #94A3B8',
      info: 'color: #4A90D9',
      warn: 'color: #FBBF24',
      error: 'color: #EF4444',
    };

    const style = styles[event.level];
    const message = `%c${timestamp} ${prefix} ${event.action}: ${event.message}`;

    switch (event.level) {
      case 'debug':
        if (event.data) {
          console.debug(message, style, event.data);
        } else {
          console.debug(message, style);
        }
        break;
      case 'info':
        if (event.data) {
          console.info(message, style, event.data);
        } else {
          console.info(message, style);
        }
        break;
      case 'warn':
        if (event.data) {
          console.warn(message, style, event.data);
        } else {
          console.warn(message, style);
        }
        break;
      case 'error':
        if (event.data) {
          console.error(message, style, event.data);
        } else {
          console.error(message, style);
        }
        break;
    }
  }
}

// ============================================
// Singleton Export
// ============================================

export const traceContext = new TraceContext();
