# agents/agents/core/golden_benchmark.py
"""
IvyQuest v13.2 - Golden Benchmark

This module compares agent outputs against golden examples from Phase 3
evaluation. Golden examples are high-quality outputs that have been
validated by human reviewers and serve as quality calibration.

The GoldenBenchmark class supports:
- Loading golden examples from Supabase
- Semantic similarity using embeddings
- Structural similarity fallback
- Caching for performance
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class GoldenExample:
    """
    A golden example for quality comparison.
    
    Golden examples represent high-quality agent outputs that serve
    as benchmarks for comparing new outputs.
    """
    id: str
    agent_type: str
    input_context: Dict[str, Any]
    expected_output: Dict[str, Any]
    quality_score: float
    voice_score: float
    archetype: Optional[str] = None
    tags: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_type": self.agent_type,
            "quality_score": self.quality_score,
            "voice_score": self.voice_score,
            "archetype": self.archetype,
            "tags": self.tags or [],
        }


class GoldenBenchmark:
    """
    Compares agent outputs against golden examples from Phase 3 evaluation.
    
    Golden examples are high-quality outputs that have been validated
    by human reviewers and serve as quality calibration.
    
    Usage:
        benchmark = GoldenBenchmark("narrative_synthesis")
        await benchmark.load_golden_examples(archetype="DoubleDown")
        similarity = await benchmark.compute_similarity(output, context)
    """

    def __init__(
        self,
        agent_type: str,
        supabase_client=None,
        embedding_model=None,
    ):
        """
        Initialize GoldenBenchmark.
        
        Args:
            agent_type: Type of agent (e.g., "narrative_synthesis", "assessment")
            supabase_client: Optional Supabase client for loading examples
            embedding_model: Optional embedding model for semantic similarity
        """
        self.agent_type = agent_type
        self.supabase = supabase_client
        self.embeddings = embedding_model
        self._golden_cache: List[GoldenExample] = []
        self._cache_archetype: Optional[str] = None

    async def load_golden_examples(
        self,
        archetype: Optional[str] = None,
        limit: int = 10,
    ) -> List[GoldenExample]:
        """
        Load golden examples from database.
        
        Args:
            archetype: Optional archetype to filter by
            limit: Maximum number of examples to load
            
        Returns:
            List of GoldenExample objects
        """
        # Return cache if archetype matches
        if self._golden_cache and self._cache_archetype == archetype:
            return self._golden_cache

        if not self.supabase:
            logger.warning("No Supabase client - using empty golden set")
            return []

        try:
            query = self.supabase.table("coaching_knowledge")\
                .select("*")\
                .eq("source_type", "golden_example")\
                .eq("category", self.agent_type)\
                .order("effectiveness_score", desc=True)\
                .limit(limit)

            if archetype:
                query = query.contains("applicable_archetypes", [archetype])

            result = await query.execute()

            self._golden_cache = [
                GoldenExample(
                    id=row["id"],
                    agent_type=row["category"],
                    input_context=row.get("content", {}).get("input", {}),
                    expected_output=row.get("content", {}).get("output", {}),
                    quality_score=row.get("effectiveness_score", 0.8) * 100,
                    voice_score=85.0,  # Golden examples should have high voice scores
                    archetype=archetype,
                    tags=row.get("applicable_archetypes", []),
                )
                for row in result.data or []
            ]
            self._cache_archetype = archetype

            logger.info(
                f"Loaded {len(self._golden_cache)} golden examples "
                f"for {self.agent_type} (archetype={archetype})"
            )

            return self._golden_cache
        except Exception as e:
            logger.error(f"Failed to load golden examples: {e}")
            return []

    async def compute_similarity(
        self,
        output: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """
        Compute similarity between output and best matching golden example.
        
        Args:
            output: The agent's output to compare
            context: Context dict containing optional "archetype" key
            
        Returns:
            float: Similarity score 0-1 (1 = identical to golden)
        """
        # Ensure we have golden examples loaded
        if not self._golden_cache:
            await self.load_golden_examples(
                archetype=context.get("archetype")
            )

        if not self._golden_cache:
            # No golden examples available - return neutral score
            logger.debug("No golden examples available, returning 0.7")
            return 0.7

        # Use semantic similarity if embedding model available
        if self.embeddings:
            return await self._compute_semantic_similarity(output)

        # Fallback to structural similarity
        return self._compute_structural_similarity(output)

    async def _compute_semantic_similarity(
        self,
        output: Dict[str, Any],
    ) -> float:
        """
        Compute semantic similarity using embeddings.
        
        Compares the output embedding against all cached golden example
        embeddings and returns the highest similarity score.
        """
        try:
            output_text = json.dumps(output, sort_keys=True, default=str)
            output_embedding = await self.embeddings.encode(output_text)

            best_similarity = 0.0
            for golden in self._golden_cache:
                golden_text = json.dumps(golden.expected_output, sort_keys=True, default=str)
                golden_embedding = await self.embeddings.encode(golden_text)

                similarity = self._cosine_similarity(output_embedding, golden_embedding)
                best_similarity = max(best_similarity, similarity)

            logger.debug(f"Semantic similarity: {best_similarity:.3f}")
            return best_similarity
        except Exception as e:
            logger.warning(f"Semantic similarity failed: {e}, falling back to structural")
            return self._compute_structural_similarity(output)

    def _compute_structural_similarity(
        self,
        output: Dict[str, Any],
    ) -> float:
        """
        Compute structural similarity based on key overlap.
        
        Uses Jaccard similarity on flattened dictionary keys.
        """
        if not self._golden_cache:
            return 0.7

        output_keys = set(self._flatten_keys(output))

        best_similarity = 0.0
        for golden in self._golden_cache:
            golden_keys = set(self._flatten_keys(golden.expected_output))

            if not golden_keys:
                continue

            # Jaccard similarity
            intersection = len(output_keys & golden_keys)
            union = len(output_keys | golden_keys)
            similarity = intersection / union if union > 0 else 0

            best_similarity = max(best_similarity, similarity)

        logger.debug(f"Structural similarity: {best_similarity:.3f}")
        return best_similarity

    def _flatten_keys(self, d: Dict, prefix: str = "") -> List[str]:
        """
        Flatten nested dict keys into dot-notation paths.
        
        Example:
            {"a": {"b": 1, "c": 2}} -> ["a", "a.b", "a.c"]
        """
        keys = []
        for k, v in d.items():
            new_key = f"{prefix}.{k}" if prefix else k
            keys.append(new_key)
            if isinstance(v, dict):
                keys.extend(self._flatten_keys(v, new_key))
        return keys

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0-1)
        """
        if len(vec1) != len(vec2):
            return 0.0
        
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot / (norm1 * norm2)

    def get_best_matching_example(
        self,
        output: Dict[str, Any],
    ) -> Optional[GoldenExample]:
        """
        Get the golden example that best matches the output.
        
        Args:
            output: The agent's output to match
            
        Returns:
            Best matching GoldenExample or None if no cache
        """
        if not self._golden_cache:
            return None

        output_keys = set(self._flatten_keys(output))
        best_match = None
        best_score = 0.0

        for golden in self._golden_cache:
            golden_keys = set(self._flatten_keys(golden.expected_output))
            intersection = len(output_keys & golden_keys)
            if intersection > best_score:
                best_score = intersection
                best_match = golden

        return best_match

    def get_improvement_suggestions(
        self,
        output: Dict[str, Any],
    ) -> List[str]:
        """
        Get suggestions for improving output based on golden examples.
        
        Compares output keys against golden examples and suggests
        missing elements.
        
        Returns:
            List of improvement suggestions
        """
        if not self._golden_cache:
            return []

        suggestions = []
        output_keys = set(self._flatten_keys(output))

        # Find keys present in golden but missing from output
        for golden in self._golden_cache:
            golden_keys = set(self._flatten_keys(golden.expected_output))
            missing = golden_keys - output_keys
            
            # Convert missing keys to suggestions
            for key in missing:
                if "." in key:
                    parent, child = key.rsplit(".", 1)
                    suggestions.append(f"Consider adding '{child}' to '{parent}'")
                else:
                    suggestions.append(f"Consider adding '{key}' field")

        # Deduplicate and limit
        return list(set(suggestions))[:5]

    def clear_cache(self) -> None:
        """Clear the golden examples cache."""
        self._golden_cache = []
        self._cache_archetype = None

    @property
    def cache_size(self) -> int:
        """Number of cached golden examples."""
        return len(self._golden_cache)

    def __repr__(self) -> str:
        return (
            f"GoldenBenchmark(agent_type={self.agent_type}, "
            f"cache_size={self.cache_size})"
        )
