/**
 * Skip Logic Utilities
 * Handle empty/missing data gracefully with encouraging messages
 */

import type { StudentProfile, Grade } from '@/lib/types/student';

export interface SkipMessage {
  show: boolean;
  message: string;
  icon: 'info' | 'success' | 'none';
}

/**
 * Check if GPA data should be skipped
 */
export function shouldSkipGPA(profile: StudentProfile): SkipMessage {
  const hasGPA = profile.aptitude?.gpa_weighted || profile.aptitude?.gpa_unweighted;

  if (!hasGPA) {
    return {
      show: true,
      message: "No GPA yet? That's okay! We'll track it as you progress.",
      icon: 'info',
    };
  }

  return { show: false, message: '', icon: 'none' };
}

/**
 * Check if test scores should be skipped
 */
export function shouldSkipTestScores(profile: StudentProfile): SkipMessage {
  const hasSAT = profile.aptitude?.sat_total;
  const hasACT = profile.aptitude?.act_total;

  if (!hasSAT && !hasACT) {
    return {
      show: true,
      message: "Haven't taken tests yet? Perfect - we'll plan test prep in your game plan!",
      icon: 'success',
    };
  }

  return { show: false, message: '', icon: 'none' };
}

/**
 * Check if AP courses should be skipped
 */
export function shouldSkipAPCourses(profile: StudentProfile, grade: Grade): SkipMessage {
  const apCount = profile.aptitude?.ap_count || 0;
  const gradeNum = typeof grade === 'number' ? grade : 12;

  if (apCount === 0 && gradeNum <= 9) {
    return {
      show: true,
      message: "0 APs is normal for 9th grade. We'll help you choose which to take.",
      icon: 'success',
    };
  }

  if (apCount === 0 && gradeNum >= 10) {
    return {
      show: true,
      message: "No APs yet? That's okay - we'll add rigor to your game plan.",
      icon: 'info',
    };
  }

  return { show: false, message: '', icon: 'none' };
}

/**
 * Check if extracurriculars should be skipped
 */
export function shouldSkipExtracurriculars(profile: StudentProfile): SkipMessage {
  const hasECs = profile.passion?.ec_commitment_years && profile.passion.ec_commitment_years > 0;

  if (!hasECs) {
    return {
      show: true,
      message: "No activities yet? That's exactly why you're here! Most students start with a blank slate.",
      icon: 'success',
    };
  }

  return { show: false, message: '', icon: 'none' };
}

/**
 * Check if leadership should be skipped
 */
export function shouldSkipLeadership(profile: StudentProfile): SkipMessage {
  const leadership = profile.passion?.leadership_level;

  if (!leadership || leadership === 'PARTICIPANT') {
    return {
      show: true,
      message: "No leadership roles yet? We'll help you build them!",
      icon: 'info',
    };
  }

  return { show: false, message: '', icon: 'none' };
}

/**
 * Check if service hours should be skipped
 */
export function shouldSkipService(profile: StudentProfile): SkipMessage {
  const hours = profile.community?.service_hours || 0;

  if (hours === 0) {
    return {
      show: true,
      message: "No service yet? We'll find meaningful opportunities for you.",
      icon: 'info',
    };
  }

  return { show: false, message: '', icon: 'none' };
}

/**
 * Check if awards should be skipped
 */
export function shouldSkipAwards(profile: StudentProfile): SkipMessage {
  const academicAwards = profile.aptitude?.academic_awards || [];
  const ecAwards = profile.passion?.ec_awards || [];

  if (academicAwards.length === 0 && ecAwards.length === 0) {
    return {
      show: true,
      message: "No awards yet? Awards come later - we'll work on this together.",
      icon: 'success',
    };
  }

  return { show: false, message: '', icon: 'none' };
}

/**
 * Determine if a field is truly required based on context
 */
export function isFieldRequired(
  fieldName: string,
  _profile: StudentProfile
): boolean {
  // Hard requirements (always mandatory)
  const alwaysRequired = [
    'identity.name',
    'identity.grade',
    'operating.parent1Occupation',
    'operating.transportation',
    'operating.availableHoursPerWeek',
    'operating.homeworkHoursPerDay',
    'operating.firstGeneration',
  ];

  if (alwaysRequired.includes(fieldName)) {
    return true;
  }

  // Everything else is optional
  return false;
}

/**
 * Get encouragement message for empty state
 */
export function getEmptyStateMessage(section: string, grade: Grade): string {
  const gradeNum = typeof grade === 'number' ? grade : 12;

  const messages: Record<string, string> = {
    academics:
      gradeNum <= 9
        ? "You're just getting started - this is the perfect time to build a strong foundation!"
        : "Don't worry about gaps - we'll address them in your personalized game plan.",

    activities:
      'Starting from scratch means we can build your profile strategically from day one!',

    leadership:
      'Leadership roles develop over time. We\'ll help you find opportunities.',

    service:
      "Service is something we can add quickly. We'll find causes that matter to you.",

    awards:
      "Awards and recognition come as you get involved. We'll guide you to competitions.",

    testing:
      gradeNum <= 10
        ? 'Perfect timing to start prep! Early practice leads to higher scores.'
        : "Let's plan your testing strategy to maximize your score potential.",

    default: "We'll work on this together!",
  };

  return messages[section] || messages.default;
}

/**
 * Get skip summary for a profile section
 */
export function getSkipSummary(profile: StudentProfile): {
  canSkipAcademics: boolean;
  canSkipActivities: boolean;
  canSkipService: boolean;
  skippedSections: string[];
} {
  const skippedSections: string[] = [];

  const canSkipAcademics =
    !profile.aptitude?.gpa_weighted &&
    !profile.aptitude?.gpa_unweighted &&
    !profile.aptitude?.sat_total &&
    !profile.aptitude?.act_total;

  if (canSkipAcademics) {
    skippedSections.push('academics');
  }

  const canSkipActivities =
    !profile.passion?.ec_commitment_years &&
    !profile.passion?.leadership_level;

  if (canSkipActivities) {
    skippedSections.push('activities');
  }

  const canSkipService = !profile.community?.service_hours;

  if (canSkipService) {
    skippedSections.push('service');
  }

  return {
    canSkipAcademics,
    canSkipActivities,
    canSkipService,
    skippedSections,
  };
}

/**
 * Get profile tier based on completeness
 */
export function getProfileTier(profile: StudentProfile): 'fresh-start' | 'emerging' | 'optimization' {
  const completeness = profile.completeness?.score || 0;

  if (completeness < 30) return 'fresh-start';
  if (completeness < 60) return 'emerging';
  return 'optimization';
}

/**
 * Get tier-specific messaging
 */
export function getTierMessage(tier: 'fresh-start' | 'emerging' | 'optimization'): {
  title: string;
  description: string;
  encouragement: string;
} {
  const messages = {
    'fresh-start': {
      title: 'Foundation Builder',
      description: "You're starting with a blank slate - and that's actually a superpower!",
      encouragement: "We'll build your profile strategically from day one, avoiding common mistakes.",
    },
    emerging: {
      title: 'Rising Star',
      description: "You've got a solid foundation. Now it's time to deepen your impact.",
      encouragement: "Let's focus on developing your spike and standing out from the crowd.",
    },
    optimization: {
      title: 'Profile Optimizer',
      description: 'You have strong credentials. Time to fine-tune for maximum impact.',
      encouragement: "We'll polish your narrative and maximize your admission chances.",
    },
  };

  return messages[tier];
}
