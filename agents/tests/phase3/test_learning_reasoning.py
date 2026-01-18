"""
Tests for Learning & Reasoning Patterns (I1, I2, I3, I5, A5, A12)

Pattern: I1 (Feedback), I2 (Adaptation), I3 (Patterns), I5 (Preferences),
         A5 (Adaptive Prompting), A12 (Metacognition)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.learning.feedback_v9 import FeedbackLoop, Feedback
from middleware.learning.adaptation_v9 import BehaviorAdapter, Adaptation
from middleware.learning.patterns_v9 import PatternRecognizer, RecognizedPattern
from middleware.learning.preferences_v9 import PreferenceLearner, Preference
from middleware.reasoning.adaptive_v9 import AdaptivePrompter, AdaptivePrompt
from middleware.reasoning.metacognition_v9 import Metacognitor, MetacognitiveAnalysis


# ============= I1: Feedback Loop Tests =============

class TestFeedbackLoop:
    """Tests for I1: Feedback Loop."""

    @pytest.fixture
    def feedback_loop(self):
        return FeedbackLoop()

    def test_is_available(self, feedback_loop):
        """Test feedback loop is always available."""
        assert feedback_loop.is_available is True

    @pytest.mark.asyncio
    async def test_record_feedback(self, feedback_loop):
        """Test recording feedback."""
        feedback = await feedback_loop.record(
            profile_id="test",
            feedback_type="explicit",
            sentiment="positive",
            score=0.9,
        )

        assert isinstance(feedback, Feedback)
        assert feedback.sentiment == "positive"

    @pytest.mark.asyncio
    async def test_record_positive(self, feedback_loop):
        """Test recording positive feedback."""
        feedback = await feedback_loop.record_positive("test")

        assert feedback.sentiment == "positive"
        assert feedback.score > 0.5

    @pytest.mark.asyncio
    async def test_record_negative(self, feedback_loop):
        """Test recording negative feedback."""
        feedback = await feedback_loop.record_negative("test")

        assert feedback.sentiment == "negative"
        assert feedback.score < 0.5

    @pytest.mark.asyncio
    async def test_record_implicit(self, feedback_loop):
        """Test recording implicit feedback."""
        feedback = await feedback_loop.record_implicit(
            profile_id="test",
            signal_type="engagement",
            score=0.8,
        )

        assert feedback.feedback_type == "implicit"

    def test_get_session_score(self, feedback_loop):
        """Test getting session score."""
        feedback_loop._session_feedback.append(Feedback(score=0.8))
        feedback_loop._session_feedback.append(Feedback(score=0.6))

        score = feedback_loop.get_session_score()
        assert score == 0.7

    def test_get_session_sentiment(self, feedback_loop):
        """Test getting session sentiment."""
        feedback_loop._session_feedback.append(Feedback(score=0.9))

        sentiment = feedback_loop.get_session_sentiment()
        assert sentiment == "positive"


# ============= I2: Behavior Adaptation Tests =============

class TestBehaviorAdapter:
    """Tests for I2: Behavior Adaptation."""

    @pytest.fixture
    def adapter(self):
        return BehaviorAdapter()

    def test_is_available(self, adapter):
        """Test adapter is always available."""
        assert adapter.is_available is True

    @pytest.mark.asyncio
    async def test_adapt(self, adapter):
        """Test creating an adaptation."""
        adaptation = await adapter.adapt(
            profile_id="test",
            adaptation_type="tone",
            new_value="casual",
            reason="User prefers informal style",
        )

        assert isinstance(adaptation, Adaptation)
        assert adaptation.new_value == "casual"

    @pytest.mark.asyncio
    async def test_revert(self, adapter):
        """Test reverting an adaptation."""
        await adapter.adapt("test", "tone", "casual")

        result = await adapter.revert("test", "tone")

        assert result is True

    def test_get_current_params(self, adapter):
        """Test getting current parameters."""
        params = adapter.get_current_params()

        assert "tone" in params
        assert "detail_level" in params

    def test_apply_to_prompt(self, adapter):
        """Test applying adaptations to prompt."""
        adapter._current_params["tone"] = "casual"
        adapter._current_params["detail_level"] = "high"

        prompt = adapter.apply_to_prompt("Base prompt")

        assert "casual" in prompt.lower()
        assert "detailed" in prompt.lower() or "thorough" in prompt.lower()

    def test_reset(self, adapter):
        """Test resetting adaptations."""
        adapter._current_params["tone"] = "casual"
        adapter.reset()

        assert adapter._current_params["tone"] == "professional"


# ============= I3: Pattern Recognition Tests =============

class TestPatternRecognizer:
    """Tests for I3: Pattern Recognition."""

    @pytest.fixture
    def recognizer(self):
        return PatternRecognizer()

    def test_is_available(self, recognizer):
        """Test recognizer is always available."""
        assert recognizer.is_available is True

    @pytest.mark.asyncio
    async def test_observe_no_pattern(self, recognizer):
        """Test observing without forming pattern."""
        result = await recognizer.observe(
            profile_id="test",
            pattern_type="topic",
            value="math",
        )

        # First observation shouldn't form a pattern
        assert result is None

    @pytest.mark.asyncio
    async def test_observe_forms_pattern(self, recognizer):
        """Test observing until pattern forms."""
        for _ in range(5):
            result = await recognizer.observe(
                profile_id="test",
                pattern_type="topic",
                value="math",
            )

        assert result is not None
        assert result.pattern_value == "math"

    def test_get_patterns(self, recognizer):
        """Test getting patterns."""
        recognizer._patterns["topic"] = {
            "math": RecognizedPattern(
                pattern_type="topic",
                pattern_value="math",
                confidence=0.8,
            )
        }

        patterns = recognizer.get_patterns()
        assert len(patterns) == 1

    def test_predict_next(self, recognizer):
        """Test predicting next value."""
        recognizer._patterns["topic"] = {
            "math": RecognizedPattern(
                pattern_type="topic",
                pattern_value="math",
                confidence=0.8,
            )
        }

        prediction = recognizer.predict_next("topic")
        assert prediction == "math"

    def test_clear(self, recognizer):
        """Test clearing patterns."""
        recognizer._patterns["test"] = {}
        recognizer.clear()
        assert len(recognizer._patterns) == 0


# ============= I5: Preference Learning Tests =============

class TestPreferenceLearner:
    """Tests for I5: Preference Learning."""

    @pytest.fixture
    def learner(self):
        return PreferenceLearner()

    def test_is_available(self, learner):
        """Test learner is always available."""
        assert learner.is_available is True

    @pytest.mark.asyncio
    async def test_set_preference(self, learner):
        """Test setting a preference."""
        preference = await learner.set_preference(
            profile_id="test",
            key="response_length",
            value="long",
        )

        assert isinstance(preference, Preference)
        assert preference.preference_value == "long"

    @pytest.mark.asyncio
    async def test_infer_preference(self, learner):
        """Test inferring a preference."""
        preference = await learner.infer_preference(
            profile_id="test",
            key="technical_depth",
            value="high",
        )

        assert preference.source == "inferred"

    def test_get_preference(self, learner):
        """Test getting a preference."""
        value = learner.get_preference("response_length")
        assert value == "medium"  # Default

    def test_get_all_preferences(self, learner):
        """Test getting all preferences."""
        prefs = learner.get_all_preferences()

        assert "response_length" in prefs
        assert "technical_depth" in prefs

    def test_apply_to_system_prompt(self, learner):
        """Test applying preferences to prompt."""
        learner._preferences["response_length"] = Preference(
            preference_key="response_length",
            preference_value="long",
            confidence=0.9,
        )

        prompt = learner.apply_to_system_prompt("Base prompt")
        assert "comprehensive" in prompt.lower() or "detailed" in prompt.lower()

    def test_reset(self, learner):
        """Test resetting preferences."""
        learner._preferences["test"] = Preference(preference_key="test", preference_value="x")
        learner.reset()

        assert "test" not in learner._preferences


# ============= A5: Adaptive Prompting Tests =============

class TestAdaptivePrompter:
    """Tests for A5: Adaptive Prompting."""

    @pytest.fixture
    def mock_preferences(self):
        """Mock preference learner."""
        prefs = MagicMock()
        prefs.apply_to_system_prompt = MagicMock(return_value="Prompt with preferences")
        prefs.get_high_confidence_preferences = MagicMock(return_value={"length": "long"})
        return prefs

    @pytest.fixture
    def mock_adapter(self):
        """Mock behavior adapter."""
        adapter = MagicMock()
        adapter.apply_to_prompt = MagicMock(return_value="Prompt with adaptations")
        adapter.get_current_params = MagicMock(return_value={"tone": "casual"})
        return adapter

    @pytest.fixture
    def prompter(self, mock_preferences, mock_adapter):
        return AdaptivePrompter(
            preference_learner=mock_preferences,
            behavior_adapter=mock_adapter,
        )

    @pytest.fixture
    def prompter_basic(self):
        return AdaptivePrompter()

    def test_is_available(self, prompter):
        """Test prompter is always available."""
        assert prompter.is_available is True

    @pytest.mark.asyncio
    async def test_adapt(self, prompter):
        """Test adapting a prompt."""
        result = await prompter.adapt(
            profile_id="test",
            base_prompt="Base prompt",
        )

        assert isinstance(result, AdaptivePrompt)
        assert "preferences" in result.adaptations_applied
        assert "behavior" in result.adaptations_applied

    @pytest.mark.asyncio
    async def test_adapt_basic(self, prompter_basic):
        """Test basic adaptation without dependencies."""
        result = await prompter_basic.adapt(
            profile_id="test",
            base_prompt="Base prompt",
        )

        assert result.adapted_prompt == "Base prompt"

    @pytest.mark.asyncio
    async def test_adapt_for_task(self, prompter):
        """Test adapting for specific task."""
        result = await prompter.adapt_for_task(
            profile_id="test",
            base_prompt="Base prompt",
            task_type="essay_review",
        )

        assert "essay" in result.original_prompt.lower() or "constructive" in result.original_prompt.lower()


# ============= A12: Metacognition Tests =============

class TestMetacognitor:
    """Tests for A12: Metacognition."""

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client."""
        client = MagicMock()

        mock_message = MagicMock()
        mock_message.content = json.dumps({
            "overall_confidence": 0.7,
            "knowledge_gaps": ["Topic A"],
            "assumptions": ["Assumption 1"],
            "limitations": ["Limitation 1"],
            "suggested_actions": ["Action 1"],
        })

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        client.chat.completions.create.return_value = mock_response
        return client

    @pytest.fixture
    def metacognitor(self, mock_openai):
        return Metacognitor(openai_client=mock_openai)

    @pytest.fixture
    def metacognitor_no_client(self):
        return Metacognitor(openai_client=None)

    def test_is_available_with_client(self, metacognitor):
        """Test availability with client."""
        assert metacognitor.is_available is True

    def test_is_available_without_client(self, metacognitor_no_client):
        """Test availability without client."""
        assert metacognitor_no_client.is_available is False

    @pytest.mark.asyncio
    async def test_analyze(self, metacognitor):
        """Test metacognitive analysis."""
        result = await metacognitor.analyze(
            request="What is machine learning?",
            response="Machine learning is a subset of AI...",
        )

        assert isinstance(result, MetacognitiveAnalysis)
        assert result.overall_confidence == 0.7
        assert len(result.knowledge_gaps) > 0

    @pytest.mark.asyncio
    async def test_analyze_graceful_degradation(self, metacognitor_no_client):
        """Test graceful degradation without client."""
        result = await metacognitor_no_client.analyze(
            request="Test",
            response="Test response",
        )

        assert isinstance(result, MetacognitiveAnalysis)
        assert result.overall_confidence == 0.5

    def test_check_uncertainty_markers(self, metacognitor):
        """Test checking for uncertainty markers."""
        text = "I think this might be correct, but I'm not sure."

        markers = metacognitor.check_for_uncertainty_markers(text)

        assert "I think" in markers
        assert "might be" in markers
        assert "I'm not sure" in markers

    def test_should_ask_for_clarification(self, metacognitor):
        """Test clarification decision."""
        low_confidence = MetacognitiveAnalysis(overall_confidence=0.3)
        high_confidence = MetacognitiveAnalysis(overall_confidence=0.9)

        assert metacognitor.should_ask_for_clarification(low_confidence) is True
        assert metacognitor.should_ask_for_clarification(high_confidence) is False

    def test_get_improvement_suggestions(self, metacognitor):
        """Test getting improvement suggestions."""
        analysis = MetacognitiveAnalysis(
            overall_confidence=0.4,
            knowledge_gaps=["Topic A", "Topic B"],
            assumptions=["Assumption 1"],
            suggested_actions=["Action 1"],
        )

        suggestions = metacognitor.get_improvement_suggestions(analysis)

        assert len(suggestions) > 0


class TestMetacognitiveAnalysis:
    """Tests for MetacognitiveAnalysis model."""

    def test_default_values(self):
        """Test default values."""
        analysis = MetacognitiveAnalysis()

        assert analysis.overall_confidence == 0.5
        assert analysis.insights == []
        assert analysis.knowledge_gaps == []

    def test_custom_values(self):
        """Test custom values."""
        analysis = MetacognitiveAnalysis(
            overall_confidence=0.8,
            knowledge_gaps=["Gap 1"],
            assumptions=["Assumption 1"],
        )

        assert analysis.overall_confidence == 0.8
        assert len(analysis.knowledge_gaps) == 1


# Run with: pytest tests/phase3/test_learning_reasoning.py -v
