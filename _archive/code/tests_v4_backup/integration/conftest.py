# agents/tests/integration/conftest.py
"""
Shared fixtures for integration tests - v5.4 True Autonomous Agents.

These fixtures provide realistic test scenarios for full system testing.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

# Import fixtures from patterns conftest
from ..patterns.conftest import (
    mock_redis,
    mock_supabase,
    mock_llm,
    sample_student_context,
    sample_temporal_context,
    sample_task_context,
    sample_working_memory,
    sample_recommendations,
    sample_goals,
    safe_messages,
    unsafe_messages,
    edge_case_messages,
    valid_gameplan_output,
    invalid_gameplan_output,
    valid_assessment_output,
)


@pytest.fixture
def full_profile_data():
    """Complete profile data simulating a real student."""
    return {
        "id": "integration-test-profile",
        "name": "Integration Test Student",
        "email": "test@example.com",
        "grade": 11,
        "high_school": "Test High School",
        "gpa": 3.8,
        "class_rank": "Top 10%",
        "archetype": "DoubleDown",
        "archetype_confidence": 0.87,
        "spike": "robotics",
        "spike_score": 0.85,
        "spike_domains": ["engineering", "robotics", "computer_science"],
        "cri_score": 78.5,
        "eds_score": 72.3,
        "brand_statement": "A future robotics engineer building autonomous systems to solve real-world problems",
        "narrative_dna": "Growing up in a family of engineers, I discovered my passion for robotics when I built my first robot at age 12...",
        "communication_style": "balanced",   # Valid enum: detailed, concise, balanced
        "motivation_type": "achievement",    # Valid enum: achievement, mastery, social
        "activities": [
            {
                "id": "act-1",
                "name": "Robotics Club",
                "type": "extracurricular",
                "domains": ["engineering", "robotics"],
                "role": "President",
                "leadership": True,
                "hours_per_week": 10,
                "years": 3,
                "impact_level": 4,
                "description": "Lead team of 15 in designing competition robots",
            },
            {
                "id": "act-2",
                "name": "Math Team",
                "type": "academic",
                "domains": ["mathematics"],
                "role": "Member",
                "leadership": False,
                "hours_per_week": 3,
                "years": 2,
                "impact_level": 2,
            },
            {
                "id": "act-3",
                "name": "Science Olympiad",
                "type": "competition",
                "domains": ["science", "engineering"],
                "role": "Team Captain - Robot Arm",
                "leadership": True,
                "hours_per_week": 5,
                "years": 2,
                "impact_level": 3,
            },
        ],
        "projects": [
            {
                "id": "proj-1",
                "name": "Autonomous Delivery Robot",
                "domains": ["robotics", "computer_science"],
                "role": "Lead Developer",
                "status": "completed",
                "innovative": True,
                "impact": "Deployed in local hospital for contactless delivery",
            },
            {
                "id": "proj-2",
                "name": "AI-Powered Plant Watering System",
                "domains": ["robotics", "environmental"],
                "role": "Creator",
                "status": "completed",
                "innovative": True,
            },
        ],
        "awards": [
            {
                "id": "award-1",
                "name": "FIRST Robotics Regional Champion",
                "level": "regional",
                "year": 2024,
                "domains": ["robotics"],
            },
            {
                "id": "award-2",
                "name": "Science Olympiad State Medalist",
                "level": "state",
                "year": 2023,
                "domains": ["science"],
            },
        ],
        "test_scores": {
            "sat": {"total": 1480, "math": 780, "reading": 700},
            "act": None,
            "ap_scores": {"Physics C": 5, "Calculus BC": 5, "Computer Science A": 4},
        },
        "target_schools": [
            {"name": "MIT", "type": "reach"},
            {"name": "Stanford", "type": "reach"},
            {"name": "Carnegie Mellon", "type": "target"},
            {"name": "Georgia Tech", "type": "safety"},
        ],
        "constraints": {
            "financial": "medium",
            "geographic": "no_preference",
            "size": "medium_to_large",
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def realistic_conversation():
    """Realistic conversation for testing chat flows."""
    return [
        {
            "role": "user",
            "content": "Hi Jenny! I'm feeling overwhelmed with college apps. Where should I start?",
        },
        {
            "role": "assistant",
            "content": "I totally understand that feeling! Let's break this down together. Given your strong robotics background, I'd suggest focusing on a few key areas...",
        },
        {
            "role": "user",
            "content": "What summer programs would be good for me?",
        },
        {
            "role": "assistant",
            "content": "Great question! With your robotics spike, here are some programs that would be perfect...",
        },
    ]


@pytest.fixture
def multiple_profiles():
    """Multiple profiles for load testing."""
    profiles = []
    archetypes = ["DoubleDown", "Pivot", "Emerging", "Renaissance"]
    spikes = ["robotics", "music", "debate", "research"]

    for i in range(10):
        profiles.append({
            "id": f"load-test-profile-{i}",
            "name": f"Test Student {i}",
            "grade": 9 + (i % 4),
            "archetype": archetypes[i % 4],
            "spike": spikes[i % 4],
            "cri_score": 60 + (i * 3),
            "eds_score": 55 + (i * 3),
        })

    return profiles
