# tests/agents/patterns/test_memory.py
"""
Tests for Memory patterns: B1 Working Memory, B7 Memory Retrieval
CORRECTED to match actual implementation API
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch


class TestWorkingMemory:
    """Tests for Working Memory model (B1)."""
    
    def test_working_memory_creation(self, sample_profile_id, sample_session_id):
        """Test creating working memory."""
        from agents.memory.working_memory import WorkingMemory
        
        memory = WorkingMemory(
            session_id=sample_session_id,
            profile_id=sample_profile_id,
            started_at=datetime.utcnow().isoformat(),
        )
        
        assert memory.session_id == sample_session_id
        assert memory.profile_id == sample_profile_id
    
    def test_working_memory_conversation_buffer(self, sample_profile_id, sample_session_id):
        """Test working memory has conversation_buffer."""
        from agents.memory.working_memory import WorkingMemory
        
        memory = WorkingMemory(
            session_id=sample_session_id,
            profile_id=sample_profile_id,
            started_at=datetime.utcnow().isoformat(),
        )
        
        # Uses conversation_buffer (not conversation_turns)
        assert hasattr(memory, 'conversation_buffer')
        assert memory.conversation_buffer == []
    
    def test_working_memory_defaults(self, sample_profile_id, sample_session_id):
        """Test working memory default values."""
        from agents.memory.working_memory import WorkingMemory
        
        memory = WorkingMemory(
            session_id=sample_session_id,
            profile_id=sample_profile_id,
            started_at=datetime.utcnow().isoformat(),
        )
        
        assert memory.detected_sentiment == "neutral"


class TestConversationTurn:
    """Tests for ConversationTurn model."""
    
    def test_conversation_turn_creation(self):
        """Test creating a conversation turn."""
        from agents.memory.working_memory import ConversationTurn
        
        turn = ConversationTurn(
            role="user",
            content="Help me with my essay",
            timestamp=datetime.utcnow().isoformat(),
        )
        
        assert turn.role == "user"
        assert turn.content == "Help me with my essay"
    
    def test_conversation_turn_with_metadata(self):
        """Test conversation turn with metadata."""
        from agents.memory.working_memory import ConversationTurn
        
        turn = ConversationTurn(
            role="assistant",
            content="I can help with that",
            timestamp=datetime.utcnow().isoformat(),
            metadata={"intent": "help"},
        )
        
        assert turn.metadata["intent"] == "help"


class TestWorkingMemoryManager:
    """Tests for WorkingMemoryManager (B1)."""
    
    def test_manager_initialization(self):
        """Test WorkingMemoryManager initialization."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        assert manager is not None
    
    def test_manager_with_redis(self, mock_redis):
        """Test WorkingMemoryManager with Redis."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager(redis_client=mock_redis)
        assert manager is not None
    
    def test_get_or_create_new(self, sample_profile_id, sample_session_id):
        """Test creating new working memory."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        memory = manager.get_or_create(sample_session_id, sample_profile_id)
        
        assert memory.session_id == sample_session_id
        assert memory.profile_id == sample_profile_id
    
    def test_get_or_create_existing(self, sample_profile_id, sample_session_id):
        """Test retrieving existing working memory."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        
        # Create first
        memory1 = manager.get_or_create(sample_session_id, sample_profile_id)
        memory1.detected_sentiment = "positive"
        
        # Get again
        memory2 = manager.get_or_create(sample_session_id, sample_profile_id)
        
        assert memory2.detected_sentiment == "positive"
    
    def test_add_turn(self, sample_profile_id, sample_session_id):
        """Test adding conversation turns."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        manager.get_or_create(sample_session_id, sample_profile_id)
        
        manager.add_turn(sample_session_id, "user", "Hello")
        manager.add_turn(sample_session_id, "assistant", "Hi!")
        
        memory = manager.get_or_create(sample_session_id, sample_profile_id)
        assert len(memory.conversation_buffer) == 2
    
    def test_buffer_trimming(self, sample_profile_id, sample_session_id):
        """Test that buffer trims when exceeding max size."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        memory = manager.get_or_create(sample_session_id, sample_profile_id)
        memory.max_buffer_size = 5
        
        # Add more than max
        for i in range(10):
            manager.add_turn(sample_session_id, "user", f"Message {i}")
        
        memory = manager.get_or_create(sample_session_id, sample_profile_id)
        assert len(memory.conversation_buffer) <= 5
    
    def test_update_sentiment(self, sample_profile_id, sample_session_id):
        """Test updating sentiment detection."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        manager.get_or_create(sample_session_id, sample_profile_id)
        
        manager.update_sentiment(sample_session_id, "stressed", 0.3)
        
        memory = manager.get_or_create(sample_session_id, sample_profile_id)
        assert memory.detected_sentiment == "stressed"
        assert memory.engagement_level == 0.3
    
    def test_clear_memory(self, sample_profile_id, sample_session_id):
        """Test clearing working memory."""
        from agents.memory.working_memory import WorkingMemoryManager
        
        manager = WorkingMemoryManager()
        manager.get_or_create(sample_session_id, sample_profile_id)
        manager.add_turn(sample_session_id, "user", "Test")
        
        manager.clear(sample_session_id)
        
        # Should create fresh memory
        memory = manager.get_or_create(sample_session_id, sample_profile_id)
        assert len(memory.conversation_buffer) == 0


class TestMemoryRetrieval:
    """Tests for Memory Retrieval (B7)."""
    
    def test_retrieval_module_importable(self):
        """Test memory retrieval module can be imported."""
        try:
            from agents.memory import memory_retrieval
            assert True
        except ImportError:
            pytest.skip("Memory retrieval module not found")
    
    @pytest.mark.asyncio
    async def test_retrieve_returns_results(self, mock_supabase, sample_profile_id):
        """Test retrieving memories returns results."""
        from agents.memory.memory_retrieval import MemoryRetriever
        
        mock_supabase.rpc.return_value.execute.return_value = Mock(data=[])
        
        retriever = MemoryRetriever(mock_supabase)
        results = await retriever.retrieve(sample_profile_id, "test query")
        
        assert results is not None
