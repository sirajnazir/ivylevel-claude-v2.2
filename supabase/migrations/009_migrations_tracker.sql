-- =====================================================
-- IvyQuest v10.0 Migration 009: Migrations Tracker
-- Tracks status of all v10.0 migration items
-- =====================================================

CREATE TABLE IF NOT EXISTS migrations_tracker (
  id SERIAL PRIMARY KEY,
  item TEXT NOT NULL UNIQUE,
  description TEXT,
  phase TEXT NOT NULL,
  week TEXT,
  priority TEXT DEFAULT 'P1', -- P0 = Critical, P1 = High, P2 = Medium
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'skipped')),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  blocked_by TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger
CREATE TRIGGER update_migrations_tracker_updated_at
  BEFORE UPDATE ON migrations_tracker
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Function to update status
CREATE OR REPLACE FUNCTION update_migration_status(
  p_item TEXT,
  p_status TEXT,
  p_notes TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
  UPDATE migrations_tracker SET
    status = p_status,
    started_at = CASE WHEN p_status = 'in_progress' AND started_at IS NULL THEN NOW() ELSE started_at END,
    completed_at = CASE WHEN p_status = 'completed' THEN NOW() ELSE completed_at END,
    notes = COALESCE(p_notes, notes)
  WHERE item = p_item;
END;
$$ LANGUAGE plpgsql;

-- Insert all 40 migration items from the spec
INSERT INTO migrations_tracker (item, description, phase, week, priority) VALUES
  -- Phase 1: Foundation + Execution Agent (Weeks 1-3)
  ('MIGRATE-001', 'Create archetypes table with default archetypes', 'Phase 1', 'Week 1', 'P1'),
  ('MIGRATE-002', 'Create profiles table with v10.0 agent attributes', 'Phase 1', 'Week 1', 'P1'),
  ('MIGRATE-003', 'Create crises table for Crisis Alchemy', 'Phase 1', 'Week 1', 'P1'),
  ('MIGRATE-004', 'Create chetty_baselines table (precomputed)', 'Phase 1', 'Week 1', 'P1'),
  ('MIGRATE-005', 'Create agent_state_versions table', 'Phase 1', 'Week 1', 'P1'),
  ('MIGRATE-006', 'Create opportunities and awards tables', 'Phase 1', 'Week 1', 'P1'),
  ('MIGRATE-007', 'Create /agents directory with Python/FastAPI service', 'Phase 1', 'Week 2', 'P1'),
  ('MIGRATE-008', 'Implement CRI computation module', 'Phase 1', 'Week 2', 'P1'),
  ('MIGRATE-009', 'Implement EDS (Execution Debt Score) computation', 'Phase 1', 'Week 2', 'P1'),
  ('MIGRATE-010', 'Docker configuration for agent service', 'Phase 1', 'Week 2', 'P2'),
  ('MIGRATE-011', 'Implement ExecutionAgent class with Agno', 'Phase 1', 'Week 3', 'P0'),
  ('MIGRATE-012', 'Implement Crisis Alchemy graph with LangGraph', 'Phase 1', 'Week 3', 'P0'),
  ('MIGRATE-013', 'Implement Human Shadow Mode with HITL handoff', 'Phase 1', 'Week 3', 'P0'),
  ('MIGRATE-014', 'Implement scaffoldProject() with Strategic Overwhelm', 'Phase 1', 'Week 3', 'P0'),
  ('MIGRATE-015', 'Implement detectBlockers() with inactivity monitoring', 'Phase 1', 'Week 3', 'P0'),

  -- Phase 2: Core Agents + Event Bus (Weeks 4-6)
  ('MIGRATE-016', 'Implement synthesizeNarrativeDNA()', 'Phase 2', 'Week 4', 'P1'),
  ('MIGRATE-017', 'Implement detectArchetype() with confidence/rationale', 'Phase 2', 'Week 4', 'P1'),
  ('MIGRATE-018', 'Implement calculateHiddenProbabilities()', 'Phase 2', 'Week 4', 'P1'),
  ('MIGRATE-019', 'Implement filterActivitiesByROI() (4+ touchpoints)', 'Phase 2', 'Week 5', 'P1'),
  ('MIGRATE-020', 'Implement plantIdentitySeeds() (6-12mo scheduling)', 'Phase 2', 'Week 5', 'P1'),
  ('MIGRATE-021', 'Implement applyStrategicOverwhelm() (1.4x capacity)', 'Phase 2', 'Week 5', 'P1'),
  ('MIGRATE-022', 'Implement event contracts (TypeScript)', 'Phase 2', 'Week 6', 'P1'),
  ('MIGRATE-023', 'Implement Supabase Realtime subscriptions', 'Phase 2', 'Week 6', 'P1'),
  ('MIGRATE-024', 'Implement state versioning on all agent changes', 'Phase 2', 'Week 6', 'P1'),

  -- Phase 3: Awards/Opportunity + Integration (Weeks 7-9)
  ('MIGRATE-025', 'Populate 200+ awards database', 'Phase 3', 'Week 7-8', 'P1'),
  ('MIGRATE-026', 'Implement matchAwards() with eligibility filtering', 'Phase 3', 'Week 7-8', 'P1'),
  ('MIGRATE-027', 'Implement calculateAwardROI() and balancePortfolio()', 'Phase 3', 'Week 7-8', 'P1'),
  ('MIGRATE-028', 'Populate 500+ opportunities database', 'Phase 3', 'Week 9', 'P1'),
  ('MIGRATE-029', 'Implement sendAdvanceAlerts() (6-month)', 'Phase 3', 'Week 9', 'P1'),
  ('MIGRATE-030', 'Implement Next.js API routes for all agents', 'Phase 3', 'Week 9', 'P1'),

  -- Phase 4: UI/UX + Testing + Rollout (Weeks 10-12)
  ('MIGRATE-031', 'Implement SuperpowerUnlock component (pyramid viz)', 'Phase 4', 'Week 10', 'P1'),
  ('MIGRATE-032', 'Implement dual parent/student views', 'Phase 4', 'Week 10', 'P1'),
  ('MIGRATE-033', 'Update dashboard with agent outputs', 'Phase 4', 'Week 10', 'P1'),
  ('MIGRATE-034', 'Jest unit tests (90% coverage)', 'Phase 4', 'Week 11', 'P1'),
  ('MIGRATE-035', 'Playwright E2E tests (full flows)', 'Phase 4', 'Week 11', 'P1'),
  ('MIGRATE-036', 'Huda benchmark replay tests', 'Phase 4', 'Week 11', 'P0'),
  ('MIGRATE-037', 'A/B testing setup (v2.2 vs v10.0)', 'Phase 4', 'Week 11', 'P2'),
  ('MIGRATE-038', 'Blue-green deployment', 'Phase 4', 'Week 12', 'P1'),
  ('MIGRATE-039', 'RLHF Success Vectors ingestion', 'Phase 4', 'Week 12', 'P1'),
  ('MIGRATE-040', 'Release v10.0 stable', 'Phase 4', 'Week 12', 'P0')
ON CONFLICT (item) DO NOTHING;

-- Update database migrations as completed (they exist now)
UPDATE migrations_tracker SET status = 'completed', completed_at = NOW()
WHERE item IN ('MIGRATE-001', 'MIGRATE-002', 'MIGRATE-003', 'MIGRATE-004', 'MIGRATE-005', 'MIGRATE-006');

-- View for migration dashboard
CREATE OR REPLACE VIEW migration_status AS
SELECT
  phase,
  COUNT(*) as total_items,
  COUNT(*) FILTER (WHERE status = 'completed') as completed,
  COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
  COUNT(*) FILTER (WHERE status = 'pending') as pending,
  COUNT(*) FILTER (WHERE status = 'blocked') as blocked,
  ROUND(COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC / COUNT(*) * 100, 1) as completion_pct
FROM migrations_tracker
GROUP BY phase
ORDER BY phase;

-- View for P0 critical items
CREATE OR REPLACE VIEW critical_migrations AS
SELECT * FROM migrations_tracker
WHERE priority = 'P0'
ORDER BY phase, week;

-- Comments
COMMENT ON TABLE migrations_tracker IS 'Tracks v10.0 migration progress (40 items)';
COMMENT ON COLUMN migrations_tracker.priority IS 'P0 = Critical (Execution Agent), P1 = High, P2 = Medium';

-- Enable RLS
ALTER TABLE migrations_tracker ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow migrations access" ON migrations_tracker FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- ROLLBACK
-- =====================================================
-- DROP VIEW IF EXISTS critical_migrations;
-- DROP VIEW IF EXISTS migration_status;
-- DROP FUNCTION IF EXISTS update_migration_status(TEXT, TEXT, TEXT);
-- DROP TABLE IF EXISTS migrations_tracker;
