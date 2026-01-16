-- =============================================================================
-- IvyQuest v4.1 ReAct A/B Test Analysis Queries
-- =============================================================================
--
-- Purpose: Analyze the effectiveness of ReAct self-correction framework
-- through A/B testing data collected in the react_analytics table.
--
-- Table Schema (react_analytics):
--   profile_id: uuid
--   agent_name: text
--   ab_test_group: text ('treatment' or 'control')
--   total_cycles: integer
--   final_quality_score: float
--   final_voice_score: float (nullable)
--   final_golden_similarity: float (nullable)
--   improvement_trajectory: jsonb (array of scores)
--   total_duration_ms: integer
--   success: boolean
--   created_at: timestamp
--
-- =============================================================================

-- -----------------------------------------------------------------------------
-- QUERY 1: Overall A/B Test Summary
-- Compare treatment (ReAct enabled) vs control (ReAct disabled) groups
-- -----------------------------------------------------------------------------
SELECT
    ab_test_group,
    COUNT(*) as total_requests,
    AVG(final_quality_score) as avg_quality_score,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY final_quality_score) as median_quality,
    STDDEV(final_quality_score) as quality_stddev,
    AVG(total_duration_ms) as avg_duration_ms,
    COUNT(*) FILTER (WHERE success = true) * 100.0 / COUNT(*) as success_rate_pct
FROM react_analytics
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY ab_test_group
ORDER BY ab_test_group;


-- -----------------------------------------------------------------------------
-- QUERY 2: Quality Score Distribution by Group
-- Understand the spread of quality scores in each group
-- -----------------------------------------------------------------------------
SELECT
    ab_test_group,
    CASE
        WHEN final_quality_score >= 90 THEN '90-100 (Excellent)'
        WHEN final_quality_score >= 80 THEN '80-89 (Good)'
        WHEN final_quality_score >= 70 THEN '70-79 (Acceptable)'
        WHEN final_quality_score >= 60 THEN '60-69 (Below Target)'
        ELSE '< 60 (Poor)'
    END as quality_bucket,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY ab_test_group) as percentage
FROM react_analytics
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY ab_test_group, quality_bucket
ORDER BY ab_test_group, quality_bucket DESC;


-- -----------------------------------------------------------------------------
-- QUERY 3: ReAct Cycle Analysis (Treatment Group Only)
-- How many cycles does it typically take to reach quality threshold?
-- -----------------------------------------------------------------------------
SELECT
    total_cycles,
    COUNT(*) as count,
    AVG(final_quality_score) as avg_final_quality,
    AVG(total_duration_ms) as avg_duration_ms,
    COUNT(*) FILTER (WHERE final_quality_score >= 70) * 100.0 / COUNT(*) as threshold_met_pct
FROM react_analytics
WHERE ab_test_group = 'treatment'
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY total_cycles
ORDER BY total_cycles;


-- -----------------------------------------------------------------------------
-- QUERY 4: Agent-Level Performance Comparison
-- Compare ReAct effectiveness across different agents
-- -----------------------------------------------------------------------------
SELECT
    agent_name,
    ab_test_group,
    COUNT(*) as total_requests,
    AVG(final_quality_score) as avg_quality_score,
    AVG(total_cycles) as avg_cycles,
    AVG(total_duration_ms) as avg_duration_ms
FROM react_analytics
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY agent_name, ab_test_group
ORDER BY agent_name, ab_test_group;


-- -----------------------------------------------------------------------------
-- QUERY 5: Improvement Trajectory Analysis
-- Analyze how quality improves across ReAct cycles
-- -----------------------------------------------------------------------------
WITH trajectory_expanded AS (
    SELECT
        profile_id,
        agent_name,
        elem.ordinality as cycle_number,
        elem.value::float as quality_score
    FROM react_analytics,
         LATERAL jsonb_array_elements(improvement_trajectory) WITH ORDINALITY as elem
    WHERE ab_test_group = 'treatment'
        AND created_at >= NOW() - INTERVAL '7 days'
)
SELECT
    cycle_number,
    COUNT(*) as data_points,
    AVG(quality_score) as avg_quality,
    MIN(quality_score) as min_quality,
    MAX(quality_score) as max_quality,
    AVG(quality_score) - LAG(AVG(quality_score)) OVER (ORDER BY cycle_number) as improvement_delta
FROM trajectory_expanded
GROUP BY cycle_number
ORDER BY cycle_number;


-- -----------------------------------------------------------------------------
-- QUERY 6: Statistical Significance Test Data
-- Prepare data for t-test or other statistical tests
-- -----------------------------------------------------------------------------
SELECT
    'treatment' as group_name,
    COUNT(*) as n,
    AVG(final_quality_score) as mean,
    STDDEV(final_quality_score) as stddev,
    VARIANCE(final_quality_score) as variance
FROM react_analytics
WHERE ab_test_group = 'treatment'
    AND created_at >= NOW() - INTERVAL '7 days'

UNION ALL

SELECT
    'control' as group_name,
    COUNT(*) as n,
    AVG(final_quality_score) as mean,
    STDDEV(final_quality_score) as stddev,
    VARIANCE(final_quality_score) as variance
FROM react_analytics
WHERE ab_test_group = 'control'
    AND created_at >= NOW() - INTERVAL '7 days';


-- -----------------------------------------------------------------------------
-- QUERY 7: Daily Trends
-- Track A/B test metrics over time
-- -----------------------------------------------------------------------------
SELECT
    DATE(created_at) as date,
    ab_test_group,
    COUNT(*) as requests,
    AVG(final_quality_score) as avg_quality,
    AVG(total_cycles) FILTER (WHERE ab_test_group = 'treatment') as avg_cycles,
    AVG(total_duration_ms) as avg_duration_ms
FROM react_analytics
WHERE created_at >= NOW() - INTERVAL '14 days'
GROUP BY DATE(created_at), ab_test_group
ORDER BY date DESC, ab_test_group;


-- -----------------------------------------------------------------------------
-- QUERY 8: Decision Dashboard
-- Key metrics for deciding whether to expand ReAct rollout
-- -----------------------------------------------------------------------------
WITH metrics AS (
    SELECT
        ab_test_group,
        COUNT(*) as n,
        AVG(final_quality_score) as avg_quality,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY final_quality_score) as median_quality,
        COUNT(*) FILTER (WHERE final_quality_score >= 70) * 100.0 / COUNT(*) as pct_above_threshold,
        AVG(total_duration_ms) as avg_latency_ms
    FROM react_analytics
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY ab_test_group
)
SELECT
    'Summary' as metric_type,
    treatment.avg_quality - control.avg_quality as quality_lift,
    treatment.median_quality - control.median_quality as median_lift,
    treatment.pct_above_threshold - control.pct_above_threshold as threshold_rate_lift,
    treatment.avg_latency_ms - control.avg_latency_ms as latency_overhead_ms,
    CASE
        WHEN treatment.avg_quality > control.avg_quality + 5
            AND treatment.pct_above_threshold > control.pct_above_threshold + 10
        THEN 'RECOMMEND: Expand rollout'
        WHEN treatment.avg_quality > control.avg_quality
        THEN 'NEUTRAL: Continue A/B test'
        ELSE 'NOT RECOMMENDED: ReAct not showing improvement'
    END as recommendation
FROM
    (SELECT * FROM metrics WHERE ab_test_group = 'treatment') treatment,
    (SELECT * FROM metrics WHERE ab_test_group = 'control') control;


-- =============================================================================
-- TABLE CREATION (Run once to set up analytics table)
-- =============================================================================

/*
CREATE TABLE IF NOT EXISTS react_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    agent_name TEXT NOT NULL,
    ab_test_group TEXT NOT NULL CHECK (ab_test_group IN ('treatment', 'control')),
    total_cycles INTEGER DEFAULT 1,
    final_quality_score FLOAT NOT NULL,
    final_voice_score FLOAT,
    final_golden_similarity FLOAT,
    improvement_trajectory JSONB DEFAULT '[]'::jsonb,
    total_duration_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes for common queries
    CONSTRAINT valid_quality_score CHECK (final_quality_score >= 0 AND final_quality_score <= 100)
);

-- Indexes
CREATE INDEX idx_react_analytics_ab_group ON react_analytics(ab_test_group);
CREATE INDEX idx_react_analytics_created_at ON react_analytics(created_at);
CREATE INDEX idx_react_analytics_agent ON react_analytics(agent_name);
CREATE INDEX idx_react_analytics_profile ON react_analytics(profile_id);
*/


-- =============================================================================
-- SAMPLE DATA GENERATION (For testing queries)
-- =============================================================================

/*
-- Generate test data for development
INSERT INTO react_analytics (profile_id, agent_name, ab_test_group, total_cycles, final_quality_score, improvement_trajectory, total_duration_ms, success)
SELECT
    gen_random_uuid() as profile_id,
    (ARRAY['Extracurriculars', 'Awards', 'Programs', 'GamePlan'])[floor(random() * 4) + 1] as agent_name,
    (ARRAY['treatment', 'control'])[floor(random() * 2) + 1] as ab_test_group,
    floor(random() * 3) + 1 as total_cycles,
    60 + random() * 40 as final_quality_score,
    CASE
        WHEN random() > 0.5 THEN '[65, 72, 78]'::jsonb
        ELSE '[68, 75]'::jsonb
    END as improvement_trajectory,
    floor(random() * 5000) + 1000 as total_duration_ms,
    random() > 0.1 as success
FROM generate_series(1, 100);
*/
