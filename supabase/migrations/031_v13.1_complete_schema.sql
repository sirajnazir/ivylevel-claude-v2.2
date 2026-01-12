-- migrations/031_v13.1_complete_schema.sql
-- IvyQuest v13.1/v13.2 Complete Database Schema
-- Adds 6 new tables to support memory system architecture
--
-- Run with: psql -d ivyquest -f 031_v13.1_complete_schema.sql
-- Or via Supabase migrations

-- ============================================================
-- PREREQUISITES
-- ============================================================

-- Ensure pgvector extension is installed
CREATE EXTENSION IF NOT EXISTS vector;

-- Ensure update_updated_at_column function exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Table 1: agent_memories (May already exist from v13.0)
-- Basic agent observations and learnings
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    
    -- Observation data
    observation JSONB NOT NULL,
    importance FLOAT DEFAULT 0.5 CHECK (importance >= 0 AND importance <= 1),
    tags TEXT[],
    
    -- Semantic search
    embedding vector(1536),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for agent_memories
CREATE INDEX IF NOT EXISTS idx_agent_memories_profile ON agent_memories(profile_id);
CREATE INDEX IF NOT EXISTS idx_agent_memories_agent ON agent_memories(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_memories_importance ON agent_memories(importance DESC);
CREATE INDEX IF NOT EXISTS idx_agent_memories_embedding ON agent_memories 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- Table 2: profile_snapshots (NEW)
-- Track profile identity evolution over time
-- ============================================================

CREATE TABLE IF NOT EXISTS profile_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    snapshot_type TEXT NOT NULL CHECK (snapshot_type IN (
        'assessment', 'milestone', 'quarterly', 'manual', 'agent_interaction'
    )),

    -- Identity snapshot
    narrative_dna TEXT,
    brand_statement TEXT,
    archetype TEXT,
    archetype_confidence FLOAT,

    -- Scores snapshot
    cri_score FLOAT,
    eds_score FLOAT,
    spike_score FLOAT,

    -- Activities snapshot
    activities_count INTEGER DEFAULT 0,
    projects_count INTEGER DEFAULT 0,
    awards_count INTEGER DEFAULT 0,

    -- Change tracking
    change_summary TEXT,
    changed_fields JSONB,
    trigger_event TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for profile_snapshots
CREATE INDEX IF NOT EXISTS idx_profile_snapshots_profile 
    ON profile_snapshots(profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profile_snapshots_type 
    ON profile_snapshots(snapshot_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profile_snapshots_archetype 
    ON profile_snapshots(archetype);

-- ============================================================
-- Table 3: coaching_knowledge (NEW)
-- Jenny's coaching methodology for RAG retrieval
-- ============================================================

CREATE TABLE IF NOT EXISTS coaching_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Categorization
    category TEXT NOT NULL CHECK (category IN (
        'crisis_response', 'narrative', 'execution', 'awards',
        'opportunity', 'time_management', 'essay_strategy', 'general'
    )),
    subcategory TEXT,

    -- Content
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_type TEXT CHECK (source_type IN (
        'jenny_transcript', 'golden_example', 'methodology', 'pattern'
    )),

    -- Applicability
    applicable_archetypes TEXT[],
    applicable_spikes TEXT[],
    applicable_situations TEXT[],

    -- Quality
    effectiveness_score FLOAT DEFAULT 0.8 CHECK (
        effectiveness_score >= 0 AND effectiveness_score <= 1
    ),
    usage_count INTEGER DEFAULT 0,

    -- Semantic search
    embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for coaching_knowledge
CREATE INDEX IF NOT EXISTS idx_coaching_knowledge_category 
    ON coaching_knowledge(category);
CREATE INDEX IF NOT EXISTS idx_coaching_knowledge_source 
    ON coaching_knowledge(source_type);
CREATE INDEX IF NOT EXISTS idx_coaching_knowledge_effectiveness 
    ON coaching_knowledge(effectiveness_score DESC);
CREATE INDEX IF NOT EXISTS idx_coaching_knowledge_embedding 
    ON coaching_knowledge USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- Table 4: outcome_history (NEW)
-- Track awards won/lost, programs completed, etc.
-- ============================================================

CREATE TABLE IF NOT EXISTS outcome_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Outcome classification
    outcome_type TEXT NOT NULL CHECK (outcome_type IN (
        'award', 'program', 'project', 'essay', 'application'
    )),
    outcome_subtype TEXT NOT NULL CHECK (outcome_subtype IN (
        'won', 'lost', 'completed', 'abandoned', 'submitted', 'accepted', 'rejected'
    )),

    -- Details
    entity_name TEXT NOT NULL,
    entity_id UUID,

    -- Prediction vs reality
    success BOOLEAN NOT NULL,
    predicted_probability FLOAT,
    actual_vs_predicted FLOAT GENERATED ALWAYS AS (
        CASE WHEN predicted_probability IS NOT NULL
        THEN (CASE WHEN success THEN 1.0 ELSE 0.0 END) - predicted_probability
        ELSE NULL END
    ) STORED,

    -- Analysis
    contributing_factors JSONB,
    lessons_learned TEXT,

    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for outcome_history
CREATE INDEX IF NOT EXISTS idx_outcome_history_profile 
    ON outcome_history(profile_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_outcome_history_type 
    ON outcome_history(outcome_type, success);
CREATE INDEX IF NOT EXISTS idx_outcome_history_entity 
    ON outcome_history(entity_name);

-- ============================================================
-- Table 5: interaction_memory (NEW)
-- Conversation summaries for long-term recall
-- ============================================================

CREATE TABLE IF NOT EXISTS interaction_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Session info
    session_id TEXT NOT NULL,
    agent_involved TEXT[],

    -- Summary
    summary TEXT NOT NULL,
    key_topics TEXT[],

    -- Decisions & actions
    key_decisions JSONB,
    action_items JSONB,

    -- Emotional context
    emotional_state TEXT CHECK (emotional_state IN (
        'positive', 'neutral', 'stressed', 'anxious', 'excited'
    )),

    -- Semantic search
    embedding vector(1536),

    -- Timing
    interaction_start TIMESTAMPTZ,
    interaction_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for interaction_memory
CREATE INDEX IF NOT EXISTS idx_interaction_memory_profile 
    ON interaction_memory(profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_interaction_memory_session 
    ON interaction_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_interaction_memory_agents 
    ON interaction_memory USING gin(agent_involved);
CREATE INDEX IF NOT EXISTS idx_interaction_memory_topics 
    ON interaction_memory USING gin(key_topics);
CREATE INDEX IF NOT EXISTS idx_interaction_memory_embedding 
    ON interaction_memory USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- Table 6: learned_patterns (NEW)
-- Auto-extracted success/failure patterns
-- ============================================================

CREATE TABLE IF NOT EXISTS learned_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Pattern classification
    pattern_type TEXT NOT NULL CHECK (pattern_type IN (
        'award_success', 'award_failure', 'crisis_resolution',
        'time_management', 'motivation', 'essay_structure', 'general'
    )),
    pattern_name TEXT NOT NULL,

    -- Pattern definition
    trigger_conditions JSONB NOT NULL,
    successful_responses JSONB NOT NULL,
    failed_approaches JSONB,

    -- Statistics
    observation_count INTEGER DEFAULT 1,
    success_rate FLOAT DEFAULT 1.0 CHECK (success_rate >= 0 AND success_rate <= 1),
    last_observed_at TIMESTAMPTZ DEFAULT NOW(),

    -- Applicability
    applicable_archetypes TEXT[],
    applicable_spikes TEXT[],

    -- Semantic search
    embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for learned_patterns
CREATE INDEX IF NOT EXISTS idx_learned_patterns_type 
    ON learned_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_learned_patterns_success_rate 
    ON learned_patterns(success_rate DESC);
CREATE INDEX IF NOT EXISTS idx_learned_patterns_embedding 
    ON learned_patterns USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- Table 7: semantic_chunks (NEW)
-- RAG chunks for any document/content
-- ============================================================

CREATE TABLE IF NOT EXISTS semantic_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source reference
    source_table TEXT NOT NULL,
    source_id UUID NOT NULL,
    source_field TEXT,

    -- Chunk info
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_tokens INTEGER,

    -- Metadata
    metadata JSONB,

    -- Semantic search
    embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for semantic_chunks
CREATE INDEX IF NOT EXISTS idx_semantic_chunks_source 
    ON semantic_chunks(source_table, source_id);
CREATE INDEX IF NOT EXISTS idx_semantic_chunks_embedding 
    ON semantic_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- SEMANTIC SEARCH FUNCTIONS
-- ============================================================

-- Function: Match agent memories
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_profile_id UUID DEFAULT NULL,
    filter_agent_id TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    profile_id UUID,
    agent_id TEXT,
    observation JSONB,
    importance FLOAT,
    tags TEXT[],
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        am.id,
        am.profile_id,
        am.agent_id,
        am.observation,
        am.importance,
        am.tags,
        1 - (am.embedding <=> query_embedding) AS similarity,
        am.created_at
    FROM agent_memories am
    WHERE
        (filter_profile_id IS NULL OR am.profile_id = filter_profile_id)
        AND (filter_agent_id IS NULL OR am.agent_id = filter_agent_id)
        AND am.embedding IS NOT NULL
        AND 1 - (am.embedding <=> query_embedding) > match_threshold
    ORDER BY am.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function: Match coaching knowledge
CREATE OR REPLACE FUNCTION match_coaching_knowledge(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_category TEXT DEFAULT NULL,
    filter_archetype TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    category TEXT,
    title TEXT,
    content TEXT,
    source_type TEXT,
    effectiveness_score FLOAT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ck.id,
        ck.category,
        ck.title,
        ck.content,
        ck.source_type,
        ck.effectiveness_score,
        1 - (ck.embedding <=> query_embedding) AS similarity
    FROM coaching_knowledge ck
    WHERE
        (filter_category IS NULL OR ck.category = filter_category)
        AND (filter_archetype IS NULL OR filter_archetype = ANY(ck.applicable_archetypes))
        AND ck.embedding IS NOT NULL
        AND 1 - (ck.embedding <=> query_embedding) > match_threshold
    ORDER BY ck.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function: Match semantic chunks
CREATE OR REPLACE FUNCTION match_semantic_chunks(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_source_table TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    source_table TEXT,
    source_id UUID,
    chunk_text TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sc.id,
        sc.source_table,
        sc.source_id,
        sc.chunk_text,
        sc.metadata,
        1 - (sc.embedding <=> query_embedding) AS similarity
    FROM semantic_chunks sc
    WHERE
        (filter_source_table IS NULL OR sc.source_table = filter_source_table)
        AND sc.embedding IS NOT NULL
        AND 1 - (sc.embedding <=> query_embedding) > match_threshold
    ORDER BY sc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

ALTER TABLE agent_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE coaching_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE outcome_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE learned_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE semantic_chunks ENABLE ROW LEVEL SECURITY;

-- Permissive policies for development
-- TODO: Restrict for production based on auth.uid()

CREATE POLICY IF NOT EXISTS "Allow all agent_memories" ON agent_memories 
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow all profile_snapshots" ON profile_snapshots 
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow all coaching_knowledge" ON coaching_knowledge 
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow all outcome_history" ON outcome_history 
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow all interaction_memory" ON interaction_memory 
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow all learned_patterns" ON learned_patterns 
    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow all semantic_chunks" ON semantic_chunks 
    FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Update timestamp triggers
CREATE TRIGGER update_agent_memories_timestamp
    BEFORE UPDATE ON agent_memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_coaching_knowledge_timestamp
    BEFORE UPDATE ON coaching_knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learned_patterns_timestamp
    BEFORE UPDATE ON learned_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE agent_memories IS 'v13.1: Agent observations and learnings';
COMMENT ON TABLE profile_snapshots IS 'v13.1: Track profile identity evolution over time';
COMMENT ON TABLE coaching_knowledge IS 'v13.1: Jenny methodology and golden examples for RAG';
COMMENT ON TABLE outcome_history IS 'v13.1: Track awards, programs, projects for pattern learning';
COMMENT ON TABLE interaction_memory IS 'v13.1: Conversation summaries for long-term recall';
COMMENT ON TABLE learned_patterns IS 'v13.1: Auto-extracted success/failure patterns';
COMMENT ON TABLE semantic_chunks IS 'v13.1: RAG chunks for semantic search';

COMMENT ON FUNCTION match_memories IS 'Semantic search for agent memories';
COMMENT ON FUNCTION match_coaching_knowledge IS 'Semantic search for coaching knowledge';
COMMENT ON FUNCTION match_semantic_chunks IS 'Semantic search for document chunks';

-- ============================================================
-- VERIFICATION
-- ============================================================

-- Verify all tables exist
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'agent_memories', 'profile_snapshots', 'coaching_knowledge',
        'outcome_history', 'interaction_memory', 'learned_patterns', 
        'semantic_chunks'
    );
    
    IF table_count = 7 THEN
        RAISE NOTICE 'SUCCESS: All 7 v13.1 tables created';
    ELSE
        RAISE WARNING 'INCOMPLETE: Only % of 7 tables created', table_count;
    END IF;
END;
$$;
