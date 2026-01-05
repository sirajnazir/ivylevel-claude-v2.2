-- =============================================================================
-- IvyQuest Clean Schema Migration
-- Migration 014: Fix timeline_events, drop legacy tables, setup triggers
-- =============================================================================

-- -----------------------------------------------------------------------------
-- STEP 1: Add missing columns to timeline_events
-- -----------------------------------------------------------------------------

ALTER TABLE timeline_events
ADD COLUMN IF NOT EXISTS related_assessment_id UUID REFERENCES assessments(id);

ALTER TABLE timeline_events
ADD COLUMN IF NOT EXISTS related_game_plan_id UUID REFERENCES game_plans(id);

-- -----------------------------------------------------------------------------
-- STEP 2: Drop all legacy tables (no data we need)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS assessment_state CASCADE;
DROP TABLE IF EXISTS checkpoint_blobs CASCADE;
DROP TABLE IF EXISTS checkpoint_writes CASCADE;
DROP TABLE IF EXISTS checkpoints CASCADE;
DROP TABLE IF EXISTS chetty_factors CASCADE;
DROP TABLE IF EXISTS eq_profiles CASCADE;
DROP TABLE IF EXISTS facts_backup_v52 CASCADE;
DROP TABLE IF EXISTS ivy_ready_scores CASCADE;
DROP TABLE IF EXISTS kb_items CASCADE;
DROP TABLE IF EXISTS psycho_context CASCADE;
DROP TABLE IF EXISTS soul_fragments CASCADE;
DROP TABLE IF EXISTS student_profile CASCADE;
DROP TABLE IF EXISTS student_profile_v61 CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS target_profiles CASCADE;

-- -----------------------------------------------------------------------------
-- STEP 3: Drop and recreate views
-- -----------------------------------------------------------------------------

DROP VIEW IF EXISTS public.v_user_dashboard CASCADE;
DROP VIEW IF EXISTS public.v_active_game_plan CASCADE;
DROP VIEW IF EXISTS public.v_current_assessment CASCADE;
DROP VIEW IF EXISTS public.v_current_week_vitals CASCADE;
DROP VIEW IF EXISTS public.v_awards CASCADE;
DROP VIEW IF EXISTS public.v_extracurriculars CASCADE;
DROP VIEW IF EXISTS public.v_programs CASCADE;
DROP VIEW IF EXISTS public.v_applications CASCADE;
DROP VIEW IF EXISTS public.v_goals CASCADE;

-- Latest assessment per user
CREATE VIEW public.v_current_assessment AS
SELECT DISTINCT ON (user_id)
  id,
  user_id,
  session_id,
  profile_data,
  scores,
  archetype,
  completeness_score,
  completed_at,
  created_at
FROM assessments
WHERE completed_at IS NOT NULL
ORDER BY user_id, completed_at DESC;

-- Active game plan per user
CREATE VIEW public.v_active_game_plan AS
SELECT
  id,
  user_id,
  assessment_id,
  plan_data,
  target_archetype,
  target_tier,
  current_phase,
  current_week,
  completion_percentage,
  plan_status,
  activated_at,
  created_at,
  updated_at
FROM game_plans
WHERE plan_status = 'active';

-- Latest week vitals per user
CREATE VIEW public.v_current_week_vitals AS
SELECT DISTINCT ON (user_id)
  id,
  user_id,
  week_number,
  week_start_date,
  progress_status,
  completion_percentage,
  academic_vitals,
  ec_vitals,
  growth_vitals,
  action_plan,
  updated_at
FROM weekly_vitals
ORDER BY user_id, week_number DESC;

-- Items by type (convenience views)
CREATE VIEW public.v_awards AS
SELECT * FROM student_items WHERE item_type = 'award';

CREATE VIEW public.v_extracurriculars AS
SELECT * FROM student_items WHERE item_type = 'extracurricular';

CREATE VIEW public.v_programs AS
SELECT * FROM student_items WHERE item_type = 'program';

CREATE VIEW public.v_applications AS
SELECT * FROM student_items WHERE item_type = 'application';

CREATE VIEW public.v_goals AS
SELECT * FROM student_items WHERE item_type = 'goal';

-- User dashboard summary
CREATE VIEW public.v_user_dashboard AS
SELECT
  p.id as user_id,
  p.email,
  p.first_name,
  p.last_name,
  p.role,
  p.grade,
  p.target_major,
  p.onboarding_completed,

  -- Assessment Summary
  a.id as latest_assessment_id,
  a.archetype,
  a.scores->>'ivy_ready_score' as ivy_ready_score,
  a.scores->>'overall' as overall_score,
  a.completeness_score,
  a.completed_at as assessment_completed_at,

  -- Game Plan Summary
  g.id as active_game_plan_id,
  g.current_phase,
  g.current_week,
  g.completion_percentage as plan_completion,
  g.target_tier,

  -- Item Counts
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'award') as award_count,
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'extracurricular') as ec_count,
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'goal') as goal_count,

  -- Timeline Event Count
  (SELECT COUNT(*) FROM timeline_events te WHERE te.user_id = p.id) as timeline_event_count

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

-- -----------------------------------------------------------------------------
-- STEP 4: Create profile sync trigger
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION sync_profile_from_assessment()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE profiles SET
    first_name = COALESCE(
      profiles.first_name,
      split_part(NEW.profile_data->'identity'->>'name', ' ', 1)
    ),
    last_name = COALESCE(
      profiles.last_name,
      CASE
        WHEN array_length(string_to_array(NEW.profile_data->'identity'->>'name', ' '), 1) > 1
        THEN split_part(NEW.profile_data->'identity'->>'name', ' ', 2)
        ELSE NULL
      END
    ),
    grade = COALESCE(
      profiles.grade,
      (NEW.profile_data->'identity'->>'grade')::INTEGER
    ),
    high_school = COALESCE(
      profiles.high_school,
      NEW.profile_data->'high_school'->>'hs_name'
    ),
    target_major = COALESCE(
      profiles.target_major,
      NEW.profile_data->>'intended_major'
    ),
    onboarding_completed = true,
    updated_at = NOW()
  WHERE id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS sync_profile_on_assessment ON assessments;
CREATE TRIGGER sync_profile_on_assessment
  AFTER INSERT OR UPDATE ON assessments
  FOR EACH ROW
  WHEN (NEW.completed_at IS NOT NULL)
  EXECUTE FUNCTION sync_profile_from_assessment();

-- -----------------------------------------------------------------------------
-- STEP 5: Create timeline event triggers
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_assessment_timeline_event()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.completed_at IS NOT NULL THEN
    INSERT INTO timeline_events (
      user_id, event_type, event_subtype, title, description,
      event_date, impact, icon, related_assessment_id, metadata
    ) VALUES (
      NEW.user_id,
      'assessment',
      'completed',
      'IvyReady Assessment Completed',
      'Completed assessment with score of ' || COALESCE((NEW.scores->>'overall')::TEXT, '0') || ' - Archetype: ' || COALESCE(NEW.archetype, 'Unknown'),
      CURRENT_DATE,
      'major',
      'clipboard-check',
      NEW.id,
      jsonb_build_object(
        'ivy_ready_score', COALESCE(NEW.scores->>'ivy_ready_score', NEW.scores->>'overall'),
        'archetype', NEW.archetype,
        'completeness_score', NEW.completeness_score
      )
    )
    ON CONFLICT DO NOTHING;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS create_timeline_on_assessment ON assessments;
CREATE TRIGGER create_timeline_on_assessment
  AFTER INSERT ON assessments
  FOR EACH ROW
  EXECUTE FUNCTION create_assessment_timeline_event();

-- Game plan timeline trigger
CREATE OR REPLACE FUNCTION create_gameplan_timeline_event()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.plan_status = 'active' THEN
    INSERT INTO timeline_events (
      user_id, event_type, event_subtype, title, description,
      event_date, impact, icon, related_game_plan_id, metadata
    ) VALUES (
      NEW.user_id,
      'milestone',
      'game_plan_created',
      'Game Plan Created',
      'Created personalized game plan targeting ' || COALESCE(NEW.target_tier, 'success'),
      CURRENT_DATE,
      'major',
      'map',
      NEW.id,
      jsonb_build_object(
        'target_tier', NEW.target_tier,
        'current_phase', NEW.current_phase
      )
    )
    ON CONFLICT DO NOTHING;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS create_timeline_on_gameplan ON game_plans;
CREATE TRIGGER create_timeline_on_gameplan
  AFTER INSERT ON game_plans
  FOR EACH ROW
  EXECUTE FUNCTION create_gameplan_timeline_event();

-- -----------------------------------------------------------------------------
-- STEP 6: Backfill - Sync existing profiles from assessments
-- -----------------------------------------------------------------------------

UPDATE profiles p SET
  first_name = COALESCE(p.first_name, split_part(a.profile_data->'identity'->>'name', ' ', 1)),
  grade = COALESCE(p.grade, (a.profile_data->'identity'->>'grade')::INTEGER),
  high_school = COALESCE(p.high_school, a.profile_data->'high_school'->>'hs_name'),
  target_major = COALESCE(p.target_major, a.profile_data->>'intended_major'),
  onboarding_completed = true,
  updated_at = NOW()
FROM assessments a
WHERE a.user_id = p.id
AND a.completed_at IS NOT NULL;

-- -----------------------------------------------------------------------------
-- STEP 7: Backfill timeline events for existing data
-- -----------------------------------------------------------------------------

-- Assessment timeline events
INSERT INTO timeline_events (user_id, event_type, event_subtype, title, description, event_date, impact, icon, related_assessment_id, metadata)
SELECT
  user_id,
  'assessment',
  'completed',
  'IvyReady Assessment Completed',
  'Completed assessment with score of ' || COALESCE((scores->>'overall')::TEXT, '0') || ' - Archetype: ' || COALESCE(archetype, 'Unknown'),
  COALESCE(completed_at::DATE, created_at::DATE),
  'major',
  'clipboard-check',
  id,
  jsonb_build_object(
    'ivy_ready_score', COALESCE(scores->>'ivy_ready_score', scores->>'overall'),
    'archetype', archetype,
    'completeness_score', completeness_score
  )
FROM assessments
WHERE completed_at IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM timeline_events te WHERE te.related_assessment_id = assessments.id
)
ON CONFLICT DO NOTHING;

-- Game plan timeline events
INSERT INTO timeline_events (user_id, event_type, event_subtype, title, description, event_date, impact, icon, related_game_plan_id, metadata)
SELECT
  user_id,
  'milestone',
  'game_plan_created',
  'Game Plan Created',
  'Created personalized game plan targeting ' || COALESCE(target_tier, 'success'),
  COALESCE(activated_at::DATE, created_at::DATE),
  'major',
  'map',
  id,
  jsonb_build_object(
    'target_tier', target_tier,
    'current_phase', current_phase
  )
FROM game_plans
WHERE plan_status = 'active'
AND NOT EXISTS (
  SELECT 1 FROM timeline_events te WHERE te.related_game_plan_id = game_plans.id
)
ON CONFLICT DO NOTHING;

-- -----------------------------------------------------------------------------
-- STEP 8: Verify
-- -----------------------------------------------------------------------------

SELECT '=== MIGRATION 014 COMPLETE ===' as status;

SELECT 'Tables remaining:' as info;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;

SELECT 'Data counts:' as info;
SELECT 'profiles' as tbl, COUNT(*) as cnt FROM profiles
UNION ALL SELECT 'assessments', COUNT(*) FROM assessments
UNION ALL SELECT 'game_plans', COUNT(*) FROM game_plans
UNION ALL SELECT 'timeline_events', COUNT(*) FROM timeline_events
UNION ALL SELECT 'weekly_vitals', COUNT(*) FROM weekly_vitals
UNION ALL SELECT 'student_items', COUNT(*) FROM student_items;
