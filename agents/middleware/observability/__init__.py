"""
Observability Module - Phase 2B

J1: Reasoning Traces - Capture agent reasoning
J3: Audit Trail - Complete audit logging
J4: Monitoring - Real-time metrics and alerting

NEW MODULE - Does not modify existing v7.0 code.
"""

from .reasoning_traces_v8 import (
    ReasoningTraceCollector,
    ReasoningTrace,
    TraceEvent,
    TraceEventType,
)
from .audit_trail_v8 import (
    AuditTrailManager,
    AuditEntry,
    AuditAction,
    AuditActorType,
)
from .monitoring_v8 import (
    MonitoringManager,
    Metric,
    MetricType,
    Alert,
    AlertRule,
    AlertSeverity,
    TimerContext,
    DEFAULT_ALERT_RULES,
)

__all__ = [
    # Reasoning Traces (J1)
    "ReasoningTraceCollector",
    "ReasoningTrace",
    "TraceEvent",
    "TraceEventType",
    # Audit Trail (J3)
    "AuditTrailManager",
    "AuditEntry",
    "AuditAction",
    "AuditActorType",
    # Monitoring (J4)
    "MonitoringManager",
    "Metric",
    "MetricType",
    "Alert",
    "AlertRule",
    "AlertSeverity",
    "TimerContext",
    "DEFAULT_ALERT_RULES",
]
