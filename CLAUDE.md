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

## CRITICAL: Documentation Management Rules

### NEVER CREATE DUPLICATE DOCS - UPDATE IN PLACE

**This is the #1 documentation rule. Violations cause chaos.**

When releasing new versions, fixing bugs, or adding features, Claude Code MUST:

1. **UPDATE the existing canonical doc** - DO NOT create a new file
2. **Add a timestamp** to the "Last Updated" field in the doc header
3. **Update the version number** if it's a version release
4. **Add changelog entry** to `/docs/CHANGELOG.md`

### Canonical Documentation Files (NEVER DUPLICATE)

These files are the SINGLE SOURCE OF TRUTH. Update them in place:

| File | Purpose | Update When |
|------|---------|-------------|
| `/STRUCTURE.md` | Project structure | Adding folders/files |
| `/docs/ARCHITECTURE.md` | System architecture | Adding components |
| `/docs/DATABASE.md` | Database schema | Adding tables/columns |
| `/docs/API.md` | API endpoints | Adding/changing APIs |
| `/docs/DEPLOYMENT.md` | Deployment guide | Changing deploy process |
| `/docs/CHANGELOG.md` | Version history | EVERY release |
| `/agents/docs/AGENTS.md` | Agent catalog | Adding/modifying agents |
| `/agents/docs/PROACTIVE.md` | Proactive system | Changing proactive features |
| `/app/docs/COMPONENTS.md` | Component guide | Adding components |
| `/app/docs/FRAMES.md` | Assessment frames | Changing frames |

### How to Update Canonical Docs

```markdown
# Document Title

**Version:** v1.1 → v1.2          ← INCREMENT VERSION
**Last Updated:** January 21, 2026 → January 22, 2026  ← UPDATE DATE

... rest of content (update relevant sections) ...
```

### When to Create NEW Files (Rare Cases Only)

Create a new file ONLY when:
1. It's a completely NEW topic/scope not covered by existing docs
2. It's a temporary PLANNING spec (prefix with `SPEC_`)

Planning specs use dated names and get archived after implementation:
```
SPEC_<feature>_YYYYMMDD.md  →  Move to /_archive/docs/specs/ when done
```

### WRONG vs RIGHT Examples

#### WRONG - Creating version duplicates:
```
docs/ARCHITECTURE.md
docs/ARCHITECTURE_v2.md        ❌ NEVER DO THIS
docs/ARCHITECTURE_20260121.md  ❌ NEVER DO THIS
docs/ARCHITECTURE_new.md       ❌ NEVER DO THIS
```

#### RIGHT - Update in place:
```
docs/ARCHITECTURE.md           ✅ Update this file
                               ✅ Change "Last Updated" date
                               ✅ Add entry to CHANGELOG.md
```

#### WRONG - Multiple API docs:
```
docs/API.md
docs/API_v2.md                 ❌
docs/API_ENDPOINTS.md          ❌
docs/API_REFERENCE.md          ❌
```

#### RIGHT - One canonical API doc:
```
docs/API.md                    ✅ Single source of truth
```

### Documentation Update Checklist

Before ANY release, bug fix, or feature:

- [ ] Update `/docs/CHANGELOG.md` with version/date/changes
- [ ] Update relevant canonical docs (ARCHITECTURE, DATABASE, API, etc.)
- [ ] Update "Last Updated" timestamp in each modified doc
- [ ] Increment version number if it's a release
- [ ] DO NOT create new files for existing topics
- [ ] Archive old planning specs to `/_archive/docs/specs/`

### Version Tracking

All version history goes in ONE file: `/docs/CHANGELOG.md`

```markdown
# Changelog

## v1.2.0 - January 22, 2026
- Added: New proactive feature X
- Fixed: Bug in opportunity matcher
- Changed: API endpoint Y

## v1.1.0 - January 21, 2026
- Added: MVP cleanup
- ...
```

---

## Planning Specs (Temporary Docs)

### When to Use Planning Specs

Use `SPEC_*.md` files ONLY for:
- New feature planning before implementation
- Design decisions that need approval
- Complex changes requiring detailed spec

### Spec File Naming

```
SPEC_<FEATURE>_YYYYMMDD.md
```

Examples:
```
SPEC_PAYMENTS_20260122.md
SPEC_REALTIME_CHAT_20260125.md
```

### Spec Lifecycle

1. **Create** in `/agents/specs/` during planning
2. **Implement** the feature
3. **Update** canonical docs with final implementation
4. **Archive** spec to `/_archive/docs/specs/`

### Spec File Location

```
/agents/specs/           # Active planning specs only
/_archive/docs/specs/    # Completed/archived specs
```

### Spec Document Structure

Every spec MUST include:
1. **Header** - Title, date, author
2. **Status** - Draft/Review/Approved/Implemented
3. **Summary** - 2-3 sentence overview
4. **Proposed Changes** - What will change
5. **Technical Details** - Implementation approach
6. **Testing Plan** - How to verify
