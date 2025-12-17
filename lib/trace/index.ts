/**
 * Trace System - Public API
 * E2E trace logging for scoring, inputs, and state changes
 */

// Core trace context
export { traceContext, TraceContext } from './TraceContext';

// Domain-specific loggers
export {
  scoringLogger,
  inputLogger,
  stateLogger,
  navigationLogger,
  apiLogger,
  twinLogger,
  performanceLogger,
} from './loggers';

// Zustand store and hooks
export {
  useTraceStore,
  initializeTraceStore,
  useTraceKeyboard,
} from './useTraceStore';

// Types
export type {
  TraceLevel,
  TraceDomain,
  TraceEvent,
  TraceSpan,
  TraceConfig,
  ScoringTraceData,
  ScoreBreakdown,
  InputTraceData,
  StateChangeTraceData,
  NavigationTraceData,
  ApiTraceData,
  TwinTraceData,
  PerformanceTraceData,
  DebugOverlayState,
} from './types';

export { DEFAULT_TRACE_CONFIG, TRACE_LEVEL_PRIORITY } from './types';
