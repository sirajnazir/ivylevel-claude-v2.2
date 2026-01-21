-- ═══════════════════════════════════════════════════════════════════════════════
-- IvyLevel Autonomous Intelligence Layer - Database Schema
-- Version: 1.0
--
-- CRITICAL: These are NEW tables only. NO modifications to existing tables.
-- Run this migration in Supabase SQL Editor.
-- ═══════════════════════════════════════════════════════════════════════════════

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- ═══════════════════════════════════════════════════════════════════════════════
-- NEW TABLE: coaching_assets
-- Stores all coaching assets (techniques, templates, references, etc.)
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS coaching_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    name VARCHAR(255) NOT NULL,
    version INT DEFAULT 1,

    -- Classification
    asset_type VARCHAR(50) NOT NULL,  -- technique, template, reference, etc.
    domain VARCHAR(50) NOT NULL,       -- assessment, execution, awards, etc.
    secondary_domains TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',

    -- Content (JSONB for flexibility)
    content JSONB NOT NULL,

    -- Trigger conditions
    trigger_config JSONB DEFAULT '{}',

    -- Applicability
    applicability JSONB DEFAULT '{}',

    -- Provenance
    provenance JSONB DEFAULT '{}',

    -- Effectiveness (learned over time)
    effectiveness JSONB DEFAULT '{
        "times_used": 0,
        "success_count": 0,
        "global_success_rate": 0,
        "by_archetype": {},
        "confidence_level": 0
    }',

    -- Embedding for vector search
    embedding vector(1536),

    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for coaching_assets
CREATE INDEX IF NOT EXISTS idx_coaching_assets_type ON coaching_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_coaching_assets_domain ON coaching_assets(domain);
CREATE INDEX IF NOT EXISTS idx_coaching_assets_tags ON coaching_assets USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_coaching_assets_active ON coaching_assets(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_coaching_assets_embedding ON coaching_assets USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ═══════════════════════════════════════════════════════════════════════════════
-- NEW TABLE: asset_usage
-- Tracks when assets are used and outcomes
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS asset_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES coaching_assets(id) ON DELETE CASCADE NOT NULL,
    profile_id UUID NOT NULL,  -- References existing profiles table

    -- Context
    agent_name VARCHAR(100),
    trigger_context TEXT,
    lifecycle_stage VARCHAR(50),

    -- Outcome
    outcome JSONB,  -- {success: bool, notes: str, rating: int}

    -- Student context at time of use
    student_archetype VARCHAR(100),
    student_phase VARCHAR(50),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asset_usage_asset ON asset_usage(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_usage_profile ON asset_usage(profile_id);
CREATE INDEX IF NOT EXISTS idx_asset_usage_archetype ON asset_usage(student_archetype);
CREATE INDEX IF NOT EXISTS idx_asset_usage_created ON asset_usage(created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- NEW TABLE: student_psychobehavioral
-- Stores learned behavioral patterns per student
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS student_psychobehavioral (
    profile_id UUID PRIMARY KEY,  -- References existing profiles

    -- Response Patterns
    pressure_response VARCHAR(50) DEFAULT 'thrives',
    feedback_reception VARCHAR(50) DEFAULT 'direct',
    motivation_style VARCHAR(50) DEFAULT 'intrinsic',
    celebration_preference VARCHAR(50) DEFAULT 'private',

    -- Work Patterns
    energy_pattern VARCHAR(50) DEFAULT 'evening',
    task_approach VARCHAR(50) DEFAULT 'sequential',
    overwhelm_threshold FLOAT DEFAULT 0.7,
    optimal_pace FLOAT DEFAULT 5.0,

    -- Communication
    communication_style VARCHAR(50) DEFAULT 'concise',
    check_in_frequency VARCHAR(50) DEFAULT 'weekly',

    -- Risk
    risk_tolerance VARCHAR(50) DEFAULT 'balanced',
    failure_recovery VARCHAR(50) DEFAULT 'quick',

    -- Learned patterns
    learned_from_interactions JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- NEW TABLE: autonomous_reasoning_cycles
-- Logs autonomous reasoning for debugging and learning
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS autonomous_reasoning_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    agent_name VARCHAR(100) NOT NULL,

    -- Reasoning trace
    monitoring_state JSONB,
    predictions JSONB,
    decisions JSONB,
    actions_taken JSONB,
    learnings JSONB,

    -- Timing
    cycle_start TIMESTAMPTZ,
    cycle_end TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reasoning_cycles_profile ON autonomous_reasoning_cycles(profile_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_cycles_agent ON autonomous_reasoning_cycles(agent_name);
CREATE INDEX IF NOT EXISTS idx_reasoning_cycles_created ON autonomous_reasoning_cycles(created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- NEW TABLE: proactive_notifications
-- Stores notifications generated by autonomous reasoning
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS proactive_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    agent_name VARCHAR(100) NOT NULL,

    -- Notification content
    notification_type VARCHAR(50),
    title VARCHAR(255),
    message TEXT,
    urgency VARCHAR(20) DEFAULT 'normal',

    -- Related data
    related_asset_id UUID REFERENCES coaching_assets(id) ON DELETE SET NULL,
    related_data JSONB,

    -- Status
    status VARCHAR(20) DEFAULT 'pending',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    viewed_at TIMESTAMPTZ,
    actioned_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_notifications_profile ON proactive_notifications(profile_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON proactive_notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON proactive_notifications(created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- NEW TABLE: student_outcomes
-- Tracks actual outcomes (wins, acceptances, completions)
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS student_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,

    -- Outcome type
    outcome_type VARCHAR(50) NOT NULL,  -- award_result, program_result, task_completion

    -- Details
    outcome_data JSONB NOT NULL,

    -- Related assets that contributed
    related_asset_ids UUID[] DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_outcomes_profile ON student_outcomes(profile_id);
CREATE INDEX IF NOT EXISTS idx_outcomes_type ON student_outcomes(outcome_type);
CREATE INDEX IF NOT EXISTS idx_outcomes_created ON student_outcomes(created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- NEW TABLE: autonomous_goals
-- Stores outcome-driven goals (separate from existing GoalMonitor progress goals)
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS autonomous_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    agent_name VARCHAR(100) NOT NULL,

    -- Goal definition
    primary_outcome TEXT NOT NULL,
    goal_type VARCHAR(50) NOT NULL,  -- win, complete, achieve, prevent
    not_goal TEXT[],  -- What this goal is NOT about

    -- Metrics
    primary_metric VARCHAR(100),
    target_value FLOAT,
    current_value FLOAT DEFAULT 0,
    secondary_metrics JSONB DEFAULT '{}',

    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, achieved, failed, paused

    -- Timing
    target_date TIMESTAMPTZ,
    achieved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_autonomous_goals_profile ON autonomous_goals(profile_id);
CREATE INDEX IF NOT EXISTS idx_autonomous_goals_agent ON autonomous_goals(agent_name);
CREATE INDEX IF NOT EXISTS idx_autonomous_goals_status ON autonomous_goals(status);

-- ═══════════════════════════════════════════════════════════════════════════════
-- FUNCTION: match_coaching_assets
-- Vector similarity search for coaching assets using pgvector
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION match_coaching_assets(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    name text,
    asset_type text,
    domain text,
    secondary_domains text[],
    tags text[],
    content jsonb,
    trigger_config jsonb,
    applicability jsonb,
    provenance jsonb,
    effectiveness jsonb,
    is_active boolean,
    created_at timestamptz,
    updated_at timestamptz,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ca.id,
        ca.name,
        ca.asset_type,
        ca.domain,
        ca.secondary_domains,
        ca.tags,
        ca.content,
        ca.trigger_config,
        ca.applicability,
        ca.provenance,
        ca.effectiveness,
        ca.is_active,
        ca.created_at,
        ca.updated_at,
        1 - (ca.embedding <=> query_embedding) as similarity
    FROM coaching_assets ca
    WHERE ca.is_active = true
    AND ca.embedding IS NOT NULL
    AND 1 - (ca.embedding <=> query_embedding) > match_threshold
    ORDER BY ca.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- FUNCTION: update_asset_effectiveness
-- Helper function to update asset effectiveness after usage
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_asset_effectiveness()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_effectiveness JSONB;
    new_times_used INT;
    new_success_count INT;
    new_success_rate FLOAT;
    arch_key TEXT;
    arch_data JSONB;
BEGIN
    -- Get current effectiveness
    SELECT effectiveness INTO current_effectiveness
    FROM coaching_assets
    WHERE id = NEW.asset_id;

    -- Update global stats
    new_times_used := COALESCE((current_effectiveness->>'times_used')::INT, 0) + 1;
    new_success_count := COALESCE((current_effectiveness->>'success_count')::INT, 0);

    IF (NEW.outcome->>'success')::BOOLEAN THEN
        new_success_count := new_success_count + 1;
    END IF;

    new_success_rate := CASE WHEN new_times_used > 0
        THEN new_success_count::FLOAT / new_times_used
        ELSE 0
    END;

    -- Update archetype-specific stats
    arch_key := NEW.student_archetype;
    IF arch_key IS NOT NULL THEN
        arch_data := COALESCE(current_effectiveness->'by_archetype'->arch_key, '{"times_used": 0, "success_count": 0, "success_rate": 0}'::JSONB);
        arch_data := jsonb_set(arch_data, '{times_used}', to_jsonb((arch_data->>'times_used')::INT + 1));

        IF (NEW.outcome->>'success')::BOOLEAN THEN
            arch_data := jsonb_set(arch_data, '{success_count}', to_jsonb((arch_data->>'success_count')::INT + 1));
        END IF;

        arch_data := jsonb_set(arch_data, '{success_rate}',
            to_jsonb(CASE WHEN (arch_data->>'times_used')::INT > 0
                THEN (arch_data->>'success_count')::FLOAT / (arch_data->>'times_used')::INT
                ELSE 0
            END));

        current_effectiveness := jsonb_set(current_effectiveness, ARRAY['by_archetype', arch_key], arch_data);
    END IF;

    -- Update the asset
    UPDATE coaching_assets
    SET
        effectiveness = jsonb_set(
            jsonb_set(
                jsonb_set(
                    jsonb_set(current_effectiveness, '{times_used}', to_jsonb(new_times_used)),
                    '{success_count}', to_jsonb(new_success_count)
                ),
                '{global_success_rate}', to_jsonb(new_success_rate)
            ),
            '{confidence_level}', to_jsonb(LEAST(1.0, new_times_used::FLOAT / 20))
        ),
        updated_at = NOW()
    WHERE id = NEW.asset_id;

    RETURN NEW;
END;
$$;

-- Create trigger for automatic effectiveness updates
DROP TRIGGER IF EXISTS trigger_update_asset_effectiveness ON asset_usage;
CREATE TRIGGER trigger_update_asset_effectiveness
    AFTER INSERT ON asset_usage
    FOR EACH ROW
    WHEN (NEW.outcome IS NOT NULL)
    EXECUTE FUNCTION update_asset_effectiveness();

-- ═══════════════════════════════════════════════════════════════════════════════
-- Verification Queries (run after migration to verify tables created)
-- ═══════════════════════════════════════════════════════════════════════════════

-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public'
-- AND table_name IN (
--     'coaching_assets',
--     'asset_usage',
--     'student_psychobehavioral',
--     'autonomous_reasoning_cycles',
--     'proactive_notifications',
--     'student_outcomes',
--     'autonomous_goals'
-- );

-- ═══════════════════════════════════════════════════════════════════════════════
-- END OF MIGRATION
-- ═══════════════════════════════════════════════════════════════════════════════
