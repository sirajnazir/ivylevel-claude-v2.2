# Claude Code Handover Package v1.0
## IvyQuest Strategic Intelligence Enrichment

**Document Type**: Claude Code Operating Instructions
**Version**: 1.0
**Date**: January 2026
**Purpose**: Guardrails, best practices, and workflows for Claude Code execution

---

## Table of Contents

1. [Project Context](#1-project-context)
2. [Critical Guardrails](#2-critical-guardrails)
3. [Development Workflow](#3-development-workflow)
4. [Git Commit Standards](#4-git-commit-standards)
5. [Master Spec Update Protocol](#5-master-spec-update-protocol)
6. [Release Notes Protocol](#6-release-notes-protocol)
7. [File Structure Standards](#7-file-structure-standards)
8. [Quality Gates](#8-quality-gates)
9. [Error Handling](#9-error-handling)
10. [Communication Standards](#10-communication-standards)

---

## 1. Project Context

### 1.1 What We're Building

**IvyQuest GamePlan Platform** - AI-powered college admissions coaching

### 1.2 Current Task

**Strategic Intelligence Enrichment** - Adding IQ layer (strategy, tactics, frameworks) to existing awards (97) and programs (58) data.

### 1.3 Key Distinction

| Layer | Description | Status |
|-------|-------------|--------|
| **IQ Layer** | Frameworks, strategies, success patterns, what works | **ACTIVE - Building Now** |
| **EQ Layer** | Jenny's voice, tone, communication style | **PARKED - Future phase** |

### 1.4 Golden Reference

**Huda Case Study** - All enrichments should be validated against Huda's actual coaching journey for accuracy.

---

## 2. Critical Guardrails

### 2.1 NEVER Do These

- NEVER modify original seed files directly - Always create new *_enriched.* files
- NEVER skip checkpoint saves - Save progress every 5 items minimum
- NEVER commit without running validation - All commits must pass quality gates
- NEVER make bulk changes without backup - Git commit BEFORE major operations
- NEVER assume - always verify - Check file paths exist before operations
- NEVER skip documentation updates - Every feature change needs spec update

### 2.2 ALWAYS Do These

- ALWAYS work incrementally - Small, testable changes
- ALWAYS preserve original data - Create new files, don't overwrite
- ALWAYS validate before committing - Run validation script
- ALWAYS update documentation - Master spec reflects current state
- ALWAYS use semantic versioning - MAJOR.MINOR.PATCH
- ALWAYS include metadata - Timestamps on enrichments, version numbers

---

## 3. Development Workflow

### 3.1 Standard Development Cycle

1. PLAN - Define scope, check specs
2. BRANCH - Create feature branch
3. IMPLEMENT - Write code incrementally
4. TEST - Run validation, check outputs
5. DOCUMENT - Update specs, add release notes
6. COMMIT - Semantic commit message
7. REVIEW - Self-review checklist
8. MERGE - Merge to main, tag release

### 3.2 Enrichment-Specific Workflow

1. LOAD DATA - Verify counts (97 awards, 58 programs)
2. SELECT BATCH - Start with top 20
3. RUN ENRICHMENT - Process in batches of 5, checkpoint every 5
4. VALIDATE - Check tier distribution, archetype coverage
5. EXPORT - Generate enriched JSON files
6. COMMIT & DOCUMENT - Git commit with semantic message

---

## 4. Git Commit Standards

### 4.1 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 4.2 Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `data` | Data changes |
| `docs` | Documentation |
| `refactor` | Code refactoring |
| `test` | Adding tests |
| `chore` | Maintenance |

### 4.3 Scope Values

- `enrichment` - Enrichment engine and process
- `awards` - Awards data and processing
- `programs` - Programs/opportunities data
- `validation` - Validation logic
- `schema` - Data schema changes
- `spec` - Specification documents

---

## 5. File Structure Standards

```
/ivyquest/
├── agents/
│   ├── seeds/
│   │   ├── awards_data.py           # Original (READ-ONLY)
│   │   ├── opportunities_data.py    # Original (READ-ONLY)
│   │   └── enriched/                # Enriched outputs
│   │       ├── awards_enriched.json
│   │       ├── programs_enriched.json
│   │       └── enrichment_metadata.json
├── scripts/
│   └── enrich_strategic_intelligence.py
├── docs/
│   ├── MASTER_SPEC.md
│   ├── MASTER_SPEC_CHANGELOG.md
│   ├── CLAUDE_CODE_HANDOVER.md
│   └── releases/
│       └── v1.0.0.md
├── .enrichment_checkpoints/
│   ├── awards_checkpoint.json
│   └── programs_checkpoint.json
└── tests/
    └── test_enrichment.py
```

---

## 6. Quality Gates

### 6.1 Pre-Commit Quality Gates

Before any commit, verify:

1. JSON Validity - All JSON files parse correctly
2. Validation Pass - Run validation script
3. No Syntax Errors - Python files compile
4. Required Files Exist - Enriched outputs present

### 6.2 Validation Criteria

| Criterion | Threshold |
|-----------|-----------|
| Tier 1 distribution | 5-25% |
| Tier 2 distribution | 15-40% |
| Tier 3 distribution | 20-50% |
| Tier 4 distribution | 10-40% |
| Archetype coverage | >= 2 items with fit >= 0.7 |
| Success patterns count | >= 3 per item |
| Strategic notes length | >= 50 chars |

---

## 7. Quick Reference

### Commands Cheat Sheet

```bash
# Start enrichment (top 20 first)
python scripts/enrich_strategic_intelligence.py --mode top20

# Continue with remaining
python scripts/enrich_strategic_intelligence.py --mode remaining

# Enrich all at once
python scripts/enrich_strategic_intelligence.py --mode all

# Enrich single item
python scripts/enrich_strategic_intelligence.py --mode single --id "ncwit-aic"

# Validate results
python scripts/enrich_strategic_intelligence.py --validate

# Create backup tag
git tag -a "backup-$(date +%Y%m%d-%H%M)" -m "Backup"

# Standard commit
git add .
git commit -m "data(enrichment): [description]"

# Create release tag
git tag -a "v1.0.0" -m "Release v1.0.0"
```

### File Locations Quick Reference

| File | Location |
|------|----------|
| Enrichment script | `scripts/enrich_strategic_intelligence.py` |
| Original awards | `agents/seeds/awards_data.py` |
| Original programs | `agents/seeds/opportunities_data.py` |
| Enriched awards | `agents/seeds/enriched/awards_enriched.json` |
| Enriched programs | `agents/seeds/enriched/programs_enriched.json` |
| Checkpoints | `.enrichment_checkpoints/` |
| Master spec | `docs/MASTER_SPEC.md` |

---

*Document Version: 1.0*
*Created: January 2026*
*Purpose: Claude Code Operating Instructions*
