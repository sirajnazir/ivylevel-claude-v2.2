-- =====================================================
-- IvyQuest v10.0 Migration 005: Chetty Baselines Table
-- MIGRATE-004: Precomputed Chetty data for CRI calculation
-- =====================================================
-- CRITICAL: This data is PRECOMPUTED, not fetched at runtime
-- Per v9.1 correction: No runtime API calls to Opportunity Insights
-- Data sourced from Chetty et al. 2023 research on economic mobility
-- =====================================================

-- Create Chetty baselines table
CREATE TABLE IF NOT EXISTS chetty_baselines (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

  -- Geographic identifiers
  zip_code TEXT NOT NULL,
  state_code TEXT,
  county_name TEXT,
  metro_area TEXT,

  -- School-specific (optional, more granular)
  school_id TEXT,
  school_name TEXT,
  school_type TEXT, -- 'public', 'private', 'charter', 'magnet'

  -- Expected performance baseline (0-1 scale)
  -- This is what a "typical" student from this area achieves
  expected_performance FLOAT NOT NULL DEFAULT 0.7
    CHECK (expected_performance >= 0 AND expected_performance <= 1),

  -- Economic mobility metrics from Chetty research
  mobility_rate FLOAT, -- Probability of moving from bottom to top quintile
  income_percentile_25 FLOAT, -- 25th percentile household income
  income_percentile_50 FLOAT, -- Median household income
  income_percentile_75 FLOAT, -- 75th percentile household income

  -- College attendance rates from the area
  college_attendance_rate FLOAT,
  elite_college_rate FLOAT, -- Attendance at highly selective schools

  -- CRI Multipliers (applied to boost students overcoming barriers)
  multiplier FLOAT DEFAULT 1.0
    CHECK (multiplier >= 1.0 AND multiplier <= 2.0),

  -- Breakdown of multiplier components
  low_ses_multiplier FLOAT DEFAULT 1.0, -- 1.1-1.2 for low-income areas
  underrepresented_multiplier FLOAT DEFAULT 1.0, -- 1.1-1.2 for underrepresented
  first_gen_multiplier FLOAT DEFAULT 1.0, -- 1.1 for first-gen concentrated areas
  rural_multiplier FLOAT DEFAULT 1.0, -- 1.05-1.1 for rural areas

  -- Data versioning
  version INTEGER DEFAULT 1,
  source TEXT DEFAULT 'chetty_2023',
  source_url TEXT,
  notes TEXT,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unique constraint on zip + school combination
CREATE UNIQUE INDEX IF NOT EXISTS idx_chetty_zip_school
  ON chetty_baselines(zip_code, COALESCE(school_id, ''));

-- Additional indexes
CREATE INDEX IF NOT EXISTS idx_chetty_zip ON chetty_baselines(zip_code);
CREATE INDEX IF NOT EXISTS idx_chetty_state ON chetty_baselines(state_code);
CREATE INDEX IF NOT EXISTS idx_chetty_mobility ON chetty_baselines(mobility_rate DESC);
CREATE INDEX IF NOT EXISTS idx_chetty_multiplier ON chetty_baselines(multiplier DESC);

-- Trigger for updated_at
CREATE TRIGGER update_chetty_baselines_updated_at
  BEFORE UPDATE ON chetty_baselines
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE chetty_baselines ENABLE ROW LEVEL SECURITY;

-- RLS Policies (read-only for all, write for service role)
CREATE POLICY "Allow public read access to baselines" ON chetty_baselines
  FOR SELECT
  USING (true);

CREATE POLICY "Service role can modify baselines" ON chetty_baselines
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- Function to get baseline with fallback
CREATE OR REPLACE FUNCTION get_chetty_baseline(
  p_zip TEXT,
  p_school_id TEXT DEFAULT NULL
)
RETURNS TABLE (
  expected_performance FLOAT,
  multiplier FLOAT,
  mobility_rate FLOAT,
  source TEXT
) AS $$
BEGIN
  -- Try exact match with school
  IF p_school_id IS NOT NULL THEN
    RETURN QUERY
    SELECT
      cb.expected_performance,
      cb.multiplier,
      cb.mobility_rate,
      cb.source
    FROM chetty_baselines cb
    WHERE cb.zip_code = p_zip AND cb.school_id = p_school_id
    LIMIT 1;

    IF FOUND THEN RETURN; END IF;
  END IF;

  -- Try zip-only match
  RETURN QUERY
  SELECT
    cb.expected_performance,
    cb.multiplier,
    cb.mobility_rate,
    cb.source
  FROM chetty_baselines cb
  WHERE cb.zip_code = p_zip AND cb.school_id IS NULL
  LIMIT 1;

  IF FOUND THEN RETURN; END IF;

  -- Return default baseline
  RETURN QUERY
  SELECT
    0.7::FLOAT as expected_performance,
    1.0::FLOAT as multiplier,
    0.5::FLOAT as mobility_rate,
    'default'::TEXT as source;
END;
$$ LANGUAGE plpgsql;

-- Insert sample baseline data (expand with full Chetty dataset)
-- These are representative examples based on Chetty research patterns
INSERT INTO chetty_baselines (
  zip_code, state_code, metro_area, expected_performance, mobility_rate, multiplier,
  low_ses_multiplier, underrepresented_multiplier, notes
) VALUES
  -- High-SES areas (baseline performance high, low multiplier)
  ('94027', 'CA', 'San Francisco Bay Area', 0.88, 0.12, 1.0, 1.0, 1.0, 'Atherton - highest income zip'),
  ('10021', 'NY', 'New York City', 0.85, 0.15, 1.0, 1.0, 1.0, 'Upper East Side Manhattan'),
  ('02138', 'MA', 'Boston Metro', 0.87, 0.14, 1.0, 1.0, 1.0, 'Cambridge/Harvard area'),

  -- Mixed-income urban areas
  ('94102', 'CA', 'San Francisco Bay Area', 0.65, 0.22, 1.15, 1.1, 1.05, 'SF Tenderloin - mixed income'),
  ('10001', 'NY', 'New York City', 0.70, 0.20, 1.1, 1.05, 1.05, 'Midtown Manhattan - mixed'),
  ('60601', 'IL', 'Chicago Metro', 0.68, 0.18, 1.12, 1.07, 1.05, 'Downtown Chicago'),

  -- Low-income urban areas (higher multipliers for overcoming barriers)
  ('77001', 'TX', 'Houston Metro', 0.55, 0.28, 1.25, 1.15, 1.1, 'East Houston - underserved'),
  ('90011', 'CA', 'Los Angeles Metro', 0.52, 0.32, 1.28, 1.18, 1.1, 'South LA - high need'),
  ('48201', 'MI', 'Detroit Metro', 0.48, 0.35, 1.30, 1.2, 1.1, 'Detroit - highest mobility potential'),

  -- Rural areas
  ('38901', 'MS', 'Rural Mississippi', 0.50, 0.38, 1.25, 1.15, 1.1, 'Rural MS - limited resources'),
  ('41701', 'KY', 'Eastern Kentucky', 0.52, 0.36, 1.22, 1.12, 1.1, 'Appalachian region'),
  ('58501', 'ND', 'North Dakota Rural', 0.60, 0.25, 1.15, 1.08, 1.07, 'Rural ND - isolation factor'),

  -- Immigrant-concentrated areas
  ('77042', 'TX', 'Houston Metro', 0.58, 0.30, 1.22, 1.12, 1.1, 'Chinatown Houston'),
  ('91731', 'CA', 'Los Angeles Metro', 0.62, 0.26, 1.18, 1.1, 1.08, 'El Monte - immigrant hub'),

  -- Default fallback (used when no match found)
  ('00000', NULL, NULL, 0.70, 0.20, 1.0, 1.0, 1.0, 'Default baseline for unknown areas')
ON CONFLICT (zip_code, COALESCE(school_id, '')) DO UPDATE SET
  expected_performance = EXCLUDED.expected_performance,
  mobility_rate = EXCLUDED.mobility_rate,
  multiplier = EXCLUDED.multiplier,
  low_ses_multiplier = EXCLUDED.low_ses_multiplier,
  underrepresented_multiplier = EXCLUDED.underrepresented_multiplier,
  notes = EXCLUDED.notes,
  updated_at = NOW();

-- Comments
COMMENT ON TABLE chetty_baselines IS 'Precomputed Chetty mobility data for CRI calculation (v10.0)';
COMMENT ON COLUMN chetty_baselines.expected_performance IS 'Baseline performance expectation (0-1) for students from this area';
COMMENT ON COLUMN chetty_baselines.multiplier IS 'CRI boost multiplier for students overcoming barriers (1.0-2.0)';
COMMENT ON COLUMN chetty_baselines.mobility_rate IS 'Probability of bottom-to-top quintile mobility (Chetty research)';
COMMENT ON FUNCTION get_chetty_baseline IS 'Get baseline with fallback: school > zip > default';

-- =====================================================
-- ROLLBACK
-- =====================================================
-- DROP FUNCTION IF EXISTS get_chetty_baseline(TEXT, TEXT);
-- DROP TRIGGER IF EXISTS update_chetty_baselines_updated_at ON chetty_baselines;
-- DROP POLICY IF EXISTS "Allow public read access to baselines" ON chetty_baselines;
-- DROP POLICY IF EXISTS "Service role can modify baselines" ON chetty_baselines;
-- DROP TABLE IF EXISTS chetty_baselines;
