# tests/agents/patterns/test_safety.py
"""
Tests for Safety patterns: E6 Guardrails
CRITICAL - These protect students (minors)
"""

import pytest


class TestCoachingGuardrail:
    """Tests for CoachingGuardrail (E6)."""
    
    def test_coaching_guardrail_importable(self):
        """Test CoachingGuardrail can be imported."""
        from agents.safety.guardrails import CoachingGuardrail
        assert CoachingGuardrail is not None
    
    def test_check_input_exists(self):
        """Test check_input method exists."""
        from agents.safety.guardrails import CoachingGuardrail
        assert hasattr(CoachingGuardrail, 'check_input')
    
    def test_check_output_exists(self):
        """Test check_output method exists."""
        from agents.safety.guardrails import CoachingGuardrail
        assert hasattr(CoachingGuardrail, 'check_output')
    
    def test_safe_input_passes(self):
        """Test normal input passes."""
        from agents.safety.guardrails import CoachingGuardrail
        is_safe, concern, action = CoachingGuardrail.check_input(
            "Can you help me with my MIT essay?"
        )
        assert is_safe is True
    
    def test_self_harm_detected(self):
        """Test self-harm detection - CRITICAL."""
        from agents.safety.guardrails import CoachingGuardrail
        is_safe, concern, action = CoachingGuardrail.check_input(
            "I feel like hurting myself because of rejections"
        )
        assert is_safe is False
        assert concern == "escalation_required"
    
    def test_suicide_detected(self):
        """Test suicide mention detection - CRITICAL."""
        from agents.safety.guardrails import CoachingGuardrail
        is_safe, concern, action = CoachingGuardrail.check_input(
            "Sometimes I feel suicidal when I think about college"
        )
        assert is_safe is False
        assert concern == "escalation_required"
    
    def test_abuse_detected(self):
        """Test abuse signal detection - CRITICAL."""
        from agents.safety.guardrails import CoachingGuardrail
        is_safe, concern, action = CoachingGuardrail.check_input(
            "My parents are abusive about my grades"
        )
        assert is_safe is False
        assert concern == "escalation_required"
    
    def test_safe_output_passes(self):
        """Test appropriate output passes."""
        from agents.safety.guardrails import CoachingGuardrail
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "Based on your profile, MIT could be a great fit."
        )
        assert is_safe is True
    
    def test_guarantee_blocked(self):
        """Test guarantee language blocked."""
        from agents.safety.guardrails import CoachingGuardrail
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "You will definitely get into Harvard!"
        )
        assert is_safe is False
    
    def test_negative_school_blocked(self):
        """Test negative school comments blocked."""
        from agents.safety.guardrails import CoachingGuardrail
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "That's a terrible school, don't apply there."
        )
        assert is_safe is False
    
    def test_diagnosis_blocked(self):
        """Test diagnosis language blocked."""
        from agents.safety.guardrails import CoachingGuardrail
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "Based on what you've told me, you are depressed."
        )
        assert is_safe is False


class TestGuardrailsManager:
    """Tests for GuardrailsManager."""
    
    def test_manager_importable(self):
        """Test GuardrailsManager can be imported."""
        from agents.safety.guardrails import GuardrailsManager
        assert GuardrailsManager is not None
    
    def test_manager_initialization(self):
        """Test GuardrailsManager can be initialized."""
        from agents.safety.guardrails import GuardrailsManager
        manager = GuardrailsManager()
        assert manager is not None
    
    def test_manager_has_validate_input(self):
        """Test GuardrailsManager has validate_input method."""
        from agents.safety.guardrails import GuardrailsManager
        manager = GuardrailsManager()
        assert hasattr(manager, 'validate_input')
    
    def test_manager_has_validate_output(self):
        """Test GuardrailsManager has validate_output method."""
        from agents.safety.guardrails import GuardrailsManager
        manager = GuardrailsManager()
        assert hasattr(manager, 'validate_output')
    
    @pytest.mark.asyncio
    async def test_validate_input_safe(self):
        """Test validation of safe input."""
        from agents.safety.guardrails import GuardrailsManager
        manager = GuardrailsManager()
        result = await manager.validate_input("Help me plan my summer activities")
        assert result["is_safe"] is True
        assert result["action"] == "proceed"
    
    @pytest.mark.asyncio
    async def test_validate_input_dangerous(self):
        """Test validation escalates dangerous input."""
        from agents.safety.guardrails import GuardrailsManager
        manager = GuardrailsManager()
        result = await manager.validate_input("I want to kill myself")
        assert result["is_safe"] is False
        assert result["action"] == "escalate"
    
    @pytest.mark.asyncio
    async def test_validate_output_safe(self):
        """Test validation of safe output."""
        from agents.safety.guardrails import GuardrailsManager
        manager = GuardrailsManager()
        result = await manager.validate_output(
            "Here are some activities that align with your interests."
        )
        assert result["is_safe"] is True
    
    @pytest.mark.asyncio
    async def test_validate_empty_safe(self):
        """Test empty input is safe."""
        from agents.safety.guardrails import GuardrailsManager
        manager = GuardrailsManager()
        result = await manager.validate_input("")
        assert result["is_safe"] is True
    
    @pytest.mark.asyncio
    async def test_normal_frustration_not_flagged(self):
        """Test normal frustration is not flagged."""
        from agents.safety.guardrails import GuardrailsManager
        manager = GuardrailsManager()
        result = await manager.validate_input(
            "I'm so frustrated with this essay! It's driving me crazy!"
        )
        assert result["action"] != "escalate"
