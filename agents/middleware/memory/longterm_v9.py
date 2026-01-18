"""
Long-Term Memory - Persistent storage across sessions.

Pattern: B4
3P: Supabase (JSONB storage)
Lines: ~100 (thin wrapper)

Features:
- Store/retrieve memories by key
- Update with confidence tracking
- Query by type/importance
- Automatic timestamp management
- Graceful degradation
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LongTermMemory(BaseModel):
    """A single long-term memory."""
    key: str
    value: Any
    memory_type: str = "fact"  # fact, preference, goal, insight
    importance: float = 0.5
    confidence: float = 1.0
    source: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LongTermMemoryManager:
    """
    Manages persistent memories using Supabase.

    Pattern B4: Long-Term Memory
    3P: Supabase JSONB

    Thin wrapper - delegates all storage to Supabase.
    """

    TABLE = "phase3_longterm_memories"

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._initialized = supabase_client is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def remember(
        self,
        profile_id: str,
        key: str,
        value: Any,
        memory_type: str = "fact",
        importance: float = 0.5,
        source: Optional[str] = None,
    ) -> bool:
        """Store or update a memory."""
        if not self.is_available:
            logger.warning("LongTermMemory not available - no Supabase client")
            return False

        try:
            result = self.supabase.table(self.TABLE).upsert({
                "profile_id": profile_id,
                "memory_key": key,
                "memory_value": value,
                "memory_type": memory_type,
                "importance": importance,
                "source": source,
                "updated_at": datetime.utcnow().isoformat(),
            }).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False

    async def recall(
        self,
        profile_id: str,
        key: str,
    ) -> Optional[Any]:
        """Retrieve a specific memory by key."""
        if not self.is_available:
            return None

        try:
            result = self.supabase.table(self.TABLE).select("*").eq(
                "profile_id", profile_id
            ).eq("memory_key", key).single().execute()

            if result.data:
                # Update access tracking
                self.supabase.table(self.TABLE).update({
                    "access_count": result.data.get("access_count", 0) + 1,
                    "last_accessed": datetime.utcnow().isoformat(),
                }).eq("id", result.data["id"]).execute()

                return result.data.get("memory_value")
            return None
        except Exception as e:
            logger.error(f"Failed to recall memory: {e}")
            return None

    async def recall_all(
        self,
        profile_id: str,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0,
        limit: int = 100,
    ) -> List[LongTermMemory]:
        """Retrieve all memories matching criteria."""
        if not self.is_available:
            return []

        try:
            query = self.supabase.table(self.TABLE).select("*").eq(
                "profile_id", profile_id
            ).gte("importance", min_importance).limit(limit)

            if memory_type:
                query = query.eq("memory_type", memory_type)

            result = query.order("importance", desc=True).execute()

            return [
                LongTermMemory(
                    key=m["memory_key"],
                    value=m["memory_value"],
                    memory_type=m["memory_type"],
                    importance=m["importance"],
                    confidence=m.get("confidence", 1.0),
                    source=m.get("source"),
                )
                for m in result.data
            ]
        except Exception as e:
            logger.error(f"Failed to recall memories: {e}")
            return []

    async def forget(
        self,
        profile_id: str,
        key: str,
    ) -> bool:
        """Remove a specific memory."""
        if not self.is_available:
            return False

        try:
            self.supabase.table(self.TABLE).delete().eq(
                "profile_id", profile_id
            ).eq("memory_key", key).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to forget memory: {e}")
            return False

    async def update_importance(
        self,
        profile_id: str,
        key: str,
        importance_delta: float,
    ) -> bool:
        """Adjust importance of a memory (reinforcement learning)."""
        if not self.is_available:
            return False

        try:
            result = self.supabase.table(self.TABLE).select("importance").eq(
                "profile_id", profile_id
            ).eq("memory_key", key).single().execute()

            if result.data:
                new_importance = max(0.0, min(1.0, result.data["importance"] + importance_delta))
                self.supabase.table(self.TABLE).update({
                    "importance": new_importance,
                    "updated_at": datetime.utcnow().isoformat(),
                }).eq("profile_id", profile_id).eq("memory_key", key).execute()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update importance: {e}")
            return False

    async def get_by_type(
        self,
        profile_id: str,
        memory_type: str,
        limit: int = 50,
    ) -> List[LongTermMemory]:
        """Get all memories of a specific type."""
        return await self.recall_all(
            profile_id=profile_id,
            memory_type=memory_type,
            limit=limit,
        )

    async def count(
        self,
        profile_id: str,
        memory_type: Optional[str] = None,
    ) -> int:
        """Count memories for a profile."""
        if not self.is_available:
            return 0

        try:
            query = self.supabase.table(self.TABLE).select("id", count="exact").eq(
                "profile_id", profile_id
            )
            if memory_type:
                query = query.eq("memory_type", memory_type)

            result = query.execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Failed to count memories: {e}")
            return 0
