-- ============================================
-- EC Agent Minimal Plumbing - Projects & Nudge Queue
-- Phase 3 v9.1 - Execution Tracking Infrastructure
-- ============================================
-- This migration:
-- 1. Creates/updates projects table for execution tracking
-- 2. Creates nudge_queue table for proactive engagement
-- 3. Creates upcoming_deadlines view for deadline tracking
-- ============================================

-- ============================================
-- PROJECTS TABLE - If not exists, create it
-- If exists, this is a no-op
-- ============================================
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,  -- References profiles(id)
    name TEXT NOT NULL,
    category TEXT,  -- 'award', 'summer_program', 'ec_goal', 'ec', 'essay', 'academic'
    status TEXT DEFAULT 'active',  -- 'active', 'completed', 'stalled', 'dropped', 'blocked'
    deadline TIMESTAMPTZ,
    last_update TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),  -- For stall detection
    notes TEXT,
    source TEXT,  -- 'game_plan', 'manual', 'agent_suggested'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Optional: For detailed tracking
    target_end_date DATE,
    type TEXT  -- Alternative categorization
);

-- Indexes for projects table
CREATE INDEX IF NOT EXISTS idx_projects_profile_id ON projects(profile_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_deadline ON projects(deadline) WHERE deadline IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_projects_last_update ON projects(last_update DESC);
CREATE INDEX IF NOT EXISTS idx_projects_source ON projects(source);
CREATE INDEX IF NOT EXISTS idx_projects_category ON projects(category);

-- ============================================
-- PROJECT_STEPS TABLE - For microstep tracking
-- ============================================
CREATE TABLE IF NOT EXISTS project_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'skipped'
    due_date DATE,
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_steps_project ON project_steps(project_id);
CREATE INDEX IF NOT EXISTS idx_project_steps_status ON project_steps(status);

-- ============================================
-- NUDGE_QUEUE TABLE - For proactive engagement
-- ============================================
CREATE TABLE IF NOT EXISTS nudge_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,  -- References profiles(id)
    nudge_type TEXT NOT NULL,  -- 'deadline_reminder', 'stall_check', 'check_in', 'celebration'
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    priority TEXT DEFAULT 'medium',  -- 'high', 'medium', 'low'
    message_draft TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'delivered', 'dismissed', 'expired'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ
);

-- Indexes for nudge_queue
CREATE INDEX IF NOT EXISTS idx_nudge_queue_profile_status ON nudge_queue(profile_id, status);
CREATE INDEX IF NOT EXISTS idx_nudge_queue_created ON nudge_queue(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_nudge_queue_priority ON nudge_queue(priority);
CREATE INDEX IF NOT EXISTS idx_nudge_queue_pending ON nudge_queue(status) WHERE status = 'pending';

-- ============================================
-- UPCOMING_DEADLINES VIEW - For deadline tracking
-- ============================================
CREATE OR REPLACE VIEW upcoming_deadlines AS
SELECT
    p.id as project_id,
    p.profile_id,
    p.name,
    p.category,
    p.deadline,
    p.status,
    EXTRACT(DAY FROM (p.deadline - NOW())) as days_until,
    CASE
        WHEN EXTRACT(DAY FROM (p.deadline - NOW())) <= 1 THEN 'critical'
        WHEN EXTRACT(DAY FROM (p.deadline - NOW())) <= 3 THEN 'urgent'
        WHEN EXTRACT(DAY FROM (p.deadline - NOW())) <= 7 THEN 'soon'
        ELSE 'normal'
    END as urgency,
    p.source,
    p.metadata
FROM projects p
WHERE p.status = 'active'
  AND p.deadline IS NOT NULL
  AND p.deadline > NOW()
ORDER BY p.deadline ASC;

-- ============================================
-- STALLED_PROJECTS VIEW - For stall detection
-- ============================================
CREATE OR REPLACE VIEW stalled_projects AS
SELECT
    p.id as project_id,
    p.profile_id,
    p.name,
    p.category,
    p.status,
    p.last_update,
    p.last_activity_at,
    EXTRACT(DAY FROM (NOW() - COALESCE(p.last_activity_at, p.last_update, p.created_at))) as days_since_activity,
    CASE
        WHEN EXTRACT(DAY FROM (NOW() - COALESCE(p.last_activity_at, p.last_update, p.created_at))) >= 14 THEN 'severe'
        WHEN EXTRACT(DAY FROM (NOW() - COALESCE(p.last_activity_at, p.last_update, p.created_at))) >= 10 THEN 'moderate'
        WHEN EXTRACT(DAY FROM (NOW() - COALESCE(p.last_activity_at, p.last_update, p.created_at))) >= 5 THEN 'mild'
        ELSE 'none'
    END as stall_severity,
    p.metadata
FROM projects p
WHERE p.status = 'active'
  AND EXTRACT(DAY FROM (NOW() - COALESCE(p.last_activity_at, p.last_update, p.created_at))) >= 5
ORDER BY days_since_activity DESC;

-- ============================================
-- WEEKLY_PLANS TABLE - For P0/P1/P2 planning
-- ============================================
CREATE TABLE IF NOT EXISTS weekly_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    p0_tasks JSONB DEFAULT '[]',  -- Must complete
    p1_tasks JSONB DEFAULT '[]',  -- Should complete
    p2_tasks JSONB DEFAULT '[]',  -- If time permits
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    generated_by TEXT DEFAULT 'execution_agent',
    notes TEXT,

    -- Unique constraint per profile per week
    CONSTRAINT weekly_plans_profile_week_unique UNIQUE (profile_id, week_start)
);

CREATE INDEX IF NOT EXISTS idx_weekly_plans_profile ON weekly_plans(profile_id);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_week ON weekly_plans(week_start DESC);

-- ============================================
-- HELPER FUNCTION: Update last_activity_at on project changes
-- ============================================
CREATE OR REPLACE FUNCTION update_project_last_activity()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the parent project's last_activity_at when a step is modified
    IF TG_TABLE_NAME = 'project_steps' AND TG_OP IN ('INSERT', 'UPDATE') THEN
        UPDATE projects
        SET last_activity_at = NOW(), last_update = NOW()
        WHERE id = NEW.project_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for project_steps changes
DROP TRIGGER IF EXISTS trigger_update_project_activity ON project_steps;
CREATE TRIGGER trigger_update_project_activity
    AFTER INSERT OR UPDATE ON project_steps
    FOR EACH ROW
    EXECUTE FUNCTION update_project_last_activity();

-- ============================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE nudge_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_plans ENABLE ROW LEVEL SECURITY;

-- ============================================
-- GRANT PERMISSIONS
-- ============================================
GRANT SELECT, INSERT, UPDATE, DELETE ON projects TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON project_steps TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON nudge_queue TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON weekly_plans TO authenticated;

GRANT ALL ON projects TO service_role;
GRANT ALL ON project_steps TO service_role;
GRANT ALL ON nudge_queue TO service_role;
GRANT ALL ON weekly_plans TO service_role;

-- Grant access to views
GRANT SELECT ON upcoming_deadlines TO authenticated;
GRANT SELECT ON stalled_projects TO authenticated;
GRANT SELECT ON upcoming_deadlines TO service_role;
GRANT SELECT ON stalled_projects TO service_role;

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================
COMMENT ON TABLE projects IS 'EC Agent: Projects for execution tracking from game plans';
COMMENT ON TABLE project_steps IS 'EC Agent: Microsteps for projects';
COMMENT ON TABLE nudge_queue IS 'EC Agent: Queue for proactive nudges (deadline reminders, stall checks)';
COMMENT ON TABLE weekly_plans IS 'EC Agent: Weekly P0/P1/P2 prioritization plans';
COMMENT ON VIEW upcoming_deadlines IS 'EC Agent: View of active projects with upcoming deadlines';
COMMENT ON VIEW stalled_projects IS 'EC Agent: View of projects that have stalled (5+ days no activity)';
