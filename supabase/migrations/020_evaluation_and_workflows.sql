-- =============================================================================
-- IvyQuest v10.0 Migration 020: Evaluation Framework & Proactive Workflows
-- Version: 1.0.0
-- Date: January 2026
--
-- Creates tables for:
-- 1. Evaluation golden dataset (benchmark testing)
-- 2. Evaluation runs (test results)
-- 3. Workflow state (proactive workflow tracking)
-- 4. Notifications (student alerts)
-- 5. Coach tasks (escalations)
-- 6. Profile extensions (narrative columns, activity tracking)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. EVALUATION GOLDEN DATASET
-- Stores benchmark examples for agent evaluation (from Jenny Duan coaching)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.evaluation_golden (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Profile identifier (can be synthetic for privacy)
  profile_id TEXT NOT NULL UNIQUE,

  -- Input profile data (complete student profile)
  input_profile JSONB NOT NULL,

  -- Expected outputs (Jenny's actual outputs)
  expected_outputs JSONB NOT NULL,
  -- Structure: {
  --   brand_statement: string,
  --   themes: string[],
  --   first_principle: string,
  --   narrative_dna: string,
  --   recommended_activities: [...],
  --   recommended_awards: [...],
  --   archetype: {id, label, confidence}
  -- }

  -- Jenny's quality annotations
  jenny_annotations JSONB DEFAULT '{}',
  -- Structure: {
  --   brand_statement_quality: 1-5,
  --   theme_coherence: 1-5,
  --   activity_alignment: 1-5,
  --   award_fit: 1-5,
  --   notes: string
  -- }

  -- Difficulty tier for stratified testing
  difficulty_tier TEXT CHECK (difficulty_tier IN ('easy', 'medium', 'hard')),

  -- Tags for filtering
  tags TEXT[] DEFAULT '{}',

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_evaluation_golden_difficulty ON evaluation_golden(difficulty_tier);
CREATE INDEX IF NOT EXISTS idx_evaluation_golden_tags ON evaluation_golden USING GIN(tags);

-- Trigger
CREATE TRIGGER evaluation_golden_updated_at
  BEFORE UPDATE ON evaluation_golden
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

-- Comment
COMMENT ON TABLE evaluation_golden IS 'Golden dataset for agent evaluation - benchmark examples from Jenny Duan coaching';


-- -----------------------------------------------------------------------------
-- 2. EVALUATION RUNS
-- Stores results from evaluation pipeline runs
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.evaluation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Run identification
  run_id TEXT NOT NULL,
  agent_version TEXT NOT NULL,

  -- Reference to golden example
  golden_id UUID REFERENCES evaluation_golden(id) ON DELETE CASCADE,

  -- Agent outputs
  actual_outputs JSONB NOT NULL,

  -- Objective metric scores (automated checks)
  objective_scores JSONB DEFAULT '{}',
  -- Structure: {
  --   brand_statement_length: {score, passed, details},
  --   theme_coverage: {score, passed, details},
  --   required_fields: {score, passed, details}
  -- }

  -- LLM-as-Judge scores
  llm_judge_scores JSONB DEFAULT '{}',
  -- Structure: {
  --   brand_statement: {score, max_score, evaluation, passed},
  --   themes: {score, max_score, overlap_count, coverage, passed},
  --   overall_quality: {score, max_score, evaluation}
  -- }

  -- Overall results
  overall_score FLOAT,
  passed BOOLEAN DEFAULT false,

  -- Performance
  duration_ms INTEGER,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_run_id ON evaluation_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_golden ON evaluation_runs(golden_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_version ON evaluation_runs(agent_version);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_passed ON evaluation_runs(passed);

-- Comment
COMMENT ON TABLE evaluation_runs IS 'Results from agent evaluation runs - tracks performance against golden dataset';


-- -----------------------------------------------------------------------------
-- 3. WORKFLOW STATE
-- Tracks proactive workflow execution per student
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.workflow_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Profile reference
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Workflow identification
  workflow_name TEXT NOT NULL,

  -- Execution tracking
  last_run TIMESTAMPTZ,
  next_run TIMESTAMPTZ,
  run_count INTEGER DEFAULT 0,

  -- Workflow-specific state
  state JSONB DEFAULT '{}',

  -- Control
  enabled BOOLEAN DEFAULT true,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Unique constraint per profile+workflow
  CONSTRAINT unique_profile_workflow UNIQUE(profile_id, workflow_name)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_state_profile ON workflow_state(profile_id);
CREATE INDEX IF NOT EXISTS idx_workflow_state_next_run ON workflow_state(next_run) WHERE enabled = true;
CREATE INDEX IF NOT EXISTS idx_workflow_state_workflow ON workflow_state(workflow_name);

-- Trigger
CREATE TRIGGER workflow_state_updated_at
  BEFORE UPDATE ON workflow_state
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

-- Comment
COMMENT ON TABLE workflow_state IS 'Tracks proactive workflow state per student (silence detection, deadline alerts, etc.)';


-- -----------------------------------------------------------------------------
-- 4. NOTIFICATIONS
-- Student notifications from workflows and agents
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Profile reference
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Notification content
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  type TEXT DEFAULT 'info' CHECK (type IN (
    'info',
    'success',
    'warning',
    'urgent',
    'deadline_low',
    'deadline_medium',
    'deadline_high',
    'silence_alert',
    'opportunity',
    'award',
    'celebration'
  )),

  -- Status
  read BOOLEAN DEFAULT false,
  read_at TIMESTAMPTZ,

  -- Action (optional deep link)
  action_url TEXT,
  action_label TEXT,

  -- Source tracking
  source TEXT, -- 'workflow', 'agent', 'coach', 'system'
  source_workflow TEXT, -- workflow name if from workflow

  -- Metadata
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_notifications_profile ON notifications(profile_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(profile_id, read) WHERE read = false;
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC);

-- RLS
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own notifications" ON notifications
  FOR SELECT USING (auth.uid() = profile_id);

CREATE POLICY "Users can update own notifications" ON notifications
  FOR UPDATE USING (auth.uid() = profile_id);

CREATE POLICY "System can insert notifications" ON notifications
  FOR INSERT WITH CHECK (true);

-- Comment
COMMENT ON TABLE notifications IS 'Student notifications from workflows, agents, and coaches';


-- -----------------------------------------------------------------------------
-- 5. COACH TASKS
-- Escalations requiring coach attention
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.coach_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Profile being coached
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Assigned coach (null if unassigned)
  coach_id UUID REFERENCES profiles(id) ON DELETE SET NULL,

  -- Task details
  task_type TEXT NOT NULL CHECK (task_type IN (
    'silence_intervention',
    'crisis_review',
    'handoff_approval',
    'plan_review',
    'escalation',
    'followup'
  )),
  priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),

  title TEXT NOT NULL,
  description TEXT,

  -- Status
  status TEXT DEFAULT 'pending' CHECK (status IN (
    'pending',
    'assigned',
    'in_progress',
    'completed',
    'dismissed'
  )),

  -- Resolution
  resolution TEXT,
  resolved_at TIMESTAMPTZ,
  resolved_by UUID REFERENCES profiles(id),

  -- Due date
  due_at TIMESTAMPTZ,

  -- Related items
  related_crisis_id UUID,
  related_item_id UUID,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_coach_tasks_profile ON coach_tasks(profile_id);
CREATE INDEX IF NOT EXISTS idx_coach_tasks_coach ON coach_tasks(coach_id);
CREATE INDEX IF NOT EXISTS idx_coach_tasks_status ON coach_tasks(status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_coach_tasks_priority ON coach_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_coach_tasks_due ON coach_tasks(due_at) WHERE status = 'pending';

-- Trigger
CREATE TRIGGER coach_tasks_updated_at
  BEFORE UPDATE ON coach_tasks
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

-- RLS
ALTER TABLE coach_tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Coaches can view tasks" ON coach_tasks
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role IN ('coach', 'admin')
    )
  );

CREATE POLICY "Coaches can manage tasks" ON coach_tasks
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM profiles p
      WHERE p.id = auth.uid()
      AND p.role IN ('coach', 'admin')
    )
  );

-- Comment
COMMENT ON TABLE coach_tasks IS 'Tasks requiring coach attention - escalations from workflows and agents';


-- -----------------------------------------------------------------------------
-- 6. PROFILE EXTENSIONS
-- Add narrative columns and activity tracking to profiles
-- -----------------------------------------------------------------------------

-- Add narrative synthesis columns (for storing NarrativeSynthesisAgent output)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_brand_statement TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_dna TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_first_principle TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_themes JSONB DEFAULT '[]';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_confidence FLOAT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS narrative_updated_at TIMESTAMPTZ;

-- Add activity tracking for silence detection
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMPTZ DEFAULT NOW();

-- Add notification preferences
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS preferred_contact_time TIME DEFAULT '15:00';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{
  "email": true,
  "push": true,
  "sms": false,
  "deadline_alerts": true,
  "weekly_digest": true,
  "silence_nudges": true
}'::jsonb;

-- Indexes for new columns
CREATE INDEX IF NOT EXISTS idx_profiles_last_activity ON profiles(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_profiles_narrative ON profiles(narrative_updated_at) WHERE narrative_brand_statement IS NOT NULL;

-- Comment
COMMENT ON COLUMN profiles.narrative_brand_statement IS 'One-sentence brand statement from NarrativeSynthesisAgent';
COMMENT ON COLUMN profiles.narrative_dna IS 'Extended narrative DNA (2-3 paragraphs)';
COMMENT ON COLUMN profiles.narrative_first_principle IS 'Core "why" driving the student';
COMMENT ON COLUMN profiles.narrative_themes IS 'Key recurring themes identified';
COMMENT ON COLUMN profiles.last_activity_at IS 'Last activity timestamp for silence detection';


-- -----------------------------------------------------------------------------
-- 7. AGENT STATE VERSIONS (ensure exists)
-- For rollback capability and state forensics
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.agent_state_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Profile reference
  profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,

  -- Agent identification
  agent TEXT NOT NULL,

  -- State snapshot
  state JSONB NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,

  -- Event tracking
  event_type TEXT,
  event_payload JSONB,

  -- Attribution
  created_by TEXT DEFAULT 'agent' CHECK (created_by IN ('agent', 'human', 'system')),
  rationale TEXT,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_state_versions_profile_agent ON agent_state_versions(profile_id, agent);
CREATE INDEX IF NOT EXISTS idx_state_versions_event ON agent_state_versions(event_type);
CREATE INDEX IF NOT EXISTS idx_state_versions_created ON agent_state_versions(created_at DESC);

-- Function to get next version
CREATE OR REPLACE FUNCTION get_next_version(p_profile_id UUID, p_agent TEXT)
RETURNS INTEGER AS $$
DECLARE
  next_version INTEGER;
BEGIN
  SELECT COALESCE(MAX(version), 0) + 1 INTO next_version
  FROM agent_state_versions
  WHERE profile_id = p_profile_id AND agent = p_agent;
  RETURN next_version;
END;
$$ LANGUAGE plpgsql;

-- Comment
COMMENT ON TABLE agent_state_versions IS 'Versioned state snapshots for agent rollback and forensics';


-- -----------------------------------------------------------------------------
-- 8. STUDENT TRACKING TABLES (for opportunities/awards tracking)
-- -----------------------------------------------------------------------------

-- Student opportunities tracking (extends student_applications)
CREATE TABLE IF NOT EXISTS public.student_opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,

  -- Status
  status TEXT DEFAULT 'tracking' CHECK (status IN (
    'tracking',
    'applying',
    'submitted',
    'accepted',
    'rejected',
    'withdrawn'
  )),

  -- Agent predictions
  fit_score FLOAT,
  predicted_acceptance FLOAT,

  -- Tracking
  added_at TIMESTAMPTZ DEFAULT NOW(),
  deadline_reminder_sent BOOLEAN DEFAULT false,

  -- Notes
  notes TEXT,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT unique_student_opportunity UNIQUE(profile_id, opportunity_id)
);

-- Student awards tracking
CREATE TABLE IF NOT EXISTS public.student_awards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  award_id UUID NOT NULL REFERENCES awards(id) ON DELETE CASCADE,

  -- Status
  status TEXT DEFAULT 'tracking' CHECK (status IN (
    'tracking',
    'applying',
    'submitted',
    'won',
    'rejected',
    'withdrawn'
  )),

  -- Agent predictions
  win_probability FLOAT,
  roi_score FLOAT,

  -- Tracking
  added_at TIMESTAMPTZ DEFAULT NOW(),
  deadline_reminder_sent BOOLEAN DEFAULT false,

  -- Notes
  notes TEXT,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT unique_student_award UNIQUE(profile_id, award_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_student_opportunities_profile ON student_opportunities(profile_id);
CREATE INDEX IF NOT EXISTS idx_student_opportunities_status ON student_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_student_awards_profile ON student_awards(profile_id);
CREATE INDEX IF NOT EXISTS idx_student_awards_status ON student_awards(status);

-- RLS
ALTER TABLE student_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_awards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own opportunity tracking" ON student_opportunities
  FOR ALL USING (auth.uid() = profile_id);

CREATE POLICY "Users can manage own award tracking" ON student_awards
  FOR ALL USING (auth.uid() = profile_id);


-- -----------------------------------------------------------------------------
-- 9. VIEW: Agent Dashboard Summary
-- Aggregates agent-related data for monitoring
-- -----------------------------------------------------------------------------

-- Drop existing view first (may exist from migration 015)
DROP VIEW IF EXISTS public.v_agent_student_profile;

CREATE VIEW public.v_agent_student_profile AS
SELECT
  p.id as profile_id,
  p.email,
  p.first_name,
  p.last_name,
  p.grade,

  -- Narrative status
  p.narrative_brand_statement IS NOT NULL as has_narrative,
  p.narrative_confidence,
  p.narrative_updated_at,

  -- Activity status
  p.last_activity_at,
  EXTRACT(days FROM NOW() - p.last_activity_at) as days_since_activity,

  -- Workflow status
  (SELECT COUNT(*) FROM workflow_state ws WHERE ws.profile_id = p.id AND ws.enabled = true) as active_workflows,

  -- Tracking counts
  (SELECT COUNT(*) FROM student_opportunities so WHERE so.profile_id = p.id AND so.status = 'tracking') as tracked_opportunities,
  (SELECT COUNT(*) FROM student_awards sa WHERE sa.profile_id = p.id AND sa.status = 'tracking') as tracked_awards,

  -- Notification count
  (SELECT COUNT(*) FROM notifications n WHERE n.profile_id = p.id AND n.read = false) as unread_notifications

FROM profiles p
WHERE p.role = 'student';


-- -----------------------------------------------------------------------------
-- COMPLETE
-- -----------------------------------------------------------------------------

-- Verify new tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'evaluation_golden',
  'evaluation_runs',
  'workflow_state',
  'notifications',
  'coach_tasks',
  'agent_state_versions',
  'student_opportunities',
  'student_awards'
)
ORDER BY table_name;
