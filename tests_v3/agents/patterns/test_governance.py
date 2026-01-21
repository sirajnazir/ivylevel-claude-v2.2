# tests/agents/patterns/test_governance.py
"""
Tests for Governance patterns: G1 Decision Rights, G3 Escalation
FINAL VERSION - Aligned with actual model structures
"""

import pytest


class TestDecisionRightsChecker:
    """Tests for DecisionRightsChecker (G1)."""
    
    def test_checker_importable(self):
        """Test DecisionRightsChecker can be imported."""
        from agents.governance.decision_rights import DecisionRightsChecker
        assert DecisionRightsChecker is not None
    
    def test_checker_initialization(self):
        """Test DecisionRightsChecker can be initialized."""
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        assert checker is not None
    
    def test_checker_has_can_decide(self):
        """Test DecisionRightsChecker has can_decide method."""
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        assert hasattr(checker, 'can_decide')
    
    def test_can_decide_returns_tuple(self):
        """Test can_decide returns a tuple."""
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        result = checker.can_decide(
            agent_name="ec_agent",
            decision_type="classify_archetype",
            confidence=0.85,
        )
        assert isinstance(result, tuple)
        assert len(result) == 3  # (can_proceed, level, reason)
    
    def test_autonomous_decision_proceeds(self):
        """Test autonomous decision is allowed to proceed."""
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        can_proceed, level, reason = checker.can_decide(
            agent_name="ec_agent",
            decision_type="classify_archetype",
            confidence=0.85,
        )
        assert can_proceed is True
    
    def test_low_confidence_blocks(self):
        """Test low confidence blocks decision."""
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        can_proceed, level, reason = checker.can_decide(
            agent_name="ec_agent",
            decision_type="classify_archetype",
            confidence=0.3,
        )
        assert can_proceed is False
        assert reason is not None
    
    def test_crisis_escalates(self):
        """Test crisis detection escalates to human."""
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        can_proceed, level, reason = checker.can_decide(
            agent_name="execution_agent",
            decision_type="crisis_detected",
            confidence=1.0,
        )
        assert can_proceed is False
    
    def test_unknown_agent_escalates(self):
        """Test unknown agent escalates."""
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        can_proceed, level, reason = checker.can_decide(
            agent_name="unknown_agent",
            decision_type="anything",
            confidence=1.0,
        )
        assert can_proceed is False
    
    def test_get_escalation_reason_exists(self):
        """Test get_escalation_reason method exists."""
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        assert hasattr(checker, 'get_escalation_reason')


class TestDecisionLevel:
    """Tests for DecisionLevel enum."""
    
    def test_decision_level_importable(self):
        """Test DecisionLevel can be imported."""
        from agents.governance.decision_rights import DecisionLevel
        assert DecisionLevel is not None
    
    def test_decision_level_is_enum(self):
        """Test DecisionLevel is an enum."""
        from agents.governance.decision_rights import DecisionLevel
        from enum import Enum
        assert issubclass(DecisionLevel, Enum)
    
    def test_decision_level_has_values(self):
        """Test DecisionLevel has values."""
        from agents.governance.decision_rights import DecisionLevel
        values = list(DecisionLevel)
        assert len(values) >= 2


class TestEscalationProtocol:
    """Tests for EscalationProtocol (G3)."""
    
    def test_protocol_importable(self):
        """Test EscalationProtocol can be imported."""
        from agents.governance.escalation import EscalationProtocol
        assert EscalationProtocol is not None
    
    def test_protocol_initialization(self):
        """Test EscalationProtocol can be initialized."""
        from agents.governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        assert protocol is not None
    
    def test_protocol_has_should_escalate(self):
        """Test EscalationProtocol has should_escalate method."""
        from agents.governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        assert hasattr(protocol, 'should_escalate')
    
    def test_should_escalate_returns_dict(self):
        """Test should_escalate returns a dict."""
        from agents.governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        result = protocol.should_escalate(
            signal_type="self_harm_signal",
            context={},
        )
        assert isinstance(result, dict)
        assert "escalate" in result
    
    def test_self_harm_escalates(self):
        """Test self-harm signal triggers escalation."""
        from agents.governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        result = protocol.should_escalate(
            signal_type="self_harm_signal",
            context={},
        )
        assert result["escalate"] is True
    
    def test_abuse_escalates(self):
        """Test abuse signal triggers escalation."""
        from agents.governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        result = protocol.should_escalate(
            signal_type="abuse_signal",
            context={},
        )
        assert result["escalate"] is True
    
    def test_normal_operation_no_escalate(self):
        """Test normal operation does not escalate."""
        from agents.governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        result = protocol.should_escalate(
            signal_type="task_completed",
            context={},
        )
        assert result["escalate"] is False
    
    def test_escalate_result_has_level(self):
        """Test escalate result includes level when escalating."""
        from agents.governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        result = protocol.should_escalate(
            signal_type="self_harm_signal",
            context={},
        )
        assert "level" in result
    
    def test_generate_escalation_message_exists(self):
        """Test generate_escalation_message method exists."""
        from agents.governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        assert hasattr(protocol, 'generate_escalation_message')


class TestEscalationLevel:
    """Tests for EscalationLevel enum."""
    
    def test_escalation_level_importable(self):
        """Test EscalationLevel can be imported."""
        from agents.governance.escalation import EscalationLevel
        assert EscalationLevel is not None
    
    def test_escalation_level_is_enum(self):
        """Test EscalationLevel is an enum."""
        from agents.governance.escalation import EscalationLevel
        from enum import Enum
        assert issubclass(EscalationLevel, Enum)
    
    def test_escalation_level_has_immediate(self):
        """Test EscalationLevel has IMMEDIATE."""
        from agents.governance.escalation import EscalationLevel
        assert hasattr(EscalationLevel, 'IMMEDIATE')
