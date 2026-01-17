"""
Pattern J2: Performance Metrics
v5.4 True Autonomous Agents

3P: Langfuse for observability
USP: Coaching quality metrics
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
import logging
import time

logger = logging.getLogger(__name__)


# Try to import Langfuse
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None
    observe = lambda *args, **kwargs: lambda f: f
    logger.warning("langfuse not installed, using local metrics only")


class MetricValue(BaseModel):
    """A single metric measurement."""
    name: str
    value: float
    unit: str = ""
    tags: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TraceSpan(BaseModel):
    """A trace span for timing."""
    span_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = "running"  # running, completed, failed


class AgentMetrics(BaseModel):
    """Metrics for a single agent execution."""
    agent_name: str
    profile_id: str
    session_id: Optional[str] = None
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: int = 0

    # Performance metrics
    llm_calls: int = 0
    llm_tokens_input: int = 0
    llm_tokens_output: int = 0
    tool_calls: int = 0
    retries: int = 0

    # Quality metrics (USP)
    quality_score: Optional[float] = None
    voice_score: Optional[float] = None
    personalization_score: Optional[float] = None

    # ReAct metrics
    react_cycles: int = 0
    quality_improvement: float = 0.0

    # Error tracking
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class MetricsCollector:
    """
    Collects and reports agent performance metrics.

    Pattern J2: Performance Metrics (3P: Langfuse)

    Why this matters:
    1. Understand agent performance
    2. Identify bottlenecks
    3. Track quality over time
    4. Enable optimization
    """

    def __init__(
        self,
        langfuse_client: Optional[Any] = None,
        project_name: str = "ivyquest",
    ):
        """
        Initialize metrics collector.

        Args:
            langfuse_client: Optional Langfuse client
            project_name: Project name for metrics
        """
        self.langfuse = langfuse_client
        self.project_name = project_name
        self._metrics: List[MetricValue] = []
        self._traces: Dict[str, TraceSpan] = {}
        self._agent_metrics: Dict[str, AgentMetrics] = {}

        # Initialize Langfuse if available and no client provided
        if LANGFUSE_AVAILABLE and not self.langfuse:
            try:
                self.langfuse = Langfuse()
            except Exception as e:
                logger.warning(f"Failed to initialize Langfuse: {e}")
                self.langfuse = None

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags
        """
        metric = MetricValue(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {},
        )
        self._metrics.append(metric)

        # Send to Langfuse if available
        if self.langfuse:
            try:
                self.langfuse.score(
                    name=name,
                    value=value,
                    comment=f"{value} {unit}",
                )
            except Exception as e:
                logger.debug(f"Failed to send metric to Langfuse: {e}")

        logger.debug(f"Metric: {name}={value}{unit}")

    def start_trace(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start a timing trace.

        Args:
            name: Trace name
            metadata: Additional metadata

        Returns:
            Trace/span ID
        """
        import uuid
        span_id = str(uuid.uuid4())

        span = TraceSpan(
            span_id=span_id,
            name=name,
            start_time=datetime.utcnow(),
            metadata=metadata or {},
        )
        self._traces[span_id] = span

        # Create Langfuse trace if available
        if self.langfuse:
            try:
                self.langfuse.trace(
                    name=name,
                    id=span_id,
                    metadata=metadata,
                )
            except Exception as e:
                logger.debug(f"Failed to create Langfuse trace: {e}")

        return span_id

    def end_trace(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TraceSpan]:
        """
        End a timing trace.

        Args:
            span_id: Span ID to end
            status: Final status
            metadata: Additional metadata to add

        Returns:
            Completed TraceSpan or None
        """
        span = self._traces.get(span_id)
        if not span:
            logger.warning(f"Trace {span_id} not found")
            return None

        span.end_time = datetime.utcnow()
        span.duration_ms = int(
            (span.end_time - span.start_time).total_seconds() * 1000
        )
        span.status = status

        if metadata:
            span.metadata.update(metadata)

        # Record duration as metric
        self.record_metric(
            f"{span.name}_duration",
            span.duration_ms,
            "ms",
            {"status": status},
        )

        return span

    @asynccontextmanager
    async def trace_operation(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Context manager for tracing an operation.

        Usage:
            async with collector.trace_operation("my_operation") as span_id:
                # ... do work ...
        """
        span_id = self.start_trace(name, metadata)
        try:
            yield span_id
            self.end_trace(span_id, "completed")
        except Exception as e:
            self.end_trace(span_id, "failed", {"error": str(e)})
            raise

    def start_agent_metrics(
        self,
        agent_name: str,
        profile_id: str,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Start collecting metrics for an agent execution.

        Returns:
            Metrics ID for tracking
        """
        import uuid
        metrics_id = str(uuid.uuid4())

        self._agent_metrics[metrics_id] = AgentMetrics(
            agent_name=agent_name,
            profile_id=profile_id,
            session_id=session_id,
        )

        return metrics_id

    def record_llm_call(
        self,
        metrics_id: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
    ) -> None:
        """Record an LLM call."""
        metrics = self._agent_metrics.get(metrics_id)
        if metrics:
            metrics.llm_calls += 1
            metrics.llm_tokens_input += tokens_input
            metrics.llm_tokens_output += tokens_output

    def record_tool_call(self, metrics_id: str) -> None:
        """Record a tool call."""
        metrics = self._agent_metrics.get(metrics_id)
        if metrics:
            metrics.tool_calls += 1

    def record_retry(self, metrics_id: str) -> None:
        """Record a retry attempt."""
        metrics = self._agent_metrics.get(metrics_id)
        if metrics:
            metrics.retries += 1

    def record_quality_scores(
        self,
        metrics_id: str,
        quality_score: Optional[float] = None,
        voice_score: Optional[float] = None,
        personalization_score: Optional[float] = None,
    ) -> None:
        """
        Record quality scores.

        USP: Coaching quality tracking.
        """
        metrics = self._agent_metrics.get(metrics_id)
        if metrics:
            if quality_score is not None:
                metrics.quality_score = quality_score
            if voice_score is not None:
                metrics.voice_score = voice_score
            if personalization_score is not None:
                metrics.personalization_score = personalization_score

    def record_react_metrics(
        self,
        metrics_id: str,
        cycles: int,
        quality_improvement: float,
    ) -> None:
        """Record ReAct cycle metrics."""
        metrics = self._agent_metrics.get(metrics_id)
        if metrics:
            metrics.react_cycles = cycles
            metrics.quality_improvement = quality_improvement

    def record_error(
        self,
        metrics_id: str,
        error: str,
        is_warning: bool = False,
    ) -> None:
        """Record an error or warning."""
        metrics = self._agent_metrics.get(metrics_id)
        if metrics:
            if is_warning:
                metrics.warnings.append(error)
            else:
                metrics.errors.append(error)

    def finish_agent_metrics(
        self,
        metrics_id: str,
    ) -> Optional[AgentMetrics]:
        """
        Finish collecting agent metrics.

        Returns:
            Completed AgentMetrics
        """
        metrics = self._agent_metrics.get(metrics_id)
        if not metrics:
            return None

        metrics.end_time = datetime.utcnow()
        metrics.duration_ms = int(
            (metrics.end_time - metrics.start_time).total_seconds() * 1000
        )

        # Send to Langfuse
        self._send_agent_metrics_to_langfuse(metrics)

        return metrics

    def _send_agent_metrics_to_langfuse(
        self,
        metrics: AgentMetrics,
    ) -> None:
        """Send agent metrics to Langfuse."""
        if not self.langfuse:
            return

        try:
            # Create a generation for LLM metrics
            if metrics.llm_calls > 0:
                self.langfuse.generation(
                    name=f"{metrics.agent_name}_llm",
                    model="gpt-4",  # Or actual model used
                    usage={
                        "prompt_tokens": metrics.llm_tokens_input,
                        "completion_tokens": metrics.llm_tokens_output,
                    },
                )

            # Record quality scores
            if metrics.quality_score is not None:
                self.langfuse.score(
                    name="quality_score",
                    value=metrics.quality_score,
                    comment=f"Agent: {metrics.agent_name}",
                )

            if metrics.voice_score is not None:
                self.langfuse.score(
                    name="voice_score",
                    value=metrics.voice_score,
                )

            # Flush to ensure delivery
            self.langfuse.flush()

        except Exception as e:
            logger.warning(f"Failed to send metrics to Langfuse: {e}")

    def get_aggregate_metrics(
        self,
        agent_name: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get aggregate metrics.

        Args:
            agent_name: Filter by agent name
            since: Filter by time

        Returns:
            Aggregated metrics
        """
        metrics_list = list(self._agent_metrics.values())

        if agent_name:
            metrics_list = [m for m in metrics_list if m.agent_name == agent_name]

        if since:
            metrics_list = [m for m in metrics_list if m.start_time >= since]

        if not metrics_list:
            return {}

        # Aggregate
        total_duration = sum(m.duration_ms for m in metrics_list)
        total_llm_calls = sum(m.llm_calls for m in metrics_list)
        total_tokens = sum(m.llm_tokens_input + m.llm_tokens_output for m in metrics_list)
        total_errors = sum(len(m.errors) for m in metrics_list)

        quality_scores = [m.quality_score for m in metrics_list if m.quality_score]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None

        return {
            "count": len(metrics_list),
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration / len(metrics_list),
            "total_llm_calls": total_llm_calls,
            "total_tokens": total_tokens,
            "total_errors": total_errors,
            "avg_quality_score": avg_quality,
        }


# Global metrics collector instance
_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


# Convenience decorator for timing functions
def timed(name: Optional[str] = None):
    """
    Decorator to time function execution.

    Usage:
        @timed("my_function")
        async def my_function():
            ...
    """
    def decorator(func: Callable):
        metric_name = name or func.__name__

        async def wrapper(*args, **kwargs):
            collector = get_metrics_collector()
            async with collector.trace_operation(metric_name):
                return await func(*args, **kwargs)

        return wrapper
    return decorator


# Convenience function
def record_metric(
    name: str,
    value: float,
    unit: str = "",
    tags: Optional[Dict[str, str]] = None,
) -> None:
    """Quick helper to record a metric."""
    collector = get_metrics_collector()
    collector.record_metric(name, value, unit, tags)
