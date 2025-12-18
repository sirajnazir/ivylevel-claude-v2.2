import type { StudentProfile } from '@/lib/types/student';
import type { RealtimeInsight } from '@/lib/insights/realtimeInsights';
import { BENCHMARKS, type BenchmarkData } from '@/lib/data/benchmarks';
import { OUTCOMES, type OutcomeData } from '@/lib/data/outcomeData';

/**
 * Base class for all insight generators
 * Provides shared utilities for percentile calculation, message formatting, etc.
 */
export abstract class BaseInsightGenerator {
  protected profile: StudentProfile;
  protected benchmarks: BenchmarkData;
  protected outcomes: OutcomeData;

  constructor(profile: StudentProfile) {
    this.profile = profile;
    this.benchmarks = BENCHMARKS;
    this.outcomes = OUTCOMES;
  }

  /**
   * Generate insight - must be implemented by subclasses
   */
  abstract generate(): RealtimeInsight | null;

  /**
   * Calculate percentile from value and distribution
   */
  protected calculatePercentile(
    value: number,
    distribution: Record<number, number>
  ): number {
    // Find the closest match in distribution
    const thresholds = Object.keys(distribution)
      .map(Number)
      .sort((a, b) => b - a); // Sort descending

    for (const threshold of thresholds) {
      if (value >= threshold) {
        return distribution[threshold];
      }
    }

    // If below all thresholds, return lowest percentile
    return distribution[thresholds[thresholds.length - 1]] || 0;
  }

  /**
   * Get multiplier for a value
   */
  protected getMultiplier(
    value: number,
    multipliers: Record<number, number>
  ): number {
    const thresholds = Object.keys(multipliers)
      .map(Number)
      .sort((a, b) => b - a);

    for (const threshold of thresholds) {
      if (value >= threshold) {
        return multipliers[threshold];
      }
    }

    return 1.0; // baseline
  }

  /**
   * Format message by replacing variables
   */
  protected formatMessage(template: string, data: Record<string, unknown>): string {
    let message = template;

    Object.keys(data).forEach(key => {
      const value = data[key];
      message = message.replace(new RegExp(`{${key}}`, 'g'), String(value));
    });

    return message;
  }

  /**
   * Get GPA range key for outcome lookup
   */
  protected getGPARange(gpa: number): keyof typeof OUTCOMES.byGPA | null {
    if (gpa >= 4.5) return '4.5+';
    if (gpa >= 4.0) return '4.0-4.5';
    if (gpa >= 3.7) return '3.7-4.0';
    if (gpa >= 3.5) return '3.5-3.7';
    return null;
  }

  /**
   * Get leadership level key
   */
  protected getLeadershipKey(
    level: string
  ): keyof typeof BENCHMARKS.leadership.distribution | null {
    const map: Record<string, keyof typeof BENCHMARKS.leadership.distribution> = {
      'FOUNDER_NATIONAL': 'national',
      'FOUNDER_STATE': 'regional',
      'STATE_PRES': 'regional',
      'SCHOOL_PRES': 'schoolWide',
      'OFFICER': 'clubOfficer',
      'PARTICIPANT': 'member',
    };
    return map[level] || null;
  }

  /**
   * Detect context factors from profile
   */
  protected detectContextFactors(): {
    hasContext: boolean;
    factors: string[];
    totalBoost: number;
  } {
    const factors: string[] = [];
    let totalBoost = 0;

    // Check work status - use hidden_capabilities.work_experience if available
    const workExperience = this.profile.assessment_intelligence?.hidden_capabilities?.work_experience;
    // Simple heuristic: if work_experience is mentioned, assume significant work
    if (workExperience && workExperience.length > 0) {
      factors.push('work experience');
      totalBoost += this.benchmarks.gpa.contextBoosts.work15Plus;
    }

    // Check first-gen status from demographics
    const firstGen = this.profile.demographics?.first_gen;
    if (firstGen) {
      factors.push('first-generation student');
      totalBoost += this.benchmarks.gpa.contextBoosts.firstGen;
    }

    // Check family responsibilities from hidden_capabilities
    const familyResponsibilities = this.profile.assessment_intelligence?.hidden_capabilities?.family_responsibilities;
    if (familyResponsibilities && familyResponsibilities.length > 0) {
      factors.push('family caretaking');
      totalBoost += this.benchmarks.gpa.contextBoosts.familyCare;
    }

    return {
      hasContext: factors.length > 0,
      factors,
      totalBoost,
    };
  }
}
