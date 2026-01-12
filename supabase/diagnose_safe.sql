-- =============================================================================
-- SAFE DATABASE DIAGNOSTIC (won't error on missing tables)
-- =============================================================================

-- 1. ALL TABLES
SELECT '=== ALL TABLES ===' as section;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- 2. ALL VIEWS
SELECT '=== ALL VIEWS ===' as section;
SELECT viewname FROM pg_views WHERE schemaname = 'public' ORDER BY viewname;

-- 3. ROW COUNTS
SELECT '=== ROW COUNTS ===' as section;
SELECT relname as table_name, n_live_tup as row_count
FROM pg_stat_user_tables WHERE schemaname = 'public' ORDER BY relname;

-- 4. V2.0 TABLES STATUS
SELECT '=== V2.0 TABLES STATUS ===' as section;
SELECT v2_table,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=v2_table)
         THEN 'EXISTS' ELSE 'MISSING' END as status
FROM (VALUES
    ('evaluation_golden'),('evaluation_runs'),('workflow_runs'),('notifications'),
    ('student_time_audits'),('weekly_plans'),('forbidden_phrases'),('speech_patterns'),
    ('jenny_voice_scores'),('crisis_transformations'),('program_redirects')
) AS t(v2_table) ORDER BY v2_table;

-- 5. CORE TABLES STATUS
SELECT '=== CORE TABLES STATUS ===' as section;
SELECT core_table,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=core_table)
         THEN 'EXISTS' ELSE 'MISSING' END as status
FROM (VALUES
    ('profiles'),('awards'),('opportunities'),('student_awards'),('projects'),('crises')
) AS t(core_table) ORDER BY core_table;

-- 6. COLUMNS ON EVALUATION_GOLDEN (if exists)
SELECT '=== EVALUATION_GOLDEN COLUMNS ===' as section;
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'evaluation_golden' ORDER BY ordinal_position;

-- 7. COLUMNS ON AWARDS (if exists)
SELECT '=== AWARDS COLUMNS ===' as section;
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'awards' ORDER BY ordinal_position;

-- 8. COLUMNS ON OPPORTUNITIES (if exists)
SELECT '=== OPPORTUNITIES COLUMNS ===' as section;
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'opportunities' ORDER BY ordinal_position;

-- 9. COLUMNS ON STUDENT_AWARDS (if exists)
SELECT '=== STUDENT_AWARDS COLUMNS ===' as section;
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'student_awards' ORDER BY ordinal_position;

-- 10. COLUMNS ON PROFILES (if exists)
SELECT '=== PROFILES COLUMNS ===' as section;
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'profiles' ORDER BY ordinal_position;

SELECT '=== DIAGNOSTIC COMPLETE ===' as section;
