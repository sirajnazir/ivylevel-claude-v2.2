# IvyLevel Documentation

**Version:** MVP 1.0.3
**Last Updated:** January 21, 2026 @ 20:15 PST
**Status:** Production

---

## Quick Links

| Document | Description |
|----------|-------------|
| [/STRUCTURE.md](/STRUCTURE.md) | **START HERE** - Complete project structure |
| [PRD.md](./PRD.md) | **MASTER SPEC** - Business + Product + UI/UX + Technical |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System architecture, tech stack, components |
| [DATABASE.md](./DATABASE.md) | Database schema, tables, migrations |
| [API.md](./API.md) | API endpoints reference |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Deployment and environment setup |
| [CHANGELOG.md](./CHANGELOG.md) | Version history and release notes |

---

## Project Structure (Quick Reference)

```
/                            # FRONTEND (Next.js)
├── app/                     # Next.js pages & routes
├── components/              # React components
├── lib/                     # Utilities & stores
├── hooks/                   # React hooks
└── types/                   # TypeScript types

/agents/                     # BACKEND (Python FastAPI)
├── agents/                  # Agent implementations
├── api/routes/              # API endpoints
├── proactive/               # Proactive system
└── main.py                  # Entry point

/supabase/migrations/        # DATABASE

/docs/                       # DOCUMENTATION (you are here)
```

**Full details:** See [/STRUCTURE.md](/STRUCTURE.md)

---

## Version Reference

**Current:** MVP 1.0.3

| Version | Type | When to Increment |
|---------|------|-------------------|
| MVP **X**.0.0 | Major | Breaking changes, major features |
| MVP 1.**Y**.0 | Feature | New features, enhancements |
| MVP 1.0.**Z** | Patch | Bug fixes, doc updates |

See [CHANGELOG.md](./CHANGELOG.md) for full history.

---

## Documentation Structure

```
/docs/                          # ← YOU ARE HERE (Master docs)
├── README.md                   # This index
├── ARCHITECTURE.md             # System architecture
├── DATABASE.md                 # Database specification
├── API.md                      # API reference
├── DEPLOYMENT.md               # Deployment guide
├── CHANGELOG.md                # Version history
└── runbooks/                   # Operational guides
    └── TROUBLESHOOTING.md

/agents/docs/                   # Backend-specific docs
├── README.md                   # Backend overview
├── AGENTS.md                   # Agent catalog & details
└── PROACTIVE.md                # Proactive system guide

/app/docs/                      # Frontend-specific docs
├── README.md                   # Frontend overview
├── COMPONENTS.md               # Component library guide
└── FRAMES.md                   # Assessment frames guide
```

---

## Naming Conventions

### For Canonical Docs (Current/Active)
```
UPPERCASE_NAME.md              # e.g., ARCHITECTURE.md, DATABASE.md
```
These are the **single source of truth**. Update in place.

### For Dated Specs (Planning/Design)
```
SPEC_<topic>_YYYYMMDD.md       # e.g., SPEC_PAYMENTS_20260201.md
```
Use for new feature planning. Move to `_archive/` when implemented.

### For Versioned Releases
```
Release notes go in CHANGELOG.md with version headers
```

---

## Keeping Docs Updated

1. **ARCHITECTURE.md** - Update when adding new components/services
2. **DATABASE.md** - Update when adding migrations
3. **API.md** - Update when adding/changing endpoints
4. **CHANGELOG.md** - Update on every release

---

## Archive

Old documentation, completed specs, and historical versions are in:
```
/_archive/docs/
├── specs/        # Completed implementation specs
├── analyses/     # Bug reports, audits, gap analyses
└── iterations/   # Old version documents (v1-v9)
```

To find old docs: `ls _archive/docs/`
