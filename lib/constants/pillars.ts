/**
 * 4-Pillar Theme Constants
 * Used throughout assessment for consistent theming
 *
 * @version 1.0.0
 * @created January 22, 2026
 */

export const PILLARS = {
  identity: {
    id: 'identity',
    name: 'Identity',
    icon: 'fingerprint',
    color: '#9698A6',
    bgLight: '#DFE0E4',
    description: 'Who you REALLY are',
    frames: [4], // Primary collection in Frame 4
  },
  aptitude: {
    id: 'aptitude',
    name: 'Aptitude',
    icon: 'star',
    color: '#FFBB6D',
    bgLight: '#FFEBD3',
    description: 'What you\'re GOOD at',
    frames: [2], // Primary collection in Frame 2
  },
  passion: {
    id: 'passion',
    name: 'Passion',
    icon: 'heart',
    color: '#FF6E6D',
    bgLight: '#FFD4D3',
    description: 'What you LOVE',
    frames: [3], // Primary collection in Frame 3
  },
  service: {
    id: 'service',
    name: 'Service',
    icon: 'users',
    color: '#55AAAA',
    bgLight: '#CCE6E6',
    description: 'Who you SERVE',
    frames: [3], // Primary collection in Frame 3
  },
} as const;

export type PillarId = keyof typeof PILLARS;

/**
 * Map frames to their primary pillars
 */
export const FRAME_TO_PILLARS: Record<number, PillarId[]> = {
  1: [], // Warmup - no pillar
  2: ['aptitude'], // Academic
  3: ['passion', 'service'], // Extracurricular
  4: ['identity'], // Operating/Context
  5: [], // Reveal - all pillars
  6: [], // Power-Ups - all pillars
};

/**
 * Calculate pillar completion percentage based on profile data
 */
export function calculatePillarCompletion(
  pillarId: PillarId,
  profile: any // StudentProfile
): number {
  switch (pillarId) {
    case 'identity':
      return calculateIdentityCompletion(profile);
    case 'aptitude':
      return calculateAptitudeCompletion(profile);
    case 'passion':
      return calculatePassionCompletion(profile);
    case 'service':
      return calculateServiceCompletion(profile);
    default:
      return 0;
  }
}

function calculateIdentityCompletion(profile: any): number {
  let score = 0;
  const maxScore = 100;

  // Basic identity (20 points)
  if (profile.identity?.name) score += 10;
  if (profile.identity?.grade) score += 10;

  // Operating data (80 points)
  if (profile.operating?.gender) score += 10;
  if (profile.operating?.culturalBackground?.length > 0) score += 10;
  if (profile.operating?.firstGeneration !== undefined) score += 10;
  if (profile.operating?.parent1Occupation) score += 10;
  if (profile.operating?.workHours !== undefined) score += 10;
  if (profile.operating?.transportation) score += 10;
  if (profile.operating?.availableHoursPerWeek !== undefined) score += 10;
  if (profile.operating?.challengeOvercome) score += 10;

  return Math.min(100, (score / maxScore) * 100);
}

function calculateAptitudeCompletion(profile: any): number {
  let score = 0;
  const maxScore = 100;

  // GPA (30 points)
  if (profile.aptitude?.gpa_weighted || profile.aptitude?.gpa_unweighted) {
    score += 30;
  }

  // Tests (30 points)
  if (profile.aptitude?.sat_total || profile.aptitude?.act_total || profile.aptitude?.test_optional) {
    score += 30;
  }

  // Rigor (25 points)
  if (profile.aptitude?.ap_count !== null || profile.aptitude?.ib_diploma) {
    score += 25;
  }

  // Awards (15 points)
  if (profile.aptitude?.academic_awards?.length > 0) {
    score += 15;
  }

  return Math.min(100, (score / maxScore) * 100);
}

function calculatePassionCompletion(profile: any): number {
  let score = 0;
  const maxScore = 100;

  // Spike (20 points)
  if (profile.passion?.spike_category) score += 20;

  // Leadership (25 points)
  if (profile.passion?.leadership_level) score += 25;

  // Commitment (20 points)
  if (profile.passion?.ec_commitment_years && profile.passion?.ec_hours_weekly) {
    score += 20;
  }

  // Projects (20 points)
  if (profile.passion?.project_description || profile.passion?.project_impact) {
    score += 20;
  }

  // Research (15 points)
  if (profile.passion?.research_level && profile.passion.research_level !== 'NONE') {
    score += 15;
  }

  return Math.min(100, (score / maxScore) * 100);
}

function calculateServiceCompletion(profile: any): number {
  let score = 0;
  const maxScore = 100;

  // Service leadership (40 points)
  if (profile.community?.service_leadership) score += 40;

  // Hours (30 points)
  if (profile.community?.service_hours) score += 30;

  // Impact (30 points)
  if (profile.community?.community_impact) score += 30;

  return Math.min(100, (score / maxScore) * 100);
}

export default {
  PILLARS,
  FRAME_TO_PILLARS,
  calculatePillarCompletion,
};
