# tests/patterns/test_governance.py
"""
Tests for Governance patterns: G1 Decision Rights, G3 Escalation
CORRECTED to match actual implementation
"""

import pytest
from datetime import datetime


class TestDecisionRightsManager:
    """Tests for DecisionRightsManager (G1)."""
    
    def test_manager_importable(self):
        """Test DecisionRightsManager can be imported."""
        from governance.decision_rights import DecisionRightsManager
        assert DecisionRightsManager is not None
    
    def test_manager_initialization(self):
        """Test DecisionRightsManager can be initialized."""
        from governance.decision_rights import DecisionRightsManager
        manager = DecisionRightsManager()
        assert manager is not None
    
    def test_manager_with_custom_matrix(self):
        """Test DecisionRightsManager with custom rights matrix."""
        from governance.decision_rights import DecisionRightsManager, DecisionCategory, DecisionLevel
        
        custom_matrix = {
            DecisionCategory.RECOMMENDATION: {
                "default": DecisionLevel.SUPERVISED,
            },
        }
        manager = DecisionRightsManager(rights_matrix=custom_matrix)
        assert manager is not None
    
    def test_determine_decision_level(self):
        """Test determine_decision_level returns DecisionLevel."""
        from governance.decision_rights import DecisionRightsManager, DecisionCategory, DecisionLevel
        
        manager = DecisionRightsManager()
        level = manager.determine_decision_level(
            DecisionCategory.RECOMMENDATION,
            confidence=0.9,
        )
        
        assert isinstance(level, DecisionLevel)
    
    def test_determine_decision_level_high_confidence(self):
        """Test high confidence returns AUTONOMOUS."""
        from governance.decision_rights import DecisionRightsManager, DecisionCategory, DecisionLevel
        
        manager = DecisionRightsManager()
        level = manager.determine_decision_level(
            DecisionCategory.RECOMMENDATION,
            confidence=0.95,
        )
        
        assert level == DecisionLevel.AUTONOMOUS
    
    def test_determine_decision_level_low_confidence(self):
        """Test low confidence escalates."""
        from governance.decision_rights import DecisionRightsManager, DecisionCategory, DecisionLevel
        
        manager = DecisionRightsManager()
        level = manager.determine_decision_level(
            DecisionCategory.RECOMMENDATION,
            confidence=0.3,
        )
        
        # Low confidence should not be AUTONOMOUS
        assert level != DecisionLevel.AUTONOMOUS
    
    def test_determine_decision_level_with_context_factors(self):
        """Test context factors affect decision level."""
        from governance.decision_rights import DecisionRightsManager, DecisionCategory, DecisionLevel
        
        manager = DecisionRightsManager()
        level = manager.determine_decision_level(
            DecisionCategory.RECOMMENDATION,
            confidence=0.85,
            context_factors=["low_confidence"],
        )
        
        assert level == DecisionLevel.SUPERVISED
    
    def test_can_agent_decide_returns_tuple(self):
        """Test can_agent_decide returns tuple of (bool, DecisionLevel)."""
        from governance.decision_rights import DecisionRightsManager, DecisionCategory
        
        manager = DecisionRightsManager()
        result = manager.can_agent_decide(
            "ec_agent",
            DecisionCategory.RECOMMENDATION,
            confidence=0.9,
        )
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
    
    def test_can_agent_decide_high_confidence(self):
        """Test high confidence allows autonomous decision."""
        from governance.decision_rights import DecisionRightsManager, DecisionCategory, DecisionLevel
        
        manager = DecisionRightsManager()
        can_decide, level = manager.can_agent_decide(
            "ec_agent",
            DecisionCategory.RECOMMENDATION,
            confidence=0.95,
        )
        
        assert can_decide is True
        assert level == DecisionLevel.AUTONOMOUS
    
    def test_can_agent_decide_crisis_escalates(self):
        """Test crisis category always escalates."""
        from governance.decision_rights import DecisionRightsManager, DecisionCategory, DecisionLevel
        
        manager = DecisionRightsManager()
        can_decide, level = manager.can_agent_decide(
            "coaching_agent",
            DecisionCategory.CRISIS,
            confidence=1.0,
        )
        
        assert can_decide is False
        assert level == DecisionLevel.ESCALATE
    
    def test_request_approval(self):
        """Test request_approval creates pending decision."""
        from governance.decision_rights import DecisionRightsManager, Decision, DecisionCategory
        
        manager = DecisionRightsManager()
        decision = Decision(
            id="dec-1",
            category=DecisionCategory.RECOMMENDATION,
            description="Recommend RSI program",
            proposed_action="Add to gameplan",
            confidence=0.75,
            agent_name="programs_agent",
        )
        
        decision_id = manager.request_approval(decision)
        
        assert decision_id == "dec-1"
        assert len(manager.get_pending_decisions()) == 1
    
    def test_approve_decision(self):
        """Test approving a decision."""
        from governance.decision_rights import DecisionRightsManager, Decision, DecisionCategory
        
        manager = DecisionRightsManager()
        decision = Decision(
            id="dec-1",
            category=DecisionCategory.RECOMMENDATION,
            description="Test",
            proposed_action="Test action",
            confidence=0.75,
            agent_name="test_agent",
        )
        manager.request_approval(decision)
        
        approved = manager.approve_decision(
            "dec-1",
            approved_by="coach@ivyquest.com",
            approved=True,
            rationale="Looks good",
        )
        
        assert approved.approved is True
        assert approved.approved_by == "coach@ivyquest.com"


class TestDecisionLevel:
    """Tests for DecisionLevel enum."""
    
    def test_decision_level_values(self):
        """Test DecisionLevel has all expected values."""
        from governance.decision_rights import DecisionLevel
        
        assert DecisionLevel.AUTONOMOUS.value == "autonomous"
        assert DecisionLevel.SUPERVISED.value == "supervised"
        assert DecisionLevel.COLLABORATIVE.value == "collaborative"
        assert DecisionLevel.ESCALATE.value == "escalate"


class TestDecisionCategory:
    """Tests for DecisionCategory enum."""
    
    def test_decision_category_values(self):
        """Test DecisionCategory has all expected values."""
        from governance.decision_rights import DecisionCategory
        
        assert DecisionCategory.RECOMMENDATION.value == "recommendation"
        assert DecisionCategory.ASSESSMENT.value == "assessment"
        assert DecisionCategory.COMMUNICATION.value == "communication"
        assert DecisionCategory.PRIORITIZATION.value == "prioritization"
        assert DecisionCategory.DEADLINE.value == "deadline"
        assert DecisionCategory.CRISIS.value == "crisis"
        assert DecisionCategory.DATA_CHANGE.value == "data_change"


class TestDecisionModel:
    """Tests for Decision model."""
    
    def test_decision_creation(self):
        """Test creating a Decision."""
        from governance.decision_rights import Decision, DecisionCategory
        
        decision = Decision(
            id="dec-1",
            category=DecisionCategory.RECOMMENDATION,
            description="Recommend summer program",
            proposed_action="Add RSI to gameplan",
            confidence=0.85,
            agent_name="programs_agent",
        )
        
        assert decision.id == "dec-1"
        assert decision.confidence == 0.85
        assert decision.requires_approval is False


class TestConvenienceFunction:
    """Tests for check_decision_rights convenience function."""
    
    def test_check_decision_rights_exists(self):
        """Test convenience function exists."""
        from governance.decision_rights import check_decision_rights
        assert check_decision_rights is not None
    
    def test_check_decision_rights_returns_tuple(self):
        """Test convenience function returns expected tuple."""
        from governance.decision_rights import check_decision_rights, DecisionCategory
        
        can_decide, level, factors = check_decision_rights(
            "ec_agent",
            DecisionCategory.RECOMMENDATION,
            confidence=0.9,
            context={},
        )
        
        assert isinstance(can_decide, bool)
        assert isinstance(factors, list)


class TestEscalationProtocol:
    """Tests for EscalationProtocol (G3)."""
    
    def test_protocol_importable(self):
        """Test EscalationProtocol can be imported."""
        from governance.escalation import EscalationProtocol
        assert EscalationProtocol is not None
    
    def test_protocol_initialization(self):
        """Test EscalationProtocol can be initialized."""
        from governance.escalation import EscalationProtocol
        protocol = EscalationProtocol()
        assert protocol is not None
    
    def test_check_for_escalation_no_trigger(self):
        """Test check_for_escalation returns None for safe message."""
        from governance.escalation import EscalationProtocol
        
        protocol = EscalationProtocol()
        result = protocol.check_for_escalation(
            "Can you help me with my essay?",
            {},
        )
        
        assert result is None
    
    def test_check_for_escalation_safety_concern(self):
        """Test check_for_escalation detects safety keywords."""
        from governance.escalation import EscalationProtocol, EscalationReason, EscalationLevel
        
        protocol = EscalationProtocol()
        result = protocol.check_for_escalation(
            "I feel unsafe at home",
            {},
        )
        
        assert result is not None
        reason, level = result
        assert reason == EscalationReason.SAFETY_CONCERN
        assert level == EscalationLevel.EMERGENCY
    
    def test_check_for_escalation_distress(self):
        """Test check_for_escalation detects distress keywords."""
        from governance.escalation import EscalationProtocol, EscalationReason, EscalationLevel
        
        protocol = EscalationProtocol()
        result = protocol.check_for_escalation(
            "I feel depressed about college rejections",
            {},
        )
        
        assert result is not None
        reason, level = result
        assert reason == EscalationReason.STUDENT_DISTRESS
        assert level == EscalationLevel.HUMAN_SYNC
    
    def test_check_for_escalation_out_of_scope(self):
        """Test check_for_escalation detects out of scope topics."""
        from governance.escalation import EscalationProtocol, EscalationReason
        
        protocol = EscalationProtocol()
        result = protocol.check_for_escalation(
            "Can you give me medical advice about my anxiety?",
            {},
        )
        
        assert result is not None
        reason, level = result
        assert reason == EscalationReason.OUT_OF_SCOPE
    
    def test_escalate_creates_escalation(self):
        """Test escalate creates an Escalation object."""
        from governance.escalation import EscalationProtocol, EscalationReason, Escalation
        
        protocol = EscalationProtocol()
        escalation = protocol.escalate(
            agent_name="coaching_agent",
            profile_id="profile-123",
            reason=EscalationReason.STUDENT_DISTRESS,
            description="Student expressed feelings of hopelessness",
        )
        
        assert isinstance(escalation, Escalation)
        assert escalation.agent_name == "coaching_agent"
        assert escalation.reason == EscalationReason.STUDENT_DISTRESS
        assert escalation.resolved is False
    
    def test_resolve_escalation(self):
        """Test resolving an escalation."""
        from governance.escalation import EscalationProtocol, EscalationReason
        
        protocol = EscalationProtocol()
        escalation = protocol.escalate(
            agent_name="coaching_agent",
            profile_id="profile-123",
            reason=EscalationReason.STUDENT_DISTRESS,
            description="Test",
        )
        
        resolved = protocol.resolve(
            escalation.id,
            resolved_by="coach@ivyquest.com",
            resolution="Contacted student and parent",
        )
        
        assert resolved.resolved is True
        assert resolved.resolved_by == "coach@ivyquest.com"
    
    def test_get_pending_escalations(self):
        """Test getting pending escalations."""
        from governance.escalation import EscalationProtocol, EscalationReason
        
        protocol = EscalationProtocol()
        protocol.escalate("agent1", "profile1", EscalationReason.LOW_CONFIDENCE, "Test 1")
        protocol.escalate("agent2", "profile2", EscalationReason.OUT_OF_SCOPE, "Test 2")
        
        pending = protocol.get_pending()
        
        assert len(pending) == 2


class TestEscalationLevel:
    """Tests for EscalationLevel enum."""
    
    def test_escalation_level_values(self):
        """Test EscalationLevel has all expected values."""
        from governance.escalation import EscalationLevel
        
        assert EscalationLevel.NONE.value == "none"
        assert EscalationLevel.SUPERVISOR.value == "supervisor"
        assert EscalationLevel.HUMAN_ASYNC.value == "human_async"
        assert EscalationLevel.HUMAN_SYNC.value == "human_sync"
        assert EscalationLevel.EMERGENCY.value == "emergency"


class TestEscalationReason:
    """Tests for EscalationReason enum."""
    
    def test_escalation_reason_values(self):
        """Test EscalationReason has expected values."""
        from governance.escalation import EscalationReason
        
        assert EscalationReason.LOW_CONFIDENCE.value == "low_confidence"
        assert EscalationReason.STUDENT_DISTRESS.value == "student_distress"
        assert EscalationReason.SAFETY_CONCERN.value == "safety_concern"
        assert EscalationReason.OUT_OF_SCOPE.value == "out_of_scope"


class TestSafetyResponse:
    """Tests for SafetyResponse class."""
    
    def test_safety_response_importable(self):
        """Test SafetyResponse can be imported."""
        from governance.escalation import SafetyResponse
        assert SafetyResponse is not None
    
    def test_get_response_safety_concern(self):
        """Test get_response for safety concern."""
        from governance.escalation import SafetyResponse, EscalationReason
        
        response = SafetyResponse.get_response(EscalationReason.SAFETY_CONCERN)
        
        assert response is not None
        assert "safety" in response.lower() or "help" in response.lower()
    
    def test_get_response_distress(self):
        """Test get_response for student distress."""
        from governance.escalation import SafetyResponse, EscalationReason
        
        response = SafetyResponse.get_response(EscalationReason.STUDENT_DISTRESS)
        
        assert response is not None
        assert len(response) > 0
