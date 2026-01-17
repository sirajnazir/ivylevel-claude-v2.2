"""
B2: Episodic Memory Pattern - Phase 2A

Record and retrieve past experiences.
Enables "Last time we tried X, Y happened."

Usage:
    from middleware.memory import EpisodicMemoryManager, Episode

    manager = EpisodicMemoryManager(supabase_client)

    # Record an episode
    episode = await manager.record_episode(
        profile_id="123",
        situation="Student stuck on essay",
        action_taken="Provided examples",
        approach_type="examples_over_instructions",
        agent_name="execution_agent",
        outcome="success",
    )

    # Recall similar episodes
    similar = await manager.recall_similar(profile_id, "essay help", k=5)
"""

from .episodic import (
    EpisodicMemoryManager,
    Episode,
    EpisodeQuery,
    EpisodeRetrievalResult,
    record_coaching_episode,
)

__all__ = [
    "EpisodicMemoryManager",
    "Episode",
    "EpisodeQuery",
    "EpisodeRetrievalResult",
    "record_coaching_episode",
]
