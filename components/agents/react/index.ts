/**
 * ReAct Visualization Components
 * ===============================
 *
 * Barrel exports for ReAct cycle visualization components.
 * v5.1: Updated to support THINK → REASON → ACT → VALIDATE phases
 * (with backwards compatibility for THINK → ACT → OBSERVE → LEARN)
 */

export { ReActVisualization } from './ReActVisualization';
export { CycleCard } from './CycleCard';
export { PhaseAccordion } from './PhaseAccordion';

// Re-export types for convenience
export type {
  // v5.1 ReAct types
  ReActPhase,
  ReActCycle,
  ReasonPhaseData,
  ValidatePhaseData,
  QualityScore,
  QualityWeights,
  QualityStatus,
  QualityTier,
  // Legacy types (backwards compatible)
  ReactMetadata,
  CycleSummary,
  ThinkPhaseData,
  ActPhaseData,
  ObservePhaseData,
  LearnPhaseData,
  PhaseType,
  LegacyPhaseType,
  PhaseColorConfig,
  InputDataFlow,
  // EC Engine types
  FourPillarsData,
  FourPillars,
  TenDimensionsData,
  TenDimensions,
  PillarData,
  DimensionData,
  GeneratedActivity,
  ECGenerationResult,
  PillarType,
  DimensionType,
  ActivityType,
  ActivitySource,
  GapType,
  OnlyTheyResult,
  // v5.1 New types
  IdentitySynthesis,
  ReframeData,
  ECContext,
  GamePlanResult,
} from '@/lib/types/react-visualization';

// Re-export constants
export {
  PHASE_COLORS,
  PILLAR_COLORS,
  PILLAR_ICONS,
  DIMENSION_PRIORITY_COLORS,
  PHASE_CONFIG,
  DIMENSION_CONFIG,
  QUALITY_TIER_COLORS,
  DEFAULT_QUALITY_WEIGHTS,
} from '@/lib/types/react-visualization';
