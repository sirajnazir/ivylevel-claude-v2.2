# Spec Updates Directory

This directory contains historical records of all specification changes to IvyQuest.

## Purpose

Every time `MASTER_SPEC.md` is modified, a corresponding update record must be created here. This provides:

- **Audit Trail**: Track what changed and why
- **Rollback Reference**: Know how to undo changes if needed
- **Communication**: Team members can review changes

## File Naming Convention

```
UPDATE_YYYYMMDD_brief-description.md
```

Examples:
- `UPDATE_20251218_initial-spec.md`
- `UPDATE_20251220_scoring-refactor.md`
- `UPDATE_20251225_api-restructure.md`

## Update Record Template

Each update file should follow this structure:

```markdown
# Spec Update: [Brief Description]

## Date
YYYY-MM-DD

## Author
[Name or GitHub username]

## Summary
Brief description of what changed and why.

## Affected Sections in MASTER_SPEC.md
- Section X.X: [description of changes]
- Section Y.Y: [description of changes]

## Breaking Changes
- [ ] This update includes breaking changes

If yes, describe:
- What breaks
- How to migrate

## Migration Steps
1. Step one
2. Step two
3. ...

## Verification Checklist
- [ ] MASTER_SPEC.md updated
- [ ] TypeScript compiles (`npm run type-check`)
- [ ] Linting passes (`npm run lint`)
- [ ] Build succeeds (`npm run build`)
- [ ] Manual testing completed

## Related Issues/PRs
- Issue #XXX
- PR #XXX
```

## Archived Specs

When major versions of MASTER_SPEC.md are archived, they are stored here with the naming convention:

```
MASTER_SPEC_YYYYMMDD.md
```

## Current Version

The current authoritative spec is always at:

```
/docs/MASTER_SPEC.md
```

---

## Quick Commands

Archive current spec before major changes:
```bash
cp docs/MASTER_SPEC.md docs/spec-updates/MASTER_SPEC_$(date +%Y%m%d).md
```

Create new update record:
```bash
touch docs/spec-updates/UPDATE_$(date +%Y%m%d)_description.md
```
