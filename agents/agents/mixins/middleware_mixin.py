"""
Middleware Integration Mixin for BaseAgent
==========================================
Provides middleware integration for all agents via mixin pattern.
This keeps BaseAgent clean while adding all 40 patterns.

v8.0 - Full integration with Phase 2B patterns.

Usage:
    from agents.mixins import MiddlewareIntegrationMixin

    class MyAgent(BaseAgent, MiddlewareIntegrationMixin):
        def __init__(self):
            super().__init__(name="MyAgent", autonomy_level=AutonomyLevel.MEDIUM)
            self.init_middleware(supabase_client=self.db, llm_client=self.llm)
"""

from typing import Dict, Any, Optional, List, Callable, TypeVar
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import middleware - graceful fallback if not available
try:
    from middleware import MiddlewareStack, create_middleware, AgentContext
    from middleware.observability.reasoning_traces_v8 import ReasoningTrace
    from middleware.quality.quality_scoring_v8 import QualityScore
    from middleware.recovery.retry_logic_v8 import RetryConfig, CircuitBreakerOpen
    MIDDLEWARE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Middleware import failed: {e}")
    MIDDLEWARE_AVAILABLE = False
    MiddlewareStack = None
    AgentContext = None
    ReasoningTrace = None
    QualityScore = None
    RetryConfig = None
    CircuitBreakerOpen = None

T = TypeVar("T")


class MiddlewareIntegrationMixin:
    """
    Mixin that adds middleware integration to any agent.

    This provides a clean interface to all 40 middleware patterns without
    requiring changes to BaseAgent.

    Attributes:
        middleware_available (bool): Class-level flag indicating if middleware is available
        _middleware: Instance of MiddlewareStack (or None)

    Example:
        class ExecutionAgent(BaseAgent, MiddlewareIntegrationMixin):
            def __init__(self):
                super().__init__(name="Execution", autonomy_level=AutonomyLevel.MEDIUM)
                self.init_middleware(supabase_client=self.db)

            async def process(self, profile_id: str, **kwargs):
                trace_id = self.start_reasoning_trace(profile_id, "session", "input")
                try:
                    async with self.with_middleware_context(profile_id) as ctx:
                        result = await self._do_work(ctx)
                        return self.middleware_finalize(result)
                finally:
                    await self.end_reasoning_trace(trace_id)
    """

    # Class-level flag
    middleware_available = MIDDLEWARE_AVAILABLE

    def init_middleware(
        self,
        supabase_client=None,
        redis_client=None,
        llm_client=None,
        langfuse_client=None,
        notify_approval: Optional[Callable] = None,
        notify_shadow: Optional[Callable] = None,
    ):
        """
        Initialize middleware stack.

        Call this in __init__ after super().__init__().

        Args:
            supabase_client: Supabase client for data access
            redis_client: Redis client for working memory
            llm_client: LLM client for reasoning
            langfuse_client: Langfuse client for observability
            notify_approval: Callback for approval notifications
            notify_shadow: Callback for shadow review notifications
        """
        if not MIDDLEWARE_AVAILABLE:
            self._middleware = None
            logger.info(f"[{getattr(self, 'name', 'Agent')}] Middleware not available")
            return

        try:
            self._middleware = MiddlewareStack(
                supabase_client=supabase_client or getattr(self, 'db', None),
                redis_client=redis_client,
                llm_client=llm_client or getattr(self, 'llm', None),
                langfuse_client=langfuse_client,
                notify_approval=notify_approval,
                notify_shadow=notify_shadow,
            )
            logger.info(f"[{getattr(self, 'name', 'Agent')}] Middleware v8 initialized")
        except Exception as e:
            logger.warning(f"[{getattr(self, 'name', 'Agent')}] Middleware init failed: {e}")
            self._middleware = None

    @property
    def middleware(self) -> Optional["MiddlewareStack"]:
        """Get middleware stack (may be None if not available)."""
        return getattr(self, '_middleware', None)

    # =========================================
    # CONTEXT MANAGEMENT
    # =========================================

    def with_middleware_context(
        self,
        profile_id: str,
        session_id: Optional[str] = None,
        task_type: str = "general",
    ):
        """
        Async context manager for middleware-wrapped execution.

        Provides AgentContext with student, temporal, task, and working_memory.

        Args:
            profile_id: Student's profile ID
            session_id: Session ID (auto-generated if not provided)
            task_type: Type of task (general, gameplan, execution, etc.)

        Returns:
            Async context manager yielding AgentContext

        Example:
            async with self.with_middleware_context(profile_id) as ctx:
                if ctx:
                    student = ctx.student
                    temporal = ctx.temporal
                result = await self._do_work()
                return self.middleware_finalize(result)
        """
        return _MiddlewareContextWrapper(
            middleware=self._middleware,
            agent_name=getattr(self, 'name', 'unknown'),
            profile_id=profile_id,
            session_id=session_id,
            task_type=task_type,
        )

    def middleware_finalize(
        self,
        result: Dict[str, Any],
        output_type: str = "general",
    ) -> Dict[str, Any]:
        """
        Finalize result with middleware validation and guardrails.

        Adds _validation metadata to result.

        Args:
            result: Agent result to finalize
            output_type: Type of output for validation rules

        Returns:
            Finalized result with _validation metadata
        """
        if self._middleware:
            try:
                return self._middleware.finalize(result, output_type)
            except Exception as e:
                logger.warning(f"Middleware finalize failed: {e}")
        return result

    # =========================================
    # J1: REASONING TRACES
    # =========================================

    def start_reasoning_trace(
        self,
        profile_id: str,
        session_id: str,
        input_message: str,
    ) -> Optional[str]:
        """
        Start a reasoning trace for observability.

        Args:
            profile_id: Student's profile ID
            session_id: Session ID
            input_message: Initial input that triggered this execution

        Returns:
            trace_id (str) or None if not available
        """
        if not self._middleware:
            return None
        try:
            trace = self._middleware.start_trace(
                profile_id=profile_id,
                session_id=session_id,
                agent_name=getattr(self, 'name', 'unknown'),
                input_message=input_message,
            )
            return trace.trace_id
        except Exception as e:
            logger.warning(f"start_trace failed: {e}")
            return None

    def add_thought(
        self,
        trace_id: Optional[str],
        thought: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a thought to the active reasoning trace.

        Args:
            trace_id: Trace ID from start_reasoning_trace
            thought: The thought/reasoning step
            metadata: Optional metadata
        """
        if self._middleware and trace_id:
            try:
                self._middleware.add_trace_thought(trace_id, thought, metadata)
            except Exception:
                pass

    def add_action(
        self,
        trace_id: Optional[str],
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add an action to the active reasoning trace.

        Args:
            trace_id: Trace ID from start_reasoning_trace
            action: The action taken
            metadata: Optional metadata
        """
        if self._middleware and trace_id:
            try:
                self._middleware.add_trace_action(trace_id, action, metadata)
            except Exception:
                pass

    async def end_reasoning_trace(
        self,
        trace_id: Optional[str],
        output: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """
        End a reasoning trace.

        Args:
            trace_id: Trace ID from start_reasoning_trace
            output: Final output summary
            success: Whether execution succeeded
            error: Error message if failed
        """
        if self._middleware and trace_id:
            try:
                await self._middleware.end_trace(trace_id, output, success, error)
            except Exception:
                pass

    # =========================================
    # H3: RETRY LOGIC
    # =========================================

    async def execute_with_retry(
        self,
        func: Callable,
        max_retries: int = 3,
        *args,
        **kwargs,
    ):
        """
        Execute function with automatic retry logic.

        Args:
            func: Async function to execute
            max_retries: Maximum retry attempts
            *args, **kwargs: Arguments to pass to func

        Returns:
            Result from func

        Raises:
            Original exception after max retries exceeded
        """
        if not self._middleware:
            return await func(*args, **kwargs)

        try:
            config = RetryConfig(max_retries=max_retries) if RetryConfig else None
            return await self._middleware.execute_with_retry(func, config, *args, **kwargs)
        except Exception:
            # Fall back to direct call on middleware error
            return await func(*args, **kwargs)

    # =========================================
    # H2: GRACEFUL DEGRADATION
    # =========================================

    async def call_with_fallback(
        self,
        service_name: str,
        primary_func: Callable,
        *args,
        **kwargs,
    ):
        """
        Call function with automatic fallback on failure.

        Args:
            service_name: Name of the service (for fallback lookup)
            primary_func: Primary function to try
            *args, **kwargs: Arguments to pass

        Returns:
            Result from primary_func or fallback
        """
        if not self._middleware:
            return await primary_func(*args, **kwargs)

        return await self._middleware.call_with_fallback(
            service_name, primary_func, *args, **kwargs
        )

    # =========================================
    # E4: QUALITY SCORING
    # =========================================

    async def score_quality(
        self,
        content: str,
        content_type: str = "general",
        use_llm: bool = False,
    ) -> Optional["QualityScore"]:
        """
        Score content quality.

        Args:
            content: Content to score
            content_type: Type of content
            use_llm: Whether to use LLM for scoring

        Returns:
            QualityScore or None if not available
        """
        if not self._middleware:
            return None
        try:
            return await self._middleware.score_quality(content, content_type, use_llm)
        except Exception as e:
            logger.warning(f"score_quality failed: {e}")
            return None

    # =========================================
    # E5: COHERENCE CHECKING
    # =========================================

    async def check_coherence(
        self,
        responses: List[str],
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Check coherence across multiple responses.

        Args:
            responses: List of responses to check
            context: Optional context

        Returns:
            CoherenceResult or None
        """
        if not self._middleware:
            return None
        try:
            return await self._middleware.check_coherence(responses, context)
        except Exception as e:
            logger.warning(f"check_coherence failed: {e}")
            return None

    # =========================================
    # J3: AUDIT TRAIL
    # =========================================

    async def audit_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        success: bool = True,
    ):
        """
        Log an action to the audit trail.

        Args:
            action: Action performed
            resource_type: Type of resource affected
            resource_id: ID of resource
            details: Additional details
            session_id: Session ID
            success: Whether action succeeded
        """
        if not self._middleware:
            return
        try:
            await self._middleware.audit_agent_action(
                agent_name=getattr(self, 'name', 'unknown'),
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                session_id=session_id,
                success=success,
            )
        except Exception:
            pass

    # =========================================
    # J4: MONITORING
    # =========================================

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Record a metric.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags
        """
        if not self._middleware:
            return
        try:
            self._middleware.record_metric(name, value, tags=tags)
        except Exception:
            pass

    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """
        Get a timer context manager for measuring durations.

        Args:
            name: Timer name
            tags: Optional tags

        Returns:
            Context manager or no-op
        """
        if self._middleware:
            try:
                return self._middleware.timer(name, tags)
            except Exception:
                pass
        # Return no-op context manager
        return _NoOpTimer()

    # =========================================
    # C1: SESSION CONTEXT
    # =========================================

    async def get_session(self, session_id: str, profile_id: str):
        """
        Get session context.

        Args:
            session_id: Session ID
            profile_id: Profile ID

        Returns:
            SessionContext or None
        """
        if not self._middleware:
            return None
        try:
            return await self._middleware.get_session_context(session_id, profile_id)
        except Exception:
            return None

    async def add_to_session(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add message to session.

        Args:
            session_id: Session ID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        if not self._middleware:
            return
        try:
            await self._middleware.add_session_message(session_id, role, content, metadata)
        except Exception:
            pass

    # =========================================
    # C3: SYSTEM CONTEXT
    # =========================================

    def check_integration_health(self, service: str) -> bool:
        """
        Check if an integration is healthy.

        Args:
            service: Service name

        Returns:
            True if healthy, False otherwise
        """
        if not self._middleware:
            return True  # Assume healthy if no middleware
        try:
            return self._middleware.check_integration_health(service)
        except Exception:
            return True

    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature: Feature name

        Returns:
            True if enabled, False otherwise
        """
        if not self._middleware:
            return False
        try:
            return self._middleware.is_feature_enabled(feature)
        except Exception:
            return False

    # =========================================
    # E6: GUARDRAILS
    # =========================================

    def check_guardrails(
        self,
        content: str,
        is_input: bool = False,
    ) -> bool:
        """
        Check content against guardrails.

        Args:
            content: Content to check
            is_input: Whether this is input (vs output)

        Returns:
            True if passed, False if blocked
        """
        if not self._middleware:
            return True
        try:
            results = self._middleware.check_guardrails(content, is_input)
            return all(r.passed for r in results)
        except Exception:
            return True

    # =========================================
    # G3: ESCALATION
    # =========================================

    def check_escalation(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[tuple]:
        """
        Check if message requires escalation.

        Args:
            message: Message to check
            context: Context for escalation check

        Returns:
            Tuple of (reason, level, safe_response) or None
        """
        if not self._middleware:
            return None
        try:
            return self._middleware.check_escalation(message, context or {})
        except Exception:
            return None


class _MiddlewareContextWrapper:
    """Async context manager wrapper for middleware execution context."""

    def __init__(
        self,
        middleware,
        agent_name: str,
        profile_id: str,
        session_id: Optional[str],
        task_type: str,
    ):
        self.middleware = middleware
        self.agent_name = agent_name
        self.profile_id = profile_id
        self.session_id = session_id
        self.task_type = task_type
        self._exec = None
        self._ctx = None

    async def __aenter__(self):
        if not self.middleware:
            return None

        try:
            # Import TaskType dynamically to avoid circular imports
            try:
                from context import TaskType
                task_type_enum = getattr(TaskType, self.task_type.upper(), TaskType.GENERAL)
            except (ImportError, AttributeError):
                task_type_enum = None

            self._exec = self.middleware.wrap_agent(
                self.agent_name,
                self.profile_id,
                self.session_id,
                task_type_enum,
            )
            self._ctx = await self._exec.__aenter__()
            return self._ctx
        except Exception as e:
            logger.warning(f"Middleware context init failed: {e}")
            return None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._exec:
            try:
                await self._exec.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
        return False


class _NoOpTimer:
    """No-op timer context manager for when middleware is unavailable."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass
