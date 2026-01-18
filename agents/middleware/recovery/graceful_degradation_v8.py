"""
H2: Graceful Degradation Pattern - Implementation

Maintain functionality when components fail.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Status of a service."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class DegradationLevel(str, Enum):
    """Levels of degradation."""
    NONE = "none"
    PARTIAL = "partial"
    FALLBACK = "fallback"
    MINIMAL = "minimal"


class ServiceHealth(BaseModel):
    """Health status of a service."""
    service_name: str
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_count: int = 0
    consecutive_failures: int = 0
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None


class DegradationState(BaseModel):
    """Current degradation state."""
    level: DegradationLevel = DegradationLevel.NONE
    degraded_services: List[str] = Field(default_factory=list)
    unavailable_services: List[str] = Field(default_factory=list)
    active_fallbacks: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    reason: Optional[str] = None


class FallbackConfig(BaseModel):
    """Configuration for a fallback."""
    service_name: str
    fallback_name: str
    trigger_after_failures: int = 3
    recovery_after_successes: int = 5
    fallback_enabled: bool = True


class GracefulDegradationManager:
    """
    Manages graceful degradation when services fail.

    Pattern H2: Graceful Degradation

    GUARDRAILS:
    - NEW class - does not modify existing recovery
    - Provides fallback mechanisms
    - Automatic recovery when services return
    """

    def __init__(
        self,
        fallback_configs: Optional[List[FallbackConfig]] = None,
        health_check_interval: int = 30,
    ):
        """
        Initialize degradation manager.

        Args:
            fallback_configs: Fallback configurations
            health_check_interval: Seconds between health checks
        """
        self.configs = {c.service_name: c for c in (fallback_configs or [])}
        self.health_interval = health_check_interval
        self._service_health: Dict[str, ServiceHealth] = {}
        self._degradation_state = DegradationState()
        self._fallback_handlers: Dict[str, Callable] = {}
        self._recovery_counts: Dict[str, int] = {}

    def register_fallback(
        self,
        service_name: str,
        fallback_handler: Callable[[Dict[str, Any]], Awaitable[Any]],
    ) -> None:
        """
        Register a fallback handler for a service.

        Args:
            service_name: Service to provide fallback for
            fallback_handler: Async function to call as fallback
        """
        self._fallback_handlers[service_name] = fallback_handler
        logger.info(f"Registered fallback for {service_name}")

    async def call_with_fallback(
        self,
        service_name: str,
        primary_func: Callable[[], Awaitable[Any]],
        fallback_args: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Call a service with automatic fallback on failure.

        Args:
            service_name: Name of the service
            primary_func: Primary function to call
            fallback_args: Arguments for fallback handler

        Returns:
            Result from primary or fallback
        """
        health = self._get_or_create_health(service_name)

        # Check if we should use fallback
        config = self.configs.get(service_name, FallbackConfig(
            service_name=service_name,
            fallback_name=f"{service_name}_fallback",
        ))

        use_fallback = (
            health.consecutive_failures >= config.trigger_after_failures
            and config.fallback_enabled
            and service_name in self._fallback_handlers
        )

        if use_fallback:
            logger.info(f"Using fallback for {service_name}")
            try:
                result = await self._fallback_handlers[service_name](
                    fallback_args or {}
                )
                self._record_fallback_use(service_name)
                return result
            except Exception as e:
                logger.error(f"Fallback also failed for {service_name}: {e}")
                raise

        # Try primary
        try:
            start = datetime.now(timezone.utc)
            result = await primary_func()
            elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

            self._record_success(service_name, elapsed)
            return result

        except Exception as e:
            self._record_failure(service_name, str(e))

            # Try fallback if available
            if service_name in self._fallback_handlers:
                logger.warning(f"Primary failed, trying fallback for {service_name}")
                try:
                    result = await self._fallback_handlers[service_name](
                        fallback_args or {}
                    )
                    self._record_fallback_use(service_name)
                    return result
                except Exception as fe:
                    logger.error(f"Fallback also failed: {fe}")

            raise

    def _get_or_create_health(self, service_name: str) -> ServiceHealth:
        """Get or create health record for service."""
        if service_name not in self._service_health:
            self._service_health[service_name] = ServiceHealth(
                service_name=service_name
            )
        return self._service_health[service_name]

    def _record_success(self, service_name: str, latency_ms: int) -> None:
        """Record successful service call."""
        health = self._get_or_create_health(service_name)
        health.status = ServiceStatus.HEALTHY
        health.last_check = datetime.now(timezone.utc)
        health.consecutive_failures = 0
        health.latency_ms = latency_ms

        # Check for recovery
        self._recovery_counts[service_name] = self._recovery_counts.get(
            service_name, 0
        ) + 1

        config = self.configs.get(service_name)
        if config and self._recovery_counts.get(service_name, 0) >= config.recovery_after_successes:
            self._recover_service(service_name)

    def _record_failure(self, service_name: str, error: str) -> None:
        """Record service failure."""
        health = self._get_or_create_health(service_name)
        health.error_count += 1
        health.consecutive_failures += 1
        health.last_check = datetime.now(timezone.utc)
        health.error_message = error

        self._recovery_counts[service_name] = 0

        config = self.configs.get(service_name, FallbackConfig(
            service_name=service_name,
            fallback_name=f"{service_name}_fallback",
        ))

        if health.consecutive_failures >= config.trigger_after_failures:
            health.status = ServiceStatus.UNAVAILABLE
            self._update_degradation_state()

    def _record_fallback_use(self, service_name: str) -> None:
        """Record that fallback was used."""
        if service_name not in self._degradation_state.active_fallbacks:
            self._degradation_state.active_fallbacks.append(service_name)

    def _recover_service(self, service_name: str) -> None:
        """Mark service as recovered."""
        logger.info(f"Service {service_name} recovered")

        if service_name in self._degradation_state.unavailable_services:
            self._degradation_state.unavailable_services.remove(service_name)
        if service_name in self._degradation_state.degraded_services:
            self._degradation_state.degraded_services.remove(service_name)
        if service_name in self._degradation_state.active_fallbacks:
            self._degradation_state.active_fallbacks.remove(service_name)

        self._recovery_counts[service_name] = 0
        self._update_degradation_state()

    def _update_degradation_state(self) -> None:
        """Update overall degradation state."""
        unavailable = [
            name for name, health in self._service_health.items()
            if health.status == ServiceStatus.UNAVAILABLE
        ]
        degraded = [
            name for name, health in self._service_health.items()
            if health.status == ServiceStatus.DEGRADED
        ]

        self._degradation_state.unavailable_services = unavailable
        self._degradation_state.degraded_services = degraded

        if unavailable:
            self._degradation_state.level = DegradationLevel.FALLBACK
            self._degradation_state.reason = f"Services unavailable: {', '.join(unavailable)}"
        elif degraded:
            self._degradation_state.level = DegradationLevel.PARTIAL
            self._degradation_state.reason = f"Services degraded: {', '.join(degraded)}"
        else:
            self._degradation_state.level = DegradationLevel.NONE
            self._degradation_state.reason = None

        if self._degradation_state.level != DegradationLevel.NONE:
            if not self._degradation_state.started_at:
                self._degradation_state.started_at = datetime.now(timezone.utc)
        else:
            self._degradation_state.started_at = None

    def get_degradation_state(self) -> DegradationState:
        """Get current degradation state."""
        return self._degradation_state

    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health status of a service."""
        return self._service_health.get(service_name)

    def get_all_health(self) -> Dict[str, ServiceHealth]:
        """Get health status of all services."""
        return dict(self._service_health)

    def is_degraded(self) -> bool:
        """Check if system is currently degraded."""
        return self._degradation_state.level != DegradationLevel.NONE


# Default fallback implementations for IvyLevel
class IvyLevelFallbacks:
    """Default fallback implementations."""

    @staticmethod
    async def llm_fallback(args: Dict[str, Any]) -> str:
        """Fallback when LLM is unavailable."""
        return (
            "I apologize, but I'm experiencing some technical difficulties. "
            "Please try again in a moment, or contact your coach directly."
        )

    @staticmethod
    async def database_fallback(args: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback when database is unavailable."""
        return {
            "status": "cached",
            "message": "Using cached data",
            "data": args.get("cached_data", {}),
        }

    @staticmethod
    async def embedding_fallback(args: Dict[str, Any]) -> List[float]:
        """Fallback when embedding service is unavailable."""
        # Return zero vector
        dimension = args.get("dimension", 1536)
        return [0.0] * dimension
