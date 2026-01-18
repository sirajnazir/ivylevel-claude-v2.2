"""
Tests for J1: Reasoning Traces, J3: Audit Trail, J4: Monitoring Patterns
"""

import pytest
from datetime import datetime, timezone, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.observability.reasoning_traces_v8 import (
    ReasoningTraceCollector,
    ReasoningTrace,
    TraceEvent,
    TraceEventType,
)
from middleware.observability.audit_trail_v8 import (
    AuditTrailManager,
    AuditEntry,
    AuditAction,
    AuditActorType,
)
from middleware.observability.monitoring_v8 import (
    MonitoringManager,
    Metric,
    MetricType,
    Alert,
    AlertRule,
    AlertSeverity,
    TimerContext,
    DEFAULT_ALERT_RULES,
)


class TestTraceEventType:
    """Tests for TraceEventType enum."""

    def test_event_types(self):
        """Test trace event type values."""
        assert TraceEventType.THOUGHT.value == "thought"
        assert TraceEventType.ACTION.value == "action"
        assert TraceEventType.OBSERVATION.value == "observation"
        assert TraceEventType.TOOL_CALL.value == "tool_call"
        assert TraceEventType.REFLECTION.value == "reflection"


class TestTraceEvent:
    """Tests for TraceEvent model."""

    def test_event_creation(self):
        """Test TraceEvent creation."""
        event = TraceEvent(
            event_type=TraceEventType.THOUGHT,
            content="Analyzing student's essay structure",
        )
        assert event.event_type == TraceEventType.THOUGHT
        assert "essay" in event.content
        assert event.event_id is not None

    def test_event_with_metadata(self):
        """Test TraceEvent with metadata."""
        event = TraceEvent(
            event_type=TraceEventType.TOOL_CALL,
            content="Calling essay analyzer",
            metadata={"tool": "essay_analyzer", "input_length": 500},
        )
        assert event.metadata["tool"] == "essay_analyzer"


class TestReasoningTrace:
    """Tests for ReasoningTrace model."""

    def test_trace_creation(self):
        """Test ReasoningTrace creation."""
        trace = ReasoningTrace(
            profile_id="profile-123",
            session_id="session-456",
            agent_name="essay_agent",
            input_message="Help me with my essay",
        )
        assert trace.profile_id == "profile-123"
        assert trace.agent_name == "essay_agent"
        assert trace.events == []

    def test_trace_with_events(self):
        """Test ReasoningTrace with events."""
        trace = ReasoningTrace(
            profile_id="profile-123",
            session_id="session-456",
            agent_name="essay_agent",
            input_message="Help me",
            events=[
                TraceEvent(event_type=TraceEventType.THOUGHT, content="Thinking..."),
                TraceEvent(event_type=TraceEventType.ACTION, content="Taking action"),
            ],
        )
        assert len(trace.events) == 2


class TestReasoningTraceCollector:
    """Tests for ReasoningTraceCollector."""

    @pytest.fixture
    def collector(self, mock_supabase, mock_langfuse):
        return ReasoningTraceCollector(
            supabase_client=mock_supabase,
            langfuse_client=mock_langfuse,
        )

    def test_collector_creation(self, collector):
        """Test collector creation."""
        assert collector is not None
        assert collector.max_events == 100

    def test_collector_creation_with_params(self, mock_supabase):
        """Test collector creation with params."""
        collector = ReasoningTraceCollector(
            supabase_client=mock_supabase,
            max_events_per_trace=50,
        )
        assert collector.max_events == 50

    def test_start_trace(self, collector):
        """Test starting a trace."""
        trace = collector.start_trace(
            profile_id="profile-123",
            session_id="session-456",
            agent_name="test_agent",
            input_message="Test input",
        )
        assert isinstance(trace, ReasoningTrace)
        assert trace.trace_id in collector._active_traces

    def test_add_thought(self, collector):
        """Test adding thought to trace."""
        trace = collector.start_trace(
            profile_id="p1",
            session_id="s1",
            agent_name="agent",
            input_message="input",
        )
        event = collector.add_thought(
            trace_id=trace.trace_id,
            thought="This is a thought",
        )
        assert event is not None
        assert event.event_type == TraceEventType.THOUGHT

    def test_add_action(self, collector):
        """Test adding action to trace."""
        trace = collector.start_trace(
            profile_id="p1",
            session_id="s1",
            agent_name="agent",
            input_message="input",
        )
        event = collector.add_action(
            trace_id=trace.trace_id,
            action="Taking action",
        )
        assert event.event_type == TraceEventType.ACTION

    def test_add_tool_call(self, collector):
        """Test adding tool call to trace."""
        trace = collector.start_trace(
            profile_id="p1",
            session_id="s1",
            agent_name="agent",
            input_message="input",
        )
        event = collector.add_tool_call(
            trace_id=trace.trace_id,
            tool_name="search",
            tool_input={"query": "test"},
        )
        assert event.event_type == TraceEventType.TOOL_CALL
        assert event.metadata["tool"] == "search"

    @pytest.mark.asyncio
    async def test_end_trace(self, collector):
        """Test ending a trace."""
        trace = collector.start_trace(
            profile_id="p1",
            session_id="s1",
            agent_name="agent",
            input_message="input",
        )
        collector.add_thought(trace.trace_id, "Thought 1")
        collector.add_action(trace.trace_id, "Action 1")

        result = await collector.end_trace(
            trace_id=trace.trace_id,
            output="Final output",
            success=True,
        )
        assert result.final_output == "Final output"
        assert result.success == True
        assert result.completed_at is not None


class TestAuditAction:
    """Tests for AuditAction enum."""

    def test_action_values(self):
        """Test audit action values."""
        assert AuditAction.CREATE.value == "create"
        assert AuditAction.UPDATE.value == "update"
        assert AuditAction.DELETE.value == "delete"
        assert AuditAction.APPROVE.value == "approve"
        assert AuditAction.REJECT.value == "reject"


class TestAuditActorType:
    """Tests for AuditActorType enum."""

    def test_actor_types(self):
        """Test audit actor type values."""
        assert AuditActorType.USER.value == "user"
        assert AuditActorType.AGENT.value == "agent"
        assert AuditActorType.SYSTEM.value == "system"
        assert AuditActorType.COACH.value == "coach"


class TestAuditEntry:
    """Tests for AuditEntry model."""

    def test_entry_creation(self):
        """Test AuditEntry creation."""
        entry = AuditEntry(
            actor_id="user-123",
            actor_type=AuditActorType.USER,
            action=AuditAction.CREATE,
            resource_type="profile",
        )
        assert entry.actor_id == "user-123"
        assert entry.action == AuditAction.CREATE
        assert entry.success == True

    def test_entry_with_details(self):
        """Test AuditEntry with details."""
        entry = AuditEntry(
            actor_id="agent-456",
            actor_type=AuditActorType.AGENT,
            action=AuditAction.UPDATE,
            resource_type="task",
            resource_id="task-789",
            details={"field": "status", "old_value": "pending", "new_value": "completed"},
        )
        assert entry.details["field"] == "status"


class TestAuditTrailManager:
    """Tests for AuditTrailManager."""

    @pytest.fixture
    def manager(self, mock_supabase):
        return AuditTrailManager(supabase_client=mock_supabase)

    def test_manager_creation(self, manager):
        """Test manager creation."""
        assert manager is not None
        assert manager._buffer_size == 100

    @pytest.mark.asyncio
    async def test_log_action(self, manager):
        """Test logging an action."""
        entry = await manager.log(
            actor_id="user-123",
            actor_type=AuditActorType.USER,
            action=AuditAction.CREATE,
            resource_type="profile",
        )
        assert entry is not None
        assert entry.action == AuditAction.CREATE

    @pytest.mark.asyncio
    async def test_log_agent_action(self, manager):
        """Test logging agent action."""
        entry = await manager.log_agent_action(
            agent_name="essay_agent",
            action="analyze_essay",
            resource_type="essay",
            resource_id="essay-123",
        )
        assert entry.actor_type == AuditActorType.AGENT

    @pytest.mark.asyncio
    async def test_log_user_action(self, manager):
        """Test logging user action."""
        entry = await manager.log_user_action(
            user_id="user-456",
            action=AuditAction.UPDATE,
            resource_type="profile",
        )
        assert entry.actor_type == AuditActorType.USER

    @pytest.mark.asyncio
    async def test_log_approval(self, manager):
        """Test logging approval."""
        entry = await manager.log_approval(
            reviewer_id="coach-123",
            reviewer_type=AuditActorType.COACH,
            approved=True,
            resource_type="essay_feedback",
            resource_id="feedback-456",
            reason="Good quality",
        )
        assert entry.action == AuditAction.APPROVE

    @pytest.mark.asyncio
    async def test_flush_buffer(self, manager):
        """Test flushing buffer."""
        # Add entries to buffer
        for i in range(5):
            await manager.log(
                actor_id=f"user-{i}",
                actor_type=AuditActorType.USER,
                action=AuditAction.CREATE,
                resource_type="test",
            )

        # Flush
        count = await manager.flush()
        assert count == 5


class TestMetricType:
    """Tests for MetricType enum."""

    def test_metric_types(self):
        """Test metric type values."""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.TIMER.value == "timer"


class TestAlertSeverity:
    """Tests for AlertSeverity enum."""

    def test_severity_values(self):
        """Test alert severity values."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestMetric:
    """Tests for Metric model."""

    def test_metric_creation(self):
        """Test Metric creation."""
        metric = Metric(
            name="response_time",
            metric_type=MetricType.TIMER,
            value=150.5,
        )
        assert metric.name == "response_time"
        assert metric.value == 150.5

    def test_metric_with_tags(self):
        """Test Metric with tags."""
        metric = Metric(
            name="api_calls",
            metric_type=MetricType.COUNTER,
            value=100,
            tags={"service": "openai", "endpoint": "completions"},
        )
        assert metric.tags["service"] == "openai"


class TestAlertRule:
    """Tests for AlertRule model."""

    def test_rule_creation(self):
        """Test AlertRule creation."""
        rule = AlertRule(
            name="high_latency",
            metric_name="response_time",
            condition="gt",
            threshold=5000,
        )
        assert rule.name == "high_latency"
        assert rule.condition == "gt"
        assert rule.severity == AlertSeverity.WARNING

    def test_rule_with_severity(self):
        """Test AlertRule with severity."""
        rule = AlertRule(
            name="critical_errors",
            metric_name="error_count",
            condition="gte",
            threshold=10,
            severity=AlertSeverity.CRITICAL,
        )
        assert rule.severity == AlertSeverity.CRITICAL


class TestMonitoringManager:
    """Tests for MonitoringManager."""

    @pytest.fixture
    def manager(self, mock_langfuse):
        return MonitoringManager(langfuse_client=mock_langfuse)

    def test_manager_creation(self, manager):
        """Test manager creation."""
        assert manager is not None

    def test_record_metric(self, manager):
        """Test recording a metric."""
        metric = manager.record_metric(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.GAUGE,
        )
        assert metric.name == "test_metric"
        assert metric.value == 42.0

    def test_increment_counter(self, manager):
        """Test incrementing counter."""
        metric1 = manager.increment("api_calls")
        assert metric1.value == 1.0

        metric2 = manager.increment("api_calls")
        assert metric2.value == 2.0

    def test_add_alert_rule(self, manager):
        """Test adding alert rule."""
        rule = AlertRule(
            name="test_alert",
            metric_name="test_metric",
            condition="gt",
            threshold=100,
        )
        manager.add_alert_rule(rule)
        assert len(manager._alert_rules) >= 1

    def test_alert_triggered(self, manager):
        """Test alert is triggered."""
        rule = AlertRule(
            name="high_value",
            metric_name="test_value",
            condition="gt",
            threshold=50,
            cooldown_seconds=0,  # No cooldown for testing
        )
        manager.add_alert_rule(rule)

        # Record metric that exceeds threshold
        manager.record_metric("test_value", 100)

        alerts = manager.get_active_alerts()
        assert len(alerts) >= 1

    def test_get_metric_stats(self, manager):
        """Test getting metric statistics."""
        for i in range(5):
            manager.record_metric("test_stats", float(i * 10))

        stats = manager.get_metric_stats("test_stats")
        assert stats["count"] == 5
        assert stats["min"] == 0
        assert stats["max"] == 40

    def test_timer_context(self, manager):
        """Test timer context manager."""
        timer = manager.timer("operation_time")
        assert isinstance(timer, TimerContext)


class TestDefaultAlertRules:
    """Tests for default alert rules."""

    def test_default_rules_exist(self):
        """Test default rules are defined."""
        assert len(DEFAULT_ALERT_RULES) > 0

    def test_high_response_time_rule(self):
        """Test high response time rule."""
        rule = next(r for r in DEFAULT_ALERT_RULES if r.name == "high_response_time")
        assert rule.metric_name == "agent_response_time_ms"
        assert rule.condition == "gt"

    def test_high_error_rate_rule(self):
        """Test high error rate rule."""
        rule = next(r for r in DEFAULT_ALERT_RULES if r.name == "high_error_rate")
        assert rule.severity == AlertSeverity.ERROR
