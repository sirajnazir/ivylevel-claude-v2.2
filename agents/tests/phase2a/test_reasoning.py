"""
Tests for A6: ReAct Loop, A7: Self-Correction, A2: Deliberative Reasoning Patterns
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.reasoning import (
    ReActLoop,
    ReActPhase,
    ReActStep,
    ReActResult,
    SelfCorrector,
    SelfCorrectionResult,
    CorrectionAttempt,
    DeliberativeReasoner,
    DeliberationStep,
    DeliberationResult,
)


class TestReActTypes:
    """Tests for ReAct type definitions."""

    def test_react_phase_values(self):
        """Test ReActPhase enum values."""
        assert ReActPhase.THINK == "think"
        assert ReActPhase.ACT == "act"
        assert ReActPhase.OBSERVE == "observe"
        assert ReActPhase.COMPLETE == "complete"

    def test_react_step_creation(self):
        """Test ReActStep model creation."""
        step = ReActStep(
            step_number=1,
            phase=ReActPhase.THINK,
            thought="I need to find information",
        )
        assert step.step_number == 1
        assert step.phase == ReActPhase.THINK

    def test_react_result_creation(self):
        """Test ReActResult model creation."""
        result = ReActResult(
            success=True,
            final_answer="The answer is X",
            total_iterations=3,
            termination_reason="goal_achieved",
        )
        assert result.success == True
        assert result.termination_reason == "goal_achieved"


class TestReActLoop:
    """Tests for ReActLoop."""

    @pytest.fixture
    def loop(self):
        return ReActLoop()

    def test_loop_creation(self, loop):
        """Test loop creation."""
        assert loop is not None
        assert loop.max_iterations == 5
        assert loop.tools == {}

    def test_loop_creation_with_params(self):
        """Test loop creation with custom params."""
        async def mock_tool(**kwargs):
            return "result"

        loop = ReActLoop(
            tools={"mock": mock_tool},
            max_iterations=3,
        )
        assert loop.max_iterations == 3
        assert "mock" in loop.tools

    def test_register_tool(self, loop):
        """Test tool registration."""
        async def search_tool(query: str):
            """Search for information."""
            return f"Results for: {query}"

        loop.register_tool("search", search_tool, "Search for information")
        assert "search" in loop.tools

    def test_summarize_observation_short(self, loop):
        """Summarize short observation returns full text."""
        result = loop._summarize_observation("Short text")
        assert result == "Short text"

    def test_summarize_observation_long(self, loop):
        """Summarize long observation truncates."""
        long_text = "x" * 300
        result = loop._summarize_observation(long_text)
        assert len(result) == 203  # 200 + "..."
        assert result.endswith("...")

    @pytest.mark.asyncio
    async def test_act_unknown_tool(self, loop):
        """Act with unknown tool returns error."""
        result = await loop._act("unknown_tool", {})
        assert "Unknown tool" in result

    @pytest.mark.asyncio
    async def test_act_no_action(self, loop):
        """Act with no action returns message."""
        result = await loop._act(None, {})
        assert "No action specified" in result

    @pytest.mark.asyncio
    async def test_act_tool_success(self, loop):
        """Act with valid tool returns result."""
        async def mock_tool(value: str):
            return f"Got: {value}"

        loop.tools["mock"] = mock_tool
        result = await loop._act("mock", {"value": "test"})
        assert result == "Got: test"

    @pytest.mark.asyncio
    async def test_run_without_llm_returns_fallback(self, loop):
        """Run without LLM returns fallback."""
        result = await loop.run("Test task")
        assert result.success == True
        assert result.final_answer == "Unable to reason about task"


class TestSelfCorrectionTypes:
    """Tests for self-correction type definitions."""

    def test_correction_attempt_creation(self):
        """Test CorrectionAttempt model creation."""
        attempt = CorrectionAttempt(
            attempt_number=1,
            original_response="Original",
            identified_issues=["Issue 1", "Issue 2"],
            corrected_response="Corrected",
            confidence_before=0.5,
            confidence_after=0.8,
        )
        assert attempt.attempt_number == 1
        assert len(attempt.identified_issues) == 2

    def test_self_correction_result_creation(self):
        """Test SelfCorrectionResult model creation."""
        result = SelfCorrectionResult(
            final_response="Final response",
            was_corrected=True,
            final_confidence=0.85,
        )
        assert result.was_corrected == True
        assert result.final_confidence == 0.85


class TestSelfCorrector:
    """Tests for SelfCorrector."""

    @pytest.fixture
    def corrector(self):
        return SelfCorrector()

    def test_corrector_creation(self, corrector):
        """Test corrector creation."""
        assert corrector is not None
        assert corrector.max_corrections == 1
        assert corrector.min_confidence == 0.7

    def test_corrector_creation_with_params(self):
        """Test corrector creation with custom params."""
        corrector = SelfCorrector(
            max_corrections=2,
            min_confidence=0.8,
        )
        assert corrector.max_corrections == 2
        assert corrector.min_confidence == 0.8

    def test_parse_response_simple(self, corrector):
        """Parse simple response."""
        content = """
RESPONSE:
This is the response.

SELF-CRITIQUE:
- Confidence (0.0-1.0): 0.8
- Issues found: None
"""
        response, confidence, issues = corrector._parse_response_and_critique(content)
        assert "This is the response" in response
        assert confidence == 0.8
        assert issues == []

    def test_parse_response_with_issues(self, corrector):
        """Parse response with issues."""
        content = """
RESPONSE:
This is the response.

SELF-CRITIQUE:
- Confidence (0.0-1.0): 0.5
- Issues found:
- Too vague
- Not actionable
"""
        response, confidence, issues = corrector._parse_response_and_critique(content)
        assert confidence == 0.5
        assert "Too vague" in issues or len(issues) > 0


class TestDeliberativeTypes:
    """Tests for deliberative type definitions."""

    def test_deliberation_step_creation(self):
        """Test DeliberationStep model creation."""
        step = DeliberationStep(
            step_name="understand",
            question="What is the student asking?",
            analysis="The student needs help with essay",
            conclusion="Focus on essay structure",
            confidence=0.8,
        )
        assert step.step_name == "understand"
        assert step.confidence == 0.8

    def test_deliberation_result_creation(self):
        """Test DeliberationResult model creation."""
        result = DeliberationResult(
            task="Help with essay",
            final_decision="Provide essay outline",
            decision_reasoning="Student is stuck on structure",
            decision_confidence=0.85,
            deliberation_time_ms=500,
        )
        assert result.decision_confidence == 0.85


class TestDeliberativeReasoner:
    """Tests for DeliberativeReasoner."""

    @pytest.fixture
    def reasoner(self):
        return DeliberativeReasoner()

    def test_reasoner_creation(self, reasoner):
        """Test reasoner creation."""
        assert reasoner is not None

    @pytest.mark.asyncio
    async def test_deliberate_step_without_llm(self, reasoner):
        """Deliberate step without LLM returns fallback."""
        result = await reasoner._deliberate_step(
            task="Test task",
            step_name="understand",
            question="What is being asked?",
            context={},
            previous_reasoning="",
        )

        assert "Unable to analyze" in result["analysis"]
        assert result["confidence"] == 0.5

    @pytest.mark.asyncio
    async def test_synthesize_decision_without_llm(self, reasoner):
        """Synthesize decision without LLM returns fallback."""
        steps = [
            DeliberationStep(
                step_name="understand",
                question="What?",
                analysis="Analysis",
                conclusion="Conclusion",
                confidence=0.7,
            )
        ]

        decision, reasoning, confidence = await reasoner._synthesize_decision(
            task="Test",
            steps=steps,
            context={},
        )

        assert decision == "Conclusion"
        assert confidence == 0.7
