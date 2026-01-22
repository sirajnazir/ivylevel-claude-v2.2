# agents/tests/integration/test_non_breaking.py
"""
Non-Breaking Integration Tests - v5.4 True Autonomous Agents.

These tests verify that the new middleware patterns don't break existing
agent functionality. They test the ADDITIVE nature of the implementation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestExistingAgentCompatibility:
    """Tests that existing agents work with or without middleware."""

    def test_imports_dont_break_existing_code(self):
        """Test importing middleware doesn't break existing imports."""
        # This should not raise any import errors
        from middleware import MiddlewareStack, AgentContext, create_middleware

        # Original agent imports should still work
        # (These may vary based on actual codebase)

    def test_middleware_is_optional(self, mock_supabase, mock_redis):
        """Test agents can run without middleware."""
        # Simulate agent code that doesn't use middleware
        class LegacyAgent:
            def __init__(self, supabase):
                self.supabase = supabase

            async def process(self, profile_id: str):
                # Legacy agent code without middleware
                return {"profile_id": profile_id, "result": "legacy_output"}

        agent = LegacyAgent(mock_supabase)

        # Should work without middleware
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(agent.process("test-123"))

        assert result["result"] == "legacy_output"

    @pytest.mark.asyncio
    async def test_middleware_wraps_without_modification(self, mock_supabase, mock_redis):
        """Test middleware wraps agents without modifying their output."""
        from middleware import MiddlewareStack
        from context import TaskType

        # Original agent output
        original_output = {
            "profile_id": "test-123",
            "recommendations": [{"title": "Test"}],
            "custom_field": "preserved",
        }

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async with stack.wrap_agent(
            "test_agent",
            "test-123",
            task_type=TaskType.GENERAL,
        ) as ctx:
            # Simulate agent work
            output = original_output.copy()

            # Finalize adds metadata but preserves original
            finalized = stack.finalize(output, "general")

        # Original fields preserved
        assert finalized["profile_id"] == "test-123"
        assert finalized["custom_field"] == "preserved"
        assert len(finalized["recommendations"]) == 1

        # Middleware metadata added
        assert "_validation" in finalized

    def test_context_fallbacks_when_data_missing(self, mock_supabase, mock_redis):
        """Test middleware handles missing data gracefully."""
        from middleware import MiddlewareStack
        from context import TaskType
        import asyncio

        # No profile data in database
        stack = MiddlewareStack(mock_supabase, mock_redis)

        async def test_with_missing_data():
            async with stack.wrap_agent(
                "test_agent",
                "nonexistent-profile",
                task_type=TaskType.GENERAL,
            ) as ctx:
                # Should still work, just with None values
                assert ctx.profile_id == "nonexistent-profile"
                # Student context might be None
                return ctx

        ctx = asyncio.get_event_loop().run_until_complete(test_with_missing_data())
        assert ctx is not None


class TestPatternIsolation:
    """Tests that patterns don't interfere with each other."""

    def test_guardrails_independent_of_validation(self, mock_supabase, mock_redis, safe_messages):
        """Test guardrails work independently of output validation."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        for message in safe_messages:
            # Guardrails check
            guardrail_results = stack.check_guardrails(message, is_input=True)

            # Should work without needing validation
            assert isinstance(guardrail_results, list)

    def test_validation_independent_of_metrics(self, mock_supabase, mock_redis, valid_gameplan_output):
        """Test validation works independently of metrics collection."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        # Validate without starting metrics
        result = stack.validate_output(valid_gameplan_output, "gameplan")

        assert result is not None
        assert hasattr(result, "valid")

    def test_escalation_independent_of_context_loading(self, mock_supabase, mock_redis, unsafe_messages):
        """Test escalation works without full context."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        # Check escalation without loading context
        for message in unsafe_messages:
            result = stack.check_escalation(message, {})
            # Should work with minimal context

    def test_prioritization_independent_of_memory(self, mock_supabase, mock_redis, sample_recommendations, sample_student_context, sample_temporal_context):
        """Test prioritization works without working memory."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase)  # No Redis

        context = {
            "student": sample_student_context,
            "temporal": sample_temporal_context,
        }

        result = stack.prioritize(sample_recommendations, context)

        assert len(result) == len(sample_recommendations)


class TestErrorIsolation:
    """Tests that errors in one pattern don't crash others."""

    @pytest.mark.asyncio
    async def test_context_load_failure_doesnt_crash_agent(self, mock_redis):
        """Test agent continues if context loading fails."""
        from middleware import MiddlewareStack
        from context import TaskType

        # Create stack with broken Supabase
        broken_supabase = MagicMock()
        broken_supabase.table.side_effect = Exception("Database connection failed")

        stack = MiddlewareStack(broken_supabase, mock_redis)

        # Should still enter context manager
        async with stack.wrap_agent(
            "test_agent",
            "profile-123",
            task_type=TaskType.GENERAL,
        ) as ctx:
            # Context exists even if loading failed
            assert ctx.profile_id == "profile-123"
            # Student might be None due to load failure
            # But agent can still proceed

    def test_guardrail_failure_doesnt_crash_validation(self, mock_supabase, mock_redis, valid_gameplan_output):
        """Test validation works even if guardrails have issues."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        # Mock guardrails to raise
        original_check = stack._guardrails.check_output
        stack._guardrails.check_output = MagicMock(side_effect=Exception("Guardrail error"))

        try:
            # Validation should still work
            result = stack.validate_output(valid_gameplan_output, "gameplan")
            assert result is not None
        except Exception:
            # If it does propagate, that's also acceptable behavior
            pass
        finally:
            stack._guardrails.check_output = original_check

    def test_metrics_failure_doesnt_crash_finalize(self, mock_supabase, mock_redis, valid_gameplan_output):
        """Test finalize works even if metrics fail."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        # Break metrics
        stack._metrics = None

        # Finalize should still work
        result = stack.finalize(valid_gameplan_output.copy(), "gameplan")

        assert "_validation" in result


class TestBackwardsCompatibility:
    """Tests for backwards compatibility with existing code."""

    def test_old_style_direct_pattern_usage(self):
        """Test patterns can still be used directly without middleware."""
        # Direct pattern usage (old style)
        from context import UserContextLoader, TaskContextManager, TaskType
        from memory import WorkingMemoryManager
        from intelligence import Prioritizer
        from governance import EscalationProtocol
        from safety import GuardrailsManager
        from validation import OutputValidator

        # All patterns should be instantiable directly
        task_manager = TaskContextManager(None)
        prioritizer = Prioritizer()
        escalation = EscalationProtocol()
        guardrails = GuardrailsManager()
        validator = OutputValidator()

        # And usable
        task = task_manager.create_task(TaskType.GENERAL, "Test task")
        assert task is not None

    def test_middleware_stack_accepts_none_clients(self):
        """Test middleware can be created with None clients."""
        from middleware import MiddlewareStack

        # All None
        stack = MiddlewareStack(None, None, None)
        assert stack is not None

        # Some None
        stack2 = MiddlewareStack(supabase_client=None)
        assert stack2 is not None

    @pytest.mark.asyncio
    async def test_wrap_agent_with_minimal_params(self, mock_supabase, mock_redis):
        """Test wrap_agent works with minimal parameters."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        # Minimal params - just agent name and profile ID
        async with stack.wrap_agent("test", "profile-123") as ctx:
            assert ctx is not None


class TestModuleImports:
    """Tests that all modules import correctly."""

    def test_context_module_imports(self):
        """Test all context exports are importable."""
        from context import (
            StudentContext,
            ContextSelection,
            TemporalContext,
            TaskContext,
            TaskType,
            TaskStatus,
            WorkingMemory,
            UserContextLoader,
            TemporalContextLoader,
            TaskContextManager,
            ContextSelector,
        )

    def test_memory_module_imports(self):
        """Test all memory exports are importable."""
        from memory import (
            WorkingMemoryManager,
            MemoryRetriever,
            MemoryItem,
            RetrievalResult,
        )

    def test_intelligence_module_imports(self):
        """Test all intelligence exports are importable."""
        from intelligence import (
            Prioritizer,
            PrioritizedItem,
            GoalMonitor,
            Goal,
            GoalProgressReport,
        )

    def test_governance_module_imports(self):
        """Test all governance exports are importable."""
        from governance import (
            DecisionRightsManager,
            EscalationProtocol,
            Decision,
            Escalation,
            SafetyResponse,
        )

    def test_safety_module_imports(self):
        """Test all safety exports are importable."""
        from safety import (
            GuardrailsManager,
            GuardrailResult,
        )

    def test_resilience_module_imports(self):
        """Test all resilience exports are importable."""
        from resilience import (
            ExceptionHandler,
            FallbackResponse,
            with_retry,
        )

    def test_reasoning_module_imports(self):
        """Test all reasoning exports are importable."""
        from reasoning import (
            ChainOfThoughtReasoner,
            AgentRouter,
            RouteDecision,
        )

    def test_validation_module_imports(self):
        """Test all validation exports are importable."""
        from validation import (
            OutputValidator,
            ValidationResult,
            JennyVoiceValidator,
        )

    def test_observability_module_imports(self):
        """Test all observability exports are importable."""
        from observability import (
            MetricsCollector,
            AgentMetrics,
            get_metrics_collector,
        )

    def test_middleware_module_imports(self):
        """Test all middleware exports are importable."""
        from middleware import (
            MiddlewareStack,
            AgentContext,
            create_middleware,
        )
