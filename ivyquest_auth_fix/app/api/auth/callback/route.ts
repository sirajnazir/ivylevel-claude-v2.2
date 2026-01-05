/**
 * Auth Callback API Route (Server-Side)
 * 
 * Handles OAuth and password recovery callbacks at the server level.
 * This bypasses React Context timing issues entirely.
 * 
 * URL: /api/auth/callback
 */

import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  
  // Get the authorization code from query params (OAuth flow)
  const code = requestUrl.searchParams.get('code');
  
  // Get error if any
  const error = requestUrl.searchParams.get('error');
  const errorDescription = requestUrl.searchParams.get('error_description');
  
  // Determine the callback type
  const type = requestUrl.searchParams.get('type'); // 'recovery', 'signup', 'invite'
  
  // Get return URL (where to redirect after auth)
  const returnUrl = requestUrl.searchParams.get('returnUrl') || '/dashboard';

  console.log('[Auth Callback API] Processing:', { code: !!code, type, error });

  // Handle errors from Supabase
  if (error) {
    console.error('[Auth Callback API] Error:', error, errorDescription);
    return NextResponse.redirect(
      new URL(`/auth/login?error=${encodeURIComponent(errorDescription || error)}`, request.url)
    );
  }

  // Create Supabase server client
  const cookieStore = await cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch (error) {
            // Called from Server Component - cookies are read-only
            console.error('[Auth Callback API] Cookie set error:', error);
          }
        },
      },
    }
  );

  // Exchange code for session (OAuth flow)
  if (code) {
    try {
      const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
      
      if (exchangeError) {
        console.error('[Auth Callback API] Exchange error:', exchangeError);
        return NextResponse.redirect(
          new URL(`/auth/login?error=${encodeURIComponent(exchangeError.message)}`, request.url)
        );
      }

      console.log('[Auth Callback API] Session established for:', data.user?.email);

      // Handle different callback types
      if (type === 'recovery') {
        // Password recovery - redirect to reset password page
        return NextResponse.redirect(new URL('/auth/reset-password/confirm', request.url));
      }

      if (type === 'signup' || type === 'invite') {
        // Email confirmation - redirect to success page or dashboard
        return NextResponse.redirect(new URL('/auth/verified', request.url));
      }

      // Default: redirect to return URL or dashboard
      return NextResponse.redirect(new URL(returnUrl, request.url));
      
    } catch (err) {
      console.error('[Auth Callback API] Exception:', err);
      return NextResponse.redirect(
        new URL('/auth/login?error=Authentication+failed', request.url)
      );
    }
  }

  // No code provided - might be hash-based callback (handled client-side)
  // Redirect to client-side callback handler
  return NextResponse.redirect(new URL('/auth/callback/client', request.url));
}
