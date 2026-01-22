# tests/patterns/test_intelligence.py
"""
Tests for Intelligence patterns: A12 Prioritization, I3 Goal Monitoring
CORRECTED to match actual implementation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock


class TestPrioritizer:
    """Tests for Prioritizer (A12 - USP)."""
    
    def test_prioritizer_importable(self):
        """Test Prioritizer can be imported."""
        from intelligence.prioritization import Prioritizer
        assert Prioritizer is not None
    
    def test_prioritizer_initialization(self):
        """Test Prioritizer can be initialized without arguments."""
        from intelligence.prioritization import Prioritizer
        prioritizer = Prioritizer()
        assert prioritizer is not None
    
    def test_prioritizer_with_custom_weights(self):
        """Test Prioritizer with custom weights."""
        from intelligence.prioritization import Prioritizer
        custom_weights = {
            "deadline_urgency": 0.30,
            "profile_alignment": 0.30,
            "impact_potential": 0.20,
            "effort_required": 0.10,
            "selectivity_match": 0.10,
        }
        prioritizer = Prioritizer(weights=custom_weights)
        assert prioritizer.weights == custom_weights
    
    def test_prioritize_empty_list(self):
        """Test prioritizing empty list returns empty list."""
        from intelligence.prioritization import Prioritizer
        prioritizer = Prioritizer()
        result = prioritizer.prioritize([], {})
        assert result == []
    
    def test_prioritize_returns_prioritized_items(self):
        """Test prioritize returns list of PrioritizedItem."""
        from intelligence.prioritization import Prioritizer, PrioritizedItem
        
        prioritizer = Prioritizer()
        items = [
            {"id": "1", "name": "Test Award", "type": "award"},
        ]
        student_context = {"grade": 11, "target_schools": ["MIT"]}
        
        result = prioritizer.prioritize(items, student_context)
        
        assert len(result) == 1
        assert isinstance(result[0], PrioritizedItem)
    
    def test_prioritized_item_has_expected_fields(self):
        """Test PrioritizedItem has all expected fields."""
        from intelligence.prioritization import Prioritizer
        
        prioritizer = Prioritizer()
        items = [{"id": "1", "name": "Test", "type": "award"}]
        result = prioritizer.prioritize(items, {"grade": 11})
        
        item = result[0]
        assert hasattr(item, 'id')
        assert hasattr(item, 'type')
        assert hasattr(item, 'name')
        assert hasattr(item, 'priority')
        assert hasattr(item, 'score')
        assert hasattr(item, 'reasoning')
    
    def test_prioritize_sorts_by_score(self):
        """Test items are sorted by score descending."""
        from intelligence.prioritization import Prioritizer
        
        prioritizer = Prioritizer()
        items = [
            {"id": "1", "name": "Low Impact", "type": "task"},
            {"id": "2", "name": "High Impact Award", "type": "award", "selectivity": "highly_selective"},
        ]
        student_context = {"grade": 11, "target_schools": ["Harvard"]}
        
        result = prioritizer.prioritize(items, student_context)
        
        # Higher scoring item should be first
        assert result[0].score >= result[1].score
    
    def test_prioritize_with_temporal_context(self):
        """Test prioritize with temporal context."""
        from intelligence.prioritization import Prioritizer
        
        prioritizer = Prioritizer()
        items = [{"id": "1", "name": "Test", "type": "task"}]
        student_context = {"grade": 11}
        temporal_context = {"current_phase": "applications"}
        
        result = prioritizer.prioritize(items, student_context, temporal_context)
        
        assert len(result) == 1
    
    def test_prioritize_max_items(self):
        """Test max_items limits results."""
        from intelligence.prioritization import Prioritizer
        
        prioritizer = Prioritizer()
        items = [{"id": str(i), "name": f"Item {i}", "type": "task"} for i in range(20)]
        
        result = prioritizer.prioritize(items, {"grade": 11}, max_items=5)
        
        assert len(result) == 5
    
    def test_score_to_priority_critical(self):
        """Test score >= 85 returns CRITICAL."""
        from intelligence.prioritization import Prioritizer, PriorityLevel
        
        prioritizer = Prioritizer()
        assert prioritizer._score_to_priority(90) == PriorityLevel.CRITICAL
    
    def test_score_to_priority_high(self):
        """Test score 70-85 returns HIGH."""
        from intelligence.prioritization import Prioritizer, PriorityLevel
        
        prioritizer = Prioritizer()
        assert prioritizer._score_to_priority(75) == PriorityLevel.HIGH
    
    def test_score_to_priority_medium(self):
        """Test score 50-70 returns MEDIUM."""
        from intelligence.prioritization import Prioritizer, PriorityLevel
        
        prioritizer = Prioritizer()
        assert prioritizer._score_to_priority(60) == PriorityLevel.MEDIUM
    
    def test_score_to_priority_low(self):
        """Test score 30-50 returns LOW."""
        from intelligence.prioritization import Prioritizer, PriorityLevel
        
        prioritizer = Prioritizer()
        assert prioritizer._score_to_priority(40) == PriorityLevel.LOW
    
    def test_score_to_priority_deferred(self):
        """Test score < 30 returns DEFERRED."""
        from intelligence.prioritization import Prioritizer, PriorityLevel
        
        prioritizer = Prioritizer()
        assert prioritizer._score_to_priority(20) == PriorityLevel.DEFERRED


class TestPriorityLevel:
    """Tests for PriorityLevel enum."""
    
    def test_priority_level_values(self):
        """Test PriorityLevel has all expected values."""
        from intelligence.prioritization import PriorityLevel
        
        assert PriorityLevel.CRITICAL.value == "critical"
        assert PriorityLevel.HIGH.value == "high"
        assert PriorityLevel.MEDIUM.value == "medium"
        assert PriorityLevel.LOW.value == "low"
        assert PriorityLevel.DEFERRED.value == "deferred"


class TestRecommendationType:
    """Tests for RecommendationType enum."""
    
    def test_recommendation_type_values(self):
        """Test RecommendationType has all expected values."""
        from intelligence.prioritization import RecommendationType
        
        assert RecommendationType.AWARD.value == "award"
        assert RecommendationType.PROGRAM.value == "program"
        assert RecommendationType.ACTIVITY.value == "activity"
        assert RecommendationType.ESSAY.value == "essay"
        assert RecommendationType.DEADLINE.value == "deadline"
        assert RecommendationType.TASK.value == "task"


class TestPrioritizedItem:
    """Tests for PrioritizedItem model."""
    
    def test_prioritized_item_creation(self):
        """Test creating PrioritizedItem."""
        from intelligence.prioritization import PrioritizedItem, PriorityLevel, RecommendationType
        
        item = PrioritizedItem(
            id="test-1",
            type=RecommendationType.AWARD,
            name="Test Award",
            priority=PriorityLevel.HIGH,
            score=75.0,
        )
        
        assert item.id == "test-1"
        assert item.type == RecommendationType.AWARD
        assert item.priority == PriorityLevel.HIGH
        assert item.score == 75.0


class TestConvenienceFunction:
    """Tests for prioritize_recommendations convenience function."""
    
    def test_prioritize_recommendations_exists(self):
        """Test convenience function exists."""
        from intelligence.prioritization import prioritize_recommendations
        assert prioritize_recommendations is not None
    
    def test_prioritize_recommendations_works(self):
        """Test convenience function works."""
        from intelligence.prioritization import prioritize_recommendations
        
        result = prioritize_recommendations(
            [{"id": "1", "name": "Test", "type": "award"}],
            {"grade": 11},
        )
        
        assert len(result) == 1


class TestGoalMonitor:
    """Tests for GoalMonitor (I3 - USP)."""
    
    def test_goal_monitor_importable(self):
        """Test GoalMonitor can be imported."""
        from intelligence.goal_monitoring import GoalMonitor
        assert GoalMonitor is not None
    
    def test_goal_monitor_initialization(self):
        """Test GoalMonitor can be initialized without arguments."""
        from intelligence.goal_monitoring import GoalMonitor
        monitor = GoalMonitor()
        assert monitor is not None
    
    def test_goal_monitor_with_supabase(self, mock_supabase):
        """Test GoalMonitor with Supabase client."""
        from intelligence.goal_monitoring import GoalMonitor
        monitor = GoalMonitor(mock_supabase)
        assert monitor.supabase == mock_supabase
    
    @pytest.mark.asyncio
    async def test_initialize_goals_returns_list(self):
        """Test initialize_goals returns list of goals."""
        from intelligence.goal_monitoring import GoalMonitor, Goal
        
        monitor = GoalMonitor()
        goals = await monitor.initialize_goals("profile-123", grade=11)
        
        assert isinstance(goals, list)
        assert all(isinstance(g, Goal) for g in goals)
    
    @pytest.mark.asyncio
    async def test_initialize_goals_grade_11(self):
        """Test initialize_goals creates appropriate goals for 11th grade."""
        from intelligence.goal_monitoring import GoalMonitor, GoalCategory
        
        monitor = GoalMonitor()
        goals = await monitor.initialize_goals("profile-123", grade=11)
        
        # Should have testing and programs goals for grade 11
        categories = {g.category for g in goals}
        assert GoalCategory.TESTING in categories
        assert GoalCategory.PROGRAMS in categories
    
    def test_assess_goal_status_completed(self):
        """Test assess_goal_status returns COMPLETED for 100% progress."""
        from intelligence.goal_monitoring import GoalMonitor, Goal, GoalStatus, GoalCategory
        
        monitor = GoalMonitor()
        goal = Goal(
            id="test-1",
            category=GoalCategory.ACTIVITIES,
            title="Test Goal",
            progress_percentage=100.0,
        )
        
        status = monitor.assess_goal_status(goal, datetime.utcnow(), {})
        assert status == GoalStatus.COMPLETED
    
    def test_assess_goal_status_not_started(self):
        """Test assess_goal_status returns NOT_STARTED for 0% progress."""
        from intelligence.goal_monitoring import GoalMonitor, Goal, GoalStatus, GoalCategory
        
        monitor = GoalMonitor()
        goal = Goal(
            id="test-1",
            category=GoalCategory.ACTIVITIES,
            title="Test Goal",
            progress_percentage=0.0,
        )
        
        status = monitor.assess_goal_status(goal, datetime.utcnow(), {})
        assert status == GoalStatus.NOT_STARTED
    
    def test_update_goal_progress(self):
        """Test update_goal_progress updates progress."""
        from intelligence.goal_monitoring import GoalMonitor, Goal, GoalCategory
        
        monitor = GoalMonitor()
        goal = Goal(
            id="test-1",
            category=GoalCategory.ACTIVITIES,
            title="Test Goal",
            progress_percentage=0.0,
        )
        
        updated = monitor.update_goal_progress(goal, 50.0)
        
        assert updated.progress_percentage == 50.0
    
    def test_add_blocker(self):
        """Test add_blocker adds blocker to goal."""
        from intelligence.goal_monitoring import GoalMonitor, Goal, GoalStatus, GoalCategory
        
        monitor = GoalMonitor()
        goal = Goal(
            id="test-1",
            category=GoalCategory.ACTIVITIES,
            title="Test Goal",
        )
        
        updated = monitor.add_blocker(goal, "Time constraint")
        
        assert "Time constraint" in updated.blockers
        assert updated.status == GoalStatus.AT_RISK
    
    @pytest.mark.asyncio
    async def test_generate_progress_report(self):
        """Test generate_progress_report returns GoalProgressReport."""
        from intelligence.goal_monitoring import GoalMonitor, Goal, GoalProgressReport, GoalCategory
        
        monitor = GoalMonitor()
        goals = [
            Goal(id="1", category=GoalCategory.ACTIVITIES, title="Test", progress_percentage=50),
        ]
        
        report = await monitor.generate_progress_report("profile-123", goals, {"grade": 11})
        
        assert isinstance(report, GoalProgressReport)
        assert report.profile_id == "profile-123"
        assert 0 <= report.overall_progress <= 100


class TestGoalStatus:
    """Tests for GoalStatus enum."""
    
    def test_goal_status_values(self):
        """Test GoalStatus has all expected values."""
        from intelligence.goal_monitoring import GoalStatus
        
        assert GoalStatus.NOT_STARTED.value == "not_started"
        assert GoalStatus.IN_PROGRESS.value == "in_progress"
        assert GoalStatus.AT_RISK.value == "at_risk"
        assert GoalStatus.ON_TRACK.value == "on_track"
        assert GoalStatus.COMPLETED.value == "completed"
        assert GoalStatus.MISSED.value == "missed"


class TestGoalCategory:
    """Tests for GoalCategory enum."""
    
    def test_goal_category_values(self):
        """Test GoalCategory has all expected values."""
        from intelligence.goal_monitoring import GoalCategory
        
        assert GoalCategory.IDENTITY.value == "identity"
        assert GoalCategory.ACTIVITIES.value == "activities"
        assert GoalCategory.ACADEMICS.value == "academics"
        assert GoalCategory.TESTING.value == "testing"
        assert GoalCategory.AWARDS.value == "awards"
        assert GoalCategory.PROGRAMS.value == "programs"
        assert GoalCategory.ESSAYS.value == "essays"
        assert GoalCategory.RECOMMENDATIONS.value == "recommendations"


class TestGoalModel:
    """Tests for Goal model."""
    
    def test_goal_creation(self):
        """Test creating a Goal."""
        from intelligence.goal_monitoring import Goal, GoalCategory
        
        goal = Goal(
            id="test-1",
            category=GoalCategory.ACTIVITIES,
            title="Build leadership portfolio",
        )
        
        assert goal.id == "test-1"
        assert goal.category == GoalCategory.ACTIVITIES
        assert goal.title == "Build leadership portfolio"
        assert goal.progress_percentage == 0.0
        assert goal.blockers == []
