"""
AssetSelector - Intelligent asset selection based on context and effectiveness.

This is the brain that decides WHICH coaching asset to use WHEN.

Selection criteria:
1. Trigger conditions match the current context
2. Applicability matches the student profile
3. Effectiveness for the student's archetype
4. Recency (avoid repeating recently used assets)
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
import logging
from datetime import datetime, timedelta

from ..primitives import CoachingAsset, AssetType, AssetDomain
from ..student import StudentIntelligenceProfile
from .asset_registry import AssetRegistry

logger = logging.getLogger(__name__)


class SelectionResult:
    """Result of asset selection with reasoning."""

    def __init__(
        self,
        asset: Optional[CoachingAsset],
        score: float,
        reasoning: List[str],
        alternatives: List[CoachingAsset] = None,
    ):
        self.asset = asset
        self.score = score
        self.reasoning = reasoning
        self.alternatives = alternatives or []

    @property
    def success(self) -> bool:
        return self.asset is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "asset_id": str(self.asset.id) if self.asset else None,
            "asset_name": self.asset.name if self.asset else None,
            "score": self.score,
            "reasoning": self.reasoning,
            "alternatives_count": len(self.alternatives),
        }


class AssetSelector:
    """
    Intelligently selects the best coaching asset for a given situation.

    Selection algorithm:
    1. Filter by trigger conditions
    2. Filter by student applicability
    3. Score by effectiveness (weighted by archetype)
    4. Penalize recently used assets
    5. Return best match with alternatives
    """

    def __init__(
        self,
        registry: AssetRegistry,
        recent_usage_window_hours: int = 24,
        repeat_penalty: float = 0.3,
    ):
        """
        Initialize the selector.

        Args:
            registry: The asset registry for database access
            recent_usage_window_hours: Hours to look back for repeat penalty
            repeat_penalty: Score penalty (0-1) for recently used assets
        """
        self.registry = registry
        self.recent_window = timedelta(hours=recent_usage_window_hours)
        self.repeat_penalty = repeat_penalty

    async def select(
        self,
        context: Dict[str, Any],
        student_profile: StudentIntelligenceProfile,
        domain: Optional[AssetDomain] = None,
        asset_type: Optional[AssetType] = None,
        exclude_ids: Optional[List[UUID]] = None,
        limit: int = 5,
    ) -> SelectionResult:
        """
        Select the best coaching asset for the given context.

        Args:
            context: Current situation context (event_type, emotional_state, etc.)
            student_profile: The student's intelligence profile
            domain: Optional domain filter
            asset_type: Optional type filter
            exclude_ids: Asset IDs to exclude from selection
            limit: Maximum number of alternatives to return

        Returns:
            SelectionResult with best asset, score, reasoning, and alternatives
        """
        reasoning = []
        exclude_ids = exclude_ids or []

        # Step 1: Get candidate assets
        candidates = await self._get_candidates(domain, asset_type)
        reasoning.append(f"Found {len(candidates)} candidate assets")

        if not candidates:
            return SelectionResult(
                asset=None,
                score=0,
                reasoning=reasoning + ["No candidates found for filters"],
            )

        # Step 2: Filter by trigger conditions
        triggered = [a for a in candidates if a.matches_trigger(context)]
        reasoning.append(f"{len(triggered)} assets match trigger conditions")

        # If no trigger matches, use all candidates but note it
        if not triggered:
            triggered = candidates
            reasoning.append("Using all candidates (no trigger matches)")

        # Step 3: Filter by student applicability
        student_context = self._build_student_context(student_profile)
        applicable = [a for a in triggered if a.applies_to_student(student_context)]
        reasoning.append(f"{len(applicable)} assets applicable to student")

        # If no applicability matches, use triggered but note it
        if not applicable:
            applicable = triggered
            reasoning.append("Using triggered assets (no applicability matches)")

        # Step 4: Remove excluded assets
        applicable = [a for a in applicable if a.id not in exclude_ids]

        # Step 5: Score remaining assets
        archetype = student_context.get("archetype")
        scored = []

        for asset in applicable:
            score = self._calculate_score(asset, archetype, context)
            scored.append((asset, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Step 6: Apply repeat penalty (would need recent usage data)
        # For now, we'll skip this as it requires additional DB query
        # TODO: Add recent usage check

        if not scored:
            return SelectionResult(
                asset=None,
                score=0,
                reasoning=reasoning + ["No assets passed all filters"],
            )

        best_asset, best_score = scored[0]
        alternatives = [a for a, _ in scored[1:limit]]

        reasoning.append(f"Selected '{best_asset.name}' with score {best_score:.2f}")
        reasoning.append(f"Effectiveness for archetype '{archetype}': {best_asset.get_effectiveness_for_archetype(archetype or 'default'):.2f}")

        return SelectionResult(
            asset=best_asset,
            score=best_score,
            reasoning=reasoning,
            alternatives=alternatives,
        )

    async def select_multiple(
        self,
        context: Dict[str, Any],
        student_profile: StudentIntelligenceProfile,
        count: int = 3,
        domain: Optional[AssetDomain] = None,
        asset_type: Optional[AssetType] = None,
    ) -> List[SelectionResult]:
        """Select multiple complementary assets."""
        results = []
        exclude = []

        for _ in range(count):
            result = await self.select(
                context=context,
                student_profile=student_profile,
                domain=domain,
                asset_type=asset_type,
                exclude_ids=exclude,
            )

            if result.success:
                results.append(result)
                exclude.append(result.asset.id)
            else:
                break

        return results

    async def select_for_crisis(
        self,
        crisis_type: str,
        student_profile: StudentIntelligenceProfile,
    ) -> SelectionResult:
        """Select the best asset for a crisis situation."""
        context = {
            "event_type": "crisis",
            "emotional_state": "distressed",
            "crisis_type": crisis_type,
        }

        return await self.select(
            context=context,
            student_profile=student_profile,
            domain=AssetDomain.EMOTIONAL,
            asset_type=AssetType.TECHNIQUE,
        )

    async def select_for_milestone(
        self,
        milestone_type: str,
        student_profile: StudentIntelligenceProfile,
    ) -> SelectionResult:
        """Select the best asset for celebrating a milestone."""
        context = {
            "event_type": "milestone",
            "milestone_type": milestone_type,
        }

        return await self.select(
            context=context,
            student_profile=student_profile,
            asset_type=AssetType.TECHNIQUE,
        )

    async def _get_candidates(
        self,
        domain: Optional[AssetDomain],
        asset_type: Optional[AssetType],
    ) -> List[CoachingAsset]:
        """Get candidate assets based on filters."""
        if domain and asset_type:
            return await self.registry.list_by_type(asset_type, domain)
        elif domain:
            return await self.registry.list_by_domain(domain)
        elif asset_type:
            return await self.registry.list_by_type(asset_type)
        else:
            # Get a mix of common assets
            techniques = await self.registry.list_by_type(AssetType.TECHNIQUE, limit=20)
            templates = await self.registry.list_by_type(AssetType.TEMPLATE, limit=20)
            return techniques + templates

    def _build_student_context(
        self,
        profile: StudentIntelligenceProfile,
    ) -> Dict[str, Any]:
        """Build student context from intelligence profile."""
        adaptations = profile.get_coaching_adaptations()

        return {
            "archetype": self._infer_archetype(profile),
            "overwhelm_threshold": profile.overwhelm_threshold,
            "risk_tolerance": profile.risk_tolerance,
            "communication_style": profile.communication_style,
            "adaptations": adaptations,
        }

    def _infer_archetype(
        self,
        profile: StudentIntelligenceProfile,
    ) -> str:
        """Infer student archetype from profile patterns."""
        # Simple archetype inference based on key traits
        if profile.pressure_response == "thrives" and profile.risk_tolerance == "high":
            return "achiever"
        elif profile.motivation_style == "intrinsic" and profile.feedback_reception == "direct":
            return "scholar"
        elif profile.motivation_style == "social" and profile.celebration_preference == "shared":
            return "collaborator"
        elif profile.task_approach == "deadline_driven" and profile.failure_recovery == "quick":
            return "sprinter"
        elif profile.risk_tolerance in ["low", "very_low"] and profile.failure_recovery == "slow":
            return "perfectionist"
        else:
            return "balanced"

    def _calculate_score(
        self,
        asset: CoachingAsset,
        archetype: Optional[str],
        context: Dict[str, Any],
    ) -> float:
        """Calculate selection score for an asset."""
        score = 0.5  # Base score

        # Effectiveness component (0-0.4)
        if archetype:
            effectiveness = asset.get_effectiveness_for_archetype(archetype)
        else:
            effectiveness = asset.effectiveness.global_success_rate

        score += effectiveness * 0.4

        # Confidence component (0-0.1)
        confidence = asset.effectiveness.confidence_level
        score += confidence * 0.1

        # Trigger match bonus (0-0.1)
        if asset.matches_trigger(context):
            score += 0.1

        # Tag relevance bonus (0-0.1)
        context_tags = context.get("tags", [])
        if context_tags and asset.tags:
            overlap = len(set(context_tags) & set(asset.tags))
            score += min(0.1, overlap * 0.02)

        return min(1.0, score)

    async def get_recommendations(
        self,
        student_profile: StudentIntelligenceProfile,
        domains: Optional[List[AssetDomain]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get recommended assets for a student based on their profile."""
        archetype = self._infer_archetype(student_profile)
        domains = domains or [AssetDomain.EXECUTION, AssetDomain.STRATEGY, AssetDomain.EMOTIONAL]

        recommendations = []

        for domain in domains:
            top_assets = await self.registry.get_top_effective(
                domain=domain,
                archetype=archetype,
                min_usage=3,
                limit=2,
            )

            for asset in top_assets:
                recommendations.append({
                    "asset": asset,
                    "domain": domain,
                    "effectiveness": asset.get_effectiveness_for_archetype(archetype),
                    "reason": f"Top performer for {archetype} archetypes in {domain}",
                })

        # Sort by effectiveness
        recommendations.sort(key=lambda x: x["effectiveness"], reverse=True)

        return recommendations[:limit]
