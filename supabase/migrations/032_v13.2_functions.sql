-- migrations/032_v13.2_functions.sql
-- IvyQuest v13.2 Additional SQL Functions
--
-- Adds:
-- - match_interaction_memory(): Semantic search for interaction memories
-- - get_profile_evolution(): Get profile evolution timeline
--
-- Run with: psql -d ivyquest -f 032_v13.2_functions.sql

-- ============================================================
-- v13.2 ADDITIONAL SQL FUNCTIONS
-- ============================================================

-- Function: Match interaction memory semantically
CREATE OR REPLACE FUNCTION match_interaction_memory(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_profile_id UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    profile_id UUID,
    session_id TEXT,
    agent_involved TEXT[],
    summary TEXT,
    key_topics TEXT[],
    key_decisions JSONB,
    action_items JSONB,
    emotional_state TEXT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        im.id,
        im.profile_id,
        im.session_id,
        im.agent_involved,
        im.summary,
        im.key_topics,
        im.key_decisions,
        im.action_items,
        im.emotional_state,
        1 - (im.embedding <=> query_embedding) AS similarity,
        im.created_at
    FROM interaction_memory im
    WHERE
        (filter_profile_id IS NULL OR im.profile_id = filter_profile_id)
        AND im.embedding IS NOT NULL
        AND 1 - (im.embedding <=> query_embedding) > match_threshold
    ORDER BY im.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function: Get profile evolution summary
CREATE OR REPLACE FUNCTION get_profile_evolution(
    target_profile_id UUID,
    lookback_days INT DEFAULT 90
)
RETURNS TABLE (
    snapshot_date DATE,
    snapshot_type TEXT,
    archetype TEXT,
    archetype_confidence FLOAT,
    cri_score FLOAT,
    eds_score FLOAT,
    spike_score FLOAT,
    activities_count INT,
    projects_count INT,
    awards_count INT,
    change_summary TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE(ps.created_at) AS snapshot_date,
        ps.snapshot_type,
        ps.archetype,
        ps.archetype_confidence,
        ps.cri_score,
        ps.eds_score,
        ps.spike_score,
        ps.activities_count,
        ps.projects_count,
        ps.awards_count,
        ps.change_summary
    FROM profile_snapshots ps
    WHERE
        ps.profile_id = target_profile_id
        AND ps.created_at > NOW() - (lookback_days || ' days')::INTERVAL
    ORDER BY ps.created_at DESC;
END;
$$;

-- Function: Get outcome statistics by type
CREATE OR REPLACE FUNCTION get_outcome_statistics(
    target_profile_id UUID,
    target_outcome_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    outcome_type TEXT,
    total_count BIGINT,
    success_count BIGINT,
    failure_count BIGINT,
    success_rate FLOAT,
    avg_predicted_probability FLOAT,
    calibration_error FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        oh.outcome_type,
        COUNT(*) AS total_count,
        SUM(CASE WHEN oh.success THEN 1 ELSE 0 END) AS success_count,
        SUM(CASE WHEN NOT oh.success THEN 1 ELSE 0 END) AS failure_count,
        AVG(CASE WHEN oh.success THEN 1.0 ELSE 0.0 END) AS success_rate,
        AVG(oh.predicted_probability) AS avg_predicted_probability,
        AVG(ABS(oh.actual_vs_predicted)) AS calibration_error
    FROM outcome_history oh
    WHERE
        oh.profile_id = target_profile_id
        AND (target_outcome_type IS NULL OR oh.outcome_type = target_outcome_type)
    GROUP BY oh.outcome_type
    ORDER BY total_count DESC;
END;
$$;

-- Function: Get active interaction topics (last 30 days)
CREATE OR REPLACE FUNCTION get_active_topics(
    target_profile_id UUID,
    lookback_days INT DEFAULT 30,
    min_mentions INT DEFAULT 2
)
RETURNS TABLE (
    topic TEXT,
    mention_count BIGINT,
    last_mentioned TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        unnest(im.key_topics) AS topic,
        COUNT(*) AS mention_count,
        MAX(im.created_at) AS last_mentioned
    FROM interaction_memory im
    WHERE
        im.profile_id = target_profile_id
        AND im.created_at > NOW() - (lookback_days || ' days')::INTERVAL
    GROUP BY unnest(im.key_topics)
    HAVING COUNT(*) >= min_mentions
    ORDER BY mention_count DESC, last_mentioned DESC
    LIMIT 20;
END;
$$;

-- Function: Get pending action items
CREATE OR REPLACE FUNCTION get_pending_action_items(
    target_profile_id UUID
)
RETURNS TABLE (
    session_id TEXT,
    action_item JSONB,
    interaction_date TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        im.session_id,
        jsonb_array_elements(im.action_items) AS action_item,
        im.created_at AS interaction_date
    FROM interaction_memory im
    WHERE
        im.profile_id = target_profile_id
        AND im.action_items IS NOT NULL
        AND jsonb_array_length(im.action_items) > 0
    ORDER BY im.created_at DESC
    LIMIT 50;
END;
$$;

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON FUNCTION match_interaction_memory IS 'v13.2: Semantic search for interaction memories';
COMMENT ON FUNCTION get_profile_evolution IS 'v13.2: Get profile evolution timeline';
COMMENT ON FUNCTION get_outcome_statistics IS 'v13.2: Get outcome statistics by type';
COMMENT ON FUNCTION get_active_topics IS 'v13.2: Get frequently discussed topics';
COMMENT ON FUNCTION get_pending_action_items IS 'v13.2: Get pending action items from interactions';

-- ============================================================
-- VERIFICATION
-- ============================================================

DO $$
DECLARE
    function_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO function_count
    FROM information_schema.routines
    WHERE routine_schema = 'public'
    AND routine_name IN (
        'match_memories', 'match_coaching_knowledge', 'match_semantic_chunks',
        'match_interaction_memory', 'get_profile_evolution', 
        'get_outcome_statistics', 'get_active_topics', 'get_pending_action_items'
    );
    
    IF function_count >= 4 THEN
        RAISE NOTICE 'SUCCESS: v13.2 functions created (% total search functions)', function_count;
    ELSE
        RAISE WARNING 'INCOMPLETE: Only % functions found', function_count;
    END IF;
END;
$$;
