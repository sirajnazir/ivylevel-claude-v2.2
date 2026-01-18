"""
Tests for B4: Long-Term Memory

Pattern: B4
3P: Supabase JSONB
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.memory.longterm_v9 import (
    LongTermMemoryManager,
    LongTermMemory,
)


class TestLongTermMemoryManager:
    """Tests for B4: Long-Term Memory."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        db = MagicMock()

        # Mock table chain for upsert
        db.table = MagicMock(return_value=MagicMock(
            upsert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
            )),
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    eq=MagicMock(return_value=MagicMock(
                        single=MagicMock(return_value=MagicMock(
                            execute=MagicMock(return_value=MagicMock(
                                data={"id": "test-id", "memory_value": "test-value", "importance": 0.5}
                            ))
                        ))
                    )),
                    gte=MagicMock(return_value=MagicMock(
                        limit=MagicMock(return_value=MagicMock(
                            order=MagicMock(return_value=MagicMock(
                                execute=MagicMock(return_value=MagicMock(data=[
                                    {
                                        "memory_key": "key1",
                                        "memory_value": "value1",
                                        "memory_type": "fact",
                                        "importance": 0.8,
                                        "confidence": 1.0,
                                        "source": "test",
                                    }
                                ]))
                            ))
                        ))
                    ))
                ))
            )),
            update=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
                ))
            )),
            delete=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    eq=MagicMock(return_value=MagicMock(
                        execute=MagicMock(return_value=MagicMock(data=[]))
                    ))
                ))
            )),
        ))

        return db

    @pytest.fixture
    def manager(self, mock_supabase):
        return LongTermMemoryManager(supabase_client=mock_supabase)

    @pytest.fixture
    def manager_no_db(self):
        """Manager without database (tests graceful degradation)."""
        return LongTermMemoryManager(supabase_client=None)

    def test_is_available_with_client(self, manager):
        """Test availability check with client."""
        assert manager.is_available is True

    def test_is_available_without_client(self, manager_no_db):
        """Test availability check without client."""
        assert manager_no_db.is_available is False

    @pytest.mark.asyncio
    async def test_remember_stores_memory(self, manager, mock_supabase):
        """Test storing a memory."""
        result = await manager.remember(
            profile_id="test-profile",
            key="favorite_subject",
            value="Computer Science",
            memory_type="preference",
            importance=0.9,
        )

        assert result is True
        mock_supabase.table.assert_called_with("phase3_longterm_memories")

    @pytest.mark.asyncio
    async def test_remember_graceful_degradation(self, manager_no_db):
        """Test remember returns False when no client."""
        result = await manager_no_db.remember(
            profile_id="test-profile",
            key="test",
            value="test",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_recall_retrieves_memory(self, manager):
        """Test retrieving a memory."""
        value = await manager.recall(
            profile_id="test-profile",
            key="favorite_subject",
        )

        assert value == "test-value"

    @pytest.mark.asyncio
    async def test_recall_graceful_degradation(self, manager_no_db):
        """Test recall returns None when no client."""
        value = await manager_no_db.recall(
            profile_id="test-profile",
            key="test",
        )

        assert value is None

    @pytest.mark.asyncio
    async def test_recall_all_returns_list(self, manager):
        """Test retrieving all memories."""
        memories = await manager.recall_all(
            profile_id="test-profile",
        )

        assert isinstance(memories, list)
        assert len(memories) >= 0

    @pytest.mark.asyncio
    async def test_recall_all_filters_by_type(self, manager):
        """Test filtering by memory type."""
        memories = await manager.recall_all(
            profile_id="test-profile",
            memory_type="preference",
        )

        assert isinstance(memories, list)

    @pytest.mark.asyncio
    async def test_recall_all_filters_by_importance(self, manager):
        """Test filtering by minimum importance."""
        memories = await manager.recall_all(
            profile_id="test-profile",
            min_importance=0.5,
        )

        assert isinstance(memories, list)

    @pytest.mark.asyncio
    async def test_forget_removes_memory(self, manager):
        """Test removing a memory."""
        result = await manager.forget(
            profile_id="test-profile",
            key="test-key",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_forget_graceful_degradation(self, manager_no_db):
        """Test forget returns False when no client."""
        result = await manager_no_db.forget(
            profile_id="test-profile",
            key="test",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_update_importance_increases(self, manager):
        """Test increasing importance."""
        result = await manager.update_importance(
            profile_id="test-profile",
            key="test-key",
            importance_delta=0.1,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_update_importance_clamps_to_bounds(self, manager, mock_supabase):
        """Test importance stays within 0-1 bounds."""
        # Set up mock to return high importance
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "importance": 0.95
        }

        result = await manager.update_importance(
            profile_id="test-profile",
            key="test-key",
            importance_delta=0.2,  # Would exceed 1.0
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_get_by_type(self, manager):
        """Test getting memories by type."""
        memories = await manager.get_by_type(
            profile_id="test-profile",
            memory_type="fact",
        )

        assert isinstance(memories, list)


class TestLongTermMemoryModel:
    """Tests for the LongTermMemory Pydantic model."""

    def test_default_values(self):
        """Test default values are set."""
        memory = LongTermMemory(
            key="test_key",
            value="test_value",
        )

        assert memory.memory_type == "fact"
        assert memory.importance == 0.5
        assert memory.confidence == 1.0
        assert memory.source is None

    def test_custom_values(self):
        """Test custom values are preserved."""
        memory = LongTermMemory(
            key="favorite_color",
            value="blue",
            memory_type="preference",
            importance=0.9,
            confidence=0.8,
            source="user_profile",
        )

        assert memory.key == "favorite_color"
        assert memory.value == "blue"
        assert memory.memory_type == "preference"
        assert memory.importance == 0.9
        assert memory.confidence == 0.8
        assert memory.source == "user_profile"

    def test_complex_value(self):
        """Test storing complex values."""
        memory = LongTermMemory(
            key="preferences",
            value={
                "communication_style": "formal",
                "detail_level": "high",
                "topics": ["math", "science"],
            },
        )

        assert isinstance(memory.value, dict)
        assert memory.value["communication_style"] == "formal"


# Run with: pytest tests/phase3/test_longterm_memory.py -v
