"""
Semantic Memory - Vector-based memory retrieval.

Pattern: B3
3P: Supabase pgvector + OpenAI embeddings
Lines: ~120 (thin wrapper)

Features:
- Store memories with vector embeddings
- Similarity search via pgvector
- Automatic embedding generation
- Graceful degradation
"""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


class SemanticMemory(BaseModel):
    """A semantic memory with vector embedding."""
    content: str
    memory_type: str = "general"  # general, insight, preference, fact
    importance: float = 0.5
    similarity: Optional[float] = None  # Set during retrieval
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SemanticMemoryManager:
    """
    Manages vector-based semantic memories using Supabase pgvector.

    Pattern B3: Semantic Memory
    3P: Supabase pgvector + OpenAI embeddings

    Thin wrapper - delegates embedding to OpenAI, storage to Supabase.
    """

    TABLE = "phase3_semantic_memories"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536

    def __init__(
        self,
        supabase_client=None,
        openai_client=None,
    ):
        self.supabase = supabase_client
        self.openai = openai_client
        self._initialized = supabase_client is not None and openai_client is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using OpenAI."""
        if not self.openai:
            return None

        try:
            response = self.openai.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    async def store(
        self,
        profile_id: str,
        content: str,
        memory_type: str = "general",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store a memory with its vector embedding."""
        if not self.is_available:
            logger.warning("SemanticMemory not available - missing clients")
            return False

        try:
            # Generate embedding
            embedding = await self._get_embedding(content)
            if not embedding:
                return False

            # Store in Supabase with pgvector
            result = self.supabase.table(self.TABLE).insert({
                "profile_id": profile_id,
                "content": content,
                "memory_type": memory_type,
                "importance": importance,
                "embedding": embedding,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
            }).execute()

            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to store semantic memory: {e}")
            return False

    async def search(
        self,
        profile_id: str,
        query: str,
        limit: int = 5,
        min_similarity: float = 0.7,
        memory_type: Optional[str] = None,
    ) -> List[SemanticMemory]:
        """Search for similar memories using vector similarity."""
        if not self.is_available:
            return []

        try:
            # Generate query embedding
            query_embedding = await self._get_embedding(query)
            if not query_embedding:
                return []

            # Use Supabase RPC for vector similarity search
            params = {
                "query_embedding": query_embedding,
                "match_threshold": min_similarity,
                "match_count": limit,
                "p_profile_id": profile_id,
            }

            if memory_type:
                params["p_memory_type"] = memory_type

            result = self.supabase.rpc(
                "match_semantic_memories",
                params,
            ).execute()

            return [
                SemanticMemory(
                    content=m["content"],
                    memory_type=m["memory_type"],
                    importance=m["importance"],
                    similarity=m.get("similarity"),
                    metadata=m.get("metadata", {}),
                )
                for m in result.data
            ]
        except Exception as e:
            logger.error(f"Failed to search semantic memories: {e}")
            return []

    async def get_by_type(
        self,
        profile_id: str,
        memory_type: str,
        limit: int = 50,
    ) -> List[SemanticMemory]:
        """Get memories by type without vector search."""
        if not self.is_available:
            return []

        try:
            result = self.supabase.table(self.TABLE).select("*").eq(
                "profile_id", profile_id
            ).eq(
                "memory_type", memory_type
            ).order(
                "importance", desc=True
            ).limit(limit).execute()

            return [
                SemanticMemory(
                    content=m["content"],
                    memory_type=m["memory_type"],
                    importance=m["importance"],
                    metadata=m.get("metadata", {}),
                )
                for m in result.data
            ]
        except Exception as e:
            logger.error(f"Failed to get memories by type: {e}")
            return []

    async def delete(
        self,
        profile_id: str,
        memory_id: str,
    ) -> bool:
        """Delete a specific memory."""
        if not self.is_available:
            return False

        try:
            self.supabase.table(self.TABLE).delete().eq(
                "profile_id", profile_id
            ).eq(
                "id", memory_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete semantic memory: {e}")
            return False

    async def count(
        self,
        profile_id: str,
        memory_type: Optional[str] = None,
    ) -> int:
        """Count memories for a profile."""
        if not self.is_available:
            return 0

        try:
            query = self.supabase.table(self.TABLE).select(
                "id", count="exact"
            ).eq("profile_id", profile_id)

            if memory_type:
                query = query.eq("memory_type", memory_type)

            result = query.execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Failed to count semantic memories: {e}")
            return 0
