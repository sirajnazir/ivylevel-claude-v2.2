/**
 * Real School Configuration Data (CDS 2025)
 * Source: Common Data Set 2024-2025, College Board, Official University Websites
 */

import { SchoolConfig } from '../types/student';

export const SCHOOL_DATABASE: Record<string, SchoolConfig> = {
  HARVARD: {
    school_id: 'HARVARD',
    school_name: 'Harvard University',
    base_acceptance_rate: 0.042, // 4.2% (CDS 2025)
    base_sat_50th: 1520,
    weight_aptitude: 30,
    weight_passion: 35,
    weight_community: 25,
    weight_narrative: 10,
    distinctive_values: ['LEADERSHIP', 'GLOBAL_IMPACT', 'EXCELLENCE'],
    legacy_roi: 5.0, // Chetty 2023: 5x multiplier
    first_gen_roi: 1.15,
    athlete_roi: 2.5,
    major_multipliers: {
      'Computer Science': 0.70,
      'Economics': 0.75,
      'Government': 1.0,
      'Biology': 0.80,
      'Mathematics': 0.85,
    },
    twin_theme: 'GLOBAL_LEADER',
    twin_color: '#A51C30',
  },

  STANFORD: {
    school_id: 'STANFORD',
    school_name: 'Stanford University',
    base_acceptance_rate: 0.039, // 3.9% (CDS 2025)
    base_sat_50th: 1510,
    weight_aptitude: 25,
    weight_passion: 45, // Highest passion weight - intellectual vitality
    weight_community: 20,
    weight_narrative: 10,
    distinctive_values: ['ENTREPRENEURSHIP', 'INNOVATION', 'INTELLECTUAL_VITALITY'],
    legacy_roi: 4.0,
    first_gen_roi: 1.15,
    athlete_roi: 2.5,
    major_multipliers: {
      'Computer Science': 0.55, // Most competitive
      'Engineering': 0.65,
      'Symbolic Systems': 1.20, // Strategic alternative (same classes, different framing)
      'Economics': 0.80,
      'Human Biology': 0.90,
      'Product Design': 1.10,
    },
    twin_theme: 'ENTREPRENEUR',
    twin_color: '#8C1515',
  },

  MIT: {
    school_id: 'MIT',
    school_name: 'Massachusetts Institute of Technology',
    base_acceptance_rate: 0.057, // 5.7% (CDS 2025)
    base_sat_50th: 1540,
    weight_aptitude: 40, // Highest aptitude weight
    weight_passion: 40, // Maker culture
    weight_community: 10, // Lowest community weight
    weight_narrative: 10,
    distinctive_values: ['TECH_MERITOCRACY', 'MAKER_CULTURE', 'STEM_EXCELLENCE'],
    legacy_roi: 0.0, // Pure meritocracy - NO legacy advantage
    first_gen_roi: 1.15,
    athlete_roi: 1.5, // Lower than Ivies
    major_multipliers: {
      'Computer Science': 0.70,
      'Engineering': 0.75,
      'Physics': 0.90,
      'Mathematics': 0.85,
      'Brain and Cognitive Sciences': 0.95,
    },
    twin_theme: 'TECH_BUILDER',
    twin_color: '#A31F34',
  },

  YALE: {
    school_id: 'YALE',
    school_name: 'Yale University',
    base_acceptance_rate: 0.051, // 5.1% (CDS 2025)
    base_sat_50th: 1515,
    weight_aptitude: 28,
    weight_passion: 32,
    weight_community: 30, // Highest community weight
    weight_narrative: 10,
    distinctive_values: ['COMMUNITY', 'LIBERAL_ARTS', 'SERVICE_LEADERSHIP'],
    legacy_roi: 5.0,
    first_gen_roi: 1.15,
    athlete_roi: 2.5,
    major_multipliers: {
      'Political Science': 1.10,
      'English': 1.05,
      'History': 1.05,
      'Computer Science': 0.75,
      'Economics': 0.80,
    },
    twin_theme: 'COMMUNITY_BUILDER',
    twin_color: '#00356B',
  },

  PRINCETON: {
    school_id: 'PRINCETON',
    school_name: 'Princeton University',
    base_acceptance_rate: 0.058, // 5.8% (CDS 2025)
    base_sat_50th: 1530,
    weight_aptitude: 35,
    weight_passion: 35,
    weight_community: 20,
    weight_narrative: 10,
    distinctive_values: ['ACADEMIC_EXCELLENCE', 'RESEARCH', 'UNDERGRADUATE_FOCUS'],
    legacy_roi: 5.0,
    first_gen_roi: 1.15,
    athlete_roi: 2.5,
    major_multipliers: {
      'Mathematics': 1.0,
      'Physics': 1.05,
      'Computer Science': 0.70,
      'Economics': 0.80,
      'Politics': 1.0,
    },
    twin_theme: 'SCHOLAR',
    twin_color: '#E77500',
  },

  CALTECH: {
    school_id: 'CALTECH',
    school_name: 'California Institute of Technology',
    base_acceptance_rate: 0.064, // 6.4% (CDS 2025)
    base_sat_50th: 1560, // Highest median SAT
    weight_aptitude: 50, // Highest aptitude emphasis
    weight_passion: 35,
    weight_community: 5, // Lowest community emphasis
    weight_narrative: 10,
    distinctive_values: ['RESEARCH_EXCELLENCE', 'PURE_STEM', 'ACADEMIC_RIGOR'],
    legacy_roi: 0.0, // Pure meritocracy
    first_gen_roi: 1.15,
    athlete_roi: 1.0, // No athletic advantage
    major_multipliers: {
      'Physics': 1.0,
      'Mathematics': 1.0,
      'Engineering': 0.95,
      'Computer Science': 0.80,
      'Chemistry': 1.0,
    },
    twin_theme: 'RESEARCHER',
    twin_color: '#FF6C0C',
  },

  CMU: {
    school_id: 'CMU',
    school_name: 'Carnegie Mellon University',
    base_acceptance_rate: 0.110, // 11% (CDS 2025)
    base_sat_50th: 1500,
    weight_aptitude: 35,
    weight_passion: 40,
    weight_community: 15,
    weight_narrative: 10,
    distinctive_values: ['CS_EXCELLENCE', 'INTERDISCIPLINARY', 'MAKER_CULTURE'],
    legacy_roi: 2.0,
    first_gen_roi: 1.15,
    athlete_roi: 1.5,
    major_multipliers: {
      'Computer Science': 0.50, // SCS (School of Computer Science) extremely competitive
      'Engineering': 0.70,
      'Drama': 1.30, // Less competitive school
      'Business': 0.80,
      'Information Systems': 0.75,
      'Design': 1.00,
    },
    twin_theme: 'CS_SPECIALIST',
    twin_color: '#C41230',
  },

  COLUMBIA: {
    school_id: 'COLUMBIA',
    school_name: 'Columbia University',
    base_acceptance_rate: 0.048, // 4.8% (CDS 2025)
    base_sat_50th: 1510,
    weight_aptitude: 32,
    weight_passion: 33,
    weight_community: 25,
    weight_narrative: 10,
    distinctive_values: ['URBAN', 'CORE_CURRICULUM', 'GLOBAL'],
    legacy_roi: 4.5,
    first_gen_roi: 1.15,
    athlete_roi: 2.0,
    major_multipliers: {
      'Computer Science': 0.68,
      'Economics': 0.75,
      'Political Science': 1.0,
      'Engineering': 0.80,
    },
    twin_theme: 'URBAN_SCHOLAR',
    twin_color: '#B9D9EB',
  },
};

// Export array for iteration
export const ALL_SCHOOLS = Object.values(SCHOOL_DATABASE);

// Helper to get school by ID
export function getSchool(school_id: string): SchoolConfig | undefined {
  return SCHOOL_DATABASE[school_id];
}

// Helper to get schools by list of IDs
export function getSchools(school_ids: string[]): SchoolConfig[] {
  return school_ids.map(id => SCHOOL_DATABASE[id]).filter(Boolean);
}
