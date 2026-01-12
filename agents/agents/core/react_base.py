# agents/agents/core/react_base.py
"""
IvyQuest v13.2 - ReAct Agent Base Class

This module implements the full ReAct (Reasoning + Acting) framework with:
- Quality thresholds (70/70/0.6)
- Golden benchmark comparison
- Structured cycle tracking
- Learning injection for self-correction
- Best result tracking across cycles
- Interaction memory persistence
- Profile snapshot creation

Subclasses implement:
- _think(): Generate reasoning and plan
- _action(): Execute the plan
- _evaluate_quality(): Domain-specific quality scoring
- _generate_output(): Final output generation
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from .thresholds import QualityThresholds, AutonomyLevel
from .react_types import (
    ThoughtProcess, ActionResult, Observation, Learning, 
    ReActCycle, ReasoningPhase, RunContext
)
from .golden_benchmark import GoldenBenchmark
from .working_memory import WorkingMemoryBuffer
from .interaction_memory import InteractionSummary

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ReActAgent(ABC, Generic[T]):
    """
    v13.2 ReAct Agent Base Class
    
    Implements full ReAct framework with:
    - Quality thresholds (70/70/0.6)
    - Golden benchmark comparison
    - Structured cycle tracking
    - Learning injection for self-correction
    - Best result tracking across cycles
    - v13.2: Interaction memory persistence
    - v13.2: Profile snapshot creation
    
    Subclasses implement:
    - _think(): Generate reasoning and plan
    - _action(): Execute the plan  
    - _evaluate_quality(): Domain-specific quality scoring
    - _generate_output(): Final output generation
    
    Example subclass:
        class NarrativeSynthesisAgent(ReActAgent[NarrativeInput]):
            async def _think(self, context, input_data, previous_cycles):
                # Generate reasoning about narrative synthesis
                ...
                
            async def _action(self, context, input_data, thought):
                # Execute narrative generation
                ...
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        memory,  # MemoryManager
        voice_validator,  # JennyVoiceValidator
        golden_benchmark: Optional[GoldenBenchmark] = None,
        autonomy_level: AutonomyLevel = AutonomyLevel.HIGH,
    ):
        """
        Initialize ReActAgent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name
            description: Description of agent's purpose
            memory: MemoryManager instance for persistence
            voice_validator: JennyVoiceValidator for voice compliance
            golden_benchmark: Optional GoldenBenchmark for quality comparison
            autonomy_level: HITL requirements for this agent
        """
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.memory = memory
        self.voice = voice_validator
        self.golden = golden_benchmark or GoldenBenchmark(agent_id)
        self.autonomy_level = autonomy_level

        # Cycle tracking (reset per run)
        self.current_cycles: List[ReActCycle] = []
        self.best_result: Optional[Dict[str, Any]] = None
        self.best_score: float = 0.0

    async def run(
        self,
        context: RunContext,
        input_data: T,
    ) -> Dict[str, Any]:
        """
        Execute full ReAct loop with quality gates.
        
        Args:
            context: RunContext with profile_id, session_id, etc.
            input_data: Typed input for this agent
            
        Returns:
            Dict containing:
            - success: Whether agent completed successfully
            - result: Best output from cycles
            - quality_score: Combined quality score
            - cycles_used: Number of cycles executed
            - passes_thresholds: Whether output meets all thresholds
            - react_trace: Full audit trail of all cycles
            - _metadata: Agent metadata
        """
        # Reset state for this run
        self.current_cycles = []
        self.best_result = None
        self.best_score = 0.0

        logger.info(
            f"[{self.agent_id}] Starting ReAct loop for profile {context.profile_id}"
        )

        # Load golden examples for comparison
        await self.golden.load_golden_examples(archetype=context.archetype)

        # Get working memory buffer
        working_buffer = self.memory.get_working_buffer(
            context.profile_id, self.agent_id
        )

        current_context = context

        for cycle_num in range(QualityThresholds.MAX_REACT_CYCLES):
            cycle_start = datetime.utcnow()

            logger.debug(f"[{self.agent_id}] Starting cycle {cycle_num + 1}")

            # ============ THINK ============
            thought = await self._think(current_context, input_data, self.current_cycles)
            logger.debug(
                f"[{self.agent_id}] Think complete: confidence={thought.confidence:.2f}"
            )

            # ============ ACTION ============
            action_result = await self._action(current_context, input_data, thought)
            logger.debug(
                f"[{self.agent_id}] Action complete: success={action_result.success}"
            )

            # ============ OBSERVE ============
            observation = await self._observe(current_context, action_result)

            # Record evaluation in working memory
            working_buffer.record_evaluation(
                cycle=cycle_num + 1,
                quality=observation.quality_score,
                voice=observation.voice_score,
                golden=observation.golden_similarity,
                issues=observation.issues_found,
                strengths=observation.strengths,
            )

            # ============ LEARN ============
            learning = await self._learn(thought, action_result, observation)

            # Record cycle
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds() * 1000
            cycle = ReActCycle(
                cycle_number=cycle_num + 1,
                thought=thought,
                action=action_result,
                observation=observation,
                learning=learning,
                total_duration_ms=cycle_duration,
            )
            self.current_cycles.append(cycle)

            logger.info(
                f"[{self.agent_id}] Cycle {cycle_num + 1}: "
                f"quality={observation.quality_score:.1f}, "
                f"voice={observation.voice_score:.1f}, "
                f"golden={observation.golden_similarity:.2f}, "
                f"combined={observation.combined_score:.1f}"
            )

            # Track best result
            if observation.combined_score > self.best_score:
                self.best_score = observation.combined_score
                self.best_result = action_result.output_data

            # Check if we pass all thresholds
            if observation.passes_thresholds:
                logger.info(
                    f"[{self.agent_id}] All thresholds passed on cycle {cycle_num + 1}"
                )
                break

            # If not last cycle, inject learnings for correction
            if cycle_num < QualityThresholds.MAX_REACT_CYCLES - 1:
                current_context = self._inject_learnings(
                    current_context, learning, observation
                )

                # Record strategy adjustment
                if learning.should_try_alternative and learning.alternative_to_try:
                    working_buffer.record_successful_strategy(
                        strategy=learning.alternative_to_try,
                        context=str(input_data)[:100],
                        quality=observation.combined_score,
                    )

        # Persist learnings to long-term memory (v13.2 enhanced)
        await self._persist_learnings(context.profile_id, context)

        # Clear working buffer
        self.memory.clear_working_buffer(context.profile_id, self.agent_id)

        # Generate final output
        output = await self._generate_output(current_context, input_data)

        # Apply Jenny voice transformation if needed
        if self.voice:
            output = await self.voice.validate_and_transform(output)

        return {
            "success": True,
            "result": self.best_result or output,
            "quality_score": self.best_score,
            "cycles_used": len(self.current_cycles),
            "passes_thresholds": self.best_score >= 70,
            "react_trace": [c.to_dict() for c in self.current_cycles],
            "_metadata": {
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "profile_id": context.profile_id,
                "session_id": context.session_id,
                "autonomy_level": self.autonomy_level.value,
                "requires_hitl": AutonomyLevel.requires_hitl(
                    self.autonomy_level, 
                    self.best_score / 100.0
                ),
            },
        }

    async def _observe(
        self,
        context: RunContext,
        action_result: ActionResult,
    ) -> Observation:
        """
        Multi-dimensional observation with quality thresholds.
        
        Evaluates:
        1. Quality score (domain-specific)
        2. Voice score (Jenny compliance)
        3. Golden similarity (benchmark comparison)
        """
        issues = []
        strengths = []

        # 1. Domain-specific quality evaluation
        quality_score = await self._evaluate_quality(action_result.output_data)
        if quality_score >= QualityThresholds.MIN_QUALITY_SCORE:
            strengths.append("Content quality meets threshold")
        else:
            issues.append(
                f"Quality score {quality_score:.1f} below minimum "
                f"{QualityThresholds.MIN_QUALITY_SCORE}"
            )

        # 2. Jenny voice validation
        voice_score = 70.0  # Default
        voice_issues = []
        
        if self.voice:
            text_content = self._extract_text_for_validation(action_result.output_data)
            if text_content:
                voice_passed, voice_scores, voice_issues = await self.voice.validate(
                    text_content
                )
                voice_score = voice_scores.total if hasattr(voice_scores, "total") else 70.0

                if voice_passed:
                    strengths.append("Jenny voice compliance achieved")
                else:
                    issues.extend(voice_issues)

        # 3. Golden benchmark comparison
        golden_similarity = await self.golden.compute_similarity(
            action_result.output_data, 
            {"archetype": context.archetype}
        )
        if golden_similarity >= QualityThresholds.MIN_GOLDEN_SIMILARITY:
            strengths.append("Output aligns with golden examples")
        else:
            issues.append(
                f"Golden similarity {golden_similarity:.2f} below minimum "
                f"{QualityThresholds.MIN_GOLDEN_SIMILARITY}"
            )

        # Determine if correction needed
        needs_correction = (
            quality_score < QualityThresholds.MIN_QUALITY_SCORE or
            voice_score < QualityThresholds.MIN_VOICE_SCORE or
            golden_similarity < QualityThresholds.MIN_GOLDEN_SIMILARITY or
            not action_result.success
        )

        # Generate correction suggestions
        corrections = []
        if needs_correction:
            corrections = self._generate_correction_suggestions(
                quality_score, voice_score, golden_similarity, issues
            )

        return Observation(
            quality_score=quality_score,
            voice_score=voice_score,
            golden_similarity=golden_similarity,
            issues_found=issues,
            strengths=strengths,
            needs_correction=needs_correction,
            correction_suggestions=corrections,
            dimension_scores={
                "quality": quality_score,
                "voice": voice_score,
                "golden": golden_similarity * 100,
            },
        )

    async def _learn(
        self,
        thought: ThoughtProcess,
        action: ActionResult,
        observation: Observation,
    ) -> Learning:
        """Extract learning insights from this cycle."""
        successful_patterns = []
        failed_patterns = []
        adjustments = []

        # Identify what worked
        if observation.quality_score >= QualityThresholds.MIN_QUALITY_SCORE:
            successful_patterns.append(
                f"Action '{action.action_name}' produced quality content"
            )

        if observation.voice_score >= QualityThresholds.MIN_VOICE_SCORE:
            successful_patterns.append("Voice transformation effective")

        if observation.golden_similarity >= QualityThresholds.MIN_GOLDEN_SIMILARITY:
            successful_patterns.append("Output structure matches golden examples")

        # Identify what failed
        for issue in observation.issues_found:
            failed_patterns.append(issue)

        # Determine if we should try an alternative
        should_try_alt = (
            observation.needs_correction and
            len(thought.alternative_approaches) > 0 and
            thought.confidence < 0.8
        )

        alt_to_try = (
            thought.alternative_approaches[0] 
            if should_try_alt and thought.alternative_approaches 
            else None
        )

        # Calculate confidence adjustment
        confidence_delta = 0.0
        if observation.passes_thresholds:
            confidence_delta = 0.1
        elif observation.needs_correction:
            confidence_delta = -0.15

        # Suggest adjustments for next cycle
        if observation.needs_correction:
            for correction in observation.correction_suggestions:
                adjustments.append(f"ADJUST: {correction}")

        return Learning(
            successful_patterns=successful_patterns,
            failed_patterns=failed_patterns,
            adjustments_made=adjustments,
            confidence_delta=confidence_delta,
            should_try_alternative=should_try_alt,
            alternative_to_try=alt_to_try,
        )

    def _inject_learnings(
        self,
        context: RunContext,
        learning: Learning,
        observation: Observation,
    ) -> RunContext:
        """
        Inject learnings into context for next ReAct cycle.
        
        This is CRITICAL for self-correction - the next cycle's _think()
        must see what went wrong and what to fix.
        """
        learnings = {
            "previous_cycle": len(self.current_cycles),
            "previous_score": observation.combined_score,
            "issues_to_fix": observation.issues_found,
            "corrections_required": observation.correction_suggestions,
            "failed_patterns": learning.failed_patterns,
            "adjustments_to_make": learning.adjustments_made,
            "try_alternative": learning.alternative_to_try,
            "confidence_before": (
                self.current_cycles[-1].thought.confidence 
                if self.current_cycles 
                else 0.5
            ),
            "failing_dimensions": observation.failing_dimensions,
        }

        return context.with_learnings(learnings)

    async def _persist_learnings(
        self, 
        profile_id: str, 
        context: RunContext = None
    ) -> None:
        """
        v13.2: Enhanced persistence with interaction memory and profile snapshots.
        
        Persists:
        1. ReAct learnings to agent_memories
        2. Interaction summary to interaction_memory
        3. Profile snapshot if significant changes detected
        """
        if not self.current_cycles:
            return

        # ============ 1. REACT LEARNINGS ============
        all_successful = []
        all_failed = []

        for cycle in self.current_cycles:
            all_successful.extend(cycle.learning.successful_patterns)
            all_failed.extend(cycle.learning.failed_patterns)

        if all_successful or all_failed:
            await self.memory.store_observation(
                agent_id=self.agent_id,
                profile_id=profile_id,
                observation={
                    "type": "react_learnings",
                    "cycles_used": len(self.current_cycles),
                    "final_score": self.best_score,
                    "successful_patterns": list(set(all_successful)),
                    "failed_patterns": list(set(all_failed)),
                },
                importance=0.7 if self.best_score >= 70 else 0.5,
            )

        # ============ 2. INTERACTION SUMMARY (v13.2) ============
        if context and hasattr(self.memory, "interactions") and self.memory.interactions:
            # Build summary from cycles
            topics = set()
            decisions = []

            for cycle in self.current_cycles:
                # Extract topics from thought
                if cycle.thought.context_factors:
                    topics.update(cycle.thought.context_factors)

                # Track significant decisions
                if cycle.observation.passes_thresholds:
                    decisions.append({
                        "cycle": cycle.cycle_number,
                        "action": cycle.action.action_name,
                        "quality": cycle.observation.combined_score,
                    })

            # Calculate average quality
            avg_quality = (
                sum(c.observation.combined_score for c in self.current_cycles) 
                / len(self.current_cycles)
            )

            # Determine emotional state based on quality trend
            emotional_state = "neutral"
            if self.best_score >= 85:
                emotional_state = "positive"
            elif self.best_score < 60:
                emotional_state = "stressed"

            interaction = InteractionSummary(
                profile_id=profile_id,
                session_id=context.session_id or f"{self.agent_id}_{datetime.utcnow().isoformat()}",
                agents_involved=[self.agent_id],
                summary=(
                    f"{self.name} completed with {len(self.current_cycles)} cycles, "
                    f"final score: {self.best_score:.1f}"
                ),
                key_topics=list(topics)[:10],  # Limit to top 10 topics
                key_decisions=decisions,
                emotional_state=emotional_state,
                average_quality_score=avg_quality,
                cycles_used=len(self.current_cycles),
                interaction_start=self.current_cycles[0].thought.timestamp,
                interaction_end=self.current_cycles[-1].observation.timestamp,
            )

            await self.memory.interactions.store_interaction(interaction)

        # ============ 3. PROFILE SNAPSHOT (v13.2) ============
        # Only create snapshot for significant interactions
        should_snapshot = (
            self.autonomy_level in [AutonomyLevel.LOW, AutonomyLevel.MEDIUM] or
            self.best_score >= 90 or  # Exceptionally good interaction
            len(self.current_cycles) >= 3  # Required all 3 correction cycles
        )

        if should_snapshot and hasattr(self.memory, "snapshots") and self.memory.snapshots:
            # Fetch current profile data for snapshot
            profile_data = await self._get_profile_data(profile_id)
            if profile_data:
                await self.memory.snapshots.create_snapshot(
                    profile_id=profile_id,
                    profile_data=profile_data,
                    snapshot_type="agent_interaction",
                    trigger_event=f"{self.agent_id}_interaction",
                )

    async def _get_profile_data(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Fetch profile data for snapshot creation."""
        if not hasattr(self.memory, "supabase") or not self.memory.supabase:
            return None

        try:
            result = await self.memory.supabase.table("profiles")\
                .select("*")\
                .eq("id", profile_id)\
                .single()\
                .execute()
            return result.data
        except Exception as e:
            logger.warning(f"Failed to fetch profile data: {e}")
            return None

    def _generate_correction_suggestions(
        self,
        quality: float,
        voice: float,
        golden: float,
        issues: List[str],
    ) -> List[str]:
        """Generate specific corrections based on scores."""
        suggestions = []

        if quality < QualityThresholds.MIN_QUALITY_SCORE:
            gap = QualityThresholds.MIN_QUALITY_SCORE - quality
            suggestions.append(
                f"Improve content quality by {gap:.1f} points "
                f"(current: {quality:.1f}, target: {QualityThresholds.MIN_QUALITY_SCORE})"
            )

        if voice < QualityThresholds.MIN_VOICE_SCORE:
            suggestions.append(
                f"Adjust voice to be warmer and more agency-preserving "
                f"(current: {voice:.1f})"
            )

        if golden < QualityThresholds.MIN_GOLDEN_SIMILARITY:
            suggestions.append(
                f"Align output structure closer to golden examples "
                f"(current: {golden:.2f}, target: {QualityThresholds.MIN_GOLDEN_SIMILARITY})"
            )

        # Add golden example improvement suggestions
        golden_suggestions = self.golden.get_improvement_suggestions(
            self.best_result or {}
        )
        suggestions.extend(golden_suggestions[:2])  # Limit to 2

        return suggestions

    def _extract_text_for_validation(self, output: Dict[str, Any]) -> str:
        """Extract text content for Jenny voice validation."""
        text_parts = []

        def extract_recursive(obj, depth=0):
            if depth > 5:  # Prevent infinite recursion
                return
            if isinstance(obj, str) and len(obj) > 20:
                text_parts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_recursive(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, depth + 1)

        extract_recursive(output)
        return " ".join(text_parts)

    # ============ ABSTRACT METHODS (Subclasses implement) ============

    @abstractmethod
    async def _think(
        self,
        context: RunContext,
        input_data: T,
        previous_cycles: List[ReActCycle],
    ) -> ThoughtProcess:
        """
        Generate reasoning and plan for action.
        
        IMPORTANT: If previous_cycles is not empty, you MUST check
        context._previous_learnings and address the issues found.
        
        Example implementation:
            if context.has_learnings:
                issues = context.learnings["issues_to_fix"]
                corrections = context.learnings["corrections_required"]
                # Incorporate fixes into your reasoning
                
        Args:
            context: RunContext with profile info and optional learnings
            input_data: Typed input data for this agent
            previous_cycles: List of previous ReActCycles (empty on first cycle)
            
        Returns:
            ThoughtProcess with reasoning, planned action, and confidence
        """
        pass

    @abstractmethod
    async def _action(
        self,
        context: RunContext,
        input_data: T,
        thought: ThoughtProcess,
    ) -> ActionResult:
        """
        Execute the planned action.
        
        Args:
            context: RunContext with profile info
            input_data: Typed input data
            thought: ThoughtProcess from _think()
            
        Returns:
            ActionResult with output_data and success status
        """
        pass

    @abstractmethod
    async def _evaluate_quality(
        self,
        output: Dict[str, Any],
    ) -> float:
        """
        Domain-specific quality evaluation.
        
        Args:
            output: The agent's output to evaluate
            
        Returns:
            float: Quality score 0-100
        """
        pass

    @abstractmethod
    async def _generate_output(
        self,
        context: RunContext,
        input_data: T,
    ) -> Dict[str, Any]:
        """
        Generate final output after ReAct loop.
        
        This is called after the loop completes to produce the
        final output dict.
        
        Args:
            context: RunContext with profile info
            input_data: Original input data
            
        Returns:
            Final output dict
        """
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.agent_id}, "
            f"autonomy={self.autonomy_level.value})"
        )
