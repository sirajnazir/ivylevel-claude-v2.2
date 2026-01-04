/**
 * Profile Types - v11.0
 */

export interface StudentProfile {
  id: string;
  name: string;
  grade: number;
  gpa?: number;
  strengths: string[];
  activities: Activity[];
  goals: string[];
  context: ProfileContext;
}

export interface Activity {
  id: string;
  name: string;
  category: 'academic' | 'service' | 'leadership' | 'creative' | 'athletic' | 'work';
  hoursPerWeek: number;
  yearsInvolved: number;
  leadership: boolean;
  achievements?: string[];
}

export interface ProfileContext {
  firstGen: boolean;
  freeReducedLunch: boolean;
  workingStudent: boolean;
  familyResponsibilities: boolean;
  ruralStudent: boolean;
  athleteRecruit: boolean;
  legacyStatus: boolean;
}

export interface CategoryScores {
  aptitude: number;
  passion: number;
  service: number;
  identity: number;
}

export interface CRIResult {
  raw: number;
  adjusted: number;
  multiplier: number;
  contextFactors: string[];
}

export interface ProfileSnapshot {
  profile: StudentProfile;
  scores: CategoryScores;
  cri: CRIResult;
  overallScore: number;
  narrativeDna?: string;
  archetype?: string;
  strengths: string[];
  gaps: string[];
}
