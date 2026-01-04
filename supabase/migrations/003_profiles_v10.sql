-- =====================================================
-- IvyQuest v10.0 Migration 003: Enhanced Profiles Table
-- MIGRATE-002: Create profiles table with v10.0 agent attributes
-- =====================================================
-- This creates a NEW profiles table for v10.0 agent data
-- Links to existing assessments table via assessment_id
-- Does NOT modify existing assessments table (incremental migration)
-- =====================================================

-- Enable vector extension for success vectors (Supabase pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create profiles table for v10.0 enhanced attributes
CREATE TABLE IF NOT EXISTS profiles (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  -- Link to existing assessment (optional - can exist independently)
  assessment_id UUID REFERENCES assessments(id) ON DELETE SET NULL,

  -- Basic identity (cached from assessment or standalone)
  user_id UUID, -- For future auth integration
  name TEXT,
  email TEXT,
  grade INTEGER CHECK (grade >= 9 AND grade <= 12),

  -- Archetype (v10.0: agent-derived with explainability)
  archetype_id UUID REFERENCES archetypes(id),
  archetype_confidence FLOAT DEFAULT 0 CHECK (archetype_confidence >= 0 AND archetype_confidence <= 1),
  archetype_rationale TEXT, -- Explainable AI: why this archetype?

  -- Context Relativity Index (v10.0: CRI scoring)
  cri FLOAT DEFAULT 1.0 CHECK (cri >= 0 AND cri <= 3.0),
  cri_components JSONB DEFAULT '{}', -- {performance, expected, barrier_multiplier, chetty_multiplier}

  -- Narrative DNA (v10.0: Identity Synthesis)
  narrative_dna TEXT, -- Single synthesized theme sentence
  narrative_themes JSONB DEFAULT '[]', -- Supporting themes extracted
  narrative_confidence FLOAT DEFAULT 0,

  -- Execution Tracking (v10.0: Execution Agent)
  execution_debt FLOAT DEFAULT 0 CHECK (execution_debt >= 0), -- EDS score
  execution_debt_updated_at TIMESTAMPTZ,
  active_projects_count INTEGER DEFAULT 0,
  completed_projects_count INTEGER DEFAULT 0,

  -- Hidden Strategy (v10.0: ACP-001 Hidden Probability Matrix)
  -- CRITICAL: These are NEVER shown to the user
  hidden_target TEXT, -- School to secretly optimize for
  hidden_probabilities JSONB DEFAULT '{}', -- {school: probability} matrix
  hidden_strategy_notes TEXT, -- Agent reasoning (internal)

  -- Identity Seeds (v10.0: ACP-006)
  identity_seeds JSONB DEFAULT '[]', -- [{seed, plant_date, bloom_date, status}]

  -- Constraints & Context (for CRI calculation)
  constraints JSONB DEFAULT '[]', -- ['family_duties', 'low_ses', ...]
  zip_code TEXT,
  school_id TEXT,

  -- Agent State Tracking
  last_agent_interaction TIMESTAMPTZ,
  agent_notes JSONB DEFAULT '{}', -- {agent_name: {last_action, notes}}

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiles_assessment ON profiles(assessment_id);
CREATE INDEX IF NOT EXISTS idx_profiles_archetype ON profiles(archetype_id);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_profiles_cri ON profiles(cri DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_execution_debt ON profiles(execution_debt DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_zip ON profiles(zip_code) WHERE zip_code IS NOT NULL;

-- Trigger for updated_at
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies (similar to assessments for now)
CREATE POLICY "Allow session-based profile access" ON profiles
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Function to create/sync profile from assessment
CREATE OR REPLACE FUNCTION sync_profile_from_assessment(p_assessment_id UUID)
RETURNS UUID AS $$
DECLARE
  v_profile_id UUID;
  v_assessment RECORD;
BEGIN
  -- Get assessment data
  SELECT * INTO v_assessment FROM assessments WHERE id = p_assessment_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Assessment not found: %', p_assessment_id;
  END IF;

  -- Check if profile already exists for this assessment
  SELECT id INTO v_profile_id FROM profiles WHERE assessment_id = p_assessment_id;

  IF v_profile_id IS NOT NULL THEN
    -- Update existing profile
    UPDATE profiles SET
      name = v_assessment.profile_data->>'name',
      email = v_assessment.email,
      grade = (v_assessment.profile_data->>'grade')::INTEGER,
      updated_at = NOW()
    WHERE id = v_profile_id;
  ELSE
    -- Create new profile
    INSERT INTO profiles (assessment_id, name, email, grade)
    VALUES (
      p_assessment_id,
      v_assessment.profile_data->>'name',
      v_assessment.email,
      (v_assessment.profile_data->>'grade')::INTEGER
    )
    RETURNING id INTO v_profile_id;
  END IF;

  RETURN v_profile_id;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE profiles IS 'Enhanced student profiles for v10.0 multi-agent system';
COMMENT ON COLUMN profiles.archetype_confidence IS 'Agent confidence in archetype detection (0-1). Handoff to human if <0.7';
COMMENT ON COLUMN profiles.archetype_rationale IS 'Explainable AI: reasoning for archetype assignment';
COMMENT ON COLUMN profiles.cri IS 'Context Relativity Index: performance relative to expected given constraints';
COMMENT ON COLUMN profiles.narrative_dna IS 'Single sentence capturing student identity/mission (ACP-002)';
COMMENT ON COLUMN profiles.execution_debt IS 'Execution Debt Score: sum of missed microsteps weighted by delay and difficulty';
COMMENT ON COLUMN profiles.hidden_target IS 'INTERNAL: School to optimize for, never shown to user (ACP-001)';
COMMENT ON COLUMN profiles.hidden_probabilities IS 'INTERNAL: Real admission probabilities, never shown to user';
COMMENT ON COLUMN profiles.identity_seeds IS 'Activities planted 6-12mo before needed (ACP-006)';

-- =====================================================
-- ROLLBACK
-- =====================================================
-- DROP FUNCTION IF EXISTS sync_profile_from_assessment(UUID);
-- DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
-- DROP POLICY IF EXISTS "Allow session-based profile access" ON profiles;
-- DROP TABLE IF EXISTS profiles;
