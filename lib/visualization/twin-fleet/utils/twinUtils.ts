/**
 * IvyQuest v3.0 — Twin Fleet Utilities
 * 
 * Color manipulation, animation helpers, and visual calculations.
 * 
 * @version 1.0.0
 * @module lib/utils/twinUtils
 */

import {
  SCORE_TIERS,
  SCHOOL_COLORS,
  ANIMATION_TIMINGS,
  type ScoreTierId,
  type SchoolId,
} from '../constants/twin.constants';

// ============================================================================
// COLOR UTILITIES
// ============================================================================

/**
 * Parse hex color to RGB components
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

/**
 * Convert RGB to hex color
 */
export function rgbToHex(r: number, g: number, b: number): string {
  return '#' + [r, g, b].map(x => {
    const hex = Math.round(Math.max(0, Math.min(255, x))).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
}

/**
 * Interpolate between two colors
 */
export function lerpColor(color1: string, color2: string, t: number): string {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  
  if (!rgb1 || !rgb2) return color1;
  
  const r = Math.round(rgb1.r + (rgb2.r - rgb1.r) * t);
  const g = Math.round(rgb1.g + (rgb2.g - rgb1.g) * t);
  const b = Math.round(rgb1.b + (rgb2.b - rgb1.b) * t);
  
  return rgbToHex(r, g, b);
}

/**
 * Adjust color brightness
 */
export function adjustBrightness(hex: string, percent: number): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  
  const factor = 1 + (percent / 100);
  
  return rgbToHex(
    rgb.r * factor,
    rgb.g * factor,
    rgb.b * factor
  );
}

/**
 * Get color with alpha
 */
export function withAlpha(hex: string, alpha: number): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
}

/**
 * Create gradient string
 */
export function createGradient(
  colors: string[],
  direction: string = '135deg'
): string {
  const stops = colors.map((color, i) => {
    const percent = (i / (colors.length - 1)) * 100;
    return `${color} ${percent}%`;
  });
  
  return `linear-gradient(${direction}, ${stops.join(', ')})`;
}

// ============================================================================
// TIER UTILITIES
// ============================================================================

/**
 * Get tier from score
 */
export function getTierFromScore(score: number): ScoreTierId {
  if (score >= 85) return 'exceptional';
  if (score >= 70) return 'competitive';
  if (score >= 50) return 'average';
  return 'developing';
}

/**
 * Get tier configuration
 */
export function getTierConfig(tier: ScoreTierId) {
  return SCORE_TIERS[tier];
}

/**
 * Get tier colors
 */
export function getTierColors(tier: ScoreTierId) {
  return SCORE_TIERS[tier].colors;
}

/**
 * Get school colors
 */
export function getSchoolColors(schoolId: SchoolId) {
  return SCHOOL_COLORS[schoolId];
}

/**
 * Blend tier colors with school colors
 */
export function blendTierAndSchoolColors(
  tier: ScoreTierId,
  schoolId: SchoolId,
  blendFactor: number = 0.5
) {
  const tierColors = getTierColors(tier);
  const schoolColors = getSchoolColors(schoolId);
  
  return {
    primary: lerpColor(tierColors.primary, schoolColors.primary, blendFactor),
    secondary: lerpColor(tierColors.secondary, schoolColors.secondary, blendFactor),
    glow: lerpColor(tierColors.glow, schoolColors.accent, blendFactor),
  };
}

// ============================================================================
// ANIMATION UTILITIES
// ============================================================================

/**
 * Linear interpolation
 */
export function lerp(start: number, end: number, t: number): number {
  return start + (end - start) * t;
}

/**
 * Clamp value between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

/**
 * Easing functions
 */
export const easings = {
  linear: (t: number) => t,
  easeIn: (t: number) => t * t,
  easeOut: (t: number) => t * (2 - t),
  easeInOut: (t: number) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  easeOutCubic: (t: number) => 1 - Math.pow(1 - t, 3),
  easeOutQuart: (t: number) => 1 - Math.pow(1 - t, 4),
  easeOutElastic: (t: number) => {
    const c4 = (2 * Math.PI) / 3;
    return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  },
  easeOutBounce: (t: number) => {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1 / d1) {
      return n1 * t * t;
    } else if (t < 2 / d1) {
      return n1 * (t -= 1.5 / d1) * t + 0.75;
    } else if (t < 2.5 / d1) {
      return n1 * (t -= 2.25 / d1) * t + 0.9375;
    } else {
      return n1 * (t -= 2.625 / d1) * t + 0.984375;
    }
  },
};

/**
 * Create animation frame counter
 */
export function createAnimationCounter(
  from: number,
  to: number,
  duration: number,
  easing: keyof typeof easings = 'easeOut',
  onUpdate: (value: number) => void,
  onComplete?: () => void
) {
  const startTime = performance.now();
  const easingFn = easings[easing];
  
  function update(currentTime: number) {
    const elapsed = currentTime - startTime;
    const progress = clamp(elapsed / duration, 0, 1);
    const easedProgress = easingFn(progress);
    const currentValue = lerp(from, to, easedProgress);
    
    onUpdate(Math.round(currentValue));
    
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      onUpdate(to);
      onComplete?.();
    }
  }
  
  requestAnimationFrame(update);
}

/**
 * Generate staggered delays
 */
export function staggerDelay(index: number, baseDelay: number = 100): number {
  return index * baseDelay;
}

/**
 * Get animation phase based on elapsed time
 */
export function getAnimationPhase(
  elapsed: number,
  phases: { name: string; duration: number }[]
): { phase: string; progress: number; phaseIndex: number } {
  let accumulated = 0;
  
  for (let i = 0; i < phases.length; i++) {
    const phase = phases[i];
    if (elapsed < accumulated + phase.duration) {
      const phaseElapsed = elapsed - accumulated;
      return {
        phase: phase.name,
        progress: phaseElapsed / phase.duration,
        phaseIndex: i,
      };
    }
    accumulated += phase.duration;
  }
  
  return {
    phase: phases[phases.length - 1].name,
    progress: 1,
    phaseIndex: phases.length - 1,
  };
}

// ============================================================================
// POSITION UTILITIES
// ============================================================================

/**
 * Calculate arc positions for fleet display
 */
export function calculateArcPositions(
  count: number,
  centerX: number,
  centerY: number,
  radius: number,
  startAngle: number = -60,
  endAngle: number = 60
): { x: number; y: number }[] {
  const positions: { x: number; y: number }[] = [];
  const angleStep = count > 1 ? (endAngle - startAngle) / (count - 1) : 0;
  
  for (let i = 0; i < count; i++) {
    const angle = startAngle + (i * angleStep);
    const radians = (angle * Math.PI) / 180;
    positions.push({
      x: centerX + radius * Math.sin(radians),
      y: centerY - radius * Math.cos(radians),
    });
  }
  
  return positions;
}

/**
 * Calculate grid positions for fleet display
 */
export function calculateGridPositions(
  count: number,
  columns: number,
  startX: number,
  startY: number,
  gap: number
): { x: number; y: number }[] {
  const positions: { x: number; y: number }[] = [];
  
  for (let i = 0; i < count; i++) {
    const col = i % columns;
    const row = Math.floor(i / columns);
    positions.push({
      x: startX + col * gap,
      y: startY + row * gap,
    });
  }
  
  return positions;
}

/**
 * Calculate orbital positions
 */
export function calculateOrbitalPositions(
  count: number,
  centerX: number,
  centerY: number,
  radius: number,
  rotation: number = 0
): { x: number; y: number }[] {
  const positions: { x: number; y: number }[] = [];
  const angleStep = 360 / count;
  
  for (let i = 0; i < count; i++) {
    const angle = rotation + (i * angleStep);
    const radians = (angle * Math.PI) / 180;
    positions.push({
      x: centerX + radius * Math.cos(radians),
      y: centerY + radius * Math.sin(radians),
    });
  }
  
  return positions;
}

// ============================================================================
// PARTICLE UTILITIES
// ============================================================================

/**
 * Generate random particle
 */
export function createParticle(
  bounds: { width: number; height: number },
  config: {
    color: string;
    sizeRange: { min: number; max: number };
    speedRange: { min: number; max: number };
    lifespanRange: { min: number; max: number };
  }
) {
  const angle = Math.random() * Math.PI * 2;
  const speed = config.speedRange.min + Math.random() * (config.speedRange.max - config.speedRange.min);
  
  return {
    id: `particle-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    x: Math.random() * bounds.width,
    y: Math.random() * bounds.height,
    size: config.sizeRange.min + Math.random() * (config.sizeRange.max - config.sizeRange.min),
    opacity: 0.3 + Math.random() * 0.5,
    color: config.color,
    velocity: {
      x: Math.cos(angle) * speed,
      y: Math.sin(angle) * speed,
    },
    lifespan: config.lifespanRange.min + Math.random() * (config.lifespanRange.max - config.lifespanRange.min),
    age: 0,
  };
}

/**
 * Update particle position
 */
export function updateParticle(
  particle: ReturnType<typeof createParticle>,
  deltaTime: number,
  bounds: { width: number; height: number }
) {
  // Update position
  particle.x += particle.velocity.x * deltaTime;
  particle.y += particle.velocity.y * deltaTime;
  
  // Wrap around bounds
  if (particle.x < 0) particle.x = bounds.width;
  if (particle.x > bounds.width) particle.x = 0;
  if (particle.y < 0) particle.y = bounds.height;
  if (particle.y > bounds.height) particle.y = 0;
  
  // Update age
  particle.age += deltaTime;
  
  // Fade out as approaching lifespan
  const lifeProgress = particle.age / particle.lifespan;
  if (lifeProgress > 0.7) {
    particle.opacity = (1 - (lifeProgress - 0.7) / 0.3) * 0.8;
  }
  
  return particle;
}

// ============================================================================
// PROBABILITY UTILITIES
// ============================================================================

/**
 * Get probability color based on thresholds
 */
export function getProbabilityColor(probability: number): string {
  if (probability >= 30) return '#10B981'; // Green
  if (probability >= 15) return '#F59E0B'; // Yellow
  if (probability >= 5) return '#F97316';  // Orange
  return '#EF4444';                         // Red
}

/**
 * Get probability label
 */
export function getProbabilityLabel(probability: number): string {
  if (probability >= 30) return 'Safety';
  if (probability >= 15) return 'Target';
  if (probability >= 5) return 'Reach';
  return 'Far Reach';
}

/**
 * Format probability as percentage
 */
export function formatProbability(probability: number): string {
  if (probability < 1) return '<1%';
  if (probability > 95) return '>95%';
  return `${Math.round(probability)}%`;
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  // Color
  hexToRgb,
  rgbToHex,
  lerpColor,
  adjustBrightness,
  withAlpha,
  createGradient,
  
  // Tier
  getTierFromScore,
  getTierConfig,
  getTierColors,
  getSchoolColors,
  blendTierAndSchoolColors,
  
  // Animation
  lerp,
  clamp,
  easings,
  createAnimationCounter,
  staggerDelay,
  getAnimationPhase,
  
  // Position
  calculateArcPositions,
  calculateGridPositions,
  calculateOrbitalPositions,
  
  // Particle
  createParticle,
  updateParticle,
  
  // Probability
  getProbabilityColor,
  getProbabilityLabel,
  formatProbability,
};
