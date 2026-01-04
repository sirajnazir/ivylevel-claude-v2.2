/**
 * IvyQuest v3.0 — Frame 3: Operating Constants
 *
 * All constant definitions for Frame 3.
 * Includes scenarios, time bands, energy patterns, capabilities, and school insights.
 *
 * @version 1.0.0
 * @module lib/constants/frame3.constants
 */

// ============================================================================
// SCENARIO DEFINITIONS (Card 1)
// ============================================================================

export const SCENARIO_IDS = ['deadline_crunch', 'free_saturday', 'new_opportunity'] as const;
export type ScenarioId = typeof SCENARIO_IDS[number];

export type ScenarioResponse =
  | 'systematic' | 'adaptive'     // deadline_crunch
  | 'social' | 'solo'             // free_saturday
  | 'cautious' | 'bold';          // new_opportunity

export interface ScenarioOption {
  id: string;
  icon: string;
  label: string;
  description: string;
  traitSignal: string;
}

export interface Scenario {
  id: ScenarioId;
  title: string;
  prompt: string;
  optionA: ScenarioOption;
  optionB: ScenarioOption;
}

// Icons are now string identifiers - use SCENARIO_ICONS from lib/constants/icons.ts
export const SCENARIOS: Record<ScenarioId, Scenario> = {
  deadline_crunch: {
    id: 'deadline_crunch',
    title: 'System Overload',
    prompt: 'A major project fails the day before deadline. You have 24 hours. What\'s your move?',
    optionA: {
      id: 'systematic',
      icon: 'systematic',
      label: 'Systematic',
      description: 'Make a checklist, prioritize tasks, work through methodically',
      traitSignal: 'systematic_thinker',
    },
    optionB: {
      id: 'adaptive',
      icon: 'adaptive',
      label: 'Adaptive',
      description: 'Dive in and fix the biggest issue first, adapt as you go',
      traitSignal: 'adaptive_thinker',
    },
  },
  free_saturday: {
    id: 'free_saturday',
    title: 'Free Saturday',
    prompt: 'It\'s Saturday. No homework, no obligations. What sounds better?',
    optionA: {
      id: 'social',
      icon: 'social',
      label: 'Rally the Squad',
      description: 'Organize something with friends — hackathon, project jam, hangout',
      traitSignal: 'extrovert_energy',
    },
    optionB: {
      id: 'solo',
      icon: 'solo',
      label: 'Deep Dive',
      description: 'Finally work on that personal project you\'ve been thinking about',
      traitSignal: 'introvert_energy',
    },
  },
  new_opportunity: {
    id: 'new_opportunity',
    title: 'New Opportunity',
    prompt: 'A prestigious competition opens. Entry deadline is next week. You\'d be starting from scratch.',
    optionA: {
      id: 'cautious',
      icon: 'cautious',
      label: 'Strategic Pass',
      description: 'Focus on what I\'m already building — quality over quantity',
      traitSignal: 'cautious_strategic',
    },
    optionB: {
      id: 'bold',
      icon: 'bold',
      label: 'Go For It',
      description: 'Tight deadline? Challenge accepted. Let\'s see what I can do.',
      traitSignal: 'bold_opportunistic',
    },
  },
};

export const SCENARIO_RESPONSE_MAP: Record<ScenarioId, [string, string]> = {
  deadline_crunch: ['systematic', 'adaptive'],
  free_saturday: ['social', 'solo'],
  new_opportunity: ['cautious', 'bold'],
};

// ============================================================================
// OPERATING STYLES
// ============================================================================

export const OPERATING_STYLE_IDS = [
  'methodical_builder',
  'dynamic_leader',
  'organized_collaborator',
  'creative_innovator',
  'balanced_operator',
] as const;

export type OperatingStyle = typeof OPERATING_STYLE_IDS[number];

export interface OperatingStyleConfig {
  id: OperatingStyle;
  label: string;
  description: string;
  traits: string[];
  auraColor: string;
}

export const OPERATING_STYLES: Record<OperatingStyle, OperatingStyleConfig> = {
  methodical_builder: {
    id: 'methodical_builder',
    label: 'Methodical Builder',
    description: 'Systematic, focused, and strategic in approach',
    traits: ['systematic', 'solo', 'cautious'],
    auraColor: '#3B82F6', // Blue
  },
  dynamic_leader: {
    id: 'dynamic_leader',
    label: 'Dynamic Leader',
    description: 'Adaptive, social, and bold in execution',
    traits: ['adaptive', 'social', 'bold'],
    auraColor: '#F97316', // Orange
  },
  organized_collaborator: {
    id: 'organized_collaborator',
    label: 'Organized Collaborator',
    description: 'Systematic thinker who thrives in teams',
    traits: ['systematic', 'social'],
    auraColor: '#10B981', // Green
  },
  creative_innovator: {
    id: 'creative_innovator',
    label: 'Creative Innovator',
    description: 'Adaptive problem-solver who works independently',
    traits: ['adaptive', 'solo'],
    auraColor: '#8B5CF6', // Purple
  },
  balanced_operator: {
    id: 'balanced_operator',
    label: 'Balanced Operator',
    description: 'Versatile approach that adapts to context',
    traits: [],
    auraColor: '#06B6D4', // Cyan
  },
};

// ============================================================================
// TIME BANDS (Card 2)
// ============================================================================

export const TIME_BAND_IDS = ['minimal', 'light', 'moderate', 'substantial', 'extensive'] as const;
export type TimeBandId = typeof TIME_BAND_IDS[number];

export interface TimeBand {
  id: TimeBandId;
  label: string;
  range: [number, number];
  score: number;
  insight: string;
}

export const TIME_BANDS: Record<TimeBandId, TimeBand> = {
  minimal: {
    id: 'minimal',
    label: '<5 hrs',
    range: [0, 4],
    score: 0.20,
    insight: 'Very limited — we\'ll suggest high-impact, low-time options',
  },
  light: {
    id: 'light',
    label: '5-10 hrs',
    range: [5, 10],
    score: 0.40,
    insight: 'Moderate capacity — focus on 1-2 key initiatives',
  },
  moderate: {
    id: 'moderate',
    label: '10-15 hrs',
    range: [10, 15],
    score: 0.60,
    insight: 'Good availability — room for meaningful projects',
  },
  substantial: {
    id: 'substantial',
    label: '15-20 hrs',
    range: [15, 20],
    score: 0.80,
    insight: 'Strong capacity — competitive program candidate',
  },
  extensive: {
    id: 'extensive',
    label: '20+ hrs',
    range: [20, 40],
    score: 1.00,
    insight: 'Excellent availability — summer program ready',
  },
};

// ============================================================================
// PRODUCTIVITY OPTIONS (Card 2)
// ============================================================================

export const PRODUCTIVITY_IDS = ['early_bird', 'night_owl', 'flexible'] as const;
export type ProductivityId = typeof PRODUCTIVITY_IDS[number];

export interface ProductivityOption {
  id: ProductivityId;
  icon: string;
  label: string;
  description: string;
  insight: string;
}

// Icons are now string identifiers - use PRODUCTIVITY_ICONS from lib/constants/icons.ts
export const PRODUCTIVITY_OPTIONS: Record<ProductivityId, ProductivityOption> = {
  early_bird: {
    id: 'early_bird',
    icon: 'early_bird',
    label: 'Early Bird',
    description: 'Best before noon',
    insight: 'Morning programs, early deadlines work well for you',
  },
  night_owl: {
    id: 'night_owl',
    icon: 'night_owl',
    label: 'Night Owl',
    description: 'After 8pm is my time',
    insight: 'Self-paced programs give you flexibility',
  },
  flexible: {
    id: 'flexible',
    icon: 'flexible',
    label: 'Flexible',
    description: 'Depends on the day',
    insight: 'You can adapt to any program schedule',
  },
};

// ============================================================================
// ENERGY SPECTRUM (Card 2)
// ============================================================================

export const ENERGY_PATTERN_IDS = [
  'highly_collaborative',
  'team_oriented',
  'balanced',
  'independent_thinker',
  'deep_focus',
] as const;

export type EnergyPattern = typeof ENERGY_PATTERN_IDS[number];

export interface EnergySpectrumConfig {
  min: {
    label: string;
    icon: string;
    description: string;
  };
  max: {
    label: string;
    icon: string;
    description: string;
  };
  positions: Array<{
    value: number;
    label: string;
    pattern: EnergyPattern;
  }>;
}

// Icons are now string identifiers - use ENERGY_ICONS from lib/constants/icons.ts
export const ENERGY_SPECTRUM: EnergySpectrumConfig = {
  min: {
    label: 'People',
    icon: 'people',
    description: 'Working with others',
  },
  max: {
    label: 'Ideas',
    icon: 'ideas',
    description: 'Working on problems',
  },
  positions: [
    { value: 0.0, label: 'Strongly People', pattern: 'highly_collaborative' },
    { value: 0.25, label: 'Mostly People', pattern: 'team_oriented' },
    { value: 0.5, label: 'Both Equally', pattern: 'balanced' },
    { value: 0.75, label: 'Mostly Ideas', pattern: 'independent_thinker' },
    { value: 1.0, label: 'Strongly Ideas', pattern: 'deep_focus' },
  ],
};

export const ENERGY_PATTERN_THRESHOLDS: Record<EnergyPattern, [number, number]> = {
  highly_collaborative: [0, 0.15],
  team_oriented: [0.15, 0.40],
  balanced: [0.40, 0.60],
  independent_thinker: [0.60, 0.85],
  deep_focus: [0.85, 1.0],
};

// ============================================================================
// HIDDEN CAPABILITIES (Card 3)
// ============================================================================

export const HIDDEN_CAPABILITY_IDS = [
  'writing',
  'public_speaking',
  'creative_design',
  'technical_build',
  'networking',
  'data_analysis',
  'strategic_planning',
  'idea_generation',
] as const;

export type HiddenCapability = typeof HIDDEN_CAPABILITY_IDS[number];

export interface HiddenCapabilityConfig {
  id: HiddenCapability;
  icon: string;
  label: string;
  description: string;
  boosterAffinity: string[];
}

// Icons are now string identifiers - use CAPABILITY_ICONS from lib/constants/icons.ts
export const HIDDEN_CAPABILITIES: Record<HiddenCapability, HiddenCapabilityConfig> = {
  writing: {
    id: 'writing',
    icon: 'writing',
    label: 'Writing',
    description: 'Essays, articles, storytelling',
    boosterAffinity: ['essay_coaching', 'journalism_programs'],
  },
  public_speaking: {
    id: 'public_speaking',
    icon: 'public_speaking',
    label: 'Public Speaking',
    description: 'Presentations, debates, pitches',
    boosterAffinity: ['debate_programs', 'ted_talks', 'model_un'],
  },
  creative_design: {
    id: 'creative_design',
    icon: 'creative_design',
    label: 'Creative Design',
    description: 'Visual arts, graphic design',
    boosterAffinity: ['portfolio_programs', 'design_competitions'],
  },
  technical_build: {
    id: 'technical_build',
    icon: 'technical_build',
    label: 'Technical Build',
    description: 'Coding, hardware, engineering',
    boosterAffinity: ['hackathons', 'robotics', 'research_programs'],
  },
  networking: {
    id: 'networking',
    icon: 'networking',
    label: 'Networking',
    description: 'Building relationships, connecting people',
    boosterAffinity: ['summer_programs', 'mentorship', 'internships'],
  },
  data_analysis: {
    id: 'data_analysis',
    icon: 'data_analysis',
    label: 'Data Analysis',
    description: 'Research, stats, quantitative work',
    boosterAffinity: ['research_programs', 'competitions', 'olympiads'],
  },
  strategic_planning: {
    id: 'strategic_planning',
    icon: 'strategic_planning',
    label: 'Strategic Planning',
    description: 'Long-term vision, goal-setting',
    boosterAffinity: ['entrepreneurship', 'leadership_programs'],
  },
  idea_generation: {
    id: 'idea_generation',
    icon: 'idea_generation',
    label: 'Idea Generation',
    description: 'Brainstorming, innovation',
    boosterAffinity: ['innovation_programs', 'entrepreneurship', 'startups'],
  },
};

// ============================================================================
// STRENGTH PROFILES (Card 3)
// ============================================================================

export const STRENGTH_PROFILE_IDS = [
  'technical_specialist',
  'creative_innovator',
  'social_leader',
  'versatile_generalist',
] as const;

export type StrengthProfile = typeof STRENGTH_PROFILE_IDS[number];

export interface StrengthProfileConfig {
  id: StrengthProfile;
  label: string;
  description: string;
  indicatorCapabilities: HiddenCapability[];
}

export const STRENGTH_PROFILES: Record<StrengthProfile, StrengthProfileConfig> = {
  technical_specialist: {
    id: 'technical_specialist',
    label: 'Technical Specialist',
    description: 'Deep expertise in technical domains',
    indicatorCapabilities: ['technical_build', 'data_analysis'],
  },
  creative_innovator: {
    id: 'creative_innovator',
    label: 'Creative Innovator',
    description: 'Imagination-driven problem solving',
    indicatorCapabilities: ['creative_design', 'writing', 'idea_generation'],
  },
  social_leader: {
    id: 'social_leader',
    label: 'Social Leader',
    description: 'People-centered influence and connection',
    indicatorCapabilities: ['public_speaking', 'networking'],
  },
  versatile_generalist: {
    id: 'versatile_generalist',
    label: 'Versatile Generalist',
    description: 'Broad skillset across multiple domains',
    indicatorCapabilities: [],
  },
};

// ============================================================================
// AURA CONFIGURATION
// ============================================================================

export interface AuraConfig {
  colors: Record<OperatingStyle, string>;
  intensityStages: {
    card1Complete: [number, number]; // min, max
    card2Complete: [number, number];
    card3Complete: [number, number];
  };
  pulseSpeed: Record<EnergyPattern, 'slow' | 'medium' | 'fast' | 'brilliant'>;
  glowRadius: Record<number, number>; // intensity -> radius
}

export const AURA_CONFIG: AuraConfig = {
  colors: {
    methodical_builder: '#3B82F6',
    dynamic_leader: '#F97316',
    organized_collaborator: '#10B981',
    creative_innovator: '#8B5CF6',
    balanced_operator: '#06B6D4',
  },
  intensityStages: {
    card1Complete: [25, 40],
    card2Complete: [50, 75],
    card3Complete: [75, 100],
  },
  pulseSpeed: {
    highly_collaborative: 'brilliant',
    team_oriented: 'fast',
    balanced: 'medium',
    independent_thinker: 'medium',
    deep_focus: 'slow',
  },
  glowRadius: {
    25: 20,
    50: 35,
    75: 50,
    100: 70,
  },
};

// ============================================================================
// SCHOOL-SPECIFIC PREFERENCES
// ============================================================================

export interface SchoolPsychometricPreference {
  preferredStyle: OperatingStyle;
  energyPattern: EnergyPattern;
  insight: string;
}

export const SCHOOL_PSYCHOMETRIC_PREFERENCES: Record<string, SchoolPsychometricPreference> = {
  MIT: {
    preferredStyle: 'methodical_builder',
    energyPattern: 'deep_focus',
    insight: 'MIT values systematic problem-solvers who can dive deep',
  },
  STANFORD: {
    preferredStyle: 'creative_innovator',
    energyPattern: 'balanced',
    insight: 'Stanford loves bold thinkers who can collaborate and iterate',
  },
  HARVARD: {
    preferredStyle: 'dynamic_leader',
    energyPattern: 'team_oriented',
    insight: 'Harvard seeks leaders who energize others and drive change',
  },
  YALE: {
    preferredStyle: 'organized_collaborator',
    energyPattern: 'highly_collaborative',
    insight: 'Yale values community-minded students with strong interpersonal skills',
  },
  PRINCETON: {
    preferredStyle: 'methodical_builder',
    energyPattern: 'independent_thinker',
    insight: 'Princeton appreciates focused, independent scholars',
  },
  CALTECH: {
    preferredStyle: 'methodical_builder',
    energyPattern: 'deep_focus',
    insight: 'Caltech seeks intensely focused technical minds',
  },
  COLUMBIA: {
    preferredStyle: 'dynamic_leader',
    energyPattern: 'balanced',
    insight: 'Columbia values intellectually curious urban leaders',
  },
  PENN: {
    preferredStyle: 'organized_collaborator',
    energyPattern: 'team_oriented',
    insight: 'Penn appreciates collaborative, business-minded thinkers',
  },
  BROWN: {
    preferredStyle: 'creative_innovator',
    energyPattern: 'balanced',
    insight: 'Brown celebrates unconventional, self-directed learners',
  },
  DUKE: {
    preferredStyle: 'dynamic_leader',
    energyPattern: 'team_oriented',
    insight: 'Duke values spirited leaders with collaborative energy',
  },
  NORTHWESTERN: {
    preferredStyle: 'organized_collaborator',
    energyPattern: 'team_oriented',
    insight: 'Northwestern seeks creative collaborators across disciplines',
  },
  UCHICAGO: {
    preferredStyle: 'methodical_builder',
    energyPattern: 'independent_thinker',
    insight: 'UChicago prizes rigorous, independent intellectual inquiry',
  },
};

// ============================================================================
// VALIDATION RULES
// ============================================================================

export const VALIDATION_RULES = {
  card1: {
    minScenariosAnswered: 2,
    totalScenarios: 3,
  },
  card2: {
    requiredFields: ['weeklyAvailableHours', 'peakProductivity', 'energySource'] as const,
    energySourceDefault: 0.5,
  },
  card3: {
    minCapabilities: 1,
    maxCapabilities: 3,
  },
};

// ============================================================================
// READINESS SCORE WEIGHTS
// ============================================================================

export const READINESS_WEIGHTS = {
  timeCapacity: 40,        // 40% weight
  operatingClarity: {
    defined: 30,           // 30% for non-balanced
    balanced: 20,          // 20% for balanced
  },
  strengthsPerCapability: 10, // 10% per capability (max 30%)
};

// ============================================================================
// IVY COMPANION MESSAGES
// ============================================================================

export const IVY_MESSAGES = {
  card1: {
    intro: "Quick scenarios to understand how you operate. No right answers — just YOU.",
    complete: "Operating style detected! Let's look at your capacity.",
  },
  card2: {
    intro: "Understanding your capacity helps us recommend programs you can actually complete.",
    complete: "Got your energy pattern! One more card to go.",
  },
  card3: {
    intro: "Select 1-3 strengths you have but haven't fully developed or showcased yet.",
    complete: "System calibration complete! Your twin is ready.",
  },
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  SCENARIOS,
  SCENARIO_IDS,
  SCENARIO_RESPONSE_MAP,
  OPERATING_STYLES,
  OPERATING_STYLE_IDS,
  TIME_BANDS,
  TIME_BAND_IDS,
  PRODUCTIVITY_OPTIONS,
  PRODUCTIVITY_IDS,
  ENERGY_SPECTRUM,
  ENERGY_PATTERN_IDS,
  ENERGY_PATTERN_THRESHOLDS,
  HIDDEN_CAPABILITIES,
  HIDDEN_CAPABILITY_IDS,
  STRENGTH_PROFILES,
  STRENGTH_PROFILE_IDS,
  AURA_CONFIG,
  SCHOOL_PSYCHOMETRIC_PREFERENCES,
  VALIDATION_RULES,
  READINESS_WEIGHTS,
  IVY_MESSAGES,
};
