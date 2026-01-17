"""
Tests for B2: Episodic Memory Pattern
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.memory import (
    EpisodicMemoryManager,
    Episode,
    EpisodeQuery,
    EpisodeRetrievalResult,
    record_coaching_episode,
)


class TestEpisodeTypes:
    """Tests for episode type definitions."""

    def test_episode_creation(self):
        """Test Episode model creation."""
        episode = Episode(
            episode_id="test-123",
            profile_id="profile-456",
            situation="Student stuck on essay",
            action_taken="Provided examples",
            approach_type="examples_over_instructions",
            agent_name="execution_agent",
            outcome="success",
        )
        assert episode.episode_id == "test-123"
        assert episode.outcome == "success"
        assert episode.significance_score == 0.5

    def test_episode_with_all_fields(self):
        """Test Episode with all optional fields."""
        episode = Episode(
            episode_id="test-123",
            profile_id="profile-456",
            situation="Student stuck on essay",
            context={"deadline": "2026-01-15"},
            action_taken="Provided examples",
            approach_type="examples_over_instructions",
            agent_name="execution_agent",
            outcome="success",
            outcome_details={"examples_provided": 3},
            student_response="That helped!",
            learnings=["Examples work better than instructions"],
            tags=["essay", "stuck"],
            significance_score=0.8,
        )
        assert episode.context == {"deadline": "2026-01-15"}
        assert len(episode.learnings) == 1
        assert len(episode.tags) == 2

    def test_episode_to_summary(self):
        """Test Episode to_summary method."""
        episode = Episode(
            episode_id="test-123",
            profile_id="profile-456",
            situation="Student stuck on essay",
            action_taken="Provided examples",
            approach_type="examples_over_instructions",
            agent_name="execution_agent",
            outcome="success",
            learnings=["Examples work well"],
        )
        summary = episode.to_summary()
        assert "Student stuck on essay" in summary
        assert "Provided examples" in summary
        assert "success" in summary
        assert "Examples work well" in summary

    def test_episode_query_creation(self):
        """Test EpisodeQuery model creation."""
        query = EpisodeQuery(
            profile_id="profile-123",
            situation_query="essay help",
            outcomes=["success"],
            max_results=10,
        )
        assert query.max_results == 10

    def test_episode_retrieval_result_creation(self):
        """Test EpisodeRetrievalResult model creation."""
        result = EpisodeRetrievalResult(
            episodes=[],
            query_embedding_used=True,
            total_found=5,
        )
        assert result.query_embedding_used == True


class TestEpisodicMemoryManager:
    """Tests for EpisodicMemoryManager."""

    @pytest.fixture
    def manager(self):
        return EpisodicMemoryManager()

    def test_manager_creation(self, manager):
        """Test manager creation."""
        assert manager is not None
        assert manager._cache == {}

    @pytest.mark.asyncio
    async def test_record_episode_creates_episode(self, manager):
        """Record episode creates episode."""
        episode = await manager.record_episode(
            profile_id="test-profile",
            situation="Student stuck on essay",
            action_taken="Provided examples",
            approach_type="examples_over_instructions",
            agent_name="execution_agent",
            outcome="success",
        )

        assert isinstance(episode, Episode)
        assert episode.profile_id == "test-profile"
        assert episode.outcome == "success"
        assert episode.episode_id is not None

    @pytest.mark.asyncio
    async def test_record_episode_caches(self, manager):
        """Record episode updates cache."""
        await manager.record_episode(
            profile_id="test-profile",
            situation="Test situation",
            action_taken="Test action",
            approach_type="test",
            agent_name="test",
            outcome="success",
        )

        assert "test-profile" in manager._cache
        assert len(manager._cache["test-profile"]) == 1

    @pytest.mark.asyncio
    async def test_record_episode_with_context(self, manager):
        """Record episode with context."""
        episode = await manager.record_episode(
            profile_id="test-profile",
            situation="Essay help",
            action_taken="Provided outline",
            approach_type="structured_guidance",
            agent_name="execution_agent",
            outcome="partial",
            context={"deadline_pressure": True},
            outcome_details={"progress": 50},
            student_response="Okay, I'll try",
            learnings=["Student responds better to structure"],
            tags=["essay", "outline"],
        )

        assert episode.context == {"deadline_pressure": True}
        assert episode.outcome == "partial"

    def test_calculate_significance_success(self, manager):
        """Significance calculation for success."""
        sig = manager._calculate_significance("success", {})
        assert sig == 0.7  # 0.5 base + 0.2 for success

    def test_calculate_significance_failure(self, manager):
        """Significance calculation for failure."""
        sig = manager._calculate_significance("failure", {})
        assert sig == 0.65  # 0.5 base + 0.15 for failure

    def test_calculate_significance_high_stakes(self, manager):
        """Significance calculation with high stakes."""
        sig = manager._calculate_significance("success", {"high_stakes": True})
        assert sig == pytest.approx(0.9)  # 0.5 + 0.2 + 0.2

    def test_calculate_significance_deadline_pressure(self, manager):
        """Significance calculation with deadline pressure."""
        sig = manager._calculate_significance("success", {"deadline_pressure": True})
        assert sig == pytest.approx(0.8)  # 0.5 + 0.2 + 0.1

    def test_calculate_significance_crisis(self, manager):
        """Significance calculation with crisis."""
        sig = manager._calculate_significance("success", {"crisis_detected": True})
        assert sig == pytest.approx(0.9)  # 0.5 + 0.2 + 0.2

    def test_calculate_significance_max_cap(self, manager):
        """Significance calculation capped at 1.0."""
        sig = manager._calculate_significance("success", {
            "high_stakes": True,
            "deadline_pressure": True,
            "crisis_detected": True,
        })
        assert sig == 1.0

    @pytest.mark.asyncio
    async def test_recall_similar_without_db_returns_empty(self, manager):
        """Recall similar without DB returns empty."""
        result = await manager.recall_similar("profile-123", "essay help")
        assert result == []

    @pytest.mark.asyncio
    async def test_recall_by_approach_without_db_returns_empty(self, manager):
        """Recall by approach without DB returns empty."""
        result = await manager.recall_by_approach(
            "profile-123",
            "examples_over_instructions",
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_get_recent_episodes_without_db_returns_empty(self, manager):
        """Get recent episodes without DB returns empty."""
        result = await manager.get_recent_episodes("profile-123")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_success_patterns_without_db_returns_empty(self, manager):
        """Get success patterns without DB returns empty."""
        result = await manager.get_success_patterns("profile-123")
        assert result == {}


class TestRecordCoachingEpisode:
    """Tests for record_coaching_episode convenience function."""

    @pytest.mark.asyncio
    async def test_record_coaching_episode(self):
        """Test record_coaching_episode function."""
        manager = EpisodicMemoryManager()
        episode = await record_coaching_episode(
            manager=manager,
            profile_id="123",
            agent_name="execution_agent",
            situation="Student stuck on essay intro",
            action="Provided 3 example hooks",
            outcome="success",
            context={"approach": "examples_over_instructions"}
        )

        assert episode.profile_id == "123"
        assert episode.approach_type == "examples_over_instructions"
        assert episode.outcome == "success"
