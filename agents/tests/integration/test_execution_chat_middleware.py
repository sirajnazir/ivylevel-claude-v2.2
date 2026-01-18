"""
Integration tests for ExecutionChatAgent middleware integration.
Tests that ExecutionChatAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestExecutionChatAgentMiddlewareIntegration:
    """Verify ExecutionChatAgent middleware integration."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    order=MagicMock(return_value=MagicMock(
                        limit=MagicMock(return_value=MagicMock(
                            execute=MagicMock(return_value=MagicMock(data=[]))
                        ))
                    ))
                ))
            )),
            insert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
            ))
        ))
        return db

    @pytest.fixture
    def agent(self):
        """Create agent with mocked dependencies."""
        with patch('agents.execution_chat.settings'):
            from agents.execution_chat import ExecutionChatAgent
            agent = ExecutionChatAgent()
            return agent

    def test_has_mixin_inheritance(self, agent):
        """Verify agent inherits from MiddlewareIntegrationMixin."""
        from agents.mixins import MiddlewareIntegrationMixin
        assert isinstance(agent, MiddlewareIntegrationMixin)

    def test_middleware_initialized(self, agent):
        """Verify middleware attribute exists after init."""
        assert hasattr(agent, 'middleware')

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

        # All should be callable
        assert callable(agent.init_middleware)
        assert callable(agent.start_reasoning_trace)

    def test_graceful_degradation(self):
        """Verify agent works even if middleware fails."""
        with patch('agents.execution_chat.settings'):
            from agents.execution_chat import ExecutionChatAgent

            # Should not raise
            try:
                agent = ExecutionChatAgent()
            except Exception as e:
                pytest.fail(f"Agent init should not raise: {e}")

            assert hasattr(agent, 'middleware')
            assert hasattr(agent, 'init_middleware')

    def test_trace_methods_safe_when_no_middleware(self, agent):
        """Verify trace methods don't crash when middleware unavailable."""
        agent._middleware = None

        trace_id = agent.start_reasoning_trace("test", "test", "test")
        assert trace_id is None

        agent.add_thought(None, "Test thought")
        agent.add_action(None, "Test action")

    @pytest.mark.asyncio
    async def test_end_trace_safe(self, agent):
        """Verify async trace methods don't crash."""
        agent._middleware = None
        await agent.end_reasoning_trace(None, success=True)

    def test_finalize_preserves_data(self, agent):
        """Verify middleware_finalize doesn't lose data."""
        original = {
            "success": True,
            "response": "Test response from chat agent",
        }
        result = agent.middleware_finalize(original.copy(), "execution_chat")

        assert result.get("success") == True
        assert result.get("response") == "Test response from chat agent"

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, agent):
        """Verify audit_action doesn't crash."""
        await agent.audit_action(
            action="execution_chat",
            resource_type="chat",
            resource_id="test-id",
            details={"context_type": "project"},
            success=True,
        )


class TestExecutionChatAgentChatSyncMethod:
    """Test the wrapped chat_sync method."""

    @pytest.fixture
    def agent(self):
        """Create agent with heavy mocking."""
        with patch('agents.execution_chat.settings'):
            from agents.execution_chat import ExecutionChatAgent
            agent = ExecutionChatAgent()

            # Mock the chat method to return a simple generator
            async def mock_chat(*args, **kwargs):
                yield {"type": "content", "content": "Hello "}
                yield {"type": "content", "content": "World!"}
                yield {"type": "done", "full_response": "Hello World!"}

            agent.chat = mock_chat

            return agent

    @pytest.mark.asyncio
    async def test_chat_sync_returns_result(self, agent):
        """Verify chat_sync still returns results."""
        result = await agent.chat_sync("test-profile-id", "Hello")

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_chat_sync_preserves_response(self, agent):
        """Verify chat_sync preserves response."""
        result = await agent.chat_sync("test-profile-id", "Hello")

        assert result.get("response") == "Hello World!"

    @pytest.mark.asyncio
    async def test_chat_sync_with_context(self, agent):
        """Verify chat_sync handles context parameters."""
        result = await agent.chat_sync(
            "test-profile-id",
            "What's my status?",
            context_type="project",
            context_id="proj-123",
        )

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_chat_sync_handles_error(self, agent):
        """Verify chat_sync handles errors from chat."""
        async def mock_chat_error(*args, **kwargs):
            yield {"type": "error", "error": "Test error"}

        agent.chat = mock_chat_error

        result = await agent.chat_sync("test-profile-id", "Hello")

        assert result.get("success") == False
        assert "error" in result


# Run with: pytest tests/integration/test_execution_chat_middleware.py -v
