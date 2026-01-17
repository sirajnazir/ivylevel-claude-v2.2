-- Phase 2A: v7.0 Important 10 Patterns
-- Database schema for new pattern tables
-- Migration: 035_phase2a_v7.0_tables.sql

-- =====================================================
-- G2: APPROVAL GATES
-- =====================================================

-- Approval requests table
CREATE TABLE IF NOT EXISTS approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('strategic', 'content', 'financial', 'crisis', 'deadline')),
    action_type TEXT NOT NULL,
    action_description TEXT,
    action_payload JSONB DEFAULT '{}',
    urgency TEXT DEFAULT 'standard' CHECK (urgency IN ('immediate', 'same_day', 'standard', 'advisory')),
    reason TEXT,
    agent_confidence FLOAT CHECK (agent_confidence >= 0 AND agent_confidence <= 1),
    agent_reasoning TEXT,
    alternatives JSONB DEFAULT '[]',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'withdrawn')),
    expires_at TIMESTAMPTZ,
    reviewer_id TEXT,
    reviewer_role TEXT,
    decision_reason TEXT,
    modifications JSONB,
    decided_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approval_requests_profile ON approval_requests(profile_id);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_category ON approval_requests(category);
CREATE INDEX IF NOT EXISTS idx_approval_requests_urgency ON approval_requests(urgency);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_approval_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_approval_requests_updated_at ON approval_requests;
CREATE TRIGGER trigger_approval_requests_updated_at
    BEFORE UPDATE ON approval_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_approval_requests_updated_at();

-- =====================================================
-- G5: HUMAN SHADOW MODE
-- =====================================================

-- Shadow proposals table
CREATE TABLE IF NOT EXISTS shadow_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    proposal_type TEXT NOT NULL CHECK (proposal_type IN ('message', 'action', 'plan_change')),
    proposed_content TEXT,
    proposed_payload JSONB DEFAULT '{}',
    student_message TEXT,
    relevant_context JSONB DEFAULT '{}',
    agent_reasoning TEXT,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    alternative_responses JSONB DEFAULT '[]',
    shadow_mode TEXT DEFAULT 'advisory' CHECK (shadow_mode IN ('off', 'advisory', 'review', 'approval')),
    final_content TEXT,
    modifications_made JSONB DEFAULT '[]',
    coach_notes TEXT,
    reviewed_at TIMESTAMPTZ,
    reviewer_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shadow_proposals_profile ON shadow_proposals(profile_id);
CREATE INDEX IF NOT EXISTS idx_shadow_proposals_shadow_mode ON shadow_proposals(shadow_mode);

-- Shadow reviews table
CREATE TABLE IF NOT EXISTS shadow_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID REFERENCES shadow_proposals(id) ON DELETE CASCADE,
    reviewer_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('approve', 'modify', 'reject', 'escalate')),
    modified_content TEXT,
    modifications_description JSONB DEFAULT '[]',
    quality_rating INT CHECK (quality_rating >= 1 AND quality_rating <= 5),
    feedback_for_agent TEXT,
    reviewed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shadow_reviews_proposal ON shadow_reviews(proposal_id);
CREATE INDEX IF NOT EXISTS idx_shadow_reviews_reviewer ON shadow_reviews(reviewer_id);

-- =====================================================
-- B2: EPISODIC MEMORY
-- =====================================================

-- Episodic memory table
CREATE TABLE IF NOT EXISTS episodic_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    situation TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    action_taken TEXT NOT NULL,
    approach_type TEXT,
    agent_name TEXT,
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'partial', 'failure')),
    outcome_details JSONB DEFAULT '{}',
    student_response TEXT,
    learnings JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    significance_score FLOAT DEFAULT 0.5 CHECK (significance_score >= 0 AND significance_score <= 1),
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_episodic_memory_profile ON episodic_memory(profile_id);
CREATE INDEX IF NOT EXISTS idx_episodic_memory_approach ON episodic_memory(approach_type);
CREATE INDEX IF NOT EXISTS idx_episodic_memory_outcome ON episodic_memory(outcome);
CREATE INDEX IF NOT EXISTS idx_episodic_memory_significance ON episodic_memory(significance_score);

-- Episodic memory similarity search function
CREATE OR REPLACE FUNCTION match_episodes(
    query_embedding vector(1536),
    match_count int,
    filter_profile_id uuid
)
RETURNS TABLE (
    id uuid,
    profile_id uuid,
    situation text,
    context jsonb,
    action_taken text,
    approach_type text,
    agent_name text,
    outcome text,
    outcome_details jsonb,
    learnings jsonb,
    significance_score float,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        em.id,
        em.profile_id,
        em.situation,
        em.context,
        em.action_taken,
        em.approach_type,
        em.agent_name,
        em.outcome,
        em.outcome_details,
        em.learnings,
        em.significance_score,
        1 - (em.embedding <=> query_embedding) as similarity
    FROM episodic_memory em
    WHERE em.profile_id = filter_profile_id
    ORDER BY em.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- =====================================================
-- PATTERN ANALYTICS
-- =====================================================

-- Pattern execution log (for J2 metrics enhancement)
CREATE TABLE IF NOT EXISTS pattern_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    session_id UUID,
    pattern_name TEXT NOT NULL,
    pattern_version TEXT DEFAULT 'v7.0',
    execution_type TEXT, -- 'approval', 'shadow', 'pivot', 'react', 'reflection', etc.
    input_context JSONB DEFAULT '{}',
    output_result JSONB DEFAULT '{}',
    duration_ms INT,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pattern_executions_profile ON pattern_executions(profile_id);
CREATE INDEX IF NOT EXISTS idx_pattern_executions_pattern ON pattern_executions(pattern_name);
CREATE INDEX IF NOT EXISTS idx_pattern_executions_session ON pattern_executions(session_id);

-- =====================================================
-- HELPER VIEWS
-- =====================================================

-- Pending approvals view
CREATE OR REPLACE VIEW pending_approvals AS
SELECT
    ar.*,
    p.first_name || ' ' || p.last_name as student_name
FROM approval_requests ar
LEFT JOIN profiles p ON ar.profile_id = p.id
WHERE ar.status = 'pending'
ORDER BY
    CASE ar.urgency
        WHEN 'immediate' THEN 1
        WHEN 'same_day' THEN 2
        WHEN 'standard' THEN 3
        WHEN 'advisory' THEN 4
    END,
    ar.created_at;

-- Shadow proposals awaiting review
CREATE OR REPLACE VIEW pending_shadow_reviews AS
SELECT
    sp.*,
    p.first_name || ' ' || p.last_name as student_name
FROM shadow_proposals sp
LEFT JOIN profiles p ON sp.profile_id = p.id
WHERE sp.shadow_mode IN ('review', 'approval')
    AND sp.reviewed_at IS NULL
ORDER BY sp.created_at;

-- Approach success rates view
CREATE OR REPLACE VIEW approach_success_rates AS
SELECT
    profile_id,
    approach_type,
    COUNT(*) as total_episodes,
    COUNT(*) FILTER (WHERE outcome = 'success') as successes,
    ROUND(
        (COUNT(*) FILTER (WHERE outcome = 'success'))::numeric /
        NULLIF(COUNT(*), 0) * 100, 2
    ) as success_rate_percent
FROM episodic_memory
GROUP BY profile_id, approach_type
HAVING COUNT(*) >= 3
ORDER BY profile_id, success_rate_percent DESC;

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

-- Enable RLS on new tables
ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE shadow_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE shadow_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE episodic_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE pattern_executions ENABLE ROW LEVEL SECURITY;

-- Policies (adjust based on your auth setup)
-- These are permissive for now - tighten based on your needs

CREATE POLICY "approval_requests_select" ON approval_requests
    FOR SELECT USING (true);

CREATE POLICY "approval_requests_insert" ON approval_requests
    FOR INSERT WITH CHECK (true);

CREATE POLICY "approval_requests_update" ON approval_requests
    FOR UPDATE USING (true);

CREATE POLICY "shadow_proposals_select" ON shadow_proposals
    FOR SELECT USING (true);

CREATE POLICY "shadow_proposals_insert" ON shadow_proposals
    FOR INSERT WITH CHECK (true);

CREATE POLICY "shadow_reviews_select" ON shadow_reviews
    FOR SELECT USING (true);

CREATE POLICY "shadow_reviews_insert" ON shadow_reviews
    FOR INSERT WITH CHECK (true);

CREATE POLICY "episodic_memory_select" ON episodic_memory
    FOR SELECT USING (true);

CREATE POLICY "episodic_memory_insert" ON episodic_memory
    FOR INSERT WITH CHECK (true);

CREATE POLICY "pattern_executions_select" ON pattern_executions
    FOR SELECT USING (true);

CREATE POLICY "pattern_executions_insert" ON pattern_executions
    FOR INSERT WITH CHECK (true);

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE approval_requests IS 'G2: Approval Gates - Human approval requests for high-stakes actions';
COMMENT ON TABLE shadow_proposals IS 'G5: Human Shadow Mode - Agent proposals for coach review';
COMMENT ON TABLE shadow_reviews IS 'G5: Human Shadow Mode - Coach reviews of proposals';
COMMENT ON TABLE episodic_memory IS 'B2: Episodic Memory - Past experiences for learning';
COMMENT ON TABLE pattern_executions IS 'Phase 2A pattern execution logging for analytics';
COMMENT ON FUNCTION match_episodes IS 'B2: Semantic search for similar past episodes';
