/**
 * Auth Provider - FIXED VERSION
 * 
 * Key fixes:
 * 1. Uses window-based singleton for Supabase client
 * 2. Properly propagates auth state changes
 * 3. Handles React 18 Strict Mode double-mounting
 * 4. Separate loading states for initial load vs operations
 */

'use client';

import React, { 
  createContext, 
  useContext, 
  useEffect, 
  useState, 
  useCallback, 
  useMemo,
  useRef,
} from 'react';
import { useRouter } from 'next/navigation';
import { getSupabaseBrowserClient, clearSupabaseSingleton } from './supabase-browser';
import type { User, Session, AuthChangeEvent } from '@supabase/supabase-js';

// =============================================================================
// TYPES
// =============================================================================

export type UserRole = 'student' | 'coach' | 'admin';

export interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  first_name: string | null;
  last_name: string | null;
  avatar_url: string | null;
  grade?: number | null;
  high_school?: string | null;
  organization?: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
}

interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
  isInitialized: boolean;  // Has initial check completed?
  isLoading: boolean;      // Is an operation in progress?
  isAuthenticated: boolean;
  error: string | null;
}

interface AuthContextValue extends AuthState {
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signUp: (email: string, password: string, role: UserRole, metadata?: Partial<UserProfile>) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: string | null }>;
  updatePassword: (newPassword: string) => Promise<{ error: string | null }>;
  updateProfile: (updates: Partial<UserProfile>) => Promise<{ error: string | null }>;
  refreshSession: () => Promise<void>;
  hasRole: (role: UserRole) => boolean;
  isStudent: () => boolean;
  isCoach: () => boolean;
  isAdmin: () => boolean;
}

// =============================================================================
// CONTEXT
// =============================================================================

const AuthContext = createContext<AuthContextValue | null>(null);

// =============================================================================
// PROVIDER
// =============================================================================

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter();
  
  // Track if we've initialized (prevents double-init in Strict Mode)
  const isInitializing = useRef(false);
  const subscriptionRef = useRef<{ unsubscribe: () => void } | null>(null);
  
  // Auth state
  const [state, setState] = useState<AuthState>({
    user: null,
    profile: null,
    session: null,
    isInitialized: false,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  // Get Supabase client (singleton)
  const supabase = useMemo(() => getSupabaseBrowserClient(), []);

  // ===========================================================================
  // FETCH PROFILE
  // ===========================================================================

  const fetchProfile = useCallback(async (userId: string): Promise<UserProfile | null> => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (error) {
        console.error('[Auth] Profile fetch error:', error);
        return null;
      }

      return data as UserProfile;
    } catch (err) {
      console.error('[Auth] Profile fetch exception:', err);
      return null;
    }
  }, [supabase]);

  // ===========================================================================
  // UPDATE STATE HELPER
  // ===========================================================================

  const updateAuthState = useCallback(async (session: Session | null) => {
    console.log('[Auth] Updating state, session:', !!session);
    
    if (session?.user) {
      const profile = await fetchProfile(session.user.id);
      
      setState({
        user: session.user,
        profile,
        session,
        isInitialized: true,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      });
      
      console.log('[Auth] State updated: authenticated');
    } else {
      setState({
        user: null,
        profile: null,
        session: null,
        isInitialized: true,
        isLoading: false,
        isAuthenticated: false,
        error: null,
      });
      
      console.log('[Auth] State updated: not authenticated');
    }
  }, [fetchProfile]);

  // ===========================================================================
  // INITIALIZATION
  // ===========================================================================

  useEffect(() => {
    // Prevent double initialization
    if (isInitializing.current) {
      console.log('[Auth] Already initializing, skipping');
      return;
    }
    isInitializing.current = true;

    console.log('[Auth] Initializing...');

    // Initial session check
    const initializeAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('[Auth] getSession error:', error);
          setState(prev => ({ 
            ...prev, 
            isInitialized: true, 
            isLoading: false,
            error: error.message 
          }));
          return;
        }

        await updateAuthState(session);
      } catch (err) {
        console.error('[Auth] Init exception:', err);
        setState(prev => ({ 
          ...prev, 
          isInitialized: true, 
          isLoading: false 
        }));
      }
    };

    initializeAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        console.log('[Auth] onAuthStateChange:', event);
        
        // Handle specific events
        switch (event) {
          case 'SIGNED_IN':
          case 'TOKEN_REFRESHED':
          case 'USER_UPDATED':
            await updateAuthState(session);
            break;
            
          case 'SIGNED_OUT':
            setState({
              user: null,
              profile: null,
              session: null,
              isInitialized: true,
              isLoading: false,
              isAuthenticated: false,
              error: null,
            });
            break;
            
          case 'PASSWORD_RECOVERY':
            // Don't change auth state for password recovery
            console.log('[Auth] Password recovery event');
            break;
            
          case 'INITIAL_SESSION':
            // Already handled by getSession()
            break;
        }
      }
    );

    subscriptionRef.current = subscription;

    // Cleanup
    return () => {
      console.log('[Auth] Cleaning up subscription');
      subscription.unsubscribe();
      isInitializing.current = false;
    };
  }, [supabase, updateAuthState]);

  // ===========================================================================
  // AUTH ACTIONS
  // ===========================================================================

  const signIn = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        setState(prev => ({ ...prev, isLoading: false, error: error.message }));
        return { error: error.message };
      }

      // State will be updated by onAuthStateChange
      return { error: null };
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Sign in failed';
      setState(prev => ({ ...prev, isLoading: false, error: message }));
      return { error: message };
    }
  }, [supabase]);

  const signUp = useCallback(async (
    email: string,
    password: string,
    role: UserRole,
    metadata?: Partial<UserProfile>
  ) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            role,
            first_name: metadata?.first_name || null,
            last_name: metadata?.last_name || null,
          },
        },
      });

      if (error) {
        setState(prev => ({ ...prev, isLoading: false, error: error.message }));
        return { error: error.message };
      }

      setState(prev => ({ ...prev, isLoading: false }));
      return { error: null };
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Sign up failed';
      setState(prev => ({ ...prev, isLoading: false, error: message }));
      return { error: message };
    }
  }, [supabase]);

  const signOut = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true }));
    
    try {
      await supabase.auth.signOut();
      clearSupabaseSingleton(); // Clear singleton on logout
      router.push('/');
    } catch (err) {
      console.error('[Auth] Sign out error:', err);
    }
    
    // State will be updated by onAuthStateChange
  }, [supabase, router]);

  const resetPassword = useCallback(async (email: string) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/callback`,
      });

      if (error) return { error: error.message };
      return { error: null };
    } catch (err) {
      return { error: err instanceof Error ? err.message : 'Password reset failed' };
    }
  }, [supabase]);

  const updatePassword = useCallback(async (newPassword: string) => {
    try {
      const { error } = await supabase.auth.updateUser({ password: newPassword });
      if (error) return { error: error.message };
      return { error: null };
    } catch (err) {
      return { error: err instanceof Error ? err.message : 'Password update failed' };
    }
  }, [supabase]);

  const updateProfile = useCallback(async (updates: Partial<UserProfile>) => {
    if (!state.user) return { error: 'Not authenticated' };

    try {
      const { error } = await supabase
        .from('profiles')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', state.user.id);

      if (error) return { error: error.message };

      // Refresh profile
      const profile = await fetchProfile(state.user.id);
      setState(prev => ({ ...prev, profile }));

      return { error: null };
    } catch (err) {
      return { error: err instanceof Error ? err.message : 'Profile update failed' };
    }
  }, [supabase, state.user, fetchProfile]);

  const refreshSession = useCallback(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    await updateAuthState(session);
  }, [supabase, updateAuthState]);

  // ===========================================================================
  // ROLE CHECKS
  // ===========================================================================

  const hasRole = useCallback((role: UserRole) => state.profile?.role === role, [state.profile]);
  const isStudent = useCallback(() => hasRole('student'), [hasRole]);
  const isCoach = useCallback(() => hasRole('coach'), [hasRole]);
  const isAdmin = useCallback(() => hasRole('admin'), [hasRole]);

  // ===========================================================================
  // CONTEXT VALUE
  // ===========================================================================

  const value = useMemo<AuthContextValue>(() => ({
    ...state,
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    updateProfile,
    refreshSession,
    hasRole,
    isStudent,
    isCoach,
    isAdmin,
  }), [
    state,
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    updateProfile,
    refreshSession,
    hasRole,
    isStudent,
    isCoach,
    isAdmin,
  ]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// =============================================================================
// HOOKS
// =============================================================================

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function useUser(): User | null {
  const { user } = useAuth();
  return user;
}

export function useProfile(): UserProfile | null {
  const { profile } = useAuth();
  return profile;
}

export function useIsAuthenticated(): boolean {
  const { isAuthenticated, isInitialized } = useAuth();
  return isInitialized && isAuthenticated;
}

export function useUserRole(): UserRole | null {
  const { profile } = useAuth();
  return profile?.role || null;
}

/**
 * Hook that waits for auth to initialize before returning state.
 * Useful in components that need to make decisions based on auth.
 */
export function useAuthReady(): { isReady: boolean; isAuthenticated: boolean } {
  const { isInitialized, isAuthenticated } = useAuth();
  return { isReady: isInitialized, isAuthenticated };
}
