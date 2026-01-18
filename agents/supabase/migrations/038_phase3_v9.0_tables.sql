-- ============================================
-- Phase 3 v9.0 Database Migration
-- Final 20 Patterns - 3P-First Approach
-- ============================================

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- B3: SEMANTIC MEMORY (pgvector)
-- ============================================
CREATE TABLE IF NOT EXISTS phase3_semantic_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimension
    memory_type TEXT DEFAULT 'general',  -- 'fact', 'preference', 'context', 'general'
    importance REAL DEFAULT 0.5,
    source_session_id TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    access_count INTEGER DEFAULT 0
);

-- Vector index for similarity search
-- Uncomment ONE of these based on your pgvector version:
-- For pgvector 0.5.0+: HNSW (recommended, no training needed)
-- CREATE INDEX IF NOT EXISTS idx_semantic_memories_embedding
-- ON phase3_semantic_memories USING hnsw (embedding vector_cosine_ops);

-- For pgvector 0.4.x: IVFFlat (requires data, run AFTER inserting rows)
-- CREATE INDEX IF NOT EXISTS idx_semantic_memories_embedding
-- ON phase3_semantic_memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- NOTE: For small datasets (<10k rows), no index is needed - sequential scan is fast enough

CREATE INDEX IF NOT EXISTS idx_semantic_memories_profile
ON phase3_semantic_memories(profile_id);

CREATE INDEX IF NOT EXISTS idx_semantic_memories_type
ON phase3_semantic_memories(memory_type);

-- Function for similarity search
CREATE OR REPLACE FUNCTION match_semantic_memories(
    query_embedding vector(1536),
    match_profile_id TEXT,
    match_count INT DEFAULT 5,
    match_threshold REAL DEFAULT 0.7
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    memory_type TEXT,
    importance REAL,
    similarity REAL,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sm.id,
        sm.content,
        sm.memory_type,
        sm.importance,
        1 - (sm.embedding <=> query_embedding) AS similarity,
        sm.metadata
    FROM phase3_semantic_memories sm
    WHERE sm.profile_id = match_profile_id
    AND 1 - (sm.embedding <=> query_embedding) > match_threshold
    ORDER BY sm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================
-- B4: LONG-TERM MEMORY
-- ============================================
CREATE TABLE IF NOT EXISTS phase3_longterm_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    memory_value JSONB NOT NULL,
    memory_type TEXT DEFAULT 'fact',  -- 'fact', 'preference', 'goal', 'insight'
    importance REAL DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),
    confidence REAL DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    source TEXT,  -- Where this memory came from
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,  -- Optional expiration
    UNIQUE(profile_id, memory_key)
);

CREATE INDEX IF NOT EXISTS idx_longterm_memories_profile
ON phase3_longterm_memories(profile_id);

CREATE INDEX IF NOT EXISTS idx_longterm_memories_type
ON phase3_longterm_memories(memory_type);

CREATE INDEX IF NOT EXISTS idx_longterm_memories_importance
ON phase3_longterm_memories(importance DESC);

-- ============================================
-- I1: FEEDBACK LEARNING
-- ============================================
CREATE TABLE IF NOT EXISTS phase3_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id TEXT NOT NULL,
    session_id TEXT,
    trace_id TEXT,  -- Langfuse trace reference
    agent_name TEXT,
    feedback_type TEXT NOT NULL,  -- 'thumbs_up', 'thumbs_down', 'rating', 'correction', 'comment'
    feedback_value REAL,  -- Numeric value if applicable (0-1 for ratings)
    feedback_text TEXT,  -- Text feedback if applicable
    context JSONB DEFAULT '{}',  -- What was the agent doing
    applied_learning JSONB,  -- What adjustment was made
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_profile ON phase3_feedback(profile_id);
CREATE INDEX IF NOT EXISTS idx_feedback_agent ON phase3_feedback(agent_name);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON phase3_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON phase3_feedback(created_at DESC);

-- ============================================
-- I2/I3: ADAPTIVE BEHAVIOR & PERSONALIZATION
-- ============================================
CREATE TABLE IF NOT EXISTS phase3_behavior_adaptations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id TEXT NOT NULL,
    behavior_key TEXT NOT NULL,  -- e.g., 'response_length', 'formality', 'detail_level'
    behavior_value JSONB NOT NULL,
    confidence REAL DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    sample_count INTEGER DEFAULT 1,
    last_feedback_id UUID REFERENCES phase3_feedback(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(profile_id, behavior_key)
);

CREATE INDEX IF NOT EXISTS idx_adaptations_profile ON phase3_behavior_adaptations(profile_id);

-- ============================================
-- I5: PATTERN RECOGNITION
-- ============================================
CREATE TABLE IF NOT EXISTS phase3_recognized_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id TEXT,  -- NULL for global patterns
    pattern_type TEXT NOT NULL,  -- 'query_pattern', 'time_pattern', 'topic_pattern'
    pattern_signature TEXT NOT NULL,
    pattern_data JSONB NOT NULL,
    occurrence_count INTEGER DEFAULT 1,
    confidence REAL DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    is_actionable BOOLEAN DEFAULT false,
    suggested_action JSONB
);

CREATE INDEX IF NOT EXISTS idx_patterns_profile ON phase3_recognized_patterns(profile_id);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON phase3_recognized_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON phase3_recognized_patterns(confidence DESC);

-- ============================================
-- D1: TOOL REGISTRY
-- ============================================
CREATE TABLE IF NOT EXISTS phase3_tool_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_name TEXT UNIQUE NOT NULL,
    tool_schema JSONB NOT NULL,  -- OpenAI function calling schema
    description TEXT,
    category TEXT,  -- 'search', 'compute', 'external', 'internal'
    is_active BOOLEAN DEFAULT true,
    requires_approval BOOLEAN DEFAULT false,
    avg_latency_ms REAL,
    success_rate REAL DEFAULT 1.0,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tool_registry_active ON phase3_tool_registry(is_active);
CREATE INDEX IF NOT EXISTS idx_tool_registry_category ON phase3_tool_registry(category);

-- ============================================
-- J5: COST TRACKING (Supplement to Langfuse)
-- ============================================
CREATE TABLE IF NOT EXISTS phase3_cost_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id TEXT,
    session_id TEXT,
    trace_id TEXT,  -- Langfuse trace reference
    agent_name TEXT,
    model TEXT NOT NULL,
    operation_type TEXT DEFAULT 'completion',  -- 'completion', 'embedding', 'moderation'
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    cost_usd NUMERIC(10, 6) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cost_profile ON phase3_cost_records(profile_id);
CREATE INDEX IF NOT EXISTS idx_cost_session ON phase3_cost_records(session_id);
CREATE INDEX IF NOT EXISTS idx_cost_created ON phase3_cost_records(created_at);
CREATE INDEX IF NOT EXISTS idx_cost_agent ON phase3_cost_records(agent_name);

-- Aggregation view for cost reporting
CREATE OR REPLACE VIEW phase3_cost_summary AS
SELECT
    profile_id,
    DATE(created_at) as date,
    agent_name,
    model,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(cost_usd) as total_cost_usd,
    COUNT(*) as request_count
FROM phase3_cost_records
GROUP BY profile_id, DATE(created_at), agent_name, model;

-- ============================================
-- B5/B6: MEMORY EXTRACTION & CONSOLIDATION LOG
-- ============================================
CREATE TABLE IF NOT EXISTS phase3_memory_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,  -- 'extraction', 'consolidation', 'decay'
    source_content TEXT,
    extracted_memories JSONB,
    memories_affected INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memory_ops_profile ON phase3_memory_operations(profile_id);
CREATE INDEX IF NOT EXISTS idx_memory_ops_type ON phase3_memory_operations(operation_type);

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================
COMMENT ON TABLE phase3_semantic_memories IS 'B3: Semantic memory with pgvector embeddings for similarity search';
COMMENT ON TABLE phase3_longterm_memories IS 'B4: Long-term memory with key-value storage';
COMMENT ON TABLE phase3_feedback IS 'I1: Feedback learning - stores user feedback for agent improvement';
COMMENT ON TABLE phase3_behavior_adaptations IS 'I2/I3: Adaptive behavior and personalization settings per profile';
COMMENT ON TABLE phase3_recognized_patterns IS 'I5: Pattern recognition - detected behavioral patterns';
COMMENT ON TABLE phase3_tool_registry IS 'D1: Tool registry for dynamic tool management';
COMMENT ON TABLE phase3_cost_records IS 'J5: Cost tracking for LLM usage';
COMMENT ON TABLE phase3_memory_operations IS 'B5/B6: Log of memory extraction and consolidation operations';
