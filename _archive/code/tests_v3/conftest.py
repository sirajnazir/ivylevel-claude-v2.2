# tests/conftest.py
"""
Shared fixtures for Critical 15 Pattern tests.
FINAL VERSION
"""

import pytest
import asyncio
from unittest.mock import Mock
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
        "gpa_weighted": 3.8,
        "archetype_id": "stem_innovator",
        "archetype_confidence": 0.85,
        "narrative_dna": "Building AI solutions for educational equity",
        "intended_major": "Computer Science",
        "target_schools": ["MIT", "Stanford", "Carnegie Mellon"],
    }


@pytest.fixture
def sample_activities():
    """Sample activities for testing."""
    return [
        {"id": str(uuid4()), "name": "AI Research Club", "category": "STEM"},
        {"id": str(uuid4()), "name": "Math Olympiad", "category": "Academic"},
        {"id": str(uuid4()), "name": "Tutoring Program", "category": "Service"},
    ]


@pytest.fixture
def sample_tasks():
    """Sample tasks for prioritization testing."""
    return [
        {"id": "task_1", "name": "Complete MIT Essay", "category": "essay_draft", "days_until": 3, "difficulty": 0.7, "blocking_count": 2},
        {"id": "task_2", "name": "Submit NCWIT Application", "category": "award_submission", "days_until": 14, "difficulty": 0.5, "blocking_count": 0},
        {"id": "task_3", "name": "Research RSI Requirements", "category": "research", "days_until": 45, "difficulty": 0.2, "blocking_count": 1},
    ]


@pytest.fixture
def sample_goals():
    """Sample goals for goal monitoring testing."""
    return [
        {"id": str(uuid4()), "name": "Get into MIT", "target_date": (datetime.utcnow() + timedelta(days=120)).isoformat(), "progress_percentage": 60, "status": "active"},
        {"id": str(uuid4()), "name": "Win National Award", "target_date": (datetime.utcnow() + timedelta(days=30)).isoformat(), "progress_percentage": 40, "status": "active"},
    ]


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = Mock()
    mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data={})
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(data=[])
    mock.rpc.return_value.execute.return_value = Mock(data=[])
    return mock


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = Mock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    return mock


@pytest.fixture
def mock_langfuse():
    """Mock Langfuse client."""
    mock = Mock()
    mock.trace.return_value = Mock()
    mock.generation.return_value = Mock()
    return mock
