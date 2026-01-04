-- =====================================================
-- IvyQuest v10.0 Migration 007: Opportunities & Awards Tables
-- MIGRATE-006: Create opportunities (500+) and awards (200+) databases
-- =====================================================
-- Supports: Awards Agent, Opportunity Agent, JTBD-2, JTBD-5
-- Features: ROI calculation, eligibility filtering, advance alerts
-- =====================================================

-- =====================================================
-- AWARDS TABLE (200+ awards database)
-- =====================================================

CREATE TYPE award_level AS ENUM (
  'school',       -- School-level recognition
  'local',        -- City/county level
  'regional',     -- Multi-county/state region
  'state',        -- State-level
  'national',     -- National recognition
  'international' -- International recognition
);

CREATE TYPE award_category AS ENUM (
  'stem',           -- Science, Technology, Engineering, Math
  'humanities',     -- Writing, History, Languages
  'arts',           -- Visual arts, Music, Theater, Film
  'leadership',     -- Leadership awards
  'service',        -- Community service recognition
  'academic',       -- Academic achievement (GPA, test scores)
  'entrepreneurship', -- Business/startup awards
  'athletics',      -- Athletic recognition
  'journalism',     -- Writing, reporting, media
  'debate',         -- Speech and debate
  'research'        -- Research competitions
);

CREATE TABLE IF NOT EXISTS awards (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  -- Basic info
  name TEXT NOT NULL,
  organization TEXT,
  description TEXT,
  website_url TEXT,

  -- Classification
  category award_category NOT NULL,
  level award_level NOT NULL,

  -- Timing
  deadline DATE,
  deadline_recurring TEXT, -- e.g., 'January 15 annually'
  notification_date DATE,
  award_month INTEGER, -- Month when typically awarded

  -- Metrics for ROI calculation
  prestige_score INTEGER CHECK (prestige_score >= 1 AND prestige_score <= 10),
  historical_win_rate FLOAT CHECK (historical_win_rate >= 0 AND historical_win_rate <= 1),
  effort_hours INTEGER, -- Estimated hours to prepare
  total_applicants INTEGER, -- Annual applicant pool
  total_winners INTEGER, -- Annual winners

  -- Eligibility criteria (JSONB for flexibility)
  eligibility JSONB DEFAULT '{}',
  -- Structure: {
  --   grades: [9, 10, 11, 12],
  --   gpa_minimum: 3.5,
  --   citizenship: ['US', 'permanent_resident'],
  --   demographics: ['underrepresented', 'first_gen'],
  --   interests: ['STEM', 'research'],
  --   requirements: ['essay', 'recommendation', 'portfolio']
  -- }

  -- Application requirements
  requirements JSONB DEFAULT '[]',
  -- Structure: ['essay', 'recommendation', 'transcript', 'portfolio', 'video', 'interview']

  -- Prize/recognition details
  prize_amount DECIMAL(10, 2),
  prize_type TEXT, -- 'cash', 'scholarship', 'recognition', 'internship'
  recognition_details TEXT,

  -- Touchpoints (for Multi-Touchpoint Leverage)
  touchpoints INTEGER DEFAULT 1 CHECK (touchpoints >= 1 AND touchpoints <= 7),
  touchpoint_types JSONB DEFAULT '[]', -- ['essay', 'interview', 'recommendation']

  -- Status
  is_active BOOLEAN DEFAULT true,
  last_verified_at TIMESTAMPTZ,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_awards_category ON awards(category);
CREATE INDEX IF NOT EXISTS idx_awards_level ON awards(level);
CREATE INDEX IF NOT EXISTS idx_awards_deadline ON awards(deadline);
CREATE INDEX IF NOT EXISTS idx_awards_prestige ON awards(prestige_score DESC);
CREATE INDEX IF NOT EXISTS idx_awards_active ON awards(is_active) WHERE is_active = true;

-- Trigger
CREATE TRIGGER update_awards_updated_at
  BEFORE UPDATE ON awards
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- OPPORTUNITIES TABLE (500+ opportunities database)
-- =====================================================

CREATE TYPE opportunity_type AS ENUM (
  'summer_program',   -- RSI, SSP, TASP, etc.
  'internship',       -- Summer/semester internships
  'research',         -- Research opportunities
  'competition',      -- Competitions (not awards)
  'conference',       -- Student conferences
  'fellowship',       -- Fellowships
  'scholarship',      -- Merit/need scholarships
  'mentorship',       -- Mentorship programs
  'leadership',       -- Leadership programs
  'study_abroad'      -- Study abroad opportunities
);

CREATE TABLE IF NOT EXISTS opportunities (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  -- Basic info
  name TEXT NOT NULL,
  organization TEXT,
  description TEXT,
  website_url TEXT,

  -- Classification
  type opportunity_type NOT NULL,
  category award_category, -- Reusing award categories

  -- Timing
  application_deadline DATE,
  deadline_recurring TEXT, -- e.g., 'December 1 annually'
  program_start_date DATE,
  program_end_date DATE,
  duration_weeks INTEGER,

  -- Selectivity metrics
  acceptance_rate FLOAT CHECK (acceptance_rate >= 0 AND acceptance_rate <= 1),
  total_applicants INTEGER,
  total_accepted INTEGER,
  prestige_score INTEGER CHECK (prestige_score >= 1 AND prestige_score <= 10),

  -- Effort and ROI
  effort_hours INTEGER, -- Application effort
  program_hours INTEGER, -- Program commitment
  touchpoints INTEGER DEFAULT 1 CHECK (touchpoints >= 1 AND touchpoints <= 7),

  -- Eligibility
  eligibility JSONB DEFAULT '{}',
  -- Same structure as awards

  -- Requirements
  requirements JSONB DEFAULT '[]',

  -- Financials
  cost DECIMAL(10, 2), -- Program cost (0 if free)
  stipend DECIMAL(10, 2), -- If paid
  financial_aid_available BOOLEAN DEFAULT false,

  -- Location
  location TEXT,
  is_virtual BOOLEAN DEFAULT false,
  is_residential BOOLEAN DEFAULT false,

  -- Status
  is_active BOOLEAN DEFAULT true,
  last_verified_at TIMESTAMPTZ,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_opportunities_type ON opportunities(type);
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline ON opportunities(application_deadline);
CREATE INDEX IF NOT EXISTS idx_opportunities_prestige ON opportunities(prestige_score DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_acceptance ON opportunities(acceptance_rate);
CREATE INDEX IF NOT EXISTS idx_opportunities_active ON opportunities(is_active) WHERE is_active = true;

-- Trigger
CREATE TRIGGER update_opportunities_updated_at
  BEFORE UPDATE ON opportunities
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- STUDENT AWARD/OPPORTUNITY APPLICATIONS
-- =====================================================

CREATE TYPE application_status AS ENUM (
  'interested',    -- Student marked as interested
  'planning',      -- Planning to apply
  'in_progress',   -- Application in progress
  'submitted',     -- Application submitted
  'waitlisted',    -- On waitlist
  'accepted',      -- Accepted!
  'rejected',      -- Rejected
  'withdrawn'      -- Student withdrew
);

CREATE TABLE IF NOT EXISTS student_applications (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- What they're applying to (one of these will be set)
  award_id UUID REFERENCES awards(id) ON DELETE SET NULL,
  opportunity_id UUID REFERENCES opportunities(id) ON DELETE SET NULL,

  -- Status tracking
  status application_status DEFAULT 'interested',
  status_history JSONB DEFAULT '[]', -- [{status, timestamp, notes}]

  -- Agent predictions (Hidden Probability Matrix - ACP-001)
  predicted_probability FLOAT,
  probability_factors JSONB, -- Factors affecting prediction
  agent_recommendation TEXT, -- 'apply', 'skip', 'backup'
  recommendation_rationale TEXT,

  -- Application tracking
  deadline DATE,
  submitted_at TIMESTAMPTZ,
  result_received_at TIMESTAMPTZ,

  -- Outcome
  outcome TEXT,
  outcome_notes TEXT,

  -- For success vector ingestion
  is_success BOOLEAN, -- True if accepted, for SUCCESS_ACHIEVED events

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraint: must have either award_id or opportunity_id
  CONSTRAINT application_target CHECK (
    (award_id IS NOT NULL AND opportunity_id IS NULL) OR
    (award_id IS NULL AND opportunity_id IS NOT NULL)
  )
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_applications_profile ON student_applications(profile_id);
CREATE INDEX IF NOT EXISTS idx_applications_award ON student_applications(award_id) WHERE award_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_applications_opportunity ON student_applications(opportunity_id) WHERE opportunity_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_applications_status ON student_applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_deadline ON student_applications(deadline);

-- Trigger
CREATE TRIGGER update_applications_updated_at
  BEFORE UPDATE ON student_applications
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SUCCESS VECTORS (for RLHF)
-- =====================================================
-- Note: pgvector extension already enabled in migration 003

CREATE TABLE IF NOT EXISTS success_vectors (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  -- Source
  profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  application_id UUID REFERENCES student_applications(id) ON DELETE SET NULL,

  -- Vector embedding (1536 dimensions for OpenAI embeddings)
  vector vector(1536),

  -- Metadata for similarity search
  metadata JSONB DEFAULT '{}',
  -- Structure: {
  --   impact: number,
  --   awards_count: number,
  --   archetype: string,
  --   constraints: [],
  --   spike: string,
  --   outcome_type: 'award' | 'opportunity'
  -- }

  -- Event tracking
  event_type TEXT NOT NULL, -- CRITICAL: Only 'SUCCESS_ACHIEVED' events
  event_payload JSONB,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity index
CREATE INDEX IF NOT EXISTS idx_success_vectors_embedding
  ON success_vectors USING hnsw (vector vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_success_vectors_profile ON success_vectors(profile_id);

-- Enable RLS on all tables
ALTER TABLE awards ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE success_vectors ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Allow public read for awards" ON awards FOR SELECT USING (true);
CREATE POLICY "Allow public read for opportunities" ON opportunities FOR SELECT USING (true);
CREATE POLICY "Allow application access" ON student_applications FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow success vector access" ON success_vectors FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- SAMPLE DATA (Top awards and opportunities)
-- =====================================================

INSERT INTO awards (name, organization, category, level, prestige_score, historical_win_rate, effort_hours, eligibility, deadline_recurring) VALUES
  ('Regeneron Science Talent Search', 'Society for Science', 'research', 'national', 10, 0.006, 200, '{"grades": [12], "requirements": ["research_project", "essay"]}', 'November 15'),
  ('NCWIT Award for Aspirations in Computing', 'NCWIT', 'stem', 'national', 9, 0.15, 20, '{"grades": [9,10,11,12], "gender": ["female", "non-binary"]}', 'November 1'),
  ('Scholastic Art & Writing Awards', 'Alliance for Young Artists', 'arts', 'national', 9, 0.10, 40, '{"grades": [7,8,9,10,11,12]}', 'December 15'),
  ('Congressional Award', 'US Congress', 'service', 'national', 9, 0.30, 100, '{"grades": [9,10,11,12], "citizenship": ["US"]}', 'Rolling'),
  ('National Speech & Debate Tournament', 'NSDA', 'debate', 'national', 9, 0.02, 150, '{"grades": [9,10,11,12]}', 'Qualifying'),
  ('USA Computing Olympiad', 'USACO', 'stem', 'national', 10, 0.01, 200, '{"grades": [9,10,11,12]}', 'December-March'),
  ('National Merit Scholarship', 'NMSC', 'academic', 'national', 8, 0.15, 5, '{"grades": [11], "requirements": ["PSAT"]}', 'October PSAT'),
  ('Presidential Scholars Program', 'US Dept of Education', 'academic', 'national', 10, 0.002, 50, '{"grades": [12]}', 'January'),
  ('American Regions Mathematics League', 'ARML', 'stem', 'regional', 8, 0.20, 80, '{"grades": [9,10,11,12]}', 'May'),
  ('Model UN Best Delegate', 'Various', 'leadership', 'regional', 7, 0.15, 60, '{"grades": [9,10,11,12]}', 'Rolling')
ON CONFLICT DO NOTHING;

INSERT INTO opportunities (name, organization, type, category, prestige_score, acceptance_rate, effort_hours, eligibility, deadline_recurring) VALUES
  ('Research Science Institute (RSI)', 'MIT/CEE', 'summer_program', 'research', 10, 0.03, 40, '{"grades": [11], "requirements": ["essay", "recommendation", "transcript"]}', 'January 15'),
  ('Summer Science Program (SSP)', 'SSP', 'summer_program', 'research', 10, 0.08, 35, '{"grades": [10,11]}', 'February 1'),
  ('TASP (Telluride Association Summer Program)', 'Telluride Association', 'summer_program', 'humanities', 10, 0.03, 40, '{"grades": [11]}', 'January 15'),
  ('MOSTEC (MIT Online Science Technology Engineering Community)', 'MIT', 'summer_program', 'stem', 9, 0.05, 30, '{"grades": [11]}', 'February'),
  ('Bank of America Student Leaders', 'Bank of America', 'internship', 'leadership', 8, 0.10, 25, '{"grades": [11,12]}', 'January 31'),
  ('Google CSSI', 'Google', 'summer_program', 'stem', 9, 0.08, 30, '{"grades": [12]}', 'March'),
  ('JCamp', 'Various Publishers', 'summer_program', 'journalism', 9, 0.10, 25, '{"grades": [11,12]}', 'Varies'),
  ('LaunchX', 'MIT', 'summer_program', 'entrepreneurship', 8, 0.15, 30, '{"grades": [10,11,12]}', 'March'),
  ('Garcia MRSEC', 'Stony Brook', 'research', 'research', 8, 0.15, 25, '{"grades": [10,11]}', 'March'),
  ('SAMS (Summer Academy for Math and Science)', 'Carnegie Mellon', 'summer_program', 'stem', 8, 0.10, 30, '{"grades": [11]}', 'January')
ON CONFLICT DO NOTHING;

-- Comments
COMMENT ON TABLE awards IS 'Database of 200+ awards for Awards Agent matching (v10.0)';
COMMENT ON TABLE opportunities IS 'Database of 500+ opportunities for Opportunity Agent (v10.0)';
COMMENT ON TABLE student_applications IS 'Tracks student award/opportunity applications with agent predictions';
COMMENT ON TABLE success_vectors IS 'Embeddings for RLHF - ONLY from SUCCESS_ACHIEVED events';
COMMENT ON COLUMN student_applications.predicted_probability IS 'Hidden Probability Matrix prediction (ACP-001) - never shown to user';

-- =====================================================
-- ROLLBACK
-- =====================================================
-- DROP TABLE IF EXISTS success_vectors;
-- DROP TABLE IF EXISTS student_applications;
-- DROP TABLE IF EXISTS opportunities;
-- DROP TABLE IF EXISTS awards;
-- DROP TYPE IF EXISTS application_status;
-- DROP TYPE IF EXISTS opportunity_type;
-- DROP TYPE IF EXISTS award_level;
-- DROP TYPE IF EXISTS award_category;
