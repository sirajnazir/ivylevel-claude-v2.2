# tests/conftest.py
"""
Shared fixtures for all Critical 15 Pattern tests.
CORRECTED to match actual implementation API
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4


# ============================================================================
# ASYNC SUPPORT
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================

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
        "budget": 50000,
        "location_preferences": ["Northeast", "West Coast"],
        "time_constraints": None,
    }


@pytest.fixture
def sample_activities():
    """Sample activities for testing."""
    return [
        {
            "id": str(uuid4()),
            "name": "AI Research Club",
            "category": "STEM",
            "hours_per_week": 5,
            "leadership_role": "President",
        },
        {
            "id": str(uuid4()),
            "name": "Math Olympiad",
            "category": "Academic",
            "hours_per_week": 3,
            "leadership_role": None,
        },
        {
            "id": str(uuid4()),
            "name": "Tutoring Program",
            "category": "Service",
            "hours_per_week": 4,
            "leadership_role": "Coordinator",
        },
    ]


@pytest.fixture
def sample_deadlines():
    """Sample deadlines for temporal context testing."""
    now = datetime.utcnow()
    return [
        {
            "id": str(uuid4()),
            "name": "MIT Early Action",
            "due_date": (now + timedelta(days=3)).isoformat(),
            "category": "application",
            "status": "upcoming",
            "task_id": None,
        },
        {
            "id": str(uuid4()),
            "name": "NCWIT Award",
            "due_date": (now + timedelta(days=14)).isoformat(),
            "category": "award",
            "status": "upcoming",
            "task_id": None,
        },
        {
            "id": str(uuid4()),
            "name": "RSI Application",
            "due_date": (now + timedelta(days=45)).isoformat(),
            "category": "program",
            "status": "upcoming",
            "task_id": None,
        },
    ]


@pytest.fixture
def sample_tasks():
    """Sample tasks for prioritization testing."""
    return [
        {
            "id": "task_1",
            "name": "Complete MIT Essay",
            "description": "Finish main essay for MIT application",
            "category": "essay_draft",
            "days_until": 3,
            "difficulty": 0.7,
            "blocking_count": 2,
            "goal": "MIT admission",
        },
        {
            "id": "task_2",
            "name": "Submit NCWIT Application",
            "description": "Complete award application",
            "category": "award_submission",
            "days_until": 14,
            "difficulty": 0.5,
            "blocking_count": 0,
            "goal": "Award recognition",
        },
        {
            "id": "task_3",
            "name": "Research RSI Requirements",
            "description": "Look up program details",
            "category": "research",
            "days_until": 45,
            "difficulty": 0.2,
            "blocking_count": 1,
            "goal": "Summer program",
        },
    ]


@pytest.fixture
def sample_goals():
    """Sample goals for goal monitoring testing."""
    return [
        {
            "id": str(uuid4()),
            "name": "Get into MIT",
            "description": "Secure admission to MIT",
            "target_date": (datetime.utcnow() + timedelta(days=120)).isoformat(),
            "success_criteria": {"submitted": True, "quality_score": 85},
            "status": "active",
            "progress_percentage": 60,
        },
        {
            "id": str(uuid4()),
            "name": "Win National Award",
            "description": "Win NCWIT or similar",
            "target_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "success_criteria": {"applications_submitted": 3, "wins": 1},
            "status": "active",
            "progress_percentage": 40,
        },
    ]


# ============================================================================
# MOCK SERVICES
# ============================================================================

@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = Mock()
    
    # Mock table().select().eq().single().execute()
    mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
        data={}
    )
    
    # Mock table().select().eq().execute()
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
        data=[]
    )
    
    # Mock rpc
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
