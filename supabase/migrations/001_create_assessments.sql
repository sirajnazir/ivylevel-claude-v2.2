-- IvyQuest Assessment Schema
-- Run this migration in your Supabase SQL editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum for coach session status
CREATE TYPE coach_session_status AS ENUM ('pending', 'scheduled', 'completed', 'cancelled');

-- Assessments table: stores student profiles and game plans
CREATE TABLE IF NOT EXISTS assessments (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  session_id TEXT NOT NULL UNIQUE,
  email TEXT,
  profile_data JSONB NOT NULL,
  game_plan_data JSONB,
  scores JSONB,
  completeness INTEGER DEFAULT 0,
  tier TEXT,
  archetype TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on session_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_assessments_session_id ON assessments(session_id);

-- Create index on email for retrieving past assessments
CREATE INDEX IF NOT EXISTS idx_assessments_email ON assessments(email) WHERE email IS NOT NULL;

-- Create index on updated_at for sorting
CREATE INDEX IF NOT EXISTS idx_assessments_updated_at ON assessments(updated_at DESC);

-- Coach sessions table: tracks coaching appointments
CREATE TABLE IF NOT EXISTS coach_sessions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  scheduled_at TIMESTAMPTZ,
  calendly_event_id TEXT,
  coach_notes TEXT,
  status coach_session_status DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on assessment_id for joins
CREATE INDEX IF NOT EXISTS idx_coach_sessions_assessment_id ON coach_sessions(assessment_id);

-- Create index on email for finding sessions by student email
CREATE INDEX IF NOT EXISTS idx_coach_sessions_email ON coach_sessions(email);

-- Enable Row Level Security (RLS)
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE coach_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Allow anonymous reads for session-based access (using session_id)
CREATE POLICY "Allow anonymous session access" ON assessments
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Allow anonymous reads for coach sessions
CREATE POLICY "Allow anonymous coach session access" ON coach_sessions
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_assessments_updated_at
  BEFORE UPDATE ON assessments
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE assessments IS 'Stores IvyQuest student assessment profiles and game plans';
COMMENT ON TABLE coach_sessions IS 'Tracks coach booking sessions linked to assessments';
COMMENT ON COLUMN assessments.session_id IS 'Unique client-side session identifier (UUID)';
COMMENT ON COLUMN assessments.profile_data IS 'Complete StudentProfile JSON from the assessment';
COMMENT ON COLUMN assessments.game_plan_data IS 'Generated GamePlan JSON if available';
COMMENT ON COLUMN assessments.scores IS 'Category scores: aptitude, passion, community, identity, overall';
COMMENT ON COLUMN assessments.completeness IS 'Profile completeness percentage (0-100)';
COMMENT ON COLUMN assessments.tier IS 'Profile classification tier (fresh-start, emerging, developed, exceptional)';
COMMENT ON COLUMN assessments.archetype IS 'Student archetype classification';
