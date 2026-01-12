"""
IvyQuest v10.0 - Evaluation Framework
=====================================

Automated evaluation infrastructure to measure agent quality
against Jenny Duan's golden coaching examples.

Components:
- GoldenDatasetLoader: Load/manage golden examples from DB
- ObjectiveMetricsCalculator: Automated deterministic checks
- LLMJudge: GPT-4/Claude scoring with rubrics
- EvaluationPipeline: Orchestrate full evaluation runs
"""

from .golden_loader import GoldenDatasetLoader, GoldenExample
from .objective_metrics import ObjectiveMetricsCalculator, ObjectiveScore
from .llm_judge import LLMJudge, JudgeScore, JudgeResult
from .pipeline import EvaluationPipeline, EvaluationResult

__all__ = [
    'GoldenDatasetLoader',
    'GoldenExample',
    'ObjectiveMetricsCalculator',
    'ObjectiveScore',
    'LLMJudge',
    'JudgeScore',
    'JudgeResult',
    'EvaluationPipeline',
    'EvaluationResult',
]
