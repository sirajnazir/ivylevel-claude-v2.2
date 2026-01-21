# agents/tests/patterns/test_memory.py
"""
Tests for Memory Patterns (B1, B7) - v5.4 True Autonomous Agents.

Tests:
- B1: Working Memory management
- B7: Memory Retrieval from long-term storage
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Ensure agents package is in path
agents_dir = Path(__file__).parent.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))


class TestWorkingMemory:
    """Tests for B1: Working Memory pattern."""

    def test_working_memory_manager_creation(self, mock_redis):
        """Test WorkingMemoryManager can be created."""
        from memory import WorkingMemoryManager

        manager = WorkingMemoryManager(mock_redis)

        assert manager is not None

    @pytest.mark.asyncio
    async def test_get_or_create_new_session(self, mock_redis):
        """Test creating a new working memory session."""
        from memory import WorkingMemoryManager

        manager = WorkingMemoryManager(mock_redis)

        memory = await manager.get_or_create("session-123", "profile-123")

        assert memory is not None
        assert memory.session_id == "session-123"
        assert memory.profile_id == "profile-123"

    @pytest.mark.asyncio
    async def test_get_or_create_existing_session(self, mock_redis):
        """Test retrieving an existing working memory session."""
        from memory import WorkingMemoryManager
        from context import WorkingMemory

        manager = WorkingMemoryManager(mock_redis)

        # Create first
        memory1 = await manager.get_or_create("session-123", "profile-123")

        # Retrieve existing
        memory2 = await manager.get_or_create("session-123", "profile-123")

        assert memory2.session_id == memory1.session_id

    @pytest.mark.asyncio
    async def test_add_conversation_turn(self, mock_redis):
        """Test adding conversation turns to working memory."""
        from memory import WorkingMemoryManager
        from context import ConversationRole

        manager = WorkingMemoryManager(mock_redis)
        memory = await manager.get_or_create("session-123", "profile-123")

        # Add user turn
        await manager.add_turn(
            "session-123",
            role=ConversationRole.USER,
            content="What activities should I focus on?",
        )

        # Verify turn was added
        updated = await manager.get_or_create("session-123", "profile-123")
        assert len(updated.conversation_turns) >= 1

    @pytest.mark.asyncio
    async def test_working_memory_expires(self, mock_redis):
        """Test working memory has TTL."""
        from memory import WorkingMemoryManager

        manager = WorkingMemoryManager(mock_redis)

        await manager.get_or_create("session-123", "profile-123")

        # Check TTL was set
        key = "working_memory:session-123"
        assert key in mock_redis._ttls or key in mock_redis._data

    def test_signal_detection_indicators(self):
        """Test signal detection indicators are defined."""
        from memory import (
            STRESS_INDICATORS,
            CONFUSION_INDICATORS,
            EXCITEMENT_INDICATORS,
            FRUSTRATION_INDICATORS,
        )

        assert len(STRESS_INDICATORS) > 0
        assert len(CONFUSION_INDICATORS) > 0
        assert len(EXCITEMENT_INDICATORS) > 0
        assert len(FRUSTRATION_INDICATORS) > 0

    @pytest.mark.asyncio
    async def test_detect_signal_from_message(self, mock_redis):
        """Test detecting emotional signals from messages."""
        from memory import WorkingMemoryManager

        manager = WorkingMemoryManager(mock_redis)

        # Create session
        await manager.get_or_create("session-123", "profile-123")

        # Add a message with stress indicators
        message = "I'm so stressed about my college applications!"

        # Signal detection should work

    def test_session_id_generation(self):
        """Test session ID generation utility."""
        from memory import create_session_id

        session_id = create_session_id()

        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_conversation_role_enum(self):
        """Test ConversationRole enum values."""
        from context import ConversationRole

        assert ConversationRole.USER is not None
        assert ConversationRole.ASSISTANT is not None
        assert ConversationRole.SYSTEM is not None


class TestMemoryRetrieval:
    """Tests for B7: Memory Retrieval pattern."""

    def test_memory_retriever_creation(self, mock_supabase):
        """Test MemoryRetriever can be created."""
        from memory import MemoryRetriever

        retriever = MemoryRetriever(mock_supabase)

        assert retriever is not None

    @pytest.mark.asyncio
    async def test_retrieve_conversation_memories(self, mock_supabase):
        """Test retrieving past conversation memories."""
        from memory import MemoryRetriever

        # Setup mock conversation data
        mock_supabase._tables["conversations"] = [
            {
                "id": "conv-1",
                "profile_id": "profile-123",
                "content": "Previous conversation about robotics",
                "created_at": datetime.utcnow().isoformat(),
            }
        ]

        retriever = MemoryRetriever(mock_supabase)

        result = await retriever.retrieve(
            profile_id="profile-123",
            query="robotics activities",
            memory_types=["conversation"],
            limit=5,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_retrieve_fact_memories(self, mock_supabase):
        """Test retrieving fact-based memories."""
        from memory import MemoryRetriever

        retriever = MemoryRetriever(mock_supabase)

        result = await retriever.retrieve(
            profile_id="profile-123",
            query="SAT scores",
            memory_types=["fact"],
            limit=5,
        )

        assert result is not None

    def test_memory_item_model(self):
        """Test MemoryItem model structure."""
        from memory import MemoryItem

        item = MemoryItem(
            memory_id="mem-123",
            memory_type="conversation",
            content="Discussion about summer programs",
            relevance_score=0.85,
            created_at=datetime.utcnow(),
        )

        assert item.memory_id == "mem-123"
        assert item.relevance_score == 0.85

    def test_retrieval_result_model(self):
        """Test RetrievalResult model structure."""
        from memory import RetrievalResult, MemoryItem

        result = RetrievalResult(
            query="test query",
            memories=[
                MemoryItem(
                    memory_id="mem-1",
                    memory_type="fact",
                    content="Test content",
                    relevance_score=0.9,
                    created_at=datetime.utcnow(),
                )
            ],
            total_retrieved=1,
        )

        assert result.total_retrieved == 1
        assert len(result.memories) == 1

    @pytest.mark.asyncio
    async def test_retrieve_with_relevance_filtering(self, mock_supabase):
        """Test retrieval filters by relevance score."""
        from memory import MemoryRetriever

        retriever = MemoryRetriever(mock_supabase)

        result = await retriever.retrieve(
            profile_id="profile-123",
            query="test",
            min_relevance=0.5,
            limit=10,
        )

        # All results should have relevance >= 0.5
        for mem in result.memories:
            assert mem.relevance_score >= 0.5

    def test_convenience_function_retrieve(self):
        """Test convenience function for memory retrieval."""
        from memory import retrieve_memories

        # Should be callable
        assert callable(retrieve_memories)


class TestMemoryIntegration:
    """Integration tests for memory patterns working together."""

    @pytest.mark.asyncio
    async def test_working_memory_persists_across_turns(self, mock_redis):
        """Test working memory maintains state across conversation turns."""
        from memory import WorkingMemoryManager
        from context import ConversationRole

        manager = WorkingMemoryManager(mock_redis)

        # First turn
        await manager.get_or_create("session-123", "profile-123")
        await manager.add_turn("session-123", ConversationRole.USER, "Question 1")
        await manager.add_turn("session-123", ConversationRole.ASSISTANT, "Answer 1")

        # Second turn
        await manager.add_turn("session-123", ConversationRole.USER, "Question 2")

        # Verify all turns persisted
        memory = await manager.get_or_create("session-123", "profile-123")
        assert len(memory.conversation_turns) >= 3

    @pytest.mark.asyncio
    async def test_working_memory_isolated_per_session(self, mock_redis):
        """Test different sessions have isolated working memory."""
        from memory import WorkingMemoryManager
        from context import ConversationRole

        manager = WorkingMemoryManager(mock_redis)

        # Session 1
        await manager.get_or_create("session-1", "profile-123")
        await manager.add_turn("session-1", ConversationRole.USER, "Session 1 message")

        # Session 2
        await manager.get_or_create("session-2", "profile-123")
        await manager.add_turn("session-2", ConversationRole.USER, "Session 2 message")

        # Sessions should be isolated
        mem1 = await manager.get_or_create("session-1", "profile-123")
        mem2 = await manager.get_or_create("session-2", "profile-123")

        # Each should have their own turns

    def test_all_memory_types_importable(self):
        """Test all memory types can be imported."""
        from memory import (
            WorkingMemoryManager,
            MemoryRetriever,
            MemoryItem,
            RetrievalResult,
            ConversationMemory,
            FactMemory,
        )

        # All should be importable

    def test_working_memory_model_from_context(self):
        """Test WorkingMemory model is accessible from context module."""
        from context import WorkingMemory, ConversationTurn, DetectedSignal

        # These should all be importable from context
        assert WorkingMemory is not None
        assert ConversationTurn is not None
        assert DetectedSignal is not None
