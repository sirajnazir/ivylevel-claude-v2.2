/**
 * Supabase Browser Client - FIXED SINGLETON
 * 
 * IMPORTANT: This module exports a function that creates the client,
 * NOT the client itself. This is because:
 * 
 * 1. Next.js App Router can run modules multiple times (SSR, client, HMR)
 * 2. Module-level singletons don't survive across different render contexts
 * 3. The ONLY reliable singleton in browser is on `window`
 * 
 * Usage:
 *   const supabase = getSupabaseBrowserClient();
 */

import { createBrowserClient, type SupabaseClient } from '@supabase/ssr';

// Type for the client
type BrowserClient = SupabaseClient;

// Key for window storage
const SUPABASE_CLIENT_KEY = '__SUPABASE_CLIENT__';

// Extend Window interface
declare global {
  interface Window {
    [SUPABASE_CLIENT_KEY]?: BrowserClient;
  }
}

/**
 * Get the singleton Supabase browser client.
 * Creates one if it doesn't exist, returns existing if it does.
 */
export function getSupabaseBrowserClient(): BrowserClient {
  // Server-side: always create new (won't have window)
  if (typeof window === 'undefined') {
    return createBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );
  }

  // Client-side: use window singleton
  if (!window[SUPABASE_CLIENT_KEY]) {
    console.log('[Supabase] Creating browser client singleton');
    window[SUPABASE_CLIENT_KEY] = createBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );
  }

  return window[SUPABASE_CLIENT_KEY];
}

/**
 * Create a fresh client (for callbacks where you need isolation)
 */
export function createFreshSupabaseClient(): BrowserClient {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

/**
 * Clear the singleton (useful for testing or logout)
 */
export function clearSupabaseSingleton(): void {
  if (typeof window !== 'undefined') {
    delete window[SUPABASE_CLIENT_KEY];
  }
}
