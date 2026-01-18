"""
Integration tests for NarrativeSynthesisAgent middleware integration.
Tests that NarrativeSynthesisAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestNarrativeSynthesisAgentMiddlewareIntegration:
    """Verify NarrativeSynthesisAgent middleware integration."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    single=MagicMock(return_value=MagicMock(
                        execute=MagicMock(return_value=MagicMock(data=None))
                    )),
                    order=MagicMock(return_value=MagicMock(
                        limit=MagicMock(return_value=MagicMock(
                            execute=MagicMock(return_value=MagicMock(data=[]))
                        ))
                    ))
                ))
            )),
            update=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
                ))
            )),
            insert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[]))
            ))
        ))
        return db

    @pytest.fixture
    def agent(self, mock_supabase):
        """Create agent with mocked dependencies."""
        with patch('agents.narrative_synthesis.get_supabase_client', return_value=mock_supabase):
            with patch('agents.narrative_synthesis.ChatOpenAI'):
                with patch('agents.narrative_synthesis.USE_GEMINI', False):
                    from agents.narrative_synthesis import NarrativeSynthesisAgent
                    agent = NarrativeSynthesisAgent()
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
        with patch('agents.narrative_synthesis.get_supabase_client', return_value=None):
            with patch('agents.narrative_synthesis.ChatOpenAI'):
                with patch('agents.narrative_synthesis.USE_GEMINI', False):
                    from agents.narrative_synthesis import NarrativeSynthesisAgent

                    # Should not raise
                    try:
                        agent = NarrativeSynthesisAgent()
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
            "brand_statement": "Test brand statement",
            "narrative_dna": "Test narrative DNA",
            "first_principle": "Test first principle",
            "themes": ["theme1", "theme2"],
            "confidence": 0.85,
        }
        result = agent.middleware_finalize(original.copy(), "narrative_synthesis")

        assert result.get("success") == True
        assert result.get("brand_statement") == "Test brand statement"
        assert result.get("confidence") == 0.85

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, agent):
        """Verify audit_action doesn't crash."""
        await agent.audit_action(
            action="narrative_synthesis",
            resource_type="narrative",
            resource_id="test-id",
            details={"confidence": 0.85},
            success=True,
        )


class TestNarrativeSynthesisAgentProcessMethod:
    """Test the wrapped process method."""

    @pytest.fixture
    def agent(self):
        """Create agent with heavy mocking."""
        with patch('agents.narrative_synthesis.get_supabase_client') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('agents.narrative_synthesis.ChatOpenAI'):
                with patch('agents.narrative_synthesis.USE_GEMINI', False):
                    from agents.narrative_synthesis import NarrativeSynthesisAgent
                    agent = NarrativeSynthesisAgent()

                    # Mock the synthesize method
                    agent.synthesize = AsyncMock(return_value={
                        "success": True,
                        "brand_statement": "A passionate builder creating tech for good",
                        "narrative_dna": "This student combines technical skill with social impact...",
                        "first_principle": "Technology should serve humanity",
                        "themes": ["innovation", "impact", "community"],
                        "confidence": 0.85,
                        "requires_handoff": False,
                    })

                    return agent

    @pytest.mark.asyncio
    async def test_process_returns_result(self, agent):
        """Verify process still returns results."""
        result = await agent.process("test-profile-id")

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_with_assessment_contract(self, agent):
        """Verify process handles assessment contract."""
        result = await agent.process(
            "test-profile-id",
            assessment_contract={
                "scores": {"identity": 0.8, "aptitude": 0.75},
                "archetype": {"id": "academic-achiever"}
            },
        )

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_preserves_brand_statement(self, agent):
        """Verify process preserves brand_statement."""
        result = await agent.process("test-profile-id")

        assert result.get("brand_statement") == "A passionate builder creating tech for good"

    @pytest.mark.asyncio
    async def test_process_preserves_narrative_dna(self, agent):
        """Verify process preserves narrative_dna."""
        result = await agent.process("test-profile-id")

        assert "technical skill" in result.get("narrative_dna", "")

    @pytest.mark.asyncio
    async def test_process_preserves_themes(self, agent):
        """Verify process preserves themes."""
        result = await agent.process("test-profile-id")

        themes = result.get("themes", [])
        assert "innovation" in themes
        assert "impact" in themes


# Run with: pytest tests/integration/test_narrative_synthesis_middleware.py -v
