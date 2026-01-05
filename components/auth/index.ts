/**
 * Auth Components - Barrel Export
 */

// Auth Provider & Hooks - re-export from lib
export {
  AuthProvider,
  useAuth,
  useUser,
  useProfile,
  useIsAuthenticated,
  useUserRole,
} from '@/lib/auth/AuthProvider';

// Entry Portal
export { EntryPortal } from './EntryPortal';

// Login & Signup
export { LoginPage } from './LoginPage';
export { SignupPage } from './SignupPage';

// Route Protection
export {
  ProtectedRoute,
  RoleGuard,
  StudentOnly,
  CoachOnly,
  AdminOnly,
  StaffOnly,
  RedirectIfAuthenticated,
  AuthLoadingScreen,
  getDashboardPath,
} from './ProtectedRoute';

// Re-export types
export type {
  UserRole,
  UserProfile,
  AuthState,
  AuthContextValue,
  LoginFormData,
  SignupFormData,
} from '@/types/auth';
