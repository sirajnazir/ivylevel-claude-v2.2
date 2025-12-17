/**
 * E2E Trace Logging System - Type Definitions
 * Full observability for scoring, inputs, and state changes
 */

// ============================================
// Core Trace Types
// ============================================

export type TraceLevel = 'debug' | 'info' | 'warn' | 'error';

export type TraceDomain =
  | 'scoring'
  | 'input'
  | 'state'
  | 'navigation'
  | 'api'
  | 'twin'
  | 'animation'
  | 'validation'
  | 'performance';

export interface TraceEvent {
  id: string;
  timestamp: number;
  level: TraceLevel;
  domain: TraceDomain;
  action: string;
  message: string;
  data?: Record<string, unknown>;
  duration?: number;
  parentSpanId?: string;
}

export interface TraceSpan {
  id: string;
  name: string;
  domain: TraceDomain;
  startTime: number;
  endTime?: number;
  duration?: number;
  status: 'running' | 'completed' | 'error';
  events: TraceEvent[];
  metadata?: Record<string, unknown>;
  parentSpanId?: string;
  childSpanIds: string[];
}

// ============================================
// Scoring-Specific Trace Types
// ============================================

export interface ScoringTraceData {
  component: string;
  rawValue: unknown;
  normalizedValue: number;
  weight: number;
  contribution: number;
  formula?: string;
  schoolId?: string;
  boostersApplied?: string[];
}

export interface ScoreBreakdown {
  aptitude: number;
  passion: number;
  community: number;
  demographics: number;
  total: number;
  schoolMultiplier?: number;
  finalScore: number;
}

// ============================================
// Input Trace Types
// ============================================

export interface InputTraceData {
  fieldId: string;
  fieldType: 'text' | 'number' | 'select' | 'slider' | 'chip' | 'voice' | 'toggle';
  previousValue: unknown;
  newValue: unknown;
  isValid: boolean;
  validationErrors?: string[];
  frameId: number;
  cardId?: string;
}

// ============================================
// State Change Trace Types
// ============================================

export interface StateChangeTraceData {
  storeName: string;
  action: string;
  path: string;
  previousState: unknown;
  nextState: unknown;
  triggeredBy: 'user' | 'system' | 'api' | 'hydration';
}

// ============================================
// Navigation Trace Types
// ============================================

export interface NavigationTraceData {
  fromFrame: number;
  toFrame: number;
  fromCard?: number;
  toCard?: number;
  direction: 'forward' | 'backward' | 'jump';
  trigger: 'button' | 'keyboard' | 'swipe' | 'auto';
  xpAwarded?: number;
}

// ============================================
// API Trace Types
// ============================================

export interface ApiTraceData {
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  requestPayload?: unknown;
  responseStatus?: number;
  responseData?: unknown;
  latencyMs: number;
  retryCount?: number;
}

// ============================================
// Twin Avatar Trace Types
// ============================================

export interface TwinTraceData {
  schoolId: string;
  schoolName: string;
  gearSlot: 'helmet' | 'armor' | 'weapon' | 'shield' | 'boots' | 'accessory';
  gearTier: 'rusty' | 'bronze' | 'iron' | 'silver' | 'gold' | 'diamond' | 'legendary' | 'mythic';
  previousGear?: string;
  newGear: string;
  attribute: string;
  attributeValue: number;
}

// ============================================
// Performance Trace Types
// ============================================

export interface PerformanceTraceData {
  metric: 'render' | 'hydration' | 'calculation' | 'animation' | 'network';
  componentName?: string;
  durationMs: number;
  frameDrops?: number;
  memoryUsage?: number;
}

// ============================================
// Debug Overlay Types
// ============================================

export interface DebugOverlayState {
  isVisible: boolean;
  activeTab: 'events' | 'spans' | 'scoring' | 'state' | 'performance';
  filter: {
    levels: TraceLevel[];
    domains: TraceDomain[];
    searchQuery: string;
  };
  isPaused: boolean;
  maxEvents: number;
}

// ============================================
// Trace Context Configuration
// ============================================

export interface TraceConfig {
  enabled: boolean;
  minLevel: TraceLevel;
  enabledDomains: TraceDomain[];
  persistToStorage: boolean;
  maxStoredEvents: number;
  maxStoredSpans: number;
  consoleOutput: boolean;
  debugOverlay: boolean;
  samplingRate: number; // 0-1, for production
  flushIntervalMs: number;
}

export const DEFAULT_TRACE_CONFIG: TraceConfig = {
  enabled: process.env.NODE_ENV === 'development',
  minLevel: 'debug',
  enabledDomains: ['scoring', 'input', 'state', 'navigation', 'api', 'twin', 'validation', 'performance'],
  persistToStorage: true,
  maxStoredEvents: 1000,
  maxStoredSpans: 100,
  consoleOutput: true,
  debugOverlay: process.env.NODE_ENV === 'development',
  samplingRate: 1.0,
  flushIntervalMs: 5000,
};

// Level priority for filtering
export const TRACE_LEVEL_PRIORITY: Record<TraceLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};
