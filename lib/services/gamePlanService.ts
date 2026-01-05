/**
 * Game Plan Service
 *
 * Handles saving and loading game plans to/from Supabase.
 * Links game plans to authenticated users and their assessments.
 */

import { getSupabaseClient } from '@/lib/supabase/client';
import type {
  GamePlan,
  GamePlanInsert,
  GamePlanUpdate,
  Json,
} from '@/lib/supabase/database.types';

// =============================================================================
// Types
// =============================================================================

export interface GamePlanData {
  summary?: {
    target_tier?: string;
    current_tier?: string;
    transformation_path?: string;
  };
  college_strategy?: {
    target?: string[];
    reach?: string[];
    match?: string[];
    safety?: string[];
  };
  phases?: Array<{
    name: string;
    duration: string;
    goals: string[];
    actions: string[];
  }>;
  boosters?: Array<{
    id: string;
    category: string;
    title: string;
    description: string;
    impact: number;
    effort: number;
    selected?: boolean;
  }>;
  [key: string]: unknown;
}

export interface SaveGamePlanParams {
  userId: string;
  assessmentId?: string;
  planData: GamePlanData;
  targetArchetype?: string;
  targetTier?: string;
  targetSchools?: string[];
}

export interface SaveGamePlanResult {
  success: boolean;
  data?: GamePlan;
  error?: string;
}

export interface LoadGamePlanResult {
  success: boolean;
  data?: {
    planData: GamePlanData;
    targetArchetype: string | null;
    currentPhase: string | null;
    currentWeek: number;
    completionPercentage: number;
    createdAt: string;
    updatedAt: string;
  };
  error?: string;
}

// =============================================================================
// Service Functions
// =============================================================================

/**
 * Save a new game plan to Supabase
 * Archives any existing active plan for the user
 */
export async function saveGamePlan(
  params: SaveGamePlanParams
): Promise<SaveGamePlanResult> {
  const { userId, assessmentId, planData, targetArchetype, targetTier, targetSchools } =
    params;

  try {
    const supabase = getSupabaseClient();

    // Archive any existing active plans
    await supabase
      .from('game_plans')
      .update({ plan_status: 'archived' })
      .eq('user_id', userId)
      .eq('plan_status', 'active');

    // Insert new plan
    const insertData: GamePlanInsert = {
      user_id: userId,
      assessment_id: assessmentId || null,
      plan_data: planData as unknown as Json,
      target_archetype: targetArchetype || planData.summary?.target_tier || null,
      target_tier: targetTier || null,
      target_schools: targetSchools ? (targetSchools as unknown as Json) : null,
      plan_status: 'active',
      activated_at: new Date().toISOString(),
      current_phase: planData.phases?.[0]?.name || 'Phase 1',
      current_week: 1,
      completion_percentage: 0,
    };

    const { data, error } = await supabase
      .from('game_plans')
      .insert(insertData)
      .select()
      .single();

    if (error) {
      console.error('[GamePlanService] Save error:', error);
      return { success: false, error: error.message };
    }

    console.log('[GamePlanService] Game plan saved:', data.id);
    return { success: true, data };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[GamePlanService] Save exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Update an existing game plan
 */
export async function updateGamePlan(
  gamePlanId: string,
  updates: {
    planData?: GamePlanData;
    currentPhase?: string;
    currentWeek?: number;
    completionPercentage?: number;
    planStatus?: 'draft' | 'active' | 'archived' | 'completed';
  }
): Promise<SaveGamePlanResult> {
  try {
    const supabase = getSupabaseClient();

    const updateData: GamePlanUpdate = {};

    if (updates.planData) {
      updateData.plan_data = updates.planData as unknown as Json;
    }
    if (updates.currentPhase !== undefined) {
      updateData.current_phase = updates.currentPhase;
    }
    if (updates.currentWeek !== undefined) {
      updateData.current_week = updates.currentWeek;
    }
    if (updates.completionPercentage !== undefined) {
      updateData.completion_percentage = updates.completionPercentage;
    }
    if (updates.planStatus !== undefined) {
      updateData.plan_status = updates.planStatus;
      if (updates.planStatus === 'completed') {
        updateData.completed_at = new Date().toISOString();
      }
    }

    const { data, error } = await supabase
      .from('game_plans')
      .update(updateData)
      .eq('id', gamePlanId)
      .select()
      .single();

    if (error) {
      console.error('[GamePlanService] Update error:', error);
      return { success: false, error: error.message };
    }

    return { success: true, data };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[GamePlanService] Update exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Load the active game plan for a user
 */
export async function loadActiveGamePlan(
  userId: string
): Promise<LoadGamePlanResult> {
  try {
    const supabase = getSupabaseClient();

    // Use the view for active game plan
    const { data, error } = await supabase
      .from('v_active_game_plan')
      .select('*')
      .eq('user_id', userId)
      .maybeSingle();

    if (error) {
      console.error('[GamePlanService] Load error:', error);
      return { success: false, error: error.message };
    }

    if (!data) {
      console.log('[GamePlanService] No active game plan found for user:', userId);
      return { success: true, data: undefined };
    }

    console.log('[GamePlanService] Game plan loaded:', data.id);
    return {
      success: true,
      data: {
        planData: data.plan_data as GamePlanData,
        targetArchetype: data.target_archetype,
        currentPhase: data.current_phase,
        currentWeek: data.current_week,
        completionPercentage: data.completion_percentage,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
      },
    };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[GamePlanService] Load exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Load all game plans for a user
 */
export async function loadAllGamePlans(userId: string): Promise<{
  success: boolean;
  data?: GamePlan[];
  error?: string;
}> {
  try {
    const supabase = getSupabaseClient();

    const { data, error } = await supabase
      .from('game_plans')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('[GamePlanService] Load all error:', error);
      return { success: false, error: error.message };
    }

    return { success: true, data: data || [] };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    console.error('[GamePlanService] Load all exception:', errorMessage);
    return { success: false, error: errorMessage };
  }
}

/**
 * Check if user has an active game plan
 */
export async function hasActiveGamePlan(userId: string): Promise<boolean> {
  try {
    const supabase = getSupabaseClient();

    const { count, error } = await supabase
      .from('game_plans')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId)
      .eq('plan_status', 'active');

    if (error) {
      console.error('[GamePlanService] Check error:', error);
      return false;
    }

    return (count ?? 0) > 0;
  } catch {
    return false;
  }
}

/**
 * Archive the active game plan
 */
export async function archiveActiveGamePlan(userId: string): Promise<boolean> {
  try {
    const supabase = getSupabaseClient();

    const { error } = await supabase
      .from('game_plans')
      .update({ plan_status: 'archived' })
      .eq('user_id', userId)
      .eq('plan_status', 'active');

    if (error) {
      console.error('[GamePlanService] Archive error:', error);
      return false;
    }

    return true;
  } catch {
    return false;
  }
}
