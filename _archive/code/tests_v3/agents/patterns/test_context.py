# tests/agents/patterns/test_context.py
"""
Tests for Context patterns: C2 User, C4 Task, C6 Temporal
FINAL VERSION - Aligned with actual API
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock


class TestStudentContext:
    """Tests for StudentContext model (C2)."""
    
    def test_student_context_importable(self):
        """Test StudentContext can be imported."""
        from agents.context.types import StudentContext
        assert StudentContext is not None
    
    def test_student_context_creation(self, sample_profile):
        """Test creating StudentContext."""
        from agents.context.types import StudentContext
        ctx = StudentContext(
            profile_id=sample_profile["id"],
            name=sample_profile["name"],
            grade=sample_profile["grade"],
        )
        assert ctx.profile_id == sample_profile["id"]
        assert ctx.name == sample_profile["name"]
    
    def test_student_context_has_profile_id(self, sample_profile):
        """Test StudentContext has profile_id."""
        from agents.context.types import StudentContext
        ctx = StudentContext(
            profile_id=sample_profile["id"],
            name=sample_profile["name"],
            grade=11,
        )
        assert hasattr(ctx, 'profile_id')


class TestContextSelection:
    """Tests for ContextSelection model."""
    
    def test_context_selection_importable(self):
        """Test ContextSelection can be imported."""
        from agents.context.types import ContextSelection
        assert ContextSelection is not None
    
    def test_context_selection_creation(self):
        """Test creating ContextSelection."""
        from agents.context.types import ContextSelection
        selection = ContextSelection()
        assert selection is not None
    
    def test_context_selection_has_include_activities(self):
        """Test ContextSelection has include_activities."""
        from agents.context.types import ContextSelection
        selection = ContextSelection(include_activities=True)
        assert selection.include_activities is True


class TestUserContextLoader:
    """Tests for UserContextLoader (C2)."""
    
    def test_loader_importable(self):
        """Test UserContextLoader can be imported."""
        from agents.context.user_context import UserContextLoader
        assert UserContextLoader is not None
    
    def test_loader_initialization(self, mock_supabase):
        """Test UserContextLoader can be initialized."""
        from agents.context.user_context import UserContextLoader
        loader = UserContextLoader(mock_supabase)
        assert loader is not None
    
    def test_loader_has_load(self, mock_supabase):
        """Test UserContextLoader has load method."""
        from agents.context.user_context import UserContextLoader
        loader = UserContextLoader(mock_supabase)
        assert hasattr(loader, 'load')
    
    @pytest.mark.asyncio
    async def test_load_returns_context(self, mock_supabase, sample_profile, sample_profile_id):
        """Test load returns context."""
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


class TestTemporalContext:
    """Tests for Temporal Context (C6)."""
    
    def test_temporal_context_importable(self):
        """Test TemporalContext can be imported."""
        from agents.context.temporal_context import TemporalContext
        assert TemporalContext is not None
    
    def test_deadline_importable(self):
        """Test Deadline can be imported."""
        from agents.context.temporal_context import Deadline
        assert Deadline is not None
    
    def test_temporal_context_creation(self):
        """Test creating TemporalContext."""
        from agents.context.temporal_context import TemporalContext
        ctx = TemporalContext(
            profile_id="test",
            current_phase="applications",
            deadlines=[],
            imminent_deadlines=[],
            urgent_count=0,
        )
        assert ctx.profile_id == "test"
    
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
    
    def test_temporal_loader_importable(self):
        """Test TemporalContextLoader can be imported."""
        from agents.context.temporal_context import TemporalContextLoader
        assert TemporalContextLoader is not None


class TestTaskContext:
    """Tests for Task Context (C4)."""
    
    def test_task_context_importable(self):
        """Test TaskContext can be imported."""
        from agents.context.task_context import TaskContext
        assert TaskContext is not None
    
    def test_task_status_importable(self):
        """Test TaskStatus can be imported."""
        from agents.context.task_context import TaskStatus
        assert TaskStatus is not None
    
    def test_task_context_creation(self):
        """Test creating TaskContext."""
        from agents.context.task_context import TaskContext, TaskStatus
        ctx = TaskContext(
            task_id="test_123",
            task_type="gameplan",
            objective="Test objective",
            status=TaskStatus.IN_PROGRESS,
        )
        assert ctx.task_id == "test_123"
    
    def test_task_context_manager_importable(self):
        """Test TaskContextManager can be imported."""
        from agents.context.task_context import TaskContextManager
        assert TaskContextManager is not None
    
    def test_task_context_manager_initialization(self):
        """Test TaskContextManager can be initialized."""
        from agents.context.task_context import TaskContextManager
        manager = TaskContextManager()
        assert manager is not None
    
    def test_task_context_manager_has_start_task(self):
        """Test TaskContextManager has start_task method."""
        from agents.context.task_context import TaskContextManager
        manager = TaskContextManager()
        assert hasattr(manager, 'start_task')
    
    def test_task_context_manager_start_task(self):
        """Test starting a task."""
        from agents.context.task_context import TaskContextManager, TaskStatus
        manager = TaskContextManager()
        ctx = manager.start_task(
            task_type="assessment",
            objective="Test",
            steps_total=5,
        )
        assert ctx.task_type == "assessment"
        assert ctx.status == TaskStatus.IN_PROGRESS


class TestContextSelector:
    """Tests for Context Selector."""
    
    def test_context_selector_importable(self):
        """Test ContextSelector can be imported."""
        from agents.context.context_selector import ContextSelector
        assert ContextSelector is not None
    
    def test_selector_for_task_exists(self):
        """Test for_task method exists."""
        from agents.context.context_selector import ContextSelector
        assert hasattr(ContextSelector, 'for_task')
    
    def test_selector_for_agent_exists(self):
        """Test for_agent method exists."""
        from agents.context.context_selector import ContextSelector
        assert hasattr(ContextSelector, 'for_agent')
    
    def test_selector_for_task_returns_selection(self):
        """Test for_task returns ContextSelection."""
        from agents.context.context_selector import ContextSelector
        selection = ContextSelector.for_task("assessment")
        assert selection is not None
    
    def test_selector_for_agent_returns_selection(self):
        """Test for_agent returns ContextSelection."""
        from agents.context.context_selector import ContextSelector
        selection = ContextSelector.for_agent("ec_agent")
        assert selection is not None
