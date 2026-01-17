-- ============================================================================
-- Migration: 034_v5.3_conversations.sql
-- Date: 2026-01-17
-- Description: Persistent chat history for Execution Agent conversations
-- Risk Level: LOW - New table, no modifications to existing data
-- ============================================================================
--
-- This is the ONLY new table needed for Execution Agent based on 3P audit.
-- All other execution infrastructure already exists:
--   - projects + project_steps (execution tracking)
--   - crises (Crisis Alchemy 4-step protocol)
--   - weekly_plans (P0/P1/P2 prioritization)
--   - weekly_vitals (progress snapshots)
--   - agent_memories (long-term memory with pgvector)
--   - notifications (pull-based alerts)
-- ============================================================================

-- ============================================================================
-- CONVERSATIONS TABLE
-- Persistent chat history with context linking to existing tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Profile reference
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Conversation Context
  agent_type TEXT NOT NULL DEFAULT 'execution',
  session_id UUID,                                -- Optional: link to react_sessions
  thread_id UUID,                                 -- Group related messages into threads

  -- Message Content
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
  content TEXT NOT NULL,

  -- Rich Content
  attachments JSONB DEFAULT '[]',                 -- [{type, url, name, size}]
  tool_calls JSONB DEFAULT '[]',                  -- Tool invocations if role='assistant'
  tool_result JSONB,                              -- Tool result if role='tool'

  -- Context References (link to existing tables)
  -- Allows conversations about specific projects, crises, weekly plans
  context_type TEXT CHECK (context_type IN (
    'project',       -- Discussing a specific project
    'crisis',        -- Crisis Alchemy conversation
    'weekly_plan',   -- Weekly planning session
    'step',          -- Specific project step
    'general',       -- General chat
    'nudge',         -- Proactive nudge response
    'onboarding'     -- Onboarding conversation
  )),
  context_id UUID,                                -- FK to projects.id, crises.id, etc.

  -- AI-Native: Proactive vs Reactive
  is_proactive BOOLEAN DEFAULT FALSE,             -- Agent-initiated (nudge)
  nudge_trigger TEXT,                             -- 'stall_5_days', 'deadline_48h', 'eds_high'

  -- Memory Extraction (feeds into agent_memories)
  extracted_facts JSONB DEFAULT '[]',             -- Facts to persist to long-term memory
  fact_extraction_done BOOLEAN DEFAULT FALSE,

  -- Message Metadata
  tokens_used INTEGER,                            -- For cost tracking
  model_used TEXT,                                -- 'gpt-4', 'claude-3', etc.
  latency_ms INTEGER,                             -- Response latency

  -- Quality/Feedback
  user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
  user_feedback TEXT,
  flagged BOOLEAN DEFAULT FALSE,                  -- Flagged for review
  flag_reason TEXT,

  -- Vector Embedding (for semantic search across conversations)
  embedding vector(1536),

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ                          -- Soft delete
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Primary lookup: user's conversations with an agent
CREATE INDEX idx_conversations_profile_agent
  ON conversations(profile_id, agent_type, created_at DESC);

-- Thread grouping
CREATE INDEX idx_conversations_thread
  ON conversations(thread_id, created_at ASC)
  WHERE thread_id IS NOT NULL;

-- Context-specific conversations (e.g., all messages about a project)
CREATE INDEX idx_conversations_context
  ON conversations(context_type, context_id, created_at DESC)
  WHERE context_type IS NOT NULL;

-- Proactive nudge tracking
CREATE INDEX idx_conversations_proactive
  ON conversations(profile_id, is_proactive, created_at DESC)
  WHERE is_proactive = TRUE;

-- Session lookup
CREATE INDEX idx_conversations_session
  ON conversations(session_id, created_at ASC)
  WHERE session_id IS NOT NULL;

-- Vector similarity search (for semantic retrieval)
CREATE INDEX idx_conversations_embedding
  ON conversations USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Flagged messages for review
CREATE INDEX idx_conversations_flagged
  ON conversations(flagged, created_at DESC)
  WHERE flagged = TRUE;

-- Unextracted facts (for batch processing)
CREATE INDEX idx_conversations_unextracted
  ON conversations(fact_extraction_done, created_at ASC)
  WHERE fact_extraction_done = FALSE AND extracted_facts != '[]'::jsonb;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update updated_at
CREATE TRIGGER update_conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Users can view their own conversations
CREATE POLICY "Users can view own conversations"
  ON conversations FOR SELECT
  USING (profile_id = auth.uid());

-- Users can insert their own conversations
CREATE POLICY "Users can insert own conversations"
  ON conversations FOR INSERT
  WITH CHECK (profile_id = auth.uid());

-- Users can update their own conversations (for ratings/feedback)
CREATE POLICY "Users can update own conversations"
  ON conversations FOR UPDATE
  USING (profile_id = auth.uid())
  WITH CHECK (profile_id = auth.uid());

-- Service role can do anything (for agent operations)
CREATE POLICY "Service role full access"
  ON conversations FOR ALL
  USING (auth.role() = 'service_role');

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Get conversation history for a profile (with optional context filter)
CREATE OR REPLACE FUNCTION get_conversation_history(
  p_profile_id UUID,
  p_agent_type TEXT DEFAULT 'execution',
  p_context_type TEXT DEFAULT NULL,
  p_context_id UUID DEFAULT NULL,
  p_limit INTEGER DEFAULT 50,
  p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
  id UUID,
  role TEXT,
  content TEXT,
  context_type TEXT,
  context_id UUID,
  is_proactive BOOLEAN,
  created_at TIMESTAMPTZ,
  attachments JSONB,
  tool_calls JSONB
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.id,
    c.role,
    c.content,
    c.context_type,
    c.context_id,
    c.is_proactive,
    c.created_at,
    c.attachments,
    c.tool_calls
  FROM conversations c
  WHERE c.profile_id = p_profile_id
    AND c.agent_type = p_agent_type
    AND c.deleted_at IS NULL
    AND (p_context_type IS NULL OR c.context_type = p_context_type)
    AND (p_context_id IS NULL OR c.context_id = p_context_id)
  ORDER BY c.created_at DESC
  LIMIT p_limit
  OFFSET p_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get recent context for agent (last N messages for prompt building)
CREATE OR REPLACE FUNCTION get_recent_context(
  p_profile_id UUID,
  p_agent_type TEXT DEFAULT 'execution',
  p_limit INTEGER DEFAULT 10
)
RETURNS JSONB AS $$
DECLARE
  v_result JSONB;
BEGIN
  SELECT jsonb_agg(
    jsonb_build_object(
      'role', c.role,
      'content', c.content,
      'context_type', c.context_type,
      'created_at', c.created_at
    ) ORDER BY c.created_at ASC
  )
  INTO v_result
  FROM (
    SELECT role, content, context_type, created_at
    FROM conversations
    WHERE profile_id = p_profile_id
      AND agent_type = p_agent_type
      AND deleted_at IS NULL
    ORDER BY created_at DESC
    LIMIT p_limit
  ) c;

  RETURN COALESCE(v_result, '[]'::jsonb);
END;
$$ LANGUAGE plpgsql STABLE;

-- Create new thread (returns thread_id)
CREATE OR REPLACE FUNCTION create_conversation_thread(
  p_profile_id UUID,
  p_agent_type TEXT DEFAULT 'execution',
  p_context_type TEXT DEFAULT NULL,
  p_context_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_thread_id UUID;
BEGIN
  v_thread_id := gen_random_uuid();

  -- Insert system message to start thread
  INSERT INTO conversations (
    profile_id, agent_type, thread_id, role, content,
    context_type, context_id
  ) VALUES (
    p_profile_id, p_agent_type, v_thread_id, 'system',
    'Thread started',
    p_context_type, p_context_id
  );

  RETURN v_thread_id;
END;
$$ LANGUAGE plpgsql;

-- Search conversations by semantic similarity
CREATE OR REPLACE FUNCTION search_conversations(
  p_profile_id UUID,
  p_query_embedding vector(1536),
  p_agent_type TEXT DEFAULT 'execution',
  p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  role TEXT,
  content TEXT,
  context_type TEXT,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.id,
    c.role,
    c.content,
    c.context_type,
    1 - (c.embedding <=> p_query_embedding) as similarity
  FROM conversations c
  WHERE c.profile_id = p_profile_id
    AND c.agent_type = p_agent_type
    AND c.embedding IS NOT NULL
    AND c.deleted_at IS NULL
  ORDER BY c.embedding <=> p_query_embedding
  LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Recent conversations per profile (for dashboard)
CREATE OR REPLACE VIEW recent_conversations AS
SELECT
  c.profile_id,
  c.agent_type,
  COUNT(*) as total_messages,
  COUNT(*) FILTER (WHERE c.role = 'user') as user_messages,
  COUNT(*) FILTER (WHERE c.role = 'assistant') as assistant_messages,
  COUNT(*) FILTER (WHERE c.is_proactive) as proactive_nudges,
  MAX(c.created_at) as last_message_at,
  AVG(c.user_rating) FILTER (WHERE c.user_rating IS NOT NULL) as avg_rating
FROM conversations c
WHERE c.deleted_at IS NULL
  AND c.created_at > NOW() - INTERVAL '30 days'
GROUP BY c.profile_id, c.agent_type;

-- Flagged conversations for review
CREATE OR REPLACE VIEW flagged_conversations AS
SELECT
  c.id,
  c.profile_id,
  p.first_name || ' ' || p.last_name as student_name,
  c.agent_type,
  c.role,
  c.content,
  c.flag_reason,
  c.created_at
FROM conversations c
JOIN profiles p ON c.profile_id = p.id
WHERE c.flagged = TRUE
  AND c.deleted_at IS NULL
ORDER BY c.created_at DESC;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE conversations IS 'Persistent chat history for agent conversations (v5.3). Links to existing execution tables via context_type/context_id.';
COMMENT ON COLUMN conversations.context_type IS 'Links to: projects, crises, weekly_plans, project_steps';
COMMENT ON COLUMN conversations.context_id IS 'FK to the context table (projects.id, crises.id, etc.)';
COMMENT ON COLUMN conversations.is_proactive IS 'TRUE if agent initiated (nudge), FALSE if user initiated';
COMMENT ON COLUMN conversations.nudge_trigger IS 'What triggered the proactive message: stall_5_days, deadline_48h, eds_high';
COMMENT ON COLUMN conversations.extracted_facts IS 'Facts extracted to feed into agent_memories for long-term recall';
COMMENT ON COLUMN conversations.embedding IS 'pgvector embedding for semantic search across conversation history';
COMMENT ON FUNCTION get_conversation_history IS 'Retrieve paginated conversation history with optional context filtering';
COMMENT ON FUNCTION get_recent_context IS 'Get last N messages as JSONB for prompt building';
COMMENT ON FUNCTION search_conversations IS 'Semantic search using pgvector cosine similarity';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
BEGIN
  -- Verify table exists
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = 'conversations'
  ) THEN
    RAISE EXCEPTION 'Migration failed: conversations table not created';
  END IF;

  -- Verify indexes exist
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE tablename = 'conversations' AND indexname = 'idx_conversations_profile_agent'
  ) THEN
    RAISE EXCEPTION 'Migration failed: idx_conversations_profile_agent not created';
  END IF;

  -- Verify functions exist
  IF NOT EXISTS (
    SELECT 1 FROM pg_proc WHERE proname = 'get_conversation_history'
  ) THEN
    RAISE EXCEPTION 'Migration failed: get_conversation_history function not created';
  END IF;

  RAISE NOTICE 'Migration 034_v5.3_conversations completed successfully';
END;
$$;

-- ============================================================================
-- ROLLBACK
-- ============================================================================
-- DROP VIEW IF EXISTS flagged_conversations;
-- DROP VIEW IF EXISTS recent_conversations;
-- DROP FUNCTION IF EXISTS search_conversations;
-- DROP FUNCTION IF EXISTS create_conversation_thread;
-- DROP FUNCTION IF EXISTS get_recent_context;
-- DROP FUNCTION IF EXISTS get_conversation_history;
-- DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
-- DROP TABLE IF EXISTS conversations;
