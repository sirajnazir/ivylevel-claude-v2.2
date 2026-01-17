"""
Memory Patterns - v5.4 True Autonomous Agents

Patterns implemented:
- B1: Working Memory (3P: Redis)
- B7: Memory Retrieval (3P: Supabase pgvector)
"""

from .working_memory import (
    WorkingMemoryManager,
    create_session_id,
    get_working_memory,
    # Signal detection constants (USP)
    STRESS_INDICATORS,
    CONFUSION_INDICATORS,
    EXCITEMENT_INDICATORS,
    FRUSTRATION_INDICATORS,
)

from .memory_retrieval import (
    MemoryRetriever,
    MemoryItem,
    RetrievalResult,
    ConversationMemory,
    FactMemory,
    retrieve_memories,
)

__all__ = [
    # Working Memory (B1)
    "WorkingMemoryManager",
    "create_session_id",
    "get_working_memory",
    "STRESS_INDICATORS",
    "CONFUSION_INDICATORS",
    "EXCITEMENT_INDICATORS",
    "FRUSTRATION_INDICATORS",
    # Memory Retrieval (B7)
    "MemoryRetriever",
    "MemoryItem",
    "RetrievalResult",
    "ConversationMemory",
    "FactMemory",
    "retrieve_memories",
]
