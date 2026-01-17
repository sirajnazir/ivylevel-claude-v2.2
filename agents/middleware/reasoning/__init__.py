"""
Reasoning Patterns - Phase 2A

A6: ReAct Loop - Full THINK -> ACT -> OBSERVE cycle
A7: Self-Correction - Internal critique and revision
A2: Deliberative Reasoning - Multi-step planning before acting

Usage:
    from middleware.reasoning import ReActLoop, SelfCorrector, DeliberativeReasoner

    # ReAct Loop
    react = ReActLoop(llm_client, tools={...})
    result = await react.run(task="Help student with essay", context={...})

    # Self-Correction
    corrector = SelfCorrector(llm_client)
    result = await corrector.generate_with_self_correction(prompt, context)

    # Deliberative Reasoning
    reasoner = DeliberativeReasoner(llm_client)
    result = await reasoner.deliberate(task, context)
"""

from .react_loop import (
    ReActLoop,
    ReActPhase,
    ReActStep,
    ReActResult,
)
from .self_correction import (
    SelfCorrector,
    SelfCorrectionResult,
    CorrectionAttempt,
)
from .deliberative import (
    DeliberativeReasoner,
    DeliberationStep,
    DeliberationResult,
)

__all__ = [
    # ReAct
    "ReActLoop",
    "ReActPhase",
    "ReActStep",
    "ReActResult",
    # Self-Correction
    "SelfCorrector",
    "SelfCorrectionResult",
    "CorrectionAttempt",
    # Deliberative
    "DeliberativeReasoner",
    "DeliberationStep",
    "DeliberationResult",
]
