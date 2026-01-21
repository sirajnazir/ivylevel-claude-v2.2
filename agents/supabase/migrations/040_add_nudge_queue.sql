-- ============================================
-- EC Agent - Add Nudge Queue Table
-- Minimal migration for proactive engagement
-- ============================================

-- NUDGE_QUEUE TABLE - For proactive engagement
CREATE TABLE IF NOT EXISTS nudge_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    nudge_type TEXT NOT NULL,  -- 'deadline_reminder', 'stall_check', 'check_in', 'celebration'
    project_id UUID,  -- Optional reference to projects
    priority TEXT DEFAULT 'medium',  -- 'high', 'medium', 'low'
    message_draft TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'delivered', 'dismissed', 'expired'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ
);

-- Indexes for nudge_queue
CREATE INDEX IF NOT EXISTS idx_nudge_queue_profile_status ON nudge_queue(profile_id, status);
CREATE INDEX IF NOT EXISTS idx_nudge_queue_pending ON nudge_queue(status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_nudge_queue_created ON nudge_queue(created_at DESC);

-- Enable RLS
ALTER TABLE nudge_queue ENABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON nudge_queue TO authenticated;
GRANT ALL ON nudge_queue TO service_role;

COMMENT ON TABLE nudge_queue IS 'EC Agent: Queue for proactive nudges (deadline reminders, stall checks, check-ins)';
