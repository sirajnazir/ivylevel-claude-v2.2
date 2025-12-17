/**
 * IvyQuest v3.0 — Theme Constants
 * 
 * Design system tokens for colors, spacing, typography.
 * 
 * @version 1.0.0
 * @module lib/constants/theme.constants
 */

// ============================================================================
// COLORS
// ============================================================================

export const colors = {
  // Primary gradient
  primary: {
    50: '#E6FAFF',
    100: '#B3F0FF',
    200: '#80E6FF',
    300: '#4DDBFF',
    400: '#1AD1FF',
    500: '#00D4FF',  // Main
    600: '#00A8CC',
    700: '#007C99',
    800: '#005066',
    900: '#002433',
  },
  
  // Secondary (Sky)
  sky: {
    50: '#F0F9FF',
    100: '#E0F2FE',
    200: '#BAE6FD',
    300: '#7DD3FC',
    400: '#38BDF8',
    500: '#0EA5E9',  // Main
    600: '#0284C7',
    700: '#0369A1',
    800: '#075985',
    900: '#0C4A6E',
  },
  
  // Blue
  blue: {
    50: '#EFF6FF',
    100: '#DBEAFE',
    200: '#BFDBFE',
    300: '#93C5FD',
    400: '#60A5FA',
    500: '#3B82F6',  // Main
    600: '#2563EB',
    700: '#1D4ED8',
    800: '#1E40AF',
    900: '#1E3A8A',
  },
  
  // Indigo
  indigo: {
    50: '#EEF2FF',
    100: '#E0E7FF',
    200: '#C7D2FE',
    300: '#A5B4FC',
    400: '#818CF8',
    500: '#6366F1',  // Main
    600: '#4F46E5',
    700: '#4338CA',
    800: '#3730A3',
    900: '#312E81',
  },
  
  // Purple
  purple: {
    50: '#FAF5FF',
    100: '#F3E8FF',
    200: '#E9D5FF',
    300: '#D8B4FE',
    400: '#C084FC',
    500: '#A855F7',
    600: '#9333EA',
    700: '#7C3AED',
    800: '#6B21A8',
    900: '#581C87',
  },
  
  // Semantic - Success (Emerald)
  success: {
    50: '#ECFDF5',
    100: '#D1FAE5',
    200: '#A7F3D0',
    300: '#6EE7B7',
    400: '#34D399',
    500: '#10B981',  // Main
    600: '#059669',
    700: '#047857',
    800: '#065F46',
    900: '#064E3B',
  },
  
  // Semantic - Warning (Amber)
  warning: {
    50: '#FFFBEB',
    100: '#FEF3C7',
    200: '#FDE68A',
    300: '#FCD34D',
    400: '#FBBF24',
    500: '#F59E0B',  // Main
    600: '#D97706',
    700: '#B45309',
    800: '#92400E',
    900: '#78350F',
  },
  
  // Semantic - Error (Red)
  error: {
    50: '#FEF2F2',
    100: '#FEE2E2',
    200: '#FECACA',
    300: '#FCA5A5',
    400: '#F87171',
    500: '#EF4444',  // Main
    600: '#DC2626',
    700: '#B91C1C',
    800: '#991B1B',
    900: '#7F1D1D',
  },
  
  // Neutrals (Slate)
  neutral: {
    50: '#F8FAFC',
    100: '#F1F5F9',
    200: '#E2E8F0',
    300: '#CBD5E1',
    400: '#94A3B8',
    500: '#64748B',
    600: '#475569',
    700: '#334155',
    800: '#1E293B',
    900: '#0F172A',
    950: '#020617',
  },
  
  // Pure
  white: '#FFFFFF',
  black: '#000000',
  transparent: 'transparent',
} as const;

// ============================================================================
// SCORE TIER COLORS
// ============================================================================

export const tierColors = {
  exceptional: {
    primary: '#FFD700',
    secondary: '#FFA500',
    glow: '#FFEC8B',
    bg: 'rgba(255, 215, 0, 0.1)',
    border: 'rgba(255, 215, 0, 0.3)',
  },
  competitive: {
    primary: '#00D4FF',
    secondary: '#0EA5E9',
    glow: '#7DD3FC',
    bg: 'rgba(0, 212, 255, 0.1)',
    border: 'rgba(0, 212, 255, 0.3)',
  },
  average: {
    primary: '#3B82F6',
    secondary: '#6366F1',
    glow: '#93C5FD',
    bg: 'rgba(59, 130, 246, 0.1)',
    border: 'rgba(59, 130, 246, 0.3)',
  },
  developing: {
    primary: '#6B7280',
    secondary: '#9CA3AF',
    glow: '#D1D5DB',
    bg: 'rgba(107, 114, 128, 0.1)',
    border: 'rgba(107, 114, 128, 0.3)',
  },
} as const;

export type TierColorKey = keyof typeof tierColors;

// ============================================================================
// SPACING
// ============================================================================

export const spacing = {
  px: '1px',
  0: '0',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  11: '2.75rem',    // 44px
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
} as const;

// Named spacing tokens
export const spacingTokens = {
  xs: spacing[1],   // 4px
  sm: spacing[2],   // 8px
  md: spacing[4],   // 16px
  lg: spacing[6],   // 24px
  xl: spacing[8],   // 32px
  '2xl': spacing[12], // 48px
} as const;

// ============================================================================
// TYPOGRAPHY
// ============================================================================

export const fontFamily = {
  sans: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif',
  mono: '"JetBrains Mono", "SF Mono", Monaco, "Cascadia Code", monospace',
} as const;

export const fontSize = {
  xs: ['0.75rem', { lineHeight: '1rem' }],       // 12px
  sm: ['0.875rem', { lineHeight: '1.25rem' }],   // 14px
  base: ['1rem', { lineHeight: '1.5rem' }],      // 16px
  lg: ['1.125rem', { lineHeight: '1.75rem' }],   // 18px
  xl: ['1.25rem', { lineHeight: '1.75rem' }],    // 20px
  '2xl': ['1.5rem', { lineHeight: '2rem' }],     // 24px
  '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
  '4xl': ['2.25rem', { lineHeight: '2.5rem' }],  // 36px
  '5xl': ['3rem', { lineHeight: '1' }],          // 48px
  '6xl': ['3.75rem', { lineHeight: '1' }],       // 60px
} as const;

export const fontWeight = {
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  extrabold: '800',
} as const;

// Named typography tokens
export const typography = {
  display: { size: '3rem', weight: '700', lineHeight: '1' },
  h1: { size: '2rem', weight: '700', lineHeight: '2.5rem' },
  h2: { size: '1.5rem', weight: '600', lineHeight: '2rem' },
  h3: { size: '1.25rem', weight: '600', lineHeight: '1.75rem' },
  body: { size: '1rem', weight: '400', lineHeight: '1.5rem' },
  small: { size: '0.875rem', weight: '400', lineHeight: '1.25rem' },
  xs: { size: '0.75rem', weight: '400', lineHeight: '1rem' },
} as const;

// ============================================================================
// BORDERS
// ============================================================================

export const borderRadius = {
  none: '0',
  sm: '0.125rem',    // 2px
  DEFAULT: '0.25rem', // 4px
  md: '0.375rem',    // 6px
  lg: '0.5rem',      // 8px
  xl: '0.75rem',     // 12px
  '2xl': '1rem',     // 16px
  '3xl': '1.5rem',   // 24px
  full: '9999px',
} as const;

export const borderWidth = {
  0: '0',
  DEFAULT: '1px',
  2: '2px',
  4: '4px',
} as const;

// ============================================================================
// SHADOWS
// ============================================================================

export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
  
  // Glow shadows
  glow: {
    primary: '0 0 20px rgba(0, 212, 255, 0.3)',
    success: '0 0 20px rgba(16, 185, 129, 0.3)',
    warning: '0 0 20px rgba(245, 158, 11, 0.3)',
    error: '0 0 20px rgba(239, 68, 68, 0.3)',
    gold: '0 0 30px rgba(255, 215, 0, 0.4)',
  },
} as const;

// ============================================================================
// TRANSITIONS
// ============================================================================

export const transitions = {
  duration: {
    fast: '100ms',
    normal: '200ms',
    slow: '300ms',
    slower: '500ms',
  },
  timing: {
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    linear: 'linear',
  },
} as const;

// ============================================================================
// Z-INDEX
// ============================================================================

export const zIndex = {
  hide: -1,
  auto: 'auto',
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  toast: 1600,
  tooltip: 1700,
} as const;

// ============================================================================
// BREAKPOINTS
// ============================================================================

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ============================================================================
// COMPONENT SIZE TOKENS
// ============================================================================

export const componentSizes = {
  button: {
    sm: { height: '32px', padding: '0 12px', fontSize: '14px' },
    md: { height: '40px', padding: '0 16px', fontSize: '14px' },
    lg: { height: '48px', padding: '0 24px', fontSize: '16px' },
  },
  input: {
    sm: { height: '32px', padding: '0 12px', fontSize: '14px' },
    md: { height: '40px', padding: '0 12px', fontSize: '14px' },
    lg: { height: '48px', padding: '0 16px', fontSize: '16px' },
  },
  badge: {
    sm: { height: '20px', padding: '0 6px', fontSize: '11px' },
    md: { height: '24px', padding: '0 8px', fontSize: '12px' },
    lg: { height: '28px', padding: '0 10px', fontSize: '14px' },
  },
} as const;

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  colors,
  tierColors,
  spacing,
  spacingTokens,
  fontFamily,
  fontSize,
  fontWeight,
  typography,
  borderRadius,
  borderWidth,
  shadows,
  transitions,
  zIndex,
  breakpoints,
  componentSizes,
};
