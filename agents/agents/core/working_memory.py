# agents/agents/core/working_memory.py
"""
IvyQuest v13.2 - Working Memory Buffer

This module implements the WorkingMemoryBuffer class, which provides
structured working memory for agent reasoning. Unlike a simple dict,
this provides:

- Context gathering structure (ContextFrame)
- Action planning tracking (PlannedAction)
- Options analysis for decisions (OptionAnalysis)
- Evaluation history for self-correction (EvaluationFrame)
- Learning accumulation within session (LearningFrame)
- Phase tracking for reasoning audit
"""

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
    """
    Context gathered from memory tiers.
    
    Contains all context an agent needs to reason effectively,
    retrieved from working, short-term, and long-term memory.
    """
    profile_summary: Dict[str, Any]
    relevant_memories: List[Dict[str, Any]]
    coaching_knowledge: List[Dict[str, Any]]
    active_tasks: List[Dict[str, Any]]
    recent_interactions: List[Dict[str, Any]]
    gathered_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_summary": self.profile_summary,
            "memory_count": len(self.relevant_memories),
            "knowledge_count": len(self.coaching_knowledge),
            "active_tasks_count": len(self.active_tasks),
            "recent_interactions_count": len(self.recent_interactions),
            "gathered_at": self.gathered_at.isoformat(),
        }


@dataclass
class PlannedAction:
    """A planned action in the ReAct loop."""
    action_type: str
    description: str
    expected_outcome: str
    confidence: float
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "description": self.description,
            "expected_outcome": self.expected_outcome,
            "confidence": self.confidence,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class OptionAnalysis:
    """
    Analysis of an option during decision-making.
    
    Used when agents need to compare multiple approaches
    and select the best one.
    """
    option_name: str
    pros: List[str]
    cons: List[str]
    fit_score: float
    risk_level: str  # "low", "medium", "high"
    recommended: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "option_name": self.option_name,
            "pros": self.pros,
            "cons": self.cons,
            "fit_score": self.fit_score,
            "risk_level": self.risk_level,
            "recommended": self.recommended,
        }


@dataclass
class EvaluationFrame:
    """
    Evaluation record for self-correction.
    
    This is CRITICAL for the ReAct loop - agents use evaluation
    history to understand what went wrong and fix it.
    """
    cycle_number: int
    quality_score: float
    voice_score: float
    golden_similarity: float
    issues_found: List[str]
    strengths_found: List[str]
    passes_threshold: bool
    needs_correction: bool
    evaluated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_number": self.cycle_number,
            "quality_score": self.quality_score,
            "voice_score": self.voice_score,
            "golden_similarity": self.golden_similarity,
            "issues_found": self.issues_found,
            "strengths_found": self.strengths_found,
            "passes_threshold": self.passes_threshold,
            "needs_correction": self.needs_correction,
            "evaluated_at": self.evaluated_at.isoformat(),
        }


@dataclass
class LearningFrame:
    """
    Accumulated learnings within a session.
    
    Tracks successful strategies, failed approaches, user preferences,
    and context insights discovered during the session.
    """
    successful_strategies: List[Dict[str, Any]] = field(default_factory=list)
    failed_approaches: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    context_insights: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "successful_strategies_count": len(self.successful_strategies),
            "failed_approaches_count": len(self.failed_approaches),
            "user_preferences": self.user_preferences,
            "context_insights": self.context_insights,
        }


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
    
    Each agent gets its own WorkingMemoryBuffer instance for a profile,
    which is cleared when the agent completes its task.
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
        """
        Set the gathered context.
        
        Transitions phase from CONTEXT_GATHERING to PLANNING.
        """
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
        """
        Record a planned action.
        
        Args:
            action_type: Type of action (e.g., "generate", "evaluate")
            description: Human-readable description
            expected_outcome: What success looks like
            confidence: Agent's confidence in this action (0-1)
            dependencies: List of prerequisite actions
            
        Returns:
            The created PlannedAction
        """
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
        """
        Record option analysis for decision-making.
        
        Args:
            option_name: Name of the option being analyzed
            pros: List of advantages
            cons: List of disadvantages
            fit_score: How well it fits the situation (0-1)
            risk_level: "low", "medium", or "high"
            recommended: Whether this is the recommended option
            
        Returns:
            The created OptionAnalysis
        """
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
        
        Args:
            cycle: Cycle number (1-indexed)
            quality: Quality score 0-100
            voice: Voice score 0-100
            golden: Golden similarity 0-1
            issues: List of issues found
            strengths: List of strengths found
            
        Returns:
            The created EvaluationFrame
        """
        from .thresholds import QualityThresholds
        passes = QualityThresholds.passes_all(quality, voice, golden)

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
        """
        Record a strategy that worked well.
        
        Args:
            strategy: Description of the strategy
            context: Context in which it was used
            quality: Quality score achieved
        """
        self.learning.successful_strategies.append({
            "strategy": strategy,
            "context": context,
            "quality_achieved": quality,
            "recorded_at": datetime.utcnow().isoformat(),
        })

    def record_failed_approach(self, approach: str) -> None:
        """Record an approach that didn't work."""
        self.learning.failed_approaches.append(approach)

    def add_context_insight(self, insight: str) -> None:
        """Add a context insight discovered during reasoning."""
        self.learning.context_insights.append(insight)

    def update_user_preference(self, key: str, value: Any) -> None:
        """Update a discovered user preference."""
        self.learning.user_preferences[key] = value

    def get_latest_evaluation(self) -> Optional[EvaluationFrame]:
        """Get most recent evaluation."""
        return self.evaluations[-1] if self.evaluations else None

    def get_improvement_trend(self) -> Dict[str, float]:
        """
        Calculate improvement across evaluations.
        
        Returns:
            Dict with delta for each dimension (positive = improvement)
        """
        if len(self.evaluations) < 2:
            return {"quality": 0.0, "voice": 0.0, "golden": 0.0}

        first = self.evaluations[0]
        last = self.evaluations[-1]

        return {
            "quality": last.quality_score - first.quality_score,
            "voice": last.voice_score - first.voice_score,
            "golden": last.golden_similarity - first.golden_similarity,
        }

    def get_all_issues(self) -> List[str]:
        """Get all unique issues across all evaluations."""
        all_issues = set()
        for eval_frame in self.evaluations:
            all_issues.update(eval_frame.issues_found)
        return list(all_issues)

    def get_all_strengths(self) -> List[str]:
        """Get all unique strengths across all evaluations."""
        all_strengths = set()
        for eval_frame in self.evaluations:
            all_strengths.update(eval_frame.strengths_found)
        return list(all_strengths)

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
            "has_context": self.context is not None,
            "planned_actions_count": len(self.planned_actions),
            "options_analyzed_count": len(self.options_analyzed),
            "evaluations_count": len(self.evaluations),
            "improvement_trend": self.get_improvement_trend(),
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"WorkingMemoryBuffer(agent={self.agent_name}, "
            f"profile={self.profile_id}, phase={self.current_phase.value}, "
            f"evals={len(self.evaluations)})"
        )
