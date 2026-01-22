# tests/patterns/test_memory.py
"""
Tests for Memory patterns: B1 Working Memory, B7 Memory Retrieval
CORRECTED to match actual implementation
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock


class TestWorkingMemoryManager:
    """Tests for WorkingMemoryManager (B1)."""
    
    def test_manager_importable(self):
        """Test WorkingMemoryManager can be imported."""
        from memory.working_memory import WorkingMemoryManager
        assert WorkingMemoryManager is not None
    
    def test_manager_initialization(self):
        """Test WorkingMemoryManager can be initialized without arguments."""
        from memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager()
        assert manager is not None
    
    def test_manager_with_redis(self, mock_redis):
        """Test WorkingMemoryManager with Redis client."""
        from memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager(redis_client=mock_redis)
        assert manager.redis == mock_redis
    
    @pytest.mark.asyncio
    async def test_get_or_create_returns_working_memory(self):
        """Test get_or_create returns WorkingMemory."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import WorkingMemory
        
        manager = WorkingMemoryManager()
        memory = await manager.get_or_create("session-123", "profile-456")
        
        assert isinstance(memory, WorkingMemory)
        assert memory.session_id == "session-123"
        assert memory.profile_id == "profile-456"
    
    @pytest.mark.asyncio
    async def test_get_or_create_caches_memory(self):
        """Test get_or_create caches and returns same memory."""
        from memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        memory1 = await manager.get_or_create("session-123", "profile-456")
        memory2 = await manager.get_or_create("session-123", "profile-456")
        
        assert memory1 is memory2
    
    @pytest.mark.asyncio
    async def test_add_turn_returns_updated_memory(self):
        """Test add_turn updates and returns WorkingMemory."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import ConversationRole
        
        manager = WorkingMemoryManager()
        await manager.get_or_create("session-123", "profile-456")
        
        memory = await manager.add_turn(
            "session-123",
            ConversationRole.USER,
            "Hello, can you help me?",
        )
        
        assert len(memory.conversation_buffer) == 1
        assert memory.conversation_buffer[0].content == "Hello, can you help me?"
    
    @pytest.mark.asyncio
    async def test_add_turn_with_metadata(self):
        """Test add_turn with metadata."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import ConversationRole
        
        manager = WorkingMemoryManager()
        await manager.get_or_create("session-123", "profile-456")
        
        memory = await manager.add_turn(
            "session-123",
            ConversationRole.USER,
            "Test message",
            metadata={"source": "web"},
        )
        
        assert memory.conversation_buffer[0].metadata["source"] == "web"
    
    @pytest.mark.asyncio
    async def test_add_turn_detects_stress(self):
        """Test add_turn detects stress signals."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import ConversationRole
        
        manager = WorkingMemoryManager()
        await manager.get_or_create("session-123", "profile-456")
        
        memory = await manager.add_turn(
            "session-123",
            ConversationRole.USER,
            "I'm so stressed and overwhelmed with deadlines",
        )
        
        # Should detect stress signals
        assert memory.detected_sentiment == "stressed"
        assert len(memory.recent_signals) > 0
        assert any(s.signal_type == "stress" for s in memory.recent_signals)
    
    @pytest.mark.asyncio
    async def test_add_turn_detects_excitement(self):
        """Test add_turn detects excitement signals."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import ConversationRole
        
        manager = WorkingMemoryManager()
        await manager.get_or_create("session-123", "profile-456")
        
        memory = await manager.add_turn(
            "session-123",
            ConversationRole.USER,
            "I'm so excited about this amazing opportunity!",
        )
        
        # Should detect excitement
        assert any(s.signal_type == "excitement" for s in memory.recent_signals)
    
    @pytest.mark.asyncio
    async def test_add_turn_trims_buffer(self):
        """Test add_turn trims buffer when too long."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import ConversationRole
        
        manager = WorkingMemoryManager()
        memory = await manager.get_or_create("session-123", "profile-456")
        
        # Add more turns than max buffer size
        for i in range(memory.max_buffer_size + 5):
            await manager.add_turn(
                "session-123",
                ConversationRole.USER,
                f"Message {i}",
            )
        
        # Should be trimmed to max size
        assert len(memory.conversation_buffer) <= memory.max_buffer_size
    
    def test_set_current_task(self):
        """Test set_current_task updates memory."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import WorkingMemory
        
        manager = WorkingMemoryManager()
        manager._memories["session-123"] = WorkingMemory(
            session_id="session-123",
            profile_id="profile-456",
        )
        
        manager.set_current_task("session-123", "task-789")
        
        assert manager._memories["session-123"].current_task == "task-789"
    
    def test_set_current_agent(self):
        """Test set_current_agent updates memory."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import WorkingMemory
        
        manager = WorkingMemoryManager()
        manager._memories["session-123"] = WorkingMemory(
            session_id="session-123",
            profile_id="profile-456",
        )
        
        manager.set_current_agent("session-123", "ec_agent")
        
        assert manager._memories["session-123"].current_agent == "ec_agent"
    
    def test_add_fact(self):
        """Test add_fact adds to session facts."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import WorkingMemory
        
        manager = WorkingMemoryManager()
        manager._memories["session-123"] = WorkingMemory(
            session_id="session-123",
            profile_id="profile-456",
        )
        
        manager.add_fact("session-123", "Student prefers STEM activities")
        
        assert "Student prefers STEM activities" in manager._memories["session-123"].session_facts
    
    def test_get_recent_context(self):
        """Test get_recent_context returns formatted turns."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import WorkingMemory, ConversationTurn, ConversationRole
        
        manager = WorkingMemoryManager()
        memory = WorkingMemory(
            session_id="session-123",
            profile_id="profile-456",
        )
        memory.conversation_buffer = [
            ConversationTurn(role=ConversationRole.USER, content="Hello"),
            ConversationTurn(role=ConversationRole.ASSISTANT, content="Hi there!"),
        ]
        manager._memories["session-123"] = memory
        
        context = manager.get_recent_context("session-123", max_turns=5)
        
        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[0]["content"] == "Hello"
    
    def test_update_scratchpad(self):
        """Test update_scratchpad stores intermediate results."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import WorkingMemory
        
        manager = WorkingMemoryManager()
        manager._memories["session-123"] = WorkingMemory(
            session_id="session-123",
            profile_id="profile-456",
        )
        
        manager.update_scratchpad("session-123", "analysis_result", {"score": 85})
        
        assert manager._memories["session-123"].scratchpad["analysis_result"]["score"] == 85
    
    def test_get_scratchpad(self):
        """Test get_scratchpad retrieves values."""
        from memory.working_memory import WorkingMemoryManager
        from context.types import WorkingMemory
        
        manager = WorkingMemoryManager()
        memory = WorkingMemory(session_id="session-123", profile_id="profile-456")
        memory.scratchpad["key"] = "value"
        manager._memories["session-123"] = memory
        
        result = manager.get_scratchpad("session-123", "key")
        
        assert result == "value"
    
    @pytest.mark.asyncio
    async def test_clear_session(self):
        """Test clear_session removes memory."""
        from memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        await manager.get_or_create("session-123", "profile-456")
        
        await manager.clear_session("session-123")
        
        assert "session-123" not in manager._memories


class TestCreateSessionId:
    """Tests for create_session_id helper."""
    
    def test_create_session_id_exists(self):
        """Test create_session_id function exists."""
        from memory.working_memory import create_session_id
        assert create_session_id is not None
    
    def test_create_session_id_returns_string(self):
        """Test create_session_id returns unique string."""
        from memory.working_memory import create_session_id
        
        id1 = create_session_id()
        id2 = create_session_id()
        
        assert isinstance(id1, str)
        assert id1 != id2


class TestMemoryRetriever:
    """Tests for MemoryRetriever (B7)."""
    
    def test_retriever_importable(self):
        """Test MemoryRetriever can be imported."""
        from memory.memory_retrieval import MemoryRetriever
        assert MemoryRetriever is not None
    
    def test_retriever_initialization(self):
        """Test MemoryRetriever can be initialized without arguments."""
        from memory.memory_retrieval import MemoryRetriever
        retriever = MemoryRetriever()
        assert retriever is not None
    
    def test_retriever_with_supabase(self, mock_supabase):
        """Test MemoryRetriever with Supabase client."""
        from memory.memory_retrieval import MemoryRetriever
        retriever = MemoryRetriever(supabase_client=mock_supabase)
        assert retriever.supabase == mock_supabase
    
    @pytest.mark.asyncio
    async def test_retrieve_returns_retrieval_result(self, mock_supabase):
        """Test retrieve returns RetrievalResult."""
        from memory.memory_retrieval import MemoryRetriever, RetrievalResult
        
        retriever = MemoryRetriever(supabase_client=mock_supabase)
        result = await retriever.retrieve(
            query="test query",
            profile_id="profile-123",
        )
        
        assert isinstance(result, RetrievalResult)
        assert result.query == "test query"
    
    @pytest.mark.asyncio
    async def test_retrieve_with_memory_type_filter(self, mock_supabase):
        """Test retrieve with memory type filter."""
        from memory.memory_retrieval import MemoryRetriever
        
        retriever = MemoryRetriever(supabase_client=mock_supabase)
        result = await retriever.retrieve(
            query="test",
            profile_id="profile-123",
            memory_type="conversation",
        )
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_retrieve_with_limit(self, mock_supabase):
        """Test retrieve with limit."""
        from memory.memory_retrieval import MemoryRetriever
        
        retriever = MemoryRetriever(supabase_client=mock_supabase)
        result = await retriever.retrieve(
            query="test",
            profile_id="profile-123",
            limit=10,
        )
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_store_memory_returns_memory_item(self):
        """Test store_memory returns MemoryItem."""
        from memory.memory_retrieval import MemoryRetriever, MemoryItem
        
        retriever = MemoryRetriever()
        item = await retriever.store_memory(
            profile_id="profile-123",
            content="Student expressed interest in AI research",
            memory_type="fact",
        )
        
        assert isinstance(item, MemoryItem)
        assert item.content == "Student expressed interest in AI research"
        assert item.type == "fact"
    
    @pytest.mark.asyncio
    async def test_store_memory_with_metadata(self):
        """Test store_memory with metadata."""
        from memory.memory_retrieval import MemoryRetriever
        
        retriever = MemoryRetriever()
        item = await retriever.store_memory(
            profile_id="profile-123",
            content="Test content",
            memory_type="fact",
            metadata={"category": "interest"},
        )
        
        assert item.metadata["category"] == "interest"
    
    @pytest.mark.asyncio
    async def test_get_recent_memories(self, mock_supabase):
        """Test get_recent_memories returns list."""
        from memory.memory_retrieval import MemoryRetriever
        
        retriever = MemoryRetriever(supabase_client=mock_supabase)
        memories = await retriever.get_recent_memories(
            profile_id="profile-123",
            limit=5,
        )
        
        assert isinstance(memories, list)


class TestMemoryItem:
    """Tests for MemoryItem model."""
    
    def test_memory_item_importable(self):
        """Test MemoryItem can be imported."""
        from memory.memory_retrieval import MemoryItem
        assert MemoryItem is not None
    
    def test_memory_item_creation(self):
        """Test creating a MemoryItem."""
        from memory.memory_retrieval import MemoryItem
        
        item = MemoryItem(
            id="mem-1",
            content="Test content",
            type="fact",
            profile_id="profile-123",
        )
        
        assert item.id == "mem-1"
        assert item.content == "Test content"
        assert item.type == "fact"


class TestRetrievalResult:
    """Tests for RetrievalResult model."""
    
    def test_retrieval_result_importable(self):
        """Test RetrievalResult can be imported."""
        from memory.memory_retrieval import RetrievalResult
        assert RetrievalResult is not None
    
    def test_retrieval_result_creation(self):
        """Test creating a RetrievalResult."""
        from memory.memory_retrieval import RetrievalResult
        
        result = RetrievalResult(
            memories=[],
            query="test",
            method="keyword",
        )
        
        assert result.query == "test"
        assert result.method == "keyword"


class TestConversationMemory:
    """Tests for ConversationMemory helper."""
    
    def test_conversation_memory_importable(self):
        """Test ConversationMemory can be imported."""
        from memory.memory_retrieval import ConversationMemory
        assert ConversationMemory is not None
    
    def test_conversation_memory_initialization(self):
        """Test ConversationMemory initialization."""
        from memory.memory_retrieval import ConversationMemory, MemoryRetriever
        
        retriever = MemoryRetriever()
        conv_memory = ConversationMemory(retriever)
        
        assert conv_memory.retriever == retriever


class TestFactMemory:
    """Tests for FactMemory helper."""
    
    def test_fact_memory_importable(self):
        """Test FactMemory can be imported."""
        from memory.memory_retrieval import FactMemory
        assert FactMemory is not None
    
    def test_fact_memory_initialization(self):
        """Test FactMemory initialization."""
        from memory.memory_retrieval import FactMemory, MemoryRetriever
        
        retriever = MemoryRetriever()
        fact_memory = FactMemory(retriever)
        
        assert fact_memory.retriever == retriever
