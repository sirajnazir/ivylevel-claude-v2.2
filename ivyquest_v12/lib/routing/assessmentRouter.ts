export interface SessionState {
  currentFrame: number;
  maxFrameReached: number;
  isComplete: boolean;
  completedAt: string | null;
}

export function getPostLoginRoute(session: SessionState | null): string {
  if (!session) return '/quest/1';
  if (session.isComplete) return '/dashboard';
  if (session.maxFrameReached > 1 && session.maxFrameReached <= 6) {
    return \`/quest/\${session.maxFrameReached}\`;
  }
  return '/quest/1';
}

export function getNextFrameUrl(currentFrame: number, isLastFrame: boolean): string {
  if (isLastFrame || currentFrame >= 6) return '/dashboard';
  return \`/quest/\${currentFrame + 1}\`;
}
