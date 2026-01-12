-- =============================================================================
-- IVYQUEST V2.0 TAILORED MIGRATION
-- =============================================================================
-- Based on diagnostic results from your database
-- This script creates ONLY what's missing
-- =============================================================================

-- =============================================================================
-- PART 1: ADD MISSING COLUMNS TO EXISTING TABLES
-- =============================================================================

-- 1.1 Add missing columns to evaluation_golden
ALTER TABLE evaluation_golden
ADD COLUMN IF NOT EXISTS agent_type TEXT DEFAULT 'assessment',
ADD COLUMN IF NOT EXISTS jenny_techniques TEXT[],
ADD COLUMN IF NOT EXISTS source_session TEXT,
ADD COLUMN IF NOT EXISTS quality_tier TEXT DEFAULT 'gold',
ADD COLUMN IF NOT EXISTS student_profile_name TEXT,
ADD COLUMN IF NOT EXISTS jenny_response_example TEXT,
ADD COLUMN IF NOT EXISTS transformation_pattern TEXT,
ADD COLUMN IF NOT EXISTS category TEXT;

-- 1.2 Add missing columns to awards
ALTER TABLE awards
ADD COLUMN IF NOT EXISTS selectivity_percentile INTEGER,
ADD COLUMN IF NOT EXISTS accepts_per_year INTEGER,
ADD COLUMN IF NOT EXISTS applicants_per_year INTEGER,
ADD COLUMN IF NOT EXISTS ideal_candidate_profile JSONB,
ADD COLUMN IF NOT EXISTS jenny_strategy TEXT,
ADD COLUMN IF NOT EXISTS vulnerability_story_boost DECIMAL(3,2) DEFAULT 0.10;

-- 1.3 Add missing columns to opportunities
ALTER TABLE opportunities
ADD COLUMN IF NOT EXISTS tier TEXT DEFAULT 'B',
ADD COLUMN IF NOT EXISTS jenny_note TEXT,
ADD COLUMN IF NOT EXISTS cost_numeric DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS redirect_trigger TEXT;

-- 1.4 Add missing columns to student_awards
ALTER TABLE student_awards
ADD COLUMN IF NOT EXISTS calculated_probability DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS fit_score DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS competition_factor DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS submission_quality_score DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS vulnerability_bonus DECIMAL(5,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS identity_alignment_bonus DECIMAL(5,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS portfolio_tier TEXT;


-- =============================================================================
-- PART 2: CREATE MISSING TABLES
-- =============================================================================

-- 2.1 forbidden_phrases (Jenny Voice)
CREATE TABLE IF NOT EXISTS forbidden_phrases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phrase TEXT NOT NULL UNIQUE,
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    category TEXT NOT NULL,
    jenny_alternative TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.2 speech_patterns (Jenny Voice)
CREATE TABLE IF NOT EXISTS speech_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type TEXT NOT NULL,
    pattern_regex TEXT,
    example TEXT NOT NULL,
    jenny_style TEXT NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.3 jenny_voice_scores
CREATE TABLE IF NOT EXISTS jenny_voice_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID,
    content_type TEXT NOT NULL,
    dimensions JSONB NOT NULL,
    total_score DECIMAL(5,2) NOT NULL,
    passed BOOLEAN NOT NULL,
    forbidden_found TEXT[],
    suggestions TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.4 student_time_audits
CREATE TABLE IF NOT EXISTS student_time_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    total_hours INTEGER DEFAULT 168,
    school_hours DECIMAL(5,2) DEFAULT 0,
    sleep_hours DECIMAL(5,2) DEFAULT 0,
    fixed_commitments DECIMAL(5,2) DEFAULT 0,
    social_media_hours DECIMAL(5,2) DEFAULT 0,
    available_hours DECIMAL(5,2) GENERATED ALWAYS AS (168 - school_hours - sleep_hours - fixed_commitments) STORED,
    passion_hours DECIMAL(5,2) GENERATED ALWAYS AS (168 - school_hours - sleep_hours - fixed_commitments - social_media_hours) STORED,
    efficiency_score DECIMAL(5,2),
    recommendations JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.5 weekly_plans
CREATE TABLE IF NOT EXISTS weekly_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    monday JSONB,
    tuesday JSONB,
    wednesday JSONB,
    thursday JSONB,
    friday JSONB,
    saturday JSONB,
    sunday JSONB,
    total_passion_hours DECIMAL(5,2),
    activities_planned INTEGER,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.6 crisis_transformations
CREATE TABLE IF NOT EXISTS crisis_transformations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crisis_type TEXT NOT NULL,
    original_narrative TEXT NOT NULL,
    transformed_narrative TEXT NOT NULL,
    jenny_technique TEXT NOT NULL,
    impact_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.7 program_redirects
CREATE TABLE IF NOT EXISTS program_redirects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_program TEXT NOT NULL,
    program_cost DECIMAL(10,2) NOT NULL,
    program_category TEXT NOT NULL,
    redirect_reason TEXT NOT NULL,
    free_alternatives JSONB NOT NULL,
    savings_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- =============================================================================
-- PART 3: CREATE INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_forbidden_phrases_severity ON forbidden_phrases(severity);
CREATE INDEX IF NOT EXISTS idx_forbidden_phrases_category ON forbidden_phrases(category);
CREATE INDEX IF NOT EXISTS idx_speech_patterns_type ON speech_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_jenny_voice_scores_content ON jenny_voice_scores(content_id, content_type);
CREATE INDEX IF NOT EXISTS idx_jenny_voice_scores_passed ON jenny_voice_scores(passed);
CREATE INDEX IF NOT EXISTS idx_student_time_audits_profile ON student_time_audits(profile_id);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_profile ON weekly_plans(profile_id);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_week ON weekly_plans(week_start);
CREATE INDEX IF NOT EXISTS idx_crisis_transformations_type ON crisis_transformations(crisis_type);
CREATE INDEX IF NOT EXISTS idx_program_redirects_category ON program_redirects(program_category);
CREATE INDEX IF NOT EXISTS idx_awards_selectivity ON awards(selectivity_percentile);
CREATE INDEX IF NOT EXISTS idx_opportunities_tier ON opportunities(tier);
CREATE INDEX IF NOT EXISTS idx_student_awards_portfolio ON student_awards(portfolio_tier);


-- =============================================================================
-- PART 4: SEED DATA
-- =============================================================================

-- 4.1 Seed forbidden_phrases
INSERT INTO forbidden_phrases (phrase, severity, category, jenny_alternative) VALUES
('I think', 'medium', 'hedging', 'I know / I believe'),
('kind of', 'medium', 'hedging', 'specifically / precisely'),
('sort of', 'medium', 'hedging', 'exactly / definitively'),
('maybe', 'medium', 'hedging', 'likely / probably / I expect'),
('just', 'low', 'diminishing', '[remove entirely]'),
('only', 'low', 'diminishing', '[reframe as positive]'),
('but', 'low', 'negating', 'and / however'),
('sorry', 'high', 'apologizing', '[remove - be direct]'),
('I can''t', 'high', 'limiting', 'I haven''t yet / I''m learning to'),
('I''m not good at', 'critical', 'self-deprecating', 'I''m developing my skills in'),
('I failed', 'high', 'negative-framing', 'I learned / I discovered'),
('It''s not a big deal', 'medium', 'diminishing', 'This matters because')
ON CONFLICT (phrase) DO NOTHING;

-- 4.2 Seed speech_patterns
INSERT INTO speech_patterns (pattern_type, pattern_regex, example, jenny_style, weight) VALUES
('opening', '^(So|Well|Um|Like)', 'So, I started this project...', 'Direct opening with impact statement', 1.0),
('hedging', '(I think|maybe|kind of|sort of)', 'I think I might be good at...', 'Confident assertion with evidence', 1.2),
('passive', '(was done|were made|has been)', 'The project was completed by...', 'Active voice with ownership', 1.0),
('weak-ending', '(I guess|or something|you know)$', '...and that''s why I like it, I guess.', 'Strong conclusion with future vision', 1.3),
('filler', '(um|uh|like|you know)', 'I, like, really want to, um, help...', 'Clean, purposeful language', 0.8)
ON CONFLICT DO NOTHING;

-- 4.3 Seed crisis_transformations examples
INSERT INTO crisis_transformations (crisis_type, original_narrative, transformed_narrative, jenny_technique, impact_score) VALUES
('academic_setback', 'I failed my AP Chemistry exam', 'When I received a challenging score on my AP Chemistry exam, I developed a systematic study approach that improved my understanding of molecular bonds and ultimately raised my grade by two letter grades', 'REFRAME_GROWTH', 0.85),
('family_hardship', 'My parents got divorced and it was hard', 'Navigating my family''s transition taught me emotional resilience and inspired my interest in family counseling, leading me to volunteer at a local support center', 'ACT_TRANSFORM', 0.90),
('health_challenge', 'I was sick and missed a lot of school', 'Managing a chronic health condition while maintaining my academic standing developed my time management skills and sparked my passion for health advocacy', 'CREATE_PURPOSE', 0.88),
('rejection', 'I didn''t get into the summer program I wanted', 'When the competitive program wasn''t the right fit, I created my own research initiative that ultimately produced more meaningful results for my community', 'VALIDATE_REDIRECT', 0.82)
ON CONFLICT DO NOTHING;

-- 4.4 Seed program_redirects examples
INSERT INTO program_redirects (original_program, program_cost, program_category, redirect_reason, free_alternatives, savings_amount) VALUES
('Summer at Brown', 8500.00, 'pre-college', 'Pay-to-play programs don''t carry admissions weight', '["MIT MOSTEC", "Yale YYGS (need-based)", "Local university research position", "Independent project with professor mentor"]', 8500.00),
('iD Tech Camp', 5000.00, 'tech_camp', 'Generic tech camps are not distinctive', '["Girls Who Code SIP", "Code.org workshops", "Local hackathon organization", "Open source contribution"]', 5000.00),
('College Essay Bootcamp', 3500.00, 'test_prep', 'Essay coaching can be self-directed', '["Free Khan Academy resources", "School counselor review", "Peer review groups", "College-specific writing workshops"]', 3500.00),
('Leadership Conference', 2500.00, 'conference', 'Conferences are passive, not distinctive', '["Start local initiative", "Community organizing", "School club leadership", "Youth advisory boards"]', 2500.00)
ON CONFLICT DO NOTHING;


-- =============================================================================
-- PART 5: UPDATE EXISTING DATA (populate new columns)
-- =============================================================================

-- 5.1 Update opportunities - set defaults for new columns
-- First, just set safe defaults for all rows
UPDATE opportunities SET
    cost_numeric = 0,
    tier = 'B'
WHERE cost_numeric IS NULL OR tier IS NULL;

-- 5.1b Try to parse cost values if they're text-based
DO $block$
BEGIN
    -- Try text-based cost parsing (if cost is TEXT type)
    UPDATE opportunities SET
        cost_numeric = CASE
            WHEN cost::TEXT ILIKE '%free%' THEN 0
            WHEN LENGTH(cost::TEXT) = 1 AND cost::TEXT LIKE '%$%' THEN 50
            WHEN LENGTH(cost::TEXT) = 2 AND cost::TEXT LIKE '%$%' THEN 500
            WHEN LENGTH(cost::TEXT) = 3 AND cost::TEXT LIKE '%$%' THEN 2000
            WHEN LENGTH(cost::TEXT) >= 4 AND cost::TEXT LIKE '%$%' THEN 5000
            ELSE cost_numeric
        END,
        tier = CASE
            WHEN cost::TEXT ILIKE '%free%' THEN 'A'
            WHEN LENGTH(cost::TEXT) <= 1 AND cost::TEXT LIKE '%$%' THEN 'A'
            WHEN LENGTH(cost::TEXT) = 2 AND cost::TEXT LIKE '%$%' THEN 'B'
            WHEN LENGTH(cost::TEXT) >= 3 AND cost::TEXT LIKE '%$%' THEN 'C'
            ELSE tier
        END;
EXCEPTION WHEN OTHERS THEN
    -- If cost column is numeric, just use numeric comparisons
    UPDATE opportunities SET
        cost_numeric = COALESCE(cost::DECIMAL, 0),
        tier = CASE
            WHEN cost IS NULL OR cost::DECIMAL = 0 THEN 'A'
            WHEN cost::DECIMAL < 100 THEN 'A'
            WHEN cost::DECIMAL < 1000 THEN 'B'
            ELSE 'C'
        END;
END $block$;

-- 5.2 Update awards with selectivity estimates
UPDATE awards SET
    selectivity_percentile = CASE
        WHEN name ILIKE '%Regeneron%' THEN 99
        WHEN name ILIKE '%Intel%' THEN 98
        WHEN name ILIKE '%Siemens%' THEN 97
        WHEN name ILIKE '%Presidential%' THEN 95
        WHEN name ILIKE '%National Merit%' THEN 90
        WHEN name ILIKE '%state%' THEN 70
        WHEN name ILIKE '%regional%' THEN 60
        WHEN name ILIKE '%local%' THEN 40
        ELSE 50
    END,
    vulnerability_story_boost = 0.10
WHERE selectivity_percentile IS NULL;


-- =============================================================================
-- PART 6: CREATE/UPDATE VIEWS
-- =============================================================================

-- 6.1 Student award portfolio view
CREATE OR REPLACE VIEW v_student_award_portfolio AS
SELECT
    sa.profile_id,
    p.first_name,
    a.name as award_name,
    sa.calculated_probability,
    sa.portfolio_tier,
    sa.fit_score,
    sa.vulnerability_bonus,
    sa.status
FROM student_awards sa
JOIN profiles p ON sa.profile_id = p.id
JOIN awards a ON sa.award_id = a.id
ORDER BY sa.profile_id, sa.portfolio_tier;

-- 6.2 Awards with stats view
CREATE OR REPLACE VIEW v_awards_with_stats AS
SELECT
    a.id,
    a.name,
    a.organization,
    a.category,
    a.description,
    a.deadline,
    a.selectivity_percentile,
    a.vulnerability_story_boost,
    a.jenny_strategy,
    COALESCE(a.selectivity_percentile, 50) as effective_selectivity,
    CASE
        WHEN a.selectivity_percentile >= 95 THEN 'Elite'
        WHEN a.selectivity_percentile >= 80 THEN 'Highly Selective'
        WHEN a.selectivity_percentile >= 60 THEN 'Selective'
        WHEN a.selectivity_percentile >= 40 THEN 'Competitive'
        ELSE 'Accessible'
    END as selectivity_tier,
    COUNT(DISTINCT sa.profile_id) as applicant_count,
    COUNT(DISTINCT CASE WHEN sa.status = 'won' THEN sa.profile_id END) as winner_count
FROM awards a
LEFT JOIN student_awards sa ON a.id = sa.award_id
GROUP BY a.id, a.name, a.organization, a.category, a.description, a.deadline,
         a.selectivity_percentile, a.vulnerability_story_boost, a.jenny_strategy;

-- 6.3 Time audit summary view
CREATE OR REPLACE VIEW v_time_audit_summary AS
SELECT
    sta.profile_id,
    p.first_name,
    sta.available_hours,
    sta.passion_hours,
    sta.social_media_hours,
    sta.efficiency_score,
    CASE
        WHEN sta.passion_hours >= 30 THEN 'Excellent'
        WHEN sta.passion_hours >= 20 THEN 'Good'
        WHEN sta.passion_hours >= 10 THEN 'Needs Improvement'
        ELSE 'Critical'
    END as time_health
FROM student_time_audits sta
JOIN profiles p ON sta.profile_id = p.id;


-- =============================================================================
-- PART 7: ENABLE RLS (Row Level Security)
-- =============================================================================

ALTER TABLE forbidden_phrases ENABLE ROW LEVEL SECURITY;
ALTER TABLE speech_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE jenny_voice_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_time_audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE crisis_transformations ENABLE ROW LEVEL SECURITY;
ALTER TABLE program_redirects ENABLE ROW LEVEL SECURITY;

-- Public read policies for reference tables
CREATE POLICY "Public read for forbidden_phrases" ON forbidden_phrases FOR SELECT USING (true);
CREATE POLICY "Public read for speech_patterns" ON speech_patterns FOR SELECT USING (true);
CREATE POLICY "Public read for crisis_transformations" ON crisis_transformations FOR SELECT USING (true);
CREATE POLICY "Public read for program_redirects" ON program_redirects FOR SELECT USING (true);

-- Simplified policies for user data (allow authenticated users)
CREATE POLICY "Authenticated read for time audits" ON student_time_audits FOR SELECT
    USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated insert for time audits" ON student_time_audits FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Authenticated read for weekly plans" ON weekly_plans FOR SELECT
    USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated manage weekly plans" ON weekly_plans FOR ALL
    USING (auth.role() = 'authenticated');

CREATE POLICY "Public read for jenny voice scores" ON jenny_voice_scores FOR SELECT USING (true);


-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

SELECT '=== MIGRATION COMPLETE ===' as status;

-- Verify new tables created
SELECT 'New tables created:' as info;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('forbidden_phrases', 'speech_patterns', 'jenny_voice_scores',
                   'student_time_audits', 'weekly_plans', 'crisis_transformations', 'program_redirects')
ORDER BY table_name;

-- Verify new columns on evaluation_golden
SELECT 'evaluation_golden columns:' as info;
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'evaluation_golden'
ORDER BY ordinal_position;

-- Verify seed data
SELECT 'Seed data counts:' as info;
SELECT 'forbidden_phrases' as table_name, COUNT(*) as count FROM forbidden_phrases
UNION ALL SELECT 'speech_patterns', COUNT(*) FROM speech_patterns
UNION ALL SELECT 'crisis_transformations', COUNT(*) FROM crisis_transformations
UNION ALL SELECT 'program_redirects', COUNT(*) FROM program_redirects;

SELECT '=== ALL DONE ===' as status;
