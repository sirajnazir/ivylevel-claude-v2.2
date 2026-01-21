# agents/tests/patterns/test_observability.py
"""
Tests for Observability Patterns (J2) - v5.4 True Autonomous Agents.

Tests:
- J2: Performance Metrics collection
"""

import pytest
import time
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestMetricsCollection:
    """Tests for J2: Performance Metrics pattern."""

    def test_metrics_collector_creation(self):
        """Test MetricsCollector can be created."""
        from observability import MetricsCollector

        collector = MetricsCollector()

        assert collector is not None

    def test_get_metrics_collector_singleton(self):
        """Test get_metrics_collector returns singleton."""
        from observability import get_metrics_collector

        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()

        assert collector1 is collector2

    def test_metric_value_model(self):
        """Test MetricValue model structure."""
        from observability import MetricValue

        metric = MetricValue(
            name="llm_latency",
            value=1250.5,
            unit="ms",
            tags={"agent": "gameplan", "model": "gpt-4"},
        )

        assert metric.name == "llm_latency"
        assert metric.value == 1250.5
        assert metric.unit == "ms"

    def test_trace_span_model(self):
        """Test TraceSpan model structure."""
        from observability import TraceSpan
        from datetime import datetime

        span = TraceSpan(
            span_id="span-123",
            trace_id="trace-456",
            name="gameplan_generation",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=1500,
            status="success",
            attributes={"profile_id": "profile-123"},
        )

        assert span.span_id == "span-123"
        assert span.duration_ms == 1500

    def test_agent_metrics_model(self):
        """Test AgentMetrics model structure."""
        from observability import AgentMetrics

        metrics = AgentMetrics(
            agent_name="gameplan_agent",
            profile_id="profile-123",
            session_id="session-456",
            start_time=time.time(),
            end_time=time.time() + 2.5,
            duration_ms=2500,
            llm_calls=3,
            llm_tokens_used=1500,
            cache_hits=2,
            cache_misses=1,
            errors=[],
            quality_score=0.85,
        )

        assert metrics.llm_calls == 3
        assert metrics.quality_score == 0.85

    def test_start_agent_metrics(self):
        """Test starting metrics collection for an agent."""
        from observability import get_metrics_collector

        collector = get_metrics_collector()

        metrics_id = collector.start_agent_metrics(
            agent_name="test_agent",
            profile_id="profile-123",
            session_id="session-456",
        )

        assert metrics_id is not None
        assert isinstance(metrics_id, str)

    def test_finish_agent_metrics(self):
        """Test finishing metrics collection."""
        from observability import get_metrics_collector

        collector = get_metrics_collector()

        metrics_id = collector.start_agent_metrics(
            agent_name="test_agent",
            profile_id="profile-123",
            session_id="session-456",
        )

        # Simulate some work
        time.sleep(0.01)

        metrics = collector.finish_agent_metrics(metrics_id)

        assert metrics is not None
        assert metrics.duration_ms > 0

    def test_record_llm_call(self):
        """Test recording LLM call metrics."""
        from observability import get_metrics_collector

        collector = get_metrics_collector()

        metrics_id = collector.start_agent_metrics(
            "test_agent", "profile-123", "session-456"
        )

        collector.record_llm_call(
            metrics_id,
            model="gpt-4",
            tokens=500,
            latency_ms=1200,
        )

        metrics = collector.finish_agent_metrics(metrics_id)

        assert metrics.llm_calls >= 1
        assert metrics.llm_tokens_used >= 500

    def test_record_error(self):
        """Test recording error metrics."""
        from observability import get_metrics_collector

        collector = get_metrics_collector()

        metrics_id = collector.start_agent_metrics(
            "test_agent", "profile-123", "session-456"
        )

        collector.record_error(metrics_id, "Test error message")

        metrics = collector.finish_agent_metrics(metrics_id)

        assert len(metrics.errors) >= 1
        assert "Test error" in metrics.errors[0]

    def test_record_metric_function(self):
        """Test convenience function for recording metrics."""
        from observability import record_metric

        # Should not raise
        record_metric("test_metric", 42.5, tags={"test": "true"})

    def test_timed_decorator(self):
        """Test timed decorator for automatic timing."""
        from observability import timed

        @timed("test_operation")
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()

        assert result == "done"
        # Timing should have been recorded

    @pytest.mark.asyncio
    async def test_timed_decorator_async(self):
        """Test timed decorator works with async functions."""
        from observability import timed
        import asyncio

        @timed("async_operation")
        async def async_slow():
            await asyncio.sleep(0.01)
            return "async done"

        result = await async_slow()

        assert result == "async done"

    def test_langfuse_availability_flag(self):
        """Test Langfuse availability flag exists."""
        from observability import LANGFUSE_AVAILABLE

        # Should be a boolean
        assert isinstance(LANGFUSE_AVAILABLE, bool)


class TestMetricsIntegration:
    """Integration tests for observability patterns."""

    def test_all_observability_types_importable(self):
        """Test all observability types can be imported."""
        from observability import (
            MetricsCollector,
            MetricValue,
            TraceSpan,
            AgentMetrics,
            get_metrics_collector,
            record_metric,
            timed,
        )

        # All should be importable

    def test_full_metrics_lifecycle(self):
        """Test complete metrics collection lifecycle."""
        from observability import get_metrics_collector

        collector = get_metrics_collector()

        # Start
        metrics_id = collector.start_agent_metrics(
            "lifecycle_test", "profile-123", "session-456"
        )

        # Record various metrics
        collector.record_llm_call(metrics_id, "gpt-4", 100, 500)
        collector.record_llm_call(metrics_id, "gpt-4", 200, 600)

        # Set quality score
        collector.set_quality_score(metrics_id, 0.88)

        # Finish
        metrics = collector.finish_agent_metrics(metrics_id)

        assert metrics.llm_calls == 2
        assert metrics.llm_tokens_used == 300
        assert metrics.quality_score == 0.88

    def test_metrics_isolation(self):
        """Test metrics are isolated between agents."""
        from observability import get_metrics_collector

        collector = get_metrics_collector()

        # Agent 1
        id1 = collector.start_agent_metrics("agent1", "profile-1", "session-1")
        collector.record_llm_call(id1, "gpt-4", 100, 500)

        # Agent 2
        id2 = collector.start_agent_metrics("agent2", "profile-2", "session-2")
        collector.record_llm_call(id2, "gpt-4", 200, 600)
        collector.record_llm_call(id2, "gpt-4", 300, 700)

        # Finish both
        metrics1 = collector.finish_agent_metrics(id1)
        metrics2 = collector.finish_agent_metrics(id2)

        assert metrics1.llm_calls == 1
        assert metrics2.llm_calls == 2

    def test_concurrent_metrics_collection(self):
        """Test concurrent metrics collection."""
        from observability import get_metrics_collector
        import threading

        collector = get_metrics_collector()
        results = []

        def collect_metrics(n):
            mid = collector.start_agent_metrics(f"agent_{n}", f"profile-{n}", f"session-{n}")
            collector.record_llm_call(mid, "gpt-4", n * 100, n * 500)
            time.sleep(0.01)
            metrics = collector.finish_agent_metrics(mid)
            results.append(metrics)

        threads = [threading.Thread(target=collect_metrics, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5

    def test_metrics_without_finish(self):
        """Test starting metrics without finishing (cleanup)."""
        from observability import get_metrics_collector

        collector = get_metrics_collector()

        # Start but don't finish - should not leak
        collector.start_agent_metrics("orphan", "profile", "session")

        # Should handle gracefully

    def test_invalid_metrics_id(self):
        """Test handling invalid metrics ID."""
        from observability import get_metrics_collector

        collector = get_metrics_collector()

        # Recording to non-existent metrics
        collector.record_llm_call("invalid-id", "gpt-4", 100, 500)

        # Finishing non-existent metrics
        result = collector.finish_agent_metrics("invalid-id")

        # Should handle gracefully (return None or default)
