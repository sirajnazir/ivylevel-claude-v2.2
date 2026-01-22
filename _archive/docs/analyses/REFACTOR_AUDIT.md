# IvyQuest Refactor Audit Report

> **Date**: 2025-12-18
> **Status**: CRITICAL - Pre-Launch Blocker
> **Auditor**: Claude Code

---

## Executive Summary

Three critical bugs have been identified that block the launch. All three stem from a common root cause: **fragmented architecture with multiple sources of truth**. This document details each bug, its root cause, and the recommended fix aligned with the refactoring protocol.

---

## Critical Issues

### KI-001: Dynamic Import Crash in Frame5GamePlan

**Severity**: CRITICAL (Page crashes on load)

**Symptom**:
```
Uncaught undefined
```
Error occurs when navigating to Game Plan page.

**Root Cause**:
Dynamic import error handler returns incorrect format:

```typescript
// CURRENT CODE (BROKEN)
const PDFDownloadLink = dynamic(
  () => import('@react-pdf/renderer')
    .then((mod) => mod.PDFDownloadLink)
    .catch((err) => {
      console.error('Failed to load PDFDownloadLink:', err);
      return () => null;  // BUG: Returns function, not module
    }),
  { ssr: false }
);
```

**Why It Breaks**:
Next.js `dynamic()` expects a module with a `default` export. When the catch handler returns `() => null`, Next.js tries to access `.default` on a function, resulting in `undefined`.

**Fix**:
```typescript
// CORRECT CODE
const PDFDownloadLink = dynamic(
  () => import('@react-pdf/renderer')
    .then((mod) => mod.PDFDownloadLink)
    .catch((err) => {
      console.error('Failed to load PDFDownloadLink:', err);
      return { default: () => null };  // Return module-like object
    }),
  { ssr: false }
);
```

**Files Affected**:
- `components/frames/Frame5GamePlan.tsx` (lines ~15-25)

**Verification**:
- Navigate to Game Plan page
- Page should render without crash
- If PDF library fails to load, graceful fallback shown

---

### KI-002: Inflated Scores (100%+) on Empty Profile

**Severity**: CRITICAL (Incorrect data display)

**Symptom**:
- Empty profile shows scores like 100%, 101%
- Scores should be 0% or show "insufficient data"

**Root Cause**:
Multiple issues compound to cause this:

1. **Multiple Sources of Truth**: Scoring happens in at least 3 places:
   - `lib/scoring/` (server-side)
   - `lib/utils/scoring.ts` (client-side)
   - Component-level calculations

2. **Stale localStorage Data**: Zustand persist middleware loads old scores from localStorage even when profile is empty.

3. **Missing Validation**: No validation that profile has sufficient data before calculating scores.

4. **Default Values Applied Incorrectly**: When fields are missing, high default values are substituted instead of 0.

**Evidence**:
```typescript
// Example of problematic pattern found in codebase
const score = data.aptitude?.gpa ?? 4.0;  // Empty profile gets 4.0 GPA!
```

**Fix Strategy**:

1. **Single Scoring Location**: All scoring MUST happen in `/api/scoring` endpoint only.

2. **Profile Completeness Check**:
```typescript
function isProfileScorable(profile: Profile): boolean {
  const requiredFields = ['identity.grade', 'aptitude.gpa', 'activities'];
  return requiredFields.every(field => hasValue(profile, field));
}
```

3. **Clear Cache on Profile Reset**:
```typescript
// When profile is cleared, also clear results
useProfileStore.getState().clearCache();
useResultsStore.getState().clearCache();
localStorage.removeItem('ivyquest-results');
```

4. **Default to Zero, Not High Values**:
```typescript
// When data is missing, score should be 0, not a default
const score = profile.aptitude?.gpa !== undefined
  ? normalizeGPA(profile.aptitude.gpa)
  : 0;
```

**Files Affected**:
- `lib/store/useResultsStore.ts`
- `lib/store/useProfileStore.ts`
- `lib/utils/scoring.ts` (should be deleted, use API)
- `lib/scoring/engine.ts`
- All components that do local scoring

**Verification**:
- Clear localStorage
- Start fresh assessment
- Navigate to results with empty profile
- All scores should show 0% or "Complete assessment for scores"

---

### KI-003: Missing CircularProgress Rings in Reveal

**Severity**: HIGH (UI mismatch from design)

**Symptom**:
- Frame5Reveal shows bar graphs instead of circular progress rings
- Design spec calls for CircularProgress component with concentric rings

**Root Cause**:
`Frame6ProfileReveal.tsx` was implemented with bar-based visualization instead of importing and using the existing `CircularProgress` component.

**Evidence**:
Frame5Reveal has CircularProgress rings:
```typescript
// Frame5Reveal.tsx
import CircularProgress from '@/components/ui/CircularProgress';
// Uses rings visualization
```

But Frame6ProfileReveal uses bars:
```typescript
// Frame6ProfileReveal.tsx
// NO CircularProgress import
// Uses inline bar divs instead
<div className="h-2 bg-gray-200 rounded">
  <div style={{ width: `${score}%` }} />
</div>
```

**Fix**:
Import and use the same CircularProgress component:

```typescript
import CircularProgress from '@/components/ui/CircularProgress';

// In render
<CircularProgress
  scores={categoryScores}
  size={300}
  animated={true}
/>
```

**Files Affected**:
- `components/frames/Frame6ProfileReveal.tsx`

**Verification**:
- Navigate to Profile Reveal frame
- Should see concentric rings visualization
- Rings should match Frame5Reveal styling

---

## Architecture Issues (Root Causes)

### Issue A: Multiple Sources of Truth

**Current State**:
```
Zustand Store ←→ localStorage ←→ Components
      ↓                              ↓
  (old data)                  (local calculations)
      ↓                              ↓
   Stale UI                    Wrong scores
```

**Required State**:
```
Supabase (Truth) → API → Zustand (Cache) → Components (Display)
```

### Issue B: Client-Side Scoring

**Problem**: Scoring logic exists in multiple places, leading to inconsistencies.

**Solution**: Delete all client-side scoring. Only `/api/scoring` calculates scores.

### Issue C: No Validation Layer

**Problem**: Data flows without validation, leading to undefined/null errors.

**Solution**: Zod schemas at all boundaries:
- API request validation
- Database response validation
- localStorage read validation

---

## Recommended Fix Order

1. **Phase 1: Stop the Bleeding** (Immediate)
   - Fix KI-001 (dynamic import crash)
   - Clear corrupted localStorage
   - Add temporary score validation

2. **Phase 2: Consolidate Scoring** (Short-term)
   - Create `/api/scoring` as single scoring endpoint
   - Remove all client-side scoring logic
   - Add profile completeness check

3. **Phase 3: Fix UI** (Short-term)
   - Import CircularProgress in Frame6ProfileReveal
   - Match styling to Frame5Reveal

4. **Phase 4: Architecture Alignment** (Medium-term)
   - Implement Zod validation layer
   - Convert stores to pure cache
   - Add Supabase as single source of truth

---

## Pre-Fix Checklist

Before implementing ANY fix:

- [ ] Read `/docs/PLAN.md` (refactoring protocol)
- [ ] Check `/docs/MASTER_SPEC.md` for current architecture
- [ ] Identify if fix is band-aid or universal solution
- [ ] Determine all files affected
- [ ] Plan verification steps

---

## Verification Test Plan

After fixes are implemented, run these scenarios:

### Test 1: Fresh Start Journey
1. Clear localStorage (`localStorage.clear()`)
2. Navigate to `/`
3. Start new assessment
4. Progress through all frames with minimal input
5. **Expected**: Scores show 0% or "insufficient data"

### Test 2: Full Profile Journey
1. Clear localStorage
2. Complete all frames with full data
3. Navigate to results
4. **Expected**: Scores reflect actual input, 0-100% range only

### Test 3: Page Refresh Persistence
1. Complete Frame 3
2. Refresh page
3. **Expected**: Progress maintained, data intact

### Test 4: Direct URL Access
1. Clear localStorage
2. Navigate directly to `/quest/5`
3. **Expected**: Redirect to appropriate starting point

---

## Sign-Off

| Role | Name | Date | Approved |
|------|------|------|----------|
| Developer | | | [ ] |
| QA | | | [ ] |
| Product | | | [ ] |

---

*This audit must be resolved before launch. All fixes must follow the refactoring protocol in `/docs/PLAN.md`.*
