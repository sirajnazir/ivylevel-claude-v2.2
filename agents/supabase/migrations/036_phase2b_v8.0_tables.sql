-- Phase 2B v8.0 Database Migration
-- 15 Enhancement Patterns - Weeks 9-12
--
-- ADDITIVE ONLY - Does not modify any existing tables
-- All new tables use phase2b_* prefix

-- ============================================
-- C1: SESSION CONTEXT - Session History
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_session_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    message_role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes for efficient retrieval
    CONSTRAINT session_history_role_check CHECK (message_role IN ('user', 'assistant', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_phase2b_session_history_session
    ON phase2b_session_history(session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_session_history_profile
    ON phase2b_session_history(profile_id, timestamp DESC);


-- ============================================
-- J1: REASONING TRACES - Trace Storage
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_reasoning_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id TEXT UNIQUE NOT NULL,
    profile_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    input_message TEXT NOT NULL,
    final_output TEXT,
    success BOOLEAN DEFAULT TRUE,
    total_events INTEGER DEFAULT 0,
    tool_calls INTEGER DEFAULT 0,
    reflections INTEGER DEFAULT 0,
    total_duration_ms INTEGER DEFAULT 0,
    events JSONB DEFAULT '[]',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phase2b_reasoning_traces_profile
    ON phase2b_reasoning_traces(profile_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_reasoning_traces_session
    ON phase2b_reasoning_traces(session_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_reasoning_traces_agent
    ON phase2b_reasoning_traces(agent_name, started_at DESC);


-- ============================================
-- J3: AUDIT TRAIL - Audit Log Storage
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id TEXT UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    actor_id TEXT NOT NULL,
    actor_type TEXT NOT NULL,  -- 'user', 'agent', 'system', 'coach', 'admin'
    action TEXT NOT NULL,  -- 'create', 'read', 'update', 'delete', 'execute', 'approve', 'reject', 'escalate', 'login', 'logout'
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    details JSONB DEFAULT '{}',
    session_id TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,

    CONSTRAINT audit_actor_type_check CHECK (actor_type IN ('user', 'agent', 'system', 'coach', 'admin')),
    CONSTRAINT audit_action_check CHECK (action IN ('create', 'read', 'update', 'delete', 'execute', 'approve', 'reject', 'escalate', 'login', 'logout'))
);

CREATE INDEX IF NOT EXISTS idx_phase2b_audit_trail_actor
    ON phase2b_audit_trail(actor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_audit_trail_resource
    ON phase2b_audit_trail(resource_type, resource_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_audit_trail_action
    ON phase2b_audit_trail(action, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_audit_trail_session
    ON phase2b_audit_trail(session_id, timestamp DESC);


-- ============================================
-- I4: STRATEGY EFFECTIVENESS - Applications
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_strategy_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id TEXT UNIQUE NOT NULL,
    strategy TEXT NOT NULL,
    context_type TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    input_situation TEXT NOT NULL,
    strategy_response TEXT NOT NULL,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    outcome TEXT,  -- 'success', 'partial', 'failure', 'unknown'
    outcome_reason TEXT,
    measured_at TIMESTAMPTZ,
    student_response_positive BOOLEAN,
    task_completed BOOLEAN,
    engagement_score FLOAT,

    CONSTRAINT strategy_outcome_check CHECK (outcome IS NULL OR outcome IN ('success', 'partial', 'failure', 'unknown'))
);

CREATE INDEX IF NOT EXISTS idx_phase2b_strategy_applications_strategy
    ON phase2b_strategy_applications(strategy, context_type, applied_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_strategy_applications_profile
    ON phase2b_strategy_applications(profile_id, strategy, applied_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_strategy_applications_outcome
    ON phase2b_strategy_applications(outcome, strategy);


-- ============================================
-- A11: PLANNING - Plan Storage
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id TEXT UNIQUE NOT NULL,
    profile_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    goal TEXT NOT NULL,
    steps JSONB NOT NULL DEFAULT '[]',
    total_steps INTEGER DEFAULT 0,
    completed_steps INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'failed', 'replanned'
    replan_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    CONSTRAINT plan_status_check CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'replanned'))
);

CREATE INDEX IF NOT EXISTS idx_phase2b_plans_profile
    ON phase2b_plans(profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_plans_status
    ON phase2b_plans(status, created_at DESC);


-- ============================================
-- E2: LLM-AS-JUDGE - Judgment Storage
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_judgments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    judgment_id TEXT UNIQUE NOT NULL,
    profile_id TEXT,
    session_id TEXT,
    content_type TEXT NOT NULL,
    content TEXT NOT NULL,
    criteria JSONB NOT NULL,
    scores JSONB NOT NULL,
    overall_score FLOAT NOT NULL,
    passed BOOLEAN NOT NULL,
    feedback TEXT,
    judge_model TEXT,
    judged_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phase2b_judgments_profile
    ON phase2b_judgments(profile_id, judged_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_judgments_content_type
    ON phase2b_judgments(content_type, judged_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_judgments_passed
    ON phase2b_judgments(passed, content_type);


-- ============================================
-- E4: QUALITY SCORING - Quality Scores Storage
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_quality_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    score_id TEXT UNIQUE NOT NULL,
    profile_id TEXT,
    session_id TEXT,
    content_type TEXT NOT NULL,
    content TEXT NOT NULL,
    dimension_scores JSONB NOT NULL,
    overall_score FLOAT NOT NULL,
    meets_threshold BOOLEAN NOT NULL,
    method TEXT NOT NULL,  -- 'heuristic', 'llm'
    scored_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phase2b_quality_scores_profile
    ON phase2b_quality_scores(profile_id, scored_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_quality_scores_content_type
    ON phase2b_quality_scores(content_type, scored_at DESC);


-- ============================================
-- G4: ATOMIC OPERATIONS - Operation Log
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_atomic_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id TEXT UNIQUE NOT NULL,
    operation_name TEXT NOT NULL,
    profile_id TEXT,
    session_id TEXT,
    input_data JSONB,
    result_data JSONB,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    rolled_back BOOLEAN DEFAULT FALSE,
    rollback_reason TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_phase2b_atomic_operations_profile
    ON phase2b_atomic_operations(profile_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_atomic_operations_success
    ON phase2b_atomic_operations(success, started_at DESC);


-- ============================================
-- H2/H3: RECOVERY - Circuit Breaker State
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_circuit_breaker_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT UNIQUE NOT NULL,
    state TEXT NOT NULL DEFAULT 'closed',  -- 'closed', 'open', 'half_open'
    failure_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_failure_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    half_open_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT cb_state_check CHECK (state IN ('closed', 'open', 'half_open'))
);

CREATE INDEX IF NOT EXISTS idx_phase2b_circuit_breaker_state
    ON phase2b_circuit_breaker_state(state, updated_at DESC);


-- ============================================
-- A9: PROMPT CHAINING - Chain Execution Log
-- ============================================

CREATE TABLE IF NOT EXISTS phase2b_chain_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chain_id TEXT UNIQUE NOT NULL,
    chain_name TEXT NOT NULL,
    profile_id TEXT,
    session_id TEXT,
    initial_context JSONB,
    steps_completed INTEGER DEFAULT 0,
    total_steps INTEGER NOT NULL,
    final_output TEXT,
    success BOOLEAN,
    error_message TEXT,
    total_duration_ms INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_phase2b_chain_executions_profile
    ON phase2b_chain_executions(profile_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase2b_chain_executions_chain_name
    ON phase2b_chain_executions(chain_name, started_at DESC);


-- ============================================
-- Enable Row Level Security (RLS) for all tables
-- ============================================

ALTER TABLE phase2b_session_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_reasoning_traces ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_audit_trail ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_strategy_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_judgments ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_quality_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_atomic_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_circuit_breaker_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase2b_chain_executions ENABLE ROW LEVEL SECURITY;


-- ============================================
-- Grant permissions to authenticated users
-- ============================================

GRANT SELECT, INSERT, UPDATE ON phase2b_session_history TO authenticated;
GRANT SELECT, INSERT, UPDATE ON phase2b_reasoning_traces TO authenticated;
GRANT SELECT, INSERT ON phase2b_audit_trail TO authenticated;
GRANT SELECT, INSERT, UPDATE ON phase2b_strategy_applications TO authenticated;
GRANT SELECT, INSERT, UPDATE ON phase2b_plans TO authenticated;
GRANT SELECT, INSERT ON phase2b_judgments TO authenticated;
GRANT SELECT, INSERT ON phase2b_quality_scores TO authenticated;
GRANT SELECT, INSERT, UPDATE ON phase2b_atomic_operations TO authenticated;
GRANT SELECT, INSERT, UPDATE ON phase2b_circuit_breaker_state TO authenticated;
GRANT SELECT, INSERT, UPDATE ON phase2b_chain_executions TO authenticated;

-- Grant to service role (for backend operations)
GRANT ALL ON phase2b_session_history TO service_role;
GRANT ALL ON phase2b_reasoning_traces TO service_role;
GRANT ALL ON phase2b_audit_trail TO service_role;
GRANT ALL ON phase2b_strategy_applications TO service_role;
GRANT ALL ON phase2b_plans TO service_role;
GRANT ALL ON phase2b_judgments TO service_role;
GRANT ALL ON phase2b_quality_scores TO service_role;
GRANT ALL ON phase2b_atomic_operations TO service_role;
GRANT ALL ON phase2b_circuit_breaker_state TO service_role;
GRANT ALL ON phase2b_chain_executions TO service_role;


-- ============================================
-- Comments for documentation
-- ============================================

COMMENT ON TABLE phase2b_session_history IS 'C1: Session Context - Stores message history for session context';
COMMENT ON TABLE phase2b_reasoning_traces IS 'J1: Reasoning Traces - Captures agent reasoning for debugging';
COMMENT ON TABLE phase2b_audit_trail IS 'J3: Audit Trail - Complete audit logging for compliance';
COMMENT ON TABLE phase2b_strategy_applications IS 'I4: Strategy Effectiveness - Tracks coaching strategy outcomes';
COMMENT ON TABLE phase2b_plans IS 'A11: Planning - Stores multi-step plans';
COMMENT ON TABLE phase2b_judgments IS 'E2: LLM-as-Judge - Stores judgment results';
COMMENT ON TABLE phase2b_quality_scores IS 'E4: Quality Scoring - Stores quality score results';
COMMENT ON TABLE phase2b_atomic_operations IS 'G4: Atomic Operations - Logs transactional operations';
COMMENT ON TABLE phase2b_circuit_breaker_state IS 'H2/H3: Recovery - Circuit breaker state for services';
COMMENT ON TABLE phase2b_chain_executions IS 'A9: Prompt Chaining - Logs chain executions';
