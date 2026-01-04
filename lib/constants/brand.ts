/**
 * Ivylevel Brand Constants
 *
 * UNIVERSAL STYLING SYSTEM
 *
 * These constants ensure consistent branding across ALL frames and components.
 * Use these instead of Tailwind CSS variables (which are designed for dark mode).
 *
 * RULE: Never use Tailwind color classes like `text-text-primary`, `bg-background-secondary`,
 *       `text-primary-blue` in Frame components. Always use inline styles with these constants.
 */

export const BRAND_COLORS = {
  // Primary Brand Colors (from original Figma design)
  primary: '#FF4A23',           // Ivylevel orange - main accent, CTAs, highlights
  primaryLight: '#FF7224',      // Accent orange for secondary highlights
  primaryDark: '#e6391a',       // Darker orange for active states
  primaryBg: 'rgba(255, 74, 35, 0.1)',    // Light orange background
  primaryBgHover: 'rgba(255, 74, 35, 0.15)', // Hover background

  // Accent (alias for consistency with v10 components)
  accent: '#FF4A23',
  accentLight: '#FF7224',
  accentBg: '#FFF7ED',

  // Secondary Brand Colors
  secondary: '#641432',         // Ivylevel maroon - headings, important text
  secondaryLight: '#8a1d45',    // Lighter maroon
  secondaryDark: '#4a0f24',     // Darker maroon
  secondaryBg: 'rgba(100, 20, 50, 0.1)',  // Light maroon background

  // Text Colors (from original Figma design)
  textHeading: '#020202',       // Near black for headings (or secondary for brand emphasis)
  textPrimary: '#020202',       // Near black - main content text
  textSecondary: '#616479',     // Gray - secondary content, subtitles
  textMuted: '#9698A6',         // Light gray - hints, placeholders
  textDisabled: '#d1d5db',      // Gray-300 for disabled

  // Background Colors (from original Figma design - warm grays)
  bgPage: '#F7F8FA',            // Cool light gray - page background
  bgPrimary: '#FFFFFF',         // Clean white - main card backgrounds
  bgSecondary: '#F5F4F3',       // Warm gray - secondary backgrounds
  bgCard: '#F5F4F3',            // Warm gray - card backgrounds
  bgPill: '#F5F4F3',            // Warm gray - pills, badges, tabs
  bgHover: '#F5F4F3',           // Warm gray - hover states
  bgSelected: 'rgba(255, 74, 35, 0.1)',    // Light orange for selected
  bgSuccess: 'rgba(29, 191, 115, 0.1)',    // Light green (updated)
  bgWarning: 'rgba(234, 183, 5, 0.1)',     // Light yellow (updated)
  bgError: 'rgba(220, 38, 38, 0.1)',       // Light red

  // v10 aliases (for component compatibility)
  successBg: '#D1FAE5',
  warningBg: '#FEF3C7',
  errorBg: '#FEE2E2',
  infoBg: '#DBEAFE',

  // Category colors (for score displays)
  aptitude: '#2563EB',
  passion: '#F97316',
  service: '#059669',
  identity: '#7C3AED',

  // Icon Colors (from original Figma design)
  iconPrimary: '#292D32',       // Dark charcoal - standard icon color
  iconMuted: '#9698A6',         // Light gray - muted icons
  iconActive: '#FF4A23',        // Orange - active/highlighted icons

  // Border Colors
  borderLight: '#E6EAEE',       // Light border (from original)
  borderDefault: '#DFE0E4',     // Default border (from original)
  borderSelected: '#FF4A23',    // Orange for selected state
  borderHover: '#FF7224',       // Accent orange on hover

  // Semantic Colors (from original Figma design)
  success: '#1DBF73',           // Original design green
  successLight: '#22c55e',      // Lighter green
  warning: '#EAB705',           // Original design yellow
  warningLight: '#fbbf24',      // Lighter yellow
  error: '#dc2626',             // Red-600
  errorLight: '#ef4444',        // Red-500
  info: '#3b82f6',              // Blue-500

  // Shadow Colors
  shadowPrimary: '0 4px 12px rgba(254, 74, 34, 0.3)',
  shadowPrimaryHover: '0 6px 20px rgba(254, 74, 34, 0.4)',
  shadowCard: '0 8px 32px rgba(100, 20, 50, 0.1)',
  shadowCardHover: '0 12px 40px rgba(100, 20, 50, 0.15)',
  shadowSuccess: '0 4px 12px rgba(29, 191, 115, 0.3)',
} as const;

/**
 * Common style objects for reuse
 */
export const BRAND_STYLES = {
  // Icon container (small)
  iconContainerSm: {
    width: '40px',
    height: '40px',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: BRAND_COLORS.primaryBg,
  },

  // Icon container (large)
  iconContainerLg: {
    width: '80px',
    height: '80px',
    borderRadius: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: BRAND_COLORS.primaryBg,
  },

  // Heading text
  heading: {
    color: BRAND_COLORS.textHeading,
    fontWeight: 600,
  },

  // Body text
  body: {
    color: BRAND_COLORS.textPrimary,
  },

  // Muted text
  muted: {
    color: BRAND_COLORS.textMuted,
  },

  // Selection button (unselected)
  buttonUnselected: {
    backgroundColor: BRAND_COLORS.bgPrimary,
    border: `1px solid ${BRAND_COLORS.borderLight}`,
    color: BRAND_COLORS.textSecondary,
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  },

  // Selection button (selected)
  buttonSelected: {
    backgroundColor: BRAND_COLORS.primary,
    border: `2px solid ${BRAND_COLORS.primary}`,
    color: 'white',
    transform: 'translateY(-2px)',
    boxShadow: BRAND_COLORS.shadowPrimary,
  },

  // Card selected state
  cardSelected: {
    backgroundColor: BRAND_COLORS.bgSelected,
    border: `2px solid ${BRAND_COLORS.borderSelected}`,
    transform: 'translateY(-2px)',
    boxShadow: BRAND_COLORS.shadowPrimary,
  },

  // Success indicator
  successIndicator: {
    backgroundColor: BRAND_COLORS.bgSuccess,
    border: `1px solid rgba(29, 191, 115, 0.2)`,
    color: BRAND_COLORS.success,
  },

  // Warning indicator
  warningIndicator: {
    backgroundColor: BRAND_COLORS.bgWarning,
    border: `1px solid rgba(234, 183, 5, 0.2)`,
    color: BRAND_COLORS.warning,
  },

  // Error indicator
  errorIndicator: {
    backgroundColor: BRAND_COLORS.bgError,
    border: `1px solid rgba(220, 38, 38, 0.2)`,
    color: BRAND_COLORS.error,
  },
} as const;

/**
 * Get feedback color based on value
 */
export function getFeedbackColor(
  type: 'excellent' | 'good' | 'average' | 'poor'
): string {
  switch (type) {
    case 'excellent':
      return BRAND_COLORS.success;
    case 'good':
      return BRAND_COLORS.primary;
    case 'average':
      return BRAND_COLORS.warning;
    case 'poor':
      return BRAND_COLORS.error;
    default:
      return BRAND_COLORS.textSecondary;
  }
}

/**
 * Category configuration for score displays
 */
export const CATEGORY_CONFIG = {
  aptitude: { label: 'Aptitude', color: BRAND_COLORS.aptitude, icon: 'Brain' },
  passion: { label: 'Passion', color: BRAND_COLORS.passion, icon: 'Heart' },
  service: { label: 'Service', color: BRAND_COLORS.service, icon: 'Users' },
  identity: { label: 'Identity', color: BRAND_COLORS.identity, icon: 'Fingerprint' },
} as const;

/**
 * Brand gradients
 */
export const BRAND_GRADIENTS = {
  primary: 'linear-gradient(135deg, #641432 0%, #8B1E4A 100%)',
  accent: 'linear-gradient(135deg, #FF4A23 0%, #FF6B47 100%)',
  warm: 'linear-gradient(135deg, #FFF5F2 0%, #FFFFFF 100%)',
  cri: 'linear-gradient(135deg, #FEF3C7 0%, #FFF7ED 50%, #FFFFFF 100%)',
} as const;
