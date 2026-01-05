-- =============================================================================
-- IvyQuest Data Extraction Triggers
-- Migration 015: Extract structured data from assessments into student_items
-- =============================================================================
--
-- PURPOSE: Extract structured data from assessment profile_data and game_plans
--          into student_items (universal ledger) for agent consumption
--
-- PHILOSOPHY: Use existing student_items table (universal ledger pattern)
--             NOT creating redundant tables like student_extracurriculars
--
-- =============================================================================

-- -----------------------------------------------------------------------------
-- PART 1: Ensure student_items has all needed columns
-- -----------------------------------------------------------------------------

-- Add columns if they don't exist (safe to run multiple times)
DO $$
BEGIN
  -- Recognition level for awards
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'recognition_level') THEN
    ALTER TABLE student_items ADD COLUMN recognition_level TEXT;
  END IF;

  -- Selectivity for awards/programs
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'selectivity') THEN
    ALTER TABLE student_items ADD COLUMN selectivity NUMERIC(5,4);
  END IF;

  -- Prestige tier (1=highest, 5=lowest)
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'prestige_tier') THEN
    ALTER TABLE student_items ADD COLUMN prestige_tier INTEGER CHECK (prestige_tier BETWEEN 1 AND 5);
  END IF;

  -- Hours per week for activities
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'hours_per_week') THEN
    ALTER TABLE student_items ADD COLUMN hours_per_week INTEGER;
  END IF;

  -- Is this a spike activity?
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'is_spike') THEN
    ALTER TABLE student_items ADD COLUMN is_spike BOOLEAN DEFAULT false;
  END IF;

  -- School-specific fields for applications
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'school_id') THEN
    ALTER TABLE student_items ADD COLUMN school_id TEXT;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'admission_probability') THEN
    ALTER TABLE student_items ADD COLUMN admission_probability NUMERIC(5,4);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'decision_type') THEN
    ALTER TABLE student_items ADD COLUMN decision_type TEXT CHECK (decision_type IN ('ED', 'ED2', 'EA', 'REA', 'RD'));
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'student_items' AND column_name = 'target_tier') THEN
    ALTER TABLE student_items ADD COLUMN target_tier TEXT CHECK (target_tier IN ('dream', 'reach', 'target', 'safety'));
  END IF;
END $$;


-- -----------------------------------------------------------------------------
-- PART 2: Award Extraction from Assessment
-- -----------------------------------------------------------------------------

-- Known award mappings (code -> display name, level, tier)
CREATE TABLE IF NOT EXISTS award_mappings (
  award_code TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  recognition_level TEXT NOT NULL,
  prestige_tier INTEGER NOT NULL,
  category TEXT NOT NULL,
  selectivity NUMERIC(5,4)
);

-- Populate award mappings
INSERT INTO award_mappings (award_code, display_name, recognition_level, prestige_tier, category, selectivity) VALUES
  -- Academic Awards (from aptitude.academic_awards)
  ('AP_SCHOLAR', 'AP Scholar', 'national', 3, 'academic', 0.15),
  ('AP_SCHOLAR_DISTINCTION', 'AP Scholar with Distinction', 'national', 2, 'academic', 0.05),
  ('AP_NATIONAL_SCHOLAR', 'AP National Scholar', 'national', 1, 'academic', 0.002),
  ('NATIONAL_MERIT_SEMIFINALIST', 'National Merit Semifinalist', 'national', 2, 'academic', 0.01),
  ('NATIONAL_MERIT_FINALIST', 'National Merit Finalist', 'national', 1, 'academic', 0.005),
  ('NATIONAL_MERIT_SCHOLAR', 'National Merit Scholar', 'national', 1, 'academic', 0.0025),
  ('USABO_QUALIFIER', 'USABO Qualifier', 'national', 2, 'competition', 0.05),
  ('USABO_SEMIFINALIST', 'USABO Semifinalist', 'national', 1, 'competition', 0.005),
  ('USABO_FINALIST', 'USABO Finalist', 'national', 1, 'competition', 0.001),
  ('USAMO_QUALIFIER', 'USAMO Qualifier', 'national', 1, 'competition', 0.002),
  ('USACO_GOLD', 'USACO Gold Division', 'national', 1, 'competition', 0.01),
  ('USACO_PLATINUM', 'USACO Platinum Division', 'national', 1, 'competition', 0.003),
  ('USACO_CAMP', 'USACO Training Camp', 'national', 1, 'competition', 0.0005),
  ('INTEL_STS_SEMIFINALIST', 'Regeneron STS Semifinalist', 'national', 1, 'research', 0.001),
  ('INTEL_STS_FINALIST', 'Regeneron STS Finalist', 'national', 1, 'research', 0.0002),
  ('ISEF_FINALIST', 'ISEF Finalist', 'international', 1, 'research', 0.001),
  ('ISEF_WINNER', 'ISEF Grand Award Winner', 'international', 1, 'research', 0.0003),

  -- EC Awards (from passion.ec_awards)
  ('SCHOOL', 'School Recognition', 'school', 5, 'general', 0.30),
  ('REGIONAL', 'Regional Recognition', 'regional', 4, 'general', 0.15),
  ('STATE', 'State Recognition', 'state', 3, 'general', 0.05),
  ('NATIONAL', 'National Recognition', 'national', 2, 'general', 0.01),
  ('INTERNATIONAL', 'International Recognition', 'international', 1, 'general', 0.005)
ON CONFLICT (award_code) DO NOTHING;


-- Function to extract awards from assessment profile_data
CREATE OR REPLACE FUNCTION extract_awards_from_assessment()
RETURNS TRIGGER AS $$
DECLARE
  award_code TEXT;
  award_info RECORD;
  profile JSONB;
BEGIN
  profile := NEW.profile_data;

  -- Extract from aptitude.academic_awards array
  IF profile->'aptitude'->'academic_awards' IS NOT NULL THEN
    FOR award_code IN SELECT jsonb_array_elements_text(profile->'aptitude'->'academic_awards')
    LOOP
      SELECT * INTO award_info FROM award_mappings WHERE award_mappings.award_code = extract_awards_from_assessment.award_code;

      IF award_info IS NOT NULL THEN
        INSERT INTO student_items (
          user_id, item_type, item_subtype, title, description,
          tier1_state, recognition_level, prestige_tier, selectivity,
          source, confidence, extended_data
        ) VALUES (
          NEW.user_id,
          'award',
          award_info.category,
          award_info.display_name,
          'Academic award extracted from assessment',
          'outcome',  -- Awards are already achieved
          award_info.recognition_level,
          award_info.prestige_tier,
          award_info.selectivity,
          'assessment_extraction',
          'high',
          jsonb_build_object(
            'award_code', award_code,
            'assessment_id', NEW.id,
            'extraction_date', NOW()
          )
        )
        ON CONFLICT DO NOTHING;
      END IF;
    END LOOP;
  END IF;

  -- Extract from passion.ec_awards array (recognition levels)
  IF profile->'passion'->'ec_awards' IS NOT NULL THEN
    FOR award_code IN SELECT jsonb_array_elements_text(profile->'passion'->'ec_awards')
    LOOP
      SELECT * INTO award_info FROM award_mappings WHERE award_mappings.award_code = extract_awards_from_assessment.award_code;

      IF award_info IS NOT NULL THEN
        INSERT INTO student_items (
          user_id, item_type, item_subtype, title, description,
          tier1_state, recognition_level, prestige_tier, selectivity,
          source, confidence, extended_data
        ) VALUES (
          NEW.user_id,
          'award',
          'extracurricular',
          award_info.display_name || ' (EC)',
          'Extracurricular recognition level from assessment',
          'outcome',
          award_info.recognition_level,
          award_info.prestige_tier,
          award_info.selectivity,
          'assessment_extraction',
          'high',
          jsonb_build_object(
            'award_code', award_code,
            'assessment_id', NEW.id,
            'from_ec_awards', true,
            'extraction_date', NOW()
          )
        )
        ON CONFLICT DO NOTHING;
      END IF;
    END LOOP;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for award extraction
DROP TRIGGER IF EXISTS extract_awards_on_assessment ON assessments;
CREATE TRIGGER extract_awards_on_assessment
  AFTER INSERT ON assessments
  FOR EACH ROW
  WHEN (NEW.completed_at IS NOT NULL)
  EXECUTE FUNCTION extract_awards_from_assessment();


-- -----------------------------------------------------------------------------
-- PART 3: Target Schools Extraction
-- -----------------------------------------------------------------------------

-- School metadata (for enrichment)
CREATE TABLE IF NOT EXISTS school_metadata (
  school_id TEXT PRIMARY KEY,
  school_name TEXT NOT NULL,
  acceptance_rate NUMERIC(5,4),
  is_ivy BOOLEAN DEFAULT false,
  is_top_20 BOOLEAN DEFAULT false,
  avg_sat INTEGER,
  avg_gpa NUMERIC(3,2)
);

-- Populate some schools
INSERT INTO school_metadata (school_id, school_name, acceptance_rate, is_ivy, is_top_20, avg_sat, avg_gpa) VALUES
  ('HARVARD', 'Harvard University', 0.032, true, true, 1550, 4.0),
  ('YALE', 'Yale University', 0.045, true, true, 1540, 4.0),
  ('PRINCETON', 'Princeton University', 0.040, true, true, 1545, 4.0),
  ('COLUMBIA', 'Columbia University', 0.037, true, true, 1545, 4.0),
  ('BROWN', 'Brown University', 0.051, true, true, 1530, 4.0),
  ('PENN', 'University of Pennsylvania', 0.055, true, true, 1535, 4.0),
  ('DARTMOUTH', 'Dartmouth College', 0.062, true, true, 1520, 4.0),
  ('CORNELL', 'Cornell University', 0.079, true, true, 1510, 4.0),
  ('MIT', 'Massachusetts Institute of Technology', 0.033, false, true, 1560, 4.0),
  ('STANFORD', 'Stanford University', 0.037, false, true, 1555, 4.0),
  ('CALTECH', 'California Institute of Technology', 0.027, false, true, 1570, 4.0),
  ('DUKE', 'Duke University', 0.060, false, true, 1540, 4.0),
  ('CHICAGO', 'University of Chicago', 0.059, false, true, 1545, 4.0),
  ('NORTHWESTERN', 'Northwestern University', 0.070, false, true, 1525, 3.95),
  ('JHU', 'Johns Hopkins University', 0.071, false, true, 1530, 3.95),
  ('RICE', 'Rice University', 0.089, false, true, 1520, 3.95),
  ('VANDERBILT', 'Vanderbilt University', 0.067, false, true, 1515, 3.95),
  ('NOTRE_DAME', 'University of Notre Dame', 0.129, false, true, 1500, 3.90),
  ('UCLA', 'UCLA', 0.087, false, true, 1470, 3.95),
  ('BERKELEY', 'UC Berkeley', 0.115, false, true, 1460, 3.95)
ON CONFLICT (school_id) DO NOTHING;


-- Function to extract target schools from assessment
CREATE OR REPLACE FUNCTION extract_target_schools_from_assessment()
RETURNS TRIGGER AS $$
DECLARE
  school_id TEXT;
  school_info RECORD;
  profile JSONB;
  student_sat INTEGER;
  student_gpa NUMERIC;
  tier TEXT;
  probability NUMERIC;
BEGIN
  profile := NEW.profile_data;

  -- Get student stats for probability calculation
  student_sat := (profile->'aptitude'->>'sat_total')::INTEGER;
  student_gpa := (profile->'aptitude'->>'gpa_weighted')::NUMERIC;

  IF profile->'target_schools' IS NOT NULL THEN
    FOR school_id IN SELECT jsonb_array_elements_text(profile->'target_schools')
    LOOP
      SELECT * INTO school_info FROM school_metadata WHERE school_metadata.school_id = extract_target_schools_from_assessment.school_id;

      -- Calculate rough probability and tier
      IF school_info IS NOT NULL THEN
        -- Simple probability heuristic (will be refined by scoring engine)
        probability := school_info.acceptance_rate;
        IF student_sat IS NOT NULL AND school_info.avg_sat IS NOT NULL THEN
          probability := probability * (1 + (student_sat - school_info.avg_sat) / 200.0);
        END IF;
        probability := GREATEST(0.01, LEAST(0.50, probability));

        -- Determine tier based on probability
        tier := CASE
          WHEN probability < 0.10 THEN 'dream'
          WHEN probability < 0.25 THEN 'reach'
          WHEN probability < 0.50 THEN 'target'
          ELSE 'safety'
        END;
      ELSE
        -- Unknown school - default values
        probability := 0.20;
        tier := 'reach';
      END IF;

      INSERT INTO student_items (
        user_id, item_type, item_subtype, title, description,
        tier1_state, school_id, target_tier, admission_probability,
        source, confidence, extended_data
      ) VALUES (
        NEW.user_id,
        'application',
        'undergraduate',
        COALESCE(school_info.school_name, school_id),
        'Target school from assessment',
        'planned',  -- Not yet applied
        school_id,
        tier,
        probability,
        'assessment_extraction',
        'high',
        jsonb_build_object(
          'assessment_id', NEW.id,
          'is_ivy', COALESCE(school_info.is_ivy, false),
          'is_top_20', COALESCE(school_info.is_top_20, false),
          'extraction_date', NOW()
        )
      )
      ON CONFLICT DO NOTHING;
    END LOOP;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for school extraction
DROP TRIGGER IF EXISTS extract_schools_on_assessment ON assessments;
CREATE TRIGGER extract_schools_on_assessment
  AFTER INSERT ON assessments
  FOR EACH ROW
  WHEN (NEW.completed_at IS NOT NULL)
  EXECUTE FUNCTION extract_target_schools_from_assessment();


-- -----------------------------------------------------------------------------
-- PART 4: Goal Extraction from Game Plan
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION extract_goals_from_gameplan()
RETURNS TRIGGER AS $$
DECLARE
  quick_win JSONB;
  long_term JSONB;
  plan JSONB;
BEGIN
  plan := NEW.plan_data;

  -- Extract quick wins as goals
  IF plan->'quickWins' IS NOT NULL THEN
    FOR quick_win IN SELECT * FROM jsonb_array_elements(plan->'quickWins')
    LOOP
      INSERT INTO student_items (
        user_id, item_type, item_subtype, title, description,
        tier1_state, metric_type, metric_value,
        source, confidence, extended_data
      ) VALUES (
        NEW.user_id,
        'goal',
        quick_win->>'category',
        quick_win->>'title',
        quick_win->>'description',
        'planned',
        'priority',
        quick_win->>'priority',
        'gameplan_extraction',
        'high',
        jsonb_build_object(
          'game_plan_id', NEW.id,
          'goal_type', 'quick_win',
          'time_commitment', quick_win->>'timeCommitment',
          'impact', quick_win->'impact',
          'tips', quick_win->'tips',
          'extraction_date', NOW()
        )
      )
      ON CONFLICT DO NOTHING;
    END LOOP;
  END IF;

  -- Extract long term goals
  IF plan->'longTermGoals' IS NOT NULL THEN
    FOR long_term IN SELECT * FROM jsonb_array_elements(plan->'longTermGoals')
    LOOP
      INSERT INTO student_items (
        user_id, item_type, item_subtype, title, description,
        tier1_state, metric_type, metric_value, deadline_date,
        source, confidence, extended_data
      ) VALUES (
        NEW.user_id,
        'goal',
        long_term->>'category',
        long_term->>'title',
        long_term->>'description',
        'planned',
        'priority',
        long_term->>'priority',
        CASE
          WHEN long_term->>'deadline' IS NOT NULL
          THEN (long_term->>'deadline')::DATE
          ELSE NULL
        END,
        'gameplan_extraction',
        'high',
        jsonb_build_object(
          'game_plan_id', NEW.id,
          'goal_type', 'long_term',
          'time_commitment', long_term->>'timeCommitment',
          'impact', long_term->'impact',
          'tips', long_term->'tips',
          'extraction_date', NOW()
        )
      )
      ON CONFLICT DO NOTHING;
    END LOOP;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for goal extraction
DROP TRIGGER IF EXISTS extract_goals_on_gameplan ON game_plans;
CREATE TRIGGER extract_goals_on_gameplan
  AFTER INSERT ON game_plans
  FOR EACH ROW
  WHEN (NEW.activated_at IS NOT NULL)
  EXECUTE FUNCTION extract_goals_from_gameplan();


-- -----------------------------------------------------------------------------
-- PART 5: Enhanced Views for Agents
-- -----------------------------------------------------------------------------

-- Complete student profile for agents (single query)
DROP VIEW IF EXISTS v_agent_student_profile CASCADE;
CREATE VIEW v_agent_student_profile AS
SELECT
  p.id as user_id,
  p.email,
  p.first_name,
  p.last_name,
  p.grade,
  p.graduation_year,
  p.target_major,

  -- Assessment data
  a.id as assessment_id,
  a.archetype,
  a.scores,
  a.completeness_score,
  a.profile_data,

  -- Key profile sections (for easy access)
  a.profile_data->'aptitude' as aptitude,
  a.profile_data->'passion' as passion,
  a.profile_data->'community' as community,
  a.profile_data->'operating' as operating,
  a.profile_data->'demographics' as demographics,
  a.profile_data->'assessment_intelligence' as intelligence,
  a.profile_data->'high_school' as high_school,

  -- Computed fields
  (a.profile_data->'operating'->>'availableHoursPerWeek')::INTEGER as available_hours,
  a.profile_data->'assessment_intelligence'->'psychometrics'->>'coachability' as coachability,
  a.profile_data->'assessment_intelligence'->'time_management'->>'burnout_risk' as burnout_risk,

  -- Active game plan
  g.id as game_plan_id,
  g.plan_data,
  g.current_phase,
  g.current_week,
  g.completion_percentage,

  -- Counts
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'award') as award_count,
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'extracurricular') as ec_count,
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'application') as school_count,
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'goal') as goal_count

FROM profiles p
LEFT JOIN LATERAL (
  SELECT * FROM assessments
  WHERE user_id = p.id AND completed_at IS NOT NULL
  ORDER BY completed_at DESC LIMIT 1
) a ON true
LEFT JOIN LATERAL (
  SELECT * FROM game_plans
  WHERE user_id = p.id AND plan_status = 'active'
  ORDER BY created_at DESC LIMIT 1
) g ON true
WHERE p.role = 'student';


-- Awards view with full details
DROP VIEW IF EXISTS v_student_awards_detailed CASCADE;
CREATE VIEW v_student_awards_detailed AS
SELECT
  si.id,
  si.user_id,
  si.title as award_name,
  si.item_subtype as category,
  si.recognition_level,
  si.prestige_tier,
  si.selectivity,
  si.tier1_state as status,
  si.extended_data,
  si.created_at
FROM student_items si
WHERE si.item_type = 'award'
ORDER BY si.prestige_tier ASC, si.created_at DESC;


-- Target schools view with probabilities
DROP VIEW IF EXISTS v_student_target_schools CASCADE;
CREATE VIEW v_student_target_schools AS
SELECT
  si.id,
  si.user_id,
  si.school_id,
  si.title as school_name,
  si.target_tier,
  si.admission_probability,
  si.decision_type,
  si.tier1_state as application_status,
  sm.is_ivy,
  sm.is_top_20,
  sm.acceptance_rate as base_acceptance_rate,
  si.extended_data,
  si.created_at
FROM student_items si
LEFT JOIN school_metadata sm ON sm.school_id = si.school_id
WHERE si.item_type = 'application'
ORDER BY
  CASE si.target_tier
    WHEN 'dream' THEN 1
    WHEN 'reach' THEN 2
    WHEN 'target' THEN 3
    WHEN 'safety' THEN 4
  END,
  si.admission_probability DESC;


-- Goals view with game plan context
DROP VIEW IF EXISTS v_student_goals CASCADE;
CREATE VIEW v_student_goals AS
SELECT
  si.id,
  si.user_id,
  si.title,
  si.description,
  si.item_subtype as category,
  si.tier1_state as status,
  si.metric_value as priority,
  si.deadline_date,
  si.extended_data->>'goal_type' as goal_type,
  si.extended_data->>'time_commitment' as time_commitment,
  si.extended_data->'impact' as impact,
  si.extended_data->'tips' as tips,
  si.created_at
FROM student_items si
WHERE si.item_type = 'goal'
ORDER BY
  CASE si.metric_value
    WHEN 'high' THEN 1
    WHEN 'medium' THEN 2
    WHEN 'low' THEN 3
  END,
  si.created_at DESC;


-- -----------------------------------------------------------------------------
-- PART 6: Backfill Existing Data
-- -----------------------------------------------------------------------------

-- Backfill awards from existing assessments (academic awards)
INSERT INTO student_items (
  user_id, item_type, item_subtype, title, description,
  tier1_state, recognition_level, prestige_tier, selectivity,
  source, confidence, extended_data
)
SELECT
  a.user_id,
  'award',
  am.category,
  am.display_name,
  'Academic award extracted from assessment',
  'outcome',
  am.recognition_level,
  am.prestige_tier,
  am.selectivity,
  'assessment_extraction',
  'high',
  jsonb_build_object(
    'award_code', award_code,
    'assessment_id', a.id,
    'extraction_date', NOW()
  )
FROM assessments a,
     jsonb_array_elements_text(a.profile_data->'aptitude'->'academic_awards') as award_code
JOIN award_mappings am ON am.award_code = award_code
WHERE a.completed_at IS NOT NULL
ON CONFLICT DO NOTHING;

-- Backfill EC awards
INSERT INTO student_items (
  user_id, item_type, item_subtype, title, description,
  tier1_state, recognition_level, prestige_tier, selectivity,
  source, confidence, extended_data
)
SELECT
  a.user_id,
  'award',
  'extracurricular',
  am.display_name || ' (EC)',
  'Extracurricular recognition level from assessment',
  'outcome',
  am.recognition_level,
  am.prestige_tier,
  am.selectivity,
  'assessment_extraction',
  'high',
  jsonb_build_object(
    'award_code', award_code,
    'assessment_id', a.id,
    'from_ec_awards', true,
    'extraction_date', NOW()
  )
FROM assessments a,
     jsonb_array_elements_text(a.profile_data->'passion'->'ec_awards') as award_code
JOIN award_mappings am ON am.award_code = award_code
WHERE a.completed_at IS NOT NULL
ON CONFLICT DO NOTHING;

-- Backfill target schools
INSERT INTO student_items (
  user_id, item_type, item_subtype, title, description,
  tier1_state, school_id, target_tier, admission_probability,
  source, confidence, extended_data
)
SELECT
  a.user_id,
  'application',
  'undergraduate',
  COALESCE(sm.school_name, school_id),
  'Target school from assessment',
  'planned',
  school_id,
  CASE
    WHEN sm.acceptance_rate < 0.10 THEN 'dream'
    WHEN sm.acceptance_rate < 0.25 THEN 'reach'
    WHEN sm.acceptance_rate < 0.50 THEN 'target'
    ELSE 'safety'
  END,
  sm.acceptance_rate,
  'assessment_extraction',
  'high',
  jsonb_build_object(
    'assessment_id', a.id,
    'is_ivy', COALESCE(sm.is_ivy, false),
    'is_top_20', COALESCE(sm.is_top_20, false),
    'extraction_date', NOW()
  )
FROM assessments a,
     jsonb_array_elements_text(a.profile_data->'target_schools') as school_id
LEFT JOIN school_metadata sm ON sm.school_id = school_id
WHERE a.completed_at IS NOT NULL
ON CONFLICT DO NOTHING;

-- Backfill goals from game plans (quick wins)
INSERT INTO student_items (
  user_id, item_type, item_subtype, title, description,
  tier1_state, metric_type, metric_value,
  source, confidence, extended_data
)
SELECT
  g.user_id,
  'goal',
  qw->>'category',
  qw->>'title',
  qw->>'description',
  'planned',
  'priority',
  qw->>'priority',
  'gameplan_extraction',
  'high',
  jsonb_build_object(
    'game_plan_id', g.id,
    'goal_type', 'quick_win',
    'time_commitment', qw->>'timeCommitment',
    'impact', qw->'impact',
    'tips', qw->'tips',
    'extraction_date', NOW()
  )
FROM game_plans g,
     jsonb_array_elements(g.plan_data->'quickWins') as qw
WHERE g.activated_at IS NOT NULL
ON CONFLICT DO NOTHING;

-- Backfill goals from game plans (long term)
INSERT INTO student_items (
  user_id, item_type, item_subtype, title, description,
  tier1_state, metric_type, metric_value,
  source, confidence, extended_data
)
SELECT
  g.user_id,
  'goal',
  lt->>'category',
  lt->>'title',
  lt->>'description',
  'planned',
  'priority',
  lt->>'priority',
  'gameplan_extraction',
  'high',
  jsonb_build_object(
    'game_plan_id', g.id,
    'goal_type', 'long_term',
    'time_commitment', lt->>'timeCommitment',
    'impact', lt->'impact',
    'tips', lt->'tips',
    'extraction_date', NOW()
  )
FROM game_plans g,
     jsonb_array_elements(g.plan_data->'longTermGoals') as lt
WHERE g.activated_at IS NOT NULL
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- PART 7: Verify Results
-- -----------------------------------------------------------------------------

SELECT '=== MIGRATION 015 COMPLETE ===' as status;

-- Check what was extracted
SELECT 'student_items summary' as check_type, item_type, COUNT(*)
FROM student_items
GROUP BY item_type
ORDER BY item_type;

-- List new tables/views created
SELECT 'New tables:' as info;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('award_mappings', 'school_metadata')
ORDER BY table_name;

SELECT 'New views:' as info;
SELECT table_name FROM information_schema.views
WHERE table_schema = 'public'
AND table_name LIKE 'v_%'
ORDER BY table_name;
