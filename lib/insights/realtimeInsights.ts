/**
 * Real-Time Insights Generator
 *
 * Generates personalized contextual insights based on specific user inputs.
 * These appear immediately after user actions (GPA change, test score entry, etc.)
 */

import type { StudentProfile } from '@/lib/types/student';

export interface OutcomeDataItem {
  label: string;
  value: string;
  comparison?: string;
}

export interface RealtimeInsight {
  id: string;
  timestamp: number;
  category: 'positive' | 'warning' | 'tip' | 'info';
  icon: string;
  title: string;
  message: string;
  priority: number; // 1-10, higher = more important
  metricType: 'gpa' | 'sat' | 'act' | 'ap' | 'leadership' | 'service' | 'research' | 'impact' | 'firstgen' | 'rigor' | 'demographics' | 'milestone' | 'general' | 'other';
  metricSubtype?: string; // e.g., 'weighted' | 'unweighted' for GPA
  percentile?: number; // 0-100, what percentile of applicants
  multiplier?: string; // e.g., "3x average"
  xpValue?: number; // Edge reward for this insight (formerly XP)
  scoreDelta?: {
    pillar: 'aptitude' | 'passion' | 'service' | 'identity';
    change: number;
  };
  outcomeData?: OutcomeDataItem[];
}

/**
 * Generates insights based on specific input changes
 */
export class RealtimeInsightGenerator {
  /**
   * GPA input insights
   */
  static generateGPAInsight(profile: StudentProfile): RealtimeInsight | null {
    const gpa = profile.aptitude?.gpa_weighted ?? profile.aptitude?.gpa_unweighted ?? 0;

    if (gpa === 0) return null;

    // Check for context factors
    const firstGen = profile.demographics?.first_gen ?? false;

    // General GPA insights
    if (gpa >= 4.5) {
      return {
        id: `gpa-high-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: 'target',
        title: 'Top 10% GPA',
        message: `Your ${gpa.toFixed(2)} weighted GPA is in the top 10% of all Ivy+ applicants. Strong academic foundation!`,
        priority: 8,
        metricType: 'gpa',
        percentile: 90,
        multiplier: '1.5x admit rate',
        outcomeData: [
          { label: 'MIT admit rate', value: '18%', comparison: 'vs 5% overall' },
          { label: 'Stanford admit rate', value: '15%', comparison: 'vs 4% overall' },
        ],
      };
    } else if (gpa >= 4.0) {
      return {
        id: `gpa-competitive-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: 'analytics',
        title: 'Competitive GPA',
        message: `Your ${gpa.toFixed(2)} GPA is competitive for top-20 schools. Focus on differentiation through your unique story and impact.`,
        priority: 6,
        metricType: 'gpa',
        percentile: 75,
        outcomeData: [
          { label: 'Top 20 avg admit', value: '12%', comparison: '2x baseline' },
        ],
      };
    } else if (gpa >= 3.7) {
      const contextMsg = firstGen
        ? `As a first-generation student, your ${gpa.toFixed(2)} GPA demonstrates significant self-direction. Context matters.`
        : `Your ${gpa.toFixed(2)} GPA will be evaluated in context: What resources did your school offer? What else was on your plate?`;
      return {
        id: `gpa-context-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: 'suggestion',
        title: 'Context Is Key',
        message: contextMsg,
        priority: 7,
        metricType: 'gpa',
        percentile: 60,
      };
    } else if (gpa >= 3.5) {
      return {
        id: `gpa-context-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: 'suggestion',
        title: 'GPA in Context',
        message: `Admissions officers evaluate your ${gpa.toFixed(2)} GPA in the context of your school's resources and your personal circumstances.`,
        priority: 7,
        metricType: 'gpa',
        percentile: 50,
      };
    } else if (gpa >= 3.0) {
      return {
        id: `gpa-below-${Date.now()}`,
        timestamp: Date.now(),
        category: 'warning',
        icon: '⚠️',
        title: 'GPA Below Typical Range',
        message: `Your ${gpa.toFixed(2)} GPA is below the typical Ivy+ range (3.9-4.0 unweighted). Strong context and exceptional non-academic achievements can offset this. Focus on building a compelling narrative.`,
        priority: 8,
        metricType: 'gpa',
        percentile: 35,
      };
    }

    return null;
  }

  /**
   * SAT/ACT input insights
   */
  static generateTestScoreInsight(profile: StudentProfile): RealtimeInsight | null {
    const sat = profile.aptitude?.sat_total ?? 0;
    const act = profile.aptitude?.act_total ?? 0;
    const testOptional = profile.aptitude?.test_optional ?? false;

    if (testOptional) {
      return {
        id: `test-optional-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: 'note',
        title: 'Test-Optional Strategy',
        message:
          'Many top schools are test-optional. Your holistic profile (GPA, activities, story) will carry the evaluation. Focus on strengthening your narrative and impact.',
        priority: 7,
        metricType: 'sat',
      };
    }

    if (sat === 0 && act === 0) return null;

    const score = sat || act;
    const scoreType = sat ? 'SAT' : 'ACT';
    const metricType = sat ? 'sat' : 'act';

    if (sat >= 1550 || act >= 35) {
      return {
        id: `test-99th-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: 'target',
        title: '99th Percentile',
        message: `Your ${score} ${scoreType} is in the 99th percentile nationally. This demonstrates strong academic readiness for any school.`,
        priority: 8,
        metricType,
        percentile: 99,
        multiplier: '2x admit rate',
        outcomeData: [
          { label: 'Ivy+ admit rate', value: '15%', comparison: 'vs 5% baseline' },
        ],
      };
    } else if (sat >= 1500 || act >= 34) {
      return {
        id: `test-competitive-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '✓',
        title: 'Competitive Test Score',
        message: `Your ${score} ${scoreType} is within the middle 50% range for all Ivy+ schools. Combined with strong academics and impact, you're in competitive range.`,
        priority: 7,
        metricType,
        percentile: 95,
        outcomeData: [
          { label: 'Within middle 50%', value: 'Yes', comparison: 'for all Ivies' },
        ],
      };
    } else if (sat >= 1450 || act >= 32) {
      return {
        id: `test-range-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: 'analytics',
        title: 'Within Range',
        message: `Your ${score} ${scoreType} is within range for selective schools. Many schools are test-optional—your holistic profile matters most.`,
        priority: 6,
        metricType,
        percentile: 90,
      };
    } else if (sat >= 1400 || act >= 30) {
      return {
        id: `test-consider-optional-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: 'suggestion',
        title: 'Consider Test-Optional',
        message: `Your ${score} ${scoreType} is solid but below typical Ivy+ ranges (1500+). Consider applying test-optional to schools where your achievements and narrative can shine.`,
        priority: 7,
        metricType,
        percentile: 85,
      };
    } else if (sat > 0 || act > 0) {
      return {
        id: `test-optional-rec-${Date.now()}`,
        timestamp: Date.now(),
        category: 'warning',
        icon: '⚠️',
        title: 'Test-Optional Recommended',
        message: `Your ${score} ${scoreType} is below the middle 50% for most selective schools. Strongly consider test-optional applications where your GPA, activities, and story carry the evaluation.`,
        priority: 8,
        metricType,
        percentile: 70,
      };
    }

    return null;
  }

  /**
   * Leadership level insights
   */
  static generateLeadershipInsight(profile: StudentProfile): RealtimeInsight | null {
    const leadership = profile.passion?.leadership_level;

    if (!leadership) return null;

    const levelMap: Record<string, number> = {
      FOUNDER_NATIONAL: 6,
      FOUNDER_STATE: 5,
      STATE_PRES: 4,
      SCHOOL_PRES: 3,
      OFFICER: 2,
      PARTICIPANT: 1,
    };

    const level = levelMap[leadership] ?? 0;

    if (level >= 5) {
      return {
        id: `leadership-national-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🌟',
        title: 'National Leadership',
        message:
          'National-level leadership appears in only 8% of applications—but these students have significantly higher admit rates. This is a major differentiator.',
        priority: 9,
        metricType: 'leadership',
        percentile: 92,
        multiplier: '3x admit rate',
        outcomeData: [
          { label: 'Only in', value: '8%', comparison: 'of applications' },
          { label: 'Admit rate boost', value: '+12%', comparison: 'vs baseline' },
        ],
      };
    } else if (level >= 4) {
      return {
        id: `leadership-regional-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '👏',
        title: 'Regional Impact',
        message: 'State or regional leadership demonstrates significant initiative and real-world impact. Only ~15% of applicants reach this level.',
        priority: 7,
        metricType: 'leadership',
        percentile: 85,
        multiplier: '2x admit rate',
        outcomeData: [
          { label: 'Applicant pool', value: '15%', comparison: 'reach this level' },
        ],
      };
    } else if (level >= 3) {
      return {
        id: `leadership-school-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: 'suggestion',
        title: 'School-Wide Leadership',
        message:
          'School-wide leadership is solid (~30% of applicants). To stand out further, consider: Can you expand your impact beyond campus? Partner with other schools?',
        priority: 6,
        metricType: 'leadership',
        percentile: 70,
      };
    } else if (level >= 2) {
      return {
        id: `leadership-club-${Date.now()}`,
        timestamp: Date.now(),
        category: 'warning',
        icon: '⚠️',
        title: 'Increase Leadership Depth',
        message: 'Club officer roles are common (~50% of applicants). To differentiate, focus on: measurable impact, scope of responsibility, or founding new initiatives.',
        priority: 7,
        metricType: 'leadership',
        percentile: 50,
      };
    }

    return null;
  }

  /**
   * Service hours insights
   */
  static generateServiceInsight(profile: StudentProfile): RealtimeInsight | null {
    const hours = profile.community?.service_hours ?? 0;

    if (hours === 0) return null;

    if (hours >= 300) {
      return {
        id: `service-exceptional-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🎖️',
        title: 'Exceptional Service Commitment',
        message: `${hours} service hours is 4x the average applicant. This shows sustained commitment! Focus on the STORY: Why this cause? What impact did you create?`,
        priority: 8,
        metricType: 'service',
        percentile: 95,
        multiplier: '4x average',
        outcomeData: [
          { label: 'Top tier applicants', value: 'Top 5%', comparison: 'by hours' },
          { label: 'Essay impact boost', value: '+15%', comparison: 'when narrative strong' },
        ],
      };
    } else if (hours >= 200) {
      return {
        id: `service-strong-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: 'social',
        title: 'Strong Service Record',
        message: `${hours} hours is 3x the average applicant. Quality of impact matters as much as quantity—make sure to highlight specific outcomes.`,
        priority: 7,
        metricType: 'service',
        percentile: 85,
        multiplier: '3x average',
        outcomeData: [
          { label: 'Applicant pool', value: 'Top 15%', comparison: 'by service hours' },
        ],
      };
    } else if (hours >= 100) {
      return {
        id: `service-solid-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: '💭',
        title: 'Solid Service Foundation',
        message: `${hours} hours is solid. Focus on the narrative: Why this cause? How did you grow? What changed because of your involvement?`,
        priority: 6,
        metricType: 'service',
        percentile: 60,
      };
    } else if (hours >= 50) {
      return {
        id: `service-modest-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: 'suggestion',
        title: 'Build Service Depth',
        message: `${hours} hours is modest for competitive applicants. Consider: Can you deepen commitment to one cause? Create measurable impact?`,
        priority: 6,
        metricType: 'service',
        percentile: 40,
      };
    } else {
      return {
        id: `service-lived-experience-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: 'suggestion',
        title: 'Service from Lived Experience',
        message:
          'Formal volunteer hours are just one form of service. Family responsibilities, community help, translation for parents—these COUNT as service when framed properly.',
        priority: 7,
        metricType: 'service',
      };
    }
  }

  /**
   * AP/Course rigor insights
   */
  static generateRigorInsight(profile: StudentProfile): RealtimeInsight | null {
    const apCount = profile.aptitude?.ap_count ?? 0;
    const ibDiploma = profile.aptitude?.ib_diploma ?? false;

    if (ibDiploma) {
      return {
        id: `rigor-ib-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: 'graduation',
        title: 'IB Diploma',
        message: 'IB Diploma demonstrates exceptional course rigor and is highly valued by admissions officers. This is equivalent to 8-12 APs in terms of rigor scoring.',
        priority: 8,
        metricType: 'ap',
        percentile: 95,
        outcomeData: [
          { label: 'Ivy+ applicant pool', value: 'Top 5%', comparison: 'by rigor' },
        ],
      };
    }

    if (apCount === 0) return null;

    if (apCount >= 12) {
      return {
        id: `rigor-exceptional-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: 'academics',
        title: 'Exceptional Course Rigor',
        message: `${apCount} AP courses demonstrates exceptional academic ambition. Make sure your AP scores (ideally 4-5) match the course count for maximum impact.`,
        priority: 8,
        metricType: 'ap',
        percentile: 92,
        outcomeData: [
          { label: 'Rigor rating', value: 'Maximum', comparison: 'on transcript' },
          { label: 'With 4-5 scores', value: '+18%', comparison: 'admit boost' },
        ],
      };
    } else if (apCount >= 8) {
      return {
        id: `rigor-strong-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: 'academics',
        title: 'Strong Course Rigor',
        message: `${apCount} APs shows strong rigor. Remember: quality and performance matter more than quantity. Focus on scores of 4-5.`,
        priority: 7,
        metricType: 'ap',
        percentile: 80,
        outcomeData: [
          { label: 'Applicant pool', value: 'Top 20%', comparison: 'by AP count' },
        ],
      };
    } else if (apCount >= 5) {
      return {
        id: `rigor-competitive-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: 'note',
        title: 'Competitive Rigor',
        message: `${apCount} APs is competitive, especially if they're in your spike area. Course rigor is evaluated relative to what YOUR school offers.`,
        priority: 6,
        metricType: 'ap',
        percentile: 60,
      };
    } else {
      return {
        id: `rigor-context-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: 'suggestion',
        title: 'Rigor in Context',
        message: `${apCount} APs will be evaluated based on what your school offers. If your school has limited APs, admissions officers understand.`,
        priority: 6,
        metricType: 'ap',
        percentile: 40,
      };
    }
  }

  /**
   * First-gen insight
   */
  static generateFirstGenInsight(profile: StudentProfile): RealtimeInsight | null {
    const firstGen = profile.demographics?.first_gen ?? false;

    if (!firstGen) return null;

    return {
      id: `firstgen-advantage-${Date.now()}`,
      timestamp: Date.now(),
      category: 'positive',
      icon: 'growth',
      title: 'First-Generation Advantage',
      message:
        'First-generation students demonstrate pioneering spirit, resourcefulness, and self-direction—qualities Ivy+ schools actively seek. Make sure your application highlights how you navigated the college process independently.',
      priority: 9,
      metricType: 'firstgen',
      percentile: 88,
      outcomeData: [
        { label: 'Admit rate boost', value: '+8%', comparison: 'at Ivy+ schools' },
        { label: 'Context consideration', value: 'High', comparison: 'by AOs' },
      ],
    };
  }

  /**
   * Project impact insights
   */
  static generateProjectImpactInsight(profile: StudentProfile): RealtimeInsight | null {
    const impact = profile.passion?.project_impact ?? 0;

    if (impact === 0) return null;

    if (impact >= 1000) {
      return {
        id: `impact-viral-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🌟',
        title: 'Significant Impact',
        message: `Reaching ${impact.toLocaleString()} people with your project shows significant real-world impact. This is the kind of "spike" that makes applications stand out.`,
        priority: 9,
        metricType: 'impact',
        percentile: 98,
        multiplier: '10x average reach',
        outcomeData: [
          { label: 'Spike rating', value: 'Exceptional', comparison: 'top 2%' },
          { label: 'Essay strength', value: 'Very Strong', comparison: 'quantified impact' },
        ],
      };
    } else if (impact >= 100) {
      return {
        id: `impact-community-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: 'social',
        title: 'Community Impact',
        message: `Your project's ${impact} person reach demonstrates initiative. Quantify results where possible in your essays—numbers tell a story.`,
        priority: 7,
        metricType: 'impact',
        percentile: 75,
        outcomeData: [
          { label: 'Above average', value: 'Yes', comparison: 'for applicants' },
        ],
      };
    } else if (impact >= 20) {
      return {
        id: `impact-group-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: 'suggestion',
        title: 'Growing Impact',
        message: `${impact} people reached is a start. Consider: How can you scale this? Partnerships, social media, or school-wide initiatives could expand your reach.`,
        priority: 6,
        metricType: 'impact',
        percentile: 50,
      };
    }

    return null;
  }

  /**
   * Research level insights
   */
  static generateResearchInsight(profile: StudentProfile): RealtimeInsight | null {
    const research = profile.passion?.research_level;

    if (!research || research === 'NONE') return null;

    const researchMap: Record<string, { category: RealtimeInsight['category']; icon: string; title: string; message: string; priority: number; percentile?: number; outcomeData?: OutcomeDataItem[] }> = {
      NATIONAL: {
        category: 'positive',
        icon: 'research',
        title: 'Published Research',
        message: 'Peer-reviewed publication is in the top 2% of applicants. This demonstrates genuine intellectual contribution—a major differentiator for STEM-focused schools.',
        priority: 9,
        percentile: 98,
        outcomeData: [
          { label: 'MIT/Caltech boost', value: '+25%', comparison: 'admit rate' },
          { label: 'Applicant pool', value: 'Top 2%', comparison: 'by research' },
        ],
      },
      STATE: {
        category: 'positive',
        icon: 'experiment',
        title: 'Recognized Researcher',
        message: 'State/regional research recognition shows initiative beyond classroom learning. Highlight your methodology and findings in your application.',
        priority: 7,
        percentile: 85,
        outcomeData: [
          { label: 'Above average', value: 'Top 15%', comparison: 'of applicants' },
        ],
      },
      SCHOOL: {
        category: 'info',
        icon: 'analytics',
        title: 'Research Foundation',
        message: 'School-level research is a strong start. Consider reaching out to local universities for summer research opportunities to deepen your work.',
        priority: 6,
        percentile: 60,
      },
      INDEPENDENT: {
        category: 'tip',
        icon: 'suggestion',
        title: 'Self-Directed Learning',
        message: 'Independent exploration shows curiosity. Document your process and findings—self-directed projects can become compelling application narratives.',
        priority: 5,
        percentile: 45,
      },
    };

    const insightData = researchMap[research];
    if (!insightData) return null;

    return {
      id: `research-${research.toLowerCase()}-${Date.now()}`,
      timestamp: Date.now(),
      metricType: 'research',
      ...insightData,
    };
  }

  /**
   * Generate insight based on attribute type
   */
  static generateInsightForAttribute(
    profile: StudentProfile,
    attribute: string
  ): RealtimeInsight | null {
    switch (attribute) {
      case 'gpa':
      case 'gpa_weighted':
      case 'gpa_unweighted':
        return this.generateGPAInsight(profile);
      case 'sat':
      case 'sat_total':
      case 'act':
      case 'act_total':
      case 'test_optional':
        return this.generateTestScoreInsight(profile);
      case 'leadership':
      case 'leadership_level':
        return this.generateLeadershipInsight(profile);
      case 'service':
      case 'service_hours':
        return this.generateServiceInsight(profile);
      case 'ap':
      case 'ap_count':
      case 'ib_diploma':
        return this.generateRigorInsight(profile);
      case 'first_gen':
        return this.generateFirstGenInsight(profile);
      case 'project_impact':
        return this.generateProjectImpactInsight(profile);
      case 'research':
      case 'research_level':
        return this.generateResearchInsight(profile);
      default:
        return null;
    }
  }
}

export default RealtimeInsightGenerator;
