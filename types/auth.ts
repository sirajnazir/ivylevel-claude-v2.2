/**
 * Authentication Types
 * 
 * Defines user roles, permissions, and auth state types
 */

import type { User, Session } from '@supabase/supabase-js';

// =============================================================================
// USER ROLES
// =============================================================================

export type UserRole = 'student' | 'coach' | 'admin';

export const USER_ROLES: Record<UserRole, { label: string; description: string; color: string }> = {
  student: {
    label: 'Student',
    description: 'Complete assessments and view your personalized game plan',
    color: '#8B5CF6', // Purple
  },
  coach: {
    label: 'Coach',
    description: 'Manage students, track progress, and provide guidance',
    color: '#10B981', // Green
  },
  admin: {
    label: 'Admin',
    description: 'Full system access, user management, and analytics',
    color: '#F59E0B', // Amber
  },
};

// =============================================================================
// USER PROFILE (Extended from Supabase User)
// =============================================================================

export interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  first_name: string | null;
  last_name: string | null;
  avatar_url: string | null;
  phone: string | null;
  
  // Student-specific
  grade?: number | null;
  high_school?: string | null;
  target_graduation?: number | null;
  
  // Coach-specific
  organization?: string | null;
  specialization?: string | null;
  max_students?: number | null;
  
  // Metadata
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
  is_active: boolean;
  is_verified: boolean;
  
  // Settings
  notification_preferences?: NotificationPreferences;
  timezone?: string;
}

export interface NotificationPreferences {
  email_updates: boolean;
  session_reminders: boolean;
  weekly_digest: boolean;
  marketing: boolean;
}

// =============================================================================
// AUTH STATE
// =============================================================================

export interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

export interface AuthContextValue extends AuthState {
  // Auth actions
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signUp: (email: string, password: string, role: UserRole, metadata?: Partial<UserProfile>) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: string | null }>;
  updatePassword: (newPassword: string) => Promise<{ error: string | null }>;
  
  // Profile actions
  updateProfile: (updates: Partial<UserProfile>) => Promise<{ error: string | null }>;
  refreshProfile: () => Promise<void>;
  
  // Role checks
  hasRole: (role: UserRole) => boolean;
  isStudent: () => boolean;
  isCoach: () => boolean;
  isAdmin: () => boolean;
}

// =============================================================================
// AUTH FORMS
// =============================================================================

export interface LoginFormData {
  email: string;
  password: string;
  remember: boolean;
}

export interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  acceptTerms: boolean;
  
  // Role-specific
  grade?: number;
  highSchool?: string;
  organization?: string;
}

export interface ResetPasswordFormData {
  email: string;
}

// =============================================================================
// ROUTE PERMISSIONS
// =============================================================================

export interface RoutePermission {
  path: string;
  allowedRoles: UserRole[];
  requireAuth: boolean;
  redirectTo?: string;
}

export const ROUTE_PERMISSIONS: RoutePermission[] = [
  // Public routes
  { path: '/', allowedRoles: [], requireAuth: false },
  { path: '/auth/login', allowedRoles: [], requireAuth: false },
  { path: '/auth/signup', allowedRoles: [], requireAuth: false },
  { path: '/auth/reset-password', allowedRoles: [], requireAuth: false },
  
  // Student routes
  { path: '/quest', allowedRoles: ['student'], requireAuth: true, redirectTo: '/auth/login?role=student' },
  { path: '/dashboard', allowedRoles: ['student'], requireAuth: true, redirectTo: '/auth/login?role=student' },
  
  // Coach routes
  { path: '/coach', allowedRoles: ['coach', 'admin'], requireAuth: true, redirectTo: '/auth/login?role=coach' },
  
  // Admin routes
  { path: '/admin', allowedRoles: ['admin'], requireAuth: true, redirectTo: '/auth/login?role=admin' },
];

// =============================================================================
// SESSION CONFIG
// =============================================================================

export const SESSION_CONFIG = {
  // Session timeout in milliseconds (30 minutes)
  TIMEOUT_MS: 30 * 60 * 1000,
  
  // Warning before timeout (5 minutes)
  WARNING_BEFORE_MS: 5 * 60 * 1000,
  
  // Activity events to track
  ACTIVITY_EVENTS: ['mousedown', 'keydown', 'scroll', 'touchstart'] as const,
  
  // Token refresh threshold (5 minutes before expiry)
  REFRESH_THRESHOLD_MS: 5 * 60 * 1000,
};

// =============================================================================
// DATABASE TYPES (for Supabase)
// =============================================================================

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: UserProfile;
        Insert: Omit<UserProfile, 'created_at' | 'updated_at'>;
        Update: Partial<Omit<UserProfile, 'id' | 'created_at'>>;
      };
      sessions: {
        Row: {
          id: string;
          user_id: string;
          device_info: string | null;
          ip_address: string | null;
          last_active_at: string;
          created_at: string;
          is_current: boolean;
        };
        Insert: Omit<Database['public']['Tables']['sessions']['Row'], 'id' | 'created_at'>;
        Update: Partial<Omit<Database['public']['Tables']['sessions']['Row'], 'id'>>;
      };
    };
  };
}
