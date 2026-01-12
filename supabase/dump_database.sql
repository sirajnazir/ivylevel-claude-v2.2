-- =============================================================================
-- IVYQUEST DATABASE COMPREHENSIVE DUMP SCRIPT
-- =============================================================================
-- Run this in Supabase SQL Editor to get a complete dump of all data
-- Output shows table structure, row counts, and sample data
-- =============================================================================

-- =============================================
-- SECTION 1: TABLE INVENTORY
-- =============================================

SELECT '=== TABLE INVENTORY ===' as section;

SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;


-- =============================================
-- SECTION 2: ROW COUNTS FOR ALL TABLES
-- =============================================

SELECT '=== ROW COUNTS ===' as section;

-- This query gets counts for all public tables
SELECT
    schemaname,
    relname as table_name,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;


-- =============================================
-- SECTION 3: V2.0 SPECIFIC TABLES - FULL DUMP
-- =============================================

-- 3.1 Forbidden Phrases (Jenny Voice)
SELECT '=== FORBIDDEN PHRASES ===' as section;
SELECT * FROM forbidden_phrases ORDER BY severity, phrase;

-- 3.2 Speech Patterns (Jenny Voice)
SELECT '=== SPEECH PATTERNS ===' as section;
SELECT * FROM speech_patterns ORDER BY pattern_type;

-- 3.3 Crisis Transformations
SELECT '=== CRISIS TRANSFORMATIONS ===' as section;
SELECT * FROM crisis_transformations ORDER BY crisis_type;

-- 3.4 Program Redirects
SELECT '=== PROGRAM REDIRECTS ===' as section;
SELECT * FROM program_redirects ORDER BY program_category;

-- 3.5 Student Time Audits
SELECT '=== STUDENT TIME AUDITS (SAMPLE) ===' as section;
SELECT * FROM student_time_audits ORDER BY created_at DESC LIMIT 20;

-- 3.6 Weekly Plans
SELECT '=== WEEKLY PLANS (SAMPLE) ===' as section;
SELECT * FROM weekly_plans ORDER BY created_at DESC LIMIT 20;

-- 3.7 Evaluation Golden Dataset
SELECT '=== EVALUATION GOLDEN DATASET ===' as section;
SELECT id, profile_id, difficulty_tier, tags, quality_tier, category, created_at
FROM evaluation_golden
ORDER BY created_at DESC
LIMIT 50;

-- 3.8 Evaluation Runs
SELECT '=== EVALUATION RUNS (RECENT) ===' as section;
SELECT * FROM evaluation_runs ORDER BY created_at DESC LIMIT 20;

-- 3.9 Workflow Runs
SELECT '=== WORKFLOW RUNS (RECENT) ===' as section;
SELECT * FROM workflow_runs ORDER BY run_at DESC LIMIT 20;

-- 3.10 Jenny Voice Scores
SELECT '=== JENNY VOICE SCORES (RECENT) ===' as section;
SELECT * FROM jenny_voice_scores ORDER BY created_at DESC LIMIT 20;


-- =============================================
-- SECTION 4: CORE TABLES - SAMPLE DATA
-- =============================================

-- 4.1 Profiles (sample)
SELECT '=== PROFILES (SAMPLE) ===' as section;
SELECT id, user_id, first_name, email, grade, cri, narrative_dna IS NOT NULL as has_narrative, created_at
FROM profiles
ORDER BY created_at DESC
LIMIT 20;

-- 4.2 Awards (all)
SELECT '=== AWARDS ===' as section;
SELECT id, name, category, selectivity_percentile, vulnerability_story_boost, deadline
FROM awards
ORDER BY name
LIMIT 50;

-- 4.3 Opportunities (sample)
SELECT '=== OPPORTUNITIES (SAMPLE) ===' as section;
SELECT id, name, category, tier, cost_numeric, redirect_trigger, deadline
FROM opportunities
ORDER BY tier, name
LIMIT 50;

-- 4.4 Student Awards (sample)
SELECT '=== STUDENT AWARDS (SAMPLE) ===' as section;
SELECT sa.id, sa.profile_id, a.name as award_name, sa.status,
       sa.calculated_probability, sa.portfolio_tier,
       sa.vulnerability_bonus, sa.identity_alignment_bonus
FROM student_awards sa
LEFT JOIN awards a ON sa.award_id = a.id
ORDER BY sa.created_at DESC
LIMIT 30;


-- =============================================
-- SECTION 5: VIEWS - DATA
-- =============================================

-- 5.1 Workflow Performance View
SELECT '=== V_WORKFLOW_PERFORMANCE ===' as section;
SELECT * FROM v_workflow_performance;

-- 5.2 Recent Workflow Runs View
SELECT '=== V_RECENT_WORKFLOW_RUNS ===' as section;
SELECT * FROM v_recent_workflow_runs LIMIT 20;

-- 5.3 Student Award Portfolio View
SELECT '=== V_STUDENT_AWARD_PORTFOLIO ===' as section;
SELECT * FROM v_student_award_portfolio ORDER BY profile_id, portfolio_tier;

-- 5.4 Awards with Stats View
SELECT '=== V_AWARDS_WITH_STATS (SAMPLE) ===' as section;
SELECT id, name, selectivity_percentile, effective_selectivity, selectivity_tier, vulnerability_story_boost
FROM v_awards_with_stats
LIMIT 30;


-- =============================================
-- SECTION 6: COLUMN DETAILS FOR V2.0 TABLES
-- =============================================

SELECT '=== COLUMN DETAILS ===' as section;

SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN (
    'forbidden_phrases',
    'speech_patterns',
    'jenny_voice_scores',
    'crisis_transformations',
    'program_redirects',
    'student_time_audits',
    'weekly_plans',
    'evaluation_golden',
    'evaluation_runs',
    'workflow_runs'
)
ORDER BY table_name, ordinal_position;


-- =============================================
-- SECTION 7: CONSTRAINTS AND INDEXES
-- =============================================

SELECT '=== INDEXES ON V2.0 TABLES ===' as section;

SELECT
    indexname,
    tablename,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN (
    'forbidden_phrases',
    'speech_patterns',
    'jenny_voice_scores',
    'crisis_transformations',
    'program_redirects',
    'student_time_audits',
    'weekly_plans',
    'evaluation_golden',
    'evaluation_runs',
    'workflow_runs'
)
ORDER BY tablename, indexname;


-- =============================================
-- SECTION 8: SUMMARY STATISTICS
-- =============================================

SELECT '=== SUMMARY STATISTICS ===' as section;

SELECT 'forbidden_phrases' as table_name, COUNT(*) as count FROM forbidden_phrases
UNION ALL
SELECT 'speech_patterns', COUNT(*) FROM speech_patterns
UNION ALL
SELECT 'crisis_transformations', COUNT(*) FROM crisis_transformations
UNION ALL
SELECT 'program_redirects', COUNT(*) FROM program_redirects
UNION ALL
SELECT 'student_time_audits', COUNT(*) FROM student_time_audits
UNION ALL
SELECT 'weekly_plans', COUNT(*) FROM weekly_plans
UNION ALL
SELECT 'jenny_voice_scores', COUNT(*) FROM jenny_voice_scores
UNION ALL
SELECT 'evaluation_golden', COUNT(*) FROM evaluation_golden
UNION ALL
SELECT 'evaluation_runs', COUNT(*) FROM evaluation_runs
UNION ALL
SELECT 'workflow_runs', COUNT(*) FROM workflow_runs
ORDER BY table_name;

SELECT '=== DUMP COMPLETE ===' as section;
