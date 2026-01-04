/**
 * IvyQuest Design System - v12.0
 * Matching Original Frontend Specification
 */

// Brand Colors
export const COLORS = {
  // Primary (Orange)
  primary: '#FF5733',
  primaryLight: 'rgba(255, 87, 51, 0.1)',
  primaryFade: '#FFC300',

  // Secondary (Purple Gradient)
  secondary: '#667eea',
  secondaryAccent: '#764ba2',

  // Text
  textHeading: '#333',
  textPrimary: '#333',
  textSecondary: '#666',
  textMuted: '#999',

  // Background
  bgPage: '#FAFAFA',
  bgCard: '#FFFFFF',
  bgSubtle: '#F5F5F5',

  // State Colors
  success: '#28a745',
  warning: '#ffc107',
  error: '#dc3545',
  info: '#17a2b8',

  // Border Colors
  borderDefault: '#e9ecef',
  borderSubtle: '#e5e7eb',
  borderHeader: '#EAEAEA',
};

// Gradients
export const GRADIENTS = {
  purple: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  orange: 'linear-gradient(90deg, #FF5733, #FFC300)',
  aptitude: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
  passion: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
  service: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
  identity: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
};

// Pillar Configuration
export const PILLAR_CONFIG = {
  aptitude: {
    label: 'Aptitude',
    color: '#3B82F6',
    gradient: GRADIENTS.aptitude,
    description: 'Academic performance & intellectual capability',
  },
  passion: {
    label: 'Passion',
    color: '#F59E0B',
    gradient: GRADIENTS.passion,
    description: 'Extracurricular depth & genuine engagement',
  },
  service: {
    label: 'Service',
    color: '#10B981',
    gradient: GRADIENTS.service,
    description: 'Community impact & leadership initiative',
  },
  identity: {
    label: 'Identity',
    color: '#8B5CF6',
    gradient: GRADIENTS.identity,
    description: 'Personal narrative & authentic story',
  },
};

// Typography
export const TYPOGRAPHY = {
  h1: { size: '32px', weight: 600 },
  h2: { size: '24px', weight: 600 },
  h3: { size: '20px', weight: 600 },
  body: { size: '14px', weight: 400 },
  small: { size: '12px', weight: 400 },
  tiny: { size: '11px', weight: 500 },
};

// Spacing
export const SPACING = {
  header: { padding: '0 32px', height: '64px' },
  main: { maxWidth: '1400px', padding: '40px' },
  card: { padding: '24px' },
  grid: { gap: '24px' },
};

// Border Radius
export const RADIUS = {
  sm: '8px',
  md: '12px',
  lg: '16px',
  pill: '24px',
  circle: '50%',
};

// Shadows
export const SHADOWS = {
  card: '0 2px 8px rgba(0, 0, 0, 0.08)',
  hover: '0 8px 24px rgba(0, 0, 0, 0.12)',
  modal: '0 8px 32px rgba(0, 0, 0, 0.15)',
};

// Transitions
export const TRANSITIONS = {
  fast: '0.2s ease',
  standard: '0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  slow: '0.4s cubic-bezier(0.4, 0, 0.2, 1)',
};

// Tab Configuration
export const TABS = [
  { id: 'assessment', label: 'Assessment', enabled: true },
  { id: 'gameplan', label: 'Game Plan', enabled: true },
  { id: 'preparation', label: 'Preparation', enabled: true },
  { id: 'growth', label: 'Growth', enabled: true },
  { id: 'sessions', label: 'Sessions', enabled: false },
  { id: 'multiagents', label: 'Multi-Agents', enabled: true },
] as const;

export type TabId = typeof TABS[number]['id'];

// Status Badge Colors
export const STATUS_COLORS = {
  completed: { bg: '#d1fae5', text: '#059669' },
  in_progress: { bg: '#fef3c7', text: '#d97706' },
  pending: { bg: '#f3f4f6', text: '#6b7280' },
  critical: { bg: '#fee2e2', text: '#dc2626' },
};

// Tier Configuration
export const TIER_CONFIG = {
  BRONZE: { color: '#CD7F32', label: 'Bronze', min: 0 },
  SILVER: { color: '#C0C0C0', label: 'Silver', min: 60 },
  GOLD: { color: '#FFD700', label: 'Gold', min: 75 },
  PLATINUM: { color: '#E5E4E2', label: 'Platinum', min: 85 },
  DIAMOND: { color: '#B9F2FF', label: 'Diamond', min: 95 },
};

export type Tier = keyof typeof TIER_CONFIG;

export function getTierFromScore(score: number): Tier {
  if (score >= 95) return 'DIAMOND';
  if (score >= 85) return 'PLATINUM';
  if (score >= 75) return 'GOLD';
  if (score >= 60) return 'SILVER';
  return 'BRONZE';
}
