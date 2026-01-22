# agents/tests/patterns/conftest.py
"""
Shared fixtures for Critical 15 Patterns tests - v5.4 True Autonomous Agents.

These fixtures provide consistent test data across all pattern tests.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


# =============================================================================
# Mock Clients
# =============================================================================


@pytest.fixture
def mock_redis():
    """Mock Redis client for working memory tests."""
    import json

    class MockRedis:
        def __init__(self):
            self._data: Dict[str, str] = {}
            self._ttls: Dict[str, int] = {}

        async def setex(self, key: str, ttl: int, value: str):
            self._data[key] = value
            self._ttls[key] = ttl
            return True

        async def get(self, key: str) -> str | None:
            return self._data.get(key)

        async def delete(self, key: str) -> int:
            if key in self._data:
                del self._data[key]
                if key in self._ttls:
                    del self._ttls[key]
                return 1
            return 0

        async def scan(self, cursor: int, match: str, count: int):
            import fnmatch

            matches = [k for k in self._data.keys() if fnmatch.fnmatch(k, match)]
            return 0, matches

        async def keys(self, pattern: str):
            import fnmatch

            return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]

        async def ping(self):
            return True

        async def expire(self, key: str, ttl: int):
            if key in self._data:
                self._ttls[key] = ttl
                return True
            return False

    return MockRedis()


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for database operations."""

    class MockQueryBuilder:
        def __init__(self, table_name: str, data: List[Dict]):
            self._table = table_name
            self._data = data
            self._filters: Dict[str, Any] = {}
            self._select_cols: str = "*"
            self._order_col: str | None = None
            self._order_desc: bool = False
            self._limit_n: int | None = None

        def select(self, cols: str = "*"):
            self._select_cols = cols
            return self

        def insert(self, data: Dict):
            import uuid

            data["id"] = data.get("id", str(uuid.uuid4()))
            data["created_at"] = datetime.utcnow().isoformat()
            self._data.append(data)
            return self

        def update(self, data: Dict):
            for item in self._data:
                if all(item.get(k) == v for k, v in self._filters.items()):
                    item.update(data)
            return self

        def eq(self, field: str, value: Any):
            self._filters[field] = value
            return self

        def neq(self, field: str, value: Any):
            self._filters[f"neq_{field}"] = value
            return self

        def gt(self, field: str, value: Any):
            self._filters[f"gt_{field}"] = value
            return self

        def gte(self, field: str, value: Any):
            self._filters[f"gte_{field}"] = value
            return self

        def lt(self, field: str, value: Any):
            self._filters[f"lt_{field}"] = value
            return self

        def lte(self, field: str, value: Any):
            self._filters[f"lte_{field}"] = value
            return self

        def order(self, col: str, desc: bool = False):
            self._order_col = col
            self._order_desc = desc
            return self

        def limit(self, n: int):
            self._limit_n = n
            return self

        def single(self):
            return self

        def maybe_single(self):
            return self

        async def execute(self):
            # Apply filters
            result = [
                item
                for item in self._data
                if all(item.get(k) == v for k, v in self._filters.items())
            ]

            # Apply ordering
            if self._order_col:
                result = sorted(
                    result,
                    key=lambda x: x.get(self._order_col, ""),
                    reverse=self._order_desc,
                )

            # Apply limit
            if self._limit_n:
                result = result[: self._limit_n]

            class Result:
                def __init__(self, data):
                    self.data = data

            return Result(result)

    class MockSupabase:
        def __init__(self):
            self._tables: Dict[str, List[Dict]] = {}
            self._rpc_handlers: Dict[str, callable] = {}

        def table(self, name: str):
            if name not in self._tables:
                self._tables[name] = []
            return MockQueryBuilder(name, self._tables[name])

        async def rpc(self, name: str, params: Dict = None):
            class Result:
                def __init__(self, data):
                    self.data = data

            if name in self._rpc_handlers:
                return Result(self._rpc_handlers[name](params))
            return Result([])

        def add_rpc_handler(self, name: str, handler: callable):
            self._rpc_handlers[name] = handler

    return MockSupabase()


@pytest.fixture
def mock_llm():
    """Mock LLM client for reasoning tests."""

    class MockLLMClient:
        def __init__(self):
            self.call_count = 0
            self.last_prompt = None
            self._responses: List[str] = []

        async def complete(self, prompt: str, **kwargs) -> str:
            self.call_count += 1
            self.last_prompt = prompt
            if self._responses:
                return self._responses.pop(0)
            return "Mock LLM response"

        async def chat(self, messages: List[Dict], **kwargs) -> str:
            self.call_count += 1
            self.last_prompt = messages[-1].get("content", "") if messages else ""
            if self._responses:
                return self._responses.pop(0)
            return "Mock chat response"

        def set_responses(self, responses: List[str]):
            self._responses = responses.copy()

    return MockLLMClient()


# =============================================================================
# Context Fixtures
# =============================================================================


@pytest.fixture
def sample_student_context():
    """Sample StudentContext data for testing."""
    return {
        "profile_id": "test-profile-123",
        "name": "Test Student",
        "grade": 11,
        "archetype": "DoubleDown",
        "archetype_confidence": 0.85,
        "spike": "robotics",
        "spike_score": 0.82,
        "communication_style": "balanced",  # Valid enum: detailed, concise, balanced
        "motivation_type": "achievement",   # Valid enum: achievement, mastery, social
        "cri_score": 75.0,
        "eds_score": 68.0,
        "brand_statement": "Building the future of automation",
        "narrative_dna": "A passionate robotics engineer from Chicago...",
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
        "target_schools": ["MIT", "Stanford", "Carnegie Mellon"],
        "constraints": {"financial": "medium", "geographic": "midwest"},
    }


@pytest.fixture
def sample_temporal_context():
    """Sample TemporalContext data for testing."""
    now = datetime.utcnow()
    return {
        "current_phase": "junior_spring",
        "days_until_deadline": 180,
        "current_month": now.month,
        "current_year": now.year,
        "deadlines": [
            {
                "name": "SAT Registration",
                "date": (now + timedelta(days=30)).isoformat(),
                "priority": "high",
                "category": "testing",
            },
            {
                "name": "Summer Program Apps",
                "date": (now + timedelta(days=60)).isoformat(),
                "priority": "medium",
                "category": "activities",
            },
        ],
        "phase_priorities": [
            "Standardized testing preparation",
            "Summer activity planning",
            "Leadership position preparation",
        ],
        "recommended_focus": "testing_and_activities",
    }


@pytest.fixture
def sample_task_context():
    """Sample TaskContext data for testing."""
    return {
        "task_id": "task-abc-123",
        "task_type": "gameplan",
        "objective": "Generate personalized college application gameplan",
        "status": "in_progress",
        "started_at": datetime.utcnow().isoformat(),
        "agent_name": "gameplan_agent",
        "sub_tasks": [
            {"name": "Load profile", "status": "completed"},
            {"name": "Analyze strengths", "status": "in_progress"},
            {"name": "Generate recommendations", "status": "pending"},
        ],
    }


@pytest.fixture
def sample_working_memory():
    """Sample WorkingMemory data for testing."""
    return {
        "session_id": "session-xyz-789",
        "profile_id": "test-profile-123",
        "created_at": datetime.utcnow().isoformat(),
        "conversation_turns": [
            {
                "role": "user",
                "content": "What activities should I focus on this semester?",
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "role": "assistant",
                "content": "Based on your robotics spike, I recommend...",
                "timestamp": datetime.utcnow().isoformat(),
            },
        ],
        "detected_signals": [
            {
                "signal_type": "interest",
                "content": "robotics",
                "confidence": 0.9,
            },
        ],
        "context_summary": "Student asking about activity recommendations",
    }


# =============================================================================
# Recommendation Fixtures
# =============================================================================


@pytest.fixture
def sample_recommendations():
    """Sample recommendations for prioritization tests."""
    return [
        {
            "id": "rec-1",
            "title": "SAT Prep Course",
            "type": "testing",
            "urgency": "high",
            "impact": 4,
            "effort": 3,
            "deadline_days": 30,
        },
        {
            "id": "rec-2",
            "title": "Robotics Competition",
            "type": "activity",
            "urgency": "medium",
            "impact": 5,
            "effort": 4,
            "deadline_days": 60,
        },
        {
            "id": "rec-3",
            "title": "Essay Draft",
            "type": "application",
            "urgency": "low",
            "impact": 5,
            "effort": 3,
            "deadline_days": 180,
        },
        {
            "id": "rec-4",
            "title": "Teacher Recommendation Request",
            "type": "application",
            "urgency": "high",
            "impact": 4,
            "effort": 1,
            "deadline_days": 15,
        },
    ]


@pytest.fixture
def sample_goals():
    """Sample goals for goal monitoring tests."""
    now = datetime.utcnow()
    return [
        {
            "id": "goal-1",
            "name": "Achieve 1500+ SAT Score",
            "category": "testing",
            "target_value": 1500,
            "current_value": 1400,
            "status": "in_progress",
            "deadline": (now + timedelta(days=90)).isoformat(),
        },
        {
            "id": "goal-2",
            "name": "Complete 3 AP Classes",
            "category": "academics",
            "target_value": 3,
            "current_value": 2,
            "status": "in_progress",
            "deadline": (now + timedelta(days=180)).isoformat(),
        },
        {
            "id": "goal-3",
            "name": "Win Regional Competition",
            "category": "activities",
            "target_value": 1,
            "current_value": 0,
            "status": "pending",
            "deadline": (now + timedelta(days=120)).isoformat(),
        },
    ]


# =============================================================================
# Message Fixtures for Guardrails/Escalation
# =============================================================================


@pytest.fixture
def safe_messages():
    """Safe messages that should pass guardrails."""
    return [
        "What activities should I focus on this semester?",
        "Can you help me plan my college applications?",
        "I'm feeling nervous about my SAT scores.",
        "What summer programs do you recommend?",
        "How can I improve my extracurricular profile?",
    ]


@pytest.fixture
def unsafe_messages():
    """Messages that should trigger guardrails/escalation."""
    return [
        "I feel like hurting myself",  # Self-harm
        "I'm being bullied at school",  # Bullying
        "My parents are pressuring me too much",  # Family stress
        "I can't take this anymore",  # Distress
    ]


@pytest.fixture
def edge_case_messages():
    """Edge case messages for boundary testing."""
    return [
        "I'm stressed about applications",  # Mild stress - should not escalate
        "My grades are killing me",  # Figurative language
        "I bombed my test",  # Slang
        "This is so frustrating!",  # Normal frustration
    ]


# =============================================================================
# Output Fixtures for Validation
# =============================================================================


@pytest.fixture
def valid_gameplan_output():
    """Valid gameplan output for validation tests."""
    return {
        "profile_id": "test-profile-123",
        "gameplan_type": "quarterly",
        "recommendations": [
            {
                "title": "SAT Preparation",
                "priority": "high",
                "description": "Focus on practice tests and time management.",
                "deadline": "2024-03-15",
                "action_items": ["Take practice test", "Review weak areas"],
            },
            {
                "title": "Summer Research",
                "priority": "medium",
                "description": "Apply to robotics research programs.",
                "deadline": "2024-02-28",
                "action_items": ["Research programs", "Prepare applications"],
            },
        ],
        "summary": "Focus on testing and summer planning this quarter.",
        "next_check_in": "2024-02-01",
    }


@pytest.fixture
def invalid_gameplan_output():
    """Invalid gameplan output for validation tests."""
    return {
        # Missing required fields
        "recommendations": [],  # Empty recommendations
        # Missing profile_id, summary, etc.
    }


@pytest.fixture
def valid_assessment_output():
    """Valid assessment output for validation tests."""
    return {
        "profile_id": "test-profile-123",
        "cri_score": 75.5,
        "eds_score": 68.2,
        "spike_analysis": {
            "primary_spike": "robotics",
            "confidence": 0.85,
            "supporting_evidence": ["Robotics Club leadership", "Autonomous drone project"],
        },
        "archetype": "DoubleDown",
        "archetype_confidence": 0.82,
        "strengths": ["Technical skills", "Leadership", "Innovation"],
        "growth_areas": ["Essay writing", "Humanities exposure"],
        "brand_statement": "A future robotics engineer building autonomous systems.",
    }
