# tests/agents/patterns/test_context.py
"""
Tests for Context patterns: C2 User, C4 Task, C6 Temporal
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch


class TestStudentContext:
    """Tests for StudentContext model (C2)."""
    
    def test_student_context_creation(self, sample_profile):
        """Test creating a StudentContext from profile data."""
        from agents.context.types import StudentContext
        
        ctx = StudentContext(
            profile_id=sample_profile["id"],
            name=sample_profile["name"],
            grade=sample_profile["grade"],
            archetype=sample_profile["archetype_id"],
            gpa=sample_profile["gpa_weighted"],
        )
        
        assert ctx.profile_id == sample_profile["id"]
        assert ctx.name == sample_profile["name"]
        assert ctx.grade == 11
        assert ctx.archetype == "stem_innovator"
    
    def test_student_context_defaults(self):
        """Test default values for optional fields."""
        from agents.context.types import StudentContext
        
        ctx = StudentContext(
            profile_id="test-id",
            name="Test",
            grade=10,
        )
        
        assert ctx.communication_style == "balanced"
        assert ctx.motivation_type == "achievement"
        assert ctx.stress_indicators == []
        assert ctx.activities == []


class TestUserContextLoader:
    """Tests for UserContextLoader (C2)."""
    
    @pytest.mark.asyncio
    async def test_load_basic_profile(self, mock_supabase, sample_profile, sample_profile_id):
        """Test loading basic profile context."""
        from agents.context.user_context import UserContextLoader
        from agents.context.types import ContextSelection
        
        # Setup mock
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data=sample_profile
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[]
        )
        
        loader = UserContextLoader(mock_supabase)
        ctx = await loader.load(sample_profile_id)
        
        assert ctx.profile_id == sample_profile_id
        assert ctx.name == sample_profile["name"]
    
    @pytest.mark.asyncio
    async def test_load_with_activities(self, mock_supabase, sample_profile, sample_activities, sample_profile_id):
        """Test loading with activities included."""
        from agents.context.user_context import UserContextLoader
        from agents.context.types import ContextSelection
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data=sample_profile
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=sample_activities
        )
        
        loader = UserContextLoader(mock_supabase)
        selection = ContextSelection(include_activities=True)
        ctx = await loader.load(sample_profile_id, selection)
        
        assert len(ctx.activities) == len(sample_activities)


class TestTemporalContext:
    """Tests for Temporal Context (C6)."""
    
    def test_deadline_creation(self):
        """Test creating a deadline."""
        from agents.context.temporal_context import Deadline
        
        now = datetime.utcnow()
        deadline = Deadline(
            id="test-1",
            name="Test Deadline",
            due_date=now + timedelta(days=2),
            category="application",
            priority="critical",
            status="imminent",
            days_until=2,
        )
        
        assert deadline.priority == "critical"
        assert deadline.status == "imminent"
        assert deadline.days_until == 2
    
    def test_temporal_context_has_urgent(self):
        """Test has_urgent_items property."""
        from agents.context.temporal_context import TemporalContext
        
        ctx = TemporalContext(
            profile_id="test",
            current_phase="applications",
            deadlines=[],
            imminent_deadlines=[],
            urgent_count=3,
        )
        
        assert ctx.has_urgent_items is True
        
        ctx.urgent_count = 0
        assert ctx.has_urgent_items is False
    
    @pytest.mark.asyncio
    async def test_temporal_loader_phase_detection(self, mock_supabase, sample_profile_id, sample_deadlines):
        """Test current phase detection."""
        from agents.context.temporal_context import TemporalContextLoader
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=sample_deadlines
        )
        
        loader = TemporalContextLoader(mock_supabase)
        ctx = await loader.load(sample_profile_id)
        
        assert ctx.current_phase in ["summer_programs", "essays", "applications", "decisions"]


class TestTaskContext:
    """Tests for Task Context (C4)."""
    
    def test_task_context_creation(self):
        """Test creating a task context."""
        from agents.context.task_context import TaskContext, TaskStatus
        
        ctx = TaskContext(
            task_id="task_123",
            task_type="gameplan",
            objective="Generate personalized game plan",
            status=TaskStatus.IN_PROGRESS,
        )
        
        assert ctx.task_id == "task_123"
        assert ctx.task_type == "gameplan"
        assert ctx.status == TaskStatus.IN_PROGRESS
    
    def test_task_context_manager_start(self):
        """Test starting a new task."""
        from agents.context.task_context import TaskContextManager, TaskStatus
        
        manager = TaskContextManager()
        ctx = manager.start_task(
            task_type="assessment",
            objective="Analyze student profile",
            steps_total=5,
        )
        
        assert ctx.task_type == "assessment"
        assert ctx.status == TaskStatus.IN_PROGRESS
        assert ctx.steps_total == 5
        assert ctx.progress_percentage == 0.0
    
    def test_task_context_manager_progress(self):
        """Test updating task progress."""
        from agents.context.task_context import TaskContextManager
        
        manager = TaskContextManager()
        manager.start_task("test", "Test task", steps_total=4)
        
        manager.update_progress(2, current_agent="ec_agent")
        
        assert manager.current_task.steps_completed == 2
        assert manager.current_task.progress_percentage == 50.0
        assert manager.current_task.current_agent == "ec_agent"
    
    def test_task_context_manager_complete(self):
        """Test completing a task."""
        from agents.context.task_context import TaskContextManager, TaskStatus
        
        manager = TaskContextManager()
        manager.start_task("test", "Test task", steps_total=4)
        
        manager.complete_task()
        
        assert manager.current_task.status == TaskStatus.COMPLETED
        assert manager.current_task.progress_percentage == 100.0


class TestContextSelector:
    """Tests for Context Selector (USP)."""
    
    def test_selector_for_assessment(self):
        """Test context selection for assessment task."""
        from agents.context.context_selector import ContextSelector
        
        selection = ContextSelector.for_task("assessment")
        
        assert selection.include_activities is True
        assert selection.include_academics is True
        assert selection.include_history is False
    
    def test_selector_for_execution(self):
        """Test context selection for execution task."""
        from agents.context.context_selector import ContextSelector
        
        selection = ContextSelector.for_task("execution")
        
        assert selection.include_activities is True
        assert selection.include_academics is False
        assert selection.include_history is True
        assert selection.max_history_items == 10
    
    def test_selector_for_crisis(self):
        """Test context selection for crisis - needs full history."""
        from agents.context.context_selector import ContextSelector
        
        selection = ContextSelector.for_task("crisis")
        
        assert selection.include_history is True
        assert selection.max_history_items == 20
    
    def test_selector_for_agent(self):
        """Test context selection by agent name."""
        from agents.context.context_selector import ContextSelector
        
        ec_selection = ContextSelector.for_agent("ec_agent")
        exec_selection = ContextSelector.for_agent("execution_agent")
        
        assert ec_selection.include_academics is True
        assert exec_selection.include_academics is False
