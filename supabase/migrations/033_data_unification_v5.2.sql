-- ============================================================================
-- Migration: Data Unification v5.2
-- Date: 2026-01-17
-- Description: Add identity columns to profiles table and agent output columns
--              to game_plans table for data unification
-- Risk Level: LOW - Adds columns, doesn't modify existing data
-- ============================================================================

-- ============================================================================
-- PROFILES TABLE: Add Missing Identity Columns
-- Note: narrative_brand_statement, narrative_dna, narrative_first_principle,
--       narrative_themes, narrative_confidence already exist from migration 020
-- ============================================================================

-- Spike (EC Agent output)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS spike TEXT;
COMMENT ON COLUMN profiles.spike IS 'Student unique spike from EC Agent';

-- Spike confidence
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS spike_confidence FLOAT DEFAULT 0;
COMMENT ON COLUMN profiles.spike_confidence IS 'Confidence score for spike identification';

-- Pillars (EC Agent 4-pillar analysis)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS pillars JSONB DEFAULT '[]'::jsonb;
COMMENT ON COLUMN profiles.pillars IS 'Four pillars: IDENTITY, APTITUDE, PASSION, SERVICE';

-- Identity synthesis (full EC Agent output)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS identity_synthesis JSONB DEFAULT '{}'::jsonb;
COMMENT ON COLUMN profiles.identity_synthesis IS 'Complete identity synthesis from EC Agent';

-- Archetype confidence (if not exists)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS archetype_confidence FLOAT DEFAULT 0;

-- Synthesis metadata
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_synthesized_at TIMESTAMPTZ;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_synthesized_by TEXT;

-- Create aliases for consistent naming (brand_statement → narrative_brand_statement)
-- These are views/computed columns for API compatibility
DO $$
BEGIN
    -- Add index on narrative_brand_statement for faster lookups
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'profiles' AND indexname = 'idx_profiles_brand_statement'
    ) THEN
        CREATE INDEX idx_profiles_brand_statement ON profiles(id)
        WHERE narrative_brand_statement IS NOT NULL;
    END IF;
END $$;

-- ============================================================================
-- GAME_PLANS TABLE: Add Agent Output Columns
-- ============================================================================

-- Add profile_id for direct profile reference (in addition to user_id)
ALTER TABLE game_plans ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES profiles(id);
COMMENT ON COLUMN game_plans.profile_id IS 'Direct reference to profile for agent outputs';

-- EC Generation Engine output
ALTER TABLE game_plans ADD COLUMN IF NOT EXISTS ec_generation JSONB;
COMMENT ON COLUMN game_plans.ec_generation IS 'EC Generation Engine output with recommended activities';

-- Awards Agent output
ALTER TABLE game_plans ADD COLUMN IF NOT EXISTS awards_data JSONB;
COMMENT ON COLUMN game_plans.awards_data IS 'Awards Agent portfolio and recommendations';

-- Programs Agent output
ALTER TABLE game_plans ADD COLUMN IF NOT EXISTS programs_data JSONB;
COMMENT ON COLUMN game_plans.programs_data IS 'Programs Agent portfolio and recommendations';

-- ReAct metadata for cycle visualization
ALTER TABLE game_plans ADD COLUMN IF NOT EXISTS react_metadata JSONB;
COMMENT ON COLUMN game_plans.react_metadata IS 'ReAct cycle metadata for visualization';

-- Generation version tracking
ALTER TABLE game_plans ADD COLUMN IF NOT EXISTS generation_version TEXT DEFAULT '5.2';
COMMENT ON COLUMN game_plans.generation_version IS 'Version of the generation engine used';

-- Index for profile_id lookups
CREATE INDEX IF NOT EXISTS idx_game_plans_profile_updated ON game_plans(profile_id, updated_at DESC);

-- ============================================================================
-- HELPER FUNCTION: Get Profile Identity (with null-safe defaults)
-- Returns identity data with COALESCE for null safety
-- ============================================================================

CREATE OR REPLACE FUNCTION get_profile_identity(p_profile_id UUID)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    name TEXT,
    email TEXT,
    grade INTEGER,
    archetype_id UUID,
    archetype_name TEXT,
    archetype_confidence FLOAT,
    -- Identity fields with COALESCE for null safety
    -- Uses existing narrative_* column names
    brand_statement TEXT,
    narrative_dna TEXT,
    narrative_themes JSONB,
    first_principle TEXT,
    spike TEXT,
    spike_confidence FLOAT,
    pillars JSONB,
    identity_synthesis JSONB,
    narrative_confidence FLOAT,
    last_synthesized_at TIMESTAMPTZ
) AS $$
BEGIN
    -- v5.2: Schema-aware query that matches actual profiles table structure
    -- Columns: first_name, last_name (not name), archetype (TEXT not archetype_id), etc.
    RETURN QUERY
    SELECT
        p.id,
        NULL::UUID as user_id,
        -- Combine first_name + last_name since 'name' column doesn't exist
        COALESCE(p.first_name || ' ' || p.last_name, p.first_name, p.last_name, '')::TEXT as name,
        p.email,
        p.grade,
        NULL::UUID as archetype_id,
        -- archetype is TEXT in this schema, not a foreign key reference
        COALESCE(p.archetype, (p.identity_synthesis->>'archetype'))::TEXT as archetype_name,
        COALESCE(p.archetype_confidence, 0.0)::FLOAT as archetype_confidence,
        -- You have BOTH brand_statement and narrative_brand_statement, prefer narrative_brand_statement
        COALESCE(p.narrative_brand_statement, p.brand_statement, '')::TEXT as brand_statement,
        COALESCE(p.narrative_dna, '')::TEXT as narrative_dna,
        COALESCE(p.narrative_themes, '[]'::jsonb) as narrative_themes,
        COALESCE(p.narrative_first_principle, '')::TEXT as first_principle,
        COALESCE(p.spike, '')::TEXT as spike,
        COALESCE(p.spike_confidence, 0.0)::FLOAT as spike_confidence,
        COALESCE(p.pillars, '[]'::jsonb) as pillars,
        COALESCE(p.identity_synthesis, '{}'::jsonb) as identity_synthesis,
        COALESCE(p.narrative_confidence, 0.0)::FLOAT as narrative_confidence,
        COALESCE(p.last_synthesized_at, p.narrative_updated_at) as last_synthesized_at
    FROM profiles p
    WHERE p.id = p_profile_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- HELPER FUNCTION: Update Profile Identity
-- Updates identity columns with COALESCE to preserve existing values
-- ============================================================================

CREATE OR REPLACE FUNCTION update_profile_identity(
    p_profile_id UUID,
    p_brand_statement TEXT DEFAULT NULL,
    p_narrative_dna TEXT DEFAULT NULL,
    p_narrative_themes JSONB DEFAULT NULL,
    p_first_principle TEXT DEFAULT NULL,
    p_spike TEXT DEFAULT NULL,
    p_spike_confidence FLOAT DEFAULT NULL,
    p_pillars JSONB DEFAULT NULL,
    p_identity_synthesis JSONB DEFAULT NULL,
    p_narrative_confidence FLOAT DEFAULT NULL,
    p_source TEXT DEFAULT 'api'
)
RETURNS VOID AS $$
BEGIN
    UPDATE profiles SET
        -- Map to existing column names (narrative_*)
        narrative_brand_statement = COALESCE(p_brand_statement, narrative_brand_statement),
        narrative_dna = COALESCE(p_narrative_dna, narrative_dna),
        narrative_themes = COALESCE(p_narrative_themes, narrative_themes),
        narrative_first_principle = COALESCE(p_first_principle, narrative_first_principle),
        narrative_confidence = COALESCE(p_narrative_confidence, narrative_confidence),
        -- New identity columns
        spike = COALESCE(p_spike, spike),
        spike_confidence = COALESCE(p_spike_confidence, spike_confidence),
        pillars = COALESCE(p_pillars, pillars),
        identity_synthesis = COALESCE(p_identity_synthesis, identity_synthesis),
        -- Metadata
        last_synthesized_at = NOW(),
        last_synthesized_by = p_source,
        narrative_updated_at = NOW(),
        updated_at = NOW()
    WHERE id = p_profile_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- HELPER FUNCTION: Get or Create Game Plan
-- Upserts game plan data for a profile
-- ============================================================================

CREATE OR REPLACE FUNCTION upsert_game_plan(
    p_profile_id UUID,
    p_user_id UUID,
    p_plan_data JSONB DEFAULT NULL,
    p_ec_generation JSONB DEFAULT NULL,
    p_awards_data JSONB DEFAULT NULL,
    p_programs_data JSONB DEFAULT NULL,
    p_react_metadata JSONB DEFAULT NULL,
    p_generation_version TEXT DEFAULT '5.2'
)
RETURNS UUID AS $$
DECLARE
    v_game_plan_id UUID;
BEGIN
    -- Try to find existing game plan for this profile
    SELECT id INTO v_game_plan_id
    FROM game_plans
    WHERE profile_id = p_profile_id
    ORDER BY updated_at DESC
    LIMIT 1;

    IF v_game_plan_id IS NULL THEN
        -- Create new game plan
        INSERT INTO game_plans (
            user_id,
            profile_id,
            plan_data,
            ec_generation,
            awards_data,
            programs_data,
            react_metadata,
            generation_version,
            plan_status,
            created_at,
            updated_at
        ) VALUES (
            p_user_id,
            p_profile_id,
            COALESCE(p_plan_data, '{}'::jsonb),
            p_ec_generation,
            p_awards_data,
            p_programs_data,
            p_react_metadata,
            p_generation_version,
            'active',
            NOW(),
            NOW()
        )
        RETURNING id INTO v_game_plan_id;
    ELSE
        -- Update existing game plan
        UPDATE game_plans SET
            plan_data = COALESCE(p_plan_data, plan_data),
            ec_generation = COALESCE(p_ec_generation, ec_generation),
            awards_data = COALESCE(p_awards_data, awards_data),
            programs_data = COALESCE(p_programs_data, programs_data),
            react_metadata = COALESCE(p_react_metadata, react_metadata),
            generation_version = p_generation_version,
            updated_at = NOW()
        WHERE id = v_game_plan_id;
    END IF;

    RETURN v_game_plan_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
BEGIN
    -- Verify profiles columns exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'profiles' AND column_name = 'spike'
    ) THEN
        RAISE EXCEPTION 'Migration failed: spike column not created';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'profiles' AND column_name = 'pillars'
    ) THEN
        RAISE EXCEPTION 'Migration failed: pillars column not created';
    END IF;

    -- Verify game_plans columns exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'game_plans' AND column_name = 'ec_generation'
    ) THEN
        RAISE EXCEPTION 'Migration failed: ec_generation column not created';
    END IF;

    -- Verify functions exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'get_profile_identity'
    ) THEN
        RAISE EXCEPTION 'Migration failed: get_profile_identity function not created';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'update_profile_identity'
    ) THEN
        RAISE EXCEPTION 'Migration failed: update_profile_identity function not created';
    END IF;

    RAISE NOTICE 'Migration 033_data_unification_v5.2 completed successfully';
END;
$$;
