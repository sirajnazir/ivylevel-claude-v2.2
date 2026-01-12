-- Migration 024: Jenny Voice
-- Purpose: Store Jenny's speech patterns and voice validation data

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
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL,
    response_id VARCHAR(100),

    -- 6-dimension scoring (out of points noted)
    forbidden_absence_score DECIMAL(3,1),    -- 25 pts
    warmth_first_score DECIMAL(3,1),         -- 20 pts
    agency_preservation_score DECIMAL(3,1),  -- 20 pts
    speech_patterns_score DECIMAL(3,1),      -- 15 pts
    exclamation_calibration_score DECIMAL(3,1), -- 10 pts
    checkin_question_score DECIMAL(3,1),     -- 10 pts

    -- Total and pass/fail
    total_score DECIMAL(4,2),
    passing BOOLEAN,

    -- Issues found
    forbidden_found TEXT[],
    issues TEXT[],

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crisis transformations table (Jenny's crisis alchemy patterns)
CREATE TABLE IF NOT EXISTS crisis_transformations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crisis_type VARCHAR(100) NOT NULL,
    situation_description TEXT NOT NULL,

    -- 4-step protocol scripts
    validation_script TEXT NOT NULL,
    micro_action_script TEXT NOT NULL,
    reframe_script TEXT NOT NULL,
    pivot_activity TEXT NOT NULL,

    -- Transformation pattern
    transformation_from VARCHAR(200),
    transformation_to VARCHAR(200),

    -- Source
    source_student VARCHAR(100),
    source_session VARCHAR(50),
    quality_tier VARCHAR(20) DEFAULT 'gold',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Program redirects table (expensive program alternatives)
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

-- Comments
COMMENT ON TABLE forbidden_phrases IS 'Phrases Jenny never uses - with approved replacements';
COMMENT ON TABLE speech_patterns IS 'Jenny characteristic speech patterns and usage rules';
COMMENT ON TABLE jenny_voice_scores IS 'Voice validation scores for agent responses';
COMMENT ON TABLE crisis_transformations IS 'Jenny Crisis Alchemy patterns from coaching sessions';
COMMENT ON TABLE program_redirects IS 'Expensive program redirects with free alternatives';
