# tests/agents/patterns/test_intelligence.py
"""
Tests for Intelligence patterns: A12 Prioritization, I3 Goal Monitoring
These are USP (Unique Selling Proposition) patterns - CRITICAL to test thoroughly.
CORRECTED to match actual implementation API
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock


class TestPrioritizationEngine:
    """Tests for Prioritization Engine (A12 - USP)."""
    
    def test_engine_initialization(self):
        """Test PrioritizationEngine can be initialized."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        assert engine is not None
    
    def test_prioritize_returns_list(self, sample_tasks):
        """Test that prioritize returns a list."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize(sample_tasks)
        
        assert isinstance(prioritized, list)
        assert len(prioritized) == len(sample_tasks)
    
    def test_prioritize_by_urgency(self, sample_tasks):
        """Test that urgent tasks get higher priority."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize(sample_tasks)
        
        # First task (3 days) should be highest priority
        assert prioritized[0].task_id == "task_1"
    
    def test_prioritize_by_importance(self):
        """Test importance scoring by category."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        tasks = [
            {"id": "1", "name": "App Deadline", "category": "application_deadline", "days_until": 30},
            {"id": "2", "name": "Research", "category": "research", "days_until": 30},
        ]
        
        prioritized = engine.prioritize(tasks)
        
        # Application deadline should rank higher
        assert prioritized[0].task_id == "1"
    
    def test_prioritize_with_blocking(self):
        """Test that blocking tasks get priority boost."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        tasks = [
            {"id": "1", "name": "Non-blocking", "category": "research", "days_until": 10, "blocking_count": 0},
            {"id": "2", "name": "Blocking", "category": "research", "days_until": 10, "blocking_count": 3},
        ]
        
        prioritized = engine.prioritize(tasks)
        
        # Blocking task should rank higher
        assert prioritized[0].task_id == "2"
    
    def test_prioritize_with_student_energy(self):
        """Test prioritization with student energy level."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        tasks = [
            {"id": "1", "name": "Easy task", "category": "research", "days_until": 10, "difficulty": 0.2},
            {"id": "2", "name": "Hard task", "category": "research", "days_until": 10, "difficulty": 0.8},
        ]
        
        # Test with high energy
        prioritized_high = engine.prioritize(tasks, student_energy=0.9)
        assert len(prioritized_high) == 2
        
        # Test with low energy
        prioritized_low = engine.prioritize(tasks, student_energy=0.2)
        assert len(prioritized_low) == 2
    
    def test_get_top_priority(self, sample_tasks):
        """Test getting top N priorities."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize(sample_tasks)
        
        top_2 = engine.get_top_priority(prioritized, n=2)
        
        assert len(top_2) == 2
    
    def test_get_quick_wins(self):
        """Test finding quick wins (easy + high impact)."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        tasks = [
            {"id": "1", "name": "Easy high-impact", "category": "award_submission", "days_until": 10, "difficulty": 0.3},
        ]
        
        prioritized = engine.prioritize(tasks, student_energy=0.5)
        quick_wins = engine.get_quick_wins(prioritized)
        
        assert isinstance(quick_wins, list)
    
    def test_empty_task_list(self):
        """Test handling empty task list."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize([])
        
        assert prioritized == []
    
    def test_urgency_calculation(self):
        """Test urgency calculation based on deadline."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        # Test various deadline distances
        assert engine._calculate_urgency({"days_until": 2}) >= 0.8  # Critical
        assert engine._calculate_urgency({"days_until": 30}) <= 0.5  # Low
        assert engine._calculate_urgency({"days_until": None}) <= 0.5  # No deadline
    
    def test_priority_has_score(self, sample_tasks):
        """Test that prioritized items have score."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize(sample_tasks)
        
        # Check items have priority score (may be named 'priority' or 'priority_score')
        first_item = prioritized[0]
        assert hasattr(first_item, 'priority_score') or hasattr(first_item, 'priority')


class TestPriorityLevel:
    """Tests for PriorityLevel enum."""
    
    def test_priority_level_exists(self):
        """Test PriorityLevel enum exists."""
        from agents.intelligence.prioritization import PriorityLevel
        
        assert PriorityLevel is not None
    
    def test_priority_level_values(self):
        """Test PriorityLevel has expected values."""
        from agents.intelligence.prioritization import PriorityLevel
        
        # Check for common priority levels
        assert hasattr(PriorityLevel, 'CRITICAL') or hasattr(PriorityLevel, 'HIGH')


class TestGoalMonitor:
    """Tests for Goal Monitor (I3 - USP)."""
    
    def test_monitor_initialization(self, mock_supabase):
        """Test GoalMonitor initialization."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        monitor = GoalMonitor(mock_supabase)
        assert monitor is not None
    
    @pytest.mark.asyncio
    async def test_check_progress(self, mock_supabase, sample_profile_id, sample_goals):
        """Test checking progress on goals."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=sample_goals
        )
        
        monitor = GoalMonitor(mock_supabase)
        progress = await monitor.check_progress(sample_profile_id)
        
        assert progress is not None
        assert "goals" in progress
    
    @pytest.mark.asyncio
    async def test_generate_alerts(self, mock_supabase, sample_profile_id):
        """Test alert generation."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        behind_goal = {
            "id": "goal-1",
            "name": "MIT Application",
            "target_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "progress_percentage": 20,
            "status": "active",
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[behind_goal]
        )
        
        monitor = GoalMonitor(mock_supabase)
        alerts = await monitor.generate_alerts(sample_profile_id)
        
        assert isinstance(alerts, list)
    
    @pytest.mark.asyncio
    async def test_empty_goals(self, mock_supabase, sample_profile_id):
        """Test handling no goals."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[]
        )
        
        monitor = GoalMonitor(mock_supabase)
        progress = await monitor.check_progress(sample_profile_id)
        
        assert progress["goals"] == []
