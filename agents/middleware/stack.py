"""
MiddlewareStack: Integration Layer for Critical 15 Patterns
v5.4 True Autonomous Agents

This is the ADDITIVE layer that wraps existing agent code.
Minimal changes to existing files (~4 lines per agent).
"""

from typing import Dict, Any, List, Optional, Callable, TypeVar
from datetime import datetime
from functools import wraps
import logging

# Import all pattern modules (absolute imports for test compatibility)
from context import (
    UserContextLoader,
    TemporalContextLoader,
    TaskContextManager,
    ContextSelector,
    StudentContext,
    TemporalContext,
    TaskContext,
    TaskType,
    WorkingMemory,
)
from memory import (
    WorkingMemoryManager,
    MemoryRetriever,
    # Note: WorkingMemory model is in context.types, not memory
)
from intelligence import (
    Prioritizer,
    GoalMonitor,
    PrioritizedItem,
    GoalProgressReport,
)
from governance import (
    DecisionRightsManager,
    EscalationProtocol,
    DecisionLevel,
    EscalationLevel,
    EscalationReason,
    SafetyResponse,
)
from safety import (
    GuardrailsManager,
    GuardrailResult,
)
from resilience import (
    ExceptionHandler,
    with_retry,
    handle_exception,
    FallbackResponse,
)
from reasoning import (
    ChainOfThoughtReasoner,
    AgentRouter,
    ReasoningChain,
    RouteDecision,
)
from validation import (
    OutputValidator,
    ValidationResult,
)
from observability import (
    MetricsCollector,
    get_metrics_collector,
    AgentMetrics,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AgentContext:
    """
    Complete context for an agent execution.

    Aggregates all context types into single object.
    """

    def __init__(
        self,
        profile_id: str,
        session_id: str,
        task_type: TaskType = TaskType.GENERAL,
    ):
        self.profile_id = profile_id
        self.session_id = session_id
        self.task_type = task_type

        # Context components (lazy loaded)
        self._student: Optional[StudentContext] = None
        self._temporal: Optional[TemporalContext] = None
        self._task: Optional[TaskContext] = None
        self._working_memory: Optional[WorkingMemory] = None

        # Metadata
        self.created_at = datetime.utcnow()
        self.metrics_id: Optional[str] = None

    @property
    def student(self) -> Optional[StudentContext]:
        return self._student

    @property
    def temporal(self) -> Optional[TemporalContext]:
        return self._temporal

    @property
    def task(self) -> Optional[TaskContext]:
        return self._task

    @property
    def working_memory(self) -> Optional[WorkingMemory]:
        return self._working_memory

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for passing to agents."""
        return {
            "profile_id": self.profile_id,
            "session_id": self.session_id,
            "student": self._student.model_dump() if self._student else None,
            "temporal": self._temporal.model_dump() if self._temporal else None,
            "task": self._task.model_dump() if self._task else None,
            "spike": self._student.spike if self._student else None,
            "archetype": self._student.archetype if self._student else None,
            "grade": self._student.grade if self._student else 11,
        }


class MiddlewareStack:
    """
    Central middleware stack that wraps agent execution.

    Usage in existing agent (4 lines):

    ```python
    from middleware import MiddlewareStack

    async def process(self, profile_id: str, **kwargs):
        middleware = MiddlewareStack(self.supabase)
        async with middleware.wrap_agent("gameplan_agent", profile_id) as ctx:
            # ... existing agent code ...
            result = await self._generate_gameplan(ctx.student, ctx.temporal)
            return middleware.finalize(result)
    ```

    This single integration point provides:
    - Context loading (C2, C4, C6)
    - Working memory (B1)
    - Guardrails (E6)
    - Exception handling (H1)
    - Metrics collection (J2)
    - Decision rights checking (G1)
    - Escalation detection (G3)
    - Output validation (E1)
    """

    def __init__(
        self,
        supabase_client=None,
        redis_client=None,
        llm_client=None,
    ):
        """
        Initialize middleware stack.

        Args:
            supabase_client: Supabase client for data access
            redis_client: Redis client for working memory
            llm_client: LLM client for reasoning
        """
        self.supabase = supabase_client
        self.redis = redis_client
        self.llm = llm_client

        # Initialize pattern handlers
        self._user_context = UserContextLoader(supabase_client) if supabase_client else None
        self._temporal_context = TemporalContextLoader(supabase_client) if supabase_client else None
        self._task_manager = TaskContextManager(supabase_client)
        self._context_selector = ContextSelector()
        self._working_memory = WorkingMemoryManager(redis_client)
        self._guardrails = GuardrailsManager()
        self._exception_handler = ExceptionHandler()
        self._decision_rights = DecisionRightsManager()
        self._escalation = EscalationProtocol()
        self._output_validator = OutputValidator()
        self._metrics = get_metrics_collector()
        self._reasoner = ChainOfThoughtReasoner(llm_client)
        self._prioritizer = Prioritizer()
        self._goal_monitor = GoalMonitor(supabase_client)

        # Current context
        self._current_context: Optional[AgentContext] = None

    async def wrap_agent(
        self,
        agent_name: str,
        profile_id: str,
        session_id: Optional[str] = None,
        task_type: TaskType = TaskType.GENERAL,
    ):
        """
        Async context manager for wrapping agent execution.

        Args:
            agent_name: Name of the agent being wrapped
            profile_id: Student's profile ID
            session_id: Session ID (auto-generated if not provided)
            task_type: Type of task being performed

        Returns:
            AgentContext with all loaded context
        """
        return _AgentExecutionContext(
            self,
            agent_name,
            profile_id,
            session_id,
            task_type,
        )

    async def _load_context(
        self,
        profile_id: str,
        session_id: str,
        task_type: TaskType,
    ) -> AgentContext:
        """Load all context for an agent execution."""
        ctx = AgentContext(profile_id, session_id, task_type)

        # Determine what context to load based on task type
        selection = self._context_selector.select_for_task(
            task_type,
            {
                "activities": True,
                "academics": True,
                "goals": True,
                "constraints": True,
            },
        )

        # Load user context (C2)
        if self._user_context:
            try:
                ctx._student = await self._user_context.load_context(
                    profile_id, selection
                )
            except Exception as e:
                logger.warning(f"Failed to load user context: {e}")

        # Load temporal context (C6)
        if self._temporal_context:
            try:
                ctx._temporal = await self._temporal_context.load_context(profile_id)
            except Exception as e:
                logger.warning(f"Failed to load temporal context: {e}")

        # Create task context (C4)
        ctx._task = self._task_manager.create_task(
            task_type=task_type,
            objective=f"Execute {task_type.value} for profile {profile_id}",
        )

        # Load working memory (B1)
        try:
            ctx._working_memory = await self._working_memory.get_or_create(
                session_id, profile_id
            )
        except Exception as e:
            logger.warning(f"Failed to load working memory: {e}")

        return ctx

    def check_escalation(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> Optional[tuple[EscalationReason, EscalationLevel, str]]:
        """
        Check if a message requires escalation.

        Returns:
            Tuple of (reason, level, safe_response) or None
        """
        result = self._escalation.check_for_escalation(message, context)
        if result:
            reason, level = result
            safe_response = SafetyResponse.get_response(reason, context)
            return (reason, level, safe_response)
        return None

    def check_guardrails(
        self,
        content: str,
        is_input: bool = False,
    ) -> List[GuardrailResult]:
        """
        Check content against guardrails.

        Args:
            content: Content to check
            is_input: Whether this is input (vs output)

        Returns:
            List of GuardrailResults
        """
        if is_input:
            return [self._guardrails.check_input(content)]
        else:
            return self._guardrails.check_output(content)

    def validate_output(
        self,
        output: Dict[str, Any],
        output_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate agent output."""
        return self._output_validator.validate(output, output_type, context)

    def prioritize(
        self,
        items: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[PrioritizedItem]:
        """Prioritize recommendations."""
        return self._prioritizer.prioritize(
            items,
            context,
            context.get("temporal", {}),
        )

    async def think_step_by_step(
        self,
        task_type: str,
        context: Dict[str, Any],
    ) -> ReasoningChain:
        """Perform chain-of-thought reasoning."""
        return await self._reasoner.reason(task_type, context)

    def finalize(
        self,
        result: Dict[str, Any],
        output_type: str = "general",
    ) -> Dict[str, Any]:
        """
        Finalize agent output with validation and metrics.

        Args:
            result: Agent result to finalize
            output_type: Type of output for validation

        Returns:
            Finalized result with _validation metadata
        """
        # Validate output
        validation = self.validate_output(
            result,
            output_type,
            self._current_context.to_dict() if self._current_context else None,
        )

        # Check guardrails on output
        guardrail_results = self.check_guardrails(str(result), is_input=False)
        guardrails_passed = all(r.passed for r in guardrail_results)

        # Add validation metadata
        result["_validation"] = {
            "valid": validation.valid and guardrails_passed,
            "score": validation.score,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "guardrails_passed": guardrails_passed,
        }

        return result


class _AgentExecutionContext:
    """Async context manager for agent execution."""

    def __init__(
        self,
        stack: MiddlewareStack,
        agent_name: str,
        profile_id: str,
        session_id: Optional[str],
        task_type: TaskType,
    ):
        self.stack = stack
        self.agent_name = agent_name
        self.profile_id = profile_id
        self.session_id = session_id or self._generate_session_id()
        self.task_type = task_type
        self._context: Optional[AgentContext] = None

    def _generate_session_id(self) -> str:
        import uuid
        return str(uuid.uuid4())

    async def __aenter__(self) -> AgentContext:
        """Enter the context manager."""
        # Start metrics collection
        self._context = await self.stack._load_context(
            self.profile_id,
            self.session_id,
            self.task_type,
        )
        self._context.metrics_id = self.stack._metrics.start_agent_metrics(
            self.agent_name,
            self.profile_id,
            self.session_id,
        )

        # Start task
        if self._context.task:
            self.stack._task_manager.start_task(
                self._context.task.task_id,
                self.agent_name,
            )

        # Store current context in stack
        self.stack._current_context = self._context

        logger.info(f"Started {self.agent_name} for profile {self.profile_id}")

        return self._context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        if self._context and self._context.metrics_id:
            # Handle any exceptions
            if exc_type:
                self.stack._metrics.record_error(
                    self._context.metrics_id,
                    f"{exc_type.__name__}: {exc_val}",
                )

            # Finish metrics collection
            metrics = self.stack._metrics.finish_agent_metrics(
                self._context.metrics_id
            )

            if metrics:
                logger.info(
                    f"Completed {self.agent_name}: "
                    f"{metrics.duration_ms}ms, "
                    f"{metrics.llm_calls} LLM calls, "
                    f"quality={metrics.quality_score}"
                )

        # Complete task
        if self._context and self._context.task:
            self.stack._task_manager.complete_task(
                self._context.task.task_id,
                success=exc_type is None,
            )

        # Clear current context
        self.stack._current_context = None

        # Don't suppress exceptions
        return False


# Convenience function for simple integration
def create_middleware(
    supabase_client=None,
    redis_client=None,
) -> MiddlewareStack:
    """
    Create a middleware stack with default configuration.

    Usage:
        middleware = create_middleware(supabase, redis)
    """
    return MiddlewareStack(supabase_client, redis_client)
