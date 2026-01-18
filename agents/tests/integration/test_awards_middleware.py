"""
Integration tests for AwardsAgent middleware integration.
Tests that AwardsAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAwardsAgentMiddlewareIntegration:
    """Verify AwardsAgent middleware integration."""

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
        with patch('agents.awards.get_supabase_client', return_value=mock_supabase):
            with patch('agents.awards.ChatOpenAI'):
                from agents.awards import AwardsAgent
                agent = AwardsAgent()
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
        assert hasattr(agent, 'init_middleware')
        assert hasattr(agent, 'with_middleware_context')
        assert hasattr(agent, 'middleware_finalize')
        assert hasattr(agent, 'start_reasoning_trace')
        assert hasattr(agent, 'audit_action')
        assert hasattr(agent, 'score_quality')
        assert callable(agent.init_middleware)

    def test_graceful_degradation(self):
        """Verify agent works even if middleware fails."""
        with patch('agents.awards.get_supabase_client', return_value=None):
            with patch('agents.awards.ChatOpenAI'):
                from agents.awards import AwardsAgent
                try:
                    agent = AwardsAgent()
                except Exception as e:
                    pytest.fail(f"Agent init should not raise: {e}")
                assert hasattr(agent, 'middleware')

    def test_trace_methods_safe_when_no_middleware(self, agent):
        """Verify trace methods don't crash when middleware unavailable."""
        agent._middleware = None
        trace_id = agent.start_reasoning_trace("test", "test", "test")
        assert trace_id is None
        agent.add_thought(None, "Test thought")
        agent.add_action(None, "Test action")

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, agent):
        """Verify audit_action doesn't crash (compliance requirement)."""
        await agent.audit_action(
            action="award_recommendation",
            resource_type="awards",
            resource_id="test-id",
            details={"total_matches": 5},
            success=True,
        )

    def test_finalize_preserves_data(self, agent):
        """Verify middleware_finalize doesn't lose data."""
        original = {
            "success": True,
            "portfolio": {"reach": [], "target": [], "safety": []},
            "total_matches": 5,
        }
        result = agent.middleware_finalize(original.copy(), "awards")
        assert result.get("success") == True
        assert result.get("total_matches") == 5


class TestAwardsAgentProcessMethod:
    """Test the wrapped process method."""

    @pytest.fixture
    def agent(self):
        """Create agent with heavy mocking."""
        with patch('agents.awards.get_supabase_client') as mock_db:
            with patch('agents.awards.ChatOpenAI'):
                from agents.awards import AwardsAgent
                agent = AwardsAgent()

                # Mock the match method
                agent.match = AsyncMock(return_value={
                    "success": True,
                    "portfolio": {"reach": [], "target": [], "safety": []},
                    "total_matches": 5,
                })

                return agent

    @pytest.mark.asyncio
    async def test_process_returns_result(self, agent):
        """Verify process still returns results."""
        result = await agent.process("test-profile-id")
        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_with_identity_synthesis(self, agent):
        """Verify process handles identity synthesis."""
        result = await agent.process(
            "test-profile-id",
            identity_synthesis={"archetype": "stem_innovator"},
        )
        assert isinstance(result, dict)
        assert result.get("success") == True


# Run with: pytest tests/integration/test_awards_middleware.py -v
