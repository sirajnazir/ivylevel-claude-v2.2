# v2.0 Migrations Guide

## Overview

The v2.0 implementation requires migrations 020-025 to be run in order.

## Migration Order (MUST RUN IN SEQUENCE)

| Order | File | Purpose | Tables/Views Created |
|-------|------|---------|---------------------|
| 1 | `020_evaluation_and_workflows.sql` | Evaluation framework + workflows | `evaluation_golden`, `evaluation_runs`, `workflow_state`, `notifications`, `coach_tasks` |
| 2 | `021_workflow_runs.sql` | Workflow execution tracking | `workflow_runs`, `v_workflow_performance`, `v_recent_workflow_runs` |
| 3 | `022_golden_dataset_expansion.sql` | Golden dataset enhancements | Adds columns to `evaluation_golden` |
| 4 | `023_time_management.sql` | 168-hour framework | `student_time_audits`, `weekly_plans` |
| 5 | `024_jenny_voice.sql` | Voice patterns + crisis data | `forbidden_phrases`, `speech_patterns`, `jenny_voice_scores`, `crisis_transformations`, `program_redirects` |
| 6 | `025_awards_probability.sql` | 2-2-1 portfolio system | Adds columns to `student_awards`, `awards`, `opportunities` + views |

## How to Run

### Option 1: Supabase Dashboard (Recommended)

1. Go to your Supabase Dashboard → SQL Editor
2. Copy and paste each migration file content in order
3. Execute each one and verify success before proceeding

### Option 2: Supabase CLI

```bash
# If you have Supabase CLI configured
cd /Users/snazir/ivyquest-claude-v2.2

# Run each migration
supabase db push --file supabase/migrations/020_evaluation_and_workflows.sql
supabase db push --file supabase/migrations/021_workflow_runs.sql
supabase db push --file supabase/migrations/022_golden_dataset_expansion.sql
supabase db push --file supabase/migrations/023_time_management.sql
supabase db push --file supabase/migrations/024_jenny_voice.sql
supabase db push --file supabase/migrations/025_awards_probability.sql
```

### Option 3: Combined Script

Run the combined script below in the Supabase SQL Editor:

```sql
-- V2.0 COMBINED MIGRATIONS
-- Run this entire script in Supabase SQL Editor

-- ============================================
-- Migration 020: Evaluation & Workflows
-- ============================================
[Copy content from 020_evaluation_and_workflows.sql]

-- ============================================
-- Migration 021: Workflow Runs
-- ============================================
[Copy content from 021_workflow_runs.sql]

-- ... etc
```

## Verification Queries

After running migrations, verify with these queries:

```sql
-- Check all new tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'evaluation_golden',
  'evaluation_runs',
  'workflow_runs',
  'student_time_audits',
  'weekly_plans',
  'forbidden_phrases',
  'speech_patterns',
  'jenny_voice_scores',
  'crisis_transformations',
  'program_redirects'
);

-- Check seed data loaded
SELECT COUNT(*) as forbidden_count FROM forbidden_phrases;
SELECT COUNT(*) as patterns_count FROM speech_patterns;

-- Check views exist
SELECT viewname
FROM pg_views
WHERE schemaname = 'public'
AND viewname IN (
  'v_workflow_performance',
  'v_recent_workflow_runs',
  'v_student_award_portfolio',
  'v_awards_with_stats'
);
```

## Tables Created by v2.0

### 020: Evaluation Framework
- `evaluation_golden` - Golden benchmark examples from Jenny coaching
- `evaluation_runs` - Agent evaluation test results

### 021: Workflow Tracking
- `workflow_runs` - Proactive workflow execution history

### 023: Time Management
- `student_time_audits` - 168-hour framework audits
- `weekly_plans` - P0/P1/P2 weekly task plans

### 024: Jenny Voice
- `forbidden_phrases` - Phrases Jenny never uses (12 seeded)
- `speech_patterns` - Jenny's characteristic patterns (5 seeded)
- `jenny_voice_scores` - Voice validation scores
- `crisis_transformations` - Crisis Alchemy patterns
- `program_redirects` - Expensive program alternatives

### 025: Awards Probability
- Adds probability columns to `student_awards`
- Adds selectivity columns to `awards`
- Adds tier/redirect columns to `opportunities`
- Creates portfolio analysis views

## Seed Data

Migration 024 automatically seeds:
- 12 forbidden phrases with replacements
- 5 speech pattern categories with examples

## Rollback

If needed, rollback in reverse order:

```sql
-- CAUTION: This deletes data!
DROP TABLE IF EXISTS program_redirects CASCADE;
DROP TABLE IF EXISTS crisis_transformations CASCADE;
DROP TABLE IF EXISTS jenny_voice_scores CASCADE;
DROP TABLE IF EXISTS speech_patterns CASCADE;
DROP TABLE IF EXISTS forbidden_phrases CASCADE;
DROP TABLE IF EXISTS weekly_plans CASCADE;
DROP TABLE IF EXISTS student_time_audits CASCADE;
DROP TABLE IF EXISTS workflow_runs CASCADE;
DROP TABLE IF EXISTS evaluation_runs CASCADE;
DROP TABLE IF EXISTS evaluation_golden CASCADE;
```
