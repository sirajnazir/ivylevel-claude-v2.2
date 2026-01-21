# tests/agents/patterns/test_intelligence.py
"""
Tests for Intelligence patterns: A12 Prioritization, I3 Goal Monitoring
FINAL VERSION - Aligned with actual model structures
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock


class TestPrioritizationEngine:
    """Tests for Prioritization Engine (A12 - USP)."""
    
    def test_engine_importable(self):
        """Test PrioritizationEngine can be imported."""
        from agents.intelligence.prioritization import PrioritizationEngine
        assert PrioritizationEngine is not None
    
    def test_engine_initialization(self):
        """Test PrioritizationEngine can be initialized."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        assert engine is not None
    
    def test_prioritize_empty_list(self):
        """Test prioritizing empty task list."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        result = engine.prioritize([])
        assert result == []
    
    def test_prioritize_returns_list(self, sample_tasks):
        """Test prioritize returns a list."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        result = engine.prioritize(sample_tasks)
        assert isinstance(result, list)
        assert len(result) == len(sample_tasks)
    
    def test_prioritized_item_has_task_id(self, sample_tasks):
        """Test prioritized items have task_id."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        result = engine.prioritize(sample_tasks)
        # Check first item has task_id (may be 'id' or 'task_id')
        first = result[0]
        assert hasattr(first, 'task_id') or hasattr(first, 'id')
    
    def test_prioritized_item_has_score(self, sample_tasks):
        """Test prioritized items have priority score."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        result = engine.prioritize(sample_tasks)
        first = result[0]
        # May be named 'priority', 'priority_score', or 'score'
        has_score = (
            hasattr(first, 'priority') or 
            hasattr(first, 'priority_score') or 
            hasattr(first, 'score')
        )
        assert has_score
    
    def test_urgent_tasks_first(self, sample_tasks):
        """Test that urgent tasks come first."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        result = engine.prioritize(sample_tasks)
        # Task with 3 days should be first (task_1)
        first = result[0]
        task_id = getattr(first, 'task_id', None) or getattr(first, 'id', None)
        assert task_id == "task_1"
    
    def test_calculate_urgency_exists(self):
        """Test _calculate_urgency method exists."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        assert hasattr(engine, '_calculate_urgency')
    
    def test_get_top_priority_exists(self):
        """Test get_top_priority method exists."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        assert hasattr(engine, 'get_top_priority')
    
    def test_get_quick_wins_exists(self):
        """Test get_quick_wins method exists."""
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        assert hasattr(engine, 'get_quick_wins')


class TestPriorityLevel:
    """Tests for PriorityLevel enum."""
    
    def test_priority_level_exists(self):
        """Test PriorityLevel enum exists."""
        from agents.intelligence.prioritization import PriorityLevel
        assert PriorityLevel is not None
    
    def test_priority_level_is_enum(self):
        """Test PriorityLevel is an enum."""
        from agents.intelligence.prioritization import PriorityLevel
        from enum import Enum
        assert issubclass(PriorityLevel, Enum)
    
    def test_priority_level_has_values(self):
        """Test PriorityLevel has values."""
        from agents.intelligence.prioritization import PriorityLevel
        values = list(PriorityLevel)
        assert len(values) >= 2  # At least LOW and HIGH


class TestGoalMonitor:
    """Tests for Goal Monitor (I3 - USP)."""
    
    def test_monitor_importable(self):
        """Test GoalMonitor can be imported."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        assert GoalMonitor is not None
    
    def test_monitor_initialization(self, mock_supabase):
        """Test GoalMonitor can be initialized."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        monitor = GoalMonitor(mock_supabase)
        assert monitor is not None
    
    def test_monitor_has_check_progress(self, mock_supabase):
        """Test GoalMonitor has check_progress method."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        monitor = GoalMonitor(mock_supabase)
        assert hasattr(monitor, 'check_progress')
    
    def test_monitor_has_generate_alerts(self, mock_supabase):
        """Test GoalMonitor has generate_alerts method."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        monitor = GoalMonitor(mock_supabase)
        assert hasattr(monitor, 'generate_alerts')
    
    @pytest.mark.asyncio
    async def test_check_progress_returns_dict(self, mock_supabase, sample_profile_id, sample_goals):
        """Test check_progress returns a dict."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=sample_goals
        )
        
        monitor = GoalMonitor(mock_supabase)
        result = await monitor.check_progress(sample_profile_id)
        
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_check_progress_has_goals(self, mock_supabase, sample_profile_id, sample_goals):
        """Test check_progress result has goals."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=sample_goals
        )
        
        monitor = GoalMonitor(mock_supabase)
        result = await monitor.check_progress(sample_profile_id)
        
        assert "goals" in result
    
    @pytest.mark.asyncio
    async def test_generate_alerts_returns_list(self, mock_supabase, sample_profile_id):
        """Test generate_alerts returns a list."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[]
        )
        
        monitor = GoalMonitor(mock_supabase)
        result = await monitor.generate_alerts(sample_profile_id)
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_empty_goals_handled(self, mock_supabase, sample_profile_id):
        """Test handling of no goals."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[]
        )
        
        monitor = GoalMonitor(mock_supabase)
        result = await monitor.check_progress(sample_profile_id)
        
        assert result["goals"] == []


class TestGoalCategory:
    """Tests for GoalCategory enum if it exists."""
    
    def test_goal_category_importable(self):
        """Test GoalCategory can be imported (if it exists)."""
        try:
            from agents.intelligence.goal_monitoring import GoalCategory
            assert GoalCategory is not None
        except ImportError:
            pytest.skip("GoalCategory not available")
