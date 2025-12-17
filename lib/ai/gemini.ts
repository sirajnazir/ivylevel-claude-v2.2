/**
 * Google Gemini AI Service
 * Handles NLP extraction from student text inputs
 */

import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from '@google/generative-ai';

// Initialize Gemini client
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_GENERATIVE_AI_API_KEY || '');

// Safety settings for educational content
const safetySettings = [
  {
    category: HarmCategory.HARM_CATEGORY_HARASSMENT,
    threshold: HarmBlockThreshold.BLOCK_NONE,
  },
  {
    category: HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    threshold: HarmBlockThreshold.BLOCK_NONE,
  },
  {
    category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
  },
  {
    category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
  },
];

// Extraction result types
export interface BragTextExtraction {
  // Spike category detection
  detected_spike: 'LEADER' | 'STEM_BUILDER' | 'HUMANITIES' | 'ARTIST' | 'ATHLETE' | 'ENTREPRENEUR' | 'ACTIVIST' | null;
  spike_confidence: number;

  // Leadership indicators
  leadership_indicators: string[];
  estimated_leadership_level: 'NATIONAL_PRES' | 'STATE_PRES' | 'SCHOOL_PRES' | 'CLUB_PRES' | 'MEMBER' | null;

  // Impact metrics (estimated)
  estimated_impact_people: number;
  impact_scope: 'NATIONAL' | 'STATE' | 'LOCAL' | 'SCHOOL' | null;

  // Research/academic indicators
  research_indicators: string[];
  estimated_research_level: 'PUBLISHED' | 'MENTORED' | 'SCHOOL' | 'NONE' | null;

  // EC awards detected
  detected_awards: ('NATIONAL' | 'STATE' | 'REGIONAL' | 'SCHOOL')[];

  // Passion keywords
  passion_keywords: string[];

  // Narrative strength (0-1)
  narrative_clarity: number;
  narrative_uniqueness: number;

  // Key phrases for essay hooks
  hook_phrases: string[];

  // Raw extraction confidence
  overall_confidence: number;
}

export interface ProjectExtraction {
  // Technical depth
  technical_complexity: 'HIGH' | 'MEDIUM' | 'LOW';
  technologies_detected: string[];

  // Impact
  estimated_users: number;
  monetization_detected: boolean;

  // Innovation
  novelty_score: number;

  // Category
  project_category: 'APP' | 'RESEARCH' | 'NONPROFIT' | 'BUSINESS' | 'CREATIVE' | 'OTHER';
}

/**
 * Extract structured attributes from student's brag text
 */
export async function extractFromBragText(bragText: string): Promise<BragTextExtraction> {
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.0-flash-exp',
    safetySettings,
  });

  const prompt = `You are an expert college admissions counselor analyzing a high school student's self-description.
Extract structured information from their "brag text" - a paragraph describing their accomplishments.

STUDENT'S BRAG TEXT:
"""
${bragText}
"""

Analyze this text and extract the following information. Be conservative with estimates - only flag things you have clear evidence for.

Return a JSON object with these exact fields:
{
  "detected_spike": "LEADER" | "STEM_BUILDER" | "HUMANITIES" | "ARTIST" | "ATHLETE" | "ENTREPRENEUR" | "ACTIVIST" | null,
  "spike_confidence": 0.0 to 1.0,
  "leadership_indicators": ["list of leadership mentions"],
  "estimated_leadership_level": "NATIONAL_PRES" | "STATE_PRES" | "SCHOOL_PRES" | "CLUB_PRES" | "MEMBER" | null,
  "estimated_impact_people": number (0 if unclear),
  "impact_scope": "NATIONAL" | "STATE" | "LOCAL" | "SCHOOL" | null,
  "research_indicators": ["list of research/academic mentions"],
  "estimated_research_level": "PUBLISHED" | "MENTORED" | "SCHOOL" | "NONE" | null,
  "detected_awards": ["NATIONAL", "STATE", "REGIONAL", "SCHOOL"],
  "passion_keywords": ["key passion/interest terms"],
  "narrative_clarity": 0.0 to 1.0,
  "narrative_uniqueness": 0.0 to 1.0,
  "hook_phrases": ["memorable phrases for essays"],
  "overall_confidence": 0.0 to 1.0
}

Leadership level guide:
- NATIONAL_PRES: National organization leadership, USA-level competition winners
- STATE_PRES: State-level president, state competition winners
- SCHOOL_PRES: Student body president, school-wide leadership
- CLUB_PRES: Club president, team captain
- MEMBER: Active member without leadership title

Spike category guide:
- LEADER: Strong leadership focus, multiple leadership roles
- STEM_BUILDER: Technical projects, coding, engineering, science competitions
- HUMANITIES: Writing, debate, social sciences, languages
- ARTIST: Visual arts, music, theater, creative pursuits
- ATHLETE: Sports achievements, athletic recruiting potential
- ENTREPRENEUR: Business ventures, startups, monetized projects
- ACTIVIST: Social causes, community organizing, advocacy

Return ONLY the JSON object, no explanation.`;

  try {
    const result = await model.generateContent(prompt);
    const response = result.response;
    const text = response.text();

    // Parse JSON from response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in response');
    }

    const extraction = JSON.parse(jsonMatch[0]) as BragTextExtraction;
    return extraction;
  } catch (error) {
    console.error('Gemini extraction error:', error);
    // Return default extraction on error
    return {
      detected_spike: null,
      spike_confidence: 0,
      leadership_indicators: [],
      estimated_leadership_level: null,
      estimated_impact_people: 0,
      impact_scope: null,
      research_indicators: [],
      estimated_research_level: null,
      detected_awards: [],
      passion_keywords: [],
      narrative_clarity: 0.5,
      narrative_uniqueness: 0.5,
      hook_phrases: [],
      overall_confidence: 0,
    };
  }
}

/**
 * Extract structured attributes from project description
 */
export async function extractFromProjectDescription(projectDescription: string): Promise<ProjectExtraction> {
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.0-flash-exp',
    safetySettings,
  });

  const prompt = `You are an expert college admissions counselor analyzing a high school student's project description.
Extract structured information about the project's technical depth, impact, and category.

PROJECT DESCRIPTION:
"""
${projectDescription}
"""

Return a JSON object with these exact fields:
{
  "technical_complexity": "HIGH" | "MEDIUM" | "LOW",
  "technologies_detected": ["list of technologies/skills mentioned"],
  "estimated_users": number (0 if unclear),
  "monetization_detected": boolean,
  "novelty_score": 0.0 to 1.0,
  "project_category": "APP" | "RESEARCH" | "NONPROFIT" | "BUSINESS" | "CREATIVE" | "OTHER"
}

Technical complexity guide:
- HIGH: Machine learning, advanced algorithms, distributed systems, published research
- MEDIUM: Full-stack apps, robotics, data analysis, hardware projects
- LOW: Basic websites, simple scripts, school assignments

Return ONLY the JSON object, no explanation.`;

  try {
    const result = await model.generateContent(prompt);
    const response = result.response;
    const text = response.text();

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in response');
    }

    return JSON.parse(jsonMatch[0]) as ProjectExtraction;
  } catch (error) {
    console.error('Gemini project extraction error:', error);
    return {
      technical_complexity: 'MEDIUM',
      technologies_detected: [],
      estimated_users: 0,
      monetization_detected: false,
      novelty_score: 0.5,
      project_category: 'OTHER',
    };
  }
}

/**
 * Generate personalized narrative tagline based on profile
 */
export async function generateNarrativeTagline(
  spikeCategory: string,
  majorIntent: string,
  topAchievement: string
): Promise<string> {
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.0-flash-exp',
    safetySettings,
  });

  const prompt = `Generate a compelling one-line narrative tagline for a college applicant.

Profile:
- Primary strength/spike: ${spikeCategory}
- Intended major: ${majorIntent}
- Top achievement: ${topAchievement}

The tagline should:
1. Be memorable and unique (not generic)
2. Connect their spike to their intended major
3. Hint at their potential impact
4. Be 8-12 words maximum

Examples of good taglines:
- "The robotics captain building accessible tech for rural communities"
- "A debate champion turning policy research into real-world advocacy"
- "The entrepreneur who coded her way from small town to startup founder"

Return ONLY the tagline, no quotes, no explanation.`;

  try {
    const result = await model.generateContent(prompt);
    const response = result.response;
    return response.text().trim().replace(/^["']|["']$/g, '');
  } catch (error) {
    console.error('Gemini tagline error:', error);
    return `A driven ${spikeCategory.toLowerCase()} pursuing ${majorIntent}`;
  }
}

/**
 * Analyze essay draft for strength and suggestions
 */
export async function analyzeEssayDraft(essayText: string): Promise<{
  strengths: string[];
  weaknesses: string[];
  hook_quality: number;
  authenticity: number;
  suggestions: string[];
}> {
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.0-flash-exp',
    safetySettings,
  });

  const prompt = `You are an expert college essay counselor. Analyze this essay draft.

ESSAY:
"""
${essayText}
"""

Return a JSON object:
{
  "strengths": ["list 2-3 strengths"],
  "weaknesses": ["list 2-3 areas for improvement"],
  "hook_quality": 0.0 to 1.0,
  "authenticity": 0.0 to 1.0,
  "suggestions": ["3 specific, actionable suggestions"]
}

Focus on:
- Opening hook effectiveness
- Voice and authenticity
- Specific details vs. generic statements
- Connection to applicant's unique story

Return ONLY the JSON object.`;

  try {
    const result = await model.generateContent(prompt);
    const response = result.response;
    const text = response.text();

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in response');
    }

    return JSON.parse(jsonMatch[0]);
  } catch (error) {
    console.error('Gemini essay analysis error:', error);
    return {
      strengths: ['Unable to analyze'],
      weaknesses: ['Unable to analyze'],
      hook_quality: 0.5,
      authenticity: 0.5,
      suggestions: ['Please try again'],
    };
  }
}
