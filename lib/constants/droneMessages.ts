/**
 * Drone Assistant Messages
 *
 * Contextual messages displayed by the Ivy drone assistant
 * for each frame and card in the assessment flow.
 */

/**
 * Frame 1: Warmup - Getting to know the student
 */
export const FRAME1_MESSAGES = {
  role: "Hi there! I'm Ivy, your college admissions assistant. Let's start by understanding who you are. Are you a student preparing for college, or a parent helping your child?",
  identity: "Great choice! Now, tell me your name and what grade you're in. This helps me personalize your Digital Twin experience.",
  schools: "Dream big! Select the schools you're interested in. Don't worry about being realistic yet - we'll analyze your fit for each one.",
  major: "What field excites you the most? Your intended major helps me understand which programs to focus on and what strengths matter most.",
} as const;

/**
 * Frame 2: Snapshot - Academic profile
 */
export const FRAME2_MESSAGES = {
  gpa: "Let's talk academics! Your GPA is one piece of the puzzle. Enter your weighted GPA if available - it gives credit for challenging courses.",
  testing: "Standardized tests are optional at many schools now, but strong scores can still help. Share what you have!",
  courseload: "Course rigor matters a lot. Taking AP, IB, or honors classes shows colleges you challenge yourself.",
  achievements: "Academic achievements like awards, competitions, or special recognitions really stand out. What are you most proud of?",
} as const;

/**
 * Frame 3: Building - Extracurriculars and activities
 */
export const FRAME3_MESSAGES = {
  activities: "Now the fun part! Your extracurriculars show who you are outside the classroom. Quality over quantity - depth of involvement matters more than a long list.",
  leadership: "Leadership doesn't just mean being president. It's about taking initiative, creating impact, and inspiring others.",
  community: "Community service and giving back shows character. What causes matter to you?",
  passions: "What truly excites you? Admissions officers love to see genuine passion and commitment over time.",
} as const;

/**
 * Frame 4: Operating (if applicable)
 */
export const FRAME4_MESSAGES = {
  default: "Almost there! A few more questions to fine-tune your Digital Twin profile.",
  scenarios: "How you handle challenges tells a lot about your character. Think about times you've shown resilience.",
  timeEnergy: "How you spend your time reflects your priorities. Walk me through a typical week.",
  capabilities: "Everyone has hidden talents! What skills or abilities might surprise people about you?",
} as const;

/**
 * Frame 5: Reveal - Results
 */
export const FRAME5_MESSAGES = {
  loading: "Analyzing your profile with our AI engine... This is exciting! Your Digital Twin Fleet is being assembled.",
  score: "Here's your Ivy+ Ready Score! This reflects your overall competitiveness across all four pillars: Aptitude, Passion, Community, and Narrative.",
  schools: "Now let's see how you match up with each school. Remember, these probabilities are personalized to YOUR unique profile.",
  fleet: "Meet your Digital Twin Fleet! Each avatar represents you at a different school, tailored to what that institution values most.",
  factors: "Understanding what's helping and holding you back is the first step to improvement. Let's dive into the details.",
  archetype: "Every successful applicant has a unique story. Your archetype captures the essence of what makes you special.",
} as const;

/**
 * Frame 6: Power-Ups - Improvement recommendations
 */
export const FRAME6_MESSAGES = {
  default: "Time to level up! Based on your profile, here are personalized power-ups to boost your chances.",
  boosters: "These boosters are tailored specifically for you. Focus on the high-impact ones first for maximum results.",
  actionPlan: "I've created a personalized action plan. Small consistent steps lead to big improvements over time!",
} as const;

/**
 * Generic/fallback messages
 */
export const GENERIC_MESSAGES = {
  welcome: "Hi! I'm Ivy, your AI college admissions assistant. I'm here to help guide you through building your Digital Twin profile.",
  encouragement: "You're doing great! Every detail you share helps me build a more accurate picture of your potential.",
  almostDone: "We're almost finished! Just a few more questions to complete your profile.",
  complete: "Fantastic work! Your Digital Twin profile is complete. Let's see what insights await!",
} as const;

/**
 * Get message for a specific frame and card
 */
export function getDroneMessage(frame: number, card?: string): string {
  switch (frame) {
    case 1:
      return card && FRAME1_MESSAGES[card as keyof typeof FRAME1_MESSAGES]
        ? FRAME1_MESSAGES[card as keyof typeof FRAME1_MESSAGES]
        : GENERIC_MESSAGES.welcome;
    case 2:
      return card && FRAME2_MESSAGES[card as keyof typeof FRAME2_MESSAGES]
        ? FRAME2_MESSAGES[card as keyof typeof FRAME2_MESSAGES]
        : GENERIC_MESSAGES.encouragement;
    case 3:
      return card && FRAME3_MESSAGES[card as keyof typeof FRAME3_MESSAGES]
        ? FRAME3_MESSAGES[card as keyof typeof FRAME3_MESSAGES]
        : GENERIC_MESSAGES.encouragement;
    case 4:
      return card && FRAME4_MESSAGES[card as keyof typeof FRAME4_MESSAGES]
        ? FRAME4_MESSAGES[card as keyof typeof FRAME4_MESSAGES]
        : FRAME4_MESSAGES.default;
    case 5:
      return card && FRAME5_MESSAGES[card as keyof typeof FRAME5_MESSAGES]
        ? FRAME5_MESSAGES[card as keyof typeof FRAME5_MESSAGES]
        : FRAME5_MESSAGES.loading;
    case 6:
      return card && FRAME6_MESSAGES[card as keyof typeof FRAME6_MESSAGES]
        ? FRAME6_MESSAGES[card as keyof typeof FRAME6_MESSAGES]
        : FRAME6_MESSAGES.default;
    default:
      return GENERIC_MESSAGES.welcome;
  }
}

export default {
  FRAME1_MESSAGES,
  FRAME2_MESSAGES,
  FRAME3_MESSAGES,
  FRAME4_MESSAGES,
  FRAME5_MESSAGES,
  FRAME6_MESSAGES,
  GENERIC_MESSAGES,
  getDroneMessage,
};
