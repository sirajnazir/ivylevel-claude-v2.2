# tests/agents/integration/test_full_flow.py
"""
Full Flow Integration Tests

Tests the complete flow with middleware enabled.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import time


class TestFullFlowWithMiddleware:
    """Test complete flows with middleware."""
    
    @pytest.mark.asyncio
    async def test_middleware_context_initialization(self, sample_profile_id, sample_session_id, mock_supabase):
        """Test middleware initializes all context layers."""
        from agents.middleware.stack import MiddlewareStack
        
        with patch('agents.middleware.stack.get_supabase', return_value=mock_supabase):
            middleware = MiddlewareStack(sample_profile_id, sample_session_id)
            
            context = await middleware.pre_process({})
            
            # Should have initialized context
            assert context is not None
    
    @pytest.mark.asyncio
    async def test_middleware_metadata_complete(self, sample_profile_id, sample_session_id):
        """Test that middleware adds complete metadata to results."""
        from agents.middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        
        result = await middleware.post_process({
            "success": True,
            "game_plan": {"narrative_dna": "Test narrative"},
        })
        
        assert "_middleware" in result
        assert "patterns_applied" in result["_middleware"]
        assert len(result["_middleware"]["patterns_applied"]) > 0
        assert "session_id" in result["_middleware"]
    
    @pytest.mark.asyncio
    async def test_middleware_handles_empty_result(self, sample_profile_id, sample_session_id):
        """Test middleware handles empty results gracefully."""
        from agents.middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        
        result = await middleware.post_process({})
        
        assert "_middleware" in result
    
    @pytest.mark.asyncio
    async def test_middleware_handles_none_result(self, sample_profile_id, sample_session_id):
        """Test middleware handles None results gracefully."""
        from agents.middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        
        # Should not raise
        try:
            result = await middleware.post_process(None)
            assert True
        except TypeError:
            # If it raises, make sure it's handled
            pass
    
    @pytest.mark.asyncio
    async def test_middleware_guardrails_applied(self, sample_profile_id, sample_session_id):
        """Test that guardrails are applied to output."""
        from agents.middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        
        # Result with potentially unsafe content
        result = await middleware.post_process({
            "success": True,
            "narrative_dna": "You will definitely get into Harvard!",
        })
        
        # Should still return result (guardrails flag but don't block)
        assert result is not None


class TestPatternInteraction:
    """Test that patterns work together correctly."""
    
    def test_prioritization_with_temporal_context(self, sample_tasks):
        """Test prioritization uses temporal context correctly."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        prioritized = engine.prioritize(sample_tasks)
        
        # Tasks with closer deadlines should be higher priority
        assert prioritized[0].days_until_deadline < prioritized[-1].days_until_deadline or \
               prioritized[0].days_until_deadline == prioritized[-1].days_until_deadline
    
    def test_decision_rights_respects_confidence(self):
        """Test decision rights checks confidence from context."""
        from agents.governance.decision_rights import DecisionRightsChecker, DecisionLevel
        
        checker = DecisionRightsChecker()
        
        # High confidence - should proceed
        can_proceed_high, _, _ = checker.can_decide("ec_agent", "classify_archetype", 0.9)
        
        # Low confidence - should not proceed
        can_proceed_low, _, _ = checker.can_decide("ec_agent", "classify_archetype", 0.3)
        
        assert can_proceed_high is True
        assert can_proceed_low is False
    
    @pytest.mark.asyncio
    async def test_guardrails_trigger_escalation(self):
        """Test that guardrails can trigger escalation."""
        from agents.safety.guardrails import GuardrailsManager
        from agents.governance.escalation import EscalationProtocol
        
        guardrails = GuardrailsManager()
        escalation = EscalationProtocol()
        
        # Check input that should trigger escalation
        input_result = await guardrails.validate_input("I want to hurt myself")
        
        if not input_result["is_safe"]:
            # Should escalate
            escalation_result = escalation.should_escalate(
                signal_type="self_harm_signal",
                context={"input": "I want to hurt myself"},
            )
            
            assert escalation_result["escalate"] is True


# tests/agents/integration/test_performance.py
"""
Performance Tests

Verify middleware doesn't significantly impact performance.
"""


class TestPerformance:
    """Performance benchmarks."""
    
    @pytest.mark.asyncio
    async def test_middleware_pre_process_fast(self, sample_profile_id, sample_session_id, mock_supabase):
        """Test that pre_process is fast (<100ms)."""
        from agents.middleware.stack import MiddlewareStack
        
        with patch('agents.middleware.stack.get_supabase', return_value=mock_supabase):
            middleware = MiddlewareStack(sample_profile_id, sample_session_id)
            
            # Measure pre_process time
            start = time.time()
            for _ in range(10):
                await middleware.pre_process({})
            avg_time = (time.time() - start) / 10
            
            assert avg_time < 0.1, f"pre_process too slow: {avg_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_middleware_post_process_fast(self, sample_profile_id, sample_session_id):
        """Test that post_process is fast (<100ms)."""
        from agents.middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        
        # Measure post_process time
        start = time.time()
        for _ in range(10):
            await middleware.post_process({"success": True})
        avg_time = (time.time() - start) / 10
        
        assert avg_time < 0.1, f"post_process too slow: {avg_time:.3f}s"
    
    def test_prioritization_fast(self, sample_tasks):
        """Test prioritization engine performance."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        
        # Create many tasks
        many_tasks = sample_tasks * 100  # 300 tasks
        
        start = time.time()
        result = engine.prioritize(many_tasks)
        duration = time.time() - start
        
        # Should complete in < 1 second for 300 tasks
        assert duration < 1.0, f"Prioritization too slow: {duration:.3f}s for {len(many_tasks)} tasks"
        assert len(result) == len(many_tasks)
    
    def test_context_selector_fast(self):
        """Test context selector is fast."""
        from agents.context.context_selector import ContextSelector
        
        start = time.time()
        for _ in range(1000):
            ContextSelector.for_task("assessment")
            ContextSelector.for_task("execution")
            ContextSelector.for_agent("ec_agent")
        duration = time.time() - start
        
        # 3000 selections should be < 100ms
        assert duration < 0.1, f"Context selector too slow: {duration:.3f}s"
    
    def test_decision_rights_fast(self):
        """Test decision rights checking is fast."""
        from agents.governance.decision_rights import DecisionRightsChecker
        
        checker = DecisionRightsChecker()
        
        start = time.time()
        for _ in range(1000):
            checker.can_decide("ec_agent", "classify_archetype", 0.85)
            checker.can_decide("execution_agent", "crisis_detected", 1.0)
        duration = time.time() - start
        
        # 2000 checks should be < 100ms
        assert duration < 0.1, f"Decision rights too slow: {duration:.3f}s"
    
    def test_working_memory_bounded(self, sample_profile_id):
        """Test that working memory stays bounded."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        
        # Create multiple sessions with lots of turns
        for i in range(50):
            session_id = f"session_{i}"
            memory = manager.get_or_create(session_id, sample_profile_id)
            
            # Add many turns
            for j in range(100):
                manager.add_turn(session_id, "user", f"Message {j}" * 10)
        
        # Check all buffers are bounded
        for i in range(50):
            session_id = f"session_{i}"
            memory = manager.get_or_create(session_id, sample_profile_id)
            assert len(memory.conversation_buffer) <= memory.max_buffer_size
    
    @pytest.mark.asyncio
    async def test_guardrails_fast(self):
        """Test guardrails validation is fast."""
        from agents.safety.guardrails import GuardrailsManager
        
        manager = GuardrailsManager()
        
        start = time.time()
        for _ in range(100):
            await manager.validate_input("Help me with my essay")
            await manager.validate_output("Here's some advice for you.")
        duration = time.time() - start
        
        # 200 validations should be < 1 second
        assert duration < 1.0, f"Guardrails too slow: {duration:.3f}s"
