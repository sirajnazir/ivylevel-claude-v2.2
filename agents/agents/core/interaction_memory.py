# agents/agents/core/interaction_memory.py
"""
IvyQuest v13.2 - Interaction Memory Manager

This module stores and retrieves conversation summaries for long-term
recall. After each agent interaction, a summary is stored with:
- Topics discussed
- Decisions made
- Action items
- Emotional context
- Quality metrics

This enables semantic search for recalling relevant past interactions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class InteractionSummary:
    """
    Summarized record of an agent-user interaction.
    Stored for long-term recall and pattern learning.
    """
    profile_id: str
    session_id: str
    agents_involved: List[str]

    # Summary
    summary: str
    key_topics: List[str]

    # Decisions and actions
    key_decisions: List[Dict[str, Any]] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)

    # Emotional context
    emotional_state: str = "neutral"  # positive, neutral, stressed, anxious, excited

    # Timing
    interaction_start: Optional[datetime] = None
    interaction_end: Optional[datetime] = None

    # Quality metrics from the interaction
    average_quality_score: Optional[float] = None
    cycles_used: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for database storage."""
        data = {
            "profile_id": self.profile_id,
            "session_id": self.session_id,
            "agent_involved": self.agents_involved,  # Column name in DB
            "summary": self.summary,
            "key_topics": self.key_topics,
            "key_decisions": self.key_decisions,
            "action_items": self.action_items,
            "emotional_state": self.emotional_state,
            "cycles_used": self.cycles_used,
        }
        if self.interaction_start:
            data["interaction_start"] = self.interaction_start.isoformat()
        if self.interaction_end:
            data["interaction_end"] = self.interaction_end.isoformat()
        if self.average_quality_score is not None:
            # Store in metadata since column doesn't exist
            pass  # Could add to JSONB metadata column
        return data

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate interaction duration in seconds."""
        if self.interaction_start and self.interaction_end:
            return (self.interaction_end - self.interaction_start).total_seconds()
        return None

    @property
    def is_multi_agent(self) -> bool:
        """Check if multiple agents were involved."""
        return len(self.agents_involved) > 1

    def __repr__(self) -> str:
        return (
            f"InteractionSummary(session={self.session_id}, "
            f"agents={self.agents_involved}, "
            f"topics={len(self.key_topics)})"
        )


class InteractionMemoryManager:
    """
    Manages interaction memories in Supabase.
    Supports semantic search for recall.
    
    Usage:
        manager = InteractionMemoryManager(supabase_client, embedding_model)
        
        # Store interaction
        summary = InteractionSummary(
            profile_id="abc123",
            session_id="session_456",
            agents_involved=["assessment"],
            summary="Completed initial assessment...",
            key_topics=["archetype", "spike", "activities"],
        )
        await manager.store_interaction(summary)
        
        # Recall similar interactions
        past = await manager.recall_similar_interactions(
            profile_id="abc123",
            query="archetype discussion",
            limit=5,
        )
    """

    def __init__(self, supabase_client, embedding_model=None):
        """
        Initialize InteractionMemoryManager.
        
        Args:
            supabase_client: Async Supabase client
            embedding_model: Optional embedding model for semantic search
        """
        self.supabase = supabase_client
        self.embeddings = embedding_model

    async def store_interaction(
        self,
        summary: InteractionSummary,
    ) -> Optional[str]:
        """
        Store an interaction summary with optional embedding.
        
        Args:
            summary: InteractionSummary to store
            
        Returns:
            ID of stored interaction or None on error
        """
        if not self.supabase:
            logger.warning("No Supabase client - interaction memory disabled")
            return None

        try:
            data = summary.to_dict()

            # Generate embedding for semantic search
            if self.embeddings:
                search_text = f"{summary.summary} {' '.join(summary.key_topics)}"
                embedding = await self.embeddings.encode(search_text)
                data["embedding"] = embedding.tolist()

            result = await self.supabase.table("interaction_memory").insert(data).execute()

            if result.data:
                interaction_id = result.data[0].get("id")
                logger.info(
                    f"Stored interaction for session {summary.session_id} "
                    f"(topics: {summary.key_topics[:3]}...)"
                )
                return interaction_id
            return None

        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
            return None

    async def recall_similar_interactions(
        self,
        profile_id: str,
        query: str,
        limit: int = 5,
    ) -> List[InteractionSummary]:
        """
        Semantic search for similar past interactions.
        
        Args:
            profile_id: Profile ID to search within
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of similar InteractionSummary objects
        """
        if not self.supabase:
            return []

        # Use semantic search if embeddings available
        if self.embeddings:
            return await self._semantic_recall(profile_id, query, limit)

        # Fallback to keyword search
        return await self._keyword_recall(profile_id, query, limit)

    async def _semantic_recall(
        self,
        profile_id: str,
        query: str,
        limit: int,
    ) -> List[InteractionSummary]:
        """Semantic search using embeddings."""
        try:
            query_embedding = await self.embeddings.encode(query)

            result = await self.supabase.rpc(
                "match_interaction_memory",
                {
                    "query_embedding": query_embedding.tolist(),
                    "match_threshold": 0.7,
                    "match_count": limit,
                    "filter_profile_id": profile_id,
                }
            ).execute()

            return [self._row_to_summary(row) for row in result.data or []]

        except Exception as e:
            logger.error(f"Semantic recall failed: {e}, falling back to keyword")
            return await self._keyword_recall(profile_id, query, limit)

    async def _keyword_recall(
        self,
        profile_id: str,
        query: str,
        limit: int,
    ) -> List[InteractionSummary]:
        """Keyword-based search fallback."""
        try:
            # Search in summary field
            result = await self.supabase.table("interaction_memory")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .ilike("summary", f"%{query}%")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return [self._row_to_summary(row) for row in result.data or []]

        except Exception as e:
            logger.error(f"Keyword recall failed: {e}")
            return []

    async def get_recent_interactions(
        self,
        profile_id: str,
        limit: int = 10,
    ) -> List[InteractionSummary]:
        """
        Get most recent interactions for a profile.
        
        Args:
            profile_id: Profile ID
            limit: Maximum results
            
        Returns:
            List of recent InteractionSummary objects
        """
        if not self.supabase:
            return []

        try:
            result = await self.supabase.table("interaction_memory")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return [self._row_to_summary(row) for row in result.data or []]

        except Exception as e:
            logger.error(f"Failed to get recent interactions: {e}")
            return []

    async def get_interactions_by_agent(
        self,
        profile_id: str,
        agent_name: str,
        limit: int = 10,
    ) -> List[InteractionSummary]:
        """
        Get interactions involving a specific agent.
        
        Args:
            profile_id: Profile ID
            agent_name: Name of agent to filter by
            limit: Maximum results
            
        Returns:
            List of matching InteractionSummary objects
        """
        if not self.supabase:
            return []

        try:
            result = await self.supabase.table("interaction_memory")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .contains("agent_involved", [agent_name])\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return [self._row_to_summary(row) for row in result.data or []]

        except Exception as e:
            logger.error(f"Failed to get interactions by agent: {e}")
            return []

    async def get_interactions_by_topic(
        self,
        profile_id: str,
        topic: str,
        limit: int = 10,
    ) -> List[InteractionSummary]:
        """
        Get interactions involving a specific topic.
        
        Args:
            profile_id: Profile ID
            topic: Topic to search for
            limit: Maximum results
            
        Returns:
            List of matching InteractionSummary objects
        """
        if not self.supabase:
            return []

        try:
            result = await self.supabase.table("interaction_memory")\
                .select("*")\
                .eq("profile_id", profile_id)\
                .contains("key_topics", [topic])\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return [self._row_to_summary(row) for row in result.data or []]

        except Exception as e:
            logger.error(f"Failed to get interactions by topic: {e}")
            return []

    async def get_action_items(
        self,
        profile_id: str,
        completed: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all action items across interactions.
        
        Args:
            profile_id: Profile ID
            completed: Filter by completion status (None = all)
            
        Returns:
            List of action item dicts
        """
        if not self.supabase:
            return []

        try:
            result = await self.supabase.table("interaction_memory")\
                .select("session_id, action_items, created_at")\
                .eq("profile_id", profile_id)\
                .not_.is_("action_items", "null")\
                .order("created_at", desc=True)\
                .execute()

            all_items = []
            for row in result.data or []:
                items = row.get("action_items", [])
                for item in items:
                    item["session_id"] = row["session_id"]
                    item["interaction_date"] = row["created_at"]
                    all_items.append(item)

            # Filter by completion status if specified
            if completed is not None:
                all_items = [
                    item for item in all_items
                    if item.get("completed", False) == completed
                ]

            return all_items

        except Exception as e:
            logger.error(f"Failed to get action items: {e}")
            return []

    async def get_emotional_timeline(
        self,
        profile_id: str,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get emotional state history.
        
        Returns timeline of emotional states across interactions.
        """
        if not self.supabase:
            return []

        try:
            result = await self.supabase.table("interaction_memory")\
                .select("session_id, emotional_state, created_at")\
                .eq("profile_id", profile_id)\
                .order("created_at", desc=True)\
                .limit(100)\
                .execute()

            return [
                {
                    "session_id": row["session_id"],
                    "emotional_state": row.get("emotional_state", "neutral"),
                    "date": row["created_at"],
                }
                for row in result.data or []
            ]

        except Exception as e:
            logger.error(f"Failed to get emotional timeline: {e}")
            return []

    def _row_to_summary(self, row: Dict[str, Any]) -> InteractionSummary:
        """Convert database row to InteractionSummary."""
        interaction_start = row.get("interaction_start")
        interaction_end = row.get("interaction_end")

        if isinstance(interaction_start, str):
            interaction_start = datetime.fromisoformat(
                interaction_start.replace("Z", "+00:00")
            )
        if isinstance(interaction_end, str):
            interaction_end = datetime.fromisoformat(
                interaction_end.replace("Z", "+00:00")
            )

        return InteractionSummary(
            profile_id=row["profile_id"],
            session_id=row["session_id"],
            agents_involved=row.get("agent_involved", []),
            summary=row["summary"],
            key_topics=row.get("key_topics", []),
            key_decisions=row.get("key_decisions", []),
            action_items=row.get("action_items", []),
            emotional_state=row.get("emotional_state", "neutral"),
            interaction_start=interaction_start,
            interaction_end=interaction_end,
        )
