"""
E4: Quality Scoring Pattern - Implementation

Comprehensive quality scoring for agent outputs.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class QualityDimension(str, Enum):
    """Dimensions of quality to score."""
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    ACTIONABILITY = "actionability"
    TONE = "tone"
    PERSONALIZATION = "personalization"
    TIMELINESS = "timeliness"


class DimensionScore(BaseModel):
    """Score for a single quality dimension."""
    dimension: QualityDimension
    score: float = Field(ge=0.0, le=1.0)
    weight: float = 1.0
    feedback: Optional[str] = None
    passed_threshold: bool = True


class QualityScore(BaseModel):
    """Comprehensive quality score."""
    overall_score: float = Field(default=0.5, ge=0.0, le=1.0)
    dimension_scores: List[DimensionScore] = Field(default_factory=list)
    weighted_score: float = Field(default=0.5, ge=0.0, le=1.0)
    passed: bool = True
    failed_dimensions: List[str] = Field(default_factory=list)
    feedback_summary: str = ""
    scored_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QualityThreshold(BaseModel):
    """Threshold for quality passing."""
    dimension: QualityDimension
    min_score: float = 0.6
    weight: float = 1.0
    is_critical: bool = False  # If critical, failure = overall failure


class QualityScorer:
    """
    Scores agent outputs on multiple quality dimensions.

    Pattern E4: Quality Scoring

    GUARDRAILS:
    - NEW class - does not modify existing scoring
    - Configurable dimensions and thresholds
    """

    DEFAULT_THRESHOLDS = [
        QualityThreshold(
            dimension=QualityDimension.RELEVANCE,
            min_score=0.7,
            weight=1.5,
            is_critical=True,
        ),
        QualityThreshold(
            dimension=QualityDimension.ACCURACY,
            min_score=0.8,
            weight=2.0,
            is_critical=True,
        ),
        QualityThreshold(
            dimension=QualityDimension.COMPLETENESS,
            min_score=0.6,
            weight=1.0,
        ),
        QualityThreshold(
            dimension=QualityDimension.CLARITY,
            min_score=0.7,
            weight=1.2,
        ),
        QualityThreshold(
            dimension=QualityDimension.ACTIONABILITY,
            min_score=0.6,
            weight=1.3,
        ),
        QualityThreshold(
            dimension=QualityDimension.TONE,
            min_score=0.7,
            weight=1.0,
        ),
    ]

    def __init__(
        self,
        llm_client=None,
        thresholds: Optional[List[QualityThreshold]] = None,
        use_llm_scoring: bool = True,
    ):
        """
        Initialize quality scorer.

        Args:
            llm_client: LLM client for scoring
            thresholds: Quality thresholds
            use_llm_scoring: Whether to use LLM for scoring
        """
        self.llm = llm_client
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.use_llm = use_llm_scoring

    async def score(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        original_query: Optional[str] = None,
    ) -> QualityScore:
        """
        Score content on all quality dimensions.

        Args:
            content: Content to score
            context: Additional context
            original_query: Original user query

        Returns:
            QualityScore with dimension scores
        """
        dimension_scores = []
        failed_dimensions = []

        for threshold in self.thresholds:
            score = await self._score_dimension(
                content=content,
                dimension=threshold.dimension,
                context=context,
                original_query=original_query,
            )

            passed = score >= threshold.min_score
            if not passed:
                failed_dimensions.append(threshold.dimension.value)

            dimension_scores.append(DimensionScore(
                dimension=threshold.dimension,
                score=score,
                weight=threshold.weight,
                passed_threshold=passed,
            ))

        # Calculate overall scores
        overall = sum(ds.score for ds in dimension_scores) / len(dimension_scores)

        total_weight = sum(t.weight for t in self.thresholds)
        weighted = sum(
            ds.score * ds.weight for ds in dimension_scores
        ) / total_weight

        # Check if passed
        passed = True
        for ds in dimension_scores:
            threshold = next(
                t for t in self.thresholds
                if t.dimension == ds.dimension
            )
            if threshold.is_critical and not ds.passed_threshold:
                passed = False
                break

        return QualityScore(
            overall_score=overall,
            dimension_scores=dimension_scores,
            weighted_score=weighted,
            passed=passed,
            failed_dimensions=failed_dimensions,
            feedback_summary=self._generate_feedback_summary(dimension_scores),
        )

    async def _score_dimension(
        self,
        content: str,
        dimension: QualityDimension,
        context: Optional[Dict[str, Any]],
        original_query: Optional[str],
    ) -> float:
        """Score a single dimension."""
        if self.llm and self.use_llm:
            return await self._llm_score_dimension(
                content, dimension, context, original_query
            )
        return self._heuristic_score_dimension(content, dimension)

    async def _llm_score_dimension(
        self,
        content: str,
        dimension: QualityDimension,
        context: Optional[Dict[str, Any]],
        original_query: Optional[str],
    ) -> float:
        """Score dimension using LLM."""
        dimension_prompts = {
            QualityDimension.RELEVANCE: "Does the response directly address the query?",
            QualityDimension.ACCURACY: "Is the information factually correct?",
            QualityDimension.COMPLETENESS: "Does it cover all aspects of the query?",
            QualityDimension.CLARITY: "Is it clear and easy to understand?",
            QualityDimension.ACTIONABILITY: "Does it provide clear next steps?",
            QualityDimension.TONE: "Is the tone appropriate and supportive?",
            QualityDimension.PERSONALIZATION: "Is it personalized to the context?",
            QualityDimension.TIMELINESS: "Is the information current and timely?",
        }

        prompt = f"""Score this response on {dimension.value}.

Question: {dimension_prompts.get(dimension, "Overall quality?")}

{"ORIGINAL QUERY: " + original_query if original_query else ""}
{"CONTEXT: " + str(context) if context else ""}

RESPONSE TO SCORE:
{content}

Provide a single score from 0.0 to 1.0 where:
- 0.0-0.3: Poor
- 0.4-0.6: Acceptable
- 0.7-0.8: Good
- 0.9-1.0: Excellent

OUTPUT: Just the number, e.g., "0.75" """

        try:
            response = await self.llm.chat.completions.create(
                model="gpt-4o-mini",  # Faster model for scoring
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=10,
            )

            score_text = response.choices[0].message.content.strip()
            return float(score_text)
        except Exception as e:
            logger.error(f"LLM scoring failed for {dimension}: {e}")
            return self._heuristic_score_dimension(content, dimension)

    def _heuristic_score_dimension(
        self,
        content: str,
        dimension: QualityDimension,
    ) -> float:
        """Score dimension using heuristics."""
        base_score = 0.5

        # Length-based adjustments
        length = len(content)
        if length > 100:
            base_score += 0.1
        if length > 300:
            base_score += 0.1

        # Structure-based adjustments
        has_structure = any(
            marker in content
            for marker in ["1.", "2.", "3.", "-", "•", "*"]
        )
        if has_structure:
            base_score += 0.1

        # Dimension-specific heuristics
        if dimension == QualityDimension.CLARITY:
            # Shorter sentences = clearer
            sentences = content.split(".")
            avg_sentence_len = len(content) / max(len(sentences), 1)
            if avg_sentence_len < 100:
                base_score += 0.1

        elif dimension == QualityDimension.ACTIONABILITY:
            action_words = ["should", "try", "start", "first", "next", "then"]
            if any(word in content.lower() for word in action_words):
                base_score += 0.15

        elif dimension == QualityDimension.TONE:
            supportive_words = ["great", "well done", "you can", "you've"]
            if any(word in content.lower() for word in supportive_words):
                base_score += 0.1

        return min(base_score, 1.0)

    def _generate_feedback_summary(
        self,
        dimension_scores: List[DimensionScore],
    ) -> str:
        """Generate feedback summary from scores."""
        strengths = []
        improvements = []

        for ds in dimension_scores:
            if ds.score >= 0.8:
                strengths.append(ds.dimension.value)
            elif ds.score < 0.6:
                improvements.append(ds.dimension.value)

        summary_parts = []
        if strengths:
            summary_parts.append(f"Strong on: {', '.join(strengths)}")
        if improvements:
            summary_parts.append(f"Improve: {', '.join(improvements)}")

        return ". ".join(summary_parts) if summary_parts else "Adequate overall"

    def quick_check(self, content: str) -> bool:
        """
        Quick quality check without full scoring.

        Args:
            content: Content to check

        Returns:
            True if passes basic quality checks
        """
        # Minimum length
        if len(content) < 50:
            return False

        # Not just whitespace
        if not content.strip():
            return False

        # Has some structure
        has_content = len(content.split()) > 10

        return has_content
