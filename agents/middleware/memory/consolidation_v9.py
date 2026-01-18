"""
Memory Consolidation - Merge and prune related memories.

Pattern: B6
3P: OpenAI (for similarity detection and merging)
Lines: ~120 (thin wrapper)

Features:
- Find duplicate/similar memories
- Merge related memories intelligently
- Prune low-importance memories
- Reinforce frequently accessed memories
- Graceful degradation
"""

from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ConsolidationResult(BaseModel):
    """Result of a consolidation operation."""
    merged_count: int = 0
    pruned_count: int = 0
    reinforced_count: int = 0
    errors: List[str] = []


MERGE_PROMPT = """You are consolidating memories about a user. Given these related memories, create a single unified memory that captures all the important information.

Related memories:
{memories}

Return a JSON object with:
- content: The merged memory content (comprehensive but concise)
- memory_type: The type (fact, preference, goal, insight)
- importance: Combined importance (0-1)

Only merge if the memories are truly about the same topic. If they're different topics, set importance to 0 to skip merging."""


class MemoryConsolidator:
    """
    Consolidates and maintains memory quality.

    Pattern B6: Memory Consolidation
    3P: OpenAI (for intelligent merging)

    Works with B4 (LongTermMemory) and B3 (SemanticMemory).
    """

    MODEL = "gpt-4o-mini"
    MAX_MEMORIES_PER_CONSOLIDATION = 100

    def __init__(
        self,
        openai_client=None,
        longterm_manager=None,
        semantic_manager=None,
    ):
        self.openai = openai_client
        self.longterm = longterm_manager
        self.semantic = semantic_manager
        self._initialized = openai_client is not None

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def consolidate(
        self,
        profile_id: str,
        prune_threshold: float = 0.2,
        merge_similarity: float = 0.85,
    ) -> ConsolidationResult:
        """Run full consolidation: merge similar, prune low-importance."""
        result = ConsolidationResult()

        if not self.is_available:
            logger.warning("MemoryConsolidator not available - no OpenAI client")
            result.errors.append("No OpenAI client available")
            return result

        # Step 1: Prune low-importance memories
        pruned = await self._prune_low_importance(profile_id, prune_threshold)
        result.pruned_count = pruned

        # Step 2: Find and merge similar memories (if semantic manager available)
        if self.semantic:
            merged = await self._merge_similar(profile_id, merge_similarity)
            result.merged_count = merged

        # Step 3: Reinforce frequently accessed memories
        if self.longterm:
            reinforced = await self._reinforce_accessed(profile_id)
            result.reinforced_count = reinforced

        return result

    async def _prune_low_importance(
        self,
        profile_id: str,
        threshold: float,
    ) -> int:
        """Remove memories below importance threshold."""
        if not self.longterm or not self.longterm.is_available:
            return 0

        try:
            # Get low-importance memories
            all_memories = await self.longterm.recall_all(
                profile_id=profile_id,
                min_importance=0.0,
                limit=self.MAX_MEMORIES_PER_CONSOLIDATION,
            )

            pruned = 0
            for memory in all_memories:
                if memory.importance < threshold:
                    success = await self.longterm.forget(profile_id, memory.key)
                    if success:
                        pruned += 1

            return pruned
        except Exception as e:
            logger.error(f"Failed to prune memories: {e}")
            return 0

    async def _merge_similar(
        self,
        profile_id: str,
        similarity_threshold: float,
    ) -> int:
        """Find and merge semantically similar memories."""
        if not self.semantic or not self.semantic.is_available:
            return 0

        try:
            # Get all memories for comparison
            memories = await self.semantic.get_by_type(
                profile_id=profile_id,
                memory_type="general",
                limit=self.MAX_MEMORIES_PER_CONSOLIDATION,
            )

            if len(memories) < 2:
                return 0

            merged = 0
            processed_indices = set()

            for i, memory in enumerate(memories):
                if i in processed_indices:
                    continue

                # Search for similar memories
                similar = await self.semantic.search(
                    profile_id=profile_id,
                    query=memory.content,
                    min_similarity=similarity_threshold,
                    limit=5,
                )

                # Filter to actual duplicates (excluding self)
                duplicates = [
                    s for s in similar
                    if s.content != memory.content and s.similarity >= similarity_threshold
                ]

                if duplicates:
                    # Merge this group
                    success = await self._merge_memory_group(
                        profile_id=profile_id,
                        memories=[memory] + duplicates,
                    )
                    if success:
                        merged += len(duplicates)
                        # Mark as processed
                        for j, m in enumerate(memories):
                            if any(d.content == m.content for d in duplicates):
                                processed_indices.add(j)

            return merged
        except Exception as e:
            logger.error(f"Failed to merge memories: {e}")
            return 0

    async def _merge_memory_group(
        self,
        profile_id: str,
        memories: List[Any],
    ) -> bool:
        """Use LLM to intelligently merge a group of related memories."""
        if not self.openai:
            return False

        try:
            # Format memories for prompt
            memory_texts = "\n".join([
                f"- {m.content} (type: {m.memory_type}, importance: {m.importance})"
                for m in memories
            ])

            response = self.openai.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You merge related memories into a single comprehensive memory. Return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": MERGE_PROMPT.format(memories=memory_texts)
                    }
                ],
                response_format={"type": "json_object"},
            )

            merged_data = json.loads(response.choices[0].message.content)

            # Skip if LLM determined they shouldn't be merged
            if merged_data.get("importance", 0) == 0:
                return False

            # Store merged memory
            if self.semantic:
                await self.semantic.store(
                    profile_id=profile_id,
                    content=merged_data["content"],
                    memory_type=merged_data.get("memory_type", "fact"),
                    importance=merged_data.get("importance", 0.5),
                    metadata={"merged_from": len(memories)},
                )

            return True
        except Exception as e:
            logger.error(f"Failed to merge memory group: {e}")
            return False

    async def _reinforce_accessed(
        self,
        profile_id: str,
        boost_amount: float = 0.05,
    ) -> int:
        """Boost importance of frequently accessed memories."""
        if not self.longterm or not self.longterm.is_available:
            return 0

        try:
            # Get memories and check access patterns
            memories = await self.longterm.recall_all(
                profile_id=profile_id,
                limit=self.MAX_MEMORIES_PER_CONSOLIDATION,
            )

            reinforced = 0
            for memory in memories:
                # Reinforce memories with importance between 0.3 and 0.9
                if 0.3 <= memory.importance < 0.9:
                    success = await self.longterm.update_importance(
                        profile_id=profile_id,
                        key=memory.key,
                        importance_delta=boost_amount,
                    )
                    if success:
                        reinforced += 1

            return reinforced
        except Exception as e:
            logger.error(f"Failed to reinforce memories: {e}")
            return 0

    async def decay_unused(
        self,
        profile_id: str,
        decay_amount: float = 0.02,
        min_importance: float = 0.1,
    ) -> int:
        """Decay importance of unused memories over time."""
        if not self.longterm or not self.longterm.is_available:
            return 0

        try:
            memories = await self.longterm.recall_all(
                profile_id=profile_id,
                min_importance=min_importance,
                limit=self.MAX_MEMORIES_PER_CONSOLIDATION,
            )

            decayed = 0
            for memory in memories:
                if memory.importance > min_importance:
                    success = await self.longterm.update_importance(
                        profile_id=profile_id,
                        key=memory.key,
                        importance_delta=-decay_amount,
                    )
                    if success:
                        decayed += 1

            return decayed
        except Exception as e:
            logger.error(f"Failed to decay memories: {e}")
            return 0
