# Master Specification Changelog

All notable changes to the IvyQuest Master Specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- (Pending changes go here)

---

## [1.0.0] - 2026-01-12

### Added

#### Strategic Intelligence Schema
- New field: `strategic_tier` (1-4) - Strategic value assessment for awards and programs
- New field: `strategic_notes` - Key strategic insight (IQ-focused, not voice/tone)
- New field: `success_patterns` - Array of actionable patterns that lead to wins
- New field: `common_mistakes` - Array of pitfalls to avoid
- New field: `archetype_fit` - Object with 8 archetype compatibility scores (0.0-1.0):
  - `academic_powerhouse`
  - `stem_innovator`
  - `creative_visionary`
  - `community_changemaker`
  - `entrepreneurial_leader`
  - `humanities_scholar`
  - `athletic_scholar`
  - `multi_hyphenate`
- New field: `differentiation_factor` - What makes winners stand out

#### Awards-Specific Fields
- New field: `win_cascade.position` - "entry" | "building" | "capstone"
- New field: `win_cascade.prerequisites` - Array of prerequisite award IDs
- New field: `win_cascade.enables` - Array of awards this enables
- New field: `timing.ideal_grades` - Array of optimal grade levels
- New field: `timing.prep_weeks` - Weeks needed to prepare
- New field: `timing.deadline_strategy` - Timing approach guidance

#### Programs-Specific Fields
- New field: `hidden_value` - Array of non-obvious benefits
- New field: `synergies.pairs_well_with` - Complementary program IDs
- New field: `synergies.leads_to` - Opportunities this unlocks
- New field: `timing.application_intensity` - "light" | "moderate" | "heavy"

#### Classification Rules
- Tier assignment logic based on acceptance rate and prestige score
- Archetype fit calculation based on category and keyword matching
- Win cascade position determination logic

### Changed
- Renamed `jenny_tier` -> `strategic_tier` (IQ-focused, not personality)
- Renamed `jenny_notes` -> `strategic_notes` (IQ-focused, not voice/tone)

### Deprecated
- None

### Removed
- EQ-layer fields (parked for future phase):
  - Voice/tone guidance
  - Communication style preferences

---

## [0.x.x] - Prior Versions

### Initial Data Schema
- Basic award fields: id, name, organization, category, level, description
- Basic program fields: id, name, organization, type, category, description
- Eligibility fields: grades, gender, citizenship
- Metrics: prestige_score, historical_win_rate, acceptance_rate, effort_hours

---

## Version History Reference

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-12 | Strategic Intelligence Enrichment |
| 0.x.x | Prior | Initial data schema |

---

*Maintained by: IvyLevel Engineering*
