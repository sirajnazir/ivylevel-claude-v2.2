# Bug Report: Inflated Scores for Empty Profiles

> **Date**: 2025-12-18
> **Status**: CRITICAL
> **Reporter**: Claude Code
> **Affects**: Frame5Reveal, Frame6ProfileReveal

---

## Summary

Empty profiles are displaying high scores (95-100%) instead of 0%. Users who skip all questions in the assessment still see inflated completeness and category scores.

---

## Symptoms

1. **Completeness shows 100%** for profiles with no user input
2. **Category scores inflated**: Aptitude 95%, Passion 100%, Service 100%, Identity 75%
3. **"Profile Optimization Phase"** shown instead of "Foundation Building Phase"
4. **Strengths listed** that shouldn't exist for empty profiles:
   - "Strong academic foundation" (hasAcademics is true)
   - "Good time availability (8 hrs/week)"
   - "Leadership experience"
   - "Community service commitment"

---

## Root Cause Analysis

### Issue 1: Default Values in Frame Components

Frame components use `??` with non-zero defaults, causing values to be saved even when user provides no input.

**Frame4Context.tsx:661**
```typescript
const availableHours = operating.availableHoursPerWeek ?? 10;
// Even if user doesn't set anything, 10 is used as default
```

This means:
- User navigates through Frame 4 without entering data
- Component renders with `availableHoursPerWeek = 10`
- This value may get saved to store through form interactions
- Frame6 sees `availableHoursPerWeek = 10` and shows "Good time availability"

### Issue 2: Completeness Calculation Timing

The `calculateCompleteness()` function in `useStudentStore.ts` is called during frame navigation, but by that time, default values have already been applied.

**Lines 501-573 in useStudentStore.ts:**
```typescript
// Academics (30 points possible)
if (profile.aptitude?.gpa_weighted || profile.aptitude?.gpa_unweighted) {
  score += 10;
  hasAcademics = true;
}
```

The logic is correct (checks for actual values), but the profile may already have been polluted with defaults.

### Issue 3: Strengths Logic Uses Stored Completeness

**Frame6ProfileReveal.tsx:266-276:**
```typescript
if (profile.completeness?.hasAcademics) {
  result.push('Strong academic foundation');
}
if ((profile.operating?.availableHoursPerWeek || 0) >= 8) {
  result.push(`Good time availability (${profile.operating?.availableHoursPerWeek} hrs/week)`);
}
```

This reads from stored state, not from fresh calculation. If `completeness.hasAcademics` was set to `true` at any point, it persists.

### Issue 4: Persist Middleware Re-saves Stale Data

When user clears localStorage, Zustand's persist middleware immediately re-saves the in-memory state, which contains the polluted profile data.

---

## Evidence

### Test 1: Scoring Functions (PASSED)

Running isolated scoring functions with empty profile returns 0:

```
TEST 5: Fresh start profile (from dev server logs)
  Aptitude: 0 (expected: 0) ✓
  Passion: 0 (expected: 0) ✓
  Service: 0 (expected: 0) ✓
  Identity: 0 (expected: 0) ✓
```

### Test 2: Server Logs Show Empty Profile

```
Frame5GamePlan: Generating game plan with profile: {
  aptitude: {
    gpa_weighted: null,
    sat_total: null,
    ap_count: null,
    ...
  },
  passion: {
    leadership_level: null,
    ec_commitment_years: null,
    ...
  },
  community: {
    service_hours: null,
    ...
  }
}
```

Profile values are correctly null, yet UI shows high scores.

### Test 3: UI Shows Wrong Data

Despite null values in profile:
- UI displays 95% Aptitude
- UI displays 100% Passion
- UI displays 100% Service
- Completeness shows 100%
- "Profile Optimization Phase" displayed

---

## Files Affected

| File | Issue |
|------|-------|
| `components/frames/Frame4Context.tsx` | Default values (`?? 10`) |
| `components/frames/Frame3Building.tsx` | May set defaults on render |
| `lib/store/useStudentStore.ts` | Persist middleware re-saves |
| `components/frames/Frame6ProfileReveal.tsx` | Uses stored completeness |

---

## Recommended Fixes

### Fix 1: Remove Default Values from Frame Components

**Before:**
```typescript
const availableHours = operating.availableHoursPerWeek ?? 10;
```

**After:**
```typescript
const availableHours = operating.availableHoursPerWeek ?? 0;
// OR
const availableHours = operating.availableHoursPerWeek; // undefined is fine
```

### Fix 2: Calculate Scores Fresh (Don't Use Stored Completeness)

**Frame6ProfileReveal should calculate everything fresh, not read from stored state:**

```typescript
// BAD: Uses stored value
const completeness = profile.completeness?.score || 0;

// GOOD: Calculate fresh
const completeness = useMemo(() => {
  let score = 0;
  if (profile.aptitude?.gpa_weighted > 0) score += 10;
  if (profile.aptitude?.sat_total > 0) score += 10;
  // ... etc
  return score;
}, [profile]);
```

### Fix 3: Don't Display Strengths Based on Stored Flags

**Before:**
```typescript
if (profile.completeness?.hasAcademics) {
  result.push('Strong academic foundation');
}
```

**After:**
```typescript
// Calculate fresh based on actual data
const hasRealAcademics = (
  (profile.aptitude?.gpa_weighted ?? 0) > 0 ||
  (profile.aptitude?.sat_total ?? 0) > 0
);
if (hasRealAcademics) {
  result.push('Strong academic foundation');
}
```

### Fix 4: Reset Completeness on Profile Reset

```typescript
resetProfile: () =>
  set((state) => {
    state.profile = createEmptyProfile();
    state.profile.completeness = {
      score: 0,
      hasAcademics: false,
      hasActivities: false,
      hasContext: false,
      hasOperating: false,
    };
    state.isDirty = false;
  }),
```

---

## Testing Protocol

### Empty Profile Test

1. Open **Incognito window**
2. Navigate to `http://localhost:3006/quest/1`
3. Enter only required fields (name)
4. **Skip all optional fields** in every frame
5. Navigate to Frame 5/6

**Expected Results:**
- All category scores: 0%
- Completeness: < 10%
- Tier: "Foundation Building Phase"
- No strengths listed (or "Starting fresh")

### Full Profile Test

1. Open **Incognito window**
2. Navigate to `http://localhost:3006/quest/1`
3. Fill in ALL fields with real data:
   - GPA: 4.2
   - SAT: 1450
   - Activities: 3+
   - Service hours: 150
   - Leadership: President
4. Navigate to Frame 5/6

**Expected Results:**
- Scores reflect entered data
- Completeness: 70-100%
- Tier: "Profile Optimization Phase"

---

## Priority

**CRITICAL** - This bug fundamentally breaks the assessment's value proposition. Users see meaningless scores that don't reflect their actual profile.

---

## Related Issues

- KI-001: Dynamic import crash (FIXED)
- KI-002: Stale localStorage (PARTIALLY FIXED - hook created but doesn't solve this)
- KI-003: Missing CircularProgress (FIXED)

---

## Next Steps

1. Audit ALL frame components for default values
2. Remove or set to 0/null all `?? nonZeroDefault` patterns
3. Make Frame6 calculate scores fresh, not from stored state
4. Add empty profile test to CI/CD
5. Consider removing `completeness` from stored state entirely

---

*Report generated by Claude Code diagnostic analysis*
