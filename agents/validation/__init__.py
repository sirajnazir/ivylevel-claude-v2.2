"""
Validation Patterns - v5.4 True Autonomous Agents

Patterns implemented:
- E1: Output Validation (3P: Pydantic)
- Jenny Voice validation (existing)
"""

from .jenny_voice import JennyVoiceValidator, JennyVoiceResult, validate_jenny_voice

from .output_validation import (
    OutputValidator,
    ValidationResult,
    QualityDimension,
    validate_output,
    QUALITY_DIMENSIONS,
)

__all__ = [
    # Jenny Voice (existing)
    'JennyVoiceValidator',
    'JennyVoiceResult',
    'validate_jenny_voice',
    # Output Validation (E1)
    'OutputValidator',
    'ValidationResult',
    'QualityDimension',
    'validate_output',
    'QUALITY_DIMENSIONS',
]
