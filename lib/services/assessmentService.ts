/**
 * Assessment Service
 *
 * Handles saving and loading assessment data to/from Supabase.
 * Links assessments to authenticated users for multi-device support.
 */

import { getSupabaseClient } from '@/lib/supabase/client';
import type {
  Assessment,
  AssessmentInsert,
  AssessmentUpdate,
  AssessmentScores,
  Json,
} from '@/lib/supabase/database.types';
import type { StudentProfile } from '@/lib/types/student';

// =============================================================================
// Types
// =============================================================================

export interface SaveAssessmentParams {
  userId: string;
  sessionId: string;
  profile: StudentProfile;
  scores: AssessmentScores;
  archetype?: string;
  completenessScore?: number;
}

export interface SaveAssessmentResult {
  success: boolean;
  data?: Assessment;
  error?: string;
}

export interface LoadAssessmentResult {
  success: boolean;
  data?: {
    profile: StudentProfile;
    scores: AssessmentScores;
    archetype: string | null;
    completedAt: string | null;
  };
  error?: string;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Calculate completeness score from profile data
 * Based on StudentProfile structure from lib/types/student.ts
 */
export function calculateCompleteness(profile: StudentProfile): number {
  let filled = 0;
  let total = 0;

  // Identity (name, grade)
  total += 2;
  if (profile.identity?.name) filled++;
  if (profile.identity?.grade) filled++;

  // Aptitude (GPA, tests, rigor)
  total += 4;
  if (profile.aptitude?.gpa_weighted) filled++;
  if (profile.aptitude?.sat_total || profile.aptitude?.act_total) filled++;
  if (profile.aptitude?.ap_count !== null && profile.aptitude?.ap_count !== undefined) filled++;
  if (profile.aptitude?.academic_awards?.length) filled++;

  // Passion (leadership, ECs, projects)
  total += 4;
  if (profile.passion?.spike_category) filled++;
  if (profile.passion?.leadership_level) filled++;
  if (profile.passion?.ec_commitment_years) filled++;
  if (profile.passion?.ec_awards?.length) filled++;

  // Community
  total += 2;
  if (profile.community?.service_leadership) filled++;
  if (profile.community?.service_hours) filled++;

  // Target schools and major
  total += 2;
  if (profile.target_schools?.length) filled++;
  if (profile.intended_major) filled++;

  return Math.round((filled / total) * 100);
}

// =============================================================================
// Service Functions
// =============================================================================

/**
 * Save assessment to Supabase
 * Uses upsert to handle both new and existing assessments
 */
export async function saveAssessment(
  params: SaveAssessmentParams
): Promise<SaveAssessmentResult> {
  const { userId, sessionId, profile, scores, archetype, completenessScore } = params;

  try {
    const supabase = getSupabaseClient();

    const insertData: AssessmentInsert = {
      user_id: userId,
      session_id: sessionId,
      profile_data: profile as unknown as Json,
      scores: scores as unknown as Json,
      archetype: archetype || null,
      completeness_score: completenessScore ?? calculateCompleteness(profile),
      completed_at: new Date().toISOString(),
    };

    const { data, error } = await supabase
      .from('assessments')
      .upsert(insertData, {
        onConflict: 'user_id,session_id',
      })
      .select()
      .single();

    if (error) {
      console.error('[AssessmentService] Save error:', error);
      return { success: false, error: error.message };
    }

    console.log('[AssessmentService] Assessment saved:', data.id);
    return { success: true, data };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[AssessmentService] Save exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Update an existing assessment
 */
export async function updateAssessment(
  assessmentId: string,
  updates: Partial<SaveAssessmentParams>
): Promise<SaveAssessmentResult> {
  try {
    const supabase = getSupabaseClient();

    const updateData: AssessmentUpdate = {};

    if (updates.profile) {
      updateData.profile_data = updates.profile as unknown as Json;
    }
    if (updates.scores) {
      updateData.scores = updates.scores as unknown as Json;
    }
    if (updates.archetype !== undefined) {
      updateData.archetype = updates.archetype;
    }
    if (updates.completenessScore !== undefined) {
      updateData.completeness_score = updates.completenessScore;
    }

    const { data, error } = await supabase
      .from('assessments')
      .update(updateData)
      .eq('id', assessmentId)
      .select()
      .single();

    if (error) {
      console.error('[AssessmentService] Update error:', error);
      return { success: false, error: error.message };
    }

    return { success: true, data };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[AssessmentService] Update exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Load the latest completed assessment for a user
 */
export async function loadLatestAssessment(
  userId: string
): Promise<LoadAssessmentResult> {
  try {
    const supabase = getSupabaseClient();

    // Use the view for latest completed assessment
    const { data, error } = await supabase
      .from('v_current_assessment')
      .select('*')
      .eq('user_id', userId)
      .maybeSingle();

    if (error) {
      console.error('[AssessmentService] Load error:', error);
      return { success: false, error: error.message };
    }

    if (!data) {
      console.log('[AssessmentService] No assessment found for user:', userId);
      return { success: true, data: undefined };
    }

    console.log('[AssessmentService] Assessment loaded:', data.id);
    return {
      success: true,
      data: {
        profile: data.profile_data as StudentProfile,
        scores: data.scores as AssessmentScores,
        archetype: data.archetype,
        completedAt: data.completed_at,
      },
    };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[AssessmentService] Load exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Load all assessments for a user
 */
export async function loadAllAssessments(userId: string): Promise<{
  success: boolean;
  data?: Assessment[];
  error?: string;
}> {
  try {
    const supabase = getSupabaseClient();

    const { data, error } = await supabase
      .from('assessments')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('[AssessmentService] Load all error:', error);
      return { success: false, error: error.message };
    }

    return { success: true, data: data || [] };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[AssessmentService] Load all exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Check if user has a completed assessment
 */
export async function hasCompletedAssessment(userId: string): Promise<boolean> {
  try {
    const supabase = getSupabaseClient();

    const { count, error } = await supabase
      .from('assessments')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId)
      .not('completed_at', 'is', null);

    if (error) {
      console.error('[AssessmentService] Check error:', error);
      return false;
    }

    return (count ?? 0) > 0;
  } catch {
    return false;
  }
}

/**
 * Delete all user data from Supabase
 * Useful for testing - allows re-running the assessment flow
 * Deletes ALL related data including profile, projects, conversations, etc.
 */
export async function deleteUserData(userId: string): Promise<{
  success: boolean;
  error?: string;
  deletedCounts?: Record<string, number>;
}> {
  try {
    const supabase = getSupabaseClient();
    const deletedCounts: Record<string, number> = {};

    console.log('[AssessmentService] Deleting all data for user:', userId);

    // First, get the profile_id (which may be the same as userId or different)
    const { data: profile } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', userId)
      .single();

    const profileId = profile?.id || userId;
    console.log('[AssessmentService] Profile ID:', profileId);

    // Helper function to delete from a table
    const deleteFromTable = async (
      tableName: string,
      idColumn: string,
      idValue: string
    ): Promise<number> => {
      try {
        const { count, error } = await supabase
          .from(tableName)
          .delete({ count: 'exact' })
          .eq(idColumn, idValue);

        if (error) {
          // Table might not exist or column mismatch - that's OK
          console.warn(`[AssessmentService] Delete ${tableName} warning:`, error.message);
          return 0;
        }
        return count ?? 0;
      } catch {
        return 0;
      }
    };

    // Delete from tables that use user_id
    const userIdTables = [
      'assessments',
      'weekly_vitals',
      'student_items',
      'timeline_events',
    ];

    for (const table of userIdTables) {
      deletedCounts[table] = await deleteFromTable(table, 'user_id', userId);
    }

    // Delete from tables that use profile_id (child tables first to avoid FK violations)
    const profileIdTables = [
      'nudge_queue',
      'conversations',
      'projects',
      'weekly_plans',
      'agent_memories',
      'crises',
      'game_plans',
      'notifications',
    ];

    for (const table of profileIdTables) {
      deletedCounts[table] = await deleteFromTable(table, 'profile_id', profileId);
    }

    // Finally delete the profile itself
    deletedCounts['profiles'] = await deleteFromTable('profiles', 'id', profileId);

    console.log('[AssessmentService] Deleted counts:', deletedCounts);
    return { success: true, deletedCounts };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[AssessmentService] Delete exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}
