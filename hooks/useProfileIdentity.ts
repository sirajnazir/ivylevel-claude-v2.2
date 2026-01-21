/**
 * useProfileIdentity Hook - v5.2 Data Unification
 * ================================================
 *
 * Single source of truth for IDENTITY data from database.
 * Does NOT replace useResultsStore for scoring data (Frames depend on it).
 *
 * Features:
 * - Reads identity data from profiles table via RPC
 * - Null-safe defaults from DB function
 * - Shorter stale time (30s) for freshness
 * - Export query invalidation helper
 *
 * Usage:
 *   const { data: identity, isLoading } = useProfileIdentity(profileId);
 *   const brandStatement = identity?.brandStatement || '';
 */

'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getSupabaseClient } from '@/lib/supabase/client';

// ============================================================================
// TYPES
// ============================================================================

export interface ProfileIdentity {
  id: string;
  userId: string | null;
  name: string | null;
  email: string | null;
  grade: number | null;

  // Archetype
  archetypeId: string | null;
  archetypeName: string | null;
  archetypeConfidence: number;

  // Identity fields (from DB)
  brandStatement: string;
  narrativeDna: string;
  narrativeThemes: string[];
  firstPrinciple: string;
  spike: string;
  spikeConfidence: number;
  pillars: string[];
  identitySynthesis: Record<string, unknown>;
  narrativeConfidence: number;

  // Metadata
  lastSynthesizedAt: string | null;
}

// ============================================================================
// QUERY KEYS
// ============================================================================

export const profileIdentityKeys = {
  all: ['profile', 'identity'] as const,
  byId: (id: string) => [...profileIdentityKeys.all, id] as const,
};

// ============================================================================
// TRANSFORM FUNCTION
// ============================================================================

function transformDbRow(row: Record<string, unknown>): ProfileIdentity {
  // Debug: Log raw row data
  console.log('[useProfileIdentity] transformDbRow received:', {
    brand_statement: row.brand_statement,
    narrative_dna: typeof row.narrative_dna === 'string' ? row.narrative_dna?.substring(0, 50) + '...' : row.narrative_dna,
    keys: Object.keys(row),
  });

  // Parse narrative_themes if it's a string
  let themes: string[] = [];
  if (row.narrative_themes) {
    if (Array.isArray(row.narrative_themes)) {
      themes = row.narrative_themes as string[];
    } else if (typeof row.narrative_themes === 'string') {
      try {
        themes = JSON.parse(row.narrative_themes);
      } catch {
        themes = [];
      }
    }
  }

  // Parse pillars if it's a string
  let pillars: string[] = [];
  if (row.pillars) {
    if (Array.isArray(row.pillars)) {
      pillars = row.pillars as string[];
    } else if (typeof row.pillars === 'string') {
      try {
        pillars = JSON.parse(row.pillars);
      } catch {
        pillars = [];
      }
    }
  }

  // Parse identity_synthesis if it's a string
  let identitySynthesis: Record<string, unknown> = {};
  if (row.identity_synthesis) {
    if (typeof row.identity_synthesis === 'object') {
      identitySynthesis = row.identity_synthesis as Record<string, unknown>;
    } else if (typeof row.identity_synthesis === 'string') {
      try {
        identitySynthesis = JSON.parse(row.identity_synthesis);
      } catch {
        identitySynthesis = {};
      }
    }
  }

  return {
    id: row.id as string,
    userId: row.user_id as string | null,
    name: row.name as string | null,
    email: row.email as string | null,
    grade: row.grade as number | null,
    archetypeId: row.archetype_id as string | null,
    archetypeName: row.archetype_name as string | null,
    archetypeConfidence: (row.archetype_confidence as number) || 0,
    brandStatement: (row.brand_statement as string) || '',
    narrativeDna: (row.narrative_dna as string) || '',
    narrativeThemes: themes,
    firstPrinciple: (row.first_principle as string) || '',
    spike: (row.spike as string) || '',
    spikeConfidence: (row.spike_confidence as number) || 0,
    pillars: pillars,
    identitySynthesis: identitySynthesis,
    narrativeConfidence: (row.narrative_confidence as number) || 0,
    lastSynthesizedAt: row.last_synthesized_at as string | null,
  };
}

// ============================================================================
// HOOKS
// ============================================================================

/**
 * Fetch profile identity from database.
 * Use this for brand_statement, spike, pillars - NOT for scoring data.
 */
export function useProfileIdentity(profileId: string | null) {
  return useQuery({
    queryKey: profileIdentityKeys.byId(profileId || ''),
    queryFn: async (): Promise<ProfileIdentity | null> => {
      if (!profileId) return null;

      try {
        const supabase = getSupabaseClient();
        const { data, error } = await supabase
          .rpc('get_profile_identity', { p_profile_id: profileId });

        if (error) {
          console.error('[useProfileIdentity] RPC error:', error);
          // Return null instead of throwing - graceful degradation
          return null;
        }

        if (!data || data.length === 0) {
          console.log('[useProfileIdentity] No data found for profile:', profileId);
          return null;
        }

        return transformDbRow(data[0]);
      } catch (err) {
        console.error('[useProfileIdentity] Exception:', err);
        return null;
      }
    },
    enabled: !!profileId,
    staleTime: 30 * 1000, // 30 seconds - shorter for freshness
    gcTime: 5 * 60 * 1000, // 5 minutes cache
    retry: 1, // Only retry once
    refetchOnWindowFocus: false,
  });
}

/**
 * Hook to invalidate profile identity cache.
 * Call this after generating new narrative.
 */
export function useInvalidateProfileIdentity() {
  const queryClient = useQueryClient();

  return (profileId: string) => {
    queryClient.invalidateQueries({
      queryKey: profileIdentityKeys.byId(profileId),
    });
    console.log('[useProfileIdentity] Cache invalidated for:', profileId);
  };
}

/**
 * Combined hook that provides both data and invalidation.
 */
export function useProfileIdentityWithInvalidation(profileId: string | null) {
  const query = useProfileIdentity(profileId);
  const invalidate = useInvalidateProfileIdentity();

  return {
    ...query,
    invalidate: () => profileId && invalidate(profileId),
  };
}

/**
 * Prefetch profile identity for a given profile ID.
 * Useful for prefetching before navigation.
 */
export function usePrefetchProfileIdentity() {
  const queryClient = useQueryClient();

  return async (profileId: string) => {
    await queryClient.prefetchQuery({
      queryKey: profileIdentityKeys.byId(profileId),
      queryFn: async () => {
        const supabase = getSupabaseClient();
        const { data, error } = await supabase
          .rpc('get_profile_identity', { p_profile_id: profileId });

        if (error || !data || data.length === 0) return null;
        return transformDbRow(data[0]);
      },
      staleTime: 30 * 1000,
    });
  };
}
