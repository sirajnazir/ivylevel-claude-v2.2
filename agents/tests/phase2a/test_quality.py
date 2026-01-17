"""
Tests for E7: Producer-Critic and E3: Reflection Loops Patterns
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.quality import (
    ProducerCriticPipeline,
    CritiqueResult,
    EvaluationCriteria,
    COACHING_CRITERIA,
    ReflectionLoop,
    ReflectionStep,
    ReflectionResult,
)


class TestCritiqueTypes:
    """Tests for critique type definitions."""

    def test_critique_result_creation(self):
        """Test CritiqueResult model creation."""
        result = CritiqueResult(
            is_acceptable=True,
            quality_score=0.8,
            criterion_scores={"relevance": 0.9, "clarity": 0.7},
            strengths=["Clear communication"],
            weaknesses=["Could be more specific"],
        )
        assert result.is_acceptable == True
        assert result.quality_score == 0.8
        assert len(result.strengths) == 1

    def test_evaluation_criteria_creation(self):
        """Test EvaluationCriteria model creation."""
        criteria = EvaluationCriteria(
            name="relevance",
            description="Output addresses the question",
            weight=0.3,
            is_critical=True,
        )
        assert criteria.name == "relevance"
        assert criteria.min_acceptable_score == 0.6

    def test_coaching_criteria_exist(self):
        """Test coaching criteria are defined."""
        assert "advice" in COACHING_CRITERIA
        assert "plan" in COACHING_CRITERIA
        assert "motivation" in COACHING_CRITERIA
        assert "general" in COACHING_CRITERIA

    def test_advice_criteria_has_actionability(self):
        """Advice criteria includes actionability."""
        advice_criteria = COACHING_CRITERIA["advice"]
        names = [c.name for c in advice_criteria]
        assert "actionability" in names
        assert "relevance" in names

    def test_plan_criteria_has_feasibility(self):
        """Plan criteria includes feasibility."""
        plan_criteria = COACHING_CRITERIA["plan"]
        names = [c.name for c in plan_criteria]
        assert "feasibility" in names
        assert "completeness" in names


class TestProducerCriticPipeline:
    """Tests for ProducerCriticPipeline."""

    @pytest.fixture
    def pipeline(self):
        return ProducerCriticPipeline()

    def test_pipeline_creation(self, pipeline):
        """Test pipeline creation."""
        assert pipeline is not None
        assert pipeline.min_quality == 0.7
        assert pipeline.max_iterations == 2

    def test_pipeline_creation_with_params(self):
        """Test pipeline creation with custom params."""
        pipeline = ProducerCriticPipeline(
            min_quality_score=0.8,
            max_iterations=3,
        )
        assert pipeline.min_quality == 0.8
        assert pipeline.max_iterations == 3

    @pytest.mark.asyncio
    async def test_critique_without_llm_returns_acceptable(self, pipeline):
        """Critique without LLM returns acceptable fallback."""
        result = await pipeline.critique(
            output="Test output",
            criteria=COACHING_CRITERIA["general"],
        )

        assert isinstance(result, CritiqueResult)
        assert result.is_acceptable == True
        assert result.quality_score == 0.7


class TestReflectionTypes:
    """Tests for reflection type definitions."""

    def test_reflection_step_creation(self):
        """Test ReflectionStep model creation."""
        step = ReflectionStep(
            step_number=1,
            original_output="Original",
            reflection="Needs improvement in tone",
            improvement_plan="Make tone more supportive",
            revised_output="Revised version",
            improvement_score=0.8,
        )
        assert step.step_number == 1
        assert step.improvement_score == 0.8

    def test_reflection_result_creation(self):
        """Test ReflectionResult model creation."""
        result = ReflectionResult(
            final_output="Final output",
            original_output="Original output",
            total_iterations=2,
            improved=True,
            improvement_delta=0.2,
            final_quality_score=0.85,
        )
        assert result.improved == True
        assert result.improvement_delta == 0.2


class TestReflectionLoop:
    """Tests for ReflectionLoop."""

    @pytest.fixture
    def loop(self):
        return ReflectionLoop()

    def test_loop_creation(self, loop):
        """Test loop creation."""
        assert loop is not None
        assert loop.max_reflections == 2

    def test_loop_creation_with_params(self):
        """Test loop creation with custom params."""
        loop = ReflectionLoop(max_reflections=3)
        assert loop.max_reflections == 3

    @pytest.mark.asyncio
    async def test_reflect_without_llm_returns_simple(self, loop):
        """Reflect without LLM returns simple reflection."""
        result = await loop._reflect(
            output="Test output",
            critique_feedback={"weaknesses": ["Too vague", "Not actionable"]},
            context={},
        )

        assert "Too vague" in result or "Not actionable" in result

    @pytest.mark.asyncio
    async def test_plan_improvements_without_llm(self, loop):
        """Plan improvements without LLM returns focus."""
        result = await loop._plan_improvements(
            reflection="Issues with clarity",
            critique_feedback={
                "regeneration_focus": "clarity",
                "improvement_suggestions": ["Be more specific"],
            },
        )

        assert "clarity" in result

    @pytest.mark.asyncio
    async def test_revise_without_llm_returns_original(self, loop):
        """Revise without LLM returns original."""
        result = await loop._revise(
            original="Original text",
            reflection="Some issues",
            plan="Fix issues",
            context={},
        )

        assert result == "Original text"

    @pytest.mark.asyncio
    async def test_evaluate_improvement_without_llm(self, loop):
        """Evaluate improvement without LLM returns 0.6."""
        result = await loop._evaluate_improvement(
            original="Original",
            revised="Revised",
            critique_feedback={"weaknesses": ["Issue 1"]},
        )

        assert result == 0.6
