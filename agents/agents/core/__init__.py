# agents/agents/core/__init__.py
"""
IvyQuest v15.0 - Core Agent Framework

This package provides the foundational components for the IvyQuest
multi-agent ReAct platform:

- ReActAgent: Base class for all agents with quality thresholds
- MemoryManager: 3-tier memory system (working, short-term, long-term)
- HandoffManager: Agent state transfer protocol
- GoldenBenchmark: Quality calibration against golden examples

Usage:
    from agents.agents.core import (
        ReActAgent, RunContext, 
        QualityThresholds, AutonomyLevel,
        MemoryManager, GoldenBenchmark,
    )
    
    class MyAgent(ReActAgent[MyInput]):
        async def _think(self, context, input_data, previous_cycles):
            ...
"""

# Quality thresholds and autonomy
from .thresholds import QualityThresholds, AutonomyLevel

# ReAct types
from .react_types import (
    ReasoningPhase,
    ThoughtProcess,
    ActionResult,
    Observation,
    Learning,
    ReActCycle,
    RunContext,
)

# Working memory
from .working_memory import (
    WorkingMemoryBuffer,
    ContextFrame,
    PlannedAction,
    OptionAnalysis,
    EvaluationFrame,
    LearningFrame,
)

# Golden benchmark
from .golden_benchmark import GoldenBenchmark, GoldenExample

# Handoffs
from .handoff import AgentHandoff, HandoffManager

# Profile snapshots (v13.2)
from .profile_snapshot import ProfileSnapshot, ProfileSnapshotManager

# Interaction memory (v13.2)
from .interaction_memory import InteractionSummary, InteractionMemoryManager

# Memory manager
from .memory import MemoryManager

# ReAct base agent
from .react_base import ReActAgent

# Voice validator
from .voice import JennyVoiceValidator, VoiceScore, VoiceDimension


__all__ = [
    # Thresholds
    "QualityThresholds",
    "AutonomyLevel",
    
    # ReAct types
    "ReasoningPhase",
    "ThoughtProcess",
    "ActionResult",
    "Observation",
    "Learning",
    "ReActCycle",
    "RunContext",
    
    # Working memory
    "WorkingMemoryBuffer",
    "ContextFrame",
    "PlannedAction",
    "OptionAnalysis",
    "EvaluationFrame",
    "LearningFrame",
    
    # Golden benchmark
    "GoldenBenchmark",
    "GoldenExample",
    
    # Handoffs
    "AgentHandoff",
    "HandoffManager",
    
    # Profile snapshots
    "ProfileSnapshot",
    "ProfileSnapshotManager",
    
    # Interaction memory
    "InteractionSummary",
    "InteractionMemoryManager",
    
    # Memory manager
    "MemoryManager",
    
    # ReAct base
    "ReActAgent",
    
    # Voice validator
    "JennyVoiceValidator",
    "VoiceScore",
    "VoiceDimension",
]

__version__ = "15.0.0"
