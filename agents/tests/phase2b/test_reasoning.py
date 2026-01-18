"""
Tests for A3: Reflective Reasoning, A9: Prompt Chaining, A11: Planning Patterns
"""

import pytest
from datetime import datetime, timezone
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from middleware.reasoning.reflective_v8 import (
    ReflectiveReasoner,
    ReflectionResult,
)
from middleware.reasoning.prompt_chaining_v8 import (
    PromptChainExecutor,
    ChainStep,
    ChainResult,
    ChainStepStatus,
    IvyLevelChains,
)
from middleware.reasoning.planning_v8 import (
    PlanningEngine,
    Plan,
    PlanStep,
    PlanStepStatus,
    PlanStepType,
)


class TestReflectionResult:
    """Tests for ReflectionResult model."""

    def test_result_creation(self):
        """Test ReflectionResult creation."""
        result = ReflectionResult(
            original_response="Initial response",
            critique="Could be more specific",
            improved_response="Improved response",
            confidence=0.85,
        )
        assert result.original_response == "Initial response"
        assert result.confidence == 0.85

    def test_result_with_issues(self):
        """Test ReflectionResult with issues."""
        result = ReflectionResult(
            original_response="Original",
            critique="Needs work",
            improved_response="Improved",
            confidence=0.9,
            issues_found=["Issue 1", "Issue 2"],
            improvements_made=["Improvement 1"],
            total_iterations=2,
        )
        assert len(result.issues_found) == 2
        assert result.total_iterations == 2


class TestReflectiveReasoner:
    """Tests for ReflectiveReasoner."""

    @pytest.fixture
    def reasoner(self, mock_llm):
        return ReflectiveReasoner(llm_client=mock_llm)

    def test_reasoner_creation(self, reasoner):
        """Test reasoner creation."""
        assert reasoner is not None
        assert reasoner.max_iterations == 3
        assert reasoner.confidence_threshold == 0.85  # actual default

    def test_reasoner_creation_with_params(self, mock_llm):
        """Test reasoner creation with custom params."""
        reasoner = ReflectiveReasoner(
            llm_client=mock_llm,
            max_iterations=5,
            confidence_threshold=0.9,
        )
        assert reasoner.max_iterations == 5
        assert reasoner.confidence_threshold == 0.9

    @pytest.mark.asyncio
    async def test_reason_without_llm(self):
        """Test reasoning without LLM returns input."""
        reasoner = ReflectiveReasoner()
        result = await reasoner.reason(
            prompt="Test input",
        )
        assert isinstance(result, ReflectionResult)
        assert "Test input" in result.original_response


class TestChainStep:
    """Tests for ChainStep model."""

    def test_step_creation(self):
        """Test ChainStep creation."""
        step = ChainStep(
            name="analyze",
            prompt_template="Analyze: {input}",
        )
        assert step.name == "analyze"
        assert step.depends_on == []

    def test_step_with_dependencies(self):
        """Test ChainStep with dependencies."""
        step = ChainStep(
            name="synthesize",
            prompt_template="Combine {analysis} and {evaluation}",
            depends_on=["analysis", "evaluation"],
        )
        assert len(step.depends_on) == 2

    def test_step_with_required_keys(self):
        """Test ChainStep with required output keys."""
        step = ChainStep(
            name="analyze",
            prompt_template="Analyze: {input}",
            required_output_keys=["themes", "tone", "issues"],
        )
        assert len(step.required_output_keys) == 3


class TestChainResult:
    """Tests for ChainResult model."""

    def test_result_creation(self):
        """Test ChainResult creation."""
        result = ChainResult(
            chain_name="essay_review",
            final_output="Combined result",
            step_outputs={"analyze": {"themes": ["growth"]}},
            steps_completed=3,
            success=True,
        )
        assert result.success == True
        assert result.steps_completed == 3
        assert result.chain_name == "essay_review"


class TestPromptChainExecutor:
    """Tests for PromptChainExecutor."""

    @pytest.fixture
    def executor(self, mock_llm):
        return PromptChainExecutor(llm_client=mock_llm)

    def test_executor_creation(self, executor):
        """Test executor creation."""
        assert executor is not None

    @pytest.mark.asyncio
    async def test_execute_simple_chain(self, executor):
        """Test executing simple chain."""
        steps = [
            ChainStep(
                name="step1",
                prompt_template="Process: {input}",
            ),
        ]
        result = await executor.execute(
            chain_name="test_chain",
            steps=steps,
            initial_context={"input": "test data"},
        )
        assert isinstance(result, ChainResult)
        assert result.steps_completed >= 0


class TestIvyLevelChains:
    """Tests for IvyLevelChains."""

    def test_essay_review_chain(self):
        """Test essay review chain creation."""
        chain = IvyLevelChains.essay_review_chain()
        assert len(chain) > 0
        step_names = [s.name for s in chain]
        assert "analyze_prompt" in step_names
        assert "evaluate_content" in step_names
        assert "generate_feedback" in step_names

    def test_activity_planning_chain(self):
        """Test activity planning chain creation."""
        chain = IvyLevelChains.activity_planning_chain()
        assert len(chain) > 0
        step_names = [s.name for s in chain]
        assert "assess_profile" in step_names
        assert "generate_recommendations" in step_names


class TestPlanStep:
    """Tests for PlanStep model."""

    def test_step_creation(self):
        """Test PlanStep creation."""
        step = PlanStep(
            step_id="step_1",
            step_type=PlanStepType.RESEARCH,
            description="Research topic",
        )
        assert step.step_id == "step_1"
        assert step.status == PlanStepStatus.PENDING

    def test_step_with_prerequisites(self):
        """Test PlanStep with prerequisites."""
        step = PlanStep(
            step_id="step_2",
            step_type=PlanStepType.GENERATE,
            description="Write outline",
            prerequisites=["step_1"],
        )
        assert step.prerequisites == ["step_1"]


class TestPlan:
    """Tests for Plan model."""

    def test_plan_creation(self):
        """Test Plan creation."""
        plan = Plan(
            plan_id="test-plan",
            goal="Write an essay",
            steps=[
                PlanStep(step_id="step_1", step_type=PlanStepType.RESEARCH, description="Research"),
                PlanStep(step_id="step_2", step_type=PlanStepType.GENERATE, description="Outline"),
            ],
        )
        assert plan.goal == "Write an essay"
        assert len(plan.steps) == 2
        assert plan.status == "created"

    def test_plan_current_step_tracking(self):
        """Test tracking current step in plan."""
        plan = Plan(
            plan_id="test-plan",
            goal="Test goal",
            steps=[
                PlanStep(step_id="step_1", step_type=PlanStepType.ANALYZE, description="Step 1", status=PlanStepStatus.COMPLETED),
                PlanStep(step_id="step_2", step_type=PlanStepType.GENERATE, description="Step 2"),
            ],
        )
        # Current step starts at 0
        assert plan.current_step == 0
        # Second step is still pending
        assert plan.steps[1].status == PlanStepStatus.PENDING


class TestPlanningEngine:
    """Tests for PlanningEngine."""

    @pytest.fixture
    def engine(self, mock_llm):
        return PlanningEngine(llm_client=mock_llm)

    def test_engine_creation(self, engine):
        """Test engine creation."""
        assert engine is not None
        assert engine.max_replans == 2

    def test_engine_creation_with_params(self, mock_llm):
        """Test engine creation with custom params."""
        engine = PlanningEngine(
            llm_client=mock_llm,
            max_replans=5,
        )
        assert engine.max_replans == 5

    @pytest.mark.asyncio
    async def test_create_plan_without_llm(self):
        """Test creating plan without LLM."""
        engine = PlanningEngine()
        plan = await engine.create_plan(
            goal="Write an essay about climate change",
        )
        assert isinstance(plan, Plan)
        assert len(plan.steps) > 0

    @pytest.mark.asyncio
    async def test_execute_plan(self, engine):
        """Test executing a plan."""
        plan = Plan(
            plan_id="test-plan",
            goal="Test goal",
            steps=[
                PlanStep(step_id="step_1", step_type=PlanStepType.ANALYZE, description="Step 1"),
            ],
        )

        result = await engine.execute_plan(plan)
        assert result.status in ["completed", "executing", "failed"]
