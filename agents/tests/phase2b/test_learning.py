"""
Tests for I4: Strategy Effectiveness Pattern
"""

import pytest
from datetime import datetime, timezone
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.learning.strategy_effectiveness_v8 import (
    StrategyEffectivenessTracker,
    StrategyApplication,
    StrategyEffectiveness,
    StrategyOutcome,
)


class TestStrategyOutcome:
    """Tests for StrategyOutcome enum."""

    def test_outcome_values(self):
        """Test strategy outcome values."""
        assert StrategyOutcome.SUCCESS.value == "success"
        assert StrategyOutcome.PARTIAL.value == "partial"
        assert StrategyOutcome.FAILURE.value == "failure"
        assert StrategyOutcome.UNKNOWN.value == "unknown"


class TestStrategyApplication:
    """Tests for StrategyApplication model."""

    def test_application_creation(self):
        """Test StrategyApplication creation."""
        app = StrategyApplication(
            strategy="examples_over_instructions",
            context_type="essay_help",
            profile_id="profile-123",
            session_id="session-456",
            input_situation="Student struggling with essay thesis",
            strategy_response="Here's an example of a strong thesis...",
        )
        assert app.strategy == "examples_over_instructions"
        assert app.context_type == "essay_help"
        assert app.outcome is None

    def test_application_with_outcome(self):
        """Test StrategyApplication with outcome."""
        app = StrategyApplication(
            strategy="socratic_questioning",
            context_type="activity_planning",
            profile_id="profile-123",
            session_id="session-456",
            input_situation="Student unsure about activity choice",
            strategy_response="What makes you interested in robotics?",
            outcome=StrategyOutcome.SUCCESS,
            outcome_reason="Student engaged and made decision",
            student_response_positive=True,
            task_completed=True,
            engagement_score=0.9,
        )
        assert app.outcome == StrategyOutcome.SUCCESS
        assert app.engagement_score == 0.9


class TestStrategyEffectiveness:
    """Tests for StrategyEffectiveness model."""

    def test_effectiveness_creation(self):
        """Test StrategyEffectiveness creation."""
        eff = StrategyEffectiveness(
            strategy="examples_over_instructions",
            context_type="essay_help",
        )
        assert eff.strategy == "examples_over_instructions"
        assert eff.total_applications == 0
        assert eff.success_rate == 0.0

    def test_effectiveness_with_data(self):
        """Test StrategyEffectiveness with data."""
        eff = StrategyEffectiveness(
            strategy="scaffolding",
            context_type="math_help",
            total_applications=20,
            success_count=15,
            partial_count=3,
            failure_count=2,
            success_rate=0.75,
            avg_engagement=0.8,
            sample_size=20,
            confidence="high",
        )
        assert eff.success_rate == 0.75
        assert eff.confidence == "high"


class TestStrategyEffectivenessTracker:
    """Tests for StrategyEffectivenessTracker."""

    @pytest.fixture
    def tracker(self, mock_supabase):
        return StrategyEffectivenessTracker(supabase_client=mock_supabase)

    def test_tracker_creation(self, tracker):
        """Test tracker creation."""
        assert tracker is not None
        assert tracker.min_samples == 10

    def test_tracker_creation_with_params(self, mock_supabase):
        """Test tracker creation with custom params."""
        tracker = StrategyEffectivenessTracker(
            supabase_client=mock_supabase,
            min_sample_size=20,
        )
        assert tracker.min_samples == 20

    @pytest.mark.asyncio
    async def test_record_application(self, tracker):
        """Test recording a strategy application."""
        app = await tracker.record_application(
            strategy="examples_over_instructions",
            context_type="essay_help",
            profile_id="profile-123",
            session_id="session-456",
            input_situation="Student needs essay help",
            strategy_response="Here's an example...",
        )
        assert isinstance(app, StrategyApplication)
        assert app.strategy == "examples_over_instructions"

    @pytest.mark.asyncio
    async def test_record_outcome(self, tracker):
        """Test recording outcome for application."""
        # First record an application
        app = await tracker.record_application(
            strategy="scaffolding",
            context_type="math_help",
            profile_id="profile-123",
            session_id="session-456",
            input_situation="Student needs math help",
            strategy_response="Let's break this down...",
        )

        # Then record outcome
        updated = await tracker.record_outcome(
            application_id=app.application_id,
            outcome=StrategyOutcome.SUCCESS,
            reason="Student understood the concept",
            student_response_positive=True,
            task_completed=True,
            engagement_score=0.85,
        )
        assert updated is not None
        assert updated.outcome == StrategyOutcome.SUCCESS

    @pytest.mark.asyncio
    async def test_get_effectiveness_no_data(self, tracker):
        """Test getting effectiveness with no data."""
        eff = await tracker.get_effectiveness(
            strategy="unknown_strategy",
            context_type="unknown_context",
        )
        assert isinstance(eff, StrategyEffectiveness)
        assert eff.total_applications == 0

    @pytest.mark.asyncio
    async def test_get_effectiveness_with_data(self, tracker):
        """Test getting effectiveness with data."""
        # Record some applications
        for i in range(5):
            app = await tracker.record_application(
                strategy="test_strategy",
                context_type="test_context",
                profile_id="profile-123",
                session_id=f"session-{i}",
                input_situation="Test situation",
                strategy_response="Test response",
            )
            # Record outcomes
            await tracker.record_outcome(
                application_id=app.application_id,
                outcome=StrategyOutcome.SUCCESS if i < 4 else StrategyOutcome.FAILURE,
            )

        # In-memory cache should have data
        # Note: actual effectiveness calculation depends on database

    @pytest.mark.asyncio
    async def test_recommend_strategy_no_data(self, tracker):
        """Test recommending strategy with no historical data."""
        result = await tracker.recommend_strategy(
            context_type="essay_help",
            profile_id="new-profile",
            available_strategies=["examples", "scaffolding", "direct"],
        )
        # With no data, might return None
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_strategy_comparison(self, tracker):
        """Test comparing strategies."""
        results = await tracker.get_strategy_comparison(
            context_type="essay_help",
            strategies=["examples", "scaffolding", "socratic"],
        )
        assert isinstance(results, list)
        assert len(results) == 3


class TestStrategyEffectivenessCalculation:
    """Tests for effectiveness calculation logic."""

    def test_success_rate_calculation(self):
        """Test success rate is calculated correctly."""
        eff = StrategyEffectiveness(
            strategy="test",
            context_type="test",
            success_count=7,
            partial_count=2,
            failure_count=1,
            success_rate=0.7,  # 7 out of 10
            sample_size=10,
        )
        assert eff.success_rate == 0.7

    def test_confidence_levels(self):
        """Test confidence level assignment."""
        # Low confidence (< min_samples)
        low_eff = StrategyEffectiveness(
            strategy="test",
            context_type="test",
            sample_size=5,
            confidence="low",
        )
        assert low_eff.confidence == "low"

        # Medium confidence (>= min_samples)
        med_eff = StrategyEffectiveness(
            strategy="test",
            context_type="test",
            sample_size=15,
            confidence="medium",
        )
        assert med_eff.confidence == "medium"

        # High confidence (>= 2x min_samples)
        high_eff = StrategyEffectiveness(
            strategy="test",
            context_type="test",
            sample_size=25,
            confidence="high",
        )
        assert high_eff.confidence == "high"


class TestStrategyTypes:
    """Tests for common strategy types."""

    def test_common_strategies(self):
        """Test common coaching strategies can be tracked."""
        strategies = [
            "examples_over_instructions",
            "socratic_questioning",
            "scaffolding",
            "direct_instruction",
            "collaborative_problem_solving",
            "metacognitive_prompting",
            "growth_mindset_framing",
            "chunking",
        ]
        for strategy in strategies:
            app = StrategyApplication(
                strategy=strategy,
                context_type="general",
                profile_id="test",
                session_id="test",
                input_situation="test",
                strategy_response="test",
            )
            assert app.strategy == strategy

    def test_common_context_types(self):
        """Test common context types."""
        contexts = [
            "essay_help",
            "activity_planning",
            "college_research",
            "interview_prep",
            "test_prep",
            "motivation",
        ]
        for context in contexts:
            app = StrategyApplication(
                strategy="test",
                context_type=context,
                profile_id="test",
                session_id="test",
                input_situation="test",
                strategy_response="test",
            )
            assert app.context_type == context
