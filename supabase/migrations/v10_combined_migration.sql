-- =====================================================
-- IvyQuest v10.0 - COMBINED MIGRATION FILE
-- =====================================================
-- Run this SINGLE file in Supabase SQL Editor to apply all v10.0 migrations
-- Or run individual migrations in order (002-009)
-- =====================================================
-- Version: 10.0.0
-- Date: December 2024
-- Total Tables: 10 new tables, 1 altered
-- =====================================================

-- IMPORTANT: Run the individual migration files in order:
-- 1. 001_create_assessments.sql (already exists)
-- 2. 002_archetypes.sql
-- 3. 003_profiles_v10.sql
-- 4. 004_crises.sql
-- 5. 005_chetty_baselines.sql
-- 6. 006_agent_state_versions.sql
-- 7. 007_opportunities_awards.sql
-- 8. 008_projects.sql
-- 9. 009_migrations_tracker.sql

-- This file is for reference - use individual files for cleaner migration history

-- =====================================================
-- QUICK START: Copy sections as needed
-- =====================================================

-- To verify all tables exist after migration:
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'assessments',      -- v2.2 existing
  'coach_sessions',   -- v2.2 existing
  'archetypes',       -- v10.0 new
  'profiles',         -- v10.0 new
  'crises',           -- v10.0 new
  'chetty_baselines', -- v10.0 new
  'agent_state_versions', -- v10.0 new
  'awards',           -- v10.0 new
  'opportunities',    -- v10.0 new
  'student_applications', -- v10.0 new
  'success_vectors',  -- v10.0 new
  'projects',         -- v10.0 new
  'project_steps',    -- v10.0 new
  'migrations_tracker' -- v10.0 new
)
ORDER BY table_name;

-- To check migration status:
SELECT * FROM migration_status;

-- To see P0 critical items:
SELECT * FROM critical_migrations;

-- =====================================================
-- ROLLBACK ALL v10.0 (USE WITH CAUTION)
-- =====================================================
-- Run these in REVERSE order if you need to rollback:

/*
-- 009 - Migrations Tracker
DROP VIEW IF EXISTS critical_migrations;
DROP VIEW IF EXISTS migration_status;
DROP FUNCTION IF EXISTS update_migration_status(TEXT, TEXT, TEXT);
DROP TABLE IF EXISTS migrations_tracker;

-- 008 - Projects
DROP VIEW IF EXISTS project_dashboard;
DROP VIEW IF EXISTS stalled_projects;
DROP FUNCTION IF EXISTS detect_blocked_projects();
DROP FUNCTION IF EXISTS calculate_eds(UUID);
DROP TRIGGER IF EXISTS project_steps_stats_update ON project_steps;
DROP FUNCTION IF EXISTS update_project_stats();
DROP TABLE IF EXISTS project_steps;
DROP TABLE IF EXISTS projects;
DROP TYPE IF EXISTS step_status;
DROP TYPE IF EXISTS project_type;
DROP TYPE IF EXISTS project_status;

-- 007 - Opportunities & Awards
DROP TABLE IF EXISTS success_vectors;
DROP TABLE IF EXISTS student_applications;
DROP TABLE IF EXISTS opportunities;
DROP TABLE IF EXISTS awards;
DROP TYPE IF EXISTS application_status;
DROP TYPE IF EXISTS opportunity_type;
DROP TYPE IF EXISTS award_level;
DROP TYPE IF EXISTS award_category;

-- 006 - Agent State Versions
DROP VIEW IF EXISTS human_overrides;
DROP VIEW IF EXISTS recent_state_changes;
DROP FUNCTION IF EXISTS rollback_to_version(UUID, TEXT, INTEGER, TEXT);
DROP FUNCTION IF EXISTS get_latest_state(UUID, TEXT);
DROP FUNCTION IF EXISTS get_state_at_version(UUID, TEXT, INTEGER);
DROP FUNCTION IF EXISTS create_state_version(UUID, TEXT, JSONB, TEXT, TEXT, TEXT, JSONB);
DROP FUNCTION IF EXISTS get_next_version(UUID, TEXT);
DROP TABLE IF EXISTS agent_state_versions;

-- 005 - Chetty Baselines
DROP FUNCTION IF EXISTS get_chetty_baseline(TEXT, TEXT);
DROP TABLE IF EXISTS chetty_baselines;

-- 004 - Crises
DROP VIEW IF EXISTS pending_crisis_approvals;
DROP TRIGGER IF EXISTS crisis_resolution_time ON crises;
DROP FUNCTION IF EXISTS calculate_crisis_resolution_time();
DROP TABLE IF EXISTS crises;
DROP TYPE IF EXISTS crisis_urgency;
DROP TYPE IF EXISTS crisis_type;
DROP TYPE IF EXISTS crisis_status;

-- 003 - Profiles v10
DROP FUNCTION IF EXISTS sync_profile_from_assessment(UUID);
DROP TABLE IF EXISTS profiles;

-- 002 - Archetypes
DROP TABLE IF EXISTS archetypes;
*/

-- =====================================================
-- END OF COMBINED MIGRATION FILE
-- =====================================================
