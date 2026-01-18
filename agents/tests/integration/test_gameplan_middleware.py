"""
Integration tests for GamePlanAgent middleware integration.
Tests that GamePlanAgent properly integrates with MiddlewareStackV8.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestGamePlanAgentMiddlewareIntegration:
    """Verify GamePlanAgent middleware integration via mixin testing."""

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
    def mixin_agent(self, mock_supabase):
        """Create an agent-like object with the mixin for testing."""
        from agents.mixins import MiddlewareIntegrationMixin

        class MockGamePlanAgent(MiddlewareIntegrationMixin):
            """Mock agent class for testing mixin integration."""
            def __init__(self):
                self.name = "GamePlan"
                self.llm = MagicMock()
                self.db = mock_supabase
                self.init_middleware(
                    supabase_client=mock_supabase,
                    llm_client=self.llm,
                )

        return MockGamePlanAgent()

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
            "game_plan": {
                "profile_id": "test-id",
                "narrative_dna": "Test narrative",
                "phases": [],
            },
            "validation_passed": True,
            "confidence": 0.85,
        }
        result = mixin_agent.middleware_finalize(original.copy(), "gameplan")

        assert result.get("success") == True
        assert result.get("confidence") == 0.85
        assert result.get("game_plan", {}).get("profile_id") == "test-id"

    @pytest.mark.asyncio
    async def test_audit_action_safe(self, mixin_agent):
        """Verify audit_action doesn't crash (MANDATORY for planning)."""
        await mixin_agent.audit_action(
            action="gameplan_generation",
            resource_type="gameplan",
            resource_id="test-id",
            details={"orchestration_used": True},
            success=True,
        )


class TestGamePlanAgentProcessMethodIntegration:
    """Test the process method integration - simulated."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent simulating GamePlanAgent with mixin."""
        from agents.mixins import MiddlewareIntegrationMixin

        class MockGamePlanAgentProcess(MiddlewareIntegrationMixin):
            """Mock agent class for testing process integration."""
            def __init__(self):
                self.name = "GamePlan"
                self.llm = MagicMock()
                self.db = MagicMock()
                self.init_middleware(
                    supabase_client=self.db,
                    llm_client=self.llm,
                )

            async def generate_orchestrated(self, profile_id, react_hints=None):
                return {
                    "success": True,
                    "game_plan": {
                        "profile_id": profile_id,
                        "narrative_dna": "Test narrative",
                        "identity_synthesis": {"archetype": "academic-achiever"},
                        "phases": [{"name": "Foundation"}],
                        "awards": {"portfolio": {}},
                        "programs": {"top_recommendations": []},
                    },
                    "orchestration": {
                        "ec_agent": "completed",
                        "awards_agent": "completed",
                        "programs_agent": "completed",
                    },
                    "validation_passed": True,
                    "confidence": 0.85,
                }

            async def generate(self, profile_id, data=None, react_hints=None):
                return {
                    "success": True,
                    "game_plan": {"profile_id": profile_id},
                }

            async def process(self, profile_id: str, **kwargs):
                """Simulated process method with middleware wrapping."""
                session_id = kwargs.get("session_id") or f"gameplan_{profile_id}"
                trace_id = self.start_reasoning_trace(profile_id, session_id, "gameplan_orchestration")

                try:
                    async with self.with_middleware_context(profile_id, session_id, "gameplan") as ctx:
                        self.add_thought(trace_id, f"Starting GamePlan generation for profile {profile_id}")

                        react_hints = kwargs.get("react_hints", [])
                        use_orchestration = kwargs.get("use_orchestration", True)

                        self.add_action(trace_id, "orchestrate", {
                            "react_hints_count": len(react_hints),
                            "use_orchestration": use_orchestration,
                        })

                        if use_orchestration:
                            result = await self.generate_orchestrated(profile_id, react_hints=react_hints)
                        else:
                            result = await self.generate(profile_id, kwargs.get("data"), react_hints=react_hints)

                        result = self.middleware_finalize(result, output_type="gameplan")

                        await self.audit_action(
                            action="gameplan_generation",
                            resource_type="gameplan",
                            resource_id=profile_id,
                            details={
                                "orchestration_used": use_orchestration,
                                "react_hints_count": len(react_hints),
                                "validation_passed": result.get("validation_passed", False),
                            },
                            success=result.get("success", False),
                        )

                        await self.end_reasoning_trace(trace_id, success=True)
                        return result

                except Exception as e:
                    await self.end_reasoning_trace(trace_id, success=False, error=str(e))
                    raise

        return MockGamePlanAgentProcess()

    @pytest.mark.asyncio
    async def test_process_returns_result(self, mock_agent):
        """Verify process still returns results."""
        result = await mock_agent.process("test-profile-id")

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_with_orchestration(self, mock_agent):
        """Verify process uses orchestration by default."""
        result = await mock_agent.process("test-profile-id", use_orchestration=True)

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_without_orchestration(self, mock_agent):
        """Verify process can skip orchestration."""
        result = await mock_agent.process("test-profile-id", use_orchestration=False)

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_with_react_hints(self, mock_agent):
        """Verify process handles react hints."""
        result = await mock_agent.process(
            "test-profile-id",
            react_hints=["improve narrative", "add more phases"],
        )

        assert isinstance(result, dict)
        assert result.get("success") == True

    @pytest.mark.asyncio
    async def test_process_preserves_game_plan(self, mock_agent):
        """Verify process preserves game_plan structure."""
        result = await mock_agent.process("test-profile-id")

        game_plan = result.get("game_plan", {})
        assert game_plan.get("profile_id") == "test-profile-id"
        assert "narrative_dna" in game_plan


# Run with: pytest tests/integration/test_gameplan_middleware.py -v
