/**
 * ReAct Visualization Components
 * ===============================
 *
 * Barrel exports for ReAct cycle visualization components.
 * These components display THINK → ACT → OBSERVE → LEARN cycles
 * similar to Claude AI's thinking accordion pattern.
 */

export { ReActVisualization } from './ReActVisualization';
export { CycleCard } from './CycleCard';
export { PhaseAccordion } from './PhaseAccordion';

// Re-export types for convenience
export type {
  ReactMetadata,
  CycleSummary,
  ThinkPhaseData,
  ActPhaseData,
  ObservePhaseData,
  LearnPhaseData,
  PhaseType,
  PhaseColorConfig,
  InputDataFlow,
  // EC Engine types
  FourPillarsData,
  TenDimensionsData,
  PillarData,
  DimensionData,
  GeneratedActivity,
  ECGenerationResult,
  PillarType,
  DimensionType,
} from '@/lib/types/react-visualization';

// Re-export constants
export {
  PHASE_COLORS,
  PILLAR_COLORS,
  PILLAR_ICONS,
  DIMENSION_PRIORITY_COLORS,
  PHASE_CONFIG,
  DIMENSION_CONFIG,
} from '@/lib/types/react-visualization';
