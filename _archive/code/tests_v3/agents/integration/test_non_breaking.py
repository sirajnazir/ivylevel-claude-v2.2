# tests/agents/integration/test_non_breaking.py
"""
Non-Breaking Integration Tests
FINAL VERSION
"""

import pytest


class TestAllModulesImportable:
    """Verify all modules can be imported."""
    
    def test_context_types(self):
        from agents.context.types import StudentContext, ContextSelection
        assert StudentContext is not None
    
    def test_context_user(self):
        from agents.context.user_context import UserContextLoader
        assert UserContextLoader is not None
    
    def test_context_temporal(self):
        from agents.context.temporal_context import TemporalContextLoader
        assert TemporalContextLoader is not None
    
    def test_context_task(self):
        from agents.context.task_context import TaskContextManager
        assert TaskContextManager is not None
    
    def test_context_selector(self):
        from agents.context.context_selector import ContextSelector
        assert ContextSelector is not None
    
    def test_memory_working(self):
        from agents.memory.working_memory import WorkingMemoryManager
        assert WorkingMemoryManager is not None
    
    def test_intelligence_prioritization(self):
        from agents.intelligence.prioritization import PrioritizationEngine
        assert PrioritizationEngine is not None
    
    def test_intelligence_goal_monitoring(self):
        from agents.intelligence.goal_monitoring import GoalMonitor
        assert GoalMonitor is not None
    
    def test_governance_decision_rights(self):
        from agents.governance.decision_rights import DecisionRightsChecker
        assert DecisionRightsChecker is not None
    
    def test_governance_escalation(self):
        from agents.governance.escalation import EscalationProtocol
        assert EscalationProtocol is not None
    
    def test_safety_guardrails(self):
        from agents.safety.guardrails import GuardrailsManager
        assert GuardrailsManager is not None
    
    def test_resilience_exception_handling(self):
        from agents.resilience.exception_handling import ExceptionHandler
        assert ExceptionHandler is not None
    
    def test_observability_metrics(self):
        from agents.observability.metrics import MetricsTracker
        assert MetricsTracker is not None
    
    def test_middleware_stack(self):
        from agents.middleware.stack import MiddlewareStack
        assert MiddlewareStack is not None


class TestMiddlewareAdditive:
    """Verify middleware is purely additive."""
    
    def test_middleware_initialization(self, sample_profile_id, sample_session_id):
        from agents.middleware.stack import MiddlewareStack
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        assert middleware is not None
    
    @pytest.mark.asyncio
    async def test_middleware_preserves_result(self, sample_profile_id, sample_session_id):
        from agents.middleware.stack import MiddlewareStack
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        original = {"success": True, "data": "test"}
        result = await middleware.post_process(original)
        assert result["success"] is True
        assert result["data"] == "test"


# tests/agents/integration/test_performance.py
"""
Performance Tests
FINAL VERSION
"""

import time


class TestPerformance:
    """Performance benchmarks."""
    
    def test_prioritization_fast(self, sample_tasks):
        from agents.intelligence.prioritization import PrioritizationEngine
        engine = PrioritizationEngine()
        many_tasks = sample_tasks * 100
        start = time.time()
        result = engine.prioritize(many_tasks)
        duration = time.time() - start
        assert duration < 1.0
        assert len(result) == len(many_tasks)
    
    def test_context_selector_fast(self):
        from agents.context.context_selector import ContextSelector
        start = time.time()
        for _ in range(1000):
            ContextSelector.for_task("assessment")
            ContextSelector.for_agent("ec_agent")
        duration = time.time() - start
        assert duration < 0.1
    
    def test_decision_rights_fast(self):
        from agents.governance.decision_rights import DecisionRightsChecker
        checker = DecisionRightsChecker()
        start = time.time()
        for _ in range(1000):
            checker.can_decide("ec_agent", "classify_archetype", 0.85)
        duration = time.time() - start
        assert duration < 0.1
    
    def test_working_memory_bounded(self, sample_profile_id):
        from agents.memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager()
        for i in range(50):
            session_id = f"session_{i}"
            memory = manager.get_or_create(session_id, sample_profile_id)
            for j in range(100):
                manager.add_turn(session_id, "user", f"Message {j}")
        for i in range(50):
            session_id = f"session_{i}"
            memory = manager.get_or_create(session_id, sample_profile_id)
            assert len(memory.conversation_buffer) <= memory.max_buffer_size
