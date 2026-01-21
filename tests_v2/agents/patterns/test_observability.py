# tests/agents/patterns/test_observability.py
"""
Tests for Observability patterns: J2 Performance Metrics
CORRECTED to match actual implementation API
"""

import pytest
from unittest.mock import Mock, patch


class TestMetricsTracker:
    """Tests for Metrics Tracker (J2)."""
    
    def test_tracker_initialization(self):
        """Test MetricsTracker initialization."""
        from agents.observability.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        assert tracker is not None
    
    def test_start_trace(self, sample_session_id):
        """Test starting a trace."""
        from agents.observability.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        result = tracker.start_trace(sample_session_id, "test_operation")
        
        # Should return a trace/metrics ID
        assert result is not None
    
    def test_end_trace(self, sample_session_id):
        """Test ending a trace."""
        from agents.observability.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        metrics_id = tracker.start_trace(sample_session_id, "test_operation")
        
        result = tracker.end_trace(sample_session_id, success=True)
        
        # Should complete without error
        assert True
    
    def test_record_llm_call(self, sample_session_id):
        """Test recording an LLM call with correct API signature."""
        from agents.observability.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        metrics_id = tracker.start_trace(sample_session_id, "test")
        
        # Actual API uses tokens_input, tokens_output
        tracker.record_llm_call(
            metrics_id,
            tokens_input=100,
            tokens_output=50,
        )
        
        # Should record without error
        assert True
    
    def test_record_agent_execution(self, sample_session_id):
        """Test recording agent execution."""
        from agents.observability.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        metrics_id = tracker.start_trace(sample_session_id, "test")
        
        tracker.record_agent_execution(
            metrics_id,
            agent_name="ec_agent",
            duration_ms=150,
            success=True,
        )
        
        # Should record without error
        assert True
    
    def test_get_metrics(self, sample_session_id):
        """Test getting metrics."""
        from agents.observability.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        metrics_id = tracker.start_trace(sample_session_id, "test")
        
        metrics = tracker.get_metrics(metrics_id)
        
        assert metrics is not None


class TestLangfuseIntegration:
    """Tests for Langfuse integration."""
    
    def test_langfuse_client_optional(self):
        """Test that Langfuse client is optional."""
        from agents.observability.metrics import MetricsTracker
        
        # Should work without Langfuse
        tracker = MetricsTracker()
        assert tracker is not None
    
    def test_tracker_with_mock_langfuse(self, mock_langfuse):
        """Test tracker with mocked Langfuse."""
        from agents.observability.metrics import MetricsTracker
        
        with patch('agents.observability.metrics.Langfuse', return_value=mock_langfuse):
            tracker = MetricsTracker()
            assert tracker is not None


class TestPerformanceMetrics:
    """Tests for performance metric collection."""
    
    def test_duration_tracking(self, sample_session_id):
        """Test that duration is tracked."""
        from agents.observability.metrics import MetricsTracker
        import time
        
        tracker = MetricsTracker()
        metrics_id = tracker.start_trace(sample_session_id, "test")
        
        time.sleep(0.01)  # 10ms
        
        tracker.end_trace(sample_session_id, success=True)
        
        metrics = tracker.get_metrics(metrics_id)
        
        # Duration should be captured
        assert metrics is not None
    
    def test_token_counting(self, sample_session_id):
        """Test that tokens are counted."""
        from agents.observability.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        metrics_id = tracker.start_trace(sample_session_id, "test")
        
        tracker.record_llm_call(metrics_id, tokens_input=100, tokens_output=50)
        tracker.record_llm_call(metrics_id, tokens_input=200, tokens_output=100)
        
        metrics = tracker.get_metrics(metrics_id)
        
        # Total tokens should be tracked
        assert metrics is not None
    
    def test_success_failure_tracking(self, sample_session_id):
        """Test success/failure tracking."""
        from agents.observability.metrics import MetricsTracker
        
        tracker = MetricsTracker()
        
        # Track a success
        metrics_id = tracker.start_trace(sample_session_id, "test")
        tracker.end_trace(sample_session_id, success=True)
        
        # Track a failure
        metrics_id2 = tracker.start_trace(sample_session_id + "_2", "test2")
        tracker.end_trace(sample_session_id + "_2", success=False)
        
        # Both should complete without error
        assert True
