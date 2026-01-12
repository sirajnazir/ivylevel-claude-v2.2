"""
Event Bus for Cross-Agent Communication in IvyQuest v13.0

Enables pub/sub pattern for agents to communicate and coordinate.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Any, Awaitable
import asyncio
import logging

logger = logging.getLogger(__name__)


class EventTypes:
    """Standard event types for agent communication."""

    # Narrative events
    NARRATIVE_SYNTHESIZED = "narrative.synthesized"
    NARRATIVE_UPDATED = "narrative.updated"

    # Awards events
    AWARDS_PORTFOLIO_BUILT = "awards.portfolio_built"
    AWARDS_PROBABILITY_CHANGED = "awards.probability_changed"
    AWARD_APPLICATION_STARTED = "awards.application_started"

    # Time events
    TIME_AUDIT_COMPLETE = "time.audit_complete"
    WEEKLY_PLAN_GENERATED = "time.weekly_plan_generated"
    SCHEDULE_CONFLICT_DETECTED = "time.schedule_conflict"

    # Crisis events
    CRISIS_DETECTED = "crisis.detected"
    CRISIS_RESPONDING = "crisis.responding"
    CRISIS_RESOLVED = "crisis.resolved"

    # Opportunity events
    OPPORTUNITY_MATCHED = "opportunity.matched"
    OPPORTUNITY_DEADLINE_APPROACHING = "opportunity.deadline_approaching"
    OPPORTUNITY_REDIRECT_SUGGESTED = "opportunity.redirect_suggested"

    # Memory events
    MEMORY_CONSOLIDATED = "memory.consolidated"
    MEMORY_THRESHOLD_REACHED = "memory.threshold_reached"

    # HITL events
    HITL_REVIEW_REQUESTED = "hitl.review_requested"
    HITL_REVIEW_COMPLETE = "hitl.review_complete"

    # Agent lifecycle events
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"


@dataclass
class AgentEvent:
    """
    An event emitted by an agent.

    Attributes:
        source_agent: ID of the agent that emitted the event
        event_type: Type of event (from EventTypes)
        payload: Event data
        profile_id: Associated student profile
        timestamp: When the event occurred
        correlation_id: ID to track related events
    """
    source_agent: str
    event_type: str
    payload: dict
    profile_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: str | None = None

    def to_dict(self) -> dict:
        """Convert to serializable dictionary."""
        return {
            "source_agent": self.source_agent,
            "event_type": self.event_type,
            "payload": self.payload,
            "profile_id": self.profile_id,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }


# Type for event handlers
EventHandler = Callable[[AgentEvent], Awaitable[Any]]


class EventBus:
    """
    Event-driven communication system for agents.

    Supports:
    - Subscribe to specific event types
    - Publish events to all subscribers
    - Event history for replay/debugging
    - Async handler execution
    """

    def __init__(self, max_history: int = 1000):
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._event_history: list[AgentEvent] = []
        self._max_history = max_history
        self._lock = asyncio.Lock()

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> Callable[[], None]:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Async function to call when event occurs

        Returns:
            Unsubscribe function
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type}")

        # Return unsubscribe function
        def unsubscribe():
            if handler in self._subscribers.get(event_type, []):
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed handler from {event_type}")

        return unsubscribe

    def subscribe_all(
        self,
        handler: EventHandler,
    ) -> Callable[[], None]:
        """
        Subscribe to ALL events.

        Args:
            handler: Async function to call for any event

        Returns:
            Unsubscribe function
        """
        return self.subscribe("*", handler)

    async def publish(
        self,
        event: AgentEvent,
    ) -> list[Any]:
        """
        Publish an event to all subscribers.

        Args:
            event: Event to publish

        Returns:
            list: Results from all handlers (including exceptions)
        """
        async with self._lock:
            # Store in history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]

        logger.info(f"Publishing event: {event.event_type} from {event.source_agent}")

        # Get handlers for this event type and wildcard subscribers
        handlers = (
            self._subscribers.get(event.event_type, []) +
            self._subscribers.get("*", [])
        )

        if not handlers:
            return []

        # Execute all handlers concurrently
        results = await asyncio.gather(
            *[self._safe_call(handler, event) for handler in handlers],
            return_exceptions=True,
        )

        # Log any exceptions
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Event handler failed: {result}")

        return results

    async def _safe_call(
        self,
        handler: EventHandler,
        event: AgentEvent,
    ) -> Any:
        """Safely call an event handler with error handling."""
        try:
            return await handler(event)
        except Exception as e:
            logger.error(f"Handler {handler.__name__} failed: {e}")
            return e

    def get_history(
        self,
        profile_id: str | None = None,
        event_types: list[str] | None = None,
        source_agent: str | None = None,
        limit: int = 100,
    ) -> list[AgentEvent]:
        """
        Get event history with optional filters.

        Args:
            profile_id: Filter by profile
            event_types: Filter by event types
            source_agent: Filter by source agent
            limit: Max events to return

        Returns:
            list[AgentEvent]: Matching events (newest first)
        """
        events = self._event_history.copy()

        if profile_id:
            events = [e for e in events if e.profile_id == profile_id]

        if event_types:
            events = [e for e in events if e.event_type in event_types]

        if source_agent:
            events = [e for e in events if e.source_agent == source_agent]

        # Return newest first
        events.reverse()
        return events[:limit]

    def get_correlated_events(
        self,
        correlation_id: str,
    ) -> list[AgentEvent]:
        """
        Get all events with the same correlation ID.

        Useful for tracing a chain of related events.
        """
        return [
            e for e in self._event_history
            if e.correlation_id == correlation_id
        ]

    def clear_history(self) -> int:
        """Clear event history. Returns count of cleared events."""
        count = len(self._event_history)
        self._event_history = []
        return count

    def get_subscriber_count(self, event_type: str | None = None) -> dict[str, int]:
        """Get count of subscribers per event type."""
        if event_type:
            return {event_type: len(self._subscribers.get(event_type, []))}
        return {k: len(v) for k, v in self._subscribers.items()}


# Global event bus instance (can be replaced with dependency injection)
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def set_event_bus(event_bus: EventBus) -> None:
    """Set the global event bus instance."""
    global _global_event_bus
    _global_event_bus = event_bus


# Convenience decorators for event handlers
def on_event(event_type: str):
    """
    Decorator to register a function as an event handler.

    Usage:
        @on_event(EventTypes.CRISIS_DETECTED)
        async def handle_crisis(event: AgentEvent):
            ...
    """
    def decorator(func: EventHandler) -> EventHandler:
        get_event_bus().subscribe(event_type, func)
        return func
    return decorator


def on_any_event():
    """
    Decorator to register a function as a handler for all events.

    Usage:
        @on_any_event()
        async def log_all_events(event: AgentEvent):
            logger.info(f"Event: {event.event_type}")
    """
    def decorator(func: EventHandler) -> EventHandler:
        get_event_bus().subscribe_all(func)
        return func
    return decorator
