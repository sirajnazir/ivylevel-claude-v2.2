/**
 * Loading Insights Generator
 *
 * Generates personalized insights displayed during Frame 5 scoring API call.
 * These Noom-style facts keep users engaged during the 1-3 second wait time.
 */

import type { StudentProfile } from '@/lib/types/student';

/**
 * Generates personalized loading insights based on student profile
 * Used during Frame 5 scoring API call
 */
export function generateLoadingInsights(profile: StudentProfile): string[] {
  const insights: string[] = [];

  // STATIC EDUCATIONAL FACTS (always include some)
  const staticInsights = [
    "Stanford evaluates students in context—your achievements are measured against your opportunities, not against every applicant.",
    "Did you know? The admissions rubric weighs 'Overcoming Barriers' at 4/5—higher than 'Special Talent' at 3/5.",
    "MIT's middle 50% SAT range is 1510-1570, but test scores are just one piece of your story.",
    "Harvard's acceptance rate dropped to 3.2% in 2024, but holistic review means your unique narrative matters most.",
    "Only 8% of Ivy+ applicants have national-level leadership—but these students have significantly higher admit rates.",
    "First-generation college students receive meaningful consideration in holistic admissions processes.",
    "Ivy+ schools seek 'well-lopsided' students with spikes, not 'well-rounded' students doing everything.",
    "Demonstrated intellectual curiosity beyond the classroom is one of the strongest predictors of admission.",
    "The Common App essay is your chance to show who you are beyond grades and test scores.",
    "Admissions officers spend an average of 8-12 minutes reviewing each application—make every detail count.",
  ];

  // Add 4 random static insights
  const shuffledStatic = [...staticInsights].sort(() => Math.random() - 0.5);
  insights.push(...shuffledStatic.slice(0, 4));

  // PERSONALIZED BASED ON GPA
  const gpa = profile.aptitude?.gpa_weighted ?? profile.aptitude?.gpa_unweighted ?? 0;
  if (gpa >= 4.5) {
    insights.push("Your weighted GPA is in the top 10% of all Ivy+ applicants—strong academic foundation.");
  } else if (gpa >= 4.0) {
    insights.push("Your GPA is competitive for top-20 schools. Focus on differentiation through your unique story.");
  } else if (gpa >= 3.7) {
    insights.push("Context matters: Your GPA combined with your responsibilities often scores higher than a perfect 4.0 alone.");
  } else if (gpa >= 3.5) {
    insights.push("Admissions officers evaluate your GPA in the context of your school's resources and your personal circumstances.");
  }

  // PERSONALIZED BASED ON TEST SCORES
  const sat = profile.aptitude?.sat_total ?? 0;
  const act = profile.aptitude?.act_total ?? 0;

  if (sat >= 1550 || act >= 35) {
    insights.push("Your test score is in the 99th percentile nationally—this demonstrates strong academic readiness.");
  } else if (sat >= 1500 || act >= 34) {
    insights.push("Your test score is within the middle 50% range for all Ivy+ schools.");
  } else if (sat >= 1450 || act >= 32) {
    insights.push("Many top schools are test-optional—your holistic profile and story matter more than test scores alone.");
  } else if (sat >= 1400 || act >= 30) {
    insights.push("Consider test-optional applications where your achievements and narrative can shine without score comparison.");
  } else if (profile.aptitude?.test_optional) {
    insights.push("Going test-optional? Research shows it doesn't hurt your chances at schools that truly embrace this policy.");
  }

  // PERSONALIZED BASED ON LEADERSHIP
  const leadership = profile.passion?.leadership_level;
  if (leadership === 'FOUNDER_NATIONAL' || leadership === 'FOUNDER_STATE') {
    insights.push("Founding an organization shows exceptional initiative—only 5% of applicants demonstrate this level of leadership.");
  } else if (leadership === 'STATE_PRES' || leadership === 'SCHOOL_PRES') {
    insights.push("Leadership positions demonstrate your ability to inspire others and create impact beyond yourself.");
  } else if (leadership === 'OFFICER') {
    insights.push("Officer roles show responsibility and engagement—consider documenting specific initiatives you've led.");
  }

  // PERSONALIZED BASED ON DEMOGRAPHICS
  if (profile.demographics?.first_gen) {
    insights.push("First-generation students demonstrate pioneering spirit and resourcefulness—qualities Ivy+ schools actively seek.");
  }

  if (profile.demographics?.legacy) {
    insights.push("Legacy status provides familiarity with the institution, but your individual achievements still drive the decision.");
  }

  if (profile.demographics?.recruited_athlete) {
    insights.push("Recruited athletes have a significant advantage—athletic excellence combined with academics is highly valued.");
  }

  // PERSONALIZED BASED ON TARGET SCHOOLS
  const targetSchools = profile.target_schools ?? [];
  if (targetSchools.some(s => s.toLowerCase().includes('stanford') || s === 'STANFORD')) {
    insights.push("Stanford explicitly seeks students with 'intellectual vitality'—deep curiosity and passion for learning beyond grades.");
  }
  if (targetSchools.some(s => s.toLowerCase().includes('mit') || s === 'MIT')) {
    insights.push("MIT values 'hands-on makers' who build things and solve real problems, not just study them theoretically.");
  }
  if (targetSchools.some(s => s.toLowerCase().includes('harvard') || s === 'HARVARD')) {
    insights.push("Harvard's holistic review emphasizes leadership potential and contributions to your community.");
  }
  if (targetSchools.some(s => s.toLowerCase().includes('princeton') || s === 'PRINCETON')) {
    insights.push("Princeton seeks students who will contribute to the undergraduate community through service and collaboration.");
  }
  if (targetSchools.some(s => s.toLowerCase().includes('yale') || s === 'YALE')) {
    insights.push("Yale values diversity of thought and seeks students who will engage deeply with the residential college system.");
  }
  if (targetSchools.some(s => s.toLowerCase().includes('columbia') || s === 'COLUMBIA')) {
    insights.push("Columbia appreciates students who thrive in urban environments and seek to leverage New York City's resources.");
  }
  if (targetSchools.some(s => s.toLowerCase().includes('caltech') || s === 'CALTECH')) {
    insights.push("Caltech is the most meritocratic of the Ivy+—they care almost exclusively about STEM research potential.");
  }

  // PERSONALIZED BASED ON COMMUNITY SERVICE
  const serviceHours = profile.community?.service_hours ?? 0;
  if (serviceHours >= 300) {
    insights.push(`Your ${serviceHours}+ service hours demonstrate sustained commitment—that's 4x the average applicant.`);
  } else if (serviceHours >= 200) {
    insights.push(`${serviceHours} service hours shows real dedication. Quality of impact matters as much as quantity.`);
  } else if (serviceHours >= 100) {
    insights.push("Focus on the story behind your service: Why this cause? What changed because of your involvement?");
  }

  // PERSONALIZED BASED ON RESEARCH
  const research = profile.passion?.research_level;
  if (research === 'NATIONAL' || research === 'STATE') {
    insights.push("Published research or significant independent study demonstrates intellectual initiative highly valued at research universities.");
  } else if (research === 'SCHOOL' || research === 'INDEPENDENT') {
    insights.push("Research experience shows curiosity beyond the classroom—a key indicator of academic potential.");
  }

  // PERSONALIZED BASED ON AP/IB
  const apCount = profile.aptitude?.ap_count ?? 0;
  const ibDiploma = profile.aptitude?.ib_diploma;

  if (ibDiploma) {
    insights.push("The IB Diploma demonstrates commitment to a rigorous, globally-minded curriculum—admissions officers recognize this.");
  } else if (apCount >= 12) {
    insights.push(`${apCount} AP courses demonstrates exceptional academic ambition and course rigor.`);
  } else if (apCount >= 8) {
    insights.push(`${apCount} APs shows strong course rigor. Remember: quality and performance matter more than quantity.`);
  } else if (apCount >= 5) {
    insights.push("Course rigor is evaluated relative to what your high school offers, not in absolute terms.");
  }

  // PERSONALIZED BASED ON SPIKE
  const spike = profile.passion?.spike_category;
  if (spike) {
    const spikeLabels: Record<string, string> = {
      RESEARCH: 'research and discovery',
      LEADER: 'leadership and organizing',
      SERVICE: 'community service and impact',
      CREATE: 'creative expression and building',
      BUSINESS: 'entrepreneurship and business',
      SPORTS: 'athletic excellence',
      FIGURING: 'exploration and self-discovery',
    };
    const spikeLabel = spikeLabels[spike] || spike.toLowerCase();
    insights.push(`Your passion for ${spikeLabel} gives you a clear narrative thread—this 'spike' helps you stand out from generalists.`);
  }

  // PERSONALIZED BASED ON HIGH SCHOOL SATURATION
  const saturation = profile.high_school?.saturation_level;
  if (saturation === 'ULTRA' || saturation === 'HIGH') {
    insights.push("Coming from a competitive high school? Differentiation is key—show what makes you unique among high-achieving peers.");
  } else if (saturation === 'LOW') {
    insights.push("From a less-represented school? This context works in your favor—you've excelled with the resources available.");
  }

  // PERSONALIZED BASED ON GRADE
  const grade = profile.identity?.grade;
  if (grade === 9 || grade === 10) {
    insights.push("Starting early gives you time to build depth in your activities. Focus on consistency over breadth.");
  } else if (grade === 11) {
    insights.push("Junior year is critical for demonstrating academic trajectory. Your GPA this year carries significant weight.");
  } else if (grade === 12) {
    insights.push("Senior year is about execution and storytelling. Your essays will tie your journey together.");
  }

  // PERSONALIZED BASED ON INTENDED MAJOR
  const major = profile.intended_major?.toLowerCase() ?? '';
  if (major.includes('computer') || major.includes('cs') || major.includes('engineering')) {
    insights.push("STEM majors are competitive at top schools—demonstrate projects and research beyond coursework.");
  } else if (major.includes('pre-med') || major.includes('biology') || major.includes('medicine')) {
    insights.push("Pre-med is highly competitive—show genuine passion for healthcare through clinical experience and research.");
  } else if (major.includes('business') || major.includes('econ')) {
    insights.push("Business/econ applicants should demonstrate entrepreneurial spirit or real-world financial acumen.");
  } else if (major.includes('art') || major.includes('music') || major.includes('theater')) {
    insights.push("Arts applicants should showcase a strong portfolio—your creative work speaks louder than grades.");
  }

  // PERSONALIZED BASED ON PROJECT IMPACT
  const projectImpact = profile.passion?.project_impact ?? 0;
  if (projectImpact >= 1000) {
    insights.push(`Reaching ${projectImpact.toLocaleString()} people with your project shows significant real-world impact.`);
  } else if (projectImpact >= 100) {
    insights.push("Your project's community impact demonstrates initiative. Quantify results where possible in your essays.");
  }

  // Shuffle all insights and return 7-9 for variety during loading
  const shuffled = insights.sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(9, shuffled.length));
}

/**
 * Get a single random insight from the personalized set
 * Useful for one-off display
 */
export function getRandomLoadingInsight(profile: StudentProfile): string {
  const insights = generateLoadingInsights(profile);
  return insights[Math.floor(Math.random() * insights.length)] || "Analyzing your profile...";
}

export default generateLoadingInsights;
