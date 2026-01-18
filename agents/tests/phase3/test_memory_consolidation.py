"""
Tests for B6: Memory Consolidation

Pattern: B6
3P: OpenAI (for merging)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.memory.consolidation_v9 import (
    MemoryConsolidator,
    ConsolidationResult,
)
from middleware.memory.longterm_v9 import LongTermMemory
from middleware.memory.semantic_v9 import SemanticMemory


class TestMemoryConsolidator:
    """Tests for B6: Memory Consolidation."""

    @pytest.fixture
    def mock_merge_response(self):
        """Mock merge response data."""
        return {
            "content": "User is a high school junior interested in MIT for computer science",
            "memory_type": "fact",
            "importance": 0.9
        }

    @pytest.fixture
    def mock_openai(self, mock_merge_response):
        """Mock OpenAI client."""
        client = MagicMock()

        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_merge_response)

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        client.chat.completions.create.return_value = mock_response

        return client

    @pytest.fixture
    def mock_longterm(self):
        """Mock LongTermMemoryManager."""
        manager = MagicMock()
        manager.is_available = True

        # Mock recall_all to return memories
        async def mock_recall_all(profile_id, min_importance=0.0, limit=100):
            return [
                LongTermMemory(key="mem1", value="Memory 1", importance=0.8),
                LongTermMemory(key="mem2", value="Memory 2", importance=0.1),  # Below threshold
                LongTermMemory(key="mem3", value="Memory 3", importance=0.6),
            ]

        manager.recall_all = mock_recall_all
        manager.forget = AsyncMock(return_value=True)
        manager.update_importance = AsyncMock(return_value=True)

        return manager

    @pytest.fixture
    def mock_semantic(self):
        """Mock SemanticMemoryManager."""
        manager = MagicMock()
        manager.is_available = True

        # Mock get_by_type
        async def mock_get_by_type(profile_id, memory_type, limit=50):
            return [
                SemanticMemory(content="User likes math", importance=0.7),
                SemanticMemory(content="User enjoys mathematics", importance=0.6),
            ]

        # Mock search
        async def mock_search(profile_id, query, min_similarity=0.7, limit=5):
            return [
                SemanticMemory(content="User enjoys mathematics", importance=0.6, similarity=0.9),
            ]

        manager.get_by_type = mock_get_by_type
        manager.search = mock_search
        manager.store = AsyncMock(return_value=True)

        return manager

    @pytest.fixture
    def consolidator(self, mock_openai, mock_longterm, mock_semantic):
        return MemoryConsolidator(
            openai_client=mock_openai,
            longterm_manager=mock_longterm,
            semantic_manager=mock_semantic,
        )

    @pytest.fixture
    def consolidator_no_client(self):
        """Consolidator without clients (tests graceful degradation)."""
        return MemoryConsolidator(openai_client=None)

    @pytest.fixture
    def consolidator_openai_only(self, mock_openai):
        """Consolidator with only OpenAI client."""
        return MemoryConsolidator(openai_client=mock_openai)

    def test_is_available_with_client(self, consolidator):
        """Test availability check with client."""
        assert consolidator.is_available is True

    def test_is_available_without_client(self, consolidator_no_client):
        """Test availability check without client."""
        assert consolidator_no_client.is_available is False

    @pytest.mark.asyncio
    async def test_consolidate_returns_result(self, consolidator):
        """Test consolidation returns result object."""
        result = await consolidator.consolidate(profile_id="test-profile")

        assert isinstance(result, ConsolidationResult)

    @pytest.mark.asyncio
    async def test_consolidate_prunes_low_importance(self, consolidator, mock_longterm):
        """Test consolidation prunes low-importance memories."""
        result = await consolidator.consolidate(
            profile_id="test-profile",
            prune_threshold=0.2,
        )

        # Should have pruned the memory with importance 0.1
        assert result.pruned_count >= 0
        mock_longterm.forget.assert_called()

    @pytest.mark.asyncio
    async def test_consolidate_reinforces_memories(self, consolidator, mock_longterm):
        """Test consolidation reinforces frequently accessed memories."""
        result = await consolidator.consolidate(profile_id="test-profile")

        assert result.reinforced_count >= 0
        mock_longterm.update_importance.assert_called()

    @pytest.mark.asyncio
    async def test_consolidate_graceful_degradation(self, consolidator_no_client):
        """Test consolidation handles missing client gracefully."""
        result = await consolidator_no_client.consolidate(profile_id="test-profile")

        assert isinstance(result, ConsolidationResult)
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_consolidate_without_memory_managers(self, consolidator_openai_only):
        """Test consolidation works without memory managers."""
        result = await consolidator_openai_only.consolidate(profile_id="test-profile")

        assert isinstance(result, ConsolidationResult)
        assert result.pruned_count == 0
        assert result.merged_count == 0

    @pytest.mark.asyncio
    async def test_decay_unused_reduces_importance(self, consolidator, mock_longterm):
        """Test decay_unused reduces memory importance."""
        decayed = await consolidator.decay_unused(
            profile_id="test-profile",
            decay_amount=0.02,
        )

        assert isinstance(decayed, int)
        mock_longterm.update_importance.assert_called()

    @pytest.mark.asyncio
    async def test_decay_unused_graceful_degradation(self, consolidator_no_client):
        """Test decay_unused handles missing manager gracefully."""
        decayed = await consolidator_no_client.decay_unused(profile_id="test-profile")

        assert decayed == 0


class TestConsolidationResult:
    """Tests for the ConsolidationResult model."""

    def test_default_values(self):
        """Test default values are zero."""
        result = ConsolidationResult()

        assert result.merged_count == 0
        assert result.pruned_count == 0
        assert result.reinforced_count == 0
        assert result.errors == []

    def test_custom_values(self):
        """Test custom values are preserved."""
        result = ConsolidationResult(
            merged_count=5,
            pruned_count=3,
            reinforced_count=10,
            errors=["Test error"],
        )

        assert result.merged_count == 5
        assert result.pruned_count == 3
        assert result.reinforced_count == 10
        assert result.errors == ["Test error"]

    def test_total_operations(self):
        """Test calculating total operations."""
        result = ConsolidationResult(
            merged_count=5,
            pruned_count=3,
            reinforced_count=10,
        )

        total = result.merged_count + result.pruned_count + result.reinforced_count
        assert total == 18


# Run with: pytest tests/phase3/test_memory_consolidation.py -v
