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


# =============================================================================
# V5.1 ENHANCED TYPES FOR VERBOSE CYCLE VISUALIZATION
# =============================================================================

# =============================================================================
# EXCEPTION HIERARCHY (P2)
# =============================================================================

class ReActError(Exception):
    """Base class for all ReAct errors."""

    def __init__(self, message: str, agent_id: str = None, cycle: int = None, phase: str = None):
        self.agent_id = agent_id
        self.cycle = cycle
        self.phase = phase
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "agent_id": self.agent_id,
            "cycle": self.cycle,
            "phase": self.phase,
            "timestamp": self.timestamp,
        }


class ThinkPhaseError(ReActError):
    """Error during THINK phase - reasoning/planning failed."""
    pass


class ActPhaseError(ReActError):
    """Error during ACT phase - execution failed."""

    def __init__(self, message: str, tool_name: str = None, **kwargs):
        self.tool_name = tool_name
        super().__init__(message, **kwargs)


class ObservePhaseError(ReActError):
    """Error during OBSERVE phase - quality validation failed."""

    def __init__(self, message: str, validation_type: str = None, **kwargs):
        self.validation_type = validation_type
        super().__init__(message, **kwargs)


class LearnPhaseError(ReActError):
    """Error during LEARN phase - learning extraction failed."""
    pass


class MaxCyclesExceededError(ReActError):
    """Quality threshold not met within max cycles."""

    def __init__(self, message: str, best_score: float = None, threshold: float = None, **kwargs):
        self.best_score = best_score
        self.threshold = threshold
        super().__init__(message, **kwargs)


# =============================================================================
# TOOL TRACKING TYPES (P0/P1)
# =============================================================================

class ToolStatus(str, Enum):
    """Status of a tool execution."""
    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ToolSelection:
    """A tool selected during THINK phase."""
    tool_id: str
    tool_name: str
    purpose: str
    priority: int = 0
    estimated_duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "purpose": self.purpose,
            "priority": self.priority,
            "estimated_duration_ms": self.estimated_duration_ms,
        }


@dataclass
class ToolExecution:
    """Record of a tool execution during ACT phase."""
    tool_id: str
    tool_name: str
    status: ToolStatus
    input_summary: Dict[str, Any] = field(default_factory=dict)
    output_summary: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "status": self.status.value,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


# =============================================================================
# VERBOSE PHASE DATA TYPES (P0)
# =============================================================================

@dataclass
class ThinkPhaseOutput:
    """
    Complete THINK phase output for visualization.
    Maps to TypeScript ThinkPhaseData interface.
    """
    reasoning: str
    planned_actions: List[str]
    focus_areas: List[str]
    gap_analysis: Dict[str, Any]
    tools_selected: List[ToolSelection]
    benchmark_targets: Dict[str, Any]
    confidence: float
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reasoning": self.reasoning,
            "planned_actions": self.planned_actions,
            "focus_areas": self.focus_areas,
            "gap_analysis": self.gap_analysis,
            "tools_selected": [t.to_dict() for t in self.tools_selected],
            "benchmark_targets": self.benchmark_targets,
            "confidence": self.confidence,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_thought_process(
        cls,
        thought: "ThoughtProcess",
        tools: List[ToolSelection],
        gap_analysis: Dict[str, Any] = None,
        benchmark_targets: Dict[str, Any] = None,
        duration_ms: int = 0
    ) -> "ThinkPhaseOutput":
        """Convert existing ThoughtProcess to verbose output."""
        return cls(
            reasoning=thought.reasoning,
            planned_actions=[thought.planned_action] + thought.alternative_approaches[:2],
            focus_areas=thought.context_factors,
            gap_analysis=gap_analysis or {},
            tools_selected=tools,
            benchmark_targets=benchmark_targets or {},
            confidence=thought.confidence,
            duration_ms=duration_ms,
        )


@dataclass
class ActPhaseOutput:
    """
    Complete ACT phase output for visualization.
    Maps to TypeScript ActPhaseData interface.
    """
    action: str
    tools_executed: List[ToolExecution]
    hints_applied: List[str]
    input_summary: Dict[str, Any]
    output_summary: Dict[str, Any]
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "tools_executed": [t.to_dict() for t in self.tools_executed],
            "hints_applied": self.hints_applied,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "duration_ms": self.duration_ms,
        }


@dataclass
class ObservePhaseOutput:
    """
    Complete OBSERVE phase output for visualization.
    Maps to TypeScript ObservePhaseData interface.
    """
    quality_scores: Dict[str, float]  # guardrails, voice, golden, only_they
    combined_score: float
    passed: bool
    failing_dimensions: List[str]
    issues_found: List[str]
    strengths_found: List[str]
    benchmark_comparison: Dict[str, Any]
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quality_scores": self.quality_scores,
            "combined_score": self.combined_score,
            "passed": self.passed,
            "failing_dimensions": self.failing_dimensions,
            "issues_found": self.issues_found,
            "strengths_found": self.strengths_found,
            "benchmark_comparison": self.benchmark_comparison,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_observation(
        cls,
        obs: "Observation",
        only_they_score: float = 0.0,
        benchmark_comparison: Dict[str, Any] = None,
        duration_ms: int = 0
    ) -> "ObservePhaseOutput":
        """Convert existing Observation to verbose output."""
        return cls(
            quality_scores={
                "guardrails": obs.quality_score,
                "voice": obs.voice_score,
                "golden": obs.golden_similarity * 100,
                "only_they": only_they_score,
            },
            combined_score=obs.combined_score,
            passed=obs.passes_thresholds,
            failing_dimensions=obs.failing_dimensions,
            issues_found=obs.issues_found,
            strengths_found=obs.strengths,
            benchmark_comparison=benchmark_comparison or {},
            duration_ms=duration_ms,
        )


@dataclass
class LearnPhaseOutput:
    """
    Complete LEARN phase output for visualization.
    Maps to TypeScript LearnPhaseData interface.
    """
    reasoning: str
    what_worked: List[str]
    what_failed: List[str]
    quality_delta: float
    corrections_to_apply: List[str]
    should_continue: bool
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reasoning": self.reasoning,
            "what_worked": self.what_worked,
            "what_failed": self.what_failed,
            "quality_delta": self.quality_delta,
            "corrections_to_apply": self.corrections_to_apply,
            "should_continue": self.should_continue,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_learning(
        cls,
        learning: "Learning",
        quality_delta: float,
        reasoning: str = "",
        duration_ms: int = 0
    ) -> "LearnPhaseOutput":
        """Convert existing Learning to verbose output."""
        return cls(
            reasoning=reasoning or f"Quality changed by {quality_delta:+.1f} points",
            what_worked=learning.successful_patterns,
            what_failed=learning.failed_patterns,
            quality_delta=quality_delta,
            corrections_to_apply=learning.adjustments_made,
            should_continue=learning.should_try_alternative,
            duration_ms=duration_ms,
        )


# =============================================================================
# VERBOSE CYCLE SUMMARY (P0)
# =============================================================================

@dataclass
class VerboseCycleSummary:
    """
    Complete cycle summary with all phase details.
    Maps to TypeScript CycleSummary interface.
    This is what the frontend needs for full visualization.
    """
    cycle: int
    think: ThinkPhaseOutput
    act: ActPhaseOutput
    observe: ObservePhaseOutput
    learn: LearnPhaseOutput
    combined_score: float
    quality_delta: float
    passed: bool
    duration_ms: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle": self.cycle,
            "think": self.think.to_dict(),
            "act": self.act.to_dict(),
            "observe": self.observe.to_dict(),
            "learn": self.learn.to_dict(),
            "combined_score": self.combined_score,
            "quality_delta": self.quality_delta,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
        }


# =============================================================================
# INPUT DATA FLOW TRACKING (P1)
# =============================================================================

@dataclass
class DataFlowNode:
    """A node in the data flow graph."""
    node_id: str
    node_type: str  # 'agent', 'data', 'external'
    label: str
    data_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "data_summary": self.data_summary,
        }


@dataclass
class DataFlowEdge:
    """An edge in the data flow graph."""
    from_node: str
    to_node: str
    data_type: str
    fields_passed: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "data_type": self.data_type,
            "fields_passed": self.fields_passed,
        }


@dataclass
class InputDataFlow:
    """
    Complete input/output data flow tracking for an agent.
    Maps to TypeScript InputDataFlow interface.
    """
    agent_id: str
    nodes: List[DataFlowNode] = field(default_factory=list)
    edges: List[DataFlowEdge] = field(default_factory=list)

    # Convenience accessors for common flows
    from_assessment: Dict[str, Any] = field(default_factory=dict)
    from_profile: Dict[str, Any] = field(default_factory=dict)
    from_upstream_agent: Dict[str, Any] = field(default_factory=dict)
    to_downstream_agents: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def add_input(self, source_id: str, source_type: str, data: Dict[str, Any], fields: List[str]):
        """Add an input to this agent."""
        self.nodes.append(DataFlowNode(
            node_id=source_id,
            node_type=source_type,
            label=source_id,
            data_summary=self._summarize(data),
        ))
        self.edges.append(DataFlowEdge(
            from_node=source_id,
            to_node=self.agent_id,
            data_type="input",
            fields_passed=fields,
        ))

    def add_output(self, target_id: str, data: Dict[str, Any], fields: List[str]):
        """Add an output from this agent."""
        self.nodes.append(DataFlowNode(
            node_id=target_id,
            node_type="agent",
            label=target_id,
            data_summary=self._summarize(data),
        ))
        self.edges.append(DataFlowEdge(
            from_node=self.agent_id,
            to_node=target_id,
            data_type="output",
            fields_passed=fields,
        ))
        self.to_downstream_agents[target_id] = self._summarize(data)

    def _summarize(self, data: Dict[str, Any], max_depth: int = 2) -> Dict[str, Any]:
        """Create a summary of data for visualization."""
        if max_depth <= 0:
            return {"_truncated": True}

        summary = {}
        for key, value in data.items():
            if isinstance(value, dict):
                summary[key] = self._summarize(value, max_depth - 1)
            elif isinstance(value, list):
                summary[key] = f"[{len(value)} items]"
            elif isinstance(value, str) and len(value) > 100:
                summary[key] = value[:100] + "..."
            else:
                summary[key] = value
        return summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "from_assessment": self.from_assessment,
            "from_profile": self.from_profile,
            "from_upstream_agent": self.from_upstream_agent,
            "to_downstream_agents": self.to_downstream_agents,
        }


# =============================================================================
# ENHANCED REACT METADATA (P0)
# =============================================================================

@dataclass
class EnhancedReActMetadata:
    """
    Enhanced ReAct metadata with verbose cycle summaries.
    This replaces the minimal _build_react_metadata() output.
    """
    success: bool
    cycles_executed: int
    max_cycles: int
    final_score: float
    passed_quality: bool
    improvement_trajectory: List[float]
    total_duration_ms: int

    # Verbose cycle summaries (the key enhancement)
    cycle_summaries: List[VerboseCycleSummary]

    # Data flow tracking
    input_data_flow: Optional[InputDataFlow] = None

    # Metadata
    agent_id: str = ""
    version: str = "5.1"
    agentic_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "cycles_executed": self.cycles_executed,
            "max_cycles": self.max_cycles,
            "final_confidence": self.final_score / 100,  # Backwards compat
            "final_score": self.final_score,
            "passed_quality": self.passed_quality,
            "improvement_trajectory": self.improvement_trajectory,
            "total_duration_ms": self.total_duration_ms,
            "cycle_summary": [c.to_dict() for c in self.cycle_summaries],
            "input_data_flow": self.input_data_flow.to_dict() if self.input_data_flow else None,
            "agent_id": self.agent_id,
            "version": self.version,
            "agentic_enabled": self.agentic_enabled,
        }


# =============================================================================
# QUALITY SCORE WITH ALL 4 WEIGHTS (Updated)
# =============================================================================

@dataclass
class QualityScore:
    """
    Quality score with all 4 weighted dimensions.
    Weights: guardrails (0.25), voice (0.20), golden (0.25), only_they (0.30)
    """
    guardrails_score: float = 0.0  # Weight: 0.25
    voice_score: float = 0.0       # Weight: 0.20
    golden_score: float = 0.0      # Weight: 0.25
    only_they_score: float = 0.0   # Weight: 0.30

    # Weights as class constants
    WEIGHTS = {
        "guardrails": 0.25,
        "voice": 0.20,
        "golden": 0.25,
        "only_they": 0.30,
    }

    @property
    def combined_score(self) -> float:
        """Compute weighted combined score."""
        return (
            self.guardrails_score * self.WEIGHTS["guardrails"] +
            self.voice_score * self.WEIGHTS["voice"] +
            self.golden_score * 100 * self.WEIGHTS["golden"] +  # golden is 0-1, scale to 0-100
            self.only_they_score * self.WEIGHTS["only_they"]
        )

    @property
    def passed(self) -> bool:
        """Check if combined score meets threshold (70)."""
        return self.combined_score >= 70.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "guardrails_score": self.guardrails_score,
            "voice_score": self.voice_score,
            "golden_score": self.golden_score,
            "only_they_score": self.only_they_score,
            "combined_score": self.combined_score,
            "passed": self.passed,
            "weights": self.WEIGHTS,
        }
