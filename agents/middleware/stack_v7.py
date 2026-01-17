"""
MiddlewareStackV7: Enhanced Integration Layer for Phase 2A Patterns
v7.0 Important 10 Patterns

This is an ADDITIVE enhancement to the existing MiddlewareStack (v6.0).
Does NOT modify the original stack.py - can be used alongside or as replacement.

Usage:
    from middleware.stack_v7 import MiddlewareStackV7

    async def process(self, profile_id: str, **kwargs):
        middleware = MiddlewareStackV7(self.supabase, self.redis, self.llm)
        async with middleware.wrap_agent("my_agent", profile_id) as ctx:
            # ... agent code with Phase 2A features ...
            result = await self._do_work(ctx)
            return middleware.finalize(result)

Phase 2A Patterns Added:
- G2: Approval Gates
- G5: Human Shadow Mode
- C5: Context Engineering
- E7: Producer-Critic
- E3: Reflection Loops
- A6: ReAct Loop
- A7: Self-Correction
- A2: Deliberative Reasoning
- B2: Episodic Memory
- H4: Pivot Strategy
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
import logging

# Import base middleware (v6.0)
from .stack import MiddlewareStack, AgentContext

# Import Phase 2A patterns
from .approval import (
    ApprovalGateManager,
    ApprovalCategory,
    ApprovalUrgency,
    ApprovalRequest,
    ApprovalDecision,
)
from .shadow import (
    HumanShadowManager,
    ShadowMode,
    ShadowProposal,
    ShadowReview,
)
from .context import (
    ContextEngineer,
    EngineeredContext,
)
from .quality import (
    ProducerCriticPipeline,
    ReflectionLoop,
    CritiqueResult,
    ReflectionResult,
)
from .reasoning import (
    ReActLoop,
    SelfCorrector,
    DeliberativeReasoner,
    ReActResult,
    SelfCorrectionResult,
    DeliberationResult,
)
from .memory import (
    EpisodicMemoryManager,
    Episode,
)
from .recovery import (
    PivotStrategy,
    PivotResult,
    PivotOption,
)

logger = logging.getLogger(__name__)


class MiddlewareStackV7(MiddlewareStack):
    """
    Enhanced middleware stack with Phase 2A patterns.

    Inherits all Critical 15 patterns from MiddlewareStack (v6.0)
    and adds the Important 10 patterns (v7.0).

    New capabilities:
    - HITL: Approval gates, Shadow mode
    - Quality: Producer-critic, Reflection loops
    - Reasoning: ReAct, Self-correction, Deliberative
    - Memory: Episodic memory
    - Recovery: Pivot strategies
    """

    def __init__(
        self,
        supabase_client=None,
        redis_client=None,
        llm_client=None,
        notify_approval: Optional[Callable[[ApprovalRequest], Awaitable[None]]] = None,
        notify_shadow: Optional[Callable[[ShadowProposal], Awaitable[None]]] = None,
    ):
        """
        Initialize enhanced middleware stack.

        Args:
            supabase_client: Supabase client for data access
            redis_client: Redis client for working memory
            llm_client: LLM client for reasoning
            notify_approval: Callback for approval notifications
            notify_shadow: Callback for shadow review notifications
        """
        # Initialize base stack (Critical 15)
        super().__init__(supabase_client, redis_client, llm_client)

        # Phase 2A: HITL (Week 5)
        self.approval_gates = ApprovalGateManager(
            supabase_client,
            notification_callback=notify_approval,
        )
        self.shadow_manager = HumanShadowManager(
            supabase_client,
            notify_coach=notify_shadow,
        )

        # Phase 2A: Context (Week 6)
        self.context_engineer = ContextEngineer(
            supabase_client,
            redis_client,
        )

        # Phase 2A: Quality (Week 6)
        self.producer_critic = ProducerCriticPipeline(llm_client)
        self.reflection_loop = ReflectionLoop(llm_client)

        # Phase 2A: Reasoning (Week 7)
        self.react_loop = ReActLoop(llm_client)
        self.self_corrector = SelfCorrector(llm_client)
        self.deliberative = DeliberativeReasoner(llm_client)

        # Phase 2A: Memory (Week 8)
        self.episodic_memory = EpisodicMemoryManager(supabase_client)

        # Phase 2A: Recovery (Week 8)
        self.pivot_strategy = PivotStrategy(self.episodic_memory)

    # =========================================
    # G2: APPROVAL GATES
    # =========================================

    def check_requires_approval(
        self,
        action_type: str,
        agent_confidence: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Check if an action requires approval."""
        return self.approval_gates.check_requires_approval(
            action_type, agent_confidence, context
        )

    async def request_approval(
        self,
        profile_id: str,
        agent_name: str,
        action_type: str,
        action_description: str,
        action_payload: Dict[str, Any],
        agent_confidence: float = 0.5,
        agent_reasoning: str = "",
    ) -> Optional[ApprovalRequest]:
        """Request approval for an action if needed."""
        rule = self.check_requires_approval(action_type, agent_confidence)
        if rule:
            return await self.approval_gates.request_approval(
                profile_id=profile_id,
                agent_name=agent_name,
                action_type=action_type,
                action_description=action_description,
                action_payload=action_payload,
                rule=rule,
                agent_confidence=agent_confidence,
                agent_reasoning=agent_reasoning,
            )
        return None

    # =========================================
    # G5: HUMAN SHADOW MODE
    # =========================================

    def get_shadow_mode(
        self,
        profile_id: str,
        agent_name: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ShadowMode:
        """Get shadow mode for current interaction."""
        return self.shadow_manager.get_shadow_mode(profile_id, agent_name, context)

    async def submit_for_shadow_review(
        self,
        profile_id: str,
        agent_name: str,
        proposal_type: str,
        proposed_content: str,
        **kwargs,
    ) -> ShadowProposal:
        """Submit a proposal for shadow review."""
        return await self.shadow_manager.submit_proposal(
            profile_id=profile_id,
            agent_name=agent_name,
            proposal_type=proposal_type,
            proposed_content=proposed_content,
            **kwargs,
        )

    # =========================================
    # C5: CONTEXT ENGINEERING
    # =========================================

    async def engineer_context(
        self,
        profile_id: str,
        session_id: str,
        task_type: str = "general",
        current_message: Optional[str] = None,
    ) -> EngineeredContext:
        """Engineer rich context for agent interaction."""
        return await self.context_engineer.engineer_context(
            profile_id=profile_id,
            session_id=session_id,
            task_type=task_type,
            current_message=current_message,
        )

    # =========================================
    # E7: PRODUCER-CRITIC
    # =========================================

    async def produce_with_critique(
        self,
        producer_func: Callable,
        output_type: str = "general",
        context: Optional[Dict[str, Any]] = None,
        **producer_kwargs,
    ) -> Dict[str, Any]:
        """Run producer-critic pattern on output."""
        return await self.producer_critic.produce_and_critique(
            producer_func=producer_func,
            output_type=output_type,
            context=context,
            **producer_kwargs,
        )

    # =========================================
    # E3: REFLECTION LOOPS
    # =========================================

    async def reflect_and_improve(
        self,
        original_output: str,
        critique_feedback: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ReflectionResult:
        """Run reflection loop to improve output."""
        return await self.reflection_loop.reflect_and_improve(
            original_output=original_output,
            critique_feedback=critique_feedback,
            context=context,
        )

    # =========================================
    # A6: REACT LOOP
    # =========================================

    async def run_react(
        self,
        task: str,
        tools: Optional[Dict[str, Callable]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ReActResult:
        """Run ReAct loop for complex task."""
        if tools:
            for name, func in tools.items():
                self.react_loop.register_tool(name, func)
        return await self.react_loop.run(task=task, context=context)

    # =========================================
    # A7: SELF-CORRECTION
    # =========================================

    async def generate_with_self_correction(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SelfCorrectionResult:
        """Generate response with self-correction."""
        return await self.self_corrector.generate_with_self_correction(
            prompt=prompt,
            context=context,
        )

    # =========================================
    # A2: DELIBERATIVE REASONING
    # =========================================

    async def deliberate(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DeliberationResult:
        """Perform deliberative reasoning on complex task."""
        return await self.deliberative.deliberate(task=task, context=context)

    # =========================================
    # B2: EPISODIC MEMORY
    # =========================================

    async def record_episode(
        self,
        profile_id: str,
        situation: str,
        action_taken: str,
        approach_type: str,
        agent_name: str,
        outcome: str,
        **kwargs,
    ) -> Episode:
        """Record an episode to episodic memory."""
        return await self.episodic_memory.record_episode(
            profile_id=profile_id,
            situation=situation,
            action_taken=action_taken,
            approach_type=approach_type,
            agent_name=agent_name,
            outcome=outcome,
            **kwargs,
        )

    async def recall_similar_episodes(
        self,
        profile_id: str,
        current_situation: str,
        k: int = 5,
    ) -> List[Episode]:
        """Recall similar past episodes."""
        return await self.episodic_memory.recall_similar(
            profile_id=profile_id,
            current_situation=current_situation,
            k=k,
        )

    async def get_success_patterns(
        self,
        profile_id: str,
    ) -> Dict[str, Any]:
        """Get successful approach patterns for a student."""
        return await self.episodic_memory.get_success_patterns(profile_id)

    # =========================================
    # H4: PIVOT STRATEGY
    # =========================================

    async def should_pivot(
        self,
        context: Dict[str, Any],
    ) -> tuple:
        """Check if a pivot is needed."""
        return await self.pivot_strategy.should_pivot(context)

    async def get_pivot_options(
        self,
        profile_id: str,
        current_approach: str,
        context: Dict[str, Any],
    ) -> List[PivotOption]:
        """Get available pivot options."""
        return await self.pivot_strategy.get_pivot_options(
            profile_id=profile_id,
            current_approach=current_approach,
            context=context,
        )

    async def execute_pivot(
        self,
        profile_id: str,
        original_approach: str,
        selected_option: PivotOption,
        execute_func: Callable,
        context: Optional[Dict[str, Any]] = None,
    ) -> PivotResult:
        """Execute a pivot to new approach."""
        return await self.pivot_strategy.execute_pivot(
            profile_id=profile_id,
            original_approach=original_approach,
            selected_option=selected_option,
            execute_func=execute_func,
            context=context,
        )


# Convenience function
def create_middleware_v7(
    supabase_client=None,
    redis_client=None,
    llm_client=None,
) -> MiddlewareStackV7:
    """
    Create a v7 middleware stack with all Phase 2A patterns.

    Usage:
        middleware = create_middleware_v7(supabase, redis, llm)
    """
    return MiddlewareStackV7(supabase_client, redis_client, llm_client)
