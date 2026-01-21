# tests/agents/patterns/test_governance.py
"""
Tests for Governance patterns: G1 Decision Rights, G3 Escalation
CORRECTED to match actual implementation API
"""

import pytest


class TestDecisionLevel:
    """Tests for DecisionLevel enum."""
    
    def test_decision_level_exists(self):
        """Test DecisionLevel enum exists."""
        from agents.governance.decision_rights import DecisionLevel
        
        assert DecisionLevel is not None
    
    def test_decision_level_has_values(self):
        """Test DecisionLevel has expected values."""
        from agents.governance.decision_rights import DecisionLevel
        
        # Check for common values (may be AUTONOMOUS, HUMAN_REVIEW, etc.)
        values = [e.value for e in DecisionLevel]
        assert len(values) > 0


class TestDecisionRights:
    """Tests for Decision Rights (G1)."""
    
    def test_checker_initialization(self):
        """Test DecisionRightsChecker initialization."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        assert checker is not None
    
    def test_can_decide_returns_tuple(self):
        """Test can_decide returns expected format."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        result = checker.can_decide(
            agent_name="ec_agent",
            decision_type="classify_archetype",
            confidence=0.85,
        )
        
        # Should return tuple of (bool, DecisionLevel, reason)
        assert isinstance(result, tuple)
        assert len(result) == 3
    
    def test_autonomous_decision_allowed(self):
        """Test that autonomous decisions are allowed."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="ec_agent",
            decision_type="classify_archetype",
            confidence=0.85,
        )
        
        assert can_proceed is True
    
    def test_low_confidence_triggers_review(self):
        """Test that low confidence triggers review/escalation."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="ec_agent",
            decision_type="classify_archetype",
            confidence=0.3,  # Very low
        )
        
        # Should not proceed autonomously with low confidence
        assert can_proceed is False
        assert reason is not None
    
    def test_crisis_escalates_to_human(self):
        """Test that crisis decisions escalate to human."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="execution_agent",
            decision_type="crisis_detected",
            confidence=1.0,
        )
        
        assert can_proceed is False
    
    def test_mental_health_escalates_to_human(self):
        """Test mental health signals escalate to human."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="execution_agent",
            decision_type="mental_health_signal",
            confidence=1.0,
        )
        
        assert can_proceed is False
    
    def test_unknown_agent_escalates(self):
        """Test handling of unknown agent."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="unknown_agent",
            decision_type="anything",
            confidence=1.0,
        )
        
        assert can_proceed is False
    
    def test_get_escalation_reason(self):
        """Test getting escalation reason."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        reason = checker.get_escalation_reason("execution_agent", "mental_health_signal")
        
        assert reason is not None
        assert len(reason) > 0


class TestEscalationLevel:
    """Tests for EscalationLevel enum."""
    
    def test_escalation_level_exists(self):
        """Test EscalationLevel enum exists."""
        from agents.governance.escalation import EscalationLevel
        
        assert EscalationLevel is not None
    
    def test_escalation_level_values(self):
        """Test EscalationLevel has expected values."""
        from agents.governance.escalation import EscalationLevel
        
        # Should have IMMEDIATE for urgent situations
        assert hasattr(EscalationLevel, 'IMMEDIATE')


class TestEscalationProtocol:
    """Tests for Escalation Protocol (G3)."""
    
    def test_protocol_initialization(self):
        """Test EscalationProtocol initialization."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        assert protocol is not None
    
    def test_should_escalate_returns_dict(self):
        """Test should_escalate returns expected format."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="self_harm_signal",
            context={},
        )
        
        assert isinstance(result, dict)
        assert "escalate" in result
    
    def test_immediate_escalation_self_harm(self):
        """Test immediate escalation for self-harm signals."""
        from agents.governance.escalation import EscalationProtocol, EscalationLevel
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="self_harm_signal",
            context={"message": "I want to hurt myself"},
        )
        
        assert result["escalate"] is True
        assert result["level"] == EscalationLevel.IMMEDIATE
    
    def test_immediate_escalation_abuse(self):
        """Test immediate escalation for abuse signals."""
        from agents.governance.escalation import EscalationProtocol, EscalationLevel
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="abuse_signal",
            context={},
        )
        
        assert result["escalate"] is True
        assert result["level"] == EscalationLevel.IMMEDIATE
    
    def test_escalation_repeated_failure(self):
        """Test escalation for repeated failures."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="repeated_failure",
            context={"failure_count": 4},
        )
        
        assert result["escalate"] is True
    
    def test_escalation_student_request(self):
        """Test escalation when student requests human."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="student_request",
            context={},
        )
        
        assert result["escalate"] is True
    
    def test_no_escalation_normal(self):
        """Test no escalation for normal operations."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="task_completed",
            context={},
        )
        
        assert result["escalate"] is False
    
    def test_generate_escalation_message(self):
        """Test escalation message generation."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        message = protocol.generate_escalation_message(
            signal_type="crisis_detected",
            context={"student_name": "Test Student"},
        )
        
        assert message is not None
        assert len(message) > 0
