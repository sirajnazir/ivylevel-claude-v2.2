"""
Governance Patterns - v5.4 True Autonomous Agents

Patterns implemented:
- G1: Decision Rights (3P: Pydantic)
- G3: Escalation Protocol (3P: Pydantic)

Critical for minors' safety and appropriate oversight.
"""

from .decision_rights import (
    DecisionRightsManager,
    Decision,
    DecisionLevel,
    DecisionCategory,
    check_decision_rights,
    detect_context_factors,
    DECISION_RIGHTS_MATRIX,
    CONFIDENCE_THRESHOLDS,
)

from .escalation import (
    EscalationProtocol,
    Escalation,
    EscalationLevel,
    EscalationReason,
    SafetyResponse,
    check_escalation_needed,
    create_escalation,
    ESCALATION_TRIGGERS,
    REASON_TO_LEVEL,
)

__all__ = [
    # Decision Rights
    "DecisionRightsManager",
    "Decision",
    "DecisionLevel",
    "DecisionCategory",
    "check_decision_rights",
    "detect_context_factors",
    "DECISION_RIGHTS_MATRIX",
    "CONFIDENCE_THRESHOLDS",
    # Escalation
    "EscalationProtocol",
    "Escalation",
    "EscalationLevel",
    "EscalationReason",
    "SafetyResponse",
    "check_escalation_needed",
    "create_escalation",
    "ESCALATION_TRIGGERS",
    "REASON_TO_LEVEL",
]
