"""
Quality Patterns - Phase 2A

E7: Producer-Critic - Generate-then-evaluate pattern
E3: Reflection Loops - Post-generation revision loop

Usage:
    from middleware.quality import ProducerCriticPipeline, ReflectionLoop

    # Producer-Critic
    pipeline = ProducerCriticPipeline(llm_client)
    result = await pipeline.produce_and_critique(producer_func, output_type="advice")

    # Reflection Loop
    reflection = ReflectionLoop(llm_client)
    improved = await reflection.reflect_and_improve(output, critique_feedback)
"""

from .producer_critic import (
    ProducerCriticPipeline,
    CritiqueResult,
    EvaluationCriteria,
    COACHING_CRITERIA,
    with_critique,
)
from .reflection import (
    ReflectionLoop,
    ReflectionStep,
    ReflectionResult,
)

__all__ = [
    # Producer-Critic
    "ProducerCriticPipeline",
    "CritiqueResult",
    "EvaluationCriteria",
    "COACHING_CRITERIA",
    "with_critique",
    # Reflection
    "ReflectionLoop",
    "ReflectionStep",
    "ReflectionResult",
]
