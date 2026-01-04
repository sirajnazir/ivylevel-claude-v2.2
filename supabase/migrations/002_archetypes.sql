-- =====================================================
-- IvyQuest v10.0 Migration 002: Archetypes Table
-- MIGRATE-001: Create archetypes table with default archetypes
-- =====================================================
-- Run: supabase db push OR execute in Supabase SQL Editor
-- Rollback: See bottom of file
-- =====================================================

-- Create archetypes table for student classification
CREATE TABLE IF NOT EXISTS archetypes (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  label TEXT NOT NULL UNIQUE,
  description TEXT,
  patterns JSONB DEFAULT '{}',
  coaching_approach TEXT,
  typical_challenges JSONB DEFAULT '[]',
  success_indicators JSONB DEFAULT '[]',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for active archetypes
CREATE INDEX IF NOT EXISTS idx_archetypes_active ON archetypes(is_active) WHERE is_active = true;

-- Insert default archetypes based on Jenny's coaching data
INSERT INTO archetypes (label, description, patterns, coaching_approach, typical_challenges, success_indicators) VALUES
  (
    'Constrained Gritty',
    'High-performing students overcoming significant barriers (family duties, low-SES, underrepresented). Like Huda: 5 awards, $23K raised, 6,400 students impacted.',
    '{"constraints": ["family_duties", "low_ses", "underrepresented", "work_hours"], "spikes": ["leadership", "community_impact", "resilience"]}',
    'Crisis Alchemy focus. Transform every barrier into a strength. Use CRI multipliers. Emphasize identity-driven narrative.',
    '["Time constraints from family duties", "Limited access to traditional opportunities", "Impostor syndrome despite achievements"]',
    '["CRI > 1.2", "Crisis-to-opportunity conversion rate > 80%", "Multi-touchpoint activities (4+)"]'
  ),
  (
    'Academic Achiever',
    'Strong academic foundation with research/STEM focus. Needs differentiation beyond numbers.',
    '{"constraints": [], "spikes": ["research", "academics", "intellectual_curiosity"]}',
    'Focus on translating academic excellence into narrative depth. Find the "why" behind achievements.',
    '["Over-reliance on metrics", "Generic activities", "Weak narrative coherence"]',
    '["Research publications or presentations", "Mentorship from faculty", "Clear intellectual thread"]'
  ),
  (
    'Creative Innovator',
    'Non-traditional path with arts, entrepreneurship, or creative pursuits. Strong spike but may lack structure.',
    '{"constraints": ["non_traditional"], "spikes": ["arts", "entrepreneurship", "creative_projects"]}',
    'Validate creative pursuits as legitimate. Help structure impact metrics. Connect creativity to mission.',
    '["Difficulty quantifying impact", "Parental pressure for traditional path", "Scattered portfolio"]',
    '["Portfolio with measurable reach", "Awards in creative fields", "Clear creative identity"]'
  ),
  (
    'Community Leader',
    'Service-oriented with strong local impact. May undervalue own achievements.',
    '{"constraints": ["underrepresented"], "spikes": ["service", "advocacy", "local_impact"]}',
    'Help scale local impact. Document numbers rigorously. Connect service to larger mission.',
    '["Undervaluing grassroots work", "Lack of prestigious awards", "Difficulty articulating impact"]',
    '["Quantified community impact (people served, funds raised)", "Leadership progression", "Advocacy wins"]'
  ),
  (
    'Athlete Scholar',
    'Recruited athlete balancing sports with academics. Time-constrained with unique opportunities.',
    '{"constraints": ["time_limited"], "spikes": ["athletics", "discipline", "teamwork"]}',
    'Leverage athletic narrative but diversify. Build academic credibility. Use discipline as differentiator.',
    '["Over-identification with sport", "Limited time for ECs", "Academic perception gap"]',
    '["Athletic recruitment interest", "Academic improvement trajectory", "Leadership beyond sport"]'
  ),
  (
    'Legacy Connector',
    'Family college connections with expectations. Needs to build independent identity.',
    '{"constraints": ["high_expectations"], "spikes": ["network_access", "preparation"]}',
    'Build genuine independent narrative. Leverage resources without appearing entitled. Find authentic passion.',
    '["Perceived privilege", "Authenticity questions", "Pressure to match family"]',
    '["Independent achievements", "Genuine community involvement", "Unique personal narrative"]'
  ),
  (
    'Late Bloomer',
    'Started building profile later than peers. High potential but less time to develop.',
    '{"constraints": ["time_compressed"], "spikes": ["rapid_growth", "focus"]}',
    'Prioritize high-ROI activities. Strategic Overwhelm with 1.4x capacity. Intensive Identity Seed planting.',
    '["Playing catch-up", "Anxiety about timeline", "Comparison to earlier starters"]',
    '["Steep growth trajectory", "Deep rather than broad activities", "Clear narrative of transformation"]'
  ),
  (
    'Undiscovered Gem',
    'High potential with hidden capabilities not yet surfaced. Needs discovery and articulation.',
    '{"constraints": ["undersold", "humble"], "spikes": ["hidden_projects", "untapped_potential"]}',
    'Deep discovery process. Surface hobby projects. Reframe modest self-presentation into confident narrative.',
    '["Underselling achievements", "Imposter syndrome", "Difficulty self-promoting"]',
    '["Hidden projects surfaced", "Reframed activities with impact metrics", "Confident articulation"]'
  )
ON CONFLICT (label) DO UPDATE SET
  description = EXCLUDED.description,
  patterns = EXCLUDED.patterns,
  coaching_approach = EXCLUDED.coaching_approach,
  typical_challenges = EXCLUDED.typical_challenges,
  success_indicators = EXCLUDED.success_indicators,
  updated_at = NOW();

-- Add updated_at trigger
CREATE TRIGGER update_archetypes_updated_at
  BEFORE UPDATE ON archetypes
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE archetypes ENABLE ROW LEVEL SECURITY;

-- Allow read access for all (archetypes are public reference data)
CREATE POLICY "Allow public read access to archetypes" ON archetypes
  FOR SELECT
  USING (true);

-- Only service role can modify
CREATE POLICY "Service role can modify archetypes" ON archetypes
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- Comments
COMMENT ON TABLE archetypes IS 'Student archetype classifications for personalized coaching (v10.0)';
COMMENT ON COLUMN archetypes.patterns IS 'JSON patterns: {constraints: [], spikes: []} for matching';
COMMENT ON COLUMN archetypes.coaching_approach IS 'Recommended coaching strategy for this archetype';

-- =====================================================
-- ROLLBACK (run if needed to undo this migration)
-- =====================================================
-- DROP TRIGGER IF EXISTS update_archetypes_updated_at ON archetypes;
-- DROP POLICY IF EXISTS "Allow public read access to archetypes" ON archetypes;
-- DROP POLICY IF EXISTS "Service role can modify archetypes" ON archetypes;
-- DROP TABLE IF EXISTS archetypes;
