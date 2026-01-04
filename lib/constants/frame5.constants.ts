/**
 * IvyQuest v3.0 — Frame 5: Power-Ups Constants
 *
 * Booster definitions, categories, and configuration.
 *
 * @version 1.0.0
 * @module constants/frame5.constants
 */

// ============================================================================
// BOOSTER CATEGORIES
// ============================================================================

export const BOOSTER_CATEGORY_IDS = ['academic', 'passion', 'community', 'operating'] as const;
export type BoosterCategoryId = typeof BOOSTER_CATEGORY_IDS[number];

// Icons are now string identifiers - use getBoosterCategoryIcon() from lib/constants/icons.ts
export const BOOSTER_CATEGORIES: Record<BoosterCategoryId, {
  id: BoosterCategoryId;
  label: string;
  icon: string;
  color: string;
  description: string;
}> = {
  academic: {
    id: 'academic',
    label: 'Academic',
    icon: 'academic',
    color: '#3B82F6',
    description: 'Strengthen your academic profile',
  },
  passion: {
    id: 'passion',
    label: 'Passion',
    icon: 'passion',
    color: '#F59E0B',
    description: 'Deepen your spike and activities',
  },
  community: {
    id: 'community',
    label: 'Community',
    icon: 'community',
    color: '#10B981',
    description: 'Expand leadership and impact',
  },
  operating: {
    id: 'operating',
    label: 'Operating',
    icon: 'operating',
    color: '#8B5CF6',
    description: 'Optimize your time and energy',
  },
};

// ============================================================================
// DIFFICULTY LEVELS
// ============================================================================

export const DIFFICULTY_IDS = ['easy', 'medium', 'hard', 'expert'] as const;
export type DifficultyId = typeof DIFFICULTY_IDS[number];

// Icons are now string identifiers - use getDifficultyIcon() from lib/constants/icons.ts
export const DIFFICULTY_LEVELS: Record<DifficultyId, {
  id: DifficultyId;
  label: string;
  icon: string;
  color: string;
  multiplier: number; // Affects impact calculation
}> = {
  easy: {
    id: 'easy',
    label: 'Easy',
    icon: 'easy',
    color: '#10B981',
    multiplier: 0.8,
  },
  medium: {
    id: 'medium',
    label: 'Medium',
    icon: 'medium',
    color: '#F59E0B',
    multiplier: 1.0,
  },
  hard: {
    id: 'hard',
    label: 'Hard',
    icon: 'hard',
    color: '#EF4444',
    multiplier: 1.2,
  },
  expert: {
    id: 'expert',
    label: 'Expert',
    icon: 'expert',
    color: '#7C3AED',
    multiplier: 1.5,
  },
};

// ============================================================================
// TIME ESTIMATES
// ============================================================================

export const TIME_ESTIMATE_IDS = ['1_week', '1_month', '3_months', '6_months', '1_year', 'ongoing'] as const;
export type TimeEstimateId = typeof TIME_ESTIMATE_IDS[number];

export const TIME_ESTIMATES: Record<TimeEstimateId, {
  id: TimeEstimateId;
  label: string;
  weeks: number;
}> = {
  '1_week': { id: '1_week', label: '1 week', weeks: 1 },
  '1_month': { id: '1_month', label: '1 month', weeks: 4 },
  '3_months': { id: '3_months', label: '3 months', weeks: 12 },
  '6_months': { id: '6_months', label: '6 months', weeks: 26 },
  '1_year': { id: '1_year', label: '1 year', weeks: 52 },
  'ongoing': { id: 'ongoing', label: 'Ongoing', weeks: 100 },
};

// ============================================================================
// BOOSTER DEFINITIONS
// ============================================================================

export interface BoosterDefinition {
  id: string;
  category: BoosterCategoryId;
  title: string;
  description: string;
  fullDescription: string;
  icon: string;
  difficulty: DifficultyId;
  timeEstimate: TimeEstimateId;
  baseImpact: number; // Base score improvement (0-15)
  targetLayer: 'aptitude' | 'passion' | 'community' | 'operating';
  prerequisites?: string[];
  triggers: {
    minScore?: number;
    maxScore?: number;
    gradeLevel?: string[];
    capabilities?: string[];
    missingElements?: string[];
  };
  actionSteps: string[];
}

export const BOOSTERS: BoosterDefinition[] = [
  // ============================================================================
  // ACADEMIC BOOSTERS
  // ============================================================================
  {
    id: 'more_ap_courses',
    category: 'academic',
    title: 'Take More AP Courses',
    description: 'Add 2-3 AP courses to demonstrate academic rigor',
    fullDescription: 'Colleges value course rigor highly. Adding AP courses in your areas of interest shows intellectual curiosity and preparedness for college-level work.',
    icon: 'more_ap_courses',
    difficulty: 'medium',
    timeEstimate: '6_months',
    baseImpact: 8,
    targetLayer: 'aptitude',
    triggers: {
      maxScore: 85,
      gradeLevel: ['9', '10', '11'],
      missingElements: ['ap_depth'],
    },
    actionSteps: [
      'Review available AP courses at your school',
      'Select courses aligned with your intended major',
      'Register for next semester',
      'Begin preparation over summer if needed',
    ],
  },
  {
    id: 'sat_improvement',
    category: 'academic',
    title: 'Boost SAT/ACT Score',
    description: 'Target a 100+ point SAT improvement',
    fullDescription: 'A higher test score can significantly improve your admissions chances. Focused preparation over 2-3 months can yield meaningful gains.',
    icon: 'sat_improvement',
    difficulty: 'medium',
    timeEstimate: '3_months',
    baseImpact: 10,
    targetLayer: 'aptitude',
    triggers: {
      maxScore: 80,
    },
    actionSteps: [
      'Take a diagnostic test to identify weak areas',
      'Create a study schedule (2-3 hours daily)',
      'Use official practice tests',
      'Consider tutoring for problem areas',
      'Schedule retake date',
    ],
  },
  {
    id: 'research_project',
    category: 'academic',
    title: 'Start a Research Project',
    description: 'Pursue independent research in your field of interest',
    fullDescription: 'Original research demonstrates intellectual initiative and depth. This is especially valuable for STEM and social science applicants.',
    icon: 'research_project',
    difficulty: 'hard',
    timeEstimate: '6_months',
    baseImpact: 12,
    targetLayer: 'aptitude',
    triggers: {
      gradeLevel: ['10', '11'],
      capabilities: ['analytical_thinking', 'methodical_builder'],
    },
    actionSteps: [
      'Identify a research question in your interest area',
      'Find a faculty mentor at local university',
      'Develop a research proposal',
      'Conduct research and document findings',
      'Submit to competitions or journals',
    ],
  },
  {
    id: 'dual_enrollment',
    category: 'academic',
    title: 'Enroll in College Courses',
    description: 'Take college-level courses for dual credit',
    fullDescription: 'Dual enrollment shows you can handle college work. It also provides exposure to a college environment and strengthens your transcript.',
    icon: 'dual_enrollment',
    difficulty: 'medium',
    timeEstimate: '6_months',
    baseImpact: 7,
    targetLayer: 'aptitude',
    triggers: {
      gradeLevel: ['10', '11', '12'],
    },
    actionSteps: [
      'Research local community college partnerships',
      'Meet with school counselor about options',
      'Apply to dual enrollment program',
      'Select courses aligned with interests',
    ],
  },

  // ============================================================================
  // PASSION BOOSTERS
  // ============================================================================
  {
    id: 'deepen_spike',
    category: 'passion',
    title: 'Deepen Your Spike',
    description: 'Take your primary activity to the next level',
    fullDescription: 'Moving from local to state or national recognition in your spike area dramatically improves your profile. Focus on depth over breadth.',
    icon: 'deepen_spike',
    difficulty: 'hard',
    timeEstimate: '6_months',
    baseImpact: 12,
    targetLayer: 'passion',
    triggers: {
      maxScore: 80,
      missingElements: ['national_recognition'],
    },
    actionSteps: [
      'Identify competitions at the next level',
      'Find mentors who have succeeded at this level',
      'Increase practice/dedication hours',
      'Document achievements and progression',
    ],
  },
  {
    id: 'start_initiative',
    category: 'passion',
    title: 'Start Your Own Initiative',
    description: 'Launch a project, club, or organization',
    fullDescription: 'Founding something demonstrates initiative, leadership, and the ability to create impact. This could be a nonprofit, app, club, or community project.',
    icon: 'start_initiative',
    difficulty: 'hard',
    timeEstimate: '3_months',
    baseImpact: 15,
    targetLayer: 'passion',
    triggers: {
      capabilities: ['creative_innovator', 'dynamic_leader'],
    },
    actionSteps: [
      'Identify a problem you want to solve',
      'Research if similar initiatives exist',
      'Create a plan and timeline',
      'Recruit a team or collaborators',
      'Launch and document impact',
    ],
  },
  {
    id: 'seek_mentorship',
    category: 'passion',
    title: 'Find a Mentor',
    description: 'Connect with an expert in your field',
    fullDescription: 'A mentor can accelerate your growth, provide guidance, and potentially write a strong recommendation letter.',
    icon: 'seek_mentorship',
    difficulty: 'medium',
    timeEstimate: '1_month',
    baseImpact: 6,
    targetLayer: 'passion',
    triggers: {},
    actionSteps: [
      'Identify potential mentors in your area',
      'Reach out with a specific ask',
      'Prepare for initial meeting',
      'Establish regular check-ins',
    ],
  },
  {
    id: 'competition_entry',
    category: 'passion',
    title: 'Enter Prestigious Competitions',
    description: 'Apply to national/international competitions',
    fullDescription: 'Awards from recognized competitions provide external validation of your abilities and can significantly boost your application.',
    icon: 'competition_entry',
    difficulty: 'hard',
    timeEstimate: '3_months',
    baseImpact: 10,
    targetLayer: 'passion',
    triggers: {
      missingElements: ['awards'],
    },
    actionSteps: [
      'Research competitions in your interest area',
      'Note deadlines and requirements',
      'Prepare submission materials',
      'Get feedback before submitting',
    ],
  },

  // ============================================================================
  // COMMUNITY BOOSTERS
  // ============================================================================
  {
    id: 'leadership_role',
    category: 'community',
    title: 'Pursue Leadership Position',
    description: 'Run for or earn a leadership role in existing organization',
    fullDescription: 'Leadership positions demonstrate your ability to influence, organize, and inspire others. Focus on roles where you can create measurable impact.',
    icon: 'leadership_role',
    difficulty: 'medium',
    timeEstimate: '3_months',
    baseImpact: 8,
    targetLayer: 'community',
    triggers: {
      maxScore: 75,
      missingElements: ['leadership'],
    },
    actionSteps: [
      'Identify organizations where you\'re active',
      'Express interest in leadership to advisors',
      'Run for elected positions if available',
      'Propose new initiatives to demonstrate capability',
    ],
  },
  {
    id: 'increase_service',
    category: 'community',
    title: 'Increase Service Hours',
    description: 'Commit to regular community service',
    fullDescription: 'Consistent service demonstrates commitment to your community. Focus on sustained involvement rather than one-time events.',
    icon: 'increase_service',
    difficulty: 'easy',
    timeEstimate: '6_months',
    baseImpact: 5,
    targetLayer: 'community',
    triggers: {
      maxScore: 70,
      missingElements: ['service_hours'],
    },
    actionSteps: [
      'Find organizations aligned with your interests',
      'Commit to regular weekly hours',
      'Track your hours and impact',
      'Seek opportunities for greater responsibility',
    ],
  },
  {
    id: 'expand_impact',
    category: 'community',
    title: 'Expand Your Impact Scope',
    description: 'Take local initiatives to state or national level',
    fullDescription: 'Scaling your impact shows ambition and capability. Consider how your local work could benefit a broader audience.',
    icon: 'expand_impact',
    difficulty: 'hard',
    timeEstimate: '6_months',
    baseImpact: 12,
    targetLayer: 'community',
    triggers: {
      capabilities: ['dynamic_leader', 'organized_collaborator'],
    },
    actionSteps: [
      'Document your local impact with metrics',
      'Identify similar needs in other communities',
      'Create a scaling plan',
      'Partner with other organizations',
      'Launch in new locations',
    ],
  },
  {
    id: 'diversify_involvement',
    category: 'community',
    title: 'Diversify Your Involvement',
    description: 'Join organizations in different areas',
    fullDescription: 'Showing breadth of involvement demonstrates well-roundedness. Balance depth in your spike with exploration in other areas.',
    icon: 'diversify_involvement',
    difficulty: 'easy',
    timeEstimate: '1_month',
    baseImpact: 4,
    targetLayer: 'community',
    triggers: {
      missingElements: ['diversity'],
    },
    actionSteps: [
      'List your current involvements by type',
      'Identify gaps (arts, service, athletics, etc.)',
      'Join 1-2 new organizations',
      'Maintain consistent participation',
    ],
  },

  // ============================================================================
  // OPERATING BOOSTERS
  // ============================================================================
  {
    id: 'optimize_time',
    category: 'operating',
    title: 'Optimize Your Schedule',
    description: 'Free up 5+ hours weekly for high-impact activities',
    fullDescription: 'Time is your most valuable resource. Audit your schedule to eliminate low-value activities and focus on what matters most.',
    icon: 'optimize_time',
    difficulty: 'easy',
    timeEstimate: '1_week',
    baseImpact: 5,
    targetLayer: 'operating',
    triggers: {
      maxScore: 70,
    },
    actionSteps: [
      'Track all activities for one week',
      'Categorize by impact (high/medium/low)',
      'Eliminate or reduce low-impact activities',
      'Block time for high-priority work',
    ],
  },
  {
    id: 'develop_capability',
    category: 'operating',
    title: 'Develop Hidden Capability',
    description: 'Turn a latent strength into a visible achievement',
    fullDescription: 'You have untapped potential. Identify a hidden capability and create an opportunity to demonstrate it.',
    icon: 'develop_capability',
    difficulty: 'medium',
    timeEstimate: '3_months',
    baseImpact: 8,
    targetLayer: 'operating',
    triggers: {
      capabilities: ['visual_thinking', 'systems_thinking', 'emotional_intelligence'],
    },
    actionSteps: [
      'Review your hidden capabilities assessment',
      'Choose one capability to develop',
      'Find an activity that showcases this strength',
      'Document your growth and achievements',
    ],
  },
  {
    id: 'build_consistency',
    category: 'operating',
    title: 'Build Consistent Habits',
    description: 'Establish daily routines for sustained performance',
    fullDescription: 'Success comes from consistency. Build habits that support your goals and maintain them over time.',
    icon: 'build_consistency',
    difficulty: 'medium',
    timeEstimate: '1_month',
    baseImpact: 6,
    targetLayer: 'operating',
    triggers: {},
    actionSteps: [
      'Identify your most important daily tasks',
      'Create a morning and evening routine',
      'Use habit tracking tools',
      'Review and adjust weekly',
    ],
  },
  {
    id: 'energy_management',
    category: 'operating',
    title: 'Master Your Energy',
    description: 'Align activities with your natural energy patterns',
    fullDescription: 'Work with your biology, not against it. Schedule demanding tasks during peak energy times.',
    icon: 'energy_management',
    difficulty: 'easy',
    timeEstimate: '1_week',
    baseImpact: 4,
    targetLayer: 'operating',
    triggers: {
      capabilities: ['balanced'],
    },
    actionSteps: [
      'Track energy levels throughout the day',
      'Identify your peak performance times',
      'Schedule important work during peaks',
      'Use low-energy times for routine tasks',
    ],
  },
];

// Create lookup map
export const BOOSTERS_BY_ID: Record<string, BoosterDefinition> = {};
for (const booster of BOOSTERS) {
  BOOSTERS_BY_ID[booster.id] = booster;
}

// Group by category
export const BOOSTERS_BY_CATEGORY: Record<BoosterCategoryId, BoosterDefinition[]> = {
  academic: BOOSTERS.filter(b => b.category === 'academic'),
  passion: BOOSTERS.filter(b => b.category === 'passion'),
  community: BOOSTERS.filter(b => b.category === 'community'),
  operating: BOOSTERS.filter(b => b.category === 'operating'),
};

// ============================================================================
// PRIORITY WEIGHTS
// ============================================================================

export const PRIORITY_WEIGHTS = {
  gap: 0.40,
  improvability: 0.30,
  urgency: 0.30,
} as const;

export const URGENCY_SCORES = {
  critical: 100, // 1 year or less to app
  high: 75,      // 2 years
  moderate: 50,  // 3+ years
} as const;

// ============================================================================
// IVY COMPANION MESSAGES
// ============================================================================

export const FRAME5_IVY_MESSAGES = {
  card1: {
    intro: "Here's your current profile strength and biggest opportunities.",
    strong: "You're in a strong position! Let's fine-tune for maximum impact.",
    average: "Solid foundation. These boosters will take you to the next level.",
    developing: "Every champion starts somewhere. Let's build your path forward.",
  },
  card2: {
    intro: "Select the power-ups that fit your goals and timeline.",
    selected: "Great choices! Each one moves you closer to your dream schools.",
  },
  card3: {
    intro: "Here's how your selections could impact your profile.",
    highImpact: "These changes could make a significant difference!",
  },
  card4: {
    intro: "Your personalized action plan is ready.",
    complete: "Remember: consistent effort beats sporadic intensity.",
  },
};

// ============================================================================
// FRAME METADATA
// ============================================================================

export const FRAME5_META = {
  id: 5,
  name: 'Power-Ups',
  description: 'Personalized boosters to strengthen your profile',
  targetDuration: 120, // seconds
  cardCount: 4,
} as const;

export default {
  BOOSTER_CATEGORIES,
  BOOSTERS,
  BOOSTERS_BY_ID,
  BOOSTERS_BY_CATEGORY,
  PRIORITY_WEIGHTS,
  FRAME5_IVY_MESSAGES,
  FRAME5_META,
};
