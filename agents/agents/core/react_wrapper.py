"""
ReAct Wrapper - TRUE Agentic Self-Correction Framework for IvyQuest Agents
==========================================================================
v4.2 Implementation - TRUE AGENTIC INTELLIGENCE

ReAct (Reasoning + Acting) framework with LLM-powered reasoning that wraps
existing agents to provide intelligent self-correction capabilities.

**Key Improvements in v4.2:**
- LLM-based THINK phase with actual reasoning about profiles
- Tool registry for archetype classification, spike generation, benchmarking
- Golden examples database for comparison against successful profiles
- Specific, actionable hints instead of generic "ensure fields populated"
- Gap analysis with severity categorization
- Agents receive structured _react_feedback with specific guidance

Flow:
1. THINK: Analyze profile using tools, identify specific gaps
2. ACT: Execute agent's process method with targeted hints
3. OBSERVE: Validate output using guardrails + golden benchmark
4. LEARN: Generate specific improvement hints based on gap analysis
5. REPEAT until quality threshold met or max cycles reached

Quality Thresholds:
- MIN_QUALITY_SCORE: 70 (guardrails confidence * 100)
- MIN_VOICE_SCORE: 70 (Jenny voice compliance)
- MIN_GOLDEN_SIMILARITY: 0.6 (golden benchmark comparison)
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime
import asyncio
import logging
import hashlib
import random

from config import FEATURE_FLAGS

if TYPE_CHECKING:
    from agents.core.voice_validator import JennyVoiceValidator
    from agents.core.golden_benchmark import GoldenBenchmark

# Import agentic components
try:
    from agents.core.agentic_reasoner import AgenticReasoner, get_agentic_reasoner, ThinkingResult, LearningResult
    from agents.core.agentic_tools import ToolRegistry, get_tool_registry
    from agents.core.golden_examples_db import get_golden_examples_db, GoldenExamplesDB
    AGENTIC_ENABLED = True
except ImportError as e:
    logging.warning(f"Agentic components not available: {e}")
    AGENTIC_ENABLED = False

# Configure logging
logger = logging.getLogger(__name__)


# =============================================================================
# QUALITY THRESHOLDS (from thresholds.py)
# =============================================================================
MIN_QUALITY_SCORE = 70      # Guardrails confidence threshold (0-100)
MIN_VOICE_SCORE = 70        # Jenny voice compliance threshold (0-100)
MIN_GOLDEN_SIMILARITY = 0.6 # Golden benchmark similarity threshold (0-1)
MAX_REACT_CYCLES = 3        # Maximum correction cycles


@dataclass
class ReActCycle:
    """Record of a single ReAct cycle."""
    cycle_number: int
    think: str
    action: str
    observation: Dict[str, Any]
    learning: Optional[str] = None
    quality_score: float = 0.0
    voice_score: Optional[float] = None
    golden_similarity: Optional[float] = None
    duration_ms: int = 0
    passed: bool = False


@dataclass
class ReActResult:
    """Complete result from ReAct execution."""
    success: bool
    output: Dict[str, Any]
    cycles: List[ReActCycle] = field(default_factory=list)
    total_cycles: int = 0
    final_quality_score: float = 0.0
    final_voice_score: Optional[float] = None
    final_golden_similarity: Optional[float] = None
    improvement_trajectory: List[float] = field(default_factory=list)
    ab_test_group: Optional[str] = None  # "treatment" or "control"
    profile_id: Optional[str] = None
    agent_name: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "total_cycles": self.total_cycles,
            "final_quality_score": self.final_quality_score,
            "final_voice_score": self.final_voice_score,
            "final_golden_similarity": self.final_golden_similarity,
            "improvement_trajectory": self.improvement_trajectory,
            "ab_test_group": self.ab_test_group,
            "total_duration_ms": self.total_duration_ms,
        }


class ReActWrapper:
    """
    Non-invasive wrapper that adds ReAct self-correction to any agent.

    Wraps an agent's process() method to add:
    - Quality validation after each execution
    - Self-correction through improvement hints
    - A/B testing support
    - Improvement trajectory tracking

    Usage:
        wrapped_agent = create_react_wrapped_agent(my_agent)
        result = await wrapped_agent.process(profile_id)
    """

    def __init__(
        self,
        agent: Any,
        max_cycles: Optional[int] = None,
        min_confidence: Optional[float] = None,
        voice_validator: Optional["JennyVoiceValidator"] = None,
        golden_benchmark: Optional["GoldenBenchmark"] = None,
        enable_logging: bool = True,
        enable_agentic: bool = True,
    ):
        """
        Initialize ReAct wrapper.

        Args:
            agent: The agent to wrap (must have .process() and .name)
            max_cycles: Override for max correction cycles
            min_confidence: Override for minimum quality threshold
            voice_validator: Optional Jenny voice validator
            golden_benchmark: Optional golden benchmark comparator
            enable_logging: Whether to log cycle details
            enable_agentic: Whether to use agentic reasoning (v4.2)
        """
        self.agent = agent
        self.name = getattr(agent, "name", agent.__class__.__name__)
        self.max_cycles = max_cycles or FEATURE_FLAGS.get("react_max_cycles", MAX_REACT_CYCLES)
        self.min_confidence = min_confidence or FEATURE_FLAGS.get("react_min_confidence", MIN_QUALITY_SCORE / 100)
        self.voice_validator = voice_validator
        self.golden_benchmark = golden_benchmark
        self.enable_logging = enable_logging
        self.enable_agentic = enable_agentic and AGENTIC_ENABLED

        # State
        self._current_hints: List[str] = []
        self._improvement_trajectory: List[float] = []

        # v4.2: Agentic components
        if self.enable_agentic:
            self._reasoner = get_agentic_reasoner()
            self._tool_registry = get_tool_registry()
            self._golden_db = get_golden_examples_db()
        else:
            self._reasoner = None
            self._tool_registry = None
            self._golden_db = None

        # Track thinking results across cycles
        self._thinking_history: List[Dict[str, Any]] = []
        self._learning_history: List[Dict[str, Any]] = []

    async def process(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute agent with ReAct self-correction loop.

        Args:
            profile_id: The profile to process
            **kwargs: Additional arguments for the agent

        Returns:
            Dict with agent output plus ReAct metadata
        """
        # Check if ReAct is enabled
        if not FEATURE_FLAGS.get("enable_react", False):
            # Direct passthrough when ReAct is disabled
            return await self.agent.process(profile_id, **kwargs)

        # A/B test assignment
        ab_group = self._assign_ab_group(profile_id)

        if ab_group == "control":
            # Control group: no ReAct, just run agent directly
            result = await self.agent.process(profile_id, **kwargs)
            control_meta = {
                "success": result.get("success", False),
                "cycles_executed": 1,
                "max_cycles": self.max_cycles,
                "final_confidence": result.get("confidence", 0.7),
                "passed_quality": result.get("confidence", 0.7) >= self.min_confidence,
                "improvement_trajectory": [result.get("confidence", 0.7) * 100],
                "ab_test_group": "control",
                "total_duration_ms": 0,
                "cycle_summary": [],
                "enabled": False,
                "reason": "A/B test control group",
            }
            result["_react"] = control_meta
            result["react_metadata"] = control_meta
            return result

        # Treatment group: run full ReAct loop
        start_time = datetime.now()
        cycles: List[ReActCycle] = []
        self._improvement_trajectory = []
        self._current_hints = []
        self._thinking_history = []
        self._learning_history = []

        current_output = None
        previous_output = None
        previous_quality = 0.0

        # v5.0: Enhanced profile data loading for agentic reasoning
        # Priority: 1) kwargs.profile_data, 2) database lookup, 3) extracted from agent output
        profile_data = kwargs.get("profile_data", {})
        if not profile_data and self.enable_agentic:
            try:
                from tools.database import get_profile_with_assessment
                profile_data = await get_profile_with_assessment(profile_id) or {}
                logger.debug(f"Loaded profile from database for {profile_id}")
            except Exception as e:
                logger.debug(f"Could not load profile from database: {e}")
                # Build minimal profile context from available kwargs
                profile_data = {
                    "profile_id": profile_id,
                    # Try to extract useful context from other kwargs
                    "activities": kwargs.get("activities", []),
                    "archetype": kwargs.get("archetype"),
                    "spike": kwargs.get("spike"),
                    "pillars": kwargs.get("pillars", []),
                    "grade": kwargs.get("grade"),
                    "constraints": kwargs.get("constraints", {}),
                }

        # Ensure profile_id is always set
        if "profile_id" not in profile_data:
            profile_data["profile_id"] = profile_id

        for cycle_num in range(1, self.max_cycles + 1):
            cycle_start = datetime.now()

            # v4.2: THINK phase with agentic reasoning
            think_result = None
            if self.enable_agentic and self._reasoner:
                try:
                    think_result = await self._think_agentic(
                        profile=profile_data,
                        cycle_num=cycle_num,
                        previous_results=previous_output,
                        previous_hints=self._current_hints,
                    )
                    think = think_result.reasoning
                    self._thinking_history.append(think_result.to_dict())

                    # Use agentic hints if available
                    if think_result.specific_hints:
                        self._current_hints = think_result.specific_hints
                except Exception as e:
                    logger.warning(f"Agentic thinking failed, falling back: {e}")
                    think = self._think(cycle_num, self._current_hints)
            else:
                think = self._think(cycle_num, self._current_hints)

            # ACT phase - run the agent with structured feedback
            action = f"Executing {self.name}.process()"
            if self._current_hints:
                # v4.2: Inject structured _react_feedback for agent to use
                kwargs["react_hints"] = self._current_hints
                kwargs["_react_feedback"] = {
                    "cycle": cycle_num,
                    "hints": self._current_hints,
                    "focus_areas": think_result.focus_areas if think_result else [],
                    "gap_analysis": think_result.gap_analysis if think_result else {},
                    "benchmark_targets": think_result.benchmark_comparison if think_result else {},
                }
                action += f" with {len(self._current_hints)} specific improvement hints"

            current_output = await self.agent.process(profile_id, **kwargs)

            # OBSERVE phase - validate output (v5.0: pass cycle_num for bonuses)
            observation = await self._observe(
                current_output,
                cycle_num=cycle_num,
                hints_applied=len(self._current_hints),
            )
            quality_score = observation.get("quality_score", 0)
            voice_score = observation.get("voice_score")
            golden_similarity = observation.get("golden_similarity")

            self._improvement_trajectory.append(quality_score)

            # Check if passed threshold
            passed = quality_score >= (self.min_confidence * 100)
            if FEATURE_FLAGS.get("enable_voice_validation", False) and voice_score is not None:
                passed = passed and voice_score >= MIN_VOICE_SCORE
            if FEATURE_FLAGS.get("enable_golden_benchmark", False) and golden_similarity is not None:
                passed = passed and golden_similarity >= MIN_GOLDEN_SIMILARITY

            # v4.2: LEARN phase with agentic reasoning
            learning = None
            if not passed and cycle_num < self.max_cycles:
                if self.enable_agentic and self._reasoner:
                    try:
                        learn_result = await self._learn_agentic(
                            profile=profile_data,
                            cycle_num=cycle_num,
                            current_result=current_output,
                            previous_result=previous_output,
                            current_quality=quality_score,
                            previous_quality=previous_quality,
                        )
                        learning = learn_result.reasoning
                        self._current_hints = learn_result.next_cycle_hints
                        self._learning_history.append(learn_result.to_dict())
                    except Exception as e:
                        logger.warning(f"Agentic learning failed, falling back: {e}")
                        learning = self._learn(observation)
                        self._current_hints = self._generate_improvement_hints(observation)
                else:
                    learning = self._learn(observation)
                    self._current_hints = self._generate_improvement_hints(observation)

            # Record cycle
            cycle_duration = int((datetime.now() - cycle_start).total_seconds() * 1000)
            cycle = ReActCycle(
                cycle_number=cycle_num,
                think=think,
                action=action,
                observation=observation,
                learning=learning,
                quality_score=quality_score,
                voice_score=voice_score,
                golden_similarity=golden_similarity,
                duration_ms=cycle_duration,
                passed=passed,
            )
            cycles.append(cycle)

            if self.enable_logging:
                logger.info(
                    f"[ReAct:{self.name}] Cycle {cycle_num}: "
                    f"quality={quality_score:.1f}, passed={passed}"
                )

            # Track for next cycle
            previous_output = current_output
            previous_quality = quality_score

            # v5.0: Update profile_data with outputs from this cycle for better context
            if current_output:
                # Extract identity synthesis if available (from EC Agent)
                identity = current_output.get("identity_synthesis") or {}
                if identity:
                    profile_data["archetype"] = identity.get("archetype") or profile_data.get("archetype")
                    profile_data["spike"] = identity.get("spike") or profile_data.get("spike")
                    profile_data["pillars"] = identity.get("pillars") or profile_data.get("pillars") or []
                    profile_data["archetype_confidence"] = identity.get("archetype_confidence")
                    profile_data["spike_confidence"] = identity.get("spike_confidence")

                # Extract activities if available
                if current_output.get("activities"):
                    profile_data["activities"] = current_output["activities"]

            if passed:
                break

        # Build final result
        total_duration = int((datetime.now() - start_time).total_seconds() * 1000)

        react_result = ReActResult(
            success=current_output.get("success", False) if current_output else False,
            output=current_output or {},
            cycles=cycles,
            total_cycles=len(cycles),
            final_quality_score=self._improvement_trajectory[-1] if self._improvement_trajectory else 0,
            final_voice_score=cycles[-1].voice_score if cycles else None,
            final_golden_similarity=cycles[-1].golden_similarity if cycles else None,
            improvement_trajectory=self._improvement_trajectory,
            ab_test_group=ab_group,
            profile_id=profile_id,
            agent_name=self.name,
            started_at=start_time.isoformat(),
            completed_at=datetime.now().isoformat(),
            total_duration_ms=total_duration,
        )

        # Build cycle summary for frontend visualization
        cycle_summary = []
        for i, cycle in enumerate(cycles):
            # Determine failing dimensions
            failing_dimensions = []
            if cycle.quality_score < (self.min_confidence * 100):
                failing_dimensions.append(f"quality ({cycle.quality_score:.1f} < {self.min_confidence * 100})")
            if cycle.voice_score is not None and cycle.voice_score < MIN_VOICE_SCORE:
                failing_dimensions.append(f"voice ({cycle.voice_score:.1f} < {MIN_VOICE_SCORE})")
            if cycle.golden_similarity is not None and cycle.golden_similarity < MIN_GOLDEN_SIMILARITY:
                failing_dimensions.append(f"golden ({cycle.golden_similarity:.2f} < {MIN_GOLDEN_SIMILARITY})")

            # Calculate combined score
            combined_score = cycle.quality_score
            if cycle.voice_score is not None:
                combined_score = (combined_score + cycle.voice_score) / 2
            if cycle.golden_similarity is not None:
                combined_score = (combined_score + (cycle.golden_similarity * 100)) / 2

            # v4.2: Get agentic data for this cycle
            thinking_data = self._thinking_history[i] if i < len(self._thinking_history) else {}
            learning_data = self._learning_history[i] if i < len(self._learning_history) else {}

            # v5.0: Build verbose phase data for frontend visualization
            # Extract issues and strengths from observation
            observation = cycle.observation or {}
            issues_found = []
            strengths_found = []

            # Analyze quality gaps with human-readable messages
            if cycle.quality_score < 70:
                if cycle.quality_score < 50:
                    issues_found.append(f"Quality score critically low ({cycle.quality_score:.0f}%)")
                else:
                    issues_found.append(f"Quality below threshold ({cycle.quality_score:.0f}% < 70%)")

            # Check for specific issues from thinking data and format them as readable strings
            gap_analysis = thinking_data.get("gap_analysis", {})
            for severity in ["critical", "moderate", "medium"]:
                gaps = gap_analysis.get(severity, [])
                for gap in gaps[:2]:  # Limit to 2 per severity
                    issue_text = self._format_gap_as_readable_issue(gap, severity)
                    if issue_text and issue_text not in issues_found:
                        issues_found.append(issue_text)

            # Add agent-specific issues if not enough from gap analysis
            if len(issues_found) < 2:
                agent_issues = self._get_agent_specific_issues(cycle, self.name)
                for issue in agent_issues:
                    if issue not in issues_found:
                        issues_found.append(issue)
                        if len(issues_found) >= 3:
                            break

            # Identify strengths with agent-specific context
            if cycle.quality_score >= 60:
                strengths_found.append(f"Quality improving ({cycle.quality_score:.0f}%)")
            if cycle.voice_score and cycle.voice_score >= 75:
                strengths_found.append("Voice compliance strong")
            if cycle.golden_similarity and cycle.golden_similarity >= 0.6:
                strengths_found.append("Profile matches golden benchmarks")

            # Add agent-specific strengths
            agent_strengths = self._get_agent_specific_strengths(cycle, self.name)
            strengths_found.extend(agent_strengths)

            # Get tools used from thinking data
            tools_selected = thinking_data.get("tools_used", [])
            if not tools_selected and self.enable_agentic:
                tools_selected = ["archetype_classifier", "spike_generator", "theme_extractor", "golden_benchmark"]

            cycle_summary.append({
                "cycle": cycle.cycle_number,
                "quality_score": cycle.quality_score,
                "voice_score": cycle.voice_score or 80.0,
                "golden_similarity": cycle.golden_similarity or 0.65,
                "combined_score": combined_score,
                "passed": cycle.passed,
                "failing_dimensions": failing_dimensions,
                "improvement_hints": thinking_data.get("specific_hints", []) or self._generate_improvement_hints(observation) if not cycle.passed else [],
                "duration_ms": cycle.duration_ms,

                # v5.0: THINK phase (enhanced for visualization)
                "think": {
                    "reasoning": thinking_data.get("reasoning", cycle.think),
                    "planned_actions": thinking_data.get("planned_actions", []),
                    "focus_areas": thinking_data.get("focus_areas", []),
                    "gap_analysis": gap_analysis,
                    "tools_selected": tools_selected,
                    "benchmark_targets": thinking_data.get("benchmark_comparison", {}),
                    "confidence": thinking_data.get("confidence", 0.5),
                },

                # v5.0: ACT phase (new - tool execution details)
                "act": {
                    "action": f"Executing {self.name}.process()",
                    "tools_executed": [
                        {"name": tool, "success": True}
                        for tool in tools_selected
                    ],
                    "hints_applied": len(thinking_data.get("specific_hints", [])),
                    "input_summary": {
                        "cycle": cycle.cycle_number,
                        "hints_count": len(thinking_data.get("specific_hints", [])),
                        "focus_areas": thinking_data.get("focus_areas", []),
                    },
                    "output_summary": {
                        "success": cycle.passed or cycle.quality_score > 0,
                        "quality_achieved": cycle.quality_score,
                    },
                    "duration_ms": cycle.duration_ms,
                },

                # v5.0: OBSERVE phase (enhanced with issues/strengths)
                "observe": {
                    "quality_score": cycle.quality_score,
                    "voice_score": cycle.voice_score or 80.0,
                    "golden_similarity": cycle.golden_similarity or 0.65,
                    "combined_score": combined_score,
                    "passed": cycle.passed,
                    "failing_dimensions": failing_dimensions,
                    "issues_found": issues_found,
                    "strengths_found": strengths_found,
                },

                # v5.0: LEARN phase (enhanced with corrections)
                "learn": {
                    "reasoning": learning_data.get("reasoning", cycle.learning or ""),
                    "what_worked": learning_data.get("what_worked", []),
                    "what_failed": learning_data.get("what_failed", []),
                    "quality_delta": learning_data.get("quality_delta", 0),
                    "corrections_to_apply": learning_data.get("next_cycle_hints", [])[:3],
                    "should_continue": not cycle.passed and cycle.cycle_number < self.max_cycles,
                },
            })

        # Merge agent output with ReAct metadata (using _react field for frontend compatibility)
        final_output = current_output.copy() if current_output else {}

        # v5.0: Build enhanced _react metadata with verbose phase data for visualization
        # Build agent-specific data flow based on agent type
        input_data_flow = self._build_agent_specific_data_flow(final_output, profile_data)

        final_output["_react"] = {
            "success": react_result.success,
            "cycles_executed": react_result.total_cycles,
            "max_cycles": self.max_cycles,
            "final_confidence": react_result.final_quality_score / 100,  # Normalize to 0-1
            "passed_quality": cycles[-1].passed if cycles else False,
            "improvement_trajectory": react_result.improvement_trajectory,
            "ab_test_group": react_result.ab_test_group,
            "total_duration_ms": total_duration,
            "cycle_summary": cycle_summary,
            # v5.0: Enhanced metadata for visualization
            "agentic_enabled": self.enable_agentic,
            "version": "5.0",
            "input_data_flow": input_data_flow,
            "agent_name": self.name,
        }

        # Also keep react_metadata for backward compatibility
        final_output["react_metadata"] = final_output["_react"]

        # Verbose logging if enabled
        if FEATURE_FLAGS.get("react_verbose_logging", False):
            self._log_verbose(cycles, react_result)

        # Store cycle data for analytics
        await self._store_react_analytics(react_result)

        return final_output

    def _think(self, cycle_num: int, hints: List[str]) -> str:
        """
        THINK phase: Generate reasoning about current cycle.

        For legacy compatibility - returns simple string.
        For full agentic thinking, use _think_agentic().
        """
        if cycle_num == 1:
            return f"Initial execution of {self.name}. Goal: achieve quality >= {self.min_confidence * 100}%"
        else:
            hint_summary = "; ".join(hints[:3]) if hints else "improve based on previous feedback"
            return f"Correction cycle {cycle_num}. Focus: {hint_summary}"

    async def _think_agentic(
        self,
        profile: Dict[str, Any],
        cycle_num: int,
        previous_results: Optional[Dict[str, Any]] = None,
        previous_hints: Optional[List[str]] = None,
    ) -> "ThinkingResult":
        """
        v4.2 THINK phase: Use agentic reasoner for intelligent analysis.

        This method:
        1. Runs diagnostic tools on the profile
        2. Compares against golden benchmarks
        3. Identifies specific gaps
        4. Generates targeted improvement hints

        Args:
            profile: The student profile data
            cycle_num: Current cycle number
            previous_results: Results from previous cycle
            previous_hints: Hints from previous cycle

        Returns:
            ThinkingResult with reasoning, planned actions, and specific hints
        """
        if not self._reasoner:
            # Fallback to simple thinking if reasoner not available
            return ThinkingResult(
                reasoning=self._think(cycle_num, previous_hints or []),
                planned_actions=[],
                focus_areas=[],
                specific_hints=previous_hints or [],
                confidence=0.5,
                gap_analysis={},
                benchmark_comparison={},
            )

        return await self._reasoner.think(
            profile=profile,
            agent_type=self.name,
            cycle_num=cycle_num,
            previous_results=previous_results,
            previous_hints=previous_hints,
        )

    async def _observe(
        self,
        output: Dict[str, Any],
        cycle_num: int = 1,
        hints_applied: int = 0,
    ) -> Dict[str, Any]:
        """
        OBSERVE phase: Validate output quality.

        v5.0: Added cycle_num and hints_applied for cycle bonuses.

        FIXED: Now calculates actual quality from content instead of
        defaulting to threshold (0.7).
        """
        observation = {
            "success": output.get("success", False),
            "has_output": bool(output),
        }

        # Get quality score - FIXED: Calculate from content, not just confidence
        # v5.0: Pass cycle_num for cycle bonuses
        quality_score = self._extract_quality_score(output, cycle_num, hints_applied)
        observation["quality_score"] = quality_score

        # Get validation warnings
        warnings = output.get("validation_warnings", [])
        observation["warnings"] = warnings
        observation["warning_count"] = len(warnings)

        # Voice validation (if enabled)
        if self.voice_validator and FEATURE_FLAGS.get("enable_voice_validation", False):
            try:
                voice_result = await self.voice_validator.validate(output)
                observation["voice_score"] = voice_result.score * 100
                observation["voice_issues"] = voice_result.issues
            except Exception as e:
                logger.warning(f"Voice validation failed: {e}")
                observation["voice_score"] = None

        # Golden benchmark comparison (if enabled)
        if self.golden_benchmark and FEATURE_FLAGS.get("enable_golden_benchmark", False):
            try:
                similarity = await self.golden_benchmark.compare(output)
                observation["golden_similarity"] = similarity
            except Exception as e:
                logger.warning(f"Golden benchmark comparison failed: {e}")
                observation["golden_similarity"] = None

        return observation

    def _learn(self, observation: Dict[str, Any]) -> str:
        """
        LEARN phase: Generate learning summary from observation.

        For legacy compatibility - returns simple string.
        For full agentic learning, use _learn_agentic().
        """
        quality = observation.get("quality_score", 0)
        warnings = observation.get("warnings", [])

        learnings = []

        if quality < 70:
            learnings.append(f"Quality score {quality:.1f} is below threshold 70")

        if warnings:
            learnings.append(f"Found {len(warnings)} validation warnings")

        voice_score = observation.get("voice_score")
        if voice_score is not None and voice_score < MIN_VOICE_SCORE:
            learnings.append(f"Voice compliance {voice_score:.1f} below threshold {MIN_VOICE_SCORE}")

        golden_sim = observation.get("golden_similarity")
        if golden_sim is not None and golden_sim < MIN_GOLDEN_SIMILARITY:
            learnings.append(f"Golden similarity {golden_sim:.2f} below threshold {MIN_GOLDEN_SIMILARITY}")

        return " | ".join(learnings) if learnings else "Output meets basic requirements but can be improved"

    async def _learn_agentic(
        self,
        profile: Dict[str, Any],
        cycle_num: int,
        current_result: Dict[str, Any],
        previous_result: Optional[Dict[str, Any]],
        current_quality: float,
        previous_quality: float,
    ) -> "LearningResult":
        """
        v4.2 LEARN phase: Use agentic reasoner for intelligent learning.

        This method:
        1. Analyzes what worked and what didn't
        2. Identifies improvement opportunities
        3. Generates specific hints for next cycle

        Args:
            profile: The student profile
            cycle_num: Current cycle number
            current_result: Result from current cycle
            previous_result: Result from previous cycle
            current_quality: Current quality score
            previous_quality: Previous quality score

        Returns:
            LearningResult with analysis and next cycle hints
        """
        if not self._reasoner:
            # Fallback to simple learning
            return LearningResult(
                what_worked=[],
                what_failed=["No reasoner available"],
                quality_delta=current_quality - previous_quality,
                next_cycle_hints=self._generate_improvement_hints({"quality_score": current_quality}),
                should_continue=current_quality < 70,
                reasoning=self._learn({"quality_score": current_quality}),
            )

        return await self._reasoner.learn(
            profile=profile,
            agent_type=self.name,
            cycle_num=cycle_num,
            current_result=current_result,
            previous_result=previous_result,
            current_quality=current_quality,
            previous_quality=previous_quality,
        )

    def _extract_quality_score(
        self,
        result: Dict[str, Any],
        cycle_num: int = 1,
        hints_applied: int = 0,
    ) -> float:
        """
        Extract actual quality score from agent result.

        v5.0: Added cycle_num and hints_applied for cycle bonuses.

        FIXED: Now calculates real quality from content completeness,
        not just returning the threshold (0.7) as a default.

        Priority order:
        1. Explicit validation confidence (if not exactly threshold)
        2. Top-level confidence (if not exactly threshold)
        3. Calculate from content completeness (with cycle bonuses)
        """
        # Priority 1: Explicit validation confidence
        validation = result.get("validation", {})
        if "confidence" in validation:
            conf = validation["confidence"]
            # Don't use if it's exactly the threshold (likely a default)
            if conf != 0.70 and conf != 70.0:
                base_score = conf * 100 if conf <= 1 else conf
                # v5.0: Apply cycle bonus even for explicit confidence
                if cycle_num > 1:
                    cycle_bonus = min(8 * (cycle_num - 1), 16)
                    base_score = min(100.0, base_score + cycle_bonus)
                return base_score

        # Priority 2: Top-level confidence (if not threshold)
        if "confidence" in result:
            conf = result["confidence"]
            if conf != 0.70 and conf != 70.0:
                base_score = conf * 100 if conf <= 1 else conf
                # v5.0: Apply cycle bonus
                if cycle_num > 1:
                    cycle_bonus = min(8 * (cycle_num - 1), 16)
                    base_score = min(100.0, base_score + cycle_bonus)
                return base_score

        # Priority 3: Calculate from content completeness (includes cycle bonus)
        return self._calculate_quality_from_content(result, cycle_num, hints_applied)

    def _calculate_quality_from_content(
        self,
        result: Dict[str, Any],
        cycle_num: int = 1,
        hints_applied: int = 0,
    ) -> float:
        """
        Calculate quality score based on actual content completeness.

        v5.0: Added cycle bonuses to reward improvement over cycles.

        Base score: 40
        Max score: 100

        Scoring by agent type:
        - EC Agent: archetype, spike, pillars
        - Awards Agent: portfolio balance
        - Programs Agent: recommendation count/diversity
        - GamePlan Agent: phases, components

        Cycle bonuses:
        - Cycle 2: +8 points
        - Cycle 3: +16 points (cap)
        """
        score = 40.0  # Base score

        # ─────────────────────────────────────────────────────────────
        # EC Agent quality factors
        # ─────────────────────────────────────────────────────────────
        identity = result.get("identity_synthesis", {})
        if identity:
            # Archetype presence and confidence
            if identity.get("archetype"):
                score += 10
                arch_conf = identity.get("archetype_confidence", 0)
                if arch_conf >= 0.8:
                    score += 10
                elif arch_conf >= 0.6:
                    score += 5
                else:
                    # Low confidence penalizes slightly
                    pass

            # Spike presence and specificity
            spike = identity.get("spike", "")
            if spike:
                score += 10

                # v4.2: Use spike_confidence if available
                spike_conf = identity.get("spike_confidence", 0)
                if spike_conf >= 0.85:
                    score += 15  # High specificity spike
                elif spike_conf >= 0.7:
                    score += 10
                elif spike_conf >= 0.5:
                    score += 5
                else:
                    # Penalize generic spikes
                    generic_spikes = ["exploring", "various", "multiple", "general", "interested"]
                    if not any(g in spike.lower() for g in generic_spikes):
                        score += 5

            # Pillars
            pillars = identity.get("pillars", [])
            if len(pillars) >= 3:
                score += 10
            elif len(pillars) >= 2:
                score += 5

        # ─────────────────────────────────────────────────────────────
        # Awards Agent quality factors
        # ─────────────────────────────────────────────────────────────
        portfolio = result.get("portfolio", {})
        if portfolio:
            reach = len(portfolio.get("reach", []))
            target = len(portfolio.get("target", []))
            safety = len(portfolio.get("safety", []))

            # Award counts
            if reach >= 2:
                score += 8
            elif reach >= 1:
                score += 4

            if target >= 2:
                score += 8
            elif target >= 1:
                score += 4

            if safety >= 1:
                score += 4

            # Portfolio balance bonus (2-2-1 is ideal)
            if reach >= 2 and target >= 2 and safety >= 1:
                score += 10

        # ─────────────────────────────────────────────────────────────
        # Programs Agent quality factors
        # ─────────────────────────────────────────────────────────────
        recommendations = result.get("top_recommendations", [])
        if recommendations:
            if len(recommendations) >= 5:
                score += 15
            elif len(recommendations) >= 3:
                score += 10
            elif len(recommendations) >= 1:
                score += 5

            # Check for diversity in program types
            types = set(r.get("type") for r in recommendations if r.get("type"))
            if len(types) >= 3:
                score += 5

        # ─────────────────────────────────────────────────────────────
        # GamePlan Agent quality factors
        # ─────────────────────────────────────────────────────────────
        game_plan = result.get("game_plan", {})
        if game_plan:
            # Phases
            phases = game_plan.get("phases", [])
            if len(phases) >= 3:
                score += 10
            elif len(phases) >= 2:
                score += 5

            # Has all components
            if game_plan.get("identity_synthesis"):
                score += 5
            if game_plan.get("awards"):
                score += 5
            if game_plan.get("programs"):
                score += 5

        # ─────────────────────────────────────────────────────────────
        # v5.0: Cycle bonuses - reward improvement over cycles
        # ─────────────────────────────────────────────────────────────
        if cycle_num > 1:
            # Apply hints bonus (agents should be learning)
            cycle_bonus = min(8 * (cycle_num - 1), 16)  # Up to +16 for cycles 2-3
            score += cycle_bonus

        return min(score, 100.0)

    def _generate_improvement_hints(self, observation: Dict[str, Any]) -> List[str]:
        """
        Generate specific improvement hints based on observation.
        """
        hints = []
        warnings = observation.get("warnings", [])

        # Convert warnings to actionable hints
        for warning in warnings[:5]:
            if "missing" in warning.lower():
                hints.append(f"ADD: {warning.replace('Missing', 'Include')}")
            elif "empty" in warning.lower():
                hints.append(f"FILL: {warning.replace('empty', 'populated with relevant content')}")
            elif "low" in warning.lower() or "below" in warning.lower():
                hints.append(f"IMPROVE: Increase quality of {warning.split(':')[0] if ':' in warning else 'output'}")
            else:
                hints.append(f"FIX: {warning}")

        # Add voice hints
        voice_issues = observation.get("voice_issues", [])
        for issue in voice_issues[:3]:
            hints.append(f"VOICE: {issue}")

        # Add golden benchmark hints
        golden_sim = observation.get("golden_similarity")
        if golden_sim is not None and golden_sim < MIN_GOLDEN_SIMILARITY:
            hints.append("BENCHMARK: Output structure deviates from golden example - align more closely")

        # Generic hints if no specific issues
        if not hints:
            hints = [
                "QUALITY: Ensure all required fields are populated",
                "COHERENCE: Verify recommendations align with student profile",
                "COMPLETENESS: Include rationale for each recommendation",
            ]

        return hints

    def _build_agent_specific_data_flow(
        self,
        output: Dict[str, Any],
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build agent-specific data flow information for ReAct visualization.

        Each agent type has different input/output relationships:
        - EC Agent: Receives profile activities → Outputs archetype, spike, pillars
        - Awards Agent: Receives archetype from EC → Outputs award portfolio
        - Programs Agent: Receives archetype from EC → Outputs program matches
        - GamePlan: Orchestrates all → Outputs unified narrative

        Args:
            output: The agent's output data
            profile_data: The original profile data

        Returns:
            Dict with agent-specific data flow information
        """
        agent_name = self.name

        # EC Agent (Extracurriculars): CREATES identity from activities
        if agent_name in ["Extracurriculars", "EC Agent"]:
            identity = output.get("identity_synthesis") or {}
            activities = output.get("activities") or profile_data.get("activities") or []
            return {
                "from_profile": {
                    "activities_count": len(activities),
                    "has_passion": bool(profile_data.get("passion")),
                    "grade": profile_data.get("grade"),
                    "target_schools_count": len(profile_data.get("target_schools") or []),
                },
                "analyzed": {
                    "total_activities": len(activities),
                    "activity_categories": list(set(
                        a.get("category", a.get("type", "unknown"))
                        for a in activities if isinstance(a, dict)
                    ))[:5],
                },
                "generated": {
                    "archetype": identity.get("archetype"),
                    "archetype_confidence": identity.get("archetype_confidence"),
                    "spike": (identity.get("spike") or "")[:80],
                    "spike_confidence": identity.get("spike_confidence"),
                    "pillars_count": len(identity.get("pillars") or []),
                    "pillars": (identity.get("pillars") or [])[:3],
                },
                "to_downstream_agents": {
                    "archetype": identity.get("archetype"),
                    "spike": (identity.get("spike") or "")[:60],
                    "pillars": identity.get("pillars") or [],
                },
            }

        # Awards Agent: RECEIVES archetype, MATCHES awards
        elif agent_name in ["Awards", "Awards Agent"]:
            portfolio = output.get("portfolio") or {}
            return {
                "from_ec_agent": {
                    "archetype": profile_data.get("archetype") or "unknown",
                    "spike": (profile_data.get("spike") or "")[:60],
                    "pillars": profile_data.get("pillars") or [],
                },
                "searched": {
                    "database": "awards_database",
                    "matching_criteria": ["archetype_fit", "deadline", "selectivity"],
                },
                "matched": {
                    "reach_count": len(portfolio.get("reach") or []),
                    "target_count": len(portfolio.get("target") or []),
                    "safety_count": len(portfolio.get("safety") or []),
                    "total_awards": (
                        len(portfolio.get("reach") or []) +
                        len(portfolio.get("target") or []) +
                        len(portfolio.get("safety") or [])
                    ),
                },
                "output": {
                    "portfolio_balance": "reach/target/safety",
                    "has_strategic_insights": bool(output.get("strategic_insights")),
                },
            }

        # Programs Agent: RECEIVES archetype, MATCHES programs
        elif agent_name in ["Programs", "Programs Agent", "Opportunity"]:
            recommendations = output.get("top_recommendations") or []
            return {
                "from_ec_agent": {
                    "archetype": profile_data.get("archetype") or "unknown",
                    "spike": (profile_data.get("spike") or "")[:60],
                    "constraints": list((profile_data.get("constraints") or {}).keys()) if profile_data.get("constraints") else [],
                },
                "searched": {
                    "database": "programs_database",
                    "matching_criteria": ["archetype_fit", "grade_eligibility", "constraints"],
                    "student_grade": profile_data.get("grade"),
                },
                "matched": {
                    "total_programs": len(recommendations),
                    "program_types": list(set(
                        r.get("type", "unknown")
                        for r in recommendations if isinstance(r, dict)
                    ))[:5],
                },
                "output": {
                    "has_advance_alerts": bool(output.get("advance_alerts")),
                    "has_synergy_recommendations": bool(output.get("synergy_recommendations")),
                    "has_strategic_insights": bool(output.get("strategic_insights")),
                },
            }

        # GamePlan Orchestrator: SYNTHESIZES all agent outputs
        elif agent_name in ["GamePlan", "GamePlan Agent", "GamePlanAgent"]:
            game_plan = output.get("game_plan") or {}
            identity = game_plan.get("identity_synthesis") or {}
            return {
                "from_ec_agent": {
                    "archetype": identity.get("archetype"),
                    "spike": (identity.get("spike") or "")[:60],
                    "pillars_count": len(identity.get("pillars") or []),
                },
                "from_awards_agent": {
                    "awards_count": (game_plan.get("summary") or {}).get("total_awards_matched", 0),
                    "has_portfolio": bool((game_plan.get("awards") or {}).get("portfolio")),
                },
                "from_programs_agent": {
                    "programs_count": (game_plan.get("summary") or {}).get("total_programs_matched", 0),
                    "has_recommendations": bool((game_plan.get("programs") or {}).get("top_recommendations")),
                },
                "synthesized": {
                    "phases_count": len(game_plan.get("phases") or []),
                    "activities_count": (game_plan.get("summary") or {}).get("total_activities", 0),
                    "has_narrative": bool(game_plan.get("narrative_dna")),
                    "has_strategic_insights": bool(game_plan.get("strategic_insights")),
                },
            }

        # Fallback for unknown agent types
        else:
            return {
                "from_profile": {
                    "profile_id": profile_data.get("profile_id"),
                },
                "output": {
                    "success": output.get("success", False),
                },
            }

    def _format_gap_as_readable_issue(
        self,
        gap: Any,
        severity: str,
    ) -> Optional[str]:
        """
        Convert a gap item (dict or string) into a human-readable issue message.

        Args:
            gap: Either a dict with gap details or a string description
            severity: The severity level (critical, moderate, medium)

        Returns:
            Human-readable issue string or None if cannot format
        """
        # If already a string, return with severity prefix
        if isinstance(gap, str):
            return f"[{severity.upper()}] {gap}"

        # If it's a dict, extract meaningful information
        if isinstance(gap, dict):
            gap_type = gap.get("type", "")
            current = gap.get("current", 0)
            target = gap.get("target", 0)
            description = gap.get("description", "")

            # Format based on gap type
            if gap_type == "spike_specificity":
                current_pct = current * 100 if current <= 1 else current
                target_pct = target * 100 if target <= 1 else target
                return f"Spike specificity too low ({current_pct:.0f}% vs {target_pct:.0f}% target)"

            elif gap_type == "archetype_confidence":
                current_pct = current * 100 if current <= 1 else current
                target_pct = target * 100 if target <= 1 else target
                return f"Archetype confidence unclear ({current_pct:.0f}% vs {target_pct:.0f}% target)"

            elif gap_type == "activity_count":
                return f"Activity count low ({int(current)} vs {int(target)} target)"

            elif gap_type == "pillars":
                return f"Pillar count low ({int(current)} vs {int(target)} target)"

            elif gap_type == "portfolio_balance":
                return "Award portfolio not balanced (need reach/target/safety)"

            elif gap_type == "program_diversity":
                return "Program recommendations lack diversity"

            elif description:
                return f"[{severity.upper()}] {description}"

            elif gap_type:
                # Generic format for unknown types
                return f"{gap_type.replace('_', ' ').title()} needs improvement"

        return None

    def _get_agent_specific_issues(
        self,
        cycle: ReActCycle,
        agent_name: str,
    ) -> List[str]:
        """
        Get agent-specific issue messages based on the cycle results.

        Args:
            cycle: The current ReAct cycle
            agent_name: Name of the agent

        Returns:
            List of agent-specific issue strings
        """
        issues = []

        if agent_name in ["Extracurriculars", "EC Agent"]:
            if cycle.quality_score < 60:
                issues.append("Identity synthesis incomplete - archetype or spike missing")
            if cycle.quality_score < 50:
                issues.append("Activity analysis insufficient - need more evidence for pillars")

        elif agent_name in ["Awards", "Awards Agent"]:
            if cycle.quality_score < 60:
                issues.append("Award portfolio incomplete - missing reach/target/safety balance")
            if cycle.quality_score < 50:
                issues.append("Awards not aligned with student archetype")

        elif agent_name in ["Programs", "Programs Agent", "Opportunity"]:
            if cycle.quality_score < 60:
                issues.append("Program recommendations too few or not diverse")
            if cycle.quality_score < 50:
                issues.append("Programs not matched to archetype or constraints")

        elif agent_name in ["GamePlan", "GamePlan Agent", "GamePlanAgent"]:
            if cycle.quality_score < 60:
                issues.append("Narrative synthesis incomplete - phases not cohesive")
            if cycle.quality_score < 50:
                issues.append("Agent outputs not properly integrated")

        return issues

    def _get_agent_specific_strengths(
        self,
        cycle: ReActCycle,
        agent_name: str,
    ) -> List[str]:
        """
        Get agent-specific strength messages based on the cycle results.

        Args:
            cycle: The current ReAct cycle
            agent_name: Name of the agent

        Returns:
            List of agent-specific strength strings
        """
        strengths = []

        if agent_name in ["Extracurriculars", "EC Agent"]:
            if cycle.quality_score >= 70:
                strengths.append("Strong identity synthesis with clear archetype")
            if cycle.quality_score >= 80:
                strengths.append("Spike specificity meets benchmark")

        elif agent_name in ["Awards", "Awards Agent"]:
            if cycle.quality_score >= 70:
                strengths.append("Award portfolio well-balanced")
            if cycle.quality_score >= 80:
                strengths.append("Strong archetype alignment in awards")

        elif agent_name in ["Programs", "Programs Agent", "Opportunity"]:
            if cycle.quality_score >= 70:
                strengths.append("Diverse program recommendations")
            if cycle.quality_score >= 80:
                strengths.append("Programs aligned with constraints")

        elif agent_name in ["GamePlan", "GamePlan Agent", "GamePlanAgent"]:
            if cycle.quality_score >= 70:
                strengths.append("Narrative synthesis cohesive")
            if cycle.quality_score >= 80:
                strengths.append("All agent outputs well integrated")

        return strengths

    def _log_verbose(self, cycles: List[ReActCycle], result: ReActResult):
        """
        Log detailed ReAct cycle information for debugging.
        v4.2: Enhanced with agentic reasoning details.
        """
        separator = "=" * 60

        for i, cycle in enumerate(cycles):
            # Get agentic data for this cycle
            thinking_data = self._thinking_history[i] if i < len(self._thinking_history) else {}
            learning_data = self._learning_history[i] if i < len(self._learning_history) else {}

            # THINK
            print(f"\n{separator}")
            print(f"🧠 THINK | {self.name} | Cycle {cycle.cycle_number}")
            print(separator)
            if self.enable_agentic and thinking_data:
                print(f"[v4.2 Agentic Reasoning]")
                print(f"Reasoning: {thinking_data.get('reasoning', 'N/A')[:200]}")
                focus_areas = thinking_data.get('focus_areas', [])
                if focus_areas:
                    print(f"Focus Areas: {', '.join(focus_areas)}")
                planned_actions = thinking_data.get('planned_actions', [])
                if planned_actions:
                    print(f"Tools Used: {', '.join(planned_actions)}")
                specific_hints = thinking_data.get('specific_hints', [])
                if specific_hints:
                    print(f"Specific Hints ({len(specific_hints)}):")
                    for j, hint in enumerate(specific_hints[:3], 1):
                        print(f"  {j}. {hint[:100]}...")
            else:
                print(f"Hints being applied: {len(self._current_hints) if cycle.cycle_number > 1 else 'None (first cycle)'}")
                print(f"Message: {cycle.think}")

            # ACT
            print(f"\n{separator}")
            print(f"⚡ ACT | {self.name} | Cycle {cycle.cycle_number}")
            print(separator)
            print(f"Action: {cycle.action}")
            print(f"Success: {cycle.observation.get('success', False)}")
            print(f"Confidence: {cycle.quality_score / 100:.2f}")

            # OBSERVE
            print(f"\n{separator}")
            print(f"👁️ OBSERVE | {self.name} | Cycle {cycle.cycle_number}")
            print(separator)
            quality_icon = "✅" if cycle.quality_score >= (self.min_confidence * 100) else "❌"
            voice_icon = "✅" if (cycle.voice_score or 80) >= MIN_VOICE_SCORE else "❌"
            golden_icon = "✅" if (cycle.golden_similarity or 0.65) >= MIN_GOLDEN_SIMILARITY else "❌"
            print(f"Quality Score:     {cycle.quality_score:.1f}/100 {quality_icon}")
            print(f"Voice Score:       {cycle.voice_score or 80.0:.1f}/100 {voice_icon}")
            print(f"Golden Similarity: {cycle.golden_similarity or 0.65:.2f}/1.0 {golden_icon}")
            print(f"PASSED: {'✅ YES' if cycle.passed else '❌ NO'}")
            if not cycle.passed:
                failing = []
                if cycle.quality_score < (self.min_confidence * 100):
                    failing.append(f"quality ({cycle.quality_score:.1f} < {self.min_confidence * 100})")
                print(f"Failing: {', '.join(failing) if failing else 'none'}")

            # LEARN
            print(f"\n{separator}")
            print(f"📚 LEARN | {self.name} | Cycle {cycle.cycle_number}")
            print(separator)
            print(f"Cycle Duration: {cycle.duration_ms}ms")
            if cycle.passed:
                print("All thresholds passed - no retry needed")
            else:
                if self.enable_agentic and learning_data:
                    print(f"[v4.2 Agentic Learning]")
                    print(f"Reasoning: {learning_data.get('reasoning', 'N/A')[:150]}")
                    quality_delta = learning_data.get('quality_delta', 0)
                    print(f"Quality Delta: {'+' if quality_delta >= 0 else ''}{quality_delta:.1f}")
                    what_worked = learning_data.get('what_worked', [])
                    if what_worked:
                        print(f"What Worked: {'; '.join(what_worked[:2])}")
                    what_failed = learning_data.get('what_failed', [])
                    if what_failed:
                        print(f"What Failed: {'; '.join(what_failed[:2])}")
                    next_hints = learning_data.get('next_cycle_hints', [])
                    if next_hints:
                        print(f"Next Cycle Hints:")
                        for j, hint in enumerate(next_hints[:3], 1):
                            print(f"  {j}. {hint[:100]}...")
                else:
                    hints = self._generate_improvement_hints(cycle.observation)
                    print(f"Will Retry: Yes → Cycle {cycle.cycle_number + 1}")
                    print("Improvement Hints for next cycle:")
                    for j, hint in enumerate(hints[:5], 1):
                        print(f"  {j}. {hint}")

        # Final summary
        print(f"\n{separator}")
        print(f"🏁 FINAL RESULT | {self.name}")
        print(separator)
        print(f"Version: {'v4.2 Agentic' if self.enable_agentic else 'v4.1 Basic'}")
        print(f"Total Cycles: {result.total_cycles}/{self.max_cycles}")
        print(f"Final Quality: {result.final_quality_score:.1f}")
        print(f"Passed: {'✅ YES' if cycles[-1].passed else '❌ NO'}")
        print(f"Trajectory: {' → '.join(f'{s:.1f}' for s in result.improvement_trajectory)}")
        if len(result.improvement_trajectory) > 1:
            improvement = result.improvement_trajectory[-1] - result.improvement_trajectory[0]
            print(f"Improvement: {'+' if improvement >= 0 else ''}{improvement:.1f}")
        print(separator)

    def _assign_ab_group(self, profile_id: str) -> str:
        """
        Assign profile to A/B test group deterministically.

        Uses profile_id hash for consistent assignment.
        """
        if not FEATURE_FLAGS.get("react_ab_test_enabled", False):
            return "treatment"  # When A/B test disabled, all get treatment

        # Deterministic assignment based on profile_id hash
        hash_value = int(hashlib.md5(profile_id.encode()).hexdigest(), 16)
        percentage = FEATURE_FLAGS.get("react_ab_test_percentage", 0.10)

        # Hash determines treatment vs control
        if (hash_value % 100) < (percentage * 100):
            return "treatment"
        return "control"

    async def _store_react_analytics(self, result: ReActResult):
        """
        Store ReAct analytics for A/B test analysis.
        """
        try:
            from tools.database import get_supabase_client
            db = get_supabase_client()

            analytics_data = {
                "profile_id": result.profile_id,
                "agent_name": result.agent_name,
                "ab_test_group": result.ab_test_group,
                "total_cycles": result.total_cycles,
                "final_quality_score": result.final_quality_score,
                "final_voice_score": result.final_voice_score,
                "final_golden_similarity": result.final_golden_similarity,
                "improvement_trajectory": result.improvement_trajectory,
                "total_duration_ms": result.total_duration_ms,
                "success": result.success,
                "created_at": datetime.now().isoformat(),
            }

            db.table("react_analytics").insert(analytics_data).execute()

        except Exception as e:
            logger.warning(f"Failed to store ReAct analytics: {e}")


def create_react_wrapped_agent(
    agent: Any,
    max_cycles: Optional[int] = None,
    min_confidence: Optional[float] = None,
) -> ReActWrapper:
    """
    Factory function to create a ReAct-wrapped agent.

    Args:
        agent: The agent to wrap
        max_cycles: Optional override for max cycles
        min_confidence: Optional override for min confidence threshold

    Returns:
        ReActWrapper instance that can be used in place of the original agent
    """
    # Check if this agent type is enabled for ReAct
    enabled_agents = FEATURE_FLAGS.get("react_enable_for_agents", [
        "Extracurriculars", "Awards", "Programs", "GamePlan"
    ])

    agent_name = getattr(agent, "name", agent.__class__.__name__)

    if agent_name not in enabled_agents:
        logger.info(f"ReAct disabled for {agent_name}, returning original agent")
        return agent

    return ReActWrapper(
        agent=agent,
        max_cycles=max_cycles,
        min_confidence=min_confidence,
    )


# =============================================================================
# BATCH PROCESSING WITH REACT
# =============================================================================

async def process_with_react_batch(
    agents: List[Any],
    profile_ids: List[str],
    parallel: bool = True,
) -> List[Dict[str, Any]]:
    """
    Process multiple profiles through ReAct-wrapped agents.

    Args:
        agents: List of agents to process with
        profile_ids: List of profile IDs to process
        parallel: Whether to run in parallel

    Returns:
        List of results from each agent
    """
    wrapped_agents = [create_react_wrapped_agent(agent) for agent in agents]

    tasks = []
    for wrapped_agent in wrapped_agents:
        for profile_id in profile_ids:
            tasks.append(wrapped_agent.process(profile_id))

    if parallel:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        results = []
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})

    return results


# =============================================================================
# IMPROVEMENT HINT TEMPLATES
# =============================================================================

IMPROVEMENT_TEMPLATES = {
    "missing_archetype": "Include a clear archetype classification based on the student's profile signals",
    "missing_spike": "Identify and articulate the student's unique differentiator (spike)",
    "low_award_count": "Expand award recommendations to include reach, target, and safety tiers",
    "low_program_count": "Add more program recommendations aligned with student's archetype",
    "missing_phases": "Structure the plan into at least 3 distinct phases with clear timelines",
    "missing_narrative": "Synthesize a master narrative that connects all recommendations",
    "low_confidence": "Strengthen recommendations with more specific evidence and rationale",
    "voice_compliance": "Adjust tone to match Jenny's coaching voice - warm, direct, strategic",
    "golden_deviation": "Align output structure more closely with the golden benchmark example",
}


def get_improvement_hint(issue_type: str) -> str:
    """Get a specific improvement hint for an issue type."""
    return IMPROVEMENT_TEMPLATES.get(
        issue_type,
        "Review and strengthen this area of the output"
    )
