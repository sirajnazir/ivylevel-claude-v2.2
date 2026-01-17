"""
Pytest configuration for Phase 2A tests.
"""

import pytest
import sys
import os

# Add agents directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture
def sample_student_context():
    """Sample student context for testing."""
    return {
        "profile_id": "test-profile-123",
        "name": "Test Student",
        "grade": 11,
        "archetype": "stem_innovator",
        "spike": "AI research",
        "pillars": ["technology", "research", "leadership"],
        "communication_style": "direct",
        "gpa": 3.9,
        "target_schools": ["MIT", "Stanford", "CMU"],
        "intended_major": "Computer Science",
    }


@pytest.fixture
def sample_temporal_context():
    """Sample temporal context for testing."""
    return {
        "current_phase": "junior_spring",
        "has_urgent_items": True,
        "deadlines": [
            {
                "name": "RSI Application",
                "days_until": 5,
                "priority": "high",
            },
            {
                "name": "SAT Test",
                "days_until": 14,
                "priority": "medium",
            },
        ],
        "imminent_deadlines": [
            {
                "name": "RSI Application",
                "days_until": 5,
                "priority": "high",
            },
        ],
    }


@pytest.fixture
def sample_working_memory():
    """Sample working memory for testing."""
    return {
        "session_id": "session-123",
        "profile_id": "test-profile-123",
        "detected_sentiment": "focused",
        "conversation_buffer": [
            {"role": "user", "content": "Help me with my essay"},
            {"role": "assistant", "content": "I'd be happy to help!"},
        ],
        "session_facts": [
            "Student is working on RSI application",
            "Deadline is in 5 days",
        ],
        "recent_signals": [
            {"signal_type": "focused", "confidence": 0.8},
        ],
        "scratchpad": {},
    }


@pytest.fixture
def sample_episode():
    """Sample episode for testing."""
    from middleware.memory import Episode
    return Episode(
        episode_id="episode-123",
        profile_id="test-profile-123",
        situation="Student stuck on essay intro",
        context={"deadline_pressure": True},
        action_taken="Provided 3 example hooks",
        approach_type="examples_over_instructions",
        agent_name="execution_agent",
        outcome="success",
        outcome_details={"examples_used": 3},
        student_response="That helped a lot!",
        learnings=["Examples work better than explanations for this student"],
        tags=["essay", "intro", "stuck"],
        significance_score=0.8,
    )


@pytest.fixture
def sample_approval_rule():
    """Sample approval rule for testing."""
    from middleware.approval import ApprovalRule, ApprovalCategory, ApprovalUrgency
    return ApprovalRule(
        rule_id="test-rule",
        action_pattern="test_action|another_action",
        category=ApprovalCategory.STRATEGIC,
        urgency=ApprovalUrgency.STANDARD,
        description="Test approval rule",
        min_confidence_bypass=0.9,
    )
