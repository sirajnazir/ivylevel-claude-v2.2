# tests/agents/integration/test_performance.py
"""
Performance Tests

Verify middleware doesn't significantly impact performance.
"""

import pytest
import time
from unittest.mock import patch


class TestPerformance:
    """Performance benchmarks."""
    
    @pytest.mark.asyncio
    async def test_middleware_pre_process_fast(self, sample_profile_id, sample_session_id, mock_supabase):
        """Test that pre_process is fast (<100ms)."""
        from agents.middleware.stack import MiddlewareStack
        
        with patch('agents.middleware.stack.get_supabase', return_value=mock_supabase):
            middleware = MiddlewareStack(sample_profile_id, sample_session_id)
            
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
        
        start = time.time()
        for _ in range(10):
            await middleware.post_process({"success": True})
        avg_time = (time.time() - start) / 10
        
        assert avg_time < 0.1, f"post_process too slow: {avg_time:.3f}s"
    
    def test_prioritization_fast(self, sample_tasks):
        """Test prioritization engine performance."""
        from agents.intelligence.prioritization import PrioritizationEngine
        
        engine = PrioritizationEngine()
        many_tasks = sample_tasks * 100  # 300 tasks
        
        start = time.time()
        result = engine.prioritize(many_tasks)
        duration = time.time() - start
        
        assert duration < 1.0, f"Prioritization too slow: {duration:.3f}s"
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
        
        assert duration < 0.1, f"Decision rights too slow: {duration:.3f}s"
    
    def test_working_memory_bounded(self, sample_profile_id):
        """Test that working memory stays bounded."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        
        for i in range(50):
            session_id = f"session_{i}"
            memory = manager.get_or_create(session_id, sample_profile_id)
            
            for j in range(100):
                manager.add_turn(session_id, "user", f"Message {j}" * 10)
        
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
        
        assert duration < 1.0, f"Guardrails too slow: {duration:.3f}s"
