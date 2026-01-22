# Middleware Integration Code - Based on Actual Implementations

**Generated:** 2025-01-17
**Source:** Extracted from actual codebase (stack.py, stack_v7.py, stack_v8.py, gameplan.py, base.py, execution.py)

---

## Phase 1: Extracted Interfaces

### 1.1 MiddlewareStackV8 Constructor

```python
# From: middleware/stack_v8.py:162-189

def __init__(
    self,
    supabase_client=None,
    redis_client=None,
    llm_client=None,
    langfuse_client=None,       # v8: Added for observability
    notify_approval=None,        # Callback for approval notifications
    notify_shadow=None,          # Callback for shadow review notifications
):
```

### 1.2 Available Components (Attributes)

```python
# Phase 1 (Base - v6.0)
self.supabase                # Supabase client
self.redis                   # Redis client
self.llm                     # LLM client
self._user_context           # UserContextLoader
self._temporal_context       # TemporalContextLoader
self._task_manager           # TaskContextManager
self._context_selector       # ContextSelector
self._working_memory         # WorkingMemoryManager
self._guardrails             # GuardrailsManager
self._exception_handler      # ExceptionHandler
self._decision_rights        # DecisionRightsManager
self._escalation             # EscalationProtocol
self._output_validator       # OutputValidator
self._metrics                # MetricsCollector
self._reasoner               # ChainOfThoughtReasoner
self._prioritizer            # Prioritizer
self._goal_monitor           # GoalMonitor

# Phase 2A (v7.0) - from stack_v7.py:119-148
self.approval_gates          # ApprovalGateManager
self.shadow_manager          # HumanShadowManager
self.context_engineer        # ContextEngineer
self.producer_critic         # ProducerCriticPipeline
self.reflection_loop         # ReflectionLoop
self.react_loop              # ReActLoop
self.self_corrector          # SelfCorrector
self.deliberative            # DeliberativeReasoner
self.episodic_memory         # EpisodicMemoryManager
self.pivot_strategy          # PivotStrategy

# Phase 2B (v8.0) - from stack_v8.py:194-262
self.langfuse                # Langfuse client
self.session_context         # SessionContextManager (C1)
self.system_context          # SystemContextProvider (C3)
self.reflective_reasoner     # ReflectiveReasoner (A3)
self.prompt_chain            # PromptChainExecutor (A9)
self.planning_engine         # PlanningEngine (A11)
self.llm_judge               # LLMJudge (E2)
self.quality_scorer          # QualityScorer (E4)
self.coherence_checker       # CoherenceChecker (E5)
self.atomic_executor         # AtomicOperationExecutor (G4)
self.degradation_manager     # GracefulDegradationManager (H2)
self.retry_executor          # RetryExecutor (H3)
self._circuit_breakers       # Dict[str, CircuitBreaker] (H3)
self.trace_collector         # ReasoningTraceCollector (J1)
self.audit_trail             # AuditTrailManager (J3)
self.monitoring              # MonitoringManager (J4)
self.strategy_tracker        # StrategyEffectivenessTracker (I4)
```

### 1.3 Key Methods by Pattern

#### Context Methods
```python
# wrap_agent - from stack.py:198-223
async def wrap_agent(
    self,
    agent_name: str,
    profile_id: str,
    session_id: Optional[str] = None,
    task_type: TaskType = TaskType.GENERAL,
) -> _AgentExecutionContext:
    """Returns async context manager providing AgentContext."""

# C1: Session Context - from stack_v8.py:268-292
async def get_session_context(self, session_id: str, profile_id: str) -> SessionContext
async def add_session_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> None

# C3: System Context - from stack_v8.py:298-308
def get_system_context(self) -> SystemContext
def check_integration_health(self, service: str) -> bool
def is_feature_enabled(self, feature: str) -> bool

# C5: Context Engineering - from stack_v7.py:224-237
async def engineer_context(self, profile_id: str, session_id: str, task_type: str = "general", current_message: Optional[str] = None) -> EngineeredContext
```

#### Guardrails & Safety Methods
```python
# E6: Guardrails - from stack.py:295-313
def check_guardrails(self, content: str, is_input: bool = False) -> List[GuardrailResult]

# G3: Escalation - from stack.py:277-293
def check_escalation(self, message: str, context: Dict[str, Any]) -> Optional[tuple[EscalationReason, EscalationLevel, str]]
```

#### Quality Methods
```python
# E1: Output Validation - from stack.py:315-322
def validate_output(self, output: Dict[str, Any], output_type: str, context: Optional[Dict] = None) -> ValidationResult

# E2: LLM Judge - from stack_v8.py:391-417
async def judge_content(self, content: str, content_type: str = "general", criteria: Optional[List] = None, context: Optional[Dict] = None) -> JudgmentResult
async def compare_content(self, content_a: str, content_b: str, criteria: Optional[List] = None) -> Dict[str, Any]

# E4: Quality Scoring - from stack_v8.py:423-434
async def score_quality(self, content: str, content_type: str = "general", use_llm: bool = False) -> QualityScore

# E5: Coherence - from stack_v8.py:440-449
async def check_coherence(self, responses: List[str], context: Optional[Dict] = None) -> CoherenceResult
```

#### Recovery Methods
```python
# H2: Graceful Degradation - from stack_v8.py:477-503
async def call_with_fallback(self, service_name: str, primary_func: Callable, *args, **kwargs) -> Any
def register_fallback(self, service_name: str, fallback_func: Callable, priority: int = 0) -> None

# H3: Retry Logic - from stack_v8.py:509-530
async def execute_with_retry(self, func: Callable, config: Optional[RetryConfig] = None, *args, **kwargs) -> Any
def get_circuit_breaker(self, service_name: str) -> CircuitBreaker
```

#### Observability Methods
```python
# J1: Reasoning Traces - from stack_v8.py:536-590
def start_trace(self, profile_id: str, session_id: str, agent_name: str, input_message: str) -> ReasoningTrace
def add_trace_thought(self, trace_id: str, thought: str, metadata: Optional[Dict] = None) -> None
def add_trace_action(self, trace_id: str, action: str, metadata: Optional[Dict] = None) -> None
async def end_trace(self, trace_id: str, output: Optional[str] = None, success: bool = True, error: Optional[str] = None) -> Optional[ReasoningTrace]

# J3: Audit Trail - from stack_v8.py:596-638
async def audit_agent_action(self, agent_name: str, action: str, resource_type: str, resource_id: Optional[str] = None, details: Optional[Dict] = None, session_id: Optional[str] = None, success: bool = True) -> None
async def flush_audit_trail(self) -> int

# J4: Monitoring - from stack_v8.py:644-665
def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE, tags: Optional[Dict[str, str]] = None) -> None
def timer(self, name: str, tags: Optional[Dict[str, str]] = None)  # Returns context manager
def get_active_alerts(self) -> List
```

#### Finalization
```python
# From stack.py:344-379
def finalize(self, result: Dict[str, Any], output_type: str = "general") -> Dict[str, Any]:
    """Finalize output with validation and guardrails check."""
```

---

## Phase 2: Integration Patterns

### 2.1 GamePlanAgent Current Pattern (REFERENCE)

```python
# From: agents/gameplan.py:52-57, 108, 230-246, 339-341, 418-424, 435-441

# IMPORTS - conditional for backward compatibility
try:
    from middleware import MiddlewareStack, create_middleware
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False

# IN __init__:
self.middleware = create_middleware(self.db) if MIDDLEWARE_AVAILABLE else None

# IN process method:
async def generate_orchestrated(self, profile_id: str, react_hints: List[str] = None) -> Dict[str, Any]:
    # Initialize middleware context
    middleware_ctx = None
    middleware_exec = None
    if self.middleware and MIDDLEWARE_AVAILABLE:
        try:
            from ..context import TaskType
            middleware_exec = self.middleware.wrap_agent(
                "gameplan_agent",
                profile_id,
                task_type=TaskType.GAMEPLAN,
            )
            middleware_ctx = await middleware_exec.__aenter__()
            print(f"[GamePlan] v5.4: Middleware context initialized")
        except Exception as mw_err:
            print(f"[GamePlan] Middleware init skipped: {mw_err}")
            middleware_ctx = None
            middleware_exec = None

    try:
        # ... agent logic ...

        # Use middleware for finalization
        if self.middleware and middleware_ctx:
            try:
                result = self.middleware.finalize(result, output_type="gameplan")
            except Exception as mw_err:
                print(f"[GamePlan] Middleware finalize skipped: {mw_err}")

        return result

    finally:
        # Clean up middleware context
        if middleware_exec:
            try:
                await middleware_exec.__aexit__(None, None, None)
            except Exception:
                pass
```

### 2.2 BaseAgent Structure (TARGET FOR INTEGRATION)

```python
# From: agents/base.py:141-150

class BaseAgent(ABC):
    """
    Abstract base class for all IvyQuest agents.

    Provides:
    - State versioning (every state change is versioned)
    - Event publishing (via Supabase Realtime)
    - HITL (Human-in-the-Loop) support
    - Profile access helpers
    """
```

### 2.3 ExecutionAgent Structure (NON-INTEGRATED)

```python
# From: agents/execution.py:46-64

class ExecutionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Execution",
            autonomy_level=AutonomyLevel.MEDIUM
        )
        self.crisis_graph = CrisisAlchemyGraph()
        self.blocker_threshold_days = settings.blocker_threshold_days

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "check_status")
        # ... no middleware integration ...
```

---

## Phase 3: Generated Integration Code

### 3.1 BaseAgent Integration Mixin

```python
# NEW FILE: agents/mixins/middleware_mixin.py

"""
Middleware Integration Mixin for BaseAgent
==========================================
Provides middleware integration for all agents via mixin pattern.
This keeps BaseAgent clean while adding all 40 patterns.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Import middleware (uses v8 by default)
try:
    from middleware import MiddlewareStack, create_middleware, AgentContext
    from middleware.observability.reasoning_traces_v8 import ReasoningTrace
    from middleware.quality.quality_scoring_v8 import QualityScore
    from middleware.recovery.retry_logic_v8 import RetryConfig, CircuitBreakerOpen
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False
    MiddlewareStack = None
    AgentContext = None

logger = logging.getLogger(__name__)


class MiddlewareIntegrationMixin:
    """
    Mixin that adds middleware integration to any agent.

    Usage:
        class MyAgent(BaseAgent, MiddlewareIntegrationMixin):
            def __init__(self):
                super().__init__(name="MyAgent", autonomy_level=AutonomyLevel.MEDIUM)
                self.init_middleware()  # Call after super().__init__
    """

    # Class-level flag
    middleware_available = MIDDLEWARE_AVAILABLE

    def init_middleware(
        self,
        supabase_client=None,
        redis_client=None,
        llm_client=None,
        langfuse_client=None,
    ):
        """Initialize middleware stack. Call in __init__ after super()."""
        if not MIDDLEWARE_AVAILABLE:
            self._middleware = None
            return

        try:
            self._middleware = MiddlewareStack(
                supabase_client=supabase_client or getattr(self, 'db', None),
                redis_client=redis_client,
                llm_client=llm_client or getattr(self, 'llm', None),
                langfuse_client=langfuse_client,
            )
            logger.info(f"[{self.name}] Middleware v8 initialized")
        except Exception as e:
            logger.warning(f"[{self.name}] Middleware init failed: {e}")
            self._middleware = None

    @property
    def middleware(self) -> Optional[MiddlewareStack]:
        """Get middleware stack (may be None if not available)."""
        return getattr(self, '_middleware', None)

    # =========================================
    # CONTEXT HELPERS
    # =========================================

    async def with_middleware_context(
        self,
        profile_id: str,
        session_id: Optional[str] = None,
        task_type: str = "general",
    ):
        """
        Async context manager for middleware-wrapped execution.

        Usage:
            async with self.with_middleware_context(profile_id) as ctx:
                # ctx.student, ctx.temporal, ctx.working_memory available
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
        """Finalize result with middleware validation."""
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
        """Start a reasoning trace, returns trace_id."""
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

    def add_thought(self, trace_id: str, thought: str, metadata: Dict = None):
        """Add thought to active trace."""
        if self._middleware and trace_id:
            try:
                self._middleware.add_trace_thought(trace_id, thought, metadata)
            except Exception:
                pass

    def add_action(self, trace_id: str, action: str, metadata: Dict = None):
        """Add action to active trace."""
        if self._middleware and trace_id:
            try:
                self._middleware.add_trace_action(trace_id, action, metadata)
            except Exception:
                pass

    async def end_reasoning_trace(
        self,
        trace_id: str,
        output: str = None,
        success: bool = True,
        error: str = None,
    ):
        """End reasoning trace."""
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
        func,
        max_retries: int = 3,
        *args,
        **kwargs,
    ):
        """Execute function with retry logic."""
        if not self._middleware:
            return await func(*args, **kwargs)

        config = RetryConfig(max_retries=max_retries) if MIDDLEWARE_AVAILABLE else None
        return await self._middleware.execute_with_retry(func, config, *args, **kwargs)

    # =========================================
    # E4: QUALITY SCORING
    # =========================================

    async def score_quality(
        self,
        content: str,
        content_type: str = "general",
    ) -> Optional[QualityScore]:
        """Score content quality."""
        if not self._middleware:
            return None
        try:
            return await self._middleware.score_quality(content, content_type)
        except Exception as e:
            logger.warning(f"score_quality failed: {e}")
            return None

    # =========================================
    # J3: AUDIT TRAIL
    # =========================================

    async def audit_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str = None,
        details: Dict = None,
        session_id: str = None,
        success: bool = True,
    ):
        """Log action to audit trail."""
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
    # C1: SESSION CONTEXT
    # =========================================

    async def get_session(self, session_id: str, profile_id: str):
        """Get session context."""
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
        metadata: Dict = None,
    ):
        """Add message to session."""
        if not self._middleware:
            return
        try:
            await self._middleware.add_session_message(session_id, role, content, metadata)
        except Exception:
            pass


class _MiddlewareContextWrapper:
    """Async context manager wrapper for middleware."""

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
            # Import TaskType dynamically
            try:
                from context import TaskType
                task_type_enum = getattr(TaskType, self.task_type.upper(), TaskType.GENERAL)
            except ImportError:
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
```

### 3.2 ExecutionAgent Integration

```python
# CHANGES TO: agents/execution.py

# ADD IMPORTS at top:
from .mixins.middleware_mixin import MiddlewareIntegrationMixin

# MODIFY class definition:
class ExecutionAgent(BaseAgent, MiddlewareIntegrationMixin):
    """
    Execution Agent: Bridges strategy-execution gap.
    Now with middleware v8 integration.
    """

    def __init__(self):
        super().__init__(
            name="Execution",
            autonomy_level=AutonomyLevel.MEDIUM
        )
        self.crisis_graph = CrisisAlchemyGraph()
        self.blocker_threshold_days = settings.blocker_threshold_days

        # v8: Initialize middleware
        self.init_middleware(supabase_client=supabase)  # Uses global supabase

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Main processing entry point with middleware integration.
        """
        action = kwargs.get("action", "check_status")
        session_id = kwargs.get("session_id")

        # Start reasoning trace
        trace_id = self.start_reasoning_trace(
            profile_id=profile_id,
            session_id=session_id or f"exec_{profile_id}_{datetime.utcnow().isoformat()}",
            input_message=f"action={action}",
        )

        try:
            # Use middleware context
            async with self.with_middleware_context(profile_id, session_id, "execution") as ctx:
                self.add_thought(trace_id, f"Processing action: {action}")

                if action == "scaffold_project":
                    result = await self.scaffold_project(profile_id, kwargs.get("project_data", {}))
                elif action == "handle_crisis":
                    result = await self.handle_crisis(
                        profile_id,
                        kwargs.get("crisis_type", "blocker"),
                        kwargs.get("description", ""),
                        kwargs.get("urgency", 3)
                    )
                elif action == "detect_blockers":
                    result = await self.detect_blockers(profile_id)
                elif action == "compute_eds":
                    eds = await self.compute_eds(profile_id)
                    result = {"success": True, "eds": eds}
                else:
                    result = await self.check_status(profile_id)

                self.add_action(trace_id, f"completed_{action}")

                # Quality check on result
                if result.get("success"):
                    quality = await self.score_quality(str(result), "execution_result")
                    if quality:
                        result["_quality_score"] = quality.overall_score

                # Finalize with middleware
                result = self.middleware_finalize(result, "execution")

                # Audit the action
                await self.audit_action(
                    action=action,
                    resource_type="profile",
                    resource_id=profile_id,
                    details={"success": result.get("success")},
                    session_id=session_id,
                    success=result.get("success", False),
                )

                await self.end_reasoning_trace(trace_id, str(result), success=result.get("success", False))
                return result

        except Exception as e:
            await self.end_reasoning_trace(trace_id, error=str(e), success=False)
            raise
```

### 3.3 ExtracurricularsAgent Integration

```python
# CHANGES TO: agents/extracurriculars.py

# ADD IMPORTS at top:
from .mixins.middleware_mixin import MiddlewareIntegrationMixin

# MODIFY class definition:
class ExtracurricularsAgent(BaseAgent, MiddlewareIntegrationMixin):
    """
    Extracurriculars Agent with middleware v8 integration.
    """

    def __init__(self):
        super().__init__(
            name="Extracurriculars",
            autonomy_level=AutonomyLevel.HIGH
        )
        # ... existing init ...

        # v8: Initialize middleware
        self.init_middleware(supabase_client=self.db, llm_client=self.llm)

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """Process with middleware integration."""
        session_id = kwargs.get("session_id")

        trace_id = self.start_reasoning_trace(
            profile_id=profile_id,
            session_id=session_id or f"ec_{profile_id}",
            input_message="Analyzing extracurriculars",
        )

        try:
            async with self.with_middleware_context(profile_id, session_id, "extracurriculars") as ctx:
                self.add_thought(trace_id, "Loading student profile and activities")

                # ... existing logic ...
                result = await self._generate_recommendations(profile_id, kwargs)

                self.add_action(trace_id, "generated_recommendations")

                # Score quality
                quality = await self.score_quality(str(result.get("recommendations", [])), "ec_recommendations")
                if quality:
                    result["_quality_score"] = quality.overall_score

                result = self.middleware_finalize(result, "extracurriculars")

                await self.end_reasoning_trace(trace_id, success=result.get("success", False))
                return result

        except Exception as e:
            await self.end_reasoning_trace(trace_id, error=str(e), success=False)
            raise
```

---

## Phase 4: Implementation Checklist

### 4.1 Pre-Flight Checks

- [x] `middleware/__init__.py` exports v8 as default (DONE in previous session)
- [x] All v8 imports resolve without error
- [ ] Create `agents/mixins/` directory
- [ ] Create `agents/mixins/__init__.py`
- [ ] Create `agents/mixins/middleware_mixin.py`

### 4.2 Agent Integration Order (By Priority)

| Priority | Agent | File | Status |
|----------|-------|------|--------|
| P0 | GamePlanAgent | `agents/gameplan.py` | ✅ Already integrated (basic) |
| P0 | ExecutionAgent | `agents/execution.py` | ❌ Needs integration |
| P1 | ExtracurricularsAgent | `agents/extracurriculars.py` | ❌ Needs integration |
| P1 | AwardsAgent | `agents/awards.py` | ❌ Needs integration |
| P1 | ProgramsAgent | `agents/programs.py` | ❌ Needs integration |
| P2 | AssessmentAgent | `agents/assessment.py` | ❌ Needs integration |
| P2 | ExecutionChatAgent | `agents/execution_chat.py` | ❌ Needs integration |
| P2 | NarrativeSynthesisAgent | `agents/narrative_synthesis.py` | ❌ Needs integration |
| P3 | ReActAgent | `agents/core/react_base.py` | ❌ Needs integration |
| P3 | BaseAgent | `agents/base.py` | ❌ Consider adding mixin |

### 4.3 Per-Agent Changes

For each agent, the changes are:

1. **Import**: Add `from .mixins.middleware_mixin import MiddlewareIntegrationMixin`
2. **Class**: Add `MiddlewareIntegrationMixin` to class inheritance
3. **Init**: Add `self.init_middleware(...)` call after `super().__init__()`
4. **Process**: Wrap with `async with self.with_middleware_context(...):`
5. **Traces**: Add `start_reasoning_trace`, `add_thought/action`, `end_reasoning_trace`
6. **Quality**: Add `score_quality` calls on outputs
7. **Audit**: Add `audit_action` calls
8. **Finalize**: Replace direct return with `self.middleware_finalize(result)`

### 4.4 Testing

```bash
# Verify imports work
python -c "from middleware import MiddlewareStack; print('OK')"

# Verify mixin works (after creating)
python -c "from agents.mixins.middleware_mixin import MiddlewareIntegrationMixin; print('OK')"

# Run existing tests
pytest agents/tests/ -v

# Run middleware tests
pytest agents/tests/phase2b/ -v
```

---

## Appendix: Method Quick Reference

| Pattern | Method | Signature |
|---------|--------|-----------|
| C1 | get_session_context | `(session_id, profile_id) -> SessionContext` |
| C1 | add_session_message | `(session_id, role, content, metadata=None)` |
| C3 | get_system_context | `() -> SystemContext` |
| C3 | check_integration_health | `(service) -> bool` |
| E4 | score_quality | `(content, content_type, use_llm=False) -> QualityScore` |
| E5 | check_coherence | `(responses, context=None) -> CoherenceResult` |
| H2 | call_with_fallback | `(service_name, primary_func, *args, **kwargs)` |
| H3 | execute_with_retry | `(func, config=None, *args, **kwargs)` |
| J1 | start_trace | `(profile_id, session_id, agent_name, input_message) -> ReasoningTrace` |
| J1 | add_trace_thought | `(trace_id, thought, metadata=None)` |
| J1 | add_trace_action | `(trace_id, action, metadata=None)` |
| J1 | end_trace | `(trace_id, output=None, success=True, error=None)` |
| J3 | audit_agent_action | `(agent_name, action, resource_type, ...)` |
| J4 | record_metric | `(name, value, metric_type, tags=None)` |

---

**Generated by:** Claude Code
**Based on:** Actual extracted code from stack.py, stack_v7.py, stack_v8.py, gameplan.py, base.py, execution.py
