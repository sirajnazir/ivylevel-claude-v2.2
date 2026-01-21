# tests/agents/integration/test_non_breaking.py
"""
Non-Breaking Integration Tests

CRITICAL: These tests verify that existing flows still work after adding patterns.
All tests here MUST pass before deploying.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestExistingFlowsUnchanged:
    """Verify existing agent flows are not broken."""
    
    def test_ec_agent_importable(self):
        """Test EC Agent can be imported."""
        try:
            from agents.agents.extracurriculars import ExtracurricularsAgent
            assert True
        except ImportError as e:
            pytest.fail(f"EC Agent import failed: {e}")
    
    def test_ec_agent_has_process(self):
        """Test EC Agent has process method."""
        from agents.agents.extracurriculars import ExtracurricularsAgent
        
        agent = ExtracurricularsAgent()
        
        assert hasattr(agent, 'process')
        assert callable(agent.process)
    
    def test_awards_agent_importable(self):
        """Test Awards Agent can be imported."""
        try:
            from agents.agents.awards import AwardsAgent
            assert True
        except ImportError as e:
            pytest.fail(f"Awards Agent import failed: {e}")
    
    def test_awards_agent_has_process(self):
        """Test Awards Agent has process method."""
        from agents.agents.awards import AwardsAgent
        
        agent = AwardsAgent()
        
        assert hasattr(agent, 'process')
        assert callable(agent.process)
    
    def test_programs_agent_importable(self):
        """Test Programs Agent can be imported."""
        try:
            from agents.agents.programs import ProgramsAgent
            assert True
        except ImportError as e:
            pytest.fail(f"Programs Agent import failed: {e}")
    
    def test_programs_agent_has_process(self):
        """Test Programs Agent has process method."""
        from agents.agents.programs import ProgramsAgent
        
        agent = ProgramsAgent()
        
        assert hasattr(agent, 'process')
        assert callable(agent.process)
    
    def test_react_wrapper_importable(self):
        """Test ReAct wrapper can be imported."""
        try:
            from agents.agents.core.react_wrapper import ReactWrapper
            assert True
        except ImportError as e:
            pytest.fail(f"ReactWrapper import failed: {e}")
    
    def test_react_wrapper_has_wrap(self):
        """Test ReAct wrapper has wrap method."""
        from agents.agents.core.react_wrapper import ReactWrapper
        
        assert hasattr(ReactWrapper, 'wrap') or hasattr(ReactWrapper, '__call__')
    
    def test_gameplan_orchestrator_importable(self):
        """Test GamePlan orchestrator can be imported."""
        try:
            from agents.agents.gameplan import GamePlanOrchestrator
            assert True
        except ImportError as e:
            pytest.fail(f"GamePlan import failed: {e}")
    
    def test_gameplan_orchestrator_has_orchestrate(self):
        """Test GamePlan orchestrator has orchestrate method."""
        from agents.agents.gameplan import GamePlanOrchestrator
        
        orchestrator = GamePlanOrchestrator()
        
        assert hasattr(orchestrator, 'orchestrate')


class TestMiddlewareIsAdditive:
    """Verify middleware is purely additive and doesn't break existing code."""
    
    def test_middleware_import_succeeds(self):
        """Test that middleware import doesn't break existing code."""
        try:
            from agents.middleware.stack import MiddlewareStack
            assert True
        except ImportError as e:
            pytest.fail(f"Middleware import failed: {e}")
    
    def test_middleware_initialization(self, sample_profile_id, sample_session_id):
        """Test middleware can be initialized."""
        from agents.middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        
        assert middleware.profile_id == sample_profile_id
    
    def test_context_modules_importable(self):
        """Test all context modules can be imported."""
        modules = [
            "agents.context.types",
            "agents.context.user_context",
            "agents.context.temporal_context",
            "agents.context.task_context",
            "agents.context.context_selector",
        ]
        
        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")
    
    def test_memory_modules_importable(self):
        """Test all memory modules can be imported."""
        modules = [
            "agents.memory.working_memory",
            "agents.memory.memory_retrieval",
        ]
        
        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")
    
    def test_intelligence_modules_importable(self):
        """Test all intelligence modules can be imported."""
        modules = [
            "agents.intelligence.prioritization",
            "agents.intelligence.goal_monitoring",
        ]
        
        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")
    
    def test_governance_modules_importable(self):
        """Test all governance modules can be imported."""
        modules = [
            "agents.governance.decision_rights",
            "agents.governance.escalation",
        ]
        
        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")
    
    def test_safety_modules_importable(self):
        """Test all safety modules can be imported."""
        modules = [
            "agents.safety.guardrails",
        ]
        
        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")
    
    def test_resilience_modules_importable(self):
        """Test all resilience modules can be imported."""
        modules = [
            "agents.resilience.exception_handling",
        ]
        
        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")


class TestMiddlewareDoesNotBreakAgents:
    """Test that middleware can wrap agents without breaking them."""
    
    @pytest.mark.asyncio
    async def test_middleware_pre_process_returns_dict(self, sample_profile_id, sample_session_id, mock_supabase):
        """Test middleware pre_process returns valid context."""
        from agents.middleware.stack import MiddlewareStack
        
        with patch('agents.middleware.stack.get_supabase', return_value=mock_supabase):
            middleware = MiddlewareStack(sample_profile_id, sample_session_id)
            
            result = await middleware.pre_process({})
            
            assert result is not None
            assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_middleware_post_process_preserves_result(self, sample_profile_id, sample_session_id):
        """Test middleware post_process doesn't lose original result."""
        from agents.middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        
        original_result = {
            "success": True,
            "game_plan": {"narrative_dna": "Test"},
            "custom_field": "preserved",
        }
        
        result = await middleware.post_process(original_result)
        
        assert result["success"] is True
        assert result["custom_field"] == "preserved"
    
    @pytest.mark.asyncio
    async def test_middleware_adds_metadata(self, sample_profile_id, sample_session_id):
        """Test middleware adds metadata without breaking result."""
        from agents.middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(sample_profile_id, sample_session_id)
        
        result = await middleware.post_process({"success": True})
        
        assert "_middleware" in result
        assert "patterns_applied" in result["_middleware"]


class TestNoCircularImports:
    """Test that there are no circular import issues."""
    
    def test_import_all_pattern_modules(self):
        """Test importing all pattern modules in sequence."""
        import_order = [
            # Types first (no dependencies)
            "agents.context.types",
            
            # Context modules
            "agents.context.user_context",
            "agents.context.temporal_context",
            "agents.context.task_context",
            "agents.context.context_selector",
            
            # Memory modules
            "agents.memory.working_memory",
            "agents.memory.memory_retrieval",
            
            # Intelligence modules
            "agents.intelligence.prioritization",
            "agents.intelligence.goal_monitoring",
            
            # Governance modules
            "agents.governance.decision_rights",
            "agents.governance.escalation",
            
            # Safety modules
            "agents.safety.guardrails",
            
            # Resilience modules
            "agents.resilience.exception_handling",
            
            # Middleware last (depends on all above)
            "agents.middleware.stack",
        ]
        
        for module in import_order:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Circular import or missing dependency in {module}: {e}")
