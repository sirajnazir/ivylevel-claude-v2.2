"""
Tests for B3: Semantic Memory

Pattern: B3
3P: Supabase pgvector + OpenAI embeddings
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.memory.semantic_v9 import (
    SemanticMemoryManager,
    SemanticMemory,
)


class TestSemanticMemoryManager:
    """Tests for B3: Semantic Memory."""

    @pytest.fixture
    def mock_embedding(self):
        """Mock embedding vector."""
        return [0.1] * 1536  # 1536 dimensions for text-embedding-3-small

    @pytest.fixture
    def mock_openai(self, mock_embedding):
        """Mock OpenAI client."""
        client = MagicMock()
        client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)]
        )
        return client

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        db = MagicMock()

        # Mock table operations
        db.table = MagicMock(return_value=MagicMock(
            insert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
            )),
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    eq=MagicMock(return_value=MagicMock(
                        order=MagicMock(return_value=MagicMock(
                            limit=MagicMock(return_value=MagicMock(
                                execute=MagicMock(return_value=MagicMock(data=[
                                    {
                                        "id": "mem-1",
                                        "content": "Test memory content",
                                        "memory_type": "general",
                                        "importance": 0.8,
                                        "metadata": {},
                                    }
                                ]))
                            ))
                        ))
                    )),
                    execute=MagicMock(return_value=MagicMock(count=5))
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

        # Mock RPC for vector search
        db.rpc = MagicMock(return_value=MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[
                {
                    "content": "Similar memory content",
                    "memory_type": "insight",
                    "importance": 0.9,
                    "similarity": 0.85,
                    "metadata": {"source": "test"},
                }
            ]))
        ))

        return db

    @pytest.fixture
    def manager(self, mock_supabase, mock_openai):
        return SemanticMemoryManager(
            supabase_client=mock_supabase,
            openai_client=mock_openai,
        )

    @pytest.fixture
    def manager_no_clients(self):
        """Manager without clients (tests graceful degradation)."""
        return SemanticMemoryManager(supabase_client=None, openai_client=None)

    @pytest.fixture
    def manager_no_openai(self, mock_supabase):
        """Manager without OpenAI (tests partial degradation)."""
        return SemanticMemoryManager(supabase_client=mock_supabase, openai_client=None)

    def test_is_available_with_clients(self, manager):
        """Test availability check with both clients."""
        assert manager.is_available is True

    def test_is_available_without_clients(self, manager_no_clients):
        """Test availability check without clients."""
        assert manager_no_clients.is_available is False

    def test_is_available_partial_clients(self, manager_no_openai):
        """Test availability requires both clients."""
        assert manager_no_openai.is_available is False

    @pytest.mark.asyncio
    async def test_store_creates_embedding_and_stores(self, manager, mock_openai, mock_supabase):
        """Test storing a memory generates embedding and stores."""
        result = await manager.store(
            profile_id="test-profile",
            content="User prefers detailed explanations",
            memory_type="preference",
            importance=0.8,
        )

        assert result is True
        mock_openai.embeddings.create.assert_called_once()
        mock_supabase.table.assert_called_with("phase3_semantic_memories")

    @pytest.mark.asyncio
    async def test_store_with_metadata(self, manager):
        """Test storing a memory with metadata."""
        result = await manager.store(
            profile_id="test-profile",
            content="Test content",
            metadata={"source": "conversation", "turn": 5},
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_store_graceful_degradation(self, manager_no_clients):
        """Test store returns False when no clients."""
        result = await manager_no_clients.store(
            profile_id="test-profile",
            content="Test content",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_search_uses_vector_similarity(self, manager, mock_supabase):
        """Test search uses RPC for vector similarity."""
        memories = await manager.search(
            profile_id="test-profile",
            query="What does the user prefer?",
            limit=5,
            min_similarity=0.7,
        )

        assert isinstance(memories, list)
        assert len(memories) == 1
        assert memories[0].similarity == 0.85
        mock_supabase.rpc.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_filters_by_type(self, manager, mock_supabase):
        """Test search can filter by memory type."""
        await manager.search(
            profile_id="test-profile",
            query="test query",
            memory_type="insight",
        )

        # Verify RPC was called with memory_type parameter
        call_args = mock_supabase.rpc.call_args
        assert "p_memory_type" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_search_graceful_degradation(self, manager_no_clients):
        """Test search returns empty list when no clients."""
        memories = await manager_no_clients.search(
            profile_id="test-profile",
            query="test query",
        )

        assert memories == []

    @pytest.mark.asyncio
    async def test_get_by_type_returns_memories(self, manager):
        """Test getting memories by type."""
        memories = await manager.get_by_type(
            profile_id="test-profile",
            memory_type="general",
        )

        assert isinstance(memories, list)

    @pytest.mark.asyncio
    async def test_delete_removes_memory(self, manager):
        """Test deleting a memory."""
        result = await manager.delete(
            profile_id="test-profile",
            memory_id="mem-123",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_graceful_degradation(self, manager_no_clients):
        """Test delete returns False when no clients."""
        result = await manager_no_clients.delete(
            profile_id="test-profile",
            memory_id="mem-123",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_count_returns_integer(self, manager):
        """Test counting memories."""
        count = await manager.count(profile_id="test-profile")

        assert isinstance(count, int)

    @pytest.mark.asyncio
    async def test_count_graceful_degradation(self, manager_no_clients):
        """Test count returns 0 when no clients."""
        count = await manager_no_clients.count(profile_id="test-profile")

        assert count == 0


class TestSemanticMemoryModel:
    """Tests for the SemanticMemory Pydantic model."""

    def test_default_values(self):
        """Test default values are set."""
        memory = SemanticMemory(content="Test content")

        assert memory.memory_type == "general"
        assert memory.importance == 0.5
        assert memory.similarity is None
        assert memory.metadata == {}

    def test_custom_values(self):
        """Test custom values are preserved."""
        memory = SemanticMemory(
            content="User enjoys mathematics",
            memory_type="preference",
            importance=0.9,
            similarity=0.85,
            metadata={"source": "profile"},
        )

        assert memory.content == "User enjoys mathematics"
        assert memory.memory_type == "preference"
        assert memory.importance == 0.9
        assert memory.similarity == 0.85
        assert memory.metadata == {"source": "profile"}

    def test_similarity_from_search(self):
        """Test similarity can be set from search results."""
        memory = SemanticMemory(
            content="Retrieved memory",
            similarity=0.92,
        )

        assert memory.similarity == 0.92


# Run with: pytest tests/phase3/test_semantic_memory.py -v
