# tests/patterns/test_observability.py
"""
Tests for Observability patterns: J2 Performance Metrics
CORRECTED to match actual implementation
"""

import pytest
from datetime import datetime


class TestMetricsCollector:
    """Tests for MetricsCollector (J2)."""
    
    def test_collector_importable(self):
        """Test MetricsCollector can be imported."""
        from observability.metrics import MetricsCollector
        assert MetricsCollector is not None
    
    def test_collector_initialization(self):
        """Test MetricsCollector can be initialized."""
        from observability.metrics import MetricsCollector
        collector = MetricsCollector()
        assert collector is not None
    
    def test_collector_with_project_name(self):
        """Test MetricsCollector with custom project name."""
        from observability.metrics import MetricsCollector
        collector = MetricsCollector(project_name="test_project")
        assert collector.project_name == "test_project"
    
    def test_record_metric(self):
        """Test recording a metric."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        collector.record_metric(
            name="test_metric",
            value=42.0,
            unit="ms",
            tags={"agent": "ec_agent"},
        )
        
        # Should complete without error
        assert len(collector._metrics) == 1
    
    def test_start_trace(self):
        """Test starting a trace returns span_id."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        span_id = collector.start_trace("test_operation")
        
        assert span_id is not None
        assert isinstance(span_id, str)
    
    def test_start_trace_with_metadata(self):
        """Test starting a trace with metadata."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        span_id = collector.start_trace(
            "test_operation",
            metadata={"profile_id": "123"},
        )
        
        assert span_id is not None
        assert collector._traces[span_id].metadata["profile_id"] == "123"
    
    def test_end_trace(self):
        """Test ending a trace returns TraceSpan."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        span_id = collector.start_trace("test_operation")
        span = collector.end_trace(span_id)
        
        assert span is not None
        assert span.status == "completed"
        assert span.duration_ms is not None
    
    def test_end_trace_failed(self):
        """Test ending a trace with failed status."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        span_id = collector.start_trace("test_operation")
        span = collector.end_trace(span_id, status="failed", metadata={"error": "Test error"})
        
        assert span.status == "failed"
        assert span.metadata["error"] == "Test error"
    
    @pytest.mark.asyncio
    async def test_trace_operation_context_manager(self):
        """Test trace_operation async context manager."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        async with collector.trace_operation("test_op") as span_id:
            assert span_id is not None
        
        # Span should be completed after context exit
        span = collector._traces[span_id]
        assert span.status == "completed"
    
    def test_start_agent_metrics(self):
        """Test starting agent metrics returns metrics_id."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        metrics_id = collector.start_agent_metrics(
            agent_name="ec_agent",
            profile_id="profile-123",
            session_id="session-456",
        )
        
        assert metrics_id is not None
        assert isinstance(metrics_id, str)
    
    def test_record_llm_call(self):
        """Test recording LLM call with tokens."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        metrics_id = collector.start_agent_metrics("ec_agent", "profile-123")
        
        collector.record_llm_call(
            metrics_id,
            tokens_input=100,
            tokens_output=50,
        )
        
        metrics = collector._agent_metrics[metrics_id]
        assert metrics.llm_calls == 1
        assert metrics.llm_tokens_input == 100
        assert metrics.llm_tokens_output == 50
    
    def test_record_tool_call(self):
        """Test recording tool call."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        metrics_id = collector.start_agent_metrics("ec_agent", "profile-123")
        
        collector.record_tool_call(metrics_id)
        collector.record_tool_call(metrics_id)
        
        metrics = collector._agent_metrics[metrics_id]
        assert metrics.tool_calls == 2
    
    def test_record_retry(self):
        """Test recording retry."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        metrics_id = collector.start_agent_metrics("ec_agent", "profile-123")
        
        collector.record_retry(metrics_id)
        
        metrics = collector._agent_metrics[metrics_id]
        assert metrics.retries == 1
    
    def test_record_quality_scores(self):
        """Test recording quality scores."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        metrics_id = collector.start_agent_metrics("ec_agent", "profile-123")
        
        collector.record_quality_scores(
            metrics_id,
            quality_score=0.85,
            voice_score=0.90,
            personalization_score=0.80,
        )
        
        metrics = collector._agent_metrics[metrics_id]
        assert metrics.quality_score == 0.85
        assert metrics.voice_score == 0.90
        assert metrics.personalization_score == 0.80
    
    def test_record_react_metrics(self):
        """Test recording ReAct metrics."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        metrics_id = collector.start_agent_metrics("ec_agent", "profile-123")
        
        collector.record_react_metrics(metrics_id, cycles=3, quality_improvement=0.15)
        
        metrics = collector._agent_metrics[metrics_id]
        assert metrics.react_cycles == 3
        assert metrics.quality_improvement == 0.15
    
    def test_record_error(self):
        """Test recording error."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        metrics_id = collector.start_agent_metrics("ec_agent", "profile-123")
        
        collector.record_error(metrics_id, "Test error")
        collector.record_error(metrics_id, "Warning", is_warning=True)
        
        metrics = collector._agent_metrics[metrics_id]
        assert len(metrics.errors) == 1
        assert len(metrics.warnings) == 1
    
    def test_finish_agent_metrics(self):
        """Test finishing agent metrics returns AgentMetrics."""
        from observability.metrics import MetricsCollector, AgentMetrics
        
        collector = MetricsCollector()
        metrics_id = collector.start_agent_metrics("ec_agent", "profile-123")
        collector.record_llm_call(metrics_id, tokens_input=100, tokens_output=50)
        
        metrics = collector.finish_agent_metrics(metrics_id)
        
        assert isinstance(metrics, AgentMetrics)
        assert metrics.agent_name == "ec_agent"
        assert metrics.duration_ms >= 0
    
    def test_get_aggregate_metrics(self):
        """Test getting aggregate metrics."""
        from observability.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        # Record some metrics
        id1 = collector.start_agent_metrics("ec_agent", "profile-1")
        collector.record_llm_call(id1, tokens_input=100, tokens_output=50)
        collector.finish_agent_metrics(id1)
        
        id2 = collector.start_agent_metrics("ec_agent", "profile-2")
        collector.record_llm_call(id2, tokens_input=200, tokens_output=100)
        collector.finish_agent_metrics(id2)
        
        agg = collector.get_aggregate_metrics(agent_name="ec_agent")
        
        assert agg["count"] == 2
        assert agg["total_llm_calls"] == 2
        assert agg["total_tokens"] == 450


class TestAgentMetrics:
    """Tests for AgentMetrics model."""
    
    def test_agent_metrics_importable(self):
        """Test AgentMetrics can be imported."""
        from observability.metrics import AgentMetrics
        assert AgentMetrics is not None
    
    def test_agent_metrics_creation(self):
        """Test creating AgentMetrics."""
        from observability.metrics import AgentMetrics
        
        metrics = AgentMetrics(
            agent_name="ec_agent",
            profile_id="profile-123",
        )
        
        assert metrics.agent_name == "ec_agent"
        assert metrics.llm_calls == 0
        assert metrics.errors == []


class TestTraceSpan:
    """Tests for TraceSpan model."""
    
    def test_trace_span_importable(self):
        """Test TraceSpan can be imported."""
        from observability.metrics import TraceSpan
        assert TraceSpan is not None


class TestMetricValue:
    """Tests for MetricValue model."""
    
    def test_metric_value_importable(self):
        """Test MetricValue can be imported."""
        from observability.metrics import MetricValue
        assert MetricValue is not None


class TestGlobalCollector:
    """Tests for global metrics collector."""
    
    def test_get_metrics_collector(self):
        """Test get_metrics_collector returns collector."""
        from observability.metrics import get_metrics_collector, MetricsCollector
        
        collector = get_metrics_collector()
        
        assert isinstance(collector, MetricsCollector)
    
    def test_get_metrics_collector_singleton(self):
        """Test get_metrics_collector returns same instance."""
        from observability.metrics import get_metrics_collector
        
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        
        assert collector1 is collector2


class TestTimedDecorator:
    """Tests for @timed decorator."""
    
    def test_timed_importable(self):
        """Test @timed decorator can be imported."""
        from observability.metrics import timed
        assert timed is not None
    
    def test_timed_creates_decorator(self):
        """Test @timed creates a decorator."""
        from observability.metrics import timed
        
        decorator = timed("test_function")
        assert callable(decorator)


class TestRecordMetricConvenience:
    """Tests for record_metric convenience function."""
    
    def test_record_metric_exists(self):
        """Test record_metric convenience function exists."""
        from observability.metrics import record_metric
        assert record_metric is not None
    
    def test_record_metric_works(self):
        """Test record_metric convenience function works."""
        from observability.metrics import record_metric
        
        # Should not raise
        record_metric("test", 42.0, "ms")
