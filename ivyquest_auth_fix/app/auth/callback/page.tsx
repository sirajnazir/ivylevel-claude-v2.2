/**
 * Client-Side Auth Callback Page
 * 
 * CRITICAL: This page does NOT use useAuth() context.
 * It directly interacts with Supabase to avoid race conditions.
 * 
 * Handles hash-based callbacks:
 * - Password recovery: #access_token=...&type=recovery
 * - Magic link: #access_token=...&type=magiclink
 * - Email confirmation: #access_token=...&type=signup
 */

'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { createBrowserClient } from '@supabase/ssr';
import { Loader2, CheckCircle, AlertCircle, KeyRound } from 'lucide-react';

// =============================================================================
// TYPES
// =============================================================================

type CallbackStatus = 
  | 'initializing'    // Just mounted
  | 'processing'      // Parsing hash, setting session
  | 'success'         // Session established
  | 'password_reset'  // Recovery flow - needs password change
  | 'error';          // Something went wrong

type CallbackType = 'recovery' | 'signup' | 'magiclink' | 'invite' | null;

// =============================================================================
// COMPONENT
// =============================================================================

export default function AuthCallbackPage() {
  const router = useRouter();
  const [status, setStatus] = useState<CallbackStatus>('initializing');
  const [callbackType, setCallbackType] = useState<CallbackType>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  
  // Prevent double processing in React Strict Mode
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Only run once
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    processCallback();
  }, []);

  /**
   * Main callback processing logic
   * Does NOT use useAuth() - directly uses Supabase client
   */
  async function processCallback() {
    setStatus('processing');
    
    // Create a fresh Supabase client for this callback
    const supabase = createBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );

    try {
      // Step 1: Check if we have hash params
      const hash = window.location.hash;
      console.log('[Callback] Hash present:', !!hash);

      if (!hash || hash.length < 2) {
        // No hash - check for existing session
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session) {
          console.log('[Callback] Existing session found');
          setStatus('success');
          setUserEmail(session.user.email || null);
          
          // Redirect to dashboard after brief delay
          setTimeout(() => router.push('/dashboard'), 1500);
          return;
        }

        // No hash, no session - redirect to login
        console.log('[Callback] No hash or session, redirecting to login');
        router.push('/auth/login');
        return;
      }

      // Step 2: Parse hash params
      const hashParams = new URLSearchParams(hash.substring(1));
      const accessToken = hashParams.get('access_token');
      const refreshToken = hashParams.get('refresh_token');
      const type = hashParams.get('type') as CallbackType;
      const errorParam = hashParams.get('error');
      const errorDescription = hashParams.get('error_description');

      console.log('[Callback] Parsed:', { 
        hasAccessToken: !!accessToken, 
        type, 
        error: errorParam 
      });

      // Store the callback type
      setCallbackType(type);

      // Step 3: Handle errors in hash
      if (errorParam) {
        console.error('[Callback] Error in hash:', errorParam, errorDescription);
        setStatus('error');
        setErrorMessage(errorDescription || errorParam);
        return;
      }

      // Step 4: Set session if we have tokens
      if (accessToken) {
        console.log('[Callback] Setting session with tokens...');
        
        const { data, error: sessionError } = await supabase.auth.setSession({
          access_token: accessToken,
          refresh_token: refreshToken || '',
        });

        if (sessionError) {
          console.error('[Callback] setSession error:', sessionError);
          setStatus('error');
          setErrorMessage(sessionError.message);
          return;
        }

        if (!data.session) {
          console.error('[Callback] No session returned');
          setStatus('error');
          setErrorMessage('Failed to establish session');
          return;
        }

        console.log('[Callback] Session established for:', data.session.user.email);
        setUserEmail(data.session.user.email || null);

        // Step 5: Handle based on callback type
        if (type === 'recovery') {
          console.log('[Callback] Password recovery flow');
          setStatus('password_reset');
          // Don't redirect - show password reset form
          return;
        }

        // For other types (signup, magiclink, invite)
        setStatus('success');
        
        // Clear hash from URL (prevents issues on refresh)
        window.history.replaceState(null, '', window.location.pathname);
        
        // Redirect after brief delay
        setTimeout(() => {
          router.push('/dashboard');
        }, 1500);
        return;
      }

      // Step 6: No tokens in hash - try to get existing session
      // (Supabase might have auto-processed the hash)
      console.log('[Callback] No tokens in hash, checking for auto-processed session...');
      
      // Wait a moment for Supabase to process
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session) {
        console.log('[Callback] Found auto-processed session');
        setUserEmail(session.user.email || null);
        
        if (type === 'recovery') {
          setStatus('password_reset');
          return;
        }
        
        setStatus('success');
        setTimeout(() => router.push('/dashboard'), 1500);
        return;
      }

      // Nothing worked
      console.log('[Callback] No session established');
      setStatus('error');
      setErrorMessage('Unable to verify your session. Please try again.');

    } catch (err) {
      console.error('[Callback] Exception:', err);
      setStatus('error');
      setErrorMessage(err instanceof Error ? err.message : 'An unexpected error occurred');
    }
  }

  // ==========================================================================
  // RENDER
  // ==========================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-pink-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
        
        {/* Initializing / Processing */}
        {(status === 'initializing' || status === 'processing') && (
          <>
            <Loader2 className="w-12 h-12 text-purple-600 animate-spin mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              Verifying your session...
            </h1>
            <p className="text-gray-600">
              Please wait while we confirm your authentication.
            </p>
          </>
        )}

        {/* Success */}
        {status === 'success' && (
          <>
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              {callbackType === 'signup' ? 'Email Verified!' : 'Welcome Back!'}
            </h1>
            <p className="text-gray-600 mb-4">
              {userEmail && <>Signed in as <strong>{userEmail}</strong></>}
            </p>
            <p className="text-sm text-gray-500">
              Redirecting to your dashboard...
            </p>
          </>
        )}

        {/* Password Reset Flow */}
        {status === 'password_reset' && (
          <PasswordResetForm 
            userEmail={userEmail}
            onSuccess={() => {
              setStatus('success');
              setTimeout(() => router.push('/dashboard'), 1500);
            }}
            onError={(msg) => {
              setStatus('error');
              setErrorMessage(msg);
            }}
          />
        )}

        {/* Error */}
        {status === 'error' && (
          <>
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-10 h-10 text-red-600" />
            </div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              Authentication Failed
            </h1>
            <p className="text-gray-600 mb-6">
              {errorMessage || 'Something went wrong. Please try again.'}
            </p>
            <button
              onClick={() => router.push('/auth/login')}
              className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
            >
              Return to Login
            </button>
          </>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// PASSWORD RESET FORM (Inline Component)
// =============================================================================

interface PasswordResetFormProps {
  userEmail: string | null;
  onSuccess: () => void;
  onError: (message: string) => void;
}

function PasswordResetForm({ userEmail, onSuccess, onError }: PasswordResetFormProps) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (password.length < 8) {
      onError('Password must be at least 8 characters');
      return;
    }
    
    if (password !== confirmPassword) {
      onError('Passwords do not match');
      return;
    }

    setIsSubmitting(true);

    try {
      // Create fresh client
      const supabase = createBrowserClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
      );

      const { error } = await supabase.auth.updateUser({ password });

      if (error) {
        console.error('[Password Reset] Error:', error);
        onError(error.message);
        setIsSubmitting(false);
        return;
      }

      console.log('[Password Reset] Success');
      onSuccess();
      
    } catch (err) {
      console.error('[Password Reset] Exception:', err);
      onError(err instanceof Error ? err.message : 'Failed to update password');
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <KeyRound className="w-10 h-10 text-purple-600" />
      </div>
      <h1 className="text-xl font-semibold text-gray-900 mb-2">
        Set New Password
      </h1>
      <p className="text-gray-600 mb-6">
        {userEmail && <>Enter a new password for <strong>{userEmail}</strong></>}
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 text-left">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            New Password
          </label>
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={isSubmitting}
            minLength={8}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Confirm Password
          </label>
          <input
            type={showPassword ? 'text' : 'password'}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={isSubmitting}
            minLength={8}
            required
          />
        </div>

        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={showPassword}
            onChange={(e) => setShowPassword(e.target.checked)}
            className="rounded border-gray-300"
          />
          Show passwords
        </label>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:shadow-lg disabled:opacity-50 transition-all flex items-center justify-center gap-2"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Updating...
            </>
          ) : (
            'Update Password'
          )}
        </button>
      </form>
    </>
  );
}
