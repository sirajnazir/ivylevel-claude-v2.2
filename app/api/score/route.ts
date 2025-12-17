/**
 * IvyQuest Scoring API Endpoint
 * POST /api/score
 *
 * Takes a StudentProfile, normalizes attributes, calculates scores and probabilities
 * Returns complete AssessmentResults with Ivy+ Score and school-by-school breakdown
 */

import { NextRequest, NextResponse } from 'next/server';
import type { StudentProfile, AssessmentResults } from '@/lib/types/student';
import { normalizeStudentProfile } from '@/lib/utils/normalize';
import { generateAssessmentResults } from '@/lib/scoring/engine';
import { getSchools } from '@/lib/data/schools';
import { prepareProfile } from '@/lib/validation/profile';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const rawProfile = body.profile as Partial<StudentProfile>;

    if (!rawProfile) {
      return NextResponse.json(
        { error: 'Missing profile in request body' },
        { status: 400 }
      );
    }

    // Step 0: Complete and validate profile at API boundary
    // This applies defaults for all missing fields (UNIVERSAL solution)
    const { profile: completedProfile, validation } = prepareProfile(rawProfile);

    if (!validation.valid) {
      console.error('Profile validation errors:', validation.errors);
      return NextResponse.json(
        { error: 'Invalid profile data', details: validation.errors },
        { status: 400 }
      );
    }

    if (validation.warnings.length > 0) {
      console.log('Profile validation warnings:', validation.warnings);
    }

    // Step 1: Normalize all Layer 1 attributes (0.0-1.0 rubric scores)
    const normalized_profile = normalizeStudentProfile(completedProfile);

    // Step 2: Generate complete assessment results
    // This runs the full IvyLevel v6.0 scoring engine:
    // - Calculates Ivy+ Ready Score (0-100)
    // - Calculates SFFA rubrics (1-6 scale)
    // - Calculates P_base using sigmoid formula
    // - Applies Chetty multipliers (legacy, first-gen, etc.)
    // - Calculates P_final for each school (capped 95%)
    // - Determines fit levels
    // - Generates helping/holding back factors
    const results: AssessmentResults = generateAssessmentResults(normalized_profile);

    // Step 3: Add school configurations to response for frontend display
    const school_configs = getSchools(completedProfile.target_schools);

    // Step 4: Return complete results
    return NextResponse.json({
      success: true,
      profile: normalized_profile, // Return normalized version
      results,
      school_configs,
      timestamp: new Date().toISOString(),
    });

  } catch (error: any) {
    console.error('Scoring API Error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error during scoring calculation',
        message: error.message,
      },
      { status: 500 }
    );
  }
}

// Health check endpoint
export async function GET() {
  return NextResponse.json({
    status: 'operational',
    version: '2.2.0',
    engine: 'IvyLevel Scoring Engine v6.0',
    features: [
      '58 Layer 1 attributes',
      '39 Layer 4 assessment intelligence points',
      '4-layer data flow',
      'Real Chetty 2023 ROI multipliers',
      'CDS 2025 acceptance rates',
      'SFFA rubric scoring (1-6 scale)',
      'NSC saturation database',
      'P_final = P_base × ROI formula',
    ],
  });
}
