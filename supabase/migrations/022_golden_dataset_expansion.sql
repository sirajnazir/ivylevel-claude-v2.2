-- Migration 022: Golden Dataset Expansion
-- Purpose: Expand golden examples table for comprehensive evaluation

-- Add new columns to evaluation_golden
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS jenny_techniques TEXT[];
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS source_session VARCHAR(50);
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS quality_tier VARCHAR(20) DEFAULT 'standard';
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS student_profile_name VARCHAR(100);
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS jenny_response_example TEXT;
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS transformation_pattern VARCHAR(200);
ALTER TABLE evaluation_golden ADD COLUMN IF NOT EXISTS category VARCHAR(100);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_golden_agent_type ON evaluation_golden(agent_type);
CREATE INDEX IF NOT EXISTS idx_golden_category ON evaluation_golden(category);
CREATE INDEX IF NOT EXISTS idx_golden_quality_tier ON evaluation_golden(quality_tier);

-- Add quality tier constraint
ALTER TABLE evaluation_golden DROP CONSTRAINT IF EXISTS check_quality_tier;
ALTER TABLE evaluation_golden ADD CONSTRAINT check_quality_tier
    CHECK (quality_tier IN ('gold', 'silver', 'bronze', 'standard'));

-- Comment on table
COMMENT ON TABLE evaluation_golden IS 'Golden examples for agent evaluation with Jenny coaching patterns';
