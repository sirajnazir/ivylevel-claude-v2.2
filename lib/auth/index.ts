/**
 * Auth Library - Barrel Export
 */

// Supabase Browser Client (for client components)
export { createBrowserSupabaseClient } from './supabase-browser';

// Supabase Server Clients (for server components/API routes)
export {
  createServerSupabaseClient,
  createAdminClient,
  createMiddlewareClient,
} from './supabase-client';

// Auth Provider & Hooks
export {
  AuthProvider,
  useAuth,
  useUser,
  useProfile,
  useIsAuthenticated,
  useUserRole,
} from './AuthProvider';
