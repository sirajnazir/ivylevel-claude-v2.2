"""
Phase 2B Test Fixtures

Shared fixtures for Phase 2B pattern tests.
"""

import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    client = MagicMock()
    client.table.return_value.insert.return_value.execute = MagicMock(
        return_value=MagicMock(data=[])
    )
    client.table.return_value.update.return_value.eq.return_value.execute = MagicMock(
        return_value=MagicMock(data=[])
    )
    client.table.return_value.select.return_value.eq.return_value.execute = MagicMock(
        return_value=MagicMock(data=[])
    )
    return client


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    client = MagicMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_llm():
    """Mock LLM client."""
    client = MagicMock()
    client.generate = AsyncMock(return_value="Generated response")
    client.chat = AsyncMock(return_value={"content": "Chat response"})
    return client


@pytest.fixture
def mock_langfuse():
    """Mock Langfuse client."""
    client = MagicMock()
    client.trace = MagicMock()
    client.span = MagicMock()
    client.score = MagicMock()
    return client


@pytest.fixture
def sample_profile_id():
    """Sample profile ID for tests."""
    return "test-profile-123"


@pytest.fixture
def sample_session_id():
    """Sample session ID for tests."""
    return "test-session-456"


@pytest.fixture
def sample_context():
    """Sample context for tests."""
    return {
        "profile_id": "test-profile-123",
        "session_id": "test-session-456",
        "agent_name": "test_agent",
        "task_type": "essay_help",
    }
