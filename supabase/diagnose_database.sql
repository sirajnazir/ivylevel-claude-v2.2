-- =============================================================================
-- IVYQUEST DATABASE DIAGNOSTIC SCRIPT
-- =============================================================================
-- Run this FIRST to see exactly what exists in your database
-- Then use this info to create the right migration
-- =============================================================================

-- =============================================================================
-- SECTION 1: ALL TABLES IN PUBLIC SCHEMA
-- =============================================================================
SELECT '=== ALL TABLES ===' as section;

SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;


-- =============================================================================
-- SECTION 2: ALL VIEWS IN PUBLIC SCHEMA
-- =============================================================================
SELECT '=== ALL VIEWS ===' as section;

SELECT viewname as view_name
FROM pg_views
WHERE schemaname = 'public'
ORDER BY viewname;


-- =============================================================================
-- SECTION 3: ROW COUNTS FOR ALL TABLES
-- =============================================================================
SELECT '=== ROW COUNTS ===' as section;

SELECT
    schemaname,
    relname as table_name,
    n_live_tup as approximate_row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY relname;


-- =============================================================================
-- SECTION 4: COLUMNS FOR KEY TABLES (if they exist)
-- =============================================================================

-- 4.1 Check profiles table columns
SELECT '=== PROFILES COLUMNS ===' as section;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'profiles'
ORDER BY ordinal_position;

-- 4.2 Check awards table columns
SELECT '=== AWARDS COLUMNS ===' as section;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'awards'
ORDER BY ordinal_position;

-- 4.3 Check opportunities table columns
SELECT '=== OPPORTUNITIES COLUMNS ===' as section;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'opportunities'
ORDER BY ordinal_position;

-- 4.4 Check student_awards table columns
SELECT '=== STUDENT_AWARDS COLUMNS ===' as section;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'student_awards'
ORDER BY ordinal_position;

-- 4.5 Check evaluation_golden table columns (v2.0)
SELECT '=== EVALUATION_GOLDEN COLUMNS ===' as section;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'evaluation_golden'
ORDER BY ordinal_position;


-- =============================================================================
-- SECTION 5: CHECK WHICH V2.0 TABLES EXIST
-- =============================================================================
SELECT '=== V2.0 TABLES STATUS ===' as section;

SELECT
    v2_table,
    CASE WHEN t.table_name IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END as status
FROM (
    VALUES
        ('evaluation_golden'),
        ('evaluation_runs'),
        ('workflow_runs'),
        ('notifications'),
        ('student_time_audits'),
        ('weekly_plans'),
        ('forbidden_phrases'),
        ('speech_patterns'),
        ('jenny_voice_scores'),
        ('crisis_transformations'),
        ('program_redirects')
) AS v2(v2_table)
LEFT JOIN information_schema.tables t
    ON t.table_schema = 'public' AND t.table_name = v2.v2_table
ORDER BY v2_table;


-- =============================================================================
-- SECTION 6: CHECK WHICH V2.0 COLUMNS EXIST ON EXISTING TABLES
-- =============================================================================
SELECT '=== V2.0 COLUMNS ON AWARDS ===' as section;

SELECT
    v2_col,
    CASE WHEN c.column_name IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END as status
FROM (
    VALUES
        ('selectivity_percentile'),
        ('accepts_per_year'),
        ('applicants_per_year'),
        ('ideal_candidate_profile'),
        ('jenny_strategy'),
        ('vulnerability_story_boost')
) AS v2(v2_col)
LEFT JOIN information_schema.columns c
    ON c.table_schema = 'public' AND c.table_name = 'awards' AND c.column_name = v2.v2_col
ORDER BY v2_col;

SELECT '=== V2.0 COLUMNS ON OPPORTUNITIES ===' as section;

SELECT
    v2_col,
    CASE WHEN c.column_name IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END as status
FROM (
    VALUES
        ('tier'),
        ('jenny_note'),
        ('cost_numeric'),
        ('redirect_trigger')
) AS v2(v2_col)
LEFT JOIN information_schema.columns c
    ON c.table_schema = 'public' AND c.table_name = 'opportunities' AND c.column_name = v2.v2_col
ORDER BY v2_col;

SELECT '=== V2.0 COLUMNS ON STUDENT_AWARDS ===' as section;

SELECT
    v2_col,
    CASE WHEN c.column_name IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END as status
FROM (
    VALUES
        ('calculated_probability'),
        ('fit_score'),
        ('competition_factor'),
        ('submission_quality_score'),
        ('vulnerability_bonus'),
        ('identity_alignment_bonus'),
        ('portfolio_tier')
) AS v2(v2_col)
LEFT JOIN information_schema.columns c
    ON c.table_schema = 'public' AND c.table_name = 'student_awards' AND c.column_name = v2.v2_col
ORDER BY v2_col;

SELECT '=== V2.0 COLUMNS ON EVALUATION_GOLDEN ===' as section;

SELECT
    v2_col,
    CASE WHEN c.column_name IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END as status
FROM (
    VALUES
        ('agent_type'),
        ('jenny_techniques'),
        ('source_session'),
        ('quality_tier'),
        ('student_profile_name'),
        ('jenny_response_example'),
        ('transformation_pattern'),
        ('category')
) AS v2(v2_col)
LEFT JOIN information_schema.columns c
    ON c.table_schema = 'public' AND c.table_name = 'evaluation_golden' AND c.column_name = v2.v2_col
ORDER BY v2_col;


-- =============================================================================
-- SECTION 7: SAMPLE DATA FROM KEY TABLES (if they exist)
-- =============================================================================
SELECT '=== SAMPLE DATA ===' as section;

-- Check forbidden_phrases content
SELECT '--- forbidden_phrases ---' as table_sample;
SELECT * FROM forbidden_phrases LIMIT 5;

-- Check speech_patterns content
SELECT '--- speech_patterns ---' as table_sample;
SELECT * FROM speech_patterns LIMIT 5;


-- =============================================================================
-- SECTION 8: FUNCTIONS AND TRIGGERS
-- =============================================================================
SELECT '=== FUNCTIONS ===' as section;

SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_name;

SELECT '=== TRIGGERS ===' as section;

SELECT trigger_name, event_object_table, action_timing, event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;


-- =============================================================================
-- SUMMARY
-- =============================================================================
SELECT '=== DIAGNOSTIC COMPLETE ===' as section;
SELECT 'Copy the output above and share it so I can create the correct migration' as next_step;
