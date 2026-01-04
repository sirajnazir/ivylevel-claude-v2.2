-- =====================================================
-- IvyQuest v10.0 Migration 004: Crises Table
-- MIGRATE-003: Create crises table for Crisis Alchemy (ACP-003)
-- =====================================================
-- Supports: 4-step Crisis Alchemy Protocol
-- Step 1: Validate (2s) - Acknowledge emotion
-- Step 2: Act (10s) - Micro-action to restore agency
-- Step 3: Reframe (30s) - Find opportunity angle
-- Step 4: Create (2min) - Design new activity/pivot
-- =====================================================

-- Create enums for crisis management
CREATE TYPE crisis_status AS ENUM (
  'detected',    -- Crisis identified by agent
  'proposed',    -- Agent has proposed response (awaiting HITL)
  'approved',    -- Human coach approved the response
  'rejected',    -- Human coach rejected, needs manual handling
  'in_progress', -- Crisis response being executed
  'resolved',    -- Crisis successfully converted to opportunity
  'escalated'    -- Requires immediate human intervention
);

CREATE TYPE crisis_type AS ENUM (
  'blocker',      -- Project/task blocker preventing progress
  'rejection',    -- Award/opportunity rejection
  'conflict',     -- Interpersonal or family conflict
  'deadline',     -- Missed or at-risk deadline
  'motivation',   -- Loss of motivation or burnout
  'academic',     -- Grade drop or academic setback
  'external',     -- External circumstances (family, health, etc.)
  'opportunity'   -- Missed opportunity that could be recovered
);

CREATE TYPE crisis_urgency AS ENUM (
  'low',       -- Can wait 1+ weeks
  'medium',    -- Should address within a week
  'high',      -- Needs attention within 48 hours
  'critical'   -- Requires immediate intervention (<24 hours)
);

-- Create crises table
CREATE TABLE IF NOT EXISTS crises (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  -- Link to profile
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Crisis identification
  type crisis_type NOT NULL,
  urgency crisis_urgency DEFAULT 'medium',
  status crisis_status DEFAULT 'detected',

  -- Crisis details
  title TEXT NOT NULL,
  description TEXT,
  detected_by TEXT DEFAULT 'agent', -- 'agent', 'user', 'coach'
  detection_source TEXT, -- e.g., 'inactivity_5_days', 'user_report', 'deadline_miss'

  -- Crisis Alchemy Protocol Steps (stored as crisis progresses)
  step1_validation JSONB, -- {message, timestamp, emotion_acknowledged}
  step2_micro_action JSONB, -- {action, completed, timestamp}
  step3_reframe JSONB, -- {opportunity_angle, narrative_connection}
  step4_creation JSONB, -- {activity_name, description, first_step, touchpoints}

  -- Full proposed response (for HITL review)
  proposed_response JSONB, -- Complete Crisis Alchemy output

  -- Human-in-the-Loop (HITL) tracking
  requires_human_approval BOOLEAN DEFAULT false,
  approval_deadline TIMESTAMPTZ, -- <1hr per spec
  approved_by TEXT, -- Coach identifier
  approval_notes TEXT,
  approval_timestamp TIMESTAMPTZ,

  -- Resolution tracking
  resolution_time TIMESTAMPTZ,
  resolution_hours FLOAT, -- Time from detection to resolution
  outcome TEXT, -- What happened after resolution
  reframed_opportunity TEXT, -- The opportunity created from crisis

  -- Impact metrics
  converted_to_activity BOOLEAN DEFAULT false,
  activity_id UUID, -- Reference to created activity if applicable
  touchpoints_gained INTEGER DEFAULT 0,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_crises_profile ON crises(profile_id);
CREATE INDEX IF NOT EXISTS idx_crises_status ON crises(status);
CREATE INDEX IF NOT EXISTS idx_crises_urgency ON crises(urgency);
CREATE INDEX IF NOT EXISTS idx_crises_type ON crises(type);
CREATE INDEX IF NOT EXISTS idx_crises_requires_approval ON crises(requires_human_approval)
  WHERE requires_human_approval = true AND status = 'proposed';
CREATE INDEX IF NOT EXISTS idx_crises_approval_deadline ON crises(approval_deadline)
  WHERE status = 'proposed';

-- Trigger for updated_at
CREATE TRIGGER update_crises_updated_at
  BEFORE UPDATE ON crises
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate resolution hours on status change
CREATE OR REPLACE FUNCTION calculate_crisis_resolution_time()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
    NEW.resolution_time = NOW();
    NEW.resolution_hours = EXTRACT(EPOCH FROM (NOW() - NEW.created_at)) / 3600;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER crisis_resolution_time
  BEFORE UPDATE ON crises
  FOR EACH ROW
  EXECUTE FUNCTION calculate_crisis_resolution_time();

-- Enable RLS
ALTER TABLE crises ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Allow profile-based crisis access" ON crises
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- View for pending HITL approvals
CREATE OR REPLACE VIEW pending_crisis_approvals AS
SELECT
  c.id,
  c.profile_id,
  p.name as student_name,
  p.email as student_email,
  c.type,
  c.urgency,
  c.title,
  c.description,
  c.proposed_response,
  c.approval_deadline,
  c.created_at,
  EXTRACT(EPOCH FROM (c.approval_deadline - NOW())) / 60 as minutes_until_deadline
FROM crises c
JOIN profiles p ON c.profile_id = p.id
WHERE c.status = 'proposed'
  AND c.requires_human_approval = true
ORDER BY c.approval_deadline ASC;

-- Comments
COMMENT ON TABLE crises IS 'Crisis tracking for Crisis Alchemy Protocol (ACP-003)';
COMMENT ON COLUMN crises.step1_validation IS 'Step 1: Acknowledge emotion immediately (2 seconds)';
COMMENT ON COLUMN crises.step2_micro_action IS 'Step 2: One concrete micro-action to restore agency (10 seconds)';
COMMENT ON COLUMN crises.step3_reframe IS 'Step 3: Find the opportunity angle in the setback (30 seconds)';
COMMENT ON COLUMN crises.step4_creation IS 'Step 4: Design new activity or pivot from crisis (2 minutes)';
COMMENT ON COLUMN crises.approval_deadline IS 'HITL approval must happen within 1 hour per spec';
COMMENT ON COLUMN crises.resolution_hours IS 'Target: <72 hours. Huda benchmark: <2 hours';

-- =====================================================
-- ROLLBACK
-- =====================================================
-- DROP VIEW IF EXISTS pending_crisis_approvals;
-- DROP TRIGGER IF EXISTS crisis_resolution_time ON crises;
-- DROP FUNCTION IF EXISTS calculate_crisis_resolution_time();
-- DROP TRIGGER IF EXISTS update_crises_updated_at ON crises;
-- DROP POLICY IF EXISTS "Allow profile-based crisis access" ON crises;
-- DROP TABLE IF EXISTS crises;
-- DROP TYPE IF EXISTS crisis_urgency;
-- DROP TYPE IF EXISTS crisis_type;
-- DROP TYPE IF EXISTS crisis_status;
