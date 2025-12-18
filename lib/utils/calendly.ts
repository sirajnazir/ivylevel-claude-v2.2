/**
 * Calendly integration utilities for IvyQuest coach scheduling
 */

export interface StudentContext {
  name: string;
  grade: number;
  email: string;
  archetype: string;
  tier: string;
  completeness: number;
}

/**
 * Generate Calendly URL with pre-filled student context
 *
 * Calendly supports custom questions via URL parameters:
 * - name: Pre-fills name field
 * - email: Pre-fills email field
 * - a1, a2, a3: Custom question answers
 */
export function generateCalendlyURL(baseURL: string, context: StudentContext): string {
  // Validate base URL
  if (!baseURL || !baseURL.startsWith('https://calendly.com/')) {
    console.error('Invalid Calendly URL:', baseURL);
    return baseURL;
  }

  const params = new URLSearchParams({
    name: context.name,
    email: context.email,
    a1: `Grade: ${context.grade}`,
    a2: `Profile: ${context.tier} (${context.completeness}% complete)`,
    a3: `Archetype: ${context.archetype}`,
  });

  return `${baseURL}?${params.toString()}`;
}

/**
 * Open Calendly in centered popup window
 */
export function openCalendlyPopup(url: string): Window | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const width = 700;
  const height = 800;
  const left = (window.screen.width - width) / 2;
  const top = (window.screen.height - height) / 2;

  const popup = window.open(
    url,
    'calendly_booking',
    `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
  );

  if (!popup) {
    console.error('Popup blocked. Please allow popups for this site.');
  }

  return popup;
}

/**
 * Check if popup was blocked by browser
 */
export function isPopupBlocked(popup: Window | null): boolean {
  return !popup || popup.closed || typeof popup.closed === 'undefined';
}

/**
 * Validate email format
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
