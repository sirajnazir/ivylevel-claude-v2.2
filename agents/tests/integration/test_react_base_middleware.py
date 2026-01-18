"""
Integration tests for ReActAgent base class middleware integration.
Tests that ReActAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any, List
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestReActAgentMiddlewareIntegration:
    """Verify ReActAgent middleware integration via mock implementation."""

    @pytest.fixture
    def mock_memory(self):
        """Mock MemoryManager."""
        memory = MagicMock()
        memory.supabase = MagicMock()
        memory.get_working_buffer = MagicMock(return_value=MagicMock(
            record_evaluation=MagicMock(),
            record_successful_strategy=MagicMock(),
        ))
        memory.clear_working_buffer = MagicMock()
        memory.store_observation = AsyncMock()
        return memory

    @pytest.fixture
    def mock_voice_validator(self):
        """Mock JennyVoiceValidator."""
        validator = MagicMock()
        validator.validate = AsyncMock(return_value=(True, MagicMock(total=85.0), []))
        validator.validate_and_transform = AsyncMock(side_effect=lambda x: x)
        return validator

    @pytest.fixture
    def mixin_agent(self, mock_memory, mock_voice_validator):
        """Create a concrete implementation of ReActAgent with mixin."""
        from agents.mixins import MiddlewareIntegrationMixin

        class TestInput(BaseModel):
            profile_id: str
            data: Dict[str, Any] = {}

        class MockReActAgent(MiddlewareIntegrationMixin):
            """Mock ReAct agent for testing mixin integration."""

            def __init__(self):
                self.agent_id = "test_react"
                self.name = "TestReAct"
                self.description = "Test ReAct agent"
                self.memory = mock_memory
                self.voice = mock_voice_validator
                self.current_cycles = []
                self.best_result = None
                self.best_score = 0.0

                # Initialize mixin
                self.init_middleware(
                    supabase_client=mock_memory.supabase,
                    llm_client=MagicMock(),
                )

        return MockReActAgent()

    def test_has_mixin_inheritance(self, mixin_agent):
        """Verify agent inherits from MiddlewareIntegrationMixin."""
        from agents.mixins import MiddlewareIntegrationMixin
        assert isinstance(mixin_agent, MiddlewareIntegrationMixin)

    def test_middleware_initialized(self, mixin_agent):
        """Verify middleware attribute exists after init."""
        assert hasattr(mixin_agent, '_middleware') or hasattr(mixin_agent, 'middleware')

    def test_has_mixin_methods(self, mixin_agent):
        """Verify mixin methods are available."""
        # Core methods
        assert hasattr(mixin_agent, 'init_middleware')
        assert hasattr(mixin_agent, 'with_middleware_context')
        assert hasattr(mixin_agent, 'middleware_finalize')

        # Trace methods (J1)
        assert hasattr(mixin_agent, 'start_reasoning_trace')
        assert hasattr(mixin_agent, 'add_thought')
        assert hasattr(mixin_agent, 'add_action')
        assert hasattr(mixin_agent, 'end_reasoning_trace')

        # Audit methods (J3)
        assert hasattr(mixin_agent, 'audit_action')

        # Quality methods (E4)
        assert hasattr(mixin_agent, 'score_quality')

        # All should be callable
        assert callable(mixin_agent.init_middleware)
        assert callable(mixin_agent.start_reasoning_trace)

    def test_trace_methods_safe_when_no_middleware(self, mixin_agent):
        """Verify trace methods don't crash when middleware unavailable."""
        mixin_agent._middleware = None

        trace_id = mixin_agent.start_reasoning_trace("test", "test", "test")
        assert trace_id is None

        mixin_agent.add_thought(None, "Test thought")
        mixin_agent.add_action(None, "Test action")

    @pytest.mark.asyncio
    async def test_end_trace_safe(self, mixin_agent):
        """Verify async trace methods don't crash."""
        mixin_agent._middleware = None
        await mixin_agent.end_reasoning_trace(None, success=True)

    def test_finalize_preserves_data(self, mixin_agent):
        """Verify middleware_finalize doesn't lose data."""
        original = {
            "success": True,
            "result": {"narrative": "Test narrative"},
            "quality_score": 85.0,
            "cycles_used": 2,
            "passes_thresholds": True,
            "react_trace": [],
            "_metadata": {"agent_id": "test"},
        }
        result = mixin_agent.middleware_finalize(original.copy(), "react_test")

        assert result.get("success") == True
        assert result.get("quality_score") == 85.0
        assert result.get("cycles_used") == 2

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, mixin_agent):
        """Verify audit_action doesn't crash (MANDATORY for ReAct decisions)."""
        await mixin_agent.audit_action(
            action="react_loop_complete",
            resource_type="react_agent",
            resource_id="test-profile",
            details={"cycles_used": 2, "final_score": 85.0},
            success=True,
        )


class TestReActAgentRunMethodIntegration:
    """Test the run method integration - simulated."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent simulating ReActAgent with mixin."""
        from agents.mixins import MiddlewareIntegrationMixin

        class MockReActRunAgent(MiddlewareIntegrationMixin):
            """Mock agent class for testing run integration."""

            def __init__(self):
                self.agent_id = "test_react_run"
                self.name = "TestReActRun"
                self.best_score = 0.0
                self.best_result = None
                self.current_cycles = []
                self.init_middleware(
                    supabase_client=MagicMock(),
                    llm_client=MagicMock(),
                )

            async def run(self, context, input_data):
                """Simulated run method with middleware wrapping."""
                session_id = f"react_{self.agent_id}_{context.profile_id}"
                trace_id = self.start_reasoning_trace(
                    context.profile_id, session_id, f"react_loop_{self.agent_id}"
                )

                try:
                    async with self.with_middleware_context(
                        context.profile_id, session_id, f"react_{self.agent_id}"
                    ) as mw_ctx:
                        self.add_thought(trace_id, f"Starting ReAct loop for {self.name}")

                        # Simulate ReAct cycle
                        self.best_score = 85.0
                        self.best_result = {"narrative": "Generated narrative"}
                        self.current_cycles = [{"cycle": 1}, {"cycle": 2}]

                        self.add_action(trace_id, "cycle_1", {"phase": "complete"})
                        self.add_action(trace_id, "cycle_2", {"phase": "complete"})

                        result = {
                            "success": True,
                            "result": self.best_result,
                            "quality_score": self.best_score,
                            "cycles_used": len(self.current_cycles),
                            "passes_thresholds": True,
                            "react_trace": self.current_cycles,
                            "_metadata": {
                                "agent_id": self.agent_id,
                                "agent_name": self.name,
                                "profile_id": context.profile_id,
                            },
                        }

                        result = self.middleware_finalize(result, output_type=f"react_{self.agent_id}")

                        await self.audit_action(
                            action="react_loop_complete",
                            resource_type="react_agent",
                            resource_id=context.profile_id,
                            details={
                                "cycles_used": len(self.current_cycles),
                                "final_score": self.best_score,
                            },
                            success=True,
                        )

                        await self.end_reasoning_trace(trace_id, success=True)
                        return result

                except Exception as e:
                    await self.end_reasoning_trace(trace_id, success=False, error=str(e))
                    raise

        return MockReActRunAgent()

    @pytest.fixture
    def mock_context(self):
        """Create mock RunContext."""
        context = MagicMock()
        context.profile_id = "test-profile-id"
        context.session_id = "test-session-id"
        context.archetype = "academic-achiever"
        return context

    @pytest.mark.asyncio
    async def test_run_returns_result(self, mock_agent, mock_context):
        """Verify run still returns results."""
        result = await mock_agent.run(mock_context, MagicMock())

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_run_preserves_quality_score(self, mock_agent, mock_context):
        """Verify run preserves quality_score."""
        result = await mock_agent.run(mock_context, MagicMock())

        assert result.get("quality_score") == 85.0

    @pytest.mark.asyncio
    async def test_run_preserves_cycles_used(self, mock_agent, mock_context):
        """Verify run preserves cycles_used."""
        result = await mock_agent.run(mock_context, MagicMock())

        assert result.get("cycles_used") == 2

    @pytest.mark.asyncio
    async def test_run_preserves_react_trace(self, mock_agent, mock_context):
        """Verify run preserves react_trace."""
        result = await mock_agent.run(mock_context, MagicMock())

        assert "react_trace" in result
        assert len(result.get("react_trace", [])) == 2

    @pytest.mark.asyncio
    async def test_run_preserves_metadata(self, mock_agent, mock_context):
        """Verify run preserves _metadata."""
        result = await mock_agent.run(mock_context, MagicMock())

        metadata = result.get("_metadata", {})
        assert metadata.get("agent_id") == "test_react_run"
        assert metadata.get("profile_id") == "test-profile-id"


# Run with: pytest tests/integration/test_react_base_middleware.py -v
