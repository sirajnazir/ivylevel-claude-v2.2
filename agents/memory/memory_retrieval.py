"""
Pattern B7: Memory Retrieval
v5.4 True Autonomous Agents

3P: Supabase pgvector for semantic search
USP: Context-aware retrieval for coaching
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class MemoryItem(BaseModel):
    """A retrievable memory item."""
    id: str
    content: str
    type: str  # conversation, fact, action, insight
    profile_id: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    relevance_score: float = 0.0


class RetrievalResult(BaseModel):
    """Result of memory retrieval."""
    memories: List[MemoryItem] = Field(default_factory=list)
    query: str = ""
    method: str = "semantic"  # semantic, keyword, recency
    total_searched: int = 0
    retrieval_time_ms: int = 0


class MemoryRetriever:
    """
    Retrieves relevant memories for context.

    Pattern B7: Memory Retrieval (3P: Supabase pgvector)

    Why this matters:
    1. Agents need historical context
    2. Students shouldn't repeat themselves
    3. Enables personalized responses
    4. Supports long-term coaching relationship
    """

    def __init__(
        self,
        supabase_client=None,
        embedding_model=None,
    ):
        """
        Initialize retriever.

        Args:
            supabase_client: Supabase client for vector search
            embedding_model: Model for generating embeddings
        """
        self.supabase = supabase_client
        self.embedding_model = embedding_model
        self._embedding_cache: Dict[str, List[float]] = {}

    async def retrieve(
        self,
        query: str,
        profile_id: str,
        memory_type: Optional[str] = None,
        limit: int = 5,
        min_relevance: float = 0.5,
    ) -> RetrievalResult:
        """
        Retrieve relevant memories for a query.

        Args:
            query: The search query
            profile_id: Student's profile ID
            memory_type: Filter by memory type (optional)
            limit: Maximum memories to return
            min_relevance: Minimum relevance score

        Returns:
            RetrievalResult with matching memories
        """
        start_time = datetime.utcnow()

        # Try semantic search first
        if self.supabase and self.embedding_model:
            memories = await self._semantic_search(
                query, profile_id, memory_type, limit, min_relevance
            )
            method = "semantic"
        else:
            # Fallback to keyword search
            memories = await self._keyword_search(
                query, profile_id, memory_type, limit
            )
            method = "keyword"

        end_time = datetime.utcnow()
        retrieval_time = int((end_time - start_time).total_seconds() * 1000)

        return RetrievalResult(
            memories=memories,
            query=query,
            method=method,
            total_searched=len(memories),
            retrieval_time_ms=retrieval_time,
        )

    async def _semantic_search(
        self,
        query: str,
        profile_id: str,
        memory_type: Optional[str],
        limit: int,
        min_relevance: float,
    ) -> List[MemoryItem]:
        """Perform semantic vector search."""
        try:
            # Generate query embedding
            query_embedding = await self._get_embedding(query)

            # Build the RPC call for vector similarity search
            rpc_params = {
                "query_embedding": query_embedding,
                "match_threshold": min_relevance,
                "match_count": limit,
                "filter_profile_id": profile_id,
            }

            if memory_type:
                rpc_params["filter_type"] = memory_type

            # Execute vector search
            response = await self.supabase.rpc(
                "match_memories",
                rpc_params
            ).execute()

            memories = []
            for row in response.data or []:
                memories.append(MemoryItem(
                    id=row["id"],
                    content=row["content"],
                    type=row["type"],
                    profile_id=row["profile_id"],
                    metadata=row.get("metadata", {}),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    relevance_score=row.get("similarity", 0.0),
                ))

            return memories

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            # Fallback to keyword search
            return await self._keyword_search(query, profile_id, memory_type, limit)

    async def _keyword_search(
        self,
        query: str,
        profile_id: str,
        memory_type: Optional[str],
        limit: int,
    ) -> List[MemoryItem]:
        """Fallback keyword-based search."""
        if not self.supabase:
            return []

        try:
            # Build query
            db_query = self.supabase.table("memories").select("*").eq(
                "profile_id", profile_id
            ).ilike("content", f"%{query}%")

            if memory_type:
                db_query = db_query.eq("type", memory_type)

            response = db_query.limit(limit).execute()

            memories = []
            for row in response.data or []:
                memories.append(MemoryItem(
                    id=row["id"],
                    content=row["content"],
                    type=row["type"],
                    profile_id=row["profile_id"],
                    metadata=row.get("metadata", {}),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    relevance_score=0.5,  # Default for keyword match
                ))

            return memories

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    async def _get_embedding(self, text: str) -> List[float]:
        """Get or compute embedding for text."""
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        if not self.embedding_model:
            # Return zero vector as fallback
            return [0.0] * 1536

        try:
            # Assuming OpenAI embedding model
            response = await self.embedding_model.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            embedding = response.data[0].embedding
            self._embedding_cache[text] = embedding
            return embedding

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [0.0] * 1536

    async def store_memory(
        self,
        profile_id: str,
        content: str,
        memory_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryItem:
        """
        Store a new memory.

        Args:
            profile_id: Student's profile ID
            content: Memory content
            memory_type: Type of memory
            metadata: Additional metadata

        Returns:
            Stored MemoryItem
        """
        import uuid

        memory = MemoryItem(
            id=str(uuid.uuid4()),
            content=content,
            type=memory_type,
            profile_id=profile_id,
            metadata=metadata or {},
        )

        if self.embedding_model:
            memory.embedding = await self._get_embedding(content)

        if self.supabase:
            try:
                await self.supabase.table("memories").insert({
                    "id": memory.id,
                    "profile_id": profile_id,
                    "content": content,
                    "type": memory_type,
                    "embedding": memory.embedding,
                    "metadata": memory.metadata,
                    "created_at": memory.created_at.isoformat(),
                }).execute()

                logger.debug(f"Stored memory {memory.id} for profile {profile_id}")

            except Exception as e:
                logger.error(f"Failed to store memory: {e}")

        return memory

    async def get_recent_memories(
        self,
        profile_id: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Get most recent memories for a profile."""
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("memories").select("*").eq(
                "profile_id", profile_id
            ).order("created_at", desc=True).limit(limit)

            if memory_type:
                query = query.eq("type", memory_type)

            response = query.execute()

            return [
                MemoryItem(
                    id=row["id"],
                    content=row["content"],
                    type=row["type"],
                    profile_id=row["profile_id"],
                    metadata=row.get("metadata", {}),
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in response.data or []
            ]

        except Exception as e:
            logger.error(f"Failed to get recent memories: {e}")
            return []


class ConversationMemory:
    """
    Specialized memory for conversation context.

    USP: Maintains coaching relationship across sessions.
    """

    def __init__(self, retriever: MemoryRetriever):
        self.retriever = retriever

    async def remember_conversation(
        self,
        profile_id: str,
        conversation: List[Dict[str, str]],
        session_id: str,
    ) -> MemoryItem:
        """Store a conversation for future reference."""
        # Summarize conversation
        content = self._summarize_conversation(conversation)

        return await self.retriever.store_memory(
            profile_id=profile_id,
            content=content,
            memory_type="conversation",
            metadata={
                "session_id": session_id,
                "turn_count": len(conversation),
            },
        )

    def _summarize_conversation(
        self,
        conversation: List[Dict[str, str]],
    ) -> str:
        """Create a summary of conversation."""
        # Simple summarization - could use LLM for better results
        user_messages = [
            m["content"] for m in conversation
            if m.get("role") == "user"
        ]

        if not user_messages:
            return "No user messages"

        # Take key points
        return " | ".join(user_messages[-3:])  # Last 3 user messages

    async def get_relevant_history(
        self,
        profile_id: str,
        current_topic: str,
        limit: int = 3,
    ) -> List[MemoryItem]:
        """Get conversation history relevant to current topic."""
        result = await self.retriever.retrieve(
            query=current_topic,
            profile_id=profile_id,
            memory_type="conversation",
            limit=limit,
        )
        return result.memories


class FactMemory:
    """
    Specialized memory for facts about a student.

    USP: Remembers student preferences, achievements, etc.
    """

    def __init__(self, retriever: MemoryRetriever):
        self.retriever = retriever

    async def remember_fact(
        self,
        profile_id: str,
        fact: str,
        category: str = "general",
    ) -> MemoryItem:
        """Store a fact about the student."""
        return await self.retriever.store_memory(
            profile_id=profile_id,
            content=fact,
            memory_type="fact",
            metadata={"category": category},
        )

    async def get_relevant_facts(
        self,
        profile_id: str,
        context: str,
        limit: int = 5,
    ) -> List[MemoryItem]:
        """Get facts relevant to current context."""
        result = await self.retriever.retrieve(
            query=context,
            profile_id=profile_id,
            memory_type="fact",
            limit=limit,
        )
        return result.memories


# Convenience functions
async def retrieve_memories(
    supabase_client,
    profile_id: str,
    query: str,
    limit: int = 5,
) -> RetrievalResult:
    """Quick helper to retrieve memories."""
    retriever = MemoryRetriever(supabase_client)
    return await retriever.retrieve(query, profile_id, limit=limit)
