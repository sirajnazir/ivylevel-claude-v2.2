-- =============================================================================
-- IvyQuest Schema Fixes & Enhancements
-- Migration 013: Profile sync, missing tables, and timeline automation
-- =============================================================================

-- -----------------------------------------------------------------------------
-- FIX 1: Add target_major column to profiles if missing
-- -----------------------------------------------------------------------------

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'profiles' AND column_name = 'target_major'
  ) THEN
    ALTER TABLE profiles ADD COLUMN target_major TEXT;
  END IF;
END $$;

-- -----------------------------------------------------------------------------
-- FIX 2: Create Profile Sync Function
-- After assessment completes, sync key fields to profiles table
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION sync_profile_from_assessment()
RETURNS TRIGGER AS $$
BEGIN
  -- Update profiles with data from assessment
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

-- Create trigger (drop if exists first)
DROP TRIGGER IF EXISTS sync_profile_on_assessment ON assessments;
CREATE TRIGGER sync_profile_on_assessment
  AFTER INSERT OR UPDATE ON assessments
  FOR EACH ROW
  WHEN (NEW.completed_at IS NOT NULL)
  EXECUTE FUNCTION sync_profile_from_assessment();

-- Manually sync existing assessments to profiles (backfill)
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
-- FIX 3: Create student_items Table (Universal Ledger) if not exists
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.student_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Item Identification
  item_type TEXT NOT NULL CHECK (item_type IN (
    'award',
    'extracurricular',
    'program',
    'application',
    'goal',
    'test',
    'essay',
    'recommendation',
    'project'
  )),
  item_subtype TEXT,

  -- Core Info
  title TEXT NOT NULL,
  description TEXT,

  -- State Machine
  tier1_state TEXT NOT NULL DEFAULT 'planned' CHECK (tier1_state IN (
    'planned',
    'in_progress',
    'submitted',
    'outcome',
    'archived'
  )),
  tier2_substate TEXT,
  status_detail TEXT,

  -- Metrics
  metric_type TEXT,
  metric_value TEXT,
  metric_unit TEXT,

  -- Dates
  start_date DATE,
  end_date DATE,
  deadline_date DATE,
  submit_date DATE,
  outcome_date DATE,

  -- Context
  organization TEXT,
  location TEXT,
  grade_levels TEXT[],

  -- Extended Data (JSONB)
  extended_data JSONB DEFAULT '{}'::jsonb,

  -- Provenance
  source TEXT DEFAULT 'user_input',
  confidence TEXT DEFAULT 'high' CHECK (confidence IN ('high', 'medium', 'low')),

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for student_items
CREATE INDEX IF NOT EXISTS idx_student_items_user ON student_items(user_id);
CREATE INDEX IF NOT EXISTS idx_student_items_type ON student_items(item_type);
CREATE INDEX IF NOT EXISTS idx_student_items_state ON student_items(tier1_state);
CREATE INDEX IF NOT EXISTS idx_student_items_type_state ON student_items(user_id, item_type, tier1_state);
CREATE INDEX IF NOT EXISTS idx_student_items_deadline ON student_items(deadline_date) WHERE deadline_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_student_items_extended ON student_items USING GIN (extended_data);

-- RLS Policies for student_items
ALTER TABLE student_items ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own items" ON student_items;
CREATE POLICY "Users can view own items" ON student_items
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own items" ON student_items;
CREATE POLICY "Users can insert own items" ON student_items
  FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own items" ON student_items;
CREATE POLICY "Users can update own items" ON student_items
  FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own items" ON student_items;
CREATE POLICY "Users can delete own items" ON student_items
  FOR DELETE USING (auth.uid() = user_id);

-- Coach policies for student_items
DROP POLICY IF EXISTS "Coaches can view student items" ON student_items;
CREATE POLICY "Coaches can view student items" ON student_items
  FOR SELECT USING (
    public.get_current_user_role() IN ('coach', 'admin')
  );


-- -----------------------------------------------------------------------------
-- FIX 4: Ensure weekly_vitals table has all columns
-- -----------------------------------------------------------------------------

-- Add game_plan_id if missing
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'weekly_vitals' AND column_name = 'game_plan_id'
  ) THEN
    ALTER TABLE weekly_vitals ADD COLUMN game_plan_id UUID REFERENCES game_plans(id);
  END IF;
END $$;

-- Add academic_year if missing
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'weekly_vitals' AND column_name = 'academic_year'
  ) THEN
    ALTER TABLE weekly_vitals ADD COLUMN academic_year TEXT;
  END IF;
END $$;


-- -----------------------------------------------------------------------------
-- FIX 5: Create/Update Helper Views
-- -----------------------------------------------------------------------------

-- Drop existing views first to allow column changes
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
-- FIX 6: Auto-create Timeline Event on Assessment Completion
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_assessment_timeline_event()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.completed_at IS NOT NULL THEN
    INSERT INTO timeline_events (
      user_id,
      event_type,
      event_subtype,
      title,
      description,
      event_date,
      impact,
      icon,
      related_assessment_id,
      metadata
    ) VALUES (
      NEW.user_id,
      'assessment',
      'completed',
      'IvyReady Assessment Completed',
      'Completed initial assessment with score of ' || COALESCE((NEW.scores->>'ivy_ready_score')::TEXT, (NEW.scores->>'overall')::TEXT, '0') || ' and archetype: ' || COALESCE(NEW.archetype, 'Unknown'),
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


-- -----------------------------------------------------------------------------
-- FIX 7: Auto-create Timeline Event on Game Plan Creation
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_gameplan_timeline_event()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.activated_at IS NOT NULL OR NEW.plan_status = 'active' THEN
    INSERT INTO timeline_events (
      user_id,
      event_type,
      event_subtype,
      title,
      description,
      event_date,
      impact,
      icon,
      related_game_plan_id,
      metadata
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
-- FIX 8: Backfill Timeline Events for Existing Data
-- -----------------------------------------------------------------------------

-- Create timeline events for existing assessments (if not already created)
INSERT INTO timeline_events (user_id, event_type, event_subtype, title, description, event_date, impact, icon, related_assessment_id, metadata)
SELECT
  user_id,
  'assessment',
  'completed',
  'IvyReady Assessment Completed',
  'Completed initial assessment with score of ' || COALESCE((scores->>'ivy_ready_score')::TEXT, (scores->>'overall')::TEXT, '0') || ' and archetype: ' || COALESCE(archetype, 'Unknown'),
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
  SELECT 1 FROM timeline_events te
  WHERE te.related_assessment_id = assessments.id
)
ON CONFLICT DO NOTHING;

-- Create timeline events for existing game plans (if not already created)
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
  SELECT 1 FROM timeline_events te
  WHERE te.related_game_plan_id = game_plans.id
)
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- VERIFY: Output summary
-- -----------------------------------------------------------------------------

SELECT 'Migration 013 complete!' as status;

-- Show table counts
SELECT 'profiles' as table_name, COUNT(*) as row_count FROM profiles
UNION ALL SELECT 'assessments', COUNT(*) FROM assessments
UNION ALL SELECT 'game_plans', COUNT(*) FROM game_plans
UNION ALL SELECT 'student_items', COUNT(*) FROM student_items
UNION ALL SELECT 'weekly_vitals', COUNT(*) FROM weekly_vitals
UNION ALL SELECT 'timeline_events', COUNT(*) FROM timeline_events;
