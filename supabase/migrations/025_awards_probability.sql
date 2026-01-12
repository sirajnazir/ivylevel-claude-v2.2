-- Migration 025: Awards Probability
-- Purpose: Add probability calculation fields to awards system

-- Add probability fields to student_awards
ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS calculated_probability DECIMAL(5,2);
ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS fit_score DECIMAL(5,2);
ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS competition_factor DECIMAL(5,2);
ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS submission_quality_score DECIMAL(5,2);
ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS vulnerability_bonus BOOLEAN DEFAULT FALSE;
ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS identity_alignment_bonus BOOLEAN DEFAULT FALSE;
ALTER TABLE student_awards ADD COLUMN IF NOT EXISTS portfolio_tier VARCHAR(20);

-- Add tier constraint
ALTER TABLE student_awards DROP CONSTRAINT IF EXISTS check_portfolio_tier;
ALTER TABLE student_awards ADD CONSTRAINT check_portfolio_tier
    CHECK (portfolio_tier IN ('likely', 'target', 'stretch', NULL));

-- Add selectivity and strategy fields to awards
ALTER TABLE awards ADD COLUMN IF NOT EXISTS selectivity_percentile INTEGER;
ALTER TABLE awards ADD COLUMN IF NOT EXISTS accepts_per_year INTEGER;
ALTER TABLE awards ADD COLUMN IF NOT EXISTS applicants_per_year INTEGER;
ALTER TABLE awards ADD COLUMN IF NOT EXISTS ideal_candidate_profile JSONB;
ALTER TABLE awards ADD COLUMN IF NOT EXISTS jenny_strategy TEXT;
ALTER TABLE awards ADD COLUMN IF NOT EXISTS vulnerability_story_boost BOOLEAN DEFAULT FALSE;

-- Add tier and redirect fields to opportunities
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS tier INTEGER DEFAULT 3;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS jenny_note TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS cost_numeric INTEGER DEFAULT 0;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS redirect_trigger BOOLEAN DEFAULT FALSE;

-- Update selectivity data for key awards
UPDATE awards SET selectivity_percentile = 30, vulnerability_story_boost = true
    WHERE name ILIKE '%ncwit%';
UPDATE awards SET selectivity_percentile = 50
    WHERE name ILIKE '%congressional%';
UPDATE awards SET selectivity_percentile = 5, vulnerability_story_boost = true
    WHERE name ILIKE '%coolidge%';
UPDATE awards SET selectivity_percentile = 2, vulnerability_story_boost = true
    WHERE name ILIKE '%cameron%';
UPDATE awards SET selectivity_percentile = 20
    WHERE name ILIKE '%scholastic%';
UPDATE awards SET selectivity_percentile = 15
    WHERE name ILIKE '%regeneron%' OR name ILIKE '%science talent%';
UPDATE awards SET selectivity_percentile = 25
    WHERE name ILIKE '%usaco%';
UPDATE awards SET selectivity_percentile = 40
    WHERE name ILIKE '%amc%' OR name ILIKE '%math olympiad%';

-- Update opportunities with tiers and redirect triggers
UPDATE opportunities SET tier = 4, redirect_trigger = true
    WHERE cost_numeric >= 5000 OR cost ILIKE '%$5%' OR cost ILIKE '%$6%' OR cost ILIKE '%$7%' OR cost ILIKE '%$8%';
UPDATE opportunities SET tier = 1
    WHERE cost_numeric = 0 AND prestige_score >= 80;
UPDATE opportunities SET tier = 2
    WHERE cost_numeric = 0 AND prestige_score >= 60 AND prestige_score < 80;
UPDATE opportunities SET tier = 3
    WHERE tier IS NULL;

-- Create portfolio summary view
CREATE OR REPLACE VIEW v_student_award_portfolio AS
SELECT
    sa.profile_id,
    sa.portfolio_tier,
    COUNT(*) as award_count,
    AVG(sa.calculated_probability) as avg_probability,
    SUM(CASE WHEN sa.vulnerability_bonus THEN 1 ELSE 0 END) as vulnerability_bonus_count,
    SUM(CASE WHEN sa.identity_alignment_bonus THEN 1 ELSE 0 END) as identity_bonus_count
FROM student_awards sa
WHERE sa.portfolio_tier IS NOT NULL
GROUP BY sa.profile_id, sa.portfolio_tier;

-- Create awards with probabilities view
CREATE OR REPLACE VIEW v_awards_with_stats AS
SELECT
    a.*,
    COALESCE(a.selectivity_percentile, 50) as effective_selectivity,
    CASE
        WHEN a.selectivity_percentile <= 10 THEN 'highly_selective'
        WHEN a.selectivity_percentile <= 30 THEN 'selective'
        WHEN a.selectivity_percentile <= 60 THEN 'competitive'
        ELSE 'accessible'
    END as selectivity_tier
FROM awards a;

-- Comments
COMMENT ON COLUMN student_awards.calculated_probability IS 'Win probability using fit*0.4 + (100-competition)*0.3 + quality*0.3 + bonuses';
COMMENT ON COLUMN student_awards.portfolio_tier IS '2-2-1 portfolio tier: likely (60%+), target (40-60%), stretch (20-40%)';
COMMENT ON COLUMN awards.vulnerability_story_boost IS 'Awards that value vulnerability/barrier-overcome stories';
COMMENT ON COLUMN opportunities.redirect_trigger IS 'If true, trigger Jenny redirect to free alternatives';
