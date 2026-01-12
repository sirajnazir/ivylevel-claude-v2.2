# agents/agents/core/thresholds.py
"""
IvyQuest v13.2 - Quality Thresholds and Autonomy Levels

This module defines the global quality thresholds used by all ReAct agents
to determine pass/fail criteria and self-correction requirements.
"""

from enum import Enum


class QualityThresholds:
    """
    Global quality thresholds for all ReAct agents.
    
    These thresholds determine:
    - When an agent's output passes without correction
    - When self-correction is triggered
    - How the combined score is calculated
    
    CRITICAL: Do not modify these values without architecture review.
    """

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

    @classmethod
    def compute_combined(cls, quality: float, voice: float, golden: float) -> float:
        """
        Compute weighted combined score.
        
        Args:
            quality: Quality score 0-100
            voice: Voice score 0-100
            golden: Golden similarity 0-1
            
        Returns:
            Combined score 0-100
        """
        return (
            quality * cls.WEIGHT_QUALITY +
            voice * cls.WEIGHT_VOICE +
            (golden * 100) * cls.WEIGHT_GOLDEN
        )

    @classmethod
    def passes_all(cls, quality: float, voice: float, golden: float) -> bool:
        """
        Check if all thresholds are met.
        
        Args:
            quality: Quality score 0-100
            voice: Voice score 0-100
            golden: Golden similarity 0-1
            
        Returns:
            True if all thresholds are met
        """
        return (
            quality >= cls.MIN_QUALITY_SCORE and
            voice >= cls.MIN_VOICE_SCORE and
            golden >= cls.MIN_GOLDEN_SIMILARITY
        )

    @classmethod
    def get_failing_dimensions(
        cls, 
        quality: float, 
        voice: float, 
        golden: float
    ) -> list[str]:
        """
        Get list of dimensions that are failing thresholds.
        
        Returns:
            List of failing dimension names
        """
        failures = []
        if quality < cls.MIN_QUALITY_SCORE:
            failures.append(f"quality ({quality:.1f} < {cls.MIN_QUALITY_SCORE})")
        if voice < cls.MIN_VOICE_SCORE:
            failures.append(f"voice ({voice:.1f} < {cls.MIN_VOICE_SCORE})")
        if golden < cls.MIN_GOLDEN_SIMILARITY:
            failures.append(f"golden ({golden:.2f} < {cls.MIN_GOLDEN_SIMILARITY})")
        return failures


class AutonomyLevel(str, Enum):
    """
    Agent autonomy levels determining HITL requirements.
    
    FULL: No human review required (deterministic calculations)
    HIGH: Auto-approve if confidence > 70%
    MEDIUM: Optional human review, required if confidence < 85%
    LOW: Always requires human review
    """

    FULL = "full"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def requires_hitl(cls, level: "AutonomyLevel", confidence: float) -> bool:
        """
        Determine if HITL is required based on level and confidence.
        
        Args:
            level: The agent's autonomy level
            confidence: Agent's confidence in output (0-1)
            
        Returns:
            True if human-in-the-loop review is required
        """
        if level == cls.FULL:
            return False
        if level == cls.HIGH:
            return confidence < 0.70
        if level == cls.MEDIUM:
            return confidence < 0.85
        return True  # LOW always requires HITL

    @classmethod
    def get_description(cls, level: "AutonomyLevel") -> str:
        """Get human-readable description of autonomy level."""
        descriptions = {
            cls.FULL: "Fully autonomous - no human review",
            cls.HIGH: "High autonomy - HITL if confidence < 70%",
            cls.MEDIUM: "Medium autonomy - HITL if confidence < 85%",
            cls.LOW: "Low autonomy - always requires HITL",
        }
        return descriptions.get(level, "Unknown autonomy level")
