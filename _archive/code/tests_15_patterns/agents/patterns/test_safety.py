# tests/agents/patterns/test_safety.py
"""
Tests for Safety patterns: E6 Guardrails
CRITICAL: These protect students (minors) - must have 100% pass rate.
"""

import pytest


class TestCoachingGuardrail:
    """Tests for Coaching Guardrail (E6)."""
    
    def test_safe_input_passes(self):
        """Test that normal input passes."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, concern, action = CoachingGuardrail.check_input(
            "Can you help me with my MIT essay?"
        )
        
        assert is_safe is True
        assert concern is None
    
    def test_self_harm_detection(self):
        """Test detection of self-harm signals - CRITICAL."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, concern, action = CoachingGuardrail.check_input(
            "I feel like hurting myself because of rejections"
        )
        
        assert is_safe is False
        assert concern == "escalation_required"
        assert action is not None
    
    def test_suicide_mention_detection(self):
        """Test detection of suicide mentions - CRITICAL."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, concern, action = CoachingGuardrail.check_input(
            "Sometimes I feel suicidal when I think about college"
        )
        
        assert is_safe is False
        assert concern == "escalation_required"
    
    def test_abuse_signal_detection(self):
        """Test detection of abuse signals - CRITICAL."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, concern, action = CoachingGuardrail.check_input(
            "My parents are abusive about my grades"
        )
        
        assert is_safe is False
        assert concern == "escalation_required"
    
    def test_safe_output_passes(self):
        """Test that appropriate output passes."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "Based on your profile, MIT could be a great fit. Let's work on strengthening your application."
        )
        
        assert is_safe is True
        assert violation is None
    
    def test_guarantee_language_blocked(self):
        """Test detection of guarantee language in output."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "You will definitely get into Harvard!"
        )
        
        assert is_safe is False
        assert violation is not None
    
    def test_certainty_language_blocked(self):
        """Test detection of 100% certainty language."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "You are 100% guaranteed admission to Stanford!"
        )
        
        assert is_safe is False
    
    def test_negative_school_language_blocked(self):
        """Test detection of negative school comments."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "That's a terrible school, don't apply there."
        )
        
        assert is_safe is False
    
    def test_diagnosis_language_blocked(self):
        """Test detection of diagnosis language."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "Based on what you've told me, you are depressed."
        )
        
        assert is_safe is False
    
    def test_adhd_diagnosis_blocked(self):
        """Test detection of ADHD diagnosis."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "You clearly have ADHD based on your symptoms."
        )
        
        assert is_safe is False
    
    def test_anxiety_diagnosis_blocked(self):
        """Test detection of anxiety diagnosis."""
        from agents.safety.guardrails import CoachingGuardrail
        
        is_safe, violation, corrected = CoachingGuardrail.check_output(
            "You are anxious and need medication."
        )
        
        assert is_safe is False


class TestGuardrailsManager:
    """Tests for GuardrailsManager integration."""
    
    @pytest.mark.asyncio
    async def test_validate_safe_input(self):
        """Test validation of safe input."""
        from agents.safety.guardrails import GuardrailsManager
        
        manager = GuardrailsManager()
        
        result = await manager.validate_input("Help me plan my summer activities")
        
        assert result["is_safe"] is True
        assert result["action"] == "proceed"
    
    @pytest.mark.asyncio
    async def test_validate_dangerous_input_escalates(self):
        """Test validation escalates dangerous input."""
        from agents.safety.guardrails import GuardrailsManager
        
        manager = GuardrailsManager()
        
        result = await manager.validate_input("I want to kill myself")
        
        assert result["is_safe"] is False
        assert result["action"] == "escalate"
    
    @pytest.mark.asyncio
    async def test_validate_safe_output(self):
        """Test validation of safe output."""
        from agents.safety.guardrails import GuardrailsManager
        
        manager = GuardrailsManager()
        
        result = await manager.validate_output(
            "Here are some activities that align with your interests."
        )
        
        assert result["is_safe"] is True
    
    @pytest.mark.asyncio
    async def test_validate_output_flags_violations(self):
        """Test that unsafe output gets flagged."""
        from agents.safety.guardrails import GuardrailsManager
        
        manager = GuardrailsManager()
        
        result = await manager.validate_output(
            "You will 100% get into Stanford!"
        )
        
        # Should flag the guarantee language
        assert result["is_safe"] is False or len(result["violations"]) > 0
    
    @pytest.mark.asyncio
    async def test_empty_input_safe(self):
        """Test that empty input is handled."""
        from agents.safety.guardrails import GuardrailsManager
        
        manager = GuardrailsManager()
        
        result = await manager.validate_input("")
        
        # Empty should be safe (no triggers)
        assert result["is_safe"] is True
    
    @pytest.mark.asyncio
    async def test_normal_frustration_not_flagged(self):
        """Test that normal frustration is not flagged as crisis."""
        from agents.safety.guardrails import GuardrailsManager
        
        manager = GuardrailsManager()
        
        result = await manager.validate_input(
            "I'm so frustrated with this essay! It's driving me crazy!"
        )
        
        # Normal frustration should not trigger escalation
        assert result["action"] != "escalate"
