/**
 * Auth Context Provider
 * 
 * Provides authentication state and actions throughout the app.
 * Uses Supabase Auth with automatic token refresh and session management.
 */

'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { createBrowserSupabaseClient } from '@/lib/auth/supabase-browser';
import type { User, Session, AuthChangeEvent } from '@supabase/supabase-js';
import type { AuthContextValue, UserProfile, UserRole, AuthState } from '@/types/auth';

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
  const [supabase] = useState(() => createBrowserSupabaseClient());
  
  const [state, setState] = useState<AuthState>({
    user: null,
    profile: null,
    session: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  // ===========================================================================
  // FETCH USER PROFILE
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
  // INITIALIZE AUTH STATE
  // ===========================================================================

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Get current session
        const { data: { session }, error } = await supabase.auth.getSession();

        if (error) {
          console.error('[Auth] Session error:', error);
          setState(prev => ({ ...prev, isLoading: false, error: error.message }));
          return;
        }

        if (session?.user) {
          const profile = await fetchProfile(session.user.id);
          setState({
            user: session.user,
            profile,
            session,
            isLoading: false,
            isAuthenticated: true,
            error: null,
          });
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (err) {
        console.error('[Auth] Init error:', err);
        setState(prev => ({ ...prev, isLoading: false }));
      }
    };

    initializeAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        console.log('[Auth] State change:', event);

        if (event === 'SIGNED_IN' && session?.user) {
          const profile = await fetchProfile(session.user.id);
          setState({
            user: session.user,
            profile,
            session,
            isLoading: false,
            isAuthenticated: true,
            error: null,
          });
        } else if (event === 'SIGNED_OUT') {
          setState({
            user: null,
            profile: null,
            session: null,
            isLoading: false,
            isAuthenticated: false,
            error: null,
          });
        } else if (event === 'TOKEN_REFRESHED' && session) {
          setState(prev => ({ ...prev, session }));
        }
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [supabase, fetchProfile]);

  // ===========================================================================
  // AUTH ACTIONS
  // ===========================================================================

  const signIn = useCallback(async (email: string, password: string): Promise<{ error: string | null }> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        setState(prev => ({ ...prev, isLoading: false, error: error.message }));
        return { error: error.message };
      }

      // Update last login
      if (data.user) {
        await supabase
          .from('profiles')
          .update({ last_login_at: new Date().toISOString() })
          .eq('id', data.user.id);
      }

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
  ): Promise<{ error: string | null }> => {
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

      // Create profile record
      if (data.user) {
        const { error: profileError } = await supabase.from('profiles').insert({
          id: data.user.id,
          email: data.user.email!,
          role,
          first_name: metadata?.first_name || null,
          last_name: metadata?.last_name || null,
          grade: metadata?.grade || null,
          high_school: metadata?.high_school || null,
          organization: metadata?.organization || null,
          is_active: true,
          is_verified: false,
        });

        if (profileError) {
          console.error('[Auth] Profile creation error:', profileError);
        }
      }

      setState(prev => ({ ...prev, isLoading: false }));
      return { error: null };
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Sign up failed';
      setState(prev => ({ ...prev, isLoading: false, error: message }));
      return { error: message };
    }
  }, [supabase]);

  const signOut = useCallback(async (): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true }));
    
    try {
      await supabase.auth.signOut();
      router.push('/');
    } catch (err) {
      console.error('[Auth] Sign out error:', err);
    } finally {
      setState({
        user: null,
        profile: null,
        session: null,
        isLoading: false,
        isAuthenticated: false,
        error: null,
      });
    }
  }, [supabase, router]);

  const resetPassword = useCallback(async (email: string): Promise<{ error: string | null }> => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password/confirm`,
      });

      if (error) return { error: error.message };
      return { error: null };
    } catch (err) {
      return { error: err instanceof Error ? err.message : 'Password reset failed' };
    }
  }, [supabase]);

  const updatePassword = useCallback(async (newPassword: string): Promise<{ error: string | null }> => {
    try {
      const { error } = await supabase.auth.updateUser({ password: newPassword });
      if (error) return { error: error.message };
      return { error: null };
    } catch (err) {
      return { error: err instanceof Error ? err.message : 'Password update failed' };
    }
  }, [supabase]);

  // ===========================================================================
  // PROFILE ACTIONS
  // ===========================================================================

  const updateProfile = useCallback(async (updates: Partial<UserProfile>): Promise<{ error: string | null }> => {
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

  const refreshProfile = useCallback(async (): Promise<void> => {
    if (!state.user) return;
    const profile = await fetchProfile(state.user.id);
    setState(prev => ({ ...prev, profile }));
  }, [state.user, fetchProfile]);

  // ===========================================================================
  // ROLE CHECKS
  // ===========================================================================

  const hasRole = useCallback((role: UserRole): boolean => {
    return state.profile?.role === role;
  }, [state.profile]);

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
    refreshProfile,
    hasRole,
    isStudent,
    isCoach,
    isAdmin,
  }), [state, signIn, signUp, signOut, resetPassword, updatePassword, updateProfile, refreshProfile, hasRole, isStudent, isCoach, isAdmin]);

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
  const { isAuthenticated } = useAuth();
  return isAuthenticated;
}

export function useUserRole(): UserRole | null {
  const { profile } = useAuth();
  return profile?.role || null;
}
