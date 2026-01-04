/**
 * Assessment Router Utility
 * Smart routing based on session state for returning users
 * @version 11.0
 */

export interface SessionState {
  currentFrame: number;
  maxFrameReached: number;
  isComplete: boolean;
  completedAt: string | null;
}

/**
 * Determine the correct route for a user based on their session state
 * - Complete → /dashboard
 * - Partial progress → /quest/{lastFrame}
 * - New user → /quest/1
 */
export function getPostLoginRoute(session: SessionState | null): string {
  if (!session) {
    return '/quest/1';
  }

  // Assessment complete - go to dashboard
  if (session.isComplete) {
    return '/dashboard';
  }

  // Partial progress - resume at last frame
  if (session.maxFrameReached > 1 && session.maxFrameReached <= 6) {
    return `/quest/${session.maxFrameReached}`;
  }

  // New user - start at beginning
  return '/quest/1';
}

/**
 * Get the URL for the next frame after completing current
 */
export function getNextFrameUrl(currentFrame: number, isLastFrame: boolean = false): string {
  if (isLastFrame || currentFrame >= 6) {
    return '/dashboard';
  }
  return `/quest/${currentFrame + 1}`;
}

/**
 * Get the URL for the previous frame
 */
export function getPrevFrameUrl(currentFrame: number): string {
  if (currentFrame <= 1) {
    return '/quest/1';
  }
  return `/quest/${currentFrame - 1}`;
}

/**
 * Check if user should be redirected from quest to dashboard
 */
export function shouldRedirectToDashboard(session: SessionState | null): boolean {
  return session?.isComplete === true;
}

/**
 * Check if user can access a specific frame
 */
export function canAccessFrame(session: SessionState | null, frameId: number): boolean {
  if (!session) {
    return frameId === 1;
  }

  // Can always access frames up to maxFrameReached
  if (frameId <= session.maxFrameReached) {
    return true;
  }

  // Can access one frame ahead of current
  if (frameId === session.currentFrame + 1) {
    return true;
  }

  return false;
}

export default {
  getPostLoginRoute,
  getNextFrameUrl,
  getPrevFrameUrl,
  shouldRedirectToDashboard,
  canAccessFrame,
};
