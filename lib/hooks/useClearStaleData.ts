'use client';

import { useEffect } from 'react';

/**
 * App Storage Version
 * Increment this when making breaking changes to stored data structures.
 * This will clear all cached data for users on older versions.
 */
const STORAGE_VERSION = '2.1.0';
const VERSION_KEY = 'ivyquest-version';

/**
 * Clear stale localStorage data when app version changes.
 *
 * This prevents bugs caused by:
 * - Old cached scores showing incorrect values (101%+)
 * - Stale profile data from previous sessions
 * - Incompatible data structures after updates
 *
 * @usage Add to root layout or app component:
 * ```tsx
 * import { useClearStaleData } from '@/lib/hooks/useClearStaleData';
 *
 * export default function RootLayout({ children }) {
 *   useClearStaleData();
 *   return <html>...</html>;
 * }
 * ```
 */
export function useClearStaleData(): void {
  useEffect(() => {
    // Only run in browser
    if (typeof window === 'undefined') return;

    try {
      const storedVersion = localStorage.getItem(VERSION_KEY);

      // If version matches, data is current
      if (storedVersion === STORAGE_VERSION) {
        return;
      }

      console.log(
        `[useClearStaleData] Version change detected: ${storedVersion || 'none'} -> ${STORAGE_VERSION}`
      );

      // Find all IvyQuest-related keys to clear
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && shouldClearKey(key)) {
          keysToRemove.push(key);
        }
      }

      // Clear stale data
      keysToRemove.forEach((key) => {
        localStorage.removeItem(key);
        console.log(`[useClearStaleData] Removed stale key: ${key}`);
      });

      // Set new version
      localStorage.setItem(VERSION_KEY, STORAGE_VERSION);

      console.log(
        `[useClearStaleData] Cleared ${keysToRemove.length} stale keys, version set to ${STORAGE_VERSION}`
      );
    } catch (error) {
      // localStorage might be disabled or quota exceeded
      console.warn('[useClearStaleData] Failed to clear stale data:', error);
    }
  }, []);
}

/**
 * Determine if a localStorage key should be cleared on version change.
 */
function shouldClearKey(key: string): boolean {
  const clearPatterns = [
    'ivyquest',
    'profile',
    'results',
    'assessment',
    'student-store',
    'session-store',
    'results-store',
    'insights-store',
  ];

  const lowercaseKey = key.toLowerCase();
  return clearPatterns.some((pattern) => lowercaseKey.includes(pattern));
}

export default useClearStaleData;
