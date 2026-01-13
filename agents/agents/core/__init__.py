"""
IvyQuest Hybrid Agent Core Components
=====================================
v4.0 - Grounded Intelligence + LLM Augmentation

Components:
- ProfileSignals: Extract signals from profile data
- StrategicRouter: Deterministic strategic approach selection
- GuardrailsEngine: Output validation
"""

from .profile_signals import ProfileSignals, extract_profile_signals
from .strategic_router import (
    StrategicRouter,
    StrategicRoute,
    StrategicApproach,
    calculate_months_to_ed,
    LLMRouter,  # Backwards compatibility alias
)
from .guardrails import GuardrailsEngine, ValidationResult, validate_awards_output, validate_programs_output

__all__ = [
    # Profile Signals
    "ProfileSignals",
    "extract_profile_signals",
    # Strategic Router
    "StrategicRouter",
    "StrategicRoute",
    "StrategicApproach",
    "calculate_months_to_ed",
    "LLMRouter",  # Backwards compatibility
    # Guardrails
    "GuardrailsEngine",
    "ValidationResult",
    "validate_awards_output",
    "validate_programs_output",
]
