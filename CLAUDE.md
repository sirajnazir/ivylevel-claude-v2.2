# Claude Code Implementation Guidelines

## CRITICAL: Solution Quality Standards

### NO BAND-AID FIXES
When implementing any fix or feature, Claude Code MUST:

1. **Treat Every Issue as a CLASS Problem**
   - Never fix just the symptom; identify the underlying pattern
   - Ask: "What category of problem is this? Where else might this occur?"
   - The fix should resolve ALL instances of this problem type, not just the one encountered

2. **Implement UNIVERSAL Solutions**
   - Solutions must work for edge cases, not just the happy path
   - Handle null, undefined, empty arrays, missing properties gracefully
   - Don't hardcode values; use configurable defaults, constants, or computed fallbacks
   - Example BAD: `const value = data.score ?? 0.3`  (magic number)
   - Example GOOD: `const value = data.score ?? DEFAULT_SCORES.community.baseline`

3. **Design for FLEXIBILITY**
   - Use configuration objects instead of hardcoded values
   - Implement proper type guards and validation at system boundaries
   - Create reusable utility functions for common patterns
   - Prefer composition over rigid inheritance

4. **Ensure FUTURE-PROOFING**
   - Consider how the codebase might evolve
   - Add appropriate abstractions that allow extension without modification
   - Document assumptions and constraints in code comments
   - Use TypeScript types/interfaces to enforce contracts

### Implementation Checklist (MUST follow before any fix)

Before implementing ANY fix, Claude Code MUST:

- [ ] **Identify Root Cause**: What is the underlying issue, not just the symptom?
- [ ] **Find All Occurrences**: Where else in the codebase might this pattern exist?
- [ ] **Design Universal Fix**: How can this fix apply to the entire class of problems?
- [ ] **Consider Edge Cases**: null, undefined, empty, invalid inputs handled?
- [ ] **Use Proper Defaults**: Are defaults configurable and documented?
- [ ] **Type Safety**: Does the fix maintain or improve type safety?
- [ ] **No Magic Numbers**: Are all constants named and centralized?
- [ ] **Validation at Boundaries**: Is input validated where it enters the system?

### Examples of WRONG vs RIGHT Approaches

#### WRONG: Band-aid fix for null handling
```typescript
// BAD - fixes one spot with magic defaults
function calculateScore(data: Data): number {
  const value = data.score ?? 0.5;  // Magic number
  return value * 100;
}
```

#### RIGHT: Universal null-safe pattern
```typescript
// GOOD - centralized defaults, reusable utility, type-safe
const SCORE_DEFAULTS = {
  baseline: 0.5,
  minimum: 0,
  maximum: 1,
} as const;

function safeNumber(value: number | null | undefined, fallback: number): number {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return fallback;
  }
  return Math.max(SCORE_DEFAULTS.minimum, Math.min(SCORE_DEFAULTS.maximum, value));
}

function calculateScore(data: Data): number {
  const value = safeNumber(data.score, SCORE_DEFAULTS.baseline);
  return value * 100;
}
```

#### WRONG: Fixing one API endpoint's missing field
```typescript
// BAD - only fixes this one endpoint
if (!profile.target_schools) {
  profile.target_schools = ['HARVARD', 'MIT'];  // Hardcoded
}
```

#### RIGHT: Centralized validation and defaults
```typescript
// GOOD - validation utility used everywhere
import { validateProfile, withDefaults } from '@/lib/validation/profile';

const validatedProfile = withDefaults(validateProfile(profile));
// Defaults come from a central config, validation is reusable
```

### Code Smell Detection

When Claude Code sees these patterns, STOP and refactor:

1. **Magic Numbers**: Any literal number in business logic
2. **Repeated Null Checks**: Same `?? default` pattern in multiple places
3. **Type Assertions**: `as Type` without validation
4. **Hardcoded Arrays/Objects**: Inline data that should be in config
5. **Copy-Paste Logic**: Similar code in multiple locations
6. **Swallowed Errors**: Empty catch blocks or ignored error states
7. **Implicit Assumptions**: Code that assumes data shape without validation
8. **Mutating Array Methods on Store Data**: `.sort()`, `.reverse()`, `.splice()` on arrays from Zustand/Redux stores (use `safeSort()`, `[...arr].sort()` etc.)

### Architectural Principles

1. **Single Source of Truth**: Constants, defaults, and configs in ONE place
2. **Fail Fast**: Validate early, provide clear error messages
3. **Defensive Programming**: Assume inputs can be invalid
4. **Separation of Concerns**: Validation, transformation, business logic separated
5. **DRY (Don't Repeat Yourself)**: Extract common patterns into utilities

## Project-Specific Notes

### UI/UX Branding Guidelines (CRITICAL)

**UNIVERSAL RULE: Never use dark-mode Tailwind CSS classes in Frame components.**

The Ivylevel brand uses a **light-mode color scheme**. The dark-mode CSS variables in `globals.css` are for system UI, NOT for Frame content.

#### DO NOT USE (Dark Mode Classes):
- `text-text-primary`, `text-text-secondary`, `text-text-muted` → These are white/light colors for dark backgrounds
- `bg-background-primary`, `bg-background-secondary` → These are dark backgrounds
- `bg-primary-blue`, `text-primary-blue` → Wrong brand color (should be orange)
- `border-border-subtle`, `border-border-default` → Dark-mode borders

#### DO USE (Brand Constants):
```typescript
import { BRAND_COLORS } from '@/lib/constants/brand';

// Text colors (inline styles)
style={{ color: BRAND_COLORS.textHeading }}    // Maroon #641432
style={{ color: BRAND_COLORS.textPrimary }}    // Gray-700 #374151
style={{ color: BRAND_COLORS.textMuted }}      // Gray-400 #9ca3af

// Background colors
style={{ backgroundColor: BRAND_COLORS.bgPrimary }}    // White with slight transparency
style={{ backgroundColor: BRAND_COLORS.primaryBg }}    // Light orange rgba(255, 74, 35, 0.1)
style={{ backgroundColor: BRAND_COLORS.bgSuccess }}    // Light green

// Border colors
style={{ border: `1px solid ${BRAND_COLORS.borderLight}` }}
style={{ border: `2px solid ${BRAND_COLORS.primary}` }}  // Selected state
```

#### Brand Color Reference:
- **Primary**: `#FF4A23` (Ivylevel orange) - main accent, buttons, selected states
- **Secondary**: `#641432` (Ivylevel maroon) - headings, important text
- **Success**: `#16a34a` (Green-600) - positive indicators
- **Warning**: `#d97706` (Amber-600) - caution indicators
- **Error**: `#dc2626` (Red-600) - negative indicators

#### File Location:
All brand constants are in `/lib/constants/brand.ts`. Import and use these instead of Tailwind classes in Frame components.

### IvyQuest Scoring System

- All scoring attributes should have centralized defaults in `/lib/constants/defaults.ts`
- Profile validation should happen at API boundaries using a validation layer
- Null handling should use utility functions, not inline `??` with magic numbers
- The scoring engine should be robust to incomplete profiles

### Data Flow

```
User Input → Validation Layer → Normalized Data → Business Logic → Output
                  ↓
            Defaults Applied (from central config)
                  ↓
            Type-safe throughout
```

## Enforcement

Claude Code MUST NOT proceed with implementation until:
1. The fix addresses the ROOT CAUSE
2. The solution is UNIVERSAL (applies to all similar cases)
3. No MAGIC NUMBERS or hardcoded values exist
4. Proper DEFAULTS and VALIDATION are in place
5. The fix is FUTURE-PROOF and extensible

## Documentation & Spec Naming Convention

### Spec File Naming (MANDATORY)

All specification documents MUST follow this naming convention:

```
SPEC_<DESCRIPTION>_<DATE>_<TIME>_v<VERSION>_<SEQ>.md
```

**Format breakdown:**
- `SPEC_` - Prefix indicating this is a specification document
- `<DESCRIPTION>` - Brief snake_case description (e.g., `AGENT_ARCHITECTURE`, `UI_FLOW`)
- `<DATE>` - Date in YYYYMMDD format
- `<TIME>` - Time in HHMM format (24-hour)
- `v<VERSION>` - Version number (e.g., v1, v2)
- `<SEQ>` - Incremental sequence number for same-day specs (001, 002, etc.)

**Examples:**
```
SPEC_AGENT_ARCHITECTURE_20260120_1830_v1_001.md
SPEC_LETTA_INTEGRATION_20260120_1900_v1_002.md
SPEC_UI_UX_FLOW_20260121_0900_v2_001.md
```

**Why this matters:**
- Many docs are generated daily - this prevents losing track of latest versions
- Enables chronological sorting in file explorers
- Clear versioning for iterative refinements
- Sequence numbers handle multiple specs on same day

### Spec File Location

All specs should be stored in:
```
/agents/specs/           # For backend/agent specs
/docs/specs/             # For frontend/UI specs (if exists)
```

### Spec Document Structure

Every spec MUST include:
1. **Header** - Title, version, date, author
2. **Status** - Draft/Review/Approved/Implemented
3. **Summary** - 2-3 sentence overview
4. **Current State** - What exists today
5. **Proposed Changes** - What will change (if applicable)
6. **Technical Details** - Architecture, DB schema, API endpoints
7. **UI/UX Flow** - User journey with screenshots/diagrams
8. **Dependencies** - What this depends on
9. **Risks & Mitigations** - What could break
10. **Testing Plan** - How to verify
