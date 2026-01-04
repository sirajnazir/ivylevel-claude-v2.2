# IvyQuest v10.0 Deployment Guide

## Overview

This guide covers the blue-green deployment strategy for IvyQuest v10.0 with incremental feature flag rollout.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRODUCTION (Blue)                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Next.js    │───►│  Supabase   │    │  OpenAI     │         │
│  │  (v2.2)     │    │  (Postgres) │    │  GPT-4      │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     STAGING (Green)                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Next.js    │───►│  Supabase   │    │  Agent      │         │
│  │  (v10.0)    │    │  (v10 ext)  │    │  Service    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                              │                  │
│                     ┌─────────────────────────┐                 │
│                     │  Agno + LangGraph       │                 │
│                     │  Python/FastAPI         │                 │
│                     └─────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Pre-Deployment Checklist

### 1. Environment Variables

Ensure all required environment variables are set:

```bash
# Required
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
OPENAI_API_KEY=...

# v10.0 Specific
AGENT_SERVICE_URL=http://localhost:8000
ENABLE_V10_AGENTS=false  # Start disabled
```

### 2. Database Migrations

Run migrations in order:

```bash
# Connect to Supabase and run migrations
supabase db push

# Or manually run each migration:
# 002_archetypes.sql
# 003_profiles_v10.sql
# 004_crises.sql
# 005_chetty_baselines.sql
# 006_agent_state_versions.sql
# 007_opportunities_awards.sql
# 008_projects.sql
# 009_migrations_tracker.sql
```

### 3. Agent Service Setup

```bash
# Navigate to agents directory
cd agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Deployment Phases

### Phase 1: Feature Flag Rollout (Week 1-2)

#### Step 1: Deploy with all flags disabled
```bash
ENABLE_V10_AGENTS=false
```

#### Step 2: Enable Assessment Agent
```bash
ENABLE_V10_AGENTS=true
ENABLE_ASSESSMENT_AGENT=true
```

#### Step 3: Enable CRI Computation
```bash
ENABLE_CRI_COMPUTATION=true
```

#### Step 4: Enable Execution Agent
```bash
ENABLE_EXECUTION_AGENT=true
ENABLE_EDS_TRACKING=true
```

### Phase 2: Crisis Alchemy Rollout (Week 3-4)

#### Step 5: Enable Crisis Alchemy (internal testing)
```bash
ENABLE_CRISIS_ALCHEMY=true
ENABLE_HITL_MODE=true
```

#### Step 6: Enable Event Bus
```bash
ENABLE_EVENT_BUS=true
ENABLE_STATE_VERSIONING=true
```

### Phase 3: Full Agent Rollout (Week 5-6)

#### Step 7: Enable Game Plan Agent
```bash
ENABLE_GAMEPLAN_AGENT=true
```

#### Step 8: Enable Awards & Opportunity Agents
```bash
ENABLE_AWARDS_AGENT=true
ENABLE_OPPORTUNITY_AGENT=true
```

### Phase 4: UI Rollout (Week 7-8)

#### Step 9: Enable Dual View
```bash
ENABLE_DUAL_VIEW=true
```

## Rollback Procedure

If issues are detected:

1. **Immediate**: Set `ENABLE_V10_AGENTS=false` to disable all v10 features
2. **Per-feature**: Disable specific features by setting their flags to `false`
3. **Full rollback**: Revert to previous deployment version

```bash
# Quick rollback via Vercel CLI
vercel rollback

# Or via environment variables
vercel env rm ENABLE_V10_AGENTS production
vercel env add ENABLE_V10_AGENTS production  # Set to "false"
```

## Monitoring

### Key Metrics to Watch

1. **CRI Computation**
   - Target: All constrained profiles should have CRI > 1.0
   - Huda benchmark: CRI > 1.2

2. **Crisis Resolution Time**
   - Target: < 72 hours from detection to resolution
   - Alert threshold: > 48 hours without HITL response

3. **Scoring Success Rate (SSR)**
   - Target: 100%
   - Any scoring errors should trigger alert

4. **EDS (Execution Debt Score)**
   - Monitor average EDS across profiles
   - Alert if EDS > 50 for any profile

### Health Check Endpoints

```bash
# Agent service health
curl http://localhost:8000/health

# Next.js health
curl http://localhost:3006/api/health
```

## Testing Commands

```bash
# Run scoring tests
npm run test:scoring

# Run Huda benchmark
npm run test:e2e:huda

# Run agent tests
npm run test:e2e:agents

# Run all tests
npm run test:all
```

## Support

For deployment issues, check:
- `/docs/TECHNICAL_SPECIFICATION.md` - Full v10.0 spec
- `/docs/SCORING_ENGINE_SPECIFICATION.md` - Scoring details
- `/agents/README.md` - Agent service documentation

---

Last updated: December 2024
Version: 10.0
