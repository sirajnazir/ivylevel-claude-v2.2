/**
 * Identity Insights Generator
 *
 * Generates personalized insights based on Identity data (Frame 4):
 * - Demographics (first-gen, cultural background)
 * - Context (work hours, family responsibilities, resources)
 * - Challenges (obstacles overcome, languages, background)
 *
 * These insights help students understand how their identity and context
 * can strengthen their application narrative.
 */

import type { StudentProfile } from '@/lib/types/student';
import type { RealtimeInsight } from './realtimeInsights';

export class IdentityInsightGenerator {
  /**
   * First-generation status insight
   */
  static generateFirstGenInsight(profile: StudentProfile): RealtimeInsight | null {
    const firstGen = profile.operating?.firstGeneration ?? null;

    if (firstGen === null) return null;

    if (firstGen === true) {
      return {
        id: `identity-firstgen-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🎓',
        title: 'First-Generation Advantage',
        message: 'Being first-generation college is a significant achievement factor. Colleges value your self-direction and family trailblazing. Make sure your story highlights how you navigated college prep without family guidance.',
        priority: 8,
        metricType: 'firstgen',
        percentile: 85,
        outcomeData: [
          { label: 'Ivy+ first-gen rate', value: '16-20%', comparison: 'actively recruited' },
          { label: 'Context boost', value: '+20%', comparison: 'in holistic review' },
        ],
      };
    }

    return null;
  }

  /**
   * Work hours + school balance insight
   */
  static generateWorkBalanceInsight(profile: StudentProfile): RealtimeInsight | null {
    const workHours = profile.operating?.workHours ?? 0;
    const gpa = profile.aptitude?.gpa_weighted ?? profile.aptitude?.gpa_unweighted ?? 0;

    if (workHours === 0) return null;

    if (workHours >= 20 && gpa >= 3.8) {
      return {
        id: `identity-work-excellence-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '💼',
        title: 'Working Student Excellence',
        message: `Working ${workHours} hrs/week WHILE maintaining a ${gpa.toFixed(2)} GPA shows exceptional time management and responsibility. This demonstrates maturity that many applicants lack. Highlight this balance in your essays.`,
        priority: 9,
        metricType: 'impact',
        percentile: 90,
        multiplier: '2x impact',
        outcomeData: [
          { label: 'Work + academics', value: 'Top 10%', comparison: 'time management signal' },
          { label: 'Maturity score', value: 'Exceptional', comparison: 'vs typical applicants' },
        ],
      };
    } else if (workHours >= 20) {
      return {
        id: `identity-work-context-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: '💡',
        title: 'Work Hours Context',
        message: `Working ${workHours} hrs/week is significant life context. Admissions officers will evaluate your academics with this in mind. Make sure to explain WHY you work (financial need, family support, etc.) in your application.`,
        priority: 7,
        metricType: 'impact',
        percentile: 75,
        outcomeData: [
          { label: 'Context weight', value: 'High', comparison: 'in holistic review' },
        ],
      };
    } else if (workHours >= 10) {
      return {
        id: `identity-work-balance-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: '⚖️',
        title: 'Balancing Work & School',
        message: `${workHours} hrs/week of work shows responsibility. If this was necessary (not optional), mention it—colleges value students who contribute to family finances.`,
        priority: 6,
        metricType: 'impact',
      };
    }

    return null;
  }

  /**
   * School resources + achievement insight
   */
  static generateResourceContextInsight(profile: StudentProfile): RealtimeInsight | null {
    const schoolResources = profile.operating?.schoolResources;
    const apCount = profile.aptitude?.ap_courses_taken ?? 0;
    const rigor = profile.aptitude?.course_rigor;

    if (!schoolResources) return null;

    if (schoolResources === 'limited' && apCount >= 5) {
      return {
        id: `identity-limited-resources-excellence-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🌟',
        title: 'Maximizing Limited Resources',
        message: `Taking ${apCount} APs at a school with LIMITED resources shows exceptional initiative. You squeezed every opportunity from your environment. This is a POWERFUL story—colleges specifically look for students who maximize their context.`,
        priority: 9,
        metricType: 'rigor',
        percentile: 95,
        multiplier: '3x impact',
        outcomeData: [
          { label: 'Context achievement', value: 'Top 5%', comparison: 'resourcefulness signal' },
          { label: 'Admit boost', value: '+25%', comparison: 'at top schools' },
        ],
      };
    } else if (schoolResources === 'limited' && rigor === 'MOST_RIGOROUS') {
      return {
        id: `identity-limited-resources-rigor-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '💪',
        title: 'Overcoming Resource Gaps',
        message: 'Taking the most rigorous schedule at a school with limited resources demonstrates self-advocacy and determination. Make sure your counselor notes this in their recommendation—it matters significantly.',
        priority: 8,
        metricType: 'rigor',
        percentile: 85,
        outcomeData: [
          { label: 'Context weight', value: 'Very High', comparison: 'in admissions' },
        ],
      };
    } else if (schoolResources === 'limited') {
      return {
        id: `identity-limited-resources-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: '📚',
        title: 'Limited Resources Narrative',
        message: 'Coming from a school with limited resources is valuable context. Highlight how you sought opportunities outside school (online courses, self-study, community resources). Resourcefulness is an Ivy+ trait.',
        priority: 7,
        metricType: 'rigor',
      };
    } else if (schoolResources === 'excellent' && apCount < 8) {
      return {
        id: `identity-excellent-resources-underutilized-${Date.now()}`,
        timestamp: Date.now(),
        category: 'warning',
        icon: '⚠️',
        title: 'Resources Not Maximized',
        message: `Your school offers excellent resources but you have taken ${apCount} APs. Top applicants from resource-rich schools typically take 10-15 APs. Consider if you could push rigor further or explain why you chose this path.`,
        priority: 7,
        metricType: 'rigor',
      };
    }

    return null;
  }

  /**
   * Challenge overcome insight
   */
  static generateChallengeInsight(profile: StudentProfile): RealtimeInsight | null {
    const challengeOvercome = profile.operating?.challengeOvercome ?? '';
    const challengeImpact = profile.operating?.challengeImpact ?? '';

    if (challengeOvercome.length < 30) return null;

    if (challengeOvercome.length >= 30 && challengeImpact.length >= 30) {
      return {
        id: `identity-challenge-narrative-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '✍️',
        title: 'Powerful Challenge Narrative',
        message: 'You have a compelling adversity → growth story. This is PREMIUM essay material. The best "challenge" essays show vulnerability + resilience + what you learned. You have all three elements.',
        priority: 9,
        metricType: 'other',
        outcomeData: [
          { label: 'Essay strength', value: 'Exceptional', comparison: 'adversity + growth' },
          { label: 'Authenticity', value: 'High', comparison: 'personal voice clear' },
        ],
      };
    } else if (challengeOvercome.length >= 30) {
      return {
        id: `identity-challenge-partial-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: '💭',
        title: 'Develop Challenge Story',
        message: 'You have described a challenge. Now add: How did it change you? What did you learn? What skills or perspectives did you gain? The IMPACT of adversity is what makes essays memorable.',
        priority: 7,
        metricType: 'other',
      };
    }

    return null;
  }

  /**
   * Multilingual insight
   */
  static generateLanguageInsight(profile: StudentProfile): RealtimeInsight | null {
    const languagesSpoken = profile.operating?.languagesSpoken ?? [];

    if (languagesSpoken.length < 2) return null;

    if (languagesSpoken.length >= 3) {
      return {
        id: `identity-multilingual-exceptional-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🌍',
        title: 'Multilingual Advantage',
        message: `Speaking ${languagesSpoken.length} languages (${languagesSpoken.slice(0, 3).join(', ')}${languagesSpoken.length > 3 ? '...' : ''}) is a unique intellectual asset. This signals cognitive flexibility, cultural bridge-building, and global perspective—all highly valued at top schools.`,
        priority: 8,
        metricType: 'other',
        percentile: 90,
        outcomeData: [
          { label: 'Language diversity', value: `${languagesSpoken.length} languages`, comparison: 'vs 1-2 typical' },
          { label: 'Global perspective', value: 'Strong signal', comparison: 'cultural asset' },
        ],
      };
    } else if (languagesSpoken.length === 2) {
      return {
        id: `identity-bilingual-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: '💬',
        title: 'Bilingual Strength',
        message: `Speaking ${languagesSpoken.join(' and ')} is an asset. If you serve as a translator for your family or community, mention it—that is concrete leadership and impact.`,
        priority: 6,
        metricType: 'other',
        percentile: 70,
      };
    }

    return null;
  }

  /**
   * Family responsibilities insight
   */
  static generateFamilyResponsibilityInsight(profile: StudentProfile): RealtimeInsight | null {
    const familyResponsibilities = profile.operating?.familyResponsibilities ?? '';
    const workHours = profile.operating?.workHours ?? 0;

    if (familyResponsibilities.length < 20) return null;

    if (familyResponsibilities.length >= 50 && workHours >= 15) {
      return {
        id: `identity-family-work-load-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🏠',
        title: 'Significant Life Responsibilities',
        message: `Balancing family responsibilities AND ${workHours} hrs/week of work shows exceptional maturity. This is powerful context that explains your time allocation. Make sure your application reflects the FULL scope of your responsibilities.`,
        priority: 9,
        metricType: 'impact',
        percentile: 95,
        outcomeData: [
          { label: 'Life responsibility', value: 'Very High', comparison: 'vs typical applicant' },
          { label: 'Maturity signal', value: 'Exceptional', comparison: 'adult-level obligations' },
        ],
      };
    } else if (familyResponsibilities.length >= 50) {
      return {
        id: `identity-family-responsibilities-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: '🏠',
        title: 'Family Context Matters',
        message: 'Your family responsibilities are significant context. If you care for siblings, translate for parents, or help with family business, these are REAL leadership experiences. Do not undervalue them.',
        priority: 7,
        metricType: 'impact',
        percentile: 80,
      };
    }

    return null;
  }

  /**
   * Cultural identity + storytelling insight
   */
  static generateCulturalIdentityInsight(profile: StudentProfile): RealtimeInsight | null {
    const culturalBackground = profile.operating?.culturalBackground ?? [];
    const comfortableDiscussing = profile.operating?.comfortableDiscussingBackground ?? null;

    if (culturalBackground.length === 0 || culturalBackground.includes('PREFER_NOT_SAY')) {
      return null;
    }

    if (culturalBackground.length >= 2 && comfortableDiscussing === true) {
      return {
        id: `identity-multiracial-story-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🎨',
        title: 'Multiracial Identity Strength',
        message: `Your ${culturalBackground.join('/')} identity gives you a unique perspective. Since you are comfortable discussing it, consider weaving this into your essays—how does navigating multiple cultures shape your worldview?`,
        priority: 7,
        metricType: 'other',
        outcomeData: [
          { label: 'Perspective diversity', value: 'High', comparison: 'cultural bridge-builder' },
        ],
      };
    } else if (comfortableDiscussing === true) {
      return {
        id: `identity-cultural-story-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: '📖',
        title: 'Cultural Identity in Essays',
        message: 'Since you are comfortable discussing your background, consider: How has your cultural identity shaped your interests, values, or perspective? Authenticity and specificity make the best identity essays.',
        priority: 6,
        metricType: 'other',
      };
    } else if (comfortableDiscussing === false) {
      return {
        id: `identity-cultural-private-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: '🔒',
        title: 'Identity Privacy Respected',
        message: 'You prefer to keep your background private—that is completely valid. You can still write powerful essays about interests, challenges, or impact without centering identity.',
        priority: 5,
        metricType: 'other',
      };
    }

    return null;
  }

  /**
   * Transportation + access insight
   */
  static generateAccessInsight(profile: StudentProfile): RealtimeInsight | null {
    const transportation = profile.operating?.transportation;
    const ecCount = profile.passion?.extracurriculars?.length ?? 0;

    if (!transportation) return null;

    if (transportation === 'limited' && ecCount >= 3) {
      return {
        id: `identity-limited-access-excellence-${Date.now()}`,
        timestamp: Date.now(),
        category: 'positive',
        icon: '🚶',
        title: 'Overcoming Access Barriers',
        message: `Having limited transportation yet participating in ${ecCount} activities shows serious determination. This is resourcefulness in action. If you walked, biked, or spent hours on public transit, mention it—it shows grit.`,
        priority: 8,
        metricType: 'impact',
        percentile: 85,
        outcomeData: [
          { label: 'Resourcefulness', value: 'Exceptional', comparison: 'overcame logistics' },
        ],
      };
    } else if (transportation === 'limited') {
      return {
        id: `identity-limited-access-${Date.now()}`,
        timestamp: Date.now(),
        category: 'tip',
        icon: '🚌',
        title: 'Access Context',
        message: 'Limited transportation is real context. If it limited your EC opportunities, mention it in "Additional Info." Admissions officers evaluate you within your circumstances.',
        priority: 6,
        metricType: 'other',
      };
    } else if (transportation === 'public-transit' && ecCount >= 4) {
      return {
        id: `identity-public-transit-commitment-${Date.now()}`,
        timestamp: Date.now(),
        category: 'info',
        icon: '🚊',
        title: 'Transit Time = Dedication',
        message: 'Relying on public transit for activities shows commitment. If you spend significant time commuting to ECs, that is part of your time investment—it counts.',
        priority: 5,
        metricType: 'other',
      };
    }

    return null;
  }

  /**
   * Master generator: analyzes all identity data and returns the most relevant insight
   */
  static generateIdentityInsight(profile: StudentProfile): RealtimeInsight | null {
    const insights = [
      this.generateFirstGenInsight(profile),
      this.generateWorkBalanceInsight(profile),
      this.generateResourceContextInsight(profile),
      this.generateChallengeInsight(profile),
      this.generateLanguageInsight(profile),
      this.generateFamilyResponsibilityInsight(profile),
      this.generateCulturalIdentityInsight(profile),
      this.generateAccessInsight(profile),
    ].filter((insight): insight is RealtimeInsight => insight !== null);

    // Return highest priority insight
    if (insights.length === 0) return null;

    return insights.sort((a, b) => b.priority - a.priority)[0];
  }
}
