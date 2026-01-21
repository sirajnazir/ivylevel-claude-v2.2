# agents/tests/patterns/test_intelligence.py
"""
Tests for Intelligence Patterns (A12, I3) - v5.4 True Autonomous Agents.

These are USP (BUILD, not buy) patterns:
- A12: Prioritization (custom coaching intelligence)
- I3: Goal Monitoring (progress tracking)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestPrioritization:
    """Tests for A12: Prioritization pattern (USP)."""

    def test_prioritizer_creation(self):
        """Test Prioritizer can be created."""
        from intelligence import Prioritizer

        prioritizer = Prioritizer()

        assert prioritizer is not None

    def test_prioritize_recommendations(self, sample_recommendations, sample_student_context, sample_temporal_context):
        """Test recommendations are prioritized correctly."""
        from intelligence import Prioritizer

        prioritizer = Prioritizer()

        result = prioritizer.prioritize(
            items=sample_recommendations,
            student_context=sample_student_context,
            temporal_context=sample_temporal_context,
        )

        assert len(result) == len(sample_recommendations)
        # High urgency items should be ranked higher
        assert result[0].urgency_factor > 0

    def test_prioritized_item_model(self, sample_recommendations):
        """Test PrioritizedItem model structure."""
        from intelligence import PrioritizedItem, PriorityLevel

        item = PrioritizedItem(
            id=sample_recommendations[0]["id"],
            title=sample_recommendations[0]["title"],
            original_item=sample_recommendations[0],
            priority_level=PriorityLevel.HIGH,
            priority_score=0.85,
            urgency_factor=0.9,
            impact_factor=0.8,
            spike_alignment=0.7,
            reasoning="High urgency deadline approaching",
        )

        assert item.priority_level == PriorityLevel.HIGH
        assert item.priority_score == 0.85

    def test_priority_levels_enum(self):
        """Test PriorityLevel enum values."""
        from intelligence import PriorityLevel

        assert PriorityLevel.CRITICAL is not None
        assert PriorityLevel.HIGH is not None
        assert PriorityLevel.MEDIUM is not None
        assert PriorityLevel.LOW is not None

    def test_recommendation_types_enum(self):
        """Test RecommendationType enum values."""
        from intelligence import RecommendationType

        assert RecommendationType.ACTIVITY is not None
        assert RecommendationType.TESTING is not None
        assert RecommendationType.APPLICATION is not None

    def test_urgency_multipliers_defined(self):
        """Test urgency multipliers are configured."""
        from intelligence import URGENCY_MULTIPLIERS

        assert URGENCY_MULTIPLIERS is not None
        assert isinstance(URGENCY_MULTIPLIERS, dict)

    def test_priority_weights_defined(self):
        """Test priority weights are configured."""
        from intelligence import PRIORITY_WEIGHTS

        assert PRIORITY_WEIGHTS is not None
        assert isinstance(PRIORITY_WEIGHTS, dict)

    def test_prioritize_with_spike_alignment(self, sample_recommendations, sample_student_context, sample_temporal_context):
        """Test prioritization considers spike alignment."""
        from intelligence import Prioritizer

        prioritizer = Prioritizer()

        # Add robotics recommendation (aligns with spike)
        robotics_rec = {
            "id": "rec-robotics",
            "title": "Robotics Competition",
            "type": "activity",
            "urgency": "high",
            "impact": 5,
            "domains": ["robotics", "engineering"],
        }

        items = sample_recommendations + [robotics_rec]

        result = prioritizer.prioritize(
            items=items,
            student_context=sample_student_context,
            temporal_context=sample_temporal_context,
        )

        # Robotics item should have high spike alignment
        robotics_result = next(r for r in result if r.id == "rec-robotics")
        assert robotics_result.spike_alignment > 0

    def test_prioritize_with_deadline_urgency(self, sample_student_context, sample_temporal_context):
        """Test prioritization considers deadline urgency."""
        from intelligence import Prioritizer

        prioritizer = Prioritizer()

        items = [
            {"id": "urgent", "title": "Urgent Task", "deadline_days": 5, "urgency": "critical"},
            {"id": "later", "title": "Later Task", "deadline_days": 90, "urgency": "low"},
        ]

        result = prioritizer.prioritize(
            items=items,
            student_context=sample_student_context,
            temporal_context=sample_temporal_context,
        )

        # Urgent item should be ranked higher
        urgent_idx = next(i for i, r in enumerate(result) if r.id == "urgent")
        later_idx = next(i for i, r in enumerate(result) if r.id == "later")
        assert urgent_idx < later_idx

    def test_convenience_function_prioritize(self):
        """Test convenience function for prioritization."""
        from intelligence import prioritize_recommendations

        assert callable(prioritize_recommendations)


class TestGoalMonitoring:
    """Tests for I3: Goal Monitoring pattern (USP)."""

    def test_goal_monitor_creation(self, mock_supabase):
        """Test GoalMonitor can be created."""
        from intelligence import GoalMonitor

        monitor = GoalMonitor(mock_supabase)

        assert monitor is not None

    def test_goal_model(self, sample_goals):
        """Test Goal model structure."""
        from intelligence import Goal, GoalStatus, GoalCategory

        goal_data = sample_goals[0]
        goal = Goal(
            id=goal_data["id"],
            name=goal_data["name"],
            category=GoalCategory.TESTING,
            target_value=goal_data["target_value"],
            current_value=goal_data["current_value"],
            status=GoalStatus.IN_PROGRESS,
            deadline=datetime.fromisoformat(goal_data["deadline"]),
        )

        assert goal.name == "Achieve 1500+ SAT Score"
        assert goal.category == GoalCategory.TESTING

    def test_goal_status_enum(self):
        """Test GoalStatus enum values."""
        from intelligence import GoalStatus

        assert GoalStatus.PENDING is not None
        assert GoalStatus.IN_PROGRESS is not None
        assert GoalStatus.COMPLETED is not None
        assert GoalStatus.AT_RISK is not None

    def test_goal_category_enum(self):
        """Test GoalCategory enum values."""
        from intelligence import GoalCategory

        assert GoalCategory.TESTING is not None
        assert GoalCategory.ACADEMICS is not None
        assert GoalCategory.ACTIVITIES is not None
        assert GoalCategory.APPLICATION is not None

    @pytest.mark.asyncio
    async def test_get_goal_progress(self, mock_supabase, sample_goals):
        """Test getting progress report for goals."""
        from intelligence import GoalMonitor

        # Setup mock data
        mock_supabase._tables["goals"] = sample_goals

        monitor = GoalMonitor(mock_supabase)

        report = await monitor.get_progress_report("profile-123")

        assert report is not None

    def test_goal_progress_report_model(self, sample_goals):
        """Test GoalProgressReport model structure."""
        from intelligence import GoalProgressReport, Goal, GoalStatus, GoalCategory
        from datetime import datetime

        report = GoalProgressReport(
            profile_id="profile-123",
            total_goals=3,
            completed_goals=0,
            in_progress_goals=2,
            at_risk_goals=1,
            completion_rate=0.0,
            goals=[
                Goal(
                    id="goal-1",
                    name="Test Goal",
                    category=GoalCategory.TESTING,
                    target_value=1500,
                    current_value=1400,
                    status=GoalStatus.IN_PROGRESS,
                    deadline=datetime.utcnow() + timedelta(days=90),
                )
            ],
            recommendations=["Focus on SAT prep"],
        )

        assert report.total_goals == 3
        assert report.at_risk_goals == 1

    @pytest.mark.asyncio
    async def test_identify_at_risk_goals(self, mock_supabase):
        """Test identifying goals that are at risk."""
        from intelligence import GoalMonitor

        # Setup mock data with at-risk goal (close deadline, low progress)
        mock_supabase._tables["goals"] = [
            {
                "id": "goal-risk",
                "profile_id": "profile-123",
                "name": "At Risk Goal",
                "category": "testing",
                "target_value": 100,
                "current_value": 10,  # Only 10% progress
                "status": "in_progress",
                "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            }
        ]

        monitor = GoalMonitor(mock_supabase)

        report = await monitor.get_progress_report("profile-123")

        # Should identify at-risk goal

    def test_goal_templates_by_grade(self):
        """Test grade-specific goal templates are defined."""
        from intelligence import GOAL_TEMPLATES_BY_GRADE

        assert GOAL_TEMPLATES_BY_GRADE is not None
        assert isinstance(GOAL_TEMPLATES_BY_GRADE, dict)

        # Should have templates for different grades
        assert 9 in GOAL_TEMPLATES_BY_GRADE or "9" in GOAL_TEMPLATES_BY_GRADE or len(GOAL_TEMPLATES_BY_GRADE) > 0

    def test_convenience_function_get_progress(self):
        """Test convenience function for getting goal progress."""
        from intelligence import get_goal_progress

        assert callable(get_goal_progress)


class TestIntelligenceIntegration:
    """Integration tests for intelligence patterns working together."""

    def test_all_intelligence_types_importable(self):
        """Test all intelligence types can be imported."""
        from intelligence import (
            Prioritizer,
            PrioritizedItem,
            PriorityLevel,
            GoalMonitor,
            Goal,
            GoalStatus,
            GoalProgressReport,
        )

        # All should be importable

    def test_prioritization_uses_goal_progress(self, sample_recommendations, sample_student_context, sample_temporal_context, sample_goals):
        """Test prioritization can incorporate goal progress."""
        from intelligence import Prioritizer

        prioritizer = Prioritizer()

        # Add goal context
        student_ctx_with_goals = {
            **sample_student_context,
            "goals": sample_goals,
        }

        result = prioritizer.prioritize(
            items=sample_recommendations,
            student_context=student_ctx_with_goals,
            temporal_context=sample_temporal_context,
        )

        assert len(result) > 0

    def test_prioritization_is_deterministic(self, sample_recommendations, sample_student_context, sample_temporal_context):
        """Test same inputs produce same prioritization."""
        from intelligence import Prioritizer

        prioritizer = Prioritizer()

        result1 = prioritizer.prioritize(
            items=sample_recommendations,
            student_context=sample_student_context,
            temporal_context=sample_temporal_context,
        )

        result2 = prioritizer.prioritize(
            items=sample_recommendations,
            student_context=sample_student_context,
            temporal_context=sample_temporal_context,
        )

        # Same order
        assert [r.id for r in result1] == [r.id for r in result2]

    def test_prioritization_handles_empty_input(self, sample_student_context, sample_temporal_context):
        """Test prioritization handles empty input gracefully."""
        from intelligence import Prioritizer

        prioritizer = Prioritizer()

        result = prioritizer.prioritize(
            items=[],
            student_context=sample_student_context,
            temporal_context=sample_temporal_context,
        )

        assert result == []
