/**
 * Archetype Detection System
 *
 * PRINCIPLE: Every student has a unique profile that maps to an archetype.
 * Archetypes are determined by the DOMINANT characteristics of the profile.
 * No student should get "Generic" - there's always a pattern to detect.
 */

import type { StudentProfile, IvyReadyScore } from '../types/student';
import type { ArchetypeID } from '../types/student';

// =============================================================================
// ARCHETYPE DEFINITIONS
// =============================================================================

export interface ArchetypeDefinition {
  id: ArchetypeID;
  label: string;
  tagline: string;
  description: string;
  matchScore: (profile: StudentProfile, scores: IvyReadyScore['category_scores']) => number;
}

/**
 * Archetype definitions with scoring functions
 * Each archetype is detected based on profile characteristics
 */
export const ARCHETYPES: ArchetypeDefinition[] = [
  // Academic Excellence Archetypes
  {
    id: 'SCHOLAR',
    label: 'The Scholar',
    tagline: 'Excellence through intellectual mastery',
    description: 'Strong academics with rigorous course load',
    matchScore: (p, scores) => {
      let score = 0;
      // High aptitude is primary
      if (scores.aptitude >= 70) score += 40;
      else if (scores.aptitude >= 50) score += 20;
      // GPA and rigor
      if ((p.aptitude.gpa_normalized ?? 0) >= 0.80) score += 20;
      if ((p.aptitude.rigor_normalized ?? 0) >= 0.70) score += 20;
      // Research bonus
      if (p.passion.research_level && p.passion.research_level !== 'NONE') score += 15;
      // Aptitude must be dominant category
      if (scores.aptitude > scores.passion && scores.aptitude > scores.community) score += 10;
      return score;
    },
  },
  {
    id: 'RESEARCHER',
    label: 'The Researcher',
    tagline: 'Driven by curiosity and discovery',
    description: 'Research-focused with scientific interests',
    matchScore: (p, scores) => {
      let score = 0;
      // Research is key
      if (p.passion.research_level === 'NATIONAL') score += 50;
      else if (p.passion.research_level === 'STATE') score += 35;
      else if (p.passion.research_level === 'SCHOOL') score += 20;
      else if (p.passion.research_level === 'INDEPENDENT') score += 10;
      // STEM major bonus
      const stemMajors = ['Computer Science', 'Biology', 'Chemistry', 'Physics', 'Mathematics', 'Engineering'];
      if (stemMajors.includes(p.intended_major ?? '')) score += 15;
      // Academic foundation
      if (scores.aptitude >= 60) score += 15;
      return score;
    },
  },

  // Leadership Archetypes
  {
    id: 'LEADER',
    label: 'The Leader',
    tagline: 'Inspiring others to achieve together',
    description: 'Strong leadership with team impact',
    matchScore: (p, scores) => {
      let score = 0;
      // Leadership level
      if (p.passion.leadership_level?.includes('FOUNDER')) score += 40;
      else if (p.passion.leadership_level?.includes('PRES')) score += 35;
      else if (p.passion.leadership_level === 'OFFICER') score += 20;
      // High passion score
      if (scores.passion >= 60) score += 20;
      // Long commitment
      if ((p.passion.ec_commitment_years ?? 0) >= 3) score += 15;
      // Community involvement
      if (scores.community >= 50) score += 10;
      return score;
    },
  },
  {
    id: 'ENTREPRENEUR',
    label: 'The Entrepreneur',
    tagline: 'Creating solutions that matter',
    description: 'Founder mentality with startup energy',
    matchScore: (p, scores) => {
      let score = 0;
      // Founder is key
      if (p.passion.leadership_level?.includes('FOUNDER')) score += 45;
      // Project impact
      if ((p.passion.project_impact ?? 0) >= 500) score += 25;
      else if ((p.passion.project_impact ?? 0) >= 100) score += 15;
      // Business/CS/Econ interest
      const bizMajors = ['Business', 'Economics', 'Computer Science', 'Engineering'];
      if (bizMajors.includes(p.intended_major ?? '')) score += 15;
      // Passion dominant
      if (scores.passion > scores.aptitude) score += 10;
      return score;
    },
  },

  // Community/Service Archetypes
  {
    id: 'CHANGEMAKER',
    label: 'The Changemaker',
    tagline: 'Transforming communities through action',
    description: 'Service-oriented with measurable impact',
    matchScore: (p, scores) => {
      let score = 0;
      // Community is primary
      if (scores.community >= 60) score += 35;
      else if (scores.community >= 45) score += 20;
      // Service leadership
      if (p.community.service_leadership === 'NATIONAL') score += 25;
      else if (p.community.service_leadership === 'REGIONAL') score += 20;
      else if (p.community.service_leadership === 'LOCAL') score += 15;
      // High hours
      if ((p.community.service_hours ?? 0) >= 200) score += 15;
      // Impact
      if ((p.community.community_impact ?? 0) >= 100) score += 10;
      // Community is dominant
      if (scores.community > scores.aptitude && scores.community > scores.passion) score += 10;
      return score;
    },
  },
  {
    id: 'ADVOCATE',
    label: 'The Advocate',
    tagline: 'Voice for those who need one',
    description: 'Social justice focus with community engagement',
    matchScore: (p, scores) => {
      let score = 0;
      // Service involvement
      if ((p.community.service_hours ?? 0) >= 150) score += 25;
      // Community score
      if (scores.community >= 50) score += 20;
      // Social science majors
      const socialMajors = ['Political Science', 'Sociology', 'Psychology', 'Government', 'Public Policy'];
      if (socialMajors.includes(p.intended_major ?? '')) score += 20;
      // First-gen or underrepresented
      if (p.demographics.first_gen) score += 15;
      return score;
    },
  },

  // Passion/Spike Archetypes
  {
    id: 'CREATOR',
    label: 'The Creator',
    tagline: 'Building what others only imagine',
    description: 'Project-focused with tangible outputs',
    matchScore: (p, scores) => {
      let score = 0;
      // Project impact is key
      if ((p.passion.project_impact ?? 0) >= 200) score += 35;
      else if ((p.passion.project_impact ?? 0) >= 50) score += 20;
      // Long commitment to craft
      if ((p.passion.ec_commitment_years ?? 0) >= 4) score += 20;
      else if ((p.passion.ec_commitment_years ?? 0) >= 3) score += 10;
      // Creative/technical majors
      const creatorMajors = ['Computer Science', 'Engineering', 'Design', 'Architecture', 'Art'];
      if (creatorMajors.includes(p.intended_major ?? '')) score += 15;
      // Passion score
      if (scores.passion >= 50) score += 15;
      return score;
    },
  },
  {
    id: 'PERFORMER',
    label: 'The Performer',
    tagline: 'Excellence on every stage',
    description: 'Arts/athletics focus with competitive achievement',
    matchScore: (p, scores) => {
      let score = 0;
      // Recruited athlete
      if (p.demographics.recruited_athlete) score += 50;
      // Performance majors
      const perfMajors = ['Music', 'Theater', 'Dance', 'Film', 'Drama'];
      if (perfMajors.includes(p.intended_major ?? '')) score += 30;
      // EC awards (competition success)
      if ((p.passion.ec_awards_normalized ?? 0) >= 0.5) score += 20;
      // High passion
      if (scores.passion >= 55) score += 15;
      return score;
    },
  },

  // Balanced Archetypes
  {
    id: 'POLYMATH',
    label: 'The Polymath',
    tagline: 'Excellence without boundaries',
    description: 'Strong across multiple dimensions',
    matchScore: (_, scores) => {
      let score = 0;
      // All scores above 50
      const allAbove50 = scores.aptitude >= 50 && scores.passion >= 50 && scores.community >= 50;
      if (allAbove50) score += 40;
      // Balanced (no dimension more than 20 points higher than another)
      const max = Math.max(scores.aptitude, scores.passion, scores.community);
      const min = Math.min(scores.aptitude, scores.passion, scores.community);
      if (max - min <= 20) score += 25;
      // High overall
      const avg = (scores.aptitude + scores.passion + scores.community) / 3;
      if (avg >= 55) score += 20;
      return score;
    },
  },
  {
    id: 'EMERGING',
    label: 'The Emerging Talent',
    tagline: 'Potential waiting to be unlocked',
    description: 'Growing profile with clear trajectory',
    matchScore: (p, scores) => {
      let score = 0;
      // Younger grade (more time to grow)
      const grade = Number(p.identity?.grade ?? 12);
      if (grade <= 10) score += 25;
      else if (grade === 11) score += 15;
      // Some activity but room to grow
      if ((p.passion.ec_commitment_years ?? 0) >= 1) score += 15;
      // Moderate scores (not yet peaked)
      const avg = (scores.aptitude + scores.passion + scores.community) / 3;
      if (avg >= 30 && avg < 55) score += 20;
      // High grit (will improve)
      if ((p.assessment_intelligence?.psychometrics?.grit_resilience ?? 0) >= 0.6) score += 15;
      return score;
    },
  },

  // Fallback - should rarely be primary
  {
    id: 'EXPLORER',
    label: 'The Explorer',
    tagline: 'Finding your unique path',
    description: 'Discovering strengths and interests',
    matchScore: (p) => {
      let score = 20; // Base score so it's always an option
      // Major undeclared
      if (!p.intended_major || p.intended_major === 'Undeclared') score += 15;
      // Major certainty exploring
      if (p.major_certainty === 'EXPLORING') score += 15;
      return score;
    },
  },
];

// =============================================================================
// ARCHETYPE DETECTION
// =============================================================================

export interface ArchetypeResult {
  id: ArchetypeID;
  label: string;
  tagline: string;
  confidence: number;  // 0-100
  alternates: Array<{ id: ArchetypeID; label: string; confidence: number }>;
}

/**
 * Detect the best-matching archetype for a profile
 * UNIVERSAL: Always returns a valid archetype, never null or "GENERIC"
 */
export function detectArchetype(
  profile: StudentProfile,
  categoryScores: IvyReadyScore['category_scores']
): ArchetypeResult {
  // Score all archetypes
  const scored = ARCHETYPES.map(arch => ({
    ...arch,
    score: arch.matchScore(profile, categoryScores),
  }));

  // Sort by score descending
  scored.sort((a, b) => b.score - a.score);

  // Get top archetype
  const primary = scored[0];
  const maxScore = Math.max(...scored.map(s => s.score));

  // Calculate confidence (primary score as percentage of max possible)
  const confidence = Math.min(100, Math.round((primary.score / Math.max(maxScore, 1)) * 100));

  // Get alternates (next 2 with reasonable scores)
  const alternates = scored
    .slice(1, 3)
    .filter(s => s.score >= primary.score * 0.5)
    .map(s => ({
      id: s.id,
      label: s.label,
      confidence: Math.round((s.score / Math.max(primary.score, 1)) * 100),
    }));

  return {
    id: primary.id,
    label: primary.label,
    tagline: primary.tagline,
    confidence,
    alternates,
  };
}

/**
 * Get archetype by ID (for lookup)
 */
export function getArchetypeById(id: ArchetypeID): ArchetypeDefinition | undefined {
  return ARCHETYPES.find(a => a.id === id);
}
