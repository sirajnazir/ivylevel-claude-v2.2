"""
Tests for H4: Pivot Strategy Pattern
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.recovery import (
    PivotStrategy,
    PivotTrigger,
    PivotOption,
    PivotResult,
)


class TestPivotTypes:
    """Tests for pivot type definitions."""

    def test_pivot_trigger_creation(self):
        """Test PivotTrigger model creation."""
        trigger = PivotTrigger(
            trigger_type="max_attempts",
            description="Maximum attempts reached",
            threshold=3,
        )
        assert trigger.trigger_type == "max_attempts"
        assert trigger.threshold == 3

    def test_pivot_option_creation(self):
        """Test PivotOption model creation."""
        option = PivotOption(
            option_id="pivot_examples",
            name="Switch to Examples",
            description="Show examples instead of explaining",
            approach_type="examples_over_instructions",
            applicability_score=0.8,
        )
        assert option.name == "Switch to Examples"
        assert option.applicability_score == 0.8

    def test_pivot_option_with_history(self):
        """Test PivotOption with historical data."""
        option = PivotOption(
            option_id="pivot_examples",
            name="Switch to Examples",
            description="Show examples",
            approach_type="examples_over_instructions",
            applicability_score=0.8,
            historical_success_rate=0.85,
        )
        assert option.historical_success_rate == 0.85

    def test_pivot_result_creation(self):
        """Test PivotResult model creation."""
        result = PivotResult(
            pivoted=True,
            original_approach="instructions",
            new_approach="examples_over_instructions",
            pivot_reason="Low confidence",
            pivot_successful=True,
            result="Success",
        )
        assert result.pivoted == True
        assert result.pivot_successful == True


class TestPivotStrategy:
    """Tests for PivotStrategy."""

    @pytest.fixture
    def strategy(self):
        return PivotStrategy()

    def test_strategy_creation(self, strategy):
        """Test strategy creation."""
        assert strategy is not None

    def test_get_default_triggers(self, strategy):
        """Test default triggers exist."""
        triggers = strategy._get_default_triggers()
        assert len(triggers) == 4
        trigger_types = [t.trigger_type for t in triggers]
        assert "max_attempts" in trigger_types
        assert "low_confidence" in trigger_types
        assert "student_feedback" in trigger_types
        assert "deadline_pressure" in trigger_types

    def test_check_trigger_max_attempts(self, strategy):
        """Check trigger for max attempts."""
        trigger = PivotTrigger(
            trigger_type="max_attempts",
            description="Max attempts",
            threshold=3,
        )
        assert strategy._check_trigger(trigger, {"attempts": 3}) == True
        assert strategy._check_trigger(trigger, {"attempts": 2}) == False

    def test_check_trigger_low_confidence(self, strategy):
        """Check trigger for low confidence."""
        trigger = PivotTrigger(
            trigger_type="low_confidence",
            description="Low confidence",
            threshold=0.4,
        )
        assert strategy._check_trigger(trigger, {"confidence": 0.3}) == True
        assert strategy._check_trigger(trigger, {"confidence": 0.5}) == False

    def test_check_trigger_student_feedback(self, strategy):
        """Check trigger for student feedback."""
        trigger = PivotTrigger(
            trigger_type="student_feedback",
            description="Student frustrated",
        )
        assert strategy._check_trigger(
            trigger, {"student_sentiment": "frustrated"}
        ) == True
        assert strategy._check_trigger(
            trigger, {"student_sentiment": "confused"}
        ) == True
        assert strategy._check_trigger(
            trigger, {"student_sentiment": "neutral"}
        ) == False

    def test_check_trigger_deadline_pressure(self, strategy):
        """Check trigger for deadline pressure."""
        trigger = PivotTrigger(
            trigger_type="deadline_pressure",
            description="Deadline near",
            threshold=3,
        )
        assert strategy._check_trigger(
            trigger, {"days_until_deadline": 2}
        ) == True
        assert strategy._check_trigger(
            trigger, {"days_until_deadline": 5}
        ) == False

    @pytest.mark.asyncio
    async def test_should_pivot_no_triggers(self, strategy):
        """Should pivot returns False when no triggers met."""
        should, reason = await strategy.should_pivot({
            "attempts": 1,
            "confidence": 0.8,
            "student_sentiment": "neutral",
        })
        assert should == False
        assert reason is None

    @pytest.mark.asyncio
    async def test_should_pivot_max_attempts(self, strategy):
        """Should pivot returns True for max attempts."""
        should, reason = await strategy.should_pivot({"attempts": 5})
        assert should == True
        assert "Maximum attempts" in reason

    @pytest.mark.asyncio
    async def test_should_pivot_low_confidence(self, strategy):
        """Should pivot returns True for low confidence."""
        should, reason = await strategy.should_pivot({"confidence": 0.2})
        assert should == True
        assert "confidence" in reason.lower()

    def test_get_coaching_pivot_options(self, strategy):
        """Get coaching pivot options."""
        options = strategy._get_coaching_pivot_options(
            current_approach="instructions",
            context={},
        )
        assert len(options) >= 3
        option_types = [o.approach_type for o in options]
        assert "examples_over_instructions" in option_types
        assert "break_into_smaller_tasks" in option_types

    def test_get_coaching_pivot_options_excludes_current(self, strategy):
        """Pivot options exclude current approach."""
        options = strategy._get_coaching_pivot_options(
            current_approach="examples_over_instructions",
            context={},
        )
        option_types = [o.approach_type for o in options]
        assert "examples_over_instructions" not in option_types

    def test_get_coaching_pivot_options_empathy_for_frustrated(self, strategy):
        """Pivot options include empathy for frustrated student."""
        options = strategy._get_coaching_pivot_options(
            current_approach="instructions",
            context={"student_sentiment": "frustrated"},
        )
        option_types = [o.approach_type for o in options]
        assert "empathy_first" in option_types

    def test_get_coaching_pivot_options_triage_for_deadline(self, strategy):
        """Pivot options include triage for deadline pressure."""
        options = strategy._get_coaching_pivot_options(
            current_approach="instructions",
            context={"days_until_deadline": 3},
        )
        option_types = [o.approach_type for o in options]
        assert "urgent_triage" in option_types

    @pytest.mark.asyncio
    async def test_get_pivot_options_sorted_by_applicability(self, strategy):
        """Pivot options sorted by applicability."""
        options = await strategy.get_pivot_options(
            profile_id="test-profile",
            current_approach="instructions",
            context={},
        )
        # Should be sorted by applicability descending
        scores = [o.applicability_score for o in options]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_execute_pivot_success(self, strategy):
        """Execute pivot with success."""
        async def mock_execute(**kwargs):
            return "New approach worked"

        option = PivotOption(
            option_id="pivot_examples",
            name="Switch to Examples",
            description="Show examples",
            approach_type="examples_over_instructions",
            applicability_score=0.8,
        )

        result = await strategy.execute_pivot(
            profile_id="test-profile",
            original_approach="instructions",
            selected_option=option,
            execute_func=mock_execute,
        )

        assert result.pivoted == True
        assert result.pivot_successful == True
        assert result.new_approach == "examples_over_instructions"
        assert result.result == "New approach worked"

    @pytest.mark.asyncio
    async def test_execute_pivot_failure(self, strategy):
        """Execute pivot with failure."""
        async def mock_execute(**kwargs):
            raise Exception("Approach failed")

        option = PivotOption(
            option_id="pivot_examples",
            name="Switch to Examples",
            description="Show examples",
            approach_type="examples_over_instructions",
            applicability_score=0.8,
        )

        result = await strategy.execute_pivot(
            profile_id="test-profile",
            original_approach="instructions",
            selected_option=option,
            execute_func=mock_execute,
        )

        assert result.pivoted == True
        assert result.pivot_successful == False
        assert "Approach failed" in result.result
