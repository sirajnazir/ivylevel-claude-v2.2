-- Migration: Add react_cycles table for analytics
-- Version: 5.1
-- Description: Queryable storage for ReAct cycle history
-- Author: IvyQuest Backend Team
-- Date: January 2026

-- ============================================================================
-- REACT CYCLES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS react_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Context
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,

    -- Cycle info
    cycle_number INT NOT NULL CHECK (cycle_number > 0),
    max_cycles INT NOT NULL DEFAULT 3,

    -- Phase data (JSONB for flexibility)
    think_data JSONB NOT NULL DEFAULT '{}',
    act_data JSONB NOT NULL DEFAULT '{}',
    observe_data JSONB NOT NULL DEFAULT '{}',
    learn_data JSONB NOT NULL DEFAULT '{}',

    -- Scores
    combined_score FLOAT NOT NULL DEFAULT 0 CHECK (combined_score >= 0 AND combined_score <= 100),
    quality_delta FLOAT DEFAULT 0,
    guardrails_score FLOAT DEFAULT 0,
    voice_score FLOAT DEFAULT 0,
    golden_score FLOAT DEFAULT 0,
    only_they_score FLOAT DEFAULT 0,

    -- Status
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    is_final_cycle BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timing
    duration_ms INT NOT NULL DEFAULT 0,
    think_duration_ms INT DEFAULT 0,
    act_duration_ms INT DEFAULT 0,
    observe_duration_ms INT DEFAULT 0,
    learn_duration_ms INT DEFAULT 0,

    -- Tools
    tools_selected JSONB DEFAULT '[]',
    tools_executed JSONB DEFAULT '[]',

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Primary query patterns
CREATE INDEX IF NOT EXISTS idx_react_cycles_profile ON react_cycles(profile_id);
CREATE INDEX IF NOT EXISTS idx_react_cycles_session ON react_cycles(session_id);
CREATE INDEX IF NOT EXISTS idx_react_cycles_agent ON react_cycles(agent_id);
CREATE INDEX IF NOT EXISTS idx_react_cycles_created ON react_cycles(created_at DESC);

-- Analytics queries
CREATE INDEX IF NOT EXISTS idx_react_cycles_score ON react_cycles(combined_score);
CREATE INDEX IF NOT EXISTS idx_react_cycles_passed ON react_cycles(passed);
CREATE INDEX IF NOT EXISTS idx_react_cycles_agent_score ON react_cycles(agent_id, combined_score);

-- Composite for session analysis
CREATE INDEX IF NOT EXISTS idx_react_cycles_session_agent ON react_cycles(session_id, agent_id, cycle_number);

-- ============================================================================
-- REACT SESSIONS TABLE (aggregates cycles)
-- ============================================================================

CREATE TABLE IF NOT EXISTS react_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Context
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    session_id TEXT UNIQUE NOT NULL,

    -- Agents involved
    agents_executed TEXT[] NOT NULL DEFAULT '{}',

    -- Aggregate scores
    final_score FLOAT DEFAULT 0,
    improvement_total FLOAT DEFAULT 0,

    -- Cycle counts
    total_cycles INT DEFAULT 0,
    passed_first_try INT DEFAULT 0,  -- Cycles that passed on first attempt
    required_retries INT DEFAULT 0,  -- Cycles that needed retries

    -- Timing
    total_duration_ms INT DEFAULT 0,

    -- Status
    success BOOLEAN DEFAULT FALSE,

    -- Timestamps
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_react_sessions_profile ON react_sessions(profile_id);
CREATE INDEX IF NOT EXISTS idx_react_sessions_success ON react_sessions(success);
CREATE INDEX IF NOT EXISTS idx_react_sessions_started ON react_sessions(started_at DESC);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Get cycle history for a session
CREATE OR REPLACE FUNCTION get_session_cycles(p_session_id TEXT)
RETURNS TABLE (
    agent_id TEXT,
    cycle_number INT,
    combined_score FLOAT,
    quality_delta FLOAT,
    passed BOOLEAN,
    duration_ms INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        rc.agent_id,
        rc.cycle_number,
        rc.combined_score,
        rc.quality_delta,
        rc.passed,
        rc.duration_ms
    FROM react_cycles rc
    WHERE rc.session_id = p_session_id
    ORDER BY rc.agent_id, rc.cycle_number;
END;
$$ LANGUAGE plpgsql;


-- Function: Get improvement trajectory for an agent
CREATE OR REPLACE FUNCTION get_agent_trajectory(p_session_id TEXT, p_agent_id TEXT)
RETURNS TABLE (
    cycle_number INT,
    combined_score FLOAT,
    quality_delta FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        rc.cycle_number,
        rc.combined_score,
        rc.quality_delta
    FROM react_cycles rc
    WHERE rc.session_id = p_session_id
      AND rc.agent_id = p_agent_id
    ORDER BY rc.cycle_number;
END;
$$ LANGUAGE plpgsql;


-- Function: Calculate agent success rate
CREATE OR REPLACE FUNCTION get_agent_success_rate(p_agent_id TEXT, p_days INT DEFAULT 30)
RETURNS TABLE (
    total_sessions BIGINT,
    passed_sessions BIGINT,
    success_rate FLOAT,
    avg_cycles_to_pass FLOAT,
    avg_final_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH agent_sessions AS (
        SELECT
            rc.session_id,
            MAX(rc.combined_score) as max_score,
            MAX(rc.cycle_number) as cycles_used,
            BOOL_OR(rc.passed AND rc.is_final_cycle) as session_passed
        FROM react_cycles rc
        WHERE rc.agent_id = p_agent_id
          AND rc.created_at > NOW() - (p_days || ' days')::INTERVAL
        GROUP BY rc.session_id
    )
    SELECT
        COUNT(*)::BIGINT as total_sessions,
        COUNT(*) FILTER (WHERE session_passed)::BIGINT as passed_sessions,
        (COUNT(*) FILTER (WHERE session_passed)::FLOAT / NULLIF(COUNT(*), 0)) as success_rate,
        AVG(cycles_used) FILTER (WHERE session_passed) as avg_cycles_to_pass,
        AVG(max_score) as avg_final_score
    FROM agent_sessions;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGER: Auto-update react_sessions on cycle insert
-- ============================================================================

CREATE OR REPLACE FUNCTION update_react_session()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert or update session record
    INSERT INTO react_sessions (
        session_id,
        profile_id,
        agents_executed,
        total_cycles,
        started_at
    )
    VALUES (
        NEW.session_id,
        NEW.profile_id,
        ARRAY[NEW.agent_id],
        1,
        NOW()
    )
    ON CONFLICT (session_id) DO UPDATE SET
        agents_executed = CASE
            WHEN NOT (NEW.agent_id = ANY(react_sessions.agents_executed))
            THEN array_append(react_sessions.agents_executed, NEW.agent_id)
            ELSE react_sessions.agents_executed
        END,
        total_cycles = react_sessions.total_cycles + 1,
        final_score = GREATEST(react_sessions.final_score, NEW.combined_score),
        success = react_sessions.success OR NEW.passed,
        completed_at = CASE WHEN NEW.is_final_cycle THEN NOW() ELSE react_sessions.completed_at END;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger only if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_update_react_session') THEN
        CREATE TRIGGER trg_update_react_session
            AFTER INSERT ON react_cycles
            FOR EACH ROW
            EXECUTE FUNCTION update_react_session();
    END IF;
END;
$$;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE react_cycles IS 'Stores individual ReAct cycle data for analytics and debugging';
COMMENT ON TABLE react_sessions IS 'Aggregates ReAct cycles into sessions for high-level analytics';
COMMENT ON FUNCTION get_session_cycles IS 'Returns all cycles for a given session';
COMMENT ON FUNCTION get_agent_trajectory IS 'Returns improvement trajectory for an agent in a session';
COMMENT ON FUNCTION get_agent_success_rate IS 'Calculates success rate statistics for an agent type';
