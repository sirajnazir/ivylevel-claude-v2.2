/**
 * Assessment Extractor - DIAGNOSIS Phase
 *
 * Extracts RAW narrative components from student profile.
 * This is DIAGNOSIS - just collecting facts, no synthesis.
 * The Game Plan Agent will SYNTHESIZE these into the Master Narrative.
 *
 * Flow:
 * Assessment (Frontend) → This Extractor → Raw Components → Game Plan Agent
 *
 * Key Principle:
 * Assessment EXTRACTS and SCORES, it does NOT create the narrative.
 * The narrative synthesis belongs to the PRESCRIPTION phase (Game Plan Agent).
 */

import type {
  StudentProfile,
  RawIdentityData,
  RawAptitudeData,
  RawPassionData,
  RawServiceData,
  AssessmentExtraction,
  ArchetypeID,
  IncomeBand,
} from '../types/student';

// =============================================================================
// IDENTITY EXTRACTION
// =============================================================================

/**
 * Extract raw identity data from profile
 * Just facts - no interpretation, no synthesis
 */
export function extractRawIdentity(profile: StudentProfile): RawIdentityData {
  const selfDescribed: string[] = [];

  // Extract self-description keywords from free text
  const freeText = [
    profile.passion?.brag_text,
    profile.passion?.leadership_description,
    profile.passion?.project_description,
    profile.passion?.research_description,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  // Look for identity-related keywords in free text
  const identityKeywords = [
    'quiet',
    'introverted',
    'shy',
    'outgoing',
    'leader',
    'builder',
    'creator',
    'helper',
    'advocate',
    'first-gen',
    'immigrant',
    'minority',
    'underrepresented',
    'eldest',
    'caregiver',
  ];

  for (const kw of identityKeywords) {
    if (freeText.includes(kw) && !selfDescribed.includes(kw)) {
      selfDescribed.push(kw);
    }
  }

  return {
    ethnicity: profile.demographics?.ethnicity || null,
    religion: null, // Would come from extended assessment questions
    first_gen: profile.demographics?.first_gen || false,
    family_structure: extractFamilyStructure(profile),
    geographic_origin: mapRegionToOrigin(profile.high_school?.region),
    socioeconomic: inferSocioeconomic(profile.demographics?.income_band),
    introversion_score:
      profile.assessment_intelligence?.psychometrics?.introversion_extroversion ?? null,
    self_described_identity: selfDescribed,
  };
}

/**
 * Extract family structure hints from profile
 */
function extractFamilyStructure(profile: StudentProfile): string[] {
  const structure: string[] = [];

  // From operating data if available
  if (profile.operating?.familyResponsibilities) {
    const resp = profile.operating.familyResponsibilities.toLowerCase();
    if (resp.includes('caregiver') || resp.includes('care for')) {
      structure.push('caregiver');
    }
    if (resp.includes('sibling') || resp.includes('brother') || resp.includes('sister')) {
      structure.push('sibling caretaker');
    }
  }

  // From family context
  if (profile.assessment_intelligence?.family_context?.family_challenges) {
    const challenges = profile.assessment_intelligence.family_context.family_challenges.toLowerCase();
    if (challenges.includes('single parent')) {
      structure.push('single parent household');
    }
  }

  return structure;
}

/**
 * Map region enum to origin description
 */
function mapRegionToOrigin(region: string | undefined): string | null {
  if (!region) return null;

  const originMap: Record<string, string> = {
    INTERNATIONAL: 'international',
    BAY_AREA: 'Bay Area',
    NORTHEAST: 'Northeast',
    SOUTH: 'South',
    MIDWEST: 'Midwest',
    SOUTHWEST: 'Southwest',
    NORTHWEST: 'Northwest',
    OTHER: null,
  };

  return originMap[region] ?? null;
}

/**
 * Infer socioeconomic status from income band
 */
function inferSocioeconomic(incomeBand: IncomeBand | undefined): string | null {
  if (!incomeBand) return null;

  const socioMap: Record<string, string> = {
    BELOW_75K: 'working class',
    '75K_150K': 'middle class',
    '150K_300K': 'upper middle class',
    ABOVE_300K: 'affluent',
    TOP_1_PERCENT: 'top 1%',
    PREFER_NOT_SAY: null,
  };

  return socioMap[incomeBand] ?? null;
}

// =============================================================================
// APTITUDE EXTRACTION
// =============================================================================

/**
 * Extract raw aptitude data from profile
 */
export function extractRawAptitude(profile: StudentProfile): RawAptitudeData {
  const mentionedSkills: string[] = [];

  // Extract skills from major
  const major = profile.intended_major?.toLowerCase() || '';
  const majorSkillMap: Record<string, string[]> = {
    computer: ['coding', 'technology'],
    cs: ['coding', 'technology'],
    software: ['coding', 'engineering'],
    bio: ['research', 'science'],
    engineer: ['engineering', 'problem-solving'],
    business: ['entrepreneurship', 'leadership'],
    medicine: ['research', 'healthcare'],
    law: ['writing', 'analysis'],
    art: ['creativity', 'design'],
    music: ['performance', 'creativity'],
    psychology: ['research', 'communication'],
    economics: ['analysis', 'quantitative'],
    math: ['quantitative', 'analysis'],
    physics: ['research', 'quantitative'],
    chemistry: ['research', 'science'],
  };

  for (const [keyword, skills] of Object.entries(majorSkillMap)) {
    if (major.includes(keyword)) {
      mentionedSkills.push(...skills);
    }
  }

  // Extract from brag text
  const brag = profile.passion?.brag_text?.toLowerCase() || '';
  const textSkillMap: Record<string, string[]> = {
    code: ['coding'],
    program: ['coding'],
    research: ['research'],
    led: ['leadership'],
    founded: ['leadership', 'entrepreneurship'],
    built: ['building', 'engineering'],
    design: ['design', 'creativity'],
    wrote: ['writing'],
    published: ['research', 'writing'],
    taught: ['teaching', 'communication'],
    organized: ['leadership', 'organization'],
  };

  for (const [keyword, skills] of Object.entries(textSkillMap)) {
    if (brag.includes(keyword)) {
      mentionedSkills.push(...skills);
    }
  }

  // Deduplicate
  const uniqueSkills = Array.from(new Set(mentionedSkills));

  return {
    gpa_weighted: profile.aptitude?.gpa_weighted ?? null,
    gpa_unweighted: profile.aptitude?.gpa_unweighted ?? null,
    sat_total: profile.aptitude?.sat_total ?? null,
    ap_count: profile.aptitude?.ap_count ?? 0,
    rigor_level: inferRigorLevel(profile.aptitude?.rigor_normalized),
    academic_awards: profile.aptitude?.academic_awards || [],
    competitions_entered: [], // Would come from extended assessment
    intended_major: profile.intended_major || null,
    mentioned_skills: uniqueSkills,
  };
}

/**
 * Infer rigor level from normalized score
 */
function inferRigorLevel(
  rigorNormalized: number | null | undefined
): 'LOW' | 'MEDIUM' | 'HIGH' | 'MAXIMUM' {
  if (rigorNormalized === null || rigorNormalized === undefined) return 'MEDIUM';
  if (rigorNormalized >= 0.9) return 'MAXIMUM';
  if (rigorNormalized >= 0.7) return 'HIGH';
  if (rigorNormalized >= 0.4) return 'MEDIUM';
  return 'LOW';
}

// =============================================================================
// PASSION EXTRACTION
// =============================================================================

/**
 * Extract raw passion data from profile
 * Game Plan Agent will find "first principles" passion from this
 */
export function extractRawPassion(profile: StudentProfile): RawPassionData {
  const passionKeywords: string[] = [];

  // Extract from all free text
  const allText = [
    profile.passion?.brag_text,
    profile.passion?.leadership_description,
    profile.passion?.project_description,
    profile.passion?.research_description,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  // Passion-related keywords that indicate first principles
  const keywords = [
    // BUILDER signals
    'game',
    'build',
    'create',
    'make',
    'develop',
    'code',
    'program',
    'design',
    'construct',
    'app',
    'website',
    'robot',
    // STORYTELLER signals
    'film',
    'story',
    'write',
    'narrative',
    'video',
    'media',
    'communicate',
    'journalism',
    'blog',
    // DISCOVERER signals
    'research',
    'discover',
    'explore',
    'investigate',
    'study',
    'analyze',
    'experiment',
    'lab',
    // ADVOCATE signals
    'advocate',
    'fight',
    'change',
    'justice',
    'rights',
    'speak',
    'voice',
    'protest',
    'policy',
    // CONNECTOR signals
    'connect',
    'community',
    'network',
    'unite',
    'bridge',
    'bring together',
    // HEALER signals
    'help',
    'care',
    'heal',
    'support',
    'nurture',
    'comfort',
    'patient',
    'medical',
    // LEADER signals
    'lead',
    'organize',
    'direct',
    'manage',
    'inspire',
    'guide',
    'president',
    'captain',
    'founded',
    // ARTIST signals
    'art',
    'music',
    'perform',
    'express',
    'creative',
    'aesthetic',
    'paint',
    'dance',
    'theater',
    // ENTREPRENEUR signals
    'start',
    'launch',
    'business',
    'venture',
    'innovate',
    'startup',
    'company',
    // SCHOLAR signals
    'learn',
    'academic',
    'intellectual',
    'knowledge',
    'curious',
    'philosophy',
    'theory',
  ];

  for (const kw of keywords) {
    if (allText.includes(kw) && !passionKeywords.includes(kw)) {
      passionKeywords.push(kw);
    }
  }

  // Extract projects from NLP extraction if available
  const projects: RawPassionData['projects'] = [];
  if (profile.passion?.brag_nlp_extracted?.projects) {
    for (const p of profile.passion.brag_nlp_extracted.projects) {
      projects.push({
        name: p.name || 'Project',
        description: p.description || '',
        impact_count: p.impact_count || null,
      });
    }
  }

  // Add project from description if exists
  if (profile.passion?.project_description) {
    projects.push({
      name: 'Main Project',
      description: profile.passion.project_description,
      impact_count: profile.passion?.project_impact || null,
    });
  }

  return {
    spike_category: profile.passion?.spike_category || null,
    spike_description: profile.passion?.leadership_description || null,
    brag_text: profile.passion?.brag_text || null,
    activities: [], // Would come from structured activity input
    projects,
    passion_keywords: passionKeywords,
  };
}

// =============================================================================
// SERVICE EXTRACTION
// =============================================================================

/**
 * Extract raw service data from profile
 */
export function extractRawService(profile: StudentProfile): RawServiceData {
  const communitiesServed: string[] = [];

  // Infer communities from service description
  const desc = profile.community?.service_description?.toLowerCase() || '';

  const communityKeywords: Record<string, string> = {
    underrepresented: 'underrepresented communities',
    minority: 'minority communities',
    youth: 'youth/students',
    kids: 'youth/students',
    student: 'youth/students',
    immigrant: 'immigrant communities',
    women: 'women/girls',
    girl: 'women/girls',
    elderly: 'elderly',
    senior: 'elderly',
    homeless: 'homeless/housing insecure',
    hunger: 'food insecure',
    food: 'food insecure',
    environment: 'environmental causes',
    climate: 'environmental causes',
    health: 'health/medical',
    mental: 'mental health',
    education: 'education access',
    literacy: 'education access',
    veterans: 'veterans',
    disability: 'disability community',
    lgbtq: 'LGBTQ+ community',
    refugee: 'refugees/asylum seekers',
  };

  for (const [keyword, community] of Object.entries(communityKeywords)) {
    if (desc.includes(keyword) && !communitiesServed.includes(community)) {
      communitiesServed.push(community);
    }
  }

  // Also check identity for service connection
  if (profile.demographics?.ethnicity) {
    const ethnicity = profile.demographics.ethnicity.toLowerCase();
    if (['asian', 'black', 'hispanic', 'native'].includes(ethnicity)) {
      communitiesServed.push(`${ethnicity} community`);
    }
  }

  if (profile.demographics?.first_gen) {
    communitiesServed.push('first-generation students');
  }

  return {
    service_hours: profile.community?.service_hours || 0,
    service_leadership: profile.community?.service_leadership || null,
    service_description: profile.community?.service_description || null,
    service_cause: null, // Would come from structured input
    communities_served: Array.from(new Set(communitiesServed)), // Dedupe
  };
}

// =============================================================================
// MAIN EXTRACTION FUNCTION
// =============================================================================

/**
 * Complete assessment extraction
 * This is the DIAGNOSIS output that gets passed to Game Plan Agent
 *
 * @param profile - Student profile from assessment
 * @param scores - Calculated rubric scores
 * @param gaps - Identified gaps with priorities
 * @param archetype - Detected archetype
 * @returns AssessmentExtraction for Game Plan Agent to synthesize
 */
export function extractForGamePlan(
  profile: StudentProfile,
  scores: { aptitude: number; passion: number; community: number; overall: number },
  gaps: Array<{
    area: string;
    current: number;
    target: number;
    priority: 'P0' | 'P1' | 'P2';
    description: string;
  }>,
  archetype: { id: ArchetypeID; confidence: number }
): AssessmentExtraction {
  return {
    scores,
    gaps,
    raw_identity: extractRawIdentity(profile),
    raw_aptitude: extractRawAptitude(profile),
    raw_passion: extractRawPassion(profile),
    raw_service: extractRawService(profile),
    archetype: archetype.id,
    archetype_confidence: archetype.confidence,
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export const assessmentExtractor = {
  extractRawIdentity,
  extractRawAptitude,
  extractRawPassion,
  extractRawService,
  extractForGamePlan,
};

export default assessmentExtractor;
