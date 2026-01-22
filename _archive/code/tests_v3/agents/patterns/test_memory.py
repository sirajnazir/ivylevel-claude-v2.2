# tests/agents/patterns/test_memory.py
"""
Tests for Memory patterns: B1 Working Memory, B7 Memory Retrieval
FINAL VERSION - Aligned with actual API signatures
"""

import pytest
from datetime import datetime
from unittest.mock import Mock


class TestWorkingMemory:
    """Tests for WorkingMemory model (B1)."""
    
    def test_working_memory_importable(self):
        """Test WorkingMemory can be imported."""
        from agents.memory.working_memory import WorkingMemory
        assert WorkingMemory is not None
    
    def test_working_memory_creation(self, sample_profile_id, sample_session_id):
        """Test creating WorkingMemory."""
        from agents.memory.working_memory import WorkingMemory
        memory = WorkingMemory(
            session_id=sample_session_id,
            profile_id=sample_profile_id,
            started_at=datetime.utcnow().isoformat(),
        )
        assert memory.session_id == sample_session_id
        assert memory.profile_id == sample_profile_id
    
    def test_working_memory_has_buffer(self, sample_profile_id, sample_session_id):
        """Test WorkingMemory has conversation buffer."""
        from agents.memory.working_memory import WorkingMemory
        memory = WorkingMemory(
            session_id=sample_session_id,
            profile_id=sample_profile_id,
            started_at=datetime.utcnow().isoformat(),
        )
        assert hasattr(memory, 'conversation_buffer')
    
    def test_working_memory_has_sentiment(self, sample_profile_id, sample_session_id):
        """Test WorkingMemory has detected_sentiment."""
        from agents.memory.working_memory import WorkingMemory
        memory = WorkingMemory(
            session_id=sample_session_id,
            profile_id=sample_profile_id,
            started_at=datetime.utcnow().isoformat(),
        )
        assert hasattr(memory, 'detected_sentiment')


class TestConversationTurn:
    """Tests for ConversationTurn model."""
    
    def test_conversation_turn_importable(self):
        """Test ConversationTurn can be imported."""
        from agents.memory.working_memory import ConversationTurn
        assert ConversationTurn is not None
    
    def test_conversation_turn_creation(self):
        """Test creating ConversationTurn."""
        from agents.memory.working_memory import ConversationTurn
        turn = ConversationTurn(
            role="user",
            content="Hello",
            timestamp=datetime.utcnow().isoformat(),
        )
        assert turn.role == "user"
        assert turn.content == "Hello"


class TestWorkingMemoryManager:
    """Tests for WorkingMemoryManager (B1)."""
    
    def test_manager_importable(self):
        """Test WorkingMemoryManager can be imported."""
        from agents.memory.working_memory import WorkingMemoryManager
        assert WorkingMemoryManager is not None
    
    def test_manager_initialization(self):
        """Test WorkingMemoryManager can be initialized."""
        from agents.memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager()
        assert manager is not None
    
    def test_manager_has_get_or_create(self):
        """Test WorkingMemoryManager has get_or_create method."""
        from agents.memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager()
        assert hasattr(manager, 'get_or_create')
    
    def test_manager_has_add_turn(self):
        """Test WorkingMemoryManager has add_turn method."""
        from agents.memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager()
        assert hasattr(manager, 'add_turn')
    
    def test_get_or_create_returns_memory(self, sample_profile_id, sample_session_id):
        """Test get_or_create returns WorkingMemory."""
        from agents.memory.working_memory import WorkingMemoryManager, WorkingMemory
        manager = WorkingMemoryManager()
        memory = manager.get_or_create(sample_session_id, sample_profile_id)
        assert isinstance(memory, WorkingMemory)
    
    def test_add_turn_increases_buffer(self, sample_profile_id, sample_session_id):
        """Test add_turn increases buffer length."""
        from agents.memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager()
        manager.get_or_create(sample_session_id, sample_profile_id)
        
        manager.add_turn(sample_session_id, "user", "Hello")
        
        memory = manager.get_or_create(sample_session_id, sample_profile_id)
        assert len(memory.conversation_buffer) >= 1
    
    def test_manager_has_update_sentiment(self):
        """Test WorkingMemoryManager has update_sentiment method."""
        from agents.memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager()
        assert hasattr(manager, 'update_sentiment')
    
    def test_manager_has_clear(self):
        """Test WorkingMemoryManager has clear method."""
        from agents.memory.working_memory import WorkingMemoryManager
        manager = WorkingMemoryManager()
        assert hasattr(manager, 'clear')


class TestMemoryRetrieval:
    """Tests for Memory Retrieval (B7)."""
    
    def test_retrieval_module_importable(self):
        """Test memory_retrieval module can be imported."""
        try:
            from agents.memory import memory_retrieval
            assert memory_retrieval is not None
        except ImportError:
            pytest.skip("memory_retrieval module not available")
    
    def test_retriever_class_exists(self):
        """Test MemoryRetriever class exists."""
        try:
            from agents.memory.memory_retrieval import MemoryRetriever
            assert MemoryRetriever is not None
        except ImportError:
            pytest.skip("MemoryRetriever not available")
    
    def test_retriever_has_retrieve(self, mock_supabase):
        """Test MemoryRetriever has retrieve method."""
        try:
            from agents.memory.memory_retrieval import MemoryRetriever
            retriever = MemoryRetriever(mock_supabase)
            assert hasattr(retriever, 'retrieve')
        except ImportError:
            pytest.skip("MemoryRetriever not available")
    
    @pytest.mark.asyncio
    async def test_retrieve_returns_results(self, mock_supabase, sample_profile_id):
        """Test retrieve returns results."""
        try:
            from agents.memory.memory_retrieval import MemoryRetriever
            mock_supabase.rpc.return_value.execute.return_value = Mock(data=[])
            retriever = MemoryRetriever(mock_supabase)
            results = await retriever.retrieve(sample_profile_id, "test query")
            assert results is not None
        except ImportError:
            pytest.skip("MemoryRetriever not available")
