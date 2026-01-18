"""
I4: Strategy Effectiveness Pattern - Implementation

Track which coaching strategies work for which students.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class StrategyOutcome(str, Enum):
    """Outcomes for strategy applications."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class StrategyApplication(BaseModel):
    """Record of a strategy being applied."""
    application_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy: str  # e.g., "examples_over_instructions", "socratic_questioning"
    context_type: str  # e.g., "essay_help", "activity_planning"
    profile_id: str
    session_id: str
    input_situation: str
    strategy_response: str
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    outcome: Optional[StrategyOutcome] = None
    outcome_reason: Optional[str] = None
    measured_at: Optional[datetime] = None
    student_response_positive: Optional[bool] = None
    task_completed: Optional[bool] = None
    engagement_score: Optional[float] = None


class StrategyEffectiveness(BaseModel):
    """Effectiveness metrics for a strategy."""
    strategy: str
    context_type: str
    total_applications: int = 0
    success_count: int = 0
    partial_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    avg_engagement: Optional[float] = None
    sample_size: int = 0
    confidence: str = "low"  # low, medium, high


class StrategyEffectivenessTracker:
    """
    Tracks strategy effectiveness across students and contexts.

    Pattern I4: Strategy Effectiveness

    GUARDRAILS:
    - NEW class - does not modify existing tracking
    - Uses Supabase for persistence
    - Provides recommendations based on history
    """

    def __init__(
        self,
        supabase_client=None,
        min_sample_size: int = 10,
    ):
        """
        Initialize tracker.

        Args:
            supabase_client: For persistence
            min_sample_size: Minimum samples for reliable stats
        """
        self.supabase = supabase_client
        self.min_samples = min_sample_size
        self._cache: Dict[str, List[StrategyApplication]] = defaultdict(list)

    async def record_application(
        self,
        strategy: str,
        context_type: str,
        profile_id: str,
        session_id: str,
        input_situation: str,
        strategy_response: str,
    ) -> StrategyApplication:
        """
        Record a strategy being applied.

        Args:
            strategy: Strategy name
            context_type: Context where applied
            profile_id: Student profile
            session_id: Session ID
            input_situation: Situation before strategy
            strategy_response: Agent's response using strategy

        Returns:
            StrategyApplication record
        """
        application = StrategyApplication(
            strategy=strategy,
            context_type=context_type,
            profile_id=profile_id,
            session_id=session_id,
            input_situation=input_situation,
            strategy_response=strategy_response,
        )

        # Cache for later measurement
        cache_key = f"{profile_id}:{session_id}"
        self._cache[cache_key].append(application)

        # Persist
        await self._persist_application(application)

        logger.debug(
            f"Recorded strategy application: {strategy} for {context_type}"
        )

        return application

    async def record_outcome(
        self,
        application_id: str,
        outcome: StrategyOutcome,
        reason: Optional[str] = None,
        student_response_positive: Optional[bool] = None,
        task_completed: Optional[bool] = None,
        engagement_score: Optional[float] = None,
    ) -> Optional[StrategyApplication]:
        """
        Record the outcome of a strategy application.

        Args:
            application_id: Application to update
            outcome: What happened
            reason: Why this outcome
            student_response_positive: Student reaction
            task_completed: Whether task completed
            engagement_score: 0-1 engagement metric

        Returns:
            Updated application
        """
        # Find in cache first
        application = None
        for cache_key, apps in self._cache.items():
            for app in apps:
                if app.application_id == application_id:
                    application = app
                    break

        if application:
            application.outcome = outcome
            application.outcome_reason = reason
            application.measured_at = datetime.now(timezone.utc)
            application.student_response_positive = student_response_positive
            application.task_completed = task_completed
            application.engagement_score = engagement_score

            # Update in database
            await self._update_outcome(application)

            logger.debug(
                f"Recorded outcome for {application.strategy}: {outcome.value}"
            )

            return application

        # Try database directly
        if self.supabase:
            try:
                self.supabase.table("phase2b_strategy_applications").update({
                    "outcome": outcome.value,
                    "outcome_reason": reason,
                    "measured_at": datetime.now(timezone.utc).isoformat(),
                    "student_response_positive": student_response_positive,
                    "task_completed": task_completed,
                    "engagement_score": engagement_score,
                }).eq("application_id", application_id).execute()
            except Exception as e:
                logger.error(f"Failed to update outcome: {e}")

        return None

    async def get_effectiveness(
        self,
        strategy: str,
        context_type: Optional[str] = None,
        profile_id: Optional[str] = None,
    ) -> StrategyEffectiveness:
        """
        Get effectiveness metrics for a strategy.

        Args:
            strategy: Strategy to analyze
            context_type: Optional context filter
            profile_id: Optional profile filter

        Returns:
            StrategyEffectiveness metrics
        """
        applications = await self._get_applications(
            strategy=strategy,
            context_type=context_type,
            profile_id=profile_id,
        )

        # Filter to those with outcomes
        measured = [a for a in applications if a.outcome is not None]

        if not measured:
            return StrategyEffectiveness(
                strategy=strategy,
                context_type=context_type or "all",
            )

        success = sum(1 for a in measured if a.outcome == StrategyOutcome.SUCCESS)
        partial = sum(1 for a in measured if a.outcome == StrategyOutcome.PARTIAL)
        failure = sum(1 for a in measured if a.outcome == StrategyOutcome.FAILURE)

        total = success + partial + failure
        success_rate = success / total if total > 0 else 0

        # Calculate average engagement
        engagement_scores = [
            a.engagement_score for a in measured
            if a.engagement_score is not None
        ]
        avg_engagement = (
            sum(engagement_scores) / len(engagement_scores)
            if engagement_scores else None
        )

        # Determine confidence
        confidence = "low"
        if total >= self.min_samples * 2:
            confidence = "high"
        elif total >= self.min_samples:
            confidence = "medium"

        return StrategyEffectiveness(
            strategy=strategy,
            context_type=context_type or "all",
            total_applications=len(applications),
            success_count=success,
            partial_count=partial,
            failure_count=failure,
            success_rate=success_rate,
            avg_engagement=avg_engagement,
            sample_size=total,
            confidence=confidence,
        )

    async def recommend_strategy(
        self,
        context_type: str,
        profile_id: str,
        available_strategies: List[str],
    ) -> Optional[str]:
        """
        Recommend best strategy for situation.

        Args:
            context_type: Context for strategy
            profile_id: Student profile
            available_strategies: Strategies to choose from

        Returns:
            Recommended strategy or None
        """
        best_strategy = None
        best_score = -1

        for strategy in available_strategies:
            # Get profile-specific effectiveness
            profile_eff = await self.get_effectiveness(
                strategy=strategy,
                context_type=context_type,
                profile_id=profile_id,
            )

            # Get general effectiveness
            general_eff = await self.get_effectiveness(
                strategy=strategy,
                context_type=context_type,
            )

            # Weighted score: prefer profile-specific if available
            if profile_eff.sample_size >= 3:
                score = profile_eff.success_rate
            elif general_eff.confidence != "low":
                score = general_eff.success_rate
            else:
                continue

            if score > best_score:
                best_score = score
                best_strategy = strategy

        if best_strategy:
            logger.info(
                f"Recommended strategy {best_strategy} for {context_type} "
                f"(score: {best_score:.2f})"
            )

        return best_strategy

    async def get_strategy_comparison(
        self,
        context_type: str,
        strategies: List[str],
    ) -> List[StrategyEffectiveness]:
        """
        Compare multiple strategies for a context.

        Args:
            context_type: Context to compare
            strategies: Strategies to compare

        Returns:
            List of effectiveness metrics
        """
        results = []
        for strategy in strategies:
            eff = await self.get_effectiveness(
                strategy=strategy,
                context_type=context_type,
            )
            results.append(eff)

        # Sort by success rate
        results.sort(key=lambda e: e.success_rate, reverse=True)
        return results

    async def _get_applications(
        self,
        strategy: str,
        context_type: Optional[str] = None,
        profile_id: Optional[str] = None,
    ) -> List[StrategyApplication]:
        """Get applications from database."""
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("phase2b_strategy_applications").select(
                "*"
            ).eq("strategy", strategy)

            if context_type:
                query = query.eq("context_type", context_type)
            if profile_id:
                query = query.eq("profile_id", profile_id)

            result = query.execute()

            return [
                StrategyApplication(
                    application_id=r["application_id"],
                    strategy=r["strategy"],
                    context_type=r["context_type"],
                    profile_id=r["profile_id"],
                    session_id=r["session_id"],
                    input_situation=r.get("input_situation", ""),
                    strategy_response=r.get("strategy_response", ""),
                    applied_at=datetime.fromisoformat(r["applied_at"]),
                    outcome=StrategyOutcome(r["outcome"]) if r.get("outcome") else None,
                    outcome_reason=r.get("outcome_reason"),
                    measured_at=datetime.fromisoformat(r["measured_at"]) if r.get("measured_at") else None,
                    student_response_positive=r.get("student_response_positive"),
                    task_completed=r.get("task_completed"),
                    engagement_score=r.get("engagement_score"),
                )
                for r in result.data
            ]
        except Exception as e:
            logger.error(f"Failed to get applications: {e}")
            return []

    async def _persist_application(self, app: StrategyApplication) -> None:
        """Persist application to database."""
        if not self.supabase:
            return

        try:
            self.supabase.table("phase2b_strategy_applications").insert({
                "application_id": app.application_id,
                "strategy": app.strategy,
                "context_type": app.context_type,
                "profile_id": app.profile_id,
                "session_id": app.session_id,
                "input_situation": app.input_situation,
                "strategy_response": app.strategy_response,
                "applied_at": app.applied_at.isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to persist application: {e}")

    async def _update_outcome(self, app: StrategyApplication) -> None:
        """Update outcome in database."""
        if not self.supabase:
            return

        try:
            self.supabase.table("phase2b_strategy_applications").update({
                "outcome": app.outcome.value if app.outcome else None,
                "outcome_reason": app.outcome_reason,
                "measured_at": app.measured_at.isoformat() if app.measured_at else None,
                "student_response_positive": app.student_response_positive,
                "task_completed": app.task_completed,
                "engagement_score": app.engagement_score,
            }).eq("application_id", app.application_id).execute()
        except Exception as e:
            logger.error(f"Failed to update outcome: {e}")
