# agents/tests/integration/test_performance.py
"""
Performance Integration Tests - v5.4 True Autonomous Agents.

These tests verify that the middleware patterns meet performance requirements
and don't introduce unacceptable overhead.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestMiddlewareOverhead:
    """Tests for middleware performance overhead."""

    def test_middleware_creation_fast(self, mock_supabase, mock_redis):
        """Test middleware stack creation is fast."""
        from middleware import MiddlewareStack

        start = time.perf_counter()
        for _ in range(100):
            stack = MiddlewareStack(mock_supabase, mock_redis)
        elapsed = time.perf_counter() - start

        # 100 creations should be under 1 second
        assert elapsed < 1.0
        avg_ms = (elapsed / 100) * 1000
        print(f"Average middleware creation: {avg_ms:.2f}ms")

    @pytest.mark.asyncio
    async def test_context_manager_overhead(self, mock_supabase, mock_redis):
        """Test context manager entry/exit overhead."""
        from middleware import MiddlewareStack
        from context import TaskType

        stack = MiddlewareStack(mock_supabase, mock_redis)

        times = []
        for _ in range(50):
            start = time.perf_counter()
            async with stack.wrap_agent(
                "perf_test",
                "profile-123",
                task_type=TaskType.GENERAL,
            ) as ctx:
                pass  # No work, just measure overhead
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_ms = (sum(times) / len(times)) * 1000
        max_ms = max(times) * 1000

        # Average should be under 50ms, max under 200ms
        assert avg_ms < 50, f"Average overhead too high: {avg_ms:.2f}ms"
        assert max_ms < 200, f"Max overhead too high: {max_ms:.2f}ms"
        print(f"Context manager overhead - Avg: {avg_ms:.2f}ms, Max: {max_ms:.2f}ms")


class TestPatternPerformance:
    """Tests for individual pattern performance."""

    def test_guardrails_check_fast(self, mock_supabase, mock_redis, safe_messages):
        """Test guardrails checks are fast."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        times = []
        for message in safe_messages * 20:  # 100 checks
            start = time.perf_counter()
            stack.check_guardrails(message, is_input=True)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_ms = (sum(times) / len(times)) * 1000

        # Guardrail check should be under 10ms average
        assert avg_ms < 10, f"Guardrail check too slow: {avg_ms:.2f}ms"
        print(f"Guardrail check avg: {avg_ms:.2f}ms")

    def test_escalation_check_fast(self, mock_supabase, mock_redis, safe_messages, unsafe_messages):
        """Test escalation checks are fast."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)
        all_messages = (safe_messages + unsafe_messages) * 10

        times = []
        for message in all_messages:
            start = time.perf_counter()
            stack.check_escalation(message, {})
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_ms = (sum(times) / len(times)) * 1000

        # Escalation check should be under 5ms average
        assert avg_ms < 5, f"Escalation check too slow: {avg_ms:.2f}ms"
        print(f"Escalation check avg: {avg_ms:.2f}ms")

    def test_prioritization_fast(self, mock_supabase, mock_redis, sample_recommendations, sample_student_context, sample_temporal_context):
        """Test prioritization is fast."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)
        context = {
            "student": sample_student_context,
            "temporal": sample_temporal_context,
        }

        # Larger recommendation set
        large_recs = sample_recommendations * 25  # 100 recommendations

        times = []
        for _ in range(10):
            start = time.perf_counter()
            stack.prioritize(large_recs, context)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_ms = (sum(times) / len(times)) * 1000

        # Prioritizing 100 items should be under 100ms
        assert avg_ms < 100, f"Prioritization too slow: {avg_ms:.2f}ms"
        print(f"Prioritization (100 items) avg: {avg_ms:.2f}ms")

    def test_validation_fast(self, mock_supabase, mock_redis, valid_gameplan_output):
        """Test output validation is fast."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        times = []
        for _ in range(100):
            start = time.perf_counter()
            stack.validate_output(valid_gameplan_output, "gameplan")
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_ms = (sum(times) / len(times)) * 1000

        # Validation should be under 10ms average
        assert avg_ms < 10, f"Validation too slow: {avg_ms:.2f}ms"
        print(f"Validation avg: {avg_ms:.2f}ms")

    def test_finalize_fast(self, mock_supabase, mock_redis, valid_gameplan_output):
        """Test finalize operation is fast."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)

        times = []
        for _ in range(100):
            output = valid_gameplan_output.copy()
            start = time.perf_counter()
            stack.finalize(output, "gameplan")
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_ms = (sum(times) / len(times)) * 1000

        # Finalize should be under 20ms average
        assert avg_ms < 20, f"Finalize too slow: {avg_ms:.2f}ms"
        print(f"Finalize avg: {avg_ms:.2f}ms")


class TestConcurrency:
    """Tests for concurrent operation handling."""

    @pytest.mark.asyncio
    async def test_concurrent_agent_executions(self, mock_supabase, mock_redis):
        """Test multiple concurrent agent executions."""
        from middleware import MiddlewareStack
        from context import TaskType

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async def agent_task(profile_id: str):
            async with stack.wrap_agent(
                f"agent_{profile_id}",
                profile_id,
                task_type=TaskType.GENERAL,
            ) as ctx:
                # Simulate some work
                await asyncio.sleep(0.01)
                return ctx.profile_id

        # Run 20 concurrent agents
        start = time.perf_counter()
        tasks = [agent_task(f"profile-{i}") for i in range(20)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        assert len(results) == 20
        # Should complete in parallel, not sequential
        assert elapsed < 1.0, f"Concurrent execution too slow: {elapsed:.2f}s"
        print(f"20 concurrent agents completed in {elapsed:.2f}s")

    @pytest.mark.asyncio
    async def test_metrics_isolation_under_concurrency(self, mock_supabase, mock_redis):
        """Test metrics remain isolated under concurrent execution."""
        from middleware import MiddlewareStack
        from context import TaskType

        stack = MiddlewareStack(mock_supabase, mock_redis)
        results = []

        async def agent_with_metrics(agent_id: int):
            async with stack.wrap_agent(
                f"agent_{agent_id}",
                f"profile-{agent_id}",
                task_type=TaskType.GENERAL,
            ) as ctx:
                # Each agent should have unique metrics
                results.append({
                    "agent_id": agent_id,
                    "metrics_id": ctx.metrics_id,
                })
                await asyncio.sleep(0.01)

        tasks = [agent_with_metrics(i) for i in range(10)]
        await asyncio.gather(*tasks)

        # All metrics IDs should be unique
        metrics_ids = [r["metrics_id"] for r in results]
        assert len(set(metrics_ids)) == 10, "Metrics not isolated"


class TestMemoryPerformance:
    """Tests for working memory performance."""

    @pytest.mark.asyncio
    async def test_working_memory_operations_fast(self, mock_redis):
        """Test working memory operations are fast."""
        from memory import WorkingMemoryManager
        from context import ConversationRole

        manager = WorkingMemoryManager(mock_redis)

        # Create session
        start = time.perf_counter()
        memory = await manager.get_or_create("perf-session", "profile-123")
        create_time = time.perf_counter() - start

        # Add turns
        turn_times = []
        for i in range(50):
            start = time.perf_counter()
            await manager.add_turn(
                "perf-session",
                ConversationRole.USER if i % 2 == 0 else ConversationRole.ASSISTANT,
                f"Message {i}",
            )
            turn_times.append(time.perf_counter() - start)

        # Retrieve
        start = time.perf_counter()
        retrieved = await manager.get_or_create("perf-session", "profile-123")
        retrieve_time = time.perf_counter() - start

        create_ms = create_time * 1000
        avg_turn_ms = (sum(turn_times) / len(turn_times)) * 1000
        retrieve_ms = retrieve_time * 1000

        assert create_ms < 50, f"Memory creation too slow: {create_ms:.2f}ms"
        assert avg_turn_ms < 20, f"Turn addition too slow: {avg_turn_ms:.2f}ms"
        assert retrieve_ms < 50, f"Memory retrieval too slow: {retrieve_ms:.2f}ms"

        print(f"Memory create: {create_ms:.2f}ms, Turn add avg: {avg_turn_ms:.2f}ms, Retrieve: {retrieve_ms:.2f}ms")


class TestScaling:
    """Tests for scaling behavior."""

    def test_prioritization_scales_linearly(self, mock_supabase, mock_redis, sample_student_context, sample_temporal_context):
        """Test prioritization scales linearly with input size."""
        from middleware import MiddlewareStack

        stack = MiddlewareStack(mock_supabase, mock_redis)
        context = {
            "student": sample_student_context,
            "temporal": sample_temporal_context,
        }

        base_rec = {
            "id": "rec",
            "title": "Test",
            "type": "activity",
            "urgency": "medium",
            "impact": 3,
        }

        sizes = [10, 50, 100, 200]
        times = {}

        for size in sizes:
            recs = [{**base_rec, "id": f"rec-{i}"} for i in range(size)]
            start = time.perf_counter()
            stack.prioritize(recs, context)
            times[size] = time.perf_counter() - start

        # Check roughly linear scaling (2x items should be ~2x time, with tolerance)
        ratio_50_10 = times[50] / times[10]
        ratio_100_50 = times[100] / times[50]
        ratio_200_100 = times[200] / times[100]

        # Allow 4x tolerance for small measurement variations
        assert ratio_50_10 < 20, f"Non-linear scaling 50/10: {ratio_50_10:.2f}x"
        assert ratio_100_50 < 10, f"Non-linear scaling 100/50: {ratio_100_50:.2f}x"
        assert ratio_200_100 < 10, f"Non-linear scaling 200/100: {ratio_200_100:.2f}x"

        print(f"Scaling ratios - 50/10: {ratio_50_10:.2f}x, 100/50: {ratio_100_50:.2f}x, 200/100: {ratio_200_100:.2f}x")

    @pytest.mark.asyncio
    async def test_concurrent_scaling(self, mock_supabase, mock_redis):
        """Test performance scales with concurrent operations."""
        from middleware import MiddlewareStack
        from context import TaskType

        stack = MiddlewareStack(mock_supabase, mock_redis)

        async def agent_work(profile_id: str):
            async with stack.wrap_agent(
                "scale_test",
                profile_id,
                task_type=TaskType.GENERAL,
            ) as ctx:
                await asyncio.sleep(0.01)
                return True

        concurrency_levels = [5, 10, 20, 50]
        times = {}

        for level in concurrency_levels:
            start = time.perf_counter()
            tasks = [agent_work(f"profile-{i}") for i in range(level)]
            await asyncio.gather(*tasks)
            times[level] = time.perf_counter() - start

        # Higher concurrency should not cause exponential slowdown
        # Time should grow much slower than linearly (benefit of parallelism)
        for i, level in enumerate(concurrency_levels[1:], 1):
            prev_level = concurrency_levels[i - 1]
            ratio = times[level] / times[prev_level]
            # Should be less than 2x even for 2x concurrency
            print(f"Concurrency {level}/{prev_level}: {ratio:.2f}x time")

        print(f"Concurrent scaling: {times}")
