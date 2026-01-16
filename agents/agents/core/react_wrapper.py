"""
ReAct Wrapper - Self-Correction Framework for IvyQuest Agents
=============================================================
v4.1 Implementation

ReAct (Reasoning + Acting) framework that wraps existing agents to provide
self-correction capabilities without modifying their internal structure.

Flow:
1. THINK: Analyze task and plan approach
2. ACT: Execute agent's process method
3. OBSERVE: Validate output using guardrails
4. LEARN: Generate improvement hints if below threshold
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
        """
        self.agent = agent
        self.name = getattr(agent, "name", agent.__class__.__name__)
        self.max_cycles = max_cycles or FEATURE_FLAGS.get("react_max_cycles", MAX_REACT_CYCLES)
        self.min_confidence = min_confidence or FEATURE_FLAGS.get("react_min_confidence", MIN_QUALITY_SCORE / 100)
        self.voice_validator = voice_validator
        self.golden_benchmark = golden_benchmark
        self.enable_logging = enable_logging

        # State
        self._current_hints: List[str] = []
        self._improvement_trajectory: List[float] = []

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
            result["react_metadata"] = {
                "enabled": False,
                "ab_test_group": "control",
                "reason": "A/B test control group",
            }
            return result

        # Treatment group: run full ReAct loop
        start_time = datetime.now()
        cycles: List[ReActCycle] = []
        self._improvement_trajectory = []
        self._current_hints = []

        current_output = None

        for cycle_num in range(1, self.max_cycles + 1):
            cycle_start = datetime.now()

            # THINK phase
            think = self._think(cycle_num, self._current_hints)

            # ACT phase - run the agent
            action = f"Executing {self.name}.process()"
            if self._current_hints:
                # Inject hints into kwargs for agent to use
                kwargs["react_hints"] = self._current_hints
                action += f" with {len(self._current_hints)} improvement hints"

            current_output = await self.agent.process(profile_id, **kwargs)

            # OBSERVE phase - validate output
            observation = await self._observe(current_output)
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

            # LEARN phase - generate hints if not passed
            learning = None
            if not passed and cycle_num < self.max_cycles:
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

        # Merge agent output with ReAct metadata
        final_output = current_output.copy() if current_output else {}
        final_output["react_metadata"] = {
            "enabled": True,
            "total_cycles": react_result.total_cycles,
            "final_quality_score": react_result.final_quality_score,
            "improvement_trajectory": react_result.improvement_trajectory,
            "ab_test_group": react_result.ab_test_group,
            "passed": cycles[-1].passed if cycles else False,
            "total_duration_ms": total_duration,
        }

        # Store cycle data for analytics
        await self._store_react_analytics(react_result)

        return final_output

    def _think(self, cycle_num: int, hints: List[str]) -> str:
        """
        THINK phase: Generate reasoning about current cycle.
        """
        if cycle_num == 1:
            return f"Initial execution of {self.name}. Goal: achieve quality >= {self.min_confidence * 100}%"
        else:
            hint_summary = "; ".join(hints[:3]) if hints else "improve based on previous feedback"
            return f"Correction cycle {cycle_num}. Focus: {hint_summary}"

    async def _observe(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        OBSERVE phase: Validate output quality.
        """
        observation = {
            "success": output.get("success", False),
            "has_output": bool(output),
        }

        # Get quality score from guardrails validation
        confidence = output.get("confidence", 0.7)
        observation["quality_score"] = confidence * 100

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
