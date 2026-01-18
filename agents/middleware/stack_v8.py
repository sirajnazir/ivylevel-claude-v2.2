"""
MiddlewareStackV8: Enhanced Integration Layer for Phase 2B Patterns
v8.0 Enhancement 15 Patterns (Weeks 9-12)

This is an ADDITIVE enhancement to the existing MiddlewareStackV7 (v7.0).
Does NOT modify the original stack_v7.py - can be used alongside or as replacement.

Usage:
    from middleware.stack_v8 import MiddlewareStackV8

    async def process(self, profile_id: str, **kwargs):
        middleware = MiddlewareStackV8(self.supabase, self.redis, self.llm)
        async with middleware.wrap_agent("my_agent", profile_id) as ctx:
            # ... agent code with Phase 2B features ...
            result = await self._do_work(ctx)
            return middleware.finalize(result)

Phase 2B Patterns Added:
Week 9:
- C1: Session Context
- C3: System Context
- A3: Reflective Reasoning

Week 10:
- A9: Prompt Chaining
- A11: Planning
- E2: LLM-as-Judge

Week 11:
- E4: Quality Scoring
- E5: Coherence Checking
- G4: Atomic Operations

Week 12:
- H2: Graceful Degradation
- H3: Retry Logic
- J1: Reasoning Traces
- J3: Audit Trail
- J4: Monitoring
- I4: Strategy Effectiveness
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
import logging

# Import base middleware (v7.0)
from .stack_v7 import MiddlewareStackV7

# Import Phase 2B patterns - Context (Week 9)
from .context.session_context_v8 import (
    SessionContextManager,
    SessionContext,
)
from .context.system_context_v8 import (
    SystemContextProvider,
    SystemContext,
    IntegrationInfo,
    IntegrationStatus,
)

# Import Phase 2B patterns - Reasoning (Week 9-10)
from .reasoning.reflective_v8 import (
    ReflectiveReasoner,
    ReflectionResult as ReflectiveResult,
)
from .reasoning.prompt_chaining_v8 import (
    PromptChainExecutor,
    ChainStep,
    ChainResult,
    IvyLevelChains,
)
from .reasoning.planning_v8 import (
    PlanningEngine,
    Plan,
    PlanStep,
)

# Import Phase 2B patterns - Quality (Week 10-11)
from .quality.llm_judge_v8 import (
    LLMJudge,
    JudgmentResult,
    JudgmentCriterion,
)
from .quality.quality_scoring_v8 import (
    QualityScorer,
    QualityScore,
    QualityDimension,
)
from .quality.coherence_v8 import (
    CoherenceChecker,
    CoherenceResult,
    CoherenceType,
)

# Import Phase 2B patterns - HITL (Week 11)
from .hitl.atomic_operations_v8 import (
    AtomicOperationExecutor,
    AtomicOperation,
    IvyLevelRollbackHandlers,
)

# Import Phase 2B patterns - Recovery (Week 12)
from .recovery.graceful_degradation_v8 import (
    GracefulDegradationManager,
    FallbackConfig,
    IvyLevelFallbacks,
)
from .recovery.retry_logic_v8 import (
    RetryExecutor,
    RetryConfig,
    BackoffStrategy,
    CircuitBreaker,
    CircuitBreakerOpen,
)

# Import Phase 2B patterns - Observability (Week 12)
from .observability.reasoning_traces_v8 import (
    ReasoningTraceCollector,
    ReasoningTrace,
    TraceEventType,
)
from .observability.audit_trail_v8 import (
    AuditTrailManager,
    AuditAction,
    AuditActorType,
)
from .observability.monitoring_v8 import (
    MonitoringManager,
    AlertRule,
    MetricType,
    DEFAULT_ALERT_RULES,
)

# Import Phase 2B patterns - Learning (Week 12)
from .learning.strategy_effectiveness_v8 import (
    StrategyEffectivenessTracker,
    StrategyApplication,
    StrategyOutcome,
)

logger = logging.getLogger(__name__)


class MiddlewareStackV8(MiddlewareStackV7):
    """
    Enhanced middleware stack with Phase 2B patterns.

    Inherits all Critical 15 (v6.0) and Important 10 (v7.0) patterns
    and adds the Enhancement 15 patterns (v8.0).

    New capabilities:
    - Context: Session context, System context
    - Reasoning: Reflective, Prompt chaining, Planning
    - Quality: LLM-as-Judge, Quality scoring, Coherence
    - HITL: Atomic operations
    - Recovery: Graceful degradation, Retry with circuit breaker
    - Observability: Reasoning traces, Audit trail, Monitoring
    - Learning: Strategy effectiveness tracking
    """

    def __init__(
        self,
        supabase_client=None,
        redis_client=None,
        llm_client=None,
        langfuse_client=None,
        notify_approval=None,
        notify_shadow=None,
    ):
        """
        Initialize enhanced middleware stack.

        Args:
            supabase_client: Supabase client for data access
            redis_client: Redis client for working memory
            llm_client: LLM client for reasoning
            langfuse_client: Langfuse client for observability
            notify_approval: Callback for approval notifications
            notify_shadow: Callback for shadow review notifications
        """
        # Initialize Phase 2A stack (Important 10)
        super().__init__(
            supabase_client,
            redis_client,
            llm_client,
            notify_approval,
            notify_shadow,
        )

        # Store Langfuse client
        self.langfuse = langfuse_client

        # =========================================
        # Week 9: Context & Reflective
        # =========================================

        # C1: Session Context
        self.session_context = SessionContextManager(
            supabase_client=supabase_client,
            redis_client=redis_client,
        )

        # C3: System Context (singleton via __new__)
        self.system_context = SystemContextProvider()

        # A3: Reflective Reasoning
        self.reflective_reasoner = ReflectiveReasoner(llm_client)

        # =========================================
        # Week 10: Chaining, Planning, Judge
        # =========================================

        # A9: Prompt Chaining
        self.prompt_chain = PromptChainExecutor(llm_client)

        # A11: Planning
        self.planning_engine = PlanningEngine(llm_client)

        # E2: LLM-as-Judge
        self.llm_judge = LLMJudge(llm_client)

        # =========================================
        # Week 11: Quality & Atomic
        # =========================================

        # E4: Quality Scoring
        self.quality_scorer = QualityScorer(llm_client)

        # E5: Coherence Checking
        self.coherence_checker = CoherenceChecker(llm_client)

        # G4: Atomic Operations
        self.atomic_executor = AtomicOperationExecutor(supabase_client)

        # =========================================
        # Week 12: Recovery, Observability, Learning
        # =========================================

        # H2: Graceful Degradation
        self.degradation_manager = GracefulDegradationManager()

        # H3: Retry Logic
        self.retry_executor = RetryExecutor()
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}

        # J1: Reasoning Traces
        self.trace_collector = ReasoningTraceCollector(
            supabase_client=supabase_client,
            langfuse_client=langfuse_client,
        )

        # J3: Audit Trail
        self.audit_trail = AuditTrailManager(supabase_client)

        # J4: Monitoring
        self.monitoring = MonitoringManager(langfuse_client)
        for rule in DEFAULT_ALERT_RULES:
            self.monitoring.add_alert_rule(rule)

        # I4: Strategy Effectiveness
        self.strategy_tracker = StrategyEffectivenessTracker(supabase_client)

    # =========================================
    # C1: SESSION CONTEXT
    # =========================================

    async def get_session_context(
        self,
        session_id: str,
        profile_id: str,
    ) -> SessionContext:
        """Get or create session context."""
        return await self.session_context.get_or_create(
            session_id=session_id,
            profile_id=profile_id,
        )

    async def add_session_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a message to session context."""
        await self.session_context.add_message(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata,
        )

    # =========================================
    # C3: SYSTEM CONTEXT
    # =========================================

    def get_system_context(self) -> SystemContext:
        """Get current system context."""
        return self.system_context.context

    def check_integration_health(self, service: str) -> bool:
        """Check if an integration is healthy."""
        return self.system_context.is_integration_healthy(service)

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.system_context.get_feature_flag(feature, default=False)

    # =========================================
    # A3: REFLECTIVE REASONING
    # =========================================

    async def reason_reflectively(
        self,
        input_data: str,
        task_type: str = "general",
        context: Optional[Dict[str, Any]] = None,
    ) -> ReflectiveResult:
        """Run reflective reasoning on input."""
        return await self.reflective_reasoner.reason(
            input_data=input_data,
            task_type=task_type,
            context=context,
        )

    # =========================================
    # A9: PROMPT CHAINING
    # =========================================

    async def run_chain(
        self,
        steps: List[ChainStep],
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> ChainResult:
        """Execute a prompt chain."""
        return await self.prompt_chain.execute_chain(
            steps=steps,
            initial_context=initial_context,
        )

    async def run_essay_review_chain(
        self,
        essay_content: str,
        essay_type: str,
        student_grade: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> ChainResult:
        """Run the essay review chain."""
        chain = IvyLevelChains.essay_review_chain()
        return await self.prompt_chain.execute_chain(
            steps=chain,
            initial_context={
                "essay_content": essay_content,
                "essay_type": essay_type,
                "student_grade": student_grade,
                **(context or {}),
            },
        )

    # =========================================
    # A11: PLANNING
    # =========================================

    async def create_plan(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Plan:
        """Create a plan for a goal."""
        return await self.planning_engine.create_plan(
            goal=goal,
            context=context,
        )

    async def execute_plan(
        self,
        plan: Plan,
        step_executor: Callable[[PlanStep, Dict[str, Any]], Awaitable[Any]],
    ) -> Plan:
        """Execute a plan step by step."""
        return await self.planning_engine.execute_plan(
            plan=plan,
            step_executor=step_executor,
        )

    # =========================================
    # E2: LLM-AS-JUDGE
    # =========================================

    async def judge_content(
        self,
        content: str,
        content_type: str = "general",
        criteria: Optional[List[JudgmentCriterion]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> JudgmentResult:
        """Judge content quality."""
        return await self.llm_judge.judge(
            content=content,
            content_type=content_type,
            criteria=criteria or LLMJudge.DEFAULT_CRITERIA,
            context=context,
        )

    async def compare_content(
        self,
        content_a: str,
        content_b: str,
        criteria: Optional[List[JudgmentCriterion]] = None,
    ) -> Dict[str, Any]:
        """Compare two pieces of content."""
        return await self.llm_judge.compare(
            content_a=content_a,
            content_b=content_b,
            criteria=criteria or LLMJudge.DEFAULT_CRITERIA,
        )

    # =========================================
    # E4: QUALITY SCORING
    # =========================================

    async def score_quality(
        self,
        content: str,
        content_type: str = "general",
        use_llm: bool = False,
    ) -> QualityScore:
        """Score content quality."""
        return await self.quality_scorer.score(
            content=content,
            content_type=content_type,
            use_llm=use_llm,
        )

    # =========================================
    # E5: COHERENCE CHECKING
    # =========================================

    async def check_coherence(
        self,
        responses: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> CoherenceResult:
        """Check coherence across responses."""
        return await self.coherence_checker.check_coherence(
            responses=responses,
            context=context,
        )

    # =========================================
    # G4: ATOMIC OPERATIONS
    # =========================================

    async def execute_atomic(
        self,
        operation: AtomicOperation,
        rollback_handler: Optional[Callable] = None,
    ) -> Any:
        """Execute an operation atomically."""
        return await self.atomic_executor.execute(
            operation=operation,
            rollback_handler=rollback_handler,
        )

    async def execute_atomic_batch(
        self,
        operations: List[AtomicOperation],
    ) -> List[Any]:
        """Execute multiple operations atomically."""
        return await self.atomic_executor.execute_batch(operations)

    # =========================================
    # H2: GRACEFUL DEGRADATION
    # =========================================

    async def call_with_fallback(
        self,
        service_name: str,
        primary_func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Call function with fallback on failure."""
        return await self.degradation_manager.call_with_fallback(
            service_name=service_name,
            primary_func=primary_func,
            *args,
            **kwargs,
        )

    def register_fallback(
        self,
        service_name: str,
        fallback_func: Callable,
        priority: int = 0,
    ) -> None:
        """Register a fallback for a service."""
        self.degradation_manager.register_fallback(
            service_name=service_name,
            fallback_func=fallback_func,
            priority=priority,
        )

    # =========================================
    # H3: RETRY LOGIC
    # =========================================

    async def execute_with_retry(
        self,
        func: Callable,
        config: Optional[RetryConfig] = None,
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with retry logic."""
        return await self.retry_executor.execute(
            func=func,
            config=config,
            *args,
            **kwargs,
        )

    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service_name not in self._circuit_breakers:
            self._circuit_breakers[service_name] = CircuitBreaker(
                name=service_name
            )
        return self._circuit_breakers[service_name]

    # =========================================
    # J1: REASONING TRACES
    # =========================================

    def start_trace(
        self,
        profile_id: str,
        session_id: str,
        agent_name: str,
        input_message: str,
    ) -> ReasoningTrace:
        """Start a reasoning trace."""
        return self.trace_collector.start_trace(
            profile_id=profile_id,
            session_id=session_id,
            agent_name=agent_name,
            input_message=input_message,
        )

    def add_trace_thought(
        self,
        trace_id: str,
        thought: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a thought to a trace."""
        self.trace_collector.add_thought(
            trace_id=trace_id,
            thought=thought,
            metadata=metadata,
        )

    def add_trace_action(
        self,
        trace_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an action to a trace."""
        self.trace_collector.add_action(
            trace_id=trace_id,
            action=action,
            metadata=metadata,
        )

    async def end_trace(
        self,
        trace_id: str,
        output: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> Optional[ReasoningTrace]:
        """End a reasoning trace."""
        return await self.trace_collector.end_trace(
            trace_id=trace_id,
            output=output,
            success=success,
            error=error,
        )

    # =========================================
    # J3: AUDIT TRAIL
    # =========================================

    async def audit_agent_action(
        self,
        agent_name: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        success: bool = True,
    ) -> None:
        """Log an agent action to audit trail."""
        await self.audit_trail.log_agent_action(
            agent_name=agent_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            session_id=session_id,
            success=success,
        )

    async def audit_user_action(
        self,
        user_id: str,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Log a user action to audit trail."""
        await self.audit_trail.log_user_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            session_id=session_id,
        )

    async def flush_audit_trail(self) -> int:
        """Flush audit trail buffer to database."""
        return await self.audit_trail.flush()

    # =========================================
    # J4: MONITORING
    # =========================================

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a metric."""
        self.monitoring.record_metric(
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags,
        )

    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Get a timer context manager."""
        return self.monitoring.timer(name=name, tags=tags)

    def get_active_alerts(self) -> List:
        """Get all active alerts."""
        return self.monitoring.get_active_alerts()

    # =========================================
    # I4: STRATEGY EFFECTIVENESS
    # =========================================

    async def record_strategy_application(
        self,
        strategy: str,
        context_type: str,
        profile_id: str,
        session_id: str,
        input_situation: str,
        strategy_response: str,
    ) -> StrategyApplication:
        """Record a strategy application."""
        return await self.strategy_tracker.record_application(
            strategy=strategy,
            context_type=context_type,
            profile_id=profile_id,
            session_id=session_id,
            input_situation=input_situation,
            strategy_response=strategy_response,
        )

    async def record_strategy_outcome(
        self,
        application_id: str,
        outcome: StrategyOutcome,
        reason: Optional[str] = None,
        student_response_positive: Optional[bool] = None,
        task_completed: Optional[bool] = None,
        engagement_score: Optional[float] = None,
    ) -> None:
        """Record the outcome of a strategy application."""
        await self.strategy_tracker.record_outcome(
            application_id=application_id,
            outcome=outcome,
            reason=reason,
            student_response_positive=student_response_positive,
            task_completed=task_completed,
            engagement_score=engagement_score,
        )

    async def recommend_strategy(
        self,
        context_type: str,
        profile_id: str,
        available_strategies: List[str],
    ) -> Optional[str]:
        """Get recommended strategy for situation."""
        return await self.strategy_tracker.recommend_strategy(
            context_type=context_type,
            profile_id=profile_id,
            available_strategies=available_strategies,
        )


# Convenience function
def create_middleware_v8(
    supabase_client=None,
    redis_client=None,
    llm_client=None,
    langfuse_client=None,
) -> MiddlewareStackV8:
    """
    Create a v8 middleware stack with all Phase 2A and 2B patterns.

    Usage:
        middleware = create_middleware_v8(supabase, redis, llm, langfuse)
    """
    return MiddlewareStackV8(
        supabase_client=supabase_client,
        redis_client=redis_client,
        llm_client=llm_client,
        langfuse_client=langfuse_client,
    )
