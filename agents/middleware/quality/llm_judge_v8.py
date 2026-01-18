"""
E2: LLM-as-Judge Pattern - Implementation

Use LLM to evaluate output quality against criteria.

NEW FILE - Does not modify existing v7.0 code.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import logging
import json
import re

logger = logging.getLogger(__name__)


class JudgmentRating(str, Enum):
    """Rating levels for judgment."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


class JudgmentCriterion(BaseModel):
    """A single evaluation criterion."""
    name: str
    description: str
    weight: float = 1.0
    min_acceptable: float = 0.6


class JudgmentResult(BaseModel):
    """Result of LLM judgment."""
    overall_rating: JudgmentRating = JudgmentRating.ACCEPTABLE
    overall_score: float = Field(default=0.5, ge=0.0, le=1.0)
    criterion_scores: Dict[str, float] = Field(default_factory=dict)
    criterion_feedback: Dict[str, str] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    judge_model: str = "gpt-4o"
    judged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LLMJudge:
    """
    Uses LLM to evaluate content against criteria.

    Pattern E2: LLM-as-Judge

    GUARDRAILS:
    - NEW class - does not modify existing evaluation
    - Uses separate judge model to avoid bias
    """

    DEFAULT_CRITERIA = [
        JudgmentCriterion(
            name="accuracy",
            description="Information is factually correct and relevant",
            weight=1.5,
        ),
        JudgmentCriterion(
            name="helpfulness",
            description="Response actually helps the student progress",
            weight=1.5,
        ),
        JudgmentCriterion(
            name="clarity",
            description="Response is clear and easy to understand",
            weight=1.0,
        ),
        JudgmentCriterion(
            name="empathy",
            description="Response shows understanding of student's situation",
            weight=1.0,
        ),
        JudgmentCriterion(
            name="actionability",
            description="Response provides clear next steps",
            weight=1.2,
        ),
    ]

    def __init__(
        self,
        llm_client=None,
        judge_model: str = "gpt-4o",
        criteria: Optional[List[JudgmentCriterion]] = None,
    ):
        """
        Initialize LLM judge.

        Args:
            llm_client: LLM client for judging
            judge_model: Model to use for judgment
            criteria: Evaluation criteria
        """
        self.llm = llm_client
        self.judge_model = judge_model
        self.criteria = criteria or self.DEFAULT_CRITERIA

    async def judge(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        reference: Optional[str] = None,
    ) -> JudgmentResult:
        """
        Judge content against criteria.

        Args:
            content: Content to evaluate
            context: Additional context
            reference: Optional reference/gold standard

        Returns:
            JudgmentResult with scores and feedback
        """
        if not self.llm:
            return self._fallback_judgment(content)

        criteria_desc = "\n".join([
            f"- {c.name} (weight: {c.weight}): {c.description}"
            for c in self.criteria
        ])

        judge_prompt = f"""Evaluate this content against the specified criteria.

CONTENT TO EVALUATE:
{content}

{"CONTEXT: " + json.dumps(context) if context else ""}
{"REFERENCE/GOLD STANDARD: " + reference if reference else ""}

EVALUATION CRITERIA:
{criteria_desc}

For each criterion, provide:
1. Score (0.0 to 1.0)
2. Brief feedback explaining the score

Then provide:
- Overall strengths (2-3 points)
- Overall weaknesses (2-3 points)
- Recommendations for improvement (2-3 points)

OUTPUT as JSON:
{{
    "criterion_scores": {{"criterion_name": score, ...}},
    "criterion_feedback": {{"criterion_name": "feedback", ...}},
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "recommendations": ["...", "..."]
}}"""

        try:
            response = await self.llm.chat.completions.create(
                model=self.judge_model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator. Be rigorous but fair."},
                    {"role": "user", "content": judge_prompt},
                ],
                temperature=0.3,
            )

            return self._parse_judgment(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Judgment failed: {e}")
            return self._fallback_judgment(content)

    def _parse_judgment(self, content: str) -> JudgmentResult:
        """Parse LLM judgment into result."""
        try:
            # Extract JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "{" in content:
                start = content.index("{")
                end = content.rindex("}") + 1
                json_str = content[start:end]
            else:
                json_str = content

            data = json.loads(json_str)

            # Calculate overall score
            total_weight = sum(c.weight for c in self.criteria)
            weighted_sum = sum(
                data.get("criterion_scores", {}).get(c.name, 0.5) * c.weight
                for c in self.criteria
            )
            overall_score = weighted_sum / total_weight if total_weight > 0 else 0.5

            # Determine rating
            if overall_score >= 0.9:
                rating = JudgmentRating.EXCELLENT
            elif overall_score >= 0.75:
                rating = JudgmentRating.GOOD
            elif overall_score >= 0.6:
                rating = JudgmentRating.ACCEPTABLE
            elif overall_score >= 0.4:
                rating = JudgmentRating.NEEDS_IMPROVEMENT
            else:
                rating = JudgmentRating.POOR

            return JudgmentResult(
                overall_rating=rating,
                overall_score=overall_score,
                criterion_scores=data.get("criterion_scores", {}),
                criterion_feedback=data.get("criterion_feedback", {}),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                recommendations=data.get("recommendations", []),
                judge_model=self.judge_model,
            )

        except Exception as e:
            logger.error(f"Failed to parse judgment: {e}")
            return JudgmentResult(
                overall_rating=JudgmentRating.ACCEPTABLE,
                overall_score=0.5,
                judge_model=self.judge_model,
            )

    def _fallback_judgment(self, content: str) -> JudgmentResult:
        """Fallback judgment without LLM."""
        # Simple heuristic-based scoring
        score = 0.5

        # Length check
        if len(content) > 100:
            score += 0.1
        if len(content) > 500:
            score += 0.1

        # Structure check
        if any(marker in content for marker in ["1.", "2.", "-", "•"]):
            score += 0.1

        score = min(score, 1.0)

        rating = JudgmentRating.ACCEPTABLE
        if score >= 0.7:
            rating = JudgmentRating.GOOD

        return JudgmentResult(
            overall_rating=rating,
            overall_score=score,
            judge_model="heuristic",
        )

    async def compare(
        self,
        content_a: str,
        content_b: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Compare two pieces of content.

        Args:
            content_a: First content
            content_b: Second content
            context: Additional context

        Returns:
            Comparison result
        """
        if not self.llm:
            return {"winner": "tie", "confidence": 0.5}

        compare_prompt = f"""Compare these two responses and determine which is better.

RESPONSE A:
{content_a}

RESPONSE B:
{content_b}

{"CONTEXT: " + json.dumps(context) if context else ""}

Evaluate both on: accuracy, helpfulness, clarity, empathy, actionability.

OUTPUT as JSON:
{{
    "winner": "A" or "B" or "tie",
    "confidence": 0.0-1.0,
    "reasoning": "explanation",
    "a_strengths": ["..."],
    "b_strengths": ["..."]
}}"""

        try:
            response = await self.llm.chat.completions.create(
                model=self.judge_model,
                messages=[{"role": "user", "content": compare_prompt}],
                temperature=0.3,
            )

            content = response.choices[0].message.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            else:
                json_str = content
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {"winner": "tie", "confidence": 0.5}

    async def batch_judge(
        self,
        contents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[JudgmentResult]:
        """
        Judge multiple contents.

        Args:
            contents: List of contents to judge
            context: Shared context

        Returns:
            List of judgment results
        """
        results = []
        for content in contents:
            result = await self.judge(content, context)
            results.append(result)
        return results

    def is_acceptable(self, result: JudgmentResult) -> bool:
        """
        Check if judgment result is acceptable.

        Args:
            result: Judgment result

        Returns:
            True if all criteria meet minimum thresholds
        """
        for criterion in self.criteria:
            score = result.criterion_scores.get(criterion.name, 0.5)
            if score < criterion.min_acceptable:
                return False
        return True
