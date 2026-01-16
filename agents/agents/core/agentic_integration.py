"""
Agentic Integration Module v5.0
================================

This module provides factory functions, batch processing, and validation
utilities for integrating agentic ReAct components into IvyQuest agents.

Key Features:
- Factory functions for creating agentic-wrapped agents
- Batch processing for multiple profiles
- Validation functions for quality assurance
- Configuration management for agentic settings

Usage:
    from agents.core.agentic_integration import (
        create_agentic_ec_agent,
        create_agentic_orchestrator,
        process_profiles_batch,
    )

    # Create an agentic EC agent
    ec_agent = create_agentic_ec_agent()
    result = await ec_agent.process(profile_id)

    # Batch process multiple profiles
    results = await process_profiles_batch(profile_ids, agent_type="ec")
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

from config import FEATURE_FLAGS

logger = logging.getLogger(__name__)

# Type variable for generic agent
T = TypeVar("T")


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class AgenticConfig:
    """Configuration for agentic processing."""

    # ReAct settings
    max_cycles: int = 3
    min_confidence: float = 0.70
    enable_agentic: bool = True

    # Quality thresholds
    quality_threshold: int = 70
    voice_threshold: int = 70
    golden_similarity_threshold: float = 0.60

    # Cycle bonuses (v5.0)
    cycle_bonus_per_cycle: int = 8
    max_cycle_bonus: int = 16

    # Confidence boosts (v5.0)
    archetype_hint_boost: float = 0.15
    general_correction_boost: float = 0.08
    spike_correction_boost: float = 0.10

    # Feature flags
    enable_verbose_logging: bool = True
    enable_ab_testing: bool = False
    ab_test_percentage: float = 0.10

    @classmethod
    def from_feature_flags(cls) -> "AgenticConfig":
        """Create config from feature flags."""
        return cls(
            max_cycles=FEATURE_FLAGS.get("react_max_cycles", 3),
            min_confidence=FEATURE_FLAGS.get("react_min_confidence", 0.70),
            enable_agentic=FEATURE_FLAGS.get("enable_agentic", True),
            enable_verbose_logging=FEATURE_FLAGS.get("react_verbose_logging", True),
            enable_ab_testing=FEATURE_FLAGS.get("react_ab_test_enabled", False),
            ab_test_percentage=FEATURE_FLAGS.get("react_ab_test_percentage", 0.10),
        )


# Global config instance
_config: Optional[AgenticConfig] = None


def get_agentic_config() -> AgenticConfig:
    """Get the global agentic configuration."""
    global _config
    if _config is None:
        _config = AgenticConfig.from_feature_flags()
    return _config


def set_agentic_config(config: AgenticConfig):
    """Set the global agentic configuration."""
    global _config
    _config = config


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_agentic_ec_agent(config: Optional[AgenticConfig] = None):
    """
    Create an agentic-wrapped Extracurriculars agent.

    Args:
        config: Optional configuration override

    Returns:
        ReAct-wrapped EC agent with agentic capabilities
    """
    from agents.extracurriculars import ExtracurricularsAgent
    from agents.core.react_wrapper import ReActWrapper

    config = config or get_agentic_config()

    agent = ExtracurricularsAgent()
    return ReActWrapper(
        agent=agent,
        max_cycles=config.max_cycles,
        min_confidence=config.min_confidence,
        enable_agentic=config.enable_agentic,
        enable_logging=config.enable_verbose_logging,
    )


def create_agentic_awards_agent(config: Optional[AgenticConfig] = None):
    """
    Create an agentic-wrapped Awards agent.

    Args:
        config: Optional configuration override

    Returns:
        ReAct-wrapped Awards agent with agentic capabilities
    """
    try:
        from agents.awards import AwardsAgent
        from agents.core.react_wrapper import ReActWrapper

        config = config or get_agentic_config()

        agent = AwardsAgent()
        return ReActWrapper(
            agent=agent,
            max_cycles=config.max_cycles,
            min_confidence=config.min_confidence,
            enable_agentic=config.enable_agentic,
            enable_logging=config.enable_verbose_logging,
        )
    except ImportError:
        logger.warning("Awards agent not available")
        return None


def create_agentic_programs_agent(config: Optional[AgenticConfig] = None):
    """
    Create an agentic-wrapped Programs agent.

    Args:
        config: Optional configuration override

    Returns:
        ReAct-wrapped Programs agent with agentic capabilities
    """
    try:
        from agents.programs import ProgramsAgent
        from agents.core.react_wrapper import ReActWrapper

        config = config or get_agentic_config()

        agent = ProgramsAgent()
        return ReActWrapper(
            agent=agent,
            max_cycles=config.max_cycles,
            min_confidence=config.min_confidence,
            enable_agentic=config.enable_agentic,
            enable_logging=config.enable_verbose_logging,
        )
    except ImportError:
        logger.warning("Programs agent not available")
        return None


def create_agentic_orchestrator(config: Optional[AgenticConfig] = None):
    """
    Create an agentic orchestrator that coordinates all agents.

    The orchestrator runs:
    1. EC Agent first (to establish identity)
    2. Awards and Programs agents in parallel
    3. Synthesizes into a coherent game plan

    Args:
        config: Optional configuration override

    Returns:
        Orchestrator function for processing profiles
    """
    config = config or get_agentic_config()

    async def orchestrate(profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Orchestrate all agents for a profile.

        Args:
            profile_id: Profile to process
            **kwargs: Additional arguments

        Returns:
            Complete game plan with all components
        """
        start_time = datetime.now()

        # Step 1: Run EC Agent (identity synthesis first)
        ec_agent = create_agentic_ec_agent(config)
        ec_result = await ec_agent.process(profile_id, **kwargs)

        if not ec_result.get("success"):
            return {
                "success": False,
                "error": "EC Agent failed",
                "ec_result": ec_result,
            }

        # Extract identity for downstream agents
        identity_synthesis = ec_result.get("identity_synthesis", {})

        # Step 2: Run Awards and Programs in parallel
        awards_agent = create_agentic_awards_agent(config)
        programs_agent = create_agentic_programs_agent(config)

        tasks = []
        if awards_agent:
            tasks.append(
                awards_agent.process(
                    profile_id,
                    identity_synthesis=identity_synthesis,
                    **kwargs,
                )
            )
        if programs_agent:
            tasks.append(
                programs_agent.process(
                    profile_id,
                    identity_synthesis=identity_synthesis,
                    **kwargs,
                )
            )

        parallel_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Extract results
        awards_result = None
        programs_result = None

        for result in parallel_results:
            if isinstance(result, Exception):
                logger.error(f"Parallel agent failed: {result}")
                continue
            if "portfolio" in result or "awards" in result:
                awards_result = result
            elif "programs" in result or "recommendations" in result:
                programs_result = result

        # Step 3: Synthesize into game plan
        total_duration = int((datetime.now() - start_time).total_seconds() * 1000)

        return {
            "success": True,
            "profile_id": profile_id,
            "identity_synthesis": identity_synthesis,
            "awards": awards_result,
            "programs": programs_result,
            "orchestration": {
                "total_duration_ms": total_duration,
                "ec_completed": ec_result.get("success", False),
                "awards_completed": awards_result is not None,
                "programs_completed": programs_result is not None,
                "version": "v5.0 Agentic",
            },
        }

    return orchestrate


# =============================================================================
# BATCH PROCESSING
# =============================================================================

async def process_profiles_batch(
    profile_ids: List[str],
    agent_type: str = "ec",
    parallel: bool = True,
    config: Optional[AgenticConfig] = None,
) -> List[Dict[str, Any]]:
    """
    Process multiple profiles through agentic agents.

    Args:
        profile_ids: List of profile IDs to process
        agent_type: Type of agent ("ec", "awards", "programs", "orchestrator")
        parallel: Whether to process in parallel
        config: Optional configuration override

    Returns:
        List of results from each profile
    """
    config = config or get_agentic_config()

    # Select agent factory
    factory_map = {
        "ec": create_agentic_ec_agent,
        "awards": create_agentic_awards_agent,
        "programs": create_agentic_programs_agent,
        "orchestrator": create_agentic_orchestrator,
    }

    factory = factory_map.get(agent_type, create_agentic_ec_agent)

    # Create agent/orchestrator
    agent_or_func = factory(config)

    if agent_or_func is None:
        return [{"success": False, "error": f"Agent type {agent_type} not available"}]

    # Process profiles
    if callable(agent_or_func) and not hasattr(agent_or_func, "process"):
        # It's an orchestrator function
        process_func = agent_or_func
    else:
        # It's an agent with .process()
        process_func = agent_or_func.process

    if parallel:
        tasks = [process_func(pid) for pid in profile_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error dicts
        return [
            r if not isinstance(r, Exception) else {"success": False, "error": str(r)}
            for r in results
        ]
    else:
        results = []
        for pid in profile_ids:
            try:
                result = await process_func(pid)
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})
        return results


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

@dataclass
class ValidationResult:
    """Result from validating an agent output."""
    is_valid: bool
    quality_score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


def validate_ec_output(result: Dict[str, Any]) -> ValidationResult:
    """
    Validate EC agent output.

    Args:
        result: EC agent result

    Returns:
        ValidationResult with quality assessment
    """
    issues = []
    recommendations = []
    quality_score = 50.0

    identity = result.get("identity_synthesis", {})

    # Check archetype
    if not identity.get("archetype"):
        issues.append("Missing archetype classification")
    else:
        quality_score += 15

    # Check archetype confidence
    confidence = identity.get("archetype_confidence", 0)
    if confidence < 0.7:
        issues.append(f"Low archetype confidence ({confidence:.0%})")
        recommendations.append("Add more activities aligned with primary archetype")
    else:
        quality_score += 10

    # Check spike
    spike = identity.get("spike", "")
    if not spike:
        issues.append("Missing spike")
    elif "exploring" in spike.lower() or "various" in spike.lower():
        issues.append("Spike is too generic")
        recommendations.append("Narrow spike to specific domain + population + approach")
    else:
        quality_score += 15

    # Check spike confidence
    spike_conf = identity.get("spike_confidence", 0)
    if spike_conf >= 0.85:
        quality_score += 10

    # Check pillars
    pillars = identity.get("pillars", [])
    if len(pillars) < 3:
        issues.append(f"Only {len(pillars)} pillars (target: 3)")
        recommendations.append("Develop activities in complementary areas")
    else:
        quality_score += 10

    is_valid = quality_score >= 70 and len(issues) == 0

    return ValidationResult(
        is_valid=is_valid,
        quality_score=min(100, quality_score),
        issues=issues,
        recommendations=recommendations,
    )


def validate_awards_output(result: Dict[str, Any]) -> ValidationResult:
    """
    Validate Awards agent output.

    Args:
        result: Awards agent result

    Returns:
        ValidationResult with quality assessment
    """
    issues = []
    recommendations = []
    quality_score = 50.0

    portfolio = result.get("portfolio", {})

    # Check portfolio balance (2-2-1 target)
    reach = len(portfolio.get("reach", []))
    target = len(portfolio.get("target", []))
    safety = len(portfolio.get("safety", []))

    if reach < 2:
        issues.append(f"Only {reach} reach awards (target: 2)")
    else:
        quality_score += 15

    if target < 2:
        issues.append(f"Only {target} target awards (target: 2)")
    else:
        quality_score += 15

    if safety < 1:
        issues.append("No safety awards")
    else:
        quality_score += 10

    # Check total
    total = reach + target + safety
    if total >= 5:
        quality_score += 10

    is_valid = quality_score >= 70

    return ValidationResult(
        is_valid=is_valid,
        quality_score=min(100, quality_score),
        issues=issues,
        recommendations=recommendations,
    )


def validate_programs_output(result: Dict[str, Any]) -> ValidationResult:
    """
    Validate Programs agent output.

    Args:
        result: Programs agent result

    Returns:
        ValidationResult with quality assessment
    """
    issues = []
    recommendations = []
    quality_score = 50.0

    programs = result.get("programs", result.get("top_recommendations", []))

    # Check program count
    if len(programs) < 3:
        issues.append(f"Only {len(programs)} programs (target: 5)")
    elif len(programs) >= 5:
        quality_score += 20
    else:
        quality_score += 10

    # Check diversity
    types = set(p.get("type", "") for p in programs)
    if len(types) >= 3:
        quality_score += 15
    elif len(types) >= 2:
        quality_score += 10

    # Check constraint respect
    if result.get("constraints_respected", True):
        quality_score += 15

    is_valid = quality_score >= 70

    return ValidationResult(
        is_valid=is_valid,
        quality_score=min(100, quality_score),
        issues=issues,
        recommendations=recommendations,
    )


# =============================================================================
# UTILITIES
# =============================================================================

def get_agentic_status() -> Dict[str, Any]:
    """
    Get current status of agentic components.

    Returns:
        Status dict with component availability and config
    """
    config = get_agentic_config()

    # Check component availability
    components = {}

    try:
        from agents.core.agentic_reasoner import get_agentic_reasoner
        components["reasoner"] = True
    except ImportError:
        components["reasoner"] = False

    try:
        from agents.core.agentic_tools import get_tool_registry
        registry = get_tool_registry()
        components["tools"] = {
            "available": True,
            "tool_count": len(registry.list_tools()),
        }
    except ImportError:
        components["tools"] = {"available": False}

    try:
        from agents.core.golden_examples_db import get_golden_examples_db
        components["golden_db"] = True
    except ImportError:
        components["golden_db"] = False

    return {
        "version": "v5.0",
        "enabled": config.enable_agentic,
        "config": {
            "max_cycles": config.max_cycles,
            "min_confidence": config.min_confidence,
            "cycle_bonus": config.cycle_bonus_per_cycle,
        },
        "components": components,
    }


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "AgenticConfig",
    "get_agentic_config",
    "set_agentic_config",
    "create_agentic_ec_agent",
    "create_agentic_awards_agent",
    "create_agentic_programs_agent",
    "create_agentic_orchestrator",
    "process_profiles_batch",
    "validate_ec_output",
    "validate_awards_output",
    "validate_programs_output",
    "ValidationResult",
    "get_agentic_status",
]
