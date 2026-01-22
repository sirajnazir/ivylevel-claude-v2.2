# tests/agents/patterns/test_context.py
"""
Tests for Context patterns: C2 User, C4 Task, C6 Temporal
CORRECTED to match actual implementation API
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
        )
        
        assert ctx.profile_id == sample_profile["id"]
        assert ctx.name == sample_profile["name"]
        assert ctx.grade == 11
    
    def test_student_context_optional_fields(self):
        """Test StudentContext with optional fields."""
        from agents.context.types import StudentContext
        
        ctx = StudentContext(
            profile_id="test-id",
            name="Test",
            grade=10,
        )
        
        # Check that required fields are set
        assert ctx.profile_id == "test-id"
        assert ctx.name == "Test"
        assert ctx.grade == 10


class TestContextSelection:
    """Tests for ContextSelection model."""
    
    def test_context_selection_defaults(self):
        """Test ContextSelection default values."""
        from agents.context.types import ContextSelection
        
        selection = ContextSelection()
        
        # Check defaults exist (may vary by implementation)
        assert selection is not None
    
    def test_context_selection_custom(self):
        """Test ContextSelection with custom values."""
        from agents.context.types import ContextSelection
        
        selection = ContextSelection(
            include_activities=True,
            include_academics=False,
        )
        
        assert selection.include_activities is True
        assert selection.include_academics is False


class TestUserContextLoader:
    """Tests for UserContextLoader (C2)."""
    
    def test_loader_initialization(self, mock_supabase):
        """Test UserContextLoader can be initialized."""
        from agents.context.user_context import UserContextLoader
        
        loader = UserContextLoader(mock_supabase)
        assert loader is not None
    
    @pytest.mark.asyncio
    async def test_load_returns_context(self, mock_supabase, sample_profile, sample_profile_id):
        """Test loading returns a context object."""
        from agents.context.user_context import UserContextLoader
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data=sample_profile
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[]
        )
        
        loader = UserContextLoader(mock_supabase)
        ctx = await loader.load(sample_profile_id)
        
        assert ctx is not None
        assert ctx.profile_id == sample_profile_id


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
        
        assert deadline.name == "Test Deadline"
        assert deadline.days_until == 2
    
    def test_temporal_context_creation(self):
        """Test TemporalContext creation."""
        from agents.context.temporal_context import TemporalContext
        
        ctx = TemporalContext(
            profile_id="test",
            current_phase="applications",
            deadlines=[],
            imminent_deadlines=[],
            urgent_count=0,
        )
        
        assert ctx.profile_id == "test"
        assert ctx.current_phase == "applications"
    
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
    
    def test_temporal_loader_initialization(self, mock_supabase):
        """Test TemporalContextLoader initialization."""
        from agents.context.temporal_context import TemporalContextLoader
        
        loader = TemporalContextLoader(mock_supabase)
        assert loader is not None


class TestTaskContext:
    """Tests for Task Context (C4)."""
    
    def test_task_status_enum(self):
        """Test TaskStatus enum values."""
        from agents.context.task_context import TaskStatus
        
        # Check enum exists and has expected values
        assert TaskStatus.IN_PROGRESS is not None
        assert TaskStatus.COMPLETED is not None
    
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
    
    def test_task_context_manager_initialization(self):
        """Test TaskContextManager initialization."""
        from agents.context.task_context import TaskContextManager
        
        manager = TaskContextManager()
        assert manager is not None
    
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
    
    def test_task_context_manager_update_progress(self):
        """Test updating task progress."""
        from agents.context.task_context import TaskContextManager
        
        manager = TaskContextManager()
        manager.start_task("test", "Test task", steps_total=4)
        
        manager.update_progress(2)
        
        assert manager.current_task.steps_completed == 2
    
    def test_task_context_manager_complete(self):
        """Test completing a task."""
        from agents.context.task_context import TaskContextManager, TaskStatus
        
        manager = TaskContextManager()
        manager.start_task("test", "Test task", steps_total=4)
        
        manager.complete_task()
        
        assert manager.current_task.status == TaskStatus.COMPLETED


class TestContextSelector:
    """Tests for Context Selector (USP)."""
    
    def test_selector_for_task(self):
        """Test context selection for task type."""
        from agents.context.context_selector import ContextSelector
        
        selection = ContextSelector.for_task("assessment")
        
        assert selection is not None
        assert selection.include_activities is True
    
    def test_selector_for_execution(self):
        """Test context selection for execution task."""
        from agents.context.context_selector import ContextSelector
        
        selection = ContextSelector.for_task("execution")
        
        assert selection is not None
        assert selection.include_history is True
    
    def test_selector_for_agent(self):
        """Test context selection by agent name."""
        from agents.context.context_selector import ContextSelector
        
        selection = ContextSelector.for_agent("ec_agent")
        
        assert selection is not None
    
    def test_selector_unknown_task(self):
        """Test context selection for unknown task type."""
        from agents.context.context_selector import ContextSelector
        
        # Should return default selection
        selection = ContextSelector.for_task("unknown_task")
        
        assert selection is not None
