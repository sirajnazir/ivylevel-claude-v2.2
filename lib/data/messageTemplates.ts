/**
 * Message templates for insights
 * Variables in {braces} will be replaced with actual data
 */

export const MESSAGE_TEMPLATES = {
  // === GPA INSIGHTS ===
  gpa: {
    high: {
      title: 'Academic Excellence',
      message: 'Your {gpa} weighted GPA ranks in the {percentile}th percentile among Ivy+ applicants. Strong academic foundation!',
    },
    medium: {
      title: 'Competitive GPA',
      message: 'Your {gpa} GPA is competitive for top-20 schools. Focus on differentiation through your unique story and impact.',
    },
    contextBoost: {
      title: 'Context Advantage Unlocked',
      message: 'Your {rawGPA} GPA + {contextFactor} = {contextGPA} contextualized. Admissions officers evaluate you relative to students with similar resources.',
    },
  },

  // === TEST SCORE INSIGHTS ===
  testScore: {
    strong: {
      title: 'Test Scores: {percentile}th Percentile',
      message: 'Your {score} SAT is in range for all top schools. Strong testing complements your academic profile.',
    },
    competitive: {
      title: 'Competitive Test Scores',
      message: 'Your {score} SAT = {percentile}th percentile. You\'re in the competitive range for most top schools.',
    },
    testOptional: {
      title: 'Test-Optional Recommended',
      message: 'Your {score} SAT is below the middle 50% for most selective schools. Strongly consider test-optional applications where your GPA, activities, and story carry the evaluation.',
    },
  },

  // === LEADERSHIP INSIGHTS ===
  leadership: {
    elite: {
      title: '{level} Leadership',
      message: '{level} leadership appears in only {percentage}% of applications—but these students have significantly higher admit rates. This is a major differentiator.',
    },
    strong: {
      title: '{level} Leadership',
      message: '{level} leadership demonstrates sustained commitment and impact. Push to next tier for maximum differentiation.',
    },
  },

  // === SERVICE INSIGHTS ===
  service: {
    exceptional: {
      title: 'Community Champion',
      message: '{hours} service hours is {multiplier}x the average applicant. This shows sustained commitment! Focus on the STORY: Why this cause? What impact did you create?',
    },
    strong: {
      title: 'Strong Service Record',
      message: '{hours} hours is {multiplier}x the average applicant. Quality of impact matters as much as quantity—make sure to highlight specific outcomes.',
    },
  },

  // === RIGOR INSIGHTS ===
  rigor: {
    exceptional: {
      title: 'Exceptional Course Rigor',
      message: '{count} AP courses demonstrates exceptional academic ambition. Make sure your AP scores (ideally 4-5) match the course count for maximum impact.',
    },
    strong: {
      title: 'Strong Course Rigor',
      message: '{count} APs shows strong rigor. Remember: quality and performance matter more than quantity. Focus on scores of 4-5.',
    },
    competitive: {
      title: 'Competitive Rigor',
      message: '{count} APs is competitive, especially if they\'re in your spike area. Course rigor is evaluated relative to what YOUR school offers.',
    },
  },

  // === MILESTONE ===
  milestone: {
    frame2Complete: {
      title: 'Academic Profile Complete!',
      message: 'Your academic foundation is secured. Next: Building Your Passion Spike—this is where 70% of differentiation happens.',
    },
    frame3Complete: {
      title: 'Passion Profile Complete!',
      message: 'You\'ve captured your impact and leadership. Next: Finalizing your full profile.',
    },
  },
} as const;

export type MessageTemplates = typeof MESSAGE_TEMPLATES;
