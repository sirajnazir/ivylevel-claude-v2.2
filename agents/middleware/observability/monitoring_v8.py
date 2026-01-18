"""
J4: Monitoring Pattern - Implementation

Real-time monitoring and alerting for agent behavior.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List, Callable
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Metric(BaseModel):
    """A single metric measurement."""
    name: str
    metric_type: MetricType
    value: float
    tags: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Alert(BaseModel):
    """An alert notification."""
    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    metric_name: str
    metric_value: float
    threshold: float
    tags: Dict[str, str] = Field(default_factory=dict)
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None


class AlertRule(BaseModel):
    """Rule for triggering alerts."""
    name: str
    metric_name: str
    condition: str  # "gt", "lt", "gte", "lte", "eq"
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    cooldown_seconds: int = 300  # Don't re-alert within this period
    tags_filter: Optional[Dict[str, str]] = None


class MonitoringManager:
    """
    Real-time monitoring for agent systems.

    Pattern J4: Monitoring

    GUARDRAILS:
    - NEW class - does not modify existing monitoring
    - Integrates with Langfuse when available
    - Supports custom alert handlers
    """

    def __init__(
        self,
        langfuse_client=None,
        alert_handlers: Optional[List[Callable[[Alert], None]]] = None,
    ):
        """
        Initialize monitoring manager.

        Args:
            langfuse_client: For Langfuse integration
            alert_handlers: Callbacks for alerts
        """
        self.langfuse = langfuse_client
        self.alert_handlers = alert_handlers or []

        self._metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._alert_rules: List[AlertRule] = []
        self._active_alerts: Dict[str, Alert] = {}
        self._last_alert_time: Dict[str, datetime] = {}
        self._max_metrics_per_name = 1000

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None,
    ) -> Metric:
        """
        Record a metric.

        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            tags: Tags for filtering

        Returns:
            Recorded Metric
        """
        metric = Metric(
            name=name,
            metric_type=metric_type,
            value=value,
            tags=tags or {},
        )

        # Store metric
        self._metrics[name].append(metric)

        # Trim old metrics
        if len(self._metrics[name]) > self._max_metrics_per_name:
            self._metrics[name] = self._metrics[name][-self._max_metrics_per_name:]

        # Check alert rules
        self._check_alerts(metric)

        # Send to Langfuse
        if self.langfuse:
            try:
                self.langfuse.score(
                    name=name,
                    value=value,
                    data_type="NUMERIC",
                )
            except Exception as e:
                logger.warning(f"Langfuse metric failed: {e}")

        return metric

    def increment(
        self,
        name: str,
        amount: float = 1.0,
        tags: Optional[Dict[str, str]] = None,
    ) -> Metric:
        """Increment a counter metric."""
        # Get current value
        current = 0.0
        if name in self._metrics and self._metrics[name]:
            current = self._metrics[name][-1].value

        return self.record_metric(
            name=name,
            value=current + amount,
            metric_type=MetricType.COUNTER,
            tags=tags,
        )

    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """
        Context manager for timing operations.

        Usage:
            with monitor.timer("operation_duration"):
                do_something()
        """
        return TimerContext(self, name, tags)

    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self._alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")

    def _check_alerts(self, metric: Metric) -> None:
        """Check if metric triggers any alerts."""
        for rule in self._alert_rules:
            if rule.metric_name != metric.name:
                continue

            # Check tags filter
            if rule.tags_filter:
                if not all(
                    metric.tags.get(k) == v
                    for k, v in rule.tags_filter.items()
                ):
                    continue

            # Check condition
            triggered = False
            if rule.condition == "gt" and metric.value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and metric.value < rule.threshold:
                triggered = True
            elif rule.condition == "gte" and metric.value >= rule.threshold:
                triggered = True
            elif rule.condition == "lte" and metric.value <= rule.threshold:
                triggered = True
            elif rule.condition == "eq" and metric.value == rule.threshold:
                triggered = True

            if triggered:
                self._trigger_alert(rule, metric)

    def _trigger_alert(self, rule: AlertRule, metric: Metric) -> None:
        """Trigger an alert."""
        # Check cooldown
        last_alert = self._last_alert_time.get(rule.name)
        if last_alert:
            cooldown = timedelta(seconds=rule.cooldown_seconds)
            if datetime.now(timezone.utc) - last_alert < cooldown:
                return

        alert = Alert(
            alert_id=f"{rule.name}_{datetime.now(timezone.utc).timestamp()}",
            name=rule.name,
            severity=rule.severity,
            message=f"{rule.metric_name} {rule.condition} {rule.threshold}: {metric.value}",
            metric_name=metric.name,
            metric_value=metric.value,
            threshold=rule.threshold,
            tags=metric.tags,
        )

        self._active_alerts[alert.alert_id] = alert
        self._last_alert_time[rule.name] = datetime.now(timezone.utc)

        logger.warning(f"Alert triggered: {alert.name} - {alert.message}")

        # Call handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Resolve an active alert."""
        alert = self._active_alerts.get(alert_id)
        if alert:
            alert.resolved_at = datetime.now(timezone.utc)
            del self._active_alerts[alert_id]
            logger.info(f"Alert resolved: {alert.name}")
        return alert

    def get_metric_stats(
        self,
        name: str,
        window_seconds: int = 300,
    ) -> Dict[str, float]:
        """
        Get statistics for a metric.

        Args:
            name: Metric name
            window_seconds: Time window

        Returns:
            Dict with count, avg, min, max, sum
        """
        metrics = self._metrics.get(name, [])

        cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
        recent = [m for m in metrics if m.timestamp > cutoff]

        if not recent:
            return {"count": 0, "avg": 0, "min": 0, "max": 0, "sum": 0}

        values = [m.value for m in recent]
        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "sum": sum(values),
        }

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self._active_alerts.values())

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard."""
        return {
            "metrics": {
                name: self.get_metric_stats(name)
                for name in self._metrics.keys()
            },
            "active_alerts": [a.model_dump() for a in self._active_alerts.values()],
            "alert_rules": [r.model_dump() for r in self._alert_rules],
        }


class TimerContext:
    """Context manager for timing operations."""

    def __init__(
        self,
        manager: MonitoringManager,
        name: str,
        tags: Optional[Dict[str, str]] = None,
    ):
        self.manager = manager
        self.name = name
        self.tags = tags
        self.start_time: Optional[datetime] = None

    def __enter__(self):
        self.start_time = datetime.now(timezone.utc)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (
                datetime.now(timezone.utc) - self.start_time
            ).total_seconds() * 1000

            self.manager.record_metric(
                name=self.name,
                value=duration_ms,
                metric_type=MetricType.TIMER,
                tags=self.tags,
            )


# Default alert rules for IvyLevel
DEFAULT_ALERT_RULES = [
    AlertRule(
        name="high_response_time",
        metric_name="agent_response_time_ms",
        condition="gt",
        threshold=5000,
        severity=AlertSeverity.WARNING,
    ),
    AlertRule(
        name="very_high_response_time",
        metric_name="agent_response_time_ms",
        condition="gt",
        threshold=10000,
        severity=AlertSeverity.ERROR,
    ),
    AlertRule(
        name="high_error_rate",
        metric_name="agent_errors",
        condition="gt",
        threshold=10,
        severity=AlertSeverity.ERROR,
    ),
    AlertRule(
        name="low_quality_score",
        metric_name="response_quality_score",
        condition="lt",
        threshold=0.5,
        severity=AlertSeverity.WARNING,
    ),
]
