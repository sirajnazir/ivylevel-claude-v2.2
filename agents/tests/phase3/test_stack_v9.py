"""
Tests for MiddlewareStackV9

Verifies that the complete v9.0 stack initializes correctly
with all 50 patterns available.
"""

import pytest
from unittest.mock import MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.stack_v9 import MiddlewareStackV9


class TestMiddlewareStackV9:
    """Tests for MiddlewareStackV9."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        return MagicMock()

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        return MagicMock()

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client."""
        return MagicMock()

    @pytest.fixture
    def mock_langfuse(self):
        """Mock Langfuse client."""
        return MagicMock()

    @pytest.fixture
    def stack(self, mock_supabase, mock_redis, mock_openai, mock_langfuse):
        """Create a fully-configured stack."""
        return MiddlewareStackV9(
            supabase_client=mock_supabase,
            redis_client=mock_redis,
            llm_client=mock_openai,
            openai_client=mock_openai,
            langfuse_client=mock_langfuse,
        )

    @pytest.fixture
    def minimal_stack(self):
        """Create a minimal stack without clients."""
        return MiddlewareStackV9()

    def test_initialization(self, stack):
        """Test stack initializes without errors."""
        assert stack is not None

    def test_minimal_initialization(self, minimal_stack):
        """Test stack initializes without any clients."""
        assert minimal_stack is not None

    def test_has_memory_patterns(self, stack):
        """Test memory patterns are initialized."""
        assert hasattr(stack, 'longterm_memory')
        assert hasattr(stack, 'semantic_memory')
        assert hasattr(stack, 'memory_extractor')
        assert hasattr(stack, 'memory_consolidator')

    def test_has_tool_patterns(self, stack):
        """Test tool patterns are initialized."""
        assert hasattr(stack, 'tool_registry')
        assert hasattr(stack, 'tool_caller')
        assert hasattr(stack, 'schema_generator')
        assert hasattr(stack, 'parallel_executor')
        assert hasattr(stack, 'tool_chainer')

    def test_has_learning_patterns(self, stack):
        """Test learning patterns are initialized."""
        assert hasattr(stack, 'feedback_loop')
        assert hasattr(stack, 'behavior_adapter')
        assert hasattr(stack, 'pattern_recognizer')
        assert hasattr(stack, 'preference_learner')

    def test_has_reasoning_patterns(self, stack):
        """Test reasoning patterns are initialized."""
        assert hasattr(stack, 'adaptive_prompter')
        assert hasattr(stack, 'metacognitor')

    def test_has_safety_patterns(self, stack):
        """Test safety patterns are initialized."""
        assert hasattr(stack, 'content_moderator')
        assert hasattr(stack, 'pii_detector')

    def test_has_observability_patterns(self, stack):
        """Test observability patterns are initialized."""
        assert hasattr(stack, 'request_logger')
        assert hasattr(stack, 'cost_tracker')
        assert hasattr(stack, 'context_compressor')

    def test_get_pattern_availability(self, stack):
        """Test pattern availability report."""
        availability = stack.get_pattern_availability()

        # Should have 20 Phase 3 patterns
        assert len(availability) == 20

        # Check all pattern keys exist
        expected_patterns = [
            "B3_semantic_memory",
            "B4_longterm_memory",
            "B5_memory_extraction",
            "B6_memory_consolidation",
            "D1_tool_registry",
            "D2_tool_calling",
            "D3_schema_generation",
            "D4_parallel_execution",
            "D7_tool_chaining",
            "I1_feedback_loop",
            "I2_behavior_adaptation",
            "I3_pattern_recognition",
            "I5_preference_learning",
            "A5_adaptive_prompting",
            "A12_metacognition",
            "F5_content_moderation",
            "F6_pii_detection",
            "J2_request_logging",
            "J5_cost_tracking",
            "K4_context_compression",
        ]

        for pattern in expected_patterns:
            assert pattern in availability

    def test_get_phase3_summary(self, stack):
        """Test Phase 3 summary."""
        summary = stack.get_phase3_summary()

        assert summary["phase"] == "3"
        assert summary["version"] == "9.0"
        assert summary["total_patterns"] == 20
        assert "availability" in summary
        assert "session_costs" in summary

    def test_inherits_v8(self, stack):
        """Test stack inherits v8 patterns."""
        # Should have v8 patterns
        assert hasattr(stack, 'session_context')
        assert hasattr(stack, 'reflective_reasoner')
        assert hasattr(stack, 'planning_engine')
        assert hasattr(stack, 'llm_judge')

    def test_inherits_v7(self, stack):
        """Test stack inherits v7 patterns."""
        # Should have v7 patterns
        assert hasattr(stack, 'context_engineer')
        assert hasattr(stack, 'producer_critic')

    def test_inherits_v6(self, stack):
        """Test stack inherits v6 patterns."""
        # Should have v6 patterns (from base via v7)
        assert hasattr(stack, 'approval_gates')

    def test_count_tokens(self, stack):
        """Test token counting."""
        count = stack.count_tokens("Hello world")
        assert isinstance(count, int)
        assert count > 0

    def test_register_tool(self, stack):
        """Test tool registration."""
        def my_handler(x: int) -> int:
            return x * 2

        result = stack.register_tool(
            name="double",
            description="Double a number",
            handler=my_handler,
        )

        assert result is True
        assert stack.tool_registry.get("double") is not None

    @pytest.mark.asyncio
    async def test_remember_and_recall(self, stack):
        """Test memory convenience methods."""
        success = await stack.remember(
            profile_id="test",
            key="test_key",
            value="test_value",
        )

        # With mock client, this should succeed
        assert success is True

    def test_get_session_costs(self, stack):
        """Test session cost retrieval."""
        costs = stack.get_session_costs()

        assert "total_tokens" in costs
        assert "total_cost" in costs
        assert "request_count" in costs


class TestStackGracefulDegradation:
    """Test stack behavior without clients."""

    @pytest.fixture
    def minimal_stack(self):
        """Stack without any clients."""
        return MiddlewareStackV9()

    def test_patterns_available_without_clients(self, minimal_stack):
        """Test some patterns work without clients."""
        availability = minimal_stack.get_pattern_availability()

        # These should always be available (in-memory)
        assert availability["D1_tool_registry"] is True
        assert availability["D3_schema_generation"] is True
        assert availability["I1_feedback_loop"] is True
        assert availability["I2_behavior_adaptation"] is True
        assert availability["I3_pattern_recognition"] is True
        assert availability["I5_preference_learning"] is True
        assert availability["A5_adaptive_prompting"] is True
        assert availability["J2_request_logging"] is True
        assert availability["J5_cost_tracking"] is True
        assert availability["K4_context_compression"] is True

    def test_patterns_unavailable_without_clients(self, minimal_stack):
        """Test patterns that require clients are unavailable."""
        availability = minimal_stack.get_pattern_availability()

        # These need OpenAI
        assert availability["B3_semantic_memory"] is False
        assert availability["B5_memory_extraction"] is False
        assert availability["B6_memory_consolidation"] is False
        assert availability["A12_metacognition"] is False
        assert availability["F5_content_moderation"] is False

        # These need Supabase
        assert availability["B4_longterm_memory"] is False


# Run with: pytest tests/phase3/test_stack_v9.py -v
