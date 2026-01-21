-- =============================================================================
-- Letta Multi-Agent Integration - Database Migration 001
-- =============================================================================
--
-- Creates all letta_* tables for the multi-agent system.
--
-- Tables:
-- - letta_agent_registry: Tracks Letta agents per student
-- - letta_memory_snapshots: Stores memory block snapshots
-- - letta_approval_queue: HITL approval workflow
-- - letta_transition_log: Tracks state transitions
--
-- Run with: psql -d your_database -f 001_create_letta_tables.sql
-- =============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- Table: letta_agent_registry
-- =============================================================================
-- Tracks Letta agent IDs for each student profile.
-- One student can have multiple agents (Orchestrator + Specialists).

CREATE TABLE IF NOT EXISTS letta_agent_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    letta_agent_id TEXT NOT NULL,
    agent_type TEXT NOT NULL,  -- orchestrator, gameplan, execution, awards, essay, assessment
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one agent per type per profile
    CONSTRAINT unique_agent_per_profile_type UNIQUE (profile_id, agent_type)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_letta_agent_registry_profile
    ON letta_agent_registry(profile_id);
CREATE INDEX IF NOT EXISTS idx_letta_agent_registry_active
    ON letta_agent_registry(profile_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_letta_agent_registry_type
    ON letta_agent_registry(agent_type);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_letta_agent_registry_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_letta_agent_registry_updated_at ON letta_agent_registry;
CREATE TRIGGER trigger_letta_agent_registry_updated_at
    BEFORE UPDATE ON letta_agent_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_letta_agent_registry_updated_at();

-- =============================================================================
-- Table: letta_memory_snapshots
-- =============================================================================
-- Stores memory block content synced from Supabase.
-- Used to keep Letta memory blocks up to date with source data.

CREATE TABLE IF NOT EXISTS letta_memory_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    block_name TEXT NOT NULL,  -- student_profile, coaching_history, etc.
    block_content TEXT NOT NULL,
    snapshot_at TIMESTAMPTZ DEFAULT NOW(),

    -- One snapshot per block per profile (upsert on conflict)
    CONSTRAINT unique_block_per_profile UNIQUE (profile_id, block_name)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_letta_memory_snapshots_profile
    ON letta_memory_snapshots(profile_id);
CREATE INDEX IF NOT EXISTS idx_letta_memory_snapshots_block
    ON letta_memory_snapshots(block_name);

-- =============================================================================
-- Table: letta_approval_queue
-- =============================================================================
-- Human-in-the-loop approval workflow for critical decisions.
-- Agents request approval, users approve/reject via API.

CREATE TABLE IF NOT EXISTS letta_approval_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,  -- submit_application, major_plan_change, etc.
    action_payload JSONB NOT NULL,  -- description, rationale, urgency, metadata
    requested_by TEXT NOT NULL,  -- agent name that requested
    status TEXT DEFAULT 'pending',  -- pending, approved, rejected
    approved_by TEXT,  -- who resolved (user or agent name)
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_letta_approval_queue_profile
    ON letta_approval_queue(profile_id);
CREATE INDEX IF NOT EXISTS idx_letta_approval_queue_pending
    ON letta_approval_queue(profile_id, status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_letta_approval_queue_status
    ON letta_approval_queue(status);
CREATE INDEX IF NOT EXISTS idx_letta_approval_queue_created
    ON letta_approval_queue(created_at DESC);

-- =============================================================================
-- Table: letta_transition_log
-- =============================================================================
-- Logs state transitions for debugging and audit.
-- Tracks when students transition to/from Letta agents.

CREATE TABLE IF NOT EXISTS letta_transition_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    from_state TEXT,  -- previous state (null for initial)
    to_state TEXT NOT NULL,  -- new state
    trigger TEXT NOT NULL,  -- what triggered the transition
    metadata JSONB DEFAULT '{}',
    transitioned_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_letta_transition_log_profile
    ON letta_transition_log(profile_id);
CREATE INDEX IF NOT EXISTS idx_letta_transition_log_time
    ON letta_transition_log(transitioned_at DESC);

-- =============================================================================
-- Row Level Security (RLS) Policies
-- =============================================================================
-- Enable RLS on all tables and create policies for authenticated users.

-- Agent Registry
ALTER TABLE letta_agent_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own agent registry"
    ON letta_agent_registry FOR SELECT
    USING (auth.uid()::text = profile_id::text);

CREATE POLICY "Service role can manage all agent registry"
    ON letta_agent_registry FOR ALL
    USING (auth.role() = 'service_role');

-- Memory Snapshots
ALTER TABLE letta_memory_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own memory snapshots"
    ON letta_memory_snapshots FOR SELECT
    USING (auth.uid()::text = profile_id::text);

CREATE POLICY "Service role can manage all memory snapshots"
    ON letta_memory_snapshots FOR ALL
    USING (auth.role() = 'service_role');

-- Approval Queue
ALTER TABLE letta_approval_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own approval requests"
    ON letta_approval_queue FOR SELECT
    USING (auth.uid()::text = profile_id::text);

CREATE POLICY "Users can update their own approval requests"
    ON letta_approval_queue FOR UPDATE
    USING (auth.uid()::text = profile_id::text);

CREATE POLICY "Service role can manage all approval requests"
    ON letta_approval_queue FOR ALL
    USING (auth.role() = 'service_role');

-- Transition Log
ALTER TABLE letta_transition_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own transition log"
    ON letta_transition_log FOR SELECT
    USING (auth.uid()::text = profile_id::text);

CREATE POLICY "Service role can manage all transition logs"
    ON letta_transition_log FOR ALL
    USING (auth.role() = 'service_role');

-- =============================================================================
-- Comments
-- =============================================================================

COMMENT ON TABLE letta_agent_registry IS
    'Tracks Letta agent IDs per student profile. One student has multiple agents.';

COMMENT ON TABLE letta_memory_snapshots IS
    'Stores memory block content synced from Supabase to Letta.';

COMMENT ON TABLE letta_approval_queue IS
    'HITL approval workflow. Agents request, users approve/reject.';

COMMENT ON TABLE letta_transition_log IS
    'Audit log of state transitions for debugging.';

-- =============================================================================
-- Migration Complete
-- =============================================================================

-- Verify tables created
DO $$
BEGIN
    RAISE NOTICE 'Letta tables created successfully:';
    RAISE NOTICE '  - letta_agent_registry';
    RAISE NOTICE '  - letta_memory_snapshots';
    RAISE NOTICE '  - letta_approval_queue';
    RAISE NOTICE '  - letta_transition_log';
END $$;
