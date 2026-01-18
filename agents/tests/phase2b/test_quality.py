"""
Tests for E2: LLM-as-Judge, E4: Quality Scoring, E5: Coherence Checking Patterns
"""

import pytest
from datetime import datetime, timezone
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.quality.llm_judge_v8 import (
    LLMJudge,
    JudgmentResult,
    JudgmentCriterion,
    JudgmentRating,
)
from middleware.quality.quality_scoring_v8 import (
    QualityScorer,
    QualityScore,
    QualityDimension,
    DimensionScore,
    QualityThreshold,
)
from middleware.quality.coherence_v8 import (
    CoherenceChecker,
    CoherenceResult,
    CoherenceType,
    CoherenceIssue,
)


class TestJudgmentCriterion:
    """Tests for JudgmentCriterion model."""

    def test_criterion_creation(self):
        """Test JudgmentCriterion creation."""
        criterion = JudgmentCriterion(
            name="helpfulness",
            description="Response is helpful to the student",
            weight=0.3,
        )
        assert criterion.name == "helpfulness"
        assert criterion.weight == 0.3

    def test_criterion_with_min_acceptable(self):
        """Test JudgmentCriterion with min_acceptable."""
        criterion = JudgmentCriterion(
            name="clarity",
            description="Response is clear",
            weight=0.2,
            min_acceptable=0.7,
        )
        assert criterion.min_acceptable == 0.7


class TestJudgmentResult:
    """Tests for JudgmentResult model."""

    def test_result_creation(self):
        """Test JudgmentResult creation."""
        result = JudgmentResult(
            overall_score=0.85,
            overall_rating=JudgmentRating.GOOD,
            criterion_scores={"helpfulness": 0.9, "clarity": 0.8},
        )
        assert result.overall_rating == JudgmentRating.GOOD
        assert result.overall_score == 0.85

    def test_result_with_feedback(self):
        """Test JudgmentResult with feedback."""
        result = JudgmentResult(
            overall_score=0.6,
            overall_rating=JudgmentRating.ACCEPTABLE,
            criterion_scores={"helpfulness": 0.5},
            weaknesses=["Needs more actionable advice"],
            recommendations=["Add specific steps"],
        )
        assert len(result.recommendations) == 1
        assert len(result.weaknesses) == 1


class TestLLMJudge:
    """Tests for LLMJudge."""

    @pytest.fixture
    def judge(self, mock_llm):
        return LLMJudge(llm_client=mock_llm)

    def test_judge_creation(self, judge):
        """Test judge creation."""
        assert judge is not None
        assert judge.judge_model == "gpt-4o"

    def test_judge_creation_with_params(self, mock_llm):
        """Test judge creation with custom params."""
        judge = LLMJudge(
            llm_client=mock_llm,
            judge_model="gpt-4",
        )
        assert judge.judge_model == "gpt-4"

    def test_default_criteria_exist(self):
        """Test default criteria are defined on judge."""
        judge = LLMJudge()
        assert len(judge.DEFAULT_CRITERIA) > 0
        names = [c.name for c in judge.DEFAULT_CRITERIA]
        assert "helpfulness" in names
        assert "accuracy" in names

    @pytest.mark.asyncio
    async def test_judge_without_llm(self):
        """Test judging without LLM returns fallback score."""
        judge = LLMJudge()
        result = await judge.judge(
            content="Test response to student with good content and examples",
        )
        assert isinstance(result, JudgmentResult)
        assert result.overall_score >= 0.5

    @pytest.mark.asyncio
    async def test_compare_without_llm(self):
        """Test comparing without LLM."""
        judge = LLMJudge()
        result = await judge.compare(
            content_a="Response A",
            content_b="Response B",
        )
        assert "winner" in result


class TestQualityDimension:
    """Tests for QualityDimension enum."""

    def test_dimension_values(self):
        """Test QualityDimension enum values."""
        assert QualityDimension.RELEVANCE.value == "relevance"
        assert QualityDimension.ACCURACY.value == "accuracy"
        assert QualityDimension.CLARITY.value == "clarity"


class TestDimensionScore:
    """Tests for DimensionScore model."""

    def test_dimension_score_creation(self):
        """Test DimensionScore creation."""
        ds = DimensionScore(
            dimension=QualityDimension.RELEVANCE,
            score=0.85,
            weight=0.25,
        )
        assert ds.dimension == QualityDimension.RELEVANCE
        assert ds.score == 0.85

    def test_dimension_score_with_feedback(self):
        """Test DimensionScore with feedback."""
        ds = DimensionScore(
            dimension=QualityDimension.CLARITY,
            score=0.6,
            weight=0.2,
            feedback="Could be clearer",
        )
        assert ds.feedback == "Could be clearer"


class TestQualityScore:
    """Tests for QualityScore model."""

    def test_score_creation(self):
        """Test QualityScore creation."""
        score = QualityScore(
            overall_score=0.82,
            passed=True,
            dimension_scores=[
                DimensionScore(dimension=QualityDimension.RELEVANCE, score=0.9, weight=0.3),
                DimensionScore(dimension=QualityDimension.CLARITY, score=0.75, weight=0.3),
            ],
        )
        assert score.passed == True
        assert len(score.dimension_scores) == 2

    def test_score_with_feedback(self):
        """Test QualityScore with feedback summary."""
        score = QualityScore(
            overall_score=0.8,
            passed=True,
            dimension_scores=[],
            feedback_summary="Strong on clarity",
        )
        assert score.feedback_summary == "Strong on clarity"


class TestQualityScorer:
    """Tests for QualityScorer."""

    @pytest.fixture
    def scorer(self, mock_llm):
        return QualityScorer(llm_client=mock_llm)

    def test_scorer_creation(self, scorer):
        """Test scorer creation."""
        assert scorer is not None
        assert scorer.thresholds is not None
        assert len(scorer.thresholds) > 0

    def test_scorer_creation_with_params(self, mock_llm):
        """Test scorer creation with custom params."""
        custom_thresholds = [
            QualityThreshold(
                dimension=QualityDimension.RELEVANCE,
                min_score=0.8,
                weight=2.0,
            ),
        ]
        scorer = QualityScorer(
            llm_client=mock_llm,
            thresholds=custom_thresholds,
        )
        assert len(scorer.thresholds) == 1
        assert scorer.thresholds[0].min_score == 0.8

    @pytest.mark.asyncio
    async def test_score_heuristic(self):
        """Test heuristic scoring (no LLM)."""
        scorer = QualityScorer(use_llm_scoring=False)
        result = await scorer.score(
            content="This is a helpful response that provides clear guidance with specific examples.",
        )
        assert isinstance(result, QualityScore)
        # Heuristic scoring provides dimension scores
        assert len(result.dimension_scores) > 0

    @pytest.mark.asyncio
    async def test_score_short_content(self):
        """Test scoring short content."""
        scorer = QualityScorer(use_llm_scoring=False)
        result = await scorer.score(
            content="Ok",
        )
        # Short content should score lower
        assert result.overall_score < 0.7


class TestCoherenceType:
    """Tests for CoherenceType enum."""

    def test_coherence_types(self):
        """Test coherence type values."""
        assert CoherenceType.LOGICAL.value == "logical"
        assert CoherenceType.TEMPORAL.value == "temporal"
        assert CoherenceType.FACTUAL.value == "factual"
        assert CoherenceType.TONAL.value == "tonal"
        assert CoherenceType.TOPICAL.value == "topical"


class TestCoherenceIssue:
    """Tests for CoherenceIssue model."""

    def test_issue_creation(self):
        """Test CoherenceIssue creation."""
        issue = CoherenceIssue(
            issue_type=CoherenceType.FACTUAL,
            description="Contradicting information about deadline",
            severity="high",
            location="Response 2 contradicts Response 1",
        )
        assert issue.issue_type == CoherenceType.FACTUAL
        assert issue.severity == "high"


class TestCoherenceResult:
    """Tests for CoherenceResult model."""

    def test_result_creation(self):
        """Test CoherenceResult creation."""
        result = CoherenceResult(
            is_coherent=True,
            coherence_score=0.9,
            issues=[],
        )
        assert result.is_coherent == True
        assert result.coherence_score == 0.9

    def test_result_with_issues(self):
        """Test CoherenceResult with issues."""
        result = CoherenceResult(
            is_coherent=False,
            coherence_score=0.5,
            issues=[
                CoherenceIssue(
                    issue_type=CoherenceType.LOGICAL,
                    description="Contradicting advice",
                    severity="high",
                ),
            ],
        )
        assert result.is_coherent == False
        assert len(result.issues) == 1


class TestCoherenceChecker:
    """Tests for CoherenceChecker."""

    @pytest.fixture
    def checker(self, mock_llm):
        return CoherenceChecker(llm_client=mock_llm)

    def test_checker_creation(self, checker):
        """Test checker creation."""
        assert checker is not None
        assert checker.min_score == 0.7

    def test_checker_creation_with_params(self, mock_llm):
        """Test checker creation with custom params."""
        checker = CoherenceChecker(
            llm_client=mock_llm,
            min_coherence_score=0.85,
        )
        assert checker.min_score == 0.85

    @pytest.mark.asyncio
    async def test_check_coherence_single_response(self, checker):
        """Test checking coherence with single response."""
        result = await checker.check_coherence(
            current_response="Single response here.",
        )
        assert isinstance(result, CoherenceResult)
        # Single response should be coherent
        assert result.is_coherent == True

    @pytest.mark.asyncio
    async def test_check_coherence_with_history(self, checker):
        """Test checking coherence with conversation history."""
        result = await checker.check_coherence(
            current_response="Great progress on the math problems!",
            conversation_history=[
                {"role": "assistant", "content": "You should focus on math today."},
                {"role": "user", "content": "Okay, I'll work on math."},
                {"role": "assistant", "content": "Let's continue working on your math skills."},
            ],
        )
        assert isinstance(result, CoherenceResult)

    @pytest.mark.asyncio
    async def test_check_coherence_without_llm(self):
        """Test checking coherence without LLM."""
        checker = CoherenceChecker()
        result = await checker.check_coherence(
            current_response="Response 1",
        )
        assert isinstance(result, CoherenceResult)
