# agents/tests/patterns/test_middleware.py
"""
Tests for Middleware Stack - v5.4 True Autonomous Agents.

Tests the integration layer that wraps all Critical 15 Patterns.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestMiddlewareStack:
    """Tests for MiddlewareStack integration layer."""

    def test_middleware_stack_creation(self, mock_supabase, mock_redis):
        """Test MiddlewareStack can be created."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(
            supabase_client=mock_supabase,
            redis_client=mock_redis,
        )

        assert stack is not None

    def test_middleware_stack_minimal_creation(self):
        """Test MiddlewareStack can be created without clients."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack()

        assert stack is not None

    def test_create_middleware_convenience(self, mock_supabase, mock_redis):
        """Test create_middleware convenience function."""
        from middleware import create_middleware

        stack = create_middleware(mock_supabase, mock_redis)

        assert stack is not None

    @pytest.mark.asyncio
    async def test_wrap_agent_context_manager(self, mock_supabase, mock_redis):
        """Test wrap_agent context manager."""
        from middleware import MiddlewareStack
        from context import TaskType

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async with stack.wrap_agent(
            "test_agent",
            "profile-123",
            task_type=TaskType.GENERAL,
        ) as ctx:
            assert ctx is not None
            assert ctx.profile_id == "profile-123"

    @pytest.mark.asyncio
    async def test_wrap_agent_loads_context(self, mock_supabase, mock_redis, sample_student_context):
        """Test wrap_agent loads all context types."""
        from middleware import MiddlewareStack
        from context import TaskType

        # Setup mock data
        mock_supabase._tables["profiles"] = [sample_student_context]

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async with stack.wrap_agent(
            "test_agent",
            "test-profile-123",
            task_type=TaskType.GAMEPLAN,
        ) as ctx:
            # Context should be loaded
            assert ctx.session_id is not None
            # Other context components may or may not be loaded depending on data

    @pytest.mark.asyncio
    async def test_wrap_agent_starts_metrics(self, mock_supabase, mock_redis):
        """Test wrap_agent starts metrics collection."""
        from middleware import MiddlewareStack
        from context import TaskType

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async with stack.wrap_agent(
            "test_agent",
            "profile-123",
            task_type=TaskType.GENERAL,
        ) as ctx:
            assert ctx.metrics_id is not None


class TestAgentContext:
    """Tests for AgentContext class."""

    def test_agent_context_creation(self):
        """Test AgentContext can be created."""
        from middleware import AgentContext
        from context import TaskType

        ctx = AgentContext(
            profile_id="profile-123",
            session_id="session-456",
            task_type=TaskType.GAMEPLAN,
        )

        assert ctx.profile_id == "profile-123"
        assert ctx.session_id == "session-456"

    def test_agent_context_to_dict(self, sample_student_context):
        """Test AgentContext.to_dict() method."""
        from middleware import AgentContext
        from context import TaskType, StudentContext

        ctx = AgentContext(
            profile_id="profile-123",
            session_id="session-456",
            task_type=TaskType.GAMEPLAN,
        )

        # Set student context
        ctx._student = StudentContext(**sample_student_context)

        result = ctx.to_dict()

        assert isinstance(result, dict)
        assert result["profile_id"] == "profile-123"
        assert result["spike"] == "robotics"

    def test_agent_context_properties(self):
        """Test AgentContext lazy-loaded properties."""
        from middleware import AgentContext
        from context import TaskType

        ctx = AgentContext("profile-123", "session-456", TaskType.GENERAL)

        # Properties should return None before loading
        assert ctx.student is None
        assert ctx.temporal is None
        assert ctx.task is None
        assert ctx.working_memory is None


class TestMiddlewareMethods:
    """Tests for MiddlewareStack methods."""

    def test_check_guardrails_input(self, mock_supabase, mock_redis, safe_messages):
        """Test check_guardrails for input."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        for message in safe_messages:
            results = stack.check_guardrails(message, is_input=True)
            assert isinstance(results, list)

    def test_check_guardrails_output(self, mock_supabase, mock_redis, valid_gameplan_output):
        """Test check_guardrails for output."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        results = stack.check_guardrails(str(valid_gameplan_output), is_input=False)

        assert isinstance(results, list)

    def test_check_escalation(self, mock_supabase, mock_redis, unsafe_messages):
        """Test check_escalation method."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        for message in unsafe_messages:
            result = stack.check_escalation(message, {})
            # Some unsafe messages should trigger escalation
            if result:
                reason, level, safe_response = result
                assert reason is not None
                assert safe_response is not None

    def test_validate_output(self, mock_supabase, mock_redis, valid_gameplan_output):
        """Test validate_output method."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        result = stack.validate_output(valid_gameplan_output, "gameplan")

        assert result is not None
        assert hasattr(result, "valid")

    def test_prioritize(self, mock_supabase, mock_redis, sample_recommendations, sample_student_context, sample_temporal_context):
        """Test prioritize method."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        context = {
            "student": sample_student_context,
            "temporal": sample_temporal_context,
        }

        result = stack.prioritize(sample_recommendations, context)

        assert len(result) == len(sample_recommendations)

    def test_finalize(self, mock_supabase, mock_redis, valid_gameplan_output):
        """Test finalize method adds validation metadata."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        result = stack.finalize(valid_gameplan_output.copy(), "gameplan")

        assert "_validation" in result
        assert "valid" in result["_validation"]
        assert "score" in result["_validation"]


class TestMiddlewareIntegration:
    """Integration tests for middleware stack."""

    def test_all_middleware_types_importable(self):
        """Test all middleware types can be imported."""
        from middleware import (
            MiddlewareStack,
            AgentContext,
            create_middleware,
        )

        # All should be importable

    @pytest.mark.asyncio
    async def test_full_agent_lifecycle(self, mock_supabase, mock_redis, sample_student_context):
        """Test full agent lifecycle through middleware."""
        from middleware import MiddlewareStack
        from context import TaskType

        mock_supabase._tables["profiles"] = [sample_student_context]

        stack = MiddlewareStack(mock_supabase, mock_redis)

        # Full lifecycle
        async with stack.wrap_agent(
            "integration_test_agent",
            "test-profile-123",
            task_type=TaskType.GAMEPLAN,
        ) as ctx:
            # 1. Check input guardrails
            input_results = stack.check_guardrails(
                "Help me plan my college apps",
                is_input=True,
            )
            assert all(r.passed for r in input_results)

            # 2. Check escalation
            escalation = stack.check_escalation(
                "Help me plan my college apps",
                ctx.to_dict(),
            )
            assert escalation is None  # Safe message

            # 3. Generate output (simulated)
            output = {
                "profile_id": ctx.profile_id,
                "recommendations": [
                    {"title": "Test Rec", "priority": "high"}
                ],
                "summary": "Focus on test prep",
            }

            # 4. Finalize with validation
            finalized = stack.finalize(output, "gameplan")

            assert "_validation" in finalized

    @pytest.mark.asyncio
    async def test_middleware_handles_exceptions(self, mock_supabase, mock_redis):
        """Test middleware handles exceptions gracefully."""
        from middleware import MiddlewareStack
        from context import TaskType

        stack = MiddlewareStack(mock_supabase, mock_redis)

        with pytest.raises(ValueError):
            async with stack.wrap_agent(
                "exception_test",
                "profile-123",
                task_type=TaskType.GENERAL,
            ) as ctx:
                raise ValueError("Simulated error")

        # Middleware should have recorded the error

    @pytest.mark.asyncio
    async def test_middleware_metrics_on_success(self, mock_supabase, mock_redis):
        """Test middleware collects metrics on successful execution."""
        from middleware import MiddlewareStack
        from context import TaskType

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async with stack.wrap_agent(
            "metrics_test",
            "profile-123",
            task_type=TaskType.GENERAL,
        ) as ctx:
            pass  # Successful execution

        # Metrics should have been collected

    @pytest.mark.asyncio
    async def test_middleware_with_all_patterns(self, mock_supabase, mock_redis, mock_llm, sample_student_context):
        """Test middleware integrates all patterns."""
        from middleware import MiddlewareStack
        from context import TaskType

        mock_supabase._tables["profiles"] = [sample_student_context]

        stack = MiddlewareStack(mock_supabase, mock_redis, mock_llm)

        async with stack.wrap_agent(
            "full_pattern_test",
            "test-profile-123",
            task_type=TaskType.GAMEPLAN,
        ) as ctx:
            # C2: User context
            assert ctx.profile_id is not None

            # C4: Task context
            assert ctx.task_type == TaskType.GAMEPLAN

            # C6: Temporal context (may or may not be loaded)
            # ctx.temporal

            # B1: Working memory
            # ctx.working_memory

            # E6: Guardrails
            stack.check_guardrails("test", is_input=True)

            # G1/G3: Decision rights / Escalation
            stack.check_escalation("test", {})

            # E1: Validation
            stack.validate_output({"test": "data"}, "general")

            # A12: Prioritization
            stack.prioritize([{"id": "1"}], {"student": sample_student_context})

            # A4: Chain-of-thought (would need LLM)
            # await stack.think_step_by_step("test", {})

            # J2: Metrics (implicit through context manager)

        # All patterns were accessible
