/**
 * Supabase Browser Client
 *
 * Client-side only Supabase client for use in React components.
 * This file should only be imported in client components.
 */

import { createBrowserClient } from '@supabase/ssr';

// =============================================================================
// ENVIRONMENT VARIABLES
// =============================================================================

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// =============================================================================
// BROWSER CLIENT (Client Components Only)
// =============================================================================

export function createBrowserSupabaseClient() {
  if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('[Supabase] Missing environment variables. Auth will not work.');
    // Return a dummy client that won't crash but won't work either
    return createBrowserClient('http://localhost', 'dummy-key');
  }
  return createBrowserClient(supabaseUrl, supabaseAnonKey);
}
