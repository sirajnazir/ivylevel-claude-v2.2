/**
 * IvyQuest Icon Constants
 * Unified icon mapping - NO EMOJI, only Lucide React icons.
 * @version 11.0
 */

import {
  Brain,
  Wrench,
  MessageCircle,
  Target,
  Users,
  Lightbulb,
  Calculator,
  Clock,
  Search,
  PenTool,
  HelpCircle,
  BookOpen,
  TrendingUp,
  Heart,
  GraduationCap,
  Trophy,
  FlaskConical,
  Briefcase,
  Star,
  Compass,
  Zap,
  Shield,
  Sparkles,
  Award,
  FileText,
  Calendar,
  MapPin,
  Globe,
  type LucideIcon,
} from 'lucide-react';

// Brand colors inline to avoid circular deps
const COLORS = {
  aptitude: '#2563EB',
  passion: '#F97316',
  service: '#059669',
  identity: '#7C3AED',
  warning: '#D97706',
  error: '#DC2626',
  info: '#2563EB',
  textSecondary: '#6B7280',
};

export interface StrengthOption {
  id: string;
  label: string;
  icon: LucideIcon;
  color: string;
  description?: string;
}

export const STRENGTH_ICONS: StrengthOption[] = [
  { id: 'memorization', label: 'Memorization & recall', icon: Brain, color: COLORS.aptitude },
  { id: 'building', label: 'Building/hands-on work', icon: Wrench, color: COLORS.passion },
  { id: 'explaining', label: 'Explaining to others', icon: MessageCircle, color: COLORS.info },
  { id: 'competitive', label: 'Competitive drive', icon: Target, color: COLORS.error },
  { id: 'connecting', label: 'Connecting with people', icon: Users, color: COLORS.service },
  { id: 'creative', label: 'Creative problem-solving', icon: Lightbulb, color: COLORS.warning },
  { id: 'math', label: 'Math/logic/patterns', icon: Calculator, color: COLORS.aptitude },
  { id: 'discipline', label: 'Discipline & consistency', icon: Clock, color: COLORS.identity },
  { id: 'curiosity', label: 'Curiosity & questioning', icon: Search, color: COLORS.passion },
  { id: 'writing', label: 'Writing & storytelling', icon: PenTool, color: COLORS.info },
  { id: 'unsure', label: 'Not sure yet', icon: HelpCircle, color: COLORS.textSecondary },
];

export interface ActionCategoryConfig {
  id: string;
  label: string;
  icon: LucideIcon;
  color: string;
  bgColor: string;
}

export const ACTION_CATEGORY_ICONS: Record<string, ActionCategoryConfig> = {
  narrative: { id: 'narrative', label: 'Narrative', icon: BookOpen, color: '#7C3AED', bgColor: '#EDE9FE' },
  activity: { id: 'activity', label: 'Activity', icon: TrendingUp, color: '#F97316', bgColor: '#FFF7ED' },
  service: { id: 'service', label: 'Service', icon: Heart, color: '#059669', bgColor: '#D1FAE5' },
  academic: { id: 'academic', label: 'Academic', icon: GraduationCap, color: '#2563EB', bgColor: '#DBEAFE' },
  awards: { id: 'awards', label: 'Awards', icon: Trophy, color: '#D97706', bgColor: '#FEF3C7' },
  research: { id: 'research', label: 'Research', icon: FlaskConical, color: '#7C3AED', bgColor: '#EDE9FE' },
  strategy: { id: 'strategy', label: 'Strategy', icon: Compass, color: '#2563EB', bgColor: '#DBEAFE' },
};

export const getActionCategoryIcon = (category: string): ActionCategoryConfig => {
  const normalized = category.toLowerCase().replace(/\s+/g, '_');
  return ACTION_CATEGORY_ICONS[normalized] || ACTION_CATEGORY_ICONS.strategy;
};

export const PRIORITY_CONFIG = {
  critical: { label: 'Critical', color: '#DC2626', bgColor: '#FEE2E2', icon: Shield },
  high: { label: 'High', color: '#F97316', bgColor: '#FFF7ED', icon: Zap },
  medium: { label: 'Medium', color: '#2563EB', bgColor: '#DBEAFE', icon: Target },
  low: { label: 'Low', color: '#6B7280', bgColor: '#F3F4F6', icon: Clock },
} as const;

export const CATEGORY_SCORE_ICONS = {
  aptitude: { icon: Brain, color: COLORS.aptitude, label: 'Aptitude' },
  passion: { icon: Heart, color: COLORS.passion, label: 'Passion' },
  service: { icon: Users, color: COLORS.service, label: 'Service' },
  identity: { icon: Sparkles, color: COLORS.identity, label: 'Identity' },
} as const;

export const INSIGHT_ICONS = {
  positive: { icon: Sparkles, color: '#059669', bgColor: '#D1FAE5' },
  suggestion: { icon: Lightbulb, color: '#D97706', bgColor: '#FEF3C7' },
  warning: { icon: Shield, color: '#DC2626', bgColor: '#FEE2E2' },
  neutral: { icon: FileText, color: '#6B7280', bgColor: '#F3F4F6' },
} as const;
