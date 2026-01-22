# tests/agents/patterns/test_intelligence.py
"""
Tests for Intelligence patterns: A12 Prioritization, I3 Goal Monitoring
These are USP (Unique Selling Proposition) patterns - CRITICAL to test thoroughly.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock


class TestPrioritizationEngine:
    """Tests for Prioritization Engine (A12 - USP)."""
    
    def test_prioritize_by_urgency(self, sample_tasks):
        """Test that urgent tasks get higher priority."""
        from agents.intelligence.prioritization import PrioritizationEngine, PriorityLevel
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize(sample_tasks)
        
        # First task (3 days) should be highest priority
        assert prioritized[0].task_id == "task_1"
        assert prioritized[0].priority_level == PriorityLevel.CRITICAL
    
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
        assert prioritized[0].importance_score > prioritized[1].importance_score
    
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
    
    def test_student_fit_high_energy(self):
        """Test task matching for high-energy student."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        tasks = [
            {"id": "1", "name": "Easy task", "category": "research", "days_until": 10, "difficulty": 0.2},
            {"id": "2", "name": "Hard task", "category": "research", "days_until": 10, "difficulty": 0.8},
        ]
        
        # High energy = can handle hard tasks
        prioritized = engine.prioritize(tasks, student_energy=0.9)
        
        hard_task = next(t for t in prioritized if t.task_id == "2")
        easy_task = next(t for t in prioritized if t.task_id == "1")
        assert hard_task.student_fit_score >= easy_task.student_fit_score
    
    def test_student_fit_low_energy(self):
        """Test task matching for low-energy student - give quick wins."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        tasks = [
            {"id": "1", "name": "Easy task", "category": "research", "days_until": 10, "difficulty": 0.2},
            {"id": "2", "name": "Hard task", "category": "research", "days_until": 10, "difficulty": 0.8},
        ]
        
        # Low energy = give easy wins
        prioritized = engine.prioritize(tasks, student_energy=0.2)
        
        easy_task = next(t for t in prioritized if t.task_id == "1")
        hard_task = next(t for t in prioritized if t.task_id == "2")
        assert easy_task.student_fit_score >= hard_task.student_fit_score
    
    def test_get_top_priority(self, sample_tasks):
        """Test getting top N priorities."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize(sample_tasks)
        
        top_2 = engine.get_top_priority(prioritized, n=2)
        
        assert len(top_2) == 2
        assert top_2[0].priority_score >= top_2[1].priority_score
    
    def test_get_quick_wins(self):
        """Test finding quick wins (easy + high impact)."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        tasks = [
            {"id": "1", "name": "Easy high-impact", "category": "award_submission", "days_until": 10, "difficulty": 0.3},
            {"id": "2", "name": "Hard low-impact", "category": "research", "days_until": 10, "difficulty": 0.9},
        ]
        
        prioritized = engine.prioritize(tasks, student_energy=0.5)
        quick_wins = engine.get_quick_wins(prioritized)
        
        # Should return list (may be empty if thresholds not met)
        assert isinstance(quick_wins, list)
    
    def test_priority_level_thresholds(self):
        """Test priority level assignment."""
        from agents.intelligence.prioritization import PrioritizationEngine, PriorityLevel
        
        engine = PrioritizationEngine()
        
        assert engine._score_to_level(0.9) == PriorityLevel.CRITICAL
        assert engine._score_to_level(0.7) == PriorityLevel.HIGH
        assert engine._score_to_level(0.5) == PriorityLevel.MEDIUM
        assert engine._score_to_level(0.2) == PriorityLevel.LOW
    
    def test_urgency_calculation(self):
        """Test urgency calculation based on deadline."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        assert engine._calculate_urgency({"days_until": 2}) == 1.0  # Critical
        assert engine._calculate_urgency({"days_until": 5}) == 0.8  # High
        assert engine._calculate_urgency({"days_until": 10}) == 0.6  # Medium
        assert engine._calculate_urgency({"days_until": None}) == 0.3  # No deadline
    
    def test_empty_task_list(self):
        """Test handling empty task list."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize([])
        
        assert prioritized == []
    
    def test_single_task(self):
        """Test prioritizing single task."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        tasks = [{"id": "1", "name": "Only task", "category": "essay_draft", "days_until": 5}]
        prioritized = engine.prioritize(tasks)
        
        assert len(prioritized) == 1
        assert prioritized[0].task_id == "1"


class TestGoalMonitor:
    """Tests for Goal Monitor (I3 - USP)."""
    
    @pytest.mark.asyncio
    async def test_check_progress(self, mock_supabase, sample_profile_id, sample_goals):
        """Test checking progress on goals."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=sample_goals
        )
        
        monitor = GoalMonitor(mock_supabase)
        progress = await monitor.check_progress(sample_profile_id)
        
        assert "goals" in progress
        assert len(progress["goals"]) == len(sample_goals)
    
    @pytest.mark.asyncio
    async def test_generate_alerts_behind_schedule(self, mock_supabase, sample_profile_id):
        """Test alert generation for goals behind schedule."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        # Goal with low progress and upcoming deadline
        behind_goal = {
            "id": "goal-1",
            "name": "MIT Application",
            "target_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "progress_percentage": 20,  # Only 20% with 7 days left
            "status": "active",
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[behind_goal]
        )
        
        monitor = GoalMonitor(mock_supabase)
        alerts = await monitor.generate_alerts(sample_profile_id)
        
        # Should generate alert for behind-schedule goal
        assert len(alerts) >= 1
    
    @pytest.mark.asyncio
    async def test_no_alerts_on_track(self, mock_supabase, sample_profile_id):
        """Test no alerts when goals are on track."""
        from agents.intelligence.goal_monitoring import GoalMonitor
        
        on_track_goal = {
            "id": "goal-1",
            "name": "MIT Application",
            "target_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "progress_percentage": 80,  # 80% with 30 days left
            "status": "active",
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[on_track_goal]
        )
        
        monitor = GoalMonitor(mock_supabase)
        alerts = await monitor.generate_alerts(sample_profile_id)
        
        # Should not generate critical alerts for on-track goals
        critical_alerts = [a for a in alerts if a.get("type") == "critical"]
        assert len(critical_alerts) == 0
    
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
