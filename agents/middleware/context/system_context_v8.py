"""
C3: System Context Pattern - Implementation

Application configuration and capability awareness.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List, Set
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentCapability(str, Enum):
    """Available agent capabilities."""
    ESSAY_REVIEW = "essay_review"
    ACTIVITY_PLANNING = "activity_planning"
    COLLEGE_RESEARCH = "college_research"
    GAME_PLAN_CREATION = "game_plan_creation"
    EXECUTION_TRACKING = "execution_tracking"
    AWARD_MATCHING = "award_matching"
    PROGRAM_MATCHING = "program_matching"
    COACHING = "coaching"
    RECOMMENDATIONS = "recommendations"


class IntegrationStatus(str, Enum):
    """External integration status."""
    ACTIVE = "active"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class IntegrationInfo(BaseModel):
    """Information about an external integration."""
    name: str
    status: IntegrationStatus = IntegrationStatus.ACTIVE
    last_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None
    health_check_url: Optional[str] = None


class SystemContext(BaseModel):
    """
    System-level context for capability awareness.

    Pattern C3: System Context

    GUARDRAILS:
    - NEW class - does not modify existing config
    - Singleton pattern for consistency
    """

    version: str = "8.0.0"
    environment: str = "production"

    # Available capabilities
    capabilities: Set[AgentCapability] = Field(
        default_factory=lambda: set(AgentCapability)
    )

    # Integration status
    integrations: Dict[str, IntegrationInfo] = Field(default_factory=dict)

    # System limits
    max_tokens_per_request: int = 8000
    max_context_window: int = 128000
    max_concurrent_requests: int = 10

    # Feature flags
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

    # Rate limits (requests per minute)
    rate_limits: Dict[str, int] = Field(default_factory=dict)

    # Degradation levels
    degradation_mode: bool = False
    degradation_reason: Optional[str] = None


class SystemContextProvider:
    """
    Provides system context to agents.

    Pattern C3: System Context Provider

    GUARDRAILS:
    - NEW class - singleton pattern
    - Does not modify existing providers
    """

    _instance: Optional["SystemContextProvider"] = None
    _context: Optional[SystemContext] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._context is None:
            self._context = self._load_context()

    def _load_context(self) -> SystemContext:
        """Load initial system context."""
        return SystemContext(
            version="8.0.0",
            environment="production",
            integrations={
                "openai": IntegrationInfo(name="OpenAI API"),
                "supabase": IntegrationInfo(name="Supabase"),
                "pinecone": IntegrationInfo(name="Pinecone"),
                "langfuse": IntegrationInfo(name="Langfuse"),
                "redis": IntegrationInfo(name="Redis"),
            },
            feature_flags={
                "enable_rag": True,
                "enable_web_search": True,
                "enable_llm_judge": True,
                "enable_reasoning_traces": True,
                "enable_shadow_mode": True,
                "enable_approval_gates": True,
            },
            rate_limits={
                "openai_gpt4": 60,
                "openai_gpt35": 200,
                "pinecone_query": 100,
                "supabase_rpc": 500,
            },
        )

    @property
    def context(self) -> SystemContext:
        """Get current system context."""
        return self._context

    def has_capability(self, capability: AgentCapability) -> bool:
        """
        Check if system has a capability.

        Args:
            capability: Capability to check

        Returns:
            True if capability is available
        """
        return capability in self._context.capabilities

    def is_integration_healthy(self, integration: str) -> bool:
        """
        Check if an integration is healthy.

        Args:
            integration: Integration name

        Returns:
            True if integration is active
        """
        info = self._context.integrations.get(integration)
        return info is not None and info.status == IntegrationStatus.ACTIVE

    def get_feature_flag(self, flag: str, default: bool = False) -> bool:
        """
        Get feature flag value.

        Args:
            flag: Flag name
            default: Default value if flag not found

        Returns:
            Flag value
        """
        return self._context.feature_flags.get(flag, default)

    def get_rate_limit(self, service: str, default: int = 60) -> int:
        """
        Get rate limit for a service.

        Args:
            service: Service name
            default: Default rate limit

        Returns:
            Requests per minute allowed
        """
        return self._context.rate_limits.get(service, default)

    async def update_integration_status(
        self,
        integration: str,
        status: IntegrationStatus,
        latency_ms: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        """
        Update integration status.

        Args:
            integration: Integration name
            status: New status
            latency_ms: Optional latency measurement
            error: Optional error message
        """
        if integration not in self._context.integrations:
            self._context.integrations[integration] = IntegrationInfo(
                name=integration
            )

        info = self._context.integrations[integration]
        info.status = status
        info.last_check = datetime.now(timezone.utc)
        info.latency_ms = latency_ms
        info.error_message = error

        if status != IntegrationStatus.ACTIVE:
            logger.warning(f"Integration {integration} status: {status}")

    def enable_degradation_mode(self, reason: str) -> None:
        """
        Enable system degradation mode.

        Args:
            reason: Reason for degradation
        """
        self._context.degradation_mode = True
        self._context.degradation_reason = reason
        logger.warning(f"Degradation mode enabled: {reason}")

    def disable_degradation_mode(self) -> None:
        """Disable system degradation mode."""
        self._context.degradation_mode = False
        self._context.degradation_reason = None
        logger.info("Degradation mode disabled")

    def set_feature_flag(self, flag: str, enabled: bool) -> None:
        """
        Set a feature flag.

        Args:
            flag: Flag name
            enabled: Whether to enable
        """
        self._context.feature_flags[flag] = enabled
        logger.info(f"Feature flag {flag} set to {enabled}")

    def disable_capability(self, capability: AgentCapability) -> None:
        """
        Disable a capability.

        Args:
            capability: Capability to disable
        """
        self._context.capabilities.discard(capability)
        logger.warning(f"Capability disabled: {capability}")

    def enable_capability(self, capability: AgentCapability) -> None:
        """
        Enable a capability.

        Args:
            capability: Capability to enable
        """
        self._context.capabilities.add(capability)
        logger.info(f"Capability enabled: {capability}")

    def get_context_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Get context dict for an agent.

        Args:
            agent_name: Name of requesting agent

        Returns:
            Context dict with relevant system info
        """
        return {
            "version": self._context.version,
            "environment": self._context.environment,
            "capabilities": [c.value for c in self._context.capabilities],
            "healthy_integrations": [
                name for name, info in self._context.integrations.items()
                if info.status == IntegrationStatus.ACTIVE
            ],
            "degraded_integrations": [
                name for name, info in self._context.integrations.items()
                if info.status == IntegrationStatus.DEGRADED
            ],
            "feature_flags": self._context.feature_flags,
            "limits": {
                "max_tokens": self._context.max_tokens_per_request,
                "max_context": self._context.max_context_window,
            },
            "degradation_mode": self._context.degradation_mode,
        }

    def get_health_report(self) -> Dict[str, Any]:
        """
        Get comprehensive health report.

        Returns:
            Health report dict
        """
        integrations = {}
        for name, info in self._context.integrations.items():
            integrations[name] = {
                "status": info.status.value,
                "last_check": info.last_check.isoformat(),
                "latency_ms": info.latency_ms,
                "error": info.error_message,
            }

        return {
            "version": self._context.version,
            "environment": self._context.environment,
            "degradation_mode": self._context.degradation_mode,
            "degradation_reason": self._context.degradation_reason,
            "integrations": integrations,
            "capabilities_count": len(self._context.capabilities),
            "features_enabled": sum(1 for v in self._context.feature_flags.values() if v),
        }
