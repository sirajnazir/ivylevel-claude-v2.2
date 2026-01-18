"""
MiddlewareStackV9: Phase 3 Final 20 Patterns
v9.0 - Complete Agent Middleware Stack

This is an ADDITIVE enhancement to MiddlewareStackV8 (v8.0).
Does NOT modify the original stack files - maintains inheritance chain.

Usage:
    from middleware.stack_v9 import MiddlewareStackV9

    async def process(self, profile_id: str, **kwargs):
        middleware = MiddlewareStackV9(self.supabase, self.openai, self.langfuse)
        async with middleware.wrap_agent("my_agent", profile_id) as ctx:
            # ... agent code with all 50 patterns ...
            result = await self._do_work(ctx)
            return middleware.finalize(result)

Phase 3 Patterns (v9.0):
Memory:
- B3: Semantic Memory (pgvector)
- B4: Long-Term Memory (JSONB)
- B5: Memory Extraction (OpenAI)
- B6: Memory Consolidation

Tools:
- D1: Tool Registry
- D2: Tool Calling
- D3: Schema Generation
- D4: Parallel Execution
- D7: Tool Chaining

Learning:
- I1: Feedback Loop
- I2: Behavior Adaptation
- I3: Pattern Recognition
- I5: Preference Learning

Reasoning:
- A5: Adaptive Prompting
- A12: Metacognition

Safety:
- F5: Content Moderation (OpenAI free)
- F6: PII Detection (Presidio)

Observability:
- J2: Request Logging
- J5: Cost Tracking (tiktoken)
- K4: Context Compression
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Import base middleware (v8.0)
from .stack_v8 import MiddlewareStackV8

# Import Phase 3 patterns - Memory
from .memory.semantic_v9 import SemanticMemoryManager
from .memory.longterm_v9 import LongTermMemoryManager
from .memory.extraction_v9 import MemoryExtractor
from .memory.consolidation_v9 import MemoryConsolidator

# Import Phase 3 patterns - Tools
from .tools.registry_v9 import ToolRegistry
from .tools.calling_v9 import ToolCaller
from .tools.schema_v9 import SchemaGenerator
from .tools.parallel_v9 import ParallelToolExecutor
from .tools.chaining_v9 import ToolChainer

# Import Phase 3 patterns - Learning
from .learning.feedback_v9 import FeedbackLoop
from .learning.adaptation_v9 import BehaviorAdapter
from .learning.patterns_v9 import PatternRecognizer
from .learning.preferences_v9 import PreferenceLearner

# Import Phase 3 patterns - Reasoning
from .reasoning.adaptive_v9 import AdaptivePrompter
from .reasoning.metacognition_v9 import Metacognitor

# Import Phase 3 patterns - Safety
from .safety.moderation_v9 import ContentModerator
from .safety.pii_v9 import PIIDetector

# Import Phase 3 patterns - Observability
from .observability.logging_v9 import RequestLogger
from .observability.cost_v9 import CostTracker

# Import Phase 3 patterns - Optimization
from .optimization.compression_v9 import ContextCompressor

logger = logging.getLogger(__name__)


class MiddlewareStackV9(MiddlewareStackV8):
    """
    Complete middleware stack with all 50 patterns.

    Inherits:
    - Critical 15 (v6.0)
    - Important 10 (v7.0)
    - Enhancement 15 (v8.0)

    Adds Phase 3 Final 20:
    - Memory: Semantic, Long-term, Extraction, Consolidation
    - Tools: Registry, Calling, Schema, Parallel, Chaining
    - Learning: Feedback, Adaptation, Patterns, Preferences
    - Reasoning: Adaptive prompting, Metacognition
    - Safety: Moderation, PII detection
    - Observability: Logging, Cost tracking, Compression
    """

    def __init__(
        self,
        supabase_client=None,
        redis_client=None,
        llm_client=None,
        openai_client=None,
        langfuse_client=None,
        notify_approval=None,
        notify_shadow=None,
    ):
        """
        Initialize complete middleware stack.

        Args:
            supabase_client: Supabase client for persistence
            redis_client: Redis client for working memory
            llm_client: LLM client for reasoning (legacy)
            openai_client: OpenAI client for embeddings/moderation
            langfuse_client: Langfuse client for observability
            notify_approval: Callback for approval notifications
            notify_shadow: Callback for shadow review notifications
        """
        # Initialize Phase 2B stack (Enhancement 15)
        super().__init__(
            supabase_client=supabase_client,
            redis_client=redis_client,
            llm_client=llm_client,
            langfuse_client=langfuse_client,
            notify_approval=notify_approval,
            notify_shadow=notify_shadow,
        )

        # Store OpenAI client (may be same as llm_client)
        self.openai = openai_client or llm_client

        # =========================================
        # Memory Patterns (B3, B4, B5, B6)
        # =========================================

        # B4: Long-Term Memory (foundation)
        self.longterm_memory = LongTermMemoryManager(
            supabase_client=supabase_client,
        )

        # B3: Semantic Memory (needs OpenAI for embeddings)
        self.semantic_memory = SemanticMemoryManager(
            supabase_client=supabase_client,
            openai_client=self.openai,
        )

        # B5: Memory Extraction
        self.memory_extractor = MemoryExtractor(
            openai_client=self.openai,
        )

        # B6: Memory Consolidation
        self.memory_consolidator = MemoryConsolidator(
            openai_client=self.openai,
            longterm_manager=self.longterm_memory,
            semantic_manager=self.semantic_memory,
        )

        # =========================================
        # Tool Patterns (D1, D2, D3, D4, D7)
        # =========================================

        # D1: Tool Registry
        self.tool_registry = ToolRegistry(
            supabase_client=supabase_client,
        )

        # D3: Schema Generation
        self.schema_generator = SchemaGenerator()

        # D2: Tool Calling
        self.tool_caller = ToolCaller(
            registry=self.tool_registry,
        )

        # D4: Parallel Tool Execution
        self.parallel_executor = ParallelToolExecutor(
            tool_caller=self.tool_caller,
        )

        # D7: Tool Chaining
        self.tool_chainer = ToolChainer(
            tool_caller=self.tool_caller,
        )

        # =========================================
        # Learning Patterns (I1, I2, I3, I5)
        # =========================================

        # I1: Feedback Loop
        self.feedback_loop = FeedbackLoop(
            supabase_client=supabase_client,
        )

        # I2: Behavior Adaptation
        self.behavior_adapter = BehaviorAdapter(
            supabase_client=supabase_client,
        )

        # I3: Pattern Recognition
        self.pattern_recognizer = PatternRecognizer(
            supabase_client=supabase_client,
        )

        # I5: Preference Learning
        self.preference_learner = PreferenceLearner(
            supabase_client=supabase_client,
            longterm_memory=self.longterm_memory,
        )

        # =========================================
        # Reasoning Patterns (A5, A12)
        # =========================================

        # A5: Adaptive Prompting
        self.adaptive_prompter = AdaptivePrompter(
            preference_learner=self.preference_learner,
            behavior_adapter=self.behavior_adapter,
            longterm_memory=self.longterm_memory,
        )

        # A12: Metacognition
        self.metacognitor = Metacognitor(
            openai_client=self.openai,
        )

        # =========================================
        # Safety Patterns (F5, F6)
        # =========================================

        # F5: Content Moderation
        self.content_moderator = ContentModerator(
            openai_client=self.openai,
        )

        # F6: PII Detection
        self.pii_detector = PIIDetector()

        # =========================================
        # Observability Patterns (J2, J5, K4)
        # =========================================

        # J2: Request Logging
        self.request_logger = RequestLogger(
            langfuse_client=langfuse_client,
            supabase_client=supabase_client,
        )

        # J5: Cost Tracking
        self.cost_tracker = CostTracker(
            supabase_client=supabase_client,
        )

        # K4: Context Compression
        self.context_compressor = ContextCompressor(
            openai_client=self.openai,
        )

        logger.info("MiddlewareStackV9 initialized with all 50 patterns")

    # =========================================
    # Memory Convenience Methods
    # =========================================

    async def remember(
        self,
        profile_id: str,
        key: str,
        value: Any,
        memory_type: str = "fact",
        importance: float = 0.5,
    ) -> bool:
        """Store a long-term memory."""
        return await self.longterm_memory.remember(
            profile_id=profile_id,
            key=key,
            value=value,
            memory_type=memory_type,
            importance=importance,
        )

    async def recall(
        self,
        profile_id: str,
        key: str,
    ) -> Optional[Any]:
        """Recall a specific memory."""
        return await self.longterm_memory.recall(profile_id, key)

    async def search_memories(
        self,
        profile_id: str,
        query: str,
        limit: int = 5,
    ) -> List[Any]:
        """Search semantic memories by similarity."""
        return await self.semantic_memory.search(
            profile_id=profile_id,
            query=query,
            limit=limit,
        )

    async def extract_and_store_memories(
        self,
        profile_id: str,
        text: str,
    ) -> int:
        """Extract memories from text and store them."""
        extracted = await self.memory_extractor.extract(text)

        stored = 0
        for memory in extracted:
            success = await self.remember(
                profile_id=profile_id,
                key=f"extracted_{memory.memory_type}_{stored}",
                value=memory.content,
                memory_type=memory.memory_type,
                importance=memory.importance,
            )
            if success:
                stored += 1

        return stored

    # =========================================
    # Safety Convenience Methods
    # =========================================

    async def check_content_safety(
        self,
        text: str,
    ) -> bool:
        """Check if content is safe."""
        result = await self.content_moderator.check(text)
        return self.content_moderator.is_safe(result)

    async def redact_pii(
        self,
        text: str,
    ) -> str:
        """Redact PII from text."""
        result = await self.pii_detector.redact(text)
        return result.redacted_text or text

    # =========================================
    # Adaptive Prompting Methods
    # =========================================

    async def adapt_prompt(
        self,
        profile_id: str,
        base_prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Adapt a prompt based on user preferences and history."""
        result = await self.adaptive_prompter.adapt(
            profile_id=profile_id,
            base_prompt=base_prompt,
            context=context,
        )
        return result.adapted_prompt

    # =========================================
    # Cost Tracking Methods
    # =========================================

    async def track_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        profile_id: Optional[str] = None,
        request_type: str = "unknown",
    ):
        """Track API cost."""
        return await self.cost_tracker.track(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            profile_id=profile_id,
            request_type=request_type,
        )

    def get_session_costs(self) -> Dict[str, Any]:
        """Get costs for current session."""
        return self.cost_tracker.get_session_total()

    # =========================================
    # Feedback Methods
    # =========================================

    async def record_feedback(
        self,
        profile_id: str,
        sentiment: str,
        context: Optional[str] = None,
    ):
        """Record user feedback."""
        if sentiment == "positive":
            return await self.feedback_loop.record_positive(profile_id, context)
        elif sentiment == "negative":
            return await self.feedback_loop.record_negative(profile_id, context)
        else:
            return await self.feedback_loop.record(
                profile_id=profile_id,
                sentiment=sentiment,
                context=context,
            )

    # =========================================
    # Context Compression Methods
    # =========================================

    async def compress_context(
        self,
        text: str,
        max_tokens: int = 4000,
    ) -> str:
        """Compress context to fit token limit."""
        result = await self.context_compressor.compress(text, max_tokens)
        return result.compressed_text

    def count_tokens(
        self,
        text: str,
    ) -> int:
        """Count tokens in text."""
        return self.cost_tracker.count_tokens(text)

    # =========================================
    # Tool Methods
    # =========================================

    def register_tool(
        self,
        name: str,
        description: str,
        handler,
        **kwargs,
    ) -> bool:
        """Register a tool."""
        return self.tool_registry.register(
            name=name,
            description=description,
            handler=handler,
            **kwargs,
        )

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ):
        """Call a registered tool."""
        return await self.tool_caller.call(tool_name, arguments)

    async def call_tools_parallel(
        self,
        tool_calls: List[Dict[str, Any]],
    ):
        """Call multiple tools in parallel."""
        return await self.parallel_executor.execute(tool_calls)

    # =========================================
    # Pattern Summary
    # =========================================

    def get_pattern_availability(self) -> Dict[str, bool]:
        """Get availability status of all Phase 3 patterns."""
        return {
            # Memory
            "B3_semantic_memory": self.semantic_memory.is_available,
            "B4_longterm_memory": self.longterm_memory.is_available,
            "B5_memory_extraction": self.memory_extractor.is_available,
            "B6_memory_consolidation": self.memory_consolidator.is_available,
            # Tools
            "D1_tool_registry": self.tool_registry.is_available,
            "D2_tool_calling": self.tool_caller.is_available,
            "D3_schema_generation": self.schema_generator.is_available,
            "D4_parallel_execution": self.parallel_executor.is_available,
            "D7_tool_chaining": self.tool_chainer.is_available,
            # Learning
            "I1_feedback_loop": self.feedback_loop.is_available,
            "I2_behavior_adaptation": self.behavior_adapter.is_available,
            "I3_pattern_recognition": self.pattern_recognizer.is_available,
            "I5_preference_learning": self.preference_learner.is_available,
            # Reasoning
            "A5_adaptive_prompting": self.adaptive_prompter.is_available,
            "A12_metacognition": self.metacognitor.is_available,
            # Safety
            "F5_content_moderation": self.content_moderator.is_available,
            "F6_pii_detection": self.pii_detector.is_available,
            # Observability
            "J2_request_logging": self.request_logger.is_available,
            "J5_cost_tracking": self.cost_tracker.is_available,
            "K4_context_compression": self.context_compressor.is_available,
        }

    def get_phase3_summary(self) -> Dict[str, Any]:
        """Get summary of Phase 3 patterns."""
        availability = self.get_pattern_availability()
        available_count = sum(1 for v in availability.values() if v)

        return {
            "phase": "3",
            "version": "9.0",
            "total_patterns": 20,
            "available_patterns": available_count,
            "availability": availability,
            "session_costs": self.get_session_costs(),
            "feedback_score": self.feedback_loop.get_session_score(),
        }
