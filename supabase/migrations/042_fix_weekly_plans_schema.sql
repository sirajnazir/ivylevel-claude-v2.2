-- ============================================
-- Fix weekly_plans table schema
-- ============================================
-- This migration adds missing columns to the weekly_plans table.
-- The table may have been created with an older schema.
-- ============================================

-- Add missing columns to weekly_plans table if they don't exist
DO $$
BEGIN
    -- Add generated_at if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'generated_at'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN generated_at TIMESTAMPTZ DEFAULT NOW();
        RAISE NOTICE 'Added generated_at column to weekly_plans';
    END IF;

    -- Add generated_by if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'generated_by'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN generated_by TEXT DEFAULT 'execution_agent';
        RAISE NOTICE 'Added generated_by column to weekly_plans';
    END IF;

    -- Add notes if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'notes'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN notes TEXT;
        RAISE NOTICE 'Added notes column to weekly_plans';
    END IF;

    -- Ensure profile_id column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'profile_id'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN profile_id UUID NOT NULL;
        RAISE NOTICE 'Added profile_id column to weekly_plans';
    END IF;

    -- Ensure week_start column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'week_start'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN week_start DATE NOT NULL DEFAULT CURRENT_DATE;
        RAISE NOTICE 'Added week_start column to weekly_plans';
    END IF;

    -- Ensure week_end column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'week_end'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN week_end DATE NOT NULL DEFAULT CURRENT_DATE;
        RAISE NOTICE 'Added week_end column to weekly_plans';
    END IF;

    -- Ensure p0_tasks column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'p0_tasks'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN p0_tasks JSONB DEFAULT '[]';
        RAISE NOTICE 'Added p0_tasks column to weekly_plans';
    END IF;

    -- Ensure p1_tasks column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'p1_tasks'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN p1_tasks JSONB DEFAULT '[]';
        RAISE NOTICE 'Added p1_tasks column to weekly_plans';
    END IF;

    -- Ensure p2_tasks column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'weekly_plans' AND column_name = 'p2_tasks'
    ) THEN
        ALTER TABLE weekly_plans ADD COLUMN p2_tasks JSONB DEFAULT '[]';
        RAISE NOTICE 'Added p2_tasks column to weekly_plans';
    END IF;
END
$$;

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_weekly_plans_profile ON weekly_plans(profile_id);
CREATE INDEX IF NOT EXISTS idx_weekly_plans_week ON weekly_plans(week_start DESC);

-- Enable RLS if not already enabled
ALTER TABLE weekly_plans ENABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON weekly_plans TO authenticated;
GRANT ALL ON weekly_plans TO service_role;

-- Add unique constraint if missing (profile_id + week_start)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'weekly_plans_profile_week_unique'
    ) THEN
        ALTER TABLE weekly_plans ADD CONSTRAINT weekly_plans_profile_week_unique
        UNIQUE (profile_id, week_start);
        RAISE NOTICE 'Added unique constraint on (profile_id, week_start)';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Unique constraint already exists or cannot be added: %', SQLERRM;
END
$$;

-- Comment
COMMENT ON TABLE weekly_plans IS 'EC Agent: Weekly P0/P1/P2 prioritization plans';
