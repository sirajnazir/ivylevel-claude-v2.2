/**
 * Auth Library - Barrel Export (Simplified Beta)
 *
 * For beta with 10-20 users:
 * - Simple email/password login only
 * - No self-signup, no password reset callbacks
 * - Admin creates accounts in Supabase Dashboard
 */

// Auth Provider & Hooks (client-side)
export {
  AuthProvider,
  useAuth,
  useUser,
  useProfile,
  useIsAuthenticated,
  useUserRole,
  useAuthReady,
  USER_ROLES,
  type UserRole,
  type UserProfile,
} from './AuthProvider';
