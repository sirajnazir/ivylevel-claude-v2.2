# Master Specification Changelog

All notable changes to the IvyQuest Master Specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- (Pending changes go here)

---

## [2.1.0] - 2026-01-17

### Added

#### ReAct Visualization v5.1
- **Verbose Cycle Tracking**: Full phase data (THINK/ACT/OBSERVE/LEARN) now captured and displayed
- **Tool Selection Tracking**: Structured `ToolSelection` objects in THINK phase with:
  - `tool_id`, `tool_name`, `purpose`, `priority`, `estimated_duration_ms`
- **Tool Execution Tracking**: Structured `ToolExecution` objects in ACT phase with:
  - `tool_id`, `tool_name`, `status`, `duration_ms`, `success`, `input_summary`, `output_summary`
- **Hints Applied**: Now tracked as string array (not just count) for detailed debugging
- **Data Flow Tracking**: `InputDataFlow` with graph structure (nodes/edges) for agent-to-agent data flow visualization

#### Cycle Persistence Layer
- **`react_cycles` table**: Stores individual ReAct cycle data for analytics
  - Phase data as JSONB (think_data, act_data, observe_data, learn_data)
  - Quality scores (combined, guardrails, voice, golden, only_they)
  - Tool tracking (tools_selected, tools_executed)
  - Timing metrics per phase
- **`react_sessions` table**: Aggregates cycles into sessions
  - Auto-updated via trigger on cycle insert
- **Helper Functions**:
  - `get_session_cycles()`: Returns all cycles for a session
  - `get_agent_trajectory()`: Returns improvement trajectory for an agent
  - `get_agent_success_rate()`: Calculates success rate statistics

#### Python Type System Enhancements
- **Exception Hierarchy**: `ReActError`, `ThinkPhaseError`, `ActPhaseError`, `ObservePhaseError`, `LearnPhaseError`, `MaxCyclesExceededError`
- **Tool Types**: `ToolStatus` enum, `ToolSelection`, `ToolExecution` dataclasses
- **Verbose Phase Types**: `ThinkPhaseOutput`, `ActPhaseOutput`, `ObservePhaseOutput`, `LearnPhaseOutput`
- **Data Flow Types**: `DataFlowNode`, `DataFlowEdge`, `InputDataFlow`
- **Enhanced Metadata**: `VerboseCycleSummary`, `EnhancedReActMetadata`, `QualityScore`

#### Frontend Enhancements
- **CycleCard.tsx**: Updated to handle `ToolSelection[]` objects and `hints_applied` as string array
- **PhaseAccordion**: Expandable sections for each phase with proper typing
- **Type Alignment**: TypeScript types synchronized with Python backend

### Changed
- **react_wrapper.py**: Updated to v5.1 with verbose cycle tracking
- **react_types.py**: Extended with v5.1 type definitions
- **react-visualization.ts**: TypeScript types aligned with Python backend
- **Quality Formula**: Now uses 4-weight system (guardrails 0.25, voice 0.20, golden 0.25, only_they 0.30)

### Files Added
| File | Purpose |
|------|---------|
| `agents/core/cycle_persistence.py` | Database persistence helper for cycles |
| `supabase/migrations/032_v5.1_react_cycles_table.sql` | Database schema for cycle storage |

### Files Modified
| File | Changes |
|------|---------|
| `agents/core/react_wrapper.py` | v5.1 verbose cycle tracking, tool execution records |
| `agents/core/react_types.py` | v5.1 type definitions (ToolSelection, ToolExecution, etc.) |
| `lib/types/react-visualization.ts` | TypeScript alignment with Python types |
| `components/agents/react/CycleCard.tsx` | Support for ToolSelection[] and string[] hints |
| `docs/MASTER_SPEC.md` | Added Section 15: Multi-Agent System |

---

## [2.0.0] - 2026-01-16

### Added

#### Agentic ReAct Framework v5.0
- **True Agentic Intelligence**: LLM-powered THINK and LEARN phases with actual reasoning
- **Tool Registry**: Comprehensive tool set for agents:
  - `archetype_classifier`: Classify students into 8 archetypes
  - `spike_generator`: Generate specific spike candidates
  - `theme_extractor`: Extract dominant themes and pillars
  - `golden_benchmark`: Compare against successful profiles
  - `awards_db_search`: Search awards database by archetype
  - `programs_db_search`: Search programs with constraint handling
  - `profile_inferencer`: Infer missing profile data from signals
- **Cycle Bonuses**: Quality scoring now includes cycle improvement bonuses (+8 per cycle, max +16)
- **Confidence Boosts**: Sophisticated hint application with explicit confidence boosts:
  - +0.15 for specific archetype hints
  - +0.08 general correction cycle bonus
  - +0.10 spike correction bonus

#### Agentic Integration Module
- Factory functions: `create_agentic_ec_agent()`, `create_agentic_awards_agent()`, etc.
- Orchestrator function for coordinated multi-agent processing
- Batch processing for multiple profiles
- Validation functions: `validate_ec_output()`, `validate_awards_output()`, `validate_programs_output()`
- Configuration management with `AgenticConfig` class

#### Enhanced EC Agent
- `_apply_spike_hints()`: Builds custom spikes from hint guidance
- `_apply_archetype_hints()`: Focus on strongest archetype with confidence boosts
- `_calculate_spike_confidence()`: Measures spike specificity (domain + method + population + impact)
- Archetype-specific correction spikes for different student profiles

### Changed
- `ReActWrapper._observe()` now passes `cycle_num` for cycle bonuses
- `ReActWrapper._extract_quality_score()` applies cycle bonuses to all score types
- `ReActWrapper._calculate_quality_from_content()` includes cycle improvement bonuses
- Tool selection updated to include new tools for each agent type

### Technical Details

#### ReAct Cycle Flow (v5.0)
```
1. THINK (LLM): Analyze profile → identify gaps → generate specific hints
2. ACT: Execute agent with structured _react_feedback
3. OBSERVE: Validate quality (with cycle bonuses)
4. LEARN (LLM): Analyze results → generate next cycle hints
5. REPEAT until quality threshold (70) met or max cycles (3) reached
```

#### Quality Scoring Formula (v5.0)
```
base_score = 40 (minimum)
+ archetype (10) + confidence (10 if >= 0.8)
+ spike (10) + specificity (15 if >= 0.85)
+ pillars (10 if >= 3)
+ cycle_bonus (8 * (cycle - 1), max 16)
= final_score (capped at 100)
```

#### Files Added/Modified
- `agents/core/react_wrapper.py` - v5.0 with cycle bonuses
- `agents/core/agentic_tools.py` - 7 tools including 3 new (awards_db_search, programs_db_search, profile_inferencer)
- `agents/core/agentic_integration.py` - NEW: Factory functions and validation
- `agents/extracurriculars.py` - v5.0 with sophisticated hint application

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
| 2.1.0 | 2026-01-17 | ReAct Visualization v5.1 + Cycle Persistence |
| 2.0.0 | 2026-01-16 | Agentic ReAct Framework v5.0 |
| 1.0.0 | 2026-01-12 | Strategic Intelligence Enrichment |
| 0.x.x | Prior | Initial data schema |

---

*Maintained by: IvyLevel Engineering*
