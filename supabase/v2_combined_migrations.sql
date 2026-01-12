-- =============================================================================
-- IVYQUEST v2.0 COMBINED MIGRATIONS
-- =============================================================================
-- Run this ENTIRE script in Supabase SQL Editor (Dashboard → SQL Editor)
-- This combines migrations 020-025 in the correct order
-- =============================================================================

-- Check if trigger function exists, create if not
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- MIGRATION 020: Evaluation Framework & Proactive Workflows
-- =============================================================================

-- 1. EVALUATION GOLDEN DATASET
CREATE TABLE IF NOT EXISTS public.evaluation_golden (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id TEXT NOT NULL UNIQUE,
  input_profile JSONB NOT NULL,
  expected_outputs JSONB NOT NULL,
  jenny_annotations JSONB DEFAULT '{}',
  difficulty_tier TEXT CHECK (difficulty_tier IN ('easy', 'medium', 'hard')),
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_golden_difficulty ON evaluation_golden(difficulty_tier);
CREATE INDEX IF NOT EXISTS idx_evaluation_golden_tags ON evaluation_golden USING GIN(tags);

DROP TRIGGER IF EXISTS evaluation_golden_updated_at ON evaluation_golden;
CREATE TRIGGER evaluation_golden_updated_at
  BEFORE UPDATE ON evaluation_golden
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

COMMENT ON TABLE evaluation_golden IS 'Golden dataset for agent evaluation - benchmark examples from Jenny Duan coaching';

-- 2. EVALUATION RUNS
CREATE TABLE IF NOT EXISTS public.evaluation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id TEXT NOT NULL,
  agent_version TEXT NOT NULL,
  golden_id UUID REFERENCES evaluation_golden(id) ON DELETE CASCADE,
  actual_outputs JSONB NOT NULL,
  objective_scores JSONB DEFAULT '{}',
  subjective_scores JSONB DEFAULT '{}',
  overall_score DECIMAL(5,2),
  passed BOOLEAN DEFAULT false,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_runs_run_id ON evaluation_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_version ON evaluation_runs(agent_version);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_golden ON evaluation_runs(golden_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_passed ON evaluation_runs(passed);

COMMENT ON TABLE evaluation_runs IS 'Results from agent evaluation runs against golden dataset';

-- 3. NOTIFICATIONS
CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  data JSONB DEFAULT '{}',
  priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
  channel TEXT DEFAULT 'in_app' CHECK (channel IN ('in_app', 'email', 'sms', 'push')),
  read BOOLEAN DEFAULT false,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_profile ON notifications(profile_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(profile_id, read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC);

COMMENT ON TABLE notifications IS 'Student notifications from proactive workflows';


-- =============================================================================
-- MIGRATION 021: Workflow Runs
-- =============================================================================

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

CREATE INDEX IF NOT EXISTS idx_workflow_runs_name ON workflow_runs(workflow_name);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_run_at ON workflow_runs(run_at DESC);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_success ON workflow_runs(success);

COMMENT ON TABLE workflow_runs IS 'Execution history for proactive workflows';

-- Workflow Performance View
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
GROUP BY workflow_name
ORDER BY workflow_name;

-- Recent Workflow Runs View
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


-- =============================================================================
-- MIGRATION 022: Golden Dataset Expansion
-- =============================================================================

ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS agent_type VARCHAR(50);
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS jenny_techniques TEXT[];
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS source_session VARCHAR(50);
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS quality_tier VARCHAR(20) DEFAULT 'standard';
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS student_profile_name VARCHAR(100);
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS jenny_response_example TEXT;
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS transformation_pattern VARCHAR(200);
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS category VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_golden_agent_type ON evaluation_golden(agent_type);
CREATE INDEX IF NOT EXISTS idx_golden_category ON evaluation_golden(category);
CREATE INDEX IF NOT EXISTS idx_golden_quality_tier ON evaluation_golden(quality_tier);

ALTER TABLE evaluation_golden DROP CONSTRAINT IF EXISTS check_quality_tier;
ALTER TABLE evaluation_golden ADD CONSTRAINT check_quality_tier
    CHECK (quality_tier IN ('gold', 'silver', 'bronze', 'standard'));


-- =============================================================================
-- MIGRATION 023: Time Management (168-Hour Framework)
-- =============================================================================

-- Student time audits table
CREATE TABLE IF NOT EXISTS student_time_audits (
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

-- Weekly plans table
CREATE TABLE IF NOT EXISTS weekly_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_time_audits_profile ON student_time_audits(profile_id);
CREATE INDEX IF NOT EXISTS idx_time_audits_date ON student_time_audits(audit_date DESC);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_profile ON weekly_plans(profile_id);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_week ON weekly_plans(week_start);

-- Trigger function
CREATE OR REPLACE FUNCTION update_time_audit_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

COMMENT ON TABLE student_time_audits IS 'Jenny 168-hour framework time audits';
COMMENT ON TABLE weekly_plans IS 'P0/P1/P2 prioritized weekly task plans';


-- =============================================================================
-- MIGRATION 024: Jenny Voice & Crisis Alchemy
-- =============================================================================

-- Forbidden phrases table
CREATE TABLE IF NOT EXISTS forbidden_phrases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phrase TEXT NOT NULL UNIQUE,
    replacement TEXT,
    reason TEXT,
    severity VARCHAR(20) DEFAULT 'high',
    category VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Speech patterns table
CREATE TABLE IF NOT EXISTS speech_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    examples TEXT[] NOT NULL,
    usage_context TEXT,
    frequency_target VARCHAR(50),
    required_position VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Voice validation scores table
CREATE TABLE IF NOT EXISTS jenny_voice_scores (
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

-- Crisis transformations table
CREATE TABLE IF NOT EXISTS crisis_transformations (
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

-- Program redirects table
CREATE TABLE IF NOT EXISTS program_redirects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expensive_program VARCHAR(200) NOT NULL,
    cost_threshold INTEGER DEFAULT 5000,
    program_category VARCHAR(100),
    redirect_reason TEXT,
    free_alternatives TEXT[] NOT NULL,
    self_directed_suggestion TEXT,
    jenny_quote TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_forbidden_severity ON forbidden_phrases(severity);
CREATE INDEX IF NOT EXISTS idx_forbidden_category ON forbidden_phrases(category);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON speech_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_voice_scores_profile ON jenny_voice_scores(profile_id);
CREATE INDEX IF NOT EXISTS idx_voice_scores_agent ON jenny_voice_scores(agent_type);
CREATE INDEX IF NOT EXISTS idx_crisis_type ON crisis_transformations(crisis_type);
CREATE INDEX IF NOT EXISTS idx_crisis_quality ON crisis_transformations(quality_tier);

-- Seed forbidden phrases
INSERT INTO forbidden_phrases (phrase, replacement, reason, severity, category) VALUES
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
ON CONFLICT (phrase) DO NOTHING;

-- Seed speech patterns
INSERT INTO speech_patterns (pattern_type, pattern_name, examples, usage_context, frequency_target, required_position) VALUES
    ('warmth', 'positive_acknowledgment', ARRAY['No worries!', 'Great!', 'That''s so cool!', 'I love it!', 'Perfect!', 'Awesome!'], 'Start of responses, after student shares', 'Every response', 'opening'),
    ('agency', 'check_in_questions', ARRAY['What do you think?', 'Does that make sense?', 'How does that feel?', 'What sounds best to you?'], 'End of suggestions', 'Every response', 'closing'),
    ('softening', 'suggestion_softeners', ARRAY['I feel like...', 'Maybe we can...', 'What if you just...', 'Have you considered...'], 'Before making recommendations', '2-3 per response', 'before_suggestions'),
    ('enthusiasm', 'genuine_excitement', ARRAY['Wow!', 'Amazing!', 'This is brilliant!', 'I''m so excited about this!'], 'When student achieves or shares wins', 'When appropriate', 'contextual'),
    ('flexibility', 'adjustment_phrases', ARRAY['We''ll try this for 2 weeks and adjust', 'Let''s see how this feels', 'We can always pivot'], 'When proposing plans', 'Once per plan', 'after_proposals')
ON CONFLICT DO NOTHING;

COMMENT ON TABLE forbidden_phrases IS 'Phrases Jenny never uses - with approved replacements';
COMMENT ON TABLE speech_patterns IS 'Jenny characteristic speech patterns and usage rules';
COMMENT ON TABLE jenny_voice_scores IS 'Voice validation scores for agent responses';
COMMENT ON TABLE crisis_transformations IS 'Jenny Crisis Alchemy patterns from coaching sessions';
COMMENT ON TABLE program_redirects IS 'Expensive program redirects with free alternatives';


-- =============================================================================
-- MIGRATION 025: Awards Probability (2-2-1 Portfolio)
-- =============================================================================

-- Add probability fields to student_awards (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'student_awards') THEN
        ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS calculated_probability DECIMAL(5,2);
        ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS fit_score DECIMAL(5,2);
        ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS competition_factor DECIMAL(5,2);
        ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS submission_quality_score DECIMAL(5,2);
        ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS vulnerability_bonus BOOLEAN DEFAULT FALSE;
        ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS identity_alignment_bonus BOOLEAN DEFAULT FALSE;
        ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS portfolio_tier VARCHAR(20);

        ALTER TABLE student_awards DROP CONSTRAINT IF EXISTS check_portfolio_tier;
        ALTER TABLE student_awards ADD CONSTRAINT check_portfolio_tier
            CHECK (portfolio_tier IN ('likely', 'target', 'stretch', NULL));
    END IF;
END $$;

-- Add selectivity and strategy fields to awards (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'awards') THEN
        ALTER TABLE awards ADD COLUMN IF NOT EXISTS selectivity_percentile INTEGER;
        ALTER TABLE awards ADD COLUMN IF NOT EXISTS accepts_per_year INTEGER;
        ALTER TABLE awards ADD COLUMN IF NOT EXISTS applicants_per_year INTEGER;
        ALTER TABLE awards ADD COLUMN IF NOT EXISTS ideal_candidate_profile JSONB;
        ALTER TABLE awards ADD COLUMN IF NOT EXISTS jenny_strategy TEXT;
        ALTER TABLE awards ADD COLUMN IF NOT EXISTS vulnerability_story_boost BOOLEAN DEFAULT FALSE;

        -- Update selectivity data for key awards
        UPDATE awards SET selectivity_percentile = 30, vulnerability_story_boost = true
            WHERE name ILIKE '%ncwit%';
        UPDATE awards SET selectivity_percentile = 50
            WHERE name ILIKE '%congressional%';
        UPDATE awards SET selectivity_percentile = 5, vulnerability_story_boost = true
            WHERE name ILIKE '%coolidge%';
        UPDATE awards SET selectivity_percentile = 2, vulnerability_story_boost = true
            WHERE name ILIKE '%cameron%';
        UPDATE awards SET selectivity_percentile = 20
            WHERE name ILIKE '%scholastic%';
        UPDATE awards SET selectivity_percentile = 15
            WHERE name ILIKE '%regeneron%' OR name ILIKE '%science talent%';
        UPDATE awards SET selectivity_percentile = 25
            WHERE name ILIKE '%usaco%';
        UPDATE awards SET selectivity_percentile = 40
            WHERE name ILIKE '%amc%' OR name ILIKE '%math olympiad%';
    END IF;
END $$;

-- Add tier and redirect fields to opportunities (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'opportunities') THEN
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS tier INTEGER DEFAULT 3;
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS jenny_note TEXT;
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS cost_numeric INTEGER DEFAULT 0;
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS redirect_trigger BOOLEAN DEFAULT FALSE;

        -- Update opportunities with tiers and redirect triggers
        -- Only use cost_numeric (which is INTEGER) for comparisons
        UPDATE opportunities SET tier = 4, redirect_trigger = true
            WHERE cost_numeric >= 5000;
        UPDATE opportunities SET tier = 1
            WHERE (cost_numeric = 0 OR cost_numeric IS NULL) AND prestige_score >= 80;
        UPDATE opportunities SET tier = 2
            WHERE (cost_numeric = 0 OR cost_numeric IS NULL) AND prestige_score >= 60 AND prestige_score < 80;
        UPDATE opportunities SET tier = 3
            WHERE tier IS NULL;
    END IF;
EXCEPTION
    WHEN undefined_column THEN
        -- prestige_score might not exist, just set defaults
        UPDATE opportunities SET tier = 3 WHERE tier IS NULL;
END $$;

-- Create portfolio summary view (only if student_awards exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'student_awards') THEN
        CREATE OR REPLACE VIEW v_student_award_portfolio AS
        SELECT
            sa.profile_id,
            sa.portfolio_tier,
            COUNT(*) as award_count,
            AVG(sa.calculated_probability) as avg_probability,
            SUM(CASE WHEN sa.vulnerability_bonus THEN 1 ELSE 0 END) as vulnerability_bonus_count,
            SUM(CASE WHEN sa.identity_alignment_bonus THEN 1 ELSE 0 END) as identity_bonus_count
        FROM student_awards sa
        WHERE sa.portfolio_tier IS NOT NULL
        GROUP BY sa.profile_id, sa.portfolio_tier;
    END IF;
END $$;

-- Create awards with probabilities view (only if awards exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'awards') THEN
        CREATE OR REPLACE VIEW v_awards_with_stats AS
        SELECT
            a.*,
            COALESCE(a.selectivity_percentile, 50) as effective_selectivity,
            CASE
                WHEN a.selectivity_percentile <= 10 THEN 'highly_selective'
                WHEN a.selectivity_percentile <= 30 THEN 'selective'
                WHEN a.selectivity_percentile <= 60 THEN 'competitive'
                ELSE 'accessible'
            END as selectivity_tier
        FROM awards a;
    END IF;
END $$;


-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Check all v2.0 tables exist
SELECT table_name, 'EXISTS' as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'evaluation_golden',
  'evaluation_runs',
  'workflow_runs',
  'notifications',
  'student_time_audits',
  'weekly_plans',
  'forbidden_phrases',
  'speech_patterns',
  'jenny_voice_scores',
  'crisis_transformations',
  'program_redirects'
)
ORDER BY table_name;

-- Check seed data
SELECT 'forbidden_phrases' as table_name, COUNT(*) as count FROM forbidden_phrases
UNION ALL
SELECT 'speech_patterns', COUNT(*) FROM speech_patterns;

SELECT '✅ v2.0 MIGRATIONS COMPLETE' as status;
