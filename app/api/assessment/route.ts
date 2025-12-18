/**
 * Assessment Persistence API
 * POST /api/assessment - Save an assessment
 * GET /api/assessment?session_id=xxx - Load an assessment by session ID
 * GET /api/assessment?email=xxx - Load assessments by email
 */

import { NextRequest, NextResponse } from 'next/server';
import { createAdminClient } from '@/lib/supabase/server';
import type { AssessmentInsert, AssessmentUpdate, Json } from '@/lib/supabase/database.types';
import type { StudentProfile } from '@/lib/types/student';

const ENABLE_PERSISTENCE = process.env.ENABLE_SUPABASE_PERSISTENCE === 'true';

export async function POST(request: NextRequest) {
  // Allow saving even if persistence is disabled (for development)
  // but log a warning
  if (!ENABLE_PERSISTENCE) {
    console.log('[Assessment API] Supabase persistence disabled, returning mock success');
    return NextResponse.json({
      success: true,
      persisted: false,
      message: 'Assessment accepted (persistence disabled)',
    });
  }

  try {
    const body = await request.json();
    const {
      session_id,
      email,
      profile,
      game_plan,
      scores,
      completeness = 0,
      tier,
      archetype,
    } = body as {
      session_id: string;
      email?: string;
      profile: StudentProfile;
      game_plan?: unknown;
      scores?: { aptitude: number; passion: number; community: number; identity: number; overall: number };
      completeness?: number;
      tier?: string;
      archetype?: string;
    };

    if (!session_id || !profile) {
      return NextResponse.json(
        { error: 'Missing required fields: session_id, profile' },
        { status: 400 }
      );
    }

    const supabase = createAdminClient();

    // Check if assessment already exists
    const { data: existing } = await supabase
      .from('assessments')
      .select('id')
      .eq('session_id', session_id)
      .single();

    const now = new Date().toISOString();

    if (existing) {
      // Update existing assessment
      const updateData: AssessmentUpdate = {
        email: email || null,
        profile_data: profile as unknown as Json,
        game_plan_data: (game_plan as unknown as Json) || null,
        scores: scores || null,
        completeness,
        tier: tier || null,
        archetype: archetype || null,
        updated_at: now,
      };

      const { error: updateError } = await supabase
        .from('assessments')
        .update(updateData)
        .eq('id', existing.id);

      if (updateError) {
        console.error('[Assessment API] Update error:', updateError);
        return NextResponse.json(
          { error: 'Failed to update assessment', details: updateError.message },
          { status: 500 }
        );
      }

      return NextResponse.json({
        success: true,
        persisted: true,
        action: 'updated',
        id: existing.id,
      });
    } else {
      // Insert new assessment
      const insertData: AssessmentInsert = {
        session_id,
        email: email || null,
        profile_data: profile as unknown as Json,
        game_plan_data: (game_plan as unknown as Json) || null,
        scores: scores || null,
        completeness,
        tier: tier || null,
        archetype: archetype || null,
        created_at: now,
        updated_at: now,
      };

      const { data: newAssessment, error: insertError } = await supabase
        .from('assessments')
        .insert(insertData)
        .select('id')
        .single();

      if (insertError) {
        console.error('[Assessment API] Insert error:', insertError);
        return NextResponse.json(
          { error: 'Failed to save assessment', details: insertError.message },
          { status: 500 }
        );
      }

      return NextResponse.json({
        success: true,
        persisted: true,
        action: 'created',
        id: newAssessment.id,
      });
    }
  } catch (error: unknown) {
    const err = error as Error;
    console.error('[Assessment API] POST error:', err);
    return NextResponse.json(
      { error: 'Internal server error', message: err.message },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  if (!ENABLE_PERSISTENCE) {
    return NextResponse.json({
      success: false,
      persisted: false,
      message: 'Supabase persistence disabled',
      data: null,
    });
  }

  try {
    const { searchParams } = new URL(request.url);
    const session_id = searchParams.get('session_id');
    const email = searchParams.get('email');

    if (!session_id && !email) {
      return NextResponse.json(
        { error: 'Missing query parameter: session_id or email required' },
        { status: 400 }
      );
    }

    const supabase = createAdminClient();

    if (session_id) {
      // Fetch by session ID (single assessment)
      const { data, error } = await supabase
        .from('assessments')
        .select('*')
        .eq('session_id', session_id)
        .single();

      if (error) {
        if (error.code === 'PGRST116') {
          // No rows returned
          return NextResponse.json({
            success: true,
            found: false,
            data: null,
          });
        }
        console.error('[Assessment API] GET error:', error);
        return NextResponse.json(
          { error: 'Failed to fetch assessment', details: error.message },
          { status: 500 }
        );
      }

      return NextResponse.json({
        success: true,
        found: true,
        data: {
          ...data,
          profile: data.profile_data,
          game_plan: data.game_plan_data,
        },
      });
    }

    if (email) {
      // Fetch by email (potentially multiple assessments)
      const { data, error } = await supabase
        .from('assessments')
        .select('*')
        .eq('email', email)
        .order('updated_at', { ascending: false });

      if (error) {
        console.error('[Assessment API] GET error:', error);
        return NextResponse.json(
          { error: 'Failed to fetch assessments', details: error.message },
          { status: 500 }
        );
      }

      return NextResponse.json({
        success: true,
        found: data.length > 0,
        count: data.length,
        data: data.map((item) => ({
          ...item,
          profile: item.profile_data,
          game_plan: item.game_plan_data,
        })),
      });
    }
  } catch (error: unknown) {
    const err = error as Error;
    console.error('[Assessment API] GET error:', err);
    return NextResponse.json(
      { error: 'Internal server error', message: err.message },
      { status: 500 }
    );
  }
}
