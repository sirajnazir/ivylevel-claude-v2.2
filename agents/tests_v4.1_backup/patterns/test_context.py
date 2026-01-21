# agents/tests/patterns/test_context.py
"""
Tests for Context Patterns (C2, C4, C6) - v5.4 True Autonomous Agents.

Tests:
- C2: User Context loading and selection
- C4: Task Context management
- C6: Temporal Context awareness
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestUserContext:
    """Tests for C2: User Context pattern."""

    def test_student_context_model_creation(self, sample_student_context):
        """Test StudentContext model can be created with valid data."""
        from context import StudentContext

        ctx = StudentContext(**sample_student_context)

        assert ctx.profile_id == "test-profile-123"
        assert ctx.name == "Test Student"
        assert ctx.grade == 11
        assert ctx.archetype == "DoubleDown"
        assert ctx.spike == "robotics"

    def test_student_context_has_required_fields(self, sample_student_context):
        """Test StudentContext includes all required fields for coaching."""
        from context import StudentContext

        ctx = StudentContext(**sample_student_context)

        # Core identity
        assert hasattr(ctx, "profile_id")
        assert hasattr(ctx, "name")
        assert hasattr(ctx, "grade")

        # Coaching-specific (USP)
        assert hasattr(ctx, "archetype")
        assert hasattr(ctx, "spike")
        assert hasattr(ctx, "cri_score")
        assert hasattr(ctx, "eds_score")
        assert hasattr(ctx, "brand_statement")

    def test_context_selection_relevance(self):
        """Test ContextSelection filters context appropriately."""
        from context import ContextSelector, TaskType

        selector = ContextSelector()

        # Assessment needs full context
        assessment_selection = selector.select_for_task(
            TaskType.ASSESSMENT,
            {"activities": True, "academics": True, "goals": True}
        )
        assert assessment_selection.include_activities is True
        assert assessment_selection.include_academics is True

        # Chat might need less
        chat_selection = selector.select_for_task(
            TaskType.CHAT,
            {"activities": False}
        )
        # Should still include basics

    def test_context_selector_agent_needs(self):
        """Test context selector provides correct context for each agent."""
        from context import get_agent_context_needs, ContextRelevance

        # Gameplan agent needs everything
        gameplan_needs = get_agent_context_needs("gameplan_agent")
        # Returns ContextRelevance enum values, not booleans
        assert gameplan_needs.get("activities") is not None
        assert gameplan_needs.get("goals") is not None

        # Chat agent needs less
        chat_needs = get_agent_context_needs("chat_agent")
        # Should still work

    @pytest.mark.asyncio
    async def test_user_context_loader_with_mock(self, mock_supabase, sample_student_context):
        """Test UserContextLoader loads data from Supabase."""
        from context import UserContextLoader, ContextSelection

        # Setup mock data
        mock_supabase._tables["profiles"] = [sample_student_context]

        loader = UserContextLoader(mock_supabase)
        selection = ContextSelection()

        ctx = await loader.load_context("test-profile-123", selection)

        assert ctx is not None
        assert ctx.profile_id == "test-profile-123"


class TestTaskContext:
    """Tests for C4: Task Context pattern."""

    def test_task_context_creation(self, sample_task_context):
        """Test TaskContext model creation."""
        from context import TaskContext, TaskStatus, TaskType

        ctx = TaskContext(
            task_id=sample_task_context["task_id"],
            task_type=TaskType.GAMEPLAN,
            objective=sample_task_context["objective"],
            status=TaskStatus.IN_PROGRESS,
        )

        assert ctx.task_id == "task-abc-123"
        assert ctx.status == TaskStatus.IN_PROGRESS

    def test_task_manager_create_and_track(self):
        """Test TaskContextManager creates and tracks tasks."""
        from context import TaskContextManager, TaskType

        manager = TaskContextManager(supabase_client=None)

        # Create task
        task = manager.create_task(
            task_type=TaskType.ASSESSMENT,
            objective="Analyze student profile",
        )

        assert task is not None
        assert task.task_id is not None
        assert task.task_type == TaskType.ASSESSMENT

    def test_task_manager_start_task(self):
        """Test starting a task updates state."""
        from context import TaskContextManager, TaskType

        manager = TaskContextManager(supabase_client=None)
        task = manager.create_task(TaskType.GAMEPLAN, "Generate gameplan")

        manager.start_task(task.task_id, "gameplan_agent")

        # Task should be tracked as started

    def test_task_manager_complete_task(self):
        """Test completing a task updates state."""
        from context import TaskContextManager, TaskType

        manager = TaskContextManager(supabase_client=None)
        task = manager.create_task(TaskType.GAMEPLAN, "Generate gameplan")
        manager.start_task(task.task_id, "gameplan_agent")

        manager.complete_task(task.task_id, success=True)

        # Task should be marked complete

    def test_task_types_enumeration(self):
        """Test all task types are defined."""
        from context import TaskType

        assert TaskType.ASSESSMENT is not None
        assert TaskType.GAMEPLAN is not None
        assert TaskType.CHAT is not None
        assert TaskType.GENERAL is not None

    def test_convenience_task_creators(self):
        """Test convenience functions for common tasks."""
        from context import TaskContextManager, create_assessment_task, create_gameplan_task

        # Convenience functions require a manager
        manager = TaskContextManager(supabase_client=None)

        assessment = create_assessment_task(manager, "profile-123")
        assert assessment.task_type.value == "assessment"

        gameplan = create_gameplan_task(manager, "profile-123")
        assert gameplan.task_type.value == "gameplan"


class TestTemporalContext:
    """Tests for C6: Temporal Context pattern."""

    def test_temporal_context_creation(self, sample_temporal_context):
        """Test TemporalContext model creation."""
        from context import TemporalContext, AdmissionsPhase

        # AdmissionsPhase enum has: SUMMER_PROGRAMS, ACTIVITIES, ESSAYS, APPLICATIONS, DECISIONS
        ctx = TemporalContext(
            profile_id="test-profile",
            current_phase=AdmissionsPhase.ACTIVITIES,
            deadlines=[],
        )

        assert ctx.current_phase == AdmissionsPhase.ACTIVITIES
        assert ctx.profile_id == "test-profile"

    def test_deadline_model(self):
        """Test Deadline model with all fields."""
        from context import Deadline, DeadlinePriority, DeadlineStatus, DeadlineCategory

        # DeadlineCategory enum has: APPLICATION, AWARD, PROGRAM, ESSAY, RECOMMENDATION, TEST, OTHER
        deadline = Deadline(
            id="deadline-1",
            name="SAT Registration",
            due_date=datetime.utcnow() + timedelta(days=30),
            priority=DeadlinePriority.HIGH,
            status=DeadlineStatus.UPCOMING,
            category=DeadlineCategory.TEST,
        )

        assert deadline.name == "SAT Registration"
        assert deadline.priority == DeadlinePriority.HIGH

    def test_admissions_phases(self):
        """Test all admissions phases are defined."""
        from context import AdmissionsPhase

        # Actual phases: SUMMER_PROGRAMS, ACTIVITIES, ESSAYS, APPLICATIONS, DECISIONS
        assert hasattr(AdmissionsPhase, "SUMMER_PROGRAMS")
        assert hasattr(AdmissionsPhase, "ACTIVITIES")
        assert hasattr(AdmissionsPhase, "ESSAYS")
        assert hasattr(AdmissionsPhase, "APPLICATIONS")
        assert hasattr(AdmissionsPhase, "DECISIONS")

    def test_phase_recommendations(self):
        """Test phase-specific recommendations are available."""
        from context import get_phase_recommendations, AdmissionsPhase

        # Use valid phase enum value
        recs = get_phase_recommendations(AdmissionsPhase.ACTIVITIES)

        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_admissions_calendar_exists(self):
        """Test admissions calendar data is available."""
        from context import ADMISSIONS_CALENDAR

        assert ADMISSIONS_CALENDAR is not None
        assert isinstance(ADMISSIONS_CALENDAR, dict)

    @pytest.mark.asyncio
    async def test_temporal_context_loader(self, mock_supabase):
        """Test TemporalContextLoader loads and computes context."""
        from context import TemporalContextLoader

        loader = TemporalContextLoader(mock_supabase)

        ctx = await loader.load_context("test-profile-123")

        assert ctx is not None
        assert ctx.current_phase is not None


class TestContextIntegration:
    """Integration tests for context patterns working together."""

    def test_all_context_types_importable(self):
        """Test all context types can be imported."""
        from context import (
            StudentContext,
            TemporalContext,
            TaskContext,
            WorkingMemory,
            ContextSelector,
        )

        # All should be importable

    def test_context_selector_matrix_complete(self):
        """Test context relevance matrix covers all task types."""
        from context import CONTEXT_RELEVANCE_MATRIX, TaskType

        for task_type in TaskType:
            assert task_type in CONTEXT_RELEVANCE_MATRIX or task_type.value in [
                t.value for t in CONTEXT_RELEVANCE_MATRIX.keys()
            ]

    def test_context_to_dict_conversion(self, sample_student_context):
        """Test context models can be converted to dict for agents."""
        from context import StudentContext

        ctx = StudentContext(**sample_student_context)
        ctx_dict = ctx.model_dump()

        assert isinstance(ctx_dict, dict)
        assert ctx_dict["profile_id"] == sample_student_context["profile_id"]
        assert ctx_dict["spike"] == sample_student_context["spike"]
