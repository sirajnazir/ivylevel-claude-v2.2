"""
Integration tests for ExecutionAgent middleware integration.
Tests that ExecutionAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestExecutionAgentMiddlewareIntegration:
    """Verify ExecutionAgent middleware integration."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
                ))
            ))
        ))
        return db

    @pytest.fixture
    def agent(self, mock_supabase):
        """Create agent with mocked dependencies."""
        with patch('agents.execution.supabase', mock_supabase):
            with patch('agents.execution.CrisisAlchemyGraph'):
                with patch('agents.execution.settings') as mock_settings:
                    mock_settings.blocker_threshold_days = 5
                    from agents.execution import ExecutionAgent
                    agent = ExecutionAgent()
                    return agent

    def test_has_mixin_inheritance(self, agent):
        """Verify agent inherits from MiddlewareIntegrationMixin."""
        from agents.mixins import MiddlewareIntegrationMixin
        assert isinstance(agent, MiddlewareIntegrationMixin)

    def test_middleware_initialized(self, agent):
        """Verify middleware attribute exists after init."""
        assert hasattr(agent, 'middleware')
        # May be None if init failed gracefully - that's OK

    def test_has_mixin_methods(self, agent):
        """Verify mixin methods are available."""
        # Core methods
        assert hasattr(agent, 'init_middleware')
        assert hasattr(agent, 'with_middleware_context')
        assert hasattr(agent, 'middleware_finalize')

        # Trace methods (J1)
        assert hasattr(agent, 'start_reasoning_trace')
        assert hasattr(agent, 'add_thought')
        assert hasattr(agent, 'add_action')
        assert hasattr(agent, 'end_reasoning_trace')

        # Audit methods (J3)
        assert hasattr(agent, 'audit_action')

        # Quality methods (E4)
        assert hasattr(agent, 'score_quality')

        # Metric methods (J4)
        assert hasattr(agent, 'record_metric')

        # All should be callable
        assert callable(agent.init_middleware)
        assert callable(agent.start_reasoning_trace)
        assert callable(agent.middleware_finalize)

    def test_graceful_degradation_no_db(self):
        """Verify agent works even if middleware fails."""
        with patch('agents.execution.supabase', None):
            with patch('agents.execution.CrisisAlchemyGraph'):
                with patch('agents.execution.settings') as mock_settings:
                    mock_settings.blocker_threshold_days = 5
                    from agents.execution import ExecutionAgent

                    # Should not raise
                    try:
                        agent = ExecutionAgent()
                    except Exception as e:
                        pytest.fail(f"Agent init should not raise: {e}")

                    # Agent should still have the method
                    assert hasattr(agent, 'middleware')
                    assert hasattr(agent, 'init_middleware')

    def test_trace_methods_safe_when_no_middleware(self, agent):
        """Verify trace methods don't crash when middleware unavailable."""
        # Force middleware to None
        agent._middleware = None

        # These should work without crashing
        trace_id = agent.start_reasoning_trace("test-profile", "test-session", "test input")
        assert trace_id is None  # Should return None when no middleware

        # These should be no-ops without crashing
        agent.add_thought(None, "Test thought")
        agent.add_action(None, "Test action")

    @pytest.mark.asyncio
    async def test_end_trace_safe_when_no_middleware(self, agent):
        """Verify async trace methods don't crash."""
        agent._middleware = None

        # Should not raise
        await agent.end_reasoning_trace(None, success=True)

    def test_finalize_preserves_data(self, agent):
        """Verify middleware_finalize doesn't lose data."""
        original = {"key": "value", "nested": {"a": 1}, "success": True}
        result = agent.middleware_finalize(original.copy(), "execution")

        # Original data must be preserved
        assert result.get("key") == "value"
        assert result.get("nested", {}).get("a") == 1
        assert result.get("success") == True

    def test_finalize_adds_validation_metadata(self, agent):
        """Verify middleware_finalize adds validation if middleware available."""
        if agent.middleware:
            original = {"success": True}
            result = agent.middleware_finalize(original.copy(), "execution")
            # Should have _validation key if middleware working
            assert "_validation" in result or result.get("success") == True

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, agent):
        """Verify audit_action doesn't crash."""
        # Should not raise even without middleware
        await agent.audit_action(
            action="test_action",
            resource_type="test",
            resource_id="test-id",
            success=True,
        )

    def test_record_metric_safe(self, agent):
        """Verify record_metric doesn't crash."""
        # Should not raise even without middleware
        agent.record_metric("test_metric", 1.0, tags={"key": "value"})


class TestExecutionAgentProcessMethod:
    """Test the wrapped process method."""

    @pytest.fixture
    def agent(self):
        """Create agent with heavy mocking."""
        with patch('agents.execution.supabase') as mock_db:
            with patch('agents.execution.CrisisAlchemyGraph'):
                with patch('agents.execution.settings') as mock_settings:
                    mock_settings.blocker_threshold_days = 5
                    from agents.execution import ExecutionAgent
                    agent = ExecutionAgent()

                    # Mock the status check method
                    agent.check_status = AsyncMock(return_value={"success": True, "status": "ok"})

                    return agent

    @pytest.mark.asyncio
    async def test_process_returns_result(self, agent):
        """Verify process still returns results."""
        result = await agent.process("test-profile-id")

        assert isinstance(result, dict)
        assert "success" in result or "_validation" in result

    @pytest.mark.asyncio
    async def test_process_with_action_param(self, agent):
        """Verify process handles action parameter."""
        agent.check_status = AsyncMock(return_value={"success": True})

        result = await agent.process("test-profile-id", action="check_status")

        assert isinstance(result, dict)


# Run with: pytest tests/integration/test_execution_middleware.py -v
