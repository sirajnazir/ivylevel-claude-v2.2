/**
 * Icon Constants - v11.0
 *
 * Centralized icon mappings using lucide-react for consistent styling.
 * Replaces all emoji icons with SVG icons for visual consistency.
 *
 * @version 11.0
 */

import {
  BookOpen,
  FlaskConical,
  MessageCircle,
  Target,
  Users,
  Palette,
  Calculator,
  Clock,
  Search,
  Pencil,
  HelpCircle,
  GraduationCap,
  Rocket,
  Lightbulb,
  Medal,
  Heart,
  Briefcase,
  HandHeart,
  Award,
  Calendar,
  TrendingUp,
  Sparkles,
  Trophy,
  Brain,
  Fingerprint,
  Flame,
  Settings,
  FileText,
  Star,
  Zap,
  Sprout,
  Leaf,
  TreeDeciduous,
  Mountain,
  Sunrise,
  Moon,
  Scale,
  ClipboardList,
  Activity,
  Compass,
  Crown,
  HeartHandshake,
  Globe,
  Theater,
  RefreshCw,
  Battery,
  Gem,
  Edit3,
  Mic,
  Wrench,
  BarChart3,
  Puzzle,
  type LucideIcon,
} from 'lucide-react';

// ============================================================================
// STRENGTH ICONS - Used in Frame4Context for strength selection
// ============================================================================

export const STRENGTH_ICONS: Record<string, LucideIcon> = {
  memorization: BookOpen,      // Was: 📚
  'hands-on': FlaskConical,    // Was: 🧪
  explaining: MessageCircle,   // Was: 💬
  competitive: Target,         // Was: 🎯
  social: Users,               // Was: 🤝
  creative: Palette,           // Was: 🎨
  analytical: Calculator,      // Was: 📊
  disciplined: Clock,          // Was: ⏰
  curious: Search,             // Was: 🔬
  writing: Pencil,             // Was: 📝
  'not-sure': HelpCircle,      // Was: ❓
};

// ============================================================================
// CATEGORY ICONS - Used in scoring breakdown and game plan
// ============================================================================

export const CATEGORY_ICONS: Record<string, LucideIcon> = {
  aptitude: Brain,             // Was: 📚
  passion: Flame,              // Was: 🔥
  community: HandHeart,        // Was: 🤝
  service: HandHeart,          // Alias for community
  operating: Settings,         // Was: ⚙️
  identity: Fingerprint,       // New for v10
};

// ============================================================================
// ACTION ICONS - Used in game plan actions
// ============================================================================

export const ACTION_ICONS: Record<string, LucideIcon> = {
  academics: BookOpen,         // Was: 📚
  testing: FileText,           // Was: 📝
  graduation: GraduationCap,   // Was: 🎓
  activities: Target,          // Was: 🎯
  growth: Rocket,              // Was: 🚀
  idea: Lightbulb,             // Was: 💡
  leadership: Medal,           // Crown-like
  service: Heart,              // Was: 🤝 (service context)
  awards: Award,               // Was: 🏆
  research: TrendingUp,        // Was: 🔬
  summer: Calendar,            // Was: 📅
  narrative: Sparkles,         // Story/personal brand
  trophy: Trophy,              // Achievements
};

// ============================================================================
// PRIORITY ICONS - Used for action priority badges
// ============================================================================

export const PRIORITY_ICONS: Record<string, LucideIcon> = {
  critical: Zap,
  high: Star,
  medium: Target,
  low: Clock,
};

// ============================================================================
// PRIORITY CONFIG - Full configuration for priority badges
// ============================================================================

export const PRIORITY_CONFIG: Record<string, { icon: LucideIcon; label: string; color: string; bgColor: string }> = {
  critical: { icon: Zap, label: 'Critical', color: '#DC2626', bgColor: '#FEE2E2' },
  high: { icon: Star, label: 'High', color: '#D97706', bgColor: '#FEF3C7' },
  medium: { icon: Target, label: 'Medium', color: '#2563EB', bgColor: '#DBEAFE' },
  low: { icon: Clock, label: 'Low', color: '#6B7280', bgColor: '#F3F4F6' },
};

// ============================================================================
// STRENGTH OPTIONS - Array-style config for StrengthSelector
// ============================================================================

export interface StrengthOption {
  id: string;
  label: string;
  icon: LucideIcon;
  color: string;
}

export const STRENGTH_OPTIONS: StrengthOption[] = [
  { id: 'memorization', label: 'Memorization', icon: BookOpen, color: '#3B82F6' },
  { id: 'hands-on', label: 'Hands-on Learning', icon: FlaskConical, color: '#8B5CF6' },
  { id: 'explaining', label: 'Explaining', icon: MessageCircle, color: '#10B981' },
  { id: 'competitive', label: 'Competition', icon: Target, color: '#EF4444' },
  { id: 'social', label: 'Collaboration', icon: Users, color: '#F59E0B' },
  { id: 'creative', label: 'Creative', icon: Palette, color: '#EC4899' },
  { id: 'analytical', label: 'Analytical', icon: Calculator, color: '#0EA5E9' },
  { id: 'disciplined', label: 'Disciplined', icon: Clock, color: '#6366F1' },
  { id: 'curious', label: 'Curious', icon: Search, color: '#14B8A6' },
  { id: 'writing', label: 'Writing', icon: Pencil, color: '#84CC16' },
];

// ============================================================================
// ACTION CATEGORY CONFIG - Full config with colors for ActionCard
// ============================================================================

export const ACTION_CATEGORY_CONFIG: Record<string, { icon: LucideIcon; color: string; bgColor: string }> = {
  academics: { icon: BookOpen, color: '#3B82F6', bgColor: '#DBEAFE' },
  testing: { icon: FileText, color: '#8B5CF6', bgColor: '#EDE9FE' },
  graduation: { icon: GraduationCap, color: '#641432', bgColor: '#FFF5F2' },
  activities: { icon: Target, color: '#EF4444', bgColor: '#FEE2E2' },
  growth: { icon: Rocket, color: '#F59E0B', bgColor: '#FEF3C7' },
  idea: { icon: Lightbulb, color: '#FBBF24', bgColor: '#FFFBEB' },
  leadership: { icon: Medal, color: '#D97706', bgColor: '#FEF3C7' },
  service: { icon: Heart, color: '#EC4899', bgColor: '#FCE7F3' },
  awards: { icon: Award, color: '#10B981', bgColor: '#D1FAE5' },
  research: { icon: TrendingUp, color: '#0EA5E9', bgColor: '#E0F2FE' },
  summer: { icon: Calendar, color: '#14B8A6', bgColor: '#CCFBF1' },
  narrative: { icon: Sparkles, color: '#7C3AED', bgColor: '#EDE9FE' },
  trophy: { icon: Trophy, color: '#F59E0B', bgColor: '#FEF3C7' },
  default: { icon: Target, color: '#6B7280', bgColor: '#F3F4F6' },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get the appropriate icon for a strength ID
 */
export function getStrengthIcon(strengthId: string): LucideIcon {
  return STRENGTH_ICONS[strengthId] || HelpCircle;
}

/**
 * Get the appropriate icon for a category ID
 */
export function getCategoryIcon(categoryId: string): LucideIcon {
  return CATEGORY_ICONS[categoryId.toLowerCase()] || Brain;
}

/**
 * Get the appropriate icon for an action category
 */
export function getActionIcon(category: string): LucideIcon {
  return ACTION_ICONS[category.toLowerCase()] || Target;
}

/**
 * Get the full config (icon + colors) for an action category
 */
export function getActionCategoryIcon(category: string): { icon: LucideIcon; color: string; bgColor: string } {
  return ACTION_CATEGORY_CONFIG[category.toLowerCase()] || ACTION_CATEGORY_CONFIG.default;
}

// ============================================================================
// ICON STYLE CONSTANTS
// ============================================================================

export const ICON_SIZES = {
  xs: 12,
  sm: 14,
  md: 18,
  lg: 24,
  xl: 32,
} as const;

export const ICON_COLORS = {
  primary: '#FF4A23',    // Ivylevel orange
  secondary: '#641432',  // Ivylevel maroon
  aptitude: '#3B82F6',   // Blue
  passion: '#F59E0B',    // Amber
  service: '#10B981',    // Green
  identity: '#8B5CF6',   // Purple
  operating: '#8B5CF6',  // Purple
  community: '#10B981',  // Green
  muted: '#9ca3af',      // Gray
  success: '#16a34a',    // Green
  warning: '#d97706',    // Amber
  error: '#dc2626',      // Red
} as const;

// ============================================================================
// BOOSTER CATEGORY ICONS - Used in Frame5 power-ups
// ============================================================================

export const BOOSTER_CATEGORY_ICONS: Record<string, LucideIcon> = {
  academic: BookOpen,      // Was: 📚
  passion: Flame,          // Was: 🔥
  community: HandHeart,    // Was: 🤝
  operating: Zap,          // Was: ⚡
};

// ============================================================================
// DIFFICULTY ICONS - Used in booster difficulty levels
// ============================================================================

export const DIFFICULTY_ICONS: Record<string, LucideIcon> = {
  easy: Sprout,            // Was: 🌱
  medium: Leaf,            // Was: 🌿
  hard: TreeDeciduous,     // Was: 🌳
  expert: Mountain,        // Was: 🏔️
};

// ============================================================================
// BOOSTER ICONS - Individual booster icons
// ============================================================================

export const BOOSTER_ICONS: Record<string, LucideIcon> = {
  // Academic
  more_ap_courses: BookOpen,        // Was: 📖
  sat_improvement: FileText,        // Was: 📝
  research_project: Search,         // Was: 🔬
  dual_enrollment: GraduationCap,   // Was: 🎓

  // Passion
  deepen_spike: Target,             // Was: 🎯
  start_initiative: Rocket,         // Was: 🚀
  seek_mentorship: Compass,         // Was: 🧭
  competition_entry: Trophy,        // Was: 🏆

  // Community
  leadership_role: Crown,           // Was: 👑
  increase_service: HeartHandshake, // Was: 💝
  expand_impact: Globe,             // Was: 🌍
  diversify_involvement: Theater,   // Was: 🎭

  // Operating
  optimize_time: Clock,             // Was: ⏰
  develop_capability: Gem,          // Was: 💎
  build_consistency: RefreshCw,     // Was: 🔄
  energy_management: Battery,       // Was: 🔋
};

// ============================================================================
// SCENARIO ICONS - Used in Frame3 scenarios
// ============================================================================

export const SCENARIO_ICONS: Record<string, LucideIcon> = {
  systematic: ClipboardList,  // Was: 📋
  adaptive: Activity,         // Was: ⚡
  social: Users,              // Was: 👥
  solo: Search,               // Was: 🔬
  cautious: Target,           // Was: 🎯
  bold: Rocket,               // Was: 🚀
};

// ============================================================================
// PRODUCTIVITY ICONS - Used in Frame3 time options
// ============================================================================

export const PRODUCTIVITY_ICONS: Record<string, LucideIcon> = {
  early_bird: Sunrise,    // Was: 🌅
  night_owl: Moon,        // Was: 🌙
  flexible: Scale,        // Was: ⚖️
};

// ============================================================================
// ENERGY SPECTRUM ICONS - Used in Frame3 energy slider
// ============================================================================

export const ENERGY_ICONS: Record<string, LucideIcon> = {
  people: Users,         // Was: 👥
  ideas: Lightbulb,      // Was: 💡
};

// ============================================================================
// HIDDEN CAPABILITY ICONS - Used in Frame3 capability selection
// ============================================================================

export const CAPABILITY_ICONS: Record<string, LucideIcon> = {
  writing: Edit3,              // Was: ✍️
  public_speaking: Mic,        // Was: 🗣️
  creative_design: Palette,    // Was: 🎨
  technical_build: Wrench,     // Was: 🔧
  networking: HandHeart,       // Was: 🤝
  data_analysis: BarChart3,    // Was: 📊
  strategic_planning: Target,  // Was: 🎯
  idea_generation: Lightbulb,  // Was: 💡
};

// ============================================================================
// INSIGHT ICONS - Used in realtime insights
// ============================================================================

export const INSIGHT_ICONS: Record<string, LucideIcon> = {
  suggestion: Lightbulb,  // Was: 💡
  achievement: Trophy,    // Was: 🏆
  target: Target,         // Was: 🎯
  analytics: BarChart3,   // Was: 📊
  note: FileText,         // Was: 📝
  graduation: GraduationCap, // Was: 🎓
  academics: BookOpen,    // Was: 📚
  research: Search,       // Was: 🔬
  experiment: FlaskConical, // Was: 🧪
  social: Users,          // Was: 🤝
  growth: Rocket,         // Was: 🚀
  strength: TrendingUp,   // Was: 💪
  narrative: Sparkles,    // Was: ✨
  passion: Flame,         // Was: 🔥
  operating: Zap,         // Was: ⚡
  warning: HelpCircle,    // Was: ⚠️
  pending: RefreshCw,     // Was: ⟳
};

// ============================================================================
// HELPER FUNCTIONS - Extended
// ============================================================================

/**
 * Get the appropriate icon for a booster category ID
 */
export function getBoosterCategoryIcon(categoryId: string): LucideIcon {
  return BOOSTER_CATEGORY_ICONS[categoryId.toLowerCase()] || Target;
}

/**
 * Get the appropriate icon for a difficulty level
 */
export function getDifficultyIcon(difficultyId: string): LucideIcon {
  return DIFFICULTY_ICONS[difficultyId.toLowerCase()] || Sprout;
}

/**
 * Get the appropriate icon for a booster
 */
export function getBoosterIcon(boosterId: string): LucideIcon {
  return BOOSTER_ICONS[boosterId] || Target;
}

/**
 * Get the appropriate icon for a capability
 */
export function getCapabilityIcon(capabilityId: string): LucideIcon {
  return CAPABILITY_ICONS[capabilityId] || Puzzle;
}

/**
 * Get the appropriate icon for an insight type
 */
export function getInsightIcon(insightType: string): LucideIcon {
  return INSIGHT_ICONS[insightType.toLowerCase()] || Lightbulb;
}

export default {
  STRENGTH_ICONS,
  STRENGTH_OPTIONS,
  CATEGORY_ICONS,
  ACTION_ICONS,
  ACTION_CATEGORY_CONFIG,
  PRIORITY_ICONS,
  PRIORITY_CONFIG,
  BOOSTER_CATEGORY_ICONS,
  DIFFICULTY_ICONS,
  BOOSTER_ICONS,
  SCENARIO_ICONS,
  PRODUCTIVITY_ICONS,
  ENERGY_ICONS,
  CAPABILITY_ICONS,
  INSIGHT_ICONS,
  ICON_SIZES,
  ICON_COLORS,
  getStrengthIcon,
  getCategoryIcon,
  getActionIcon,
  getActionCategoryIcon,
  getBoosterCategoryIcon,
  getDifficultyIcon,
  getBoosterIcon,
  getCapabilityIcon,
  getInsightIcon,
};
