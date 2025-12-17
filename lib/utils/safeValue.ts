/**
 * Universal Safe Value Utilities
 *
 * PRINCIPLE: Centralized null/undefined/NaN handling for the entire codebase.
 * These utilities ensure defensive programming without scattering ?? operators.
 */

import { VALIDATION_BOUNDS } from '../constants/defaults';

// =============================================================================
// SAFE NUMBER UTILITIES
// =============================================================================

/**
 * Safely convert a value to a number, with bounds validation
 *
 * @param value - The value to convert (number, null, undefined, or NaN)
 * @param fallback - The default value if conversion fails
 * @param bounds - Optional min/max bounds to clamp the result
 * @returns A valid number, clamped to bounds if specified
 *
 * @example
 * safeNumber(null, 0.5) // returns 0.5
 * safeNumber(0.8, 0.5) // returns 0.8
 * safeNumber(1.5, 0.5, { min: 0, max: 1 }) // returns 1.0 (clamped)
 * safeNumber(NaN, 0.5) // returns 0.5
 */
export function safeNumber(
  value: number | null | undefined,
  fallback: number,
  bounds?: { min?: number; max?: number }
): number {
  // Handle null, undefined, NaN
  if (value === null || value === undefined || Number.isNaN(value)) {
    return applyBounds(fallback, bounds);
  }

  return applyBounds(value, bounds);
}

/**
 * Apply min/max bounds to a number
 */
function applyBounds(
  value: number,
  bounds?: { min?: number; max?: number }
): number {
  if (!bounds) return value;

  let result = value;
  if (bounds.min !== undefined) {
    result = Math.max(bounds.min, result);
  }
  if (bounds.max !== undefined) {
    result = Math.min(bounds.max, result);
  }
  return result;
}

/**
 * Safe normalized score (0.0 - 1.0)
 */
export function safeNormalized(
  value: number | null | undefined,
  fallback: number
): number {
  return safeNumber(value, fallback, VALIDATION_BOUNDS.normalized);
}

/**
 * Safe percentage score (0 - 100)
 */
export function safePercentage(
  value: number | null | undefined,
  fallback: number
): number {
  return Math.round(safeNumber(value, fallback, VALIDATION_BOUNDS.percentageScore));
}

/**
 * Safe probability (0.0 - 0.95, per spec cap)
 */
export function safeProbability(
  value: number | null | undefined,
  fallback: number
): number {
  return safeNumber(value, fallback, VALIDATION_BOUNDS.probability);
}

/**
 * Safe SFFA rubric rating (1 - 6)
 */
export function safeRubricRating(
  value: number | null | undefined,
  fallback: number
): number {
  return Math.round(safeNumber(value, fallback, VALIDATION_BOUNDS.rubricRating));
}

// =============================================================================
// SAFE STRING UTILITIES
// =============================================================================

/**
 * Safely get a string value with fallback
 *
 * @param value - The value to convert
 * @param fallback - The default value if null/undefined/empty
 * @returns A valid string
 */
export function safeString(
  value: string | null | undefined,
  fallback: string = ''
): string {
  if (value === null || value === undefined) {
    return fallback;
  }
  return value;
}

/**
 * Safely get a non-empty string (trims whitespace)
 */
export function safeNonEmptyString(
  value: string | null | undefined,
  fallback: string = ''
): string {
  const trimmed = safeString(value, fallback).trim();
  return trimmed.length > 0 ? trimmed : fallback;
}

// =============================================================================
// SAFE ARRAY UTILITIES
// =============================================================================

/**
 * Safely get an array with fallback
 *
 * @param value - The value to check
 * @param fallback - The default array if null/undefined/empty
 * @returns A valid array
 */
export function safeArray<T>(
  value: T[] | null | undefined,
  fallback: T[] = []
): T[] {
  if (!Array.isArray(value) || value.length === 0) {
    return fallback;
  }
  return value;
}

/**
 * Safely get the first element of an array
 */
export function safeFirst<T>(
  value: T[] | null | undefined,
  fallback: T
): T {
  if (!Array.isArray(value) || value.length === 0) {
    return fallback;
  }
  return value[0];
}

// =============================================================================
// SAFE OBJECT UTILITIES
// =============================================================================

/**
 * Safely get a nested property with fallback
 *
 * @param obj - The object to access
 * @param path - Dot-separated path (e.g., 'aptitude.gpa_weighted')
 * @param fallback - The default value if path doesn't exist
 * @returns The value at path or fallback
 */
export function safeGet<T>(
  obj: Record<string, unknown> | null | undefined,
  path: string,
  fallback: T
): T {
  if (!obj) return fallback;

  const keys = path.split('.');
  let current: unknown = obj;

  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== 'object') {
      return fallback;
    }
    current = (current as Record<string, unknown>)[key];
  }

  if (current === null || current === undefined) {
    return fallback;
  }

  return current as T;
}

/**
 * Check if a value is defined (not null and not undefined)
 */
export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

/**
 * Check if a value is a valid number (not NaN, not null, not undefined)
 */
export function isValidNumber(value: unknown): value is number {
  return typeof value === 'number' && !Number.isNaN(value);
}

// =============================================================================
// COMPUTATION HELPERS
// =============================================================================

/**
 * Compute weighted sum with safe handling of missing values
 *
 * @param items - Array of { value, weight, fallback } objects
 * @returns Weighted sum with fallbacks applied
 *
 * @example
 * weightedSum([
 *   { value: data.gpa, weight: 0.35, fallback: 0.5 },
 *   { value: data.sat, weight: 0.30, fallback: 0.5 },
 * ])
 */
export function weightedSum(
  items: Array<{
    value: number | null | undefined;
    weight: number;
    fallback: number;
  }>
): number {
  return items.reduce((sum, item) => {
    const safeValue = safeNormalized(item.value, item.fallback);
    return sum + safeValue * item.weight;
  }, 0);
}

/**
 * Compute average with safe handling of missing values
 *
 * @param values - Array of values (some may be null/undefined)
 * @param fallback - Fallback for missing values
 * @returns Average of all values
 */
export function safeAverage(
  values: Array<number | null | undefined>,
  fallback: number
): number {
  if (values.length === 0) return fallback;

  const sum = values.reduce<number>((acc, val) => {
    return acc + safeNumber(val, fallback);
  }, 0);

  return sum / values.length;
}

// =============================================================================
// SAFE ARRAY MUTATION UTILITIES
// =============================================================================

/**
 * Safely sort an array without mutating the original
 *
 * IMPORTANT: Array.sort() mutates in place. When arrays come from
 * Zustand/immer stores or const assertions, they are frozen/read-only.
 * Always use this utility to avoid "Cannot assign to read only property" errors.
 *
 * @param array - The array to sort (won't be mutated)
 * @param compareFn - Optional comparison function
 * @returns A new sorted array
 *
 * @example
 * // Instead of: items.sort((a, b) => a.value - b.value)
 * // Use: safeSort(items, (a, b) => a.value - b.value)
 */
export function safeSort<T>(
  array: T[] | readonly T[] | null | undefined,
  compareFn?: (a: T, b: T) => number
): T[] {
  if (!array || array.length === 0) return [];
  return [...array].sort(compareFn);
}

/**
 * Safely reverse an array without mutating the original
 */
export function safeReverse<T>(
  array: T[] | readonly T[] | null | undefined
): T[] {
  if (!array || array.length === 0) return [];
  return [...array].reverse();
}

/**
 * Safely filter and sort an array in one operation
 */
export function safeSortBy<T>(
  array: T[] | readonly T[] | null | undefined,
  keyFn: (item: T) => number,
  descending: boolean = false
): T[] {
  if (!array || array.length === 0) return [];
  return [...array].sort((a, b) => {
    const diff = keyFn(a) - keyFn(b);
    return descending ? -diff : diff;
  });
}
