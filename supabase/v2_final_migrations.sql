-- =============================================================================
-- IVYQUEST v2.0 FINAL COMBINED MIGRATIONS (BULLETPROOF VERSION)
-- =============================================================================
-- Run this ENTIRE script in Supabase SQL Editor
-- Handles all edge cases and missing columns gracefully
-- =============================================================================

-- Utility function for updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_time_audit_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- PART 1: CREATE NEW TABLES (these are safe - IF NOT EXISTS)
-- =============================================================================

-- 1.1 Evaluation Golden Dataset
CREATE TABLE IF NOT EXISTS public.evaluation_golden (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id TEXT NOT NULL,
  input_profile JSONB NOT NULL DEFAULT '{}'::jsonb,
  expected_outputs JSONB NOT NULL DEFAULT '{}'::jsonb,
  jenny_annotations JSONB DEFAULT '{}',
  difficulty_tier TEXT,
  tags TEXT[] DEFAULT '{}',
  agent_type VARCHAR(50),
  jenny_techniques TEXT[],
  source_session VARCHAR(50),
  quality_tier VARCHAR(20) DEFAULT 'standard',
  student_profile_name VARCHAR(100),
  jenny_response_example TEXT,
  transformation_pattern VARCHAR(200),
  category VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.2 Evaluation Runs
CREATE TABLE IF NOT EXISTS public.evaluation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id TEXT NOT NULL,
  agent_version TEXT NOT NULL,
  golden_id UUID,
  actual_outputs JSONB NOT NULL DEFAULT '{}'::jsonb,
  objective_scores JSONB DEFAULT '{}',
  subjective_scores JSONB DEFAULT '{}',
  overall_score DECIMAL(5,2),
  passed BOOLEAN DEFAULT false,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.3 Workflow Runs
CREATE TABLE IF NOT EXISTS public.workflow_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_name TEXT NOT NULL,
  success BOOLEAN NOT NULL DEFAULT false,
  profiles_processed INTEGER DEFAULT 0,
  notifications_sent INTEGER DEFAULT 0,
  errors TEXT[] DEFAULT '{}',
  duration_ms INTEGER,
  run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.4 Notifications
CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  data JSONB DEFAULT '{}',
  priority TEXT DEFAULT 'normal',
  channel TEXT DEFAULT 'in_app',
  read BOOLEAN DEFAULT false,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.5 Student Time Audits (168-hour framework)
CREATE TABLE IF NOT EXISTS public.student_time_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID,
    audit_date TIMESTAMPTZ DEFAULT NOW(),
    sleep_hours DECIMAL(4,2) DEFAULT 8,
    school_hours DECIMAL(4,2) DEFAULT 7.5,
    commute_minutes INTEGER DEFAULT 30,
    religious_hours DECIMAL(4,2) DEFAULT 0,
    misc_hours DECIMAL(4,2) DEFAULT 3,
    social_media_current DECIMAL(4,2),
    social_media_target DECIMAL(4,2) DEFAULT 1,
    hours_recovered DECIMAL(4,2),
    fixed_total DECIMAL(5,2),
    flexible_total DECIMAL(5,2),
    passion_hours_available DECIMAL(5,2),
    daily_passion_hours DECIMAL(4,2),
    schedule_template JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.6 Weekly Plans (P0/P1/P2)
CREATE TABLE IF NOT EXISTS public.weekly_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID,
    week_start DATE NOT NULL DEFAULT CURRENT_DATE,
    week_end DATE NOT NULL DEFAULT CURRENT_DATE + 7,
    p0_tasks JSONB DEFAULT '[]'::jsonb,
    p1_tasks JSONB DEFAULT '[]'::jsonb,
    p2_tasks JSONB DEFAULT '[]'::jsonb,
    total_hours_estimated DECIMAL(5,2),
    total_hours_available DECIMAL(5,2),
    buffer_hours DECIMAL(4,2),
    p0_completed INTEGER DEFAULT 0,
    p1_completed INTEGER DEFAULT 0,
    p2_completed INTEGER DEFAULT 0,
    completion_rate DECIMAL(3,2),
    flexibility_note TEXT DEFAULT 'We''ll try this for 2 weeks and adjust if needed',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.7 Forbidden Phrases (Jenny Voice)
CREATE TABLE IF NOT EXISTS public.forbidden_phrases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phrase TEXT NOT NULL,
    replacement TEXT,
    reason TEXT,
    severity VARCHAR(20) DEFAULT 'high',
    category VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.8 Speech Patterns (Jenny Voice)
CREATE TABLE IF NOT EXISTS public.speech_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    examples TEXT[] NOT NULL DEFAULT '{}',
    usage_context TEXT,
    frequency_target VARCHAR(50),
    required_position VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.9 Jenny Voice Scores
CREATE TABLE IF NOT EXISTS public.jenny_voice_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID,
    agent_type VARCHAR(50) NOT NULL,
    response_id VARCHAR(100),
    forbidden_absence_score DECIMAL(3,1),
    warmth_first_score DECIMAL(3,1),
    agency_preservation_score DECIMAL(3,1),
    speech_patterns_score DECIMAL(3,1),
    exclamation_calibration_score DECIMAL(3,1),
    checkin_question_score DECIMAL(3,1),
    total_score DECIMAL(4,2),
    passing BOOLEAN,
    forbidden_found TEXT[],
    issues TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.10 Crisis Transformations (Crisis Alchemy)
CREATE TABLE IF NOT EXISTS public.crisis_transformations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crisis_type VARCHAR(100) NOT NULL,
    situation_description TEXT NOT NULL,
    validation_script TEXT NOT NULL,
    micro_action_script TEXT NOT NULL,
    reframe_script TEXT NOT NULL,
    pivot_activity TEXT NOT NULL,
    transformation_from VARCHAR(200),
    transformation_to VARCHAR(200),
    source_student VARCHAR(100),
    source_session VARCHAR(50),
    quality_tier VARCHAR(20) DEFAULT 'gold',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.11 Program Redirects ($5K+ alternatives)
CREATE TABLE IF NOT EXISTS public.program_redirects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expensive_program VARCHAR(200) NOT NULL,
    cost_threshold INTEGER DEFAULT 5000,
    program_category VARCHAR(100),
    redirect_reason TEXT,
    free_alternatives TEXT[] NOT NULL DEFAULT '{}',
    self_directed_suggestion TEXT,
    jenny_quote TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- =============================================================================
-- PART 2: CREATE INDEXES (safe - IF NOT EXISTS)
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_evaluation_golden_difficulty ON evaluation_golden(difficulty_tier);
CREATE INDEX IF NOT EXISTS idx_evaluation_golden_tags ON evaluation_golden USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_golden_agent_type ON evaluation_golden(agent_type);
CREATE INDEX IF NOT EXISTS idx_golden_category ON evaluation_golden(category);
CREATE INDEX IF NOT EXISTS idx_golden_quality_tier ON evaluation_golden(quality_tier);

CREATE INDEX IF NOT EXISTS idx_evaluation_runs_run_id ON evaluation_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_version ON evaluation_runs(agent_version);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_passed ON evaluation_runs(passed);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_name ON workflow_runs(workflow_name);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_run_at ON workflow_runs(run_at DESC);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_success ON workflow_runs(success);

CREATE INDEX IF NOT EXISTS idx_notifications_profile ON notifications(profile_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(profile_id, read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);

CREATE INDEX IF NOT EXISTS idx_time_audits_profile ON student_time_audits(profile_id);
CREATE INDEX IF NOT EXISTS idx_time_audits_date ON student_time_audits(audit_date DESC);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_profile ON weekly_plans(profile_id);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_week ON weekly_plans(week_start);

CREATE INDEX IF NOT EXISTS idx_forbidden_severity ON forbidden_phrases(severity);
CREATE INDEX IF NOT EXISTS idx_forbidden_category ON forbidden_phrases(category);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON speech_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_voice_scores_profile ON jenny_voice_scores(profile_id);
CREATE INDEX IF NOT EXISTS idx_voice_scores_agent ON jenny_voice_scores(agent_type);
CREATE INDEX IF NOT EXISTS idx_crisis_type ON crisis_transformations(crisis_type);
CREATE INDEX IF NOT EXISTS idx_crisis_quality ON crisis_transformations(quality_tier);


-- =============================================================================
-- PART 3: ADD COLUMNS TO EXISTING TABLES (with error handling)
-- =============================================================================

-- 3.1 Add columns to student_awards (if table exists)
DO $$
BEGIN
    -- Check if student_awards table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'student_awards') THEN
        -- Add each column individually with error handling
        BEGIN
            ALTER TABLE student_awards ADD COLUMN calculated_probability DECIMAL(5,2);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE student_awards ADD COLUMN fit_score DECIMAL(5,2);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE student_awards ADD COLUMN competition_factor DECIMAL(5,2);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE student_awards ADD COLUMN submission_quality_score DECIMAL(5,2);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE student_awards ADD COLUMN vulnerability_bonus BOOLEAN DEFAULT FALSE;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE student_awards ADD COLUMN identity_alignment_bonus BOOLEAN DEFAULT FALSE;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE student_awards ADD COLUMN portfolio_tier VARCHAR(20);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;
    END IF;
END $$;

-- 3.2 Add columns to awards (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'awards') THEN
        BEGIN
            ALTER TABLE awards ADD COLUMN selectivity_percentile INTEGER;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE awards ADD COLUMN accepts_per_year INTEGER;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE awards ADD COLUMN applicants_per_year INTEGER;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE awards ADD COLUMN ideal_candidate_profile JSONB;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE awards ADD COLUMN jenny_strategy TEXT;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE awards ADD COLUMN vulnerability_story_boost BOOLEAN DEFAULT FALSE;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;
    END IF;
END $$;

-- 3.3 Add columns to opportunities (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'opportunities') THEN
        BEGIN
            ALTER TABLE opportunities ADD COLUMN tier INTEGER DEFAULT 3;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE opportunities ADD COLUMN jenny_note TEXT;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE opportunities ADD COLUMN cost_numeric INTEGER DEFAULT 0;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;

        BEGIN
            ALTER TABLE opportunities ADD COLUMN redirect_trigger BOOLEAN DEFAULT FALSE;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END;
    END IF;
END $$;


-- =============================================================================
-- PART 4: SEED DATA (with conflict handling)
-- =============================================================================

-- 4.1 Seed forbidden phrases
INSERT INTO forbidden_phrases (phrase, replacement, reason, severity, category)
SELECT * FROM (VALUES
    ('but', 'and', 'Creates opposition, negates previous statement', 'high', 'connectors'),
    ('however', 'and', 'Too formal, creates opposition', 'high', 'connectors'),
    ('you should have', 'next time, you might try', 'Implies past failure', 'high', 'criticism'),
    ('that''s wrong', 'let''s look at this differently', 'Direct criticism', 'high', 'criticism'),
    ('you need to', 'it would help to', 'Removes agency', 'high', 'directives'),
    ('I told you', 'as we discussed', 'Implies student error', 'high', 'criticism'),
    ('unfortunately', 'let''s figure out how to', 'Negative framing', 'high', 'framing'),
    ('to be honest', NULL, 'Filler, implies previous dishonesty', 'medium', 'fillers'),
    ('with all due respect', NULL, 'Passive aggressive', 'medium', 'fillers'),
    ('actually', NULL, 'Condescending correction', 'medium', 'fillers'),
    ('basically', NULL, 'Oversimplifying filler', 'medium', 'fillers'),
    ('obviously', NULL, 'Makes student feel dumb', 'medium', 'fillers')
) AS v(phrase, replacement, reason, severity, category)
WHERE NOT EXISTS (SELECT 1 FROM forbidden_phrases WHERE forbidden_phrases.phrase = v.phrase);

-- 4.2 Seed speech patterns
INSERT INTO speech_patterns (pattern_type, pattern_name, examples, usage_context, frequency_target, required_position)
SELECT * FROM (VALUES
    ('warmth', 'positive_acknowledgment', ARRAY['No worries!', 'Great!', 'That''s so cool!', 'I love it!', 'Perfect!', 'Awesome!'], 'Start of responses, after student shares', 'Every response', 'opening'),
    ('agency', 'check_in_questions', ARRAY['What do you think?', 'Does that make sense?', 'How does that feel?', 'What sounds best to you?'], 'End of suggestions', 'Every response', 'closing'),
    ('softening', 'suggestion_softeners', ARRAY['I feel like...', 'Maybe we can...', 'What if you just...', 'Have you considered...'], 'Before making recommendations', '2-3 per response', 'before_suggestions'),
    ('enthusiasm', 'genuine_excitement', ARRAY['Wow!', 'Amazing!', 'This is brilliant!', 'I''m so excited about this!'], 'When student achieves or shares wins', 'When appropriate', 'contextual'),
    ('flexibility', 'adjustment_phrases', ARRAY['We''ll try this for 2 weeks and adjust', 'Let''s see how this feels', 'We can always pivot'], 'When proposing plans', 'Once per plan', 'after_proposals')
) AS v(pattern_type, pattern_name, examples, usage_context, frequency_target, required_position)
WHERE NOT EXISTS (SELECT 1 FROM speech_patterns WHERE speech_patterns.pattern_name = v.pattern_name);


-- =============================================================================
-- PART 5: UPDATE EXISTING DATA (safe updates)
-- =============================================================================

-- 5.1 Update awards selectivity (if table and column exist)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'awards' AND column_name = 'selectivity_percentile') THEN
        UPDATE awards SET selectivity_percentile = 30, vulnerability_story_boost = true WHERE name ILIKE '%ncwit%' AND selectivity_percentile IS NULL;
        UPDATE awards SET selectivity_percentile = 50 WHERE name ILIKE '%congressional%' AND selectivity_percentile IS NULL;
        UPDATE awards SET selectivity_percentile = 5, vulnerability_story_boost = true WHERE name ILIKE '%coolidge%' AND selectivity_percentile IS NULL;
        UPDATE awards SET selectivity_percentile = 2, vulnerability_story_boost = true WHERE name ILIKE '%cameron%' AND selectivity_percentile IS NULL;
        UPDATE awards SET selectivity_percentile = 20 WHERE name ILIKE '%scholastic%' AND selectivity_percentile IS NULL;
        UPDATE awards SET selectivity_percentile = 15 WHERE (name ILIKE '%regeneron%' OR name ILIKE '%science talent%') AND selectivity_percentile IS NULL;
        UPDATE awards SET selectivity_percentile = 25 WHERE name ILIKE '%usaco%' AND selectivity_percentile IS NULL;
        UPDATE awards SET selectivity_percentile = 40 WHERE (name ILIKE '%amc%' OR name ILIKE '%math olympiad%') AND selectivity_percentile IS NULL;
    END IF;
END $$;

-- 5.2 Update opportunities tiers (if table and column exist)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'opportunities' AND column_name = 'tier') THEN
        UPDATE opportunities SET tier = 4, redirect_trigger = true WHERE cost_numeric >= 5000;
        UPDATE opportunities SET tier = 3 WHERE tier IS NULL;
    END IF;
END $$;


-- =============================================================================
-- PART 6: CREATE VIEWS (only if required columns exist)
-- =============================================================================

-- 6.1 Workflow Performance View
CREATE OR REPLACE VIEW public.v_workflow_performance AS
SELECT
  workflow_name,
  COUNT(*) as total_runs,
  SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_runs,
  ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as success_rate,
  SUM(profiles_processed) as total_profiles_processed,
  SUM(notifications_sent) as total_notifications_sent,
  AVG(duration_ms)::INTEGER as avg_duration_ms,
  MAX(run_at) as last_run_at
FROM workflow_runs
WHERE run_at > NOW() - INTERVAL '30 days'
GROUP BY workflow_name;

-- 6.2 Recent Workflow Runs View
CREATE OR REPLACE VIEW public.v_recent_workflow_runs AS
SELECT
  id,
  workflow_name,
  success,
  profiles_processed,
  notifications_sent,
  array_length(errors, 1) as error_count,
  duration_ms,
  run_at,
  CASE
    WHEN run_at > NOW() - INTERVAL '1 hour' THEN 'recent'
    WHEN run_at > NOW() - INTERVAL '24 hours' THEN 'today'
    WHEN run_at > NOW() - INTERVAL '7 days' THEN 'this_week'
    ELSE 'older'
  END as recency
FROM workflow_runs
ORDER BY run_at DESC
LIMIT 100;

-- 6.3 Student Award Portfolio View (only if columns exist)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'student_awards' AND column_name = 'portfolio_tier'
    ) THEN
        EXECUTE '
            CREATE OR REPLACE VIEW public.v_student_award_portfolio AS
            SELECT
                sa.profile_id,
                sa.portfolio_tier,
                COUNT(*) as award_count,
                AVG(sa.calculated_probability) as avg_probability,
                SUM(CASE WHEN sa.vulnerability_bonus THEN 1 ELSE 0 END) as vulnerability_bonus_count,
                SUM(CASE WHEN sa.identity_alignment_bonus THEN 1 ELSE 0 END) as identity_bonus_count
            FROM student_awards sa
            WHERE sa.portfolio_tier IS NOT NULL
            GROUP BY sa.profile_id, sa.portfolio_tier
        ';
    END IF;
END $$;

-- 6.4 Awards with Stats View (only if columns exist)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'awards' AND column_name = 'selectivity_percentile'
    ) THEN
        EXECUTE '
            CREATE OR REPLACE VIEW public.v_awards_with_stats AS
            SELECT
                a.*,
                COALESCE(a.selectivity_percentile, 50) as effective_selectivity,
                CASE
                    WHEN a.selectivity_percentile <= 10 THEN ''highly_selective''
                    WHEN a.selectivity_percentile <= 30 THEN ''selective''
                    WHEN a.selectivity_percentile <= 60 THEN ''competitive''
                    ELSE ''accessible''
                END as selectivity_tier
            FROM awards a
        ';
    END IF;
END $$;


-- =============================================================================
-- PART 7: CREATE TRIGGERS
-- =============================================================================

DROP TRIGGER IF EXISTS evaluation_golden_updated_at ON evaluation_golden;
CREATE TRIGGER evaluation_golden_updated_at
  BEFORE UPDATE ON evaluation_golden
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trigger_time_audit_updated ON student_time_audits;
CREATE TRIGGER trigger_time_audit_updated
    BEFORE UPDATE ON student_time_audits
    FOR EACH ROW
    EXECUTE FUNCTION update_time_audit_timestamp();

DROP TRIGGER IF EXISTS trigger_weekly_plan_updated ON weekly_plans;
CREATE TRIGGER trigger_weekly_plan_updated
    BEFORE UPDATE ON weekly_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_time_audit_timestamp();


-- =============================================================================
-- PART 8: ADD TABLE COMMENTS
-- =============================================================================

COMMENT ON TABLE evaluation_golden IS 'Golden dataset for agent evaluation - benchmark examples from Jenny coaching';
COMMENT ON TABLE evaluation_runs IS 'Results from agent evaluation runs against golden dataset';
COMMENT ON TABLE workflow_runs IS 'Execution history for proactive workflows';
COMMENT ON TABLE notifications IS 'Student notifications from proactive workflows';
COMMENT ON TABLE student_time_audits IS 'Jenny 168-hour framework time audits';
COMMENT ON TABLE weekly_plans IS 'P0/P1/P2 prioritized weekly task plans';
COMMENT ON TABLE forbidden_phrases IS 'Phrases Jenny never uses - with approved replacements';
COMMENT ON TABLE speech_patterns IS 'Jenny characteristic speech patterns and usage rules';
COMMENT ON TABLE jenny_voice_scores IS 'Voice validation scores for agent responses';
COMMENT ON TABLE crisis_transformations IS 'Jenny Crisis Alchemy patterns from coaching sessions';
COMMENT ON TABLE program_redirects IS 'Expensive program redirects with free alternatives';


-- =============================================================================
-- VERIFICATION
-- =============================================================================

SELECT '=== MIGRATION VERIFICATION ===' as section;

-- Check all new tables
SELECT table_name, 'EXISTS' as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'evaluation_golden', 'evaluation_runs', 'workflow_runs', 'notifications',
  'student_time_audits', 'weekly_plans', 'forbidden_phrases', 'speech_patterns',
  'jenny_voice_scores', 'crisis_transformations', 'program_redirects'
)
ORDER BY table_name;

-- Check seed data counts
SELECT 'forbidden_phrases' as table_name, COUNT(*) as row_count FROM forbidden_phrases
UNION ALL
SELECT 'speech_patterns', COUNT(*) FROM speech_patterns
ORDER BY table_name;

-- Check views
SELECT viewname as view_name, 'EXISTS' as status
FROM pg_views
WHERE schemaname = 'public'
AND viewname IN ('v_workflow_performance', 'v_recent_workflow_runs', 'v_student_award_portfolio', 'v_awards_with_stats');

SELECT '✅ V2.0 MIGRATIONS COMPLETE' as final_status;
