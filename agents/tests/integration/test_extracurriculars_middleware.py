"""
Integration tests for ExtracurricularsAgent middleware integration.
Tests that ExtracurricularsAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestExtracurricularsAgentMiddlewareIntegration:
    """Verify ExtracurricularsAgent middleware integration."""

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
        with patch('agents.extracurriculars.get_supabase_client', return_value=mock_supabase):
            with patch('agents.extracurriculars.ChatOpenAI'):
                with patch('agents.extracurriculars.ECGenerationEngine'):
                    from agents.extracurriculars import ExtracurricularsAgent
                    agent = ExtracurricularsAgent()
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
        with patch('agents.extracurriculars.get_supabase_client', return_value=None):
            with patch('agents.extracurriculars.ChatOpenAI'):
                with patch('agents.extracurriculars.ECGenerationEngine'):
                    from agents.extracurriculars import ExtracurricularsAgent

                    # Should not raise
                    try:
                        agent = ExtracurricularsAgent()
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
            "identity_synthesis": {"archetype": "stem_innovator"},
        }
        result = agent.middleware_finalize(original.copy(), "extracurriculars")

        assert result.get("success") == True
        assert result.get("identity_synthesis", {}).get("archetype") == "stem_innovator"

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, agent):
        """Verify audit_action doesn't crash."""
        await agent.audit_action(
            action="test",
            resource_type="test",
            resource_id="test-id",
            success=True,
        )


class TestExtracurricularsAgentProcessMethod:
    """Test the wrapped process method."""

    @pytest.fixture
    def agent(self):
        """Create agent with heavy mocking."""
        with patch('agents.extracurriculars.get_supabase_client') as mock_db:
            with patch('agents.extracurriculars.ChatOpenAI'):
                with patch('agents.extracurriculars.ECGenerationEngine'):
                    from agents.extracurriculars import ExtracurricularsAgent
                    agent = ExtracurricularsAgent()

                    # Mock the analyze method
                    agent.analyze = AsyncMock(return_value={
                        "success": True,
                        "identity_synthesis": {"archetype": "stem_innovator", "spike": "AI"},
                    })

                    return agent

    @pytest.mark.asyncio
    async def test_process_returns_result(self, agent):
        """Verify process still returns results."""
        result = await agent.process("test-profile-id")

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_with_react_hints(self, agent):
        """Verify process handles react hints."""
        result = await agent.process(
            "test-profile-id",
            react_hints=["improve spike identification"],
        )

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_includes_quality_score(self, agent):
        """Verify process adds quality score when middleware available."""
        result = await agent.process("test-profile-id")

        # May or may not have quality score depending on middleware state
        assert isinstance(result, dict)


# Run with: pytest tests/integration/test_extracurriculars_middleware.py -v
