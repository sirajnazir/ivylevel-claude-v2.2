-- =============================================================================
-- IvyQuest Beta Database Schema
-- Version: 1.0.0
-- Date: January 2026
--
-- Run this in Supabase SQL Editor
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. UTILITY FUNCTIONS
-- -----------------------------------------------------------------------------

-- Auto-update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 1. PROFILES (Extended User Metadata)
-- -----------------------------------------------------------------------------

-- Drop existing if needed (careful in production!)
DROP TABLE IF EXISTS public.profiles CASCADE;

CREATE TABLE public.profiles (
  -- Primary Key (matches auth.users.id)
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Basic Info
  email TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'coach', 'admin', 'parent')),
  first_name TEXT,
  last_name TEXT,

  -- Student-Specific (NULL for non-students)
  grade INTEGER CHECK (grade IS NULL OR grade BETWEEN 9 AND 12),
  graduation_year INTEGER,
  high_school TEXT,
  target_major TEXT,

  -- Coach/Admin Specific
  organization TEXT,

  -- Onboarding State
  onboarding_completed BOOLEAN DEFAULT false,
  onboarding_step INTEGER DEFAULT 0,

  -- Preferences (JSONB for flexibility)
  preferences JSONB DEFAULT '{
    "notifications": true,
    "theme": "light",
    "timezone": "America/Los_Angeles"
  }'::jsonb,

  -- Status
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_profiles_role ON profiles(role);
CREATE INDEX idx_profiles_graduation_year ON profiles(graduation_year);
CREATE INDEX idx_profiles_email ON profiles(email);

-- RLS Policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Coaches can view student profiles" ON profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role IN ('coach', 'admin')
    )
  );

-- Trigger: Auto-create profile on signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, role, first_name, last_name, grade, high_school)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'role', 'student'),
    NEW.raw_user_meta_data->>'first_name',
    NEW.raw_user_meta_data->>'last_name',
    (NEW.raw_user_meta_data->>'grade')::INTEGER,
    NEW.raw_user_meta_data->>'high_school'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- Trigger: Auto-update timestamp
CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();


-- -----------------------------------------------------------------------------
-- 2. ASSESSMENTS (IvyReady Assessment Results)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS public.assessments CASCADE;

CREATE TABLE public.assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Assessment Metadata
  session_id TEXT NOT NULL,
  assessment_version TEXT DEFAULT 'v13',
  assessment_type TEXT DEFAULT 'full' CHECK (assessment_type IN ('full', 'quick', 'refresh')),

  -- Profile Snapshot (JSONB - complete profile at assessment time)
  profile_data JSONB NOT NULL,

  -- Scores (JSONB - assessment results)
  scores JSONB NOT NULL,

  -- Archetype Detection
  archetype TEXT,
  archetype_confidence DECIMAL(3,2),

  -- Completeness
  completeness_score INTEGER DEFAULT 0 CHECK (completeness_score BETWEEN 0 AND 100),
  questions_answered INTEGER DEFAULT 0,
  total_questions INTEGER DEFAULT 0,

  -- Timestamps
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT unique_user_session UNIQUE(user_id, session_id)
);

-- Indexes
CREATE INDEX idx_assessments_user ON assessments(user_id);
CREATE INDEX idx_assessments_completed ON assessments(completed_at) WHERE completed_at IS NOT NULL;
CREATE INDEX idx_assessments_archetype ON assessments(archetype);
CREATE INDEX idx_assessments_scores ON assessments USING GIN (scores);
CREATE INDEX idx_assessments_profile ON assessments USING GIN (profile_data);

-- RLS Policies
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own assessments" ON assessments
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own assessments" ON assessments
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own assessments" ON assessments
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Coaches can view student assessments" ON assessments
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role IN ('coach', 'admin')
    )
  );


-- -----------------------------------------------------------------------------
-- 3. GAME PLANS (Strategic Multi-Year Plans)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS public.game_plans CASCADE;

CREATE TABLE public.game_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  assessment_id UUID REFERENCES assessments(id),

  -- Plan Metadata
  plan_version INTEGER DEFAULT 1,
  plan_status TEXT DEFAULT 'active' CHECK (plan_status IN ('draft', 'active', 'archived', 'completed')),

  -- Plan Content (JSONB - full game plan)
  plan_data JSONB NOT NULL,

  -- Target Profile
  target_archetype TEXT,
  target_tier TEXT,
  target_schools JSONB,

  -- Progress Tracking
  current_phase TEXT,
  current_week INTEGER DEFAULT 1,
  completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  activated_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_game_plans_user ON game_plans(user_id);
CREATE INDEX idx_game_plans_status ON game_plans(plan_status);
CREATE INDEX idx_game_plans_active ON game_plans(user_id, plan_status) WHERE plan_status = 'active';
CREATE INDEX idx_game_plans_data ON game_plans USING GIN (plan_data);

-- RLS Policies
ALTER TABLE game_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own game plans" ON game_plans
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own game plans" ON game_plans
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own game plans" ON game_plans
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Coaches can view student game plans" ON game_plans
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role IN ('coach', 'admin')
    )
  );

-- Trigger: Auto-update timestamp
CREATE TRIGGER game_plans_updated_at
  BEFORE UPDATE ON game_plans
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();


-- -----------------------------------------------------------------------------
-- 4. WEEKLY VITALS (Weekly Progress & Action Plans)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS public.weekly_vitals CASCADE;

CREATE TABLE public.weekly_vitals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  game_plan_id UUID REFERENCES game_plans(id),

  -- Week Identification
  week_number INTEGER NOT NULL,
  week_start_date DATE NOT NULL,
  week_end_date DATE NOT NULL,
  academic_year TEXT,

  -- Progress Status
  progress_status TEXT DEFAULT 'not_started' CHECK (progress_status IN ('not_started', 'behind', 'on_track', 'ahead')),
  completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),

  -- Vitals Snapshots (JSONB)
  academic_vitals JSONB,
  ec_vitals JSONB,
  growth_vitals JSONB,

  -- Action Plan (JSONB - weekly execution items)
  action_plan JSONB,

  -- Session Info
  session_date TIMESTAMPTZ,
  session_notes TEXT,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT unique_user_week UNIQUE(user_id, week_number)
);

-- Indexes
CREATE INDEX idx_weekly_vitals_user ON weekly_vitals(user_id);
CREATE INDEX idx_weekly_vitals_week ON weekly_vitals(user_id, week_number);
CREATE INDEX idx_weekly_vitals_date ON weekly_vitals(week_start_date);
CREATE INDEX idx_weekly_vitals_action_plan ON weekly_vitals USING GIN (action_plan);
CREATE INDEX idx_weekly_vitals_academic ON weekly_vitals USING GIN (academic_vitals);

-- RLS Policies
ALTER TABLE weekly_vitals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own weekly vitals" ON weekly_vitals
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own weekly vitals" ON weekly_vitals
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own weekly vitals" ON weekly_vitals
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Coaches can view student weekly vitals" ON weekly_vitals
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role IN ('coach', 'admin')
    )
  );

-- Trigger: Auto-update timestamp
CREATE TRIGGER weekly_vitals_updated_at
  BEFORE UPDATE ON weekly_vitals
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();


-- -----------------------------------------------------------------------------
-- 5. STUDENT ITEMS (Universal Ledger - Awards, ECs, Programs, etc.)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS public.student_items CASCADE;

CREATE TABLE public.student_items (
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

-- Indexes
CREATE INDEX idx_student_items_user ON student_items(user_id);
CREATE INDEX idx_student_items_type ON student_items(item_type);
CREATE INDEX idx_student_items_state ON student_items(tier1_state);
CREATE INDEX idx_student_items_type_state ON student_items(user_id, item_type, tier1_state);
CREATE INDEX idx_student_items_deadline ON student_items(deadline_date) WHERE deadline_date IS NOT NULL;
CREATE INDEX idx_student_items_extended ON student_items USING GIN (extended_data);

-- RLS Policies
ALTER TABLE student_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own items" ON student_items
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own items" ON student_items
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own items" ON student_items
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own items" ON student_items
  FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Coaches can view student items" ON student_items
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role IN ('coach', 'admin')
    )
  );

-- Trigger: Auto-update timestamp
CREATE TRIGGER student_items_updated_at
  BEFORE UPDATE ON student_items
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();


-- -----------------------------------------------------------------------------
-- 6. TIMELINE EVENTS (Growth Journey)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS public.timeline_events CASCADE;

CREATE TABLE public.timeline_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Event Type
  event_type TEXT NOT NULL CHECK (event_type IN (
    'milestone',
    'growth_event',
    'phase_transition',
    'academic',
    'application',
    'award',
    'program',
    'project'
  )),
  event_subtype TEXT,

  -- Event Info
  title TEXT NOT NULL,
  description TEXT,
  event_date DATE NOT NULL,

  -- Impact
  impact TEXT CHECK (impact IN ('minor', 'moderate', 'major')),
  impact_score INTEGER CHECK (impact_score IS NULL OR impact_score BETWEEN 1 AND 10),

  -- Visual
  icon TEXT,
  color TEXT,

  -- Links
  related_item_id UUID REFERENCES student_items(id),

  -- Extended Data
  metadata JSONB DEFAULT '{}'::jsonb,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_timeline_user ON timeline_events(user_id);
CREATE INDEX idx_timeline_date ON timeline_events(user_id, event_date DESC);
CREATE INDEX idx_timeline_type ON timeline_events(event_type);
CREATE INDEX idx_timeline_impact ON timeline_events(impact) WHERE impact = 'major';

-- RLS Policies
ALTER TABLE timeline_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own timeline" ON timeline_events
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own events" ON timeline_events
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Coaches can view student timeline" ON timeline_events
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role IN ('coach', 'admin')
    )
  );


-- -----------------------------------------------------------------------------
-- 7. COACH RELATIONSHIPS (Coach-Student Mapping)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS public.coach_relationships CASCADE;

CREATE TABLE public.coach_relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  coach_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  student_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Relationship Status
  status TEXT DEFAULT 'active' CHECK (status IN ('pending', 'active', 'paused', 'ended')),

  -- Permissions
  can_view_assessments BOOLEAN DEFAULT true,
  can_view_game_plan BOOLEAN DEFAULT true,
  can_edit_game_plan BOOLEAN DEFAULT false,
  can_view_progress BOOLEAN DEFAULT true,
  can_send_messages BOOLEAN DEFAULT true,

  -- Timestamps
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_coach_rel_coach ON coach_relationships(coach_id);
CREATE INDEX idx_coach_rel_student ON coach_relationships(student_id);
CREATE UNIQUE INDEX idx_coach_rel_unique ON coach_relationships(coach_id, student_id) WHERE status = 'active';

-- RLS Policies
ALTER TABLE coach_relationships ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Coaches can view their relationships" ON coach_relationships
  FOR SELECT USING (auth.uid() = coach_id);

CREATE POLICY "Students can view their coach" ON coach_relationships
  FOR SELECT USING (auth.uid() = student_id);

CREATE POLICY "Coaches can manage relationships" ON coach_relationships
  FOR ALL USING (auth.uid() = coach_id);


-- -----------------------------------------------------------------------------
-- 8. HELPER VIEWS
-- -----------------------------------------------------------------------------

-- Latest assessment per user
CREATE OR REPLACE VIEW public.v_current_assessment AS
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
CREATE OR REPLACE VIEW public.v_active_game_plan AS
SELECT
  id,
  user_id,
  assessment_id,
  plan_version,
  plan_data,
  target_archetype,
  current_phase,
  current_week,
  completion_percentage,
  created_at,
  updated_at
FROM game_plans
WHERE plan_status = 'active';

-- Latest week vitals per user
CREATE OR REPLACE VIEW public.v_current_week_vitals AS
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
CREATE OR REPLACE VIEW public.v_awards AS
SELECT * FROM student_items WHERE item_type = 'award';

CREATE OR REPLACE VIEW public.v_extracurriculars AS
SELECT * FROM student_items WHERE item_type = 'extracurricular';

CREATE OR REPLACE VIEW public.v_programs AS
SELECT * FROM student_items WHERE item_type = 'program';

CREATE OR REPLACE VIEW public.v_applications AS
SELECT * FROM student_items WHERE item_type = 'application';

CREATE OR REPLACE VIEW public.v_goals AS
SELECT * FROM student_items WHERE item_type = 'goal';

-- User dashboard summary
CREATE OR REPLACE VIEW public.v_user_dashboard AS
SELECT
  p.id as user_id,
  p.email,
  p.first_name,
  p.last_name,
  p.role,
  p.grade,
  p.graduation_year,
  p.onboarding_completed,

  -- Assessment Summary
  a.id as latest_assessment_id,
  a.archetype,
  a.scores->>'ivy_ready_score' as ivy_ready_score,
  a.completed_at as assessment_completed_at,

  -- Game Plan Summary
  g.id as active_game_plan_id,
  g.current_phase,
  g.current_week,
  g.completion_percentage as plan_completion,

  -- Weekly Vitals Summary
  w.week_number as current_week_number,
  w.progress_status,
  w.completion_percentage as week_completion,

  -- Item Counts
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'award') as award_count,
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'extracurricular') as ec_count,
  (SELECT COUNT(*) FROM student_items si WHERE si.user_id = p.id AND si.item_type = 'application') as application_count,

  -- Timeline Event Count
  (SELECT COUNT(*) FROM timeline_events te WHERE te.user_id = p.id) as timeline_event_count

FROM profiles p
LEFT JOIN v_current_assessment a ON a.user_id = p.id
LEFT JOIN v_active_game_plan g ON g.user_id = p.id
LEFT JOIN v_current_week_vitals w ON w.user_id = p.id
WHERE p.role = 'student';


-- -----------------------------------------------------------------------------
-- 9. GRANTS (if needed for specific roles)
-- -----------------------------------------------------------------------------

-- Grant usage to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;


-- -----------------------------------------------------------------------------
-- DONE!
-- -----------------------------------------------------------------------------

-- Verify tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Verify views created
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;
