/**
 * Game Plan Generation Engine
 *
 * Generates personalized action items based on:
 * - Profile tier (fresh-start, emerging, optimization)
 * - Profile completeness
 * - Operating data (available time, strengths, interests)
 * - Skip logic findings (missing data areas)
 *
 * @version 1.0.0
 */

import type {
  StudentProfile,
  ProfileTier,
  OperatingData,
  Grade,
} from '@/lib/types/student';
import {
  getProfileTier,
  getTierMessage,
  getSkipSummary,
  shouldSkipGPA,
  shouldSkipTestScores,
  shouldSkipAPCourses,
  shouldSkipExtracurriculars,
  shouldSkipLeadership,
  shouldSkipService,
  shouldSkipAwards,
} from '@/lib/utils/skipLogic';

// ============================================================================
// TYPES
// ============================================================================

export type ActionPriority = 'critical' | 'high' | 'medium' | 'low';
export type ActionCategory =
  | 'academics'
  | 'activities'
  | 'leadership'
  | 'service'
  | 'testing'
  | 'awards'
  | 'narrative'
  | 'research'
  | 'summer';

export interface GamePlanAction {
  id: string;
  title: string;
  description: string;
  category: ActionCategory;
  priority: ActionPriority;
  timeCommitment: string; // e.g., "2-3 hrs/week"
  deadline?: string; // e.g., "Before junior year", "Fall semester"
  prerequisite?: string; // ID of action that must be done first
  icon: string;
  impact: {
    pillar: 'aptitude' | 'passion' | 'community' | 'identity';
    points: number; // Estimated score improvement
  };
  tips: string[];
  resources?: {
    name: string;
    url?: string;
  }[];
}

export interface GamePlanPhase {
  id: string;
  title: string;
  description: string;
  timeframe: string; // e.g., "Next 3 months", "This semester"
  actions: GamePlanAction[];
}

export interface GamePlan {
  tier: ProfileTier;
  tierInfo: {
    title: string;
    description: string;
    encouragement: string;
  };
  totalEstimatedHours: number;
  weeklyCommitment: number;
  phases: GamePlanPhase[];
  quickWins: GamePlanAction[]; // Actions that can be done immediately
  longTermGoals: GamePlanAction[]; // Major milestones
  warnings: string[]; // Critical items to address
  summary: {
    strengthAreas: string[];
    improvementAreas: string[];
    focusRecommendation: string;
  };
}

// ============================================================================
// CONSTANTS
// ============================================================================

const DEFAULT_WEEKLY_HOURS = 10;

// v11: Icon identifiers map to lucide-react icons in UI layer
// This allows the engine to remain data-only while UI handles rendering
const ACTION_TEMPLATES: Record<string, Omit<GamePlanAction, 'id' | 'priority'>> = {
  // Academic Actions
  IMPROVE_GPA: {
    title: 'Improve Your GPA',
    description: 'Focus on academic improvement strategies to boost your GPA over the next semester.',
    category: 'academics',
    timeCommitment: '3-5 hrs/week',
    icon: 'academics',  // v11: icon identifier
    impact: { pillar: 'aptitude', points: 10 },
    tips: [
      'Meet with teachers during office hours weekly',
      'Form or join a study group for challenging subjects',
      'Use active recall instead of passive reading',
      'Track assignments with a planner to avoid missed deadlines',
    ],
  },
  PREP_SAT: {
    title: 'Start SAT/ACT Preparation',
    description: 'Begin structured test prep to maximize your standardized test scores.',
    category: 'testing',
    timeCommitment: '4-6 hrs/week',
    deadline: '6 months before test date',
    icon: 'testing',  // v11: icon identifier
    impact: { pillar: 'aptitude', points: 12 },
    tips: [
      'Take a diagnostic test to identify weak areas',
      'Focus 70% of time on weak areas, 30% on maintaining strengths',
      'Practice with official test materials when possible',
      'Simulate test conditions with timed practice tests',
    ],
    resources: [
      { name: 'Khan Academy SAT Prep', url: 'https://www.khanacademy.org/sat' },
      { name: 'College Board Practice Tests' },
    ],
  },
  ADD_AP_COURSES: {
    title: 'Add AP/Honors Courses',
    description: 'Increase course rigor by enrolling in AP or Honors classes aligned with your interests.',
    category: 'academics',
    timeCommitment: '5-8 hrs/week per course',
    deadline: 'Course selection period',
    icon: 'graduation',  // v11: icon identifier
    impact: { pillar: 'aptitude', points: 8 },
    tips: [
      'Start with 1-2 APs in subjects you enjoy',
      'Talk to current AP students about workload',
      'Balance AP load with extracurricular commitments',
      'Consider self-studying for APs not offered at your school',
    ],
  },

  // Activity Actions
  START_ACTIVITY: {
    title: 'Start a Meaningful Activity',
    description: 'Begin an extracurricular activity aligned with your interests and potential major.',
    category: 'activities',
    timeCommitment: '3-5 hrs/week',
    icon: 'activities',  // v11: icon identifier
    impact: { pillar: 'passion', points: 8 },
    tips: [
      'Choose something you genuinely enjoy, not just for the resume',
      'Look for activities related to your intended major/career',
      'Quality and depth matter more than quantity',
      'Commit to activities for multiple years when possible',
    ],
  },
  DEEPEN_ACTIVITY: {
    title: 'Deepen Existing Activity',
    description: 'Take your current activities to the next level through increased involvement and impact.',
    category: 'activities',
    timeCommitment: '2-4 hrs/week additional',
    icon: 'growth',  // v11: icon identifier
    impact: { pillar: 'passion', points: 10 },
    tips: [
      'Propose a new initiative or project within the activity',
      'Mentor newer members',
      'Seek opportunities to compete at higher levels',
      'Document your contributions and impact quantitatively',
    ],
  },
  START_PASSION_PROJECT: {
    title: 'Launch a Passion Project',
    description: 'Create something unique that showcases your initiative and genuine interests.',
    category: 'activities',
    timeCommitment: '4-6 hrs/week',
    icon: 'idea',  // v11: icon identifier
    impact: { pillar: 'passion', points: 15 },
    tips: [
      'Identify a problem you care about solving',
      'Start small and iterate based on feedback',
      'Document your journey and learnings',
      'Aim for measurable impact (people helped, money raised, etc.)',
    ],
  },

  // Leadership Actions
  SEEK_LEADERSHIP: {
    title: 'Pursue Leadership Roles',
    description: 'Step up to leadership positions in your current activities.',
    category: 'leadership',
    timeCommitment: '2-3 hrs/week additional',
    deadline: 'Before election/selection periods',
    icon: 'leadership',  // v11: icon identifier
    impact: { pillar: 'passion', points: 12 },
    tips: [
      'Express interest to current leaders early',
      'Take initiative on projects before the title',
      'Leadership isn\'t just about titles - show you can guide others',
      'Create a leadership opportunity if one doesn\'t exist',
    ],
  },
  DEMONSTRATE_INITIATIVE: {
    title: 'Demonstrate Initiative',
    description: 'Take charge of a project or start something new that shows leadership without a formal title.',
    category: 'leadership',
    timeCommitment: '3-4 hrs/week',
    icon: 'growth',  // v11: icon identifier (Zap/lightning)
    impact: { pillar: 'passion', points: 10 },
    tips: [
      'Identify a gap or need in your school/community',
      'Propose a solution and take ownership',
      'Recruit others to help scale your impact',
      'Document outcomes and lessons learned',
    ],
  },

  // Service Actions
  START_SERVICE: {
    title: 'Begin Community Service',
    description: 'Start volunteering in an area that aligns with your interests and values.',
    category: 'service',
    timeCommitment: '2-4 hrs/week',
    icon: 'service',  // v11: icon identifier
    impact: { pillar: 'community', points: 8 },
    tips: [
      'Choose service that connects to your interests/major',
      'Consistent weekly commitment beats sporadic large events',
      'Build relationships with the people you serve',
      'Reflect on what you\'re learning from the experience',
    ],
  },
  DEEPEN_SERVICE: {
    title: 'Deepen Service Impact',
    description: 'Transform your service from volunteer hours to meaningful, sustained impact.',
    category: 'service',
    timeCommitment: '3-5 hrs/week',
    icon: 'narrative',  // v11: icon identifier (star/sparkle)
    impact: { pillar: 'community', points: 12 },
    tips: [
      'Move from participant to organizer/leader',
      'Create a sustainable project or program',
      'Measure and document your impact quantitatively',
      'Connect service to a larger mission or cause',
    ],
  },

  // Awards & Recognition
  PURSUE_AWARDS: {
    title: 'Pursue Academic Competitions',
    description: 'Participate in competitions and contests to earn recognition in your field.',
    category: 'awards',
    timeCommitment: '3-5 hrs/week',
    icon: 'trophy',  // v11: icon identifier
    impact: { pillar: 'aptitude', points: 12 },
    tips: [
      'Start with school-level competitions to build confidence',
      'Research competitions aligned with your intended major',
      'Join or form a competition prep group',
      'Participation matters even without winning - shows initiative',
    ],
    resources: [
      { name: 'Science Olympiad' },
      { name: 'DECA' },
      { name: 'Math Olympiad' },
      { name: 'Debate tournaments' },
    ],
  },

  // Summer Actions
  SUMMER_PROGRAM: {
    title: 'Apply to Summer Programs',
    description: 'Participate in a selective summer program to deepen knowledge and demonstrate commitment.',
    category: 'summer',
    timeCommitment: '2-6 weeks',
    deadline: 'December-February for most programs',
    icon: 'summer',  // v11: icon identifier
    impact: { pillar: 'aptitude', points: 10 },
    tips: [
      'Research program selectivity and reputation',
      'Apply to a mix of reach and likely programs',
      'Free programs (MOSTEC, SAMS, etc.) are often more impressive than paid',
      'Start applications early - many have January deadlines',
    ],
  },
  SUMMER_INTERNSHIP: {
    title: 'Secure a Summer Internship',
    description: 'Get hands-on experience in your field of interest through an internship or research position.',
    category: 'summer',
    timeCommitment: '20-40 hrs/week during summer',
    deadline: 'January-March for applications',
    icon: '💼',
    impact: { pillar: 'passion', points: 12 },
    tips: [
      'Start reaching out to potential mentors/employers early',
      'Cold emailing works - reach out to local professionals',
      'Create something tangible you can show/discuss',
      'Unpaid but meaningful experience > paid but irrelevant',
    ],
  },
  SUMMER_RESEARCH: {
    title: 'Pursue Research Opportunity',
    description: 'Conduct research with a professor or in a formal program to build intellectual depth.',
    category: 'research',
    timeCommitment: '15-25 hrs/week during summer',
    deadline: 'February-March for formal programs',
    icon: 'research',
    impact: { pillar: 'aptitude', points: 15 },
    tips: [
      'Email professors at local universities with genuine interest',
      'Read their recent papers before reaching out',
      'Be specific about what interests you in their work',
      'Even high schoolers can contribute meaningfully to research',
    ],
  },

  // Narrative Actions
  BUILD_NARRATIVE: {
    title: 'Clarify Your Personal Narrative',
    description: 'Develop a cohesive story that connects your activities, interests, and goals.',
    category: 'narrative',
    timeCommitment: '1-2 hrs/week',
    icon: 'narrative',
    impact: { pillar: 'identity', points: 10 },
    tips: [
      'Identify 2-3 themes that connect your activities',
      'Think about what makes you unique',
      'Start journaling about meaningful experiences',
      'Ask trusted adults what they see as your strengths',
    ],
  },
  EXPLORE_INTERESTS: {
    title: 'Explore and Define Interests',
    description: 'Actively explore different areas to discover what genuinely excites you.',
    category: 'narrative',
    timeCommitment: '2-3 hrs/week',
    icon: 'idea',
    impact: { pillar: 'identity', points: 8 },
    tips: [
      'Try new activities without pressure to commit',
      'Read widely in areas that interest you',
      'Talk to professionals in fields you\'re curious about',
      'It\'s okay to not know exactly what you want yet',
    ],
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Calculate time until college applications
 */
function getTimeUntilApplications(grade: Grade): {
  monthsRemaining: number;
  urgencyLevel: 'relaxed' | 'moderate' | 'urgent' | 'critical';
} {
  const gradeNum = typeof grade === 'number' ? grade : parseInt(grade as string) || 12;

  // Rough estimates: applications start Aug of senior year
  const monthsPerGrade = 10; // school year months
  const monthsRemaining = Math.max(0, (12 - gradeNum) * monthsPerGrade);

  let urgencyLevel: 'relaxed' | 'moderate' | 'urgent' | 'critical';
  if (monthsRemaining > 24) urgencyLevel = 'relaxed';
  else if (monthsRemaining > 12) urgencyLevel = 'moderate';
  else if (monthsRemaining > 6) urgencyLevel = 'urgent';
  else urgencyLevel = 'critical';

  return { monthsRemaining, urgencyLevel };
}

/**
 * Determine action priority based on profile and timing
 */
function determinePriority(
  action: Omit<GamePlanAction, 'id' | 'priority'>,
  profile: StudentProfile,
  tier: ProfileTier,
  urgencyLevel: string,
): ActionPriority {
  // Critical priorities for seniors
  if (urgencyLevel === 'critical') {
    if (['academics', 'testing', 'narrative'].includes(action.category)) {
      return 'critical';
    }
    return 'high';
  }

  // Fresh-start students need foundational items first
  if (tier === 'fresh-start') {
    if (action.category === 'activities' || action.category === 'academics') {
      return 'high';
    }
    if (action.category === 'awards' || action.category === 'research') {
      return 'low';
    }
    return 'medium';
  }

  // Optimization students focus on polishing
  if (tier === 'optimization') {
    if (action.category === 'narrative' || action.category === 'research') {
      return 'high';
    }
    if (action.category === 'academics') {
      return 'medium';
    }
    return 'medium';
  }

  // Default: emerging students
  if (action.impact.points >= 12) return 'high';
  if (action.impact.points >= 8) return 'medium';
  return 'low';
}

/**
 * Create an action from a template
 */
function createAction(
  templateKey: string,
  profile: StudentProfile,
  tier: ProfileTier,
  urgencyLevel: string,
): GamePlanAction | null {
  const template = ACTION_TEMPLATES[templateKey];
  if (!template) return null;

  return {
    id: `action-${templateKey.toLowerCase()}-${Date.now()}`,
    ...template,
    priority: determinePriority(template, profile, tier, urgencyLevel),
  };
}

/**
 * Filter actions based on available time
 */
function filterByAvailableTime(
  actions: GamePlanAction[],
  availableHoursPerWeek: number,
): GamePlanAction[] {
  // Parse time commitment strings to hours
  const parseTimeCommitment = (str: string): number => {
    const match = str.match(/(\d+)(?:-(\d+))?\s*hrs?\/week/);
    if (match) {
      const min = parseInt(match[1]);
      const max = match[2] ? parseInt(match[2]) : min;
      return (min + max) / 2;
    }
    return 3; // default
  };

  // Sort by priority, then filter to fit within available time
  const sorted = [...actions].sort((a, b) => {
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });

  const result: GamePlanAction[] = [];
  let totalHours = 0;

  for (const action of sorted) {
    const hours = parseTimeCommitment(action.timeCommitment);
    if (totalHours + hours <= availableHoursPerWeek * 1.2) {
      // Allow 20% overflow
      result.push(action);
      totalHours += hours;
    }
  }

  return result;
}

// ============================================================================
// MAIN ENGINE
// ============================================================================

/**
 * Generate a personalized game plan based on student profile
 */
export function generateGamePlan(profile: StudentProfile): GamePlan {
  const tier = getProfileTier(profile);
  const tierInfo = getTierMessage(tier);
  const skipSummary = getSkipSummary(profile);
  const grade = profile.identity?.grade || 12;
  const { urgencyLevel } = getTimeUntilApplications(grade);
  const operating = profile.operating || {};
  const availableHours = operating.availableHoursPerWeek || DEFAULT_WEEKLY_HOURS;

  const allActions: GamePlanAction[] = [];
  const warnings: string[] = [];

  // ============================================================================
  // ANALYZE GAPS AND GENERATE ACTIONS
  // ============================================================================

  // Check academic gaps
  const gpaSkip = shouldSkipGPA(profile);
  const testSkip = shouldSkipTestScores(profile);
  const apSkip = shouldSkipAPCourses(profile, grade);

  if (gpaSkip.show) {
    // No GPA - focus on establishing baseline
    const action = createAction('IMPROVE_GPA', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
    if (urgencyLevel === 'urgent' || urgencyLevel === 'critical') {
      warnings.push('GPA is a critical factor - focus on academic improvement immediately.');
    }
  }

  if (testSkip.show) {
    const action = createAction('PREP_SAT', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
    if (urgencyLevel === 'critical') {
      warnings.push('Standardized tests needed urgently for applications.');
    }
  }

  if (apSkip.show && typeof grade === 'number' && grade >= 10) {
    const action = createAction('ADD_AP_COURSES', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
  }

  // Check activity gaps
  const ecSkip = shouldSkipExtracurriculars(profile);
  const leadershipSkip = shouldSkipLeadership(profile);
  const serviceSkip = shouldSkipService(profile);
  const awardsSkip = shouldSkipAwards(profile);

  if (ecSkip.show) {
    const action = createAction('START_ACTIVITY', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
    if (tier === 'fresh-start') {
      const passionAction = createAction('START_PASSION_PROJECT', profile, tier, urgencyLevel);
      if (passionAction) allActions.push(passionAction);
    }
  } else {
    // Has activities - suggest deepening
    const action = createAction('DEEPEN_ACTIVITY', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
  }

  if (leadershipSkip.show) {
    const action = createAction('SEEK_LEADERSHIP', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
    const initiativeAction = createAction('DEMONSTRATE_INITIATIVE', profile, tier, urgencyLevel);
    if (initiativeAction) allActions.push(initiativeAction);
  }

  if (serviceSkip.show) {
    const action = createAction('START_SERVICE', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
  } else {
    // Has service - suggest deepening
    const action = createAction('DEEPEN_SERVICE', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
  }

  if (awardsSkip.show && tier !== 'fresh-start') {
    const action = createAction('PURSUE_AWARDS', profile, tier, urgencyLevel);
    if (action) allActions.push(action);
  }

  // Add summer/research opportunities for appropriate grades
  const gradeNum = typeof grade === 'number' ? grade : 12;
  if (gradeNum >= 10 && gradeNum <= 11) {
    const summerAction = createAction('SUMMER_PROGRAM', profile, tier, urgencyLevel);
    if (summerAction) allActions.push(summerAction);

    if (tier !== 'fresh-start') {
      const researchAction = createAction('SUMMER_RESEARCH', profile, tier, urgencyLevel);
      if (researchAction) allActions.push(researchAction);
    }

    if (operating.careerDirection === 'yes' && operating.careerInterest) {
      const internAction = createAction('SUMMER_INTERNSHIP', profile, tier, urgencyLevel);
      if (internAction) allActions.push(internAction);
    }
  }

  // Narrative building for all tiers
  if (tier === 'fresh-start' || !operating.careerDirection || operating.careerDirection === 'no-idea') {
    const exploreAction = createAction('EXPLORE_INTERESTS', profile, tier, urgencyLevel);
    if (exploreAction) allActions.push(exploreAction);
  }

  if (tier === 'emerging' || tier === 'optimization') {
    const narrativeAction = createAction('BUILD_NARRATIVE', profile, tier, urgencyLevel);
    if (narrativeAction) allActions.push(narrativeAction);
  }

  // ============================================================================
  // ORGANIZE INTO PHASES
  // ============================================================================

  // Filter by available time
  const filteredActions = filterByAvailableTime(allActions, availableHours);

  // Separate quick wins and long-term goals
  const quickWins = filteredActions.filter(
    (a) =>
      a.timeCommitment.includes('1-2') ||
      a.timeCommitment.includes('2-3') ||
      a.category === 'narrative'
  );

  const longTermGoals = filteredActions.filter(
    (a) =>
      a.category === 'research' ||
      a.category === 'summer' ||
      a.impact.points >= 12
  );

  // Create phases
  const phase1Actions = filteredActions.filter((a) => a.priority === 'critical' || a.priority === 'high');
  const phase2Actions = filteredActions.filter((a) => a.priority === 'medium');
  const phase3Actions = filteredActions.filter((a) => a.priority === 'low');

  const phases: GamePlanPhase[] = [];

  if (phase1Actions.length > 0) {
    phases.push({
      id: 'phase-1',
      title: 'Immediate Priorities',
      description: 'Focus on these actions first for maximum impact.',
      timeframe: urgencyLevel === 'critical' ? 'This month' : 'Next 1-2 months',
      actions: phase1Actions,
    });
  }

  if (phase2Actions.length > 0) {
    phases.push({
      id: 'phase-2',
      title: 'Building Momentum',
      description: 'Continue with these actions as you establish your foundation.',
      timeframe: urgencyLevel === 'critical' ? 'Next 2-3 months' : 'Next 3-6 months',
      actions: phase2Actions,
    });
  }

  if (phase3Actions.length > 0) {
    phases.push({
      id: 'phase-3',
      title: 'Long-Term Development',
      description: 'Work on these when you have established core activities.',
      timeframe: 'Next 6-12 months',
      actions: phase3Actions,
    });
  }

  // ============================================================================
  // GENERATE SUMMARY
  // ============================================================================

  const strengthAreas: string[] = [];
  const improvementAreas: string[] = [];

  // Analyze strengths based on what's NOT skipped
  if (!gpaSkip.show) strengthAreas.push('Academic foundation');
  if (!testSkip.show) strengthAreas.push('Test scores');
  if (!ecSkip.show) strengthAreas.push('Extracurricular involvement');
  if (!leadershipSkip.show) strengthAreas.push('Leadership experience');
  if (!serviceSkip.show) strengthAreas.push('Community service');
  if (!awardsSkip.show) strengthAreas.push('Awards & recognition');

  // Analyze improvement areas based on what IS skipped
  if (gpaSkip.show) improvementAreas.push('Academic performance');
  if (testSkip.show) improvementAreas.push('Standardized testing');
  if (ecSkip.show) improvementAreas.push('Extracurricular activities');
  if (leadershipSkip.show) improvementAreas.push('Leadership roles');
  if (serviceSkip.show) improvementAreas.push('Community engagement');
  if (awardsSkip.show) improvementAreas.push('Awards & competitions');

  // Generate focus recommendation
  let focusRecommendation: string;
  if (tier === 'fresh-start') {
    focusRecommendation =
      'Start with one meaningful activity and focus on maintaining strong grades. ' +
      'Quality and consistency matter more than quantity at this stage.';
  } else if (tier === 'emerging') {
    focusRecommendation =
      'Deepen your existing activities and pursue leadership opportunities. ' +
      'Begin developing your unique narrative that ties everything together.';
  } else {
    focusRecommendation =
      'Focus on differentiating yourself through unique projects and research. ' +
      'Polish your narrative and maximize impact in your areas of strength.';
  }

  // Calculate total hours
  const totalEstimatedHours = filteredActions.reduce((total, action) => {
    const match = action.timeCommitment.match(/(\d+)(?:-(\d+))?\s*hrs?\/week/);
    if (match) {
      const avg = match[2] ? (parseInt(match[1]) + parseInt(match[2])) / 2 : parseInt(match[1]);
      return total + avg * 4; // Monthly hours
    }
    return total + 12; // Default 3hrs/week * 4 weeks
  }, 0);

  return {
    tier,
    tierInfo,
    totalEstimatedHours,
    weeklyCommitment: Math.min(availableHours, Math.ceil(totalEstimatedHours / 4)),
    phases,
    quickWins,
    longTermGoals,
    warnings,
    summary: {
      strengthAreas,
      improvementAreas,
      focusRecommendation,
    },
  };
}

/**
 * Get personalized recommendations based on specific operating data
 */
export function getStrengthBasedRecommendations(
  strengths: string[] | undefined,
): { activity: string; rationale: string }[] {
  const recommendations: { activity: string; rationale: string }[] = [];

  if (!strengths || strengths.length === 0) return recommendations;

  const strengthMapping: Record<string, { activity: string; rationale: string }> = {
    memorization: {
      activity: 'Academic competitions (Science Olympiad, Quiz Bowl)',
      rationale: 'Your strong memory makes you well-suited for knowledge-based competitions.',
    },
    'hands-on': {
      activity: 'Robotics, Engineering clubs, or Maker projects',
      rationale: 'Your hands-on skills are perfect for building and creating things.',
    },
    explaining: {
      activity: 'Tutoring, Teaching assistant, or Educational content creation',
      rationale: 'Your ability to explain concepts helps others and demonstrates mastery.',
    },
    competitive: {
      activity: 'Competitive debate, Model UN, or Sports',
      rationale: 'Your competitive drive will help you excel in head-to-head activities.',
    },
    social: {
      activity: 'Student government, Event planning, or Community organizing',
      rationale: 'Your people skills are valuable for leadership and community-building.',
    },
    creative: {
      activity: 'Arts, Design thinking projects, or Entrepreneurship',
      rationale: 'Your creativity sets you apart in innovative problem-solving.',
    },
    analytical: {
      activity: 'Math competitions, Research, or Data-driven projects',
      rationale: 'Your analytical skills are perfect for rigorous intellectual pursuits.',
    },
    disciplined: {
      activity: 'Long-term independent research or Consistent volunteering',
      rationale: 'Your discipline makes you reliable for commitments requiring persistence.',
    },
    curious: {
      activity: 'Research programs, Independent studies, or Science fairs',
      rationale: 'Your curiosity drives meaningful exploration and discovery.',
    },
    writing: {
      activity: 'School newspaper, Literary magazine, or Blogging',
      rationale: 'Your writing talent is valuable for storytelling and communication.',
    },
  };

  for (const strength of strengths) {
    const rec = strengthMapping[strength];
    if (rec) recommendations.push(rec);
  }

  return recommendations;
}

/**
 * Calculate burnout risk based on time commitments
 */
export function calculateBurnoutRisk(
  availableHours: number,
  homeworkHours: number,
  workHours?: number,
): 'low' | 'moderate' | 'high' {
  const weeklyWorkload = (workHours || 0) + homeworkHours * 7 + availableHours;

  // Assuming ~35 hours of school per week
  const totalWeeklyCommitment = 35 + weeklyWorkload;

  // Healthy range: 50-65 hours total
  // Moderate: 65-80 hours
  // High risk: 80+ hours
  if (totalWeeklyCommitment >= 80) return 'high';
  if (totalWeeklyCommitment >= 65) return 'moderate';
  return 'low';
}
