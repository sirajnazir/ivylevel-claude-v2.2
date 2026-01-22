# agents/tests/test_memory.py
"""
IvyQuest v13.2 - Memory System Unit Tests

Tests for:
- WorkingMemoryBuffer - Working memory operations
- EvaluationFrame - Evaluation recording
- Improvement trend calculation
"""

import pytest
from datetime import datetime

from agents.agents.core.working_memory import (
    WorkingMemoryBuffer,
    ContextFrame,
    PlannedAction,
    OptionAnalysis,
    EvaluationFrame,
    LearningFrame,
    ReasoningPhase,
)


class TestWorkingMemoryBuffer:
    """Test WorkingMemoryBuffer operations."""

    def test_creation(self):
        """Test buffer creation."""
        buffer = WorkingMemoryBuffer("assessment", "profile-123")
        
        assert buffer.agent_name == "assessment"
        assert buffer.profile_id == "profile-123"
        assert buffer.context is None
        assert len(buffer.evaluations) == 0
        assert buffer.current_phase == ReasoningPhase.CONTEXT_GATHERING

    def test_set_context(self):
        """Test setting context transitions phase."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        context = ContextFrame(
            profile_summary={"name": "Test"},
            relevant_memories=[],
            coaching_knowledge=[],
            active_tasks=[],
            recent_interactions=[],
        )
        buffer.set_context(context)
        
        assert buffer.context is not None
        assert buffer.current_phase == ReasoningPhase.PLANNING

    def test_plan_action(self):
        """Test planning an action."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        action = buffer.plan_action(
            action_type="generate",
            description="Generate narrative",
            expected_outcome="High-quality narrative",
            confidence=0.85,
            dependencies=["profile_loaded"],
        )
        
        assert len(buffer.planned_actions) == 1
        assert action.action_type == "generate"
        assert action.confidence == 0.85
        assert "profile_loaded" in action.dependencies

    def test_analyze_option(self):
        """Test option analysis."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        option = buffer.analyze_option(
            option_name="Approach A",
            pros=["Fast", "Reliable"],
            cons=["Less creative"],
            fit_score=0.8,
            risk_level="low",
            recommended=True,
        )
        
        assert len(buffer.options_analyzed) == 1
        assert option.option_name == "Approach A"
        assert option.recommended is True
        assert option.fit_score == 0.8

    def test_record_evaluation_passing(self):
        """Test recording a passing evaluation."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        eval_frame = buffer.record_evaluation(
            cycle=1,
            quality=80,
            voice=75,
            golden=0.7,
            issues=[],
            strengths=["Good quality"],
        )
        
        assert len(buffer.evaluations) == 1
        assert eval_frame.passes_threshold is True
        assert eval_frame.needs_correction is False
        assert buffer.current_phase == ReasoningPhase.EVALUATION

    def test_record_evaluation_failing(self):
        """Test recording a failing evaluation."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        eval_frame = buffer.record_evaluation(
            cycle=1,
            quality=65,
            voice=70,
            golden=0.55,
            issues=["Quality below threshold"],
            strengths=[],
        )
        
        assert eval_frame.passes_threshold is False
        assert eval_frame.needs_correction is True
        assert buffer.current_phase == ReasoningPhase.CORRECTION

    def test_improvement_trend_no_evals(self):
        """Test trend with no evaluations."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        trend = buffer.get_improvement_trend()
        assert trend["quality"] == 0.0
        assert trend["voice"] == 0.0
        assert trend["golden"] == 0.0

    def test_improvement_trend_one_eval(self):
        """Test trend with single evaluation."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        buffer.record_evaluation(1, 70, 70, 0.6, [], [])
        
        trend = buffer.get_improvement_trend()
        assert trend["quality"] == 0.0

    def test_improvement_trend_multiple_evals(self):
        """Test improvement trend calculation."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        # First evaluation (bad)
        buffer.record_evaluation(
            cycle=1,
            quality=65,
            voice=70,
            golden=0.55,
            issues=["Quality below threshold"],
            strengths=["Voice acceptable"],
        )
        
        # Second evaluation (improved)
        buffer.record_evaluation(
            cycle=2,
            quality=75,
            voice=78,
            golden=0.65,
            issues=[],
            strengths=["All thresholds met"],
        )
        
        trend = buffer.get_improvement_trend()
        
        assert trend["quality"] == 10.0  # 75 - 65
        assert trend["voice"] == 8.0     # 78 - 70
        assert trend["golden"] == pytest.approx(0.1)  # 0.65 - 0.55

    def test_record_successful_strategy(self):
        """Test recording successful strategy."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        buffer.record_successful_strategy(
            strategy="Use detailed examples",
            context="narrative synthesis",
            quality=85,
        )
        
        assert len(buffer.learning.successful_strategies) == 1
        assert buffer.learning.successful_strategies[0]["quality_achieved"] == 85

    def test_record_failed_approach(self):
        """Test recording failed approach."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        buffer.record_failed_approach("Too generic response")
        
        assert len(buffer.learning.failed_approaches) == 1
        assert "Too generic" in buffer.learning.failed_approaches[0]

    def test_add_context_insight(self):
        """Test adding context insight."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        buffer.add_context_insight("Student prefers detailed feedback")
        
        assert len(buffer.learning.context_insights) == 1

    def test_update_user_preference(self):
        """Test updating user preference."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        buffer.update_user_preference("tone", "warm")
        buffer.update_user_preference("detail_level", "high")
        
        assert buffer.learning.user_preferences["tone"] == "warm"
        assert buffer.learning.user_preferences["detail_level"] == "high"

    def test_get_latest_evaluation(self):
        """Test getting latest evaluation."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        assert buffer.get_latest_evaluation() is None
        
        buffer.record_evaluation(1, 70, 70, 0.6, [], [])
        buffer.record_evaluation(2, 80, 80, 0.7, [], [])
        
        latest = buffer.get_latest_evaluation()
        assert latest.cycle_number == 2
        assert latest.quality_score == 80

    def test_get_all_issues(self):
        """Test getting all issues across evaluations."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        buffer.record_evaluation(1, 65, 70, 0.6, ["Issue A", "Issue B"], [])
        buffer.record_evaluation(2, 70, 65, 0.6, ["Issue B", "Issue C"], [])
        
        issues = buffer.get_all_issues()
        assert "Issue A" in issues
        assert "Issue B" in issues
        assert "Issue C" in issues
        assert len(issues) == 3  # Deduplicated

    def test_get_all_strengths(self):
        """Test getting all strengths across evaluations."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        buffer.record_evaluation(1, 80, 80, 0.7, [], ["Strength A"])
        buffer.record_evaluation(2, 85, 85, 0.8, [], ["Strength B"])
        
        strengths = buffer.get_all_strengths()
        assert "Strength A" in strengths
        assert "Strength B" in strengths

    def test_clear(self):
        """Test clearing the buffer."""
        buffer = WorkingMemoryBuffer("test", "p-123")
        
        # Add some data
        buffer.set_context(ContextFrame({}, [], [], [], []))
        buffer.record_evaluation(1, 80, 80, 0.7, [], [])
        buffer.scratch["key"] = "value"
        
        # Clear
        buffer.clear()
        
        assert buffer.context is None
        assert len(buffer.evaluations) == 0
        assert len(buffer.scratch) == 0
        assert buffer.current_phase == ReasoningPhase.CONTEXT_GATHERING

    def test_to_dict(self):
        """Test serialization."""
        buffer = WorkingMemoryBuffer("assessment", "p-123")
        buffer.record_evaluation(1, 80, 80, 0.7, [], [])
        
        data = buffer.to_dict()
        
        assert data["agent_name"] == "assessment"
        assert data["profile_id"] == "p-123"
        assert data["evaluations_count"] == 1
        assert "created_at" in data

    def test_repr(self):
        """Test string representation."""
        buffer = WorkingMemoryBuffer("narrative", "p-456")
        buffer.record_evaluation(1, 80, 80, 0.7, [], [])
        
        repr_str = repr(buffer)
        assert "narrative" in repr_str
        assert "p-456" in repr_str


class TestContextFrame:
    """Test ContextFrame dataclass."""

    def test_creation(self):
        """Test context frame creation."""
        context = ContextFrame(
            profile_summary={"name": "Test", "archetype": "DoubleDown"},
            relevant_memories=[{"id": "1"}],
            coaching_knowledge=[{"id": "2"}],
            active_tasks=[],
            recent_interactions=[],
        )
        
        assert context.profile_summary["archetype"] == "DoubleDown"
        assert len(context.relevant_memories) == 1

    def test_to_dict(self):
        """Test serialization."""
        context = ContextFrame(
            profile_summary={},
            relevant_memories=[{}, {}],
            coaching_knowledge=[{}],
            active_tasks=[{}, {}, {}],
            recent_interactions=[],
        )
        
        data = context.to_dict()
        assert data["memory_count"] == 2
        assert data["knowledge_count"] == 1
        assert data["active_tasks_count"] == 3


class TestPlannedAction:
    """Test PlannedAction dataclass."""

    def test_creation(self):
        """Test planned action creation."""
        action = PlannedAction(
            action_type="generate",
            description="Generate narrative",
            expected_outcome="Quality narrative",
            confidence=0.85,
            dependencies=["context_loaded"],
        )
        
        assert action.action_type == "generate"
        assert action.confidence == 0.85

    def test_to_dict(self):
        """Test serialization."""
        action = PlannedAction(
            action_type="test",
            description="Test action",
            expected_outcome="Success",
            confidence=0.9,
        )
        
        data = action.to_dict()
        assert data["confidence"] == 0.9
        assert "created_at" in data


class TestOptionAnalysis:
    """Test OptionAnalysis dataclass."""

    def test_creation(self):
        """Test option analysis creation."""
        option = OptionAnalysis(
            option_name="Approach A",
            pros=["Fast", "Simple"],
            cons=["Less thorough"],
            fit_score=0.75,
            risk_level="low",
            recommended=True,
        )
        
        assert option.option_name == "Approach A"
        assert len(option.pros) == 2
        assert option.recommended is True

    def test_to_dict(self):
        """Test serialization."""
        option = OptionAnalysis(
            option_name="Test",
            pros=["Good"],
            cons=["Bad"],
            fit_score=0.5,
            risk_level="medium",
        )
        
        data = option.to_dict()
        assert data["fit_score"] == 0.5
        assert data["risk_level"] == "medium"


class TestEvaluationFrame:
    """Test EvaluationFrame dataclass."""

    def test_creation(self):
        """Test evaluation frame creation."""
        frame = EvaluationFrame(
            cycle_number=1,
            quality_score=80,
            voice_score=75,
            golden_similarity=0.7,
            issues_found=["Minor issue"],
            strengths_found=["Good structure"],
            passes_threshold=True,
            needs_correction=False,
        )
        
        assert frame.cycle_number == 1
        assert frame.quality_score == 80
        assert frame.passes_threshold is True

    def test_to_dict(self):
        """Test serialization."""
        frame = EvaluationFrame(
            cycle_number=2,
            quality_score=65,
            voice_score=70,
            golden_similarity=0.55,
            issues_found=["Issue"],
            strengths_found=[],
            passes_threshold=False,
            needs_correction=True,
        )
        
        data = frame.to_dict()
        assert data["cycle_number"] == 2
        assert data["needs_correction"] is True
        assert "evaluated_at" in data


class TestLearningFrame:
    """Test LearningFrame dataclass."""

    def test_creation(self):
        """Test learning frame creation."""
        frame = LearningFrame()
        
        assert len(frame.successful_strategies) == 0
        assert len(frame.failed_approaches) == 0
        assert len(frame.user_preferences) == 0

    def test_to_dict(self):
        """Test serialization."""
        frame = LearningFrame(
            successful_strategies=[{"strategy": "A"}],
            failed_approaches=["B"],
            user_preferences={"tone": "warm"},
            context_insights=["Insight 1"],
        )
        
        data = frame.to_dict()
        assert data["successful_strategies_count"] == 1
        assert data["failed_approaches_count"] == 1
        assert data["user_preferences"]["tone"] == "warm"
