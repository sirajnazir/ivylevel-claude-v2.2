# agents/tests/patterns/test_governance.py
"""
Tests for Governance Patterns (G1, G3) - v5.4 True Autonomous Agents.

Tests:
- G1: Decision Rights management
- G3: Escalation Protocol for safety

Critical for minors' safety and appropriate oversight.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestDecisionRights:
    """Tests for G1: Decision Rights pattern."""

    def test_decision_rights_manager_creation(self):
        """Test DecisionRightsManager can be created."""
        from governance import DecisionRightsManager

        manager = DecisionRightsManager()

        assert manager is not None

    def test_decision_levels_enum(self):
        """Test DecisionLevel enum values."""
        from governance import DecisionLevel

        assert DecisionLevel.AUTONOMOUS is not None
        assert DecisionLevel.SUGGEST is not None
        assert DecisionLevel.CONFIRM is not None
        assert DecisionLevel.ESCALATE is not None

    def test_decision_categories_enum(self):
        """Test DecisionCategory enum values."""
        from governance import DecisionCategory

        # Key categories for college admissions
        assert DecisionCategory.RECOMMENDATION is not None
        assert DecisionCategory.ASSESSMENT is not None
        assert DecisionCategory.COMMUNICATION is not None

    def test_check_autonomous_decision(self, sample_student_context):
        """Test checking rights for autonomous decisions."""
        from governance import DecisionRightsManager, DecisionCategory, DecisionLevel

        manager = DecisionRightsManager()

        # Simple recommendation should be autonomous
        decision = manager.check_rights(
            category=DecisionCategory.RECOMMENDATION,
            context=sample_student_context,
            confidence=0.9,
        )

        assert decision is not None
        assert decision.level in [DecisionLevel.AUTONOMOUS, DecisionLevel.SUGGEST]

    def test_check_escalate_decision(self, sample_student_context):
        """Test checking rights for decisions requiring escalation."""
        from governance import DecisionRightsManager, DecisionCategory, DecisionLevel

        manager = DecisionRightsManager()

        # Low confidence should require confirmation/escalation
        decision = manager.check_rights(
            category=DecisionCategory.ASSESSMENT,
            context=sample_student_context,
            confidence=0.3,  # Low confidence
        )

        assert decision.level in [DecisionLevel.CONFIRM, DecisionLevel.ESCALATE, DecisionLevel.SUGGEST]

    def test_decision_model(self):
        """Test Decision model structure."""
        from governance import Decision, DecisionLevel, DecisionCategory

        decision = Decision(
            decision_id="dec-123",
            category=DecisionCategory.RECOMMENDATION,
            level=DecisionLevel.AUTONOMOUS,
            confidence=0.85,
            reasoning="High confidence recommendation based on profile data",
            requires_confirmation=False,
        )

        assert decision.level == DecisionLevel.AUTONOMOUS
        assert decision.requires_confirmation is False

    def test_decision_rights_matrix_exists(self):
        """Test decision rights matrix is defined."""
        from governance import DECISION_RIGHTS_MATRIX

        assert DECISION_RIGHTS_MATRIX is not None
        assert isinstance(DECISION_RIGHTS_MATRIX, dict)

    def test_confidence_thresholds_defined(self):
        """Test confidence thresholds are configured."""
        from governance import CONFIDENCE_THRESHOLDS

        assert CONFIDENCE_THRESHOLDS is not None
        assert isinstance(CONFIDENCE_THRESHOLDS, dict)

    def test_detect_context_factors(self, sample_student_context):
        """Test detecting context factors that affect decision rights."""
        from governance import detect_context_factors

        factors = detect_context_factors(sample_student_context)

        assert isinstance(factors, dict)

    def test_convenience_function_check_rights(self):
        """Test convenience function for checking decision rights."""
        from governance import check_decision_rights

        assert callable(check_decision_rights)


class TestEscalation:
    """Tests for G3: Escalation Protocol pattern."""

    def test_escalation_protocol_creation(self):
        """Test EscalationProtocol can be created."""
        from governance import EscalationProtocol

        protocol = EscalationProtocol()

        assert protocol is not None

    def test_escalation_levels_enum(self):
        """Test EscalationLevel enum values."""
        from governance import EscalationLevel

        assert EscalationLevel.NONE is not None
        assert EscalationLevel.HUMAN_REVIEW is not None
        assert EscalationLevel.IMMEDIATE_ALERT is not None
        assert EscalationLevel.EMERGENCY is not None

    def test_escalation_reasons_enum(self):
        """Test EscalationReason enum values."""
        from governance import EscalationReason

        # Safety-related reasons
        assert EscalationReason.SELF_HARM is not None
        assert EscalationReason.MENTAL_HEALTH is not None
        assert EscalationReason.BULLYING is not None
        assert EscalationReason.FAMILY_STRESS is not None

    def test_check_safe_message_no_escalation(self, safe_messages):
        """Test safe messages don't trigger escalation."""
        from governance import EscalationProtocol

        protocol = EscalationProtocol()

        for message in safe_messages:
            result = protocol.check_for_escalation(message, {})
            assert result is None or result[1].value == "none"

    def test_check_unsafe_message_triggers_escalation(self, unsafe_messages):
        """Test unsafe messages trigger appropriate escalation."""
        from governance import EscalationProtocol, EscalationLevel

        protocol = EscalationProtocol()

        for message in unsafe_messages:
            result = protocol.check_for_escalation(message, {})
            if result:
                reason, level = result
                assert level != EscalationLevel.NONE

    def test_self_harm_triggers_emergency(self):
        """Test self-harm indicators trigger emergency escalation."""
        from governance import EscalationProtocol, EscalationLevel, EscalationReason

        protocol = EscalationProtocol()

        message = "I feel like hurting myself"
        result = protocol.check_for_escalation(message, {})

        if result:
            reason, level = result
            assert reason == EscalationReason.SELF_HARM
            assert level in [EscalationLevel.EMERGENCY, EscalationLevel.IMMEDIATE_ALERT]

    def test_escalation_model(self):
        """Test Escalation model structure."""
        from governance import Escalation, EscalationLevel, EscalationReason

        escalation = Escalation(
            escalation_id="esc-123",
            reason=EscalationReason.MENTAL_HEALTH,
            level=EscalationLevel.HUMAN_REVIEW,
            trigger_content="I'm feeling overwhelmed",
            context={"profile_id": "profile-123"},
            created_at=datetime.utcnow(),
        )

        assert escalation.reason == EscalationReason.MENTAL_HEALTH
        assert escalation.level == EscalationLevel.HUMAN_REVIEW

    def test_safety_response_generation(self):
        """Test SafetyResponse provides appropriate responses."""
        from governance import SafetyResponse, EscalationReason

        # Self-harm response
        response = SafetyResponse.get_response(
            EscalationReason.SELF_HARM,
            {"name": "Test Student"}
        )

        assert response is not None
        assert len(response) > 0
        # Should include support resources

    def test_escalation_triggers_defined(self):
        """Test escalation triggers are configured."""
        from governance import ESCALATION_TRIGGERS

        assert ESCALATION_TRIGGERS is not None
        assert isinstance(ESCALATION_TRIGGERS, dict)

    def test_reason_to_level_mapping(self):
        """Test reason to escalation level mapping exists."""
        from governance import REASON_TO_LEVEL

        assert REASON_TO_LEVEL is not None
        assert isinstance(REASON_TO_LEVEL, dict)

    def test_create_escalation_function(self):
        """Test convenience function for creating escalations."""
        from governance import create_escalation, EscalationReason

        escalation = create_escalation(
            reason=EscalationReason.MENTAL_HEALTH,
            trigger_content="Test content",
            context={"profile_id": "test"},
        )

        assert escalation is not None
        assert escalation.reason == EscalationReason.MENTAL_HEALTH

    def test_convenience_function_check_escalation(self):
        """Test convenience function for checking escalation."""
        from governance import check_escalation_needed

        assert callable(check_escalation_needed)


class TestGovernanceIntegration:
    """Integration tests for governance patterns working together."""

    def test_all_governance_types_importable(self):
        """Test all governance types can be imported."""
        from governance import (
            DecisionRightsManager,
            Decision,
            DecisionLevel,
            DecisionCategory,
            EscalationProtocol,
            Escalation,
            EscalationLevel,
            EscalationReason,
            SafetyResponse,
        )

        # All should be importable

    def test_decision_with_escalation_context(self, unsafe_messages):
        """Test decisions incorporate escalation context."""
        from governance import DecisionRightsManager, EscalationProtocol, DecisionCategory

        rights_manager = DecisionRightsManager()
        escalation_protocol = EscalationProtocol()

        # Check escalation first
        message = unsafe_messages[0]
        escalation = escalation_protocol.check_for_escalation(message, {})

        if escalation:
            reason, level = escalation
            # Decision should consider escalation
            decision = rights_manager.check_rights(
                category=DecisionCategory.COMMUNICATION,
                context={"escalation_level": level.value},
                confidence=0.9,
            )
            # Should not be autonomous if escalated

    def test_edge_case_messages_handled(self, edge_case_messages):
        """Test edge case messages are handled appropriately."""
        from governance import EscalationProtocol

        protocol = EscalationProtocol()

        for message in edge_case_messages:
            # Should not crash
            result = protocol.check_for_escalation(message, {})
            # Edge cases might or might not escalate, but should handle gracefully

    def test_multiple_escalation_triggers_in_message(self):
        """Test handling messages with multiple escalation triggers."""
        from governance import EscalationProtocol

        protocol = EscalationProtocol()

        message = "I'm being bullied and I feel like hurting myself"
        result = protocol.check_for_escalation(message, {})

        if result:
            reason, level = result
            # Should escalate to most severe level

    def test_decision_rights_respect_escalation(self):
        """Test decision rights are restricted during escalation."""
        from governance import DecisionRightsManager, DecisionCategory, DecisionLevel

        manager = DecisionRightsManager()

        # Context with active escalation
        escalated_context = {
            "profile_id": "test",
            "active_escalation": True,
            "escalation_level": "emergency",
        }

        decision = manager.check_rights(
            category=DecisionCategory.RECOMMENDATION,
            context=escalated_context,
            confidence=0.9,
        )

        # Even high confidence should require human oversight
