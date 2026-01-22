# tests/agents/patterns/test_governance.py
"""
Tests for Governance patterns: G1 Decision Rights, G3 Escalation
"""

import pytest


class TestDecisionRights:
    """Tests for Decision Rights (G1)."""
    
    def test_autonomous_decision_allowed(self):
        """Test that autonomous decisions are allowed."""
        from agents.governance.decision_rights import DecisionRightsChecker, DecisionLevel
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="ec_agent",
            decision_type="classify_archetype",
            confidence=0.85,
        )
        
        assert can_proceed is True
        assert level == DecisionLevel.AUTONOMOUS
        assert reason is None
    
    def test_review_required_decision(self):
        """Test that some decisions require review."""
        from agents.governance.decision_rights import DecisionRightsChecker, DecisionLevel
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="ec_agent",
            decision_type="generate_spike",
            confidence=0.85,
        )
        
        assert can_proceed is True
        assert level == DecisionLevel.REVIEW_REQUIRED
    
    def test_escalate_crisis_to_human(self):
        """Test that crisis decisions escalate to human."""
        from agents.governance.decision_rights import DecisionRightsChecker, DecisionLevel
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="execution_agent",
            decision_type="crisis_detected",
            confidence=1.0,
        )
        
        assert can_proceed is False
        assert level == DecisionLevel.HUMAN_ONLY
    
    def test_escalate_mental_health_to_human(self):
        """Test mental health signals escalate to human."""
        from agents.governance.decision_rights import DecisionRightsChecker, DecisionLevel
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="execution_agent",
            decision_type="mental_health_signal",
            confidence=1.0,
        )
        
        assert can_proceed is False
        assert level == DecisionLevel.HUMAN_ONLY
    
    def test_low_confidence_triggers_escalation(self):
        """Test that low confidence triggers escalation."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="ec_agent",
            decision_type="classify_archetype",
            confidence=0.5,  # Below 0.7 threshold
        )
        
        assert can_proceed is False
        assert "confidence" in reason.lower()
    
    def test_unknown_agent_escalates(self):
        """Test handling of unknown agent."""
        from agents.governance.decision_rights import DecisionRightsChecker, DecisionLevel
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, reason = checker.can_decide(
            agent_name="unknown_agent",
            decision_type="anything",
            confidence=1.0,
        )
        
        assert can_proceed is False
        assert level == DecisionLevel.HUMAN_ONLY
    
    def test_escalation_reason_messages(self):
        """Test human-readable escalation reasons."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        reason = checker.get_escalation_reason("execution_agent", "mental_health_signal")
        
        assert len(reason) > 0
        assert "mental health" in reason.lower() or "coach" in reason.lower()
    
    def test_awards_agent_decisions(self):
        """Test Awards Agent decision rights."""
        from agents.governance.decision_rights import DecisionRightsChecker, DecisionLevel
        
        checker = DecisionRightsChecker()
        
        # Search should be autonomous
        can_proceed, level, _ = checker.can_decide(
            agent_name="awards_agent",
            decision_type="search_awards",
            confidence=0.9,
        )
        assert can_proceed is True
        assert level == DecisionLevel.AUTONOMOUS
    
    def test_programs_agent_budget_escalation(self):
        """Test Programs Agent budget escalation."""
        from agents.governance.decision_rights import DecisionRightsChecker, DecisionLevel
        
        checker = DecisionRightsChecker()
        
        can_proceed, level, _ = checker.can_decide(
            agent_name="programs_agent",
            decision_type="budget_exceeds_limit",
            confidence=1.0,
        )
        
        assert can_proceed is False
        assert level == DecisionLevel.HUMAN_ONLY


class TestEscalationProtocol:
    """Tests for Escalation Protocol (G3)."""
    
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
            context={"message": "My parents hit me"},
        )
        
        assert result["escalate"] is True
        assert result["level"] == EscalationLevel.IMMEDIATE
    
    def test_urgent_escalation_repeated_failure(self):
        """Test urgent escalation for repeated failures."""
        from agents.governance.escalation import EscalationProtocol, EscalationLevel
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="repeated_failure",
            context={"failure_count": 4},
        )
        
        assert result["escalate"] is True
        assert result["level"] in [EscalationLevel.URGENT, EscalationLevel.IMMEDIATE]
    
    def test_urgent_escalation_student_request(self):
        """Test escalation when student requests human."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="student_request",
            context={"request": "I want to talk to a real person"},
        )
        
        assert result["escalate"] is True
    
    def test_no_escalation_normal_operation(self):
        """Test no escalation for normal operations."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="task_completed",
            context={},
        )
        
        assert result["escalate"] is False
    
    def test_escalation_message_generation(self):
        """Test escalation message generation."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        message = protocol.generate_escalation_message(
            signal_type="crisis_detected",
            context={"student_name": "Test Student"},
        )
        
        assert len(message) > 0
    
    def test_escalation_with_context(self):
        """Test escalation includes context."""
        from agents.governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        
        result = protocol.should_escalate(
            signal_type="crisis_detected",
            context={"profile_id": "123", "severity": "high"},
        )
        
        assert result["escalate"] is True
        assert "context" in result or result.get("reason") is not None
