"""
Tests for C1: Session Context and C3: System Context Patterns
"""

import pytest
from datetime import datetime, timezone
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.context.session_context_v8 import (
    SessionContextManager,
    SessionContext,
    SessionMessage,
)
from middleware.context.system_context_v8 import (
    SystemContextProvider,
    SystemContext,
    IntegrationInfo,
    IntegrationStatus,
    AgentCapability,
)


class TestSessionMessage:
    """Tests for SessionMessage model."""

    def test_message_creation(self):
        """Test SessionMessage creation."""
        msg = SessionMessage(
            role="user",
            content="Hello, I need help with my essay.",
        )
        assert msg.role == "user"
        assert "essay" in msg.content
        assert msg.timestamp is not None

    def test_message_with_metadata(self):
        """Test SessionMessage with metadata."""
        msg = SessionMessage(
            role="assistant",
            content="I can help with that.",
            metadata={"agent": "essay_agent", "confidence": 0.9},
        )
        assert msg.metadata["agent"] == "essay_agent"
        assert msg.metadata["confidence"] == 0.9


class TestSessionContext:
    """Tests for SessionContext model."""

    def test_context_creation(self):
        """Test SessionContext creation."""
        ctx = SessionContext(
            session_id="test-session",
            profile_id="test-profile",
        )
        assert ctx.session_id == "test-session"
        assert ctx.profile_id == "test-profile"
        assert ctx.messages == []
        assert ctx.current_topic is None

    def test_context_with_messages(self):
        """Test SessionContext with messages."""
        ctx = SessionContext(
            session_id="test-session",
            profile_id="test-profile",
            messages=[
                SessionMessage(role="user", content="Hello"),
                SessionMessage(role="assistant", content="Hi there!"),
            ],
        )
        assert len(ctx.messages) == 2

    def test_get_recent_messages(self):
        """Test getting recent messages via slicing."""
        ctx = SessionContext(
            session_id="test-session",
            profile_id="test-profile",
            messages=[
                SessionMessage(role="user", content="Message 1"),
                SessionMessage(role="assistant", content="Response 1"),
                SessionMessage(role="user", content="Message 2"),
                SessionMessage(role="assistant", content="Response 2"),
                SessionMessage(role="user", content="Message 3"),
            ],
        )
        # Get recent messages via slicing
        recent = ctx.messages[-3:]
        assert len(recent) == 3
        assert recent[-1].content == "Message 3"


class TestSessionContextManager:
    """Tests for SessionContextManager."""

    @pytest.fixture
    def manager(self, mock_supabase, mock_redis):
        return SessionContextManager(
            supabase_client=mock_supabase,
            redis_client=mock_redis,
        )

    def test_manager_creation(self, manager):
        """Test manager creation."""
        assert manager is not None
        assert manager.ttl == 3600  # default TTL

    def test_manager_creation_with_params(self, mock_supabase):
        """Test manager creation with custom params."""
        manager = SessionContextManager(
            supabase_client=mock_supabase,
            ttl_seconds=7200,
        )
        assert manager.ttl == 7200

    @pytest.mark.asyncio
    async def test_get_session_creates_new(self, manager, sample_session_id, sample_profile_id):
        """Test getting/creating new session context."""
        ctx = await manager.get_session(
            session_id=sample_session_id,
            profile_id=sample_profile_id,
        )
        assert ctx.session_id == sample_session_id
        assert ctx.profile_id == sample_profile_id

    @pytest.mark.asyncio
    async def test_add_message(self, manager, sample_session_id, sample_profile_id):
        """Test adding message to context."""
        await manager.get_session(sample_session_id, sample_profile_id)
        result = await manager.add_message(
            session_id=sample_session_id,
            role="user",
            content="Test message",
        )
        assert result is not None
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_sliding_window_trimming(self, mock_supabase):
        """Test sliding window message trimming via max_messages."""
        manager = SessionContextManager(
            supabase_client=mock_supabase,
        )

        # Create session with custom max_messages
        session = await manager.get_session("test-session", "test-profile")
        session.max_messages = 5  # Set smaller window for test

        # Add more messages than window
        for i in range(7):
            await manager.add_message("test-session", "user", f"Message {i}")

        ctx = manager._local_cache.get("test-session")
        # Should be trimmed to max_messages
        assert len(ctx.messages) <= 5


class TestIntegrationInfo:
    """Tests for IntegrationInfo model."""

    def test_info_creation(self):
        """Test IntegrationInfo creation."""
        info = IntegrationInfo(
            name="supabase",
            status=IntegrationStatus.ACTIVE,
        )
        assert info.name == "supabase"
        assert info.status == IntegrationStatus.ACTIVE

    def test_info_degraded(self):
        """Test degraded integration status."""
        info = IntegrationInfo(
            name="openai",
            status=IntegrationStatus.DEGRADED,
            error_message="Rate limit exceeded",
        )
        assert info.status == IntegrationStatus.DEGRADED
        assert info.error_message == "Rate limit exceeded"


class TestSystemContext:
    """Tests for SystemContext model."""

    def test_context_creation(self):
        """Test SystemContext creation."""
        ctx = SystemContext()
        assert ctx.capabilities is not None
        assert ctx.integrations == {}
        assert ctx.rate_limits == {}

    def test_context_with_capabilities(self):
        """Test SystemContext with capabilities."""
        # Capabilities is a Set[AgentCapability]
        ctx = SystemContext(
            capabilities={
                AgentCapability.ESSAY_REVIEW,
                AgentCapability.ACTIVITY_PLANNING,
            },
        )
        assert AgentCapability.ESSAY_REVIEW in ctx.capabilities
        assert AgentCapability.ACTIVITY_PLANNING in ctx.capabilities


class TestSystemContextProvider:
    """Tests for SystemContextProvider."""

    def test_singleton_instance(self):
        """Test singleton pattern."""
        provider1 = SystemContextProvider()
        provider2 = SystemContextProvider()
        assert provider1 is provider2

    def test_get_context(self):
        """Test getting system context."""
        provider = SystemContextProvider()
        ctx = provider.context
        assert isinstance(ctx, SystemContext)

    def test_set_feature_flag(self):
        """Test setting feature flag."""
        provider = SystemContextProvider()
        provider.set_feature_flag("test_feature", True)
        assert provider.get_feature_flag("test_feature") == True

    def test_get_feature_flag_default(self):
        """Test default feature check."""
        provider = SystemContextProvider()
        # Unknown feature defaults to False
        assert provider.get_feature_flag("unknown_feature") == False

    @pytest.mark.asyncio
    async def test_update_integration_status(self):
        """Test updating integration status."""
        provider = SystemContextProvider()
        await provider.update_integration_status(
            integration="test_service",
            status=IntegrationStatus.ACTIVE,
        )
        assert provider.is_integration_healthy("test_service") == True

    def test_is_integration_healthy_unknown(self):
        """Test checking unknown integration health."""
        provider = SystemContextProvider()
        # Unknown integration is not healthy
        assert provider.is_integration_healthy("totally_unknown_service") == False
