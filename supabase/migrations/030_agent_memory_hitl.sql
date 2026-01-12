-- ============================================================
-- IvyQuest v13.0 Database Migration
-- Agent Memory System + HITL Workflow
-- ============================================================

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- AGENT MEMORIES TABLE
-- 3-tier memory system: Working (in-memory), Short-term (Redis), Long-term (Supabase)
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_memories (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    content JSONB NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002 dimensions
    importance FLOAT DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),
    archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_agent_memories_profile
ON agent_memories(profile_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_agent_memories_agent
ON agent_memories(agent_id, profile_id);

CREATE INDEX IF NOT EXISTS idx_agent_memories_archived
ON agent_memories(profile_id, archived) WHERE archived = FALSE;

-- Semantic search index (IVFFlat for approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_agent_memories_embedding
ON agent_memories USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================================
-- MEMORY SEARCH FUNCTION
-- Semantic search using pgvector with filters
-- ============================================================

CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_profile_id UUID DEFAULT NULL,
    min_importance FLOAT DEFAULT 0.0
)
RETURNS TABLE (
    id TEXT,
    agent_id TEXT,
    profile_id UUID,
    content JSONB,
    importance FLOAT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        am.id,
        am.agent_id,
        am.profile_id,
        am.content,
        am.importance,
        1 - (am.embedding <=> query_embedding) AS similarity,
        am.created_at
    FROM agent_memories am
    WHERE
        (filter_profile_id IS NULL OR am.profile_id = filter_profile_id)
        AND am.archived = FALSE
        AND am.importance >= min_importance
        AND am.embedding IS NOT NULL
        AND 1 - (am.embedding <=> query_embedding) > match_threshold
    ORDER BY am.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================
-- HITL REQUESTS TABLE
-- Human-in-the-Loop workflow for high-stakes agent decisions
-- ============================================================

CREATE TABLE IF NOT EXISTS hitl_requests (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    proposed_action JSONB NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    reasoning TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_review', 'approved', 'rejected', 'modified', 'expired')),
    reviewer_id TEXT,
    review_notes TEXT,
    modified_action JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

-- Indexes for HITL queries
CREATE INDEX IF NOT EXISTS idx_hitl_requests_profile
ON hitl_requests(profile_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_hitl_requests_pending
ON hitl_requests(status, created_at DESC) WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_hitl_requests_agent
ON hitl_requests(agent_id, status);

-- ============================================================
-- AGENT EVENTS TABLE
-- Event log for cross-agent communication
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_events (
    id BIGSERIAL PRIMARY KEY,
    source_agent TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    correlation_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for event queries
CREATE INDEX IF NOT EXISTS idx_agent_events_profile
ON agent_events(profile_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_agent_events_type
ON agent_events(event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_agent_events_correlation
ON agent_events(correlation_id) WHERE correlation_id IS NOT NULL;

-- ============================================================
-- AGENT THOUGHT LOGS TABLE
-- ReAct loop thought logging for debugging and analysis
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_thought_logs (
    id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    iteration INT NOT NULL,
    state TEXT NOT NULL,
    thought TEXT NOT NULL,
    action_taken TEXT,
    observation JSONB,
    correction TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for thought log queries
CREATE INDEX IF NOT EXISTS idx_thought_logs_run
ON agent_thought_logs(run_id, iteration);

CREATE INDEX IF NOT EXISTS idx_thought_logs_agent_profile
ON agent_thought_logs(agent_id, profile_id, created_at DESC);

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Update updated_at timestamp on agent_memories
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_agent_memories_timestamp ON agent_memories;
CREATE TRIGGER update_agent_memories_timestamp
    BEFORE UPDATE ON agent_memories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- MEMORY CONSOLIDATION FUNCTION
-- Archives old memories and creates summary
-- ============================================================

CREATE OR REPLACE FUNCTION consolidate_profile_memories(
    target_profile_id UUID,
    consolidation_threshold INT DEFAULT 100,
    archive_count INT DEFAULT 50
)
RETURNS TABLE (
    archived_count INT,
    remaining_count INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_count INT;
    archived_ids TEXT[];
BEGIN
    -- Get current memory count
    SELECT COUNT(*) INTO current_count
    FROM agent_memories
    WHERE profile_id = target_profile_id AND archived = FALSE;

    -- Only consolidate if threshold exceeded
    IF current_count <= consolidation_threshold THEN
        RETURN QUERY SELECT 0::INT, current_count::INT;
        RETURN;
    END IF;

    -- Get oldest memory IDs to archive
    SELECT ARRAY_AGG(id) INTO archived_ids
    FROM (
        SELECT id
        FROM agent_memories
        WHERE profile_id = target_profile_id AND archived = FALSE
        ORDER BY created_at ASC
        LIMIT archive_count
    ) oldest;

    -- Archive the memories
    UPDATE agent_memories
    SET archived = TRUE, updated_at = NOW()
    WHERE id = ANY(archived_ids);

    -- Return counts
    RETURN QUERY
    SELECT
        array_length(archived_ids, 1)::INT,
        (current_count - array_length(archived_ids, 1))::INT;
END;
$$;

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on tables
ALTER TABLE agent_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE hitl_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_thought_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for re-runs)
DROP POLICY IF EXISTS "Users can view their own memories" ON agent_memories;
DROP POLICY IF EXISTS "Service role can manage all memories" ON agent_memories;
DROP POLICY IF EXISTS "Allow all access to memories" ON agent_memories;

DROP POLICY IF EXISTS "Users can view their own HITL requests" ON hitl_requests;
DROP POLICY IF EXISTS "Service role can manage all HITL requests" ON hitl_requests;
DROP POLICY IF EXISTS "Allow all access to hitl_requests" ON hitl_requests;

DROP POLICY IF EXISTS "Users can view their own events" ON agent_events;
DROP POLICY IF EXISTS "Service role can manage all events" ON agent_events;
DROP POLICY IF EXISTS "Allow all access to agent_events" ON agent_events;

DROP POLICY IF EXISTS "Users can view their own thought logs" ON agent_thought_logs;
DROP POLICY IF EXISTS "Service role can manage all thought logs" ON agent_thought_logs;
DROP POLICY IF EXISTS "Allow all access to thought_logs" ON agent_thought_logs;

-- For development/MVP: allow all authenticated access
-- In production, replace with proper user-scoped policies

-- Policies for agent_memories
CREATE POLICY "Allow all access to memories"
    ON agent_memories FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policies for hitl_requests
CREATE POLICY "Allow all access to hitl_requests"
    ON hitl_requests FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policies for agent_events
CREATE POLICY "Allow all access to agent_events"
    ON agent_events FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policies for thought_logs
CREATE POLICY "Allow all access to thought_logs"
    ON agent_thought_logs FOR ALL
    USING (true)
    WITH CHECK (true);

-- NOTE: For production with proper auth, uncomment these and remove the "Allow all" policies:
-- CREATE POLICY "Users can view their own memories"
--     ON agent_memories FOR SELECT
--     USING (
--         auth.uid() IS NOT NULL AND
--         profile_id IN (SELECT id FROM profiles WHERE user_id = auth.uid())
--     );
-- CREATE POLICY "Service role can manage all memories"
--     ON agent_memories FOR ALL
--     USING (auth.role() = 'service_role');

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE agent_memories IS 'Long-term memory storage for v13.0 agent system with pgvector semantic search';
COMMENT ON TABLE hitl_requests IS 'Human-in-the-Loop workflow requests for agent decisions requiring human review';
COMMENT ON TABLE agent_events IS 'Event log for cross-agent communication and coordination';
COMMENT ON TABLE agent_thought_logs IS 'ReAct loop thought logs for debugging and analysis';
COMMENT ON FUNCTION match_memories IS 'Semantic search for memories using cosine similarity with pgvector';
COMMENT ON FUNCTION consolidate_profile_memories IS 'Archives old memories when count exceeds threshold';
