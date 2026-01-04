/**
 * IvyQuest Contextual Insights
 * Frame-specific AI prompts with actionable suggestions.
 * @version 10.0
 */

export type InsightSeverity = 'positive' | 'suggestion' | 'warning' | 'neutral';
export type InsightCategory = 'APTITUDE' | 'PASSION' | 'SERVICE' | 'IDENTITY' | 'CONTEXT' | 'GENERAL';

export interface InsightAction {
  label: string;
  handler: string;
  data?: Record<string, unknown>;
}

export interface Insight {
  id: string;
  type: InsightSeverity;
  category: InsightCategory;
  message: string;
  detail?: string;
  actionable: boolean;
  action?: InsightAction;
}

type InsightGenerator = (profile: any) => Insight[];

export const FRAME_INSIGHTS: Record<number, InsightGenerator> = {
  // Frame 2: Snapshot
  2: (profile) => {
    const insights: Insight[] = [];
    const gpa = profile?.aptitude?.gpa_unweighted;
    const sat = profile?.aptitude?.sat_total;
    const act = profile?.aptitude?.act_total;
    const isFirstGen = profile?.demographics?.first_gen;

    if (gpa !== undefined) {
      if (gpa >= 3.7) {
        insights.push({
          id: 'gpa-excellent', type: 'positive', category: 'APTITUDE',
          message: `Your ${gpa.toFixed(2)} GPA puts you in a strong academic position!`,
          detail: 'Top colleges look for students who challenge themselves academically.',
          actionable: false,
        });
      } else if (gpa >= 3.0) {
        insights.push({
          id: 'gpa-context', type: 'positive', category: 'APTITUDE',
          message: `Your GPA of ${gpa.toFixed(2)} is solid! Context matters more than you think.`,
          detail: isFirstGen 
            ? 'First-gen students with your GPA often outperform higher-GPA students who had more resources.'
            : 'Admissions officers evaluate GPA in context of your school and opportunities.',
          actionable: false,
        });
      } else if (gpa < 3.0) {
        insights.push({
          id: 'gpa-improve', type: 'suggestion', category: 'APTITUDE',
          message: 'There\'s room to strengthen your academic profile.',
          detail: 'An upward trend in grades can be very compelling to admissions committees.',
          actionable: true,
          action: { label: 'See GPA improvement strategies', handler: 'openGPAStrategies' },
        });
      }
    }

    if (sat && sat >= 1400) {
      insights.push({
        id: 'sat-strong', type: 'positive', category: 'APTITUDE',
        message: `Your SAT score of ${sat} is competitive for selective schools!`,
        actionable: false,
      });
    } else if (act && act >= 30) {
      insights.push({
        id: 'act-strong', type: 'positive', category: 'APTITUDE',
        message: `Your ACT score of ${act} positions you well for top colleges!`,
        actionable: false,
      });
    } else if (!sat && !act) {
      insights.push({
        id: 'test-optional', type: 'neutral', category: 'APTITUDE',
        message: 'Many top schools are test-optional now.',
        detail: 'Strong extracurriculars and essays can offset not submitting scores.',
        actionable: true,
        action: { label: 'View test-optional schools', handler: 'openTestOptionalList' },
      });
    }

    return insights;
  },

  // Frame 3: Building
  3: (profile) => {
    const insights: Insight[] = [];
    const ecTypes = profile?.passion?.ec_types || [];
    const leadershipLevel = profile?.passion?.leadership_level || 0;
    const awards = profile?.passion?.ec_awards || [];
    const commitment = profile?.passion?.ec_commitment_years || 0;

    if (leadershipLevel < 3 && ecTypes.length >= 3) {
      insights.push({
        id: 'leadership-potential', type: 'suggestion', category: 'PASSION',
        message: `You've got ${ecTypes.length} activities but haven't highlighted leadership yet.`,
        detail: 'Most activities have hidden leadership opportunities. Let me help you find them.',
        actionable: true,
        action: { label: 'Identify leadership potential', handler: 'openLeadershipTips' },
      });
    } else if (leadershipLevel >= 4) {
      insights.push({
        id: 'leadership-strong', type: 'positive', category: 'PASSION',
        message: 'Your leadership experience stands out!',
        detail: 'Founding or presiding over organizations shows initiative admissions love.',
        actionable: false,
      });
    }

    if (commitment >= 3) {
      insights.push({
        id: 'commitment-deep', type: 'positive', category: 'PASSION',
        message: `${commitment}+ years of commitment shows real dedication.`,
        detail: 'Depth beats breadth. Colleges want to see sustained passion.',
        actionable: false,
      });
    }

    const hasService = ecTypes.some((t: string) => 
      ['community_service', 'volunteering', 'nonprofit'].includes(t.toLowerCase())
    );
    if (!hasService && ecTypes.length > 0) {
      insights.push({
        id: 'add-service', type: 'suggestion', category: 'SERVICE',
        message: 'Adding community service could round out your profile.',
        detail: 'Service shows you care about impact beyond personal achievement.',
        actionable: true,
        action: { label: 'Find service opportunities', handler: 'openServiceOpportunities' },
      });
    }

    if (awards.length >= 3) {
      insights.push({
        id: 'awards-strong', type: 'positive', category: 'PASSION',
        message: `${awards.length} awards demonstrate recognized excellence!`,
        actionable: false,
      });
    }

    return insights;
  },

  // Frame 4: Context
  4: (profile) => {
    const insights: Insight[] = [];
    const demo = profile?.demographics;
    const availableHours = profile?.operating?.availableHoursPerWeek || 0;

    if (demo?.first_gen) {
      insights.push({
        id: 'first-gen-strength', type: 'positive', category: 'CONTEXT',
        message: 'Being first-generation is a significant strength in your application.',
        detail: 'Jenny\'s first-gen students had 28% higher admit rates at top schools. Your unique perspective matters.',
        actionable: false,
      });
    }

    if (demo?.family_duties) {
      insights.push({
        id: 'family-superpower', type: 'positive', category: 'CONTEXT',
        message: 'Family responsibilities can be a superpower in your application.',
        detail: 'Students who mention family duties authentically had 23% higher admit rates in our data.',
        actionable: true,
        action: { label: 'Learn how to frame this', handler: 'openFamilyFraming' },
      });
    }

    if (demo?.low_ses) {
      insights.push({
        id: 'ses-context', type: 'positive', category: 'CONTEXT',
        message: 'Your economic background provides important context for your achievements.',
        detail: 'Admissions committees evaluate accomplishments relative to available resources.',
        actionable: false,
      });
    }

    if (availableHours < 10) {
      insights.push({
        id: 'time-constraints', type: 'suggestion', category: 'CONTEXT',
        message: `With ${availableHours} hours/week available, let's focus on high-impact activities.`,
        detail: 'Quality over quantity. We\'ll prioritize actions that maximize your profile.',
        actionable: true,
        action: { label: 'See time-efficient strategies', handler: 'openTimeStrategies' },
      });
    }

    const constraintCount = [demo?.first_gen, demo?.family_duties, demo?.low_ses].filter(Boolean).length;
    if (constraintCount >= 2) {
      insights.push({
        id: 'multiple-contexts', type: 'positive', category: 'CONTEXT',
        message: 'Your unique combination of experiences creates a compelling narrative.',
        detail: 'Multiple context factors significantly boost your Context Relativity Index.',
        actionable: false,
      });
    }

    return insights;
  },

  // Frame 5: Reveal
  5: (profile) => [{
    id: 'reveal-celebration', type: 'positive', category: 'GENERAL',
    message: 'You\'ve completed your profile assessment!',
    detail: 'Now let\'s turn insights into action with your personalized game plan.',
    actionable: false,
  }],

  // Frame 6: Quick Start
  6: (profile) => [{
    id: 'quick-start-focus', type: 'suggestion', category: 'GENERAL',
    message: 'Focus on these 3 actions this week for maximum impact.',
    detail: 'Research shows completing just ONE action in 24 hours predicts long-term success.',
    actionable: true,
    action: { label: 'Start Action #1 now', handler: 'startFirstAction' },
  }],
};

export function getFrameInsights(frameNumber: number, profile: any): Insight[] {
  const generator = FRAME_INSIGHTS[frameNumber];
  return generator ? generator(profile) : [];
}

export function getPrimaryInsight(frameNumber: number, profile: any): Insight | null {
  const insights = getFrameInsights(frameNumber, profile);
  const priority: InsightSeverity[] = ['positive', 'suggestion', 'warning', 'neutral'];
  for (const type of priority) {
    const match = insights.find(i => i.type === type);
    if (match) return match;
  }
  return insights[0] || null;
}

// Insight action handlers
export const INSIGHT_HANDLERS: Record<string, (data?: any) => void> = {
  openGPAStrategies: () => console.log('Opening GPA strategies'),
  openTestOptionalList: () => console.log('Opening test-optional list'),
  openLeadershipTips: () => console.log('Opening leadership tips'),
  openServiceOpportunities: () => console.log('Opening service opportunities'),
  openFamilyFraming: () => console.log('Opening family framing guide'),
  openTimeStrategies: () => console.log('Opening time strategies'),
  startFirstAction: () => console.log('Starting first action'),
};

export function executeInsightAction(action: InsightAction): void {
  const handler = INSIGHT_HANDLERS[action.handler];
  if (handler) handler(action.data);
}
