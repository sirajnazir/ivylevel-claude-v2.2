/**
 * IvyQuest v3.0 — Twin Fleet Constants
 * 
 * School colors, avatar configurations, and animation timings.
 * 
 * @version 1.0.0
 * @module lib/constants/twin.constants
 */

// ============================================================================
// SCORE TIER CONFIGURATION
// ============================================================================

export const SCORE_TIERS = {
  exceptional: {
    id: 'exceptional',
    label: 'Exceptional',
    minScore: 85,
    maxScore: 100,
    colors: {
      primary: '#FFD700',    // Gold
      secondary: '#FFA500',  // Orange
      glow: '#FFEC8B',       // Light gold
    },
    auraIntensity: 1.0,
    particleDensity: 1.5,
    animationSpeed: 1.2,
  },
  competitive: {
    id: 'competitive',
    label: 'Competitive',
    minScore: 70,
    maxScore: 84,
    colors: {
      primary: '#00D4FF',    // Cyan
      secondary: '#0EA5E9',  // Sky blue
      glow: '#7DD3FC',       // Light cyan
    },
    auraIntensity: 0.8,
    particleDensity: 1.2,
    animationSpeed: 1.0,
  },
  average: {
    id: 'average',
    label: 'Average',
    minScore: 50,
    maxScore: 69,
    colors: {
      primary: '#3B82F6',    // Blue
      secondary: '#6366F1',  // Indigo
      glow: '#93C5FD',       // Light blue
    },
    auraIntensity: 0.6,
    particleDensity: 0.8,
    animationSpeed: 0.9,
  },
  developing: {
    id: 'developing',
    label: 'Developing',
    minScore: 0,
    maxScore: 49,
    colors: {
      primary: '#6B7280',    // Gray
      secondary: '#9CA3AF',  // Light gray
      glow: '#D1D5DB',       // Lighter gray
    },
    auraIntensity: 0.4,
    particleDensity: 0.5,
    animationSpeed: 0.8,
  },
} as const;

export type ScoreTierId = keyof typeof SCORE_TIERS;

// ============================================================================
// SCHOOL COLOR PALETTE
// ============================================================================

export const SCHOOL_COLORS = {
  HARVARD: {
    id: 'HARVARD',
    name: 'Harvard',
    primary: '#A51C30',      // Crimson
    secondary: '#1E1E1E',    // Black
    accent: '#FFD700',       // Gold
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #A51C30 0%, #6B1220 100%)',
  },
  YALE: {
    id: 'YALE',
    name: 'Yale',
    primary: '#0F4D92',      // Yale Blue
    secondary: '#FFFFFF',    // White
    accent: '#00356B',       // Dark blue
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #0F4D92 0%, #00356B 100%)',
  },
  PRINCETON: {
    id: 'PRINCETON',
    name: 'Princeton',
    primary: '#FF8F00',      // Orange
    secondary: '#000000',    // Black
    accent: '#E77500',       // Dark orange
    text: '#000000',
    gradient: 'linear-gradient(135deg, #FF8F00 0%, #E77500 100%)',
  },
  STANFORD: {
    id: 'STANFORD',
    name: 'Stanford',
    primary: '#8C1515',      // Cardinal
    secondary: '#FFFFFF',    // White
    accent: '#B83A4B',       // Light cardinal
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #8C1515 0%, #5E0D0D 100%)',
  },
  MIT: {
    id: 'MIT',
    name: 'MIT',
    primary: '#750014',      // MIT Red
    secondary: '#8A8B8C',    // Gray
    accent: '#A31F34',       // Cardinal
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #750014 0%, #A31F34 100%)',
  },
  COLUMBIA: {
    id: 'COLUMBIA',
    name: 'Columbia',
    primary: '#B9D9EB',      // Columbia Blue
    secondary: '#002B7F',    // Dark blue
    accent: '#9BCBEB',       // Light blue
    text: '#002B7F',
    gradient: 'linear-gradient(135deg, #002B7F 0%, #004AAD 100%)',
  },
  PENN: {
    id: 'PENN',
    name: 'Penn',
    primary: '#011F5B',      // Penn Blue
    secondary: '#990000',    // Penn Red
    accent: '#004785',       // Light blue
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #011F5B 0%, #990000 100%)',
  },
  BROWN: {
    id: 'BROWN',
    name: 'Brown',
    primary: '#4E3629',      // Brown
    secondary: '#ED1C24',    // Red
    accent: '#6B4423',       // Light brown
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #4E3629 0%, #2D1F18 100%)',
  },
  DARTMOUTH: {
    id: 'DARTMOUTH',
    name: 'Dartmouth',
    primary: '#00693E',      // Dartmouth Green
    secondary: '#FFFFFF',    // White
    accent: '#12312B',       // Dark green
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #00693E 0%, #004225 100%)',
  },
  CORNELL: {
    id: 'CORNELL',
    name: 'Cornell',
    primary: '#B31B1B',      // Carnelian
    secondary: '#FFFFFF',    // White
    accent: '#222222',       // Dark gray
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #B31B1B 0%, #7E1313 100%)',
  },
  DUKE: {
    id: 'DUKE',
    name: 'Duke',
    primary: '#003087',      // Duke Blue
    secondary: '#FFFFFF',    // White
    accent: '#001A57',       // Navy
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #003087 0%, #001A57 100%)',
  },
  NORTHWESTERN: {
    id: 'NORTHWESTERN',
    name: 'Northwestern',
    primary: '#4E2A84',      // Purple
    secondary: '#FFFFFF',    // White
    accent: '#836EAA',       // Light purple
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #4E2A84 0%, #372060 100%)',
  },
  UCHICAGO: {
    id: 'UCHICAGO',
    name: 'UChicago',
    primary: '#800000',      // Maroon
    secondary: '#FFFFFF',    // White
    accent: '#A50000',       // Light maroon
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #800000 0%, #5A0000 100%)',
  },
  CALTECH: {
    id: 'CALTECH',
    name: 'Caltech',
    primary: '#FF6C0C',      // Orange
    secondary: '#FFFFFF',    // White
    accent: '#76777B',       // Gray
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #FF6C0C 0%, #C65000 100%)',
  },
  JOHNS_HOPKINS: {
    id: 'JOHNS_HOPKINS',
    name: 'Johns Hopkins',
    primary: '#002D72',      // Hopkins Blue
    secondary: '#FFFFFF',    // White
    accent: '#68ACE5',       // Light blue
    text: '#FFFFFF',
    gradient: 'linear-gradient(135deg, #002D72 0%, #001A42 100%)',
  },
} as const;

export type SchoolId = keyof typeof SCHOOL_COLORS;

// ============================================================================
// OPERATING STYLE VISUALS
// ============================================================================

export const OPERATING_STYLE_VISUALS = {
  methodical_builder: {
    id: 'methodical_builder',
    label: 'Methodical Builder',
    particlePattern: 'structured',
    animationStyle: 'steady',
    auraShape: 'geometric',
    pulseRate: 0.8,
  },
  dynamic_leader: {
    id: 'dynamic_leader',
    label: 'Dynamic Leader',
    particlePattern: 'expansive',
    animationStyle: 'energetic',
    auraShape: 'radiant',
    pulseRate: 1.2,
  },
  creative_explorer: {
    id: 'creative_explorer',
    label: 'Creative Explorer',
    particlePattern: 'flowing',
    animationStyle: 'organic',
    auraShape: 'fluid',
    pulseRate: 1.0,
  },
  analytical_thinker: {
    id: 'analytical_thinker',
    label: 'Analytical Thinker',
    particlePattern: 'precise',
    animationStyle: 'calculated',
    auraShape: 'angular',
    pulseRate: 0.9,
  },
  collaborative_connector: {
    id: 'collaborative_connector',
    label: 'Collaborative Connector',
    particlePattern: 'networked',
    animationStyle: 'harmonic',
    auraShape: 'orbital',
    pulseRate: 1.1,
  },
} as const;

export type OperatingStyleId = keyof typeof OPERATING_STYLE_VISUALS;

// ============================================================================
// AVATAR SIZES
// ============================================================================

export const TWIN_SIZES = {
  xs: { width: 48, height: 72, scale: 0.5 },
  sm: { width: 64, height: 96, scale: 0.7 },
  md: { width: 96, height: 144, scale: 1.0 },
  lg: { width: 128, height: 192, scale: 1.3 },
  xl: { width: 192, height: 288, scale: 1.8 },
} as const;

export type TwinSize = keyof typeof TWIN_SIZES;

// ============================================================================
// ANIMATION TIMINGS (ms)
// ============================================================================

export const ANIMATION_TIMINGS = {
  // Materialization sequence
  materialize: {
    particleConverge: 300,
    silhouetteForm: 300,
    featuresResolve: 300,
    auraActivate: 300,
    total: 1200,
  },
  
  // Score reveal
  scoreReveal: {
    counterStart: 0,
    countUp: 1000,
    landOnFinal: 500,
    tierBadge: 200,
    auraIntensify: 300,
    total: 2000,
  },
  
  // School twin spawn
  schoolSpawn: {
    basePulse: 200,
    cloneSeparate: 200,
    moveToPosition: 200,
    colorsApply: 200,
    fitRingAppear: 200,
    total: 800,
  },
  
  // Launch sequence
  launch: {
    backgroundDim: 150,
    twinElevate: 150,
    lightStreak: 150,
    sceneTransition: 150,
    fadeIn: 150,
    total: 600,
  },
  
  // General
  auraFloat: 3000,      // Aura breathing animation
  particleCycle: 5000,  // Particle orbit cycle
  idleBob: 2000,        // Idle bobbing motion
  pulseInterval: 1500,  // Pulse effect interval
} as const;

// ============================================================================
// PARTICLE CONFIGURATION
// ============================================================================

export const PARTICLE_CONFIG = {
  base: {
    count: 20,
    size: { min: 2, max: 6 },
    speed: { min: 0.5, max: 1.5 },
    opacity: { min: 0.3, max: 0.8 },
    lifespan: { min: 2000, max: 4000 },
  },
  
  dense: {
    count: 40,
    size: { min: 2, max: 8 },
    speed: { min: 0.8, max: 2.0 },
    opacity: { min: 0.4, max: 0.9 },
    lifespan: { min: 1500, max: 3500 },
  },
  
  sparse: {
    count: 10,
    size: { min: 2, max: 4 },
    speed: { min: 0.3, max: 1.0 },
    opacity: { min: 0.2, max: 0.6 },
    lifespan: { min: 2500, max: 5000 },
  },
} as const;

// ============================================================================
// AURA CONFIGURATION
// ============================================================================

export const AURA_CONFIG = {
  baseBlur: 20,
  maxBlur: 40,
  baseShadowSize: 30,
  maxShadowSize: 60,
  breathingAmplitude: 0.1,
  glowLayers: 3,
} as const;

// ============================================================================
// FLEET LAYOUT
// ============================================================================

export const FLEET_LAYOUTS = {
  arc: {
    id: 'arc',
    description: 'School twins arranged in arc above base',
    baseTwinPosition: { x: 50, y: 70 },  // % position
    schoolTwinRadius: 35,                 // % from center
    schoolTwinStartAngle: -60,            // degrees
    schoolTwinEndAngle: 60,               // degrees
  },
  grid: {
    id: 'grid',
    description: 'School twins in grid, base twin below',
    baseTwinPosition: { x: 50, y: 80 },
    gridColumns: 4,
    gridGap: 15,                          // %
    gridStartY: 10,                       // %
  },
  line: {
    id: 'line',
    description: 'All twins in horizontal line',
    baseTwinPosition: { x: 50, y: 50 },
    lineY: 50,                            // %
    lineSpacing: 12,                      // %
  },
  focus: {
    id: 'focus',
    description: 'Selected twin large, others small around',
    baseTwinPosition: { x: 50, y: 50 },
    focusScale: 1.5,
    othersScale: 0.6,
    orbitalRadius: 40,                    // %
  },
} as const;

export type FleetLayoutId = keyof typeof FLEET_LAYOUTS;

// ============================================================================
// HUD CONFIGURATION
// ============================================================================

export const HUD_CONFIG = {
  hudOpacity: 0.9,
  showScoreBars: true,
  showSchoolLabels: true,
  showProbabilityBadges: true,
  showStyleMatchIndicator: true,
  animateScoreChanges: true,
  
  scoreBarColors: {
    aptitude: '#3B82F6',    // Blue
    passion: '#F59E0B',     // Amber
    community: '#10B981',   // Emerald
    operating: '#8B5CF6',   // Purple
  },
  
  probabilityThresholds: {
    high: 30,      // >= 30% = green
    medium: 15,    // >= 15% = yellow
    low: 5,        // >= 5% = orange
    veryLow: 0,    // < 5% = red
  },
  
  probabilityColors: {
    high: '#10B981',
    medium: '#F59E0B',
    low: '#F97316',
    veryLow: '#EF4444',
  },
} as const;

// ============================================================================
// COMMAND DECK THEMES
// ============================================================================

export const COMMAND_DECK_THEMES = {
  default: {
    id: 'default',
    background: 'linear-gradient(180deg, #0F172A 0%, #1E293B 100%)',
    gridColor: 'rgba(59, 130, 246, 0.1)',
    accentColor: '#00D4FF',
    textColor: '#FFFFFF',
    hudOpacity: 0.9,
  },
  // School-specific themes derived from SCHOOL_COLORS at runtime
} as const;

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  SCORE_TIERS,
  SCHOOL_COLORS,
  OPERATING_STYLE_VISUALS,
  TWIN_SIZES,
  ANIMATION_TIMINGS,
  PARTICLE_CONFIG,
  AURA_CONFIG,
  FLEET_LAYOUTS,
  HUD_CONFIG,
  COMMAND_DECK_THEMES,
};
