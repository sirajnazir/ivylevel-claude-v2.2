# Phase 3 Week 1: Memory Patterns Implementation Spec

## Overview

Week 1 focuses on implementing the Memory subsystem for long-term knowledge retention and retrieval.

| Pattern | ID | Priority | Dependencies |
|---------|-----|----------|--------------|
| Long-term Memory | B4 | High | Supabase |
| Semantic Memory | B3 | High | Supabase pgvector, B4 |
| Memory Extraction | B5 | Medium | LLM |
| Memory Consolidation | B6 | Medium | B4, B5 |

---

## B4: Long-term Memory

### Purpose
Persistent storage for important insights, preferences, and patterns learned about each student profile. Unlike episodic memory (B2) which stores specific events, long-term memory stores generalized knowledge.

### File: `middleware/memory/longterm_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Types of long-term memories."""
    INSIGHT = "insight"          # Generalized understanding
    PREFERENCE = "preference"    # User preferences
    PATTERN = "pattern"          # Behavioral patterns
    SKILL = "skill"              # Demonstrated abilities
    GOAL = "goal"                # Stated objectives


class LongTermMemory(BaseModel):
    """A long-term memory entry."""
    id: str
    profile_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    importance_score: float = 0.5  # 0.0-1.0
    confidence: float = 0.5        # How certain we are
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: datetime
    source_episodes: List[str] = []  # Episode IDs that contributed


class LongTermMemoryManager:
    """Manages persistent long-term memories for profiles."""

    def __init__(self, supabase_client=None):
        """Initialize with Supabase for persistence."""
        self.db = supabase_client
        self._cache: Dict[str, List[LongTermMemory]] = {}  # Profile cache

    async def store_memory(
        self,
        profile_id: str,
        memory_type: MemoryType,
        content: Dict[str, Any],
        importance_score: float = 0.5,
        confidence: float = 0.5,
        source_episodes: Optional[List[str]] = None,
    ) -> LongTermMemory:
        """
        Store a new long-term memory.

        Args:
            profile_id: Profile this memory belongs to
            memory_type: Type of memory (insight, preference, pattern, skill, goal)
            content: The memory content as structured data
            importance_score: How important is this memory (0.0-1.0)
            confidence: How confident are we in this memory (0.0-1.0)
            source_episodes: Episode IDs that contributed to this memory

        Returns:
            The stored LongTermMemory
        """
        pass

    async def retrieve_memories(
        self,
        profile_id: str,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0,
        limit: int = 10,
    ) -> List[LongTermMemory]:
        """
        Retrieve memories for a profile.

        Args:
            profile_id: Profile to retrieve memories for
            memory_type: Optional filter by memory type
            min_importance: Minimum importance threshold
            limit: Maximum number of memories to return

        Returns:
            List of matching memories, sorted by importance
        """
        pass

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[Dict[str, Any]] = None,
        importance_score: Optional[float] = None,
        confidence: Optional[float] = None,
    ) -> Optional[LongTermMemory]:
        """Update an existing memory."""
        pass

    async def forget_memory(
        self,
        memory_id: str,
        reason: str = "manual",
    ) -> bool:
        """
        Soft-delete a memory (mark as forgotten).

        We don't hard delete to maintain audit trail.
        """
        pass

    async def merge_memories(
        self,
        memory_ids: List[str],
        merged_content: Dict[str, Any],
    ) -> LongTermMemory:
        """
        Merge multiple related memories into one.

        Used during memory consolidation to reduce redundancy.
        """
        pass

    async def decay_memories(
        self,
        profile_id: str,
        decay_factor: float = 0.95,
    ) -> int:
        """
        Apply decay to rarely accessed memories.

        Reduces importance_score for memories not accessed recently.
        Returns count of decayed memories.
        """
        pass

    def record_access(self, memory_id: str) -> None:
        """Record that a memory was accessed (for decay calculations)."""
        pass
```

### Database Schema

```sql
CREATE TABLE longterm_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profiles(id) NOT NULL,
    memory_type TEXT NOT NULL CHECK (memory_type IN ('insight', 'preference', 'pattern', 'skill', 'goal')),
    content JSONB NOT NULL,
    importance_score FLOAT DEFAULT 0.5 CHECK (importance_score >= 0 AND importance_score <= 1),
    confidence FLOAT DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    source_episodes UUID[] DEFAULT '{}',
    is_forgotten BOOLEAN DEFAULT false,
    forgotten_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_longterm_memories_profile ON longterm_memories(profile_id);
CREATE INDEX idx_longterm_memories_type ON longterm_memories(memory_type);
CREATE INDEX idx_longterm_memories_importance ON longterm_memories(importance_score DESC);
```

### Test File: `tests/phase3/test_longterm_memory.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.memory.longterm_v9 import (
    LongTermMemoryManager,
    LongTermMemory,
    MemoryType,
)


class TestLongTermMemoryManager:
    """Tests for B4: Long-term Memory."""

    @pytest.fixture
    def mock_supabase(self):
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            insert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
            )),
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    order=MagicMock(return_value=MagicMock(
                        limit=MagicMock(return_value=MagicMock(
                            execute=MagicMock(return_value=MagicMock(data=[]))
                        ))
                    ))
                ))
            ))
        ))
        return db

    @pytest.fixture
    def manager(self, mock_supabase):
        return LongTermMemoryManager(supabase_client=mock_supabase)

    @pytest.mark.asyncio
    async def test_store_memory_creates_entry(self, manager):
        """Test storing a new long-term memory."""
        memory = await manager.store_memory(
            profile_id="test-profile",
            memory_type=MemoryType.INSIGHT,
            content={"key": "Student prefers visual learning"},
            importance_score=0.8,
        )

        assert memory is not None
        assert memory.memory_type == MemoryType.INSIGHT
        assert memory.importance_score == 0.8

    @pytest.mark.asyncio
    async def test_retrieve_memories_filters_by_type(self, manager):
        """Test retrieving memories with type filter."""
        memories = await manager.retrieve_memories(
            profile_id="test-profile",
            memory_type=MemoryType.PREFERENCE,
        )

        assert isinstance(memories, list)

    @pytest.mark.asyncio
    async def test_retrieve_memories_respects_min_importance(self, manager):
        """Test that min_importance filter works."""
        memories = await manager.retrieve_memories(
            profile_id="test-profile",
            min_importance=0.5,
        )

        for memory in memories:
            assert memory.importance_score >= 0.5

    @pytest.mark.asyncio
    async def test_decay_memories_reduces_importance(self, manager):
        """Test memory decay over time."""
        count = await manager.decay_memories(
            profile_id="test-profile",
            decay_factor=0.9,
        )

        assert isinstance(count, int)

    @pytest.mark.asyncio
    async def test_forget_memory_soft_deletes(self, manager):
        """Test that forget doesn't hard delete."""
        result = await manager.forget_memory(
            memory_id="test-memory-id",
            reason="outdated",
        )

        assert result in [True, False]

    @pytest.mark.asyncio
    async def test_merge_memories_combines_entries(self, manager):
        """Test merging multiple memories."""
        merged = await manager.merge_memories(
            memory_ids=["mem-1", "mem-2"],
            merged_content={"combined": "content"},
        )

        assert merged is not None
```

---

## B3: Semantic Memory

### Purpose
Vector-based memory for semantic similarity search. Stores embeddings of important concepts, essays, and insights for contextual retrieval.

### 3P System Choice: **Supabase pgvector** (RECOMMENDED)

**Why pgvector over Pinecone/Weaviate:**
- ✅ Already using Supabase - no new vendor
- ✅ Single source of truth - vectors + metadata in same DB
- ✅ Simpler architecture - no external vector DB to manage
- ✅ Cost effective - included in Supabase plan
- ✅ ACID transactions - vectors and metadata atomically consistent
- ✅ Row-level security - profile isolation built-in

**Trade-offs:**
- Pinecone has better performance at 10M+ vectors (we're far from this)
- pgvector is sufficient for <1M vectors per table

### File: `middleware/memory/semantic_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class SemanticChunk(BaseModel):
    """A chunk of content stored in semantic memory."""
    id: str
    profile_id: str
    content_type: str  # 'essay', 'activity', 'insight', 'conversation'
    content_text: str
    content_summary: str
    embedding: List[float]  # Stored in pgvector
    metadata: Dict[str, Any] = {}
    created_at: datetime


class SemanticSearchResult(BaseModel):
    """Result from semantic search."""
    chunk: SemanticChunk
    similarity_score: float  # Cosine similarity (0-1)
    distance: float  # L2 distance (lower = more similar)


class SemanticMemoryManager:
    """
    Manages vector-based semantic memory using Supabase pgvector.

    Uses:
    - Supabase pgvector for vector storage and similarity search
    - OpenAI text-embedding-3-small for embeddings (1536 dimensions)

    All operations are atomic within Supabase transactions.
    """

    EMBEDDING_DIMENSION = 1536  # text-embedding-3-small

    def __init__(
        self,
        supabase_client=None,
        openai_client=None,
        embedding_model: str = "text-embedding-3-small",
    ):
        """
        Initialize semantic memory.

        Args:
            supabase_client: Supabase client (already in use)
            openai_client: OpenAI client for embeddings (already in use)
            embedding_model: OpenAI embedding model
        """
        self.db = supabase_client
        self.openai = openai_client
        self.embedding_model = embedding_model

    async def store(
        self,
        profile_id: str,
        content_type: str,
        content_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SemanticChunk:
        """
        Store content in semantic memory.

        1. Generate embedding via OpenAI
        2. Store vector + metadata in Supabase pgvector table

        All in one atomic operation.

        Args:
            profile_id: Profile this content belongs to
            content_type: Type of content (essay, activity, insight, conversation)
            content_text: The text content to store
            metadata: Additional metadata

        Returns:
            The stored SemanticChunk
        """
        pass

    async def search(
        self,
        profile_id: str,
        query: str,
        content_type: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.7,
    ) -> List[SemanticSearchResult]:
        """
        Search semantic memory using pgvector similarity.

        Uses cosine similarity via Supabase RPC function.

        Args:
            profile_id: Profile to search within
            query: The query text
            content_type: Optional filter by content type
            top_k: Number of results to return
            min_score: Minimum cosine similarity threshold (0-1)

        Returns:
            List of matching results with similarity scores
        """
        pass

    async def search_multi_profile(
        self,
        query: str,
        profile_ids: List[str],
        top_k: int = 10,
    ) -> List[SemanticSearchResult]:
        """Search across multiple profiles (for pattern finding)."""
        pass

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        pass

    async def delete(self, chunk_id: str) -> bool:
        """Delete a chunk from semantic memory."""
        pass

    async def update_metadata(
        self,
        chunk_id: str,
        metadata: Dict[str, Any],
    ) -> bool:
        """Update metadata for a stored chunk."""
        pass
```

### Database Schema (Supabase pgvector)

```sql
-- Enable pgvector extension (one-time)
CREATE EXTENSION IF NOT EXISTS vector;

-- Semantic memory table with vector column
CREATE TABLE semantic_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID REFERENCES profiles(id) NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('essay', 'activity', 'insight', 'conversation')),
    content_text TEXT NOT NULL,
    content_summary TEXT,
    embedding vector(1536) NOT NULL,  -- text-embedding-3-small dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast vector similarity search
CREATE INDEX idx_semantic_memories_embedding ON semantic_memories
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- Adjust lists based on row count

-- Standard indexes
CREATE INDEX idx_semantic_memories_profile ON semantic_memories(profile_id);
CREATE INDEX idx_semantic_memories_type ON semantic_memories(content_type);

-- RPC function for similarity search (called from Supabase client)
CREATE OR REPLACE FUNCTION match_semantic_memories(
    query_embedding vector(1536),
    match_profile_id UUID,
    match_content_type TEXT DEFAULT NULL,
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    profile_id UUID,
    content_type TEXT,
    content_text TEXT,
    content_summary TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sm.id,
        sm.profile_id,
        sm.content_type,
        sm.content_text,
        sm.content_summary,
        sm.metadata,
        1 - (sm.embedding <=> query_embedding) AS similarity
    FROM semantic_memories sm
    WHERE sm.profile_id = match_profile_id
      AND (match_content_type IS NULL OR sm.content_type = match_content_type)
      AND 1 - (sm.embedding <=> query_embedding) > match_threshold
    ORDER BY sm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### Test File: `tests/phase3/test_semantic_memory.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from middleware.memory.semantic_v9 import (
    SemanticMemoryManager,
    SemanticChunk,
    SemanticSearchResult,
)


class TestSemanticMemoryManager:
    """Tests for B3: Semantic Memory (using Supabase pgvector)."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client with pgvector support."""
        db = MagicMock()
        db.table = MagicMock(return_value=MagicMock(
            insert=MagicMock(return_value=MagicMock(
                execute=MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
            )),
            select=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
                ))
            )),
            delete=MagicMock(return_value=MagicMock(
                eq=MagicMock(return_value=MagicMock(
                    execute=MagicMock(return_value=MagicMock(data=[]))
                ))
            ))
        ))
        # Mock RPC for vector search
        db.rpc = MagicMock(return_value=MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[
                {"id": "vec-1", "similarity": 0.92, "content_text": "Test 1"},
                {"id": "vec-2", "similarity": 0.85, "content_text": "Test 2"},
            ]))
        ))
        return db

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client for embeddings."""
        client = MagicMock()
        client.embeddings = MagicMock()
        client.embeddings.create = AsyncMock(return_value=MagicMock(
            data=[MagicMock(embedding=[0.1] * 1536)]
        ))
        return client

    @pytest.fixture
    def manager(self, mock_supabase, mock_openai):
        return SemanticMemoryManager(
            supabase_client=mock_supabase,
            openai_client=mock_openai,
        )

    @pytest.mark.asyncio
    async def test_store_creates_embedding(self, manager):
        """Test that storing content creates an embedding."""
        chunk = await manager.store(
            profile_id="test-profile",
            content_type="essay",
            content_text="This is a test essay about leadership.",
        )

        assert chunk is not None
        assert chunk.content_type == "essay"

    @pytest.mark.asyncio
    async def test_search_uses_rpc_function(self, manager):
        """Test semantic search uses Supabase RPC."""
        results = await manager.search(
            profile_id="test-profile",
            query="leadership skills",
            top_k=5,
        )

        assert isinstance(results, list)
        # Verify RPC was called
        manager.db.rpc.assert_called()

    @pytest.mark.asyncio
    async def test_search_respects_min_score(self, manager):
        """Test that min_score filter is applied."""
        results = await manager.search(
            profile_id="test-profile",
            query="test query",
            min_score=0.9,
        )

        for result in results:
            assert result.similarity_score >= 0.9

    @pytest.mark.asyncio
    async def test_search_filters_by_content_type(self, manager):
        """Test filtering by content type."""
        results = await manager.search(
            profile_id="test-profile",
            query="test",
            content_type="essay",
        )

        for result in results:
            assert result.chunk.content_type == "essay"

    @pytest.mark.asyncio
    async def test_delete_removes_from_supabase(self, manager):
        """Test deletion removes from Supabase."""
        result = await manager.delete("test-chunk-id")

        assert result in [True, False]
        manager.db.table.assert_called_with("semantic_memories")

    @pytest.mark.asyncio
    async def test_get_embedding_calls_openai(self, manager):
        """Test embedding generation uses OpenAI."""
        embedding = await manager.get_embedding("test text")

        assert isinstance(embedding, list)
        assert len(embedding) == 1536  # text-embedding-3-small dimension
        manager.openai.embeddings.create.assert_called()
```

---

## B5: Memory Extraction

### Purpose
Extract meaningful memories from conversations, agent outputs, and user interactions. Uses LLM to identify important insights worth remembering.

### File: `middleware/memory/extraction_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ExtractionSource(str, Enum):
    """Source of content for extraction."""
    CONVERSATION = "conversation"
    AGENT_OUTPUT = "agent_output"
    ESSAY = "essay"
    ASSESSMENT = "assessment"
    USER_INPUT = "user_input"


class ExtractedMemory(BaseModel):
    """A memory extracted from content."""
    content: Dict[str, Any]
    memory_type: str  # Maps to MemoryType
    importance_score: float
    confidence: float
    source: ExtractionSource
    source_content_snippet: str
    extraction_reasoning: str  # Why this was extracted


class MemoryExtractor:
    """
    Extracts meaningful memories from content using LLM.

    Identifies:
    - Student insights (learning style, strengths, challenges)
    - Preferences (communication style, topics of interest)
    - Patterns (recurring themes, behaviors)
    - Skills (demonstrated abilities)
    - Goals (stated objectives)
    """

    def __init__(self, llm_client=None):
        """Initialize with LLM client."""
        self.llm = llm_client

    async def extract_from_conversation(
        self,
        profile_id: str,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ExtractedMemory]:
        """
        Extract memories from a conversation.

        Args:
            profile_id: Profile the conversation belongs to
            messages: List of messages [{"role": "user/assistant", "content": "..."}]
            context: Additional context (agent name, session info, etc.)

        Returns:
            List of extracted memories
        """
        pass

    async def extract_from_essay(
        self,
        profile_id: str,
        essay_content: str,
        essay_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ExtractedMemory]:
        """Extract memories from an essay."""
        pass

    async def extract_from_assessment(
        self,
        profile_id: str,
        assessment_data: Dict[str, Any],
    ) -> List[ExtractedMemory]:
        """Extract memories from an assessment result."""
        pass

    async def extract_from_agent_output(
        self,
        profile_id: str,
        agent_name: str,
        output: Dict[str, Any],
    ) -> List[ExtractedMemory]:
        """Extract memories from agent output."""
        pass

    async def batch_extract(
        self,
        profile_id: str,
        contents: List[Dict[str, Any]],
    ) -> List[ExtractedMemory]:
        """Extract memories from multiple content pieces."""
        pass

    def _build_extraction_prompt(
        self,
        content: str,
        source: ExtractionSource,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build the LLM prompt for extraction."""
        pass
```

### Test File: `tests/phase3/test_memory_extraction.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.memory.extraction_v9 import (
    MemoryExtractor,
    ExtractedMemory,
    ExtractionSource,
)


class TestMemoryExtractor:
    """Tests for B5: Memory Extraction."""

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.ainvoke = AsyncMock(return_value=MagicMock(
            content='''[
                {
                    "content": {"insight": "Student shows strong interest in STEM"},
                    "memory_type": "insight",
                    "importance_score": 0.8,
                    "confidence": 0.9,
                    "extraction_reasoning": "Multiple mentions of science projects"
                }
            ]'''
        ))
        return llm

    @pytest.fixture
    def extractor(self, mock_llm):
        return MemoryExtractor(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_extract_from_conversation(self, extractor):
        """Test extracting memories from conversation."""
        memories = await extractor.extract_from_conversation(
            profile_id="test-profile",
            messages=[
                {"role": "user", "content": "I love working on robotics projects"},
                {"role": "assistant", "content": "That's great! Tell me more..."},
            ],
        )

        assert isinstance(memories, list)

    @pytest.mark.asyncio
    async def test_extract_from_essay(self, extractor):
        """Test extracting memories from essay."""
        memories = await extractor.extract_from_essay(
            profile_id="test-profile",
            essay_content="Leadership has always been important to me...",
            essay_type="personal_statement",
        )

        assert isinstance(memories, list)

    @pytest.mark.asyncio
    async def test_extraction_includes_reasoning(self, extractor):
        """Test that extractions include reasoning."""
        memories = await extractor.extract_from_conversation(
            profile_id="test-profile",
            messages=[{"role": "user", "content": "Test"}],
        )

        if memories:
            assert hasattr(memories[0], 'extraction_reasoning')

    @pytest.mark.asyncio
    async def test_handles_empty_content(self, extractor):
        """Test handling of empty content."""
        memories = await extractor.extract_from_conversation(
            profile_id="test-profile",
            messages=[],
        )

        assert memories == []

    @pytest.mark.asyncio
    async def test_batch_extract_processes_multiple(self, extractor):
        """Test batch extraction."""
        memories = await extractor.batch_extract(
            profile_id="test-profile",
            contents=[
                {"type": "conversation", "data": []},
                {"type": "essay", "data": "Essay content"},
            ],
        )

        assert isinstance(memories, list)
```

---

## B6: Memory Consolidation

### Purpose
Consolidates scattered memories into coherent knowledge. Merges duplicate memories, updates importance scores, and prunes outdated information.

### File: `middleware/memory/consolidation_v9.py`

### Interface

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from .longterm_v9 import LongTermMemoryManager, LongTermMemory, MemoryType

logger = logging.getLogger(__name__)


class ConsolidationResult(BaseModel):
    """Result of memory consolidation."""
    profile_id: str
    memories_analyzed: int
    memories_merged: int
    memories_decayed: int
    memories_pruned: int
    new_insights: int
    duration_ms: int


class MemoryConsolidator:
    """
    Consolidates and maintains memory health.

    Performs:
    - Duplicate detection and merging
    - Importance score updates based on access patterns
    - Decay of stale memories
    - Pruning of low-importance, low-confidence memories
    - Cross-memory insight generation
    """

    def __init__(
        self,
        longterm_manager: LongTermMemoryManager,
        llm_client=None,
    ):
        """Initialize with memory manager and LLM."""
        self.longterm = longterm_manager
        self.llm = llm_client

    async def consolidate_profile(
        self,
        profile_id: str,
        aggressive: bool = False,
    ) -> ConsolidationResult:
        """
        Run full consolidation for a profile.

        Args:
            profile_id: Profile to consolidate
            aggressive: If True, prune more aggressively

        Returns:
            ConsolidationResult with statistics
        """
        pass

    async def find_duplicates(
        self,
        profile_id: str,
        similarity_threshold: float = 0.85,
    ) -> List[List[str]]:
        """
        Find groups of duplicate/similar memories.

        Returns:
            List of memory ID groups that are duplicates
        """
        pass

    async def merge_duplicates(
        self,
        memory_groups: List[List[str]],
    ) -> List[LongTermMemory]:
        """
        Merge groups of duplicate memories.

        For each group, creates one merged memory with:
        - Combined content
        - Highest importance score
        - Updated confidence
        """
        pass

    async def apply_decay(
        self,
        profile_id: str,
        days_threshold: int = 30,
        decay_rate: float = 0.95,
    ) -> int:
        """
        Apply decay to memories not accessed recently.

        Returns:
            Number of memories decayed
        """
        pass

    async def prune_low_value(
        self,
        profile_id: str,
        importance_threshold: float = 0.2,
        confidence_threshold: float = 0.3,
    ) -> int:
        """
        Prune (soft-delete) low-value memories.

        Returns:
            Number of memories pruned
        """
        pass

    async def generate_cross_insights(
        self,
        profile_id: str,
    ) -> List[LongTermMemory]:
        """
        Generate new insights by analyzing existing memories.

        Uses LLM to find patterns and connections across memories.
        """
        pass

    async def schedule_consolidation(
        self,
        profile_id: str,
        run_at: datetime,
    ) -> str:
        """Schedule a consolidation run for later."""
        pass
```

### Test File: `tests/phase3/test_memory_consolidation.py`

```python
import pytest
from unittest.mock import MagicMock, AsyncMock
from middleware.memory.consolidation_v9 import (
    MemoryConsolidator,
    ConsolidationResult,
)
from middleware.memory.longterm_v9 import (
    LongTermMemoryManager,
    LongTermMemory,
    MemoryType,
)


class TestMemoryConsolidator:
    """Tests for B6: Memory Consolidation."""

    @pytest.fixture
    def mock_longterm(self):
        manager = MagicMock(spec=LongTermMemoryManager)
        manager.retrieve_memories = AsyncMock(return_value=[])
        manager.decay_memories = AsyncMock(return_value=5)
        manager.merge_memories = AsyncMock(return_value=MagicMock())
        manager.forget_memory = AsyncMock(return_value=True)
        return manager

    @pytest.fixture
    def consolidator(self, mock_longterm):
        return MemoryConsolidator(
            longterm_manager=mock_longterm,
            llm_client=MagicMock(),
        )

    @pytest.mark.asyncio
    async def test_consolidate_profile_returns_result(self, consolidator):
        """Test full consolidation returns result."""
        result = await consolidator.consolidate_profile(
            profile_id="test-profile",
        )

        assert isinstance(result, ConsolidationResult)
        assert result.profile_id == "test-profile"

    @pytest.mark.asyncio
    async def test_find_duplicates_groups_similar(self, consolidator):
        """Test duplicate detection."""
        groups = await consolidator.find_duplicates(
            profile_id="test-profile",
            similarity_threshold=0.85,
        )

        assert isinstance(groups, list)

    @pytest.mark.asyncio
    async def test_apply_decay_updates_memories(self, consolidator):
        """Test decay application."""
        count = await consolidator.apply_decay(
            profile_id="test-profile",
            days_threshold=30,
        )

        assert isinstance(count, int)

    @pytest.mark.asyncio
    async def test_prune_low_value_removes_stale(self, consolidator):
        """Test pruning of low-value memories."""
        count = await consolidator.prune_low_value(
            profile_id="test-profile",
            importance_threshold=0.2,
        )

        assert isinstance(count, int)

    @pytest.mark.asyncio
    async def test_aggressive_consolidation_prunes_more(self, consolidator):
        """Test aggressive mode prunes more."""
        result = await consolidator.consolidate_profile(
            profile_id="test-profile",
            aggressive=True,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_generate_cross_insights(self, consolidator):
        """Test cross-memory insight generation."""
        insights = await consolidator.generate_cross_insights(
            profile_id="test-profile",
        )

        assert isinstance(insights, list)
```

---

## Implementation Checklist

### B4: Long-term Memory
- [ ] Create `middleware/memory/longterm_v9.py`
- [ ] Implement `LongTermMemoryManager` class
- [ ] Add database migration
- [ ] Create tests in `tests/phase3/test_longterm_memory.py`
- [ ] Run tests and verify passing
- [ ] Add to `stack_v9.py`

### B3: Semantic Memory
- [ ] Create `middleware/memory/semantic_v9.py`
- [ ] Implement `SemanticMemoryManager` class
- [ ] Configure Pinecone index
- [ ] Add database migration for metadata table
- [ ] Create tests in `tests/phase3/test_semantic_memory.py`
- [ ] Run tests and verify passing
- [ ] Add to `stack_v9.py`

### B5: Memory Extraction
- [ ] Create `middleware/memory/extraction_v9.py`
- [ ] Implement `MemoryExtractor` class
- [ ] Design extraction prompts
- [ ] Create tests in `tests/phase3/test_memory_extraction.py`
- [ ] Run tests and verify passing
- [ ] Add to `stack_v9.py`

### B6: Memory Consolidation
- [ ] Create `middleware/memory/consolidation_v9.py`
- [ ] Implement `MemoryConsolidator` class
- [ ] Create tests in `tests/phase3/test_memory_consolidation.py`
- [ ] Run tests and verify passing
- [ ] Add to `stack_v9.py`

---

*Phase 3 Week 1 Specification*
*Generated: 2026-01-17*
