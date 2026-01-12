-- =============================================================================
-- IVYQUEST V2.0 GOLDEN DATA SEED SCRIPT
-- =============================================================================
-- Run this in Supabase SQL Editor to seed Jenny's coaching intelligence
-- This adds MORE data to existing tables (won't delete existing data)
-- =============================================================================

-- =============================================================================
-- PART 1: VERIFY CURRENT COUNTS
-- =============================================================================

SELECT '=== CURRENT DATA COUNTS ===' as section;

SELECT 'forbidden_phrases' as table_name, COUNT(*) as count FROM forbidden_phrases
UNION ALL SELECT 'speech_patterns', COUNT(*) FROM speech_patterns
UNION ALL SELECT 'crisis_transformations', COUNT(*) FROM crisis_transformations
UNION ALL SELECT 'program_redirects', COUNT(*) FROM program_redirects
UNION ALL SELECT 'evaluation_golden', COUNT(*) FROM evaluation_golden
UNION ALL SELECT 'awards', COUNT(*) FROM awards
UNION ALL SELECT 'opportunities', COUNT(*) FROM opportunities
ORDER BY table_name;


-- =============================================================================
-- PART 2: SEED ADDITIONAL FORBIDDEN PHRASES
-- =============================================================================

SELECT '=== SEEDING FORBIDDEN PHRASES ===' as section;

-- Add more forbidden phrases if not already present
INSERT INTO forbidden_phrases (phrase, severity, category, jenny_alternative)
SELECT * FROM (VALUES
    ('to be honest', 'medium', 'filler', '[remove - implies previous dishonesty]'),
    ('actually', 'low', 'filler', '[remove - implies correction]'),
    ('basically', 'low', 'filler', '[remove - dumbs down conversation]'),
    ('obviously', 'medium', 'filler', '[remove - makes student feel stupid]'),
    ('you must', 'high', 'directive', 'you might consider'),
    ('you have to', 'high', 'directive', 'it could help to'),
    ('don''t worry', 'medium', 'dismissive', 'I understand'),
    ('it''s fine', 'medium', 'dismissive', 'let''s work through this'),
    ('you always', 'high', 'generalizing', '[be specific about the instance]'),
    ('you never', 'high', 'generalizing', '[be specific about the instance]'),
    ('that''s not important', 'high', 'dismissive', 'let''s prioritize together'),
    ('everyone does this', 'medium', 'dismissive', 'this is your unique journey')
) AS new_phrases(phrase, severity, category, jenny_alternative)
WHERE NOT EXISTS (
    SELECT 1 FROM forbidden_phrases fp WHERE fp.phrase = new_phrases.phrase
);


-- =============================================================================
-- PART 3: SEED ADDITIONAL SPEECH PATTERNS
-- =============================================================================

SELECT '=== SEEDING SPEECH PATTERNS ===' as section;

INSERT INTO speech_patterns (pattern_type, pattern_regex, example, jenny_style, weight)
SELECT * FROM (VALUES
    ('encouragement', NULL, 'You''ve totally got this!', 'Builds confidence with enthusiasm', 1.2),
    ('acknowledgment', NULL, 'I love that idea!', 'Validates student input warmly', 1.1),
    ('collaboration', NULL, 'Let''s figure this out together', 'Creates partnership feeling', 1.0),
    ('reframe', NULL, 'Here''s the opportunity:', 'Transforms setbacks to growth', 1.3),
    ('philosophy', NULL, 'Specificity beats generality', 'Jenny''s core wisdom', 1.5),
    ('validation', NULL, 'That makes total sense', 'Validates student feelings', 1.0),
    ('pivot', NULL, 'What if we flip this?', 'Redirects negative to positive', 1.2),
    ('ownership', NULL, 'You built that - own it!', 'Builds student agency', 1.1)
) AS new_patterns(pattern_type, pattern_regex, example, jenny_style, weight)
WHERE NOT EXISTS (
    SELECT 1 FROM speech_patterns sp WHERE sp.example = new_patterns.example
);


-- =============================================================================
-- PART 4: SEED ADDITIONAL CRISIS TRANSFORMATIONS
-- =============================================================================

SELECT '=== SEEDING CRISIS TRANSFORMATIONS ===' as section;

INSERT INTO crisis_transformations (crisis_type, original_narrative, transformed_narrative, jenny_technique, impact_score)
SELECT * FROM (VALUES
    ('comparison',
     'My friend got into TASP and I didn''t',
     'While my friend pursued existing programs, I channeled that energy into creating my own research initiative that reached 200 students in my community',
     'REDIRECT_ENERGY',
     0.85),
    ('identity_attack',
     'Someone called me a diversity admit',
     'When someone questioned my belonging, I transformed that doubt into fuel for founding a mentorship program that has helped 50+ underrepresented students navigate the college process',
     'TRANSFORM_ATTACK',
     0.92),
    ('overwhelm',
     'I have too many things to do and can''t focus',
     'When I felt overwhelmed by competing priorities, I developed a systematic approach to time management that I now teach to other students',
     'SYSTEMIZE_CHAOS',
     0.78),
    ('imposter_syndrome',
     'I don''t deserve to be here',
     'Initial doubts about my place in competitive spaces drove me to mentor others who felt the same way, creating a support network of 30+ students',
     'CHANNEL_DOUBT',
     0.88)
) AS new_crises(crisis_type, original_narrative, transformed_narrative, jenny_technique, impact_score)
WHERE NOT EXISTS (
    SELECT 1 FROM crisis_transformations ct WHERE ct.crisis_type = new_crises.crisis_type
);


-- =============================================================================
-- PART 5: SEED ADDITIONAL PROGRAM REDIRECTS
-- =============================================================================

SELECT '=== SEEDING PROGRAM REDIRECTS ===' as section;

INSERT INTO program_redirects (original_program, program_cost, program_category, redirect_reason, free_alternatives, savings_amount)
SELECT * FROM (VALUES
    ('Brown Pre-College Program',
     8500.00,
     'pre-college',
     'Expensive pre-college programs don''t give admissions advantage',
     '["Brown STEM for Rising Stars (free)", "Local university summer research", "Online Brown courses", "Start independent research project"]'::jsonb,
     8500.00),
    ('Yale Young Global Scholars',
     6500.00,
     'global_affairs',
     'Pay-to-play programs aren''t distinctive on applications',
     '["Yale YYGS need-based aid", "Model UN leadership", "Local policy internship", "Start international affairs club"]'::jsonb,
     6500.00),
    ('Wharton Business Camp',
     7000.00,
     'business',
     'Business skills are best learned by actually running a business',
     '["Diamond Challenge (free)", "DECA competitions", "Start actual business", "Young Entrepreneurs Academy"]'::jsonb,
     7000.00),
    ('MIT Launch',
     8000.00,
     'entrepreneurship',
     'Entrepreneurship is learned by doing, not by paying for programs',
     '["MIT MOSTEC (free)", "Lemelson-MIT InvenTeam", "Start your own venture", "Local startup internship"]'::jsonb,
     8000.00)
) AS new_redirects(original_program, program_cost, program_category, redirect_reason, free_alternatives, savings_amount)
WHERE NOT EXISTS (
    SELECT 1 FROM program_redirects pr WHERE pr.original_program = new_redirects.original_program
);


-- =============================================================================
-- PART 6: SEED EVALUATION GOLDEN EXAMPLES
-- =============================================================================

SELECT '=== SEEDING EVALUATION GOLDEN EXAMPLES ===' as section;

-- Note: evaluation_golden has a unique constraint on profile_id
-- We'll update existing records with additional metadata instead of inserting new ones
-- Or skip if golden examples already exist

-- Update existing golden records with agent_type and quality_tier if missing
UPDATE evaluation_golden SET
    agent_type = COALESCE(agent_type, 'narrative'),
    quality_tier = COALESCE(quality_tier, 'gold'),
    category = COALESCE(category, 'coaching_example')
WHERE agent_type IS NULL OR quality_tier IS NULL;

SELECT 'Updated existing evaluation_golden records with metadata' as status;


-- =============================================================================
-- PART 7: UPDATE AWARDS WITH JENNY STRATEGY (if missing)
-- =============================================================================

SELECT '=== UPDATING AWARDS WITH JENNY STRATEGY ===' as section;

UPDATE awards SET
    jenny_strategy = CASE
        WHEN name ILIKE '%NCWIT%' THEN 'Lead with identity transformation story. Show how CS changed your relationship with your identity.'
        WHEN name ILIKE '%Regeneron%' THEN 'Emphasize genuine intellectual curiosity and research journey, not just results.'
        WHEN name ILIKE '%Coca-Cola%' THEN 'Focus on sustained community impact and leadership through service.'
        WHEN name ILIKE '%QuestBridge%' THEN 'Authentic financial hardship narrative transformed into drive and resilience.'
        WHEN name ILIKE '%National Merit%' THEN 'Consistent academic excellence plus genuine intellectual interests.'
        ELSE 'Connect your authentic story to the award''s core values.'
    END
WHERE jenny_strategy IS NULL;


-- =============================================================================
-- PART 8: VERIFY FINAL COUNTS
-- =============================================================================

SELECT '=== FINAL DATA COUNTS ===' as section;

SELECT 'forbidden_phrases' as table_name, COUNT(*) as count FROM forbidden_phrases
UNION ALL SELECT 'speech_patterns', COUNT(*) FROM speech_patterns
UNION ALL SELECT 'crisis_transformations', COUNT(*) FROM crisis_transformations
UNION ALL SELECT 'program_redirects', COUNT(*) FROM program_redirects
UNION ALL SELECT 'evaluation_golden', COUNT(*) FROM evaluation_golden
ORDER BY table_name;


SELECT '=== SEED COMPLETE ===' as section;
SELECT 'Run verify_golden_dataset.py to confirm all checks pass' as next_step;
