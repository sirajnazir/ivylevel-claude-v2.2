# agents/tests/conftest.py
"""
IvyQuest v13.2 - Pytest Configuration

Shared fixtures and configuration for tests.
"""

import pytest
import sys
from pathlib import Path

# Add agents directory to path
agents_dir = Path(__file__).parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    return {
        "id": "test-profile-123",
        "name": "Test Student",
        "archetype": "DoubleDown",
        "archetype_confidence": 0.85,
        "cri_score": 75.0,
        "eds_score": 68.0,
        "spike_score": 0.82,
        "narrative_dna": "A passionate robotics engineer...",
        "brand_statement": "Building the future of automation",
        "activities": [
            {"name": "Robotics Club", "domains": ["engineering", "robotics"]},
            {"name": "Math Team", "domains": ["mathematics"]},
        ],
        "projects": [
            {"name": "Autonomous Drone", "domains": ["engineering", "robotics"]},
        ],
        "awards": [
            {"name": "Regional Robotics Champion", "level": "regional"},
        ],
    }


@pytest.fixture
def sample_assessment_input():
    """Sample assessment input for testing."""
    return {
        "profile_summary": {
            "name": "Test Student",
            "grade": 11,
        },
        "activities": [
            {
                "name": "Robotics Club",
                "domains": ["engineering", "robotics"],
                "leadership": True,
                "impact_level": 3,
            },
            {
                "name": "Math Team",
                "domains": ["mathematics"],
                "leadership": False,
                "impact_level": 2,
            },
            {
                "name": "Science Olympiad",
                "domains": ["science", "engineering"],
                "leadership": False,
                "impact_level": 2,
            },
        ],
        "projects": [
            {
                "name": "Autonomous Drone",
                "domains": ["engineering", "robotics"],
                "role": "lead",
                "innovative": True,
            },
        ],
        "awards": [
            {
                "name": "Regional Robotics Champion",
                "level": "regional",
                "domains": ["robotics"],
            },
        ],
    }


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    class MockRedis:
        def __init__(self):
            self.data = {}

        async def setex(self, key, ttl, value):
            self.data[key] = value

        async def get(self, key):
            return self.data.get(key)

        async def delete(self, key):
            if key in self.data:
                del self.data[key]
                return 1
            return 0

        async def scan(self, cursor, match, count):
            import fnmatch
            matches = [k for k in self.data.keys() if fnmatch.fnmatch(k, match)]
            return 0, matches

        async def ping(self):
            return True

    return MockRedis()


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    class MockTable:
        def __init__(self):
            self.data = []
            self._filters = {}

        def select(self, *args, **kwargs):
            return self

        def insert(self, data):
            if isinstance(data, dict):
                data["id"] = f"mock-{len(self.data)}"
            self.data.append(data)
            return self

        def eq(self, field, value):
            self._filters[field] = value
            return self

        def order(self, *args, **kwargs):
            return self

        def limit(self, n):
            return self

        def single(self):
            return self

        async def execute(self):
            class Result:
                def __init__(self, data):
                    self.data = data
            return Result(self.data)

    class MockSupabase:
        def __init__(self):
            self._tables = {}

        def table(self, name):
            if name not in self._tables:
                self._tables[name] = MockTable()
            return self._tables[name]

        async def rpc(self, name, params):
            class Result:
                data = []
            return Result()

    return MockSupabase()


@pytest.fixture
def memory_manager(mock_redis, mock_supabase):
    """Memory manager with mocks."""
    from agents.agents.core import MemoryManager
    return MemoryManager(
        redis_client=mock_redis,
        supabase_client=mock_supabase,
    )
