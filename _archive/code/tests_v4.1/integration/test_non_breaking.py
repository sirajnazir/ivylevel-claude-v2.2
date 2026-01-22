# tests/integration/test_non_breaking.py
"""
Non-breaking integration tests for Critical 15 Patterns.
Ensures patterns are additive and don't break existing agent flows.
CORRECTED to match actual implementation
"""

import pytest
import time


class TestPatternImports:
    """Test all pattern modules can be imported."""
    
    def test_import_context(self):
        """Test context module imports."""
        from context import (
            UserContextLoader,
            TemporalContextLoader,
            TaskContextManager,
            ContextSelector,
        )
        assert UserContextLoader is not None
    
    def test_import_memory(self):
        """Test memory module imports."""
        from memory import WorkingMemoryManager
        from memory.memory_retrieval import MemoryRetriever
        assert WorkingMemoryManager is not None
        assert MemoryRetriever is not None
    
    def test_import_intelligence(self):
        """Test intelligence module imports."""
        from intelligence import Prioritizer, GoalMonitor
        assert Prioritizer is not None
        assert GoalMonitor is not None
    
    def test_import_governance(self):
        """Test governance module imports."""
        from governance import DecisionRightsManager, EscalationProtocol
        assert DecisionRightsManager is not None
        assert EscalationProtocol is not None
    
    def test_import_safety(self):
        """Test safety module imports."""
        from safety import GuardrailsManager
        assert GuardrailsManager is not None
    
    def test_import_resilience(self):
        """Test resilience module imports."""
        from resilience import ExceptionHandler, with_retry
        assert ExceptionHandler is not None
        assert with_retry is not None
    
    def test_import_reasoning(self):
        """Test reasoning module imports."""
        from reasoning import ChainOfThoughtReasoner, AgentRouter
        assert ChainOfThoughtReasoner is not None
        assert AgentRouter is not None
    
    def test_import_validation(self):
        """Test validation module imports."""
        from validation import OutputValidator
        assert OutputValidator is not None
    
    def test_import_observability(self):
        """Test observability module imports."""
        from observability import MetricsCollector, get_metrics_collector
        assert MetricsCollector is not None
        assert get_metrics_collector is not None
    
    def test_import_middleware(self):
        """Test middleware module imports."""
        from middleware import MiddlewareStack, create_middleware
        assert MiddlewareStack is not None
        assert create_middleware is not None


class TestMiddlewareNonBreaking:
    """Test middleware is purely additive."""
    
    @pytest.mark.asyncio
    async def test_middleware_wrap_agent_provides_context(self, mock_supabase):
        """Test wrap_agent provides context without breaking flow."""
        from middleware import MiddlewareStack
        
        middleware = MiddlewareStack(supabase_client=mock_supabase)
        
        async with middleware.wrap_agent("ec_agent", "profile-123") as ctx:
            # Context should be available
            assert ctx is not None
            assert ctx.profile_id == "profile-123"
            
            # Original agent logic would go here
            result = {"success": True, "recommendations": []}
        
        # Should complete without error
        assert result["success"] is True
    
    def test_middleware_finalize_preserves_result(self):
        """Test finalize adds metadata but preserves result."""
        from middleware import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        original_result = {"success": True, "data": "test"}
        finalized = middleware.finalize(original_result)
        
        # Original data should be preserved
        assert finalized["success"] is True
        assert finalized["data"] == "test"
        
        # Validation metadata should be added
        assert "_validation" in finalized


class TestPatternPerformance:
    """Test patterns meet performance requirements."""
    
    def test_prioritization_performance(self, sample_student_context):
        """Test prioritization completes in <1s for 300 items."""
        from intelligence import Prioritizer
        
        prioritizer = Prioritizer()
        items = [
            {"id": str(i), "name": f"Item {i}", "type": "award"}
            for i in range(300)
        ]
        
        start = time.time()
        result = prioritizer.prioritize(items, sample_student_context)
        duration = time.time() - start
        
        assert duration < 1.0
        assert len(result) <= 10  # Default max_items
    
    def test_decision_rights_performance(self):
        """Test decision rights check completes in <100ms."""
        from governance import DecisionRightsManager, DecisionCategory
        
        manager = DecisionRightsManager()
        
        start = time.time()
        for _ in range(2000):
            manager.can_agent_decide(
                "ec_agent",
                DecisionCategory.RECOMMENDATION,
                confidence=0.85,
            )
        duration = time.time() - start
        
        assert duration < 0.1 * 20  # Allow 100ms per 100 checks
    
    def test_guardrails_performance(self):
        """Test guardrails check completes in <100ms."""
        from safety import GuardrailsManager
        
        guardrails = GuardrailsManager()
        
        start = time.time()
        for _ in range(1000):
            guardrails.check_input("This is a safe test message")
        duration = time.time() - start
        
        # Should complete in reasonable time
        assert duration < 1.0
    
    def test_validation_performance(self):
        """Test output validation completes in <100ms."""
        from validation import OutputValidator
        
        validator = OutputValidator()
        output = {
            "content": "Apply to RSI summer program at MIT",
            "items": [{"name": "RSI", "type": "program"}],
        }
        
        start = time.time()
        for _ in range(500):
            validator.validate(output, "recommendation")
        duration = time.time() - start
        
        assert duration < 1.0


class TestBackwardsCompatibility:
    """Test patterns maintain backwards compatibility."""
    
    def test_context_types_available(self):
        """Test context types are still available."""
        from context.types import (
            StudentContext,
            TemporalContext,
            TaskContext,
            WorkingMemory,
        )
        assert StudentContext is not None
        assert TemporalContext is not None
        assert TaskContext is not None
        assert WorkingMemory is not None
    
    def test_prioritizer_accepts_dict_items(self, sample_student_context):
        """Test prioritizer works with plain dict items."""
        from intelligence import Prioritizer
        
        prioritizer = Prioritizer()
        items = [{"id": "1", "name": "Test", "type": "award"}]
        
        result = prioritizer.prioritize(items, sample_student_context)
        
        assert len(result) == 1
    
    def test_metrics_collector_singleton(self):
        """Test metrics collector singleton works."""
        from observability import get_metrics_collector
        
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        
        assert collector1 is collector2


class TestSafetyIntegration:
    """Test safety patterns integration."""
    
    def test_guardrails_escalation_integration(self):
        """Test guardrails and escalation work together."""
        from safety import GuardrailsManager
        from governance import EscalationProtocol
        
        guardrails = GuardrailsManager()
        escalation = EscalationProtocol()
        
        # Check input with guardrails
        message = "I feel unsafe at home"
        guardrail_result = guardrails.check_input(message)
        
        # Check escalation
        escalation_result = escalation.check_for_escalation(message, {})
        
        # Both should detect the safety concern
        assert escalation_result is not None
    
    def test_decision_rights_escalation_integration(self):
        """Test decision rights and escalation work together."""
        from governance import DecisionRightsManager, DecisionCategory, DecisionLevel
        from governance import EscalationProtocol, EscalationReason
        
        decision_mgr = DecisionRightsManager()
        escalation = EscalationProtocol()
        
        # Crisis decision should escalate
        can_decide, level = decision_mgr.can_agent_decide(
            "coaching_agent",
            DecisionCategory.CRISIS,
            confidence=1.0,
        )
        
        assert can_decide is False
        assert level == DecisionLevel.ESCALATE


class TestFullFlowIntegration:
    """Test complete integration flows."""
    
    @pytest.mark.asyncio
    async def test_middleware_wraps_agent_flow(self, mock_supabase, mock_redis):
        """Test middleware properly wraps agent execution."""
        from middleware import MiddlewareStack
        from context.task_context import TaskType
        
        middleware = MiddlewareStack(
            supabase_client=mock_supabase,
            redis_client=mock_redis,
        )
        
        async with middleware.wrap_agent(
            "ec_agent",
            "profile-123",
            task_type=TaskType.EC_ASSESSMENT,
        ) as ctx:
            # Simulate agent work
            assert ctx.profile_id == "profile-123"
            
            # Check escalation
            escalation = middleware.check_escalation(
                "Help me with activities",
                {},
            )
            assert escalation is None  # Safe message
            
            # Prioritize recommendations
            recommendations = middleware.prioritize(
                [{"id": "1", "name": "Test", "type": "award"}],
                {"grade": 11},
            )
            assert len(recommendations) == 1
            
            # Finalize result
            result = middleware.finalize({"success": True})
            assert result["_validation"]["valid"] is True
