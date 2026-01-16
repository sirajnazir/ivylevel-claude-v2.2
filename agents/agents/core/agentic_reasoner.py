"""
Agentic Reasoner - LLM-based THINK Phase for True ReAct Framework
=================================================================

This module provides intelligent, LLM-powered reasoning for the THINK phase
of the ReAct loop. Instead of generic hints like "Ensure all fields populated",
the reasoner analyzes the actual profile and generates specific, actionable
insights and guidance.

The reasoner:
1. Analyzes the current profile state
2. Identifies specific gaps and opportunities
3. Generates targeted improvement hints
4. Tracks reasoning across cycles for iterative improvement

Usage:
    from agents.core.agentic_reasoner import AgenticReasoner

    reasoner = AgenticReasoner()
    thinking = await reasoner.think(
        profile=profile_data,
        agent_type="Extracurriculars",
        cycle_num=1,
        previous_results=None,
    )
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging
import json

from agents.core.agentic_tools import ToolRegistry, ToolResult, get_tool_registry
from agents.core.golden_examples_db import get_golden_examples_db, GoldenExamplesDB

logger = logging.getLogger(__name__)


@dataclass
class ThinkingResult:
    """Result from the THINK phase."""
    reasoning: str  # Full reasoning text
    planned_actions: List[str]  # Tools to use
    focus_areas: List[str]  # What to focus on
    specific_hints: List[str]  # Specific, actionable hints
    confidence: float  # Confidence in the plan
    gap_analysis: Dict[str, Any]  # Identified gaps
    benchmark_comparison: Dict[str, Any]  # How profile compares to golden

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reasoning": self.reasoning,
            "planned_actions": self.planned_actions,
            "focus_areas": self.focus_areas,
            "specific_hints": self.specific_hints,
            "confidence": self.confidence,
            "gap_analysis": self.gap_analysis,
            "benchmark_comparison": self.benchmark_comparison,
        }


@dataclass
class LearningResult:
    """Result from the LEARN phase."""
    what_worked: List[str]
    what_failed: List[str]
    quality_delta: float  # Change in quality score
    next_cycle_hints: List[str]  # Specific hints for next cycle
    should_continue: bool  # Whether to continue cycling
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "what_worked": self.what_worked,
            "what_failed": self.what_failed,
            "quality_delta": self.quality_delta,
            "next_cycle_hints": self.next_cycle_hints,
            "should_continue": self.should_continue,
            "reasoning": self.reasoning,
        }


class AgenticReasoner:
    """
    LLM-powered reasoner for the THINK phase of ReAct.

    Provides intelligent analysis of profiles and generates
    specific, actionable guidance for each agent type.
    """

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        golden_db: Optional[GoldenExamplesDB] = None,
    ):
        """
        Initialize the reasoner.

        Args:
            tool_registry: Registry of agentic tools
            golden_db: Database of golden examples
        """
        self.tool_registry = tool_registry or get_tool_registry()
        self.golden_db = golden_db or get_golden_examples_db()
        self._cycle_history: List[Dict[str, Any]] = []

    async def think(
        self,
        profile: Dict[str, Any],
        agent_type: str,
        cycle_num: int,
        previous_results: Optional[Dict[str, Any]] = None,
        previous_hints: Optional[List[str]] = None,
    ) -> ThinkingResult:
        """
        Execute the THINK phase - analyze profile and plan approach.

        Args:
            profile: The student profile
            agent_type: Type of agent (Extracurriculars, Awards, etc.)
            cycle_num: Current cycle number (1-based)
            previous_results: Results from previous cycle if any
            previous_hints: Hints from previous cycle if any

        Returns:
            ThinkingResult with reasoning and planned actions
        """
        # Step 1: Run diagnostic tools to understand the profile
        tool_results = await self._run_diagnostic_tools(profile, agent_type)

        # Step 2: Compare against golden benchmarks
        benchmark_comparison = self._compare_to_benchmark(profile, tool_results)

        # Step 3: Identify specific gaps
        gap_analysis = self._analyze_gaps(profile, tool_results, benchmark_comparison)

        # Step 4: Generate specific hints based on agent type and gaps
        specific_hints = self._generate_specific_hints(
            agent_type=agent_type,
            gap_analysis=gap_analysis,
            tool_results=tool_results,
            cycle_num=cycle_num,
            previous_hints=previous_hints,
        )

        # Step 5: Plan which tools/actions to take
        planned_actions = self._select_tools(agent_type, gap_analysis)

        # Step 6: Build reasoning narrative
        reasoning = self._build_reasoning_narrative(
            profile=profile,
            agent_type=agent_type,
            cycle_num=cycle_num,
            tool_results=tool_results,
            gap_analysis=gap_analysis,
            specific_hints=specific_hints,
            previous_results=previous_results,
        )

        # Step 7: Identify focus areas
        focus_areas = self._identify_focus_areas(gap_analysis, agent_type)

        # Calculate confidence
        confidence = self._calculate_confidence(tool_results, gap_analysis)

        return ThinkingResult(
            reasoning=reasoning,
            planned_actions=planned_actions,
            focus_areas=focus_areas,
            specific_hints=specific_hints,
            confidence=confidence,
            gap_analysis=gap_analysis,
            benchmark_comparison=benchmark_comparison,
        )

    async def learn(
        self,
        profile: Dict[str, Any],
        agent_type: str,
        cycle_num: int,
        current_result: Dict[str, Any],
        previous_result: Optional[Dict[str, Any]] = None,
        current_quality: float = 0.0,
        previous_quality: float = 0.0,
    ) -> LearningResult:
        """
        Execute the LEARN phase - analyze what worked and what didn't.

        Args:
            profile: The student profile
            agent_type: Type of agent
            cycle_num: Current cycle number
            current_result: Result from current cycle
            previous_result: Result from previous cycle
            current_quality: Current quality score
            previous_quality: Previous quality score

        Returns:
            LearningResult with analysis and next cycle hints
        """
        quality_delta = current_quality - previous_quality

        # Analyze what changed between cycles
        what_worked = []
        what_failed = []

        if quality_delta > 0:
            what_worked.append(f"Quality improved by {quality_delta:.1f} points")
            # Identify what improved
            improvements = self._identify_improvements(current_result, previous_result)
            what_worked.extend(improvements)
        elif quality_delta < 0:
            what_failed.append(f"Quality decreased by {abs(quality_delta):.1f} points")
        else:
            what_failed.append("No quality improvement - hints may not be applied correctly")

        # Check specific elements
        identity = current_result.get("identity_synthesis", {})
        if identity:
            # Check spike
            spike = identity.get("spike", "")
            spike_conf = identity.get("spike_confidence", 0)
            if spike_conf >= 0.85:
                what_worked.append(f"Spike specificity achieved ({spike_conf:.0%})")
            elif spike_conf < 0.70:
                what_failed.append(f"Spike too generic ({spike_conf:.0%})")

            # Check archetype
            arch_conf = identity.get("archetype_confidence", 0)
            if arch_conf >= 0.80:
                what_worked.append(f"Archetype confidence strong ({arch_conf:.0%})")
            elif arch_conf < 0.65:
                what_failed.append(f"Archetype unclear ({arch_conf:.0%})")

        # Determine if should continue
        should_continue = current_quality < 70 and cycle_num < 3

        # Generate next cycle hints based on what failed
        next_cycle_hints = self._generate_next_cycle_hints(
            what_failed=what_failed,
            agent_type=agent_type,
            current_result=current_result,
            current_quality=current_quality,
        )

        # Build reasoning
        reasoning = self._build_learning_reasoning(
            quality_delta=quality_delta,
            what_worked=what_worked,
            what_failed=what_failed,
            should_continue=should_continue,
            cycle_num=cycle_num,
        )

        return LearningResult(
            what_worked=what_worked,
            what_failed=what_failed,
            quality_delta=quality_delta,
            next_cycle_hints=next_cycle_hints,
            should_continue=should_continue,
            reasoning=reasoning,
        )

    # =========================================================================
    # PRIVATE METHODS - Tool Execution
    # =========================================================================

    async def _run_diagnostic_tools(
        self,
        profile: Dict[str, Any],
        agent_type: str,
    ) -> Dict[str, ToolResult]:
        """Run diagnostic tools to understand the profile."""
        results = {}

        # Select tools based on agent type
        tools_to_run = self.tool_registry.select_tools(agent_type, profile)

        for tool_name in tools_to_run:
            try:
                result = await self.tool_registry.execute(tool_name, profile)
                results[tool_name] = result
                logger.debug(f"Tool {tool_name} executed: {result.success}")
            except Exception as e:
                logger.warning(f"Tool {tool_name} failed: {e}")
                results[tool_name] = ToolResult(
                    tool_name=tool_name,
                    success=False,
                    error=str(e),
                )

        return results

    def _compare_to_benchmark(
        self,
        profile: Dict[str, Any],
        tool_results: Dict[str, ToolResult],
    ) -> Dict[str, Any]:
        """Compare profile to golden benchmarks."""
        # Get archetype from tool results or profile
        archetype = profile.get("archetype", "stem_innovator")
        if "archetype_classifier" in tool_results:
            arch_result = tool_results["archetype_classifier"]
            if arch_result.success:
                archetype = arch_result.data.get("archetype", archetype)

        # Build profile data for comparison
        profile_for_comparison = {
            "archetype": archetype,
            "activities": profile.get("activities", []),
            "pillars": profile.get("pillars", []),
            "spike_specificity": 0.5,  # Default
            "archetype_confidence": 0.5,  # Default
        }

        # Update from tool results
        if "spike_generator" in tool_results:
            spike_result = tool_results["spike_generator"]
            if spike_result.success:
                profile_for_comparison["spike_specificity"] = spike_result.data.get(
                    "spike_specificity", 0.5
                )

        if "archetype_classifier" in tool_results:
            arch_result = tool_results["archetype_classifier"]
            if arch_result.success:
                profile_for_comparison["archetype_confidence"] = arch_result.data.get(
                    "archetype_confidence", 0.5
                )

        if "theme_extractor" in tool_results:
            theme_result = tool_results["theme_extractor"]
            if theme_result.success:
                profile_for_comparison["pillars"] = [
                    p.get("name", "") for p in theme_result.data.get("pillars", [])
                ]

        # Compare to benchmark
        return self.golden_db.compare_to_benchmark(profile_for_comparison, archetype)

    def _analyze_gaps(
        self,
        profile: Dict[str, Any],
        tool_results: Dict[str, ToolResult],
        benchmark_comparison: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze specific gaps in the profile."""
        gaps = {
            "critical": [],  # Gaps that must be fixed
            "moderate": [],  # Important but not critical
            "minor": [],  # Nice to have
        }

        # Get gaps from benchmark comparison
        benchmark_gaps = benchmark_comparison.get("gaps", {})

        for metric, gap_data in benchmark_gaps.items():
            if not gap_data.get("meets_target", False):
                gap_value = gap_data.get("gap", 0)
                current = gap_data.get("current", 0)
                target = gap_data.get("target", 0)

                # Categorize by severity
                if gap_value > 0.2 or not gap_data.get("meets_min", False):
                    gaps["critical"].append({
                        "type": metric,
                        "current": current,
                        "target": target,
                        "gap": gap_value,
                    })
                elif gap_value > 0.1:
                    gaps["moderate"].append({
                        "type": metric,
                        "current": current,
                        "target": target,
                        "gap": gap_value,
                    })
                else:
                    gaps["minor"].append({
                        "type": metric,
                        "current": current,
                        "target": target,
                        "gap": gap_value,
                    })

        # Add tool-specific gaps
        for tool_name, result in tool_results.items():
            if result.success and result.suggestions:
                for suggestion in result.suggestions[:2]:
                    gaps["moderate"].append({
                        "type": f"{tool_name}_suggestion",
                        "description": suggestion,
                    })

        return gaps

    # =========================================================================
    # PRIVATE METHODS - Hint Generation
    # =========================================================================

    def _generate_specific_hints(
        self,
        agent_type: str,
        gap_analysis: Dict[str, Any],
        tool_results: Dict[str, ToolResult],
        cycle_num: int,
        previous_hints: Optional[List[str]] = None,
    ) -> List[str]:
        """Generate specific, actionable hints based on gaps and agent type."""
        hints = []
        previous_hints = previous_hints or []

        # Process critical gaps first
        for gap in gap_analysis.get("critical", []):
            hint = self._gap_to_hint(gap, agent_type, cycle_num)
            if hint and hint not in previous_hints:
                hints.append(hint)

        # Then moderate gaps
        for gap in gap_analysis.get("moderate", []):
            hint = self._gap_to_hint(gap, agent_type, cycle_num)
            if hint and hint not in previous_hints:
                hints.append(hint)

        # Add tool-specific hints
        for tool_name, result in tool_results.items():
            if result.success:
                for suggestion in result.suggestions[:2]:
                    if suggestion not in previous_hints and suggestion not in hints:
                        hints.append(suggestion)

        # Add agent-specific hints if no gaps found
        if not hints:
            hints = self._get_agent_specific_hints(agent_type, tool_results)

        # Limit to top 5 most important hints
        return hints[:5]

    def _gap_to_hint(
        self,
        gap: Dict[str, Any],
        agent_type: str,
        cycle_num: int,
    ) -> Optional[str]:
        """Convert a gap to a specific, actionable hint."""
        gap_type = gap.get("type", "")
        current = gap.get("current", 0)
        target = gap.get("target", 0)
        description = gap.get("description", "")

        # Handle benchmark metric gaps
        if gap_type == "spike_specificity":
            if current < 0.7:
                return (
                    f"CRITICAL: Spike specificity is {current:.0%} (target: {target:.0%}). "
                    "Make the spike more specific by specifying: "
                    "(1) WHO you serve, (2) WHAT exactly you do, (3) WHERE/WHEN."
                )
            else:
                return (
                    f"Spike specificity is {current:.0%} (target: {target:.0%}). "
                    "Add concrete details to narrow focus."
                )

        elif gap_type == "archetype_confidence":
            if current < 0.65:
                return (
                    f"CRITICAL: Archetype confidence is {current:.0%}. "
                    "Profile appears scattered. Focus activities on ONE dominant theme. "
                    "Consider removing activities that don't align with primary archetype."
                )
            else:
                return (
                    f"Archetype confidence is {current:.0%} (target: {target:.0%}). "
                    "Strengthen alignment by deepening top 2-3 activities."
                )

        elif gap_type == "activity_count":
            gap_amount = int(target - current)
            return (
                f"Activity count is {int(current)} (target: {int(target)}). "
                f"Add {gap_amount} more activities aligned with spike and archetype."
            )

        elif gap_type == "pillars":
            return (
                f"Profile has {int(current)} pillars (target: {int(target)}). "
                "Develop activities in a complementary area that supports your spike."
            )

        # Handle tool suggestion gaps
        elif gap_type.endswith("_suggestion"):
            return description

        return None

    def _get_agent_specific_hints(
        self,
        agent_type: str,
        tool_results: Dict[str, ToolResult],
    ) -> List[str]:
        """Get agent-specific hints when no gaps are found."""
        hints = {
            "Extracurriculars": [
                "Ensure spike is specific to a domain, population, and approach",
                "Verify archetype classification matches activity portfolio",
                "Check that pillars represent distinct but complementary areas",
            ],
            "Awards": [
                "Ensure award recommendations follow 2-2-1 portfolio balance (reach/target/safety)",
                "Verify each award aligns with student archetype",
                "Include win cascade path from entry to capstone awards",
            ],
            "Programs": [
                "Match programs to student's spike and archetype",
                "Balance prestigious programs with accessible options",
                "Consider timeline and application requirements",
            ],
            "GamePlan": [
                "Ensure master narrative connects all recommendations",
                "Verify phases have clear milestones and timelines",
                "Check that awards and programs align with identity synthesis",
            ],
        }

        return hints.get(agent_type, ["Improve output quality and completeness"])

    def _generate_next_cycle_hints(
        self,
        what_failed: List[str],
        agent_type: str,
        current_result: Dict[str, Any],
        current_quality: float,
    ) -> List[str]:
        """Generate hints for the next cycle based on what failed."""
        hints = []

        for failure in what_failed:
            failure_lower = failure.lower()

            if "spike" in failure_lower and "generic" in failure_lower:
                # Get example spike from golden DB
                archetype = current_result.get("identity_synthesis", {}).get(
                    "archetype", "stem_innovator"
                )
                example_spikes = self.golden_db.get_example_spikes(archetype, limit=1)
                if example_spikes:
                    hints.append(
                        f"SPIKE TOO GENERIC: Replace with specific focus. "
                        f"Example: '{example_spikes[0]}'"
                    )
                else:
                    hints.append(
                        "SPIKE TOO GENERIC: Narrow to specific domain + population + approach"
                    )

            elif "archetype" in failure_lower and "unclear" in failure_lower:
                hints.append(
                    "ARCHETYPE UNCLEAR: Activities don't form coherent narrative. "
                    "Reduce breadth, increase depth in primary area."
                )

            elif "no quality improvement" in failure_lower:
                hints.append(
                    "HINTS NOT APPLIED: Previous hints did not improve quality. "
                    "Ensure agent reads and applies _react_feedback hints."
                )

            elif "quality decreased" in failure_lower:
                hints.append(
                    "QUALITY REGRESSION: Review changes from previous cycle. "
                    "Restore what was working, modify only what needed improvement."
                )

        # Add quality-based hints
        if current_quality < 50:
            hints.append(
                "CRITICAL QUALITY ISSUE: Score below 50%. "
                "Focus on completing required fields and basic structure."
            )
        elif current_quality < 70:
            hints.append(
                f"Quality is {current_quality:.0f}% (target: 70%). "
                "Address top 2-3 gaps to reach threshold."
            )

        return hints[:5]

    # =========================================================================
    # PRIVATE METHODS - Reasoning and Planning
    # =========================================================================

    def _select_tools(
        self,
        agent_type: str,
        gap_analysis: Dict[str, Any],
    ) -> List[str]:
        """Select tools to run based on agent type and gaps."""
        base_tools = {
            "Extracurriculars": ["archetype_classifier", "spike_generator", "theme_extractor"],
            "Awards": ["archetype_classifier", "golden_benchmark"],
            "Programs": ["archetype_classifier", "golden_benchmark"],
            "GamePlan": ["archetype_classifier", "spike_generator", "golden_benchmark"],
        }

        tools = base_tools.get(agent_type, ["archetype_classifier"])

        # Add golden_benchmark if we have critical gaps
        critical_gaps = gap_analysis.get("critical", [])
        if critical_gaps and "golden_benchmark" not in tools:
            tools.append("golden_benchmark")

        return tools

    def _identify_focus_areas(
        self,
        gap_analysis: Dict[str, Any],
        agent_type: str,
    ) -> List[str]:
        """Identify the main focus areas for this cycle."""
        focus_areas = []

        # Add critical gaps as focus areas
        for gap in gap_analysis.get("critical", []):
            focus_areas.append(gap.get("type", "unknown").replace("_", " ").title())

        # Add moderate gaps
        for gap in gap_analysis.get("moderate", [])[:2]:
            area = gap.get("type", "").replace("_", " ").title()
            if area and area not in focus_areas:
                focus_areas.append(area)

        # Default focus areas by agent type
        if not focus_areas:
            defaults = {
                "Extracurriculars": ["Spike Specificity", "Archetype Clarity", "Pillar Definition"],
                "Awards": ["Portfolio Balance", "Archetype Fit", "Win Cascade"],
                "Programs": ["Archetype Alignment", "Strategic Fit", "Timeline"],
                "GamePlan": ["Narrative Coherence", "Phase Structure", "Recommendation Integration"],
            }
            focus_areas = defaults.get(agent_type, ["Output Quality"])[:3]

        return focus_areas[:3]

    def _build_reasoning_narrative(
        self,
        profile: Dict[str, Any],
        agent_type: str,
        cycle_num: int,
        tool_results: Dict[str, ToolResult],
        gap_analysis: Dict[str, Any],
        specific_hints: List[str],
        previous_results: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a narrative reasoning explanation."""
        activities = profile.get("activities", [])
        activity_count = len(activities)

        # Start reasoning
        reasoning_parts = []

        # Cycle context
        if cycle_num == 1:
            reasoning_parts.append(
                f"Initial execution of {agent_type} agent. "
                f"Profile has {activity_count} activities."
            )
        else:
            reasoning_parts.append(
                f"Correction cycle {cycle_num} for {agent_type} agent. "
                f"Applying {len(specific_hints)} improvement hints."
            )

        # Tool insights
        for tool_name, result in tool_results.items():
            if result.success:
                if tool_name == "archetype_classifier":
                    arch = result.data.get("archetype", "unknown")
                    conf = result.data.get("archetype_confidence", 0)
                    reasoning_parts.append(
                        f"Archetype classified as {arch} ({conf:.0%} confidence)."
                    )
                elif tool_name == "spike_generator":
                    spike = result.data.get("spike", "")
                    spec = result.data.get("spike_specificity", 0)
                    if spike:
                        reasoning_parts.append(
                            f"Generated spike: '{spike[:80]}...' ({spec:.0%} specificity)."
                        )
                elif tool_name == "theme_extractor":
                    pillars = result.data.get("pillars", [])
                    if pillars:
                        pillar_names = [p.get("name", "") for p in pillars[:3]]
                        reasoning_parts.append(
                            f"Identified pillars: {', '.join(pillar_names)}."
                        )

        # Gap summary
        critical_count = len(gap_analysis.get("critical", []))
        moderate_count = len(gap_analysis.get("moderate", []))
        if critical_count > 0:
            reasoning_parts.append(
                f"Found {critical_count} critical gaps that must be addressed."
            )
        if moderate_count > 0:
            reasoning_parts.append(
                f"Found {moderate_count} moderate gaps for improvement."
            )

        # Action plan
        if specific_hints:
            reasoning_parts.append(
                f"Plan: Address {len(specific_hints)} specific issues."
            )

        return " ".join(reasoning_parts)

    def _build_learning_reasoning(
        self,
        quality_delta: float,
        what_worked: List[str],
        what_failed: List[str],
        should_continue: bool,
        cycle_num: int,
    ) -> str:
        """Build reasoning for the LEARN phase."""
        parts = []

        # Quality change
        if quality_delta > 0:
            parts.append(f"Cycle {cycle_num} improved quality by {quality_delta:.1f} points.")
        elif quality_delta < 0:
            parts.append(f"Cycle {cycle_num} decreased quality by {abs(quality_delta):.1f} points.")
        else:
            parts.append(f"Cycle {cycle_num} showed no quality change.")

        # What worked
        if what_worked:
            parts.append(f"Successes: {'; '.join(what_worked[:2])}.")

        # What failed
        if what_failed:
            parts.append(f"Issues: {'; '.join(what_failed[:2])}.")

        # Next steps
        if should_continue:
            parts.append(f"Will continue to cycle {cycle_num + 1}.")
        else:
            parts.append("No further cycles needed or maximum reached.")

        return " ".join(parts)

    def _identify_improvements(
        self,
        current_result: Dict[str, Any],
        previous_result: Optional[Dict[str, Any]],
    ) -> List[str]:
        """Identify what improved between cycles."""
        improvements = []

        if not previous_result:
            return improvements

        # Compare identity synthesis
        current_identity = current_result.get("identity_synthesis", {})
        previous_identity = previous_result.get("identity_synthesis", {})

        # Spike improvement
        current_spike_conf = current_identity.get("spike_confidence", 0)
        previous_spike_conf = previous_identity.get("spike_confidence", 0)
        if current_spike_conf > previous_spike_conf:
            improvements.append(
                f"Spike confidence improved: {previous_spike_conf:.0%} → {current_spike_conf:.0%}"
            )

        # Archetype improvement
        current_arch_conf = current_identity.get("archetype_confidence", 0)
        previous_arch_conf = previous_identity.get("archetype_confidence", 0)
        if current_arch_conf > previous_arch_conf:
            improvements.append(
                f"Archetype confidence improved: {previous_arch_conf:.0%} → {current_arch_conf:.0%}"
            )

        return improvements

    def _calculate_confidence(
        self,
        tool_results: Dict[str, ToolResult],
        gap_analysis: Dict[str, Any],
    ) -> float:
        """Calculate confidence in the reasoning."""
        # Base confidence from tool success
        successful_tools = sum(1 for r in tool_results.values() if r.success)
        total_tools = len(tool_results)
        tool_confidence = successful_tools / total_tools if total_tools else 0.5

        # Reduce confidence for critical gaps
        critical_gaps = len(gap_analysis.get("critical", []))
        gap_penalty = min(critical_gaps * 0.1, 0.3)

        return max(0.3, min(1.0, tool_confidence - gap_penalty))


# =============================================================================
# MODULE EXPORTS
# =============================================================================

# Singleton instance
_reasoner: Optional[AgenticReasoner] = None


def get_agentic_reasoner() -> AgenticReasoner:
    """Get the singleton agentic reasoner."""
    global _reasoner
    if _reasoner is None:
        _reasoner = AgenticReasoner()
    return _reasoner
