# IvyQuest Refactoring Protocol

> **Version**: 1.0.0
> **Last Updated**: 2025-12-18
> **Status**: ACTIVE

## Purpose

This document establishes a mandatory protocol for all refactoring work on IvyQuest. Every refactor MUST follow this process to prevent architectural drift and maintain system integrity.

---

## Pre-Refactor Checklist

Before ANY refactoring begins, complete this checklist:

### 1. Audit Current State

```bash
# Run these commands and document results
npm run type-check        # TypeScript errors
npm run lint              # ESLint issues
npm run test              # Test status (if applicable)
```

Document findings in `/docs/REFACTOR_AUDIT.md`

### 2. Archive Current Spec

```bash
# Create dated snapshot of MASTER_SPEC.md
cp docs/MASTER_SPEC.md docs/spec-updates/MASTER_SPEC_$(date +%Y%m%d).md
```

### 3. Identify Affected Systems

For EVERY refactor, list all affected systems:

| System | Impact Level | Files Affected |
|--------|-------------|----------------|
| Routing | HIGH/MED/LOW | List files |
| State Management | HIGH/MED/LOW | List files |
| API Layer | HIGH/MED/LOW | List files |
| Components | HIGH/MED/LOW | List files |
| Scoring Engine | HIGH/MED/LOW | List files |
| Data Persistence | HIGH/MED/LOW | List files |

### 4. Create Migration Plan

Document step-by-step migration with rollback points.

---

## Refactoring Rules

### Rule 1: Single Source of Truth

**Every piece of data must have exactly ONE authoritative source.**

| Data Type | Source of Truth | Location |
|-----------|-----------------|----------|
| User Profile | Supabase | `profiles` table |
| Assessment Answers | Supabase | `assessments` table |
| Calculated Scores | API (server-side) | `/api/scoring` |
| UI State Only | Zustand | `useProfileStore` (cache only) |
| Navigation State | URL | Next.js router |

### Rule 2: No Duplicate Logic

Before writing ANY logic, check if it exists:

```bash
# Search for existing implementations
grep -r "functionName" lib/
grep -r "similar pattern" components/
```

If similar logic exists:
1. Extract to shared utility
2. Import from single location
3. Delete duplicates

### Rule 3: Validation at Boundaries

All data validation happens at system boundaries:

```
External Input → Zod Schema → Validated Data → Business Logic
```

**Boundaries requiring validation:**
- API route handlers (incoming requests)
- Supabase data fetches (database responses)
- localStorage reads (persisted state)
- URL parameters (navigation state)

### Rule 4: Type Safety Throughout

```typescript
// BAD: Type assertion without validation
const profile = data as Profile;

// GOOD: Runtime validation with Zod
const profile = ProfileSchema.parse(data);
```

### Rule 5: No Magic Numbers

```typescript
// BAD
const score = value ?? 0.5;

// GOOD
import { SCORE_DEFAULTS } from '@/lib/constants/scoring';
const score = value ?? SCORE_DEFAULTS.baseline;
```

---

## Post-Refactor Requirements

### 1. Update MASTER_SPEC.md

Every refactor MUST update the master spec:

```markdown
## Change Log Entry Format

### [Date] - Brief Description
- **Changed**: What was modified
- **Reason**: Why it was changed
- **Migration**: How to update dependent code
- **Breaking**: Yes/No - what breaks
```

### 2. Create Spec Update Record

Create `/docs/spec-updates/UPDATE_YYYYMMDD_description.md`:

```markdown
# Spec Update: [Description]

## Date: YYYY-MM-DD

## Summary
Brief description of changes

## Affected Sections in MASTER_SPEC.md
- Section X.X: [changes]
- Section Y.Y: [changes]

## Migration Steps
1. Step one
2. Step two

## Verification
- [ ] TypeScript compiles
- [ ] All tests pass
- [ ] Manual testing completed
- [ ] MASTER_SPEC.md updated
```

### 3. Verification Checklist

```bash
# Must pass before PR merge
npm run type-check   # Zero errors
npm run lint         # Zero errors
npm run build        # Successful build
```

### 4. Manual Test Scenarios

Run these scenarios after every significant refactor:

1. **Fresh Start Journey**: Empty profile through all frames
2. **Full Profile Journey**: Complete profile through all frames
3. **Partial Profile**: Mixed data through all frames
4. **Page Refresh**: State persistence on each frame
5. **Direct URL Access**: Navigate directly to each frame

---

## Emergency Rollback

If a refactor causes production issues:

```bash
# 1. Identify last stable commit
git log --oneline -10

# 2. Create rollback branch
git checkout -b rollback/issue-description

# 3. Revert to stable state
git revert <commit-hash>

# 4. Deploy immediately
# Follow deployment procedures
```

---

## Spec Maintenance Schedule

| Frequency | Action |
|-----------|--------|
| Every PR | Update MASTER_SPEC.md if architecture changes |
| Weekly | Review spec for accuracy |
| Monthly | Archive spec snapshot |
| Quarterly | Full spec audit |

---

## File Locations

| Document | Path | Purpose |
|----------|------|---------|
| Master Spec | `/docs/MASTER_SPEC.md` | Current system architecture |
| Refactor Audit | `/docs/REFACTOR_AUDIT.md` | Current issues to fix |
| Spec Updates | `/docs/spec-updates/` | Historical changes |
| This Protocol | `/docs/PLAN.md` | How to refactor |

---

## Ownership

- **Spec Owner**: Lead Developer
- **Update Approval**: Required for breaking changes
- **Audit Responsibility**: All contributors

---

*This protocol is mandatory. PRs that modify architecture without spec updates will be rejected.*
