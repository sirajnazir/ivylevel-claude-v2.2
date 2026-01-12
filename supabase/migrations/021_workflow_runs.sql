-- =============================================================================
-- IvyQuest v10.0 Migration 021: Workflow Runs Table
-- Version: 1.0.0
-- Date: January 2026
--
-- Creates table for tracking workflow execution history.
-- Used by WorkflowRunner to log each workflow run.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. WORKFLOW RUNS
-- Stores execution history for all proactive workflows
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.workflow_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Workflow identification
  workflow_name TEXT NOT NULL,

  -- Execution results
  success BOOLEAN NOT NULL DEFAULT false,
  profiles_processed INTEGER DEFAULT 0,
  notifications_sent INTEGER DEFAULT 0,

  -- Errors (array of error messages)
  errors TEXT[] DEFAULT '{}',

  -- Performance
  duration_ms INTEGER,

  -- Execution timestamp
  run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_runs_name ON workflow_runs(workflow_name);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_run_at ON workflow_runs(run_at DESC);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_success ON workflow_runs(success);

-- Comment
COMMENT ON TABLE workflow_runs IS 'Execution history for proactive workflows (silence detector, deadline alerts, etc.)';


-- -----------------------------------------------------------------------------
-- 2. VIEW: Workflow Performance Summary
-- Aggregates workflow performance metrics
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW public.v_workflow_performance AS
SELECT
  workflow_name,
  COUNT(*) as total_runs,
  SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_runs,
  ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as success_rate,
  SUM(profiles_processed) as total_profiles_processed,
  SUM(notifications_sent) as total_notifications_sent,
  AVG(duration_ms)::INTEGER as avg_duration_ms,
  MAX(run_at) as last_run_at
FROM workflow_runs
WHERE run_at > NOW() - INTERVAL '30 days'
GROUP BY workflow_name
ORDER BY workflow_name;

COMMENT ON VIEW v_workflow_performance IS 'Performance metrics for workflows over the last 30 days';


-- -----------------------------------------------------------------------------
-- 3. VIEW: Recent Workflow Runs
-- Quick access to recent runs with error details
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW public.v_recent_workflow_runs AS
SELECT
  id,
  workflow_name,
  success,
  profiles_processed,
  notifications_sent,
  array_length(errors, 1) as error_count,
  duration_ms,
  run_at,
  CASE
    WHEN run_at > NOW() - INTERVAL '1 hour' THEN 'recent'
    WHEN run_at > NOW() - INTERVAL '24 hours' THEN 'today'
    WHEN run_at > NOW() - INTERVAL '7 days' THEN 'this_week'
    ELSE 'older'
  END as recency
FROM workflow_runs
ORDER BY run_at DESC
LIMIT 100;

COMMENT ON VIEW v_recent_workflow_runs IS 'Recent workflow runs for monitoring dashboard';


-- -----------------------------------------------------------------------------
-- COMPLETE
-- -----------------------------------------------------------------------------

-- Verify table created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name = 'workflow_runs';
