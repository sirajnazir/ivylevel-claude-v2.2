-- ============================================================
-- IvyQuest v10.0 - Proactive Autonomy Tables
-- ============================================================
-- Adds missing tables for proactive coaching capabilities:
-- - nudge_queue: Proactive nudges for students
-- - proactive_notifications: Autonomous notifications
-- - student_outcomes: Track real outcomes (wins, completions)
-- - autonomous_reasoning_cycles: Log reasoning cycles for learning
-- - coaching_assets: Jenny's coaching techniques with effectiveness
-- ============================================================

-- ============================================================
-- 1. NUDGE QUEUE TABLE
-- Proactive nudges queued by scheduler jobs
-- ============================================================

CREATE TABLE IF NOT EXISTS nudge_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    nudge_type TEXT NOT NULL CHECK (nudge_type IN (
        'deadline_reminder', 'stall_check', 'check_in',
        'opportunity_match', 'eds_threshold', 'celebration',
        'weekly_summary', 'goal_progress'
    )),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    message_draft TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'delivered', 'dismissed', 'expired')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

-- Indexes for nudge_queue
CREATE INDEX IF NOT EXISTS idx_nudge_queue_profile ON nudge_queue(profile_id);
CREATE INDEX IF NOT EXISTS idx_nudge_queue_pending ON nudge_queue(profile_id, status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_nudge_queue_type ON nudge_queue(nudge_type);
CREATE INDEX IF NOT EXISTS idx_nudge_queue_priority ON nudge_queue(priority);
CREATE INDEX IF NOT EXISTS idx_nudge_queue_created ON nudge_queue(created_at DESC);

-- ============================================================
-- 2. PROACTIVE NOTIFICATIONS TABLE
-- Autonomous notifications from reasoning cycles
-- ============================================================

CREATE TABLE IF NOT EXISTS proactive_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL DEFAULT 'autonomous_monitor',
    notification_type TEXT NOT NULL CHECK (notification_type IN (
        'proactive', 'deadline_alert', 'opportunity_match',
        'celebration', 'check_in', 'goal_reminder', 'insight'
    )),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    urgency TEXT DEFAULT 'normal' CHECK (urgency IN ('low', 'normal', 'high', 'critical')),
    related_asset_id UUID,
    related_data JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'viewed', 'acted', 'dismissed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    viewed_at TIMESTAMPTZ,
    acted_at TIMESTAMPTZ
);

-- Indexes for proactive_notifications
CREATE INDEX IF NOT EXISTS idx_proactive_notifications_profile ON proactive_notifications(profile_id);
CREATE INDEX IF NOT EXISTS idx_proactive_notifications_pending ON proactive_notifications(profile_id, status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_proactive_notifications_type ON proactive_notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_proactive_notifications_created ON proactive_notifications(created_at DESC);

-- ============================================================
-- 3. STUDENT OUTCOMES TABLE
-- Track actual outcomes (wins, completions, rejections)
-- ============================================================

CREATE TABLE IF NOT EXISTS student_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    outcome_type TEXT NOT NULL CHECK (outcome_type IN (
        'award_win', 'award_loss', 'program_accepted', 'program_rejected',
        'goal_completed', 'goal_abandoned', 'project_completed',
        'skill_mastered', 'milestone_achieved', 'custom'
    )),
    outcome_data JSONB NOT NULL DEFAULT '{}',
    -- Linkage to what contributed to this outcome
    related_asset_ids TEXT[] DEFAULT '{}',  -- coaching assets that helped
    related_goal_id UUID,
    related_project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    -- For learning what works
    contributing_factors JSONB DEFAULT '{}',
    student_reflection TEXT,
    agent_analysis TEXT,
    -- Timestamps
    outcome_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for student_outcomes
CREATE INDEX IF NOT EXISTS idx_student_outcomes_profile ON student_outcomes(profile_id);
CREATE INDEX IF NOT EXISTS idx_student_outcomes_type ON student_outcomes(outcome_type);
CREATE INDEX IF NOT EXISTS idx_student_outcomes_date ON student_outcomes(outcome_date DESC);

-- ============================================================
-- 4. AUTONOMOUS REASONING CYCLES TABLE
-- Log each reasoning cycle for debugging and learning
-- ============================================================

CREATE TABLE IF NOT EXISTS autonomous_reasoning_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL DEFAULT 'autonomous_monitor',
    trigger_event TEXT NOT NULL, -- 'scheduled', 'activity', 'request', 'deadline', etc.
    -- State at cycle start
    monitoring_state JSONB DEFAULT '{}',
    -- Reasoning outputs
    predictions JSONB DEFAULT '[]',
    decisions JSONB DEFAULT '{}',
    -- Actions taken
    actions_taken JSONB DEFAULT '{}',
    notification_sent BOOLEAN DEFAULT FALSE,
    -- Learning feedback
    learnings JSONB DEFAULT '{}',
    -- Timing
    cycle_start TIMESTAMPTZ,
    cycle_end TIMESTAMPTZ,
    duration_ms INT,
    -- Errors if any
    errors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for autonomous_reasoning_cycles
CREATE INDEX IF NOT EXISTS idx_reasoning_cycles_profile ON autonomous_reasoning_cycles(profile_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_cycles_trigger ON autonomous_reasoning_cycles(trigger_event);
CREATE INDEX IF NOT EXISTS idx_reasoning_cycles_created ON autonomous_reasoning_cycles(created_at DESC);

-- ============================================================
-- 5. COACHING ASSETS TABLE
-- Jenny's coaching techniques with effectiveness tracking
-- ============================================================

CREATE TABLE IF NOT EXISTS coaching_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK (category IN (
        'technique', 'response_pattern', 'reframe', 'question',
        'celebration', 'nudge', 'crisis_response', 'story'
    )),
    description TEXT,
    content TEXT NOT NULL,
    -- Applicability
    applicable_archetypes TEXT[] DEFAULT '{}',
    applicable_situations TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    -- Effectiveness tracking
    times_used INT DEFAULT 0,
    success_count INT DEFAULT 0,
    effectiveness_score FLOAT DEFAULT 0.5 CHECK (effectiveness_score >= 0 AND effectiveness_score <= 1),
    -- Source
    source TEXT DEFAULT 'jenny', -- 'jenny', 'generated', 'human'
    -- Active/disabled
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for coaching_assets
CREATE INDEX IF NOT EXISTS idx_coaching_assets_category ON coaching_assets(category);
CREATE INDEX IF NOT EXISTS idx_coaching_assets_effectiveness ON coaching_assets(effectiveness_score DESC);
CREATE INDEX IF NOT EXISTS idx_coaching_assets_active ON coaching_assets(is_active) WHERE is_active = TRUE;

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_coaching_assets_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_coaching_assets_updated_at ON coaching_assets;
CREATE TRIGGER trigger_coaching_assets_updated_at
    BEFORE UPDATE ON coaching_assets
    FOR EACH ROW
    EXECUTE FUNCTION update_coaching_assets_updated_at();

-- ============================================================
-- 6. TECHNIQUE EFFECTIVENESS TABLE
-- Track which techniques work for which archetypes
-- ============================================================

CREATE TABLE IF NOT EXISTS technique_effectiveness (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES coaching_assets(id) ON DELETE CASCADE,
    archetype TEXT NOT NULL,
    situation_type TEXT,
    -- Tracking
    times_used INT DEFAULT 0,
    success_count INT DEFAULT 0,
    effectiveness_rate FLOAT GENERATED ALWAYS AS (
        CASE WHEN times_used > 0 THEN success_count::FLOAT / times_used ELSE 0 END
    ) STORED,
    -- Statistical confidence
    confidence FLOAT DEFAULT 0.0, -- increases with more data points
    -- Learning
    learnings JSONB DEFAULT '[]',
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- Unique per asset/archetype/situation
    UNIQUE (asset_id, archetype, situation_type)
);

-- Indexes for technique_effectiveness
CREATE INDEX IF NOT EXISTS idx_technique_effectiveness_asset ON technique_effectiveness(asset_id);
CREATE INDEX IF NOT EXISTS idx_technique_effectiveness_archetype ON technique_effectiveness(archetype);
CREATE INDEX IF NOT EXISTS idx_technique_effectiveness_rate ON technique_effectiveness(effectiveness_rate DESC);

-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Get pending nudges for a profile (sorted by priority)
CREATE OR REPLACE FUNCTION get_pending_nudges(
    p_profile_id UUID,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    nudge_type TEXT,
    project_id UUID,
    priority TEXT,
    message_draft TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE sql
STABLE
AS $$
    SELECT id, nudge_type, project_id, priority, message_draft, metadata, created_at
    FROM nudge_queue
    WHERE profile_id = p_profile_id
      AND status = 'pending'
      AND (expires_at IS NULL OR expires_at > NOW())
    ORDER BY
        CASE priority
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END,
        created_at
    LIMIT p_limit;
$$;

-- Update coaching asset effectiveness after an outcome
CREATE OR REPLACE FUNCTION update_asset_effectiveness(
    p_asset_id UUID,
    p_archetype TEXT,
    p_situation_type TEXT,
    p_was_successful BOOLEAN
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Upsert technique effectiveness record
    INSERT INTO technique_effectiveness (
        asset_id, archetype, situation_type, times_used, success_count, last_used_at, updated_at
    )
    VALUES (
        p_asset_id,
        p_archetype,
        p_situation_type,
        1,
        CASE WHEN p_was_successful THEN 1 ELSE 0 END,
        NOW(),
        NOW()
    )
    ON CONFLICT (asset_id, archetype, situation_type)
    DO UPDATE SET
        times_used = technique_effectiveness.times_used + 1,
        success_count = technique_effectiveness.success_count + CASE WHEN p_was_successful THEN 1 ELSE 0 END,
        confidence = LEAST(1.0, (technique_effectiveness.times_used + 1) / 20.0), -- 20 uses = full confidence
        last_used_at = NOW(),
        updated_at = NOW();

    -- Also update the overall asset statistics
    UPDATE coaching_assets
    SET
        times_used = times_used + 1,
        success_count = success_count + CASE WHEN p_was_successful THEN 1 ELSE 0 END,
        effectiveness_score = (success_count + CASE WHEN p_was_successful THEN 1 ELSE 0 END)::FLOAT / (times_used + 1),
        updated_at = NOW()
    WHERE id = p_asset_id;
END;
$$;

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

-- Enable RLS
ALTER TABLE nudge_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE proactive_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE autonomous_reasoning_cycles ENABLE ROW LEVEL SECURITY;
ALTER TABLE coaching_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE technique_effectiveness ENABLE ROW LEVEL SECURITY;

-- Policies (permissive for MVP, tighten for production)
CREATE POLICY "nudge_queue_all_access" ON nudge_queue FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "proactive_notifications_all_access" ON proactive_notifications FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "student_outcomes_all_access" ON student_outcomes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "reasoning_cycles_all_access" ON autonomous_reasoning_cycles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "coaching_assets_all_access" ON coaching_assets FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "technique_effectiveness_all_access" ON technique_effectiveness FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON nudge_queue TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON proactive_notifications TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON student_outcomes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON autonomous_reasoning_cycles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON coaching_assets TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON technique_effectiveness TO authenticated;

GRANT ALL ON nudge_queue TO service_role;
GRANT ALL ON proactive_notifications TO service_role;
GRANT ALL ON student_outcomes TO service_role;
GRANT ALL ON autonomous_reasoning_cycles TO service_role;
GRANT ALL ON coaching_assets TO service_role;
GRANT ALL ON technique_effectiveness TO service_role;

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE nudge_queue IS 'v10.0 Proactive nudges queued by scheduler for delivery to students';
COMMENT ON TABLE proactive_notifications IS 'v10.0 Autonomous notifications from reasoning cycles';
COMMENT ON TABLE student_outcomes IS 'v10.0 Track actual outcomes (wins, completions) for learning';
COMMENT ON TABLE autonomous_reasoning_cycles IS 'v10.0 Log each autonomous reasoning cycle for debugging and learning';
COMMENT ON TABLE coaching_assets IS 'v10.0 Jennys coaching techniques with effectiveness tracking';
COMMENT ON TABLE technique_effectiveness IS 'v10.0 Track which techniques work for which archetypes';

COMMENT ON FUNCTION get_pending_nudges IS 'Get pending nudges for a profile, sorted by priority';
COMMENT ON FUNCTION update_asset_effectiveness IS 'Update coaching asset effectiveness after an outcome';

-- ============================================================
-- Migration Complete
-- ============================================================

DO $$
BEGIN
    RAISE NOTICE 'v10.0 Proactive Autonomy tables created successfully:';
    RAISE NOTICE '  - nudge_queue';
    RAISE NOTICE '  - proactive_notifications';
    RAISE NOTICE '  - student_outcomes';
    RAISE NOTICE '  - autonomous_reasoning_cycles';
    RAISE NOTICE '  - coaching_assets';
    RAISE NOTICE '  - technique_effectiveness';
END $$;
