/**
 * Student Profile Store (Zustand)
 * Manages the student profile state across all frames
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type {
  StudentProfile,
  StudentIdentity,
  AptitudeAttributes,
  PassionAttributes,
  CommunityAttributes,
  HighSchoolContext,
  DemographicContext,
  MajorContext,
  AssessmentIntelligence,
  Grade,
  Role,
  MajorCertainty,
  SpikeCategory,
  LeadershipLevel,
  ResearchLevel,
  ServiceLeadership,
  SaturationLevel,
  Ethnicity,
  IncomeBand,
  HSType,
  Region,
  ParentArchetype,
  CoachabilityLevel,
  BurnoutRisk,
  // Frame 4 Operating types
  OperatingData,
  ProfileCompleteness,
  ProfileClassification,
} from '../types/student';

// Default empty profile
const createEmptyProfile = (): StudentProfile => ({
  session_id: crypto.randomUUID(),
  timestamp: new Date().toISOString(),
  identity: {
    role: 'STUDENT',
    name: '',
    grade: 11,
  },
  target_schools: [],
  intended_major: '',
  major_certainty: 'EXPLORING',
  aptitude: {
    gpa_weighted: null,
    gpa_normalized: null,
    gpa_unweighted: null,
    sat_total: null,
    sat_normalized: null,
    act_total: null,
    act_normalized: null,
    test_optional: false,
    ap_count: null,
    ap_avg_score: null,
    rigor_normalized: null,
    ib_diploma: false,
    academic_awards: [],
    awards_normalized: null,
  },
  passion: {
    spike_category: null,
    leadership_level: null,
    leadership_normalized: null,
    ec_commitment_years: null,
    ec_hours_weekly: null,
    commitment_normalized: null,
    project_impact: null,
    project_normalized: null,
    project_description: '',
    research_level: null,
    research_normalized: null,
    ec_awards: [],
    ec_awards_normalized: null,
    brag_text: '',
    brag_nlp_extracted: null,
  },
  community: {
    service_leadership: null,
    service_normalized: null,
    service_hours: null,
    hours_normalized: null,
    community_impact: null,
    impact_normalized: null,
  },
  high_school: {
    hs_name: '',
    hs_code: '',
    hs_type: 'PUBLIC',
    region: 'BAY_AREA',
    saturation_level: 'MEDIUM',
    ivy_applicants_per_year: 0,
    saturation_adjustment: 0,
  },
  demographics: {
    ethnicity: 'PREFER_NOT_SAY',
    ethnicity_multiplier: 1.0,
    first_gen: false,
    first_gen_multiplier: 1.0,
    legacy: false,
    legacy_schools: [],
    income_band: 'PREFER_NOT_SAY',
    income_top_1_percent: false,
    income_multiplier: 1.0,
    recruited_athlete: false,
    athlete_multiplier: 1.0,
  },
  major_context: {
    intended_major: '',
    major_certainty: 'EXPLORING',
    major_multiplier: 1.0,
  },
  assessment_intelligence: {
    psychometrics: {
      grit_resilience: 0.5,
      introversion_extroversion: 0,
      coachability: 'MEDIUM',
      coachability_score: 0.5,
      vision_clarity: 0.5,
      identity_comfort: 0.5,
      maturity_level: 0.5,
      articulation_ability: 0.5,
      openness: 0.5,
      conscientiousness: 0.5,
      extraversion: 0.5,
      agreeableness: 0.5,
      neuroticism: 0.5,
    },
    time_management: {
      homework_hours_daily: 3,
      social_media_hours_daily: 2,
      ec_hours_weekly: 10,
      sleep_hours_daily: 7,
      committed_hours_weekly: 100,
      reclaimable_hours_weekly: 20,
      burnout_risk: 'MEDIUM',
    },
    hidden_capabilities: {
      hidden_technical_projects: [],
      hobby_passions: [],
      unconventional_interests: [],
    },
    family_context: {
      parent_archetype: 'BALANCED',
      academic_expectations: 'FLEXIBLE',
    },
    academic_intelligence: {
      grade_pattern_trajectory: 'STABLE',
      test_anxiety_indicator: 0.3,
    },
  },
});

interface StudentStoreState {
  profile: StudentProfile;
  isLoading: boolean;
  isDirty: boolean;

  // Identity
  setIdentity: (identity: Partial<StudentIdentity>) => void;
  setRole: (role: Role) => void;
  setName: (name: string) => void;
  setGrade: (grade: Grade) => void;

  // Schools & Major
  setTargetSchools: (schools: string[]) => void;
  toggleTargetSchool: (schoolId: string) => void;
  setIntendedMajor: (major: string) => void;
  setMajorCertainty: (certainty: MajorCertainty) => void;

  // Aptitude
  setAptitude: (aptitude: Partial<AptitudeAttributes>) => void;
  setGPA: (weighted: number, unweighted?: number) => void;
  setSAT: (total: number) => void;
  setACT: (total: number) => void;
  setAPCourses: (count: number, avgScore: number) => void;
  setAcademicAwards: (awards: string[]) => void;
  setTestOptional: (optional: boolean) => void;

  // Passion
  setPassion: (passion: Partial<PassionAttributes>) => void;
  updatePassion: <K extends keyof PassionAttributes>(field: K, value: PassionAttributes[K]) => void;
  setSpikeCategory: (spike: SpikeCategory) => void;
  setLeadershipLevel: (level: LeadershipLevel) => void;
  setECCommitment: (years: number, hoursWeekly: number) => void;
  setProjectImpact: (impact: number, description: string) => void;
  setResearchLevel: (level: ResearchLevel) => void;
  setECAwards: (awards: string[]) => void;
  setBragText: (text: string) => void;

  // Community
  setCommunity: (community: Partial<CommunityAttributes>) => void;
  setServiceLeadership: (level: ServiceLeadership) => void;
  setServiceHours: (hours: number) => void;
  setCommunityImpact: (impact: number) => void;

  // High School
  setHighSchool: (hs: HighSchoolContext) => void;

  // Demographics
  setDemographics: (demo: Partial<DemographicContext>) => void;
  setEthnicity: (ethnicity: Ethnicity) => void;
  setFirstGen: (firstGen: boolean) => void;
  setLegacy: (legacy: boolean, schools: string[]) => void;
  setIncomeBand: (band: IncomeBand) => void;
  setRecruitedAthlete: (athlete: boolean) => void;

  // Assessment Intelligence (Layer 4)
  setAssessmentIntelligence: (ai: Partial<AssessmentIntelligence>) => void;
  setPsychometrics: (psych: Partial<AssessmentIntelligence['psychometrics']>) => void;
  setTimeManagement: (tm: Partial<AssessmentIntelligence['time_management']>) => void;

  // Frame 4: Operating Data (NEW)
  updateOperating: <K extends keyof OperatingData>(field: K, value: OperatingData[K]) => void;
  updateOperatingBulk: (data: Partial<OperatingData>) => void;
  calculateCompleteness: () => number;

  // Profile management
  resetProfile: () => void;
  loadProfile: (profile: StudentProfile) => void;
  getProfile: () => StudentProfile;
}

export const useStudentStore = create<StudentStoreState>()(
  devtools(
    persist(
      immer((set, get) => ({
        profile: createEmptyProfile(),
        isLoading: false,
        isDirty: false,

        // Identity
        setIdentity: (identity) =>
          set((state) => {
            Object.assign(state.profile.identity, identity);
            state.isDirty = true;
          }),
        setRole: (role) =>
          set((state) => {
            state.profile.identity.role = role;
            state.isDirty = true;
          }),
        setName: (name) =>
          set((state) => {
            state.profile.identity.name = name;
            state.isDirty = true;
          }),
        setGrade: (grade) =>
          set((state) => {
            state.profile.identity.grade = grade;
            state.isDirty = true;
          }),

        // Schools & Major
        setTargetSchools: (schools) =>
          set((state) => {
            state.profile.target_schools = schools;
            state.isDirty = true;
          }),
        toggleTargetSchool: (schoolId) =>
          set((state) => {
            const idx = state.profile.target_schools.indexOf(schoolId);
            if (idx === -1) {
              state.profile.target_schools.push(schoolId);
            } else {
              state.profile.target_schools.splice(idx, 1);
            }
            state.isDirty = true;
          }),
        setIntendedMajor: (major) =>
          set((state) => {
            state.profile.intended_major = major;
            state.profile.major_context.intended_major = major;
            state.isDirty = true;
          }),
        setMajorCertainty: (certainty) =>
          set((state) => {
            state.profile.major_certainty = certainty;
            state.profile.major_context.major_certainty = certainty;
            state.isDirty = true;
          }),

        // Aptitude
        setAptitude: (aptitude) =>
          set((state) => {
            Object.assign(state.profile.aptitude, aptitude);
            state.isDirty = true;
          }),
        setGPA: (weighted, unweighted) =>
          set((state) => {
            state.profile.aptitude.gpa_weighted = weighted;
            if (unweighted !== undefined) {
              state.profile.aptitude.gpa_unweighted = unweighted;
            }
            state.isDirty = true;
          }),
        setSAT: (total) =>
          set((state) => {
            state.profile.aptitude.sat_total = total;
            state.profile.aptitude.test_optional = false;
            state.isDirty = true;
          }),
        setACT: (total) =>
          set((state) => {
            state.profile.aptitude.act_total = total;
            state.profile.aptitude.test_optional = false;
            state.isDirty = true;
          }),
        setAPCourses: (count, avgScore) =>
          set((state) => {
            state.profile.aptitude.ap_count = count;
            state.profile.aptitude.ap_avg_score = avgScore;
            state.isDirty = true;
          }),
        setAcademicAwards: (awards) =>
          set((state) => {
            state.profile.aptitude.academic_awards = awards;
            state.isDirty = true;
          }),
        setTestOptional: (optional) =>
          set((state) => {
            state.profile.aptitude.test_optional = optional;
            if (optional) {
              state.profile.aptitude.sat_total = null;
              state.profile.aptitude.act_total = null;
            }
            state.isDirty = true;
          }),

        // Passion
        setPassion: (passion) =>
          set((state) => {
            Object.assign(state.profile.passion, passion);
            state.isDirty = true;
          }),
        updatePassion: (field, value) =>
          set((state) => {
            (state.profile.passion as Record<string, unknown>)[field] = value;
            state.isDirty = true;
          }),
        setSpikeCategory: (spike) =>
          set((state) => {
            state.profile.passion.spike_category = spike;
            state.isDirty = true;
          }),
        setLeadershipLevel: (level) =>
          set((state) => {
            state.profile.passion.leadership_level = level;
            state.isDirty = true;
          }),
        setECCommitment: (years, hoursWeekly) =>
          set((state) => {
            state.profile.passion.ec_commitment_years = years;
            state.profile.passion.ec_hours_weekly = hoursWeekly;
            state.isDirty = true;
          }),
        setProjectImpact: (impact, description) =>
          set((state) => {
            state.profile.passion.project_impact = impact;
            state.profile.passion.project_description = description;
            state.isDirty = true;
          }),
        setResearchLevel: (level) =>
          set((state) => {
            state.profile.passion.research_level = level;
            state.isDirty = true;
          }),
        setECAwards: (awards) =>
          set((state) => {
            state.profile.passion.ec_awards = awards;
            state.isDirty = true;
          }),
        setBragText: (text) =>
          set((state) => {
            state.profile.passion.brag_text = text;
            state.isDirty = true;
          }),

        // Community
        setCommunity: (community) =>
          set((state) => {
            Object.assign(state.profile.community, community);
            state.isDirty = true;
          }),
        setServiceLeadership: (level) =>
          set((state) => {
            state.profile.community.service_leadership = level;
            state.isDirty = true;
          }),
        setServiceHours: (hours) =>
          set((state) => {
            state.profile.community.service_hours = hours;
            state.isDirty = true;
          }),
        setCommunityImpact: (impact) =>
          set((state) => {
            state.profile.community.community_impact = impact;
            state.isDirty = true;
          }),

        // High School
        setHighSchool: (hs) =>
          set((state) => {
            state.profile.high_school = hs;
            state.isDirty = true;
          }),

        // Demographics
        setDemographics: (demo) =>
          set((state) => {
            Object.assign(state.profile.demographics, demo);
            state.isDirty = true;
          }),
        setEthnicity: (ethnicity) =>
          set((state) => {
            state.profile.demographics.ethnicity = ethnicity;
            state.isDirty = true;
          }),
        setFirstGen: (firstGen) =>
          set((state) => {
            state.profile.demographics.first_gen = firstGen;
            state.profile.demographics.first_gen_multiplier = firstGen ? 1.15 : 1.0;
            state.isDirty = true;
          }),
        setLegacy: (legacy, schools) =>
          set((state) => {
            state.profile.demographics.legacy = legacy;
            state.profile.demographics.legacy_schools = schools;
            state.isDirty = true;
          }),
        setIncomeBand: (band) =>
          set((state) => {
            state.profile.demographics.income_band = band;
            state.profile.demographics.income_top_1_percent = band === 'TOP_1_PERCENT';
            state.isDirty = true;
          }),
        setRecruitedAthlete: (athlete) =>
          set((state) => {
            state.profile.demographics.recruited_athlete = athlete;
            state.profile.demographics.athlete_multiplier = athlete ? 2.5 : 1.0;
            state.isDirty = true;
          }),

        // Assessment Intelligence
        setAssessmentIntelligence: (ai) =>
          set((state) => {
            if (ai.psychometrics) {
              Object.assign(state.profile.assessment_intelligence.psychometrics, ai.psychometrics);
            }
            if (ai.time_management) {
              Object.assign(state.profile.assessment_intelligence.time_management, ai.time_management);
            }
            if (ai.hidden_capabilities) {
              Object.assign(state.profile.assessment_intelligence.hidden_capabilities, ai.hidden_capabilities);
            }
            if (ai.family_context) {
              Object.assign(state.profile.assessment_intelligence.family_context, ai.family_context);
            }
            if (ai.academic_intelligence) {
              Object.assign(state.profile.assessment_intelligence.academic_intelligence, ai.academic_intelligence);
            }
            state.isDirty = true;
          }),
        setPsychometrics: (psych) =>
          set((state) => {
            Object.assign(state.profile.assessment_intelligence.psychometrics, psych);
            state.isDirty = true;
          }),
        setTimeManagement: (tm) =>
          set((state) => {
            Object.assign(state.profile.assessment_intelligence.time_management, tm);
            state.isDirty = true;
          }),

        // Frame 4: Operating Data
        updateOperating: (field, value) =>
          set((state) => {
            if (!state.profile.operating) {
              state.profile.operating = {};
            }
            (state.profile.operating as Record<string, unknown>)[field] = value;
            state.isDirty = true;
          }),
        updateOperatingBulk: (data) =>
          set((state) => {
            if (!state.profile.operating) {
              state.profile.operating = {};
            }
            Object.assign(state.profile.operating, data);
            state.isDirty = true;
          }),
        calculateCompleteness: () => {
          const profile = get().profile;
          let score = 0;
          let hasAcademics = false;
          let hasActivities = false;
          let hasContext = false;
          let hasOperating = false;

          // Academics (30 points possible)
          if (profile.aptitude?.gpa_weighted || profile.aptitude?.gpa_unweighted) {
            score += 10;
            hasAcademics = true;
          }
          if (profile.aptitude?.sat_total || profile.aptitude?.act_total) {
            score += 10;
            hasAcademics = true;
          }
          if (profile.aptitude?.ap_count && profile.aptitude.ap_count > 0) {
            score += 10;
            hasAcademics = true;
          }

          // Activities (40 points possible)
          const ecCommitment = profile.passion?.ec_commitment_years;
          const serviceHours = profile.community?.service_hours || 0;
          const leadershipLevel = profile.passion?.leadership_level;

          if (ecCommitment && ecCommitment > 0) {
            score += 20;
            hasActivities = true;
          }
          if (serviceHours > 0) {
            score += 10;
            hasActivities = true;
          }
          if (leadershipLevel && leadershipLevel !== 'PARTICIPANT') {
            score += 10;
            hasActivities = true;
          }

          // Context (15 points possible)
          if (profile.operating?.parent1Occupation) {
            score += 5;
            hasContext = true;
          }
          if (profile.operating?.transportation) {
            score += 5;
            hasContext = true;
          }
          if (profile.operating?.firstGeneration !== undefined && profile.operating.firstGeneration !== null) {
            score += 5;
            hasContext = true;
          }

          // Operating (15 points possible)
          if (profile.operating?.availableHoursPerWeek !== undefined) {
            score += 5;
            hasOperating = true;
          }
          if (profile.operating?.favoriteSubject) {
            score += 5;
            hasOperating = true;
          }
          if (profile.operating?.strengths && profile.operating.strengths.length > 0) {
            score += 5;
            hasOperating = true;
          }

          // Update completeness in store
          set((state) => {
            state.profile.completeness = {
              score,
              hasAcademics,
              hasActivities,
              hasContext,
              hasOperating,
            };
          });

          return score;
        },

        // Profile management
        resetProfile: () =>
          set((state) => {
            state.profile = createEmptyProfile();
            state.isDirty = false;
          }),
        loadProfile: (profile) =>
          set((state) => {
            state.profile = profile;
            state.isDirty = false;
          }),
        getProfile: () => get().profile,
      })),
      {
        name: 'ivyquest-student-profile',
        partialize: (state) => ({ profile: state.profile }),
      }
    ),
    { name: 'StudentStore' }
  )
);
