/**
 * Supabase Server Client Configuration
 *
 * Server-side only Supabase client for API routes and Server Components.
 * For client components, use supabase-browser.ts instead.
 */

import { createServerClient } from '@supabase/ssr';
import { createClient } from '@supabase/supabase-js';
import { cookies } from 'next/headers';

// Use a simplified Database type that's compatible with the Supabase client
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Database = any;

// =============================================================================
// ENVIRONMENT VARIABLES
// =============================================================================

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

// =============================================================================
// SERVER CLIENT (Server Components & API Routes)
// =============================================================================

export async function createServerSupabaseClient() {
  const cookieStore = await cookies();

  return createServerClient<Database>(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        } catch {
          // Called from Server Component - ignore
        }
      },
    },
  });
}

// =============================================================================
// ADMIN CLIENT (Service Role - Server Only)
// =============================================================================

export function createAdminClient() {
  if (!supabaseServiceKey) {
    throw new Error('Missing SUPABASE_SERVICE_ROLE_KEY');
  }
  return createClient<Database>(supabaseUrl, supabaseServiceKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}

// =============================================================================
// MIDDLEWARE CLIENT
// =============================================================================

export function createMiddlewareClient(request: Request) {
  let response = new Response();

  const supabase = createServerClient<Database>(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return parseCookies(request.headers.get('cookie') || '');
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value, options }) => {
          response.headers.append(
            'Set-Cookie',
            serializeCookie(name, value, options)
          );
        });
      },
    },
  });

  return { supabase, response };
}

// =============================================================================
// COOKIE UTILITIES
// =============================================================================

function parseCookies(cookieString: string): Array<{ name: string; value: string }> {
  return cookieString.split(';').map((cookie) => {
    const [name, ...rest] = cookie.trim().split('=');
    return { name, value: rest.join('=') };
  }).filter(c => c.name);
}

function serializeCookie(
  name: string,
  value: string,
  options?: { path?: string; maxAge?: number; httpOnly?: boolean; secure?: boolean; sameSite?: boolean | 'lax' | 'strict' | 'none' }
): string {
  let cookie = `${name}=${value}`;
  if (options?.path) cookie += `; Path=${options.path}`;
  if (options?.maxAge) cookie += `; Max-Age=${options.maxAge}`;
  if (options?.httpOnly) cookie += '; HttpOnly';
  if (options?.secure) cookie += '; Secure';
  if (options?.sameSite) cookie += `; SameSite=${options.sameSite}`;
  return cookie;
}
