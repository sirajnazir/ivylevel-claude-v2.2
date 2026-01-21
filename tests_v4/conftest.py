# tests/conftest.py
"""
Shared fixtures for Critical 15 Pattern tests.
v4 - CORRECTED to match actual implementation
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_profile_id():
    """Generate a sample profile ID."""
    return str(uuid4())


@pytest.fixture
def sample_session_id():
    """Generate a sample session ID."""
    return f"session_{uuid4().hex[:8]}"


@pytest.fixture
def sample_profile():
    """Sample student profile for testing."""
    return {
        "id": str(uuid4()),
        "name": "Test Student",
        "grade": 11,
        "gpa": 3.8,
        "archetype": "academic_all_star",
        "spike": "AI and Machine Learning",
        "pillars": ["technology", "research", "leadership"],
        "target_schools": ["MIT", "Stanford", "Carnegie Mellon"],
        "activities": [
            {"id": "1", "name": "AI Club", "category": "STEM"},
            {"id": "2", "name": "Math Team", "category": "Academic"},
        ],
        "constraints": {
            "weekly_hours_available": 15,
            "budget": 2000,
        },
    }


@pytest.fixture
def sample_student_context(sample_profile):
    """Sample student context dict."""
    return {
        "grade": sample_profile["grade"],
        "gpa": sample_profile["gpa"],
        "archetype": sample_profile["archetype"],
        "spike": sample_profile["spike"],
        "pillars": sample_profile["pillars"],
        "target_schools": sample_profile["target_schools"],
        "activities": sample_profile["activities"],
        "constraints": sample_profile["constraints"],
    }


@pytest.fixture
def sample_temporal_context():
    """Sample temporal context."""
    return {
        "current_phase": "applications",
        "deadlines": [
            {"name": "MIT EA", "days_until": 14},
            {"name": "Stanford REA", "days_until": 21},
        ],
    }


@pytest.fixture
def sample_items():
    """Sample items for prioritization."""
    return [
        {
            "id": "1",
            "name": "USACO Gold",
            "type": "award",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "selectivity": "highly_selective",
        },
        {
            "id": "2",
            "name": "RSI",
            "type": "program",
            "deadline": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "selectivity": "highly_selective",
        },
        {
            "id": "3",
            "name": "Local Science Fair",
            "type": "award",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "selectivity": "competitive",
        },
    ]


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = Mock()
    
    # Chain for table().select().eq().single().execute()
    mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
        data={}
    )
    
    # Chain for table().select().eq().execute()
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
        data=[]
    )
    
    # Chain for table().insert().execute()
    mock.table.return_value.insert.return_value.execute.return_value = Mock(
        data={}
    )
    
    # rpc for similarity search
    mock.rpc.return_value.execute.return_value = Mock(data=[])
    
    return mock


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = Mock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    mock.exists.return_value = False
    return mock


@pytest.fixture
def mock_langfuse():
    """Mock Langfuse client."""
    mock = Mock()
    mock.trace.return_value = Mock()
    mock.generation.return_value = Mock()
    mock.score.return_value = Mock()
    mock.flush.return_value = None
    return mock


@pytest.fixture
def mock_llm_client():
    """Mock LLM client."""
    mock = AsyncMock()
    mock.chat.completions.create.return_value = Mock(
        choices=[
            Mock(message=Mock(content="Test response"))
        ]
    )
    return mock
