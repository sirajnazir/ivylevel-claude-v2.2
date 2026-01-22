# agents/tests/test_react_base.py
"""
IvyQuest v13.2 - ReAct Framework Unit Tests

Tests for:
- QualityThresholds - Threshold values and calculations
- AutonomyLevel - HITL requirements
- Observation - Combined scoring and threshold checks
- ReActCycle - Serialization
- RunContext - Learning injection
"""

import pytest
from datetime import datetime

from agents.agents.core.thresholds import QualityThresholds, AutonomyLevel
from agents.agents.core.react_types import (
    ThoughtProcess, ActionResult, Observation, Learning, 
    ReActCycle, ReasoningPhase, RunContext
)


class TestQualityThresholds:
    """Test quality threshold constants and calculations."""

    def test_threshold_values(self):
        """Verify threshold constants are set correctly."""
        assert QualityThresholds.MIN_QUALITY_SCORE == 70
        assert QualityThresholds.MIN_VOICE_SCORE == 70
        assert QualityThresholds.MIN_GOLDEN_SIMILARITY == 0.6
        assert QualityThresholds.MAX_REACT_CYCLES == 3

    def test_weight_sum(self):
        """Weights should sum to 1.0."""
        total = (
            QualityThresholds.WEIGHT_QUALITY +
            QualityThresholds.WEIGHT_VOICE +
            QualityThresholds.WEIGHT_GOLDEN
        )
        assert total == pytest.approx(1.0)

    def test_compute_combined_balanced(self):
        """Test combined score with balanced inputs."""
        # 80*0.4 + 80*0.3 + (0.8*100)*0.3 = 32 + 24 + 24 = 80
        result = QualityThresholds.compute_combined(80, 80, 0.8)
        assert result == pytest.approx(80.0)

    def test_compute_combined_varied(self):
        """Test combined score with varied inputs."""
        # 90*0.4 + 70*0.3 + (0.5*100)*0.3 = 36 + 21 + 15 = 72
        result = QualityThresholds.compute_combined(90, 70, 0.5)
        assert result == pytest.approx(72.0)

    def test_passes_all_true(self):
        """Test when all thresholds pass."""
        assert QualityThresholds.passes_all(70, 70, 0.6) is True
        assert QualityThresholds.passes_all(85, 90, 0.8) is True
        assert QualityThresholds.passes_all(100, 100, 1.0) is True

    def test_passes_all_false(self):
        """Test when thresholds fail."""
        # Quality fails
        assert QualityThresholds.passes_all(69, 70, 0.6) is False
        # Voice fails
        assert QualityThresholds.passes_all(70, 69, 0.6) is False
        # Golden fails
        assert QualityThresholds.passes_all(70, 70, 0.59) is False
        # All fail
        assert QualityThresholds.passes_all(50, 50, 0.3) is False

    def test_get_failing_dimensions_all_pass(self):
        """No failures when all pass."""
        failures = QualityThresholds.get_failing_dimensions(80, 80, 0.7)
        assert len(failures) == 0

    def test_get_failing_dimensions_quality_fails(self):
        """Identify quality failure."""
        failures = QualityThresholds.get_failing_dimensions(65, 80, 0.7)
        assert len(failures) == 1
        assert "quality" in failures[0]

    def test_get_failing_dimensions_multiple(self):
        """Identify multiple failures."""
        failures = QualityThresholds.get_failing_dimensions(65, 65, 0.5)
        assert len(failures) == 3


class TestAutonomyLevel:
    """Test autonomy level HITL requirements."""

    def test_full_never_requires_hitl(self):
        """FULL autonomy never requires HITL."""
        assert AutonomyLevel.requires_hitl(AutonomyLevel.FULL, 0.1) is False
        assert AutonomyLevel.requires_hitl(AutonomyLevel.FULL, 0.5) is False
        assert AutonomyLevel.requires_hitl(AutonomyLevel.FULL, 0.9) is False
        assert AutonomyLevel.requires_hitl(AutonomyLevel.FULL, 1.0) is False

    def test_high_threshold(self):
        """HIGH requires HITL below 70%."""
        assert AutonomyLevel.requires_hitl(AutonomyLevel.HIGH, 0.69) is True
        assert AutonomyLevel.requires_hitl(AutonomyLevel.HIGH, 0.70) is False
        assert AutonomyLevel.requires_hitl(AutonomyLevel.HIGH, 0.71) is False
        assert AutonomyLevel.requires_hitl(AutonomyLevel.HIGH, 0.9) is False

    def test_medium_threshold(self):
        """MEDIUM requires HITL below 85%."""
        assert AutonomyLevel.requires_hitl(AutonomyLevel.MEDIUM, 0.80) is True
        assert AutonomyLevel.requires_hitl(AutonomyLevel.MEDIUM, 0.84) is True
        assert AutonomyLevel.requires_hitl(AutonomyLevel.MEDIUM, 0.85) is False
        assert AutonomyLevel.requires_hitl(AutonomyLevel.MEDIUM, 0.90) is False

    def test_low_always_requires_hitl(self):
        """LOW always requires HITL."""
        assert AutonomyLevel.requires_hitl(AutonomyLevel.LOW, 0.0) is True
        assert AutonomyLevel.requires_hitl(AutonomyLevel.LOW, 0.5) is True
        assert AutonomyLevel.requires_hitl(AutonomyLevel.LOW, 0.99) is True
        assert AutonomyLevel.requires_hitl(AutonomyLevel.LOW, 1.0) is True

    def test_enum_values(self):
        """Test enum string values."""
        assert AutonomyLevel.FULL.value == "full"
        assert AutonomyLevel.HIGH.value == "high"
        assert AutonomyLevel.MEDIUM.value == "medium"
        assert AutonomyLevel.LOW.value == "low"


class TestObservation:
    """Test Observation combined scoring."""

    def test_combined_score_calculation(self):
        """Combined score uses correct weights."""
        obs = Observation(
            quality_score=80,
            voice_score=80,
            golden_similarity=0.8,
        )
        # 80*0.4 + 80*0.3 + 80*0.3 = 32 + 24 + 24 = 80
        assert obs.combined_score == pytest.approx(80.0)

    def test_combined_score_mixed(self):
        """Test mixed score values."""
        obs = Observation(
            quality_score=100,
            voice_score=50,
            golden_similarity=0.5,
        )
        # 100*0.4 + 50*0.3 + 50*0.3 = 40 + 15 + 15 = 70
        assert obs.combined_score == pytest.approx(70.0)

    def test_passes_thresholds_all_pass(self):
        """Passes when all scores meet thresholds."""
        obs = Observation(
            quality_score=75,
            voice_score=75,
            golden_similarity=0.65,
        )
        assert obs.passes_thresholds is True

    def test_passes_thresholds_quality_fails(self):
        """Fails when quality below threshold."""
        obs = Observation(
            quality_score=65,  # Below 70
            voice_score=75,
            golden_similarity=0.65,
        )
        assert obs.passes_thresholds is False

    def test_passes_thresholds_voice_fails(self):
        """Fails when voice below threshold."""
        obs = Observation(
            quality_score=75,
            voice_score=65,  # Below 70
            golden_similarity=0.65,
        )
        assert obs.passes_thresholds is False

    def test_passes_thresholds_golden_fails(self):
        """Fails when golden below threshold."""
        obs = Observation(
            quality_score=75,
            voice_score=75,
            golden_similarity=0.55,  # Below 0.6
        )
        assert obs.passes_thresholds is False

    def test_failing_dimensions(self):
        """Test failing dimensions property."""
        obs = Observation(
            quality_score=65,
            voice_score=65,
            golden_similarity=0.55,
        )
        assert len(obs.failing_dimensions) == 3

    def test_to_dict(self):
        """Test serialization."""
        obs = Observation(
            quality_score=80,
            voice_score=75,
            golden_similarity=0.7,
            issues_found=["Minor issue"],
            strengths=["Good structure"],
        )
        data = obs.to_dict()
        
        assert data["quality_score"] == 80
        assert data["voice_score"] == 75
        assert data["golden_similarity"] == 0.7
        assert "combined_score" in data
        assert "passes_thresholds" in data
        assert data["issues_found"] == ["Minor issue"]


class TestThoughtProcess:
    """Test ThoughtProcess dataclass."""

    def test_creation(self):
        """Test basic creation."""
        thought = ThoughtProcess(
            thought="I should analyze the profile",
            reasoning="The student needs narrative synthesis",
            planned_action="generate_narrative",
            confidence=0.85,
            context_factors=["archetype", "spike"],
        )
        
        assert thought.thought == "I should analyze the profile"
        assert thought.confidence == 0.85
        assert len(thought.context_factors) == 2

    def test_to_dict(self):
        """Test serialization."""
        thought = ThoughtProcess(
            thought="Test",
            reasoning="Test reasoning",
            planned_action="test_action",
            confidence=0.9,
            context_factors=["factor1"],
            alternative_approaches=["alt1", "alt2"],
        )
        data = thought.to_dict()
        
        assert data["thought"] == "Test"
        assert data["confidence"] == 0.9
        assert data["alternatives"] == ["alt1", "alt2"]
        assert "timestamp" in data


class TestActionResult:
    """Test ActionResult dataclass."""

    def test_creation(self):
        """Test basic creation."""
        action = ActionResult(
            action_name="generate_content",
            tool_used="llm",
            input_data={"prompt": "test"},
            output_data={"content": "generated"},
            success=True,
        )
        
        assert action.action_name == "generate_content"
        assert action.success is True
        assert action.output_data["content"] == "generated"

    def test_with_error(self):
        """Test failed action."""
        action = ActionResult(
            action_name="api_call",
            tool_used=None,
            input_data={},
            output_data={},
            success=False,
            error_message="Connection failed",
        )
        
        assert action.success is False
        assert action.error_message == "Connection failed"


class TestLearning:
    """Test Learning dataclass."""

    def test_creation(self):
        """Test basic creation."""
        learning = Learning(
            successful_patterns=["Pattern A worked"],
            failed_patterns=["Pattern B failed"],
            adjustments_made=["Increased detail"],
            confidence_delta=0.1,
        )
        
        assert len(learning.successful_patterns) == 1
        assert learning.confidence_delta == 0.1

    def test_alternative(self):
        """Test alternative suggestion."""
        learning = Learning(
            successful_patterns=[],
            should_try_alternative=True,
            alternative_to_try="Use different approach",
        )
        
        assert learning.should_try_alternative is True
        assert learning.alternative_to_try == "Use different approach"


class TestReActCycle:
    """Test ReActCycle serialization."""

    def test_to_dict(self):
        """Test cycle serialization."""
        thought = ThoughtProcess(
            thought="Test thought",
            reasoning="Test reasoning",
            planned_action="test_action",
            confidence=0.8,
            context_factors=["factor1"],
        )
        action = ActionResult(
            action_name="test_action",
            tool_used=None,
            input_data={},
            output_data={"result": "test"},
            success=True,
        )
        observation = Observation(
            quality_score=85,
            voice_score=80,
            golden_similarity=0.75,
        )
        learning = Learning(
            successful_patterns=["pattern1"],
        )

        cycle = ReActCycle(
            cycle_number=1,
            thought=thought,
            action=action,
            observation=observation,
            learning=learning,
            total_duration_ms=100.0,
        )

        data = cycle.to_dict()

        assert data["cycle_number"] == 1
        assert data["thought"]["confidence"] == 0.8
        assert data["action"]["success"] is True
        assert data["observation"]["quality_score"] == 85
        assert "pattern1" in data["learning"]["successful_patterns"]
        assert data["total_duration_ms"] == 100.0

    def test_passed_property(self):
        """Test passed property."""
        cycle = ReActCycle(
            cycle_number=1,
            thought=ThoughtProcess(
                thought="t", reasoning="r", planned_action="a",
                confidence=0.8, context_factors=[]
            ),
            action=ActionResult(
                action_name="a", tool_used=None,
                input_data={}, output_data={}, success=True
            ),
            observation=Observation(
                quality_score=80, voice_score=80, golden_similarity=0.7
            ),
            learning=Learning(),
            total_duration_ms=50.0,
        )
        
        assert cycle.passed is True

    def test_summary(self):
        """Test summary property."""
        cycle = ReActCycle(
            cycle_number=2,
            thought=ThoughtProcess(
                thought="t", reasoning="r", planned_action="a",
                confidence=0.8, context_factors=[]
            ),
            action=ActionResult(
                action_name="a", tool_used=None,
                input_data={}, output_data={}, success=True
            ),
            observation=Observation(
                quality_score=65, voice_score=70, golden_similarity=0.5
            ),
            learning=Learning(),
            total_duration_ms=50.0,
        )
        
        summary = cycle.summary
        assert "Cycle 2" in summary
        assert "FAIL" in summary
        assert "65" in summary


class TestRunContext:
    """Test RunContext learning injection."""

    def test_basic_creation(self):
        """Test basic context creation."""
        ctx = RunContext(
            profile_id="test-123",
            session_id="session-456",
            archetype="DoubleDown",
        )
        
        assert ctx.profile_id == "test-123"
        assert ctx.archetype == "DoubleDown"
        assert ctx.has_learnings is False

    def test_with_learnings(self):
        """Test learning injection creates new context."""
        ctx = RunContext(profile_id="test-123")
        
        learnings = {
            "issues_to_fix": ["Quality too low"],
            "corrections_required": ["Add more detail"],
        }
        
        new_ctx = ctx.with_learnings(learnings)
        
        # Original unchanged
        assert ctx.has_learnings is False
        
        # New context has learnings
        assert new_ctx.has_learnings is True
        assert new_ctx.learnings["issues_to_fix"] == ["Quality too low"]
        assert new_ctx.profile_id == "test-123"  # Other fields preserved

    def test_learnings_property(self):
        """Test learnings property returns empty dict when none."""
        ctx = RunContext(profile_id="test")
        assert ctx.learnings == {}

    def test_to_dict(self):
        """Test serialization."""
        ctx = RunContext(
            profile_id="test-123",
            session_id="session-456",
            user_id="user-789",
            archetype="Trailblazer",
        )
        data = ctx.to_dict()
        
        assert data["profile_id"] == "test-123"
        assert data["session_id"] == "session-456"
        assert data["archetype"] == "Trailblazer"
        assert data["has_learnings"] is False


class TestReasoningPhase:
    """Test ReasoningPhase enum."""

    def test_values(self):
        """Test phase values."""
        assert ReasoningPhase.CONTEXT_GATHERING.value == "context_gathering"
        assert ReasoningPhase.PLANNING.value == "planning"
        assert ReasoningPhase.EXECUTION.value == "execution"
        assert ReasoningPhase.EVALUATION.value == "evaluation"
        assert ReasoningPhase.CORRECTION.value == "correction"
