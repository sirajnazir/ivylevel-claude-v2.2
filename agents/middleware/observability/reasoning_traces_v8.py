"""
J1: Reasoning Traces Pattern - Implementation

Capture and store agent reasoning for debugging and improvement.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class TraceEventType(str, Enum):
    """Types of trace events."""
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    DECISION = "decision"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    REFLECTION = "reflection"
    ERROR = "error"


class TraceEvent(BaseModel):
    """A single event in a reasoning trace."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: TraceEventType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    parent_event_id: Optional[str] = None


class ReasoningTrace(BaseModel):
    """Complete reasoning trace for an agent interaction."""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    session_id: str
    agent_name: str
    input_message: str
    events: List[TraceEvent] = Field(default_factory=list)
    final_output: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    total_duration_ms: int = 0


class ReasoningTraceCollector:
    """
    Collects reasoning traces from agents.

    Pattern J1: Reasoning Traces

    GUARDRAILS:
    - NEW class - does not modify existing tracing
    - Integrates with Langfuse when available
    - Falls back to local storage
    """

    def __init__(
        self,
        supabase_client=None,
        langfuse_client=None,
        max_events_per_trace: int = 100,
    ):
        """
        Initialize trace collector.

        Args:
            supabase_client: For persistence
            langfuse_client: For Langfuse integration
            max_events_per_trace: Maximum events to store
        """
        self.supabase = supabase_client
        self.langfuse = langfuse_client
        self.max_events = max_events_per_trace
        self._active_traces: Dict[str, ReasoningTrace] = {}

    def start_trace(
        self,
        profile_id: str,
        session_id: str,
        agent_name: str,
        input_message: str,
    ) -> ReasoningTrace:
        """
        Start a new reasoning trace.

        Args:
            profile_id: Student profile
            session_id: Session ID
            agent_name: Agent name
            input_message: Input that triggered reasoning

        Returns:
            New ReasoningTrace
        """
        trace = ReasoningTrace(
            profile_id=profile_id,
            session_id=session_id,
            agent_name=agent_name,
            input_message=input_message,
        )

        self._active_traces[trace.trace_id] = trace

        # Start Langfuse trace if available
        if self.langfuse:
            try:
                self.langfuse.trace(
                    id=trace.trace_id,
                    name=f"{agent_name}_reasoning",
                    input=input_message,
                    metadata={
                        "profile_id": profile_id,
                        "session_id": session_id,
                    },
                )
            except Exception as e:
                logger.warning(f"Langfuse trace start failed: {e}")

        logger.debug(f"Started trace {trace.trace_id}")
        return trace

    def add_event(
        self,
        trace_id: str,
        event_type: TraceEventType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_event_id: Optional[str] = None,
    ) -> Optional[TraceEvent]:
        """
        Add event to a trace.

        Args:
            trace_id: Trace to add to
            event_type: Type of event
            content: Event content
            metadata: Additional metadata
            parent_event_id: Parent event if nested

        Returns:
            Added TraceEvent or None
        """
        trace = self._active_traces.get(trace_id)
        if not trace:
            logger.warning(f"Trace {trace_id} not found")
            return None

        if len(trace.events) >= self.max_events:
            logger.warning(f"Trace {trace_id} reached max events")
            return None

        event = TraceEvent(
            event_type=event_type,
            content=content,
            metadata=metadata or {},
            parent_event_id=parent_event_id,
        )

        trace.events.append(event)

        # Log to Langfuse
        if self.langfuse:
            try:
                span_type = "span"
                if event_type == TraceEventType.TOOL_CALL:
                    span_type = "generation"

                self.langfuse.span(
                    trace_id=trace_id,
                    name=event_type.value,
                    input=content,
                    metadata=metadata,
                )
            except Exception as e:
                logger.warning(f"Langfuse span failed: {e}")

        return event

    def add_thought(
        self,
        trace_id: str,
        thought: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TraceEvent]:
        """Add a thought event."""
        return self.add_event(
            trace_id=trace_id,
            event_type=TraceEventType.THOUGHT,
            content=thought,
            metadata=metadata,
        )

    def add_action(
        self,
        trace_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TraceEvent]:
        """Add an action event."""
        return self.add_event(
            trace_id=trace_id,
            event_type=TraceEventType.ACTION,
            content=action,
            metadata=metadata,
        )

    def add_tool_call(
        self,
        trace_id: str,
        tool_name: str,
        tool_input: Dict[str, Any],
    ) -> Optional[TraceEvent]:
        """Add a tool call event."""
        return self.add_event(
            trace_id=trace_id,
            event_type=TraceEventType.TOOL_CALL,
            content=f"Calling {tool_name}",
            metadata={"tool": tool_name, "input": tool_input},
        )

    def add_tool_result(
        self,
        trace_id: str,
        tool_name: str,
        result: Any,
        parent_event_id: Optional[str] = None,
    ) -> Optional[TraceEvent]:
        """Add a tool result event."""
        return self.add_event(
            trace_id=trace_id,
            event_type=TraceEventType.TOOL_RESULT,
            content=f"Result from {tool_name}",
            metadata={"tool": tool_name, "result": str(result)[:500]},
            parent_event_id=parent_event_id,
        )

    def add_reflection(
        self,
        trace_id: str,
        reflection: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TraceEvent]:
        """Add a reflection event."""
        return self.add_event(
            trace_id=trace_id,
            event_type=TraceEventType.REFLECTION,
            content=reflection,
            metadata=metadata,
        )

    def add_error(
        self,
        trace_id: str,
        error: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TraceEvent]:
        """Add an error event."""
        return self.add_event(
            trace_id=trace_id,
            event_type=TraceEventType.ERROR,
            content=error,
            metadata=metadata,
        )

    async def end_trace(
        self,
        trace_id: str,
        output: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> Optional[ReasoningTrace]:
        """
        End a trace and persist it.

        Args:
            trace_id: Trace to end
            output: Final output
            success: Whether reasoning succeeded
            error: Error message if failed

        Returns:
            Completed trace
        """
        trace = self._active_traces.get(trace_id)
        if not trace:
            logger.warning(f"Trace {trace_id} not found")
            return None

        trace.completed_at = datetime.now(timezone.utc)
        trace.final_output = output
        trace.success = success
        trace.error_message = error
        trace.total_duration_ms = int(
            (trace.completed_at - trace.started_at).total_seconds() * 1000
        )

        # Persist to database
        await self._persist_trace(trace)

        # End Langfuse trace
        if self.langfuse:
            try:
                self.langfuse.trace(
                    id=trace_id,
                    output=output,
                    status="SUCCESS" if success else "ERROR",
                )
            except Exception as e:
                logger.warning(f"Langfuse trace end failed: {e}")

        # Remove from active
        self._active_traces.pop(trace_id, None)

        logger.debug(
            f"Ended trace {trace_id}: {len(trace.events)} events, "
            f"{trace.total_duration_ms}ms"
        )

        return trace

    async def _persist_trace(self, trace: ReasoningTrace) -> None:
        """Persist trace to database."""
        if not self.supabase:
            return

        try:
            self.supabase.table("phase2b_reasoning_traces").insert({
                "trace_id": trace.trace_id,
                "profile_id": trace.profile_id,
                "session_id": trace.session_id,
                "agent_name": trace.agent_name,
                "input_message": trace.input_message,
                "final_output": trace.final_output,
                "success": trace.success,
                "total_events": len(trace.events),
                "tool_calls": sum(
                    1 for e in trace.events
                    if e.event_type == TraceEventType.TOOL_CALL
                ),
                "reflections": sum(
                    1 for e in trace.events
                    if e.event_type == TraceEventType.REFLECTION
                ),
                "total_duration_ms": trace.total_duration_ms,
                "events": [e.model_dump() for e in trace.events],
            }).execute()
        except Exception as e:
            logger.error(f"Failed to persist trace: {e}")

    def get_active_trace(self, trace_id: str) -> Optional[ReasoningTrace]:
        """Get an active trace."""
        return self._active_traces.get(trace_id)

    def get_trace_summary(self, trace: ReasoningTrace) -> Dict[str, Any]:
        """Get summary of a trace."""
        return {
            "trace_id": trace.trace_id,
            "agent": trace.agent_name,
            "events": len(trace.events),
            "event_types": {
                et.value: sum(1 for e in trace.events if e.event_type == et)
                for et in TraceEventType
            },
            "duration_ms": trace.total_duration_ms,
            "success": trace.success,
        }
