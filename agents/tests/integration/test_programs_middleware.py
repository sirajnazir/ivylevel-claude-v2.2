"""
Integration tests for ProgramsAgent middleware integration.
Tests that ProgramsAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestProgramsAgentMiddlewareIntegration:
    """Verify ProgramsAgent middleware integration."""

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
        db.rpc = MagicMock(return_value=MagicMock(
            execute=MagicMock(return_value=MagicMock(data=1))
        ))
        return db

    @pytest.fixture
    def agent(self, mock_supabase):
        """Create agent with mocked dependencies."""
        with patch('agents.programs.get_supabase_client', return_value=mock_supabase):
            with patch('agents.programs.ChatOpenAI'):
                from agents.programs import ProgramsAgent
                agent = ProgramsAgent()
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
        with patch('agents.programs.get_supabase_client', return_value=None):
            with patch('agents.programs.ChatOpenAI'):
                from agents.programs import ProgramsAgent

                # Should not raise
                try:
                    agent = ProgramsAgent()
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
            "total_matches": 5,
            "top_recommendations": [{"name": "RSI"}],
            "archetype_used": "stem_innovator",
        }
        result = agent.middleware_finalize(original.copy(), "programs")

        assert result.get("success") == True
        assert result.get("total_matches") == 5
        assert result.get("archetype_used") == "stem_innovator"

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, agent):
        """Verify audit_action doesn't crash (compliance requirement)."""
        await agent.audit_action(
            action="programs_recommendation",
            resource_type="programs",
            resource_id="test-id",
            details={"total_matches": 5},
            success=True,
        )


class TestProgramsAgentProcessMethod:
    """Test the wrapped process method."""

    @pytest.fixture
    def agent(self):
        """Create agent with heavy mocking."""
        with patch('agents.programs.get_supabase_client') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('agents.programs.ChatOpenAI'):
                from agents.programs import ProgramsAgent
                agent = ProgramsAgent()

                # Mock the match method
                agent.match = AsyncMock(return_value={
                    "success": True,
                    "total_matches": 5,
                    "top_recommendations": [{"name": "RSI", "fit_score": 0.85}],
                    "advance_alerts": [{"name": "SSP", "days_until": 60}],
                    "synergy_recommendations": [],
                    "timeline": [],
                    "strategic_insights": [],
                    "archetype_used": "stem_innovator",
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
            identity_synthesis={"archetype": "stem_innovator", "spike": "AI"},
        )

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_with_route_config(self, agent):
        """Verify process handles route_config."""
        result = await agent.process(
            "test-profile-id",
            route_config={
                "be_prescriptive": True,
                "max_recommendations": 5,
            },
        )

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_preserves_match_count(self, agent):
        """Verify process preserves total_matches."""
        result = await agent.process("test-profile-id")

        assert result.get("total_matches") == 5

    @pytest.mark.asyncio
    async def test_process_preserves_archetype(self, agent):
        """Verify process preserves archetype_used."""
        result = await agent.process("test-profile-id")

        assert result.get("archetype_used") == "stem_innovator"


# Run with: pytest tests/integration/test_programs_middleware.py -v
