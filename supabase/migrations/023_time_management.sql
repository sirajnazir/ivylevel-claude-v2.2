-- Migration 023: Time Management
-- Purpose: Support 168-hour framework and weekly planning

-- Student time audits table
CREATE TABLE IF NOT EXISTS student_time_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    audit_date TIMESTAMPTZ DEFAULT NOW(),

    -- Fixed allocations (hours per day unless noted)
    sleep_hours DECIMAL(4,2) DEFAULT 8,
    school_hours DECIMAL(4,2) DEFAULT 7.5,
    commute_minutes INTEGER DEFAULT 30,
    religious_hours DECIMAL(4,2) DEFAULT 0,
    misc_hours DECIMAL(4,2) DEFAULT 3,

    -- Social media audit
    social_media_current DECIMAL(4,2),
    social_media_target DECIMAL(4,2) DEFAULT 1,
    hours_recovered DECIMAL(4,2),

    -- Calculated totals (weekly)
    fixed_total DECIMAL(5,2),
    flexible_total DECIMAL(5,2),
    passion_hours_available DECIMAL(5,2),
    daily_passion_hours DECIMAL(4,2),

    -- Schedule template
    schedule_template JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Weekly plans table
CREATE TABLE IF NOT EXISTS weekly_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,

    -- Priority-based task lists (P0/P1/P2)
    p0_tasks JSONB DEFAULT '[]'::jsonb,
    p1_tasks JSONB DEFAULT '[]'::jsonb,
    p2_tasks JSONB DEFAULT '[]'::jsonb,

    -- Time budget
    total_hours_estimated DECIMAL(5,2),
    total_hours_available DECIMAL(5,2),
    buffer_hours DECIMAL(4,2),

    -- Completion tracking
    p0_completed INTEGER DEFAULT 0,
    p1_completed INTEGER DEFAULT 0,
    p2_completed INTEGER DEFAULT 0,
    completion_rate DECIMAL(3,2),

    -- Jenny's flexibility note
    flexibility_note TEXT DEFAULT 'We''ll try this for 2 weeks and adjust if needed',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_time_audits_profile ON student_time_audits(profile_id);
CREATE INDEX IF NOT EXISTS idx_time_audits_date ON student_time_audits(audit_date DESC);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_profile ON weekly_plans(profile_id);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_week ON weekly_plans(week_start);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_time_audit_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_time_audit_updated ON student_time_audits;
CREATE TRIGGER trigger_time_audit_updated
    BEFORE UPDATE ON student_time_audits
    FOR EACH ROW
    EXECUTE FUNCTION update_time_audit_timestamp();

DROP TRIGGER IF EXISTS trigger_weekly_plan_updated ON weekly_plans;
CREATE TRIGGER trigger_weekly_plan_updated
    BEFORE UPDATE ON weekly_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_time_audit_timestamp();

-- Comments
COMMENT ON TABLE student_time_audits IS 'Jenny 168-hour framework time audits';
COMMENT ON TABLE weekly_plans IS 'P0/P1/P2 prioritized weekly task plans';
