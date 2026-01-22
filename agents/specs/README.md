# Agent Specs (Planning)

This folder is for **new feature planning specs** only.

---

## Current Documentation

Canonical documentation is now in:

| Location | Content |
|----------|---------|
| `/docs/` | Master docs (ARCHITECTURE, DATABASE, API, DEPLOYMENT, CHANGELOG) |
| `/agents/docs/` | Backend-specific docs (AGENTS, PROACTIVE) |
| `/app/docs/` | Frontend-specific docs (COMPONENTS, FRAMES) |

---

## Using This Folder

### For New Features

When planning a new feature, create a dated spec:

```
SPEC_<feature>_YYYYMMDD.md
```

Example: `SPEC_PAYMENTS_20260215.md`

### After Implementation

Move completed specs to:
```
/_archive/docs/specs/
```

---

## Archive

Historical specs are in `/_archive/docs/specs/`:
- Phase 3 weekly specs (PHASE3_WEEK1-5)
- Platform architecture specs
- Proactive autonomy spec (now in /agents/docs/PROACTIVE.md)
- Agent state docs (now in /agents/docs/AGENTS.md)
