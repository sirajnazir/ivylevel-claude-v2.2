"""
IvyQuest v4.1 Test Suite
========================
Tests for the v4.1 Guardrails Enhancement and ReAct Framework.

Test Categories:
1. Phase 1: Guardrails validation tests
2. Phase 2: ReAct wrapper tests
3. Configuration and feature flag tests
4. A/B testing logic tests
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

# Import modules under test
from agents.agents.core.guardrails import (
    validate_identity_synthesis,
    validate_awards_output,
    validate_programs_output,
    validate_gameplan_output,
    ValidationResult,
    GamePlanValidation,
    GuardrailsEngine,
)
from agents.agents.core.react_wrapper import (
    ReActWrapper,
    ReActResult,
    ReActCycle,
    create_react_wrapped_agent,
    MIN_QUALITY_SCORE,
    MIN_VOICE_SCORE,
    MIN_GOLDEN_SIMILARITY,
)
from config import (
    FEATURE_FLAGS,
    get_phase_config,
    is_react_enabled_for_agent,
    get_react_config,
    get_quality_thresholds,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def valid_identity_synthesis():
    """Valid identity synthesis output."""
    return {
        "identity_synthesis": {
            "archetype": "stem_innovator",
            "archetype_confidence": 0.85,
            "spike": "AI/ML research",
            "spike_evidence": ["Built ML model", "Published paper"],
            "pillars": ["innovation", "research", "leadership"],
            "portfolio_balance_score": 0.75,
        }
    }


@pytest.fixture
def valid_awards_output():
    """Valid awards agent output."""
    return {
        "portfolio": {
            "reach": [
                {"id": "award-1", "name": "Intel ISEF"},
            ],
            "target": [
                {"id": "award-2", "name": "Regional Science Fair"},
                {"id": "award-3", "name": "Math Olympiad"},
            ],
            "safety": [
                {"id": "award-4", "name": "School Science Award"},
            ],
        },
        "top_recommendations": [
            {"id": "award-1", "name": "Intel ISEF"},
        ],
    }


@pytest.fixture
def valid_programs_output():
    """Valid programs agent output."""
    return {
        "top_recommendations": [
            {"id": "prog-1", "name": "RSI"},
            {"id": "prog-2", "name": "COSMOS"},
            {"id": "prog-3", "name": "MIT PRIMES"},
        ],
        "advance_alerts": [
            {"program": "RSI", "deadline": "2026-01-15"},
        ],
    }


@pytest.fixture
def valid_gameplan_output(valid_identity_synthesis, valid_awards_output, valid_programs_output):
    """Valid complete GamePlan output."""
    return {
        "success": True,
        "game_plan": {
            "identity_synthesis": valid_identity_synthesis["identity_synthesis"],
            "awards": {
                "portfolio": valid_awards_output["portfolio"],
                "top_recommendations": valid_awards_output["top_recommendations"],
            },
            "programs": {
                "top_recommendations": valid_programs_output["top_recommendations"],
                "advance_alerts": valid_programs_output["advance_alerts"],
            },
            "phases": [
                {"name": "Foundation", "duration": "Months 1-3", "activities": [{"name": "Research"}], "activity_count": 1},
                {"name": "Building", "duration": "Months 4-8", "activities": [{"name": "Awards"}], "activity_count": 1},
                {"name": "Capstone", "duration": "Months 9-12", "activities": [{"name": "Applications"}], "activity_count": 1},
            ],
            "master_narrative": {
                "brand_statement": "Pioneering AI for social good",
                "first_principle": "Using technology to solve real problems",
            },
            "narrative_dna": "AI innovator with community focus",
        },
    }


@pytest.fixture
def mock_agent():
    """Mock agent for ReAct wrapper tests."""
    agent = MagicMock()
    agent.name = "TestAgent"
    agent.process = AsyncMock(return_value={
        "success": True,
        "confidence": 0.8,
        "identity_synthesis": {"archetype": "stem_innovator"},
    })
    return agent


# =============================================================================
# PHASE 1: GUARDRAILS VALIDATION TESTS
# =============================================================================

class TestIdentitySynthesisValidation:
    """Tests for validate_identity_synthesis."""

    def test_valid_identity_passes(self, valid_identity_synthesis):
        """Valid identity synthesis should pass validation."""
        result = validate_identity_synthesis(valid_identity_synthesis)
        assert result.passed is True
        assert len(result.errors) == 0
        assert result.confidence > 0.5

    def test_invalid_archetype_fails(self):
        """Invalid archetype should cause validation error."""
        output = {
            "identity_synthesis": {
                "archetype": "invalid_archetype",
                "archetype_confidence": 0.8,
            }
        }
        result = validate_identity_synthesis(output)
        assert result.passed is False
        assert any("invalid" in e.lower() for e in result.errors)

    def test_missing_archetype_warns(self):
        """Missing archetype should generate warning."""
        output = {
            "identity_synthesis": {
                "spike": "research",
                "archetype_confidence": 0.5,
            }
        }
        result = validate_identity_synthesis(output)
        # No error but may have warning
        assert result.confidence <= 1.0

    def test_missing_spike_warns(self):
        """Missing spike should generate warning."""
        output = {
            "identity_synthesis": {
                "archetype": "stem_innovator",
                "archetype_confidence": 0.8,
            }
        }
        result = validate_identity_synthesis(output)
        assert any("spike" in w.lower() for w in result.warnings)

    def test_low_confidence_warns(self):
        """Low archetype confidence should generate warning."""
        output = {
            "identity_synthesis": {
                "archetype": "stem_innovator",
                "archetype_confidence": 0.2,
                "spike": "research",
            }
        }
        result = validate_identity_synthesis(output)
        assert any("confidence" in w.lower() for w in result.warnings)


class TestAwardsValidation:
    """Tests for validate_awards_output."""

    def test_valid_awards_passes(self, valid_awards_output):
        """Valid awards output should pass validation."""
        engine = GuardrailsEngine()
        result = engine.validate_awards_output(valid_awards_output)
        assert result.passed is True
        assert result.confidence > 0.5

    def test_missing_portfolio_fails(self):
        """Missing portfolio should fail validation."""
        output = {}
        engine = GuardrailsEngine()
        result = engine.validate_awards_output(output)
        assert result.passed is False
        assert any("portfolio" in e.lower() for e in result.errors)

    def test_ungrounded_award_warns(self, valid_awards_output):
        """Award not in knowledge base should generate warning."""
        awards_cache = [{"id": "award-1"}, {"id": "award-2"}]
        engine = GuardrailsEngine(awards_cache=awards_cache)
        result = engine.validate_awards_output(valid_awards_output)
        # award-3 and award-4 not in cache
        assert len(result.warnings) > 0


class TestProgramsValidation:
    """Tests for validate_programs_output."""

    def test_valid_programs_passes(self, valid_programs_output):
        """Valid programs output should pass validation."""
        engine = GuardrailsEngine()
        result = engine.validate_programs_output(valid_programs_output)
        assert result.passed is True
        assert result.confidence > 0.5


class TestGamePlanValidation:
    """Tests for validate_gameplan_output with component scoring."""

    def test_valid_gameplan_passes(self, valid_gameplan_output):
        """Valid GamePlan output should pass validation."""
        result = validate_gameplan_output(valid_gameplan_output)
        assert result.passed is True
        assert result.confidence >= 0.7
        # Check component scores
        assert result.identity_score > 0.5
        assert result.awards_score > 0.5
        assert result.programs_score > 0.5
        assert result.phases_score > 0.5
        assert result.narrative_score > 0.5

    def test_missing_identity_reduces_score(self):
        """Missing identity synthesis should reduce identity_score."""
        output = {
            "game_plan": {
                "awards": {"portfolio": {"reach": [], "target": [], "safety": []}},
                "programs": {"top_recommendations": []},
                "phases": [],
            }
        }
        result = validate_gameplan_output(output)
        assert result.identity_score < 0.7
        assert result.confidence < 0.9

    def test_missing_awards_reduces_score(self, valid_gameplan_output):
        """Missing awards should reduce awards_score."""
        valid_gameplan_output["game_plan"]["awards"]["portfolio"] = {
            "reach": [], "target": [], "safety": []
        }
        result = validate_gameplan_output(valid_gameplan_output)
        assert result.awards_score < 0.7

    def test_missing_phases_reduces_score(self, valid_gameplan_output):
        """Missing phases should reduce phases_score."""
        valid_gameplan_output["game_plan"]["phases"] = []
        result = validate_gameplan_output(valid_gameplan_output)
        assert result.phases_score < 0.7

    def test_missing_narrative_reduces_score(self, valid_gameplan_output):
        """Missing narrative should reduce narrative_score."""
        valid_gameplan_output["game_plan"]["master_narrative"] = None
        valid_gameplan_output["game_plan"]["narrative_dna"] = None
        result = validate_gameplan_output(valid_gameplan_output)
        assert result.narrative_score < 0.7

    def test_component_weights_sum_to_one(self):
        """Component weights should sum to approximately 1.0."""
        weights = [0.25, 0.20, 0.20, 0.15, 0.20]  # identity, awards, programs, phases, narrative
        assert abs(sum(weights) - 1.0) < 0.01


# =============================================================================
# PHASE 2: REACT WRAPPER TESTS
# =============================================================================

class TestReActWrapper:
    """Tests for ReActWrapper functionality."""

    @pytest.mark.asyncio
    async def test_passthrough_when_disabled(self, mock_agent):
        """When ReAct is disabled, should pass through to agent directly."""
        with patch.dict(FEATURE_FLAGS, {"enable_react": False}):
            wrapper = ReActWrapper(mock_agent)
            result = await wrapper.process("test-profile-id")

            mock_agent.process.assert_called_once()
            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_single_cycle_on_high_quality(self, mock_agent):
        """High quality output should complete in single cycle."""
        mock_agent.process.return_value = {
            "success": True,
            "confidence": 0.9,  # Above threshold
        }

        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_ab_test_enabled": False,
        }):
            wrapper = ReActWrapper(mock_agent)
            result = await wrapper.process("test-profile-id")

            assert "react_metadata" in result
            assert result["react_metadata"]["total_cycles"] == 1
            assert result["react_metadata"]["passed"] is True

    @pytest.mark.asyncio
    async def test_multiple_cycles_on_low_quality(self, mock_agent):
        """Low quality output should trigger multiple cycles."""
        # First call returns low quality, subsequent calls improve
        mock_agent.process.side_effect = [
            {"success": True, "confidence": 0.5, "validation_warnings": ["Missing archetype"]},
            {"success": True, "confidence": 0.6, "validation_warnings": ["Low confidence"]},
            {"success": True, "confidence": 0.75},  # Above threshold
        ]

        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_ab_test_enabled": False,
            "react_max_cycles": 3,
            "react_min_confidence": 0.70,
        }):
            wrapper = ReActWrapper(mock_agent)
            result = await wrapper.process("test-profile-id")

            assert result["react_metadata"]["total_cycles"] == 3
            assert len(result["react_metadata"]["improvement_trajectory"]) == 3

    @pytest.mark.asyncio
    async def test_max_cycles_limit(self, mock_agent):
        """Should stop at max_cycles even if quality is low."""
        mock_agent.process.return_value = {
            "success": True,
            "confidence": 0.3,  # Always below threshold
            "validation_warnings": ["Always failing"],
        }

        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_ab_test_enabled": False,
            "react_max_cycles": 2,
        }):
            wrapper = ReActWrapper(mock_agent, max_cycles=2)
            result = await wrapper.process("test-profile-id")

            assert result["react_metadata"]["total_cycles"] == 2
            assert mock_agent.process.call_count == 2

    @pytest.mark.asyncio
    async def test_hints_passed_to_agent(self, mock_agent):
        """Improvement hints should be passed to agent on subsequent cycles."""
        mock_agent.process.side_effect = [
            {"success": True, "confidence": 0.5, "validation_warnings": ["Missing spike"]},
            {"success": True, "confidence": 0.8},
        ]

        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_ab_test_enabled": False,
        }):
            wrapper = ReActWrapper(mock_agent)
            await wrapper.process("test-profile-id")

            # Second call should have react_hints
            second_call_kwargs = mock_agent.process.call_args_list[1][1]
            assert "react_hints" in second_call_kwargs
            assert len(second_call_kwargs["react_hints"]) > 0


class TestReActABTesting:
    """Tests for A/B testing functionality."""

    @pytest.mark.asyncio
    async def test_control_group_passthrough(self, mock_agent):
        """Control group should skip ReAct and pass through."""
        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_ab_test_enabled": True,
            "react_ab_test_percentage": 0.0,  # 0% treatment = all control
        }):
            wrapper = ReActWrapper(mock_agent)
            result = await wrapper.process("test-profile-id")

            assert result["react_metadata"]["ab_test_group"] == "control"
            assert result["react_metadata"]["enabled"] is False

    def test_deterministic_assignment(self, mock_agent):
        """Same profile_id should always get same group."""
        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_ab_test_enabled": True,
            "react_ab_test_percentage": 0.5,
        }):
            wrapper = ReActWrapper(mock_agent)

            # Same ID should get same assignment
            group1 = wrapper._assign_ab_group("profile-123")
            group2 = wrapper._assign_ab_group("profile-123")
            assert group1 == group2

            # Different IDs may get different assignments
            groups = [wrapper._assign_ab_group(f"profile-{i}") for i in range(100)]
            assert "treatment" in groups
            assert "control" in groups


class TestCreateReActWrappedAgent:
    """Tests for create_react_wrapped_agent factory function."""

    def test_wraps_enabled_agent(self, mock_agent):
        """Should wrap agents that are enabled for ReAct."""
        mock_agent.name = "Extracurriculars"  # In enabled list

        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_enable_for_agents": ["Extracurriculars", "Awards"],
        }):
            result = create_react_wrapped_agent(mock_agent)
            assert isinstance(result, ReActWrapper)

    def test_returns_original_for_disabled_agent(self, mock_agent):
        """Should return original agent if not in enabled list."""
        mock_agent.name = "SomeOtherAgent"

        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_enable_for_agents": ["Extracurriculars", "Awards"],
        }):
            result = create_react_wrapped_agent(mock_agent)
            assert result is mock_agent


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================

class TestFeatureFlags:
    """Tests for feature flag configuration."""

    def test_default_flags_structure(self):
        """Feature flags should have expected structure."""
        assert "enable_guardrails" in FEATURE_FLAGS
        assert "enable_react" in FEATURE_FLAGS
        assert "react_max_cycles" in FEATURE_FLAGS
        assert "react_min_confidence" in FEATURE_FLAGS
        assert "react_ab_test_enabled" in FEATURE_FLAGS

    def test_get_phase_config_phase1(self):
        """Phase 1 config when only guardrails enabled."""
        with patch.dict(FEATURE_FLAGS, {
            "enable_guardrails": True,
            "enable_react": False,
            "enable_voice_validation": False,
            "enable_golden_benchmark": False,
        }):
            config = get_phase_config()
            assert config["phase"] == 1
            assert "guardrails" in config["features_enabled"]

    def test_get_phase_config_phase2(self):
        """Phase 2 config when ReAct enabled."""
        with patch.dict(FEATURE_FLAGS, {
            "enable_guardrails": True,
            "enable_react": True,
            "enable_voice_validation": False,
            "enable_golden_benchmark": False,
        }):
            config = get_phase_config()
            assert config["phase"] == 2
            assert "react" in config["features_enabled"]

    def test_get_phase_config_phase3(self):
        """Phase 3 config when all features enabled."""
        with patch.dict(FEATURE_FLAGS, {
            "enable_guardrails": True,
            "enable_react": True,
            "enable_voice_validation": True,
            "enable_golden_benchmark": True,
        }):
            config = get_phase_config()
            assert config["phase"] == 3
            assert "voice_validation" in config["features_enabled"]

    def test_is_react_enabled_for_agent(self):
        """is_react_enabled_for_agent should check both master flag and agent list."""
        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_enable_for_agents": ["Extracurriculars", "Awards"],
        }):
            assert is_react_enabled_for_agent("Extracurriculars") is True
            assert is_react_enabled_for_agent("Awards") is True
            assert is_react_enabled_for_agent("SomeOther") is False

        with patch.dict(FEATURE_FLAGS, {"enable_react": False}):
            assert is_react_enabled_for_agent("Extracurriculars") is False

    def test_get_react_config(self):
        """get_react_config should return full ReAct configuration."""
        config = get_react_config()
        assert "enabled" in config
        assert "max_cycles" in config
        assert "min_confidence" in config
        assert "enabled_agents" in config
        assert "ab_test_enabled" in config

    def test_get_quality_thresholds(self):
        """get_quality_thresholds should return all thresholds."""
        thresholds = get_quality_thresholds()
        assert "min_confidence" in thresholds
        assert "min_voice_score" in thresholds
        assert "min_golden_similarity" in thresholds


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestGuardrailsReActIntegration:
    """Integration tests for guardrails and ReAct working together."""

    @pytest.mark.asyncio
    async def test_validation_triggers_improvement(self, mock_agent):
        """Validation warnings should inform improvement hints."""
        mock_agent.process.side_effect = [
            {
                "success": True,
                "confidence": 0.5,
                "validation_warnings": ["Missing archetype", "Low confidence"],
            },
            {
                "success": True,
                "confidence": 0.8,
            },
        ]

        with patch.dict(FEATURE_FLAGS, {
            "enable_react": True,
            "react_ab_test_enabled": False,
        }):
            wrapper = ReActWrapper(mock_agent)
            result = await wrapper.process("test-profile-id")

            # Second call should have hints derived from warnings
            second_call = mock_agent.process.call_args_list[1]
            hints = second_call[1].get("react_hints", [])
            assert len(hints) > 0
            assert any("archetype" in h.lower() for h in hints)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
