-- =====================================================
-- IvyQuest v10.0 Migration 008: Projects Table
-- Supports Execution Agent: scaffoldProject(), EDS calculation
-- =====================================================
-- Features: Strategic Overwhelm (1.4x), microstep tracking,
-- blocker detection, Talk-First-Write-Second
-- =====================================================

CREATE TYPE project_status AS ENUM (
  'planning',     -- In planning phase
  'active',       -- Currently being executed
  'paused',       -- Temporarily paused (blocker or capacity)
  'blocked',      -- Has a blocking issue
  'completed',    -- Successfully completed
  'abandoned'     -- Abandoned (counts toward EDS)
);

CREATE TYPE project_type AS ENUM (
  'extracurricular',  -- EC activity
  'research',         -- Research project
  'community',        -- Community service
  'competition',      -- Competition prep
  'award',           -- Award application
  'opportunity',     -- Opportunity application
  'essay',           -- Essay writing
  'startup',         -- Entrepreneurial venture
  'creative',        -- Creative project
  'other'
);

CREATE TYPE step_status AS ENUM (
  'pending',      -- Not started
  'in_progress',  -- Currently working on
  'completed',    -- Done
  'skipped',      -- Intentionally skipped (stretch goal)
  'missed',       -- Missed deadline (counts toward EDS)
  'blocked'       -- Blocked by external factor
);

-- Main projects table
CREATE TABLE IF NOT EXISTS projects (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  -- Profile reference
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Project details
  name TEXT NOT NULL,
  description TEXT,
  type project_type DEFAULT 'extracurricular',
  status project_status DEFAULT 'planning',

  -- Timeline
  target_start_date DATE,
  target_end_date DATE,
  actual_start_date DATE,
  actual_end_date DATE,

  -- Agent-generated structure
  scaffolded_by TEXT DEFAULT 'agent', -- 'agent', 'user', 'coach'
  scaffold_version INTEGER DEFAULT 1,

  -- Strategic Overwhelm tracking (ACP-004)
  base_step_count INTEGER, -- Original step count
  overwhelm_step_count INTEGER, -- After 1.4x inflation
  overwhelm_factor FLOAT DEFAULT 1.4,

  -- Step summary (denormalized for quick access)
  total_steps INTEGER DEFAULT 0,
  completed_steps INTEGER DEFAULT 0,
  missed_steps INTEGER DEFAULT 0,
  completion_rate FLOAT GENERATED ALWAYS AS (
    CASE WHEN total_steps > 0 THEN completed_steps::FLOAT / total_steps ELSE 0 END
  ) STORED,

  -- Touchpoints (Multi-Touchpoint Leverage - ACP-005)
  touchpoints JSONB DEFAULT '[]', -- ['club', 'essay', 'recommendation', ...]
  touchpoint_count INTEGER DEFAULT 0,

  -- Activity tracking for blocker detection
  last_activity_at TIMESTAMPTZ DEFAULT NOW(),
  days_since_activity INTEGER GENERATED ALWAYS AS (
    EXTRACT(DAY FROM NOW() - last_activity_at)::INTEGER
  ) STORED,

  -- Talk-First-Write-Second (ACP-007)
  has_voice_notes BOOLEAN DEFAULT false,
  voice_notes JSONB DEFAULT '[]', -- [{transcript, timestamp, duration}]

  -- Impact metrics
  impact_description TEXT,
  quantified_impact JSONB DEFAULT '{}', -- {people_reached, funds_raised, hours_contributed}

  -- Narrative connection
  narrative_connection TEXT, -- How this connects to Narrative DNA
  identity_seed_id UUID, -- If this project was planted as an Identity Seed

  -- Metadata
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project steps (microsteps)
CREATE TABLE IF NOT EXISTS project_steps (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

  -- Step details
  title TEXT NOT NULL,
  description TEXT,
  step_order INTEGER NOT NULL, -- Order in the project
  status step_status DEFAULT 'pending',

  -- Timing
  target_date DATE,
  completed_at TIMESTAMPTZ,
  days_delayed INTEGER DEFAULT 0, -- Days past target (for EDS)

  -- Difficulty weighting (for EDS calculation)
  difficulty FLOAT DEFAULT 1.0 CHECK (difficulty >= 0.1 AND difficulty <= 3.0),
  estimated_hours FLOAT,
  actual_hours FLOAT,

  -- Step classification
  is_stretch_goal BOOLEAN DEFAULT false, -- Part of Strategic Overwhelm
  is_milestone BOOLEAN DEFAULT false, -- Major milestone
  is_blocking BOOLEAN DEFAULT false, -- Blocks other steps

  -- Dependencies
  depends_on UUID[], -- Array of step IDs this depends on
  blocks UUID[], -- Array of step IDs this blocks

  -- Templates and resources
  template_id TEXT, -- Reference to step template
  resources JSONB DEFAULT '[]', -- [{type, url, description}]

  -- Notes
  notes TEXT,
  blocker_description TEXT, -- If blocked, what's the blocker?

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_projects_profile ON projects(profile_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_type ON projects(type);
CREATE INDEX IF NOT EXISTS idx_projects_last_activity ON projects(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_project_steps_project ON project_steps(project_id);
CREATE INDEX IF NOT EXISTS idx_project_steps_status ON project_steps(status);
CREATE INDEX IF NOT EXISTS idx_project_steps_target_date ON project_steps(target_date);

-- Triggers
CREATE TRIGGER update_projects_updated_at
  BEFORE UPDATE ON projects
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_steps_updated_at
  BEFORE UPDATE ON project_steps
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Function to update project stats when steps change
CREATE OR REPLACE FUNCTION update_project_stats()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE projects SET
    total_steps = (SELECT COUNT(*) FROM project_steps WHERE project_id = COALESCE(NEW.project_id, OLD.project_id)),
    completed_steps = (SELECT COUNT(*) FROM project_steps WHERE project_id = COALESCE(NEW.project_id, OLD.project_id) AND status = 'completed'),
    missed_steps = (SELECT COUNT(*) FROM project_steps WHERE project_id = COALESCE(NEW.project_id, OLD.project_id) AND status = 'missed'),
    last_activity_at = NOW()
  WHERE id = COALESCE(NEW.project_id, OLD.project_id);

  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER project_steps_stats_update
  AFTER INSERT OR UPDATE OR DELETE ON project_steps
  FOR EACH ROW
  EXECUTE FUNCTION update_project_stats();

-- Function to calculate EDS for a profile
CREATE OR REPLACE FUNCTION calculate_eds(p_profile_id UUID)
RETURNS FLOAT AS $$
DECLARE
  v_eds FLOAT;
BEGIN
  SELECT COALESCE(SUM(
    CASE WHEN ps.status = 'missed' THEN
      ps.days_delayed * ps.difficulty
    ELSE 0 END
  ), 0)
  INTO v_eds
  FROM projects p
  JOIN project_steps ps ON p.id = ps.project_id
  WHERE p.profile_id = p_profile_id;

  -- Update profile with new EDS
  UPDATE profiles SET
    execution_debt = v_eds,
    execution_debt_updated_at = NOW()
  WHERE id = p_profile_id;

  RETURN v_eds;
END;
$$ LANGUAGE plpgsql;

-- Function to detect blocked projects (>5 days inactivity)
CREATE OR REPLACE FUNCTION detect_blocked_projects()
RETURNS TABLE (
  project_id UUID,
  profile_id UUID,
  project_name TEXT,
  days_inactive INTEGER,
  current_status project_status
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    p.id as project_id,
    p.profile_id,
    p.name as project_name,
    p.days_since_activity as days_inactive,
    p.status as current_status
  FROM projects p
  WHERE p.status IN ('active', 'planning')
    AND p.days_since_activity >= 5
  ORDER BY p.days_since_activity DESC;
END;
$$ LANGUAGE plpgsql;

-- Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_steps ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Allow project access" ON projects FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow step access" ON project_steps FOR ALL USING (true) WITH CHECK (true);

-- View for stalled projects (for Execution Agent monitoring)
CREATE OR REPLACE VIEW stalled_projects AS
SELECT
  p.id as project_id,
  p.profile_id,
  pr.name as student_name,
  p.name as project_name,
  p.type,
  p.status,
  p.days_since_activity,
  p.completion_rate,
  p.total_steps,
  p.completed_steps,
  p.missed_steps
FROM projects p
JOIN profiles pr ON p.profile_id = pr.id
WHERE p.status IN ('active', 'planning', 'blocked')
  AND p.days_since_activity >= 5
ORDER BY p.days_since_activity DESC;

-- View for project dashboard
CREATE OR REPLACE VIEW project_dashboard AS
SELECT
  p.profile_id,
  COUNT(*) as total_projects,
  COUNT(*) FILTER (WHERE p.status = 'completed') as completed_projects,
  COUNT(*) FILTER (WHERE p.status = 'active') as active_projects,
  COUNT(*) FILTER (WHERE p.status = 'blocked') as blocked_projects,
  AVG(p.completion_rate) as avg_completion_rate,
  SUM(p.touchpoint_count) as total_touchpoints
FROM projects p
GROUP BY p.profile_id;

-- Comments
COMMENT ON TABLE projects IS 'Student projects tracked by Execution Agent (v10.0)';
COMMENT ON TABLE project_steps IS 'Microsteps within projects for Strategic Overwhelm (ACP-004)';
COMMENT ON COLUMN projects.overwhelm_factor IS 'Strategic Overwhelm: assign 1.4x tasks, expect 73% completion';
COMMENT ON COLUMN project_steps.difficulty IS 'EDS weight: higher difficulty = more debt if missed';
COMMENT ON FUNCTION calculate_eds IS 'Compute Execution Debt Score: sum(missed_steps * days_delayed * difficulty)';
COMMENT ON FUNCTION detect_blocked_projects IS 'Find projects with >5 days inactivity for intervention';

-- =====================================================
-- ROLLBACK
-- =====================================================
-- DROP VIEW IF EXISTS project_dashboard;
-- DROP VIEW IF EXISTS stalled_projects;
-- DROP FUNCTION IF EXISTS detect_blocked_projects();
-- DROP FUNCTION IF EXISTS calculate_eds(UUID);
-- DROP TRIGGER IF EXISTS project_steps_stats_update ON project_steps;
-- DROP FUNCTION IF EXISTS update_project_stats();
-- DROP TRIGGER IF EXISTS update_project_steps_updated_at ON project_steps;
-- DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
-- DROP TABLE IF EXISTS project_steps;
-- DROP TABLE IF EXISTS projects;
-- DROP TYPE IF EXISTS step_status;
-- DROP TYPE IF EXISTS project_type;
-- DROP TYPE IF EXISTS project_status;
