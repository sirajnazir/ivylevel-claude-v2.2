"""
Safety Patterns - v5.4 True Autonomous Agents

Patterns implemented:
- E6: Guardrails (3P: Guardrails AI)

Critical for minors' protection.
"""

from .guardrails import (
    GuardrailsManager,
    MinorSafetyGuardrail,
    OutputValidator,
    GuardrailResult,
    GuardrailType,
    GuardrailViolation,
    check_content_safety,
    validate_agent_output,
    BLOCKED_PATTERNS,
    SENSITIVE_TOPICS,
    SAFE_ALTERNATIVES,
)

__all__ = [
    "GuardrailsManager",
    "MinorSafetyGuardrail",
    "OutputValidator",
    "GuardrailResult",
    "GuardrailType",
    "GuardrailViolation",
    "check_content_safety",
    "validate_agent_output",
    "BLOCKED_PATTERNS",
    "SENSITIVE_TOPICS",
    "SAFE_ALTERNATIVES",
]
