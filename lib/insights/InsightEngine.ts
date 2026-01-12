/**
 * InsightEngine - Core Insight Generation Logic
 *
 * Generates real-time contextual insights based on student profile.
 * Source: Ported from Gemini Phoenix v2.2 InsightLogic system (~445 lines)
 *
 * 7 Insight Categories:
 * 1. HYPER_LOCAL - High school peer benchmarking
 * 2. CONTEXT - Demographics, region, hooks
 * 3. TEMPORAL - Grade-aware timing insights
 * 4. APTITUDE - GPA, SAT, rigor
 * 5. PASSION - Leadership, research, impact
 * 6. PSYCHOMETRIC - Grit, burnout, time management
 * 7. INSTITUTIONAL - CDS benchmarks, school-specific
 */

import {
  Insight,
  InsightCategory,
  InsightSeverity,
  InsightGenerationContext,
  InsightResult,
  StudentProfile,
  GradeLevel,
} from './types';

import {
  HIGH_SCHOOLS,
  getHighSchool,
  calculateAPUtilization,
  getStanfordMatriculation,
} from '@/lib/data/high-schools';

import {
  CDS_DATA,
  getCDSData,
  getPercentileRank,
  compareSATToSchool,
  compareGPAToSchool,
  calculateDemographicMultiplier,
} from '@/lib/data/cds-data';

// ============================================================================
// INSIGHT ENGINE CLASS
// ============================================================================

export class InsightEngine {
  /**
   * Main entry point: Generate all insights for a student profile
   */
  static generate(context: InsightGenerationContext): InsightResult {
    const insights: Insight[] = [];
    const { profile } = context;

    // Grade level helpers
    const grade = profile.grade;
    const isEarly = ['8', '9', '10'].includes(grade);
    const isJunior = grade === '11';
    const isSenior = grade === '12';

    // Generate insights from all 7 categories
    insights.push(...this.generateHyperLocalInsights(profile, isEarly, isJunior, isSenior));
    insights.push(...this.generateContextInsights(profile));
    insights.push(...this.generateTemporalInsights(profile, isEarly, isJunior, isSenior));
    insights.push(...this.generateAptitudeInsights(profile, isEarly));
    insights.push(...this.generatePassionInsights(profile, isEarly, isSenior));
    insights.push(...this.generatePsychometricInsights(profile));
    insights.push(...this.generateInstitutionalInsights(profile, isEarly));
    // Jenny Intelligence: Identity Insights
    insights.push(...this.generateIdentityInsights(profile));

    // Deduplicate and prioritize
    const uniqueInsights = this.deduplicateInsights(insights);
    const prioritizedInsights = this.prioritizeInsights(uniqueInsights);

    return {
      insights: prioritizedInsights,
      generatedAt: new Date().toISOString(),
      attributeTrigger: context.attribute,
    };
  }

  // ==========================================================================
  // CATEGORY 1: HYPER-LOCAL BENCHMARKING
  // ==========================================================================

  private static generateHyperLocalInsights(
    profile: StudentProfile,
    isEarly: boolean,
    isJunior: boolean,
    isSenior: boolean
  ): Insight[] {
    const insights: Insight[] = [];
    const schoolId = profile.high_school_id;

    if (!schoolId) return insights;

    const school = getHighSchool(schoolId);
    if (!school) return insights;

    const studentAps = profile.ap_count || 0;
    const studentSat = profile.sat_total || 0;

    // Signal 1: Rigor Context (AP Utilization Rate)
    const utilizationRate = calculateAPUtilization(schoolId, studentAps);

    if (utilizationRate < 0.25 && (isJunior || isSenior)) {
      insights.push({
        id: `hyper-rigor-low-${Date.now()}`,
        category: 'HYPER_LOCAL',
        title: 'Rigor Under-Utilization',
        message: `Your school (${school.name}) offers ${school.apOfferings} APs. You have taken ${studentAps}. Admissions officers calculate a "Utilization Rate." You are at ${(utilizationRate * 100).toFixed(0)}%. To be rated "Most Demanding," aim for >50% utilization.`,
        severity: 'critical',
        priority: 9,
        dataSource: `${school.name} Profile 2024`,
        data: {
          studentValue: studentAps,
          benchmark: school.apOfferings,
          percentile: utilizationRate * 100,
        },
      });
    } else if (utilizationRate >= 0.5) {
      insights.push({
        id: `hyper-rigor-strong-${Date.now()}`,
        category: 'HYPER_LOCAL',
        title: 'Maximum Rigor Confirmed',
        message: `You are utilizing ${(utilizationRate * 100).toFixed(0)}% of ${school.name}'s AP catalog (${studentAps}/${school.apOfferings}). This satisfies the "Most Demanding" curriculum threshold.`,
        severity: 'positive',
        priority: 7,
        dataSource: `${school.name} Profile 2024`,
      });
    }

    // Signal 2: The "Hacker Path" (Dual Enrollment)
    if (school.dualEnrollment.strategicValue === 'HIGH' && studentAps < 8) {
      insights.push({
        id: `hyper-dual-enroll-${Date.now()}`,
        category: 'HYPER_LOCAL',
        title: 'Rigor Hack: Dual Enrollment',
        message: `Since ${school.name} has fewer APs than Bay Area competitors (avg 24), you must leverage ${school.dualEnrollment.partnerCollege || 'Community College'}. Taking "Calculus III" or "Physics" there is the only way to match the rigor of a Monta Vista transcript.`,
        severity: 'warning',
        priority: 8,
        dataSource: 'Strategic Course Planning',
      });
    }

    // Signal 3: Peer Benchmark (SAT Gap)
    const stanfordStats = getStanfordMatriculation(schoolId);

    if (stanfordStats && studentSat > 0) {
      const gap = studentSat - stanfordStats.avgAdmitSat;

      if (gap < -20) {
        insights.push({
          id: `hyper-sat-gap-${Date.now()}`,
          category: 'HYPER_LOCAL',
          title: 'The "Peer Gap"',
          message: `The average ${school.name} student admitted to Stanford had a ${stanfordStats.avgAdmitSat}. You are ${Math.abs(gap)} points behind your immediate predecessors. In a high-saturation school, being below the school average is a significant drag.`,
          severity: 'warning',
          priority: 8,
          dataSource: `${school.name} Matriculation Data`,
          delta: `${gap} pts`,
          data: {
            studentValue: studentSat,
            benchmark: stanfordStats.avgAdmitSat,
          },
        });
      } else if (gap >= 0) {
        insights.push({
          id: `hyper-sat-pass-${Date.now()}`,
          category: 'HYPER_LOCAL',
          title: 'Cleared Local Bar',
          message: `You have matched or exceeded the ${stanfordStats.avgAdmitSat} average for Stanford admits from ${school.name}. This removes the "Academic Drag" and shifts the focus entirely to your Spike.`,
          severity: 'positive',
          priority: 7,
          dataSource: `${school.name} Matriculation Data`,
        });
      }
    }

    // Signal 4: Local Spike Patterns
    const mySpike = profile.research_level;
    const commonSpikes = stanfordStats?.commonSpikes || [];

    if (commonSpikes.length > 0 && !commonSpikes.includes('Research') && mySpike !== 'PEER_REVIEWED') {
      insights.push({
        id: `hyper-pattern-miss-${Date.now()}`,
        category: 'HYPER_LOCAL',
        title: 'Missing Success Pattern',
        message: `Historical analysis of admits from ${school.name} shows a pattern: ${commonSpikes.join(', ')}. Your profile currently lacks these specific signals.`,
        severity: 'neutral',
        priority: 6,
        dataSource: 'Alumni Pattern Recognition',
      });
    }

    return insights;
  }

  // ==========================================================================
  // CATEGORY 2: CONTEXT LAYER (Demographics)
  // ==========================================================================

  private static generateContextInsights(profile: StudentProfile): Insight[] {
    const insights: Insight[] = [];

    if (profile.income_top_1 && !profile.legacy) {
      insights.push({
        id: `ctx-saturation-${Date.now()}`,
        category: 'CONTEXT',
        title: 'High Saturation Zone',
        message: `You are competing against students with identical resource access. Without 'Legacy' (5x), your Non-Academic rating must be top 1% to compete. A 4.0 GPA is a baseline, not a differentiator.`,
        severity: 'warning',
        priority: 8,
        dataSource: 'Chetty: Public vs Private Multipliers',
      });
    }

    if (profile.region === 'BAY_AREA' && !profile.legacy) {
      insights.push({
        id: `ctx-bayarea-${Date.now()}`,
        category: 'CONTEXT',
        title: 'Bay Area Saturation',
        message: `Bay Area applicants face intense competition. Your peer set includes students from Monta Vista, Gunn, and Palo Alto High. Standing out requires exceptional non-academic differentiation.`,
        severity: 'warning',
        priority: 7,
        dataSource: 'Chetty: Regional Distribution Analysis',
      });
    }

    if (profile.ethnicity === 'ASIAN' && profile.intended_major === 'Computer Science') {
      insights.push({
        id: `ctx-pivot-${Date.now()}`,
        category: 'CONTEXT',
        title: 'Strategic Major Pivot',
        message: `CS is the toughest pool (0.85x odds). Framing your narrative around 'Symbolic Systems' or 'Computational Ethics' enters the Humanities pool (+30% boost) while keeping the tech focus.`,
        severity: 'neutral',
        priority: 6,
        dataSource: 'Chetty: Major Selection ROI',
      });
    }

    if (profile.legacy) {
      insights.push({
        id: `ctx-legacy-${Date.now()}`,
        category: 'CONTEXT',
        title: 'Legacy Advantage Active',
        message: `Legacy status provides 5x admission probability multiplier. This is equivalent to a 160-point SAT boost in predictive power.`,
        severity: 'positive',
        priority: 9,
        dataSource: 'Chetty: Legacy ROI Analysis',
      });
    }

    if (profile.first_gen) {
      insights.push({
        id: `ctx-firstgen-${Date.now()}`,
        category: 'CONTEXT',
        title: 'First-Gen Narrative Unlocked',
        message: `First-generation status activates a compelling narrative arc. Pair this with evidence of 'overcoming' in essays for maximum Personal Rating impact.`,
        severity: 'positive',
        priority: 7,
        dataSource: 'Ivy Rubric: Personal Rating Drivers',
      });
    }

    if (profile.region === 'RURAL') {
      insights.push({
        id: `ctx-rural-${Date.now()}`,
        category: 'CONTEXT',
        title: 'Geographic Diversity Bonus',
        message: `Rural origin activates 'Geo-Diversity' consideration. You're competing in a smaller pool with less saturation. Structural advantage confirmed.`,
        severity: 'positive',
        priority: 7,
        dataSource: 'Chetty: Regional Distribution',
      });
    }

    return insights;
  }

  // ==========================================================================
  // CATEGORY 3: GRADE-AWARE TEMPORAL INSIGHTS
  // ==========================================================================

  private static generateTemporalInsights(
    profile: StudentProfile,
    isEarly: boolean,
    isJunior: boolean,
    isSenior: boolean
  ): Insight[] {
    const insights: Insight[] = [];
    const impact = profile.project_impact || 0;
    const studentSat = profile.sat_total || 0;

    // Early Start Advantage (9-10th grade + Any Spike)
    if (isEarly && impact > 100) {
      insights.push({
        id: `time-early-start-${Date.now()}`,
        category: 'TEMPORAL',
        title: 'Compound Interest Effect',
        message: `Starting a project in ${profile.grade}th grade gives you the most valuable asset: TIME. You have 2-3 years to scale this to National Level.`,
        severity: 'positive',
        priority: 8,
        dataSource: 'Chetty: EC Consistency',
      });
    }

    // Early Grade - Time to Build
    if (isEarly && impact === 0) {
      insights.push({
        id: `time-early-opportunity-${Date.now()}`,
        category: 'TEMPORAL',
        title: 'Prime Building Window',
        message: `As a ${profile.grade}th grader, you have time to build something significant. Start a project NOW—compound growth over 2-3 years creates the "Founder Story" that seniors can't fake.`,
        severity: 'neutral',
        priority: 7,
        dataSource: 'Timeline Strategy',
      });
    }

    // Senior Urgency - Low Impact
    if (isSenior && impact < 500) {
      insights.push({
        id: `time-senior-gap-${Date.now()}`,
        category: 'TEMPORAL',
        title: 'The Runway is Gone',
        message: `As a senior, you don't have time to build a new non-profit. You must pivot to 'Packaging.' Your strategy shifts from 'Building' to 'Storytelling'.`,
        severity: 'critical',
        priority: 9,
        dataSource: 'Application Strategy',
      });
    }

    // Junior Urgency - Time is Now
    if (isJunior && impact < 500) {
      insights.push({
        id: `time-junior-window-${Date.now()}`,
        category: 'TEMPORAL',
        title: 'Final Building Window',
        message: `Junior year is your LAST chance to build new initiatives. After this summer, you shift to "Packaging Mode." Any spike must be launched NOW.`,
        severity: 'warning',
        priority: 8,
        dataSource: 'Timeline Strategy',
      });
    }

    // Test Optional Risk (11-12th + No Test + Competitive Region)
    if (!isEarly && studentSat === 0 && profile.region === 'BAY_AREA') {
      insights.push({
        id: `time-test-optional-${Date.now()}`,
        category: 'TEMPORAL',
        title: 'The "Test Optional" Trap',
        message: `For unhooked applicants from competitive zones (Bay Area), 'Test Optional' often signals 'Low Score' to AOs. Reinstating a score of 1500+ is the single highest ROI intervention.`,
        severity: 'warning',
        priority: 8,
        dataSource: 'Dartmouth/Yale Testing Data 2024',
      });
    }

    return insights;
  }

  // ==========================================================================
  // CATEGORY 4: APTITUDE LAYER
  // ==========================================================================

  private static generateAptitudeInsights(profile: StudentProfile, isEarly: boolean): Insight[] {
    const insights: Insight[] = [];
    const gpa = profile.gpa_weighted || 0;
    const studentSat = profile.sat_total || 0;
    const awards = profile.academic_awards || [];

    if (gpa >= 4.0) {
      insights.push({
        id: `apt-gpa-ceiling-${Date.now()}`,
        category: 'APTITUDE',
        title: 'Academic Baseline Secured',
        message: `A ${gpa.toFixed(2)} GPA meets the Academic Rating 1 threshold. At this level, additional GPA gains have diminishing returns—focus shifts to Spike and Narrative.`,
        severity: 'positive',
        priority: 7,
        dataSource: 'Ivy Rubric: Academic Rating Thresholds',
        data: { studentValue: gpa },
      });
    }

    if (gpa > 0 && gpa < 3.7) {
      insights.push({
        id: `apt-gpa-low-${Date.now()}`,
        category: 'APTITUDE',
        title: 'Academic Core At Risk',
        message: `A ${gpa.toFixed(2)} GPA falls below Academic Rating 2 threshold for most Ivies. This becomes a 'filter' unless offset by exceptional Spikes or Hooks.`,
        severity: 'critical',
        priority: 9,
        dataSource: 'Ivy Rubric: Minimum Thresholds',
        data: { studentValue: gpa },
      });
    }

    if (studentSat > 0 && studentSat < 1550 && !isEarly) {
      insights.push({
        id: `apt-sat-threshold-${Date.now()}`,
        category: 'APTITUDE',
        title: 'The 1550+ Threshold',
        message: `A ${studentSat} is strong, but for unhooked applicants, 1550+ acts as a 'Soft Gate' for Academic Rating 1. +${1550 - studentSat} points equals a minor legacy boost.`,
        severity: 'neutral',
        priority: 6,
        dataSource: 'Chetty: Test Score Predictive Value',
        delta: `+${1550 - studentSat} to threshold`,
        data: { studentValue: studentSat, benchmark: 1550 },
      });
    }

    if (awards.length === 0 && !isEarly) {
      insights.push({
        id: `apt-award-gap-${Date.now()}`,
        category: 'APTITUDE',
        title: 'The "Validation" Gap',
        message: `A 4.0 GPA is internal to your school. You need External Validation (Olympiads, CTFs, National Merit) to prove grades hold up nationally.`,
        severity: 'warning',
        priority: 7,
        dataSource: 'Chetty: Academic Ratings',
      });
    }

    if (awards.includes('INTERNATIONAL') || awards.includes('USAMO') || awards.includes('REGENERON')) {
      insights.push({
        id: `apt-award-gold-${Date.now()}`,
        category: 'APTITUDE',
        title: 'Elite Distinction Confirmed',
        message: `International/National-level recognition (USAMO, Regeneron, MOP) is the strongest signal of Academic Rating 1.`,
        severity: 'positive',
        priority: 9,
        dataSource: 'Harvard Rubric: Academic Rating 1 Criteria',
      });
    }

    return insights;
  }

  // ==========================================================================
  // CATEGORY 5: PASSION LAYER
  // ==========================================================================

  private static generatePassionInsights(
    profile: StudentProfile,
    isEarly: boolean,
    isSenior: boolean
  ): Insight[] {
    const insights: Insight[] = [];
    const research = profile.research_level;
    const impact = profile.project_impact || 0;
    const leadership = profile.leadership_level;

    if (research === 'PEER_REVIEWED') {
      insights.push({
        id: `pas-research-gold-${Date.now()}`,
        category: 'PASSION',
        title: 'Intellectual Vitality: Gold',
        message: `Publication in a peer-reviewed journal is the "Gold Standard" for Intellectual Vitality. This moves you from "Student" to "Scholar."`,
        severity: 'positive',
        priority: 9,
        dataSource: 'Harvard Admissions Rubric: IV Rating 1',
      });
    }

    if (research === 'RSI_SIMR') {
      insights.push({
        id: `pas-research-program-${Date.now()}`,
        category: 'PASSION',
        title: 'Elite Research Program',
        message: `RSI/SIMR acceptance (<10% rate) is a strong Intellectual Vitality signal.`,
        severity: 'positive',
        priority: 8,
        dataSource: 'Ivy Rubric: IV Rating 2',
      });
    }

    if (impact >= 10000) {
      insights.push({
        id: `pas-impact-national-${Date.now()}`,
        category: 'PASSION',
        title: 'National Impact Confirmed',
        message: `Reaching ${impact.toLocaleString()}+ people is founder-level impact. This triggers the 2.0x Non-Academic Multiplier.`,
        severity: 'positive',
        priority: 9,
        dataSource: 'Chetty: Non-Academic Ratings ROI',
        data: { studentValue: impact },
      });
    }

    if (impact >= 500 && impact < 10000) {
      insights.push({
        id: `pas-impact-regional-${Date.now()}`,
        category: 'PASSION',
        title: 'Regional Impact Achieved',
        message: `${impact.toLocaleString()}+ reach moves you from "Participant" to "Leader." Push to 10k for the 2.0x multiplier.`,
        severity: 'positive',
        priority: 7,
        dataSource: 'Chetty: Non-Academic Ratings',
        data: { studentValue: impact, benchmark: 10000 },
      });
    }

    if (leadership === 'OFFICER' || leadership === 'MEMBER') {
      insights.push({
        id: `pas-leader-depth-${Date.now()}`,
        category: 'PASSION',
        title: 'Title vs. Impact',
        message: `"President" of a 10-member club scores lower than "Founder" impacting 1,000. Focus on the *verb*, not the *noun*.`,
        severity: 'warning',
        priority: 6,
        dataSource: 'Chetty: Non-Academic Ratings',
      });
    }

    if (impact === 0 && !isEarly) {
      insights.push({
        id: `pas-no-spike-${Date.now()}`,
        category: 'PASSION',
        title: 'Spike Missing',
        message: `No quantifiable impact detected. Without a demonstrable Spike reaching 100+ people, Non-Academic Rating defaults to average (3).`,
        severity: 'critical',
        priority: 9,
        dataSource: 'Chetty: Non-Academic Distribution',
      });
    }

    return insights;
  }

  // ==========================================================================
  // CATEGORY 6: PSYCHOMETRIC LAYER
  // ==========================================================================

  private static generatePsychometricInsights(profile: StudentProfile): Insight[] {
    const insights: Insight[] = [];
    const grit = profile.grit_resilience || 0.5;
    const burnout = profile.burnout_risk;

    if (grit > 0.8) {
      insights.push({
        id: `psy-grit-high-${Date.now()}`,
        category: 'PSYCHOMETRIC',
        title: 'High Resilience Detected',
        message: `Your narrative demonstrates "Anti-Fragility"—the ability to grow from failure. This is a key "Personal Rating" factor.`,
        severity: 'positive',
        priority: 7,
        dataSource: 'Personal Rating Rubric',
      });
    }

    if (grit < 0.4) {
      insights.push({
        id: `psy-grit-low-${Date.now()}`,
        category: 'PSYCHOMETRIC',
        title: 'Resilience Narrative Needed',
        message: `No clear "overcome adversity" signal detected. Consider surfacing a challenge narrative in your Personal Statement.`,
        severity: 'neutral',
        priority: 5,
        dataSource: 'Personal Rating Enhancement',
      });
    }

    if (burnout === 'HIGH') {
      insights.push({
        id: `psy-burnout-${Date.now()}`,
        category: 'PSYCHOMETRIC',
        title: 'Schedule Saturation',
        message: `Your "Burn Rate" is critical. We must *prune* low-ROI activities (e.g., generic volunteering) to make room for a Spike.`,
        severity: 'warning',
        priority: 8,
        dataSource: '168-Hour Framework',
      });
    }

    return insights;
  }

  // ==========================================================================
  // CATEGORY 7: INSTITUTIONAL BENCHMARKING (CDS Data)
  // ==========================================================================

  private static generateInstitutionalInsights(
    profile: StudentProfile,
    isEarly: boolean
  ): Insight[] {
    const insights: Insight[] = [];
    const studentSat = profile.sat_total || 0;
    const targetSchools = profile.target_schools || [];

    // MIT Math Floor Check
    if (targetSchools.includes('mit') && studentSat > 0) {
      const mitData = getCDSData('mit');
      if (mitData) {
        const estimatedMath = Math.round(studentSat / 2) + 10;

        if (estimatedMath < mitData.sat_25th / 2) {
          insights.push({
            id: `inst-mit-math-${Date.now()}`,
            category: 'INSTITUTIONAL',
            title: 'The MIT Math Floor',
            message: `MIT's 25th percentile for Math is ${Math.round(mitData.sat_25th / 2)}. Your estimated Math (~${estimatedMath}) may be below this threshold. MIT views Math readiness as a binary gate.`,
            severity: 'critical',
            priority: 9,
            dataSource: 'MIT Common Data Set 2023-24',
          });
        }
      }
    }

    // Legacy Reality Check (MIT/Caltech don't consider legacy)
    if (profile.legacy) {
      const legacyNullSchools = targetSchools.filter((sid) => {
        const college = getCDSData(sid);
        return college && college.legacy_roi <= 1.0;
      });

      if (legacyNullSchools.length > 0) {
        insights.push({
          id: `inst-legacy-waste-${Date.now()}`,
          category: 'INSTITUTIONAL',
          title: 'Legacy Advantage Nullified',
          message: `You have Legacy status, but you're targeting ${legacyNullSchools.join(', ')}. These schools explicitly state Legacy is "Not Considered" in their CDS. Your structural advantage evaporates here.`,
          severity: 'warning',
          priority: 7,
          dataSource: 'CDS Section C7',
        });
      }
    }

    // Below 25th Percentile Check
    if (studentSat > 0 && !isEarly) {
      const belowThreshold = targetSchools.filter((sid) => {
        const cds = getCDSData(sid);
        return cds && studentSat < cds.sat_25th;
      });

      if (belowThreshold.length > 0) {
        const lowestCds = getCDSData(belowThreshold[0]);
        const lowestBar = lowestCds?.sat_25th || 1400;

        insights.push({
          id: `inst-sat-floor-${Date.now()}`,
          category: 'INSTITUTIONAL',
          title: 'Below Institutional Floor',
          message: `Your SAT (${studentSat}) falls below the 25th percentile (${lowestBar}) for ${belowThreshold.length} target school(s): ${belowThreshold.join(', ')}. You are in the "Needs Hook" zone.`,
          severity: 'critical',
          priority: 9,
          dataSource: 'Common Data Set 2023-24',
          delta: `${studentSat - lowestBar} pts`,
          data: { studentValue: studentSat, benchmark: lowestBar },
        });
      }
    }

    // Stanford REA vs Princeton REA Strategy
    if (targetSchools.includes('stanford') && targetSchools.includes('princeton')) {
      const stanfordEarly = getCDSData('stanford')?.acceptance_rate_ea;
      const princetonEarly = getCDSData('princeton')?.acceptance_rate_ea;

      if (stanfordEarly && princetonEarly && princetonEarly > stanfordEarly) {
        insights.push({
          id: `inst-rea-selection-${Date.now()}`,
          category: 'INSTITUTIONAL',
          title: 'REA Optimization',
          message: `Both Stanford and Princeton offer REA. Stanford's REA rate is ${(stanfordEarly * 100).toFixed(1)}% vs Princeton's ${(princetonEarly * 100).toFixed(1)}%. Princeton shows a stronger "demonstrated interest" advantage.`,
          severity: 'neutral',
          priority: 6,
          dataSource: 'CDS Section C21 Analysis',
        });
      }
    }

    return insights;
  }

  // ==========================================================================
  // JENNY INTELLIGENCE: IDENTITY INSIGHTS
  // ==========================================================================

  /**
   * Jenny Intelligence: Identity Insights
   * Surface deep identity-level patterns that reveal the student's core narrative
   */
  private static generateIdentityInsights(profile: StudentProfile): Insight[] {
    const insights: Insight[] = [];

    // Identity Pattern 1: The "Hidden Why"
    // What truly drives this student beyond surface-level activities?
    const hiddenWhy = this.detectHiddenWhy(profile);
    if (hiddenWhy) {
      insights.push({
        id: `identity-hidden-why-${Date.now()}`,
        category: 'PSYCHOMETRIC',
        title: 'Your Hidden "Why"',
        message: hiddenWhy.message,
        severity: 'positive',
        priority: 8,
        dataSource: 'Jenny Intelligence: Identity Pattern Analysis',
        data: hiddenWhy.data,
      });
    }

    // Identity Pattern 2: The "Contradiction Opportunity"
    // Apparent contradictions in profile that can become unique strengths
    const contradiction = this.detectContradiction(profile);
    if (contradiction) {
      insights.push({
        id: `identity-contradiction-${Date.now()}`,
        category: 'CONTEXT',
        title: 'Your Unique Contradiction',
        message: contradiction.message,
        severity: 'positive',
        priority: 7,
        dataSource: 'Jenny Intelligence: Narrative Pattern Analysis',
        data: contradiction.data,
      });
    }

    // Identity Pattern 3: The "Growth Arc"
    // Evidence of transformation over time
    const growthArc = this.detectGrowthArc(profile);
    if (growthArc) {
      insights.push({
        id: `identity-growth-arc-${Date.now()}`,
        category: 'TEMPORAL',
        title: 'Your Growth Story',
        message: growthArc.message,
        severity: growthArc.strength === 'strong' ? 'positive' : 'neutral',
        priority: growthArc.strength === 'strong' ? 8 : 6,
        dataSource: 'Jenny Intelligence: Transformation Analysis',
        data: growthArc.data,
      });
    }

    // Identity Pattern 4: The "Bridge Builder"
    // Connections between seemingly unrelated activities
    const bridges = this.detectBridges(profile);
    if (bridges.length > 0) {
      insights.push({
        id: `identity-bridges-${Date.now()}`,
        category: 'PASSION',
        title: 'Your Connecting Threads',
        message: `You have ${bridges.length} potential narrative thread(s) connecting your activities: ${bridges.join(', ')}. These bridges are goldmines for essays.`,
        severity: 'positive',
        priority: 7,
        dataSource: 'Jenny Intelligence: Narrative Threading',
        data: { bridges },
      });
    }

    return insights;
  }

  private static detectHiddenWhy(profile: StudentProfile): { message: string; data: Record<string, unknown> } | null {
    const activities = profile.activities || [];
    const major = profile.intended_major;
    const serviceHours = profile.service_hours || 0;
    const firstGen = profile.first_gen;

    // Pattern: Service-to-Major connection
    if (serviceHours > 100 && major) {
      const serviceConnection = this.findServiceConnection(major);
      if (serviceConnection) {
        return {
          message: `Your ${serviceHours}+ service hours suggest a deeper purpose beyond academics. Your interest in ${major} combined with community engagement reveals you're driven by ${serviceConnection}. This "why" is your essay gold.`,
          data: { serviceHours, major, connection: serviceConnection },
        };
      }
    }

    // Pattern: First-gen drive
    if (firstGen) {
      return {
        message: `As a first-generation college applicant, you carry the weight and honor of opening doors for your family. This isn't just about you—it's about everyone who came before. Admissions officers know this story is real.`,
        data: { firstGen: true },
      };
    }

    // Pattern: Activity depth over breadth
    const deepActivities = activities.filter(a => (a.years || 0) >= 3);
    if (deepActivities.length >= 2) {
      return {
        message: `You've invested 3+ years in ${deepActivities.length} activities. This depth signals that you're not chasing credentials—you're pursuing genuine passion. Your "why" is authenticity itself.`,
        data: { deepActivities: deepActivities.length },
      };
    }

    return null;
  }

  private static findServiceConnection(major: string): string | null {
    const connections: Record<string, string> = {
      'Computer Science': 'using technology to solve real human problems',
      'Medicine': 'healing and helping others at their most vulnerable',
      'Engineering': 'building solutions that improve lives',
      'Business': 'creating value that benefits communities',
      'Education': 'empowering others to reach their potential',
      'Psychology': 'understanding and supporting human wellbeing',
      'Political Science': 'advocating for systemic change',
      'Environmental Science': 'protecting the planet for future generations',
    };
    return connections[major] || null;
  }

  private static detectContradiction(profile: StudentProfile): { message: string; data: Record<string, unknown> } | null {
    const major = profile.intended_major;
    const activities = profile.activities || [];
    const activityTypes = activities.map(a => a.type || '').filter(Boolean);

    // Pattern: STEM + Arts
    const hasStem = major?.match(/Science|Engineering|Math|CS|Computer/i) || activityTypes.some(t => t.match(/STEM|science|tech/i));
    const hasArts = activityTypes.some(t => t.match(/art|music|theater|creative|writing/i));

    if (hasStem && hasArts) {
      return {
        message: `You bridge the STEM-Arts divide—a rare combination. While others specialize, you synthesize. This "contradiction" is actually your superpower: you can communicate technical concepts creatively, or bring analytical rigor to creative work.`,
        data: { hasStem: true, hasArts: true },
      };
    }

    // Pattern: Competitive + Service
    const hasCompetitive = activityTypes.some(t => t.match(/competition|olympiad|tournament|debate/i));
    const hasService = activityTypes.some(t => t.match(/volunteer|service|community|nonprofit/i));

    if (hasCompetitive && hasService) {
      return {
        message: `You're both fiercely competitive and deeply service-oriented. This isn't a contradiction—it's a sign that you compete not for ego, but to maximize your ability to give back. Frame this in your essays.`,
        data: { hasCompetitive: true, hasService: true },
      };
    }

    return null;
  }

  private static detectGrowthArc(profile: StudentProfile): { message: string; strength: 'strong' | 'emerging'; data: Record<string, unknown> } | null {
    const grit = profile.grit_resilience || 0.5;
    const activities = profile.activities || [];

    // Look for progression evidence
    const hasProgression = activities.some(a =>
      a.description?.match(/grew|improved|transformed|evolved|built|founded|started/i)
    );

    if (grit > 0.7 && hasProgression) {
      return {
        message: `Your profile shows clear evidence of transformation. You don't just participate—you grow, adapt, and level up. This growth arc is exactly what admissions officers look for: someone who will continue evolving at their institution.`,
        strength: 'strong',
        data: { grit, hasProgression: true },
      };
    }

    if (grit > 0.5) {
      return {
        message: `Your profile hints at a growth story waiting to be told. Consider: what challenges have shaped you? What did you try, fail at, then master? Mining these moments will strengthen your narrative.`,
        strength: 'emerging',
        data: { grit },
      };
    }

    return null;
  }

  private static detectBridges(profile: StudentProfile): string[] {
    const bridges: string[] = [];
    const activities = profile.activities || [];
    const major = profile.intended_major;

    // Look for thematic connections
    const themes = {
      leadership: activities.filter(a => a.role?.match(/president|founder|captain|leader|director/i)),
      innovation: activities.filter(a => a.description?.match(/created|launched|built|designed|invented/i)),
      teaching: activities.filter(a => a.description?.match(/taught|mentored|tutored|coached|trained/i)),
      impact: activities.filter(a => a.description?.match(/helped|served|raised|donated|impacted/i)),
    };

    if (themes.leadership.length >= 2) bridges.push('Leadership across contexts');
    if (themes.innovation.length >= 2) bridges.push('Creative problem-solving');
    if (themes.teaching.length >= 2) bridges.push('Passion for empowering others');
    if (themes.impact.length >= 2) bridges.push('Measurable community impact');

    // Major-activity bridge
    if (major && activities.some(a => a.description?.toLowerCase().includes(major.toLowerCase()))) {
      bridges.push(`${major} connects to extracurriculars`);
    }

    return bridges;
  }

  // ==========================================================================
  // UTILITIES
  // ==========================================================================

  /**
   * Remove duplicate insights (same ID prefix)
   */
  private static deduplicateInsights(insights: Insight[]): Insight[] {
    const seen = new Set<string>();
    return insights.filter((insight) => {
      // Get base ID (without timestamp)
      const baseId = insight.id.replace(/-\d+$/, '');
      if (seen.has(baseId)) return false;
      seen.add(baseId);
      return true;
    });
  }

  /**
   * Sort insights by priority (highest first)
   */
  private static prioritizeInsights(insights: Insight[]): Insight[] {
    return [...insights].sort((a, b) => b.priority - a.priority);
  }

  /**
   * Filter insights by criteria
   */
  static filterInsights(
    insights: Insight[],
    options: {
      categories?: InsightCategory[];
      severities?: InsightSeverity[];
      minPriority?: number;
      maxResults?: number;
    }
  ): Insight[] {
    let filtered = insights;

    if (options.categories?.length) {
      filtered = filtered.filter((i) => options.categories!.includes(i.category));
    }

    if (options.severities?.length) {
      filtered = filtered.filter((i) => options.severities!.includes(i.severity));
    }

    if (options.minPriority !== undefined) {
      filtered = filtered.filter((i) => i.priority >= options.minPriority!);
    }

    if (options.maxResults !== undefined) {
      filtered = filtered.slice(0, options.maxResults);
    }

    return filtered;
  }

  /**
   * Get insights statistics
   */
  static getStats(insights: Insight[]): {
    total: number;
    byCategory: Record<InsightCategory, number>;
    bySeverity: Record<InsightSeverity, number>;
    averagePriority: number;
  } {
    const byCategory: Record<InsightCategory, number> = {
      HYPER_LOCAL: 0,
      CONTEXT: 0,
      TEMPORAL: 0,
      APTITUDE: 0,
      PASSION: 0,
      PSYCHOMETRIC: 0,
      INSTITUTIONAL: 0,
    };

    const bySeverity: Record<InsightSeverity, number> = {
      critical: 0,
      warning: 0,
      positive: 0,
      neutral: 0,
    };

    insights.forEach((i) => {
      byCategory[i.category]++;
      bySeverity[i.severity]++;
    });

    const avgPriority =
      insights.length > 0
        ? insights.reduce((sum, i) => sum + i.priority, 0) / insights.length
        : 0;

    return {
      total: insights.length,
      byCategory,
      bySeverity,
      averagePriority: Number(avgPriority.toFixed(1)),
    };
  }
}

export default InsightEngine;
