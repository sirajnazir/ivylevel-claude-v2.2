"""
Integration tests for AssessmentAgent middleware integration.
Tests that AssessmentAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestAssessmentAgentMiddlewareIntegration:
    """Verify AssessmentAgent middleware integration."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
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
        db.rpc = MagicMock(return_value=MagicMock(
            execute=MagicMock(return_value=MagicMock(data=1))
        ))
        return db

    @pytest.fixture
    def agent(self, mock_supabase):
        """Create agent with mocked dependencies."""
        with patch('agents.assessment.get_supabase_client', return_value=mock_supabase):
            with patch('agents.assessment.ChatOpenAI'):
                from agents.assessment import AssessmentAgent
                agent = AssessmentAgent()
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
        with patch('agents.assessment.get_supabase_client', return_value=None):
            with patch('agents.assessment.ChatOpenAI'):
                from agents.assessment import AssessmentAgent

                # Should not raise
                try:
                    agent = AssessmentAgent()
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
            "narrative_dna": {"dna": "Test narrative DNA"},
            "archetype": {"id": "academic-achiever", "label": "Academic Achiever"},
            "cri": 1.2,
            "requires_handoff": False,
        }
        result = agent.middleware_finalize(original.copy(), "assessment")

        assert result.get("success") == True
        assert result.get("cri") == 1.2
        assert result.get("requires_handoff") == False

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, agent):
        """Verify audit_action doesn't crash (MANDATORY for assessment data)."""
        await agent.audit_action(
            action="assessment_enhancement",
            resource_type="assessment",
            resource_id="test-id",
            details={"archetype": "academic-achiever"},
            success=True,
        )


class TestAssessmentAgentProcessMethod:
    """Test the wrapped process method."""

    @pytest.fixture
    def agent(self):
        """Create agent with heavy mocking."""
        with patch('agents.assessment.get_supabase_client') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('agents.assessment.ChatOpenAI'):
                from agents.assessment import AssessmentAgent
                agent = AssessmentAgent()

                # Mock the enhance method
                agent.enhance = AsyncMock(return_value={
                    "success": True,
                    "narrative_dna": {
                        "dna": "Test narrative DNA",
                        "themes": ["stem", "innovation"],
                        "confidence": 0.85
                    },
                    "archetype": {
                        "id": "academic-achiever",
                        "label": "Academic Achiever",
                        "confidence": 0.8
                    },
                    "cri": 1.2,
                    "hidden_target": "MIT",
                    "constraint_reframes": [],
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
    async def test_process_with_data(self, agent):
        """Verify process handles additional data."""
        result = await agent.process(
            "test-profile-id",
            data={"intended_major": "Computer Science"},
        )

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_preserves_narrative_dna(self, agent):
        """Verify process preserves narrative_dna."""
        result = await agent.process("test-profile-id")

        assert result.get("narrative_dna") is not None
        assert result.get("narrative_dna", {}).get("dna") == "Test narrative DNA"

    @pytest.mark.asyncio
    async def test_process_preserves_archetype(self, agent):
        """Verify process preserves archetype."""
        result = await agent.process("test-profile-id")

        assert result.get("archetype") is not None
        assert result.get("archetype", {}).get("id") == "academic-achiever"

    @pytest.mark.asyncio
    async def test_process_preserves_cri(self, agent):
        """Verify process preserves CRI score."""
        result = await agent.process("test-profile-id")

        assert result.get("cri") == 1.2


# Run with: pytest tests/integration/test_assessment_middleware.py -v
