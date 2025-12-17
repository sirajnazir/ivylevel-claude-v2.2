/**
 * IvyQuest v3.0 — Analytics Hooks
 * 
 * React hooks for analytics functionality.
 * 
 * @version 1.0.0
 * @module hooks
 */

// Main hooks are exported from context
export { useAnalytics, useSessionMetrics } from '../context/AnalyticsContext';

// Re-export for convenience
export type {
  UseAnalyticsReturn,
  UseSessionMetricsReturn,
} from '../types/analytics.types';
