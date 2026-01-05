/**
 * Simplified Beta Auth System
 * 
 * For beta release with 10-20 users:
 * - Admin creates accounts in Supabase Dashboard
 * - Admin sends credentials to users manually
 * - Users login with email/password
 * - No self-signup, no password reset callbacks
 * 
 * This eliminates ALL callback complexity.
 */

'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { createBrowserClient } from '@supabase/ssr';
import type { User, Session } from '@supabase/supabase-js';

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
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

interface AuthContextValue extends AuthState {
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  clearError: () => void;
}

// =============================================================================
// CONTEXT
// =============================================================================

const AuthContext = createContext<AuthContextValue | null>(null);

// =============================================================================
// SIMPLE SUPABASE CLIENT (no singleton complexity)
// =============================================================================

function getSupabase() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// =============================================================================
// PROVIDER
// =============================================================================

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    profile: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  // Initialize - check for existing session
  useEffect(() => {
    let mounted = true;
    
    const init = async () => {
      const supabase = getSupabase();
      
      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (!mounted) return;
        
        if (session?.user) {
          // Fetch profile
          const { data: profile } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', session.user.id)
            .single();
          
          if (!mounted) return;
          
          setState({
            user: session.user,
            profile: profile as UserProfile,
            isLoading: false,
            isAuthenticated: true,
            error: null,
          });
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (err) {
        console.error('[Auth] Init error:', err);
        if (mounted) {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      }
    };

    init();
    
    return () => { mounted = false; };
  }, []);

  // Sign In - simple email/password, no callbacks
  const signIn = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    const supabase = getSupabase();
    
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim().toLowerCase(),
        password,
      });

      if (error) {
        setState(prev => ({ ...prev, isLoading: false, error: error.message }));
        return { error: error.message };
      }

      if (!data.user) {
        setState(prev => ({ ...prev, isLoading: false, error: 'Login failed' }));
        return { error: 'Login failed' };
      }

      // Fetch profile
      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', data.user.id)
        .single();

      setState({
        user: data.user,
        profile: profile as UserProfile,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      });

      return { error: null };
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setState(prev => ({ ...prev, isLoading: false, error: message }));
      return { error: message };
    }
  }, []);

  // Sign Out
  const signOut = useCallback(async () => {
    const supabase = getSupabase();
    await supabase.auth.signOut();
    
    setState({
      user: null,
      profile: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,
    });
    
    router.push('/');
  }, [router]);

  // Clear Error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    ...state,
    signIn,
    signOut,
    clearError,
  }), [state, signIn, signOut, clearError]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// =============================================================================
// HOOKS
// =============================================================================

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

export function useUser() {
  const { user } = useAuth();
  return user;
}

export function useProfile() {
  const { profile } = useAuth();
  return profile;
}
