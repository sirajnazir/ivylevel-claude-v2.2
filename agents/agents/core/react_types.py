# agents/agents/core/react_types.py
"""
IvyQuest v13.2 - Structured Types for ReAct Framework

This module defines all the dataclasses used by the ReAct agent framework:
- ThoughtProcess: Structured output from Think phase
- ActionResult: Result from Action phase
- Observation: Multi-dimensional evaluation from Observe phase
- Learning: Insights extracted from a cycle
- ReActCycle: Complete record of one ReAct iteration
"""

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
    """
    Structured thought from Think phase.
    
    Contains the agent's reasoning, planned action, confidence level,
    and alternative approaches considered.
    """
    thought: str
    reasoning: str
    planned_action: str
    confidence: float
    context_factors: List[str]
    alternative_approaches: List[str] = field(default_factory=list)
    memory_recalls: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/API response."""
        return {
            "thought": self.thought,
            "reasoning": self.reasoning,
            "planned_action": self.planned_action,
            "confidence": self.confidence,
            "context_factors": self.context_factors,
            "alternatives": self.alternative_approaches,
            "memory_recalls": self.memory_recalls,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ActionResult:
    """
    Result from Action phase.
    
    Contains the action executed, tool used (if any), input/output data,
    and success status.
    """
    action_name: str
    tool_used: Optional[str]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/API response."""
        return {
            "action_name": self.action_name,
            "tool_used": self.tool_used,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "success": self.success,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Observation:
    """
    Multi-dimensional observation from Observe phase.
    
    Evaluates the action result across three dimensions:
    - quality_score: Domain-specific content quality (0-100)
    - voice_score: Jenny voice compliance (0-100)  
    - golden_similarity: Similarity to golden examples (0-1)
    
    Also tracks issues found, strengths, and correction suggestions.
    """
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
        """Weighted combined score using QualityThresholds weights."""
        from .thresholds import QualityThresholds
        return QualityThresholds.compute_combined(
            self.quality_score, self.voice_score, self.golden_similarity
        )

    @property
    def passes_thresholds(self) -> bool:
        """Check if all thresholds are met."""
        from .thresholds import QualityThresholds
        return QualityThresholds.passes_all(
            self.quality_score, self.voice_score, self.golden_similarity
        )

    @property
    def failing_dimensions(self) -> List[str]:
        """Get list of dimensions failing thresholds."""
        from .thresholds import QualityThresholds
        return QualityThresholds.get_failing_dimensions(
            self.quality_score, self.voice_score, self.golden_similarity
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/API response."""
        return {
            "quality_score": self.quality_score,
            "voice_score": self.voice_score,
            "golden_similarity": self.golden_similarity,
            "combined_score": self.combined_score,
            "passes_thresholds": self.passes_thresholds,
            "failing_dimensions": self.failing_dimensions,
            "issues_found": self.issues_found,
            "strengths": self.strengths,
            "needs_correction": self.needs_correction,
            "correction_suggestions": self.correction_suggestions,
            "dimension_scores": self.dimension_scores,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Learning:
    """
    Insights extracted from a ReAct cycle.
    
    Used to inform the next cycle's reasoning and for long-term
    pattern learning.
    """
    successful_patterns: List[str] = field(default_factory=list)
    failed_patterns: List[str] = field(default_factory=list)
    adjustments_made: List[str] = field(default_factory=list)
    confidence_delta: float = 0.0
    should_try_alternative: bool = False
    alternative_to_try: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/API response."""
        return {
            "successful_patterns": self.successful_patterns,
            "failed_patterns": self.failed_patterns,
            "adjustments_made": self.adjustments_made,
            "confidence_delta": self.confidence_delta,
            "should_try_alternative": self.should_try_alternative,
            "alternative_to_try": self.alternative_to_try,
        }


@dataclass
class ReActCycle:
    """
    Complete record of one ReAct iteration.
    
    Contains all four phases (Think, Act, Observe, Learn) plus
    timing information. Used for audit trails and debugging.
    """
    cycle_number: int
    thought: ThoughtProcess
    action: ActionResult
    observation: Observation
    learning: Learning
    total_duration_ms: float
    phase: ReasoningPhase = ReasoningPhase.EVALUATION

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize for storage/API response.
        
        Returns a complete representation of the cycle suitable
        for inclusion in react_trace.
        """
        return {
            "cycle_number": self.cycle_number,
            "thought": self.thought.to_dict(),
            "action": self.action.to_dict(),
            "observation": self.observation.to_dict(),
            "learning": self.learning.to_dict(),
            "total_duration_ms": self.total_duration_ms,
            "phase": self.phase.value,
        }

    @property
    def passed(self) -> bool:
        """Check if this cycle passed all thresholds."""
        return self.observation.passes_thresholds

    @property
    def summary(self) -> str:
        """Get a brief summary of the cycle."""
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return (
            f"Cycle {self.cycle_number} [{status}]: "
            f"Q={self.observation.quality_score:.0f}, "
            f"V={self.observation.voice_score:.0f}, "
            f"G={self.observation.golden_similarity:.2f}, "
            f"Combined={self.observation.combined_score:.1f}"
        )


@dataclass
class RunContext:
    """
    Context passed through the ReAct loop.
    
    Contains profile information, session tracking, and injected
    learnings from previous cycles.
    """
    profile_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    archetype: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Injected learnings from previous cycles (set by _inject_learnings)
    _previous_learnings: Optional[Dict[str, Any]] = field(default=None, repr=False)

    def with_learnings(self, learnings: Dict[str, Any]) -> "RunContext":
        """
        Create new context with injected learnings.
        
        This is called between ReAct cycles to pass learning
        information to the next cycle's _think() method.
        
        Args:
            learnings: Dictionary containing previous cycle's issues,
                      corrections, and adjustments
                      
        Returns:
            New RunContext with learnings attached
        """
        new_ctx = RunContext(
            profile_id=self.profile_id,
            session_id=self.session_id,
            user_id=self.user_id,
            archetype=self.archetype,
            metadata=self.metadata.copy(),
            _previous_learnings=learnings,
        )
        return new_ctx

    @property
    def has_learnings(self) -> bool:
        """Check if this context has injected learnings."""
        return self._previous_learnings is not None

    @property
    def learnings(self) -> Dict[str, Any]:
        """Get injected learnings or empty dict."""
        return self._previous_learnings or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging."""
        return {
            "profile_id": self.profile_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "archetype": self.archetype,
            "has_learnings": self.has_learnings,
        }
