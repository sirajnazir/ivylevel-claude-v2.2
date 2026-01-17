"""
B2: Episodic Memory Pattern - Implementation

Record and retrieve past experiences. Enables "Last time we tried X, Y happened."
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from datetime import datetime
from pydantic import BaseModel, Field
import logging
import uuid

logger = logging.getLogger(__name__)


class Episode(BaseModel):
    """A recorded experience/episode."""
    episode_id: str
    profile_id: str

    # What happened
    situation: str  # "Student stuck on RSI essay intro"
    context: Dict[str, Any] = Field(default_factory=dict)  # State at the time

    # What we did
    action_taken: str  # "Provided 3 example hooks"
    approach_type: str  # "examples_over_instructions"
    agent_name: str

    # What resulted
    outcome: str  # "success", "partial", "failure"
    outcome_details: Dict[str, Any] = Field(default_factory=dict)
    student_response: Optional[str] = None  # How student reacted

    # What we learned
    learnings: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    significance_score: float = Field(default=0.5, ge=0.0, le=1.0)

    def to_summary(self) -> str:
        """Convert to natural language summary."""
        return (
            f"Situation: {self.situation}\n"
            f"Action: {self.action_taken}\n"
            f"Outcome: {self.outcome}\n"
            f"Learning: {', '.join(self.learnings) if self.learnings else 'None recorded'}"
        )


class EpisodeQuery(BaseModel):
    """Query for finding relevant episodes."""
    profile_id: str
    situation_query: Optional[str] = None
    approach_types: Optional[List[str]] = None
    outcomes: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    min_significance: float = 0.0
    max_results: int = 5


class EpisodeRetrievalResult(BaseModel):
    """Result of episode retrieval."""
    episodes: List[Episode]
    query_embedding_used: bool = False
    total_found: int = 0


class EpisodicMemoryManager:
    """
    Manages episodic memory (experiences).

    Pattern B2: Episodic Memory

    Enables:
    - "Last time we tried X, Y happened"
    - Learning from what worked/didn't work
    - Personalizing approach based on past success

    Integration with Critical 15:
    - Uses B7 Memory Retrieval for semantic search
    - Feeds I3 Goal Monitoring with outcome data
    - Enhances A12 Prioritization with success history
    """

    def __init__(
        self,
        supabase_client=None,
        embedding_func: Optional[Callable[[str], Awaitable[List[float]]]] = None,
    ):
        """
        Initialize episodic memory manager.

        Args:
            supabase_client: For persistence
            embedding_func: Function to generate embeddings
        """
        self.supabase = supabase_client
        self.embed = embedding_func
        self._cache: Dict[str, List[Episode]] = {}

    async def record_episode(
        self,
        profile_id: str,
        situation: str,
        action_taken: str,
        approach_type: str,
        agent_name: str,
        outcome: str,
        context: Optional[Dict[str, Any]] = None,
        outcome_details: Optional[Dict[str, Any]] = None,
        student_response: Optional[str] = None,
        learnings: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Episode:
        """
        Record a new episode.

        Args:
            profile_id: Student profile
            situation: What was happening
            action_taken: What we did
            approach_type: Type of approach used
            agent_name: Which agent acted
            outcome: "success", "partial", "failure"
            context: State at the time
            outcome_details: Details about outcome
            student_response: How student reacted
            learnings: What we learned
            tags: Categorization tags

        Returns:
            Recorded Episode
        """
        # Calculate significance
        significance = self._calculate_significance(outcome, context)

        episode = Episode(
            episode_id=str(uuid.uuid4()),
            profile_id=profile_id,
            situation=situation,
            context=context or {},
            action_taken=action_taken,
            approach_type=approach_type,
            agent_name=agent_name,
            outcome=outcome,
            outcome_details=outcome_details or {},
            student_response=student_response,
            learnings=learnings or [],
            tags=tags or [],
            significance_score=significance,
        )

        # Persist
        await self._persist_episode(episode)

        # Update cache
        if profile_id not in self._cache:
            self._cache[profile_id] = []
        self._cache[profile_id].append(episode)

        logger.info(
            f"Recorded episode: {episode.episode_id} "
            f"({outcome}, significance={significance})"
        )

        return episode

    async def recall_similar(
        self,
        profile_id: str,
        current_situation: str,
        k: int = 5,
    ) -> List[Episode]:
        """
        Recall episodes similar to current situation.

        Args:
            profile_id: Student profile
            current_situation: What's happening now
            k: Number of episodes to retrieve

        Returns:
            List of similar past episodes
        """
        if not self.supabase:
            return []

        # Generate embedding if available
        if self.embed:
            try:
                embedding = await self.embed(current_situation)

                result = self.supabase.rpc(
                    "match_episodes",
                    {
                        "query_embedding": embedding,
                        "match_count": k,
                        "filter_profile_id": profile_id,
                    }
                ).execute()

                if result.data:
                    return [Episode(**ep) for ep in result.data]
            except Exception as e:
                logger.warning(f"Semantic episode search failed: {e}")

        # Fallback to recent episodes
        return await self.get_recent_episodes(profile_id, k)

    async def recall_by_approach(
        self,
        profile_id: str,
        approach_type: str,
        outcome_filter: Optional[str] = None,
    ) -> List[Episode]:
        """
        Recall episodes using a specific approach.

        Args:
            profile_id: Student profile
            approach_type: Type of approach used
            outcome_filter: Filter by outcome ("success", "failure", etc.)

        Returns:
            Episodes matching criteria
        """
        if not self.supabase:
            return []

        query = self.supabase.table("episodic_memory").select("*").eq(
            "profile_id", profile_id
        ).eq("approach_type", approach_type)

        if outcome_filter:
            query = query.eq("outcome", outcome_filter)

        try:
            result = query.order("created_at", desc=True).limit(10).execute()
            return [Episode(**ep) for ep in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Episode recall failed: {e}")
            return []

    async def get_recent_episodes(
        self,
        profile_id: str,
        limit: int = 10,
    ) -> List[Episode]:
        """Get most recent episodes for a student."""
        if not self.supabase:
            return []

        try:
            result = self.supabase.table("episodic_memory").select("*").eq(
                "profile_id", profile_id
            ).order("created_at", desc=True).limit(limit).execute()

            return [Episode(**ep) for ep in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Get recent episodes failed: {e}")
            return []

    async def get_success_patterns(
        self,
        profile_id: str,
    ) -> Dict[str, Any]:
        """
        Analyze successful patterns for a student.

        Returns patterns like:
        - "examples_over_instructions works 80% of the time"
        - "morning sessions have higher completion rates"
        """
        if not self.supabase:
            return {}

        try:
            result = self.supabase.table("episodic_memory").select(
                "approach_type, outcome"
            ).eq("profile_id", profile_id).execute()

            if not result.data:
                return {}

            # Analyze by approach type
            approach_stats: Dict[str, Dict[str, int]] = {}
            for ep in result.data:
                approach = ep["approach_type"]
                outcome = ep["outcome"]

                if approach not in approach_stats:
                    approach_stats[approach] = {"success": 0, "total": 0}

                approach_stats[approach]["total"] += 1
                if outcome == "success":
                    approach_stats[approach]["success"] += 1

            # Calculate success rates
            patterns = {}
            for approach, stats in approach_stats.items():
                if stats["total"] >= 3:  # Minimum sample size
                    success_rate = stats["success"] / stats["total"]
                    patterns[approach] = {
                        "success_rate": success_rate,
                        "sample_size": stats["total"],
                        "recommendation": "use" if success_rate >= 0.6 else "avoid",
                    }

            return patterns
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {}

    def _calculate_significance(
        self,
        outcome: str,
        context: Optional[Dict[str, Any]],
    ) -> float:
        """Calculate how significant an episode is."""
        significance = 0.5

        # Outcomes matter more
        if outcome == "success":
            significance += 0.2
        elif outcome == "failure":
            significance += 0.15  # Failures are also valuable to learn from

        # High-stakes situations matter more
        context = context or {}
        if context.get("high_stakes"):
            significance += 0.2
        if context.get("deadline_pressure"):
            significance += 0.1
        if context.get("crisis_detected"):
            significance += 0.2

        return min(significance, 1.0)

    async def _persist_episode(self, episode: Episode) -> None:
        """Persist episode to database."""
        if not self.supabase:
            return

        try:
            # Generate embedding for situation
            embedding = None
            if self.embed:
                embedding = await self.embed(episode.situation)

            data = {
                "id": episode.episode_id,
                "profile_id": episode.profile_id,
                "situation": episode.situation,
                "context": episode.context,
                "action_taken": episode.action_taken,
                "approach_type": episode.approach_type,
                "agent_name": episode.agent_name,
                "outcome": episode.outcome,
                "outcome_details": episode.outcome_details,
                "student_response": episode.student_response,
                "learnings": episode.learnings,
                "tags": episode.tags,
                "significance_score": episode.significance_score,
                "created_at": episode.created_at.isoformat(),
            }

            if embedding:
                data["embedding"] = embedding

            self.supabase.table("episodic_memory").insert(data).execute()
        except Exception as e:
            logger.error(f"Failed to persist episode: {e}")


# Convenience function for recording from agent context
async def record_coaching_episode(
    manager: EpisodicMemoryManager,
    profile_id: str,
    agent_name: str,
    situation: str,
    action: str,
    outcome: str,
    context: Optional[Dict[str, Any]] = None,
) -> Episode:
    """
    Convenience function to record a coaching episode.

    Usage:
        await record_coaching_episode(
            manager=episodic_memory,
            profile_id="123",
            agent_name="execution_agent",
            situation="Student stuck on essay intro",
            action="Provided 3 example hooks",
            outcome="success",
            context={"approach": "examples_over_instructions"}
        )
    """
    return await manager.record_episode(
        profile_id=profile_id,
        situation=situation,
        action_taken=action,
        approach_type=context.get("approach", "general") if context else "general",
        agent_name=agent_name,
        outcome=outcome,
        context=context,
    )
