-- =====================================================
-- IvyQuest v10.0 Migration 006: Agent State Versioning
-- MIGRATE-005: Create agent_state_versions for rollback/forensics
-- =====================================================
-- CRITICAL: Every agent state change MUST be versioned
-- Per v9.1: Enables rollback, A/B replay, and audit trails
-- Supports Human Shadow Mode override tracking
-- =====================================================

-- Create agent state versions table
CREATE TABLE IF NOT EXISTS agent_state_versions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  -- Profile reference
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Agent identification
  agent TEXT NOT NULL, -- 'Assessment', 'Execution', 'GamePlan', 'Awards', 'Opportunity'

  -- Version tracking
  version INTEGER NOT NULL,
  previous_version INTEGER, -- For chain tracking

  -- State snapshot (complete state at this version)
  state JSONB NOT NULL,

  -- State diff (optional, for efficient storage)
  state_diff JSONB, -- Only changes from previous version

  -- Event that triggered this version
  event_type TEXT NOT NULL, -- e.g., 'assessment_enhanced', 'crisis_resolved', 'gameplan_generated'
  event_payload JSONB, -- Original event data

  -- Provenance tracking
  created_by TEXT NOT NULL CHECK (created_by IN ('agent', 'human', 'system')),
  created_by_id TEXT, -- User ID or agent ID
  rationale TEXT, -- Why this change was made (especially for human overrides)

  -- Human-in-the-Loop tracking
  is_human_override BOOLEAN DEFAULT false,
  override_approved_by TEXT, -- Coach who approved
  override_reason TEXT,

  -- Rollback support
  is_rolled_back BOOLEAN DEFAULT false,
  rolled_back_to_version INTEGER,
  rollback_reason TEXT,
  rollback_timestamp TIMESTAMPTZ,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unique constraint on profile + agent + version
CREATE UNIQUE INDEX IF NOT EXISTS idx_state_versions_unique
  ON agent_state_versions(profile_id, agent, version);

-- Indexes for queries
CREATE INDEX IF NOT EXISTS idx_state_versions_profile ON agent_state_versions(profile_id);
CREATE INDEX IF NOT EXISTS idx_state_versions_agent ON agent_state_versions(agent);
CREATE INDEX IF NOT EXISTS idx_state_versions_event ON agent_state_versions(event_type);
CREATE INDEX IF NOT EXISTS idx_state_versions_created_by ON agent_state_versions(created_by);
CREATE INDEX IF NOT EXISTS idx_state_versions_human_override ON agent_state_versions(is_human_override)
  WHERE is_human_override = true;
CREATE INDEX IF NOT EXISTS idx_state_versions_created_at ON agent_state_versions(created_at DESC);

-- Function to get next version number
CREATE OR REPLACE FUNCTION get_next_version(
  p_profile_id UUID,
  p_agent TEXT
)
RETURNS INTEGER AS $$
DECLARE
  v_next_version INTEGER;
BEGIN
  SELECT COALESCE(MAX(version), 0) + 1
  INTO v_next_version
  FROM agent_state_versions
  WHERE profile_id = p_profile_id AND agent = p_agent;

  RETURN v_next_version;
END;
$$ LANGUAGE plpgsql;

-- Function to create a new state version
CREATE OR REPLACE FUNCTION create_state_version(
  p_profile_id UUID,
  p_agent TEXT,
  p_state JSONB,
  p_event_type TEXT,
  p_created_by TEXT DEFAULT 'agent',
  p_rationale TEXT DEFAULT NULL,
  p_event_payload JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_version_id UUID;
  v_version INTEGER;
  v_prev_version INTEGER;
  v_prev_state JSONB;
BEGIN
  -- Get next version number
  v_version := get_next_version(p_profile_id, p_agent);
  v_prev_version := v_version - 1;

  -- Get previous state for diff calculation
  IF v_prev_version > 0 THEN
    SELECT state INTO v_prev_state
    FROM agent_state_versions
    WHERE profile_id = p_profile_id
      AND agent = p_agent
      AND version = v_prev_version;
  END IF;

  -- Insert new version
  INSERT INTO agent_state_versions (
    profile_id,
    agent,
    version,
    previous_version,
    state,
    event_type,
    event_payload,
    created_by,
    rationale,
    is_human_override
  ) VALUES (
    p_profile_id,
    p_agent,
    v_version,
    CASE WHEN v_prev_version > 0 THEN v_prev_version ELSE NULL END,
    p_state,
    p_event_type,
    p_event_payload,
    p_created_by,
    p_rationale,
    p_created_by = 'human'
  )
  RETURNING id INTO v_version_id;

  RETURN v_version_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get state at a specific version
CREATE OR REPLACE FUNCTION get_state_at_version(
  p_profile_id UUID,
  p_agent TEXT,
  p_version INTEGER
)
RETURNS JSONB AS $$
DECLARE
  v_state JSONB;
BEGIN
  SELECT state INTO v_state
  FROM agent_state_versions
  WHERE profile_id = p_profile_id
    AND agent = p_agent
    AND version = p_version;

  RETURN v_state;
END;
$$ LANGUAGE plpgsql;

-- Function to get latest state
CREATE OR REPLACE FUNCTION get_latest_state(
  p_profile_id UUID,
  p_agent TEXT
)
RETURNS JSONB AS $$
DECLARE
  v_state JSONB;
BEGIN
  SELECT state INTO v_state
  FROM agent_state_versions
  WHERE profile_id = p_profile_id
    AND agent = p_agent
  ORDER BY version DESC
  LIMIT 1;

  RETURN v_state;
END;
$$ LANGUAGE plpgsql;

-- Function to rollback to a previous version
CREATE OR REPLACE FUNCTION rollback_to_version(
  p_profile_id UUID,
  p_agent TEXT,
  p_target_version INTEGER,
  p_reason TEXT
)
RETURNS UUID AS $$
DECLARE
  v_current_version INTEGER;
  v_target_state JSONB;
  v_new_version_id UUID;
BEGIN
  -- Get current version
  SELECT MAX(version) INTO v_current_version
  FROM agent_state_versions
  WHERE profile_id = p_profile_id AND agent = p_agent;

  IF v_current_version IS NULL OR p_target_version >= v_current_version THEN
    RAISE EXCEPTION 'Invalid rollback: target version must be less than current version';
  END IF;

  -- Get target state
  v_target_state := get_state_at_version(p_profile_id, p_agent, p_target_version);

  IF v_target_state IS NULL THEN
    RAISE EXCEPTION 'Target version % not found', p_target_version;
  END IF;

  -- Create new version with rolled back state
  v_new_version_id := create_state_version(
    p_profile_id,
    p_agent,
    v_target_state,
    'rollback',
    'system',
    p_reason
  );

  -- Mark the new version as a rollback
  UPDATE agent_state_versions
  SET
    is_rolled_back = false, -- This IS the rollback, not rolled back itself
    rolled_back_to_version = p_target_version,
    rollback_reason = p_reason,
    rollback_timestamp = NOW()
  WHERE id = v_new_version_id;

  RETURN v_new_version_id;
END;
$$ LANGUAGE plpgsql;

-- Enable RLS
ALTER TABLE agent_state_versions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Allow state version access" ON agent_state_versions
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- View for recent state changes (for monitoring dashboard)
CREATE OR REPLACE VIEW recent_state_changes AS
SELECT
  asv.id,
  asv.profile_id,
  p.name as student_name,
  asv.agent,
  asv.version,
  asv.event_type,
  asv.created_by,
  asv.is_human_override,
  asv.rationale,
  asv.created_at
FROM agent_state_versions asv
LEFT JOIN profiles p ON asv.profile_id = p.id
ORDER BY asv.created_at DESC
LIMIT 100;

-- View for human overrides (for audit)
CREATE OR REPLACE VIEW human_overrides AS
SELECT
  asv.id,
  asv.profile_id,
  p.name as student_name,
  asv.agent,
  asv.event_type,
  asv.override_approved_by,
  asv.override_reason,
  asv.rationale,
  asv.created_at
FROM agent_state_versions asv
LEFT JOIN profiles p ON asv.profile_id = p.id
WHERE asv.is_human_override = true
ORDER BY asv.created_at DESC;

-- Comments
COMMENT ON TABLE agent_state_versions IS 'Versioned state snapshots for all agent state changes (v10.0)';
COMMENT ON COLUMN agent_state_versions.version IS 'Incrementing version per profile+agent combination';
COMMENT ON COLUMN agent_state_versions.state IS 'Complete state snapshot at this version';
COMMENT ON COLUMN agent_state_versions.created_by IS 'agent=automated, human=HITL override, system=rollback';
COMMENT ON COLUMN agent_state_versions.is_human_override IS 'True if this change was a human override via HITL';
COMMENT ON FUNCTION create_state_version IS 'Create a new versioned state snapshot';
COMMENT ON FUNCTION rollback_to_version IS 'Rollback agent state to a previous version';

-- =====================================================
-- ROLLBACK
-- =====================================================
-- DROP VIEW IF EXISTS human_overrides;
-- DROP VIEW IF EXISTS recent_state_changes;
-- DROP FUNCTION IF EXISTS rollback_to_version(UUID, TEXT, INTEGER, TEXT);
-- DROP FUNCTION IF EXISTS get_latest_state(UUID, TEXT);
-- DROP FUNCTION IF EXISTS get_state_at_version(UUID, TEXT, INTEGER);
-- DROP FUNCTION IF EXISTS create_state_version(UUID, TEXT, JSONB, TEXT, TEXT, TEXT, JSONB);
-- DROP FUNCTION IF EXISTS get_next_version(UUID, TEXT);
-- DROP POLICY IF EXISTS "Allow state version access" ON agent_state_versions;
-- DROP TABLE IF EXISTS agent_state_versions;
