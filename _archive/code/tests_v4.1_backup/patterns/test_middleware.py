# tests/patterns/test_middleware.py
"""
Tests for MiddlewareStack integration
CORRECTED to match actual implementation (wrap_agent async context manager)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestMiddlewareStack:
    """Tests for MiddlewareStack."""
    
    def test_middleware_importable(self):
        """Test MiddlewareStack can be imported."""
        from middleware.stack import MiddlewareStack
        assert MiddlewareStack is not None
    
    def test_middleware_initialization(self):
        """Test MiddlewareStack can be initialized without arguments."""
        from middleware.stack import MiddlewareStack
        middleware = MiddlewareStack()
        assert middleware is not None
    
    def test_middleware_with_supabase(self, mock_supabase):
        """Test MiddlewareStack with Supabase client."""
        from middleware.stack import MiddlewareStack
        middleware = MiddlewareStack(supabase_client=mock_supabase)
        assert middleware.supabase == mock_supabase
    
    def test_middleware_with_redis(self, mock_redis):
        """Test MiddlewareStack with Redis client."""
        from middleware.stack import MiddlewareStack
        middleware = MiddlewareStack(redis_client=mock_redis)
        assert middleware.redis == mock_redis
    
    def test_wrap_agent_exists(self):
        """Test wrap_agent method exists."""
        from middleware.stack import MiddlewareStack
        middleware = MiddlewareStack()
        assert hasattr(middleware, 'wrap_agent')
    
    @pytest.mark.asyncio
    async def test_wrap_agent_context_manager(self, mock_supabase):
        """Test wrap_agent as async context manager."""
        from middleware.stack import MiddlewareStack, AgentContext
        
        middleware = MiddlewareStack(supabase_client=mock_supabase)
        
        async with middleware.wrap_agent(
            "ec_agent",
            "profile-123",
            session_id="session-456",
        ) as ctx:
            assert isinstance(ctx, AgentContext)
            assert ctx.profile_id == "profile-123"
            assert ctx.session_id == "session-456"
    
    @pytest.mark.asyncio
    async def test_wrap_agent_auto_session_id(self, mock_supabase):
        """Test wrap_agent generates session_id if not provided."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(supabase_client=mock_supabase)
        
        async with middleware.wrap_agent("ec_agent", "profile-123") as ctx:
            assert ctx.session_id is not None
    
    def test_check_escalation(self):
        """Test check_escalation method."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        # Safe message
        result = middleware.check_escalation(
            "Help me with my essay",
            {},
        )
        assert result is None
        
        # Dangerous message
        result = middleware.check_escalation(
            "I feel unsafe at home",
            {},
        )
        assert result is not None
    
    def test_check_guardrails(self):
        """Test check_guardrails method."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        results = middleware.check_guardrails("This is safe content")
        
        assert isinstance(results, list)
        assert len(results) > 0
    
    def test_validate_output(self):
        """Test validate_output method."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        result = middleware.validate_output(
            {"success": True, "data": "test"},
            output_type="general",
        )
        
        assert result is not None
    
    def test_prioritize(self):
        """Test prioritize method."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        items = [{"id": "1", "name": "Test Award", "type": "award"}]
        context = {"grade": 11}
        
        result = middleware.prioritize(items, context)
        
        assert isinstance(result, list)
    
    def test_finalize(self):
        """Test finalize method adds validation metadata."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        result = middleware.finalize({"success": True})
        
        assert "_validation" in result
        assert "valid" in result["_validation"]


class TestAgentContext:
    """Tests for AgentContext."""
    
    def test_agent_context_importable(self):
        """Test AgentContext can be imported."""
        from middleware.stack import AgentContext
        assert AgentContext is not None
    
    def test_agent_context_creation(self):
        """Test creating AgentContext."""
        from middleware.stack import AgentContext
        from context.task_context import TaskType
        
        ctx = AgentContext(
            profile_id="profile-123",
            session_id="session-456",
            task_type=TaskType.GENERAL,
        )
        
        assert ctx.profile_id == "profile-123"
        assert ctx.session_id == "session-456"
    
    def test_agent_context_to_dict(self):
        """Test AgentContext.to_dict()."""
        from middleware.stack import AgentContext
        from context.task_context import TaskType
        
        ctx = AgentContext(
            profile_id="profile-123",
            session_id="session-456",
        )
        
        d = ctx.to_dict()
        
        assert d["profile_id"] == "profile-123"
        assert d["session_id"] == "session-456"


class TestAgentExecutionContext:
    """Tests for _AgentExecutionContext."""
    
    @pytest.mark.asyncio
    async def test_context_starts_metrics(self, mock_supabase):
        """Test context manager starts metrics collection."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(supabase_client=mock_supabase)
        
        async with middleware.wrap_agent("ec_agent", "profile-123") as ctx:
            assert ctx.metrics_id is not None
    
    @pytest.mark.asyncio
    async def test_context_handles_exception(self, mock_supabase):
        """Test context manager handles exceptions."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(supabase_client=mock_supabase)
        
        with pytest.raises(ValueError):
            async with middleware.wrap_agent("ec_agent", "profile-123") as ctx:
                raise ValueError("Test error")


class TestCreateMiddleware:
    """Tests for create_middleware convenience function."""
    
    def test_create_middleware_exists(self):
        """Test create_middleware function exists."""
        from middleware.stack import create_middleware
        assert create_middleware is not None
    
    def test_create_middleware_returns_stack(self, mock_supabase, mock_redis):
        """Test create_middleware returns MiddlewareStack."""
        from middleware.stack import create_middleware, MiddlewareStack
        
        middleware = create_middleware(mock_supabase, mock_redis)
        
        assert isinstance(middleware, MiddlewareStack)


class TestMiddlewareComponents:
    """Tests for middleware components."""
    
    def test_has_user_context_loader(self, mock_supabase):
        """Test middleware has user context loader."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(supabase_client=mock_supabase)
        
        assert middleware._user_context is not None
    
    def test_has_temporal_context_loader(self, mock_supabase):
        """Test middleware has temporal context loader."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack(supabase_client=mock_supabase)
        
        assert middleware._temporal_context is not None
    
    def test_has_guardrails(self):
        """Test middleware has guardrails."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        assert middleware._guardrails is not None
    
    def test_has_metrics(self):
        """Test middleware has metrics collector."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        assert middleware._metrics is not None
    
    def test_has_prioritizer(self):
        """Test middleware has prioritizer."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        assert middleware._prioritizer is not None
    
    def test_has_decision_rights(self):
        """Test middleware has decision rights manager."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        assert middleware._decision_rights is not None
    
    def test_has_escalation(self):
        """Test middleware has escalation protocol."""
        from middleware.stack import MiddlewareStack
        
        middleware = MiddlewareStack()
        
        assert middleware._escalation is not None
