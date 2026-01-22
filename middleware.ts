/**
 * Auth Middleware
 * 
 * Server-side authentication checks for protected routes.
 * Runs before page renders to ensure user is authenticated.
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { createServerClient } from '@supabase/ssr';

// =============================================================================
// ROUTE CONFIGURATION
// =============================================================================

// Routes that require authentication
const PROTECTED_ROUTES = [
  '/dashboard',
  '/assessment',
  '/quest', // Legacy route (deprecated)
  '/reset', // Utility route for deleting user data (requires auth)
  '/coach',
  '/admin',
  '/account',
];

// Routes that should redirect to dashboard if already authenticated
const AUTH_ROUTES = [
  '/auth/login',
  '/auth/signup',
];

// Public routes (no auth check needed)
const PUBLIC_ROUTES = [
  '/',
  '/auth/reset-password',
  '/auth/callback',
  '/api',
  '/logout', // Utility route for signing out (no auth needed)
];

// =============================================================================
// MIDDLEWARE
// =============================================================================

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip middleware for static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname.includes('.') ||
    pathname.startsWith('/api/')
  ) {
    return NextResponse.next();
  }

  // Create Supabase client for middleware
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            request.cookies.set(name, value);
            response.cookies.set(name, value, options);
          });
        },
      },
    }
  );

  // Get session
  const { data: { session } } = await supabase.auth.getSession();

  // Check if route is protected
  const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route));
  const isAuthRoute = AUTH_ROUTES.some(route => pathname.startsWith(route));

  // =========================================================================
  // REDIRECT LOGIC
  // =========================================================================

  // Protected route + no session = redirect to login
  if (isProtectedRoute && !session) {
    const loginUrl = new URL('/auth/login', request.url);
    loginUrl.searchParams.set('returnUrl', pathname);
    
    // Determine role from pathname for better UX
    if (pathname.startsWith('/coach')) {
      loginUrl.searchParams.set('role', 'coach');
    } else if (pathname.startsWith('/admin')) {
      loginUrl.searchParams.set('role', 'admin');
    } else {
      loginUrl.searchParams.set('role', 'student');
    }
    
    return NextResponse.redirect(loginUrl);
  }

  // Auth route + session = redirect to dashboard
  if (isAuthRoute && session) {
    // Get user profile to determine dashboard
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', session.user.id)
      .single();

    const dashboardUrl = getDashboardUrl(profile?.role, request.url);
    return NextResponse.redirect(dashboardUrl);
  }

  // =========================================================================
  // ROLE-BASED ACCESS CONTROL
  // =========================================================================

  if (session) {
    // Get user role from profile
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', session.user.id)
      .single();

    const userRole = profile?.role;

    // Coach routes require coach or admin role
    if (pathname.startsWith('/coach') && !['coach', 'admin'].includes(userRole)) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    // Admin routes require admin role
    if (pathname.startsWith('/admin') && userRole !== 'admin') {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    // Student routes allow only students
    if ((pathname.startsWith('/dashboard') || pathname.startsWith('/assessment') || pathname.startsWith('/quest')) &&
        userRole && !['student', 'admin'].includes(userRole)) {
      return NextResponse.redirect(new URL('/coach', request.url));
    }
  }

  return response;
}

// =============================================================================
// CONFIG
// =============================================================================

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};

// =============================================================================
// HELPERS
// =============================================================================

function getDashboardUrl(role: string | undefined, baseUrl: string): URL {
  switch (role) {
    case 'coach':
      return new URL('/coach', baseUrl);
    case 'admin':
      return new URL('/admin', baseUrl);
    case 'student':
    default:
      return new URL('/dashboard', baseUrl);
  }
}
