/**
 * Frame 4: Reveal - Constants
 * Score tiers, school configs, categories, and animation timings
 */

// Score tier boundaries and labels
export const SCORE_TIERS = {
  exceptional: { min: 85, label: 'Exceptional', color: '#10B981' },
  competitive: { min: 70, label: 'Competitive', color: '#3B82F6' },
  average: { min: 50, label: 'Average', color: '#F59E0B' },
  below: { min: 0, label: 'Below Average', color: '#EF4444' },
} as const;

// Fit labels for school probability ranges
export const FIT_LABELS = {
  safety: { min: 40, label: 'Safety', color: '#10B981' },
  target: { min: 20, label: 'Target', color: '#F59E0B' },
  reach: { min: 0, label: 'Reach', color: '#EF4444' },
} as const;

// Category configuration for scoring breakdown
// Icons are now string identifiers - use getCategoryIcon() from lib/constants/icons.ts
export const CATEGORIES = [
  { id: 'aptitude', label: 'Aptitude', icon: 'aptitude', weight: 0.35, description: 'Academic performance & rigor' },
  { id: 'passion', label: 'Passion', icon: 'passion', weight: 0.30, description: 'Spike activities & depth' },
  { id: 'community', label: 'Community', icon: 'community', weight: 0.20, description: 'Service & leadership impact' },
  { id: 'operating', label: 'Operating', icon: 'operating', weight: 0.15, description: 'Style & execution capacity' },
] as const;

// School acceptance rates and configurations
export const SCHOOL_CONFIGS: Record<string, {
  name: string;
  acceptanceRate: number;
  color: string;
  strengths: string[];
  culture: string;
}> = {
  harvard: {
    name: 'Harvard University',
    acceptanceRate: 0.032,
    color: '#A51C30',
    strengths: ['leadership', 'academics', 'extracurriculars'],
    culture: 'Well-rounded achievers with leadership potential',
  },
  yale: {
    name: 'Yale University',
    acceptanceRate: 0.045,
    color: '#00356B',
    strengths: ['humanities', 'arts', 'community'],
    culture: 'Creative intellectuals with strong community ties',
  },
  princeton: {
    name: 'Princeton University',
    acceptanceRate: 0.040,
    color: '#FF8F00',
    strengths: ['research', 'academics', 'stem'],
    culture: 'Independent thinkers with research passion',
  },
  columbia: {
    name: 'Columbia University',
    acceptanceRate: 0.039,
    color: '#9BCBEB',
    strengths: ['urban', 'global', 'interdisciplinary'],
    culture: 'Global citizens thriving in urban environments',
  },
  upenn: {
    name: 'University of Pennsylvania',
    acceptanceRate: 0.059,
    color: '#011F5B',
    strengths: ['business', 'entrepreneurship', 'practical'],
    culture: 'Pragmatic innovators blending academics with action',
  },
  brown: {
    name: 'Brown University',
    acceptanceRate: 0.051,
    color: '#4E3629',
    strengths: ['open-curriculum', 'creativity', 'self-directed'],
    culture: 'Self-directed learners charting unique paths',
  },
  dartmouth: {
    name: 'Dartmouth College',
    acceptanceRate: 0.062,
    color: '#00693E',
    strengths: ['outdoors', 'community', 'undergraduate'],
    culture: 'Tight-knit community with outdoor spirit',
  },
  cornell: {
    name: 'Cornell University',
    acceptanceRate: 0.079,
    color: '#B31B1B',
    strengths: ['diversity', 'practical', 'stem'],
    culture: 'Diverse programs with hands-on learning',
  },
  mit: {
    name: 'MIT',
    acceptanceRate: 0.038,
    color: '#8B0000',
    strengths: ['stem', 'innovation', 'research'],
    culture: 'Makers and innovators solving hard problems',
  },
  stanford: {
    name: 'Stanford University',
    acceptanceRate: 0.036,
    color: '#8C1515',
    strengths: ['entrepreneurship', 'tech', 'innovation'],
    culture: 'Entrepreneurs and changemakers in Silicon Valley',
  },
  duke: {
    name: 'Duke University',
    acceptanceRate: 0.060,
    color: '#003087',
    strengths: ['athletics', 'research', 'community'],
    culture: 'Spirited achievers balancing academics and athletics',
  },
  northwestern: {
    name: 'Northwestern University',
    acceptanceRate: 0.070,
    color: '#4E2A84',
    strengths: ['journalism', 'arts', 'interdisciplinary'],
    culture: 'Creative professionals with diverse interests',
  },
};

// Launch sequence animation timings (in milliseconds)
export const LAUNCH_TIMINGS = {
  countdown: 3000,      // 3-2-1 countdown
  launch: 1200,         // Fleet liftoff
  flight: 800,          // Transit animation
  landing: 600,         // Impact moment
  revealDelay: 400,     // Pause before score
  scoreAnimation: 1500, // Score ring fill
  marketAnimation: 1200,// Market reality bar
  labelFadeIn: 300,     // Text fade in
} as const;

// Animation easing curves
export const EASING = {
  scoreReveal: [0.4, 0, 0.2, 1] as const,
  cardSwipe: [0.25, 0.1, 0.25, 1] as const,
  bounce: [0.68, -0.55, 0.265, 1.55] as const,
  smooth: [0.4, 0, 0.2, 1] as const,
} as const;

// Color scheme for reveal
export const REVEAL_COLORS = {
  // Score tiers
  exceptional: '#10B981',    // Green (85+)
  competitive: '#3B82F6',    // Blue (70-84)
  average: '#F59E0B',        // Amber (50-69)
  below: '#EF4444',          // Red (<50)

  // Fit labels
  reach: '#EF4444',          // Red
  target: '#F59E0B',         // Amber
  safety: '#10B981',         // Green

  // Category bars
  aptitude: '#3B82F6',       // Blue
  passion: '#F59E0B',        // Amber
  community: '#10B981',      // Green
  operating: '#8B5CF6',      // Purple
} as const;

// Benchmark labels for score context
export const SCORE_BENCHMARKS = [
  { value: 50, label: 'Average' },
  { value: 70, label: 'Competitive' },
  { value: 85, label: 'Exceptional' },
] as const;

// Card autoplay settings
export const SCHOOL_CARD_AUTOPLAY = {
  enabled: true,
  interval: 2500, // ms between cards
  pauseOnHover: true,
} as const;

// Screen shake configuration for landing
export const SCREEN_SHAKE = {
  intensity: 10,
  duration: 400,
  decay: 0.9,
} as const;

// Particle configuration for engine glow
export const ENGINE_PARTICLES = {
  count: 20,
  size: { min: 2, max: 6 },
  speed: { min: 1, max: 3 },
  color: '#F59E0B',
  lifetime: 1000,
} as const;
