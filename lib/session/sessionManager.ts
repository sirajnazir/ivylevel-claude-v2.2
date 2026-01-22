/**
 * Session Manager
 *
 * Centralized session management for the IvyQuest platform.
 * Handles logout, session reset, and fresh assessment starts.
 *
 * This is the SINGLE SOURCE OF TRUTH for session lifecycle management.
 * All components should use these functions instead of directly manipulating stores.
 *
 * @version 1.0.0
 */

import { useSessionStore } from '@/lib/store/useSessionStore';
import { useStudentStore } from '@/lib/store/useStudentStore';
import { useResultsStore } from '@/lib/store/useResultsStore';
import { useInsightsStore } from '@/lib/store/useInsightsStore';

// =============================================================================
// CONSTANTS
// =============================================================================

/**
 * All localStorage keys used by the application.
 * Keep this list updated when adding new persisted stores.
 */
const STORAGE_KEYS = [
  'ivyquest-session-v10',
  'ivyquest-student-profile',
  'ivyquest-results',
  'ivyquest-frame3-operating',
  'ivyquest-twin-fleet',
  'ivyquest-insights',
] as const;

// =============================================================================
// TYPES
// =============================================================================

export interface SessionInfo {
  sessionId: string;
  userId: string | null;
  isCompleted: boolean;
  startedAt: string;
  completedAt: string | null;
}

export interface LogoutOptions {
  /** Redirect path after logout. Defaults to '/' */
  redirectTo?: string;
  /** Whether to force reload the page. Defaults to true for clean state */
  forceReload?: boolean;
}

export interface StartFreshOptions {
  /** Redirect path after reset. Defaults to '/assessment' */
  redirectTo?: string;
}

// =============================================================================
// CORE FUNCTIONS
// =============================================================================

/**
 * Clears all persisted storage.
 * Called internally by logout and startFresh.
 */
function clearAllStorage(): void {
  if (typeof window === 'undefined') return;

  STORAGE_KEYS.forEach((key) => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.warn(`[SessionManager] Failed to clear ${key}:`, error);
    }
  });

  console.log('[SessionManager] All storage cleared');
}

/**
 * Resets all Zustand stores to their initial state.
 * Called internally by logout and startFresh.
 */
function resetAllStores(): void {
  try {
    // Reset session store (generates new session ID)
    useSessionStore.getState().resetSession();

    // Reset student profile
    useStudentStore.getState().resetProfile();

    // Clear assessment results
    useResultsStore.getState().clearResults();

    // Clear insights
    useInsightsStore.getState().clearInsights();

    console.log('[SessionManager] All stores reset');
  } catch (error) {
    console.error('[SessionManager] Error resetting stores:', error);
  }
}

// =============================================================================
// PUBLIC API
// =============================================================================

/**
 * Logs out the current user and clears all session data.
 *
 * This function:
 * 1. Resets all Zustand stores to initial state
 * 2. Clears all persisted localStorage
 * 3. Optionally redirects to home page
 * 4. Optionally force reloads for clean React state
 *
 * @param options - Logout configuration options
 *
 * @example
 * ```tsx
 * import { logout } from '@/lib/session/sessionManager';
 *
 * const handleLogout = () => {
 *   logout({ redirectTo: '/' });
 * };
 * ```
 */
export function logout(options: LogoutOptions = {}): void {
  const { redirectTo = '/', forceReload = true } = options;

  console.log('[SessionManager] Logging out...');

  // Step 1: Reset all stores
  resetAllStores();

  // Step 2: Clear all storage
  clearAllStorage();

  // Step 3: Redirect and/or reload
  if (typeof window !== 'undefined') {
    if (forceReload) {
      // Force reload ensures completely clean React state
      window.location.href = redirectTo;
    } else if (redirectTo) {
      // Soft navigation (for use with Next.js router)
      window.location.pathname = redirectTo;
    }
  }
}

/**
 * Starts a fresh assessment session.
 *
 * This function:
 * 1. Clears any existing assessment data
 * 2. Generates a new session ID
 * 3. Redirects to the assessment start
 *
 * Use this when user wants to retake the assessment.
 *
 * @param options - Configuration options
 *
 * @example
 * ```tsx
 * import { startFreshAssessment } from '@/lib/session/sessionManager';
 *
 * const handleRetake = () => {
 *   startFreshAssessment({ redirectTo: '/assessment' });
 * };
 * ```
 */
export function startFreshAssessment(options: StartFreshOptions = {}): void {
  const { redirectTo = '/assessment' } = options;

  console.log('[SessionManager] Starting fresh assessment...');

  // Reset all stores and storage
  resetAllStores();
  clearAllStorage();

  // Redirect to assessment start
  if (typeof window !== 'undefined') {
    window.location.href = redirectTo;
  }
}

/**
 * Gets current session information.
 *
 * @returns Current session info or null if no session
 */
export function getSessionInfo(): SessionInfo | null {
  try {
    const state = useSessionStore.getState();
    return {
      sessionId: state.session_id,
      userId: state.user_id,
      isCompleted: state.is_completed,
      startedAt: state.started_at,
      completedAt: state.completed_at,
    };
  } catch {
    return null;
  }
}

/**
 * Checks if there is an active session.
 *
 * @returns true if session exists and is not completed
 */
export function hasActiveSession(): boolean {
  const info = getSessionInfo();
  return info !== null && !info.isCompleted;
}

/**
 * Checks if the assessment has been completed.
 *
 * @returns true if assessment is completed
 */
export function isAssessmentCompleted(): boolean {
  const info = getSessionInfo();
  return info?.isCompleted ?? false;
}

// =============================================================================
// REACT HOOK (for components that need reactive updates)
// =============================================================================

/**
 * Hook for session management in React components.
 * Provides reactive access to session state and management functions.
 *
 * @example
 * ```tsx
 * import { useSessionManager } from '@/lib/session/sessionManager';
 *
 * function LogoutButton() {
 *   const { logout, isCompleted } = useSessionManager();
 *   return <button onClick={() => logout()}>Logout</button>;
 * }
 * ```
 */
export function useSessionManager() {
  const isCompleted = useSessionStore((s) => s.is_completed);
  const sessionId = useSessionStore((s) => s.session_id);
  const userId = useSessionStore((s) => s.user_id);

  return {
    // State
    sessionId,
    userId,
    isCompleted,

    // Actions
    logout,
    startFreshAssessment,
    getSessionInfo,
    hasActiveSession,
    isAssessmentCompleted,
  };
}

// =============================================================================
// DEFAULT EXPORT
// =============================================================================

export default {
  logout,
  startFreshAssessment,
  getSessionInfo,
  hasActiveSession,
  isAssessmentCompleted,
  useSessionManager,
};
