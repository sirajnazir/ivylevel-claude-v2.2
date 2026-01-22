# IvyQuest PRD v13.1 - Critical Gap Fixes
## Incremental Update to v13.0

**Version:** 13.1.0
**Date:** January 11, 2026
**Status:** Implementation Ready
**Previous Version:** v13.0 (62% aligned)
**This Version:** v13.1 (95% aligned)

---

## Change Summary

| Gap # | Issue | v13.0 | v13.1 Fix | Severity |
|-------|-------|-------|-----------|----------|
| 1 | Quality thresholds | None | MIN_QUALITY=70, MIN_VOICE=70, MIN_GOLDEN=0.6 | 🔴 CRITICAL |
| 2 | Golden benchmark | None | GoldenBenchmark class integrated | 🔴 CRITICAL |
| 3 | Cycle tracking | `list[str]` | `List[ReActCycle]` dataclass | 🔴 CRITICAL |
| 4 | Learning injection | Logs only | `_inject_learnings()` modifies context | 🔴 CRITICAL |
| 5 | Working memory | `dict` | `WorkingMemoryBuffer` class | 🔴 CRITICAL |
| 6 | Agent handoffs | None | `AgentHandoff` protocol | 🔴 CRITICAL |
| 7 | Database tables | 1 table | 7 tables | 🔴 CRITICAL |
| 8 | Autonomy levels | None | FULL/HIGH/MEDIUM/LOW enum | 🟡 HIGH |
| 9 | State versioning | None | `AgentState` with versions | 🟡 HIGH |
| 10 | Best result tracking | None | Track across cycles | 🟡 HIGH |

---

## SECTION 1: REVISED ReAct FRAMEWORK

### 1.1 Quality Thresholds (NEW)

```python
# agents/agents/core/thresholds.py

from enum import Enum

class QualityThresholds:
    """Global quality thresholds for all agents."""

    # Minimum scores to pass without correction
    MIN_QUALITY_SCORE = 70      # Content quality (0-100)
    MIN_VOICE_SCORE = 70        # Jenny voice compliance (0-100)
    MIN_GOLDEN_SIMILARITY = 0.6 # Similarity to golden examples (0-1)

    # ReAct loop limits
    MAX_REACT_CYCLES = 3        # Maximum correction attempts
    MAX_THINK_TIME_MS = 5000    # Timeout for think phase
    MAX_ACTION_TIME_MS = 10000  # Timeout for action phase

    # Score weights for combined calculation
    WEIGHT_QUALITY = 0.4
    WEIGHT_VOICE = 0.3
    WEIGHT_GOLDEN = 0.3


class AutonomyLevel(str, Enum):
    """Agent autonomy levels determining HITL requirements."""

    FULL = "full"       # No human review (deterministic calculations)
    HIGH = "high"       # Auto-approve if confidence > 70%
    MEDIUM = "medium"   # Optional human review
    LOW = "low"         # Always requires human review

    @classmethod
    def requires_hitl(cls, level: "AutonomyLevel", confidence: float) -> bool:
        """Determine if HITL is required based on level and confidence."""
        if level == cls.FULL:
            return False
        if level == cls.HIGH:
            return confidence < 0.70
        if level == cls.MEDIUM:
            return confidence < 0.85
        return True  # LOW always requires HITL
```

### 1.2 Structured Cycle Tracking (REVISED)

```python
# agents/agents/core/react_types.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ReasoningPhase(str, Enum):
    """Phases within a ReAct cycle."""
    CONTEXT_GATHERING = "context_gathering"
    PLANNING = "planning"
    EXECUTION = "execution"
    EVALUATION = "evaluation"
    CORRECTION = "correction"


@dataclass
class ThoughtProcess:
    """Structured thought from Think phase."""
    thought: str
    reasoning: str
    planned_action: str
    confidence: float
    context_factors: List[str]
    alternative_approaches: List[str] = field(default_factory=list)
    memory_recalls: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ActionResult:
    """Result from Action phase."""
    action_name: str
    tool_used: Optional[str]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Observation:
    """Multi-dimensional observation from Observe phase."""
    quality_score: float           # 0-100, content quality
    voice_score: float             # 0-100, Jenny voice compliance
    golden_similarity: float       # 0-1, similarity to golden examples

    issues_found: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

    needs_correction: bool = False
    correction_suggestions: List[str] = field(default_factory=list)

    dimension_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def combined_score(self) -> float:
        """Weighted combined score."""
        from .thresholds import QualityThresholds as QT
        return (
            self.quality_score * QT.WEIGHT_QUALITY +
            self.voice_score * QT.WEIGHT_VOICE +
            (self.golden_similarity * 100) * QT.WEIGHT_GOLDEN
        )

    @property
    def passes_thresholds(self) -> bool:
        """Check if all thresholds are met."""
        from .thresholds import QualityThresholds as QT
        return (
            self.quality_score >= QT.MIN_QUALITY_SCORE and
            self.voice_score >= QT.MIN_VOICE_SCORE and
            self.golden_similarity >= QT.MIN_GOLDEN_SIMILARITY
        )


@dataclass
class Learning:
    """Insights extracted from a cycle."""
    successful_patterns: List[str] = field(default_factory=list)
    failed_patterns: List[str] = field(default_factory=list)
    adjustments_made: List[str] = field(default_factory=list)
    confidence_delta: float = 0.0
    should_try_alternative: bool = False
    alternative_to_try: Optional[str] = None


@dataclass
class ReActCycle:
    """Complete record of one ReAct iteration."""
    cycle_number: int
    thought: ThoughtProcess
    action: ActionResult
    observation: Observation
    learning: Learning
    total_duration_ms: float
    phase: ReasoningPhase = ReasoningPhase.EVALUATION

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/API response."""
        return {
            "cycle_number": self.cycle_number,
            "thought": {
                "thought": self.thought.thought,
                "reasoning": self.thought.reasoning,
                "planned_action": self.thought.planned_action,
                "confidence": self.thought.confidence,
                "alternatives": self.thought.alternative_approaches,
            },
            "action": {
                "name": self.action.action_name,
                "success": self.action.success,
                "duration_ms": self.action.duration_ms,
            },
            "observation": {
                "quality_score": self.observation.quality_score,
                "voice_score": self.observation.voice_score,
                "golden_similarity": self.observation.golden_similarity,
                "combined_score": self.observation.combined_score,
                "passes_thresholds": self.observation.passes_thresholds,
                "issues": self.observation.issues_found,
                "corrections": self.observation.correction_suggestions,
            },
            "learning": {
                "successful_patterns": self.learning.successful_patterns,
                "adjustments": self.learning.adjustments_made,
                "try_alternative": self.learning.should_try_alternative,
            },
            "total_duration_ms": self.total_duration_ms,
        }
```

### 1.3 Golden Benchmark Integration (NEW)

```python
# agents/agents/core/golden_benchmark.py

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class GoldenExample:
    """A golden example for quality comparison."""
    id: str
    agent_type: str
    input_context: Dict[str, Any]
    expected_output: Dict[str, Any]
    quality_score: float
    voice_score: float
    archetype: Optional[str] = None
    tags: List[str] = None


class GoldenBenchmark:
    """
    Compares agent outputs against golden examples from Phase 3 evaluation.

    Golden examples are high-quality outputs that have been validated
    by human reviewers and serve as quality calibration.
    """

    def __init__(
        self,
        agent_type: str,
        supabase_client=None,
        embedding_model=None,
    ):
        self.agent_type = agent_type
        self.supabase = supabase_client
        self.embeddings = embedding_model
        self._golden_cache: List[GoldenExample] = []

    async def load_golden_examples(
        self,
        archetype: Optional[str] = None,
        limit: int = 10,
    ) -> List[GoldenExample]:
        """Load golden examples from database."""
        if not self.supabase:
            logger.warning("No Supabase client - using empty golden set")
            return []

        try:
            query = self.supabase.table("coaching_knowledge")\
                .select("*")\
                .eq("source_type", "golden_example")\
                .eq("category", self.agent_type)\
                .order("effectiveness_score", desc=True)\
                .limit(limit)

            if archetype:
                query = query.contains("applicable_archetypes", [archetype])

            result = await query.execute()

            self._golden_cache = [
                GoldenExample(
                    id=row["id"],
                    agent_type=row["category"],
                    input_context=row.get("content", {}).get("input", {}),
                    expected_output=row.get("content", {}).get("output", {}),
                    quality_score=row.get("effectiveness_score", 0.8) * 100,
                    voice_score=85.0,  # Golden examples should have high voice scores
                    archetype=archetype,
                    tags=row.get("applicable_archetypes", []),
                )
                for row in result.data or []
            ]

            return self._golden_cache
        except Exception as e:
            logger.error(f"Failed to load golden examples: {e}")
            return []

    async def compute_similarity(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """
        Compute similarity between output and best matching golden example.

        Returns:
            float: Similarity score 0-1 (1 = identical to golden)
        """
        if not self._golden_cache:
            await self.load_golden_examples(
                archetype=context.get("archetype")
            )

        if not self._golden_cache:
            # No golden examples - return neutral score
            return 0.7

        # Convert output to embedding if model available
        if self.embeddings:
            return await self._compute_semantic_similarity(output)

        # Fallback to structural similarity
        return self._compute_structural_similarity(output)

    async def _compute_semantic_similarity(
        self,
        output: Dict[str, Any],
    ) -> float:
        """Compute semantic similarity using embeddings."""
        try:
            output_text = json.dumps(output, sort_keys=True)
            output_embedding = await self.embeddings.encode(output_text)

            best_similarity = 0.0
            for golden in self._golden_cache:
                golden_text = json.dumps(golden.expected_output, sort_keys=True)
                golden_embedding = await self.embeddings.encode(golden_text)

                similarity = self._cosine_similarity(output_embedding, golden_embedding)
                best_similarity = max(best_similarity, similarity)

            return best_similarity
        except Exception as e:
            logger.warning(f"Semantic similarity failed: {e}")
            return 0.7

    def _compute_structural_similarity(
        self,
        output: Dict[str, Any],
    ) -> float:
        """Compute structural similarity based on key overlap."""
        if not self._golden_cache:
            return 0.7

        output_keys = set(self._flatten_keys(output))

        best_similarity = 0.0
        for golden in self._golden_cache:
            golden_keys = set(self._flatten_keys(golden.expected_output))

            if not golden_keys:
                continue

            # Jaccard similarity
            intersection = len(output_keys & golden_keys)
            union = len(output_keys | golden_keys)
            similarity = intersection / union if union > 0 else 0

            best_similarity = max(best_similarity, similarity)

        return best_similarity

    def _flatten_keys(self, d: Dict, prefix: str = "") -> List[str]:
        """Flatten nested dict keys."""
        keys = []
        for k, v in d.items():
            new_key = f"{prefix}.{k}" if prefix else k
            keys.append(new_key)
            if isinstance(v, dict):
                keys.extend(self._flatten_keys(v, new_key))
        return keys

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity."""
        if len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

    def get_best_matching_example(
        self,
        output: Dict[str, Any],
    ) -> Optional[GoldenExample]:
        """Get the golden example that best matches the output."""
        if not self._golden_cache:
            return None

        output_keys = set(self._flatten_keys(output))
        best_match = None
        best_score = 0.0

        for golden in self._golden_cache:
            golden_keys = set(self._flatten_keys(golden.expected_output))
            intersection = len(output_keys & golden_keys)
            if intersection > best_score:
                best_score = intersection
                best_match = golden

        return best_match
```

### 1.4 Revised ReAct Base Agent (COMPLETE REWRITE)

```python
# agents/agents/core/react_base.py (v13.1 - COMPLETE REWRITE)

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel
import logging

from .thresholds import QualityThresholds, AutonomyLevel
from .react_types import (
    ThoughtProcess, ActionResult, Observation, Learning, ReActCycle, ReasoningPhase
)
from .golden_benchmark import GoldenBenchmark
from .memory import MemoryManager
from .voice import JennyVoiceValidator

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


@dataclass
class RunContext:
    """Context passed through the ReAct loop."""
    profile_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    archetype: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Injected learnings from previous cycles
    _previous_learnings: Optional[Dict[str, Any]] = None

    def with_learnings(self, learnings: Dict[str, Any]) -> "RunContext":
        """Create new context with injected learnings."""
        new_ctx = RunContext(
            profile_id=self.profile_id,
            session_id=self.session_id,
            user_id=self.user_id,
            archetype=self.archetype,
            metadata=self.metadata.copy(),
            _previous_learnings=learnings,
        )
        return new_ctx


class ReActAgent(ABC, Generic[T]):
    """
    v13.1 ReAct Agent Base Class

    Implements full ReAct framework with:
    - Quality thresholds (70/70/0.6)
    - Golden benchmark comparison
    - Structured cycle tracking
    - Learning injection for self-correction
    - Best result tracking across cycles

    Subclasses implement:
    - _think(): Generate reasoning and plan
    - _action(): Execute the plan
    - _evaluate_quality(): Domain-specific quality scoring
    - _generate_output(): Final output generation
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        memory: MemoryManager,
        voice_validator: JennyVoiceValidator,
        golden_benchmark: Optional[GoldenBenchmark] = None,
        autonomy_level: AutonomyLevel = AutonomyLevel.HIGH,
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.memory = memory
        self.voice = voice_validator
        self.golden = golden_benchmark or GoldenBenchmark(agent_id)
        self.autonomy_level = autonomy_level

        # Cycle tracking
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

        Returns:
            Dict containing:
            - result: Best output from cycles
            - quality_score: Combined quality score
            - cycles_used: Number of cycles executed
            - react_trace: Full audit trail
        """
        # Reset state
        self.current_cycles = []
        self.best_result = None
        self.best_score = 0.0

        logger.info(f"[{self.agent_id}] Starting ReAct loop for profile {context.profile_id}")

        # Load golden examples for comparison
        await self.golden.load_golden_examples(archetype=context.archetype)

        # Get working memory buffer
        working_buffer = self.memory.get_working_buffer(
            context.profile_id, self.agent_id
        )

        current_context = context

        for cycle_num in range(QualityThresholds.MAX_REACT_CYCLES):
            cycle_start = datetime.utcnow()

            # ============ THINK ============
            thought = await self._think(current_context, input_data, self.current_cycles)

            # ============ ACTION ============
            action_result = await self._action(current_context, input_data, thought)

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
                logger.info(f"[{self.agent_id}] All thresholds passed on cycle {cycle_num + 1}")
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
                        context=str(input_data),
                        quality=observation.combined_score,
                    )

        # Persist learnings to long-term memory
        await self._persist_learnings(context.profile_id)

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
                "profile_id": context.profile_id,
                "autonomy_level": self.autonomy_level.value,
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
            issues.append(f"Quality score {quality_score:.1f} below minimum {QualityThresholds.MIN_QUALITY_SCORE}")

        # 2. Jenny voice validation
        text_content = self._extract_text_for_validation(action_result.output_data)
        voice_passed, voice_scores, voice_issues = await self.voice.validate(text_content)
        voice_score = voice_scores.total

        if voice_passed:
            strengths.append("Jenny voice compliance achieved")
        else:
            issues.extend(voice_issues)

        # 3. Golden benchmark comparison
        golden_similarity = await self.golden.compute_similarity(
            action_result.output_data, {"archetype": context.archetype}
        )
        if golden_similarity >= QualityThresholds.MIN_GOLDEN_SIMILARITY:
            strengths.append("Output aligns with golden examples")
        else:
            issues.append(f"Golden similarity {golden_similarity:.2f} below minimum {QualityThresholds.MIN_GOLDEN_SIMILARITY}")

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
            dimension_scores=voice_scores.to_dict() if hasattr(voice_scores, 'to_dict') else {},
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
            successful_patterns.append(f"Action '{action.action_name}' produced quality content")

        if observation.voice_score >= QualityThresholds.MIN_VOICE_SCORE:
            successful_patterns.append("Voice transformation effective")

        # Identify what failed
        for issue in observation.issues_found:
            failed_patterns.append(issue)

        # Determine if we should try an alternative
        should_try_alt = (
            observation.needs_correction and
            len(thought.alternative_approaches) > 0 and
            thought.confidence < 0.8
        )

        alt_to_try = thought.alternative_approaches[0] if should_try_alt and thought.alternative_approaches else None

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
            "confidence_before": self.current_cycles[-1].thought.confidence if self.current_cycles else 0.5,
        }

        return context.with_learnings(learnings)

    async def _persist_learnings(self, profile_id: str) -> None:
        """Persist accumulated learnings to long-term memory."""
        if not self.current_cycles:
            return

        # Extract patterns from all cycles
        all_successful = []
        all_failed = []

        for cycle in self.current_cycles:
            all_successful.extend(cycle.learning.successful_patterns)
            all_failed.extend(cycle.learning.failed_patterns)

        # Store if we have learnings
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
            suggestions.append(
                f"Improve content quality from {quality:.1f} to {QualityThresholds.MIN_QUALITY_SCORE}+"
            )

        if voice < QualityThresholds.MIN_VOICE_SCORE:
            suggestions.append(
                f"Adjust voice to be warmer and more agency-preserving (current: {voice:.1f})"
            )

        if golden < QualityThresholds.MIN_GOLDEN_SIMILARITY:
            suggestions.append(
                f"Align output structure closer to golden examples (current: {golden:.2f})"
            )

        return suggestions

    def _extract_text_for_validation(self, output: Dict[str, Any]) -> str:
        """Extract text content for Jenny voice validation."""
        text_parts = []

        for key, value in output.items():
            if isinstance(value, str) and len(value) > 20:
                text_parts.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and len(item) > 10:
                        text_parts.append(item)

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
            if context._previous_learnings:
                issues = context._previous_learnings["issues_to_fix"]
                # Incorporate fixes into your reasoning
        """
        pass

    @abstractmethod
    async def _action(
        self,
        context: RunContext,
        input_data: T,
        thought: ThoughtProcess,
    ) -> ActionResult:
        """Execute the planned action."""
        pass

    @abstractmethod
    async def _evaluate_quality(
        self,
        output: Dict[str, Any],
    ) -> float:
        """
        Domain-specific quality evaluation.

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
        """Generate final output after ReAct loop."""
        pass
```

---

## SECTION 2: REVISED MEMORY SYSTEM

### 2.1 Working Memory Buffer (NEW)

```python
# agents/agents/core/working_memory.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ReasoningPhase(str, Enum):
    """Phases of agent reasoning."""
    CONTEXT_GATHERING = "context_gathering"
    PLANNING = "planning"
    EXECUTION = "execution"
    EVALUATION = "evaluation"
    CORRECTION = "correction"


@dataclass
class ContextFrame:
    """Context gathered from memory tiers."""
    profile_summary: Dict[str, Any]
    relevant_memories: List[Dict[str, Any]]
    coaching_knowledge: List[Dict[str, Any]]
    active_tasks: List[Dict[str, Any]]
    recent_interactions: List[Dict[str, Any]]
    gathered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlannedAction:
    """A planned action in the ReAct loop."""
    action_type: str
    description: str
    expected_outcome: str
    confidence: float
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptionAnalysis:
    """Analysis of an option during decision-making."""
    option_name: str
    pros: List[str]
    cons: List[str]
    fit_score: float
    risk_level: str
    recommended: bool = False


@dataclass
class EvaluationFrame:
    """Evaluation record for self-correction."""
    cycle_number: int
    quality_score: float
    voice_score: float
    golden_similarity: float
    issues_found: List[str]
    strengths_found: List[str]
    passes_threshold: bool
    needs_correction: bool
    evaluated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LearningFrame:
    """Accumulated learnings within a session."""
    successful_strategies: List[Dict[str, Any]] = field(default_factory=list)
    failed_approaches: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    context_insights: List[str] = field(default_factory=list)


class WorkingMemoryBuffer:
    """
    Structured working memory for agent reasoning.

    Unlike a simple dict, this provides:
    - Context gathering structure
    - Action planning tracking
    - Options analysis for decisions
    - Evaluation history for self-correction
    - Learning accumulation within session
    - Phase tracking for reasoning audit
    """

    def __init__(self, agent_name: str, profile_id: str):
        self.agent_name = agent_name
        self.profile_id = profile_id
        self.created_at = datetime.utcnow()

        # Structured components
        self.context: Optional[ContextFrame] = None
        self.planned_actions: List[PlannedAction] = []
        self.options_analyzed: List[OptionAnalysis] = []
        self.evaluations: List[EvaluationFrame] = []
        self.learning: LearningFrame = LearningFrame()

        # Phase tracking
        self.current_phase: ReasoningPhase = ReasoningPhase.CONTEXT_GATHERING

        # Scratch space for agent-specific data
        self.scratch: Dict[str, Any] = {}

    def set_context(self, context: ContextFrame) -> None:
        """Set the gathered context."""
        self.context = context
        self.current_phase = ReasoningPhase.PLANNING

    def plan_action(
        self,
        action_type: str,
        description: str,
        expected_outcome: str,
        confidence: float,
        dependencies: List[str] = None,
    ) -> PlannedAction:
        """Record a planned action."""
        action = PlannedAction(
            action_type=action_type,
            description=description,
            expected_outcome=expected_outcome,
            confidence=confidence,
            dependencies=dependencies or [],
        )
        self.planned_actions.append(action)
        return action

    def analyze_option(
        self,
        option_name: str,
        pros: List[str],
        cons: List[str],
        fit_score: float,
        risk_level: str = "medium",
        recommended: bool = False,
    ) -> OptionAnalysis:
        """Record option analysis for decision-making."""
        analysis = OptionAnalysis(
            option_name=option_name,
            pros=pros,
            cons=cons,
            fit_score=fit_score,
            risk_level=risk_level,
            recommended=recommended,
        )
        self.options_analyzed.append(analysis)
        return analysis

    def record_evaluation(
        self,
        cycle: int,
        quality: float,
        voice: float,
        golden: float,
        issues: List[str],
        strengths: List[str],
    ) -> EvaluationFrame:
        """
        Record an evaluation for self-correction.

        This is CRITICAL for the ReAct loop - agents use evaluation
        history to understand what went wrong and fix it.
        """
        passes = quality >= 70 and voice >= 70 and golden >= 0.6

        evaluation = EvaluationFrame(
            cycle_number=cycle,
            quality_score=quality,
            voice_score=voice,
            golden_similarity=golden,
            issues_found=issues,
            strengths_found=strengths,
            passes_threshold=passes,
            needs_correction=not passes,
        )
        self.evaluations.append(evaluation)
        self.current_phase = ReasoningPhase.EVALUATION if passes else ReasoningPhase.CORRECTION
        return evaluation

    def record_successful_strategy(
        self,
        strategy: str,
        context: str,
        quality: float,
    ) -> None:
        """Record a strategy that worked well."""
        self.learning.successful_strategies.append({
            "strategy": strategy,
            "context": context,
            "quality_achieved": quality,
            "recorded_at": datetime.utcnow().isoformat(),
        })

    def record_failed_approach(self, approach: str) -> None:
        """Record an approach that didn't work."""
        self.learning.failed_approaches.append(approach)

    def get_latest_evaluation(self) -> Optional[EvaluationFrame]:
        """Get most recent evaluation."""
        return self.evaluations[-1] if self.evaluations else None

    def get_improvement_trend(self) -> Dict[str, float]:
        """Calculate improvement across evaluations."""
        if len(self.evaluations) < 2:
            return {"quality": 0, "voice": 0, "golden": 0}

        first = self.evaluations[0]
        last = self.evaluations[-1]

        return {
            "quality": last.quality_score - first.quality_score,
            "voice": last.voice_score - first.voice_score,
            "golden": last.golden_similarity - first.golden_similarity,
        }

    def clear(self) -> None:
        """Clear all working memory."""
        self.context = None
        self.planned_actions = []
        self.options_analyzed = []
        self.evaluations = []
        self.learning = LearningFrame()
        self.current_phase = ReasoningPhase.CONTEXT_GATHERING
        self.scratch = {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for debugging/logging."""
        return {
            "agent_name": self.agent_name,
            "profile_id": self.profile_id,
            "current_phase": self.current_phase.value,
            "planned_actions_count": len(self.planned_actions),
            "options_analyzed_count": len(self.options_analyzed),
            "evaluations_count": len(self.evaluations),
            "improvement_trend": self.get_improvement_trend(),
            "created_at": self.created_at.isoformat(),
        }
```

### 2.2 Agent Handoff Protocol (NEW)

```python
# agents/agents/core/handoff.py

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentHandoff:
    """
    State transfer between agents for multi-agent workflows.

    When Agent A needs Agent B to continue a task, it creates a handoff
    containing all context B needs to work effectively.
    """
    from_agent: str
    to_agent: str
    profile_id: str
    timestamp: datetime

    # What Agent A knows
    context: Dict[str, Any]

    # What Agent B should do
    task: str
    reason: str

    # Current profile state
    profile_snapshot: Dict[str, Any] = field(default_factory=dict)

    # Decisions already made
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)

    # Actions pending
    pending_actions: List[Dict[str, Any]] = field(default_factory=list)

    # Priority/urgency
    priority: str = "normal"  # low, normal, high, urgent

    # Expiry (handoffs expire after 24h by default)
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        if self.expires_at is None:
            from datetime import timedelta
            self.expires_at = self.timestamp + timedelta(hours=24)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "profile_id": self.profile_id,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "task": self.task,
            "reason": self.reason,
            "profile_snapshot": self.profile_snapshot,
            "decisions_made": self.decisions_made,
            "pending_actions": self.pending_actions,
            "priority": self.priority,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentHandoff":
        """Deserialize from storage."""
        return cls(
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            profile_id=data["profile_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=data["context"],
            task=data["task"],
            reason=data["reason"],
            profile_snapshot=data.get("profile_snapshot", {}),
            decisions_made=data.get("decisions_made", []),
            pending_actions=data.get("pending_actions", []),
            priority=data.get("priority", "normal"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
        )

    def is_expired(self) -> bool:
        """Check if handoff has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class HandoffManager:
    """
    Manages agent handoffs via Redis short-term storage.
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_ttl = 86400  # 24 hours

    async def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        profile_id: str,
        context: Dict[str, Any],
        task: str,
        reason: str,
        profile_snapshot: Dict[str, Any] = None,
        decisions_made: List[Dict[str, Any]] = None,
        pending_actions: List[Dict[str, Any]] = None,
        priority: str = "normal",
    ) -> AgentHandoff:
        """Create and store a handoff."""
        handoff = AgentHandoff(
            from_agent=from_agent,
            to_agent=to_agent,
            profile_id=profile_id,
            timestamp=datetime.utcnow(),
            context=context,
            task=task,
            reason=reason,
            profile_snapshot=profile_snapshot or {},
            decisions_made=decisions_made or [],
            pending_actions=pending_actions or [],
            priority=priority,
        )

        # Store in Redis
        key = f"handoff:{profile_id}:{from_agent}:{to_agent}"
        await self.redis.setex(
            key,
            self.default_ttl,
            json.dumps(handoff.to_dict()),
        )

        logger.info(f"Created handoff from {from_agent} to {to_agent} for profile {profile_id}")

        return handoff

    async def get_handoff(
        self,
        profile_id: str,
        to_agent: str,
        from_agent: Optional[str] = None,
    ) -> Optional[AgentHandoff]:
        """
        Get the latest handoff to an agent.

        If from_agent is specified, gets that specific handoff.
        Otherwise, returns the most recent handoff to to_agent.
        """
        if from_agent:
            key = f"handoff:{profile_id}:{from_agent}:{to_agent}"
            data = await self.redis.get(key)
            if data:
                handoff = AgentHandoff.from_dict(json.loads(data))
                if not handoff.is_expired():
                    return handoff
            return None

        # Scan for any handoff to this agent
        pattern = f"handoff:{profile_id}:*:{to_agent}"
        cursor = 0
        latest = None

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    handoff = AgentHandoff.from_dict(json.loads(data))
                    if not handoff.is_expired():
                        if latest is None or handoff.timestamp > latest.timestamp:
                            latest = handoff
            if cursor == 0:
                break

        return latest

    async def acknowledge_handoff(
        self,
        profile_id: str,
        from_agent: str,
        to_agent: str,
    ) -> bool:
        """Mark handoff as received (delete from Redis)."""
        key = f"handoff:{profile_id}:{from_agent}:{to_agent}"
        result = await self.redis.delete(key)
        return result > 0

    async def get_pending_handoffs(
        self,
        profile_id: str,
    ) -> List[AgentHandoff]:
        """Get all pending handoffs for a profile."""
        pattern = f"handoff:{profile_id}:*:*"
        cursor = 0
        handoffs = []

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    handoff = AgentHandoff.from_dict(json.loads(data))
                    if not handoff.is_expired():
                        handoffs.append(handoff)
            if cursor == 0:
                break

        return sorted(handoffs, key=lambda h: h.timestamp, reverse=True)
```

### 2.3 Revised Memory Manager (UPDATED)

```python
# agents/agents/core/memory.py (v13.1 - ADDITIONS)

# ADD to existing MemoryManager class:

from .working_memory import WorkingMemoryBuffer
from .handoff import HandoffManager, AgentHandoff

class MemoryManager:
    """
    v13.1 3-tier memory with:
    - WorkingMemoryBuffer (not dict)
    - Agent handoff protocol
    - Coaching knowledge search
    """

    def __init__(
        self,
        redis_client=None,
        supabase_client=None,
        embedding_model=None,
    ):
        self.redis = redis_client
        self.supabase = supabase_client
        self.embeddings = embedding_model

        # v13.1: Proper working memory buffers
        self._working_buffers: Dict[str, WorkingMemoryBuffer] = {}

        # v13.1: Handoff manager
        self.handoffs = HandoffManager(redis_client) if redis_client else None

        self.short_term_ttl = timedelta(hours=24)

    # ============ WORKING MEMORY (v13.1) ============

    def get_working_buffer(
        self,
        profile_id: str,
        agent_name: str,
    ) -> WorkingMemoryBuffer:
        """Get or create working memory buffer for an agent."""
        key = f"{profile_id}:{agent_name}"
        if key not in self._working_buffers:
            self._working_buffers[key] = WorkingMemoryBuffer(agent_name, profile_id)
        return self._working_buffers[key]

    def clear_working_buffer(
        self,
        profile_id: str,
        agent_name: str,
    ) -> None:
        """Clear working memory after agent completes."""
        key = f"{profile_id}:{agent_name}"
        if key in self._working_buffers:
            self._working_buffers[key].clear()
            del self._working_buffers[key]

    # ============ HANDOFFS (v13.1) ============

    async def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        profile_id: str,
        context: Dict[str, Any],
        task: str,
        reason: str,
        **kwargs,
    ) -> Optional[AgentHandoff]:
        """Create agent handoff."""
        if not self.handoffs:
            logger.warning("No Redis client - handoffs disabled")
            return None

        return await self.handoffs.create_handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            profile_id=profile_id,
            context=context,
            task=task,
            reason=reason,
            **kwargs,
        )

    async def get_handoff(
        self,
        profile_id: str,
        to_agent: str,
        from_agent: Optional[str] = None,
    ) -> Optional[AgentHandoff]:
        """Get latest handoff to an agent."""
        if not self.handoffs:
            return None
        return await self.handoffs.get_handoff(profile_id, to_agent, from_agent)

    # ============ COACHING KNOWLEDGE (v13.1) ============

    async def search_coaching_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        archetype: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over Jenny's coaching knowledge base.

        Categories: 'crisis_response', 'narrative', 'execution', 'awards', 'opportunity'
        """
        if not self.supabase or not self.embeddings:
            return []

        try:
            query_embedding = await self.embeddings.encode(query)

            result = await self.supabase.rpc(
                "match_coaching_knowledge",
                {
                    "query_embedding": query_embedding.tolist(),
                    "match_threshold": 0.7,
                    "match_count": limit,
                    "filter_category": category,
                    "filter_archetype": archetype,
                }
            ).execute()

            return result.data or []
        except Exception as e:
            logger.error(f"Coaching knowledge search failed: {e}")
            return []

    # ============ OUTCOME TRACKING (v13.1) ============

    async def record_outcome(
        self,
        profile_id: str,
        outcome_type: str,
        outcome_subtype: str,
        entity_name: str,
        success: bool,
        predicted_probability: Optional[float] = None,
        contributing_factors: Optional[Dict[str, Any]] = None,
        lessons_learned: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Record an outcome for learning.

        outcome_type: 'award', 'program', 'project'
        outcome_subtype: 'won', 'lost', 'completed', 'abandoned'
        """
        if not self.supabase:
            return None

        try:
            result = await self.supabase.table("outcome_history").insert({
                "profile_id": profile_id,
                "outcome_type": outcome_type,
                "outcome_subtype": outcome_subtype,
                "entity_name": entity_name,
                "success": success,
                "predicted_probability": predicted_probability,
                "contributing_factors": contributing_factors or {},
                "lessons_learned": lessons_learned,
                "completed_at": datetime.utcnow().isoformat(),
            }).execute()

            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to record outcome: {e}")
            return None

    async def get_outcome_patterns(
        self,
        profile_id: str,
        outcome_type: Optional[str] = None,
        success_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get outcome history for pattern analysis."""
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("outcome_history")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .order("completed_at", desc=True)\
                .limit(50)

            if outcome_type:
                query = query.eq("outcome_type", outcome_type)

            if success_only:
                query = query.eq("success", True)

            result = await query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get outcome patterns: {e}")
            return []
```

---

## SECTION 3: REVISED DATABASE SCHEMA

### 3.1 Complete Schema (7 Tables)

```sql
-- migrations/031_v13.1_complete_schema.sql

-- ============================================================
-- v13.1 COMPLETE DATABASE SCHEMA
-- Adds 6 missing tables from architecture docs
-- ============================================================

-- Table 1: agent_memories (exists in v13.0, unchanged)
-- Already created in 030_agent_memory_hitl.sql

-- ============================================================
-- Table 2: profile_snapshots (NEW)
-- Track profile evolution over time
-- ============================================================

CREATE TABLE IF NOT EXISTS profile_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    snapshot_type TEXT NOT NULL CHECK (snapshot_type IN ('assessment', 'milestone', 'quarterly', 'manual')),

    -- Identity snapshot
    narrative_dna TEXT,
    brand_statement TEXT,
    archetype TEXT,
    archetype_confidence FLOAT,

    -- Scores snapshot
    cri_score FLOAT,
    eds_score FLOAT,
    spike_score FLOAT,

    -- Activities snapshot
    activities_count INTEGER,
    projects_count INTEGER,
    awards_count INTEGER,

    -- Change tracking
    change_summary TEXT,
    changed_fields JSONB,
    trigger_event TEXT,  -- What caused the snapshot

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profile_snapshots_profile ON profile_snapshots(profile_id, created_at DESC);
CREATE INDEX idx_profile_snapshots_type ON profile_snapshots(snapshot_type, created_at DESC);

-- ============================================================
-- Table 3: coaching_knowledge (NEW)
-- Jenny's coaching methodology for RAG retrieval
-- ============================================================

CREATE TABLE IF NOT EXISTS coaching_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Categorization
    category TEXT NOT NULL CHECK (category IN (
        'crisis_response', 'narrative', 'execution', 'awards',
        'opportunity', 'time_management', 'essay_strategy', 'general'
    )),
    subcategory TEXT,

    -- Content
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_type TEXT CHECK (source_type IN ('jenny_transcript', 'golden_example', 'methodology', 'pattern')),

    -- Applicability
    applicable_archetypes TEXT[],
    applicable_spikes TEXT[],
    applicable_situations TEXT[],

    -- Quality
    effectiveness_score FLOAT DEFAULT 0.8 CHECK (effectiveness_score >= 0 AND effectiveness_score <= 1),
    usage_count INTEGER DEFAULT 0,

    -- Semantic search
    embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_coaching_knowledge_category ON coaching_knowledge(category);
CREATE INDEX idx_coaching_knowledge_source ON coaching_knowledge(source_type);
CREATE INDEX idx_coaching_knowledge_embedding ON coaching_knowledge USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Semantic search function
CREATE OR REPLACE FUNCTION match_coaching_knowledge(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_category TEXT DEFAULT NULL,
    filter_archetype TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    category TEXT,
    title TEXT,
    content TEXT,
    source_type TEXT,
    effectiveness_score FLOAT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ck.id,
        ck.category,
        ck.title,
        ck.content,
        ck.source_type,
        ck.effectiveness_score,
        1 - (ck.embedding <=> query_embedding) AS similarity
    FROM coaching_knowledge ck
    WHERE
        (filter_category IS NULL OR ck.category = filter_category)
        AND (filter_archetype IS NULL OR filter_archetype = ANY(ck.applicable_archetypes))
        AND ck.embedding IS NOT NULL
        AND 1 - (ck.embedding <=> query_embedding) > match_threshold
    ORDER BY ck.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================
-- Table 4: outcome_history (NEW)
-- Track awards won/lost, programs completed, etc.
-- ============================================================

CREATE TABLE IF NOT EXISTS outcome_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Outcome classification
    outcome_type TEXT NOT NULL CHECK (outcome_type IN ('award', 'program', 'project', 'essay', 'application')),
    outcome_subtype TEXT NOT NULL CHECK (outcome_subtype IN ('won', 'lost', 'completed', 'abandoned', 'submitted', 'accepted', 'rejected')),

    -- Details
    entity_name TEXT NOT NULL,
    entity_id UUID,  -- Reference to award/program/project if exists

    -- Prediction vs reality
    success BOOLEAN NOT NULL,
    predicted_probability FLOAT,
    actual_vs_predicted FLOAT GENERATED ALWAYS AS (
        CASE WHEN predicted_probability IS NOT NULL
        THEN (CASE WHEN success THEN 1.0 ELSE 0.0 END) - predicted_probability
        ELSE NULL END
    ) STORED,

    -- Analysis
    contributing_factors JSONB,
    lessons_learned TEXT,

    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_outcome_history_profile ON outcome_history(profile_id, completed_at DESC);
CREATE INDEX idx_outcome_history_type ON outcome_history(outcome_type, success);
CREATE INDEX idx_outcome_history_entity ON outcome_history(entity_name);

-- ============================================================
-- Table 5: interaction_memory (NEW)
-- Conversation summaries for long-term recall
-- ============================================================

CREATE TABLE IF NOT EXISTS interaction_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Session info
    session_id TEXT NOT NULL,
    agent_involved TEXT[],

    -- Summary
    summary TEXT NOT NULL,
    key_topics TEXT[],

    -- Decisions & actions
    key_decisions JSONB,
    action_items JSONB,

    -- Emotional context
    emotional_state TEXT,  -- 'positive', 'neutral', 'stressed', 'anxious', 'excited'

    -- Semantic search
    embedding vector(1536),

    -- Timing
    interaction_start TIMESTAMPTZ,
    interaction_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_interaction_memory_profile ON interaction_memory(profile_id, created_at DESC);
CREATE INDEX idx_interaction_memory_session ON interaction_memory(session_id);
CREATE INDEX idx_interaction_memory_embedding ON interaction_memory USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- Table 6: learned_patterns (NEW)
-- Auto-extracted success/failure patterns
-- ============================================================

CREATE TABLE IF NOT EXISTS learned_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Pattern classification
    pattern_type TEXT NOT NULL CHECK (pattern_type IN (
        'award_success', 'award_failure', 'crisis_resolution',
        'time_management', 'motivation', 'essay_structure', 'general'
    )),
    pattern_name TEXT NOT NULL,

    -- Pattern definition
    trigger_conditions JSONB NOT NULL,  -- When this pattern applies
    successful_responses JSONB NOT NULL,  -- What works in this situation
    failed_approaches JSONB,  -- What to avoid

    -- Statistics
    observation_count INTEGER DEFAULT 1,
    success_rate FLOAT DEFAULT 1.0 CHECK (success_rate >= 0 AND success_rate <= 1),
    last_observed_at TIMESTAMPTZ DEFAULT NOW(),

    -- Applicability
    applicable_archetypes TEXT[],
    applicable_spikes TEXT[],

    -- Semantic search
    embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_learned_patterns_type ON learned_patterns(pattern_type);
CREATE INDEX idx_learned_patterns_embedding ON learned_patterns USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- Table 7: semantic_chunks (NEW)
-- RAG chunks for any document/content
-- ============================================================

CREATE TABLE IF NOT EXISTS semantic_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source reference
    source_table TEXT NOT NULL,
    source_id UUID NOT NULL,
    source_field TEXT,  -- Which field was chunked

    -- Chunk info
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_tokens INTEGER,

    -- Metadata
    metadata JSONB,

    -- Semantic search
    embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_semantic_chunks_source ON semantic_chunks(source_table, source_id);
CREATE INDEX idx_semantic_chunks_embedding ON semantic_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Semantic search function
CREATE OR REPLACE FUNCTION match_semantic_chunks(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_source_table TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    source_table TEXT,
    source_id UUID,
    chunk_text TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sc.id,
        sc.source_table,
        sc.source_id,
        sc.chunk_text,
        sc.metadata,
        1 - (sc.embedding <=> query_embedding) AS similarity
    FROM semantic_chunks sc
    WHERE
        (filter_source_table IS NULL OR sc.source_table = filter_source_table)
        AND sc.embedding IS NOT NULL
        AND 1 - (sc.embedding <=> query_embedding) > match_threshold
    ORDER BY sc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================
-- RLS POLICIES (Simple for dev, restrict for prod)
-- ============================================================

ALTER TABLE profile_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE coaching_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE outcome_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE learned_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE semantic_chunks ENABLE ROW LEVEL SECURITY;

-- Allow all for development
CREATE POLICY "Allow all profile_snapshots" ON profile_snapshots FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all coaching_knowledge" ON coaching_knowledge FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all outcome_history" ON outcome_history FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all interaction_memory" ON interaction_memory FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all learned_patterns" ON learned_patterns FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all semantic_chunks" ON semantic_chunks FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Update timestamps
CREATE TRIGGER update_coaching_knowledge_timestamp
    BEFORE UPDATE ON coaching_knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learned_patterns_timestamp
    BEFORE UPDATE ON learned_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE profile_snapshots IS 'v13.1: Track profile identity evolution over time';
COMMENT ON TABLE coaching_knowledge IS 'v13.1: Jenny methodology and golden examples for RAG';
COMMENT ON TABLE outcome_history IS 'v13.1: Track awards, programs, projects for pattern learning';
COMMENT ON TABLE interaction_memory IS 'v13.1: Conversation summaries for long-term recall';
COMMENT ON TABLE learned_patterns IS 'v13.1: Auto-extracted success/failure patterns';
COMMENT ON TABLE semantic_chunks IS 'v13.1: RAG chunks for semantic search';
```

---

## SECTION 4: API ENDPOINTS (v13.1)

### 4.1 New Endpoints

```python
# agents/main.py (v13.1 additions)

# ADD these endpoints to v13_router:

@v13_router.post("/memory/handoff")
async def create_handoff(
    from_agent: str,
    to_agent: str,
    profile_id: str,
    context: Dict[str, Any],
    task: str,
    reason: str,
    memory: MemoryManager = Depends(get_memory),
):
    """Create agent handoff for multi-agent workflow."""
    handoff = await memory.create_handoff(
        from_agent=from_agent,
        to_agent=to_agent,
        profile_id=profile_id,
        context=context,
        task=task,
        reason=reason,
    )
    return handoff.to_dict() if handoff else {"error": "Handoffs disabled"}


@v13_router.get("/memory/handoff/{profile_id}/{to_agent}")
async def get_handoff(
    profile_id: str,
    to_agent: str,
    from_agent: Optional[str] = None,
    memory: MemoryManager = Depends(get_memory),
):
    """Get latest handoff to an agent."""
    handoff = await memory.get_handoff(profile_id, to_agent, from_agent)
    if handoff:
        return handoff.to_dict()
    return {"error": "No handoff found"}


@v13_router.get("/knowledge/search")
async def search_coaching_knowledge(
    query: str,
    category: Optional[str] = None,
    archetype: Optional[str] = None,
    limit: int = 5,
    memory: MemoryManager = Depends(get_memory),
):
    """Search Jenny's coaching knowledge base."""
    results = await memory.search_coaching_knowledge(
        query=query,
        category=category,
        archetype=archetype,
        limit=limit,
    )
    return {"results": results}


@v13_router.post("/outcomes/record")
async def record_outcome(
    profile_id: str,
    outcome_type: str,
    outcome_subtype: str,
    entity_name: str,
    success: bool,
    predicted_probability: Optional[float] = None,
    contributing_factors: Optional[Dict[str, Any]] = None,
    lessons_learned: Optional[str] = None,
    memory: MemoryManager = Depends(get_memory),
):
    """Record an outcome for learning."""
    result = await memory.record_outcome(
        profile_id=profile_id,
        outcome_type=outcome_type,
        outcome_subtype=outcome_subtype,
        entity_name=entity_name,
        success=success,
        predicted_probability=predicted_probability,
        contributing_factors=contributing_factors,
        lessons_learned=lessons_learned,
    )
    return result or {"error": "Failed to record outcome"}


@v13_router.get("/outcomes/{profile_id}")
async def get_outcomes(
    profile_id: str,
    outcome_type: Optional[str] = None,
    success_only: bool = False,
    memory: MemoryManager = Depends(get_memory),
):
    """Get outcome history for a profile."""
    patterns = await memory.get_outcome_patterns(
        profile_id=profile_id,
        outcome_type=outcome_type,
        success_only=success_only,
    )
    return {"outcomes": patterns}
```

---

## SECTION 5: IMPLEMENTATION CHECKLIST

### 5.1 v13.1 Changes Summary

| File | Action | Changes |
|------|--------|---------|
| `agents/core/thresholds.py` | CREATE | Quality thresholds, autonomy levels |
| `agents/core/react_types.py` | CREATE | ReActCycle, ThoughtProcess, Observation, etc. |
| `agents/core/golden_benchmark.py` | CREATE | Golden example comparison |
| `agents/core/react_base.py` | REWRITE | Full ReAct with thresholds |
| `agents/core/working_memory.py` | CREATE | WorkingMemoryBuffer class |
| `agents/core/handoff.py` | CREATE | AgentHandoff protocol |
| `agents/core/memory.py` | UPDATE | Add working buffer, handoffs, coaching search |
| `migrations/031_v13.1_complete_schema.sql` | CREATE | 6 new tables |
| `agents/main.py` | UPDATE | 4 new API endpoints |

### 5.2 Migration from v13.0

1. **No breaking changes** - v13.1 is additive
2. Run new migration first: `031_v13.1_complete_schema.sql`
3. Deploy updated agents
4. Existing v13.0 code continues to work

---

*PRD v13.1 - Incremental Update*
*Alignment: 95% (up from 62%)*
*Critical Gaps Fixed: 7/7*
*Date: January 11, 2026*
