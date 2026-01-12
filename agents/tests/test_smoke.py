# agents/tests/test_smoke.py
"""
IvyQuest v13.2 - Smoke Tests

Smoke tests verify basic system functionality after deployment.
Run these tests to ensure the system is healthy:

    pytest agents/tests/test_smoke.py -v

These tests require a running server at localhost:8000.
"""

import pytest
import httpx
from typing import Optional

BASE_URL = "http://localhost:8000"

# Skip if server not running
def server_running() -> bool:
    """Check if server is running."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        return result == 0
    except Exception:
        return False

requires_server = pytest.mark.skipif(
    not server_running(),
    reason="Server not running at localhost:8000"
)


@requires_server
@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify health endpoint returns v13 status."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v13/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["healthy", "degraded"]
        assert data["version"] == "15.0.0"
        assert data["react_enabled"] is True
        assert "thresholds" in data
        assert data["thresholds"]["min_quality"] == 70
        assert data["thresholds"]["min_voice"] == 70


@requires_server
@pytest.mark.asyncio
async def test_health_thresholds():
    """Verify thresholds are correctly configured."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v13/health")
        data = response.json()
        
        thresholds = data["thresholds"]
        assert thresholds["min_quality"] == 70
        assert thresholds["min_voice"] == 70
        assert thresholds["min_golden"] == 0.6
        assert thresholds["max_cycles"] == 3


@requires_server
@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify root returns info."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "IvyQuest" in data.get("message", "")


@requires_server
@pytest.mark.asyncio
async def test_knowledge_search_endpoint():
    """Verify coaching knowledge search endpoint responds."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v13/knowledge/search",
            params={"query": "crisis management", "limit": 3}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "results" in data
        assert data["query"] == "crisis management"


@requires_server
@pytest.mark.asyncio
async def test_handoff_get_nonexistent():
    """Verify handoff endpoint handles non-existent correctly."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v13/memory/handoff/fake-profile/gameplan"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return error or empty handoff
        assert "error" in data or "from_agent" in data


@requires_server
@pytest.mark.asyncio
async def test_outcomes_endpoint():
    """Verify outcomes endpoint responds."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v13/outcomes/fake-profile-id"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "outcomes" in data


@requires_server
@pytest.mark.asyncio
async def test_observations_endpoint():
    """Verify observations endpoint responds."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v13/memory/observations/fake-profile-id"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "observations" in data


@requires_server
@pytest.mark.asyncio
async def test_profile_evolution_endpoint():
    """Verify profile evolution endpoint responds (v13.2)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v13/profile/fake-profile-id/evolution"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Either has snapshots or error (if Supabase not configured)
        assert "snapshots" in data or "error" in data


@requires_server
@pytest.mark.asyncio
async def test_interactions_recall_endpoint():
    """Verify interactions recall endpoint responds (v13.2)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v13/interactions/fake-profile-id/recall",
            params={"query": "archetype discussion"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Either has interactions or error (if not configured)
        assert "interactions" in data or "error" in data


@requires_server
@pytest.mark.asyncio
async def test_working_memory_debug():
    """Verify working memory debug endpoint responds."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v13/memory/working/active"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "active_buffers" in data
        assert "count" in data


# ============================================================
# OFFLINE UNIT TESTS (No server required)
# ============================================================

class TestImports:
    """Test that all modules import correctly."""

    def test_import_core(self):
        """Test core module imports."""
        from agents.agents.core import (
            QualityThresholds,
            AutonomyLevel,
            ReActAgent,
            RunContext,
            ThoughtProcess,
            ActionResult,
            Observation,
            Learning,
            ReActCycle,
            MemoryManager,
            GoldenBenchmark,
            WorkingMemoryBuffer,
            AgentHandoff,
            HandoffManager,
            ProfileSnapshot,
            ProfileSnapshotManager,
            InteractionSummary,
            InteractionMemoryManager,
        )
        
        assert QualityThresholds.MIN_QUALITY_SCORE == 70
        assert QualityThresholds.MIN_VOICE_SCORE == 70
        assert QualityThresholds.MIN_GOLDEN_SIMILARITY == 0.6

    def test_import_thresholds(self):
        """Test thresholds module."""
        from agents.agents.core.thresholds import QualityThresholds, AutonomyLevel
        
        # Verify threshold values
        assert QualityThresholds.MIN_QUALITY_SCORE == 70
        assert QualityThresholds.MAX_REACT_CYCLES == 3
        
        # Verify autonomy levels
        assert AutonomyLevel.FULL.value == "full"
        assert AutonomyLevel.requires_hitl(AutonomyLevel.LOW, 0.99) is True

    def test_import_react_types(self):
        """Test react_types module."""
        from agents.agents.core.react_types import (
            ThoughtProcess, ActionResult, Observation, Learning, ReActCycle, RunContext
        )
        
        # Create instances to verify structure
        thought = ThoughtProcess(
            thought="test",
            reasoning="test",
            planned_action="test",
            confidence=0.5,
            context_factors=[],
        )
        assert thought.confidence == 0.5

    def test_import_working_memory(self):
        """Test working_memory module."""
        from agents.agents.core.working_memory import (
            WorkingMemoryBuffer, EvaluationFrame
        )
        
        buffer = WorkingMemoryBuffer("test", "profile-123")
        assert buffer.agent_name == "test"

    def test_import_handoff(self):
        """Test handoff module."""
        from agents.agents.core.handoff import AgentHandoff, HandoffManager
        from datetime import datetime
        
        handoff = AgentHandoff(
            from_agent="a",
            to_agent="b",
            profile_id="p",
            timestamp=datetime.utcnow(),
            context={},
            task="task",
            reason="reason",
        )
        assert handoff.from_agent == "a"


class TestVersionConsistency:
    """Test version consistency across modules."""

    def test_version_string(self):
        """Test version string is correct."""
        from agents.agents.core import __version__
        assert __version__ == "15.0.0"

    def test_threshold_values_consistent(self):
        """Test threshold values are consistent with PRD."""
        from agents.agents.core.thresholds import QualityThresholds
        
        # These MUST match PRD v13.2 specification
        assert QualityThresholds.MIN_QUALITY_SCORE == 70
        assert QualityThresholds.MIN_VOICE_SCORE == 70
        assert QualityThresholds.MIN_GOLDEN_SIMILARITY == 0.6
        assert QualityThresholds.MAX_REACT_CYCLES == 3
        
        # Weights must sum to 1.0
        total = (
            QualityThresholds.WEIGHT_QUALITY +
            QualityThresholds.WEIGHT_VOICE +
            QualityThresholds.WEIGHT_GOLDEN
        )
        assert total == pytest.approx(1.0)


class TestObservationThresholds:
    """Test Observation uses correct thresholds."""

    def test_passes_at_minimum(self):
        """Test passes_thresholds at exact minimums."""
        from agents.agents.core.react_types import Observation
        
        obs = Observation(
            quality_score=70,
            voice_score=70,
            golden_similarity=0.6,
        )
        assert obs.passes_thresholds is True

    def test_fails_just_below(self):
        """Test fails_thresholds just below minimums."""
        from agents.agents.core.react_types import Observation
        
        # Quality just below
        obs1 = Observation(quality_score=69.9, voice_score=70, golden_similarity=0.6)
        assert obs1.passes_thresholds is False
        
        # Voice just below
        obs2 = Observation(quality_score=70, voice_score=69.9, golden_similarity=0.6)
        assert obs2.passes_thresholds is False
        
        # Golden just below
        obs3 = Observation(quality_score=70, voice_score=70, golden_similarity=0.59)
        assert obs3.passes_thresholds is False
